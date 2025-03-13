<template>
  <div class="student-page">
    <!-- 导航侧边栏 -->
    <StudentNavbar />

    <!-- 主内容区 -->
    <div class="main-content">
      <div class="student-home">
        <h1>学生主页</h1>
        
        <!-- 加载状态 -->
        <div v-if="isLoading" class="loading-info">
          <div class="loading-spinner"></div>
          <p>正在加载个人信息...</p>
        </div>
        
        <!-- 个人信息提示卡片 -->
        <div v-if="!isLoading && !hasProfileInfo" class="profile-reminder">
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
      hasProfileInfo: false,
      isLoading: true
    }
  },
  created() {
    // 检查用户是否已设置个人信息
    this.checkProfileInfo();
    
    // 检查用户登录状态
    const username = sessionStorage.getItem('username');
    if (!username) {
      this.$router.push('/logIn');
    }
  },
  methods: {
    async checkProfileInfo() {
      this.isLoading = true;
      
      // 先检查sessionStorage
      const profile = JSON.parse(sessionStorage.getItem('userProfile') || '{}')
      if (profile.studentId && profile.className) {
        this.hasProfileInfo = true;
        this.isLoading = false;
        return;
      }
      
      // 如果sessionStorage没有数据，尝试从服务器获取
      const userEmail = sessionStorage.getItem('userEmail')
      if (!userEmail) {
        this.hasProfileInfo = false;
        this.isLoading = false;
        return;
      }
      
      try {
        const response = await fetch(`/api/profile/${userEmail}`);
        const data = await response.json();
        
        if (data.success && data.profile && data.profile.student_id && data.profile.class_name) {
          // 服务器有数据，保存到sessionStorage
          const profileData = {
            studentId: data.profile.student_id || '',
            className: data.profile.class_name || '',
            major: data.profile.major || '',
            name: data.profile.name || ''
          };
          
          sessionStorage.setItem('userProfile', JSON.stringify(profileData));
          this.hasProfileInfo = true;
        } else {
          this.hasProfileInfo = false;
        }
      } catch (error) {
        console.error('获取用户信息失败:', error);
        this.hasProfileInfo = false;
      }
      
      this.isLoading = false;
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

/* 加载状态样式 */
.loading-info {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  padding: 20px;
  margin-bottom: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.loading-spinner {
  border: 3px solid #f3f3f3;
  border-top: 3px solid #4CAF50;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  animation: spin 1s linear infinite;
  margin-bottom: 10px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
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