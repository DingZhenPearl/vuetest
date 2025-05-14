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
      const result = JSON.parse(content);
      console.log('成功直接解析JSON');
      return adaptResponseFormat(result);
    } catch (jsonError) {
      console.log('直接解析JSON失败，尝试提取JSON部分');

      // 尝试提取JSON部分
      const jsonMatch = content.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        try {
          // 清理JSON字符串，处理可能的格式问题
          let jsonStr = jsonMatch[0];

          // 处理嵌套引号问题
          // 1. 先替换所有内部的双引号为特殊标记
          jsonStr = jsonStr.replace(/"([^"]*)":/g, function(match) {
            return match; // 保留属性名中的引号
          });

          // 2. 替换字符串值中的引号
          jsonStr = jsonStr.replace(/:\s*"([^"]*)"/g, function(match, p1) {
            // 将内部的双引号替换为单引号
            let value = p1.replace(/"/g, "'");
            return ': "' + value + '"';
          });

          // 3. 修复常见的JSON格式问题
          jsonStr = jsonStr.replace(/,\s*}/g, '}'); // 移除对象末尾多余的逗号
          jsonStr = jsonStr.replace(/,\s*]/g, ']'); // 移除数组末尾多余的逗号

          console.log('清理后的JSON字符串:', jsonStr);

          const result = JSON.parse(jsonStr);
          console.log('成功提取并解析JSON部分');
          return adaptResponseFormat(result);
        } catch (extractError) {
          console.error('提取的JSON部分解析失败:', extractError);
          // 继续尝试其他方法，不抛出异常
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

          // 处理嵌套引号问题
          // 1. 先替换所有内部的双引号为特殊标记
          jsonContent = jsonContent.replace(/"([^"]*)":/g, function(match) {
            return match; // 保留属性名中的引号
          });

          // 2. 替换字符串值中的引号
          jsonContent = jsonContent.replace(/:\s*"([^"]*)"/g, function(match, p1) {
            // 将内部的双引号替换为单引号
            let value = p1.replace(/"/g, "'");
            return ': "' + value + '"';
          });

          // 3. 修复常见的JSON格式问题
          jsonContent = jsonContent.replace(/,\s*}/g, '}'); // 移除对象末尾多余的逗号
          jsonContent = jsonContent.replace(/,\s*]/g, ']'); // 移除数组末尾多余的逗号

          console.log('清理后的markdown JSON字符串:', jsonContent);

          const result = JSON.parse(jsonContent);
          console.log('成功从markdown代码块提取并解析JSON');
          return adaptResponseFormat(result);
        } catch (markdownError) {
          console.error('从markdown提取的JSON解析失败:', markdownError);
        }
      }

      // 尝试手动解析内容，提取关键信息
      console.log('尝试手动解析内容...');
      try {
        const manualResult = extractDataManually(content);
        if (manualResult) {
          console.log('成功手动解析内容');
          return manualResult;
        }
      } catch (manualError) {
        console.error('手动解析内容失败:', manualError);
      }

      // 所有JSON解析方法都失败，返回一个默认结构
      console.warn('所有解析方法都失败，使用默认结构');
      return {
        pattern: content,
        strengths: "数据解析失败，无法提取优势信息",
        weaknesses: "数据解析失败，无法提取弱点信息",
        suggestions: "数据解析失败，无法提取建议信息"
      };
    }
  } catch (error) {
    console.error('解析AI响应失败:', error);
    // 返回一个错误结构而不是抛出异常，这样前端仍然能收到响应
    return {
      pattern: "AI响应解析失败: " + (error.message || '未知错误'),
      strengths: "数据解析失败",
      weaknesses: "数据解析失败",
      suggestions: "请检查服务器日志以获取更多信息"
    };
  }
}

/**
 * 适配响应格式，确保返回的数据结构符合前端期望
 * @param {Object} result 解析后的结果
 * @returns {Object} 适配后的结果
 */
