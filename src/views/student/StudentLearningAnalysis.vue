<template>
  <div class="learning-analysis-container">
    <StudentNavbar />
    <div class="main-content">
      <div class="page-header">
        <h1>个性化学习分析</h1>
        <p class="subtitle">基于您的学习行为和表现，使用大模型为您提供个性化学习建议</p>
      </div>

      <div class="analysis-content">
        <!-- 错误信息显示区域 -->
        <el-alert
          v-if="hasError"
          :title="errorTitle"
          :description="errorMessage"
          type="error"
          show-icon
          :closable="false"
          class="error-alert"
        />

        <!-- 顶部统计卡片 -->
        <div v-if="isLoadingStats" class="loading-stats">
          <el-skeleton :rows="1" animated>
            <template #template>
              <el-row :gutter="20">
                <el-col :xs="24" :sm="12" :md="6" v-for="i in 4" :key="i">
                  <el-skeleton-item variant="p" style="height: 80px" />
                </el-col>
              </el-row>
            </template>
          </el-skeleton>
        </div>
        <el-row v-else :gutter="20" class="stats-cards">
          <el-col :xs="24" :sm="12" :md="6" v-for="stat in overallStats" :key="stat.title">
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

        <!-- 学习路径推荐 -->
        <el-card class="recommendation-card">
          <template #header>
            <div class="card-header">
              <span>个性化学习路径推荐</span>
              <el-button type="primary" size="small" @click="refreshRecommendations">刷新推荐</el-button>
            </div>
          </template>
          <div v-if="isLoadingRecommendations" class="loading-recommendations">
            <el-skeleton :rows="3" animated />
          </div>
          <div v-else-if="recommendations.length === 0" class="no-recommendations">
            <p>暂无学习推荐，请先完成一些习题以获取个性化推荐。</p>
          </div>
          <div v-else class="recommendations-list">
            <div v-for="(rec, index) in recommendations" :key="index" class="recommendation-item">
              <div class="recommendation-header">
                <div class="recommendation-title">
                  <i :class="rec.chapterId ? 'el-icon-reading' : 'el-icon-star-on'"></i>
                  <span>{{ rec.title }}</span>
                  <el-tag v-if="rec.chapterId" size="mini" type="success" class="chapter-tag">章节学习</el-tag>
                </div>
                <div class="recommendation-tag" :class="getTagClass(rec.priority)">
                  {{ getPriorityLabel(rec.priority) }}
                </div>
              </div>
              <div class="recommendation-content">
                <p>{{ rec.description }}</p>
              </div>
              <div class="recommendation-resources" v-if="rec.resources && rec.resources.length > 0">
                <h4>推荐资源:</h4>
                <ul>
                  <li v-for="(resource, rIndex) in rec.resources" :key="rIndex">
                    <a :href="resource.url" target="_blank" v-if="resource.url">{{ resource.title }}</a>
                    <span v-else>{{ resource.title }}</span>
                    <span class="resource-description" v-if="resource.description"> - {{ resource.description }}</span>
                  </li>
                </ul>
              </div>
              <div class="recommendation-actions">
                <el-button type="primary" size="small" @click="startLearning(rec)" v-if="rec.actionable">开始学习</el-button>
                <el-button type="info" size="small" @click="markAsRead(rec, index)">标记为已读</el-button>
              </div>
            </div>
          </div>
        </el-card>

        <!-- 学习进度和表现 -->
        <div v-if="isLoadingCharts" class="loading-charts">
          <el-skeleton :rows="1" animated>
            <template #template>
              <el-row :gutter="20">
                <el-col :xs="24" :md="12" v-for="i in 2" :key="i">
                  <el-skeleton-item variant="p" style="height: 300px" />
                </el-col>
              </el-row>
            </template>
          </el-skeleton>
        </div>
        <el-row v-else :gutter="20" class="performance-section">
          <el-col :xs="24" :md="12">
            <el-card class="analysis-card">
              <template #header>
                <div class="card-header">
                  <span>学习进度</span>
                </div>
              </template>
              <div ref="progressChart" class="chart-container"></div>
            </el-card>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-card class="analysis-card">
              <template #header>
                <div class="card-header">
                  <span>解题表现</span>
                </div>
              </template>
              <div ref="performanceChart" class="chart-container"></div>
            </el-card>
          </el-col>
        </el-row>

        <!-- 学习行为分析 -->
        <el-card class="analysis-card">
          <template #header>
            <div class="card-header">
              <span>学习行为分析</span>
              <el-button type="primary" size="small" @click="refreshBehaviorAnalysis" :loading="isLoadingBehaviorAnalysis">
                更新分析
              </el-button>
            </div>
          </template>
          <!-- 局部加载状态 -->
          <div v-if="isLoadingBehaviorAnalysis" class="loading-behavior-analysis">
            <el-skeleton :rows="6" animated />
          </div>
          <div v-else-if="learningBehaviorAnalysis" class="behavior-analysis">
            <div class="analysis-section">
              <h3>学习模式分析</h3>
              <p>{{ learningBehaviorAnalysis.pattern }}</p>
            </div>
            <div class="analysis-section">
              <h3>优势领域</h3>
              <p>{{ learningBehaviorAnalysis.strengths }}</p>
            </div>
            <div class="analysis-section">
              <h3>待提升领域</h3>
              <p>{{ learningBehaviorAnalysis.weaknesses }}</p>
            </div>
            <div class="analysis-section">
              <h3>学习建议</h3>
              <p>{{ learningBehaviorAnalysis.suggestions }}</p>
            </div>
          </div>
          <div v-else class="no-data">
            <p>暂无学习行为分析数据，请完成更多习题以获取分析。</p>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script>
