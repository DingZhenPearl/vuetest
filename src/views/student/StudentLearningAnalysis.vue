<template>
  <div class="learning-analysis-container">
    <StudentNavbar />
    <div class="main-content">
      <div class="page-header">
        <h1>个性化学习分析</h1>
        <p class="subtitle">基于您的学习行为和表现，为您提供个性化学习建议</p>
      </div>

      <!-- 加载状态 -->
      <div v-if="isLoading" class="loading-container">
        <el-skeleton :rows="10" animated />
      </div>

      <div v-else class="analysis-content">
        <!-- 顶部统计卡片 -->
        <el-row :gutter="20" class="stats-cards">
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
                  <i class="el-icon-star-on"></i>
                  <span>{{ rec.title }}</span>
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
        <el-row :gutter="20" class="performance-section">
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
            </div>
          </template>
          <div v-if="learningBehaviorAnalysis" class="behavior-analysis">
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
      isLoading: true,
      isLoadingRecommendations: true,
      studentId: '',
      overallStats: [
        { title: '已完成习题', value: 0, icon: 'el-icon-check' },
        { title: '平均完成率', value: '0%', icon: 'el-icon-data-line' },
        { title: '学习时长', value: '0小时', icon: 'el-icon-time' },
        { title: '待完成习题', value: 0, icon: 'el-icon-document' }
      ],
      recommendations: [],
      learningBehaviorAnalysis: null,
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
      this.isLoading = true
      
      // 获取学生ID
      const profile = JSON.parse(sessionStorage.getItem('userProfile') || '{}')
      this.studentId = profile.studentId || ''
      
      if (!this.studentId) {
        this.$message.error('未找到学生信息，请先完善个人资料')
        this.isLoading = false
        return
      }
      
      try {
        // 加载学习数据
        await this.loadLearningData()
        
        // 加载个性化推荐
        await this.loadRecommendations()
        
        // 初始化图表
        this.$nextTick(() => {
          this.initCharts()
        })
      } catch (error) {
        console.error('加载学习分析数据失败:', error)
        this.$message.error('加载学习分析数据失败')
      } finally {
        this.isLoading = false
      }
    },
    async loadLearningData() {
      try {
        const response = await axios.get(`/api/coding/stats/${encodeURIComponent(this.studentId)}`)
        const data = response.data
        
        if (data.success && data.data) {
          // 更新统计数据
          this.updateStats(data.data)
          
          // 更新学习行为分析
          this.updateLearningBehaviorAnalysis(data.data)
        }
      } catch (error) {
        console.error('获取学习数据失败:', error)
        throw error
      }
    },
    async loadRecommendations() {
      this.isLoadingRecommendations = true
      try {
        const response = await axios.get(`/api/learning/recommendations/${encodeURIComponent(this.studentId)}`)
        const data = response.data
        
        if (data.success && data.recommendations) {
          this.recommendations = data.recommendations
        } else {
          this.recommendations = []
        }
      } catch (error) {
        console.error('获取学习推荐失败:', error)
        this.recommendations = []
      } finally {
        this.isLoadingRecommendations = false
      }
    },
    updateStats(data) {
      // 更新统计卡片数据
      if (data.student_stats) {
        const stats = data.student_stats
        this.overallStats[0].value = stats.completed_problems || 0
        this.overallStats[1].value = `${stats.completion_rate || 0}%`
        this.overallStats[2].value = this.formatTime(stats.total_learning_time || 0)
        this.overallStats[3].value = stats.pending_problems || 0
      }
    },
    updateLearningBehaviorAnalysis(data) {
      // 更新学习行为分析
      if (data.learning_behavior) {
        this.learningBehaviorAnalysis = data.learning_behavior
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
      // 示例数据，实际应从API获取
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
            name: '学习进度',
            type: 'pie',
            radius: '50%',
            data: [
              { value: 60, name: '已完成' },
              { value: 40, name: '未完成' }
            ],
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
    },
    renderPerformanceChart() {
      // 示例数据，实际应从API获取
      const option = {
        tooltip: {
          trigger: 'axis'
        },
        legend: {
          data: ['解题时间', '尝试次数']
        },
        xAxis: {
          type: 'category',
          data: ['简单', '中等', '困难']
        },
        yAxis: {
          type: 'value'
        },
        series: [
          {
            name: '解题时间',
            type: 'bar',
            data: [5, 15, 30]
          },
          {
            name: '尝试次数',
            type: 'bar',
            data: [1, 3, 5]
          }
        ]
      }
      
      this.charts.performance.setOption(option)
    },
    refreshRecommendations() {
      this.loadRecommendations()
    },
    startLearning(recommendation) {
      if (recommendation.problemId) {
        this.$router.push(`/student/exams?problem=${recommendation.problemId}`)
      } else {
        this.$message.info('即将开始学习该内容')
      }
    },
    markAsRead(recommendation, index) {
      // 实际应调用API标记为已读
      this.recommendations.splice(index, 1)
      this.$message.success('已标记为已读')
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
</style>
