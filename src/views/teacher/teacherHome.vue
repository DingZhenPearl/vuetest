<template>
  <div class="teacher-page">
    <!-- 导航侧边栏 -->
    <TeacherNavbar />

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 加载状态 -->
      <t-loading :loading="isLoading" fullscreen>
        <template #tip>
          <span>正在加载数据...</span>
        </template>
      </t-loading>

      <!-- 欢迎区域 -->
      <div class="welcome-section">
        <div class="welcome-header">
          <h1>欢迎回来，{{ userName || '老师' }}</h1>
          <p class="welcome-subtitle">今天是 {{ currentDate }}，祝您工作愉快！</p>
        </div>
      </div>

      <!-- 顶部统计卡片 -->
      <div class="stats-overview">
        <t-row :gutter="[16, 16]">
          <t-col :xs="24" :sm="12" :md="6" :lg="6" :xl="6">
            <t-card class="stat-card" :bordered="false" theme="poster2">
              <template #footer>
                <div class="stat-title">学生总数</div>
              </template>
              <div class="stat-value">{{ stats.totalStudents }}</div>
              <div class="stat-trend">
                <t-tag theme="success" variant="light">
                  <template #icon><i class="el-icon-top"></i></template>
                  {{ stats.studentGrowth }}%
                </t-tag>
                <span class="trend-text">较上月</span>
              </div>
            </t-card>
          </t-col>
          <t-col :xs="24" :sm="12" :md="6" :lg="6" :xl="6">
            <t-card class="stat-card" :bordered="false" theme="poster2">
              <template #footer>
                <div class="stat-title">活跃学生</div>
              </template>
              <div class="stat-value">{{ stats.activeStudents }}</div>
              <div class="stat-trend">
                <t-tag theme="success" variant="light">
                  <template #icon><i class="el-icon-top"></i></template>
                  {{ stats.activeGrowth }}%
                </t-tag>
                <span class="trend-text">较上周</span>
              </div>
            </t-card>
          </t-col>
          <t-col :xs="24" :sm="12" :md="6" :lg="6" :xl="6">
            <t-card class="stat-card" :bordered="false" theme="poster2">
              <template #footer>
                <div class="stat-title">题目总数</div>
              </template>
              <div class="stat-value">{{ stats.totalProblems }}</div>
              <div class="stat-trend">
                <t-tag theme="success" variant="light">
                  <template #icon><i class="el-icon-top"></i></template>
                  {{ stats.problemGrowth }}%
                </t-tag>
                <span class="trend-text">较上月</span>
              </div>
            </t-card>
          </t-col>
          <t-col :xs="24" :sm="12" :md="6" :lg="6" :xl="6">
            <t-card class="stat-card" :bordered="false" theme="poster2">
              <template #footer>
                <div class="stat-title">提交次数</div>
              </template>
              <div class="stat-value">{{ stats.totalSubmissions }}</div>
              <div class="stat-trend">
                <t-tag theme="success" variant="light">
                  <template #icon><i class="el-icon-top"></i></template>
                  {{ stats.submissionGrowth }}%
                </t-tag>
                <span class="trend-text">较上周</span>
              </div>
            </t-card>
          </t-col>
        </t-row>
      </div>

      <!-- 主要内容区 -->
      <div class="dashboard-content">
        <!-- 左侧内容 -->
        <div class="dashboard-left">
          <!-- 题目完成情况 -->
          <t-card title="题目完成情况" class="chart-card">
            <div class="chart-container" ref="problemChartContainer"></div>
          </t-card>
        </div>

        <!-- 右侧内容 -->
        <div class="dashboard-right">
          <!-- 快捷功能 -->
          <t-card title="快捷功能" class="feature-card">
            <t-row :gutter="[16, 16]">
              <t-col :span="8" v-for="(feature, index) in features" :key="index">
                <div class="feature-item" @click="navigateTo(feature.route)">
                  <i :class="feature.icon"></i>
                  <div class="feature-info">
                    <h3>{{ feature.title }}</h3>
                    <p>{{ feature.description }}</p>
                  </div>
                </div>
              </t-col>
            </t-row>
          </t-card>

          <!-- 待处理事项 -->
          <t-card title="待处理事项" class="todo-card">
            <template #actions>
              <t-button theme="primary" variant="text" @click="refreshTodos">
                <i class="el-icon-refresh"></i> 刷新
              </t-button>
            </template>
            <t-list v-if="todos.length > 0">
              <t-list-item v-for="(todo, index) in todos" :key="index">
                <template #content>
                  <div class="todo-item">
                    <div class="todo-content">
                      <div class="todo-title">{{ todo.title }}</div>
                      <div class="todo-description">{{ todo.description }}</div>
                    </div>
                    <t-button theme="primary" size="small" variant="outline" @click="handleTodo(todo)">
                      处理
                    </t-button>
                  </div>
                </template>
              </t-list-item>
            </t-list>
            <div v-else class="empty-todos">
              <p>暂无待处理事项</p>
            </div>
          </t-card>

          <!-- 最近学生提问 -->
          <t-card title="最近学生提问" class="questions-card">
            <t-list v-if="questions.length > 0">
              <t-list-item v-for="(question, index) in questions" :key="index">
                <template #content>
                  <div class="question-item">
                    <div class="question-info">
                      <span class="student-name">{{ question.studentName }}</span>
                      <span class="question-time">{{ formatTime(question.time) }}</span>
                    </div>
                    <div class="question-content">{{ question.content }}</div>
                    <t-button theme="primary" size="small" variant="outline" @click="viewQuestion(question)">
                      查看详情
                    </t-button>
                  </div>
                </template>
              </t-list-item>
            </t-list>
            <div v-else class="empty-questions">
              <p>暂无学生提问</p>
            </div>
          </t-card>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts';
