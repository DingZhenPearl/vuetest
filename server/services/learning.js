/**
 * 学习分析和推荐服务
 */
const { executePythonScript } = require('./python');
const { OpenAI } = require('openai');

// 创建OpenAI客户端
const openai = new OpenAI({
  apiKey: "ipzotlGevNqQsafvWSXi:cooExiNRkHtQtHkkIqNk",
  baseURL: 'https://spark-api-open.xf-yun.com/v1'
});

/**
 * 生成个性化学习推荐
 * @param {string} studentId - 学生ID
 * @returns {Promise<Array>} 学习推荐列表
 */
async function generateLearningRecommendations(studentId) {
  try {
    console.log(`开始为学生 ${studentId} 生成个性化学习推荐...`);

    // 1. 获取学生的学习数据
    console.log(`正在获取学生 ${studentId} 的学习数据...`);
    const studentData = await getStudentLearningData(studentId);

    if (!studentData || !studentData.success) {
      console.error('获取学生学习数据失败');
      return [];
    }
    console.log(`成功获取学生学习数据:`, studentData.data);

    // 2. 获取所有章节数据
    console.log(`正在获取所有章节数据...`);
    const chaptersData = await getChaptersData();
    console.log(`成功获取章节数据，共 ${chaptersData.length} 个章节`);

    // 3. 使用大模型分析学生数据并生成推荐
    console.log(`正在使用AI生成个性化推荐...`);
    const recommendations = await generateRecommendationsWithAI(studentData.data, studentId, chaptersData);
    console.log(`成功生成推荐，共 ${recommendations.length} 条推荐`);

    return recommendations;
  } catch (error) {
    console.error('生成学习推荐失败:', error);
    throw error;
  }
}

/**
 * 获取学生学习数据
 * @param {string} studentId - 学生ID
 * @returns {Promise<Object>} 学生学习数据
 */
async function getStudentLearningData(studentId) {
  try {
    // 调用Python脚本获取学生学习数据
    const result = await executePythonScript('learning_data.py', [
      'get_student_data',
      studentId
    ]);

    if (!result || !result.success) {
      console.warn('获取学生学习数据失败:', result);
      throw new Error(result?.message || '获取学生学习数据失败');
    }

    return result;
  } catch (error) {
    console.error('获取学生学习数据失败:', error);
    throw error;
  }
}

/**
 * 获取所有章节数据
 * @returns {Promise<Array>} 章节数据列表
 */
async function getChaptersData() {
  try {
    console.log('开始获取所有章节数据...');
    // 调用Python脚本获取所有章节数据
    const result = await executePythonScript('teaching_content.py', ['get_all_chapters']);

    if (!result || !result.success) {
      console.warn('获取章节数据失败:', result);
      return [];
    }

    const chapters = result.chapters || [];
    console.log(`成功获取章节数据，章节列表:`, chapters.map(ch => ({
      id: ch.chapter_id,
      title: ch.chapter_title,
      sections: ch.sections ? ch.sections.length : 0
    })));

    return chapters;
  } catch (error) {
    console.error('获取章节数据失败:', error);
    return [];
  }
}

/**
 * 使用AI生成个性化学习推荐
 * @param {Object} studentData - 学生学习数据
 * @param {string} studentId - 学生ID
 * @param {Array} chaptersData - 章节数据
 * @returns {Promise<Array>} 学习推荐列表
 */
async function generateRecommendationsWithAI(studentData, studentId, chaptersData) {
  try {
    console.log(`开始为学生 ${studentId} 使用AI生成个性化推荐...`);

    // 构建提示词
    console.log('正在构建AI提示词...');
    const prompt = buildPromptForRecommendations(studentData, studentId, chaptersData);
    console.log('提示词构建完成，长度:', prompt.length);

    // 调用大模型API
    console.log('正在调用AI接口...');
    const completion = await openai.chat.completions.create({
      model: 'lite', // 使用讯飞星火大模型
      messages: [
        {
          role: 'system',
          content: '你是一个专业的教育顾问和学习路径规划专家，擅长分析学生的学习行为和表现，并提供个性化的学习建议和资源推荐。你需要根据学生的学习情况，推荐适合的章节学习内容。'
        },
        {
          role: 'user',
          content: prompt
        }
      ],
      temperature: 0.7,
      max_tokens: 2000
    });

    // 解析AI响应
    console.log('收到AI响应，正在解析...');
    const aiResponse = completion.choices[0].message.content;
    console.log('AI原始响应:', aiResponse);

    const recommendations = parseAIResponseToRecommendations(aiResponse);
    console.log('解析后的推荐列表:', recommendations);

    // 检查是否包含章节推荐
    const chapterRecommendations = recommendations.filter(rec => rec.chapterId);
    console.log(`推荐中包含 ${chapterRecommendations.length} 条章节推荐:`,
      chapterRecommendations.map(rec => ({
        title: rec.title,
        chapterId: rec.chapterId
      }))
    );

    return recommendations;
  } catch (error) {
    console.error('AI生成推荐失败:', error);
    // 返回默认推荐
    console.log('使用默认推荐...');
    return getDefaultRecommendations();
  }
}

