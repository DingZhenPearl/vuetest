/**
 * 用户个人信息相关路由
 */
const express = require('express');
const router = express.Router();
const { executePythonScript } = require('../services/python');

/**
 * 初始化数据表
 */
router.post('/init', async (req, res) => {
  try {
    const result = await executePythonScript('profile_operations.py', ['create_tables']);
    res.json(result);
  } catch (error) {
    console.error('初始化个人信息表失败:', error);
    res.status(500).json({
      success: false,
      message: '服务器错误',
      error: error.message
    });
  }
});

/**
 * 保存学生个人信息
 */
router.post('/student', async (req, res) => {
  try {
    const { email, student_id, class_name, major, name } = req.body;
    
    if (!email) {
      return res.status(400).json({
        success: false,
        message: '缺少必要参数: email'
      });
    }
    
    const result = await executePythonScript('profile_operations.py', [
      'save_student_profile',
      JSON.stringify({
        email,
        student_id: student_id || '',
        class_name: class_name || '',
        major: major || '',
        name: name || ''
      })
    ]);
    
    res.json(result);
  } catch (error) {
    console.error('保存学生个人信息失败:', error);
    res.status(500).json({
      success: false,
      message: '服务器错误',
      error: error.message
    });
  }
});

/**
 * 获取学生个人信息
 */
router.get('/student/:email', async (req, res) => {
  try {
    const { email } = req.params;
    
    if (!email) {
      return res.status(400).json({
        success: false,
        message: '缺少必要参数: email'
      });
    }
    
    const result = await executePythonScript('profile_operations.py', [
      'get_student_profile',
      email
    ]);
    
    res.json(result);
  } catch (error) {
    console.error('获取学生个人信息失败:', error);
    res.status(500).json({
      success: false,
      message: '服务器错误',
      error: error.message
    });
  }
});

/**
 * 获取班级所有学生
 */
router.get('/class-students/:className', async (req, res) => {
  try {
    const { className } = req.params;
    
    if (!className) {
      return res.status(400).json({
        success: false,
        message: '缺少必要参数: className'
      });
    }
    
    const result = await executePythonScript('profile_operations.py', [
      'get_class_students',
      className
    ]);
    
    res.json(result);
  } catch (error) {
    console.error('获取班级学生失败:', error);
    res.status(500).json({
      success: false,
      message: '服务器错误',
      error: error.message
    });
  }
});

/**
 * 获取班级所有学生（替代方法）
 */
router.get('/students-by-class/:className', async (req, res) => {
  try {
    const { className } = req.params;
    
    if (!className) {
      return res.status(400).json({
        success: false,
        message: '缺少必要参数: className'
      });
    }
    
    // 尝试从编程提交记录中获取学生数据
    const result = await executePythonScript('coding_data.py', [
      'get_students_by_class',
      className
    ]);
    
    res.json(result);
  } catch (error) {
    console.error('获取班级学生失败:', error);
    res.status(500).json({
      success: false,
      message: '服务器错误',
      error: error.message
    });
  }
});

module.exports = router;
