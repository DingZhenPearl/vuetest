<template>
  <div class="teacher-answer-page">
    <!-- 导航侧边栏 -->
    <TeacherNavbar />

    <!-- 主内容区 -->
    <div class="main-content">
      <h1>学生问题讨论区</h1>

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

        <div class="forum-list">
          <table class="forum-table" v-if="questions.length > 0">
            <thead>
              <tr>
                <th class="title-col">话题</th>
                <th class="author-col">发布者</th>
                <th class="status-col">状态</th>
                <th class="date-col">发布时间</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="question in questions" :key="question.id" class="question-row" @click="viewQuestionDetail(question)">
                <td class="title-col">
                  <div class="question-title">{{ question.title }}</div>
                  <div class="post-meta">
                    <span v-if="question.posted_as_teacher" class="teacher-badge">教师身份发布</span>
                    <span class="author">{{ question.email }}</span>
                    <span class="reply-count">{{ getReplyCount(question) }} 回复</span>
                  </div>
                </td>
                <td class="author-col">{{ question.email }}</td>
                <td class="status-col">
                  <span :class="['status-badge', question.status === 'pending' ? 'status-pending' : 'status-answered']">
                    {{ question.status === 'pending' ? '未回复' : '已回复' }}
                  </span>
                </td>
                <td class="date-col">{{ formatDate(question.created_at) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 问题详情弹窗 -->
      <div v-if="currentQuestion" class="question-detail-modal">
        <div class="modal-content">
          <div class="modal-header">
            <h2>话题详情</h2>
            <button @click="closeQuestionDetail" class="close-btn">&times;</button>
          </div>
          
          <div class="topic-container">
            <!-- 主题内容 -->
            <div class="post main-post">
              <div class="post-header">
                <h3 class="post-title">{{ currentQuestion.title }}</h3>
                <div class="post-meta">
                  <span class="author student">{{ currentQuestion.email }}</span>
                  <span class="post-time">{{ formatDate(currentQuestion.created_at) }}</span>
                  <span :class="['status-label', currentQuestion.status === 'pending' ? 'status-pending' : 'status-answered']">
                    {{ currentQuestion.status === 'pending' ? '未回复' : '已回复' }}
                  </span>
                </div>
              </div>
              <div class="post-content">{{ currentQuestion.content }}</div>
            </div>

            <!-- 回复列表 -->
            <div class="replies">
              <!-- 老师的回答作为第一条回复 -->
              <div v-if="currentQuestion.answer" class="post reply">
                <div class="post-header">
                  <div class="post-meta">
                    <span class="author teacher">我</span>
                    <span class="post-time">{{ formatDate(currentQuestion.answered_at) }}</span>
                    <button 
                      @click="deleteAnswer(currentQuestion.id)" 
                      class="delete-reply-btn"
                      title="删除回复">
                      <i class="fas fa-trash"></i> 删除
                    </button>
                  </div>
                </div>
                <div class="post-content">
                  {{ currentQuestion.answer }}
                </div>
              </div>

              <!-- 追问追答显示为普通的论坛回复 -->
              <template v-if="currentQuestion.follow_ups && currentQuestion.follow_ups.length > 0">
                <div 
                  v-for="(followUp, index) in getFollowUps(currentQuestion.follow_ups)" 
                  :key="index"
                  class="post reply">
                  <div class="post-header">
                    <div class="post-meta">
                      <template v-if="followUp.user === 'teacher'">
                        <span class="author teacher">{{ followUp.email }}</span>
                      </template>
                      <template v-else>
                        <!-- 修改这里：显示实际的回复者邮箱 -->
                        <span class="author student">{{ followUp.email }}</span>
                      </template>
                      <span class="post-time">{{ formatDate(followUp.time) }}</span>
                      <!-- 只允许删除自己的回复 -->
                      <button 
                        v-if="followUp.user === 'teacher' && followUp.email === userEmail" 
                        @click="deleteFollowUp(currentQuestion.id, index)" 
                        class="delete-reply-btn"
                        title="删除回复">
                        <i class="fas fa-trash"></i> 删除
                      </button>
                    </div>
                  </div>
                  <div class="post-content">
                    {{ followUp.content }}
                  </div>
                </div>
              </template>

              <!-- 统一的回复表单 - 取代原来的两个表单 -->
              <form class="reply-form" @submit.prevent="submitReply(currentQuestion.id)">
                <h3 class="reply-title">{{ !currentQuestion.answer ? '回复主题' : '添加回复' }}</h3>
                <textarea 
                  v-model="replyText" 
                  placeholder="输入你的回复..." 
                  required
                ></textarea>
                <button 
                  type="submit" 
                  class="submit-btn" 
                  :disabled="submittingReply"
                >
                  发表回复
                </button>
              </form>
            </div>
          </div>
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
      currentQuestion: null,
      submittingReply: false,
      replyText: '',  // 统一的回复文本
      answerTexts: {}, // 保留这个以避免破坏其他逻辑
      followUpTexts: {} // 保留这个以避免破坏其他逻辑
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
        const response = await fetch('/api/questions/all') // 更新API路径
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
    
    // 查看问题详情
    viewQuestionDetail(question) {
      this.currentQuestion = question
      this.replyText = '' // 重置回复文本
    },
    
    // 关闭问题详情
    closeQuestionDetail() {
      this.currentQuestion = null
    },
    
    // 统一的回复提交处理
    async submitReply(questionId) {
      if (!this.replyText.trim()) return
      
      this.submittingReply = true
      
      try {
        let  responseData
        // endpoint,
        // 根据问题是否已回答选择不同的API
        if (!this.currentQuestion.answer) {
          // 首次回答
          responseData = await this.submitFirstAnswer(questionId, this.replyText)
        } else {
          // 追加回复
          responseData = await this.submitFollowUpAnswer(questionId, this.replyText)
        }
        
        if (responseData.success) {
          this.replyText = ''
          await this.loadAllQuestions()
          
          // 更新当前问题
          if (this.currentQuestion && this.currentQuestion.id === questionId) {
            this.currentQuestion = this.questions.find(q => q.id === questionId)
          }
        } else {
          alert(responseData.message || '提交回复失败')
        }
      } catch (error) {
        console.error('提交回复出错:', error)
        alert('提交失败，请重试')
      } finally {
        this.submittingReply = false
      }
    },
    
    // 提交首次回答
    async submitFirstAnswer(questionId, answer) {
      const response = await fetch('/api/questions/answer', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          questionId,
          answer,
          teacherEmail: sessionStorage.getItem('userEmail') // 添加教师邮箱
        })
      })
      
      return await response.json()
    },
    
    // 提交追加回答
    async submitFollowUpAnswer(questionId, content) {
      const response = await fetch('/api/questions/follow-up-answer', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          questionId,
          content,
          teacherEmail: sessionStorage.getItem('userEmail') // 添加教师邮箱
        })
      })
      
      return await response.json()
    },
    
    // 删除回答
    async deleteAnswer(questionId) {
      if (!confirm('确定要删除这条回复吗？删除后不可恢复。')) {
        return
      }
      
      try {
        // 这里需要添加一个新的API端点处理删除回答
        const response = await fetch(`/api/questions/answer/${questionId}`, {
          method: 'DELETE'
        })
        
        const data = await response.json()
        
        if (data.success) {
          await this.loadAllQuestions()
          // 更新当前问题
          if (this.currentQuestion && this.currentQuestion.id === questionId) {
            this.currentQuestion = this.questions.find(q => q.id === questionId)
          }
        } else {
          alert(data.message || '删除回复失败')
        }
      } catch (error) {
        console.error('删除回答出错:', error)
        alert('删除失败，请重试')
      }
    },
    
    // 删除追答
    async deleteFollowUp(questionId, index) {
      if (!confirm('确定要删除这条回复吗？删除后不可恢复。')) {
        return
      }
      
      try {
        const response = await fetch(`/api/questions/follow-up/${questionId}/${index}`, {
          method: 'DELETE'
        })
        const data = await response.json()
        
        if (data.success) {
          await this.loadAllQuestions()
          
          // 更新当前问题
          if (this.currentQuestion && this.currentQuestion.id === questionId) {
            this.currentQuestion = this.questions.find(q => q.id === questionId)
          }
        } else {
          alert(data.message || '删除回复失败')
        }
      } catch (error) {
        console.error('删除回复出错:', error)
        alert('删除失败，请重试')
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
    
    // 获取回复数量
    getReplyCount(question) {
      let count = 0
      
      // 如果有回答，计数+1
      if(question.answer) count++
      
      // 加上追问/追答的数量
      if(question.follow_ups) {
        try {
          const followUps = typeof question.follow_ups === 'string' 
            ? JSON.parse(question.follow_ups) 
            : question.follow_ups
          count += followUps.length
        } catch(e) {
          console.error('解析追问数据失败:', e)
        }
      }
      
      return count
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
  background-color: #f5f5f5;
}

.main-content {
  margin-left: 250px;
  padding: 20px;
  width: calc(100% - 250px);
  box-sizing: border-box;
}

h1, h2, h3 {
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

/* 论坛列表样式 */
.forum-list {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  overflow: hidden;
}

.forum-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.forum-table th {
  background-color: #f8f9fa;
  padding: 15px;
  border-bottom: 2px solid #eee;
  font-weight: bold;
}

.forum-table td {
  padding: 15px;
  border-bottom: 1px solid #eee;
}

.question-row {
  cursor: pointer;
}

.question-row:hover {
  background-color: #f9f9f9;
}

.title-col {
  width: 40%;
}

.author-col {
  width: 20%;
}

.status-col {
  width: 15%;
}

.date-col {
  width: 25%;
}

.question-title {
  font-weight: 500;
  color: #2c3e50;
  margin-bottom: 5px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.reply-count {
  font-size: 12px;
  color: #888;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
  display: inline-block;
}

.status-pending {
  background-color: #ffd700;
  color: #000;
}

.status-answered {
  background-color: #4CAF50;
  color: white;
}

/* 问题详情弹窗 */
.question-detail-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: #fff;
  border-radius: 8px;
  width: 80%;
  max-width: 1000px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
}

close-btn:hover {
  color: #333;
}

/* 主题详情样式 - 论坛风格 */
.topic-container {
  padding: 0;
}

.post {
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.post-header {
  margin-bottom: 15px;
}

.post-title {
  margin: 0 0 10px 0;
  font-size: 20px;
}

.post-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
  font-size: 12px;
  color: #666;
}

.author {
  font-weight: bold;
  color: #333;
}

.author.teacher {
  color: #4CAF50;
}

.author.student {
  color: #2196F3;
}

.post-time {
  color: #888;
}

.status-label {
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.post-content {
  line-height: 1.6;
  font-size: 16px;
  white-space: pre-line;
}

.replies {
  border-top: 1px solid #ddd;
}

.reply {
  padding: 15px 20px;
  background-color: white;
}

.reply:nth-child(odd) {
  background-color: #f9f9f9;
}

.reply-form {
  padding: 20px;
  border-top: 1px solid #ddd;
  background-color: white;
}

.reply-title {
  font-size: 18px;
  margin-bottom: 15px;
  color: #333;
}

.reply-form textarea {
  width: 100%;
  min-height: 100px;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  font-family: inherit;
  margin-bottom: 15px;
  box-sizing: border-box;
  resize: vertical;
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

/* 删除回复按钮样式 */
.delete-reply-btn {
  background-color: transparent;
  border: none;
  color: #f44336;
  cursor: pointer;
  padding: 3px 8px;
  font-size: 12px;
  border-radius: 4px;
  transition: all 0.3s;
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 5px;
}

.delete-reply-btn:hover {
  background-color: rgba(244, 67, 54, 0.1);
}

.teacher-badge {
  background-color: #4CAF50;
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
  margin-right: 8px;
}
</style>