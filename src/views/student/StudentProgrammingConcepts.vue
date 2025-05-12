<template>
  <div class="programming-concepts-container">
    <StudentNavbar />
    <div class="main-content">
      <div class="page-header">
        <h1>学习资源</h1>
        <p class="subtitle">按章节学习C++编程基础知识和进阶概念</p>
      </div>

      <!-- 章节导航 -->
      <el-card class="chapter-navigation" v-loading="loading">
        <template #header>
          <div class="card-header">
            <span>学习章节</span>
            <div class="header-actions">
              <el-input
                v-model="searchKeyword"
                placeholder="搜索章节或关键词"
                :prefix-icon="Search"
                clearable
                size="small"
                style="width: 220px; margin-right: 10px;"
              />
              <el-select v-model="difficultyFilter" placeholder="难度" size="small" style="width: 120px;">
                <el-option label="全部" value="" />
                <el-option label="入门" value="入门" />
                <el-option label="基础" value="基础" />
                <el-option label="中级" value="中级" />
                <el-option label="高级" value="高级" />
              </el-select>
            </div>
          </div>
        </template>

        <!-- 章节列表 -->
        <el-empty v-if="chapters.length === 0 && !loading" description="暂无章节内容"></el-empty>
        <el-collapse v-else v-model="activeChapters" accordion>
          <el-collapse-item v-for="chapter in filteredChapters" :key="chapter.id" :name="chapter.id">
            <template #title>
              <div class="chapter-title">
                <span class="chapter-number">{{ chapter.number }}</span>
                <span class="chapter-name">{{ chapter.title }}</span>
                <el-tag size="small" :type="getDifficultyType(chapter.difficulty)" class="chapter-difficulty">
                  {{ chapter.difficulty }}
                </el-tag>
              </div>
            </template>

            <!-- 章节内容 -->
            <div class="chapter-content">
              <p class="chapter-description">{{ chapter.description }}</p>

              <!-- 章节内的小节列表 -->
              <div class="sections-list">
                <div
                  v-for="section in chapter.sections"
                  :key="section.id"
                  class="section-item"
                  :class="{ 'completed': isCompleted(section.id) }"
                  @click="openSection(chapter, section)"
                >
                  <div class="section-info">
                    <div class="section-title">
                      <i :class="getSectionIcon(section.type)"></i>
                      <span>{{ section.title }}</span>
                    </div>
                    <div class="section-meta">
                      <span class="section-type">{{ getSectionType(section.type) }}</span>
                      <span class="section-duration">{{ section.duration }}分钟</span>
                    </div>
                  </div>
                  <div class="section-status">
                    <el-tag size="mini" :type="isCompleted(section.id) ? 'success' : 'info'">
                      {{ isCompleted(section.id) ? '已完成' : '未学习' }}
                    </el-tag>
                    <i class="el-icon-arrow-right"></i>
                  </div>
                </div>
              </div>
            </div>
          </el-collapse-item>
        </el-collapse>
      </el-card>

      <!-- 学习内容对话框 -->
      <el-dialog
        :title="currentSection ? currentSection.title : ''"
        v-model="sectionDialogVisible"
        width="80%"
        :before-close="closeSectionDialog"
        class="section-dialog"
      >
        <div v-if="currentSection" class="section-content">
          <!-- 理论内容 -->
          <div v-if="currentSection.type === 'theory'" class="theory-content">
            <div v-html="currentSection.content"></div>

            <div class="code-examples" v-if="currentSection.examples && currentSection.examples.length > 0">
              <h3>代码示例</h3>
              <div v-for="(example, index) in currentSection.examples" :key="index" class="code-example">
                <h4>{{ example.title }}</h4>
                <pre><code class="language-cpp">{{ example.code }}</code></pre>
                <p v-if="example.explanation">{{ example.explanation }}</p>
              </div>
            </div>
          </div>

          <!-- 练习内容 -->
          <div v-else-if="currentSection.type === 'exercise'" class="exercise-content">
            <div v-html="currentSection.content"></div>

            <div class="exercise-task">
              <h3>练习任务</h3>
              <p>{{ currentSection.task }}</p>
              <pre v-if="currentSection.template"><code class="language-cpp">{{ currentSection.template }}</code></pre>

              <el-input
                type="textarea"
                v-model="exerciseAnswer"
                :rows="10"
                placeholder="在这里编写你的代码..."
                class="exercise-textarea"
              ></el-input>

              <div class="exercise-actions">
                <el-button type="primary" @click="submitExercise">提交答案</el-button>
                <el-button @click="resetExercise">重置</el-button>
              </div>
            </div>
          </div>

          <!-- 视频内容 -->
          <div v-else-if="currentSection.type === 'video'" class="video-content">
            <div class="video-container">
              <iframe
                :src="currentSection.videoUrl"
                frameborder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowfullscreen="allowfullscreen"
                sandbox="allow-top-navigation allow-same-origin allow-forms allow-scripts"
                scrolling="no"
              ></iframe>
            </div>

            <div v-html="currentSection.content" class="video-description"></div>
          </div>

          <!-- 测验内容 -->
          <div v-else-if="currentSection.type === 'quiz'" class="quiz-content">
            <div v-html="currentSection.content"></div>

            <div class="quiz-questions">
              <div v-for="(question, qIndex) in currentSection.questions" :key="qIndex" class="quiz-question">
                <h3>问题 {{ qIndex + 1 }}: {{ question.text }}</h3>
                <el-radio-group v-model="quizAnswers[qIndex]">
                  <el-radio
                    v-for="(option, oIndex) in question.options"
                    :key="oIndex"
                    :label="oIndex"
                    class="quiz-option"
                  >
                    {{ option }}
                  </el-radio>
                </el-radio-group>
              </div>

              <div class="quiz-actions">
                <el-button type="primary" @click="submitQuiz">提交答案</el-button>
                <el-button @click="resetQuiz">重置</el-button>
              </div>
            </div>
          </div>
        </div>

        <template #footer>
          <span class="dialog-footer">
            <el-button @click="closeSectionDialog">关闭</el-button>
            <el-button type="primary" @click="markAsCompleted">标记为已完成</el-button>
          </span>
        </template>
      </el-dialog>
    </div>
  </div>
