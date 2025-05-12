<template>
  <div class="teaching-contents-container">
    <TeacherNavbar />

    <div class="teaching-contents">
      <h1>教学内容管理</h1>

      <!-- 章节表单 -->
      <div class="chapter-form-container">
        <h2>{{ isEditing ? '编辑章节' : '添加新章节' }}</h2>

        <el-form :model="chapterForm" :rules="rules" ref="chapterForm" label-width="100px">
          <el-form-item label="章节ID" prop="chapter_id" :disabled="isEditing">
            <el-input v-model="chapterForm.chapter_id" placeholder="例如：ch1" :disabled="isEditing"></el-input>
          </el-form-item>

          <el-form-item label="章节编号" prop="chapter_number">
            <el-input v-model="chapterForm.chapter_number" placeholder="例如：第一章"></el-input>
          </el-form-item>

          <el-form-item label="章节标题" prop="chapter_title">
            <el-input v-model="chapterForm.chapter_title" placeholder="例如：绪论"></el-input>
          </el-form-item>

          <el-form-item label="难度" prop="chapter_difficulty">
            <el-select v-model="chapterForm.chapter_difficulty" placeholder="选择难度">
              <el-option label="入门" value="入门"></el-option>
              <el-option label="基础" value="基础"></el-option>
              <el-option label="中级" value="中级"></el-option>
              <el-option label="高级" value="高级"></el-option>
            </el-select>
          </el-form-item>

          <el-form-item label="章节描述" prop="chapter_description">
            <el-input type="textarea" v-model="chapterForm.chapter_description" :rows="3" placeholder="章节内容简介"></el-input>
          </el-form-item>

          <!-- 小节管理 -->
          <div class="sections-container">
            <h3>小节管理</h3>

            <div v-for="(section, index) in chapterForm.sections" :key="index" class="section-item">
              <el-divider>小节 {{ index + 1 }}</el-divider>

              <!-- 小节概览（非编辑状态） -->
              <div v-if="!section.isEditing" class="section-overview">
                <div class="section-header">
                  <div class="section-info">
                    <h4>{{ section.title || '未命名小节' }}</h4>
                    <div class="section-meta">
                      <el-tag size="small" :type="getSectionTypeColor(section.type)">{{ getSectionTypeName(section.type) }}</el-tag>
                      <span class="section-duration">{{ section.duration }}分钟</span>
                      <span class="section-id">ID: {{ section.id }}</span>
                    </div>
                  </div>
                  <div class="section-actions">
                    <el-button size="small" type="primary" @click="editSection(index)">编辑</el-button>
                    <el-button size="small" type="danger" @click="removeSection(index)">删除</el-button>
                  </div>
                </div>

                <!-- 小节内容预览 -->
                <div class="section-preview">
                  <div class="preview-item">
                    <strong>内容预览：</strong>
                    <div class="content-preview" v-html="getContentPreview(section.content)"></div>
                  </div>

                  <!-- 视频预览 -->
                  <div v-if="section.type === 'video'" class="preview-item">
                    <strong>视频URL：</strong>
                    <div class="video-preview">{{ section.videoUrl }}</div>
                  </div>

                  <!-- 理论小节示例数量 -->
                  <div v-if="section.type === 'theory' && section.examples && section.examples.length > 0" class="preview-item">
                    <strong>代码示例：</strong>
                    <div>包含 {{ section.examples.length }} 个代码示例</div>
                  </div>

                  <!-- 练习小节任务预览 -->
                  <div v-if="section.type === 'exercise' && section.task" class="preview-item">
                    <strong>任务描述：</strong>
                    <div class="content-preview">{{ getTextPreview(section.task) }}</div>
                  </div>

                  <!-- 测验小节题目数量 -->
                  <div v-if="section.type === 'quiz' && section.questions && section.questions.length > 0" class="preview-item">
                    <strong>测验题目：</strong>
                    <div>包含 {{ section.questions.length }} 道题目</div>
                  </div>
                </div>
              </div>

              <!-- 小节编辑表单（编辑状态） -->
              <div v-else class="section-edit-form">
                <el-form-item :label="'小节ID'" :prop="'sections.' + index + '.id'" :rules="{ required: true, message: '请输入小节ID', trigger: 'blur' }">
                  <el-input v-model="section.id" placeholder="例如：ch1-s1"></el-input>
                </el-form-item>

                <el-form-item :label="'小节标题'" :prop="'sections.' + index + '.title'" :rules="{ required: true, message: '请输入小节标题', trigger: 'blur' }">
                  <el-input v-model="section.title" placeholder="小节标题"></el-input>
                </el-form-item>

                <el-form-item :label="'类型'" :prop="'sections.' + index + '.type'" :rules="{ required: true, message: '请选择小节类型', trigger: 'change' }">
                  <el-select v-model="section.type" placeholder="选择类型">
                    <el-option label="理论" value="theory"></el-option>
                    <el-option label="练习" value="exercise"></el-option>
                    <el-option label="视频" value="video"></el-option>
                    <el-option label="测验" value="quiz"></el-option>
                  </el-select>
                </el-form-item>

                <el-form-item :label="'时长(分钟)'" :prop="'sections.' + index + '.duration'" :rules="{ required: true, message: '请输入时长', trigger: 'blur' }">
                  <el-input-number v-model="section.duration" :min="1" :max="120"></el-input-number>
                </el-form-item>

                <el-form-item :label="'内容'" :prop="'sections.' + index + '.content'" :rules="{ required: true, message: '请输入内容', trigger: 'blur' }">
                  <el-input type="textarea" v-model="section.content" :rows="3" placeholder="支持HTML格式"></el-input>
                </el-form-item>

                <!-- 根据类型显示不同的表单项 -->
                <template v-if="section.type === 'theory'">
                  <el-form-item label="代码示例">
                    <el-button size="small" type="primary" @click="addExample(index)">添加示例</el-button>

                    <div v-for="(example, exIndex) in section.examples" :key="exIndex" class="example-item">
                      <el-divider>示例 {{ exIndex + 1 }}</el-divider>

                      <el-form-item label="标题">
                        <el-input v-model="example.title" placeholder="示例标题"></el-input>
                      </el-form-item>

                      <el-form-item label="代码">
                        <el-input type="textarea" v-model="example.code" :rows="5" placeholder="代码内容"></el-input>
                      </el-form-item>

                      <el-form-item label="说明">
                        <el-input type="textarea" v-model="example.explanation" :rows="2" placeholder="代码说明"></el-input>
                      </el-form-item>

                      <el-button size="small" type="danger" @click="removeExample(index, exIndex)">删除示例</el-button>
                    </div>
                  </el-form-item>
                </template>

                <template v-if="section.type === 'exercise'">
                  <el-form-item label="任务描述">
                    <el-input type="textarea" v-model="section.task" :rows="3" placeholder="练习任务描述"></el-input>
                  </el-form-item>

                  <el-form-item label="代码模板">
                    <el-input type="textarea" v-model="section.template" :rows="5" placeholder="初始代码模板"></el-input>
                  </el-form-item>
                </template>

                <template v-if="section.type === 'video'">
                  <el-form-item label="视频URL">
                    <el-input
                      v-model="section.originalVideoUrl"
                      placeholder="输入原始视频链接，将自动转换为嵌入式外链"
                      @input="handleVideoUrlChange(index)"
                      @blur="handleVideoUrlBlur(index)">
                      <template #append>
                        <el-button @click="convertVideoUrl(index)">转换</el-button>
                      </template>
                    </el-input>
                    <div class="video-url-tips">
                      <small>支持B站、腾讯视频、优酷、爱奇艺、YouTube等平台的视频链接</small>
                    </div>
                  </el-form-item>

                  <el-form-item label="嵌入URL" v-if="section.videoUrl">
                    <el-input v-model="section.videoUrl" disabled></el-input>
                    <div class="video-url-converted" v-if="section.videoUrlConverted">
                      <el-tag size="small" type="success">已自动转换为嵌入式外链</el-tag>
                    </div>
                  </el-form-item>

                  <!-- 视频预览 -->
                  <el-form-item label="视频预览" v-if="section.videoUrl">
                    <div class="video-preview-container">
                      <iframe
                        :src="section.videoUrl"
                        frameborder="0"
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                        allowfullscreen="allowfullscreen"
                        sandbox="allow-top-navigation allow-same-origin allow-forms allow-scripts"
                        scrolling="no"
                      ></iframe>
                    </div>
                  </el-form-item>
                </template>

                <template v-if="section.type === 'quiz'">
                  <el-form-item label="测验题目">
                    <el-button size="small" type="primary" @click="addQuestion(index)">添加题目</el-button>

                    <div v-for="(question, qIndex) in section.questions" :key="qIndex" class="question-item">
                      <el-divider>题目 {{ qIndex + 1 }}</el-divider>

                      <el-form-item label="题目内容">
                        <el-input v-model="question.text" placeholder="题目内容"></el-input>
                      </el-form-item>

                      <el-form-item label="选项">
                        <div v-for="(option, oIndex) in question.options" :key="oIndex" class="option-item">
                          <el-input v-model="question.options[oIndex]" placeholder="选项内容">
                            <template #prepend>选项 {{ oIndex + 1 }}</template>
                          </el-input>
                        </div>

                        <div class="option-buttons">
                          <el-button size="small" type="primary" @click="addOption(index, qIndex)">添加选项</el-button>
                          <el-button size="small" type="danger" @click="removeOption(index, qIndex)" :disabled="question.options.length <= 2">删除选项</el-button>
                        </div>
                      </el-form-item>

                      <el-form-item label="正确答案">
                        <el-select v-model="question.correctAnswer" placeholder="选择正确答案">
                          <el-option v-for="(_, oIndex) in question.options" :key="oIndex" :label="`选项 ${oIndex + 1}`" :value="oIndex"></el-option>
                        </el-select>
                      </el-form-item>

                      <el-button size="small" type="danger" @click="removeQuestion(index, qIndex)">删除题目</el-button>
                    </div>
                  </el-form-item>
                </template>

                <div class="section-edit-actions">
                  <el-button size="small" type="primary" @click="saveSection(index)">保存小节</el-button>
                  <el-button size="small" @click="cancelEditSection(index)">取消</el-button>
                </div>
              </div>
            </div>

            <el-button type="primary" @click="addSection">添加小节</el-button>
          </div>

          <div class="form-actions">
            <el-button type="primary" @click="submitChapter">{{ isEditing ? '更新章节' : '添加章节' }}</el-button>
            <el-button @click="resetForm">重置</el-button>
            <el-button v-if="isEditing" @click="cancelEdit">取消编辑</el-button>
          </div>
        </el-form>
      </div>

      <!-- 章节列表 -->
      <div class="chapters-list-container">
        <h2>章节列表</h2>

        <!-- 过滤和搜索 -->
        <div class="filter-container">
          <el-input
            placeholder="搜索章节"
            v-model="searchQuery"
            clearable
            prefix-icon="el-icon-search"
            style="width: 300px; margin-right: 10px;"
          ></el-input>

          <el-select v-model="difficultyFilter" placeholder="难度筛选" clearable>
            <el-option label="全部" value=""></el-option>
            <el-option label="入门" value="入门"></el-option>
            <el-option label="基础" value="基础"></el-option>
            <el-option label="中级" value="中级"></el-option>
            <el-option label="高级" value="高级"></el-option>
          </el-select>
        </div>

        <!-- 章节表格 -->
        <el-table
          :data="filteredChapters"
          style="width: 100%"
          border
          v-loading="loading"
        >
          <el-table-column prop="chapter_number" label="章节编号" width="120"></el-table-column>
          <el-table-column prop="chapter_title" label="标题"></el-table-column>
          <el-table-column prop="chapter_difficulty" label="难度" width="100">
            <template #default="scope">
              <el-tag :type="getDifficultyType(scope.row.chapter_difficulty)">
                {{ scope.row.chapter_difficulty }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="小节数量" width="100">
            <template #default="scope">
              {{ scope.row.sections.length }}
            </template>
          </el-table-column>
          <el-table-column label="创建时间" width="180">
            <template #default="scope">
              {{ formatDate(scope.row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200">
            <template #default="scope">
              <div class="table-actions">
                <el-button size="mini" @click="editChapter(scope.row)" type="primary">编辑</el-button>
                <el-button size="mini" @click="deleteChapter(scope.row.chapter_id)" type="danger">删除</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script>
import TeacherNavbar from '../../components/teacher/TeacherNavbar.vue';
import { convertVideoUrl } from '../../utils/videoUrlConverter';

export default {
  name: 'TeacherTeachingContents',
  components: {
    TeacherNavbar
  },
  data() {
    return {
      loading: false,
      chapters: [],
      searchQuery: '',
      difficultyFilter: '',
      isEditing: false,
      chapterForm: {
        teacher_email: '',
        chapter_id: '',
        chapter_number: '',
        chapter_title: '',
        chapter_difficulty: '',
        chapter_description: '',
        sections: []
      },
      rules: {
        chapter_id: [
          { required: true, message: '请输入章节ID', trigger: 'blur' },
          { pattern: /^[a-zA-Z0-9-_]+$/, message: '章节ID只能包含字母、数字、下划线和连字符', trigger: 'blur' }
        ],
        chapter_number: [
          { required: true, message: '请输入章节编号', trigger: 'blur' }
        ],
        chapter_title: [
          { required: true, message: '请输入章节标题', trigger: 'blur' }
        ],
        chapter_difficulty: [
          { required: true, message: '请选择难度', trigger: 'change' }
        ],
        chapter_description: [
          { required: true, message: '请输入章节描述', trigger: 'blur' }
        ]
      }
    };
  },
  computed: {
    filteredChapters() {
      return this.chapters.filter(chapter => {
        // 应用搜索过滤
        const matchesSearch = this.searchQuery === '' ||
          chapter.chapter_title.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
          chapter.chapter_description.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
          chapter.chapter_number.toLowerCase().includes(this.searchQuery.toLowerCase());

        // 应用难度过滤
        const matchesDifficulty = this.difficultyFilter === '' ||
          chapter.chapter_difficulty === this.difficultyFilter;

        return matchesSearch && matchesDifficulty;
      });
    }
  },
  created() {
    // 获取当前登录教师的邮箱
    this.chapterForm.teacher_email = sessionStorage.getItem('userEmail') || '';

    // 加载章节列表
    this.loadChapters();
  },
  methods: {
    // 加载章节列表
    async loadChapters() {
      this.loading = true;
      try {
        const response = await fetch('/api/teaching-content/chapters');
        const data = await response.json();

        if (data.success) {
          this.chapters = data.chapters || [];
        } else {
          this.$message.error(data.message || '获取章节列表失败');
        }
      } catch (error) {
        console.error('获取章节列表失败:', error);
        this.$message.error('获取章节列表失败');
      } finally {
        this.loading = false;
      }
    },

    // 添加章节
    async submitChapter() {
      this.$refs.chapterForm.validate(async valid => {
        if (!valid) {
          return false;
        }

        this.loading = true;

        try {
          let url, method;

          if (this.isEditing) {
            url = `/api/teaching-content/chapters/${this.chapterForm.chapter_id}`;
            method = 'PUT';
          } else {
            url = '/api/teaching-content/chapters';
            method = 'POST';
          }

          const response = await fetch(url, {
            method,
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(this.chapterForm)
          });

          const data = await response.json();

          if (data.success) {
            this.$message.success(this.isEditing ? '章节更新成功' : '章节添加成功');
            this.resetForm();
            this.loadChapters();
          } else {
            this.$message.error(data.message || (this.isEditing ? '更新章节失败' : '添加章节失败'));
          }
        } catch (error) {
          console.error(this.isEditing ? '更新章节失败:' : '添加章节失败:', error);
          this.$message.error(this.isEditing ? '更新章节失败' : '添加章节失败');
        } finally {
          this.loading = false;
        }
      });
    },

    // 编辑章节
    editChapter(chapter) {
      this.isEditing = true;

      // 深拷贝章节数据
      this.chapterForm = JSON.parse(JSON.stringify({
        teacher_email: chapter.teacher_email,
        chapter_id: chapter.chapter_id,
        chapter_number: chapter.chapter_number,
        chapter_title: chapter.chapter_title,
        chapter_difficulty: chapter.chapter_difficulty,
        chapter_description: chapter.chapter_description,
        sections: chapter.sections
      }));

      // 确保每个小节都有必要的字段，并设置为非编辑状态
      this.chapterForm.sections.forEach(section => {
        // 设置为非编辑状态
        section.isEditing = false;

        // 确保必要字段存在
        if (section.type === 'theory' && !section.examples) {
          section.examples = [];
        } else if (section.type === 'exercise' && !section.task) {
          section.task = '';
        } else if (section.type === 'exercise' && !section.template) {
          section.template = '';
        } else if (section.type === 'video') {
          // 对于视频小节，确保有originalVideoUrl字段
          if (!section.originalVideoUrl && section.videoUrl) {
            // 如果没有原始URL但有嵌入URL，将嵌入URL作为原始URL
            section.originalVideoUrl = section.videoUrl;
          } else if (!section.originalVideoUrl) {
            section.originalVideoUrl = '';
          }

          // 确保有videoUrl字段
          if (!section.videoUrl) {
            section.videoUrl = '';
          }

          // 确保有videoUrlConverted字段
          if (section.videoUrlConverted === undefined) {
            section.videoUrlConverted = false;
          }
        } else if (section.type === 'quiz' && !section.questions) {
          section.questions = [];
        }
      });

      // 滚动到表单顶部
      window.scrollTo(0, 0);
    },

    // 删除章节
    async deleteChapter(chapterId) {
      this.$confirm('确定要删除这个章节吗？此操作不可恢复。', '警告', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        this.loading = true;

        try {
          const response = await fetch(`/api/teaching-content/chapters/${chapterId}`, {
            method: 'DELETE'
          });

          const data = await response.json();

          if (data.success) {
            this.$message.success('章节删除成功');
            this.loadChapters();
          } else {
            this.$message.error(data.message || '删除章节失败');
          }
        } catch (error) {
          console.error('删除章节失败:', error);
          this.$message.error('删除章节失败');
        } finally {
          this.loading = false;
        }
      }).catch(() => {
        // 取消删除
      });
    },

    // 重置表单
    resetForm() {
      this.$refs.chapterForm.resetFields();
      this.chapterForm.sections = [];
      this.isEditing = false;
    },

    // 取消编辑
    cancelEdit() {
      this.resetForm();
    },

    // 添加小节
    addSection() {
      this.chapterForm.sections.push({
        id: `${this.chapterForm.chapter_id}-s${this.chapterForm.sections.length + 1}`,
        title: '',
        type: 'theory',
        duration: 15,
        content: '',
        examples: [],
        originalVideoUrl: '', // 添加原始视频URL字段
        videoUrl: '', // 添加嵌入式视频URL字段
        videoUrlConverted: false, // 添加视频URL转换状态字段
        isEditing: true // 新添加的小节默认处于编辑状态
      });
    },

    // 删除小节
    removeSection(index) {
      this.$confirm('确定要删除这个小节吗？此操作不可恢复。', '警告', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.chapterForm.sections.splice(index, 1);
        this.$message.success('小节删除成功');
      }).catch(() => {
        // 取消删除
      });
    },

    // 编辑小节
    editSection(index) {
      // 创建小节的备份，以便取消编辑时恢复
      this.chapterForm.sections[index]._backup = JSON.parse(JSON.stringify(this.chapterForm.sections[index]));
      this.chapterForm.sections[index].isEditing = true;
    },

    // 保存小节
    saveSection(index) {
      // 验证小节表单
      this.$refs.chapterForm.validateField(`sections.${index}.id`);
      this.$refs.chapterForm.validateField(`sections.${index}.title`);
      this.$refs.chapterForm.validateField(`sections.${index}.type`);
      this.$refs.chapterForm.validateField(`sections.${index}.duration`);
      this.$refs.chapterForm.validateField(`sections.${index}.content`);

      // 删除备份
      delete this.chapterForm.sections[index]._backup;
      // 退出编辑模式
      this.chapterForm.sections[index].isEditing = false;

      this.$message.success('小节保存成功');
    },

    // 取消编辑小节
    cancelEditSection(index) {
      if (this.chapterForm.sections[index]._backup) {
        // 恢复备份数据
        const backup = this.chapterForm.sections[index]._backup;
        const isEditing = false; // 设置为非编辑状态

        // 恢复所有属性，但保留isEditing状态
        Object.keys(backup).forEach(key => {
          if (key !== '_backup') {
            this.chapterForm.sections[index][key] = backup[key];
          }
        });

        // 设置为非编辑状态
        this.chapterForm.sections[index].isEditing = isEditing;

        // 删除备份
        delete this.chapterForm.sections[index]._backup;
      } else {
        // 如果是新添加的小节，没有备份，则直接退出编辑模式
        this.chapterForm.sections[index].isEditing = false;
      }
    },

    // 获取小节类型名称
    getSectionTypeName(type) {
      switch (type) {
        case 'theory': return '理论';
        case 'exercise': return '练习';
        case 'video': return '视频';
        case 'quiz': return '测验';
        default: return '未知';
      }
    },

    // 获取小节类型颜色
    getSectionTypeColor(type) {
      switch (type) {
        case 'theory': return 'info';
        case 'exercise': return 'warning';
        case 'video': return 'success';
        case 'quiz': return 'danger';
        default: return 'info';
      }
    },

    // 获取内容预览
    getContentPreview(content) {
      if (!content) return '无内容';

      // 移除HTML标签，只保留文本
      const textContent = content.replace(/<[^>]*>/g, '');

      // 截取前100个字符
      return textContent.length > 100 ? textContent.substring(0, 100) + '...' : textContent;
    },

    // 获取文本预览
    getTextPreview(text) {
      if (!text) return '无内容';

      // 截取前100个字符
      return text.length > 100 ? text.substring(0, 100) + '...' : text;
    },

    // 添加代码示例
    addExample(sectionIndex) {
      if (!this.chapterForm.sections[sectionIndex].examples) {
        this.chapterForm.sections[sectionIndex].examples = [];
      }

      this.chapterForm.sections[sectionIndex].examples.push({
        title: '',
        code: '',
        explanation: ''
      });
    },

    // 删除代码示例
    removeExample(sectionIndex, exampleIndex) {
      this.chapterForm.sections[sectionIndex].examples.splice(exampleIndex, 1);
    },

    // 添加测验题目
    addQuestion(sectionIndex) {
      if (!this.chapterForm.sections[sectionIndex].questions) {
        this.chapterForm.sections[sectionIndex].questions = [];
      }

      this.chapterForm.sections[sectionIndex].questions.push({
        text: '',
        options: ['', ''],
        correctAnswer: 0
      });
    },

    // 删除测验题目
    removeQuestion(sectionIndex, questionIndex) {
      this.chapterForm.sections[sectionIndex].questions.splice(questionIndex, 1);
    },

    // 处理视频URL变化
    handleVideoUrlChange(sectionIndex) {
      // 当用户输入URL时，暂时不进行转换，等待用户完成输入
      const section = this.chapterForm.sections[sectionIndex];

      // 如果URL为空，清空嵌入URL
      if (!section.originalVideoUrl) {
        section.videoUrl = '';
        section.videoUrlConverted = false;
      }
    },

    // 处理视频URL失去焦点
    handleVideoUrlBlur(sectionIndex) {
      // 当输入框失去焦点时，自动转换URL
      this.convertVideoUrl(sectionIndex);
    },

    // 转换视频URL
    convertVideoUrl(sectionIndex) {
      const section = this.chapterForm.sections[sectionIndex];

      // 如果原始URL为空，不进行转换
      if (!section.originalVideoUrl) {
        section.videoUrl = '';
        section.videoUrlConverted = false;
        return;
      }

      // 使用转换工具转换URL
      const result = convertVideoUrl(section.originalVideoUrl);

      // 如果转换成功，更新嵌入URL
      if (result.isConverted) {
        section.videoUrl = result.embedUrl;
        section.videoUrlConverted = true;
        this.$message.success(`已自动转换为${result.type}嵌入式外链`);
      } else if (result.embedUrl) {
        // 如果URL已经是嵌入式链接，直接使用
        section.videoUrl = result.embedUrl;
        section.videoUrlConverted = false;
      } else {
        // 如果转换失败，使用原始URL
        section.videoUrl = section.originalVideoUrl;
        section.videoUrlConverted = false;
        this.$message.warning('无法识别的视频链接格式，将使用原始链接');
      }
    },

    // 添加选项
    addOption(sectionIndex, questionIndex) {
      this.chapterForm.sections[sectionIndex].questions[questionIndex].options.push('');
    },

    // 删除选项
    removeOption(sectionIndex, questionIndex) {
      const options = this.chapterForm.sections[sectionIndex].questions[questionIndex].options;
      if (options.length > 2) {
        options.pop();
      }
    },

    // 格式化日期
    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleString();
    },

    // 获取难度标签类型
    getDifficultyType(difficulty) {
      switch (difficulty) {
        case '入门': return 'success';
        case '基础': return 'info';
        case '中级': return 'warning';
        case '高级': return 'danger';
        default: return 'info';
      }
    }
  }
};
</script>

<style scoped>
.teaching-contents-container {
  display: flex;
}

.teaching-contents {
  padding: 20px;
  background-color: #f4f4f4;
  min-height: 100vh;
  margin-left: 250px; /* 与侧边栏宽度相同 */
  width: calc(100% - 250px);
  box-sizing: border-box;
}

@media (max-width: 768px) {
  .teaching-contents {
    margin-left: 64px;
    width: calc(100% - 64px);
  }
}

h1 {
  margin-bottom: 20px;
  color: #303133;
}

h2 {
  margin-bottom: 15px;
  color: #303133;
}

.chapter-form-container {
  background-color: #fff;
  padding: 20px;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.sections-container {
  margin-top: 20px;
  border-top: 1px solid #ebeef5;
  padding-top: 20px;
}

.section-item {
  background-color: #f9f9f9;
  padding: 15px;
  border-radius: 4px;
  margin-bottom: 15px;
}

.section-actions {
  display: flex;
  justify-content: flex-end;
  gap: 5px;
}

.section-edit-actions {
  display: flex;
  justify-content: flex-end;
  gap: 5px;
  margin-top: 15px;
}

.section-overview {
  padding: 10px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.section-info h4 {
  margin: 0 0 5px 0;
  font-size: 16px;
}

.section-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12px;
  color: #606266;
}

.section-duration, .section-id {
  display: inline-flex;
  align-items: center;
}

.section-preview {
  margin-top: 10px;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.preview-item {
  margin-bottom: 8px;
}

.preview-item:last-child {
  margin-bottom: 0;
}

.content-preview {
  max-height: 60px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  font-size: 13px;
  color: #606266;
}

.video-preview {
  font-size: 13px;
  color: #409EFF;
  word-break: break-all;
}

.video-url-tips {
  margin-top: 5px;
  color: #909399;
}

.video-url-converted {
  margin-top: 5px;
}

.video-preview-container {
  width: 100%;
  height: 0;
  padding-bottom: 56.25%; /* 16:9 宽高比 */
  position: relative;
  overflow: hidden;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.video-preview-container iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border: none;
}

.example-item, .question-item {
  background-color: #fff;
  padding: 15px;
  border-radius: 4px;
  margin-bottom: 10px;
  border: 1px solid #ebeef5;
}

.option-item {
  margin-bottom: 10px;
}

.option-buttons {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.form-actions {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.chapters-list-container {
  background-color: #fff;
  padding: 20px;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.filter-container {
  display: flex;
  margin-bottom: 20px;
}

.table-actions {
  display: flex;
  gap: 5px;
}
</style>
