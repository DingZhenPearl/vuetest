<template>
  <div class="login-container">
    <div class="title-container">
      <img src="@/assets/logo.png" alt="logo" class="logo">
      <h1 class="system-title">教育管理系统</h1>
    </div>
    <div class="login-form">
      <h2>{{ showRegisterForm ? '用户注册' : '用户登录' }}</h2>
      <div v-if="error" class="error-message">
        {{ error }}
      </div>
      
      <!-- 登录表单 -->
      <div v-if="!showRegisterForm">
        <div class="form-group">
          <label>用户名</label>
          <input type="text" v-model="username" placeholder="请输入用户名">
        </div>
        <div class="form-group">
          <label>密码</label>
          <input type="password" v-model="password" placeholder="请输入密码">
        </div>
        <div class="form-group role-select">
          <label>身份</label>
          <div class="role-buttons">
            <button 
              :class="['role-btn', { active: role === 'teacher' }]" 
              @click="role = 'teacher'">老师</button>
            <button 
              :class="['role-btn', { active: role === 'student' }]" 
              @click="role = 'student'">学生</button>
          </div>
        </div>
        <button class="login-btn" @click="login" :disabled="isLoading">
          {{ isLoading ? '登录中...' : '登录' }}
        </button>
      </div>
      
      <!-- 注册表单 -->
      <div v-if="showRegisterForm">
        <div class="form-group">
          <label>用户名</label>
          <input type="text" v-model="registerUsername" placeholder="请输入用户名">
        </div>
        <div class="form-group">
          <label>密码</label>
          <input type="password" v-model="registerPassword" placeholder="请输入密码">
        </div>
        <div class="form-group">
          <label>确认密码</label>
          <input type="password" v-model="confirmPassword" placeholder="请再次输入密码">
        </div>
        <div class="form-group role-select">
          <label>身份</label>
          <div class="role-buttons">
            <button 
              :class="['role-btn', { active: registerRole === 'teacher' }]" 
              @click="registerRole = 'teacher'">老师</button>
            <button 
              :class="['role-btn', { active: registerRole === 'student' }]" 
              @click="registerRole = 'student'">学生</button>
          </div>
        </div>
        <button class="login-btn" @click="register" :disabled="isRegistering">
          {{ isRegistering ? '注册中...' : '注册' }}
        </button>
      </div>
      
      <div class="toggle-form">
        <a href="#" @click.prevent="toggleForm">
          {{ showRegisterForm ? '已有账号？立即登录' : '没有账号？立即注册' }}
        </a>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'logIn',
  data() {
    return {
      username: '',
      password: '',
      role: 'student',
      error: '',
      isLoading: false,
      
      // 注册相关数据
      showRegisterForm: false,
      registerUsername: '',
      registerPassword: '',
      confirmPassword: '',
      registerRole: 'student',
      isRegistering: false
    }
  },
  methods: {
    toggleForm() {
      this.showRegisterForm = !this.showRegisterForm;
      this.error = ''; // 切换表单时清空错误信息
    },
    
    async login() {
      // 验证输入
      if (!this.username.trim()) {
        this.error = '请输入用户名';
        return;
      }
      if (!this.password.trim()) {
        this.error = '请输入密码';
        return;
      }
      
      this.isLoading = true;
      this.error = '';
      
      try {
        // 调用登录API
        const response = await fetch('/api/auth/login', { // 更新API路径
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            user_type: this.role,
            email: this.username,
            password: this.password
          })
        });
        
        const data = await response.json();
        
        if (response.ok) {
          // 登录成功，处理登录成功后的逻辑
          this.handleLoginSuccess();
        } else {
          this.error = data.message || '登录失败，请检查账号和密码';
        }
      } catch (error) {
        console.error('登录错误:', error);
        this.error = '服务器连接错误，请稍后重试';
      } finally {
        this.isLoading = false;
      }
    },
    
    async register() {
      // 验证输入
      if (!this.registerUsername.trim()) {
        this.error = '请输入用户名';
        return;
      }
      if (!this.registerPassword.trim()) {
        this.error = '请输入密码';
        return;
      }
      if (this.registerPassword !== this.confirmPassword) {
        this.error = '两次输入的密码不一致';
        return;
      }
      
      this.isRegistering = true;
      this.error = '';
      
      try {
        // 调用注册API
        const response = await fetch('/api/auth/register', { // 更新API路径
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            user_type: this.registerRole,
            email: this.registerUsername,
            password: this.registerPassword
          })
        });
        
        const data = await response.json();
        
        if (response.ok) {
          // 注册成功，显示成功消息并切换到登录表单
          alert('注册成功！请登录您的账号');
          this.showRegisterForm = false;
          this.username = this.registerUsername;
          this.password = '';
        } else {
          this.error = data.message || '注册失败，请稍后重试';
        }
      } catch (error) {
        console.error('注册错误:', error);
        this.error = '服务器连接错误，请稍后重试';
      } finally {
        this.isRegistering = false;
      }
    },

    // 登录成功后的处理
    handleLoginSuccess() {
      // 先清除可能存在的旧数据
      sessionStorage.clear();
      
      // 使用 sessionStorage 保存新用户信息
      sessionStorage.setItem('userRole', this.role);
      sessionStorage.setItem('username', this.username);
      sessionStorage.setItem('userEmail', this.username);
      
      // 生成用户标识符
      const uid = btoa(this.username).replace(/=/g, '').replace(/\+/g, '-').replace(/\//g, '_');
      sessionStorage.setItem('userIdentifier', uid);
      
      this.$router.push({
        path: `/${this.role}/home`,
        query: { role: this.role, uid: uid }
      });
    }
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 20px;
}