/**
 * 构建用于生成推荐的提示词
 * @param {Object} studentData - 学生学习数据
 * @param {string} studentId - 学生ID
 * @param {Array} chaptersData - 章节数据
 * @returns {string} 提示词
 */
function buildPromptForRecommendations(studentData, studentId, chaptersData) {
  // 提取章节基本信息，简化数据量
  const simplifiedChapters = chaptersData.map(chapter => ({
    id: chapter.chapter_id,
    number: chapter.chapter_number,
    title: chapter.chapter_title,
    difficulty: chapter.chapter_difficulty,
    description: chapter.chapter_description,
    sectionCount: chapter.sections ? chapter.sections.length : 0
  }));

  return `请基于以下学生的学习数据和可用的章节内容，生成3-5条个性化学习建议和资源推荐。
学生ID: ${studentId}

学习数据:
${JSON.stringify(studentData, null, 2)}

可用的学习章节:
${JSON.stringify(simplifiedChapters, null, 2)}

请分析学生的优势和不足，并提供具体的学习路径建议，重点推荐适合学生当前水平的章节内容。每条建议应包含：
1. 标题
2. 详细描述
3. 优先级（high/medium/low）
4. 相关资源推荐（如有）
5. 是否可立即执行的行动项（actionable）
6. 推荐的章节ID（chapterId，从上面的章节列表中选择）

请确保至少有2-3条推荐是针对具体章节的学习建议。

请以JSON格式返回，格式如下：
[
  {
    "title": "建议标题",
    "description": "详细描述",
    "priority": "优先级",
    "resources": [
      {
        "title": "资源标题",
        "url": "资源链接（如有）",
        "description": "资源描述"
      }
    ],
    "actionable": true/false,
    "problemId": "相关题目ID（如有）",
    "chapterId": "推荐章节ID（如有）"
  }
]`;
}

/**
 * 解析AI响应为推荐对象数组
 * @param {string} aiResponse - AI响应文本
 * @returns {Array} 推荐对象数组
 */
function parseAIResponseToRecommendations(aiResponse) {
  try {
    console.log('开始解析AI响应...');

    // 尝试从AI响应中提取JSON
    const jsonMatch = aiResponse.match(/\[\s*\{.*\}\s*\]/s);

    if (jsonMatch) {
      console.log('找到JSON格式的响应');
      const jsonStr = jsonMatch[0];
      console.log('提取的JSON字符串:', jsonStr.substring(0, 100) + '...');

      const parsed = JSON.parse(jsonStr);
      console.log(`成功解析JSON，包含 ${parsed.length} 条推荐`);

      // 检查是否包含章节推荐
      const chapterRecs = parsed.filter(rec => rec.chapterId);
      console.log(`解析出 ${chapterRecs.length} 条章节推荐`);

      return parsed;
    }

    // 如果没有找到JSON格式，尝试解析整个响应
    console.log('未找到JSON格式，尝试解析整个响应');
    const parsed = JSON.parse(aiResponse);
    console.log(`成功解析整个响应，包含 ${parsed.length} 条推荐`);
    return parsed;
  } catch (error) {
    console.error('解析AI响应失败:', error);
    console.log('原始AI响应:', aiResponse);
    console.log('使用默认推荐...');
    return getDefaultRecommendations();
  }
}

/**
 * 获取默认推荐（当AI生成失败时使用）
 * @returns {Array} 默认推荐列表
 */
function getDefaultRecommendations() {
  return [
    {
      title: "学习数据结构绪论",
      description: "建议先学习数据结构的基本概念和算法分析方法，这将为后续学习打下坚实基础。",
      priority: "high",
      resources: [
        {
          title: "绪论章节",
          url: "/student/programming-concepts",
          description: "数据结构基本概念与必要知识"
        }
      ],
      actionable: true,
      chapterId: "ch1"
    },
    {
      title: "掌握线性表基础知识",
      description: "线性表是最基础的数据结构，理解线性表的概念和实现对学习其他数据结构非常重要。",
      priority: "medium",
      resources: [
        {
          title: "线性表章节",
          url: "/student/programming-concepts",
          description: "学习顺序表与链表的基本概念和实现"
        }
      ],
      actionable: true,
      chapterId: "ch2"
    },
    {
      title: "完成更多编程练习",
      description: "通过持续练习提高编程技能，建议每天至少完成1-2道编程题。",
      priority: "high",
      resources: [
        {
          title: "编程习题集",
          url: "/student/exams",
          description: "平台提供的编程习题"
        }
      ],
      actionable: true
    },
    {
      title: "学习栈和队列",
      description: "栈和队列是线性表的扩展，是算法实现的重要工具，建议深入学习。",
      priority: "medium",
      resources: [
        {
          title: "线性表的扩展章节",
          url: "/student/programming-concepts",
          description: "学习栈、队列等线性表扩展结构"
        }
      ],
      actionable: true,
      chapterId: "ch3"
    }
  ];
}

module.exports = {
  generateLearningRecommendations,
  getStudentLearningData
};
