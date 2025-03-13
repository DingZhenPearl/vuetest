/**
 * 题目管理相关路由
 */
const express = require('express');
const router = express.Router();
// 使用统一的 Python 脚本执行服务
const { executePythonScript } = require('../services/python');

/**
 * 获取教师的题目列表
 */
router.get('/teacher/:email', async (req, res) => {
  try {
    // 注释掉简化实现
    /*
    res.json({
      success: true,
      problems: [
        // ...
      ]
    });
    */
    
    // 取消注释完整实现
    const email = req.params.email;
    const result = await executePythonScript('problem_operations.py', [
      'get_teacher_problems',
      email
    ]);
    res.json(result);
  } catch (error) {
    console.error('获取题目列表失败:', error);
    res.status(500).json({ success: false, message: '服务器错误' });
  }
});

/**
 * 获取所有题目列表（供学生使用）
 */
router.get('/all', async (req, res) => {
  try {
    const result = await executePythonScript('problem_operations.py', [
      'get_all_problems'
    ]);
    res.json(result);
  } catch (error) {
    console.error('获取所有题目列表失败:', error);
    res.status(500).json({ success: false, message: '服务器错误' });
  }
});

/**
 * 提交新题目
 */
router.post('/submit', async (req, res) => {
  try {
    // 注释掉简化实现
    /*
    res.json({
      success: true,
      message: "题目提交成功"
    });
    */
    
    // 取消注释完整实现的代码
    const { email, title, difficulty, content } = req.body;
    const result = await executePythonScript('problem_operations.py', [
      'submit_problem',
      email,
      title,
      difficulty,
      content
    ]);
    res.json(result);
  } catch (error) {
    console.error('提交题目失败:', error);
    res.status(500).json({ success: false, message: '服务器错误' });
  }
});

/**
 * 更新题目
 */
router.put('/:id', async (req, res) => {
  try {
    // 注释掉简化实现
    /*
    res.json({
      success: true,
      message: "题目更新成功"
    });
    */
    
    // 完整实现
    const problemId = req.params.id;
    const { title, difficulty, content } = req.body;
    const result = await executePythonScript('problem_operations.py', [
      'update_problem',
      problemId,
      title,
      difficulty,
      content
    ]);
    res.json(result);
  } catch (error) {
    console.error('更新题目失败:', error);
    res.status(500).json({ success: false, message: '服务器错误' });
  }
});

/**
 * 删除题目
 */
router.delete('/:id', async (req, res) => {
  try {
    // 注释掉简化实现
    /*
    res.json({
      success: true,
      message: "题目删除成功"
    });
    */
    
    // 完整实现
    const problemId = req.params.id;
    const result = await executePythonScript('problem_operations.py', [
      'delete_problem',
      problemId
    ]);
    res.json(result);
  } catch (error) {
    console.error('删除题目失败:', error);
    res.status(500).json({ success: false, message: '服务器错误' });
  }
});

module.exports = router;