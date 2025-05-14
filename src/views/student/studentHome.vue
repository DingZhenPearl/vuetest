<template>
  <div class="student-page">
    <!-- 导航侧边栏 -->
    <StudentNavbar />

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 个人信息提示卡片 -->
      <t-alert v-if="!isLoading && !hasProfileInfo" theme="warning" message="请完善个人信息" class="profile-alert">
        <template #description>
          <div class="alert-content">
            <p>请设置您的学号和班级等基本信息，以便更好地使用平台功能。</p>
            <t-button theme="warning" variant="outline" @click="goToProfile">设置个人信息</t-button>
          </div>
        </template>
      </t-alert>

      <!-- 欢迎区域 -->
      <div class="welcome-section">
        <div class="welcome-header">
          <h1>欢迎回来，{{ userName || '同学' }}</h1>
          <p class="welcome-subtitle">今天是 {{ currentDate }}，祝您学习愉快！</p>
        </div>
        <div class="user-stats">
          <t-statistic title="学习天数" :value="userStats.studyDays" trend="up" />
          <t-statistic title="完成习题" :value="userStats.completedProblems" trend="up" />
          <t-statistic title="学习时长" :value="userStats.studyHours + '小时'" />
        </div>
      </div>

      <!-- 主要内容区 -->
      <div class="dashboard-content">
        <!-- 左侧内容 -->
        <div class="dashboard-left">
          <!-- 学习进度概览 -->
          <t-card title="学习进度概览" class="progress-card">
            <template #actions>
              <t-button theme="primary" variant="text" @click="refreshProgressChart">
                <i class="el-icon-refresh"></i> 刷新
              </t-button>
            </template>
            <div class="progress-container" ref="progressChartContainer"></div>
          </t-card>

          <!-- 快捷功能卡片 -->
          <t-card title="快捷功能" class="feature-card">
            <t-row :gutter="[16, 16]">
              <t-col :xs="12" :sm="12" :md="6" :lg="6" :xl="6" v-for="(feature, index) in features" :key="index">
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
        </div>

        <!-- 右侧内容 -->
        <div class="dashboard-right">
          <!-- 个性化学习推荐 -->
          <t-card title="个性化学习推荐" class="recommendation-card">
            <template #actions>
              <t-button theme="primary" variant="text" @click="refreshRecommendations">
                <i class="el-icon-refresh"></i> 刷新
              </t-button>
            </template>
            <!-- 局部加载状态 -->
            <t-loading :loading="isLoadingRecommendations" overlay>
              <template #tip>
                <span>正在获取推荐...</span>
              </template>
              <div v-if="recommendations.length === 0" class="empty-recommendations">
                <p>暂无学习推荐，请先完成一些习题</p>
              </div>
              <div v-else class="recommendation-list">
                <div v-for="(item, index) in recommendations" :key="index" class="recommendation-item">
                  <div class="recommendation-icon">
                    <i :class="getRecommendationIcon(item.type)"></i>
                  </div>
                  <div class="recommendation-content">
                    <h4>{{ item.title }}</h4>
                    <p>{{ item.description }}</p>
                  </div>
                </div>
              </div>
            </t-loading>
          </t-card>

          <!-- 最近活动 -->
          <t-card title="最近活动" class="activity-card">
            <template #actions>
              <t-button theme="primary" variant="text" @click="refreshActivities">
                <i class="el-icon-refresh"></i> 刷新
              </t-button>
            </template>
            <t-list v-if="activities.length > 0">
              <t-list-item v-for="(activity, index) in activities" :key="index">
                <template #content>
                  <div class="activity-item">
                    <div class="activity-time">{{ formatTime(activity.time) }}</div>
                    <div class="activity-content">
                      <span class="activity-type">{{ activity.type }}</span>
                      <span class="activity-description">{{ activity.description }}</span>
                    </div>
                  </div>
                </template>
              </t-list-item>
            </t-list>
            <div v-else class="empty-activities">
              <p>暂无活动记录，请完成一些习题或提问</p>
            </div>
          </t-card>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import StudentNavbar from '@/components/student/StudentNavbar.vue'