import StudentNavbar from '@/components/student/StudentNavbar.vue'
import * as echarts from 'echarts'
import axios from 'axios'

export default {
  name: 'StudentLearningAnalysis',
  components: {
    StudentNavbar
  },
  data() {
    return {
      isLoadingStats: true,
      isLoadingRecommendations: true,
      isLoadingBehaviorAnalysis: false,
      isLoadingCharts: true,
      studentId: '',
      hasError: false,
      errorTitle: '',
      errorMessage: '',
      overallStats: [
        { title: '已完成习题', value: 0, icon: 'el-icon-check' },
        { title: '平均完成率', value: '0%', icon: 'el-icon-data-line' },
        { title: '学习时长', value: '0小时', icon: 'el-icon-time' },
        { title: '待完成习题', value: 0, icon: 'el-icon-document' }
      ],
      recommendations: [],
      learningBehaviorAnalysis: null,
      chartData: {
        progress: null,
        performance: null
      },
      charts: {
        progress: null,
        performance: null
      }
    }
  },
  mounted() {
    this.initData()
  },
  beforeUnmount() {
    // 销毁图表实例
    if (this.charts.progress) {
      this.charts.progress.dispose()
    }
    if (this.charts.performance) {
      this.charts.performance.dispose()
    }
  },
  methods: {
    async initData() {
      // 重置错误状态
      this.hasError = false
      this.errorTitle = ''
      this.errorMessage = ''

      // 获取学生ID
      const profile = JSON.parse(sessionStorage.getItem('userProfile') || '{}')
      this.studentId = profile.studentId || ''

      if (!this.studentId) {
        this.showError('未找到学生信息', '请先完善个人资料')
        this.isLoadingStats = false
        this.isLoadingRecommendations = false
        this.isLoadingCharts = false
        return
      }

      try {
        // 并行加载各部分数据
        await Promise.all([
          this.loadStats(),
          this.loadRecommendations(),
          this.loadBehaviorAnalysis(),
          this.loadChartData()
        ])
      } catch (error) {
        console.error('加载学习分析数据失败:', error)
        this.showError('加载学习分析数据失败', error.message || '未知错误')
      }
    },
    // 加载统计数据
    async loadStats() {
      this.isLoadingStats = true
      try {
        console.log('正在获取学生学习统计数据，学生ID:', this.studentId)
        const response = await axios.get(`/api/learning/student-data/${encodeURIComponent(this.studentId)}`)
        const data = response.data
        console.log('收到学习统计数据:', data)

        if (data.success && data.data) {
          // 更新统计数据
          this.updateStats(data.data)
        } else {
          console.warn('学习统计数据获取失败或为空:', data.message || '未知原因')
          // 显示错误信息
          this.showError('学习统计数据获取失败', data.message || '未知原因')
        }
      } catch (error) {
        console.error('获取学习统计数据失败:', error)
        // 显示错误信息
        this.showError('学习统计数据获取失败', error.message || '未知错误')
      } finally {
        this.isLoadingStats = false
      }
    },

    // 加载行为分析数据
    async loadBehaviorAnalysis() {
      try {
        console.log('正在获取学习行为分析数据，学生ID:', this.studentId)
        await this.fetchBehaviorAnalysis(false)
      } catch (error) {
        console.error('获取学习行为分析失败:', error)
        // 显示错误信息
        this.showError('学习行为分析数据获取失败', error.message || '未知错误')
      }
    },

    // 加载图表数据
    async loadChartData() {
      this.isLoadingCharts = true
      try {
        console.log('正在获取图表数据，学生ID:', this.studentId)
        const behaviorResponse = await axios.get(`/api/learning/behavior-analysis/${encodeURIComponent(this.studentId)}`)
        const behaviorData = behaviorResponse.data

        if (behaviorData.success && behaviorData.data) {
          // 更新图表数据
          this.updateChartData(behaviorData.data)

          // 初始化图表
          this.$nextTick(() => {
            this.initCharts()
          })
        } else {
          console.warn('图表数据获取失败:', behaviorData.message || '未知原因')
          this.showError('图表数据获取失败', behaviorData.message || '未知原因')
        }
      } catch (error) {
        console.error('获取图表数据失败:', error)
        this.showError('获取图表数据失败', error.message || '未知错误')
      } finally {
        this.isLoadingCharts = false
      }
    },
    async loadRecommendations() {
      this.isLoadingRecommendations = true
      try {
        console.log(`开始为学生 ${this.studentId} 加载个性化学习推荐...`)
        const response = await axios.get(`/api/learning/recommendations/${encodeURIComponent(this.studentId)}`)
        const data = response.data
        console.log('收到推荐数据:', data)

        if (data.success && data.recommendations) {
          this.recommendations = data.recommendations
          console.log(`成功加载 ${this.recommendations.length} 条推荐`)

          // 统计章节推荐和题目推荐
          const chapterRecs = this.recommendations.filter(rec => rec.chapterId)
          const problemRecs = this.recommendations.filter(rec => rec.problemId)
          console.log(`包含 ${chapterRecs.length} 条章节推荐和 ${problemRecs.length} 条题目推荐`)

          // 打印章节推荐详情
          if (chapterRecs.length > 0) {
            console.log('章节推荐详情:')
            chapterRecs.forEach(rec => {
              console.log(`- ${rec.title} (章节ID: ${rec.chapterId})`)
            })
          }
        } else {
          console.warn('获取学习推荐失败:', data.message || '未知原因')
          this.showError('获取学习推荐失败', data.message || '未知原因')
          this.recommendations = []
          throw new Error(data.message || '获取学习推荐失败')
        }
      } catch (error) {
        console.error('获取学习推荐失败:', error)
        this.showError('获取学习推荐失败', error.message || '未知错误')
        this.recommendations = []
        throw error
      } finally {
        this.isLoadingRecommendations = false
      }
    },
    updateStats(data) {
      // 更新统计卡片数据
      if (data.student_stats) {
        const stats = data.student_stats
        console.log('更新统计卡片数据:', stats)
        this.overallStats[0].value = stats.completed_problems || 0
        this.overallStats[1].value = `${stats.completion_rate || 0}%`
        this.overallStats[2].value = this.formatTime(stats.total_learning_time || 0)
        this.overallStats[3].value = stats.pending_problems || 0
      } else {
        console.warn('未找到student_stats数据:', data)
        // 尝试从其他数据结构中提取统计信息
        if (data.problem_stats) {
          const problemStats = data.problem_stats
          const completedProblems = problemStats.solved_problems || 0
          const totalProblems = problemStats.total_problems || 0
          const completionRate = totalProblems > 0 ? Math.round((completedProblems / totalProblems) * 100) : 0
          const avgTimeSpent = problemStats.avg_time_spent || 0
          const totalLearningTime = Math.round(avgTimeSpent * completedProblems / 60) // 转换为分钟

          console.log('从problem_stats提取统计数据:', {
            completedProblems,
            totalProblems,
            completionRate,
            totalLearningTime
          })

          this.overallStats[0].value = completedProblems
          this.overallStats[1].value = `${completionRate}%`
          this.overallStats[2].value = this.formatTime(totalLearningTime)
          this.overallStats[3].value = totalProblems - completedProblems
        }
      }
    },
    updateLearningBehaviorAnalysis(data) {
      // 更新学习行为分析
      console.log('收到学习行为分析数据:', data)

      try {
        if (data.behavior_analysis) {
          // 检查是否有必要的字段
          const analysis = data.behavior_analysis
          const requiredFields = ['pattern', 'strengths', 'weaknesses', 'suggestions']
          const missingFields = requiredFields.filter(field => !analysis[field])

          if (missingFields.length > 0) {
            console.warn(`学习行为分析数据缺少字段: ${missingFields.join(', ')}`)
            // 为缺失字段设置默认值
            if (!analysis.pattern) {
              analysis.pattern = "您尚未完成足够的习题，无法生成详细的学习模式分析。建议先完成一些基础习题，以便系统能够分析您的学习行为。"
            }
            if (!analysis.strengths) {
              analysis.strengths = "暂无足够数据分析您的优势领域。请完成更多习题以获取详细分析。"
            }
            if (!analysis.weaknesses) {
              analysis.weaknesses = "暂无足够数据分析您的待提升领域。请完成更多习题以获取详细分析。"
            }
            if (!analysis.suggestions) {
              analysis.suggestions = "建议从基础习题开始，逐步提高难度。定期练习，保持学习的连续性。尝试不同类型的题目，拓展知识面。"
            }
          }

          // 检查是否是默认的空数据或者只包含标题
          if (analysis.pattern === "学习模式分析" ||
              analysis.pattern === "详细的学习模式分析内容，不要只写标题" ||
              (analysis.strengths && analysis.strengths.includes("无显著优势领域"))) {
            console.warn('收到默认的空学习行为分析数据或只包含标题')
            // 显示提示信息
            this.$message.info('正在重新获取学习行为分析...')
            // 自动刷新分析
            setTimeout(() => {
              this.refreshBehaviorAnalysis()
            }, 1000)
          }

          // 保存分析数据
          this.learningBehaviorAnalysis = analysis
          console.log('使用behavior_analysis数据:', this.learningBehaviorAnalysis)
        } else if (data.learning_behavior) {
          // 兼容旧数据结构
          const analysis = data.learning_behavior

          // 检查必要字段
          if (!analysis.pattern) {
            analysis.pattern = "您尚未完成足够的习题，无法生成详细的学习模式分析。建议先完成一些基础习题，以便系统能够分析您的学习行为。"
          }
          if (!analysis.strengths) {
            analysis.strengths = "暂无足够数据分析您的优势领域。请完成更多习题以获取详细分析。"
          }
          if (!analysis.weaknesses) {
            analysis.weaknesses = "暂无足够数据分析您的待提升领域。请完成更多习题以获取详细分析。"
          }
          if (!analysis.suggestions) {
            analysis.suggestions = "建议从基础习题开始，逐步提高难度。定期练习，保持学习的连续性。尝试不同类型的题目，拓展知识面。"
          }

          this.learningBehaviorAnalysis = analysis
          console.log('使用learning_behavior数据:', this.learningBehaviorAnalysis)
        } else {
          console.warn('未找到有效的学习行为分析数据，使用默认数据')
          // 使用默认数据而不是抛出错误
          this.learningBehaviorAnalysis = {
            pattern: "您尚未完成足够的习题，无法生成详细的学习模式分析。建议先完成一些基础习题，以便系统能够分析您的学习行为。",
            strengths: "暂无足够数据分析您的优势领域。请完成更多习题以获取详细分析。",
            weaknesses: "暂无足够数据分析您的待提升领域。请完成更多习题以获取详细分析。",
            suggestions: "建议从基础习题开始，逐步提高难度。定期练习，保持学习的连续性。尝试不同类型的题目，拓展知识面。"
          }
          this.$message.info('暂无学习行为分析数据，请完成更多习题以获取详细分析')
        }
      } catch (error) {
        console.error('处理学习行为分析数据时出错:', error)
        this.showError('处理学习行为分析数据时出错', error.message || '未知错误')
        // 使用默认数据
        this.learningBehaviorAnalysis = {
          pattern: "处理分析数据时出错，请稍后重试。",
          strengths: "数据处理错误，无法显示优势领域。",
          weaknesses: "数据处理错误，无法显示待提升领域。",
          suggestions: "请稍后刷新页面重试，或联系管理员解决问题。"
        }
      }
    },

    updateChartData(data) {
      // 更新图表数据
      console.log('更新图表数据:', data)
      if (!data) {
        console.warn('图表数据为空')
        this.showError('图表数据为空', '无法获取学习数据以生成图表')
        throw new Error('图表数据为空')
      }

      if (!data.learning_data) {
        console.warn('学习数据为空')
        this.showError('学习数据为空', '无法获取学习数据以生成图表')
        throw new Error('学习数据为空')
      }

      try {
        // 检查学习数据是否完整
        if (!data.learning_data.learning_stats) {
          console.warn('学习统计数据不完整')
          this.showError('学习统计数据不完整', '无法获取完整的学习统计数据以生成图表')
          throw new Error('学习统计数据不完整')
        }

        if (!data.learning_data.difficulty_stats) {
          console.warn('难度统计数据不完整')
          this.showError('难度统计数据不完整', '无法获取完整的难度统计数据以生成图表')
          throw new Error('难度统计数据不完整')
        }

        // 存储图表数据以便在初始化图表时使用
        this.chartData = {
          progress: this.prepareProgressChartData(data),
          performance: this.preparePerformanceChartData(data)
        }

        console.log('准备的图表数据:', this.chartData)

        // 如果图表已经初始化，则立即更新
        if (this.charts.progress) {
          console.log('更新进度图表')
          this.renderProgressChart()
        }

        if (this.charts.performance) {
          console.log('更新表现图表')
          this.renderPerformanceChart()
        }
      } catch (error) {
        console.error('处理图表数据时出错:', error)
        this.showError('处理图表数据时出错', error.message || '未知错误')
        throw error
      }
    },

    prepareProgressChartData(data) {
      try {
        if (!data || !data.learning_data || !data.learning_data.learning_stats) {
          console.warn('学习统计数据不完整')
          this.showError('学习统计数据不完整', '无法获取完整的学习统计数据以生成图表')
          throw new Error('学习统计数据不完整')
        }

        const learningStats = data.learning_data.learning_stats
        const totalProblems = learningStats.total_problems || 0
        const solvedProblems = learningStats.solved_problems || 0
        const pendingProblems = totalProblems - solvedProblems

        // 如果没有数据，显示错误
        if (totalProblems === 0) {
          console.warn('没有题目数据')
          this.showError('没有题目数据', '您尚未尝试任何题目，无法生成学习进度图表')
          throw new Error('没有题目数据')
        }

        return [
          { value: solvedProblems, name: '已完成' },
          { value: pendingProblems, name: '未完成' }
        ]
      } catch (error) {
        console.error('准备进度图表数据时出错:', error)
        this.showError('准备进度图表数据时出错', error.message || '未知错误')
        throw error
      }
    },

    preparePerformanceChartData(data) {
      try {
        if (!data || !data.learning_data || !data.learning_data.difficulty_stats) {
          console.warn('难度统计数据不完整')
          this.showError('难度统计数据不完整', '无法获取完整的难度统计数据以生成图表')
          throw new Error('难度统计数据不完整')
        }

        const difficultyStats = data.learning_data.difficulty_stats

        // 如果没有数据，显示错误
        if (!difficultyStats || !difficultyStats.length) {
          console.warn('没有难度统计数据')
          this.showError('没有难度统计数据', '无法获取难度统计数据以生成图表')
          throw new Error('没有难度统计数据')
        }

        // 准备数据
        const categories = []
        const timeData = []
        const attemptsData = []

        // 按难度级别排序
        const sortOrder = { '简单': 0, '中等': 1, '困难': 2, 'easy': 0, 'medium': 1, 'hard': 2 }
        const sortedStats = [...difficultyStats].sort((a, b) => {
          return (sortOrder[a.difficulty] || 0) - (sortOrder[b.difficulty] || 0)
        })

        sortedStats.forEach(stat => {
          // 处理可能的英文难度级别
          let difficulty = stat.difficulty
          if (difficulty === 'easy') difficulty = '简单'
          if (difficulty === 'medium') difficulty = '中等'
          if (difficulty === 'hard') difficulty = '困难'

          categories.push(difficulty)
          timeData.push(Math.round((stat.avg_time_spent || 0) / 60)) // 转换为分钟
          attemptsData.push(stat.attempted_problems || 0)
        })

        return {
          categories,
          series: [
            {
              name: '平均解题时间(分钟)',
              type: 'bar',
              data: timeData
            },
            {
              name: '尝试题目数',
              type: 'bar',
              data: attemptsData
            }
          ]
        }
      } catch (error) {
        console.error('准备表现图表数据时出错:', error)
        this.showError('准备表现图表数据时出错', error.message || '未知错误')
        throw error
      }
    },
    initCharts() {
      // 初始化进度图表
      if (this.$refs.progressChart) {
        this.charts.progress = echarts.init(this.$refs.progressChart)
        this.renderProgressChart()
      }

      // 初始化表现图表
      if (this.$refs.performanceChart) {
        this.charts.performance = echarts.init(this.$refs.performanceChart)
        this.renderPerformanceChart()
      }
    },
    renderProgressChart() {
      try {
        if (!this.chartData || !this.chartData.progress) {
          console.warn('进度图表数据不完整')
          this.showError('进度图表数据不完整', '无法获取完整的进度图表数据')
          return
        }

        const chartData = this.chartData.progress

        const option = {
          tooltip: {
            trigger: 'item',
            formatter: '{a} <br/>{b}: {c} ({d}%)'
          },
          legend: {
            orient: 'vertical',
            left: 'left',
            data: chartData.map(item => item.name)
          },
          series: [
            {
              name: '学习进度',
              type: 'pie',
              radius: '50%',
              data: chartData,
              emphasis: {
                itemStyle: {
                  shadowBlur: 10,
                  shadowOffsetX: 0,
                  shadowColor: 'rgba(0, 0, 0, 0.5)'
                }
              }
            }
          ]
        }

        this.charts.progress.setOption(option)
      } catch (error) {
        console.error('渲染进度图表时出错:', error)
        this.showError('渲染进度图表时出错', error.message || '未知错误')
      }
    },
    renderPerformanceChart() {
      try {
        if (!this.chartData || !this.chartData.performance) {
          console.warn('表现图表数据不完整')
          this.showError('表现图表数据不完整', '无法获取完整的表现图表数据')
          return
        }

        const chartData = this.chartData.performance

        const option = {
          tooltip: {
            trigger: 'axis',
            axisPointer: {
              type: 'shadow'
            }
          },
          legend: {
            data: chartData.series.map(item => item.name)
          },
          grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
          },
          xAxis: {
            type: 'category',
            data: chartData.categories
          },
          yAxis: {
            type: 'value'
          },
          series: chartData.series
        }

        this.charts.performance.setOption(option)
      } catch (error) {
        console.error('渲染表现图表时出错:', error)
        this.showError('渲染表现图表时出错', error.message || '未知错误')
      }
    },
    async refreshRecommendations() {
      try {
        this.isLoadingRecommendations = true
        await axios.get(`/api/learning/recommendations/${encodeURIComponent(this.studentId)}?refresh=true`)
        await this.loadRecommendations()
        this.$message.success('推荐已更新')
      } catch (error) {
        console.error('刷新推荐失败:', error)
        this.$message.error('刷新推荐失败: ' + (error.message || '未知错误'))
      } finally {
        this.isLoadingRecommendations = false
      }
    },

    // 获取学习行为分析数据
    async fetchBehaviorAnalysis(showLoading = true) {
      try {
        if (showLoading) {
          this.isLoadingBehaviorAnalysis = true
        } else {
          // 初始加载时也设置加载状态
          this.isLoadingBehaviorAnalysis = true
        }

        const behaviorResponse = await axios.get(`/api/learning/behavior-analysis/${encodeURIComponent(this.studentId)}`)
        const behaviorData = behaviorResponse.data
        console.log('收到学习行为分析数据:', behaviorData)

        if (behaviorData.success && behaviorData.data) {
          // 更新学习行为分析
          this.updateLearningBehaviorAnalysis(behaviorData.data)

          if (showLoading) {
            this.$message.success('学习行为分析已更新')
          }
        } else {
          console.warn('学习行为分析数据获取失败:', behaviorData.message || '未知原因')
          // 显示错误信息
          this.showError('学习行为分析数据获取失败', behaviorData.message || '未知原因')
          throw new Error(behaviorData.message || '学习行为分析数据获取失败')
        }
      } catch (error) {
        console.error('获取学习行为分析失败:', error)
        if (showLoading) {
          this.$message.error('获取学习行为分析失败: ' + (error.message || '未知错误'))
        }
        throw error
      } finally {
        this.isLoadingBehaviorAnalysis = false
      }
    },

    // 刷新学习行为分析
    async refreshBehaviorAnalysis() {
      try {
        await this.fetchBehaviorAnalysis(true)
      } catch (error) {
        console.error('刷新学习行为分析失败:', error)
      }
    },
    startLearning(recommendation) {
      console.log('开始学习推荐内容:', recommendation)

      if (recommendation.problemId) {
        // 如果有题目ID，跳转到习题页面
        console.log(`跳转到题目: ${recommendation.problemId}`)
        this.$router.push(`/student/exams?problem=${recommendation.problemId}`)
      } else if (recommendation.chapterId) {
        // 如果有章节ID，跳转到编程概念页面并打开对应章节
        console.log(`跳转到章节: ${recommendation.chapterId}`)
        this.$router.push({
          path: '/student/programming-concepts',
          query: { chapter: recommendation.chapterId }
        })
        this.$message.success(`正在前往学习${recommendation.title}`)
      } else {
        console.log('没有找到可跳转的内容')
        this.$message.info('即将开始学习该内容')
      }
    },
    async markAsRead(recommendation, index) {
      try {
        // 调用API标记为已读
        await axios.post(`/api/learning/recommendations/${recommendation.id}/read`, {
          studentId: this.studentId
        })

        // 从列表中移除
        this.recommendations.splice(index, 1)
        this.$message.success('已标记为已读')
      } catch (error) {
        console.error('标记为已读失败:', error)
        this.$message.error('标记为已读失败，请重试')
      }
    },
    getTagClass(priority) {
      switch (priority) {
        case 'high': return 'tag-high'
        case 'medium': return 'tag-medium'
        case 'low': return 'tag-low'
        default: return ''
      }
    },
    getPriorityLabel(priority) {
      switch (priority) {
        case 'high': return '优先'
        case 'medium': return '推荐'
        case 'low': return '可选'
        default: return '推荐'
      }
    },
    formatTime(minutes) {
      const hours = Math.floor(minutes / 60)
      const mins = minutes % 60
      return `${hours}小时${mins}分钟`
    },

    // 显示错误信息
    showError(title, message) {
      console.error(`${title}: ${message}`)
      this.$message.error(`${title}: ${message}`)
      this.hasError = true
      this.errorTitle = title
      this.errorMessage = message
    }
  }
}
</script>