import TeacherNavbar from '@/components/teacher/TeacherNavbar.vue';
import axios from 'axios';

export default {
  name: 'TeacherHome',
  components: {
    TeacherNavbar
  },
  data() {
    return {
      isLoading: true,
      userName: '',
      currentDate: '',
      problemChart: null,
      stats: {
        totalStudents: 0,
        studentGrowth: 0,
        activeStudents: 0,
        activeGrowth: 0,
        totalProblems: 0,
        problemGrowth: 0,
        totalSubmissions: 0,
        submissionGrowth: 0
      },
      features: [
        {
          title: '学生提问',
          description: '查看和回复学生的提问',
          icon: 'el-icon-chat-line-round',
          route: '/teacher/answer'
        },
        {
          title: '出题管理',
          description: '创建和管理编程题目',
          icon: 'el-icon-edit-outline',
          route: '/teacher/problems'
        },
        {
          title: '教学内容',
          description: '管理教学内容',
          icon: 'el-icon-reading',
          route: '/teacher/teaching-contents'
        },
        {
          title: '数据分析',
          description: '查看教学数据分析',
          icon: 'el-icon-data-analysis',
          route: '/teacher/data-analysis'
        }
      ],
      todos: [],
      questions: []
    }
  },
  created() {
    // 检查用户登录状态
    const username = sessionStorage.getItem('username');
    if (!username) {
      this.$router.push('/logIn');
      return;
    }

    this.userName = username;

    // 设置当前日期
    this.setCurrentDate();

    // 初始化数据
    this.initData();
  },
  mounted() {
    // 在DOM渲染完成后初始化图表
    this.$nextTick(() => {
      this.initCharts();
    });
  },
  beforeUnmount() {
    // 销毁图表实例
    if (this.problemChart) {
      this.problemChart.dispose();
    }

    // 移除窗口大小变化监听
    window.removeEventListener('resize', this.resizeCharts);
  },
  methods: {
    // 初始化所有数据
    async initData() {
      this.isLoading = true;

      try {
        // 并行执行多个数据获取任务
        await Promise.all([
          this.fetchStats(),
          this.fetchTodos(),
          this.fetchQuestions()
        ]);
      } catch (error) {
        console.error('初始化数据失败:', error);
      } finally {
        this.isLoading = false;

        // 在数据加载完成后初始化图表
        this.$nextTick(() => {
          this.initCharts();
        });
      }
    },

    // 设置当前日期
    setCurrentDate() {
      const now = new Date();
      const options = { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' };
      this.currentDate = now.toLocaleDateString('zh-CN', options);
    },

    // 获取统计数据
    async fetchStats() {
      try {
        const response = await axios.get('/api/teaching/stats');

        if (response.data.success) {
          const data = response.data.data || {};

          // 更新统计数据
          this.stats = {
            totalStudents: data.total_students || 0,
            studentGrowth: data.student_growth || 0,
            activeStudents: data.active_students || 0,
            activeGrowth: data.active_growth || 0,
            totalProblems: data.total_problems || 0,
            problemGrowth: data.problem_growth || 0,
            totalSubmissions: data.total_submissions || 0,
            submissionGrowth: data.submission_growth || 0
          };
        } else {
          // 显示错误信息
          this.$message.error(response.data.message || '获取统计数据失败');
          console.error('获取统计数据失败:', response.data);
        }
      } catch (error) {
        // 显示错误信息
        this.$message.error('获取统计数据失败: ' + (error.message || '未知错误'));
        console.error('获取统计数据失败:', error);
      }
    },

    // 获取待处理事项
    async fetchTodos() {
      try {
        const response = await axios.get('/api/teaching/todos');

        if (response.data.success) {
          this.todos = response.data.todos || [];
        }
      } catch (error) {
        console.error('获取待处理事项失败:', error);
        // 使用默认值
        this.todos = [];
      }
    },

    // 刷新待处理事项
    async refreshTodos() {
      try {
        this.$message.info('正在更新待处理事项...');
        await this.fetchTodos();
        this.$message.success('待处理事项已更新');
      } catch (error) {
        this.$message.error('更新待处理事项失败');
      }
    },

    // 处理待办事项
    handleTodo(todo) {
      if (todo.type === 'question') {
        this.navigateTo('/teacher/answer');
      } else if (todo.type === 'submission') {
        this.navigateTo('/teacher/data-analysis');
      } else {
        this.navigateTo(todo.route || '/teacher/home');
      }
    },

    // 获取学生提问
    async fetchQuestions() {
      try {
        const response = await axios.get('/api/questions/all');

        if (response.data.success) {
          // 获取最近5个问题
          this.questions = (response.data.questions || [])
            .filter(q => q.status === 'pending')
            .slice(0, 5)
            .map(q => ({
              id: q.id,
              studentName: q.student_name || q.email.split('@')[0],
              content: q.title,
              time: q.created_at,
              route: `/teacher/answer?id=${q.id}`
            }));
        }
      } catch (error) {
        console.error('获取学生提问失败:', error);
        this.questions = [];
      }
    },

    // 查看问题详情
    viewQuestion(question) {
      this.navigateTo(question.route || '/teacher/answer');
    },

    // 初始化图表
    initCharts() {
      this.initProblemChart();

      // 添加窗口大小变化监听
      window.addEventListener('resize', this.resizeCharts);
    },

    // 初始化题目完成情况图表
    initProblemChart() {
      if (!this.$refs.problemChartContainer) return;

      // 创建图表实例
      this.problemChart = echarts.init(this.$refs.problemChartContainer);

      // 获取图表数据并渲染
      this.fetchProblemData();
    },

    // 获取题目完成情况数据
    async fetchProblemData() {
      try {
        const response = await axios.get('/api/teaching/problem-completion');

        if (response.data.success) {
          this.renderProblemChart(response.data.data);
        } else {
          // 显示具体错误信息
          const errorMsg = response.data.message || '获取题目完成情况数据失败';
          this.renderErrorProblemChart(errorMsg);
        }
      } catch (error) {
        console.error('获取题目完成情况数据失败:', error);
        this.renderErrorProblemChart('获取题目完成情况数据失败: ' + (error.message || '未知错误'));
      }
    },

    // 渲染题目完成情况图表
    renderProblemChart(data) {
      // 如果没有数据，显示空图表
      if (!data || !data.difficulties || data.difficulties.length === 0 ||
          !data.student_completion_rates || !data.problem_attempt_rates ||
          !data.success_rates || !data.avg_attempts_per_problem ||
          data.student_completion_rates.length === 0 || data.problem_attempt_rates.length === 0) {
        this.renderEmptyProblemChart();
        return;
      }

      // 准备图表数据
      const difficulties = data.difficulties;
      const studentCompletionRates = data.student_completion_rates;
      const problemAttemptRates = data.problem_attempt_rates;
      const successRates = data.success_rates;
      const avgAttemptsPerProblem = data.avg_attempts_per_problem;
      const activeStudents = data.active_students || 0;

      // 设置图表选项
      const option = {
        title: {
          text: `活跃学生数: ${activeStudents}`,
          subtext: '基于真实学生数据的科学统计',
          left: 'center',
          top: 0,
          textStyle: {
            fontSize: 14
          },
          subtextStyle: {
            fontSize: 12
          }
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          },
          formatter: function(params) {
            let result = params[0].name + '<br/>';
            params.forEach(param => {
              let marker = param.marker;
              let seriesName = param.seriesName;
              let value = param.value;
              let unit = seriesName === '平均尝试次数' ? '次' : '%';
              result += marker + ' ' + seriesName + ': ' + value + unit + '<br/>';
            });
            return result;
          }
        },
        legend: {
          data: ['学生平均完成率', '题目尝试率', '提交成功率', '平均尝试次数'],
          top: 30
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          top: 80,
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: difficulties
        },
        yAxis: [
          {
            type: 'value',
            name: '百分比',
            min: 0,
            max: 100,
            position: 'left',
            axisLabel: {
              formatter: '{value}%'
            }
          },
          {
            type: 'value',
            name: '次数',
            min: 0,
            position: 'right',
            axisLabel: {
              formatter: '{value}次'
            }
          }
        ],
        series: [
          {
            name: '学生平均完成率',
            type: 'bar',
            data: studentCompletionRates,
            itemStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: '#83bff6' },
                { offset: 0.5, color: '#188df0' },
                { offset: 1, color: '#0d47a1' }
              ])
            }
          },
          {
            name: '题目尝试率',
            type: 'bar',
            data: problemAttemptRates,
            itemStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: '#ffb980' },
                { offset: 0.5, color: '#ff7f50' },
                { offset: 1, color: '#d94e20' }
              ])
            }
          },
          {
            name: '提交成功率',
            type: 'line',
            data: successRates,
            symbol: 'circle',
            symbolSize: 8,
            lineStyle: {
              width: 3
            },
            itemStyle: {
              color: '#67c23a'
            }
          },
          {
            name: '平均尝试次数',
            type: 'line',
            yAxisIndex: 1,
            data: avgAttemptsPerProblem,
            symbol: 'diamond',
            symbolSize: 8,
            lineStyle: {
              width: 3,
              type: 'dashed'
            },
            itemStyle: {
              color: '#e6a23c'
            }
          }
        ]
      };

      // 渲染图表
      this.problemChart.setOption(option);
    },

    // 渲染空题目完成情况图表
    renderEmptyProblemChart() {
      const option = {
        title: {
          text: '暂无题目完成情况数据',
          left: 'center',
          top: 'center',
          textStyle: {
            color: '#999',
            fontSize: 16,
            fontWeight: 'normal'
          }
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        legend: {
          data: ['学生平均完成率', '题目尝试率', '提交成功率', '平均尝试次数'],
          top: 30
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          top: 80,
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: []
        },
        yAxis: [
          {
            type: 'value',
            name: '百分比',
            min: 0,
            max: 100,
            position: 'left',
            axisLabel: {
              formatter: '{value}%'
            }
          },
          {
            type: 'value',
            name: '次数',
            min: 0,
            position: 'right',
            axisLabel: {
              formatter: '{value}次'
            }
          }
        ],
        series: [
          {
            name: '学生平均完成率',
            type: 'bar',
            data: [],
            itemStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: '#83bff6' },
                { offset: 0.5, color: '#188df0' },
                { offset: 1, color: '#0d47a1' }
              ])
            }
          },
          {
            name: '题目尝试率',
            type: 'bar',
            data: [],
            itemStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: '#ffb980' },
                { offset: 0.5, color: '#ff7f50' },
                { offset: 1, color: '#d94e20' }
              ])
            }
          },
          {
            name: '提交成功率',
            type: 'line',
            data: [],
            symbol: 'circle',
            symbolSize: 8,
            lineStyle: {
              width: 3
            },
            itemStyle: {
              color: '#67c23a'
            }
          },
          {
            name: '平均尝试次数',
            type: 'line',
            yAxisIndex: 1,
            data: [],
            symbol: 'diamond',
            symbolSize: 8,
            lineStyle: {
              width: 3,
              type: 'dashed'
            },
            itemStyle: {
              color: '#e6a23c'
            }
          }
        ]
      };

      this.problemChart.setOption(option);
      this.$message.warning('暂无题目完成情况数据');
    },

    // 渲染错误题目完成情况图表
    renderErrorProblemChart(errorMsg) {
      const option = {
        title: {
          text: '获取数据失败',
          left: 'center',
          top: 'center',
          textStyle: {
            color: '#f56c6c',
            fontSize: 16,
            fontWeight: 'normal'
          }
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        legend: {
          data: ['学生平均完成率', '题目尝试率', '提交成功率', '平均尝试次数'],
          top: 30
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          top: 80,
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: []
        },
        yAxis: [
          {
            type: 'value',
            name: '百分比',
            min: 0,
            max: 100,
            position: 'left',
            axisLabel: {
              formatter: '{value}%'
            }
          },
          {
            type: 'value',
            name: '次数',
            min: 0,
            position: 'right',
            axisLabel: {
              formatter: '{value}次'
            }
          }
        ],
        series: [
          {
            name: '学生平均完成率',
            type: 'bar',
            data: [],
            itemStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: '#83bff6' },
                { offset: 0.5, color: '#188df0' },
                { offset: 1, color: '#0d47a1' }
              ])
            }
          },
          {
            name: '题目尝试率',
            type: 'bar',
            data: [],
            itemStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: '#ffb980' },
                { offset: 0.5, color: '#ff7f50' },
                { offset: 1, color: '#d94e20' }
              ])
            }
          },
          {
            name: '提交成功率',
            type: 'line',
            data: [],
            symbol: 'circle',
            symbolSize: 8,
            lineStyle: {
              width: 3
            },
            itemStyle: {
              color: '#67c23a'
            }
          },
          {
            name: '平均尝试次数',
            type: 'line',
            yAxisIndex: 1,
            data: [],
            symbol: 'diamond',
            symbolSize: 8,
            lineStyle: {
              width: 3,
              type: 'dashed'
            },
            itemStyle: {
              color: '#e6a23c'
            }
          }
        ]
      };

      this.problemChart.setOption(option);

      // 显示错误信息
      this.$message.error(errorMsg);
    },

    // 调整图表大小
    resizeCharts() {
      if (this.problemChart) {
        this.problemChart.resize();
      }
    },

    // 格式化时间
    formatTime(timestamp) {
      if (!timestamp) return '';

      const date = new Date(timestamp);
      const now = new Date();
      const diff = now - date;

      // 小于1天，显示相对时间
      if (diff < 24 * 60 * 60 * 1000) {
        const hours = Math.floor(diff / (60 * 60 * 1000));
        if (hours < 1) {
          const minutes = Math.floor(diff / (60 * 1000));
          return minutes < 1 ? '刚刚' : `${minutes}分钟前`;
        }
        return `${hours}小时前`;
      }

      // 大于1天，显示具体日期
      return date.toLocaleDateString('zh-CN', { month: 'numeric', day: 'numeric', hour: 'numeric', minute: 'numeric' });
    },

    // 导航到指定路由
    navigateTo(route) {
      this.$router.push(route);
    }
  }
}
</script>

