/**
 * 渐进式编程辅导AI服务
 * 提供流式AI输出功能
 */
const OpenAI = require('openai');

// 初始化OpenAI客户端
const openai = new OpenAI({
    apiKey: 'sk-jvemhtlzzpiaawbmveoqgzohziojbngggfrtvhtxxszyxzzy',
    baseURL: 'https://api.siliconflow.cn/v1/'
});

/**
 * 生成流式AI回复
 * @param {Object} req - Express请求对象
 * @param {Object} res - Express响应对象
 */
async function generateStreamingGuidance(req, res) {
    try {
        const { prompt, systemRole, temperature = 0.3, maxTokens = 3000 } = req.body;
        
        if (!prompt) {
            return res.status(400).json({ error: '缺少必要的prompt参数' });
        }
        
        // 构建消息数组
        const messages = [
            { 
                role: "system", 
                content: systemRole || "你是一个编程辅导助手，提供清晰、准确的编程指导。" 
            },
            { role: "user", content: prompt }
        ];
        
        // 设置响应头以支持流式传输
        res.setHeader('Content-Type', 'text/event-stream');
        res.setHeader('Cache-Control', 'no-cache');
        res.setHeader('Connection', 'keep-alive');
        
        // 创建流式请求
        const stream = await openai.chat.completions.create({
            model: "Qwen/Qwen2.5-Coder-7B-Instruct",
            messages: messages,
            temperature: parseFloat(temperature),
            max_tokens: parseInt(maxTokens),
            stream: true,
        });
        
        let responseText = '';
        
        // 处理流式响应
        for await (const part of stream) {
            const content = part.choices[0]?.delta?.content || '';
            if (content) {
                responseText += content;
                // 发送新的内容片段到客户端
                res.write(`data: ${JSON.stringify({ token: content })}\n\n`);
            }
        }
        
        // 流结束，发送完成信号
        res.write(`data: ${JSON.stringify({ done: true, fullResponse: responseText })}\n\n`);
        res.end();
        
    } catch (error) {
        console.error('流式AI服务错误:', error);
        // 尝试发送错误响应
        try {
            res.write(`data: ${JSON.stringify({ error: error.message || '服务器错误' })}\n\n`);
            res.end();
        } catch (sendError) {
            console.error('发送错误响应失败:', sendError);
        }
    }
}

/**
 * 生成非流式AI回复（备用方法）
 * @param {Object} req - Express请求对象
 * @param {Object} res - Express响应对象
 */
async function generateGuidance(req, res) {
    try {
        const { prompt, systemRole, temperature = 0.3, maxTokens = 3000 } = req.body;
        
        if (!prompt) {
            return res.status(400).json({ error: '缺少必要的prompt参数' });
        }
        
        // 构建消息数组
        const messages = [
            { 
                role: "system", 
                content: systemRole || "你是一个编程辅导助手，提供清晰、准确的编程指导。" 
            },
            { role: "user", content: prompt }
        ];
        
        // 创建非流式请求
        const completion = await openai.chat.completions.create({
            model: "Qwen/Qwen2.5-Coder-7B-Instruct",
            messages: messages,
            temperature: parseFloat(temperature),
            max_tokens: parseInt(maxTokens)
        });
        
        // 返回完整响应
        res.json({ 
            success: true, 
            content: completion.choices[0].message.content 
        });
        
    } catch (error) {
        console.error('AI服务错误:', error);
        res.status(500).json({ 
            success: false, 
            error: error.message || '服务器错误' 
        });
    }
}

module.exports = {
    generateStreamingGuidance,
    generateGuidance
};
