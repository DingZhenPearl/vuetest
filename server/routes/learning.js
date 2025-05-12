/**
 * 学习分析和推荐相关路由
 */
const express = require('express');
const router = express.Router();
const { executePythonScript } = require('../services/python');
const { generateLearningRecommendations, getStudentLearningData } = require('../services/learning');

/**
 * 获取学生个性化学习推荐
 */
router.get('/recommendations/:studentId', async (req, res) => {
  try {
    const { studentId } = req.params;

    if (!studentId) {
      return res.status(400).json({
        success: false,
        message: '缺少学生ID参数'
      });
    }

    // 调用服务生成个性化学习推荐
    const recommendations = await generateLearningRecommendations(studentId);

    res.json({
      success: true,
      recommendations
    });
  } catch (error) {
    console.error('获取学习推荐失败:', error);
    res.status(500).json({
      success: false,
      message: '服务器错误',
      error: error.message
    });
  }
});

/**
 * 标记推荐为已读
 */
router.post('/recommendations/:recommendationId/read', async (req, res) => {
  try {
    const { recommendationId } = req.params;
    const { studentId } = req.body;

    if (!recommendationId || !studentId) {
      return res.status(400).json({
        success: false,
        message: '缺少必要参数'
      });
    }

    // 调用Python脚本标记推荐为已读
    const result = await executePythonScript('learning_recommendations.py', [
      'mark_as_read',
      studentId,
      recommendationId
    ]);

    res.json(result);
  } catch (error) {
    console.error('标记推荐为已读失败:', error);
    res.status(500).json({
      success: false,
      message: '服务器错误',
      error: error.message
    });
  }
});

/**
 * 获取学生学习行为分析
 */
router.get('/behavior-analysis/:studentId', async (req, res) => {
  try {
    const { studentId } = req.params;

    if (!studentId) {
      return res.status(400).json({
        success: false,
        message: '缺少学生ID参数'
      });
    }

    console.log(`正在获取学生学习行为分析，学生ID: ${studentId}`);

    try {
      // 调用Python脚本获取学习行为分析
      const result = await executePythonScript('learning_analysis.py', [
        'analyze_behavior',
        studentId
      ]);

      console.log(`学习行为分析结果:`, result);

      // 检查结果是否有效
      if (!result || !result.success) {
        console.warn(`学习行为分析结果无效:`, result);
        return res.json({
          success: false,
          message: result?.message || '获取学习行为分析失败',
          error: result?.rawOutput || '未知错误'
        });
      }

      res.json(result);
    } catch (scriptError) {
      console.error('执行Python脚本失败:', scriptError);
      // 返回默认分析数据
      res.json({
        success: true,
        data: {
          behavior_analysis: {
            pattern: "您尚未完成足够的习题，无法生成详细的学习模式分析。建议先完成一些基础习题，以便系统能够分析您的学习行为。",
            strengths: "暂无足够数据分析您的优势领域。请完成更多习题以获取详细分析。",
            weaknesses: "暂无足够数据分析您的待提升领域。请完成更多习题以获取详细分析。",
            suggestions: "建议从基础习题开始，逐步提高难度。定期练习，保持学习的连续性。尝试不同类型的题目，拓展知识面。"
          }
        }
      });
    }
  } catch (error) {
    console.error('获取学习行为分析失败:', error);
    res.status(500).json({
      success: false,
      message: '服务器错误',
      error: error.message
    });
  }
});

/**
 * 获取学生学习数据
 */
router.get('/student-data/:studentId', async (req, res) => {
  try {
    const { studentId } = req.params;

    if (!studentId) {
      return res.status(400).json({
        success: false,
        message: '缺少学生ID参数'
      });
    }

    console.log(`正在获取学生学习数据，学生ID: ${studentId}`);

    try {
      // 调用服务获取学生学习数据
      const result = await getStudentLearningData(studentId);
      res.json(result);
    } catch (scriptError) {
      console.error('获取学生学习数据失败:', scriptError);
      res.status(500).json({
        success: false,
        message: '获取学生学习数据失败',
        error: scriptError.message
      });
    }
  } catch (error) {
    console.error('获取学生学习数据失败:', error);
    res.status(500).json({
      success: false,
      message: '服务器错误',
      error: error.message
    });
  }
});

module.exports = router;