<style scoped>
/* 整体布局 */
.teacher-page {
  display: flex;
  min-height: 100vh;
  font-family: Arial, sans-serif;
  margin: 0;
  background-color: #f5f7fa;
}

/* 主内容区样式 */
.main-content {
  margin-left: 250px;
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

/* 欢迎区域 */
.welcome-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  background-color: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.welcome-header h1 {
  margin: 0;
  font-size: 24px;
  color: #0052d9;
}

.welcome-subtitle {
  color: #888;
  margin-top: 8px;
}

/* 统计卡片 */
.stats-overview {
  margin-bottom: 24px;
}

.stat-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #0052d9;
  margin-bottom: 8px;
}

.stat-title {
  font-size: 14px;
  color: #666;
}

.stat-trend {
  display: flex;
  align-items: center;
  margin-top: 8px;
}

.trend-text {
  margin-left: 8px;
  font-size: 12px;
  color: #999;
}

/* 主要内容区 */
.dashboard-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

/* 左侧内容 */
.dashboard-left {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.chart-card {
  margin-bottom: 0;
}

.chart-container {
  height: 300px;
  width: 100%;
}

/* 右侧内容 */
.dashboard-right {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.feature-card, .todo-card, .questions-card {
  margin-bottom: 0;
}

.feature-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 16px;
  border-radius: 8px;
  background-color: #f5f7fa;
  cursor: pointer;
  transition: all 0.3s;
}

.feature-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  background-color: #e9f1ff;
}