.title-container {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 2rem;
}

.logo {
  width: 60px;
  height: 60px;
  margin-right: 1rem;
  filter: drop-shadow(0 4px 6px rgba(0, 0, 0, 0.1));
}

.system-title {
  color: #2c3e50;
  font-size: 2.2rem;
  font-weight: 600;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.login-form {
  background: white;
  padding: 35px 40px;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  width: 380px;
  max-width: 90%;
  position: relative;
  overflow: hidden;
}

.login-form::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 5px;
  background: linear-gradient(90deg, #3498db, #2980b9, #1abc9c);
}

.login-form h2 {
  color: #2c3e50;
  margin-bottom: 1.5rem;
  font-weight: 600;
  text-align: center;
  font-size: 1.8rem;
}

.form-group {
  margin-bottom: 22px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #34495e;
  font-size: 0.95rem;
}

.form-group input {
  width: 100%;
  padding: 12px 15px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.3s ease;
  background-color: #f9f9f9;
}

.form-group input:focus {
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
  background-color: white;
  outline: none;
}

.role-buttons {
  display: flex;
  gap: 12px;
}

.role-btn {
  flex: 1;
  padding: 12px;
  background-color: #f5f7fa;
  border: 1px solid #e0e0e0;
  cursor: pointer;
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s ease;
  color: #555;
}

.role-btn:hover {
  background-color: #edf2f7;
}

.role-btn.active {
  background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
  color: white;
  border-color: #2980b9;
  box-shadow: 0 4px 10px rgba(52, 152, 219, 0.3);
}

.login-btn {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  transition: all 0.3s ease;
  margin-top: 10px;
  box-shadow: 0 4px 10px rgba(52, 152, 219, 0.3);
}

.login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(52, 152, 219, 0.4);
}

.login-btn:disabled {
  background: linear-gradient(135deg, rgba(52, 152, 219, 0.5) 0%, rgba(41, 128, 185, 0.5) 100%);
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.toggle-form {
  margin-top: 20px;
  text-align: center;
}

.toggle-form a {
  color: #3498db;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.3s ease;
}

.toggle-form a:hover {
  color: #2980b9;
  text-decoration: underline;
}

.error-message {
  background-color: #fff5f5;
  color: #e53e3e;
  padding: 12px 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  font-size: 0.9rem;
  border-left: 4px solid #e53e3e;
}

.register-form {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}
</style>