</template>

<script>
import StudentNavbar from '@/components/student/StudentNavbar.vue'
import { Search } from '@element-plus/icons-vue'

export default {
  name: 'StudentProgrammingConcepts',
  components: {
    StudentNavbar
  },
  setup() {
    return {
      Search
    }
  },
  data() {
    return {
      searchKeyword: '',
      difficultyFilter: '',
      activeChapters: [],
      completedSections: [],
      sectionDialogVisible: false,
      currentChapter: null,
      currentSection: null,
      exerciseAnswer: '',
      quizAnswers: [],
      loading: false,
      chapters: []
    }
  },
  computed: {
    filteredChapters() {
      return this.chapters.filter(chapter => {
        // 应用搜索过滤
        const matchesSearch = this.searchKeyword === '' ||
          chapter.title.toLowerCase().includes(this.searchKeyword.toLowerCase()) ||
          chapter.description.toLowerCase().includes(this.searchKeyword.toLowerCase()) ||
          chapter.sections.some(section => section.title.toLowerCase().includes(this.searchKeyword.toLowerCase()));

        // 应用难度过滤
        const matchesDifficulty = this.difficultyFilter === '' ||
          chapter.difficulty.toLowerCase() === this.difficultyFilter.toLowerCase();

        return matchesSearch && matchesDifficulty;
      });
    }
  },
  mounted() {
    console.log('StudentProgrammingConcepts组件已挂载');

    // 从本地存储加载已完成的章节
    const savedCompletedSections = localStorage.getItem('completedSections');
    if (savedCompletedSections) {
      this.completedSections = JSON.parse(savedCompletedSections);
      console.log(`从本地存储加载了 ${this.completedSections.length} 个已完成的小节`);
    }

    // 检查URL参数中是否有指定章节
    const chapterId = this.$route.query.chapter;
    if (chapterId) {
      console.log(`检测到URL参数中指定的章节ID: ${chapterId}`);
    }

    // 从后端加载章节数据
    this.loadChapters().then(() => {
      // 检查URL参数中是否有指定章节
      if (chapterId) {
        console.log(`章节数据加载完成，准备打开指定章节: ${chapterId}`);
        this.openChapterFromParam(chapterId);
      }
    });
  },
  methods: {
    // 从后端加载章节数据
    async loadChapters() {
      console.log('开始从后端加载章节数据...');
      this.loading = true;
      try {
        const response = await fetch('/api/teaching-content/chapters');
        const data = await response.json();
        console.log('收到章节数据响应:', data);

        if (data.success) {
          // 将后端数据转换为前端需要的格式
          this.chapters = data.chapters.map(chapter => ({
            id: chapter.chapter_id,
            number: chapter.chapter_number,
            title: chapter.chapter_title,
            difficulty: chapter.chapter_difficulty,
            description: chapter.chapter_description,
            sections: chapter.sections
          }));

          console.log(`成功加载 ${this.chapters.length} 个章节`);
          console.log('章节列表:', this.chapters.map(ch => ({
            id: ch.id,
            title: ch.title,
            sections: ch.sections ? ch.sections.length : 0
          })));
        } else {
          this.$message.error(data.message || '获取章节数据失败');
          console.error('获取章节数据失败:', data.message);
        }
      } catch (error) {
        console.error('获取章节数据失败:', error);
        this.$message.error('获取章节数据失败，请稍后重试');
      } finally {
        this.loading = false;
      }
    },

    getDifficultyType(difficulty) {
      switch (difficulty.toLowerCase()) {
        case '入门': return 'success';
        case '基础': return 'info';
        case '中级': return 'warning';
        case '高级': return 'danger';
        default: return 'info';
      }
    },
    getSectionIcon(type) {
      // 在 Element Plus 中，图标需要单独导入和注册
      // 这里我们暂时返回类名，后续可以替换为导入的图标组件
      switch (type) {
        case 'theory': return 'el-icon-reading';
        case 'exercise': return 'el-icon-edit-outline';
        case 'video': return 'el-icon-video-camera';
        case 'quiz': return 'el-icon-question';
        default: return 'el-icon-document';
      }
    },
    getSectionType(type) {
      switch (type) {
        case 'theory': return '理论';
        case 'exercise': return '练习';
        case 'video': return '视频';
        case 'quiz': return '测验';
        default: return '内容';
      }
    },
    isCompleted(sectionId) {
      return this.completedSections.includes(sectionId);
    },
    openSection(chapter, section) {
      this.currentChapter = chapter;
      this.currentSection = section;
      this.sectionDialogVisible = true;

      // 重置练习和测验状态
      this.exerciseAnswer = section.type === 'exercise' ? section.template || '' : '';
      this.quizAnswers = section.type === 'quiz' ? new Array(section.questions.length).fill(null) : [];
    },
    closeSectionDialog() {
      this.sectionDialogVisible = false;
      this.currentChapter = null;
      this.currentSection = null;
    },
    markAsCompleted() {
      if (this.currentSection && !this.isCompleted(this.currentSection.id)) {
        this.completedSections.push(this.currentSection.id);
        localStorage.setItem('completedSections', JSON.stringify(this.completedSections));
        this.$message.success('已标记为已完成！');
      }
      this.closeSectionDialog();
    },
    submitExercise() {
      // 这里可以添加代码验证逻辑
      this.$message.success('练习提交成功！');
      this.markAsCompleted();
    },
    resetExercise() {
      if (this.currentSection && this.currentSection.type === 'exercise') {
        this.exerciseAnswer = this.currentSection.template || '';
      }
    },
    submitQuiz() {
      if (this.currentSection && this.currentSection.type === 'quiz') {
        const questions = this.currentSection.questions;
        let correctCount = 0;

        for (let i = 0; i < questions.length; i++) {
          if (this.quizAnswers[i] === questions[i].correctAnswer) {
            correctCount++;
          }
        }

        const percentage = Math.round((correctCount / questions.length) * 100);

        if (percentage >= 70) {
          this.$message.success(`测验完成！你的得分: ${percentage}%`);
          this.markAsCompleted();
        } else {
          this.$message.warning(`测验完成，但得分不足。你的得分: ${percentage}%。需要至少70%才能通过。`);
        }
      }
    },
    resetQuiz() {
      if (this.currentSection && this.currentSection.type === 'quiz') {
        this.quizAnswers = new Array(this.currentSection.questions.length).fill(null);
      }
    },

    // 根据URL参数打开指定章节
    openChapterFromParam(chapterId) {
      console.log(`尝试打开URL参数中指定的章节: ${chapterId}`);

      // 查找对应章节
      const chapter = this.chapters.find(ch => ch.id === chapterId);
      if (chapter) {
        console.log(`找到匹配的章节:`, chapter);
        // 展开章节
        this.activeChapters = [chapter.id];
        console.log(`已设置活动章节为: ${chapter.id}`);

        // 滚动到章节位置
        this.$nextTick(() => {
          const chapterElement = document.querySelector(`[aria-controls="${chapter.id}"]`);
          if (chapterElement) {
            console.log(`找到章节DOM元素，正在滚动到视图中...`);
            chapterElement.scrollIntoView({ behavior: 'smooth', block: 'center' });

            // 显示提示信息
            this.$message.success(`已定位到推荐章节：${chapter.title}`);
          } else {
            console.warn(`未找到章节DOM元素: [aria-controls="${chapter.id}"]`);
          }
        });
      } else {
        console.warn(`未找到匹配的章节: ${chapterId}`);
        console.log('可用章节列表:', this.chapters.map(ch => ({ id: ch.id, title: ch.title })));
        this.$message.warning('未找到推荐的章节，请刷新页面重试');
      }
    }
  }
}
</script>

