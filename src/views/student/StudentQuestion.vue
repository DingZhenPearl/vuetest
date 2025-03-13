<template>
  <div class="question-page">
    <!-- 导航侧边栏 -->
    <StudentNavbar />

    <!-- 主内容区 -->
    <div class="main-content">
      <h1>编程问题求助</h1>
      
      <form class="question-form" @submit.prevent="submitQuestion">
        <input type="text" v-model="questionForm.title" placeholder="问题标题" required>
        <textarea v-model="questionForm.content" placeholder="详细描述你的问题..." required></textarea>
        <button type="submit" class="submit-btn" :disabled="isSubmitting">
          {{ isEditMode ? '更新问题' : '提交问题' }}
        </button>
        <button v-if="isEditMode" type="button" class="cancel-btn" @click="cancelEdit">取消编辑</button>
      </form>

      <div class="questions-list">
        <div v-if="loading" class="loading">加载中...</div>
        <div v-else-if="questions.length === 0" class="empty-state">
          暂无提问记录，请提交您的第一个问题
        </div>
        
        <div v-for="question in questions" :key="question.id" class="question-item">
          <div class="question-header">
            <h3>{{ question.title }}</h3>
            <div v-if="question.status === 'pending'" class="question-actions">
              <button @click="editQuestion(question)" class="edit-btn">编辑</button>
              <button @click="deleteQuestion(question.id)" class="delete-btn">删除</button>
            </div>
          </div>

          <div class="question-meta">
            <span class="time-info">提问时间: {{ formatDate(question.created_at) }}</span>
            <span :class="['status', question.status === 'pending' ? 'pending' : 'answered']">
              状态: {{ question.status === 'pending' ? '待回答' : '已回答' }}
            </span>
          </div>

          <p class="question-content">{{ question.content }}</p>
          
          <div v-if="question.answer" class="answer">
            <div class="answer-header">
              <strong>老师回答：</strong>
              <span class="time-info">回答时间: {{ formatDate(question.answered_at) }}</span>
            </div>
            <p>{{ question.answer }}</p>
          </div>

          <!-- 追问/追答列表 -->
          <div v-if="question.follow_ups && question.follow_ups.length > 0">
            <div 
              v-for="(followUp, index) in getFollowUps(question.follow_ups)" 
              :key="index"
              :class="['follow-up', followUp.user === 'teacher' ? 'teacher' : '']">
              <div class="follow-up-header">
                <span>{{ followUp.user === 'teacher' ? '老师追答' : '我的追问' }}</span>
                <span class="time-info">{{ formatDate(followUp.time) }}</span>
              </div>
              <p>{{ followUp.content }}</p>
            </div>
          </div>

          <!-- 追问表单 -->
          <form class="follow-up-form" @submit.prevent="submitFollowUp(question.id)">
            <textarea v-model="followUpTexts[question.id]" placeholder="输入追问内容..." required></textarea>
            <button type="submit" class="submit-btn" :disabled="isSubmittingFollowUp">提交追问</button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import StudentNavbar from '@/components/student/StudentNavbar.vue'

