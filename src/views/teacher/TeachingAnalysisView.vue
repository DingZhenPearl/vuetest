<template>
  <div class="page-container">
    <TeacherNavbar />
    <div class="content-container">
      <div class="teaching-analysis">
        <!-- 顶部统计卡片 -->
        <el-row :gutter="20" class="stats-cards">
          <el-col :span="6" v-for="stat in overallStats" :key="stat.title">
            <el-card shadow="hover" :body-style="{ padding: '20px' }">
              <div class="stat-card">
                <div class="stat-icon">
                  <i :class="stat.icon"></i>
                </div>
                <div class="stat-content">
                  <div class="stat-value">{{ stat.value }}</div>
                  <div class="stat-title">{{ stat.title }}</div>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <!-- 班级选择器 -->
        <div class="class-selector">
          <el-select v-model="selectedClass" placeholder="选择班级" @change="loadClassData">
            <el-option
              v-for="item in classList"
              :key="item"
              :label="item"
              :value="item">
            </el-option>
          </el-select>
        </div>

        <!-- 主要分析内容区域 -->
        <el-row :gutter="20" class="analysis-content">
          <!-- 左侧内容 -->
          <el-col :span="16">
            <!-- 学习趋势图 -->
            <el-card class="analysis-card">
              <template #header>
                <div class="card-header">
                  <span>学习趋势分析</span>
                  <el-radio-group v-model="trendTimeRange" size="small">
                    <el-radio-button label="week">周</el-radio-button>
                    <el-radio-button label="month">月</el-radio-button>
                  </el-radio-group>
                </div>
              </template>
              <div ref="trendChart" class="chart-container"></div>
            </el-card>

            <!-- 问题难度分布 -->
            <el-card class="analysis-card">
              <template #header>
                <div class="card-header">
                  <span>题目难度分布</span>
                </div>
              </template>
              <div ref="difficultyChart" class="chart-container"></div>
            </el-card>
          </el-col>

          <!-- 右侧内容 -->
          <el-col :span="8">
            <!-- 常见错误分析 -->
            <el-card class="analysis-card">
              <template #header>
                <div class="card-header">
                  <span>常见错误模式</span>
                </div>
              </template>
              <el-table :data="errorPatterns" style="width: 100%">
                <el-table-column prop="error_type" label="错误类型" width="180" />
                <el-table-column prop="occurrence_count" label="出现次数" width="100" />
                <el-table-column prop="affected_students" label="影响学生数" />
              </el-table>
            </el-card>

            <!-- 学习进度分布 -->
            <el-card class="analysis-card">
              <template #header>
                <div class="card-header">
                  <span>学习进度分布</span>
                </div>
              </template>
              <div ref="progressChart" class="chart-container"></div>
            </el-card>
          </el-col>
        </el-row>

        <!-- 学生表现详情 -->
        <el-card class="analysis-card">
          <template #header>
            <div class="card-header">
              <span>学生表现详情</span>
              <el-input
                v-model="search"
                placeholder="搜索学生"
                style="width: 200px"
              />
            </div>
          </template>
          <el-table
            :data="filteredStudentData"
            style="width: 100%"
            :default-sort="{ prop: 'completion_rate', order: 'descending' }">
            <el-table-column prop="student_id" label="学号" sortable />
            <el-table-column prop="completion_rate" label="完成率" sortable>
              <template #default="scope">
                <el-progress
                  :percentage="scope.row.completion_rate"
                  :color="getProgressColor(scope.row.completion_rate)"
                />
              </template>
            </el-table-column>
            <el-table-column prop="avg_score" label="平均分" sortable />
            <el-table-column prop="total_time" label="学习时长" sortable>
              <template #default="scope">
                {{ formatTime(scope.row.total_time) }}
              </template>
            </el-table-column>
            <el-table-column label="操作">
              <template #default="scope">
                <el-button
                  size="small"
                  @click="showStudentDetail(scope.row)"
                >详情</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script>
import TeacherNavbar from '@/components/teacher/TeacherNavbar.vue'
import axios from 'axios';
import * as echarts from 'echarts';

