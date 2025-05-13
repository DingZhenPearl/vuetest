const express = require('express');
const router = express.Router();
const { executePythonScript } = require('../services/python');

router.get('/learning-patterns/:className?', async (req, res) => {
    try {
        const { className } = req.params;
        const args = ['analyze_learning_patterns'];
        if (className) args.push(className);

        const result = await executePythonScript('teaching_stats.py', args);
        res.json(result);
    } catch (error) {
        console.error('分析学习模式失败:', error);
        res.status(500).json({
            success: false,
            message: '服务器错误',
            error: error.message
        });
    }
});

router.get('/class-list', async (req, res) => {
    try {
        console.log('正在获取班级列表...');
        const result = await executePythonScript('teaching_stats.py', ['get_class_list']);
        console.log('班级列表结果:', result);

        // 确保返回一个数组
        if (result.success && !result.classes) {
            result.classes = [];
        }

        res.json(result);
    } catch (error) {
        console.error('获取班级列表失败:', error);
        res.status(500).json({
            success: false,
            message: '服务器错误',
            error: error.message,
            classes: [] // 确保即使失败也返回空数组
        });
    }
});

/**
 * 获取教学统计数据
 */
router.get('/stats', async (req, res) => {
    try {
        console.log('正在获取教学统计数据...');
        const result = await executePythonScript('teaching_stats_api.py', ['get_stats']);
        res.json(result);
    } catch (error) {
        console.error('获取教学统计数据失败:', error);
        res.status(500).json({
            success: false,
            message: '服务器错误',
            error: error.message
        });
    }
});

/**
 * 获取活动趋势数据
 */
router.get('/activity-trend', async (req, res) => {
    try {
        const { range } = req.query;
        console.log(`正在获取活动趋势数据，时间范围: ${range || 'week'}...`);
        const result = await executePythonScript('teaching_stats_api.py', ['get_activity_trend', range || 'week']);
        res.json(result);
    } catch (error) {
        console.error('获取活动趋势数据失败:', error);
        res.status(500).json({
            success: false,
            message: '服务器错误',
            error: error.message
        });
    }
});

/**
 * 获取题目完成情况数据
 */
router.get('/problem-completion', async (req, res) => {
    try {
        console.log('正在获取题目完成情况数据...');
        const result = await executePythonScript('teaching_stats_api.py', ['get_problem_completion']);
        res.json(result);
    } catch (error) {
        console.error('获取题目完成情况数据失败:', error);
        res.status(500).json({
            success: false,
            message: '服务器错误',
            error: error.message
        });
    }
});

/**
 * 获取待处理事项
 */
router.get('/todos', async (req, res) => {
    try {
        console.log('正在获取待处理事项...');
        const result = await executePythonScript('teaching_stats_api.py', ['get_todos']);
        res.json(result);
    } catch (error) {
        console.error('获取待处理事项失败:', error);
        res.status(500).json({
            success: false,
            message: '服务器错误',
            error: error.message
        });
    }
});

module.exports = router;
