/**
 * AI分析服务 - 用于分析教学和编程数据
 */
const axios = require('axios');
const config = require('../config');

/**
 * 分析教学数据
 * @param {Object} data 教学数据
 * @returns {Promise<Object>} 分析结果
 */
async function analyzeTeachingData(data) {
  try {
    // 准备发送给AI模型的数据
    const prompt = generateTeachingPrompt(data);

    // 调用AI模型API
    const response = await callAIModel(prompt);

    // 解析AI模型返回的结果
    return parseAIResponse(response);
  } catch (error) {
    console.error('分析教学数据失败:', error);
    throw new Error('分析教学数据失败: ' + (error.message || '未知错误'));
  }
}

/**
 * 分析编程数据
 * @param {Object} data 编程数据
 * @returns {Promise<Object>} 分析结果
 */
async function analyzeCodingData(data) {
  try {
    // 准备发送给AI模型的数据
    const prompt = generateCodingPrompt(data);

    // 调用AI模型API
    const response = await callAIModel(prompt);

    // 解析AI模型返回的结果
    return parseAIResponse(response);
  } catch (error) {
    console.error('分析编程数据失败:', error);
    throw new Error('分析编程数据失败: ' + (error.message || '未知错误'));
  }
}

/**
 * 综合分析教学和编程数据
 * @param {Object} data 包含教学和编程数据的对象
 * @returns {Promise<Object>} 分析结果
 */
async function analyzeCombinedData(data) {
  try {
    // 准备发送给AI模型的数据
    const prompt = generateCombinedPrompt(data);

    // 调用AI模型API
    const response = await callAIModel(prompt);

    // 解析AI模型返回的结果
    return parseAIResponse(response);
  } catch (error) {
    console.error('综合分析数据失败:', error);
    throw new Error('综合分析数据失败: ' + (error.message || '未知错误'));
  }
}

/**
 * 生成教学数据分析的提示词
 * @param {Object} data 教学数据
 * @returns {String} 提示词
 */
function generateTeachingPrompt(data) {
  // 提取关键数据
  const { daily_trends, problem_difficulty, progress_distribution, efficiency_analysis, error_patterns } = data;

  // 构建提示词
  return `
  请分析以下教学数据，并提供教学洞察和建议：

  1. 日常趋势数据:
  ${JSON.stringify(daily_trends)}

  2. 题目难度分布:
  ${JSON.stringify(problem_difficulty)}

  3. 学习进度分布:
  ${JSON.stringify(progress_distribution)}

  4. 学习效率分析:
  ${JSON.stringify(efficiency_analysis)}

  5. 错误模式:
  ${JSON.stringify(error_patterns)}

  请提供以下分析:
  1. 总体学习情况摘要
  2. 学生的优势领域（至少3点）
  3. 学生的弱点领域（至少3点）
  4. 针对教师的教学建议（至少5点）

  请以JSON格式返回，格式如下:
  {
    "summary": "总体学习情况摘要",
    "strengths": ["优势1", "优势2", "优势3"],
    "weaknesses": ["弱点1", "弱点2", "弱点3"],
    "recommendations": ["建议1", "建议2", "建议3", "建议4", "建议5"]
  }
  `;
}

/**
 * 生成编程数据分析的提示词
 * @param {Object} data 编程数据
 * @returns {String} 提示词
 */
function generateCodingPrompt(data) {
  // 提取关键数据
  const { class_stats, student_rankings, problem_stats } = data;

  // 构建提示词
  return `
  请分析以下编程数据，并提供教学洞察和建议：

  1. 班级统计数据:
  ${JSON.stringify(class_stats)}

  2. 学生排名数据:
  ${JSON.stringify(student_rankings)}

  3. 问题统计数据:
  ${JSON.stringify(problem_stats)}

  请提供以下分析:
  1. 总体编程学习情况摘要
  2. 学生的编程优势领域（至少3点）
  3. 学生的编程弱点领域（至少3点）
  4. 针对教师的编程教学建议（至少5点）

  请以JSON格式返回，格式如下:
  {
    "summary": "总体编程学习情况摘要",
    "strengths": ["优势1", "优势2", "优势3"],
    "weaknesses": ["弱点1", "弱点2", "弱点3"],
    "recommendations": ["建议1", "建议2", "建议3", "建议4", "建议5"]
  }
  `;
}

/**
 * 调用AI模型API
 * @param {String} prompt 提示词
 * @returns {Promise<Object>} AI模型返回的结果
 */
