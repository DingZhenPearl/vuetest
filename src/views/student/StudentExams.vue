<template>
  <div class="student-layout">
    <!-- 引入导航栏 -->
    <StudentNavbar />
    
    <div class="student-exams" :class="{ 'with-sidebar': !isSidebarCollapsed }">
      <h1>编程题目列表</h1>
      
      <div class="exam-filters">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索题目"
          prefix-icon="el-icon-search"
          clearable
          class="search-input"
        />
        <el-select v-model="difficultyFilter" placeholder="难度筛选" clearable style="width: 120px">
          <el-option label="全部" value="" />
          <el-option label="简单" value="easy" />
          <el-option label="中等" value="medium" />
          <el-option label="困难" value="hard" />
        </el-select>
      </div>

      <!-- 添加刷新按钮 -->
      <el-button 
        type="primary" 
        :icon="refreshIcon" 
        style="margin-bottom: 15px"
        @click="loadProblems"
        :loading="loading">
        刷新题目列表
      </el-button>

      <el-table :data="filteredProblems" style="width: 100%" v-loading="loading" border>
        <el-table-column prop="title" label="题目名称" width="200" />
        <el-table-column prop="content" label="题目内容">
          <template #default="scope">
            <div class="problem-content">
              {{ truncateContent(scope.row.content) }}
              <el-button 
                v-if="scope.row.content && scope.row.content.length > 100" 
                type="text" 
                @click="showFullContent(scope.row)">
                查看完整内容
              </el-button>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="difficulty" label="难度" width="120">
          <template #default="scope">
            <el-tag :type="getDifficultyTag(scope.row.difficulty)">{{ getDifficultyText(scope.row.difficulty) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="发布时间" width="180">
          <template #default="scope">
            {{ formatDateTime(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(getStatusForProblem(scope.row.id))">
              {{ getStatusText(getStatusForProblem(scope.row.id)) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button size="mini" type="primary" @click="startSolveProblem(scope.row)">
              开始解题
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 题目详情对话框 -->
      <el-dialog 
        v-model="dialogVisible" 
        :title="currentProblem?.title || '题目详情'" 
        width="70%">
        <div class="problem-detail">
          <h3>难度: <el-tag :type="getDifficultyTag(currentProblem?.difficulty)">
            {{ getDifficultyText(currentProblem?.difficulty) }}
          </el-tag></h3>
          <div class="content-box">
            {{ currentProblem?.content }}
          </div>
          <div class="dialog-footer">
            <p class="publish-time">发布时间: {{ formatDateTime(currentProblem?.created_at) }}</p>
          </div>
        </div>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="dialogVisible = false">关闭</el-button>
            <el-button type="primary" @click="startSolveProblem(currentProblem)">
              开始解题
            </el-button>
          </span>
        </template>
      </el-dialog>
    </div>
  </div>
</template>

<script>
import StudentNavbar from '../../components/student/StudentNavbar.vue';

export default {
  name: 'StudentExams',
  components: {
    StudentNavbar
  },
  data() {
    return {
      loading: false,
      searchKeyword: '',
      difficultyFilter: '',
      isSidebarCollapsed: false,
      refreshIcon: 'el-icon-refresh',
      problems: [],
      currentProblem: null,
      dialogVisible: false
    }
  },
  computed: {
    filteredProblems() {
      return this.problems.filter(problem => {
        // 筛选关键词
        const matchesKeyword = this.searchKeyword === '' || 
          problem.title.toLowerCase().includes(this.searchKeyword.toLowerCase()) ||
          problem.content.toLowerCase().includes(this.searchKeyword.toLowerCase());
        
        // 筛选难度
        const matchesDifficulty = this.difficultyFilter === '' || problem.difficulty === this.difficultyFilter;
        
        return matchesKeyword && matchesDifficulty;
      });
    },
    problemStatus() {
      // 从本地存储获取题目状态
      const statusMap = {};
      this.problems.forEach(problem => {
        const storageKey = `problem-status-${problem.id}`;
        const status = localStorage.getItem(storageKey) || 'notStarted';
        statusMap[problem.id] = status;
      });
      return statusMap;
    }
  },
  mounted() {
    // 监听侧边栏折叠状态变化的事件
    window.addEventListener('resize', this.checkSidebarState);
    this.checkSidebarState();
    
    // 加载题目列表
    this.loadProblems();
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.checkSidebarState);
  },
  methods: {
    // 加载题目列表
    async loadProblems() {
      this.loading = true;
      
      try {
        const response = await fetch('/api/problems/all');
        
        if (!response.ok) {
          throw new Error(`HTTP错误! 状态码: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success && Array.isArray(data.problems)) {
          this.problems = data.problems;
        } else {
          console.error('获取题目列表失败:', data);
          this.$message.error(data.message || '获取题目列表失败');
        }
      } catch (error) {
        console.error('加载题目出错:', error);
        this.$message.error(`加载题目列表失败: ${error.message}`);
        
        // 使用测试数据作为备选
        this.problems = [
          {
            id: 1,
            title: '离线测试题目',
            difficulty: 'easy',
            content: '当API不可用时显示的测试题目',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
          }
        ];
      } finally {
        this.loading = false;
      }
    },
    
    // 截断内容
    truncateContent(content) {
      if (!content) return '';
      return content.length > 100 ? content.slice(0, 100) + '...' : content;
    },
    
    // 显示完整内容
    showFullContent(problem) {
      this.currentProblem = problem;
      this.dialogVisible = true;
    },
    
    // 格式化日期时间
    formatDateTime(dateTimeStr) {
      if (!dateTimeStr) return '';
      
      const date = new Date(dateTimeStr);
      return date.toLocaleString('zh-CN', { 
        year: 'numeric', 
        month: '2-digit', 
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      });
    },
    
    // 检查侧边栏状态
    checkSidebarState() {
      // 根据窗口宽度判断侧边栏状态
      this.isSidebarCollapsed = window.innerWidth <= 768;
    },
    
    // 开始解题
    startSolveProblem(problem) {
      // 保存当前选择的题目到本地存储
      localStorage.setItem('currentProblem', JSON.stringify(problem));
      
      // 更新题目状态为进行中
      localStorage.setItem(`problem-status-${problem.id}`, 'inProgress');
      
      // 尝试打开VSCode
      this.openVSCode(problem);
      
      // 关闭对话框（如果打开）
      this.dialogVisible = false;
    },
    
    // 打开VSCode
    openVSCode(problem) {
      // 创建一个临时解题工作区的信息
      const workspaceInfo = {
        problemId: problem.id,
        title: problem.title,
        difficulty: problem.difficulty,
        openTime: new Date().toISOString()
      };
      
      // 保存到本地存储
      localStorage.setItem(`problem-workspace-${problem.id}`, JSON.stringify(workspaceInfo));
      
      // 提示用户
      this.$notify({
        title: '准备解题',
        message: `题目《${problem.title}》已加载，请在VSCode中创建新文件来解答`,
        type: 'success',
        duration: 5000
      });
      
      // 使用VSCode协议尝试打开
      window.open('vscode://');
    },
    
    // 获取难度标签类型
    getDifficultyTag(difficulty) {
      switch(difficulty) {
        case 'easy': return 'success';
        case 'medium': return 'warning';
        case 'hard': return 'danger';
        default: return 'info';
      }
    },
    
    // 获取难度文本
    getDifficultyText(difficulty) {
      switch(difficulty) {
        case 'easy': return '简单';
        case 'medium': return '中等';
        case 'hard': return '困难';
        default: return '未知';
      }
    },
    
    // 获取题目状态
    getStatusForProblem(problemId) {
      return this.problemStatus[problemId] || 'notStarted';
    },
    
    // 获取状态标签类型
    getStatusType(status) {
      switch(status) {
        case 'notStarted': return 'info';
        case 'inProgress': return 'warning';
        case 'completed': return 'success';
        default: return 'info';
      }
    },
    
    // 获取状态文本
    getStatusText(status) {
      switch(status) {
        case 'notStarted': return '未开始';
        case 'inProgress': return '进行中';
        case 'completed': return '已完成';
        default: return '未知';
      }
    }
  }
}
</script>

<style scoped>
.student-layout {
  display: flex;
  width: 100%;
  min-height: 100vh;
}

.student-exams {
  padding: 20px;
  flex-grow: 1;
  transition: margin-left 0.3s;
  margin-left: 64px; /* 适应折叠侧边栏宽度 */
}

.student-exams.with-sidebar {
  margin-left: 250px; /* 适应展开侧边栏宽度 */
}

h1 {
  margin-bottom: 20px;
}

.exam-filters {
  display: flex;
  margin-bottom: 20px;
  gap: 10px;
}

.search-input {
  width: 250px;
}

.problem-content {
  white-space: pre-line;
  line-height: 1.5;
}

.problem-detail .content-box {
  white-space: pre-line;
  padding: 15px;
  border: 1px solid #eaeaea;
  border-radius: 5px;
  background-color: #f9f9f9;
  margin: 15px 0;
  line-height: 1.6;
  min-height: 100px;
  max-height: 400px;
  overflow-y: auto;
}

.publish-time {
  color: #999;
  font-size: 0.9em;
  text-align: right;
}

/* 响应式布局 */
@media (max-width: 768px) {
  .student-exams {
    margin-left: 0;
  }
  
  .student-exams.with-sidebar {
    margin-left: 0;
  }
  
  .exam-filters {
    flex-direction: column;
  }
  
  .search-input {
    width: 100%;
  }
}
</style>