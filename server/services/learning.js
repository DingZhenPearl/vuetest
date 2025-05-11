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
    // 1. 获取学生的学习数据
    const studentData = await getStudentLearningData(studentId);
    
    if (!studentData || !studentData.success) {
      console.error('获取学生学习数据失败');
      return [];
    }
    
    // 2. 使用大模型分析学生数据并生成推荐
    const recommendations = await generateRecommendationsWithAI(studentData.data, studentId);
    
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
    
    return result;
  } catch (error) {
    console.error('获取学生学习数据失败:', error);
    throw error;
  }
}

/**
 * 使用AI生成个性化学习推荐
 * @param {Object} studentData - 学生学习数据
 * @param {string} studentId - 学生ID
 * @returns {Promise<Array>} 学习推荐列表
 */
async function generateRecommendationsWithAI(studentData, studentId) {
  try {
    // 构建提示词
    const prompt = buildPromptForRecommendations(studentData, studentId);
    
    // 调用大模型API
    const completion = await openai.chat.completions.create({
      model: 'lite', // 使用讯飞星火大模型
      messages: [
        {
          role: 'system',
          content: '你是一个专业的教育顾问和学习路径规划专家，擅长分析学生的学习行为和表现，并提供个性化的学习建议和资源推荐。'
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
    const aiResponse = completion.choices[0].message.content;
    const recommendations = parseAIResponseToRecommendations(aiResponse);
    
    return recommendations;
  } catch (error) {
    console.error('AI生成推荐失败:', error);
    // 返回默认推荐
    return getDefaultRecommendations();
  }
}

/**
 * 构建用于生成推荐的提示词
 * @param {Object} studentData - 学生学习数据
 * @param {string} studentId - 学生ID
 * @returns {string} 提示词
 */
function buildPromptForRecommendations(studentData, studentId) {
  return `请基于以下学生的学习数据，生成3-5条个性化学习建议和资源推荐。
学生ID: ${studentId}

学习数据:
${JSON.stringify(studentData, null, 2)}

请分析学生的优势和不足，并提供具体的学习路径建议。每条建议应包含：
1. 标题
2. 详细描述
3. 优先级（high/medium/low）
4. 相关资源推荐（如有）
5. 是否可立即执行的行动项（actionable）

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
    "problemId": "相关题目ID（如有）"
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
    // 尝试从AI响应中提取JSON
    const jsonMatch = aiResponse.match(/\[\s*\{.*\}\s*\]/s);
    
    if (jsonMatch) {
      const jsonStr = jsonMatch[0];
      return JSON.parse(jsonStr);
    }
    
    // 如果没有找到JSON格式，尝试解析整个响应
    return JSON.parse(aiResponse);
  } catch (error) {
    console.error('解析AI响应失败:', error);
    console.log('原始AI响应:', aiResponse);
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
      title: "学习算法基础",
      description: "掌握基本算法和数据结构，这将帮助你更高效地解决编程问题。",
      priority: "medium",
      resources: [
        {
          title: "算法入门",
          description: "推荐学习排序、搜索等基础算法"
        }
      ],
      actionable: false
    },
    {
      title: "参与小组讨论",
      description: "与同学交流学习心得，分享解题思路，互相学习。",
      priority: "low",
      resources: [],
      actionable: false
    }
  ];
}

module.exports = {
  generateLearningRecommendations
};