import * as echarts from 'echarts'
import axios from 'axios'

export default {
  name: 'StudentHome',
  components: {
    StudentNavbar
  },
  data() {
    return {
      hasProfileInfo: false,
      isLoading: true,
      isLoadingRecommendations: false,
      userName: '',
      studentId: '',
      currentDate: '',
      progressChart: null,
      userStats: {
        studyDays: 0,
        completedProblems: 0,
        studyHours: 0
      },
      features: [
        {
          title: '习题集',
          description: '练习编程题目',
          icon: 'el-icon-notebook-1',
          route: '/student/exams'
        },
        {
          title: 'AI对话',
          description: '智能学习助手',
          icon: 'el-icon-cpu',
          route: '/student/aiChat'
        },
        {
          title: '学习资源',
          description: '查看学习材料',
          icon: 'el-icon-edit-outline',
          route: '/student/programming-concepts'
        },
        {
          title: '学习分析',
          description: '查看学习情况',
          icon: 'el-icon-data-analysis',
          route: '/student/learning-analysis'
        },
        {
          title: '问题求助',
          description: '向老师提问',
          icon: 'el-icon-chat-line-round',
          route: '/student/question'
        },
        {
          title: '个人信息',
          description: '管理个人资料',
          icon: 'el-icon-user',
          route: '/student/profile'
        }
      ],
      recommendations: [],
      activities: []
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
      if (this.hasProfileInfo) {
        this.initProgressChart();
      }
    });
  },
  beforeUnmount() {
    // 销毁图表实例
    if (this.progressChart) {
      this.progressChart.dispose();
    }

    // 移除窗口大小变化监听
    window.removeEventListener('resize', this.resizeChart);
  },
  methods: {
    // 初始化所有数据
    async initData() {
      this.isLoading = true;

      try {
        // 先检查用户信息
        await this.checkProfileInfo();

        if (this.hasProfileInfo) {
          console.log('用户已设置个人信息，学生ID:', this.studentId);

          // 清除所有缓存数据，确保获取最新数据
          try {
            localStorage.removeItem(`progress_data_${this.studentId}`);
            localStorage.removeItem(`recommendations_${this.studentId}`);
            localStorage.removeItem(`activities_${this.studentId}`);
            localStorage.removeItem(`user_stats_${this.studentId}`);
            console.log('已清除所有缓存数据，确保获取最新数据');
          } catch (e) {
            console.error('清除缓存失败:', e);
          }

          // 先获取学习进度数据，确保图表显示正确
          console.log('开始获取学习进度数据...');
          await this.updateProgressDataCache(false);

          // 然后并行执行其他数据获取任务
          await Promise.all([
            this.fetchUserStats(),
            this.fetchRecommendations(),
            this.fetchActivities()
          ]);
        } else {
          console.warn('用户未设置个人信息，无法获取学习进度数据');
        }
      } catch (error) {
        console.error('初始化数据失败:', error);
      } finally {
        this.isLoading = false;

        // 在数据加载完成后初始化图表
        this.$nextTick(() => {
          if (this.hasProfileInfo) {
            console.log('初始化学习进度图表...');
            this.initProgressChart();
          }
        });
      }
    },

    // 设置当前日期
    setCurrentDate() {
      const now = new Date();
      const options = { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' };
      this.currentDate = now.toLocaleDateString('zh-CN', options);
    },

    // 检查用户是否已设置个人信息
    async checkProfileInfo() {
      // 先检查sessionStorage
      const profile = JSON.parse(sessionStorage.getItem('userProfile') || '{}')
      if (profile.studentId && profile.className) {
        this.hasProfileInfo = true;
        this.studentId = profile.studentId;
        return;
      }

      // 如果sessionStorage没有数据，尝试从服务器获取
      const userEmail = sessionStorage.getItem('userEmail')
      if (!userEmail) {
        this.hasProfileInfo = false;
        return;
      }

      try {
        const response = await fetch(`/api/profile/${userEmail}`);
        const data = await response.json();

        if (data.success && data.profile && data.profile.student_id && data.profile.class_name) {
          // 服务器有数据，保存到sessionStorage
          const profileData = {
            studentId: data.profile.student_id || '',
            className: data.profile.class_name || '',
            major: data.profile.major || '',
            name: data.profile.name || ''
          };

          sessionStorage.setItem('userProfile', JSON.stringify(profileData));
          this.hasProfileInfo = true;
          this.studentId = profileData.studentId;
        } else {
          this.hasProfileInfo = false;
        }
      } catch (error) {
        console.error('获取用户信息失败:', error);
        this.hasProfileInfo = false;
      }
    },

    // 获取用户统计数据
    async fetchUserStats() {
      if (!this.hasProfileInfo || !this.studentId) return;

      // 检查本地存储中是否有缓存的统计数据
      const cachedData = this.getUserStatsFromCache();
      if (cachedData) {
        console.log('使用缓存的用户统计数据');
        this.userStats = cachedData.stats;

        // 如果缓存时间超过12小时，在后台更新缓存
        if (this.isCacheExpired(cachedData.timestamp, 12)) {
          console.log('用户统计数据缓存已过期，在后台更新');
          this.updateUserStatsCache(false);
        }
        return;
      }

      // 如果没有缓存数据，从服务器获取
      await this.updateUserStatsCache(true);
    },

    // 从缓存中获取用户统计数据
    getUserStatsFromCache() {
      try {
        const cacheKey = `user_stats_${this.studentId}`;
        const cachedDataStr = localStorage.getItem(cacheKey);

        if (!cachedDataStr) return null;

        return JSON.parse(cachedDataStr);
      } catch (error) {
        console.error('读取缓存用户统计数据失败:', error);
        return null;
      }
    },

    // 更新用户统计数据缓存
    async updateUserStatsCache(showLoading = true) {
      try {
        if (showLoading) {
          // 这里不显示加载消息，避免过多的提示
        }

        const response = await axios.get(`/api/learning/student-data/${this.studentId}`);
        console.log('收到学生学习数据:', response.data);

        if (response.data.success) {
          const data = response.data.data || {};

          // 从student_stats中提取数据
          let completedProblems = 0;
          let studyHours = 0;

          if (data.student_stats) {
            const stats = data.student_stats;
            console.log('从student_stats提取数据:', stats);
            completedProblems = stats.completed_problems || 0;
            studyHours = Math.round(stats.total_learning_time / 60) || 0; // 转换为小时
          } else if (data.problem_stats) {
            // 如果没有student_stats，尝试从problem_stats中提取
            const problemStats = data.problem_stats;
            console.log('从problem_stats提取数据:', problemStats);
            completedProblems = problemStats.solved_problems || 0;
            const avgTimeSpent = problemStats.avg_time_spent || 0;
            studyHours = Math.round((avgTimeSpent * completedProblems / 60) / 60) || 0; // 转换为小时
          }

          // 计算学习天数（从所有历史活动中提取）
          let studyDays = 0;
          if (data.activity_history && Array.isArray(data.activity_history)) {
            // 计算不同的学习日期数量
            const uniqueDates = new Set();
            data.activity_history.forEach(activity => {
              if (activity.submission_date) {
                uniqueDates.add(activity.submission_date.split(' ')[0]); // 只取日期部分
              }
            });
            studyDays = uniqueDates.size || 0;
            console.log(`从活动历史中计算出学习天数: ${studyDays}天，共有${data.activity_history.length}条活动记录`);

            // 如果没有活动记录，至少设置为1天
            if (studyDays === 0 && completedProblems > 0) {
              studyDays = 1;
              console.log('没有活动记录但有完成的题目，设置学习天数为1天');
            }
          } else if (completedProblems > 0) {
            // 如果有完成的题目但没有活动记录，至少设置为1天
            studyDays = 1;
            console.log('没有活动历史数据但有完成的题目，设置学习天数为1天');
          }

          // 如果数据中有recent_activity但没有activity_history，尝试从recent_activity中提取
          if (studyDays === 0 && data.recent_activity && Array.isArray(data.recent_activity)) {
            const uniqueDates = new Set();
            data.recent_activity.forEach(activity => {
              if (activity.submission_date) {
                uniqueDates.add(activity.submission_date.split(' ')[0]);
              }
            });
            studyDays = uniqueDates.size || 0;
            console.log(`从recent_activity中计算出学习天数: ${studyDays}天，共有${data.recent_activity.length}条活动记录`);

            if (studyDays === 0 && completedProblems > 0) {
              studyDays = 1;
            }
          }

          // 更新用户统计数据
          const userStats = {
            studyDays: studyDays,
            completedProblems: completedProblems,
            studyHours: studyHours
          };

          console.log('更新用户统计数据:', userStats);

          // 更新组件数据
          this.userStats = userStats;

          // 保存到本地存储
          const cacheData = {
            stats: userStats,
            timestamp: new Date().getTime()
          };

          const cacheKey = `user_stats_${this.studentId}`;
          localStorage.setItem(cacheKey, JSON.stringify(cacheData));
        } else if (showLoading) {
          // 显示错误信息
          this.$message.error(response.data.message || '获取用户统计数据失败');
          console.error('获取用户统计数据失败:', response.data);
        }
      } catch (error) {
        if (showLoading) {
          // 显示错误信息
          this.$message.error('获取用户统计数据失败: ' + (error.message || '未知错误'));
        }
        console.error('获取用户统计数据失败:', error);
      }
    },

    // 获取个性化学习推荐
    async fetchRecommendations() {
      if (!this.hasProfileInfo || !this.studentId) return;

      // 检查本地存储中是否有缓存的推荐数据
      const cachedData = this.getRecommendationsFromCache();
      if (cachedData) {
        console.log('使用缓存的推荐数据');
        this.recommendations = cachedData.recommendations;

        // 如果缓存时间超过24小时，在后台更新缓存
        if (this.isCacheExpired(cachedData.timestamp, 24)) {
          console.log('缓存已过期，在后台更新');
          this.updateRecommendationsCache(false);
        }
        return;
      }

      // 如果没有缓存数据，从服务器获取
      await this.updateRecommendationsCache(true);
    },

    // 从缓存中获取推荐数据
    getRecommendationsFromCache() {
      try {
        const cacheKey = `recommendations_${this.studentId}`;
        const cachedDataStr = localStorage.getItem(cacheKey);

        if (!cachedDataStr) return null;

        return JSON.parse(cachedDataStr);
      } catch (error) {
        console.error('读取缓存推荐数据失败:', error);
        return null;
      }
    },

    // 检查缓存是否过期
    isCacheExpired(timestamp, hours) {
      if (!timestamp) return true;

      const now = new Date().getTime();
      const expiryTime = hours * 60 * 60 * 1000; // 转换为毫秒

      return (now - timestamp) > expiryTime;
    },

    // 更新推荐缓存
    async updateRecommendationsCache(showLoading = true) {
      try {
        if (showLoading) {
          this.isLoadingRecommendations = true;
        }

        const response = await axios.get(`/api/learning/recommendations/${this.studentId}`);

        if (response.data.success) {
          const recommendations = response.data.recommendations || [];

          // 更新组件数据
          this.recommendations = recommendations;

          // 保存到本地存储
          const cacheData = {
            recommendations: recommendations,
            timestamp: new Date().getTime()
          };

          const cacheKey = `recommendations_${this.studentId}`;
          localStorage.setItem(cacheKey, JSON.stringify(cacheData));

          if (showLoading) {
            this.$message.success('获取推荐成功');
          }
        } else if (showLoading) {
          this.$message.error(response.data.message || '获取推荐失败');
        }
      } catch (error) {
        console.error('获取学习推荐失败:', error);
        if (showLoading) {
          this.$message.error('获取推荐失败: ' + (error.message || '未知错误'));
        }
        this.recommendations = [];
      } finally {
        if (showLoading) {
          this.isLoadingRecommendations = false;
        }
      }
    },

    // 刷新推荐
    async refreshRecommendations() {
      if (!this.hasProfileInfo || !this.studentId) {
        this.$message.warning('请先完善个人信息');
        return;
      }

      try {
        this.$message.info('正在更新推荐...');
        await this.updateRecommendationsCache(true);
      } catch (error) {
        this.$message.error('更新推荐失败');
      }
    },

    // 获取用户活动记录
    async fetchActivities() {
      if (!this.hasProfileInfo || !this.studentId) return;

      // 检查本地存储中是否有缓存的活动数据
      const cachedData = this.getActivitiesFromCache();
      if (cachedData) {
        console.log('使用缓存的活动数据');
        this.activities = cachedData.activities;

        // 如果缓存时间超过6小时，在后台更新缓存
        // 活动数据变化较频繁，所以缓存时间较短
        if (this.isCacheExpired(cachedData.timestamp, 6)) {
          console.log('活动数据缓存已过期，在后台更新');
          this.updateActivitiesCache(false);
        }
        return;
      }

      // 如果没有缓存数据，从服务器获取
      await this.updateActivitiesCache(false);
    },

    // 从缓存中获取活动数据
    getActivitiesFromCache() {
      try {
        const cacheKey = `activities_${this.studentId}`;
        const cachedDataStr = localStorage.getItem(cacheKey);

        if (!cachedDataStr) return null;

        return JSON.parse(cachedDataStr);
      } catch (error) {
        console.error('读取缓存活动数据失败:', error);
        return null;
      }
    },

    // 更新活动数据缓存
    async updateActivitiesCache(showLoading = true) {
      try {
        if (showLoading) {
          this.$message.info('正在获取活动记录...');
        }

        const response = await axios.get(`/api/learning/student-activities/${this.studentId}`);

        if (response.data.success) {
          const activities = response.data.activities || [];

          // 更新组件数据
          this.activities = activities;

          // 保存到本地存储
          const cacheData = {
            activities: activities,
            timestamp: new Date().getTime()
          };

          const cacheKey = `activities_${this.studentId}`;
          localStorage.setItem(cacheKey, JSON.stringify(cacheData));

          if (showLoading) {
            if (activities.length > 0) {
              this.$message.success('活动记录已更新');
            } else {
              this.$message.info('暂无活动记录');
            }
          }
        } else {
          this.activities = [];
          if (showLoading) {
            this.$message.warning(response.data.message || '暂无活动记录');
          }
        }
      } catch (error) {
        console.error('获取活动记录失败:', error);
        this.activities = [];
        if (showLoading) {
          this.$message.error('获取活动记录失败: ' + (error.message || '未知错误'));
        }
      }
    },

    // 刷新活动记录
    async refreshActivities() {
      if (!this.hasProfileInfo || !this.studentId) {
        this.$message.warning('请先完善个人信息');
        return;
      }

      // 清除缓存
      try {
        localStorage.removeItem(`activities_${this.studentId}`);
      } catch (error) {
        console.error('清除活动数据缓存失败:', error);
      }

      // 重新获取数据
      await this.updateActivitiesCache(true);
    },

    // 初始化进度图表
    initProgressChart() {
      console.log('开始初始化进度图表...');

      if (!this.$refs.progressChartContainer) {
        console.warn('图表容器不存在，无法初始化图表');
        return;
      }

      // 创建图表实例
      try {
        this.progressChart = echarts.init(this.$refs.progressChartContainer);
        console.log('图表实例创建成功');
      } catch (error) {
        console.error('创建图表实例失败:', error);
        return;
      }

      // 添加窗口大小变化监听
      window.addEventListener('resize', this.resizeChart);

      // 如果没有学生ID，显示空图表
      if (!this.studentId) {
        console.warn('没有学生ID，显示空图表');
        this.renderEmptyChart();
        return;
      }

      // 获取图表数据并渲染
      console.log('开始获取图表数据...');
      this.fetchChartData();
    },

    // 获取图表数据
    async fetchChartData() {
      console.log('获取学习进度图表数据...');

      try {
        // 直接从服务器获取最新数据，不使用缓存
        console.log(`正在直接从服务器获取学生ID为 ${this.studentId} 的学习进度数据...`);

        const response = await axios.get(`/api/learning/student-progress/${this.studentId}`);
        console.log('服务器返回的原始响应:', response);

        if (response.data && response.data.success) {
          const progressData = response.data.data;
          console.log('获取到的学习进度数据:', JSON.stringify(progressData, null, 2));

          // 检查数据结构
          if (progressData && progressData.chapters) {
            console.log(`学习进度数据包含 ${progressData.chapters.length} 个章节`);

            // 检查每个章节的数据
            progressData.chapters.forEach((chapter, index) => {
              console.log(`章节 ${index+1}: ${chapter.chapter_title}, 完成率: ${chapter.completion_rate}%, 已完成: ${chapter.completed_sections}/${chapter.total_sections}`);
            });

            // 渲染图表
            this.renderProgressChart(progressData);

            // 保存到缓存
            const cacheData = {
              data: progressData,
              timestamp: new Date().getTime()
            };
            localStorage.setItem(`progress_data_${this.studentId}`, JSON.stringify(cacheData));
          } else {
            console.error('学习进度数据结构不完整:', progressData);
            this.renderEmptyChart();
          }
        } else {
          console.error('获取学习进度数据失败:', response.data ? response.data.message : '未知错误');
          this.renderEmptyChart();
        }
      } catch (error) {
        console.error('获取学习进度数据出错:', error);
        console.error('错误详情:', error.stack || error);
        this.renderEmptyChart();

        // 检查是否有缓存数据
        const cachedData = this.getProgressDataFromCache();
        if (cachedData) {
          console.log('服务器获取失败，使用缓存的进度数据');
          this.renderProgressChart(cachedData.data);
        }
      }
    },

    // 从缓存中获取进度数据
    getProgressDataFromCache() {
      try {
        const cacheKey = `progress_data_${this.studentId}`;
        const cachedDataStr = localStorage.getItem(cacheKey);

        if (!cachedDataStr) return null;

        return JSON.parse(cachedDataStr);
      } catch (error) {
        console.error('读取缓存进度数据失败:', error);
        return null;
      }
    },

    // 更新进度数据缓存
    async updateProgressDataCache(showLoading = true) {
      try {
        if (showLoading) {
          this.$message.info('正在获取学习进度数据...');
        }

        console.log(`正在获取学生ID为 ${this.studentId} 的学习进度数据...`);
        const response = await axios.get(`/api/learning/student-progress/${this.studentId}`);
        console.log('获取到的学习进度数据响应:', response.data);

        if (response.data.success) {
          const progressData = response.data.data;
          console.log('学习进度数据详情:', JSON.stringify(progressData, null, 2));

          // 渲染图表
          this.renderProgressChart(progressData);

          // 保存到本地存储
          const cacheData = {
            data: progressData,
            timestamp: new Date().getTime()
          };

          const cacheKey = `progress_data_${this.studentId}`;
          localStorage.setItem(cacheKey, JSON.stringify(cacheData));

          if (showLoading) {
            this.$message.success('学习进度数据已更新');
          }
        } else {
          console.warn('获取学习进度数据失败:', response.data.message);
          this.renderEmptyChart();
          if (showLoading) {
            this.$message.warning('暂无学习进度数据');
          }
        }
      } catch (error) {
        console.error('获取进度数据失败:', error);
        console.error('错误详情:', error.stack || error);
        this.renderEmptyChart();
        if (showLoading) {
          this.$message.error('获取学习进度数据失败: ' + (error.message || '未知错误'));
        }
      }
    },

    // 刷新学习进度图表
    async refreshProgressChart() {
      if (!this.hasProfileInfo || !this.studentId) {
        this.$message.warning('请先完善个人信息');
        return;
      }

      // 清除缓存
      try {
        localStorage.removeItem(`progress_data_${this.studentId}`);
      } catch (error) {
        console.error('清除进度数据缓存失败:', error);
      }

      // 重新获取数据
      await this.updateProgressDataCache(true);
    },

    // 渲染进度图表
    renderProgressChart(data) {
      console.log('开始渲染进度图表，数据:', data);

      // 如果没有数据，显示空图表
      if (!data || !data.chapters || data.chapters.length === 0) {
        console.warn('没有章节数据，显示空图表');
        this.renderEmptyChart();
        return;
      }

      // 确保图表实例存在
      if (!this.progressChart) {
        console.error('图表实例不存在，无法渲染');
        return;
      }

      const chapters = data.chapters;
      console.log(`准备渲染 ${chapters.length} 个章节的进度数据`);

      const chapterTitles = chapters.map(chapter => chapter.chapter_title);

      // 使用小节完成率而不是题目完成率
      const completionRates = chapters.map(chapter => {
        // 确保有完成率数据
        if (typeof chapter.completion_rate === 'number') {
          return chapter.completion_rate;
        }

        // 如果没有直接的完成率数据，但有小节数据，则计算完成率
        if (chapter.total_sections && typeof chapter.completed_sections === 'number') {
          const rate = chapter.total_sections > 0
            ? Math.round((chapter.completed_sections / chapter.total_sections) * 100)
            : 0;
          console.log(`章节 ${chapter.chapter_title} 的完成率: ${rate}% (${chapter.completed_sections}/${chapter.total_sections})`);
          return rate;
        }

        // 如果没有任何数据，返回0
        console.warn(`章节 ${chapter.chapter_title} 没有完成率数据，使用0`);
        return 0;
      });

      console.log('章节标题:', chapterTitles);
      console.log('完成率:', completionRates);

      const option = {
        tooltip: {
          trigger: 'axis',
          formatter: function(params) {
            const chapter = chapters[params[0].dataIndex];
            let tooltipText = `${chapter.chapter_title}: ${params[0].value}%`;

            // 添加小节完成情况
            if (chapter.total_sections) {
              tooltipText += `<br/>已完成 ${chapter.completed_sections || 0}/${chapter.total_sections} 个小节`;
            }

            return tooltipText;
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: chapterTitles,
          axisLabel: {
            interval: 0,
            rotate: 30
          }
        },
        yAxis: {
          type: 'value',
          max: 100,
          axisLabel: {
            formatter: '{value}%'
          }
        },
        series: [
          {
            name: '完成率',
            type: 'bar',
            data: completionRates,
            itemStyle: {
              color: function(params) {
                // 根据完成率设置不同的颜色
                const value = params.value;
                if (value === 0) {
                  return '#e0e0e0'; // 未开始
                } else if (value < 30) {
                  return '#ff9800'; // 刚开始
                } else if (value < 70) {
                  return '#4caf50'; // 进行中
                } else {
                  return '#2196f3'; // 接近完成
                }
              }
            },
            emphasis: {
              itemStyle: {
                color: function(params) {
                  // 高亮时的颜色
                  const value = params.value;
                  if (value === 0) {
                    return '#bdbdbd'; // 未开始
                  } else if (value < 30) {
                    return '#f57c00'; // 刚开始
                  } else if (value < 70) {
                    return '#388e3c'; // 进行中
                  } else {
                    return '#1976d2'; // 接近完成
                  }
                }
              }
            },
            label: {
              show: true,
              position: 'top',
              formatter: '{c}%'
            }
          }
        ]
      };

      try {
        console.log('设置图表选项...');
        this.progressChart.setOption(option);
        console.log('图表渲染成功');
      } catch (error) {
        console.error('渲染图表失败:', error);
      }
    },

    // 渲染空图表
    renderEmptyChart() {
      // 创建一个完全空白的图表，只显示坐标轴
      const option = {
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: ['绪论', '线性表', '线性表的扩展', '树', '图', '查找', '排序'],
          axisLabel: {
            interval: 0,
            rotate: 30
          }
        },
        yAxis: {
          type: 'value',
          max: 100,
          axisLabel: {
            formatter: '{value}%'
          }
        },
        series: [
          {
            name: '完成率',
            type: 'bar',
            data: [0, 0, 0, 0, 0, 0, 0], // 全部为0的数据
            itemStyle: {
              color: '#e0e0e0' // 使用浅灰色表示没有数据
            }
          }
        ],
        tooltip: {
          trigger: 'axis',
          formatter: '{b}: {c}%'
        }
      };

      this.progressChart.setOption(option);

      // 显示提示信息
      this.$message.info('暂无学习进度数据，请先完成一些习题');
    },

    // 调整图表大小
    resizeChart() {
      if (this.progressChart) {
        this.progressChart.resize();
      }
    },

    // 获取推荐图标
    getRecommendationIcon(type) {
      const iconMap = {
        'problem': 'el-icon-edit-outline',
        'chapter': 'el-icon-reading',
        'video': 'el-icon-video-camera',
        'article': 'el-icon-document',
        'quiz': 'el-icon-question'
      };

      return iconMap[type] || 'el-icon-star-on';
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
    },

    // 跳转到个人信息页面
    goToProfile() {
      this.$router.push('/student/profile');
    },

    // 清除所有缓存数据
    clearAllCache() {
      if (!this.studentId) return;

      try {
        // 清除推荐数据缓存
        localStorage.removeItem(`recommendations_${this.studentId}`);

        // 清除进度数据缓存
        localStorage.removeItem(`progress_data_${this.studentId}`);

        // 清除活动数据缓存
        localStorage.removeItem(`activities_${this.studentId}`);

        // 清除用户统计数据缓存
        localStorage.removeItem(`user_stats_${this.studentId}`);

        console.log('已清除所有缓存数据');
      } catch (error) {
        console.error('清除缓存数据失败:', error);
      }
    }
  }
}
</script>

