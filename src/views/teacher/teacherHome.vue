<template>
    <div class="teacher-home">
      <h1>老师主页</h1>
      <div class="teacher-content">
        <p>欢迎使用教师管理系统</p>
        <!-- 教师特有功能 -->
        <div class="feature-cards">
          <div class="card">
            <h3>班级管理</h3>
            <p>管理您的班级和学生名单</p>
          </div>
          <div class="card">
            <h3>课程安排</h3>
            <p>查看和编辑您的课程表</p>
          </div>
          <div class="card">
            <h3>成绩录入</h3>
            <p>为学生录入和修改成绩</p>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'TeacherHome'
  }
  </script>
  
  <style scoped>
  .teacher-home {
    padding: 20px;
  }
  
  .teacher-content {
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