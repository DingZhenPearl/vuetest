<template>
  <div class="profile-page">
    <!-- 导航侧边栏 -->
    <TeacherNavbar />

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
            <label for="teacherId">教师工号</label>
            <input type="text" id="teacherId" v-model="profile.teacherId" placeholder="请输入您的教师工号" required>
          </div>
          
          <div class="form-group">
            <label for="department">所属院系</label>
            <input type="text" id="department" v-model="profile.department" placeholder="请输入您的所属院系" required>
          </div>
          
          <div class="form-group">
            <label for="title">职称</label>
            <select id="title" v-model="profile.title" required>
              <option value="">请选择职称</option>
              <option value="助教">助教</option>
              <option value="讲师">讲师</option>
              <option value="副教授">副教授</option>
              <option value="教授">教授</option>
              <option value="其他">其他</option>
            </select>
          </div>
          
          <div class="form-group">
            <label for="name">姓名</label>
            <input type="text" id="name" v-model="profile.name" placeholder="请输入您的姓名" required>
          </div>
          
          <div class="form-group">
            <label for="phone">联系电话</label>
            <input type="tel" id="phone" v-model="profile.phone" placeholder="请输入您的联系电话">
          </div>
          
          <div class="form-group">
            <label for="officeLocation">办公地点</label>
            <input type="text" id="officeLocation" v-model="profile.officeLocation" placeholder="请输入您的办公地点">
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
import TeacherNavbar from '@/components/teacher/TeacherNavbar.vue'

export default {
  name: 'TeacherProfile',
  components: {
    TeacherNavbar
  },
  data() {
    return {
      profile: {
        email: '',
        teacherId: '',
        department: '',
        title: '',
        name: '',
        phone: '',
        officeLocation: ''
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
        // 从服务器获取个人信息，指定角色为teacher
        const response = await fetch(`/api/profile/${userEmail}?role=teacher`)
        const data = await response.json()
        
        if (data.success && data.profile) {
          // 服务器有数据，使用服务器数据
          this.profile.teacherId = data.profile.teacher_id || ''
          this.profile.department = data.profile.department || ''
          this.profile.title = data.profile.title || ''
          this.profile.name = data.profile.name || ''
          this.profile.phone = data.profile.phone || ''
          this.profile.officeLocation = data.profile.office_location || ''
          
          // 更新会话存储
          sessionStorage.setItem('userProfile', JSON.stringify({
            teacherId: this.profile.teacherId,
            department: this.profile.department,
            title: this.profile.title,
            name: this.profile.name
          }))
        } else {
          // 服务器无数据，清空表单
          this.profile.teacherId = ''
          this.profile.department = ''
          this.profile.title = ''
          this.profile.name = ''
          this.profile.phone = ''
          this.profile.officeLocation = ''
          // 清除可能存在的旧缓存
          sessionStorage.removeItem('userProfile')
        }
      } catch (error) {
        console.error('加载个人信息失败:', error)
        
        // 仅在服务器请求失败时才尝试使用会话存储中的备份数据
        const savedProfile = JSON.parse(sessionStorage.getItem('userProfile') || '{}')
        this.profile.teacherId = savedProfile.teacherId || ''
        this.profile.department = savedProfile.department || ''
        this.profile.title = savedProfile.title || ''
        this.profile.name = savedProfile.name || ''
        this.profile.phone = savedProfile.phone || ''
        this.profile.officeLocation = savedProfile.officeLocation || ''
      } finally {
        this.isLoading = false
      }
    },
    
    async saveProfile() {
      this.isSaving = true
      this.message = ''
      
      try {
        // 保存到服务器
        const response = await fetch('/api/profile/teacher/save', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            email: this.profile.email,
            teacherId: this.profile.teacherId,
            department: this.profile.department,
            title: this.profile.title,
            name: this.profile.name,
            phone: this.profile.phone,
            officeLocation: this.profile.officeLocation
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
            teacherId: this.profile.teacherId,
            department: this.profile.department,
            title: this.profile.title,
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
  border-radius: 50%;
  border-top: 4px solid #3498db;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.message {
  padding: 12px 15px;
  margin-bottom: 20px;
  border-radius: 4px;
  font-size: 14px;
}

.success {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.error {
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

label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #2c3e50;
}

input, select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.3s;
}

input:focus, select:focus {
  border-color: #3498db;
  outline: none;
}

input:disabled {
  background-color: #f9f9f9;
  cursor: not-allowed;
}

.hint {
  display: block;
  margin-top: 5px;
  font-size: 12px;
  color: #7f8c8d;
}

.save-btn {
  background-color: #3498db;
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
  margin-top: 10px;
  align-self: flex-start;
}

.save-btn:hover {
  background-color: #2980b9;
}

.save-btn:disabled {
  background-color: #95a5a6;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .main-content {
    margin-left: 0;
    width: 100%;
    padding: 15px;
  }
  
  .profile-container {
    padding: 20px;
  }
  
  .save-btn {
    width: 100%;
  }
}
</style>
