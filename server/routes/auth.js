/**
 * 用户认证相关路由
 */
const express = require('express');
const router = express.Router();
const { executePythonScript } = require('../services/python');

/**
 * 用户登录
 * 接收用户类型、邮箱和密码，验证用户身份
 */
router.post('/login', async (req, res) => {
    try {
        const { user_type, email, password } = req.body;
        
        if (!user_type) {
            return res.status(400).json({ success: false, message: '缺少用户类型' });
        }

        const result = await executePythonScript('db_operations.py', [
            'login',
            user_type,
            email,
            password
        ]);

        if (result.success) {
            res.json({ success: true, message: '登录成功' });
        } else {
            res.status(401).json({ success: false, message: result.message || '邮箱或密码错误' });
        }
    } catch (error) {
        console.error('登录错误详情:', error);
        res.status(500).json({ success: false, message: `服务器错误: ${error.message}` });
    }
});

/**
 * 用户注册
 * 接收用户类型、邮箱和密码，创建新用户
 */
router.post('/register', async (req, res) => {
    try {
        const { user_type, email, password } = req.body;

        const result = await executePythonScript('db_operations.py', [
            'register',
            user_type,
            email,
            password
        ]);

        if (result.success) {
            res.json({ success: true, message: '注册成功' });
        } else {
            res.status(400).json({ success: false, message: result.message || '注册失败' });
        }
    } catch (error) {
        console.error('注册错误:', error);
        res.status(500).json({ success: false, message: '服务器错误' });
    }
});

module.exports = router;