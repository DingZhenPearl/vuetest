/**
 * 学生编程数据处理路由
 */
const express = require('express');
const router = express.Router();
const codingService = require('../services/coding');
// 引入C++代码验证服务
const { compileAndRunCpp, validateCppCode } = require('../services/cppRuntime');

/**
 * 提交编程数据
 * 接收学生编程行为数据并存储到数据库
 */
router.post('/submit', async (req, res) => {
  try {
    console.log('收到编程数据提交请求:', JSON.stringify(req.body, null, 2));

    const {
      student_class,
      student_id,
      problem_id,
      problem_title,
      code_content,
      submit_result,
      execution_errors,
      first_view_time,
      submission_time,
      coding_time
    } = req.body;

    // 数据验证
    if (!student_id || !problem_id || !code_content) {
      console.error('缺少必要参数:', { student_id, problem_id, code_content });
      return res.status(400).json({
        success: false,
        message: '缺少必要参数'
      });
    }

    // 确保所有必要字段都存在
    const submissionData = {
      student_class: student_class || '',
      student_id,
      problem_id,
      problem_title: problem_title || '',
      code_content,
      submit_result,
      execution_errors,
      first_view_time: first_view_time || null,
      submission_time: submission_time || new Date().toISOString(),
      coding_time: coding_time || 0
    };

    console.log('处理后的提交数据:', submissionData);

    // 调用服务处理数据
    const result = await codingService.submitCodingData(submissionData);
    console.log('数据处理结果:', result);

    res.json(result);
  } catch (error) {
    console.error('提交编程数据失败:', error);
    res.status(500).json({
      success: false,
      message: '服务器错误',
      error: error.message
    });
  }
});

/**
 * 获取学生的编程统计数据
 */
router.get('/stats/:studentId', async (req, res) => {
  try {
    const { studentId } = req.params;
    const result = await codingService.getStudentCodingStats(studentId);
    res.json(result);
  } catch (error) {
    console.error('获取编程统计数据失败:', error);
    res.status(500).json({
      success: false,
      message: '服务器错误',
      error: error.message
    });
  }
});

/**
 * 获取班级的编程统计数据
 */
router.get('/class/:className', async (req, res) => {
  try {
    const { className } = req.params;
    const result = await codingService.getClassCodingStats(className);
    res.json(result);
  } catch (error) {
    console.error('获取班级编程统计数据失败:', error);
    res.status(500).json({
      success: false,
      message: '服务器错误',
      error: error.message
    });
  }
});

/**
 * 获取特定题目的提交统计
 */
router.get('/problem/:problemId', async (req, res) => {
  try {
    const { problemId } = req.params;
    const result = await codingService.getProblemStats(problemId);
    res.json(result);
  } catch (error) {
    console.error('获取题目统计数据失败:', error);
    res.status(500).json({
      success: false,
      message: '服务器错误',
      error: error.message
    });
  }
});

/**
 * 运行C++代码
 */
router.post('/run-cpp', async (req, res) => {
  try {
    const { code, input } = req.body;
    
    if (!code) {
      return res.status(400).json({
        success: false,
        message: '代码不能为空'
      });
    }
    
    const result = await compileAndRunCpp(code, input || '');
    res.json(result);
  } catch (error) {
    console.error('运行C++代码失败:', error);
    res.status(500).json({
      success: false,
      message: '服务器错误',
      error: error.message
    });
  }
});

/**
 * 使用样例验证C++代码
 */
router.post('/verify-cpp', async (req, res) => {
  try {
    const { code, input, expectedOutput } = req.body;
    
    if (!code || !expectedOutput) {
      return res.status(400).json({
        success: false,
        message: '代码和预期输出不能为空'
      });
    }
    
    const result = await validateCppCode(code, input || '', expectedOutput);
    res.json(result);
  } catch (error) {
    console.error('验证C++代码失败:', error);
    res.status(500).json({
      success: false,
      message: '服务器错误',
      error: error.message
    });
  }
});

module.exports = router;