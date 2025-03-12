/**
 * 用户个人信息相关路由
 */
const express = require('express');
const router = express.Router();
const { executePythonScript } = require('../services/python');

/**
 * 保存用户个人信息
 */
router.post('/save', async (req, res) => {
    try {
        const { email, studentId, className, major, name } = req.body;
        
        // 打印更详细的日志
        console.log('保存个人信息请求:', { email, studentId, className, major, name });
        
        // 参数验证
        if (!email) {
            return res.status(400).json({
                success: false,
                message: '邮箱不能为空'
            });
        }
        
        const result = await executePythonScript('profile_operations.py', [
            'save_profile',
            email,
            studentId || '',
            className || '',
            major || '',
            name || ''
        ]);
        
        console.log('Python脚本返回结果:', result);
        res.json(result);
    } catch (error) {
        console.error('保存个人信息失败，详细错误:', error);
        res.status(500).json({
            success: false,
            message: '服务器错误，保存个人信息失败'
        });
    }
});

/**
 * 获取用户个人信息
 */
router.get('/:email', async (req, res) => {
    try {
        const email = req.params.email;
        
        if (!email) {
            return res.status(400).json({
                success: false,
                message: '邮箱不能为空'
            });
        }
        
        const result = await executePythonScript('profile_operations.py', [
            'get_profile',
            email
        ]);
        
        res.json(result);
    } catch (error) {
        console.error('获取个人信息失败:', error);
        res.status(500).json({
            success: false,
            message: '服务器错误，获取个人信息失败'
        });
    }
});

module.exports = router;