<style scoped>
.learning-analysis-container {
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
  margin-bottom: 20px;
}

.page-header h1 {
  margin-bottom: 5px;
  color: #303133;
}

.subtitle {
  color: #606266;
  font-size: 14px;
}

.loading-container {
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

.stat-value {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 5px;
}

.stat-title {
  font-size: 14px;
  color: #606266;
}

.recommendation-card,
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
}

.recommendation-item {
  border-bottom: 1px solid #EBEEF5;
  padding: 15px 0;
}

.recommendation-item:last-child {
  border-bottom: none;
}

.recommendation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.recommendation-title {
  font-size: 16px;
  font-weight: bold;
  display: flex;
  align-items: center;
}

.recommendation-title i {
  color: #E6A23C;
  margin-right: 5px;
}

.recommendation-title i.el-icon-reading {
  color: #409EFF;
}

.chapter-tag {
  margin-left: 8px;
  font-size: 10px;
  padding: 0 5px;
  height: 18px;
  line-height: 16px;
}

.recommendation-tag {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.tag-high {
  background-color: #F56C6C;
  color: white;
}

.tag-medium {
  background-color: #E6A23C;
  color: white;
}

.tag-low {
  background-color: #67C23A;
  color: white;
}

.recommendation-content {
  margin-bottom: 10px;
}

.recommendation-resources {
  background-color: #F5F7FA;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 10px;
}

.recommendation-resources h4 {
  margin-top: 0;
  margin-bottom: 5px;
}

.recommendation-resources ul {
  margin: 0;
  padding-left: 20px;
}

.resource-description {
  color: #909399;
  font-size: 12px;
}

.recommendation-actions {
  display: flex;
  justify-content: flex-end;
}

.behavior-analysis {
  padding: 10px;
}

.analysis-section {
  margin-bottom: 15px;
}

.analysis-section h3 {
  margin-top: 0;
  margin-bottom: 10px;
  font-size: 16px;
  color: #303133;
}

.no-data,
.no-recommendations {
  text-align: center;
  padding: 20px;
  color: #909399;
}

.performance-section {
  margin-bottom: 20px;
}

.error-alert {
  margin-bottom: 20px;
}
</style>
