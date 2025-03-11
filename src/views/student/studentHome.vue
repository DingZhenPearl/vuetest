<template>
  <div class="student-page">
    <!-- 导航侧边栏 -->
    <StudentNavbar />

    <!-- 主内容区 -->
    <div class="main-content">
      <div class="student-home">
        <h1>学生主页</h1>
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
  methods: {
    goToExams() {
      this.$router.push('/student/exams')
    },
    goToHomework() {
      this.$router.push('/student/homework')
    },
    goToGrades() {
      this.$router.push('/student/grades')
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
  gap: 20px;
  margin-top: 20px;
}

.card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 15px;
  width: 200px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
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
</style>