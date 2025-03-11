<template>
    <div class="login-container">
      <h1>教育管理系统</h1>
      <div class="login-form">
        <h2>用户登录</h2>
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
        <button class="login-btn" @click="login">登录</button>
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
        role: 'student'
      }
    },
    methods: {
      login() {
        // 验证输入
        if (!this.username.trim()) {
          alert('请输入用户名');
          return;
        }
        if (!this.password.trim()) {
          alert('请输入密码');
          return;
        }
        
        // 这里应该有实际的登录逻辑，比如API调用
        // 简化示例：根据选择的角色导航到不同页面
        localStorage.setItem('userRole', this.role);
        localStorage.setItem('username', this.username);
        // 模拟存储用户邮箱信息 (用于显示在导航栏)
        localStorage.setItem('userEmail', `${this.username}@example.com`);
        
        // 获取重定向URL，如果没有则使用默认路径
        const redirectPath = this.$route.query.redirect || `/${this.role}/home`;
        
        // 跳转到对应页面
        this.$router.push(redirectPath);
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
    background-color: #f5f5f5;
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
  </style>