async function callAIModel(prompt) {
  try {
    // 这里使用配置文件中的AI模型API地址和密钥
    const apiUrl = config.AI_API_URL || 'https://api.openai.com/v1/chat/completions';
    const apiKey = config.AI_API_KEY;

    // 如果没有配置API密钥，则返回模拟数据
    if (!apiKey) {
      console.warn('未配置AI API密钥，返回模拟数据');
      return generateMockResponse(prompt);
    }

    const response = await axios.post(apiUrl, {
      model: config.AI_MODEL || "gpt-3.5-turbo",
      messages: [
        {
          role: "system",
          content: "你是一个专业的教育数据分析师，擅长分析学生的学习数据并提供有价值的教学建议。"
        },
        {
          role: "user",
          content: prompt
        }
      ],
      temperature: 0.7,
      max_tokens: 2000
    }, {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`
      }
    });

    return response.data;
  } catch (error) {
    console.error('调用AI模型失败:', error);
    // 如果API调用失败，也返回模拟数据
    console.warn('AI API调用失败，返回模拟数据');
    return generateMockResponse(prompt);
  }
}

/**
 * 生成模拟的AI响应数据
 * @param {String} prompt 提示词
 * @returns {Object} 模拟的AI响应数据
 */
function generateMockResponse(prompt) {
  // 根据提示词中是否包含"教学"或"编程"来返回不同的模拟数据
  const isTeaching = prompt.includes('教学数据');

  // 模拟的AI响应内容
  const mockContent = {
    choices: [
      {
        message: {
          content: JSON.stringify(isTeaching ? {
            summary: "根据分析的教学数据，学生整体学习情况良好，但存在一些需要改进的地方。大部分学生能够按时完成作业，但在复杂概念的理解上存在困难。",
            strengths: [
              "学生在基础知识掌握方面表现良好，完成率高",
              "学习参与度整体较高，大部分学生能够保持活跃",
              "简单题目的解决能力强，正确率高"
            ],
            weaknesses: [
              "复杂概念理解困难，特别是在抽象数据结构方面",
              "部分学生学习时间分配不合理，导致效率低下",
              "错误模式集中在算法设计和逻辑推理方面"
            ],
            recommendations: [
              "增加复杂概念的实例讲解，使用可视化工具辅助教学",
              "设计针对性的练习，帮助学生克服常见错误",
              "提供更多的学习资源和辅导机会",
              "调整教学进度，为难点内容分配更多时间",
              "鼓励学生之间的协作学习，促进知识共享"
            ]
          } : {
            summary: "根据分析的编程数据，学生在编程实践中表现出不同水平的能力。整体上，基础语法掌握良好，但在算法设计和问题解决策略方面存在明显差异。",
            strengths: [
              "基础语法和语言特性掌握牢固",
              "简单问题的解决速度快，代码质量高",
              "大部分学生能够独立完成基础编程任务"
            ],
            weaknesses: [
              "复杂算法设计能力不足，特别是在递归和动态规划方面",
              "代码优化意识不强，效率问题突出",
              "调试能力有限，解决错误的时间成本高"
            ],
            recommendations: [
              "增加算法设计专题讲解，提供更多实例和练习",
              "引入代码审查环节，培养代码质量和优化意识",
              "教授系统化的调试方法和工具使用",
              "设计递进式的编程挑战，逐步提高难度",
              "组织编程竞赛或项目实践，提高综合应用能力"
            ]
          })
        }
      }
    ]
  };

  return mockContent;
}

/**
 * 解析AI模型返回的结果
 * @param {Object} response AI模型返回的结果
 * @returns {Object} 解析后的结果
 */
function parseAIResponse(response) {
  try {
    // 从响应中提取AI生成的内容
    const content = response.choices[0].message.content;

    // 尝试解析JSON
    const jsonMatch = content.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      return JSON.parse(jsonMatch[0]);
    }

    // 如果无法解析JSON，则返回一个默认结构
    return {
      summary: content,
      strengths: [],
      weaknesses: [],
      recommendations: []
    };
  } catch (error) {
    console.error('解析AI响应失败:', error);
    throw new Error('解析AI响应失败: ' + (error.message || '未知错误'));
  }
}

/**
 * 生成综合分析的提示词
 * @param {Object} data 包含教学和编程数据的对象
 * @returns {String} 提示词
 */
function generateCombinedPrompt(data) {
  // 提取关键数据
  const { teaching, coding, className } = data;

  // 构建提示词
  return `
  请综合分析以下教学和编程数据，并提供教学洞察和建议：

  班级: ${className}

  1. 教学数据:
  ${JSON.stringify(teaching)}

  2. 编程数据:
  ${JSON.stringify(coding)}

  请提供以下综合分析:
  1. 总体学习情况摘要（综合教学和编程数据）
  2. 学生的优势领域（至少3点）
  3. 学生的弱点领域（至少3点）
  4. 针对教师的教学建议（至少5点）
  5. 教学与编程学习的关联性分析

  请以JSON格式返回，格式如下:
  {
    "summary": "总体学习情况摘要",
    "strengths": ["优势1", "优势2", "优势3"],
    "weaknesses": ["弱点1", "弱点2", "弱点3"],
    "recommendations": ["建议1", "建议2", "建议3", "建议4", "建议5"],
    "correlation": "教学与编程学习的关联性分析"
  }
  `;
}

module.exports = {
  analyzeTeachingData,
  analyzeCodingData,
  analyzeCombinedData
};
