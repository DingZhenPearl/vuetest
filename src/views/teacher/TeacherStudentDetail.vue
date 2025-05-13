<template>
  <div class="student-detail-container">
    <TeacherNavbar />
    <div class="main-content">
      <div class="page-header">
        <div class="back-button">
          <el-button icon="el-icon-arrow-left" @click="goBack">返回</el-button>
        </div>
        <h1>学生学习详情</h1>
      </div>

      <!-- 加载状态 -->
      <div v-if="isLoading" class="loading-container">
        <div class="loading-text">正在加载学生数据，请稍候...</div>
        <el-skeleton :rows="10" animated />
      </div>

      <!-- 学生数据 -->
      <div v-else-if="studentData" class="student-data">
        <!-- 学生基本信息卡片 -->
        <el-card class="info-card">
          <template #header>
            <div class="card-header">
              <span>基本信息</span>
            </div>
          </template>
          <div class="student-info">
            <div class="info-item">
              <span class="label">学号:</span>
              <span class="value">{{ studentData.student_id }}</span>
            </div>
            <div class="info-item">
              <span class="label">姓名:</span>
              <span class="value">{{ studentData.name || '未设置' }}</span>
            </div>
            <div class="info-item">
              <span class="label">班级:</span>
              <span class="value">{{ studentData.class_name || '未设置' }}</span>
            </div>
            <div class="info-item">
              <span class="label">专业:</span>
              <span class="value">{{ studentData.major || '未设置' }}</span>
            </div>
          </div>
        </el-card>

        <!-- 学习统计卡片 -->
        <el-row :gutter="20" class="stats-cards">
          <el-col :span="6" v-for="stat in learningStats" :key="stat.title">
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

        <!-- 学习进度图表 -->
        <el-row :gutter="20" class="chart-row">
          <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
            <el-card class="chart-card">
              <template #header>
                <div class="card-header">
                  <span>学习进度</span>
                </div>
              </template>
              <div ref="progressChart" class="chart-container"></div>
            </el-card>
          </el-col>
          <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
            <el-card class="chart-card">
              <template #header>
                <div class="card-header">
                  <span>解题时间分布</span>
                </div>
              </template>
              <div ref="timeChart" class="chart-container"></div>
            </el-card>
          </el-col>
        </el-row>

        <!-- AI分析结果 -->
        <el-card class="ai-analysis-card">
          <template #header>
            <div class="card-header">
              <span>AI学习分析</span>
              <el-button type="primary" size="small" @click="runAIAnalysis" :loading="aiLoading">
                更新分析
              </el-button>
            </div>
          </template>
          <div v-if="aiAnalysisResult" class="ai-analysis-content">
            <div class="analysis-section">
              <h3>学习模式分析</h3>
              <p>{{ aiAnalysisResult.pattern }}</p>
            </div>
            <el-divider></el-divider>
            <div class="analysis-section">
              <h3>优势领域</h3>
              <p>{{ aiAnalysisResult.strengths }}</p>
            </div>
            <el-divider></el-divider>
            <div class="analysis-section">
              <h3>待提升领域</h3>
              <p>{{ aiAnalysisResult.weaknesses }}</p>
            </div>
            <el-divider></el-divider>
            <div class="analysis-section">
              <h3>学习建议</h3>
              <p>{{ aiAnalysisResult.suggestions }}</p>
            </div>
          </div>
          <div v-else class="no-analysis">
            <p>暂无AI分析结果，点击"更新分析"按钮获取分析。</p>
          </div>
        </el-card>

        <!-- 题目完成情况 -->
        <el-card class="problems-card">
          <template #header>
            <div class="card-header">
              <span>题目完成情况</span>
              <el-input
                v-model="problemSearch"
                placeholder="搜索题目"
                prefix-icon="el-icon-search"
                clearable
                style="width: 200px">
              </el-input>
            </div>
          </template>
          <el-table
            :data="filteredProblems"
            style="width: 100%"
            border
            stripe
            :default-sort="{prop: 'submission_time', order: 'descending'}">
            <el-table-column prop="problem_id" label="题目ID" width="100" sortable />
            <el-table-column prop="problem_title" label="题目标题" sortable />
            <el-table-column label="状态" width="100" sortable>
              <template #default="scope">
                <el-tag :type="scope.row.is_solved ? 'success' : 'danger'">
                  {{ scope.row.is_solved ? '已解决' : '未解决' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="attempts" label="尝试次数" width="100" sortable />
            <el-table-column label="解题时间" width="150" sortable>
              <template #default="scope">
                {{ formatTime(scope.row.time_spent_seconds) }}
              </template>
            </el-table-column>
            <el-table-column prop="submission_time" label="最后提交时间" width="180" sortable>
              <template #default="scope">
                {{ formatDate(scope.row.submission_time) }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </div>

      <!-- 无数据提示 -->
      <div v-else class="no-data">
        <el-empty description="未找到学生数据"></el-empty>
      </div>
    </div>
  </div>
</template>

<script>
import TeacherNavbar from '@/components/teacher/TeacherNavbar.vue'
import axios from 'axios';
import * as echarts from 'echarts';

export default {
  name: 'TeacherStudentDetail',
  components: {
    TeacherNavbar
  },
  data() {
    return {
      studentId: '',
      isLoading: true,
      studentData: null,
      problemSearch: '',
      problems: [],
      learningStats: [
        { title: '完成题目数', value: 0, icon: 'el-icon-check' },
        { title: '平均解题时间', value: '0分钟', icon: 'el-icon-time' },
        { title: '平均尝试次数', value: 0, icon: 'el-icon-refresh' },
        { title: '最近活跃度', value: '低', icon: 'el-icon-data-line' }
      ],
      charts: {
        progress: null,
        time: null
      },
      aiLoading: false,
      aiAnalysisResult: null
    };
  },
  computed: {
    filteredProblems() {
      if (!this.problemSearch) return this.problems;
      const query = this.problemSearch.toLowerCase();
      return this.problems.filter(problem =>
        problem.problem_id.toLowerCase().includes(query) ||
        problem.problem_title.toLowerCase().includes(query)
      );
    }
  },
  mounted() {
    // 从URL获取学生ID
    this.studentId = this.$route.query.id;
    if (!this.studentId) {
      this.$message.error('缺少学生ID参数');
      this.goBack();
      return;
    }

    document.title = `学生详情 - ${this.studentId}`;
    this.loadStudentData();

    // 添加窗口大小变化事件监听
    window.addEventListener('resize', this.handleResize);
  },
  beforeUnmount() {
    // 移除窗口大小变化事件监听
    window.removeEventListener('resize', this.handleResize);

    // 清理图表实例
    Object.values(this.charts).forEach(chart => {
      if (chart) {
        chart.dispose();
      }
    });
  },
  methods: {
    goBack() {
      this.$router.go(-1);
    },
    async loadStudentData() {
      this.isLoading = true;
      try {
        // 获取学生详细数据
        const response = await axios.get(`/api/teaching/student-detail/${this.studentId}`);

        console.log('学生详情数据:', response.data);

        if (!response.data.success) {
          throw new Error(response.data.message || '获取学生数据失败');
        }

        this.studentData = response.data.data.student;
        this.problems = response.data.data.problems || [];

        console.log('学生基本信息:', this.studentData);
        console.log('题目数据:', this.problems);
        console.log('难度统计:', response.data.data.difficulty_stats);

        // 更新统计数据
        this.updateStats(response.data.data);

        // 确保DOM更新后再初始化图表
        setTimeout(() => {
          console.log('延迟初始化图表...');
          console.log('图表容器:', this.$refs.progressChart, this.$refs.timeChart);
          this.initCharts(response.data.data);
        }, 300);

        // 获取AI分析结果
        if (response.data.data.ai_analysis) {
          this.aiAnalysisResult = response.data.data.ai_analysis;
        }
      } catch (error) {
        console.error('加载学生数据失败:', error);
        this.$message.error('加载学生数据失败: ' + (error.message || '未知错误'));
      } finally {
        this.isLoading = false;
      }
    },
    updateStats(data) {
      if (!data) return;

      const stats = data.learning_stats || {};

      // 更新统计卡片
      this.learningStats[0].value = stats.solved_problems || 0;
      this.learningStats[1].value = this.formatTime(stats.avg_time_spent || 0);
      this.learningStats[2].value = stats.avg_attempts ? stats.avg_attempts.toFixed(1) : 0;

      // 计算活跃度
      const recentActivity = data.recent_activity || [];
      let activityLevel = '低';
      if (recentActivity.length > 3) {
        activityLevel = '高';
      } else if (recentActivity.length > 1) {
        activityLevel = '中';
      }
      this.learningStats[3].value = activityLevel;
    },
    initCharts(data) {
      if (!data) {
        console.error('初始化图表失败：数据为空');
        return;
      }

      // 检查图表容器是否存在
      if (!this.$refs.progressChart) {
        console.error('进度图表容器不存在');
        // 延迟重试
        setTimeout(() => {
          console.log('重试初始化图表...');
          this.initCharts(data);
        }, 500);
        return;
      }

      if (!this.$refs.timeChart) {
        console.error('时间分布图表容器不存在');
        // 延迟重试
        setTimeout(() => {
          console.log('重试初始化图表...');
          this.initCharts(data);
        }, 500);
        return;
      }

      console.log('图表容器已就绪，开始初始化图表');

      try {
        // 初始化进度图表
        this.initProgressChart(data);

        // 初始化时间分布图表
        this.initTimeChart(data);

        console.log('图表初始化完成');
      } catch (error) {
        console.error('图表初始化出错:', error);
      }
    },
    initProgressChart(data) {
      try {
        console.log('初始化进度图表...');
        const difficultyStats = data.difficulty_stats || [];
        console.log('难度统计数据:', difficultyStats);

        // 如果没有数据，显示空图表
        if (!difficultyStats || difficultyStats.length === 0) {
          console.warn('没有难度统计数据，显示空图表');

          // 初始化图表
          const chartDom = this.$refs.progressChart;
          if (!chartDom) {
            console.error('进度图表DOM元素不存在');
            return;
          }

          this.charts.progress = echarts.init(chartDom);

          // 设置空图表
          const option = {
            title: {
              text: '暂无数据',
              left: 'center',
              top: 'center'
            },
            tooltip: {
              trigger: 'axis'
            },
            xAxis: {
              type: 'category',
              data: []
            },
            yAxis: {
              type: 'value'
            },
            series: []
          };

          this.charts.progress.setOption(option);
          return;
        }

        // 准备图表数据
        const difficultyData = [];

        // 详细记录每个难度项
        difficultyStats.forEach((item, index) => {
          console.log(`难度项 ${index}:`, item);
          console.log(`  - 难度值:`, item.difficulty, '类型:', typeof item.difficulty);
          console.log(`  - 尝试题目数:`, item.attempted_problems);
          console.log(`  - 已解决题目数:`, item.solved_problems);

          const difficultyText = this.getDifficultyText(item.difficulty);
          console.log(`  - 难度文本:`, difficultyText);

          // 确定难度级别，用于排序
          let difficultyLevel = 0;
          if (difficultyText === '简单' || item.difficulty === 'easy') {
            difficultyLevel = 1;
          } else if (difficultyText === '中等' || item.difficulty === 'medium') {
            difficultyLevel = 2;
          } else if (difficultyText === '困难' || item.difficulty === 'hard') {
            difficultyLevel = 3;
          }

          difficultyData.push({
            text: difficultyText,
            level: difficultyLevel,
            attempted: item.attempted_problems,
            solved: item.solved_problems
          });
        });

        // 按难度级别排序
        difficultyData.sort((a, b) => a.level - b.level);

        // 提取排序后的数据
        const categories = difficultyData.map(item => item.text);
        const attempted = difficultyData.map(item => item.attempted);
        const solved = difficultyData.map(item => item.solved);

        console.log('排序后的图表数据:', { categories, attempted, solved });

        // 初始化图表
        const chartDom = this.$refs.progressChart;
        if (!chartDom) {
          console.error('进度图表DOM元素不存在');
          return;
        }

        // 如果已经初始化过，先销毁
        if (this.charts.progress) {
          this.charts.progress.dispose();
        }

        this.charts.progress = echarts.init(chartDom);

        const option = {
          tooltip: {
            trigger: 'axis',
            axisPointer: {
              type: 'shadow'
            }
          },
          legend: {
            data: ['尝试题目', '已解决']
          },
          grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
          },
          xAxis: {
            type: 'category',
            data: categories
          },
          yAxis: {
            type: 'value'
          },
          series: [
            {
              name: '尝试题目',
              type: 'bar',
              data: attempted
            },
            {
              name: '已解决',
              type: 'bar',
              data: solved
            }
          ]
        };

        this.charts.progress.setOption(option);
        console.log('进度图表初始化完成');
      } catch (error) {
        console.error('初始化进度图表出错:', error);
      }
    },
    initTimeChart() {
      try {
        console.log('初始化时间分布图表...');
        const problems = this.problems || [];
        console.log('题目数据:', problems);

        // 准备图表数据
        const timeRanges = ['<5分钟', '5-15分钟', '15-30分钟', '30-60分钟', '>60分钟'];
        const counts = [0, 0, 0, 0, 0];

        let solvedCount = 0;
        problems.forEach(problem => {
          if (!problem.is_solved) return;
          solvedCount++;

          const minutes = Math.floor(problem.time_spent_seconds / 60);
          if (minutes < 5) {
            counts[0]++;
          } else if (minutes < 15) {
            counts[1]++;
          } else if (minutes < 30) {
            counts[2]++;
          } else if (minutes < 60) {
            counts[3]++;
          } else {
            counts[4]++;
          }
        });

        console.log('解题时间分布:', { timeRanges, counts, solvedCount });

        // 初始化图表
        const chartDom = this.$refs.timeChart;
        if (!chartDom) {
          console.error('时间分布图表DOM元素不存在');
          return;
        }

        // 如果已经初始化过，先销毁
        if (this.charts.time) {
          this.charts.time.dispose();
        }

        this.charts.time = echarts.init(chartDom);

        // 如果没有已解决的题目，显示空图表
        if (solvedCount === 0) {
          console.warn('没有已解决的题目，显示空图表');

          const option = {
            title: {
              text: '暂无数据',
              left: 'center',
              top: 'center'
            },
            tooltip: {
              trigger: 'item'
            },
            series: []
          };

          this.charts.time.setOption(option);
          return;
        }

        const option = {
          tooltip: {
            trigger: 'item',
            formatter: '{a} <br/>{b}: {c} ({d}%)'
          },
          legend: {
            orient: 'vertical',
            left: 10,
            data: timeRanges
          },
          series: [
            {
              name: '解题时间',
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
              data: timeRanges.map((range, index) => ({
                value: counts[index],
                name: range
              }))
            }
          ]
        };

        this.charts.time.setOption(option);
        console.log('时间分布图表初始化完成');
      } catch (error) {
        console.error('初始化时间分布图表出错:', error);
      }
    },
    async runAIAnalysis() {
      this.aiLoading = true;
      try {
        const response = await axios.post(`/api/teaching/student-detail/ai-analysis`, {
          studentId: this.studentId
        });

        if (!response.data.success) {
          throw new Error(response.data.message || 'AI分析失败');
        }

        this.aiAnalysisResult = response.data.analysis;
        this.$message.success('AI分析完成');
      } catch (error) {
        console.error('AI分析失败:', error);
        this.$message.error('AI分析失败: ' + (error.message || '未知错误'));
      } finally {
        this.aiLoading = false;
      }
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
    formatDate(dateString) {
      if (!dateString) return '';

      try {
        return new Date(dateString).toLocaleString('zh-CN', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit'
        });
      } catch (e) {
        return dateString;
      }
    },
    getDifficultyText(difficulty) {
      console.log('获取难度文本，原始值:', difficulty, '类型:', typeof difficulty);

      // 处理不同类型的难度值
      const difficultyMap = {
        // 数字类型
        1: '简单',
        2: '中等',
        3: '困难',
        // 字符串类型 - 数字
        '1': '简单',
        '2': '中等',
        '3': '困难',
        // 字符串类型 - 英文
        'easy': '简单',
        'medium': '中等',
        'hard': '困难'
      };

      // 如果是字符串类型，尝试转换为小写
      let difficultyValue = difficulty;
      if (typeof difficulty === 'string') {
        difficultyValue = difficulty.toLowerCase();
      }

      const result = difficultyMap[difficultyValue] || '未知';
      console.log('难度映射结果:', result);

      // 如果结果仍然是未知，尝试其他方法
      if (result === '未知') {
        console.log('尝试其他映射方法...');

        // 尝试根据字符串内容判断
        if (typeof difficulty === 'string') {
          if (difficulty.includes('easy') || difficulty.includes('简单')) {
            return '简单';
          } else if (difficulty.includes('medium') || difficulty.includes('中等')) {
            return '中等';
          } else if (difficulty.includes('hard') || difficulty.includes('困难')) {
            return '困难';
          }
        }
      }

      return result;
    },

    // 处理窗口大小变化
    handleResize() {
      console.log('窗口大小变化，重新调整图表大小');
      // 延迟执行，确保DOM已更新
      setTimeout(() => {
        Object.values(this.charts).forEach(chart => {
          if (chart) {
            try {
              chart.resize();
            } catch (error) {
              console.error('调整图表大小失败:', error);
            }
          }
        });
      }, 200);
    }
  }
}
</script>

<style scoped>
.student-detail-container {
  display: flex;
  min-height: 100vh;
  background-color: #f5f7fa;
}

.main-content {
  flex: 1;
  padding: 20px;
  margin-left: 250px;
  transition: margin-left 0.3s;
}

@media (max-width: 768px) {
  .main-content {
    margin-left: 64px;
  }
}

.page-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.back-button {
  margin-right: 15px;
}

.loading-container {
  padding: 20px;
  background-color: white;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.loading-text {
  font-size: 18px;
  color: #409EFF;
  text-align: center;
  margin-bottom: 20px;
  font-weight: bold;
}

.info-card {
  margin-bottom: 20px;
}

.student-info {
  display: flex;
  flex-wrap: wrap;
}

.info-item {
  width: 50%;
  margin-bottom: 10px;
}

.label {
  font-weight: bold;
  margin-right: 10px;
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
  display: flex;
  flex-direction: column;
}

.stat-title {
  font-size: 14px;
  color: #606266;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.chart-row {
  margin-bottom: 20px;
}

.chart-card {
  margin-bottom: 20px;
}

.chart-container {
  height: 300px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.ai-analysis-card {
  margin-bottom: 20px;
}

.ai-analysis-content {
  padding: 10px;
}

.analysis-section {
  margin-bottom: 15px;
}

.analysis-section h3 {
  margin-bottom: 10px;
  color: #303133;
}

.no-analysis {
  text-align: center;
  padding: 20px;
  color: #909399;
}

.problems-card {
  margin-bottom: 20px;
}

.no-data {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 400px;
}
</style>
