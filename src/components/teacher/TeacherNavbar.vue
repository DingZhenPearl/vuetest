<template>
  <div class="sidebar">
    <h2 id="userEmail">{{ userEmail || '加载中...' }}</h2>
    <router-link to="/teacher/home" active-class="active">主页</router-link>
    <router-link to="/teacher/class" active-class="active">学员管理</router-link>
    <router-link to="/teacher/grades" active-class="active">成绩统计管理</router-link>
    <router-link to="#" @click.prevent="showAlert('权限管理')">权限管理</router-link>
    <router-link to="#" @click.prevent="showAlert('系统设置')">系统设置</router-link>
    <router-link to="/teacher/analysis" active-class="active">学生学习行为分析</router-link>
    <router-link to="/teacher/answer" active-class="active">学生提问管理</router-link>
    <router-link to="/teacher/python" active-class="active">教学数据管理</router-link>
    <router-link to="#" @click.prevent="showAlert('数据分析可视化')">数据分析可视化</router-link>
    <router-link to="#" @click.prevent="showAlert('教学反馈报告')">教学反馈报告</router-link>
    <a @click="logout" href="#">退出登录</a>
  </div>
</template>

<script>
export default {
  name: 'TeacherNavbar',
  data() {
    return {
      userEmail: ''
    }
  },
  created() {
    // 从本地存储获取用户邮箱
    this.userEmail = localStorage.getItem('userEmail') || '未登录用户';
  },
  methods: {
    showAlert(featureName) {
      alert(`${featureName}功能正在开发中，敬请期待！`);
    },
    returnToMainPage() {
      this.$router.push('/teacher/home');
    },
    logout() {
      localStorage.removeItem('userEmail');
      localStorage.removeItem('username');
      localStorage.removeItem('userRole');
      this.$router.push('/logIn');
    }
  }
}
</script>

<style scoped>
.sidebar {
  width: 250px;
  background-color: #2c3e50;
  color: #ecf0f1;
  position: fixed;
  left: 0;
  top: 0;
  height: 100vh;
  padding: 20px;
  box-sizing: border-box;
  overflow-y: auto;
  z-index: 1000;
}

.sidebar h2 {
  text-align: center;
  margin-bottom: 20px;
  font-size: 1.2rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.sidebar a {
  color: #ecf0f1;
  text-decoration: none;
  padding: 10px 15px;
  margin-bottom: 10px;
  border-radius: 4px;
  display: block;
  transition: background-color 0.3s;
  cursor: pointer;
}

.sidebar a:hover, .sidebar a.router-link-active, .sidebar a.active {
  background-color: #34495e;
}
</style>