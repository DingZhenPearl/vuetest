<template>
  <div class="not-found">
    <div class="content">
      <h1>404</h1>
      <h2>页面未找到</h2>
      <p>抱歉，您请求的页面不存在或已被移除。</p>
      <button @click="goHome">返回首页</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NotFound',
  methods: {
    goHome() {
      // 从 sessionStorage 获取用户角色，而不是 localStorage
      const userRole = sessionStorage.getItem('userRole');
      if (userRole) {
        this.$router.push(`/${userRole}/home`);
      } else {
        this.$router.push('/logIn');
      }
    }
  }
}
</script>

<style scoped>
.not-found {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f5f5f5;
  text-align: center;
}

.content {
  max-width: 500px;
  padding: 40px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
}

h1 {
  font-size: 80px;
  margin: 0;
  color: #e74c3c;
}

h2 {
  margin-top: 0;
  color: #2c3e50;
}

p {
  color: #7f8c8d;
  margin-bottom: 30px;
}

button {
  background-color: #3498db;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}

button:hover {
  background-color: #2980b9;
}
</style>