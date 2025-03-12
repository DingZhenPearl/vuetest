<template>
  <div class="teacher-answer-page">
    <!-- 导航侧边栏 -->
    <TeacherNavbar />

    <!-- 主内容区 -->
    <div class="main-content">
      <h1>学生问题列表</h1>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>加载中，请稍候...</p>
      </div>

      <!-- 问题列表 -->
      <div v-else class="questions-list">
        <div v-if="questions.length === 0" class="empty-state">
          暂无学生提问
        </div>

        <div v-for="question in questions" :key="question.id" class="question-card">
          <!-- 问题头部信息 -->
          <div class="question-header">
            <div class="student-info">学生邮箱: {{ question.email }}</div>
            <div class="time-info">提问时间: {{ formatDate(question.created_at) }}</div>
          </div>

          <!-- 问题内容 -->
          <h3>{{ question.title }}</h3>
          <p>{{ question.content }}</p>
          <span 
            :class="['status-badge', question.status === 'pending' ? 'status-pending' : 'status-answered']"
          >
            {{ question.status === 'pending' ? '待回答' : '已回答' }}
          </span>

          <!-- 回答区域 -->
          <div v-if="question.answer" class="answer-content">
            <div class="answer-header">
              <strong>回答：</strong>
              <span class="time-info">回答时间: {{ formatDate(question.answered_at) }}</span>
            </div>
            <p>{{ question.answer }}</p>
          </div>
          <form v-else class="answer-form" @submit.prevent="submitAnswer(question.id)">
            <textarea v-model="answerTexts[question.id]" placeholder="输入你的回答..." required></textarea>
            <button type="submit" class="submit-btn" :disabled="submittingAnswer">提交回答</button>
          </form>

          <!-- 追问/追答列表 -->
          <div v-if="question.follow_ups && question.follow_ups.length > 0">
            <div 
              v-for="(followUp, index) in getFollowUps(question.follow_ups)" 
              :key="index"
              :class="['follow-up', followUp.user === 'teacher' ? 'teacher' : '']"
            >
              <div class="follow-up-header">
                <span>{{ followUp.user === 'teacher' ? '老师追答' : '学生追问' }}</span>
                <span class="time-info">{{ formatDate(followUp.time) }}</span>
              </div>
              <p>{{ followUp.content }}</p>
            </div>
          </div>

          <!-- 追答表单 -->
          <form class="follow-up-form" @submit.prevent="submitFollowUpAnswer(question.id)">
            <textarea 
              v-model="followUpTexts[question.id]" 
              placeholder="输入追答内容..." 
              required
            ></textarea>
            <button 
              type="submit" 
              class="submit-btn" 
              :disabled="submittingFollowUp"
            >
              提交追答
            </button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import TeacherNavbar from '@/components/teacher/TeacherNavbar.vue'

export default {
  name: 'TeacherAnswer',
  components: {
    TeacherNavbar
  },
  data() {
    return {
      questions: [],
      loading: true,
      submittingAnswer: false,
      submittingFollowUp: false,
      answerTexts: {},   // 存储每个问题的回答文本
      followUpTexts: {}  // 存储每个问题的追答文本
    }
  },
  created() {
    this.loadAllQuestions()
  },
  methods: {
    // 加载所有学生问题
    async loadAllQuestions() {
      this.loading = true
      try {
        const response = await fetch('/api/all-questions')
        const data = await response.json()
        
        if (data.success && Array.isArray(data.questions)) {
          this.questions = data.questions
          
          // 初始化每个问题的回答和追答输入字段
          this.questions.forEach(q => {
            if (!this.answerTexts[q.id]) {
              this.answerTexts[q.id] = ''
            }
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
    
    // 提交问题回答
    async submitAnswer(questionId) {
      const answer = this.answerTexts[questionId].trim()
      if (!answer) return
      
      this.submittingAnswer = true
      
      try {
        const response = await fetch('/api/submit-answer', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            questionId,
            answer
          })
        })
        
        const data = await response.json()
        
        if (data.success) {
          this.$notify({
            title: '成功',
            message: '回答提交成功',
            type: 'success'
          })
          this.answerTexts[questionId] = ''
          await this.loadAllQuestions()
        } else {
          this.$notify({
            title: '失败',
            message: data.message || '提交回答失败',
            type: 'error'
          })
        }
      } catch (error) {
        console.error('提交回答出错:', error)
        this.$notify({
          title: '错误',
          message: '提交失败，请重试',
          type: 'error'
        })
      } finally {
        this.submittingAnswer = false
      }
    },
    
    // 提交追答
    async submitFollowUpAnswer(questionId) {
      const content = this.followUpTexts[questionId].trim()
      if (!content) return
      
      this.submittingFollowUp = true
      
      try {
        const response = await fetch('/api/follow-up-answer', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            questionId,
            content
          })
        })
        
        const data = await response.json()
        
        if (data.success) {
          this.followUpTexts[questionId] = ''
          await this.loadAllQuestions()
        } else {
          alert(data.message || '提交追答失败')
        }
      } catch (error) {
        console.error('提交追答出错:', error)
        alert('提交失败，请重试')
      } finally {
        this.submittingFollowUp = false
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
.teacher-answer-page {
  display: flex;
  min-height: 100vh;
}

.main-content {
  margin-left: 250px;
  padding: 20px;
  width: calc(100% - 250px);
  box-sizing: border-box;
  background-color: #f4f4f4;
}

h1 {
  color: #2c3e50;
  margin-bottom: 20px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.loading-spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border-left-color: #4CAF50;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-state {
  background: white;
  padding: 30px;
  text-align: center;
  color: #666;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.questions-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.question-card {
  border: 1px solid #ddd;
  padding: 20px;
  border-radius: 8px;
  background-color: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.student-info {
  color: #666;
  font-size: 14px;
}

.time-info {
  color: #666;
  font-size: 14px;
}

.status-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
  margin: 10px 0;
}

.status-pending {
  background-color: #ffd700;
  color: #000;
}

.status-answered {
  background-color: #4CAF50;
  color: white;
}

.answer-form {
  margin-top: 15px;
}

.answer-form textarea,
.follow-up-form textarea {
  width: 100%;
  min-height: 100px;
  padding: 10px;
  margin: 10px 0;
  border: 1px solid #ddd;
  border-radius: 4px;
  resize: vertical;
  font-family: inherit;
  box-sizing: border-box;
}

.submit-btn {
  background-color: #4CAF50;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.submit-btn:hover {
  background-color: #45a049;
}

.submit-btn:disabled {
  background-color: #a5d6a7;
  cursor: not-allowed;
}

.answer-content {
  margin: 15px 0;
  padding: 15px;
  background-color: #f9f9f9;
  border-left: 3px solid #4CAF50;
  border-radius: 4px;
}

.answer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding-bottom: 5px;
  border-bottom: 1px solid #eee;
}

.follow-up {
  margin: 15px 0;
  padding: 12px;
  border-left: 3px solid #2196F3;
  background: #f8f9fa;
  border-radius: 4px;
}

.follow-up.teacher {
  border-left-color: #4CAF50;
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
</style>