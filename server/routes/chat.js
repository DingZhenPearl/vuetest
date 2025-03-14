/**
 * 聊天相关路由
 */
const express = require('express');
const router = express.Router();
const { executePythonScript } = require('../services/python');
// 因为需要流式响应，添加一个新的方法导入
const { generateAIResponse, generateStreamingResponse } = require('../services/ai');

/**
 * 处理聊天消息
 * 接收用户消息，调用AI模型生成回复（流式响应）
 */
router.post('/message', async (req, res) => {
    try {
        const { message, messageHistory } = req.body;
        
        // 构建完整的对话历史
        const messages = messageHistory.map(msg => ({
            role: msg.sender === 'user' ? 'user' : 'assistant',
            content: msg.content
        }));
        
        // 添加当前用户消息
        messages.push({ role: "user", content: message });
        
        // 设置响应头以支持流式传输
        res.setHeader('Content-Type', 'text/event-stream');
        res.setHeader('Cache-Control', 'no-cache');
        res.setHeader('Connection', 'keep-alive');
        
        // 使用流式生成回复
        await generateStreamingResponse(messages, (token) => {
            // 每次有新token时发送到前端
            res.write(`data: ${JSON.stringify({ token })}\n\n`);
        }, () => {
            // 完成时发送结束信号
            res.write(`data: ${JSON.stringify({ done: true })}\n\n`);
            res.end();
        });
    } catch (error) {
        console.error('OpenAI API调用失败:', error);
        res.write(`data: ${JSON.stringify({ error: '服务器错误' })}\n\n`);
        res.end();
    }
});

/**
 * 获取用户聊天历史记录
 */
router.post('/history', async (req, res) => {
    try {
        const { email } = req.body;
        const result = await executePythonScript('chat_history.py', ['get_history', email]);
        
        // 确保我们返回的是解析后的JSON数据，而不是字符串
        if (typeof result === 'string') {
            try {
                res.json(JSON.parse(result));
            } catch (parseError) {
                console.error('解析历史记录JSON失败:', parseError);
                res.json([]);
            }
        } else {
            res.json(result);
        }
    } catch (error) {
        console.error('获取聊天历史失败:', error);
        res.status(500).json({ success: false, message: '服务器错误' });
    }
});

/**
 * 保存新的聊天记录
 */
router.post('/save', async (req, res) => {
    try {
        const { email, messages } = req.body;
        const result = await executePythonScript('chat_history.py', [
            'save_chat',
            email,
            JSON.stringify(messages)
        ]);
        res.json(result);
    } catch (error) {
        console.error('保存聊天记录失败:', error);
        res.status(500).json({ success: false, message: '服务器错误' });
    }
});

/**
 * 获取特定聊天记录详情
 */
router.get('/:id', async (req, res) => {
    try {
        const chatId = req.params.id;
        const result = await executePythonScript('chat_history.py', ['get_chat', chatId]);
        
        // 确保我们返回的是解析后的JSON数据，而不是字符串
        if (typeof result === 'string') {
            try {
                res.json(JSON.parse(result));
            } catch (parseError) {
                console.error('解析聊天记录JSON失败:', parseError);
                res.json({ success: false, message: '数据格式错误' });
            }
        } else {
            res.json(result);
        }
    } catch (error) {
        console.error('获取聊天记录失败:', error);
        res.status(500).json({ success: false, message: '服务器错误' });
    }
});

/**
 * 删除特定聊天记录
 */
router.delete('/:id', async (req, res) => {
    try {
        const chatId = req.params.id;
        const result = await executePythonScript('chat_history.py', ['delete_chat', chatId]);
        res.json(result);
    } catch (error) {
        console.error('删除聊天记录失败:', error);
        res.status(500).json({ success: false, message: '服务器错误' });
    }
});

/**
 * 更新特定聊天记录
 */
router.post('/update', async (req, res) => {
    try {
        const { chatId, messages } = req.body;
        const result = await executePythonScript('chat_history.py', [
            'update_chat',
            chatId,
            JSON.stringify(messages)
        ]);
        res.json(result);
    } catch (error) {
        console.error('更新聊天记录失败:', error);
        res.status(500).json({ success: false, message: '服务器错误' });
    }
});

module.exports = router;