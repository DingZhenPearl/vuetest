<template>
  <el-dialog
    :title="isTeacher ? '题目相关问题' : '提交问题'"
    v-model="dialogVisible"
    width="60%"
    :before-close="handleClose"
  >
    <!-- 教师查看相关题目问题时的内容 -->
    <div v-if="isTeacher && relatedProblemId" class="problems-questions">
      <h3>与题目 #{{relatedProblemId}} 相关的问题</h3>
      
      <div v-if="loading" class="loading">
        <i class="el-icon-loading"></i> 加载中...
      </div>
      
      <div v-else-if="questions.length === 0" class="empty-state">
        暂无与该题目相关的问题
      </div>
      
      <div v-else class="questions-list">
        <div v-for="question in questions" :key="question.id" class="question-item">
          <h4>{{ question.title }}</h4>
          <p>{{ question.content }}</p>
          <div class="meta-info">
            <span>提问者: {{ question.email }}</span>
            <span>状态: {{ question.status === 'pending' ? '待回答' : '已回答' }}</span>
          </div>
          
          <el-button 
            type="primary" 
            size="small" 
            @click="goToAnswer(question.id)" 
            v-if="question.status === 'pending'">
            回答问题
          </el-button>
        </div>
      </div>
    </div>
    
    <!-- 学生提问或教师回复通用表单 -->
    <div v-else class="question-form-container">
      <p v-if="relatedProblemId">
        您正在提交关于题目 #{{relatedProblemId}} 的问题
      </p>
      
      <el-form :model="questionForm" :rules="rules" ref="questionForm" label-width="80px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="questionForm.title" placeholder="请输入问题标题"></el-input>
        </el-form-item>
        
        <el-form-item label="内容" prop="content">
          <el-input 
            type="textarea" 
            v-model="questionForm.content" 
            :rows="6"
            placeholder="请详细描述您的问题..."
          ></el-input>
        </el-form-item>
      </el-form>
    </div>
    
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button 
          v-if="!isTeacher || (isTeacher && !relatedProblemId)"
          type="primary" 
          :loading="submitting"
          @click="submitQuestion">
          提交
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script>
export default {
  name: 'QuestionDialogComponent',
  props: {
    visible: {
      type: Boolean,
      required: true
    },
    isTeacher: {
      type: Boolean,
      default: false
    },
    relatedProblemId: {
      type: Number,
      default: null
    }
  },
  emits: ['update:visible', 'question-submitted'],
  data() {
    return {
      loading: false,
      submitting: false,
      questions: [],
      questionForm: {
        title: '',
        content: ''
      },
      rules: {
        title: [
          { required: true, message: '请输入问题标题', trigger: 'blur' },
          { min: 3, max: 100, message: '长度在 3 到 100 个字符', trigger: 'blur' }
        ],
        content: [
          { required: true, message: '请输入问题内容', trigger: 'blur' },
          { min: 10, max: 2000, message: '长度在 10 到 2000 个字符', trigger: 'blur' }
        ]
      }
    }
  },
  computed: {
    dialogVisible: {
      get() {
        return this.visible;
      },
      set(value) {
        this.$emit('update:visible', value);
      }
    }
  },
  watch: {
    visible(val) {
      if (val && this.isTeacher && this.relatedProblemId) {
        // 当对话框显示且是教师查看相关问题时，加载相关题目的问题
        this.loadRelatedQuestions();
      }
      
      // 每次显示对话框时重置表单
      if (val && !this.isTeacher) {
        this.$nextTick(() => {
          if (this.$refs.questionForm) {
            this.$refs.questionForm.resetFields();
          }
        });
      }
    }
  },
  methods: {
    handleClose() {
      this.dialogVisible = false;
      // 重置表单
      if (this.$refs.questionForm) {
        this.$refs.questionForm.resetFields();
      }
    },
    
    // 提交问题
    async submitQuestion() {
      if (this.$refs.questionForm) {
        try {
          await this.$refs.questionForm.validate();
        } catch (e) {
          return; // 表单验证失败
        }
        
        this.submitting = true;
        try {
          // 获取当前用户邮箱
          const email = sessionStorage.getItem('userEmail');
          if (!email) {
            this.$message.error('用户未登录，请先登录');
            return;
          }
          
          const requestBody = {
            email: email,
            title: this.questionForm.title,
            content: this.questionForm.content
          };
          
          // 如果有关联的题目ID，添加到问题内容中
          if (this.relatedProblemId) {
            requestBody.content = `[关联题目ID: ${this.relatedProblemId}] ` + requestBody.content;
          }
          
          const response = await fetch('/api/questions/submit', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
          });
          
          const data = await response.json();
          
          if (data.success) {
            this.$message({
              message: '问题提交成功',
              type: 'success'
            });
            
            // 通知父组件提交成功
            this.$emit('question-submitted');
            
            // 关闭对话框
            this.handleClose();
          } else {
            this.$message.error(data.message || '提交失败');
          }
        } catch (error) {
          console.error('提交问题出错:', error);
          this.$message.error('网络错误，请稍后重试');
        } finally {
          this.submitting = false;
        }
      }
    },
    
    // 加载与题目相关的问题
    async loadRelatedQuestions() {
      if (!this.relatedProblemId) return;
      
      this.loading = true;
      try {
        const response = await fetch('/api/questions/all');
        const data = await response.json();
        
        if (data.success && Array.isArray(data.questions)) {
          // 过滤出与当前题目相关的问题
          this.questions = data.questions.filter(q => {
            // 检查内容中是否包含题目ID的引用
            return q.content.includes(`[关联题目ID: ${this.relatedProblemId}]`);
          });
        } else {
          console.error('获取问题列表失败:', data);
        }
      } catch (error) {
        console.error('加载相关问题失败:', error);
        this.$message.error('加载相关问题失败');
      } finally {
        this.loading = false;
      }
    },
    
    // 跳转到回答问题页面
    goToAnswer(questionId) {
      // 关闭对话框
      this.handleClose();
      
      // 导航到回答问题页面，传递问题ID参数
      this.$router.push(`/teacher/answer?id=${questionId}`);
    }
  }
}
</script>

<style scoped>
.questions-list {
  max-height: 400px;
  overflow-y: auto;
}

.question-item {
  border: 1px solid #eee;
  border-radius: 4px;
  padding: 15px;
  margin-bottom: 15px;
  background-color: #fafafa;
}

.question-item h4 {
  margin-top: 0;
  margin-bottom: 10px;
}

.question-item .meta-info {
  display: flex;
  justify-content: space-between;
  color: #666;
  font-size: 0.9em;
  margin: 10px 0;
}

.empty-state {
  text-align: center;
  color: #999;
  padding: 30px 0;
}

.loading {
  text-align: center;
  padding: 30px 0;
}

.question-form-container {
  margin-top: 15px;
}
</style>