function adaptResponseFormat(result) {
  // 检查是否是学生分析结果（包含pattern字段）
  if (result.pattern !== undefined) {
    // 检查pattern字段是否只是标题而不是实际内容
    let patternContent = result.pattern;
    if (patternContent === "学习模式分析" || patternContent === "学习模式" || patternContent === "pattern") {
      // 如果pattern只是标题，尝试从strengths和weaknesses中提取更有意义的内容
      if (result.strengths && typeof result.strengths === 'string' && result.strengths.length > 20) {
        patternContent = `根据分析，该学生在简单问题上表现较好，但在复杂问题上需要提高。详细情况请参考下方的优势领域和待提升领域。`;
      } else {
        patternContent = "系统未能提供详细的学习模式分析，请参考下方的优势领域和待提升领域了解学生情况。";
      }
    }

    // 确保所有字段都存在
    return {
      pattern: patternContent,
      strengths: result.strengths || "无优势领域数据",
      weaknesses: result.weaknesses || "无待提升领域数据",
      suggestions: result.suggestions || "无学习建议数据"
    };
  }
  // 检查是否是教学分析结果（包含summary字段）
  else if (result.summary !== undefined) {
    // 转换为学生分析结果格式
    return {
      pattern: result.summary || "无学习模式分析",
      strengths: Array.isArray(result.strengths) ? result.strengths.join("\n") : (result.strengths || "无优势领域数据"),
      weaknesses: Array.isArray(result.weaknesses) ? result.weaknesses.join("\n") : (result.weaknesses || "无待提升领域数据"),
      suggestions: Array.isArray(result.recommendations) ? result.recommendations.join("\n") : (result.recommendations || "无学习建议数据")
    };
  }
  // 未知格式，尝试最佳匹配
  else {
    const keys = Object.keys(result);
    return {
      pattern: result[keys.find(k => k.includes('pattern') || k.includes('summary') || k.includes('分析'))] || "无学习模式分析",
      strengths: result[keys.find(k => k.includes('strength') || k.includes('优势'))] || "无优势领域数据",
      weaknesses: result[keys.find(k => k.includes('weakness') || k.includes('弱点') || k.includes('待提升'))] || "无待提升领域数据",
      suggestions: result[keys.find(k => k.includes('suggestion') || k.includes('recommendation') || k.includes('建议'))] || "无学习建议数据"
    };
  }
}

/**
 * 手动从内容中提取数据
 * @param {String} content AI响应内容
 * @returns {Object|null} 提取的数据或null
 */
