/**
 * 问答系统相关路由
 */
const express = require('express');
const router = express.Router();
const { executePythonScript } = require('../services/python');

/**
 * 学生提交问题
 */
router.post('/submit', async (req, res) => {
    try {
        const { email, title, content } = req.body;
        const result = await executePythonScript('qa_operations.py', [
            'submit_question',
            email,
            title,
            content
        ]);
        res.json(result);
    } catch (error) {
        console.error('提交问题失败:', error);
        res.status(500).json({ success: false, message: '服务器错误' });
    }
});

/**
 * 获取特定学生的问题列表
 */
router.get('/student/:email', async (req, res) => {
    try {
        const email = req.params.email;
        const result = await executePythonScript('qa_operations.py', [
            'get_student_questions',
            email
        ]);
        res.json(result);
    } catch (error) {
        console.error('获取问题列表失败:', error);
        res.status(500).json({ success: false, message: '服务器错误' });
    }
});

/**
 * 获取所有学生问题（供教师使用）
 */
router.get('/all', async (req, res) => {
    try {
        const result = await executePythonScript('qa_operations.py', ['get_all_questions']);
        res.json(result);
    } catch (error) {
        console.error('获取所有问题失败:', error);
        res.status(500).json({ success: false, message: '服务器错误' });
    }
});

/**
 * 教师提交回答
 */
router.post('/answer', async (req, res) => {
    try {
        const { questionId, answer, teacherEmail } = req.body;
        const result = await executePythonScript('qa_operations.py', [
            'submit_answer',
            questionId.toString(),
            answer,
            teacherEmail // 传递教师邮箱
        ]);
        res.json(result);
    } catch (error) {
        console.error('提交回答失败:', error);
        res.status(500).json({ success: false, message: '服务器错误' });
    }
});

/**
 * 删除问题
 */
router.delete('/:id', async (req, res) => {
    try {
        const questionId = req.params.id;
        const result = await executePythonScript('qa_operations.py', [
            'delete_question',
            questionId
        ]);
        res.json(result);
    } catch (error) {
        console.error('删除问题失败:', error);
        res.status(500).json({ success: false, message: '服务器错误' });
    }
});

/**
 * 更新问题
 */
router.put('/:id', async (req, res) => {
    try {
        const questionId = req.params.id;
        const { title, content } = req.body;
        const result = await executePythonScript('qa_operations.py', [
            'update_question',
            questionId,
            title,
            content
        ]);
        res.json(result);
    } catch (error) {
        console.error('更新问题失败:', error);
        res.status(500).json({ success: false, message: '服务器错误' });
    }
});

/**
 * 学生提交追问
 */
router.post('/follow-up', async (req, res) => {
    try {
        const { questionId, content, email } = req.body;
        const result = await executePythonScript('qa_operations.py', [
            'submit_follow_up',
            questionId.toString(),
            content,
            email,        // 传递学生邮箱
            'false'       // 标记为学生回复
        ]);
        res.json(result);
    } catch (error) {
        res.status(500).json({ success: false, message: '服务器错误' });
    }
});

/**
 * 教师回复追问
 */
router.post('/follow-up-answer', async (req, res) => {
    try {
        const { questionId, content, teacherEmail } = req.body;
        const result = await executePythonScript('qa_operations.py', [
            'submit_follow_up',
            questionId.toString(),
            content,
            teacherEmail,
            'true'
        ]);
        res.json(result);
    } catch (error) {
        res.status(500).json({ success: false, message: '服务器错误' });
    }
});

/**
 * 删除回复（追问/追答）
 */
router.delete('/follow-up/:questionId/:index', async (req, res) => {
    try {
        const { questionId, index } = req.params;
        const result = await executePythonScript('qa_operations.py', [
            'delete_follow_up',
            questionId,
            index
        ]);
        res.json(result);
    } catch (error) {
        console.error('删除回复失败:', error);
        res.status(500).json({ success: false, message: '服务器错误' });
    }
});

/**
 * 删除教师回答
 */
router.delete('/answer/:id', async (req, res) => {
    try {
        const questionId = req.params.id;
        const result = await executePythonScript('qa_operations.py', [
            'delete_answer',
            questionId
        ]);
        res.json(result);
    } catch (error) {
        console.error('删除回答失败:', error);
        res.status(500).json({ success: false, message: '服务器错误' });
    }
});

module.exports = router;