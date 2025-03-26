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
        const result = await executePythonScript('teaching_stats.py', ['get_class_list']);
        res.json(result);
    } catch (error) {
        console.error('获取班级列表失败:', error);
        res.status(500).json({
            success: false,
            message: '服务器错误',
            error: error.message
        });
    }
});

module.exports = router;
