<template>
  <div class="question-page">
    <!-- 导航侧边栏 -->
    <StudentNavbar />

    <!-- 主内容区 -->
    <div class="main-content">
      <h1>编程问题讨论区</h1>
      
      <!-- 问题提交表单，始终可见 -->
      <form class="question-form" @submit.prevent="submitQuestion" v-if="!showQuestionDetail">
        <input type="text" v-model="questionForm.title" placeholder="话题标题" required>
        <textarea v-model="questionForm.content" placeholder="详细描述你的问题或想法..." required></textarea>
        <button type="submit" class="submit-btn" :disabled="isSubmitting">发布主题</button>
      </form>

      <!-- 返回按钮，只在详情页显示 -->
      <button v-if="showQuestionDetail" @click="backToList" class="back-btn">
        <i class="fas fa-arrow-left"></i> 返回主题列表
      </button>

      <!-- 问题列表 -->
      <div class="questions-list" v-if="!showQuestionDetail">
        <div v-if="loading" class="loading">加载中...</div>
        <div v-else-if="questions.length === 0" class="empty-state">
          暂无主题，来发布第一个主题吧！
        </div>
        
        <div class="forum-list">
          <table class="forum-table">
            <thead>
              <tr>
                <th class="title-col">主题</th>
                <th class="status-col">状态</th>
                <th class="date-col">发布时间</th>
                <th class="actions-col">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="question in paginatedQuestions" :key="question.id" class="question-row">
                <td class="title-col">
                  <a href="#" @click.prevent="viewQuestionDetail(question)" class="question-link">
                    {{ question.title }}
                  </a>
                  <div class="reply-count">
                    {{ getReplyCount(question) }} 回复
                  </div>
                </td>
                <td class="status-col">
                  <span :class="['status-badge', question.status === 'pending' ? 'pending' : 'answered']">
                    {{ question.status === 'pending' ? '未回复' : '已回复' }}
                  </span>
                </td>
                <td class="date-col">{{ formatDate(question.created_at) }}</td>
                <td class="actions-col">
                  <div class="question-actions">
                    <!-- 移除了编辑按钮，只保留删除功能 -->
                    <button @click="deleteQuestion(question.id)" class="delete-btn">删除</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- 分页控件 -->
        <div class="pagination" v-if="questions.length > 0">
          <button 
            @click="changePage(currentPage - 1)" 
            :disabled="currentPage === 1" 
            class="page-btn"
          >
            上一页
          </button>
          <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
          <button 
            @click="changePage(currentPage + 1)" 
            :disabled="currentPage === totalPages" 
            class="page-btn"
          >
            下一页
          </button>
        </div>
      </div>

      <!-- 主题详情页 -->
      <div v-if="showQuestionDetail && currentQuestion" class="question-detail">
        <div class="topic-container">
          <!-- 主题内容 -->
          <div class="post main-post">
            <div class="post-header">
              <h2 class="post-title">{{ currentQuestion.title }}</h2>
              <div class="post-meta">
                <span class="author">我</span>
                <span class="post-time">{{ formatDate(currentQuestion.created_at) }}</span>
                <span :class="['status-label', currentQuestion.status === 'pending' ? 'pending' : 'answered']">
                  {{ currentQuestion.status === 'pending' ? '未回复' : '已回复' }}
                </span>
              </div>
            </div>
            <div class="post-content">
              {{ currentQuestion.content }}
            </div>
          </div>

          <!-- 回复列表 -->
          <div class="replies">
            <!-- 老师的回答作为第一条回复 -->
            <div v-if="currentQuestion.answer" class="post reply">
              <div class="post-header">
                <div class="post-meta">
                  <span class="author teacher">老师</span>
                  <span class="post-time">{{ formatDate(currentQuestion.answered_at) }}</span>
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
                    <span :class="['author', followUp.user === 'teacher' ? 'teacher' : '']">
                      {{ followUp.user === 'teacher' ? '老师' : '我' }}
                    </span>
                    <span class="post-time">{{ formatDate(followUp.time) }}</span>
                    <!-- 修改条件，确保删除按钮显示出来 -->
                    <button 
                      v-if="followUp.user === 'student'" 
                      @click="deleteFollowUp(currentQuestion.id, index)" 
                      class="delete-reply-btn">
                      <i class="fas fa-trash"></i> 删除
                    </button>
                  </div>
                </div>
                <div class="post-content">
                  {{ followUp.content }}
                </div>
              </div>
            </template>
          </div>

          <!-- 回复表单 -->
          <form class="reply-form" @submit.prevent="submitFollowUp(currentQuestion.id)">
            <h3 class="reply-title">回复</h3>
            <textarea v-model="followUpTexts[currentQuestion.id]" placeholder="添加回复..." required></textarea>
            <button type="submit" class="submit-btn" :disabled="isSubmittingFollowUp">发表回复</button>
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
      isEditMode: false, // 保留状态变量，以免影响其他逻辑
      currentEditId: null, // 保留状态变量，以免影响其他逻辑
      questionForm: {
        title: '',
        content: ''
      },
      followUpTexts: {},
      userEmail: '',
      showQuestionDetail: false,
      currentQuestion: null,
      // 分页相关
      currentPage: 1,
      pageSize: 10
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
  computed: {
    // 计算总页数
    totalPages() {
      return Math.ceil(this.questions.length / this.pageSize)
    },
    // 获取当前页的问题列表
    paginatedQuestions() {
      const start = (this.currentPage - 1) * this.pageSize
      const end = start + this.pageSize
      return this.questions.slice(start, end)
    }
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
    
    // 提交问题 - 保留，但不再支持编辑模式
    async submitQuestion() {
      if (!this.questionForm.title.trim() || !this.questionForm.content.trim()) {
        alert('请填写完整的主题信息')
        return
      }
      
      this.isSubmitting = true
      
      try {
        // 创建新主题 - 移除了编辑逻辑
        const response = await fetch('/api/questions/submit', {
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

        const data = await response.json()
        
        if (data.success) {
          this.resetForm()
          this.loadQuestions()
          alert('主题发布成功')
        } else {
          alert(data.message || '操作失败，请重试')
        }
      } catch (error) {
        console.error('发布主题出错:', error)
        alert('发布失败，请检查网络连接')
      } finally {
        this.isSubmitting = false
      }
    },
    
    // 删除问题
    async deleteQuestion(questionId) {
      if (!confirm('确定要删除这个主题吗？删除后不可恢复。')) {
        return
      }
      
      try {
        const response = await fetch(`/api/questions/${questionId}`, {
          method: 'DELETE'
        })
        const data = await response.json()
        
        if (data.success) {
          alert('主题删除成功')
          this.loadQuestions()
        } else {
          alert(data.message || '删除失败')
        }
      } catch (error) {
        console.error('删除主题出错:', error)
        alert('删除失败，请重试')
      }
    },
    
    // 重置表单 - 保留但简化
    resetForm() {
      this.questionForm.title = ''
      this.questionForm.content = ''
    },
    
    // 提交追问/回复
    async submitFollowUp(questionId) {
      const content = this.followUpTexts[questionId]?.trim()
      if (!content) return
      
      this.isSubmittingFollowUp = true
      
      try {
        const response = await fetch('/api/questions/follow-up', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ questionId, content })
        })
        
        if (response.ok) {
          this.followUpTexts[questionId] = ''
          await this.loadQuestions()
          
          // 更新当前问题
          if (this.currentQuestion && this.currentQuestion.id === questionId) {
            this.currentQuestion = this.questions.find(q => q.id === questionId)
          }
        } else {
          const error = await response.json()
          alert(error.message || '提交回复失败')
        }
      } catch (error) {
        console.error('提交回复出错:', error)
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
    
    // 获取回复数量
    getReplyCount(question) {
      let count = 0
      
      // 如果有老师回答，计数+1
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
    },

    // 查看问题详情
    viewQuestionDetail(question) {
      this.currentQuestion = question
      this.showQuestionDetail = true
      // 滚动到顶部
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      })
    },

    // 返回问题列表
    backToList() {
      this.showQuestionDetail = false
      this.currentQuestion = null
    },

    // 切换分页
    changePage(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.currentPage = page
      }
    },

    // 删除回复（追问）
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
          // 更新当前问题
          await this.loadQuestions()
          
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
    }
  }
}
</script>