export default {
  name: 'TeachingAnalysisView',
  components: {
    TeacherNavbar
  },
  data() {
    return {
      selectedClass: '',
      classList: [],
      trendTimeRange: 'week',
      search: '',
      overallStats: [
        { title: '活跃学生数', value: 0, icon: 'el-icon-user' },
        { title: '平均完成率', value: '0%', icon: 'el-icon-data-line' },
        { title: '本周提交数', value: 0, icon: 'el-icon-document' },
        { title: '待解决问题', value: 0, icon: 'el-icon-warning' }
      ],
      errorPatterns: [],
      studentData: [],
      charts: {
        trend: null,
        difficulty: null,
        progress: null
      }
    };
  },
  computed: {
    filteredStudentData() {
      return this.studentData.filter(student =>
        student.student_id.toLowerCase().includes(this.search.toLowerCase())
      );
    }
  },
  methods: {
    async loadClassList() {
      try {
        const response = await axios.get('/api/teaching/class-list');
        this.classList = response.data.classes;
        if (this.classList.length > 0) {
          this.selectedClass = this.classList[0];
          this.loadClassData();
        }
      } catch (error) {
        console.error('加载班级列表失败:', error);
        this.$message.error('加载班级列表失败');
      }
    },
    async loadClassData() {
      try {
        const response = await axios.get(`/api/teaching/learning-patterns/${this.selectedClass}`);
        const data = response.data.data;
        
        // 更新统计数据
        this.updateStats(data);
        
        // 更新图表
        this.updateCharts(data);
        
        // 更新错误模式
        this.errorPatterns = data.error_patterns;
        
        // 更新学生数据
        this.processStudentData(data);
      } catch (error) {
        console.error('加载班级数据失败:', error);
        this.$message.error('加载班级数据失败');
      }
    },
    updateStats(data) {
      const stats = data.daily_trends.reduce((acc, curr) => {
        return {
          activeStudents: Math.max(acc.activeStudents, curr.active_students),
          totalSubmissions: acc.totalSubmissions + curr.total_submissions,
          successRate: acc.successRate + (curr.successful_submissions / curr.total_submissions)
        };
      }, { activeStudents: 0, totalSubmissions: 0, successRate: 0 });
      
      this.overallStats[0].value = stats.activeStudents;
      this.overallStats[1].value = `${Math.round(stats.successRate * 100)}%`;
      this.overallStats[2].value = stats.totalSubmissions;
      this.overallStats[3].value = this.errorPatterns.length;
    },
    updateCharts(data) {
      // 更新趋势图表
      this.initTrendChart(data.daily_trends);
      
      // 更新难度分布图表
      this.initDifficultyChart(data.problem_difficulty);
      
      // 更新进度分布图表
      this.initProgressChart(data.progress_distribution);
    },
    initTrendChart(data) {
      if (!this.charts.trend) {
        this.charts.trend = echarts.init(this.$refs.trendChart);
      }
      
      const option = {
        tooltip: {
          trigger: 'axis'
        },
        legend: {
          data: ['提交次数', '成功次数', '活跃学生']
        },
        xAxis: {
          type: 'category',
          data: data.map(item => item.date)
        },
        yAxis: [
          {
            type: 'value',
            name: '次数'
          },
          {
            type: 'value',
            name: '人数'
          }
        ],
        series: [
          {
            name: '提交次数',
            type: 'line',
            data: data.map(item => item.total_submissions)
          },
          {
            name: '成功次数',
            type: 'line',
            data: data.map(item => item.successful_submissions)
          },
          {
            name: '活跃学生',
            type: 'bar',
            yAxisIndex: 1,
            data: data.map(item => item.active_students)
          }
        ]
      };
      
      this.charts.trend.setOption(option);
    },
    initDifficultyChart(data) {
      if (!this.charts.difficulty) {
        this.charts.difficulty = echarts.init(this.$refs.difficultyChart);
      }
      
      const option = {
        tooltip: {
          trigger: 'item'
        },
        legend: {
          orient: 'vertical',
          left: 'left'
        },
        series: [
          {
            type: 'pie',
            radius: ['40%', '70%'],
            data: data.map(item => ({
              name: item.problem_title,
              value: item.attempt_count
            }))
          }
        ]
      };
      
      this.charts.difficulty.setOption(option);
    },
    initProgressChart(data) {
      if (!this.charts.progress) {
        this.charts.progress = echarts.init(this.$refs.progressChart);
      }
      
      const option = {
        tooltip: {
          trigger: 'axis'
        },
        xAxis: {
          type: 'category',
          data: ['0-20%', '20-40%', '40-60%', '60-80%', '80-100%']
        },
        yAxis: {
          type: 'value'
        },
        series: [
          {
            type: 'bar',
            data: this.calculateProgressDistribution(data)
          }
        ]
      };
      
      this.charts.progress.setOption(option);
    },
    calculateProgressDistribution(data) {
      const distribution = new Array(5).fill(0);
      data.forEach(student => {
        const progress = (student.problems_solved / student.problems_attempted) * 100;
        const index = Math.min(Math.floor(progress / 20), 4);
        distribution[index]++;
      });
      return distribution;
    },
    getProgressColor(rate) {
      if (rate >= 80) return '#67C23A';
      if (rate >= 60) return '#E6A23C';
      return '#F56C6C';
    },
    formatTime(minutes) {
      const hours = Math.floor(minutes / 60);
      const mins = minutes % 60;
      return `${hours}小时${mins}分钟`;
    },
    showStudentDetail(student) {
      this.$router.push({
        path: '/teacher/student-detail',
        query: { id: student.student_id }
      });
    },
    processStudentData(data) {
      this.studentData = data.efficiency_analysis.map(student => ({
        student_id: student.student_id,
        completion_rate: Math.round((student.successful_submissions / student.total_submissions) * 100),
        avg_score: Math.round(student.avg_solving_time),
        total_time: student.total_time || 0
      }));
    }
  },
  mounted() {
    this.loadClassList();
    
    // 监听窗口大小变化，重绘图表
    window.addEventListener('resize', () => {
      Object.values(this.charts).forEach(chart => {
        chart && chart.resize();
      });
    });
  },
  beforeUnmount() {
    // 清理图表实例
    Object.values(this.charts).forEach(chart => {
      chart && chart.dispose();
    });
    window.removeEventListener('resize', this.handleResize);
  }
};
</script>