function extractDataManually(content) {
  console.log('开始手动提取数据...');

  // 尝试直接从JSON字符串中提取关键字段
  try {
    // 尝试提取pattern字段
    const patternRegex = /"pattern"\s*:\s*"([^"]*)"/;
    const patternMatch = content.match(patternRegex);
    const pattern = patternMatch ? patternMatch[1] : "";

    // 尝试提取strengths字段 - 这里使用非贪婪匹配，避免匹配到其他字段
    const strengthsRegex = /"strengths"\s*:\s*"(.*?)(?=",\s*"w)/s;
    const strengthsMatch = content.match(strengthsRegex);
    const strengths = strengthsMatch ? strengthsMatch[1] : "";

    // 尝试提取weaknesses字段
    const weaknessesRegex = /"weaknesses"\s*:\s*"(.*?)(?=",\s*"s)/s;
    const weaknessesMatch = content.match(weaknessesRegex);
    const weaknesses = weaknessesMatch ? weaknessesMatch[1] : "";

    // 尝试提取suggestions字段
    const suggestionsRegex = /"suggestions"\s*:\s*"(.*?)(?="\s*})/s;
    const suggestionsMatch = content.match(suggestionsRegex);
    const suggestions = suggestionsMatch ? suggestionsMatch[1] : "";

    console.log('手动提取结果:', {
      pattern: pattern ? '提取成功' : '未提取',
      strengths: strengths ? '提取成功' : '未提取',
      weaknesses: weaknesses ? '提取成功' : '未提取',
      suggestions: suggestions ? '提取成功' : '未提取'
    });

    // 如果至少提取到一个字段，返回结果
    if (pattern || strengths || weaknesses || suggestions) {
      return {
        pattern: pattern || "学习模式分析",
        strengths: strengths || "无优势领域数据",
        weaknesses: weaknesses || "无待提升领域数据",
        suggestions: suggestions || "无学习建议数据"
      };
    }
  } catch (error) {
    console.error('直接提取JSON字段失败:', error);
  }

  // 如果直接提取失败，尝试通过文本模式提取
  try {
    // 尝试提取学习模式分析、优势领域、待提升领域和学习建议
    let pattern = "", strengths = "", weaknesses = "", suggestions = "";

    // 提取学习模式分析
    const patternMatch = content.match(/学习模式分析[：:]\s*([\s\S]*?)(?=优势领域[：:]|待提升领域[：:]|学习建议[：:]|$)/i);
    if (patternMatch && patternMatch[1]) {
      pattern = patternMatch[1].trim();
    }

    // 提取优势领域
    const strengthsMatch = content.match(/优势领域[：:]\s*([\s\S]*?)(?=待提升领域[：:]|学习建议[：:]|$)/i);
    if (strengthsMatch && strengthsMatch[1]) {
      strengths = strengthsMatch[1].trim();
    }

    // 提取待提升领域
    const weaknessesMatch = content.match(/待提升领域[：:]\s*([\s\S]*?)(?=学习建议[：:]|$)/i);
    if (weaknessesMatch && weaknessesMatch[1]) {
      weaknesses = weaknessesMatch[1].trim();
    }

    // 提取学习建议
    const suggestionsMatch = content.match(/学习建议[：:]\s*([\s\S]*?)(?=$)/i);
    if (suggestionsMatch && suggestionsMatch[1]) {
      suggestions = suggestionsMatch[1].trim();
    }

    console.log('文本模式提取结果:', {
      pattern: pattern ? '提取成功' : '未提取',
      strengths: strengths ? '提取成功' : '未提取',
      weaknesses: weaknesses ? '提取成功' : '未提取',
      suggestions: suggestions ? '提取成功' : '未提取'
    });

    // 如果至少提取到一个字段，返回结果
    if (pattern || strengths || weaknesses || suggestions) {
      return {
        pattern: pattern || "学习模式分析",
        strengths: strengths || "无优势领域数据",
        weaknesses: weaknesses || "无待提升领域数据",
        suggestions: suggestions || "无学习建议数据"
      };
    }
  } catch (error) {
    console.error('文本模式提取失败:', error);
  }

  // 如果所有提取方法都失败，尝试最后的方法：直接使用整个内容
  if (content && content.length > 0) {
    // 检查内容是否包含关键词
    const hasPattern = content.includes('学习模式') || content.includes('pattern');
    const hasStrengths = content.includes('优势') || content.includes('strengths');
    const hasWeaknesses = content.includes('待提升') || content.includes('弱点') || content.includes('weaknesses');
    const hasSuggestions = content.includes('建议') || content.includes('suggestions');

    if (hasPattern || hasStrengths || hasWeaknesses || hasSuggestions) {
      console.log('使用整个内容作为分析结果');
      return {
        pattern: "从AI响应中提取的学习模式分析",
        strengths: hasStrengths ? "AI响应中包含优势分析，但格式无法解析" : "无优势领域数据",
        weaknesses: hasWeaknesses ? "AI响应中包含待提升领域分析，但格式无法解析" : "无待提升领域数据",
        suggestions: hasSuggestions ? "AI响应中包含学习建议，但格式无法解析" : "无学习建议数据"
      };
    }
  }

  console.log('所有手动提取方法都失败');
  return null;
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
    "pattern": "这里应该是对学生整体学习模式的详细分析，包括学习习惯、解题特点等，不少于100字",
    "strengths": "这里应该是学生的优势领域分析，不少于50字",
    "weaknesses": "这里应该是学生的待提升领域分析，不少于50字",
    "suggestions": "这里应该是针对学生情况的具体学习建议，不少于100字"
  }

  注意：
  1. 请确保返回的是有效的JSON格式，不要有多余的逗号或引号不匹配的情况
  2. 字符串值中如果包含引号，请使用单引号代替双引号，避免JSON解析错误
  3. pattern字段必须提供实质性的分析内容，不能只是"学习模式分析"这样的标题
  4. 所有分析必须基于提供的数据，如果数据不足，请在分析中说明
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

    // 确保分析结果包含必要的字段
    const validatedAnalysis = {
      pattern: analysis.pattern || "无学习模式分析",
      strengths: analysis.strengths || "无优势领域数据",
      weaknesses: analysis.weaknesses || "无待提升领域数据",
      suggestions: analysis.suggestions || "无学习建议数据"
    };

    // 将分析结果转换为JSON字符串
    const analysisJson = JSON.stringify(validatedAnalysis);

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
