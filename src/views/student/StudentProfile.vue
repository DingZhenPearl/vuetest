<template>
  <div class="profile-page">
    <!-- 导航侧边栏 -->
    <StudentNavbar />

    <!-- 主内容区 -->
    <div class="main-content">
      <div class="profile-container">
        <h1>个人信息设置</h1>
        
        <!-- 加载状态 -->
        <div v-if="isLoading" class="loading">
          <div class="loading-spinner"></div>
          <p>加载中，请稍候...</p>
        </div>
        
        <!-- 提示信息 -->
        <div v-if="message" :class="['message', messageType]">
          {{ message }}
        </div>

        <!-- 个人信息表单 -->
        <form class="profile-form" @submit.prevent="saveProfile" v-if="!isLoading">
          <div class="form-group">
            <label for="email">电子邮箱</label>
            <input type="email" id="email" v-model="profile.email" disabled>
            <span class="hint">邮箱作为登录账号不可更改</span>
          </div>
          
          <div class="form-group">
            <label for="studentId">学号</label>
            <input type="text" id="studentId" v-model="profile.studentId" placeholder="请输入您的学号" required>
          </div>
          
          <div class="form-group">
            <label for="className">班级</label>
            <input type="text" id="className" v-model="profile.className" placeholder="请输入您的班级" required>
          </div>
          
          <div class="form-group">
            <label for="major">专业</label>
            <input type="text" id="major" v-model="profile.major" placeholder="请输入您的专业">
          </div>
          
          <div class="form-group">
            <label for="name">姓名</label>
            <input type="text" id="name" v-model="profile.name" placeholder="请输入您的姓名">
          </div>
          
          <button type="submit" class="save-btn" :disabled="isSaving">
            {{ isSaving ? '保存中...' : '保存设置' }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import StudentNavbar from '@/components/student/StudentNavbar.vue'

export default {
  name: 'StudentProfile',
  components: {
    StudentNavbar
  },
  data() {
    return {
      profile: {
        email: '',
        studentId: '',
        className: '',
        major: '',
        name: ''
      },
      isLoading: false,
      isSaving: false,
      message: '',
      messageType: 'success'
    }
  },
  created() {
    this.loadUserProfile()
  },
  methods: {
    async loadUserProfile() {
      // 从会话存储加载用户邮箱
      const userEmail = sessionStorage.getItem('userEmail') || ''
      if (!userEmail) {
        this.$router.push('/logIn')
        return
      }
      
      this.profile.email = userEmail
      this.isLoading = true
      
      try {
        // 先尝试从服务器获取个人信息
        const response = await fetch(`/api/profile/${userEmail}`)
        const data = await response.json()
        
        if (data.success && data.profile) {
          // 服务器有数据，使用服务器数据
          this.profile.studentId = data.profile.student_id || ''
          this.profile.className = data.profile.class_name || ''
          this.profile.major = data.profile.major || ''
          this.profile.name = data.profile.name || ''
          
          // 同步到会话存储
          sessionStorage.setItem('userProfile', JSON.stringify({
            studentId: this.profile.studentId,
            className: this.profile.className,
            major: this.profile.major,
            name: this.profile.name
          }))
        } else {
          // 服务器无数据，尝试从会话存储获取
          const savedProfile = JSON.parse(sessionStorage.getItem('userProfile') || '{}')
          
          this.profile.studentId = savedProfile.studentId || ''
          this.profile.className = savedProfile.className || ''
          this.profile.major = savedProfile.major || ''
          this.profile.name = savedProfile.name || ''
        }
      } catch (error) {
        console.error('加载个人信息失败:', error)
        
        // 从会话存储加载
        const savedProfile = JSON.parse(sessionStorage.getItem('userProfile') || '{}')
        this.profile.studentId = savedProfile.studentId || ''
        this.profile.className = savedProfile.className || ''
        this.profile.major = savedProfile.major || ''
        this.profile.name = savedProfile.name || ''
      } finally {
        this.isLoading = false
      }
    },
    
    async saveProfile() {
      this.isSaving = true
      this.message = ''
      
      try {
        // 保存到服务器
        const response = await fetch('/api/profile/save', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            email: this.profile.email,
            studentId: this.profile.studentId,
            className: this.profile.className,
            major: this.profile.major,
            name: this.profile.name
          })
        })
        
        // 检查响应状态码
        if (!response.ok) {
          throw new Error(`服务器响应错误: ${response.status} ${response.statusText}`);
        }
        
        // 尝试解析响应内容
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
          throw new Error('服务器返回格式错误，预期为JSON格式');
        }
        
        const data = await response.json();
        
        if (data.success) {
          // 同时保存到会话存储
          sessionStorage.setItem('userProfile', JSON.stringify({
            studentId: this.profile.studentId,
            className: this.profile.className,
            major: this.profile.major,
            name: this.profile.name
          }))
          
          this.message = '个人信息保存成功！'
          this.messageType = 'success'
        } else {
          throw new Error(data.message || '服务器错误')
        }
      } catch (error) {
        console.error('保存个人信息失败:', error)
        this.message = `保存失败: ${error.message || '请检查网络连接'}`
        this.messageType = 'error'
        
        // 保存到会话存储作为备份
        sessionStorage.setItem('userProfile', JSON.stringify({
          studentId: this.profile.studentId,
          className: this.profile.className,
          major: this.profile.major,
          name: this.profile.name
        }))
      } finally {
        this.isSaving = false
        
        // 3秒后隐藏消息
        setTimeout(() => {
          this.message = ''
        }, 3000)
      }
    }
  }
}
</script>

<style scoped>
.profile-page {
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

.profile-container {
  max-width: 700px;
  margin: 0 auto;
  background-color: white;
  border-radius: 8px;
  padding: 30px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

h1 {
  color: #2c3e50;
  margin-bottom: 25px;
  font-size: 24px;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 0;
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

.message {
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 20px;
}

.message.success {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.message.error {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.profile-form {
  display: flex;
  flex-direction: column;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
  color: #2c3e50;
}

.form-group input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  box-sizing: border-box;
}

.form-group input:focus {
  border-color: #4CAF50;
  outline: none;
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.25);
}

.form-group input:disabled {
  background-color: #f8f8f8;
  cursor: not-allowed;
}

.hint {
  display: block;
  margin-top: 5px;
  font-size: 12px;
  color: #6c757d;
}

.save-btn {
  background-color: #4CAF50;
  color: white;
  padding: 12px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  align-self: flex-start;
  margin-top: 10px;
  transition: background-color 0.3s;
}

.save-btn:hover {
  background-color: #45a049;
}

.save-btn:disabled {
  background-color: #a5d6a7;
  cursor: not-allowed;
}
</style>