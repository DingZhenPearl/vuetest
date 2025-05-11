<template>
  <div class="programming-concepts-container">
    <StudentNavbar />
    <div class="main-content">
      <div class="page-header">
        <h1>编程概念学习</h1>
        <p class="subtitle">按章节学习C++编程基础知识和进阶概念</p>
      </div>

      <!-- 章节导航 -->
      <el-card class="chapter-navigation">
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
                <el-option label="入门" value="beginner" />
                <el-option label="基础" value="basic" />
                <el-option label="中级" value="intermediate" />
                <el-option label="高级" value="advanced" />
              </el-select>
            </div>
          </div>
        </template>

        <!-- 章节列表 -->
        <el-collapse v-model="activeChapters" accordion>
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
                allowfullscreen
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
      chapters: [
        {
          id: 'ch1',
          number: '第一章',
          title: 'C++基础入门',
          difficulty: '入门',
          description: '本章介绍C++编程的基础知识，包括变量、数据类型、输入输出等基本概念。',
          sections: [
            {
              id: 'ch1-s1',
              title: 'C++简介与环境搭建',
              type: 'theory',
              duration: 15,
              content: '<p>C++是一种通用的编程语言，支持多种编程范式，包括过程式、面向对象和泛型编程。</p><p>本节将介绍C++的基本特性以及如何搭建开发环境。</p>',
              examples: [
                {
                  title: '第一个C++程序',
                  code: '#include <iostream>\n\nint main() {\n    std::cout << "Hello, World!" << std::endl;\n    return 0;\n}',
                  explanation: '这是一个简单的C++程序，它输出"Hello, World!"到控制台。'
                }
              ]
            },
            {
              id: 'ch1-s2',
              title: '变量与数据类型',
              type: 'theory',
              duration: 20,
              content: '<p>C++中的变量是用于存储数据的命名存储位置。每个变量都有一个特定的数据类型，它决定了变量可以存储的数据类型和大小。</p>',
              examples: [
                {
                  title: '基本数据类型示例',
                  code: '#include <iostream>\n\nint main() {\n    int age = 25;                 // 整数\n    double salary = 5000.50;      // 浮点数\n    char grade = \'A\';            // 字符\n    bool isEmployed = true;      // 布尔值\n    \n    std::cout << "Age: " << age << std::endl;\n    std::cout << "Salary: " << salary << std::endl;\n    std::cout << "Grade: " << grade << std::endl;\n    std::cout << "Employed: " << isEmployed << std::endl;\n    \n    return 0;\n}',
                  explanation: '这个例子展示了C++中的基本数据类型：整数(int)、浮点数(double)、字符(char)和布尔值(bool)。'
                }
              ]
            },
            {
              id: 'ch1-s3',
              title: '基本输入输出',
              type: 'exercise',
              duration: 25,
              content: '<p>C++使用iostream库进行基本的输入和输出操作。std::cout用于输出，std::cin用于输入。</p>',
              task: '编写一个程序，提示用户输入他们的姓名和年龄，然后输出一条包含这些信息的消息。',
              template: '#include <iostream>\n#include <string>\n\nint main() {\n    // 在这里编写你的代码\n    \n    return 0;\n}'
            },
            {
              id: 'ch1-s4',
              title: 'C++基础知识测验',
              type: 'quiz',
              duration: 10,
              content: '<p>完成以下测验来测试你对C++基础知识的理解。</p>',
              questions: [
                {
                  text: '哪个头文件用于基本的输入输出操作？',
                  options: ['<stdio.h>', '<iostream>', '<iomanip>', '<fstream>'],
                  correctAnswer: 1
                },
                {
                  text: '以下哪个不是C++的基本数据类型？',
                  options: ['int', 'double', 'string', 'char'],
                  correctAnswer: 2
                },
                {
                  text: '在C++中，如何声明一个常量？',
                  options: ['constant int x = 5;', 'const int x = 5;', 'int const x = 5;', 'B和C都正确'],
                  correctAnswer: 3
                }
              ]
            }
          ]
        },
        {
          id: 'ch2',
          number: '第二章',
          title: '控制流与循环',
          difficulty: '基础',
          description: '本章介绍C++中的条件语句、循环结构和控制流程，帮助你编写能够做出决策和重复执行任务的程序。',
          sections: [
            {
              id: 'ch2-s1',
              title: '条件语句 (if-else)',
              type: 'theory',
              duration: 20,
              content: '<p>条件语句允许程序根据特定条件执行不同的代码块。C++中最基本的条件语句是if-else语句。</p>',
              examples: [
                {
                  title: 'if-else示例',
                  code: '#include <iostream>\n\nint main() {\n    int age;\n    \n    std::cout << "请输入你的年龄: ";\n    std::cin >> age;\n    \n    if (age >= 18) {\n        std::cout << "你是成年人。" << std::endl;\n    } else {\n        std::cout << "你是未成年人。" << std::endl;\n    }\n    \n    return 0;\n}',
                  explanation: '这个程序根据用户输入的年龄判断他们是成年人还是未成年人。'
                }
              ]
            },
            {
              id: 'ch2-s2',
              title: '循环结构 (for, while)',
              type: 'video',
              duration: 15,
              videoUrl: 'https://www.example.com/embed/cpp-loops',
              content: '<p>循环允许程序重复执行代码块。C++提供了几种循环结构，包括for循环和while循环。</p>'
            }
          ]
        },
        {
          id: 'ch3',
          number: '第三章',
          title: '函数与模块化编程',
          difficulty: '中级',
          description: '本章介绍如何使用函数进行模块化编程，提高代码的可重用性和可维护性。',
          sections: [
            {
              id: 'ch3-s1',
              title: '函数基础',
              type: 'theory',
              duration: 25,
              content: '<p>函数是执行特定任务的代码块。它们帮助组织代码，提高可重用性，并使程序更易于理解和维护。</p>',
              examples: [
                {
                  title: '函数定义与调用',
                  code: '#include <iostream>\n\n// 函数声明\nint add(int a, int b);\n\nint main() {\n    int result = add(5, 3);\n    std::cout << "5 + 3 = " << result << std::endl;\n    return 0;\n}\n\n// 函数定义\nint add(int a, int b) {\n    return a + b;\n}',
                  explanation: '这个例子展示了如何定义和调用一个简单的函数，该函数接受两个整数参数并返回它们的和。'
                }
              ]
            }
          ]
        }
      ]
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
    // 从本地存储加载已完成的章节
    const savedCompletedSections = localStorage.getItem('completedSections');
    if (savedCompletedSections) {
      this.completedSections = JSON.parse(savedCompletedSections);
    }
  },
  methods: {
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
