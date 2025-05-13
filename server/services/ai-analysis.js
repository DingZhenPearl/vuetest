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
    const apiUrl = config.AI_API_URL || 'https://spark-api-open.xf-yun.com/v1/chat/completions';
    const apiKey = config.AI_API_KEY;

    // 如果没有配置API密钥，则抛出错误
    if (!apiKey) {
      console.error('未配置AI API密钥');
      throw new Error('未配置AI API密钥，请在服务器配置中设置有效的API密钥');
    }

    // 检查API密钥格式是否符合讯飞的要求（应该是 apiKey:apiSecret 格式）
    if (!apiKey.includes(':')) {
      console.warn('API密钥格式可能不正确，讯飞API需要 apiKey:apiSecret 格式');
    }

    console.log('调用讯飞星火大模型API...');

    const response = await axios.post(apiUrl, {
      model: config.AI_MODEL || "lite",
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

    console.log('讯飞API响应状态:', response.status);

    // 检查响应是否有效
    if (!response.data || !response.data.choices || !response.data.choices[0]) {
      console.error('讯飞API返回的数据格式不正确:', response.data);
      throw new Error('API返回的数据格式不正确');
    }

    return response.data;
  } catch (error) {
    console.error('调用讯飞AI模型失败:', error);
    if (error.response) {
      console.error('错误响应数据:', error.response.data);
      console.error('错误响应状态:', error.response.status);
    }
    // 抛出错误，不返回模拟数据
    throw new Error('讯飞AI API调用失败: ' + (error.message || '未知错误'));
  }
}



/**
 * 解析AI模型返回的结果
 * @param {Object} response AI模型返回的结果
 * @returns {Object} 解析后的结果
 */
function parseAIResponse(response) {
  try {
    console.log('解析AI响应...');

    // 检查响应格式
    if (!response || !response.choices || !response.choices[0]) {
      console.error('AI响应格式不正确:', response);
      throw new Error('AI响应格式不正确');
    }

    // 从响应中提取AI生成的内容
    const content = response.choices[0].message.content;
    console.log('AI响应内容:', content);

    // 尝试解析JSON
    try {
      // 首先尝试直接解析整个内容
      return JSON.parse(content);
    } catch (jsonError) {
      console.log('直接解析JSON失败，尝试提取JSON部分');

      // 尝试提取JSON部分
      const jsonMatch = content.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        try {
          const result = JSON.parse(jsonMatch[0]);
          console.log('成功提取并解析JSON部分');
          return result;
        } catch (extractError) {
          console.error('提取的JSON部分解析失败:', extractError);
          throw extractError;
        }
      }

      // 如果内容包含markdown代码块，尝试提取
      if (content.includes('```json')) {
        try {
          let jsonContent = content.split('```json')[1];
          if (jsonContent.includes('```')) {
            jsonContent = jsonContent.split('```')[0];
          }
          jsonContent = jsonContent.trim();
          const result = JSON.parse(jsonContent);
          console.log('成功从markdown代码块提取并解析JSON');
          return result;
        } catch (markdownError) {
          console.error('从markdown提取的JSON解析失败:', markdownError);
        }
      }

      // 所有JSON解析方法都失败，返回一个默认结构
      console.warn('所有JSON解析方法都失败，使用默认结构');
      return {
        summary: content,
        strengths: ["数据解析失败，无法提取优势信息"],
        weaknesses: ["数据解析失败，无法提取弱点信息"],
        recommendations: ["数据解析失败，无法提取建议信息"],
        correlation: "数据解析失败，无法提取关联性分析"
      };
    }
  } catch (error) {
    console.error('解析AI响应失败:', error);
    // 返回一个错误结构而不是抛出异常，这样前端仍然能收到响应
    return {
      summary: "AI响应解析失败: " + (error.message || '未知错误'),
      strengths: ["数据解析失败"],
      weaknesses: ["数据解析失败"],
      recommendations: ["请检查服务器日志以获取更多信息"],
      correlation: "数据解析失败"
    };
  }
}

/**
 * 生成综合分析的提示词
 * @param {Object} data 包含教学和编程数据的对象
 * @returns {String} 提示词
 */
