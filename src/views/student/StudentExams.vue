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

        <!-- 添加提问按钮 -->
        <el-button
          type="info"
          icon="el-icon-question"
          style="margin-left: auto"
          @click="showQuestionDialog(null)">
          提交问题
        </el-button>
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
                type="text"
                @click="showFullContent(scope.row)">
                查看完整题目
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
        <el-table-column label="操作" width="250">
          <template #default="scope">
            <el-button size="mini" type="primary" @click="startSolveProblem(scope.row)">
              开始解题
            </el-button>
            <el-button size="mini" type="info" @click="showQuestionDialog(scope.row.id)">
              提问
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

          <!-- 添加输入示例显示 -->
          <template v-if="currentProblem?.input_example">
            <h3>输入示例:</h3>
            <div class="example-box">
              <pre>{{ currentProblem.input_example }}</pre>
            </div>
          </template>

          <!-- 添加输出示例显示 -->
          <template v-if="currentProblem?.output_example">
            <h3>输出示例:</h3>
            <div class="example-box">
              <pre>{{ currentProblem.output_example }}</pre>
            </div>
          </template>

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
            <el-button type="info" @click="showQuestionFromDetail()">
              提交问题
            </el-button>
          </span>
        </template>
      </el-dialog>

      <!-- 问题对话框组件 -->
      <QuestionDialogComponent
        v-model:visible="questionDialogVisible"
        :is-teacher="false"
        :related-problem-id="selectedProblemId"
        @question-submitted="handleQuestionSubmitted"
      />
    </div>
  </div>
</template>

<script>
import StudentNavbar from '../../components/student/StudentNavbar.vue';
import QuestionDialogComponent from '../../components/common/QuestionDialogComponent.vue';