export default {
  name: 'StudentQuestion',
  components: {
    StudentNavbar
  },
  data() {
    return {
      questions: [],
      loading: true,
      isSubmitting: false,
      isSubmittingFollowUp: false,
      isEditMode: false,
      currentEditId: null,
      questionForm: {
        title: '',
        content: ''
      },
      followUpTexts: {},
      userEmail: ''
    }
  },
  created() {
    // 获取当前登录用户的邮箱
    this.userEmail = sessionStorage.getItem('userEmail')
    if (!this.userEmail) {
      this.$router.push('/login')
      return
    }
    
    this.loadQuestions()
  },
  methods: {
    // 加载学生的问题列表
    async loadQuestions() {
      this.loading = true
      try {
        const response = await fetch(`/api/questions/student/${this.userEmail}`) // 更新API路径
        const data = await response.json()
        
        if (data.success && Array.isArray(data.questions)) {
          this.questions = data.questions
          // 初始化每个问题的追问输入字段
          this.questions.forEach(q => {
            if (!this.followUpTexts[q.id]) {
              this.followUpTexts[q.id] = ''
            }
          })
        } else {
          console.error('获取问题列表失败:', data)
        }
      } catch (error) {
        console.error('加载问题列表出错:', error)
      } finally {
        this.loading = false
      }
    },
    
    // 提交问题
    async submitQuestion() {
      if (!this.questionForm.title.trim() || !this.questionForm.content.trim()) {
        alert('请填写完整的问题信息')
        return
      }
      
      this.isSubmitting = true
      
      try {
        let response
        
        if (this.isEditMode) {
          // 更新现有问题
          response = await fetch(`/api/questions/${this.currentEditId}`, {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              title: this.questionForm.title,
              content: this.questionForm.content
            })
          })
        } else {
          // 创建新问题
          response = await fetch('/api/questions/submit', { // 更新API路径
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              email: this.userEmail,
              title: this.questionForm.title,
              content: this.questionForm.content
            })
          })
        }

        const data = await response.json()
        
        if (data.success) {
          this.resetForm()
          this.loadQuestions()
          alert(this.isEditMode ? '问题更新成功' : '问题提交成功')
        } else {
          alert(data.message || '操作失败，请重试')
        }
      } catch (error) {
        console.error('提交问题出错:', error)
        alert('提交失败，请检查网络连接')
      } finally {
        this.isSubmitting = false
      }
    },
    
    // 删除问题
    async deleteQuestion(questionId) {
      if (!confirm('确定要删除这个问题吗？')) {
        return
      }
      
      try {
        const response = await fetch(`/api/questions/${questionId}`, { // 更新API路径
          method: 'DELETE'
        })
        const data = await response.json()
        
        if (data.success) {
          alert('问题删除成功')
          this.loadQuestions()
        } else {
          alert(data.message || '删除失败')
        }
      } catch (error) {
        console.error('删除问题出错:', error)
        alert('删除失败，请重试')
      }
    },
    
    // 编辑问题
    editQuestion(question) {
      this.isEditMode = true
      this.currentEditId = question.id
      this.questionForm.title = question.title
      this.questionForm.content = question.content
      
      // 滚动到表单位置
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      })
    },
    
    // 取消编辑
    cancelEdit() {
      this.resetForm()
    },
    
    // 重置表单
    resetForm() {
      this.isEditMode = false
      this.currentEditId = null
      this.questionForm.title = ''
      this.questionForm.content = ''
    },
    
    // 提交追问
    async submitFollowUp(questionId) {
      const content = this.followUpTexts[questionId]?.trim()
      if (!content) return
      
      this.isSubmittingFollowUp = true
      
      try {
        const response = await fetch('/api/questions/follow-up', { // 更新API路径
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ questionId, content })
        })
        
        if (response.ok) {
          this.followUpTexts[questionId] = ''
          await this.loadQuestions()
        } else {
          const error = await response.json()
          alert(error.message || '提交追问失败')
        }
      } catch (error) {
        console.error('提交追问出错:', error)
        alert('提交失败，请重试')
      } finally {
        this.isSubmittingFollowUp = false
      }
    },
    
    // 处理追问/追答数据
    getFollowUps(followUps) {
      if (!followUps) return []
      
      try {
        if (typeof followUps === 'string') {
          return JSON.parse(followUps)
        }
        return followUps
      } catch (e) {
        console.error('解析追问数据失败:', e)
        return []
      }
    },
    
    // 格式化日期
    formatDate(dateString) {
      if (!dateString) return ''
      
      try {
        return new Date(dateString).toLocaleString('zh-CN', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit'
        })
      } catch (e) {
        console.error('日期格式化失败:', e)
        return dateString
      }
    }
  }
}
</script>

<style scoped>
.question-page {
  display: flex;
  min-height: 100vh;
}

.main-content {
  margin-left: 250px;
  padding: 20px;
  width: calc(100% - 250px);
  box-sizing: border-box;
}

h1 {
  color: #2c3e50;
  margin-bottom: 20px;
}

.question-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 30px;
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.question-form input, 
.question-form textarea {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  font-family: inherit;
}

.question-form textarea {
  min-height: 200px;
  resize: vertical;
}

.submit-btn {
  background-color: #4CAF50;
  color: white;
  padding: 12px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s;
}

.submit-btn:hover {
  background-color: #45a049;
}

.submit-btn:disabled {
  background-color: #a5d6a7;
  cursor: not-allowed;
}

.cancel-btn {
  padding: 12px 20px;
  background-color: #f5f5f5;
  color: #333;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}

.cancel-btn:hover {
  background-color: #e0e0e0;
}

.questions-list {
  margin-top: 30px;
}

.loading, .empty-state {
  text-align: center;
  padding: 30px;
  color: #666;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.question-item {
  border: 1px solid #ddd;
  padding: 15px;
  margin-bottom: 15px;
  border-radius: 8px;
  background: white;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.question-header h3 {
  margin: 0;
}

.question-meta {
  display: flex;
  align-items: center;
  margin: 10px 0;
  color: #666;
}

.time-info {
  color: #666;
  font-size: 14px;
  margin-right: 15px;
}

.status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
}

.status.pending {
  background-color: #ffd700;
  color: #000;
}

.status.answered {
  background-color: #4CAF50;
  color: white;
}

.question-content {
  margin-bottom: 15px;
  white-space: pre-line;
}

.answer {
  margin-top: 10px;
  padding: 10px;
  background-color: #f9f9f9;
  border-left: 3px solid #4CAF50;
  margin-bottom: 15px;
}

.answer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding-bottom: 5px;
  border-bottom: 1px solid #eee;
}

.question-actions {
  display: flex;
  gap: 10px;
}

.edit-btn, .delete-btn {
  padding: 5px 10px;
  border-radius: 4px;
  cursor: pointer;
  border: none;
}

.edit-btn {
  background-color: #4CAF50;
  color: white;
}

.delete-btn {
  background-color: #f44336;
  color: white;
}

.edit-btn:hover {
  background-color: #45a049;
}

.delete-btn:hover {
  background-color: #da190b;
}

.follow-up {
  margin: 15px 0;
  padding: 12px;
  border-left: 3px solid #2196F3;
  background: #f8f9fa;
  border-radius: 4px;
}

.follow-up.teacher {
  border-color: #4CAF50;
}

.follow-up-header {
  display: flex;
  justify-content: space-between;
  color: #666;
  margin-bottom: 8px;
}

.follow-up-form {
  margin-top: 20px;
}

.follow-up-form textarea {
  width: 100%;
  min-height: 80px;
  margin: 10px 0;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-family: inherit;
  box-sizing: border-box;
}
</style>