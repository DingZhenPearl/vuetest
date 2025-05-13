/**
 * AI分析路由 - 处理AI分析相关的请求
 */
const express = require('express');
const router = express.Router();
const aiAnalysisService = require('../services/ai-analysis');

/**
 * 分析教学和编程数据
 * POST /api/teaching/ai-analysis
 *
 * 请求体:
 * {
 *   analysisType: 'teaching' | 'coding',  // 分析类型
 *   className: String,                    // 班级名称
 *   data: Object                          // 要分析的数据
 * }
 *
 * 响应:
 * {
 *   success: Boolean,
 *   analysis: {
 *     summary: String,
 *     strengths: Array<String>,
 *     weaknesses: Array<String>,
 *     recommendations: Array<String>
 *   },
 *   message: String (可选，仅在失败时返回)
 * }
 */
router.post('/ai-analysis', async (req, res) => {
  try {
    const { analysisType, className, data } = req.body;

    if (!analysisType || !className || !data) {
      return res.status(400).json({
        success: false,
        message: '缺少必要参数'
      });
    }

    let analysis;

    // 根据分析类型调用不同的分析服务
    if (analysisType === 'teaching') {
      analysis = await aiAnalysisService.analyzeTeachingData(data);
    } else if (analysisType === 'coding') {
      analysis = await aiAnalysisService.analyzeCodingData(data);
    } else if (analysisType === 'combined') {
      analysis = await aiAnalysisService.analyzeCombinedData(data);
    } else {
      return res.status(400).json({
        success: false,
        message: '不支持的分析类型'
      });
    }

    // 返回分析结果
    res.json({
      success: true,
      analysis
    });
  } catch (error) {
    console.error('AI分析失败:', error);
    res.status(500).json({
      success: false,
      message: error.message || '服务器内部错误'
    });
  }
});

module.exports = router;
