<template>
  <div class="teacher-problems-container">
    <TeacherNavbar />

    <div class="teacher-problems">
      <h1>题目管理</h1>

      <!-- 题目表单 -->
      <div class="problem-form-container">
        <h2>{{ isEditing ? '编辑题目' : '添加新题目' }}</h2>

        <el-form :model="problemForm" :rules="rules" ref="problemForm" label-width="100px">
          <el-form-item label="题目名称" prop="title">
            <el-input v-model="problemForm.title" placeholder="请输入题目名称"></el-input>
          </el-form-item>

          <el-form-item label="题目难度" prop="difficulty">
            <el-select v-model="problemForm.difficulty" placeholder="请选择题目难度" style="width: 100%">
              <el-option label="简单" value="easy"></el-option>
              <el-option label="中等" value="medium"></el-option>
              <el-option label="困难" value="hard"></el-option>
            </el-select>
          </el-form-item>

          <!-- 添加章节选择 -->
          <el-form-item label="关联章节" prop="chapterId">
            <el-select v-model="problemForm.chapterId" placeholder="请选择关联章节" style="width: 100%" filterable clearable>
              <el-option
                v-for="chapter in chapters"
                :key="chapter.chapter_id"
                :label="`${chapter.chapter_number} ${chapter.chapter_title}`"
                :value="chapter.chapter_id">
              </el-option>
            </el-select>
          </el-form-item>

          <el-form-item label="题目详情" prop="content">
            <el-input type="textarea" v-model="problemForm.content"
                      placeholder="请输入题目详情" :rows="6"></el-input>
          </el-form-item>

          <!-- 新增输入示例字段 -->
          <el-form-item label="输入示例" prop="inputExample">
            <el-input type="textarea" v-model="problemForm.inputExample"
                      placeholder="请输入示例数据" :rows="3"></el-input>
          </el-form-item>

          <!-- 新增输出示例字段 -->
          <el-form-item label="输出示例" prop="outputExample">
            <el-input type="textarea" v-model="problemForm.outputExample"
                      placeholder="请输入期望输出" :rows="3"></el-input>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="submitProblem" :loading="submitting">
              {{ isEditing ? '更新题目' : '提交题目' }}
            </el-button>
            <el-button @click="resetForm">重置</el-button>
            <el-button v-if="isEditing" @click="cancelEdit">取消编辑</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 题目列表 -->
      <div class="problems-list-container">
        <h2>题目列表</h2>

        <!-- 过滤和搜索 -->
        <div class="filter-container">
          <el-input
            placeholder="搜索题目"
            v-model="searchQuery"
            clearable
            prefix-icon="el-icon-search"
            style="width: 300px; margin-right: 10px;"
          ></el-input>

          <el-select v-model="difficultyFilter" placeholder="难度筛选" clearable style="margin-right: 10px;">
            <el-option label="全部" value=""></el-option>
            <el-option label="简单" value="easy"></el-option>
            <el-option label="中等" value="medium"></el-option>
            <el-option label="困难" value="hard"></el-option>
          </el-select>

          <!-- 添加章节筛选 -->
          <el-select v-model="chapterFilter" placeholder="章节筛选" clearable style="width: 180px;" filterable>
            <el-option label="全部章节" value=""></el-option>
            <el-option
              v-for="chapter in chapters"
              :key="chapter.chapter_id"
              :label="`${chapter.chapter_number} ${chapter.chapter_title}`"
              :value="chapter.chapter_id">
            </el-option>
          </el-select>

          <!-- 批量设置章节按钮 -->
          <el-button
            type="primary"
            icon="el-icon-s-operation"
            style="margin-left: auto; margin-right: 10px;"
            @click="showBatchChapterDialog">
            批量设置章节
          </el-button>

          <!-- 添加查看问题按钮 -->
          <el-button
            type="info"
            icon="el-icon-question"
            @click="goToQuestionsList">
            查看题目相关问题
          </el-button>
        </div>

        <!-- 题目表格 -->
        <el-table :data="filteredProblems" style="width: 100%" v-loading="loading">
          <el-table-column prop="title" label="题目名称" min-width="180"></el-table-column>
          <el-table-column prop="difficulty" label="难度" width="80">
            <template #default="scope">
              <el-tag :type="getDifficultyTag(scope.row.difficulty)">
                {{ getDifficultyText(scope.row.difficulty) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="chapter_id" label="关联章节" width="180">
            <template #default="scope">
              <el-tag v-if="scope.row.chapter_id" type="info">
                {{ getChapterName(scope.row.chapter_id) }}
              </el-tag>
              <span v-else>未关联章节</span>
            </template>
          </el-table-column>
          <el-table-column prop="teacher_email" label="出题教师" width="180"></el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="150"></el-table-column>
          <el-table-column label="操作" width="340" fixed="right">
            <template #default="scope">
              <div class="operation-buttons">
                <!-- 仅题目所有者可以编辑和删除 -->
                <template v-if="scope.row.is_owner">
                  <el-button size="mini" @click="editProblem(scope.row)" type="primary">编辑</el-button>
                  <el-button size="mini" @click="deleteProblem(scope.row.id)" type="danger">删除</el-button>
                </template>
                <el-button size="mini" @click="viewSubmissions(scope.row)" type="info">答题情况</el-button>
                <el-button size="mini" @click="viewQuestions(scope.row)" type="info">相关问题</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- 添加问题对话框组件 -->
    <QuestionDialogComponent
      v-model:visible="questionDialogVisible"
      :is-teacher="true"
      :related-problem-id="currentProblemId"
      @question-submitted="handleQuestionSubmitted"
    />

    <!-- 添加答题情况对话框 -->
    <el-dialog
      title="答题情况"
      v-model="submissionsDialogVisible"
      width="70%">
      <el-table :data="submissionStats" v-loading="loadingStats">
        <el-table-column prop="student_class" label="班级"></el-table-column>
        <el-table-column prop="student_id" label="学号"></el-table-column>
        <el-table-column prop="submission_count" label="提交次数"></el-table-column>
        <el-table-column prop="best_result" label="最佳结果">
          <template #default="scope">
            <el-tag :type="scope.row.best_result === 'success' ? 'success' : 'danger'">
              {{ scope.row.best_result === 'success' ? '通过' : '未通过' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="first_submission" label="首次提交时间"></el-table-column>
        <el-table-column prop="last_submission" label="最近提交时间"></el-table-column>
      </el-table>
    </el-dialog>

    <!-- 批量设置章节对话框 -->
    <el-dialog
      title="批量设置章节关联"
      v-model="batchChapterDialogVisible"
      width="50%">
      <div>
        <p>选择要设置的章节：</p>
        <el-select v-model="batchChapterId" placeholder="请选择章节" style="width: 100%" filterable>
          <el-option
            v-for="chapter in chapters"
            :key="chapter.chapter_id"
            :label="`${chapter.chapter_number} ${chapter.chapter_title}`"
            :value="chapter.chapter_id">
          </el-option>
        </el-select>

        <p style="margin-top: 20px;">选择筛选条件：</p>
        <el-radio-group v-model="batchFilterType">
          <el-radio label="all">所有题目</el-radio>
          <el-radio label="difficulty">按难度筛选</el-radio>
          <el-radio label="noChapter">未关联章节的题目</el-radio>
        </el-radio-group>

        <el-select
          v-if="batchFilterType === 'difficulty'"
          v-model="batchDifficulty"
          placeholder="选择难度"
          style="margin-top: 10px; width: 100%">
          <el-option label="简单" value="easy"></el-option>
          <el-option label="中等" value="medium"></el-option>
          <el-option label="困难" value="hard"></el-option>
        </el-select>

        <p style="margin-top: 20px;">将更新以下题目：</p>
        <el-table ref="batchTable" :data="batchFilteredProblems" style="width: 100%" max-height="300px">
          <el-table-column type="selection" width="55"></el-table-column>
          <el-table-column prop="title" label="题目名称" min-width="180"></el-table-column>
          <el-table-column prop="difficulty" label="难度" width="80">
            <template #default="scope">
              <el-tag :type="getDifficultyTag(scope.row.difficulty)">
                {{ getDifficultyText(scope.row.difficulty) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="chapter_id" label="当前章节" width="150">
            <template #default="scope">
              <el-tag v-if="scope.row.chapter_id" type="info">
                {{ getChapterName(scope.row.chapter_id) }}
              </el-tag>
              <span v-else>未关联章节</span>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="batchChapterDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="batchUpdateChapter" :loading="batchUpdating">
            确认更新
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import TeacherNavbar from '../../components/teacher/TeacherNavbar.vue';
import QuestionDialogComponent from '../../components/common/QuestionDialogComponent.vue';

export default {
  name: 'TeacherProblems',
  components: {
    TeacherNavbar,
    QuestionDialogComponent
  },
  data() {
    return {
      problemForm: {
        id: null,
        title: '',
        difficulty: '',
        content: '',
        inputExample: '',   // 新增输入示例字段
        outputExample: '',   // 新增输出示例字段
        chapterId: ''       // 新增关联章节字段
      },
      chapters: [],         // 章节列表
      rules: {
        title: [
          { required: true, message: '请输入题目名称', trigger: 'blur' },
          { min: 2, max: 100, message: '长度在 2 到 100 个字符', trigger: 'blur' }
        ],
        difficulty: [
          { required: true, message: '请选择题目难度', trigger: 'change' }
        ],
        content: [
          { required: true, message: '请输入题目详情', trigger: 'blur' }
        ],
        // 输入输出示例可以为空，不添加required规则
      },
      problems: [],
      isEditing: false,
      submitting: false,
      loading: false,
      searchQuery: '',
      difficultyFilter: '',
      chapterFilter: '',
      // 添加问题对话框相关数据
      questionDialogVisible: false,
      currentProblemId: null,
      submissionsDialogVisible: false,
      submissionStats: [],
      loadingStats: false,
      // 批量设置章节相关数据
      batchChapterDialogVisible: false,
      batchChapterId: '',
      batchFilterType: 'all',
      batchDifficulty: 'easy',
      batchSelectedProblems: [],
      batchUpdating: false,
    }
  },
  mounted() {
    this.loadProblems();
    this.loadChapters();
  },
  computed: {
    filteredProblems() {
      return this.problems.filter(problem => {
        // 难度筛选
        const matchesDifficulty = !this.difficultyFilter || problem.difficulty === this.difficultyFilter;

        // 章节筛选
        const matchesChapter = !this.chapterFilter || problem.chapter_id === this.chapterFilter;

        // 搜索查询
        const matchesSearch = !this.searchQuery ||
          problem.title.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
          problem.content.toLowerCase().includes(this.searchQuery.toLowerCase());

        return matchesDifficulty && matchesChapter && matchesSearch;
      });
    },

    // 批量设置章节时的筛选题目
    batchFilteredProblems() {
      return this.problems.filter(problem => {
        if (this.batchFilterType === 'all') {
          return true;
        } else if (this.batchFilterType === 'difficulty') {
          return problem.difficulty === this.batchDifficulty;
        } else if (this.batchFilterType === 'noChapter') {
          return !problem.chapter_id;
        }
        return false;
      });
    }
  },
  methods: {
    // 加载章节列表
    async loadChapters() {
      try {
        const response = await fetch('/api/teaching-content/chapters');
        const data = await response.json();

        if (data.success && Array.isArray(data.chapters)) {
          this.chapters = data.chapters;
        } else {
          console.error('获取章节列表失败:', data);
        }
      } catch (error) {
        console.error('加载章节列表出错:', error);
      }
    },

    // 加载题目列表
    async loadProblems() {
      this.loading = true;
      try {
        const email = sessionStorage.getItem('userEmail');
        if (!email) {
          this.$message.error('用户未登录，将使用测试数据');
          // 使用测试数据，修改时间格式
          const now = new Date().toLocaleString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
          }).replace(/\//g, '-');

          this.problems = [
            {
              id: 1,
              title: '本地测试题目1',
              difficulty: 'easy',
              content: '这是一个本地测试题目',
              created_at: now,
              updated_at: now
            },
            {
              id: 2,
              title: '本地测试题目2',
              difficulty: 'medium',
              content: '这是第二个本地测试题目',
              created_at: now,
              updated_at: now
            }
          ];
          return;
        }

        // 尝试从API加载数据
        const response = await fetch(`/api/problems/teacher/${email}`);

        if (!response.ok) {
          console.error(`API请求失败: ${response.status} ${response.statusText}`);
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

    // 提交题目
    async submitProblem() {
      try {
        await this.$refs.problemForm.validate();
      } catch (error) {
        return;
      }

      this.submitting = true;

      try {
        const email = sessionStorage.getItem('userEmail');
        if (!email) {
          this.$message.error('用户未登录');
          return;
        }

        let response;

        // 添加调试信息
        console.log('准备发送请求到:', this.isEditing ?
          `/api/problems/${this.problemForm.id}` : '/api/problems/submit');

        if (this.isEditing) {
          // 更新现有题目
          response = await fetch(`/api/problems/${this.problemForm.id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              title: this.problemForm.title,
              difficulty: this.problemForm.difficulty,
              content: this.problemForm.content,
              inputExample: this.problemForm.inputExample,   // 添加输入示例
              outputExample: this.problemForm.outputExample, // 添加输出示例
              chapterId: this.problemForm.chapterId          // 添加章节ID
            })
          });
        } else {
          // 创建新题目
          response = await fetch('/api/problems/submit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              email: email,
              title: this.problemForm.title,
              difficulty: this.problemForm.difficulty,
              content: this.problemForm.content,
              inputExample: this.problemForm.inputExample,   // 添加输入示例
              outputExample: this.problemForm.outputExample, // 添加输出示例
              chapterId: this.problemForm.chapterId          // 添加章节ID
            })
          });
        }

        // 检查响应状态
        if (!response.ok) {
          const contentType = response.headers.get('content-type');
          if (contentType && contentType.includes('application/json')) {
            const errorData = await response.json();
            throw new Error(errorData.message || `服务器错误: ${response.status}`);
          } else {
            // 如果不是JSON响应，获取文本内容用于调试
            const textResponse = await response.text();
            console.error('服务器返回非JSON数据:', textResponse.substring(0, 200));
            throw new Error(`服务器返回了非预期的响应: ${response.status}`);
          }
        }

        const data = await response.json();

        if (data.success) {
          this.$message.success(this.isEditing ? '题目已更新' : '题目已提交');
          this.resetForm();
          this.loadProblems();
        } else {
          this.$message.error(data.message || '操作失败');
        }
      } catch (error) {
        console.error('提交题目出错:', error);
        this.$message.error(`提交失败: ${error.message}`);
      } finally {
        this.submitting = false;
      }
    },

    // 编辑题目
    editProblem(problem) {
      this.isEditing = true;
      this.problemForm.id = problem.id;
      this.problemForm.title = problem.title;
      this.problemForm.difficulty = problem.difficulty;
      this.problemForm.content = problem.content;
      this.problemForm.inputExample = problem.input_example || '';  // 添加输入示例，处理可能为null的情况
      this.problemForm.outputExample = problem.output_example || ''; // 添加输出示例，处理可能为null的情况
      this.problemForm.chapterId = problem.chapter_id || ''; // 添加章节ID，处理可能为null的情况

      // 滚动到表单顶部
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
    },

    // 删除题目
    async deleteProblem(problemId) {
      if (!confirm('确定要删除这个题目吗？')) {
        return;
      }

      try {
        const response = await fetch(`/api/problems/${problemId}`, {
          method: 'DELETE'
        });
        const data = await response.json();

        if (data.success) {
          this.$message.success('题目已删除');
          this.loadProblems();
        } else {
          this.$message.error(data.message || '删除失败');
        }
      } catch (error) {
        console.error('删除题目出错:', error);
        this.$message.error('删除失败，请重试');
      }
    },

    // 重置表单
    resetForm() {
      this.$refs.problemForm.resetFields();
      if (this.isEditing) {
        this.isEditing = false;
        this.problemForm.id = null;
      }
    },

    // 取消编辑
    cancelEdit() {
      this.isEditing = false;
      this.problemForm.id = null;
      this.resetForm();
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

    // 获取章节名称
    getChapterName(chapterId) {
      if (!chapterId) return '未关联章节';

      const chapter = this.chapters.find(ch => ch.chapter_id === chapterId);
      if (chapter) {
        return `${chapter.chapter_number} ${chapter.chapter_title}`;
      }
      return '未知章节';
    },

    // 跳转到问题列表页面
    goToQuestionsList() {
      this.$router.push('/teacher/answer');
    },

    // 显示批量设置章节对话框
    showBatchChapterDialog() {
      this.batchChapterDialogVisible = true;
      this.batchChapterId = '';
      this.batchFilterType = 'all';
      this.batchDifficulty = 'easy';
      this.batchSelectedProblems = [];
    },

    // 批量更新章节关联
    async batchUpdateChapter() {
      if (!this.batchChapterId) {
        this.$message.warning('请选择要关联的章节');
        return;
      }

      // 获取选中的题目
      const selectedRows = this.$refs.batchTable.selection;
      if (!selectedRows || selectedRows.length === 0) {
        this.$message.warning('请选择要更新的题目');
        return;
      }

      this.batchUpdating = true;

      try {
        // 逐个更新题目的章节关联
        for (const problem of selectedRows) {
          await fetch(`/api/problems/${problem.id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              title: problem.title,
              difficulty: problem.difficulty,
              content: problem.content,
              inputExample: problem.input_example || '',
              outputExample: problem.output_example || '',
              chapterId: this.batchChapterId
            })
          });
        }

        this.$message.success(`成功更新 ${selectedRows.length} 个题目的章节关联`);
        this.batchChapterDialogVisible = false;

        // 重新加载题目列表
        this.loadProblems();
      } catch (error) {
        console.error('批量更新章节失败:', error);
        this.$message.error('批量更新章节失败，请查看控制台了解详情');
      } finally {
        this.batchUpdating = false;
      }
    },

    // 查看特定题目相关的问题
    viewQuestions(problem) {
      this.currentProblemId = problem.id;
      this.questionDialogVisible = true;
    },

    // 处理问题提交成功的回调
    handleQuestionSubmitted() {
      this.$notify({
        title: '成功',
        message: '问题答复已提交',
        type: 'success',
        duration: 2000
      });

      // 可以根据需要添加额外的逻辑，例如更新问题列表等
    },

    // 查看答题情况
    async viewSubmissions(problem) {
      this.submissionsDialogVisible = true;
      this.loadingStats = true;

      try {
        const response = await fetch(`/api/problems/${problem.id}/submissions`);
        const data = await response.json();

        if (data.success) {
          this.submissionStats = data.submissions;
        } else {
          this.$message.error(data.message || '获取答题情况失败');
        }
      } catch (error) {
        console.error('获取答题情况失败:', error);
        this.$message.error('获取答题情况失败');
      } finally {
        this.loadingStats = false;
      }
    },
  }
}
</script>

<style scoped>
.teacher-problems-container {
  display: flex;
}

.teacher-problems {
  padding: 20px;
  background-color: #f4f4f4;
  min-height: 100vh;
  margin-left: 250px; /* 与侧边栏宽度相同 */
  width: calc(100% - 250px);
  box-sizing: border-box;
}

.problem-form-container, .problems-list-container {
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.filter-container {
  display: flex;
  margin-bottom: 15px;
  align-items: center;
}

.operation-buttons {
  display: flex;
  gap: 8px;  /* 按钮之间的间距 */
  justify-content: flex-start;
  flex-wrap: nowrap;
  padding: 0 4px;
}

.operation-buttons .el-button {
  margin-left: 0;  /* 覆盖element-ui的默认间距 */
  margin-right: 0;
}

@media (max-width: 768px) {
  .teacher-problems {
    margin-left: 0;
    width: 100%;
  }
}
</style>