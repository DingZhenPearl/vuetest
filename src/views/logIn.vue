<template>
    <div class="login-container">
      <h1>教育管理系统</h1>
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
        // 使用 sessionStorage 替代 localStorage
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
    height: 100vh;
    background-color: #e0e7ff;
  }
  
  .login-form {
    background: white;
    padding: 30px;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    width: 350px;
  }
  
  .form-group {
    margin-bottom: 20px;
  }
  
  .form-group label {
    display: block;
    margin-bottom: 5px;
    font-weight: bold;
  }
  
  .form-group input {
    width: 100%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
  }
  
  .role-buttons {
    display: flex;
    gap: 10px;
  }
  
  .role-btn {
    flex: 1;
    padding: 10px;
    background-color: #f0f0f0;
    border: 1px solid #ddd;
    cursor: pointer;
    border-radius: 4px;
  }
  
  .role-btn.active {
    background-color: #42b983;
    color: white;
    border-color: #42b983;
  }
  
  .login-btn {
    width: 100%;
    padding: 12px;
    background-color: #42b983;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 16px;
  }
  
  .login-btn:disabled {
    background-color: #a8d5c2;
    cursor: not-allowed;
  }
  
  .toggle-form {
    margin-top: 15px;
    text-align: center;
  }
  
  .toggle-form a {
    color: #42b983;
    text-decoration: none;
  }
  
  .toggle-form a:hover {
    text-decoration: underline;
  }
  
  .error-message {
    background-color: #ffebee;
    color: #c62828;
    padding: 10px;
    border-radius: 4px;
    margin-bottom: 15px;
    font-size: 14px;
  }
  
  .register-form {
    margin-top: 20px;
    padding-top: 20px;
    border-top: 1px solid #eee;
  }
  </style>