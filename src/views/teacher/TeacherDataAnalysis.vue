<template>
  <div class="teacher-data-analysis-container">
    <TeacherNavbar />
    <div class="main-content">
      <div class="page-header">
        <h1>教学数据分析</h1>
        <div class="header-actions">
          <div class="class-selector-container">
            <span class="selector-label">当前班级：</span>
            <el-select v-model="selectedClass" placeholder="选择班级" @change="loadData" style="width: 180px;">
              <el-option
                v-for="item in classList"
                :key="item"
                :label="item"
                :value="item">
              </el-option>
            </el-select>
          </div>
          <el-button type="primary" @click="runAIAnalysis" :loading="aiLoading">
            AI分析
          </el-button>
        </div>
      </div>

      <!-- 加载状态 -->
      <div v-if="isLoading" class="loading-container">
        <div class="loading-text">正在加载数据，请稍候...</div>
        <el-skeleton :rows="10" animated />
      </div>

      <!-- 主要内容区域 -->
      <div v-if="!isLoading" class="analysis-content">
        <!-- 总体统计卡片 -->
        <div class="stats-cards">
          <el-card v-for="(stat, index) in overallStats" :key="index" class="stat-card">
            <div class="stat-icon"><i :class="stat.icon"></i></div>
            <div class="stat-content">
              <div class="stat-title">{{ stat.title }}</div>
              <div class="stat-value">{{ stat.value }}</div>
            </div>
          </el-card>
        </div>

        <!-- 图表区域 -->
        <el-row :gutter="20" class="chart-row">
          <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
            <el-card class="chart-card">
              <template #header>
                <div class="card-header">
                  <span>学习趋势分析</span>
                  <el-radio-group v-model="trendTimeRange" size="small" @change="updateTrendChart">
                    <el-radio-button label="week">周</el-radio-button>
                    <el-radio-button label="month">月</el-radio-button>
                  </el-radio-group>
                </div>
              </template>
              <div ref="trendChart" class="chart-container"></div>
            </el-card>
          </el-col>
          <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
            <el-card class="chart-card">
              <template #header>
                <div class="card-header">
                  <span>题目难度分布</span>
                </div>
              </template>
              <div ref="difficultyChart" class="chart-container"></div>
            </el-card>
          </el-col>
        </el-row>

        <el-row :gutter="20" class="chart-row">
          <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
            <el-card class="chart-card">
              <template #header>
                <div class="card-header">
                  <span>常见错误类型</span>
                </div>
              </template>
              <div ref="errorChart" class="chart-container"></div>
            </el-card>
          </el-col>
          <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
            <el-card class="chart-card">
              <template #header>
                <div class="card-header">
                  <span>学习进度分布</span>
                </div>
              </template>
              <div ref="progressChart" class="chart-container"></div>
            </el-card>
          </el-col>
        </el-row>

        <!-- AI分析结果 -->
        <el-card v-if="aiAnalysisResult" class="ai-analysis-card">
          <template #header>
            <div class="card-header">
              <span>AI分析洞察</span>
            </div>
          </template>
          <div class="ai-analysis-content">
            <div class="analysis-section">
              <h3>总体学习情况</h3>
              <p>{{ aiAnalysisResult.summary }}</p>
            </div>
            <el-divider></el-divider>
            <div class="analysis-section">
              <h3>优势领域</h3>
              <ul>
                <li v-for="(strength, index) in aiAnalysisResult.strengths" :key="index">
                  {{ strength }}
                </li>
              </ul>
            </div>
            <el-divider></el-divider>
            <div class="analysis-section">
              <h3>待提升领域</h3>
              <ul>
                <li v-for="(weakness, index) in aiAnalysisResult.weaknesses" :key="index">
                  {{ weakness }}
                </li>
              </ul>
            </div>
            <el-divider></el-divider>
            <div class="analysis-section">
              <h3>教学建议</h3>
              <ul>
                <li v-for="(recommendation, index) in aiAnalysisResult.recommendations" :key="index">
                  {{ recommendation }}
                </li>
              </ul>
            </div>
            <el-divider v-if="aiAnalysisResult.correlation"></el-divider>
            <div class="analysis-section" v-if="aiAnalysisResult.correlation">
              <h3>教学与编程学习关联性</h3>
              <p>{{ aiAnalysisResult.correlation }}</p>
            </div>
          </div>
        </el-card>

        <!-- 学生数据表格 -->
        <el-card class="student-data-card">
          <template #header>
            <div class="card-header">
              <span>学生学习效率分析</span>
              <el-input
                v-model="searchQuery"
                placeholder="搜索学生ID"
                prefix-icon="el-icon-search"
                clearable
                style="width: 200px">
              </el-input>
            </div>
          </template>
          <el-table
            :data="paginatedStudentData"
            style="width: 100%"
            border
            stripe
            :default-sort="{prop: 'successful_submissions', order: 'descending'}">
            <el-table-column prop="student_id" label="学生ID" sortable />
            <el-table-column prop="total_submissions" label="总提交数" sortable />
            <el-table-column prop="successful_submissions" label="成功提交数" sortable />
            <el-table-column label="成功率" sortable>
              <template #default="scope">
                {{ calculateSuccessRate(scope.row) }}
              </template>
            </el-table-column>
            <el-table-column label="平均解题时间" sortable>
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

          <!-- 分页控件 -->
          <div class="pagination-container">
            <el-pagination
              background
              layout="prev, pager, next, sizes, total"
              :total="filteredStudentData.length"
              :page-size="pageSize"
              :page-sizes="[10, 20, 50, 100]"
              :current-page="currentPage"
              @current-change="handleCurrentChange"
              @size-change="handleSizeChange">
            </el-pagination>
          </div>
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
  name: 'TeacherDataAnalysis',
  components: {
    TeacherNavbar
  },
  data() {
    return {
      isLoading: true,
      selectedClass: '',
      classList: [],
      trendTimeRange: 'week',
      searchQuery: '',
      // 分页相关
      currentPage: 1,
      pageSize: 10,
      overallStats: [
        { title: '活跃学生数', value: 0, icon: 'el-icon-user' },
        { title: '平均成功率', value: '0%', icon: 'el-icon-data-line' },
        { title: '本周提交数', value: 0, icon: 'el-icon-document' },
        { title: '常见错误类型', value: 0, icon: 'el-icon-warning' }
      ],
      // 图表实例
      charts: {
        trend: null,
        difficulty: null,
        error: null,
        progress: null
      },
      // 数据
      analysisData: null,
      studentData: [],
      errorPatterns: [],
      // AI分析
      aiLoading: false,
      aiAnalysisResult: null
    };
  },
  computed: {
    filteredStudentData() {
      if (!this.searchQuery) return this.studentData;
      const query = this.searchQuery.toLowerCase();
      return this.studentData.filter(student =>
        student.student_id.toLowerCase().includes(query)
      );
    },
    paginatedStudentData() {
      const start = (this.currentPage - 1) * this.pageSize;
      const end = start + this.pageSize;
      return this.filteredStudentData.slice(start, end);
    }
  },
  mounted() {
    this.loadClassList();
  },
  beforeUnmount() {
    console.log('组件卸载，清理资源');

    // 移除窗口大小变化的事件监听器
    window.removeEventListener('resize', this.resizeCharts);

    // 销毁图表实例
    Object.values(this.charts).forEach(chart => {
      if (chart) {
        try {
          chart.dispose();
          console.log('图表实例已销毁');
        } catch (error) {
          console.error('销毁图表实例失败:', error);
        }
      }
    });
  },
  methods: {
    async loadClassList() {
      try {
        console.log('正在加载班级列表...');

        // 从API获取班级列表
        try {
          const response = await axios.get('/api/teaching/class-list');
          console.log('班级列表响应:', response.data);

          if (response.data.success && response.data.classes && response.data.classes.length > 0) {
            this.classList = response.data.classes;
          } else {
            const errorMsg = response.data.message || '获取班级列表失败';
            console.error(errorMsg);
            this.$message.error(errorMsg);
            this.isLoading = false;
            return;
          }
        } catch (error) {
          console.error('从API加载班级列表失败:', error);
          this.$message.error('加载班级列表失败: ' + (error.message || '未知错误'));
          this.isLoading = false;
          return;
        }

        if (this.classList.length > 0) {
          this.selectedClass = this.classList[0];
          this.loadData();
        } else {
          this.isLoading = false;
          this.$message.warning('没有可用的班级数据');
        }
      } catch (error) {
        console.error('加载班级列表失败:', error);
        this.$message.error('加载班级列表失败');
        this.isLoading = false;
      }
    },
    async loadData() {
      this.isLoading = true;
      this.aiAnalysisResult = null;
      this.studentData = []; // 重置学生数据

      try {
        console.log('开始加载数据，班级:', this.selectedClass);

        // 重置分析数据
        this.analysisData = null;

        // 加载班级所有学生数据
        let classStudentsLoaded = false;
        try {
          await this.loadClassStudents();
          classStudentsLoaded = true;
        } catch (error) {
          console.error('加载班级学生数据失败:', error);
          this.$message.error('加载班级学生数据失败: ' + (error.message || '未知错误'));
        }

        // 加载教学数据
        let teachingDataLoaded = false;
        try {
          await this.loadTeachingData();
          teachingDataLoaded = true;
        } catch (error) {
          console.error('加载教学数据失败:', error);
          this.$message.error('加载教学数据失败: ' + (error.message || '未知错误'));
        }

        // 加载编程数据
        let codingDataLoaded = false;
        try {
          await this.loadCodingData();
          codingDataLoaded = true;
        } catch (error) {
          console.error('加载编程数据失败:', error);
          this.$message.error('加载编程数据失败: ' + (error.message || '未知错误'));
        }

        // 如果所有数据源都加载失败，显示错误信息
        if (!classStudentsLoaded && !teachingDataLoaded && !codingDataLoaded) {
          console.error('所有数据源加载失败');
          this.$message.error('无法获取数据，请检查后端API和数据库');
          this.isLoading = false;
          return;
        }

        // 处理学生数据
        this.processStudentData();

        this.isLoading = false;

        // 等待DOM更新后初始化图表
        this.$nextTick(() => {
          // 使用setTimeout确保DOM完全渲染
          setTimeout(() => {
            console.log('DOM已完全更新，初始化图表');
            this.updateCharts();
          }, 200);
        });
      } catch (error) {
        console.error('加载数据失败:', error);
        this.$message.error('加载数据失败: ' + (error.message || '未知错误'));
        this.isLoading = false;
      }
    },
    async loadClassStudents() {
      try {
        console.log('正在加载班级学生数据...');

        // 初始化学生数据集合
        let allStudents = new Map();
        let dataSourcesCount = 0;

        // 1. 首先尝试从edu_profiles_student表获取学生数据
        try {
          console.log('从edu_profiles_student表获取学生数据...');
          const profileResponse = await axios.get(`/api/profiles/class-students/${this.selectedClass}`);

          if (profileResponse.data.success && profileResponse.data.students && Array.isArray(profileResponse.data.students)) {
            dataSourcesCount++;
            const students = profileResponse.data.students;

            // 将学生添加到集合中
            students.forEach(student => {
              if (student.student_id) {
                allStudents.set(student.student_id, {
                  student_id: student.student_id,
                  name: student.name || student.student_id,
                  class_name: student.class_name || this.selectedClass,
                  email: student.email || '',
                  major: student.major || ''
                });
              }
            });

            console.log(`从edu_profiles_student表获取了${students.length}名学生`);
          }
        } catch (profileError) {
          console.warn('从edu_profiles_student表获取学生数据失败:', profileError);
        }

        // 2. 然后尝试从edu_coding_submissions表获取学生数据
        try {
          console.log('从edu_coding_submissions表获取学生数据...');
          const codingResponse = await axios.get(`/api/profiles/students-by-class/${this.selectedClass}`);

          if (codingResponse.data.success && codingResponse.data.students && Array.isArray(codingResponse.data.students)) {
            dataSourcesCount++;
            const students = codingResponse.data.students;

            // 将学生添加到集合中，如果已存在则不覆盖
            students.forEach(student => {
              if (student.student_id && !allStudents.has(student.student_id)) {
                allStudents.set(student.student_id, {
                  student_id: student.student_id,
                  name: student.name || student.student_id,
                  class_name: student.class_name || this.selectedClass,
                  email: student.email || '',
                  major: student.major || ''
                });
              }
            });

            console.log(`从edu_coding_submissions表获取了${students.length}名学生`);
          }
        } catch (codingError) {
          console.warn('从edu_coding_submissions表获取学生数据失败:', codingError);
        }

        // 检查是否获取到了学生数据
        if (allStudents.size === 0) {
          if (dataSourcesCount === 0) {
            console.error('所有数据源都无法获取学生数据');
            this.$message.error('无法获取班级学生数据，请检查后端API和数据库');
          } else {
            console.error('数据源中没有有效的学生数据');
            this.$message.error('没有找到该班级的学生数据');
          }
          return false;
        }

        // 将学生数据保存到分析数据中
        if (!this.analysisData) {
          this.analysisData = {};
        }

        // 将Map转换为数组
        this.analysisData.class_students = Array.from(allStudents.values());
        console.log(`成功获取班级学生数据，共${this.analysisData.class_students.length}名学生`);

        return true;
      } catch (error) {
        console.error('加载班级学生数据失败:', error);
        this.$message.error('加载班级学生数据失败: ' + (error.message || '未知错误'));
        return false;
      }
    },

    async loadTeachingData() {
      try {
        console.log('正在加载教学数据...');
        const response = await axios.get(`/api/teaching/learning-patterns/${this.selectedClass}`);

        console.log('教学数据响应:', response.data);

        if (!response.data.success) {
          const errorMsg = response.data.message || '获取教学数据失败';
          console.error(errorMsg);
          this.$message.error(errorMsg);
          return false;
        }

        // 检查数据是否有效
        if (!response.data.data) {
          console.error('教学数据无效');
          this.$message.error('教学数据无效');
          return false;
        }

        // 检查是否有学生数据
        const { progress_distribution, efficiency_analysis } = response.data.data;
        if ((!progress_distribution || progress_distribution.length === 0) &&
            (!efficiency_analysis || efficiency_analysis.length === 0)) {
          console.warn('教学数据中没有学生数据');
        }

        // 如果分析数据不存在，创建一个空对象
        if (!this.analysisData) {
          this.analysisData = {};
        }

        // 合并教学数据到分析数据中
        Object.assign(this.analysisData, response.data.data);

        // 更新统计数据
        this.updateStats();

        return true;
      } catch (error) {
        console.error('加载教学数据失败:', error);
        this.$message.error('加载教学数据失败: ' + (error.message || '未知错误'));
        return false;
      }
    },
    async loadCodingData() {
      try {
        console.log('正在加载编程数据...');
        const response = await axios.get(`/api/coding/class/${encodeURIComponent(this.selectedClass)}`);

        console.log('编程数据响应:', response.data);

        if (!response.data.success) {
          const errorMsg = response.data.message || '获取编程数据失败';
          console.error(errorMsg);
          this.$message.error(errorMsg);
          return false;
        }

        // 检查数据是否有效
        if (!response.data.data) {
          console.error('编程数据无效');
          this.$message.error('编程数据无效');
          return false;
        }

        // 检查是否有学生数据
        const { student_rankings } = response.data.data;
        if (!student_rankings || student_rankings.length === 0) {
          console.warn('编程数据中没有学生数据');
        } else {
          console.log(`编程数据中包含 ${student_rankings.length} 名学生的数据`);
        }

        // 如果分析数据不存在，创建一个空对象
        if (!this.analysisData) {
          this.analysisData = {};
        }

        // 合并编程数据到分析数据中
        this.analysisData.coding_data = response.data.data;

        // 尝试获取所有学生ID
        if (student_rankings && student_rankings.length > 0) {
          // 如果class_students不存在，创建一个空数组
          if (!this.analysisData.class_students) {
            this.analysisData.class_students = [];
          }

          // 将student_rankings中的学生ID添加到class_students中
          student_rankings.forEach(student => {
            if (student.student_id) {
              // 检查是否已存在该学生
              const existingStudent = this.analysisData.class_students.find(s =>
                s.student_id === student.student_id
              );

              if (!existingStudent) {
                this.analysisData.class_students.push({
                  student_id: student.student_id,
                  name: student.student_id, // 使用ID作为名称
                  class_name: this.selectedClass
                });
              }
            }
          });

          console.log(`从编程数据中提取了 ${this.analysisData.class_students.length} 名学生`);
        }

        return true;
      } catch (error) {
        console.error('加载编程数据失败:', error);
        this.$message.error('加载编程数据失败: ' + (error.message || '未知错误'));
        return false;
      }
    },

    // 显示错误信息
    showError(message) {
      console.error(message);
      this.$message.error(message);
      this.isLoading = false;
    },
    updateStats() {
      console.log('更新统计数据，analysisData:', this.analysisData);

      if (!this.analysisData) {
        console.warn('没有分析数据可用');
        return;
      }

      // 更新统计卡片数据
      const { progress_distribution, daily_trends, error_patterns } = this.analysisData;

      console.log('进度分布:', progress_distribution);
      console.log('日常趋势:', daily_trends);
      console.log('错误模式:', error_patterns);

      // 活跃学生数
      this.overallStats[0].value = progress_distribution ? progress_distribution.length : 0;
      console.log('活跃学生数:', this.overallStats[0].value);

      // 平均成功率
      let totalSuccess = 0;
      let totalSubmissions = 0;
      if (daily_trends && daily_trends.length > 0) {
        daily_trends.forEach(day => {
          totalSuccess += day.successful_submissions || 0;
          totalSubmissions += day.total_submissions || 0;
        });
        const successRate = totalSubmissions > 0 ? (totalSuccess / totalSubmissions * 100).toFixed(1) : 0;
        this.overallStats[1].value = `${successRate}%`;
      } else {
        this.overallStats[1].value = '0%';
      }
      console.log('平均成功率:', this.overallStats[1].value);

      // 本周提交数
      let weekSubmissions = 0;
      if (daily_trends && daily_trends.length > 0) {
        // 获取最近7天的数据
        const recentDays = daily_trends.slice(0, 7);
        recentDays.forEach(day => {
          weekSubmissions += day.total_submissions || 0;
        });
      }
      this.overallStats[2].value = weekSubmissions;
      console.log('本周提交数:', this.overallStats[2].value);

      // 常见错误类型数
      this.overallStats[3].value = error_patterns ? error_patterns.length : 0;
      console.log('常见错误类型数:', this.overallStats[3].value);
    },
    updateCharts() {
      console.log('更新所有图表');

      if (!this.analysisData) {
        console.warn('没有分析数据可用于更新图表');
        return;
      }

      // 尝试初始化图表，如果DOM元素不存在则设置重试
      const initCharts = () => {
        try {
          console.log('开始初始化各个图表');

          // 检查DOM元素是否存在
          const trendChartEl = this.$refs.trendChart;
          const difficultyChartEl = this.$refs.difficultyChart;
          const errorChartEl = this.$refs.errorChart;
          const progressChartEl = this.$refs.progressChart;

          // 检查是否所有图表DOM元素都存在
          const allChartsExist = trendChartEl && difficultyChartEl && errorChartEl && progressChartEl;

          console.log('图表DOM元素状态:',
            '趋势图:', trendChartEl ? '存在' : '不存在',
            '难度图:', difficultyChartEl ? '存在' : '不存在',
            '错误图:', errorChartEl ? '存在' : '不存在',
            '进度图:', progressChartEl ? '存在' : '不存在',
            '所有图表存在:', allChartsExist ? '是' : '否'
          );

          // 如果所有图表DOM元素都不存在，设置重试
          if (!allChartsExist) {
            console.log('部分图表DOM元素不存在，将在200ms后重试');
            setTimeout(initCharts, 200);
            return;
          }

          // 初始化趋势图表
          this.initTrendChart();

          // 初始化难度分布图表
          this.initDifficultyChart();

          // 初始化错误类型图表
          this.initErrorChart();

          // 初始化进度分布图表
          this.initProgressChart();

          // 添加窗口大小变化时自动调整图表大小
          window.addEventListener('resize', this.resizeCharts);

          console.log('所有图表初始化完成');
        } catch (error) {
          console.error('初始化图表时发生错误:', error);
          // 发生错误时也设置重试
          console.log('初始化图表出错，将在200ms后重试');
          setTimeout(initCharts, 200);
        }
      };

      // 开始初始化图表
      initCharts();
    },
    processStudentData() {
      console.log('处理学生数据');

      // 重置学生数据
      this.studentData = [];

      if (!this.analysisData) {
        console.warn('没有分析数据可用于处理学生数据');
        return;
      }

      // 尝试从不同来源获取学生数据并合并
      let studentDataMap = new Map(); // 使用Map来合并相同学生ID的数据
      let dataSourcesCount = 0;

      // 0. 首先从class_students获取所有学生基本信息
      if (this.analysisData.class_students && this.analysisData.class_students.length > 0) {
        dataSourcesCount++;
        console.log('从class_students获取学生基本信息，数量:', this.analysisData.class_students.length);
        this.analysisData.class_students.forEach(student => {
          if (!student.student_id) {
            console.warn('发现无效学生数据(缺少student_id):', student);
            return;
          }
          studentDataMap.set(student.student_id, {
            student_id: student.student_id,
            name: student.name || student.student_id,
            class_name: student.class_name || this.selectedClass,
            email: student.email || '',
            major: student.major || '',
            total_submissions: 0,
            successful_submissions: 0,
            avg_solving_time: 0,
            max_attempts: 0,
            problems_attempted: 0,
            problems_solved: 0
          });
        });
      }

      // 1. 从efficiency_analysis获取学习效率数据
      if (this.analysisData.efficiency_analysis && this.analysisData.efficiency_analysis.length > 0) {
        dataSourcesCount++;
        console.log('从efficiency_analysis获取学生数据，数量:', this.analysisData.efficiency_analysis.length);
        this.analysisData.efficiency_analysis.forEach(student => {
          if (!student.student_id) {
            console.warn('发现无效学生数据(缺少student_id):', student);
            return;
          }

          const studentId = student.student_id;
          if (studentDataMap.has(studentId)) {
            // 更新现有数据
            const existingData = studentDataMap.get(studentId);
            studentDataMap.set(studentId, {
              ...existingData,
              total_submissions: student.total_submissions || existingData.total_submissions,
              successful_submissions: student.successful_submissions || existingData.successful_submissions,
              avg_solving_time: student.avg_solving_time || existingData.avg_solving_time,
              max_attempts: student.max_attempts || existingData.max_attempts
            });
          } else {
            // 添加新数据
            studentDataMap.set(studentId, {
              student_id: studentId,
              name: studentId,
              class_name: this.selectedClass,
              email: '',
              major: '',
              total_submissions: student.total_submissions || 0,
              successful_submissions: student.successful_submissions || 0,
              avg_solving_time: student.avg_solving_time || 0,
              max_attempts: student.max_attempts || 0,
              problems_attempted: 0,
              problems_solved: 0
            });
          }
        });
      }

      // 2. 从progress_distribution获取学习进度数据
      if (this.analysisData.progress_distribution && this.analysisData.progress_distribution.length > 0) {
        dataSourcesCount++;
        console.log('从progress_distribution获取学生数据，数量:', this.analysisData.progress_distribution.length);
        this.analysisData.progress_distribution.forEach(student => {
          if (!student.student_id) {
            console.warn('发现无效学生数据(缺少student_id):', student);
            return;
          }

          const studentId = student.student_id;
          if (studentDataMap.has(studentId)) {
            // 更新现有数据
            const existingData = studentDataMap.get(studentId);
            studentDataMap.set(studentId, {
              ...existingData,
              problems_attempted: student.problems_attempted || existingData.problems_attempted,
              problems_solved: student.problems_solved || existingData.problems_solved,
              avg_time_spent: student.avg_time_spent || existingData.avg_time_spent,
              avg_attempts: student.avg_attempts || existingData.avg_attempts
            });
          } else {
            // 添加新数据
            studentDataMap.set(studentId, {
              student_id: studentId,
              name: studentId,
              class_name: this.selectedClass,
              email: '',
              major: '',
              total_submissions: 0,
              successful_submissions: 0,
              avg_solving_time: student.avg_time_spent || 0,
              max_attempts: student.avg_attempts || 0,
              problems_attempted: student.problems_attempted || 0,
              problems_solved: student.problems_solved || 0
            });
          }
        });
      }

      // 3. 从coding_data.student_rankings获取编程数据
      if (this.analysisData.coding_data && this.analysisData.coding_data.student_rankings && this.analysisData.coding_data.student_rankings.length > 0) {
        dataSourcesCount++;
        console.log('从coding_data.student_rankings获取学生数据，数量:', this.analysisData.coding_data.student_rankings.length);
        this.analysisData.coding_data.student_rankings.forEach(student => {
          if (!student.student_id) {
            console.warn('发现无效学生数据(缺少student_id):', student);
            return;
          }

          const studentId = student.student_id;
          if (studentDataMap.has(studentId)) {
            // 更新现有数据
            const existingData = studentDataMap.get(studentId);
            studentDataMap.set(studentId, {
              ...existingData,
              total_submissions: student.total_submissions || existingData.total_submissions,
              successful_submissions: student.solved_problems || existingData.successful_submissions,
              success_rate: student.success_rate
            });
          } else {
            // 添加新数据
            studentDataMap.set(studentId, {
              student_id: studentId,
              name: studentId,
              class_name: this.selectedClass,
              email: '',
              major: '',
              total_submissions: student.total_submissions || 0,
              successful_submissions: student.solved_problems || 0,
              success_rate: student.success_rate,
              avg_solving_time: 0,
              max_attempts: 0,
              problems_attempted: 0,
              problems_solved: 0
            });
          }
        });
      }

      // 如果所有来源都没有数据，显示错误信息
      if (studentDataMap.size === 0) {
        if (dataSourcesCount === 0) {
          console.error('没有找到任何学生数据源');
          this.$message.error('无法获取学生数据，请检查后端API和数据库');
        } else {
          console.error('所有数据源中都没有有效的学生数据');
          this.$message.error('数据源中没有有效的学生数据');
        }
        return;
      }

      // 将Map转换为数组
      this.studentData = Array.from(studentDataMap.values());
      console.log(`处理后的学生数据: ${this.studentData.length}个学生`);

      // 检查是否有足够的学生数据
      if (this.studentData.length < 5) {
        console.warn(`学生数据较少，只有${this.studentData.length}个学生`);
      }

      // 输出学生数据示例和所有学生ID
      console.log('学生数据示例:', this.studentData.slice(0, 3));
      console.log('所有学生ID:', this.studentData.map(s => s.student_id).join(', '));
    },
    initTrendChart() {
      console.log('初始化趋势图表');

      if (!this.analysisData || !this.analysisData.daily_trends) {
        console.warn('没有日常趋势数据可用于图表');
        return;
      }

      const chartDom = this.$refs.trendChart;
      if (!chartDom) {
        console.warn('找不到趋势图表DOM元素');
        return;
      }

      // 销毁旧图表
      if (this.charts.trend) {
        this.charts.trend.dispose();
      }

      // 处理数据
      const dailyTrends = this.analysisData.daily_trends;
      console.log('日常趋势数据:', dailyTrends);

      const dates = [];
      const submissions = [];
      const successRate = [];

      // 根据时间范围筛选数据
      const filteredData = this.trendTimeRange === 'week'
        ? dailyTrends.slice(0, 7)
        : dailyTrends.slice(0, 30);

      console.log('过滤后的趋势数据:', filteredData);

      // 反转数据以按日期升序显示
      filteredData.reverse().forEach(item => {
        dates.push(item.date);
        submissions.push(item.total_submissions);
        const rate = item.total_submissions > 0
          ? (item.successful_submissions / item.total_submissions * 100).toFixed(1)
          : 0;
        successRate.push(parseFloat(rate));
      });

      console.log('图表数据 - 日期:', dates);
      console.log('图表数据 - 提交数:', submissions);
      console.log('图表数据 - 成功率:', successRate);

      try {
        // 创建图表
        this.charts.trend = echarts.init(chartDom);
        const option = {
          tooltip: {
            trigger: 'axis',
            axisPointer: {
              type: 'cross',
              crossStyle: {
                color: '#999'
              }
            }
          },
          legend: {
            data: ['提交数', '成功率']
          },
          xAxis: [
            {
              type: 'category',
              data: dates,
              axisPointer: {
                type: 'shadow'
              }
            }
          ],
          yAxis: [
            {
              type: 'value',
              name: '提交数',
              min: 0,
              axisLabel: {
                formatter: '{value}'
              }
            },
            {
              type: 'value',
              name: '成功率',
              min: 0,
              max: 100,
              axisLabel: {
                formatter: '{value}%'
              }
            }
          ],
          series: [
            {
              name: '提交数',
              type: 'bar',
              data: submissions
            },
            {
              name: '成功率',
              type: 'line',
              yAxisIndex: 1,
              data: successRate,
              smooth: true
            }
          ]
        };

        this.charts.trend.setOption(option);
        console.log('趋势图表初始化成功');

        // 添加窗口大小变化时自动调整图表大小
        window.addEventListener('resize', this.resizeCharts);
      } catch (error) {
        console.error('初始化趋势图表失败:', error);
      }
    },
    updateTrendChart() {
      this.initTrendChart();
    },
    initDifficultyChart() {
      if (!this.analysisData || !this.analysisData.problem_difficulty) return;

      const chartDom = this.$refs.difficultyChart;
      if (!chartDom) return;

      // 销毁旧图表
      if (this.charts.difficulty) {
        this.charts.difficulty.dispose();
      }

      // 处理数据
      const problemData = this.analysisData.problem_difficulty;
      const problems = [];
      const successRates = [];
      const avgTimes = [];

      problemData.forEach(item => {
        problems.push(item.problem_title);
        successRates.push(parseFloat(item.success_rate || 0).toFixed(1));

        // 处理平均解题时间，如果为null或undefined则设为0
        let avgTime = item.avg_solution_time;
        if (avgTime === null || avgTime === undefined) {
          avgTime = 0;
        } else {
          // 确保是数字并限制在合理范围内
          avgTime = parseFloat(avgTime);
          if (isNaN(avgTime) || avgTime < 0) {
            avgTime = 0;
          } else if (avgTime > 10800) {
            // 如果超过3小时(10800秒)，限制为10800
            avgTime = 10800;
          }
        }
        // 保留整数秒数
        avgTimes.push(Math.round(avgTime));
      });

      // 创建图表
      this.charts.difficulty = echarts.init(chartDom);
      const option = {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross',
            crossStyle: {
              color: '#999'
            }
          },
          formatter: function(params) {
            let result = params[0].name + '<br/>';
            params.forEach(param => {
              let marker = param.marker;
              let seriesName = param.seriesName;
              let value = param.value;

              // 为平均解题时间格式化显示
              if (seriesName === '平均解题时间(秒)') {
                if (value >= 3600) {
                  // 大于1小时，显示为小时
                  const hours = Math.floor(value / 3600);
                  const mins = Math.floor((value % 3600) / 60);
                  const secs = Math.round(value % 60);
                  value = hours + '小时' + (mins > 0 ? mins + '分' : '') + (secs > 0 ? secs + '秒' : '');
                } else if (value >= 60) {
                  // 大于1分钟，显示为分钟
                  const mins = Math.floor(value / 60);
                  const secs = Math.round(value % 60);
                  value = mins + '分' + (secs > 0 ? secs + '秒' : '');
                } else {
                  value = value + '秒';
                }
              } else if (seriesName === '成功率') {
                value = value + '%';
              }

              result += marker + ' ' + seriesName + ': ' + value + '<br/>';
            });
            return result;
          }
        },
        legend: {
          data: ['成功率', '平均解题时间(秒)']
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: [
          {
            type: 'category',
            data: problems,
            axisLabel: {
              interval: 0,
              rotate: 45,
              formatter: function (value) {
                return value.length > 10 ? value.substring(0, 10) + '...' : value;
              }
            }
          }
        ],
        yAxis: [
          {
            type: 'value',
            name: '成功率',
            min: 0,
            max: 100,
            axisLabel: {
              formatter: '{value}%'
            }
          },
          {
            type: 'value',
            name: '时间(秒)',
            min: 0,
            // 不设置max，让其自适应数据范围
            axisLabel: {
              formatter: function(value) {
                if (value >= 3600) {
                  // 大于1小时，显示为小时
                  const hours = Math.floor(value / 3600);
                  const mins = Math.floor((value % 3600) / 60);
                  return hours + '小时' + (mins > 0 ? mins + '分' : '');
                } else if (value >= 60) {
                  // 大于1分钟，显示为分钟
                  const mins = Math.floor(value / 60);
                  const secs = value % 60;
                  return mins + '分' + (secs > 0 ? secs + '秒' : '');
                }
                return value + '秒';
              }
            }
          }
        ],
        series: [
          {
            name: '成功率',
            type: 'bar',
            data: successRates
          },
          {
            name: '平均解题时间(秒)',
            type: 'line',
            yAxisIndex: 1,
            data: avgTimes
          }
        ]
      };

      this.charts.difficulty.setOption(option);
    },
    initErrorChart() {
      const chartDom = this.$refs.errorChart;
      if (!chartDom) return;

      // 销毁旧图表
      if (this.charts.error) {
        this.charts.error.dispose();
      }

      // 获取错误数据
      let errorData = [];

      // 首先尝试从教学数据中获取错误模式
      if (this.analysisData && this.analysisData.error_patterns) {
        errorData = this.analysisData.error_patterns;
      }
      // 如果没有教学数据中的错误模式，尝试从编程数据中获取
      else if (this.analysisData && this.analysisData.coding_data && this.analysisData.coding_data.common_errors) {
        errorData = this.analysisData.coding_data.common_errors;
      }

      // 如果没有错误数据，返回
      if (errorData.length === 0) {
        console.log('没有错误数据可供显示');
        return;
      }

      console.log('错误数据:', errorData);

      const errorTypes = [];
      const errorCounts = [];

      errorData.forEach(item => {
        // 获取错误消息，适应不同的数据结构
        let errorMsg = '';
        let count = 0;

        if (item.error_message) {
          errorMsg = item.error_message;
          count = item.count || 1;
        } else if (item.execution_errors) {
          errorMsg = item.execution_errors;
          count = item.count || 1;
        } else {
          // 如果没有明确的错误消息字段，使用第一个非count的字段
          const keys = Object.keys(item).filter(k => k !== 'count');
          if (keys.length > 0) {
            errorMsg = String(item[keys[0]]);
            count = item.count || 1;
          } else {
            return; // 跳过这个项目
          }
        }

        // 截断错误消息以适应图表显示
        errorMsg = errorMsg.length > 20 ? errorMsg.substring(0, 20) + '...' : errorMsg;
        errorTypes.push(errorMsg);
        errorCounts.push(count);
      });

      // 如果没有有效的错误类型，返回
      if (errorTypes.length === 0) {
        console.log('没有有效的错误类型可供显示');
        return;
      }

      // 创建图表
      this.charts.error = echarts.init(chartDom);
      const option = {
        tooltip: {
          trigger: 'item',
          formatter: '{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'vertical',
          left: 'left',
          data: errorTypes
        },
        series: [
          {
            name: '错误类型',
            type: 'pie',
            radius: '55%',
            center: ['50%', '60%'],
            data: errorTypes.map((type, index) => ({
              name: type,
              value: errorCounts[index]
            })),
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            }
          }
        ]
      };

      this.charts.error.setOption(option);
    },
    initProgressChart() {
      if (!this.analysisData || !this.analysisData.progress_distribution) return;

      const chartDom = this.$refs.progressChart;
      if (!chartDom) return;

      // 销毁旧图表
      if (this.charts.progress) {
        this.charts.progress.dispose();
      }

      // 处理数据
      const progressData = this.analysisData.progress_distribution;

      // 计算完成率分布
      const completionRates = [];
      progressData.forEach(student => {
        const attempted = student.problems_attempted || 0;
        const solved = student.problems_solved || 0;
        const rate = attempted > 0 ? (solved / attempted * 100) : 0;
        completionRates.push(parseFloat(rate.toFixed(1)));
      });

      // 创建图表
      this.charts.progress = echarts.init(chartDom);
      const option = {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'value',
          boundaryGap: [0, 0.01],
          axisLabel: {
            formatter: '{value}%'
          },
          max: 100
        },
        yAxis: {
          type: 'category',
          data: ['0-20%', '20-40%', '40-60%', '60-80%', '80-100%']
        },
        series: [
          {
            name: '学生数量',
            type: 'bar',
            data: this.calculateProgressDistribution(completionRates)
          }
        ]
      };

      this.charts.progress.setOption(option);
    },
    calculateProgressDistribution(rates) {
      // 计算完成率分布
      const distribution = [0, 0, 0, 0, 0]; // 0-20%, 20-40%, 40-60%, 60-80%, 80-100%

      rates.forEach(rate => {
        if (rate < 20) distribution[0]++;
        else if (rate < 40) distribution[1]++;
        else if (rate < 60) distribution[2]++;
        else if (rate < 80) distribution[3]++;
        else distribution[4]++;
      });

      return distribution;
    },
    async runAIAnalysis() {
      this.aiLoading = true;
      this.aiAnalysisResult = null;

      try {
        // 检查是否已加载数据
        if (!this.analysisData) {
          this.$message.warning('请先加载数据再进行AI分析');
          this.aiLoading = false;
          return;
        }

        console.log('正在进行AI分析...');
        console.log('分析数据:', this.analysisData);

        // 检查数据是否完整
        if (!this.analysisData.daily_trends || !this.analysisData.problem_difficulty ||
            !this.analysisData.error_patterns || !this.analysisData.progress_distribution ||
            !this.analysisData.efficiency_analysis) {
          console.warn('分析数据不完整，尝试重新加载数据');

          // 尝试重新加载教学数据
          try {
            await this.loadTeachingData();
          } catch (error) {
            console.error('重新加载教学数据失败:', error);
          }

          // 尝试重新加载编程数据
          try {
            await this.loadCodingData();
          } catch (error) {
            console.error('重新加载编程数据失败:', error);
          }

          // 再次检查数据是否完整
          if (!this.analysisData || !this.analysisData.daily_trends) {
            this.$message.error('分析数据不完整，无法进行AI分析');
            this.aiLoading = false;
            return;
          }
        }

        // 构建正确的数据结构
        const analysisData = {
          teaching: {
            daily_trends: this.analysisData.daily_trends || [],
            problem_difficulty: this.analysisData.problem_difficulty || [],
            error_patterns: this.analysisData.error_patterns || [],
            progress_distribution: this.analysisData.progress_distribution || [],
            efficiency_analysis: this.analysisData.efficiency_analysis || []
          },
          coding: this.analysisData.coding_data || {
            class_stats: {},
            student_rankings: [],
            problem_stats: []
          },
          className: this.selectedClass
        };

        console.log('发送到AI分析的数据结构:', analysisData);

        // 调用AI分析API
        const response = await axios.post('/api/teaching/ai-analysis', {
          analysisType: 'combined',
          className: this.selectedClass,
          data: analysisData
        });

        console.log('AI分析响应:', response.data);

        if (response.data.success) {
          this.aiAnalysisResult = response.data.analysis;

          // 检查分析结果是否有效
          if (this.aiAnalysisResult) {
            console.log('AI分析结果类型:', typeof this.aiAnalysisResult.summary, typeof this.aiAnalysisResult.strengths);

            // 检查summary是否为字符串并包含"数据缺失"
            const summaryHasDataMissing = typeof this.aiAnalysisResult.summary === 'string' &&
                                         this.aiAnalysisResult.summary.includes('数据缺失');

            // 检查strengths是否为数组，且第一个元素是字符串并包含"数据缺失"
            const strengthsHasDataMissing = Array.isArray(this.aiAnalysisResult.strengths) &&
                                           this.aiAnalysisResult.strengths.length > 0 &&
                                           typeof this.aiAnalysisResult.strengths[0] === 'string' &&
                                           this.aiAnalysisResult.strengths[0].includes('数据缺失');

            if (summaryHasDataMissing || strengthsHasDataMissing) {
              console.warn('AI分析结果显示数据缺失');
              this.$message.warning('AI分析结果显示数据缺失，请确保数据库中有足够的学生数据');
            }
          }
        } else {
          const errorMsg = response.data.message || 'AI分析失败';
          console.error(errorMsg);
          this.$message.error(errorMsg);
        }
      } catch (error) {
        console.error('AI分析失败:', error);
        this.$message.error('AI分析请求失败: ' + (error.message || '未知错误'));
      } finally {
        this.aiLoading = false;
      }
    },


    // 调整所有图表大小
    resizeCharts() {
      console.log('调整图表大小');
      Object.values(this.charts).forEach(chart => {
        if (chart) {
          try {
            chart.resize();
          } catch (error) {
            console.error('调整图表大小失败:', error);
          }
        }
      });
    },

    // 分页处理方法
    handleCurrentChange(val) {
      this.currentPage = val;
    },

    handleSizeChange(val) {
      this.pageSize = val;
      this.currentPage = 1; // 重置到第一页
    },

    calculateSuccessRate(student) {
      if (!student.total_submissions || student.total_submissions === 0) {
        return '0%';
      }
      const rate = (student.successful_submissions / student.total_submissions * 100).toFixed(1);
      return `${rate}%`;
    },
    formatTime(minutes) {
      if (!minutes) return '0分钟';

      if (typeof minutes === 'number') {
        const hours = Math.floor(minutes / 60);
        const mins = minutes % 60;
        return hours > 0 ? `${hours}小时${mins}分钟` : `${mins}分钟`;
      }

      return minutes;
    },
    showStudentDetail(student) {
      console.log('查看学生详情:', student);

      // 检查学生ID是否有效
      if (!student || !student.student_id) {
        this.$message.warning('无效的学生数据');
        return;
      }

      // 跳转到学生详情页面
      this.$router.push({
        path: '/teacher/student-detail',
        query: { id: student.student_id }
      });
    }
  }
}
</script>

<style scoped>
.teacher-data-analysis-container {
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
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.class-selector-container {
  display: flex;
  align-items: center;
  margin-right: 15px;
  min-width: 250px;
}

.selector-label {
  margin-right: 10px;
  font-size: 14px;
  font-weight: 500;
  color: #606266;
  white-space: nowrap;
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

.stats-cards {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 20px;
}

.stat-card {
  flex: 1;
  min-width: 200px;
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

.analysis-section ul {
  padding-left: 20px;
}

.analysis-section li {
  margin-bottom: 5px;
}

.student-data-card {
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style>