<style scoped>
.question-page {
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

/* 表单样式 */
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

.back-btn {
  margin-bottom: 20px;
  padding: 10px 15px;
  background-color: #f1f1f1;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.back-btn:hover {
  background-color: #e0e0e0;
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

.question-row:hover {
  background-color: #f9f9f9;
}

.title-col {
  width: 45%;
}

.status-col {
  width: 15%;
}

.date-col {
  width: 25%;
}

.actions-col {
  width: 15%;
}

.question-link {
  color: #2c3e50;
  text-decoration: none;
  font-weight: 500;
  font-size: 16px;
  display: block;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.question-link:hover {
  color: #4CAF50;
}

.reply-count {
  font-size: 12px;
  color: #888;
  margin-top: 5px;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
  display: inline-block;
}

.status-badge.pending {
  background-color: #ffd700;
  color: #000;
}

.status-badge.answered {
  background-color: #4CAF50;
  color: white;
}

/* 分页控件 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 20px;
  gap: 15px;
}

.page-btn {
  padding: 8px 15px;
  border: 1px solid #ddd;
  background-color: white;
  border-radius: 4px;
  cursor: pointer;
}

.page-btn:disabled {
  background-color: #f9f9f9;
  color: #ccc;
  cursor: not-allowed;
}

.page-btn:hover:not(:disabled) {
  background-color: #f1f1f1;
}

.page-info {
  font-size: 14px;
  color: #666;
}

/* 主题详情样式 - 论坛风格 */
.topic-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  overflow: hidden;
}

.post {
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.post:last-child {
  border-bottom: none;
}

.main-post {
  background-color: #f9f9f9;
}

.post-header {
  margin-bottom: 15px;
}

.post-title {
  margin: 0 0 10px 0;
  font-size: 24px;
}

.post-meta {
  display: flex;
  align-items: center;
  gap: 15px;
  color: #666;
  font-size: 14px;
  width: 100%;
}

.author {
  font-weight: bold;
  color: #333;
}

.author.teacher {
  color: #4CAF50;
}

.post-time {
  color: #888;
}

.status-label {
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.status-label.pending {
  background-color: #ffd700;
  color: #000;
}

.status-label.answered {
  background-color: #4CAF50;
  color: white;
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

/* 移除编辑按钮相关样式 */
.question-actions {
  display: flex;
  justify-content: flex-end;
}

.delete-btn {
  padding: 5px 10px;
  border-radius: 4px;
  cursor: pointer;
  border: none;
  background-color: #f44336;
  color: white;
}

.delete-btn:hover {
  background-color: #da190b;
}

.loading, .empty-state {
  text-align: center;
  padding: 30px;
  color: #666;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* 删除回复按钮样式调整 */
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
</style>