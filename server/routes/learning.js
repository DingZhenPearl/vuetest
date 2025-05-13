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

/**
 * 获取学生活动记录
 */
router.get('/student-activities/:studentId', async (req, res) => {
  try {
    const { studentId } = req.params;

    if (!studentId) {
      return res.status(400).json({
        success: false,
        message: '缺少学生ID参数'
      });
    }

    console.log(`正在获取学生活动记录，学生ID: ${studentId}`);

    try {
      // 调用Python脚本获取学生活动记录
      const result = await executePythonScript('student_activity.py', [
        'get_activities',
        studentId
      ]);

      res.json(result);
    } catch (scriptError) {
      console.error('获取学生活动记录失败:', scriptError);
      res.status(500).json({
        success: false,
        message: '获取学生活动记录失败',
        error: scriptError.message
      });
    }
  } catch (error) {
    console.error('获取学生活动记录失败:', error);
    res.status(500).json({
      success: false,
      message: '服务器错误',
      error: error.message
    });
  }
});

/**
 * 获取学生学习进度
 */
router.get('/student-progress/:studentId', async (req, res) => {
  try {
    const { studentId } = req.params;

    if (!studentId) {
      return res.status(400).json({
        success: false,
        message: '缺少学生ID参数'
      });
    }

    console.log(`正在获取学生学习进度，学生ID: ${studentId}`);

    try {
      // 调用Python脚本获取学生学习进度
      const result = await executePythonScript('student_activity.py', [
        'get_progress',
        studentId
      ]);

      res.json(result);
    } catch (scriptError) {
      console.error('获取学生学习进度失败:', scriptError);
      res.status(500).json({
        success: false,
        message: '获取学生学习进度失败',
        error: scriptError.message
      });
    }
  } catch (error) {
    console.error('获取学生学习进度失败:', error);
    res.status(500).json({
      success: false,
      message: '服务器错误',
      error: error.message
    });
  }
});

/**
 * 保存学生小节学习进度
 */
router.post('/section-progress/save/:studentId/:sectionId', async (req, res) => {
  try {
    const { studentId, sectionId } = req.params;

    if (!studentId || !sectionId) {
      return res.status(400).json({
        success: false,
        message: '缺少必要参数'
      });
    }

    console.log(`正在保存学生小节学习进度，学生ID: ${studentId}, 小节ID: ${sectionId}`);

    try {
      // 调用Python脚本保存学生小节学习进度
      const result = await executePythonScript('section_progress_api.py', [
        'save_progress',
        studentId,
        sectionId
      ]);

      res.json(result);
    } catch (scriptError) {
      console.error('保存学生小节学习进度失败:', scriptError);
      res.status(500).json({
        success: false,
        message: '保存学生小节学习进度失败',
        error: scriptError.message
      });
    }
  } catch (error) {
    console.error('保存学生小节学习进度失败:', error);
    res.status(500).json({
      success: false,
      message: '服务器错误',
      error: error.message
    });
  }
});

/**
 * 获取学生已完成的小节
 */
router.get('/section-progress/completed/:studentId', async (req, res) => {
  try {
    const { studentId } = req.params;

    if (!studentId) {
      return res.status(400).json({
        success: false,
        message: '缺少学生ID参数'
      });
    }

    console.log(`正在获取学生已完成的小节，学生ID: ${studentId}`);

    try {
      // 调用Python脚本获取学生已完成的小节
      const result = await executePythonScript('section_progress_api.py', [
        'get_completed',
        studentId
      ]);

      res.json(result);
    } catch (scriptError) {
      console.error('获取学生已完成的小节失败:', scriptError);
      res.status(500).json({
        success: false,
        message: '获取学生已完成的小节失败',
        error: scriptError.message
      });
    }
  } catch (error) {
    console.error('获取学生已完成的小节失败:', error);
    res.status(500).json({
      success: false,
      message: '服务器错误',
      error: error.message
    });
  }
});

/**
 * 从localStorage导入学习进度
 */
router.post('/section-progress/import/:studentId', async (req, res) => {
  try {
    const { studentId } = req.params;
    const { section_ids } = req.body;

    if (!studentId || !section_ids || !Array.isArray(section_ids)) {
      return res.status(400).json({
        success: false,
        message: '缺少必要参数或参数格式错误'
      });
    }

    console.log(`正在导入学生学习进度，学生ID: ${studentId}, 小节数: ${section_ids.length}`);

    try {
      // 调用Python脚本导入学生学习进度
      const result = await executePythonScript('section_progress_api.py', [
        'import',
        studentId,
        JSON.stringify(section_ids)
      ]);

      res.json(result);
    } catch (scriptError) {
      console.error('导入学生学习进度失败:', scriptError);
      res.status(500).json({
        success: false,
        message: '导入学生学习进度失败',
        error: scriptError.message
      });
    }
  } catch (error) {
    console.error('导入学生学习进度失败:', error);
    res.status(500).json({
      success: false,
      message: '服务器错误',
      error: error.message
    });
  }
});

module.exports = router;