.feature-item i {
  font-size: 24px;
  margin-bottom: 12px;
  color: #0052d9;
}

.feature-info h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 4px;
}

.feature-info p {
  margin: 0;
  font-size: 12px;
  color: #888;
}

.empty-todos, .empty-questions {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100px;
  color: #999;
}

.todo-item, .question-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.todo-content, .question-content {
  flex: 1;
  margin-right: 16px;
}

.todo-title {
  font-weight: 500;
  margin-bottom: 4px;
}

.todo-description, .question-content {
  font-size: 14px;
  color: #666;
}

.question-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.student-name {
  font-weight: 500;
}

.question-time {
  font-size: 12px;
  color: #999;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .dashboard-content {
    grid-template-columns: 1fr;
  }

  .welcome-section {
    flex-direction: column;
    align-items: flex-start;
  }
}

@media (max-width: 768px) {
  .main-content {
    margin-left: 50px;
    padding: 16px;
  }

  .feature-item {
    padding: 12px;
  }

  .todo-item, .question-item {
    flex-direction: column;
  }

  .todo-content, .question-content {
    margin-right: 0;
    margin-bottom: 12px;
  }
}

@media (max-width: 480px) {
  .main-content {
    margin-left: 0;
    padding-top: 60px;
  }

  .welcome-section {
    padding: 16px;
  }

  .welcome-header h1 {
    font-size: 20px;
  }

  .stat-value {
    font-size: 24px;
  }
}
</style>