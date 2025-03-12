<template>
  <div class="student-page">
    <!-- 导航侧边栏 -->
    <StudentNavbar />

    <!-- 主内容区 -->
    <div class="main-content">
      <div class="student-home">
        <h1>学生主页</h1>
        
        <!-- 个人信息提示卡片 -->
        <div v-if="!hasProfileInfo" class="profile-reminder">
          <div class="reminder-content">
            <h3>完善个人信息</h3>
            <p>请设置您的学号和班级等基本信息，以便更好地使用平台功能。</p>
            <button class="setup-profile-btn" @click="goToProfile">设置个人信息</button>
          </div>
        </div>
        
        <div class="student-content">
          <p>欢迎使用学生学习平台</p>
          <!-- 学生特有功能 -->
          <div class="feature-cards">
            <div class="card" @click="goToExams">
              <h3>我的课程</h3>
              <p>查看已选课程和课表</p>
            </div>
            <div class="card" @click="goToHomework">
              <h3>作业管理</h3>
              <p>查看和提交课程作业</p>
            </div>
            <div class="card" @click="goToGrades">
              <h3>成绩查询</h3>
              <p>查询各科目的学习成绩</p>
            </div>
            <div class="card" @click="goToProfile">
              <h3>个人信息</h3>
              <p>设置学号、班级等个人信息</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
  
<script>
import StudentNavbar from '@/components/student/StudentNavbar.vue'

export default {
  name: 'StudentHome',
  components: {
    StudentNavbar
  },
  data() {
    return {
      hasProfileInfo: false
    }
  },
  created() {
    // 检查用户是否已设置个人信息
    this.checkProfileInfo()
  },
  methods: {
    checkProfileInfo() {
      const profile = JSON.parse(localStorage.getItem('userProfile') || '{}')
      // 判断是否设置了学号和班级
      this.hasProfileInfo = !!(profile.studentId && profile.className)
    },
    goToExams() {
      this.$router.push('/student/exams')
    },
    goToHomework() {
      this.$router.push('/student/homework')
    },
    goToGrades() {
      this.$router.push('/student/grades')
    },
    goToProfile() {
      this.$router.push('/student/profile')
    }
  }
}
</script>
  
<style scoped>
/* 整体布局 */
.student-page {
  display: flex;
  min-height: 100vh;
  font-family: Arial, sans-serif;
  margin: 0;
  background-color: #f4f4f4;
}

/* 主内容区样式 */
.main-content {
  margin-left: 250px;
  flex: 1;
  padding: 20px;
}

/* 学生主页样式 */
.student-home {
  padding: 20px;
}

.student-content {
  margin-top: 20px;
}

.feature-cards {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-top: 20px;
}

.card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 15px;
  width: calc(50% - 20px);
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
  background-color: white;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

/* 个人信息提示卡片 */
.profile-reminder {
  background: linear-gradient(to right, #4CAF50, #8BC34A);
  border-radius: 8px;
  color: white;
  margin-bottom: 30px;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.reminder-content {
  padding: 20px;
}

.reminder-content h3 {
  margin-top: 0;
  font-size: 20px;
}

.setup-profile-btn {
  background-color: white;
  color: #4CAF50;
  border: none;
  border-radius: 4px;
  padding: 10px 20px;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s;
}

.setup-profile-btn:hover {
  background-color: #f5f5f5;
}

h1 {
  color: #2c3e50;
  margin-bottom: 20px;
}

p {
  color: #34495e;
  line-height: 1.6;
  font-size: 16px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .main-content {
    margin-left: 0;
    padding-top: 60px;
  }
  
  .card {
    width: 100%;
  }
}
</style>