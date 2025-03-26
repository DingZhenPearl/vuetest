<template>
  <div class="teacher-coding-analysis">
    <h1>教学编程数据分析</h1>

    <!-- Class Selection -->
    <div class="section">
      <h2>班级数据分析</h2>
      <label for="class-select">选择班级:</label>
      <select id="class-select" v-model="selectedClass" @change="fetchClassStats">
        <option disabled value="">请选择一个班级</option>
        <option v-for="className in classList" :key="className" :value="className">
          {{ className }}
        </option>
      </select>
      <div v-if="loadingClassStats">正在加载班级数据...</div>
      <div v-if="classStatsError" class="error">{{ classStatsError }}</div>
      <div v-if="classStats">
        <h3>班级概览 ({{ selectedClass }})</h3>
        <pre>{{ classStats.class_stats }}</pre>
        <h3>题目完成情况</h3>
        <pre>{{ classStats.problem_stats }}</pre>
        <h3>学生排名</h3>
        <pre>{{ classStats.student_rankings }}</pre>
      </div>
    </div>

    <!-- Problem Selection -->
    <div class="section">
      <h2>题目数据分析</h2>
      <label for="problem-select">选择题目:</label>
      <select id="problem-select" v-model="selectedProblem" @change="fetchProblemStats">
         <option disabled value="">请选择一个题目</option>
        <option v-for="problem in problemList" :key="problem.id" :value="problem.id">
          {{ problem.id }} - {{ problem.title }}
        </option>
      </select>
      <div v-if="loadingProblemStats">正在加载题目数据...</div>
      <div v-if="problemStatsError" class="error">{{ problemStatsError }}</div>
      <div v-if="problemStats">
         <h3>题目概览 ({{ selectedProblem }})</h3>
         <pre>{{ problemStats.problem_info }}</pre>
         <h3>各班级完成情况</h3>
         <pre>{{ problemStats.class_stats }}</pre>
         <h3>常见错误</h3>
         <pre>{{ problemStats.common_errors }}</pre>
         <h3>解题时间分布</h3>
         <pre>{{ problemStats.solving_time_distribution }}</pre>
      </div>
    </div>

    <!-- 新增学习模式分析部分 -->
    <div class="section learning-patterns">
      <h2>学习模式分析</h2>
      
      <!-- 每日提交趋势图 -->
      <div class="chart-container">
        <h3>每日提交趋势</h3>
        <v-chart :option="dailyTrendsOption" autoresize />
      </div>
      
      <!-- 难度分布 -->
      <div class="chart-container">
        <h3>题目难度分布</h3>
        <v-chart :option="difficultyOption" autoresize />
      </div>
      
      <!-- 错误模式分析 -->
      <div class="error-patterns">
        <h3>常见错误模式</h3>
        <el-table :data="errorPatterns" stripe>
          <el-table-column prop="error_type" label="错误类型" width="300" show-overflow-tooltip />
          <el-table-column prop="occurrence_count" label="出现次数" width="120" />
          <el-table-column prop="affected_students" label="影响学生数" width="120" />
          <el-table-column prop="related_problems" label="相关题目" show-overflow-tooltip />
        </el-table>
      </div>
      
      <!-- 学习进度分布 -->
      <div class="chart-container">
        <h3>学习进度分布</h3>
        <v-chart :option="progressOption" autoresize />
      </div>
      
      <!-- 学习效率分析 -->
      <div class="chart-container">
        <h3>学习效率分析</h3>
        <el-table :data="efficiencyAnalysis" stripe>
          <el-table-column prop="student_id" label="学生ID" />
          <el-table-column prop="success_rate" label="成功率">
            <template #default="scope">
              {{ ((scope.row.successful_submissions / scope.row.total_submissions) * 100).toFixed(1) }}%
            </template>
          </el-table-column>
          <el-table-column prop="avg_solving_time" label="平均解题时间">
            <template #default="scope">
              {{ formatTime(scope.row.avg_solving_time) }}
            </template>
          </el-table-column>
          <el-table-column prop="efficiency_score" label="效率评分">
            <template #default="scope">
              <el-progress
                :percentage="calculateEfficiencyScore(scope.row)"
                :color="getEfficiencyColor"
              />
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script>
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { LineChart, BarChart, PieChart } from 'echarts/charts';
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components';
import VChart from 'echarts';
import axios from 'axios';

use([
  CanvasRenderer,
  LineChart,
  BarChart,
  PieChart,
  GridComponent,
  TooltipComponent,
  LegendComponent
]);