export default {
  name: 'StudentExams',
  components: {
    StudentNavbar,
    QuestionDialogComponent
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
      dialogVisible: false,
      // 添加问题对话框相关数据
      questionDialogVisible: false,
      selectedProblemId: null,
      // 添加题目状态相关数据
      problemStatusData: {},
      loadingStatus: false
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
      // 优先使用后端数据，如果后端数据不可用则使用本地存储
      const statusMap = {};
      this.problems.forEach(problem => {
        let statusFound = false;

        // 检查是否有后端数据
        if (this.problemStatusData && this.problemStatusData.problem_details) {
          // 在后端数据中查找当前题目
          const problemDetail = this.problemStatusData.problem_details.find(
            detail => detail.problem_id === problem.id.toString()
          );

          if (problemDetail) {
            // 如果找到后端数据，使用后端数据的状态
            statusMap[problem.id] = problemDetail.is_solved ? 'completed' : 'inProgress';
            statusFound = true;
          }
        }

        // 如果没有找到后端数据，回退到本地存储
        if (!statusFound) {
          const storageKey = `problem-status-${problem.id}`;
          const status = localStorage.getItem(storageKey) || 'notStarted';
          statusMap[problem.id] = status;
        }
      });
      return statusMap;
    }
  },
  mounted() {
    // 监听侧边栏折叠状态变化的事件
    window.addEventListener('resize', this.checkSidebarState);
    this.checkSidebarState();

    // 加载题目列表（会自动加载题目状态）
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

          // 加载题目后刷新题目状态
          this.loadProblemStatus();
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

      // 延迟一段时间后刷新题目状态（给后端一些时间更新）
      setTimeout(() => {
        this.loadProblemStatus();
      }, 3000);
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

      // 创建一个弹窗提示用户操作
      this.$confirm('请选择如何打开VSCode：', '跳转到VSCode', {
        confirmButtonText: '打开新窗口',
        cancelButtonText: '切换到已有窗口',
        type: 'info',
        center: true,
        distinguishCancelAndClose: true,
        showClose: false,
        closeOnClickModal: false
      }).then(() => {
        // 用户选择打开新窗口
        this.openNewVSCodeWindow(problem.id);
      }).catch(action => {
        if (action === 'cancel') {
          // 用户选择切换到已有窗口
          this.switchToExistingVSCode(problem.id);
        }
      });

      // 关闭其他对话框
      this.dialogVisible = false;
    },

    // 打开新的VSCode窗口
    openNewVSCodeWindow(problemId) {
      try {
        // 使用随机参数避免缓存
        const random = Math.random().toString(36).substring(2);

        // 使用正确的VSCode协议格式来打开新窗口
        // 注意：vscode协议不支持直接在file后面使用new-window作为路径
        const url = `vscode://vscode.commands.executeCommand/workbench.action.newWindow?problemId=${problemId}&r=${random}`;
        window.location.href = url;

        // 备选方案1：使用另一种命令格式
        setTimeout(() => {
          if (!document.hidden) { // 如果页面仍可见，说明可能第一个协议未生效
            const link = document.createElement('a');
            link.href = `vscode://vscode.env.openWindow?problemId=${problemId}&r=${random}`;
            link.click();
          }
        }, 500);

        // 备选方案2：尝试启动VSCode不带任何参数
        setTimeout(() => {
          if (!document.hidden) { // 如果页面仍可见，说明之前的协议未生效
            const link = document.createElement('a');
            link.href = `vscode://`;
            link.click();
          }
        }, 1000);

        this.$notify({
          title: '正在打开新的VSCode窗口',
          message: '如果自动打开失败，请手动启动VSCode',
          type: 'info',
          duration: 5000
        });
      } catch (e) {
        console.error('打开新VSCode窗口失败:', e);
        this.showManualVSCodeOpeningDialog();
      }
    },

    // 切换到已有的VSCode窗口
    switchToExistingVSCode(problemId) {
      try {
        // 存储一个标记，表明我们尝试激活现有窗口
        localStorage.setItem('vscode-activation-target', 'existing-window');
        localStorage.setItem('vscode-current-problem-id', problemId.toString());

        // 使用随机参数避免缓存
        // const random = Math.random().toString(36).substring(2);

        // 使用多种尝试方法激活VSCode
        const activationMethods = [
          // 1. 直接使用最基础的协议 - 这应该会激活VSCode但不会创建新窗口
          () => {
            window.location.href = `vscode://`;
          },

          // 2. 使用文件浏览器命令
          () => {
            const link = document.createElement('a');
            link.href = `vscode://file-explorer.focus`;
            link.click();
          },

          // 3. 尝试使用更广泛支持的URL格式
          // () => {
          //   const link = document.createElement('a');
          //   // 使用斜杠后面添加多路径参数，这通常更可靠
          //   link.href = `vscode://file/focus/explorer?r=${random}`;
          //   link.click();
          // },

          // 4. 打开命令面板
          () => {
            const link = document.createElement('a');
            link.href = `vscode://workbench/command-palette`;
            link.click();
          }
        ];

        // 按顺序尝试不同的激活方法，间隔300ms
        let currentMethodIndex = 0;
        const tryNextMethod = () => {
          if (currentMethodIndex < activationMethods.length) {
            activationMethods[currentMethodIndex]();
            currentMethodIndex++;
            setTimeout(tryNextMethod, 300);
          } else {
            // 所有方法都尝试后，显示手动指引
            setTimeout(() => {
              if (!document.hidden) {
                this.showImprovedManualVSCodeSwitchDialog();
              }
            }, 500);
          }
        };

        // 开始尝试激活VSCode
        tryNextMethod();

        this.$notify({
          title: '正在切换到VSCode',
          message: '正在尝试激活已运行的VSCode窗口',
          type: 'info',
          duration: 3000
        });

      } catch (e) {
        console.error('切换到现有VSCode窗口失败:', e);
        this.showImprovedManualVSCodeSwitchDialog();
      }
    },

    // 显示手动打开VSCode的对话框
    showManualVSCodeOpeningDialog() {
      this.$alert(
        `<div>
           <p>请按照以下步骤手动打开VSCode:</p>
           <ol>
             <li>切换到正在运行的VSCode窗口</li>
             <li>如果VSCode未运行，请手动启动VSCode应用程序</li>
             <li>题目信息已准备好，可以在VSCode中开始解题</li>
           </ol>
         </div>`,
        '手动打开VSCode',
        {
          dangerouslyUseHTMLString: true,
          confirmButtonText: '我已打开VSCode',
          center: true,
          callback: () => {
            this.$message({
              type: 'success',
              message: '题目已加载，祝解题愉快！'
            });
          }
        }
      );
    },

    // 改进的手动切换VSCode对话框
    showImprovedManualVSCodeSwitchDialog() {
      this.$alert(
        `<div>
          <p>自动切换VSCode窗口失败，请尝试以下步骤:</p>
          <ol>
            <li><strong>直接切换窗口</strong>: 使用Alt+Tab切换到已打开的VSCode窗口</li>
            <li><strong>检查任务栏</strong>: 点击任务栏上的VSCode图标切换窗口</li>
            <li><strong>手动启动</strong>: 如果VSCode未运行，请从开始菜单打开VSCode</li>
          </ol>
          <p>题目信息已保存，VSCode插件会自动加载相关题目。</p>
        </div>`,
        '手动切换到VSCode',
        {
          dangerouslyUseHTMLString: true,
          confirmButtonText: '我已切换到VSCode',
          center: true,
          callback: () => {
            this.$message({
              type: 'success',
              message: '题目已准备好，祝解题愉快！'
            });
          }
        }
      );
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
    },

    // 显示问题对话框
    showQuestionDialog(problemId) {
      this.selectedProblemId = problemId;
      this.questionDialogVisible = true;

      // 如果当前有题目详情对话框打开，则关闭它
      if (this.dialogVisible) {
        this.dialogVisible = false;
      }
    },

    // 从详情对话框打开问题对话框
    showQuestionFromDetail() {
      if (this.currentProblem) {
        this.selectedProblemId = this.currentProblem.id;
        this.questionDialogVisible = true;
        this.dialogVisible = false;
      }
    },

    // 处理问题提交成功的回调
    handleQuestionSubmitted() {
      this.$notify({
        title: '成功',
        message: '您的问题已提交，教师会尽快答复',
        type: 'success',
        duration: 3000
      });
    },

    // 从后端加载题目状态
    async loadProblemStatus() {
      this.loadingStatus = true;

      try {
        // 获取当前用户的学生ID
        const userProfile = JSON.parse(sessionStorage.getItem('userProfile') || '{}');
        const studentId = userProfile.studentId || sessionStorage.getItem('userEmail');

        if (!studentId) {
          console.error('无法获取学生ID');
          return;
        }

        console.log('正在获取学生题目状态，学生ID:', studentId);

        // 调用后端API获取学生的编程统计数据
        const response = await fetch(`/api/coding/stats/${encodeURIComponent(studentId)}`);

        // 保存原始响应文本用于调试
        const responseText = await response.text();
        console.log('原始响应文本:', responseText);

        let data;
        try {
          // 处理可能包含多个JSON对象的情况
          // 尝试获取最后一个有效的JSON对象
          const jsonLines = responseText.split(/\r?\n/).filter(line => line.trim());
          if (jsonLines.length > 0) {
            // 使用最后一个JSON对象
            const lastJsonLine = jsonLines[jsonLines.length - 1];
            data = JSON.parse(lastJsonLine);
            console.log('使用最后一个JSON对象:', lastJsonLine);
          } else {
            throw new Error('响应中没有有效的JSON对象');
          }
        } catch (e) {
          console.error('解析响应JSON失败:', e);
          console.error('原始响应文本:', responseText);
          return;
        }

        if (data.success && data.data) {
          console.log('获取到的题目状态数据:', data.data);
          this.problemStatusData = data.data;

          // 打印每个题目的状态，用于调试
          if (data.data.problem_details) {
            console.log('题目状态详情:');
            data.data.problem_details.forEach(detail => {
              console.log(`题目ID: ${detail.problem_id}, 是否已解决: ${detail.is_solved}`);
            });
          }
        } else {
          console.error('获取题目状态失败:', data);
        }
      } catch (error) {
        console.error('加载题目状态出错:', error);
      } finally {
        this.loadingStatus = false;
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
  align-items: center;
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

/* 新增输入输出示例样式 */
.problem-detail .example-box {
  padding: 10px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  background-color: #f5f5f5;
  margin-bottom: 15px;
  overflow-x: auto;
}

.problem-detail .example-box pre {
  margin: 0;
  font-family: 'Courier New', Courier, monospace;
  white-space: pre-wrap;
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