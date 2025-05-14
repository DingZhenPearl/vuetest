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
          content: '你是一个专业的编程教育顾问和学习路径规划专家，擅长按照课程章节组织学习建议。你的核心任务是分析学生在各个章节相关知识点上的表现，并提供按章节组织的学习路径。你必须按照数据结构课程的章节顺序提供系统化的学习建议，而不是按照难度分类。你的推荐应该考虑章节间的逻辑依赖关系，确保学习路径的连贯性和有效性。每条推荐都必须明确指出推荐的章节名称，并解释为什么这个章节适合学生当前的学习需求。'
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
    // 返回基于学生数据的默认推荐
    console.log('使用基于学生数据的默认推荐...');
    return getDefaultRecommendations(studentData);
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
  // 提取章节基本信息，包括章节内容和小节
  const detailedChapters = chaptersData.map(chapter => {
    // 提取章节的基本信息
    const chapterInfo = {
      id: chapter.chapter_id,
      number: chapter.chapter_number,
      title: chapter.chapter_title,
      difficulty: chapter.chapter_difficulty,
      description: chapter.chapter_description
    };

    // 提取章节的小节信息
    if (chapter.sections && Array.isArray(chapter.sections)) {
      chapterInfo.sections = chapter.sections.map(section => ({
        id: section.id,
        title: section.title,
        type: section.type,
        duration: section.duration
      }));
    } else {
      chapterInfo.sections = [];
    }

    return chapterInfo;
  });

  // 提取学生的编程表现关键指标
  let performanceHighlights = '';
  let chapterPerformance = '';

  if (studentData && studentData.learning_data) {
    const learningStats = studentData.learning_data.learning_stats || {};
    const difficultyStats = studentData.learning_data.difficulty_stats || [];
    const errorPatterns = studentData.learning_data.error_patterns || [];

    // 计算完成率
    const totalProblems = learningStats.total_problems || 0;
    const solvedProblems = learningStats.solved_problems || 0;
    const completionRate = totalProblems > 0 ? (solvedProblems / totalProblems * 100).toFixed(2) : 0;

    // 构建表现摘要
    performanceHighlights = `
学生编程表现关键指标:
- 题目完成率: ${completionRate}% (已完成${solvedProblems}/${totalProblems}题)
- 平均尝试次数: ${learningStats.avg_attempts || 0}
- 平均解题时间: ${learningStats.avg_time_spent ? (learningStats.avg_time_spent / 60).toFixed(2) : 0}分钟
- 最长解题时间: ${learningStats.max_time_spent ? (learningStats.max_time_spent / 60).toFixed(2) : 0}分钟

常见错误类型:
${errorPatterns.map(err => `- ${err.error_type}: 出现${err.occurrence_count}次`).join('\n')}
`;

    // 尝试从学生数据中提取按章节分类的表现
    // 注意：这里假设studentData中可能包含按章节分类的数据
    // 如果没有，我们会在提示词中说明这一点
    if (studentData.chapter_performance) {
      chapterPerformance = `
按章节分类的解题情况:
${studentData.chapter_performance.map(cp =>
  `- ${cp.chapter_title} (${cp.chapter_id}): 尝试${cp.attempted_problems || 0}题，完成${cp.solved_problems || 0}题，平均用时${cp.avg_time_spent ? (cp.avg_time_spent / 60).toFixed(2) : 0}分钟`
).join('\n')}
`;
    } else {
      chapterPerformance = `
注意：当前数据中没有按章节分类的详细表现数据，请基于学生的整体表现和错误模式，推断学生在各章节相关知识点上的可能表现，并据此提供针对性的章节推荐。
`;
    }
  }

  return `请作为一位专业的编程教育顾问，基于以下学生的详细学习数据和编程表现，生成按章节组织的个性化学习建议和关键知识点推荐。

学生ID: ${studentId}

${performanceHighlights}

${chapterPerformance}

完整学习数据:
${JSON.stringify(studentData, null, 2)}

可用的学习章节和资源:
${JSON.stringify(detailedChapters, null, 2)}

请深入分析学生的编程表现，特别关注以下方面：
1. 学生在哪些章节相关的问题上表现较好或较差
2. 学生常犯的错误模式与哪些章节的知识点相关
3. 学生的学习进度和当前可能的知识盲点
4. 学生需要巩固的基础知识和需要拓展的进阶知识

基于上述分析，提供3-5条按章节组织的学习建议，这些建议应该：
- 直接针对学生在特定章节相关知识点上的表现
- 按照数据结构课程的章节顺序提供系统化的学习路径
- 优先推荐学生表现较弱的章节，帮助学生弥补知识盲点
- 同时考虑章节间的依赖关系，确保学习路径的连贯性

每条建议必须包含：
1. 标题（应明确指出推荐的章节名称）
2. 详细描述（必须解释为什么推荐这个章节，以及这个章节如何帮助学生解决当前的学习问题）
3. 优先级（high/medium/low，基于学生在该章节相关知识点上的表现）
4. 关键知识点列表（该章节中学生应该重点掌握的3-5个核心概念或技能）
5. 推荐的章节ID（chapterId，必须从上面的章节列表中选择）

请确保：
- 所有推荐必须按照章节组织，而不是按照难度分类
- 至少覆盖3个不同的章节，形成完整的学习路径
- 关键知识点必须具体且实用，直接指出学生需要掌握的核心概念
- 如果学生在某些章节相关的题目上有明显错误模式，应该详细说明这些错误与章节知识点的关联
- 推荐应该考虑章节间的逻辑顺序和依赖关系，例如先学习基础章节再学习进阶章节

请以JSON格式返回，格式如下：
[
  {
    "title": "学习[章节名称]",
    "description": "详细描述，必须解释为什么推荐这个章节，以及这个章节如何帮助学生解决当前的学习问题",
    "priority": "优先级",
    "keyPoints": [
      "关键知识点1：简短描述这个知识点的重要性和应用场景",
      "关键知识点2：简短描述这个知识点的重要性和应用场景",
      "关键知识点3：简短描述这个知识点的重要性和应用场景"
    ],
    "chapterId": "章节ID"
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
    // 注意：这里无法访问studentData，因此传入null，getDefaultRecommendations函数会处理null情况
    return getDefaultRecommendations(null);
  }
}

/**
 * 获取默认推荐（当AI生成失败时使用）
 * @param {Object} studentData - 学生学习数据，可能为空
 * @returns {Array} 默认推荐列表
 */
function getDefaultRecommendations(studentData) {
  // 定义章节顺序和内容
  const chapters = [
    {
      id: "ch1",
      title: "绪论",
      description: "数据结构的基本概念和算法分析方法",
      priority: "high",
      resources: [
        {
          title: "数据结构概述",
          url: "/student/programming-concepts",
          description: "数据结构基本概念与分类，帮助建立系统的知识框架"
        },
        {
          title: "算法分析基础",
          url: "/student/programming-concepts",
          description: "学习时间复杂度和空间复杂度分析，提高算法效率意识"
        }
      ]
    },
    {
      id: "ch2",
      title: "线性表",
      description: "线性表的基本概念、顺序存储结构和链式存储结构",
      priority: "high",
      resources: [
        {
          title: "线性表的基本概念",
          url: "/student/programming-concepts",
          description: "学习线性表的抽象数据类型和基本操作，夯实基础"
        },
        {
          title: "链表应用_循环链表",
          url: "/student/programming-concepts",
          description: "学习链表的实际应用场景和循环链表的概念，提高实践能力"
        }
      ]
    },
    {
      id: "ch3",
      title: "栈和队列",
      description: "栈和队列的概念、实现和应用",
      priority: "medium",
      resources: [
        {
          title: "栈的基本概念与实现",
          url: "/student/programming-concepts",
          description: "学习栈的基本概念、实现方式和应用场景，提高解题效率"
        }
      ]
    },
    {
      id: "ch4",
      title: "树",
      description: "树的基本概念、二叉树、二叉搜索树等",
      priority: "medium",
      resources: [
        {
          title: "树的基本概念",
          url: "/student/programming-concepts",
          description: "学习树的基本概念、实现方式和应用场景"
        }
      ]
    },
    {
      id: "ch5",
      title: "图",
      description: "图的基本概念、存储结构和基本操作",
      priority: "low",
      resources: [
        {
          title: "图的基本概念",
          url: "/student/programming-concepts?chapter=ch5",
          description: "学习图的基本概念、存储结构和基本操作"
        }
      ]
    },
    {
      id: "ch6",
      title: "查找",
      description: "各种查找算法及其性能分析",
      priority: "medium",
      resources: [
        {
          title: "查找的基本概念",
          url: "/student/programming-concepts?chapter=ch6",
          description: "学习顺序查找、二分查找等基本查找算法，提高代码效率"
        }
      ]
    },
    {
      id: "ch7",
      title: "排序",
      description: "各种排序算法及其性能分析",
      priority: "medium",
      resources: [
        {
          title: "排序算法概述",
          url: "/student/programming-concepts?chapter=ch7",
          description: "学习各种排序算法的原理、实现和性能分析"
        }
      ]
    }
  ];

  // 尝试从学生数据中提取一些基本信息
  let hasErrorPatterns = false;
  let hasLowCompletionRate = true; // 默认假设完成率较低
  let hasLongSolvingTime = false;
  let completionRate = 0;
  let solvedProblems = 0;

  // 如果有学生数据，进行简单分析
  if (studentData && studentData.learning_data) {
    const learningStats = studentData.learning_data.learning_stats || {};
    const errorPatterns = studentData.learning_data.error_patterns || [];

    // 检查是否有错误模式
    hasErrorPatterns = errorPatterns.length > 0;

    // 检查完成率
    const totalProblems = learningStats.total_problems || 0;
    solvedProblems = learningStats.solved_problems || 0;
    if (totalProblems > 0) {
      completionRate = solvedProblems / totalProblems;
      hasLowCompletionRate = completionRate < 0.6; // 完成率低于60%视为较低
    }

    // 检查解题时间
    const avgTimeSpent = learningStats.avg_time_spent || 0;
    hasLongSolvingTime = avgTimeSpent > 600; // 平均解题时间超过10分钟视为较长
  }

  // 基于学生表现和章节顺序生成推荐
  const recommendations = [];

  // 定义章节的关键知识点
  const chapterKeyPoints = {
    "ch1": [
      "数据结构的基本概念：理解数据结构的定义、分类和基本特性",
      "算法复杂度分析：掌握时间复杂度和空间复杂度的计算方法",
      "渐进符号：理解O、Ω、Θ符号的含义和应用场景",
      "算法效率评估：学会分析和比较不同算法的效率"
    ],
    "ch2": [
      "线性表的抽象数据类型：理解线性表的基本操作和实现方式",
      "顺序表的实现：掌握基于数组的线性表实现及其优缺点",
      "链表的实现：掌握单链表、双链表和循环链表的结构和操作",
      "线性表的应用：理解线性表在实际问题中的应用场景"
    ],
    "ch3": [
      "栈的基本概念：理解栈的后进先出特性及其实现方式",
      "队列的基本概念：理解队列的先进先出特性及其实现方式",
      "栈和队列的应用：掌握栈和队列在算法设计中的应用",
      "递归与栈：理解递归调用与栈的关系"
    ],
    "ch4": [
      "树的基本概念：理解树的定义、术语和基本性质",
      "二叉树：掌握二叉树的特性、遍历方法和实现",
      "二叉搜索树：理解二叉搜索树的特性和基本操作",
      "平衡树：了解AVL树、红黑树等平衡树的基本概念"
    ],
    "ch5": [
      "图的基本概念：理解图的定义、术语和基本性质",
      "图的存储结构：掌握邻接矩阵和邻接表的实现方式",
      "图的遍历：掌握深度优先搜索和广度优先搜索算法",
      "最短路径算法：理解Dijkstra算法和Floyd算法的原理"
    ],
    "ch6": [
      "顺序查找：理解顺序查找的原理和适用场景",
      "二分查找：掌握二分查找的原理、实现和时间复杂度",
      "哈希查找：理解哈希函数、冲突解决和哈希表的实现",
      "查找算法比较：能够根据具体场景选择合适的查找算法"
    ],
    "ch7": [
      "内部排序算法：掌握冒泡排序、插入排序、选择排序等基本排序算法",
      "高级排序算法：理解快速排序、归并排序、堆排序的原理和实现",
      "排序算法的稳定性：理解排序稳定性的概念及其重要性",
      "排序算法的比较：能够根据数据特点选择合适的排序算法"
    ]
  };

  // 1. 首先推荐绪论章节（对所有学生）
  recommendations.push({
    title: `学习${chapters[0].title}`,
    description: hasLowCompletionRate
      ? `您的题目完成率较低（${(completionRate * 100).toFixed(2)}%），建议先系统学习${chapters[0].title}章节，掌握数据结构的基本概念和算法分析方法，这将为后续学习打下坚实基础。`
      : `为了更系统地学习数据结构，建议先学习${chapters[0].title}章节，掌握数据结构的基本概念和算法分析方法，这将帮助您更好地理解后续章节。`,
    priority: chapters[0].priority,
    keyPoints: chapterKeyPoints["ch1"],
    chapterId: chapters[0].id
  });

  // 2. 然后推荐线性表章节（对所有学生）
  recommendations.push({
    title: `学习${chapters[1].title}`,
    description: hasErrorPatterns
      ? `您在编程中出现了一些错误模式，这可能与对基础数据结构理解不够深入有关。${chapters[1].title}是最基础的数据结构，建议重点学习顺序表和链表的实现原理，这将帮助您解决常见的编程错误。`
      : `${chapters[1].title}是最基础的数据结构，理解线性表的概念和实现对学习其他数据结构非常重要。建议学习顺序表和链表的实现方式及其应用场景，为后续章节打下基础。`,
    priority: chapters[1].priority,
    keyPoints: chapterKeyPoints["ch2"],
    chapterId: chapters[1].id
  });

  // 3. 根据学生表现选择后续章节
  // 如果解题时间长，推荐栈和队列
  if (hasLongSolvingTime) {
    recommendations.push({
      title: `学习${chapters[2].title}`,
      description: `您的平均解题时间较长，学习${chapters[2].title}可以帮助您更高效地解决特定类型的问题。栈和队列在算法实现中有广泛应用，掌握这些数据结构将显著提高您的解题效率。`,
      priority: "high",
      keyPoints: chapterKeyPoints["ch3"],
      chapterId: chapters[2].id
    });
  }
  // 如果完成率高，推荐树结构
  else if (!hasLowCompletionRate && solvedProblems > 5) {
    recommendations.push({
      title: `学习${chapters[3].title}`,
      description: `您已经掌握了基础的线性数据结构，现在可以学习更复杂的${chapters[3].title}结构。树是一种重要的非线性数据结构，在许多高级算法中都有应用，学习树的概念和实现将帮助您解决更复杂的问题。`,
      priority: chapters[3].priority,
      keyPoints: chapterKeyPoints["ch4"],
      chapterId: chapters[3].id
    });
  }
  // 否则，继续推荐栈和队列
  else {
    recommendations.push({
      title: `学习${chapters[2].title}`,
      description: `在掌握了线性表的基础知识后，建议学习${chapters[2].title}，它们是线性表的扩展和应用。这些数据结构在解决实际问题中有广泛应用，是算法实现的重要工具。`,
      priority: chapters[2].priority,
      keyPoints: chapterKeyPoints["ch3"],
      chapterId: chapters[2].id
    });
  }

  // 4. 如果学生表现较好，额外推荐一个进阶章节
  if (!hasLowCompletionRate && solvedProblems > 10) {
    // 根据已解决的题目数量选择不同的进阶章节
    if (solvedProblems > 15) {
      // 推荐排序算法
      recommendations.push({
        title: `学习${chapters[6].title}`,
        description: `您的学习表现优秀（已解决${solvedProblems}题），建议学习${chapters[6].title}章节，深入了解各种排序算法及其性能分析。这将帮助您在复杂场景中选择最合适的算法，提高代码效率。`,
        priority: chapters[6].priority,
        keyPoints: chapterKeyPoints["ch7"],
        chapterId: chapters[6].id
      });
    } else {
      // 推荐查找算法
      recommendations.push({
        title: `学习${chapters[5].title}`,
        description: `基于您的学习表现（已解决${solvedProblems}题），您已经掌握了基础知识，建议学习${chapters[5].title}章节，了解各种查找算法及其应用。这将帮助您解决更复杂的问题并提高代码效率。`,
        priority: chapters[5].priority,
        keyPoints: chapterKeyPoints["ch6"],
        chapterId: chapters[5].id
      });
    }
  }

  // 确保至少有3条推荐
  if (recommendations.length < 3) {
    // 找出尚未推荐的章节
    const recommendedChapterIds = recommendations.map(rec => rec.chapterId);
    const unrecommendedChapters = chapters.filter(ch => !recommendedChapterIds.includes(ch.id));

    if (unrecommendedChapters.length > 0) {
      const nextChapter = unrecommendedChapters[0];
      recommendations.push({
        title: `学习${nextChapter.title}`,
        description: `按照数据结构课程的学习顺序，在掌握前面章节的基础上，建议继续学习${nextChapter.title}章节。${nextChapter.description}，这将进一步拓展您的知识面。`,
        priority: nextChapter.priority,
        keyPoints: chapterKeyPoints[nextChapter.id] || ["掌握基本概念和术语", "理解核心算法和数据结构", "学习实际应用场景和案例"],
        chapterId: nextChapter.id
      });
    }
  }

  return recommendations;
}

module.exports = {
  generateLearningRecommendations,
  getStudentLearningData
};
