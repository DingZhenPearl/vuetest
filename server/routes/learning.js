/**
 * 学习分析和推荐相关路由
 */
const express = require('express');
const router = express.Router();
const { executePythonScript } = require('../services/python');
const { generateLearningRecommendations } = require('../services/learning');

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
    
    // 调用Python脚本获取学习行为分析
    const result = await executePythonScript('learning_analysis.py', [
      'analyze_behavior',
      studentId
    ]);
    
    res.json(result);
  } catch (error) {
    console.error('获取学习行为分析失败:', error);
    res.status(500).json({
      success: false,
      message: '服务器错误',
      error: error.message
    });
  }
});

module.exports = router;
