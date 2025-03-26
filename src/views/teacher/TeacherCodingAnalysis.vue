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
        <el-descriptions :column="3" border>
          <el-descriptions-item label="总学生数">{{ classStats.class_stats.total_students }}</el-descriptions-item>
          <el-descriptions-item label="总提交次数">{{ classStats.class_stats.total_submissions }}</el-descriptions-item>
          <el-descriptions-item label="成功率">{{ classStats.class_stats.success_rate }}%</el-descriptions-item>
        </el-descriptions>

        <h3>题目完成情况</h3>
        <el-table :data="classStats.problem_stats" stripe>
          <el-table-column prop="problem_title" label="题目" />
          <el-table-column prop="students_attempted" label="尝试人数" />
          <el-table-column prop="success_rate" label="通过率">
            <template #default="scope">{{ scope.row.success_rate }}%</template>
          </el-table-column>
        </el-table>

        <h3>学生排名</h3>
        <el-table :data="classStats.student_rankings" stripe>
          <el-table-column prop="student_id" label="学生ID" />
          <el-table-column prop="solved_problems" label="已解决题目" />
          <el-table-column prop="success_rate" label="成功率">
            <template #default="scope">{{ scope.row.success_rate }}%</template>
          </el-table-column>
        </el-table>
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
        <div ref="dailyTrendsChart" style="width:100%; height:300px;"></div>
      </div>
      
      <!-- 难度分布 -->
      <div class="chart-container">
        <h3>题目难度分布</h3>
        <div ref="difficultyChart" style="width:100%; height:300px;"></div>
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
        <div ref="progressChart" style="width:100%; height:300px;"></div>
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
// 修改导入，使用echarts
import * as echarts from 'echarts/core';
import { BarChart, LineChart } from 'echarts/charts';
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
  DataZoomComponent
} from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';

// 注册必需的组件
echarts.use([
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
  DataZoomComponent,
  BarChart,
  LineChart,
  CanvasRenderer
]);

import axios from 'axios';

