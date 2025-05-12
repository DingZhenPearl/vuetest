<template>
  <div class="teacher-home-container">
    <TeacherNavbar />
    <div class="teacher-home">
      <h1>教师主页</h1>
      <div class="teacher-content">
        <p>欢迎使用教师管理系统</p>

        <!-- 顶部统计数据 -->
        <div class="top-stats">
          <div class="stat-card">
            <h3>总学员人数</h3>
            <p>{{ stats.totalStudents }}</p>
          </div>
          <div class="stat-card">
            <h3>总访问人数</h3>
            <p>{{ stats.totalVisits }}</p>
          </div>
          <div class="stat-card">
            <h3>总登录人数</h3>
            <p>{{ stats.totalLogins }}</p>
          </div>
          <div class="stat-card">
            <h3>总岗位数</h3>
            <p>{{ stats.totalPositions }}</p>
          </div>
        </div>

        <!-- 图表展示区 -->
        <div class="chart-container">
          <h3>学员行为统计图</h3>
          <canvas ref="chartCanvas"></canvas>
        </div>

        <!-- 教师特有功能 -->
        <div class="feature-cards">
          <div class="card" v-for="(feature, index) in features" :key="index" @click="navigateTo(feature.route)">
            <h3>{{ feature.title }}</h3>
            <p>{{ feature.description }}</p>
          </div>
        </div>

        <!-- 底部统计数据 -->
        <div class="bottom-stats">
          <div class="bottom-card">
            <h3>当前学员统计</h3>
            <p>{{ stats.currentStudents }}</p>
          </div>
          <div class="bottom-card">
            <h3>附件统计</h3>
            <p>{{ stats.attachments }}</p>
          </div>
          <div class="bottom-card">
            <h3>岗位统计</h3>
            <p>{{ stats.positions }}</p>
          </div>
          <div class="bottom-card">
            <h3>登录统计</h3>
            <p>{{ stats.logins }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Chart from 'chart.js/auto';
import TeacherNavbar from '@/components/teacher/TeacherNavbar.vue';

export default {
  name: 'TeacherHome',
  components: {
    TeacherNavbar
  },
  data() {
    return {
      chart: null,
      stats: {
        totalStudents: 25482,
        totalVisits: 19484,
        totalLogins: 25481,
        totalPositions: 2584,
        currentStudents: 1254,
        attachments: 1054,
        positions: 1254,
        logins: 2564
      },
      features: [
        {
          title: '学生提问',
          description: '查看和回复学生的提问',
          route: '/teacher/answer'
        },
        {
          title: '数据管理',
          description: '管理教学相关数据',
          route: '/teacher/python'
        },
        {
          title: '出题管理',
          description: '创建和管理编程题目',
          route: '/teacher/problems'
        },
        {
          title: '教学分析',
          description: '查看教学数据分析',
          route: '/teacher/teaching-analysis'
        }
      ]
    }
  },
  mounted() {
    this.initChart();
  },
  beforeUnmount() {
    if (this.chart) {
      this.chart.destroy();
    }
  },
  methods: {
    initChart() {
      const ctx = this.$refs.chartCanvas.getContext('2d');
      this.chart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: ['6:37', '11:16:44', '11:16:49', '11:17:00', '11:17:08'],
          datasets: [{
            label: '实时在线人数',
            data: [430, 458, 125, 80, 32],
            borderColor: '#007bff',
            borderWidth: 2,
            fill: true,
            backgroundColor: 'rgba(0, 123, 255, 0.1)'
          }]
        },
        options: {
          responsive: true,
          plugins: {
            legend: {
              display: true,
            }
          }
        }
      });
    },
    navigateTo(route) {
      this.$router.push(route);
    }
  }
}
</script>

<style scoped>
.teacher-home-container {
  display: flex;
}

.teacher-home {
  padding: 20px;
  background-color: #f4f4f4;
  min-height: 100vh;
  margin-left: 250px; /* 与侧边栏宽度相同 */
  width: calc(100% - 250px);
  box-sizing: border-box;
}

.teacher-content {
  margin-top: 20px;
}

.top-stats {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.stat-card {
  flex: 1;
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.stat-card h3 {
  margin-bottom: 10px;
  color: #2c3e50;
}

.chart-container {
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.feature-cards {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin: 20px 0;
}

.card {
  background-color: #fff;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 15px;
  width: calc(25% - 15px);
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  cursor: pointer;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

.bottom-stats {
  display: flex;
  gap: 20px;
}

.bottom-card {
  flex: 1;
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  text-align: center;
}

@media (max-width: 768px) {
  .teacher-home {
    margin-left: 0;
    width: 100%;
  }

  .top-stats, .bottom-stats {
    flex-direction: column;
  }

  .card {
    width: 100%;
  }
}
</style>