<template>
  <div class="sidebar">
    <h2 id="userEmail">{{ userEmail || '加载中...' }}</h2>
    <el-menu class="sidebar-menu">
      <el-menu-item index="1" @click="navigateTo('/teacher/home')">
        <span>首页</span>
      </el-menu-item>
      <el-menu-item index="2" @click="navigateTo('/teacher/class')">
        <span>学员管理</span>
      </el-menu-item>
      <el-menu-item index="3" @click="navigateTo('/teacher/grades')">
        <span>成绩统计管理</span>
      </el-menu-item>
      <el-menu-item index="4" @click="showAlert('权限管理')">
        <span>权限管理</span>
      </el-menu-item>
      <el-menu-item index="5" @click="showAlert('系统设置')">
        <span>系统设置</span>
      </el-menu-item>
      <el-menu-item index="6" @click="navigateTo('/teacher/analysis')">
        <span>学生学习行为分析</span>
      </el-menu-item>
      <el-menu-item index="7" @click="navigateTo('/teacher/answer')">
        <span>学生提问管理</span>
      </el-menu-item>
      <el-menu-item index="8" @click="navigateTo('/teacher/python')">
        <span>教学数据管理</span>
      </el-menu-item>
      <el-menu-item index="9" @click="showAlert('数据分析可视化')">
        <span>数据分析可视化</span>
      </el-menu-item>
      <el-menu-item index="10" @click="showAlert('教学反馈报告')">
        <span>教学反馈报告</span>
      </el-menu-item>
      <el-menu-item index="11" @click="logout">
        <span>退出登录</span>
      </el-menu-item>
    </el-menu>
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
    },
    navigateTo(path) {
      // 在导航链接中添加角色参数
      this.$router.push({ 
        path, 
        query: { role: 'teacher' }
      });
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

/* 仅保留悬停效果，移除 router-link-active 和 active 类的样式 */
.sidebar a:hover {
  background-color: #34495e;
}
</style>