<style scoped>
.programming-concepts-container {
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

.chapter-navigation {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
}

.chapter-title {
  display: flex;
  align-items: center;
}

.chapter-number {
  font-weight: bold;
  margin-right: 10px;
  color: #409EFF;
}

.chapter-name {
  flex: 1;
}

.chapter-difficulty {
  margin-left: 10px;
}

.chapter-description {
  color: #606266;
  margin-bottom: 15px;
}

.sections-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 15px;
}

.section-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border-radius: 4px;
  background-color: #fff;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.3s;
}

.section-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px 0 rgba(0, 0, 0, 0.15);
}

.section-item.completed {
  border-left: 4px solid #67C23A;
}

.section-info {
  flex: 1;
}

.section-title {
  display: flex;
  align-items: center;
  font-weight: bold;
  margin-bottom: 5px;
}

.section-title i {
  margin-right: 8px;
  color: #409EFF;
}

.section-meta {
  display: flex;
  font-size: 12px;
  color: #909399;
}

.section-type {
  margin-right: 10px;
  padding: 2px 6px;
  background-color: #f0f2f5;
  border-radius: 2px;
}

.section-status {
  display: flex;
  align-items: center;
}

.section-status i {
  margin-left: 8px;
  color: #C0C4CC;
}

.section-content {
  padding: 10px;
}

.theory-content, .exercise-content, .video-content, .quiz-content {
  margin-bottom: 20px;
}

.code-examples {
  margin-top: 20px;
}

.code-example {
  margin-bottom: 15px;
  background-color: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
}

.code-example pre {
  background-color: #282c34;
  color: #abb2bf;
  padding: 15px;
  border-radius: 4px;
  overflow-x: auto;
}

.exercise-task {
  margin-top: 20px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.exercise-textarea {
  margin: 15px 0;
}

.exercise-actions, .quiz-actions {
  margin-top: 15px;
  display: flex;
  justify-content: flex-end;
}

.video-container {
  position: relative;
  padding-bottom: 56.25%; /* 16:9 比例 */
  height: 0;
  overflow: hidden;
  margin-bottom: 20px;
}

.video-container iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.quiz-question {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.quiz-option {
  display: block;
  margin: 10px 0;
}
</style>