export default {
  name: 'TeacherCodingAnalysis',
  components: {
    VChart
  },
  data() {
    return {
      selectedClass: '',
      classStats: null,
      loadingClassStats: false,
      classStatsError: '',
      selectedProblem: '',
      problemStats: null,
      loadingProblemStats: false,
      problemStatsError: '',
      classList: [],
      problemList: [],
      learningPatterns: null,
      loadingPatterns: false,
      patternsError: ''
    };
  },
  computed: {
    dailyTrendsOption() {
      if (!this.learningPatterns?.daily_trends) return {};
      const data = this.learningPatterns.daily_trends;
      
      return {
        tooltip: { trigger: 'axis' },
        legend: { data: ['提交数', '成功提交', '活跃学生'] },
        xAxis: {
          type: 'category',
          data: data.map(d => d.date)
        },
        yAxis: { type: 'value' },
        series: [
          {
            name: '提交数',
            type: 'line',
            data: data.map(d => d.total_submissions)
          },
          {
            name: '成功提交',
            type: 'line',
            data: data.map(d => d.successful_submissions)
          },
          {
            name: '活跃学生',
            type: 'line',
            data: data.map(d => d.active_students)
          }
        ]
      };
    },
    // ...其他图表配置
  },
  methods: {
    async fetchClassStats() {
      if (!this.selectedClass) return;
      this.loadingClassStats = true;
      this.classStatsError = '';
      this.classStats = null;
      try {
        const response = await axios.get(`/api/coding/class/${this.selectedClass}`);
        if (response.data && response.data.success) {
          this.classStats = response.data.data;
        } else {
          this.classStatsError = response.data.message || '获取班级数据失败';
        }
      } catch (error) {
        console.error('Error fetching class stats:', error);
        this.classStatsError = `获取班级数据时出错: ${error.message}`;
      } finally {
        this.loadingClassStats = false;
      }
    },
    async fetchProblemStats() {
      if (!this.selectedProblem) return;
      this.loadingProblemStats = true;
      this.problemStatsError = '';
      this.problemStats = null;
      try {
        const response = await axios.get(`/api/coding/problem/${this.selectedProblem}`);
         if (response.data && response.data.success) {
          this.problemStats = response.data.data;
        } else {
          this.problemStatsError = response.data.message || '获取题目数据失败';
        }
      } catch (error) {
        console.error('Error fetching problem stats:', error);
        this.problemStatsError = `获取题目数据时出错: ${error.message}`;
      } finally {
        this.loadingProblemStats = false;
      }
    },
    async fetchLearningPatterns() {
      this.loadingPatterns = true;
      try {
        const response = await axios.get(`/api/teaching/learning-patterns${this.selectedClass ? `/${this.selectedClass}` : ''}`);
        if (response.data.success) {
          this.learningPatterns = response.data.data;
        } else {
          this.patternsError = response.data.message;
        }
      } catch (error) {
        console.error('获取学习模式数据失败:', error);
        this.patternsError = error.message;
      } finally {
        this.loadingPatterns = false;
      }
    },
    async fetchClassList() {
      try {
        const response = await axios.get('/api/teaching/class-list');
        if (response.data.success) {
          this.classList = response.data.classes;
        }
      } catch (error) {
        console.error('获取班级列表失败:', error);
      }
    },
    async fetchProblemList() {
      try {
        const response = await axios.get('/api/problems/all');
        if (response.data.success) {
          this.problemList = response.data.problems.map(p => ({
            id: p.id,
            title: p.title
          }));
        }
      } catch (error) {
        console.error('获取题目列表失败:', error);
      }
    },
    formatTime(seconds) {
      const hours = Math.floor(seconds / 3600);
      const minutes = Math.floor((seconds % 3600) / 60);
      return hours > 0 ? `${hours}小时${minutes}分钟` : `${minutes}分钟`;
    },
    calculateEfficiencyScore({ successful_submissions, total_submissions, avg_solving_time, max_attempts }) {
      const successRate = (successful_submissions / total_submissions) * 100;
      const timeScore = Math.max(0, 100 - (avg_solving_time / 3600) * 20);
      const attemptScore = Math.max(0, 100 - max_attempts * 10);
      return Math.round((successRate + timeScore + attemptScore) / 3);
    },
    getEfficiencyColor(percentage) {
      if (percentage > 80) return '#67C23A';
      if (percentage > 60) return '#E6A23C';
      return '#F56C6C';
    }
  },
  watch: {
    selectedClass() {
      this.fetchLearningPatterns();
    }
  },
  async created() {
    // 页面加载时获取班级和题目列表
    await Promise.all([
      this.fetchClassList(),
      this.fetchProblemList()
    ]);
    
    // 获取学习模式数据
    this.fetchLearningPatterns();
  }
};
</script>

<style scoped>
.teacher-coding-analysis {
  padding: 20px;
}
.section {
  margin-bottom: 30px;
  padding: 15px;
  border: 1px solid #eee;
  border-radius: 5px;
}
label {
  margin-right: 10px;
}
select {
  margin-bottom: 15px;
  padding: 5px;
}
.error {
  color: red;
  margin-top: 10px;
}
pre {
  background-color: #f5f5f5;
  padding: 10px;
  border-radius: 3px;
  white-space: pre-wrap; /* Allows wrapping */
  word-wrap: break-word; /* Breaks long words */
}

.chart-container {
  height: 400px;
  margin: 20px 0;
}

.error-patterns {
  margin: 20px 0;
}

.learning-patterns {
  background-color: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
}
</style>
