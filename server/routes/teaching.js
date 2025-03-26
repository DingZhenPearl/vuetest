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

module.exports = router;
