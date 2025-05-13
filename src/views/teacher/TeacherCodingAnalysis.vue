<template>
  <div class="page-container">
    <TeacherNavbar />
    <div class="content-container">
      <div class="coding-analysis">
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
            <!-- 提交趋势图 -->
            <el-card class="analysis-card">
              <template #header>
                <div class="card-header">
                  <span>编程提交趋势</span>
                  <el-radio-group v-model="trendTimeRange" size="small">
                    <el-radio-button label="week">周</el-radio-button>
                    <el-radio-button label="month">月</el-radio-button>
                  </el-radio-group>
                </div>
              </template>
              <div ref="submissionTrendChart" class="chart-container"></div>
            </el-card>

            <!-- 编程语言分布 -->
            <el-card class="analysis-card">
              <template #header>
                <div class="card-header">
                  <span>编程错误类型分布</span>
                </div>
              </template>
              <div ref="errorTypeChart" class="chart-container"></div>
            </el-card>
          </el-col>

          <!-- 右侧内容 -->
          <el-col :span="8">
            <!-- 常见错误分析 -->
            <el-card class="analysis-card">
              <template #header>
                <div class="card-header">
                  <span>常见编程错误</span>
                </div>
              </template>
              <el-table :data="errorPatterns" style="width: 100%">
                <el-table-column prop="error_type" label="错误类型" width="180" />
                <el-table-column prop="occurrence_count" label="出现次数" width="100" />
                <el-table-column prop="affected_students" label="影响学生数" />
              </el-table>
            </el-card>

            <!-- 编程能力分布 -->
            <el-card class="analysis-card">
              <template #header>
                <div class="card-header">
                  <span>编程能力分布</span>
                </div>
              </template>
              <div ref="codingAbilityChart" class="chart-container"></div>
            </el-card>
          </el-col>
        </el-row>

        <!-- 学生编程表现详情 -->
        <el-card class="analysis-card">
          <template #header>
            <div class="card-header">
              <span>学生编程表现详情</span>
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
            :default-sort="{ prop: 'success_rate', order: 'descending' }">
            <el-table-column prop="student_id" label="学号" sortable />
            <el-table-column prop="success_rate" label="成功率" sortable>
              <template #default="scope">
                <el-progress
                  :percentage="scope.row.success_rate"
                  :color="getProgressColor(scope.row.success_rate)"
                />
              </template>
            </el-table-column>
            <el-table-column prop="total_submissions" label="提交次数" sortable />
            <el-table-column prop="avg_solving_time" label="平均解题时间" sortable>
              <template #default="scope">
                {{ formatTime(scope.row.avg_solving_time) }}
              </template>
            </el-table-column>
            <el-table-column prop="max_attempts" label="最多尝试次数" sortable />
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
  name: 'TeacherCodingAnalysis',
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
        { title: '平均成功率', value: '0%', icon: 'el-icon-data-line' },
        { title: '本周提交数', value: 0, icon: 'el-icon-document' },
        { title: '常见错误类型', value: 0, icon: 'el-icon-warning' }
      ],
      errorPatterns: [],
      studentData: [],
      charts: {
        submissionTrend: null,
        errorType: null,
        codingAbility: null
      },
      isLoading: false
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
        this.isLoading = true;
        const response = await axios.get('/api/teaching/class-list');
        this.classList = response.data.classes;
        if (this.classList.length > 0) {
          this.selectedClass = this.classList[0];
          this.loadClassData();
        }
      } catch (error) {
        console.error('加载班级列表失败:', error);
        this.$message.error('加载班级列表失败');
      } finally {
        this.isLoading = false;
      }
    },
    async loadClassData() {
      try {
        this.isLoading = true;
        const response = await axios.get(`/api/coding/class/${encodeURIComponent(this.selectedClass)}`);

        if (!response.data.success) {
          this.$message.error(response.data.message || '获取班级数据失败');
          return;
        }

        const data = response.data.data;

        // 更新统计数据
        this.updateStats(data);

        // 更新图表
        this.updateCharts(data);

        // 更新错误模式
        this.updateErrorPatterns(data);

        // 更新学生数据
        this.processStudentData(data);
      } catch (error) {
        console.error('加载班级数据失败:', error);
        this.$message.error('加载班级数据失败: ' + (error.message || '未知错误'));
      } finally {
        this.isLoading = false;
      }
    },
    updateStats(data) {
      if (!data || !data.class_stats) {
        return;
      }

      const stats = data.class_stats;

      // 更新统计卡片数据
      this.overallStats[0].value = stats.total_students || 0;
      this.overallStats[1].value = `${Math.round(stats.success_rate || 0)}%`;
      this.overallStats[2].value = stats.total_submissions || 0;

      // 错误类型数量
      if (data.problem_stats) {
        const errorTypes = new Set();
        data.problem_stats.forEach(problem => {
          if (problem.common_errors) {
            problem.common_errors.forEach(error => {
              errorTypes.add(error.error_type);
            });
          }
        });
        this.overallStats[3].value = errorTypes.size;
      }
    },
    updateCharts(data) {
      if (!data) return;

      // 初始化提交趋势图表
      this.initSubmissionTrendChart(data.student_rankings || []);

      // 初始化错误类型分布图表
      this.initErrorTypeChart(data.problem_stats || []);

      // 初始化编程能力分布图表
      this.initCodingAbilityChart(data.student_rankings || []);
    },
    initSubmissionTrendChart(studentRankings) {
      if (!this.charts.submissionTrend) {
        this.charts.submissionTrend = echarts.init(this.$refs.submissionTrendChart);
      }

      // 按照解决问题数量对学生进行排序
      const sortedStudents = [...studentRankings].sort((a, b) => b.solved_problems - a.solved_problems);

      // 取前10名学生
      const top10Students = sortedStudents.slice(0, 10);

      const option = {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        legend: {
          data: ['已解决问题', '总提交次数']
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'value'
        },
        yAxis: {
          type: 'category',
          data: top10Students.map(student => student.student_id)
        },
        series: [
          {
            name: '已解决问题',
            type: 'bar',
            stack: 'total',
            label: {
              show: true
            },
            emphasis: {
              focus: 'series'
            },
            data: top10Students.map(student => student.solved_problems)
          },
          {
            name: '总提交次数',
            type: 'bar',
            stack: 'total',
            label: {
              show: true
            },
            emphasis: {
              focus: 'series'
            },
            data: top10Students.map(student => student.total_submissions)
          }
        ]
      };

      this.charts.submissionTrend.setOption(option);
    },
    initErrorTypeChart(problemStats) {
      if (!this.charts.errorType) {
        this.charts.errorType = echarts.init(this.$refs.errorTypeChart);
      }

      // 收集所有错误类型及其出现次数
      const errorCounts = {};
      problemStats.forEach(problem => {
        if (problem.common_errors) {
          problem.common_errors.forEach(error => {
            if (!errorCounts[error.error_type]) {
              errorCounts[error.error_type] = 0;
            }
            errorCounts[error.error_type] += error.count;
          });
        }
      });

      // 转换为饼图数据格式
      const pieData = Object.entries(errorCounts).map(([name, value]) => ({ name, value }));

      const option = {
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'vertical',
          left: 10,
          data: pieData.map(item => item.name)
        },
        series: [
          {
            name: '错误类型',
            type: 'pie',
            radius: ['50%', '70%'],
            avoidLabelOverlap: false,
            label: {
              show: false,
              position: 'center'
            },
            emphasis: {
              label: {
                show: true,
                fontSize: '18',
                fontWeight: 'bold'
              }
            },
            labelLine: {
              show: false
            },
            data: pieData
          }
        ]
      };

      this.charts.errorType.setOption(option);
    },
    initCodingAbilityChart(studentRankings) {
      if (!this.charts.codingAbility) {
        this.charts.codingAbility = echarts.init(this.$refs.codingAbilityChart);
      }

      // 计算成功率分布
      const successRateRanges = [
        { range: '0-20%', count: 0 },
        { range: '20-40%', count: 0 },
        { range: '40-60%', count: 0 },
        { range: '60-80%', count: 0 },
        { range: '80-100%', count: 0 }
      ];

      studentRankings.forEach(student => {
        const successRate = student.success_rate || 0;
        const index = Math.min(Math.floor(successRate / 20), 4);
        successRateRanges[index].count++;
      });

      const option = {
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} 人'
        },
        xAxis: {
          type: 'category',
          data: successRateRanges.map(item => item.range)
        },
        yAxis: {
          type: 'value'
        },
        series: [
          {
            name: '学生数量',
            type: 'bar',
            data: successRateRanges.map(item => item.count),
            itemStyle: {
              color: function(params) {
                const colors = ['#F56C6C', '#E6A23C', '#E6A23C', '#67C23A', '#67C23A'];
                return colors[params.dataIndex];
              }
            }
          }
        ]
      };

      this.charts.codingAbility.setOption(option);
    },
    updateErrorPatterns(data) {
      if (!data || !data.problem_stats) {
        this.errorPatterns = [];
        return;
      }

      // 收集所有错误类型及其统计信息
      const errorMap = new Map();

      data.problem_stats.forEach(problem => {
        if (problem.common_errors) {
          problem.common_errors.forEach(error => {
            if (!errorMap.has(error.error_type)) {
              errorMap.set(error.error_type, {
                error_type: error.error_type,
                occurrence_count: 0,
                affected_students: new Set()
              });
            }

            const errorInfo = errorMap.get(error.error_type);
            errorInfo.occurrence_count += error.count;

            // 如果有学生ID信息，添加到受影响学生集合中
            if (error.student_ids) {
              error.student_ids.forEach(id => errorInfo.affected_students.add(id));
            }
          });
        }
      });

      // 转换为数组并计算受影响学生数量
      this.errorPatterns = Array.from(errorMap.values()).map(error => ({
        error_type: error.error_type,
        occurrence_count: error.occurrence_count,
        affected_students: error.affected_students.size
      }));

      // 按出现次数排序
      this.errorPatterns.sort((a, b) => b.occurrence_count - a.occurrence_count);
    },
    processStudentData(data) {
      if (!data || !data.student_rankings) {
        this.studentData = [];
        return;
      }

      this.studentData = data.student_rankings.map(student => ({
        student_id: student.student_id,
        success_rate: parseFloat(student.success_rate) || 0,
        total_submissions: student.total_submissions || 0,
        solved_problems: student.solved_problems || 0,
        avg_solving_time: student.avg_solving_time || 0,
        max_attempts: student.max_attempts || 0
      }));
    },
    getProgressColor(rate) {
      if (rate >= 80) return '#67C23A';
      if (rate >= 60) return '#E6A23C';
      return '#F56C6C';
    },
    formatTime(seconds) {
      if (!seconds) return '0分钟';

      const minutes = Math.floor(seconds / 60);
      if (minutes < 60) {
        return `${minutes}分钟`;
      }

      const hours = Math.floor(minutes / 60);
      const remainingMinutes = minutes % 60;
      return `${hours}小时${remainingMinutes}分钟`;
    },
    showStudentDetail(student) {
      this.$router.push({
        path: '/teacher/student-detail',
        query: { id: student.student_id }
      });
    },
    handleResize() {
      Object.values(this.charts).forEach(chart => {
        chart && chart.resize();
      });
    }
  },
  mounted() {
    document.title = '编程数据分析 - 教师端';
    this.loadClassList();

    // 监听窗口大小变化，重绘图表
    window.addEventListener('resize', this.handleResize);
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

.coding-analysis {
  max-width: 1800px;
  margin: 0 auto;
}

/* 适配小屏幕 */
@media (max-width: 768px) {
  .content-container {
    margin-left: 50px;
    padding: 10px;
  }

  .stats-cards {
    margin-bottom: 15px;
  }

  .el-col {
    margin-bottom: 10px;
  }
}

/* 统计卡片样式 */
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

/* 班级选择器 */
.class-selector {
  margin-bottom: 20px;
}

/* 分析卡片 */
.analysis-card {
  margin-bottom: 20px;
  background: white;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  height: 300px;
  width: 100%;
  background: white;
  padding: 15px;
  border-radius: 4px;
}

.analysis-content {
  margin-bottom: 20px;
}

/* 表格样式 */
:deep(.el-progress-bar__inner) {
  transition: all 0.3s;
}

:deep(.el-card__body) {
  padding: 20px;
}

:deep(.el-table .cell) {
  padding: 8px;
}

/* 确保图表容器在小屏幕上也能正常显示 */
@media (max-width: 1200px) {
  .chart-container {
    height: 250px;
  }
}
</style>
