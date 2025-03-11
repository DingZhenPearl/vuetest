<template>
    <div class="student-home">
      <h1>学生主页</h1>
      <div class="student-content">
        <p>欢迎使用学生学习平台</p>
        <!-- 学生特有功能 -->
        <div class="feature-cards">
          <div class="card">
            <h3>我的课程</h3>
            <p>查看已选课程和课表</p>
          </div>
          <div class="card">
            <h3>作业管理</h3>
            <p>查看和提交课程作业</p>
          </div>
          <div class="card">
            <h3>成绩查询</h3>
            <p>查询各科目的学习成绩</p>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'StudentHome'
  }
  </script>
  
  <style scoped>
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
  }
  </style>