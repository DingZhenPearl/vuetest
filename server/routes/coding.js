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
    const {
      studentClass,
      studentId,
      problemId,
      problemTitle,
      codeContent,
      submitResult,
      executionErrors = null,
      firstViewTime,
      submissionTime
    } = req.body;

    // 数据验证
    if (!studentId || !problemId || !codeContent) {
      return res.status(400).json({
        success: false,
        message: '缺少必要参数'
      });
    }

    // 调用服务处理数据
    const result = await codingService.submitCodingData({
      student_class: studentClass,
      student_id: studentId,
      problem_id: problemId,
      problem_title: problemTitle,
      code_content: codeContent,
      submit_result: submitResult ? 'success' : 'failed',
      execution_errors: executionErrors,
      first_view_time: firstViewTime,
      submission_time: submissionTime
    });

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