function generateCombinedPrompt(data) {
  // 提取关键数据
  const { teaching = {}, coding = {}, className = '未知班级' } = data;

  // 检查数据是否为空
  const hasTeachingData = teaching &&
    (teaching.daily_trends?.length > 0 ||
     teaching.problem_difficulty?.length > 0 ||
     teaching.progress_distribution?.length > 0 ||
     teaching.efficiency_analysis?.length > 0);

  const hasCodingData = coding &&
    (coding.student_rankings?.length > 0 ||
     coding.problem_stats?.length > 0 ||
     Object.keys(coding.class_stats || {}).length > 0);

  // 如果数据为空，添加提示
  let dataStatusMessage = '';
  if (!hasTeachingData && !hasCodingData) {
    dataStatusMessage = `
    注意：提供的教学数据和编程数据都为空或不完整。请检查数据库中是否有该班级的学生数据。
    如果数据确实不存在，请在分析结果中明确指出数据缺失，并建议教师收集更多数据。
    `;
  } else if (!hasTeachingData) {
    dataStatusMessage = `
    注意：提供的教学数据为空或不完整，但编程数据有效。请基于可用的编程数据进行分析。
    `;
  } else if (!hasCodingData) {
    dataStatusMessage = `
    注意：提供的编程数据为空或不完整，但教学数据有效。请基于可用的教学数据进行分析。
    `;
  }

  // 构建提示词
  return `
  请综合分析以下教学和编程数据，并提供教学洞察和建议：
  ${dataStatusMessage}
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

  如果数据不足以进行全面分析，请在相应部分说明数据缺失，并提供基于有限数据的分析或建议教师如何收集更多数据。

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

/**
 * 分析单个学生的学习数据
 * @param {Object} data 学生学习数据
 * @returns {Promise<Object>} 分析结果
 */
async function analyzeStudentData(data) {
  try {
    // 准备发送给AI模型的数据
    const prompt = generateStudentPrompt(data);

    // 调用AI模型API
    const response = await callAIModel(prompt);

    // 解析AI模型返回的结果
    const result = parseAIResponse(response);

    // 保存分析结果到数据库
    try {
      await saveStudentAnalysis(data.student.student_id, result);
    } catch (saveError) {
      console.warn('保存学生分析结果失败:', saveError);
      // 继续返回结果，即使保存失败
    }

    return result;
  } catch (error) {
    console.error('分析学生数据失败:', error);
    throw new Error('分析学生数据失败: ' + (error.message || '未知错误'));
  }
}

/**
 * 生成学生数据分析的提示词
 * @param {Object} data 学生数据
 * @returns {String} 提示词
 */
function generateStudentPrompt(data) {
  // 提取关键数据
  const { student, learning_stats, difficulty_stats, error_patterns, recent_activity, problems } = data;

  // 构建提示词
  return `
  请分析以下学生的学习数据，并提供详细的学习模式分析、优势领域、待提升领域和学习建议。

  学生基本信息:
  ${JSON.stringify(student)}

  学习统计数据:
  ${JSON.stringify(learning_stats)}

  按难度分类的解题情况:
  ${JSON.stringify(difficulty_stats)}

  常见错误类型:
  ${JSON.stringify(error_patterns)}

  最近一周的活动:
  ${JSON.stringify(recent_activity)}

  题目完成情况:
  ${JSON.stringify(problems ? problems.slice(0, 10) : [])}

  请以JSON格式返回分析结果，格式如下:
  {
    "pattern": "学习模式分析",
    "strengths": "优势领域",
    "weaknesses": "待提升领域",
    "suggestions": "学习建议"
  }
  `;
}

/**
 * 保存学生分析结果到数据库
 * @param {String} studentId 学生ID
 * @param {Object} analysis 分析结果
 * @returns {Promise<void>}
 */
async function saveStudentAnalysis(studentId, analysis) {
  try {
    const { executePythonScript } = require('../services/python');

    // 将分析结果转换为JSON字符串
    const analysisJson = JSON.stringify(analysis);

    // 调用Python脚本保存分析结果
    const result = await executePythonScript('save_student_analysis.py', [
      studentId,
      analysisJson
    ]);

    if (!result.success) {
      throw new Error(result.message || '保存分析结果失败');
    }

    console.log(`成功保存学生${studentId}的分析结果到数据库`);
  } catch (error) {
    console.error(`保存学生${studentId}的分析结果失败:`, error);
    throw error;
  }
}

module.exports = {
  analyzeTeachingData,
  analyzeCodingData,
  analyzeCombinedData,
  analyzeStudentData
};