<style scoped>
.page-container {
  display: flex;
  width: 100%;
  min-height: 100vh;
  background-color: #f0f2f5;
}

.content-container {
  flex: 1;
  margin-left: 250px; /* 导航栏宽度 */
  padding: 20px;
  transition: margin-left 0.3s;
}

/* 当导航栏折叠时调整内容区域 */
.sidebar.collapsed + .content-container {
  margin-left: 64px;
}

.teaching-analysis {
  max-width: 1800px;
  margin: 0 auto;
}

/* 适配小屏幕 */
@media (max-width: 768px) {
  .content-container {
    margin-left: 0;
    padding: 10px;
  }
  
  .stats-cards {
    margin-bottom: 15px;
  }
  
  .el-col {
    margin-bottom: 10px;
  }
}

/* 保留原有样式 */
.teaching-analysis {
  padding: 20px;
}

.stats-cards {
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
}

.stat-icon {
  font-size: 24px;
  margin-right: 15px;
  color: #409EFF;
}

.stat-content {
  flex-grow: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 5px;
}

.stat-title {
  font-size: 14px;
  color: #909399;
}

.class-selector {
  margin-bottom: 20px;
}

.analysis-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  height: 300px;
  width: 100%;
}

.analysis-content {
  margin-bottom: 20px;
}

.el-table {
  margin-top: 10px;
}

:deep(.el-progress-bar__inner) {
  transition: all 0.3s;
}

:deep(.el-card__body) {
  padding: 20px;
}

:deep(.el-table .cell) {
  padding: 8px;
}

/* 调整卡片样式 */
.analysis-card {
  background: white;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.chart-container {
  background: white;
  padding: 15px;
  border-radius: 4px;
}

/* 优化表格在小屏幕上的显示 */
:deep(.el-table) {
  max-width: 100%;
  overflow-x: auto;
}

/* 确保图表容器在小屏幕上也能正常显示 */
@media (max-width: 1200px) {
  .chart-container {
    height: 250px;
  }
}
</style>
