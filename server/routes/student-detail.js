/**
 * 学生详情相关路由
 */
const express = require('express');
const router = express.Router();
const { executePythonScript } = require('../services/python');
const aiAnalysisService = require('../services/ai-analysis');

/**
 * 获取学生详细信息
 * GET /api/teaching/student-detail/:studentId
 */
router.get('/:studentId', async (req, res) => {
  try {
    const { studentId } = req.params;

    if (!studentId) {
      return res.status(400).json({
        success: false,
        message: '缺少学生ID参数'
      });
    }

    console.log(`正在获取学生详细信息，学生ID: ${studentId}`);

    // 调用Python脚本获取学生详细数据
    const result = await executePythonScript('student_detail.py', [
      'get_student_detail',
      studentId
    ]);

    if (!result.success) {
      return res.status(500).json({
        success: false,
        message: result.message || '获取学生详细信息失败',
        error: result.error || '未知错误'
      });
    }

    res.json(result);
  } catch (error) {
    console.error('获取学生详细信息失败:', error);
    res.status(500).json({
      success: false,
      message: '服务器错误',
      error: error.message
    });
  }
});

/**
 * 获取学生AI分析
 * POST /api/teaching/student-detail/ai-analysis
 *
 * 请求体:
 * {
 *   studentId: String  // 学生ID
 * }
 */
router.post('/ai-analysis', async (req, res) => {
  try {
    const { studentId } = req.body;

    if (!studentId) {
      return res.status(400).json({
        success: false,
        message: '缺少学生ID参数'
      });
    }

    console.log(`正在进行学生AI分析，学生ID: ${studentId}`);

    // 1. 获取学生详细数据
    const studentData = await executePythonScript('student_detail.py', [
      'get_student_detail',
      studentId
    ]);

    if (!studentData.success) {
      return res.status(500).json({
        success: false,
        message: studentData.message || '获取学生详细信息失败',
        error: studentData.error || '未知错误'
      });
    }

    // 2. 使用AI分析服务分析学生数据
    const analysis = await aiAnalysisService.analyzeStudentData(studentData.data);

    // 3. 返回分析结果
    res.json({
      success: true,
      analysis
    });
  } catch (error) {
    console.error('学生AI分析失败:', error);
    res.status(500).json({
      success: false,
      message: '服务器错误',
      error: error.message
    });
  }
});

module.exports = router;
