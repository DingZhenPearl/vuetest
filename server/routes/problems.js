/**
 * 题目管理相关路由
 */
const express = require('express');
const router = express.Router();
// 使用统一的 Python 脚本执行服务
const { executePythonScript } = require('../services/python');
// 引入C++代码验证服务
const { validateCppCode } = require('../services/cppRuntime');

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
    const { email, title, difficulty, content, inputExample, outputExample } = req.body;
    const result = await executePythonScript('problem_operations.py', [
      'submit_problem',
      email,
      title,
      difficulty,
      content,
      inputExample || '',  // 处理可能为空的情况
      outputExample || ''  // 处理可能为空的情况
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
    const { title, difficulty, content, inputExample, outputExample } = req.body;
    const result = await executePythonScript('problem_operations.py', [
      'update_problem',
      problemId,
      title,
      difficulty,
      content,
      inputExample || '',  // 处理可能为空的情况
      outputExample || ''  // 处理可能为空的情况
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

/**
 * 获取题目的答题情况
 */
router.get('/:id/submissions', async (req, res) => {
  try {
    const problemId = req.params.id;
    const result = await executePythonScript('problem_operations.py', [
      'get_problem_submissions_stats',
      problemId
    ]);
    res.json(result);
  } catch (error) {
    console.error('获取答题情况失败:', error);
    res.status(500).json({
      success: false,
      message: '服务器错误',
      error: error.message
    });
  }
});

/**
 * 验证C++代码
 */
router.post('/validate-cpp', async (req, res) => {
  try {
    const { code, problemId } = req.body;
    
    if (!code || !problemId) {
      return res.status(400).json({
        success: false,
        message: '缺少必要参数'
      });
    }
    
    // 获取题目样例信息
    const problemResult = await executePythonScript('problem_operations.py', [
      'get_problem_detail',
      problemId
    ]);
    
    // 确保题目详情获取成功
    if (!problemResult.success || !problemResult.problem) {
      return res.status(404).json({
        success: false,
        message: '题目不存在或无法获取题目详情'
      });
    }
    
    const { input_example, output_example } = problemResult.problem;
    
    // 验证代码
    const validationResult = await validateCppCode(code, input_example, output_example);
    
    // 返回验证结果
    res.json(validationResult);
  } catch (error) {
    console.error('C++代码验证失败:', error);
    res.status(500).json({
      success: false,
      message: '服务器错误',
      error: error.message
    });
  }
});

module.exports = router;