<style scoped>
/* 整体布局 */
.student-page {
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

/* 个人信息提示卡片 */
.profile-alert {
  margin-bottom: 24px;
}

.alert-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
}

.alert-content p {
  margin: 0;
  margin-right: 20px;
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

.user-stats {
  display: flex;
  gap: 24px;
}

/* 主要内容区 */
.dashboard-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
}

/* 左侧内容 */
.dashboard-left {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.progress-card {
  margin-bottom: 0;
}

.progress-container {
  height: 300px;
  width: 100%;
}

.feature-card {
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

/* 右侧内容 */
.dashboard-right {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.recommendation-card, .activity-card {
  margin-bottom: 0;
  height: 100%;
}

.empty-recommendations, .empty-activities {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100px;
  color: #999;
}

.recommendation-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.recommendation-item {
  display: flex;
  background-color: #f5f7fa;
  border-radius: 8px;
  padding: 16px;
  transition: all 0.3s;
}

.recommendation-item:hover {
  background-color: #e9f1ff;
}

.recommendation-icon {
  font-size: 24px;
  margin-right: 16px;
  color: #0052d9;
  display: flex;
  align-items: center;
}

.recommendation-content {
  flex: 1;
}

.recommendation-content h4 {
  margin: 0;
  margin-bottom: 8px;
  font-size: 16px;
}

.recommendation-content p {
  margin: 0;
  margin-bottom: 12px;
  font-size: 14px;
  color: #666;
}

.activity-item {
  display: flex;
  align-items: flex-start;
  margin-bottom: 12px;
}

.activity-time {
  font-size: 12px;
  color: #999;
  width: 80px;
  flex-shrink: 0;
}

.activity-content {
  flex: 1;
}

.activity-type {
  font-weight: 500;
  margin-right: 8px;
}

.activity-description {
  color: #666;
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

  .user-stats {
    margin-top: 16px;
    width: 100%;
    justify-content: space-between;
  }
}

@media (max-width: 768px) {
  .main-content {
    margin-left: 50px;
    padding: 16px;
  }

  .user-stats {
    flex-direction: column;
    gap: 8px;
  }

  .feature-item {
    padding: 12px;
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

  .recommendation-item {
    flex-direction: column;
  }

  .recommendation-icon {
    margin-right: 0;
    margin-bottom: 12px;
  }
}
</style>