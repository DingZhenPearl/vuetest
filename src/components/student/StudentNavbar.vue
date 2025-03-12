<template>
  <div class="sidebar">
    <h2 id="userEmail">{{ userEmail || '加载中...' }}</h2>
    <a href="#" @click.prevent="goToHome">主页</a>
    <a href="#" @click.prevent="goToExams">习题集</a>
    <a href="#" @click.prevent="explainProgrammingConcepts">编程概念讲解</a>
    <a href="#" @click.prevent="caseAnalysis">实战案例分析</a>
    <a href="#" @click.prevent="goToQuestion">提问</a>
    <a href="#" @click.prevent="troubleshooting">疑难解答</a>
    <a href="#" @click.prevent="learningBehaviorAnalysis">学习行为分析</a>
    <a href="#" @click.prevent="goToAiChat">AI对话</a>
    <a href="#" @click.prevent="logout">退出登录</a>
  </div>
</template>

<script>
export default {
  name: 'StudentNavbar',
  data() {
    return {
      userEmail: ''
    }
  },
  created() {
    this.initializeUserData()
  },
  methods: {
    initializeUserData() {
      // 从localStorage获取用户邮箱
      this.userEmail = localStorage.getItem('userEmail') || '未登录'
    },
    goToHome() {
      this.$router.push('/student')
    },
    goToExams() {
      this.$router.push('/student/exams')
    },
    goToQuestion() {
      this.$router.push('/student/question')
    },
    goToAiChat() {
      this.$router.push('/student/aiChat')
    },
    explainProgrammingConcepts() {
      alert('编程概念讲解功能尚未实现')
    },
    caseAnalysis() {
      alert('实战案例分析功能尚未实现')
    },
    troubleshooting() {
      alert('疑难解答功能尚未实现')
    },
    learningBehaviorAnalysis() {
      alert('学习行为分析功能尚未实现')
    },
    logout() {
      localStorage.removeItem('userEmail')
      this.$router.push('/login')
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
  font-size: calc(0.7rem + 0.5vw); /* 动态适应字体大小 */
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap; /* 防止长邮箱地址换行 */
  padding: 0 5px; /* 添加一些内边距防止文字贴近边缘 */
  max-width: 100%; /* 确保不超过父容器宽度 */
  transition: font-size 0.3s; /* 平滑过渡效果 */
}

/* 为不同的屏幕宽度设置字体大小限制 */
@media screen and (max-width: 1200px) {
  .sidebar h2 {
    font-size: 0.85rem;
  }
}

@media screen and (max-width: 768px) {
  .sidebar h2 {
    font-size: 0.75rem;
  }
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

.sidebar a:hover {
  background-color: #34495e;
}
</style>