export default {
  name: 'TeacherCodingAnalysis',
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
      patternsError: '',
      dailyTrendsChart: null,
      difficultyChart: null,
      progressChart: null
    };
  },
  computed: {
    errorPatterns() {
      return this.learningPatterns?.error_patterns || [];
    },
    efficiencyAnalysis() {
      return this.learningPatterns?.efficiency_analysis || [];
    }
  },
  watch: {
    learningPatterns: {
      handler(newVal) {
        if (newVal) {
          this.$nextTick(() => {
            this.initCharts();
            this.updateCharts();
          });
        }
      },
      deep: true
    }
  },
  methods: {
    async fetchClassStats() {
      if (!this.selectedClass) return;
      this.loadingClassStats = true;
      this.classStatsError = '';
      this.classStats = null;
      try {
        const response = await axios.get(`/api/coding/class/${this.selectedClass}`);
        console.log('班级统计数据响应:', response.data); // 添加调试日志
        if (response.data && response.data.success) {
          this.classStats = response.data.data;
        } else {
          throw new Error(response.data.message || '获取班级数据失败');
        }
      } catch (error) {
        console.error('获取班级统计失败:', error);
        this.$message.error(`获取班级数据失败: ${error.message}`);
        this.classStatsError = error.message;
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
        this.$message.info('正在加载班级列表...');
        const userEmail = sessionStorage.getItem('userEmail');
        const response = await axios.get('/api/teaching/class-list', {
          params: { teacher_email: userEmail }
        });
        
        if (response.data && response.data.success) {
          this.classList = response.data.classes || [];
          // 如果列表非空，自动选择第一个班级
          if (this.classList.length > 0) {
            this.selectedClass = this.classList[0];
            this.fetchClassStats();
          }
        } else {
          throw new Error(response.data.message || '获取班级列表失败');
        }
      } catch (error) {
        console.error('获取班级列表错误:', error);
        this.$message.error('获取班级列表失败: ' + error.message);
      }
    },
    
    async fetchProblemList() {
      try {
        this.$message.info('正在加载题目列表...');
        const userEmail = sessionStorage.getItem('userEmail');
        const response = await axios.get(`/api/problems/teacher/${userEmail}`);
        
        if (response.data && response.data.success && Array.isArray(response.data.problems)) {
          this.problemList = response.data.problems.map(p => ({
            id: p.id.toString(),
            title: p.title || '未命名题目'
          }));
          // 如果列表非空，自动选择第一个题目
          if (this.problemList.length > 0) {
            this.selectedProblem = this.problemList[0].id;
            this.fetchProblemStats();
          }
        } else {
          throw new Error(response.data.message || '获取题目列表失败');
        }
      } catch (error) {
        console.error('获取题目列表错误:', error);
        this.$message.error('获取题目列表失败: ' + error.message);
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
    },
    initCharts() {
      // 初始化图表实例
      if (!this.dailyTrendsChart) {
        this.dailyTrendsChart = echarts.init(this.$refs.dailyTrendsChart);
      }
      if (!this.difficultyChart) {
        this.difficultyChart = echarts.init(this.$refs.difficultyChart);
      }
      if (!this.progressChart) {
        this.progressChart = echarts.init(this.$refs.progressChart);
      }
    },
    
    updateCharts() {
      // 更新每日趋势图表
      if (this.learningPatterns?.daily_trends?.length) {
        this.dailyTrendsChart.setOption({
          tooltip: {
            trigger: 'axis',
            axisPointer: {
              type: 'cross',
              label: {
                backgroundColor: '#6a7985'
              }
            }
          },
          legend: {
            data: ['提交数', '成功提交', '活跃学生'],
            bottom: 10
          },
          grid: {
            left: '3%',
            right: '4%',
            bottom: '15%',
            containLabel: true
          },
          xAxis: {
            type: 'category',
            boundaryGap: false,
            data: this.learningPatterns.daily_trends.map(d => d.date.split(' ')[0]),
            axisLabel: {
              rotate: 45
            }
          },
          yAxis: {
            type: 'value'
          },
          series: [
            {
              name: '提交数',
              type: 'line',
              areaStyle: {
                opacity: 0.1
              },
              data: this.learningPatterns.daily_trends.map(d => d.total_submissions)
            },
            {
              name: '成功提交',
              type: 'line',
              areaStyle: {
                opacity: 0.1
              },
              data: this.learningPatterns.daily_trends.map(d => d.successful_submissions)
            },
            {
              name: '活跃学生',
              type: 'line',
              areaStyle: {
                opacity: 0.1
              },
              data: this.learningPatterns.daily_trends.map(d => d.active_students)
            }
          ]
        });
      }

      // 更新难度分布图表
      if (this.learningPatterns?.problem_difficulty?.length) {
        this.difficultyChart.setOption({
          tooltip: {
            trigger: 'axis',
            axisPointer: {
              type: 'shadow'
            }
          },
          legend: {
            data: ['提交次数', '成功率', '平均解题时间'],
            bottom: 10
          },
          grid: {
            left: '3%',
            right: '4%',
            bottom: '15%',
            containLabel: true
          },
          xAxis: {
            type: 'category',
            data: this.learningPatterns.problem_difficulty.map(d => d.problem_title),
            axisLabel: {
              rotate: 45,
              interval: 0
            }
          },
          yAxis: [
            {
              type: 'value',
              name: '次数'
            },
            {
              type: 'value',
              name: '比率/时间',
              max: 100
            }
          ],
          series: [
            {
              name: '提交次数',
              type: 'bar',
              data: this.learningPatterns.problem_difficulty.map(d => d.attempt_count)
            },
            {
              name: '成功率',
              type: 'line',
              yAxisIndex: 1,
              data: this.learningPatterns.problem_difficulty.map(d => parseFloat(d.success_rate))
            },
            {
              name: '平均解题时间',
              type: 'line',
              yAxisIndex: 1,
              data: this.learningPatterns.problem_difficulty.map(d => parseFloat(d.avg_solution_time))
            }
          ]
        });
      }

      // 更新学习进度分布图表
      if (this.learningPatterns?.progress_distribution?.length) {
        this.progressChart.setOption({
          tooltip: {
            trigger: 'axis',
            axisPointer: {
              type: 'shadow'
            }
          },
          legend: {
            data: ['尝试题数', '已解决', '平均尝试次数'],
            bottom: 10
          },
          grid: {
            left: '3%',
            right: '4%',
            bottom: '15%',
            containLabel: true
          },
          xAxis: {
            type: 'category',
            data: this.learningPatterns.progress_distribution.map(d => d.student_id),
            axisLabel: {
              rotate: 45,
              interval: 0
            }
          },
          yAxis: [
            {
              type: 'value',
              name: '题目数'
            },
            {
              type: 'value',
              name: '尝试次数'
            }
          ],
          series: [
            {
              name: '尝试题数',
              type: 'bar',
              data: this.learningPatterns.progress_distribution.map(d => d.problems_attempted)
            },
            {
              name: '已解决',
              type: 'bar',
              data: this.learningPatterns.progress_distribution.map(d => d.problems_solved)
            },
            {
              name: '平均尝试次数',
              type: 'line',
              yAxisIndex: 1,
              data: this.learningPatterns.progress_distribution.map(d => parseFloat(d.avg_attempts))
            }
          ]
        });
      }
    }
  },
  mounted() {
    // 页面加载时初始化图表
    this.initCharts();
    
    // 添加窗口大小改变的监听
    window.addEventListener('resize', () => {
      this.dailyTrendsChart?.resize();
      this.difficultyChart?.resize();
      this.progressChart?.resize();
    });
  },
  beforeUnmount() {
    // 组件销毁时释放图表实例
    this.dailyTrendsChart?.dispose();
    this.difficultyChart?.dispose();
    this.progressChart?.dispose();
    
    // 移除窗口大小改变的监听
    window.removeEventListener('resize', this.handleResize);
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
