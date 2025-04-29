/**
 * 渐进式编程辅导AI服务
 * 提供流式AI输出功能
 */
const OpenAI = require('openai');

// 创建OpenAI客户端函数
function createOpenAIClient(apiKey, baseURL) {
    // 检查是否使用本地ollama模型
    if (apiKey === 'ollama' || (!apiKey && !baseURL)) {
        // 默认使用本地ollama配置
        return new OpenAI({
            apiKey: 'ollama',
            baseURL: 'http://localhost:11434/v1/'
        });
    }

    // 使用提供的配置或默认配置
    return new OpenAI({
        apiKey: apiKey || 'sk-jvemhtlzzpiaawbmveoqgzohziojbngggfrtvhtxxszyxzzy',
        baseURL: baseURL || 'https://api.siliconflow.cn/v1/'
    });
}

/**
 * 生成流式AI回复
 * @param {Object} req - Express请求对象
 * @param {Object} res - Express响应对象
 */
async function generateStreamingGuidance(req, res) {
    try {
        const { prompt, systemRole, temperature = 0.3, maxTokens = 3000, apiKey, apiEndpoint, modelName } = req.body;

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

        // 创建OpenAI客户端
        const openai = createOpenAIClient(
            apiKey,
            apiEndpoint ? new URL(apiEndpoint).origin : undefined
        );

        // 确定使用的模型名称
        let modelToUse = modelName || "Qwen/Qwen2.5-Coder-7B-Instruct";

        // 如果是使用ollama，则使用qwen3:8b模型
        if (apiKey === 'ollama' || (!apiKey && !apiEndpoint)) {
            modelToUse = "qwen3:8b";
        }

        console.log(`使用模型: ${modelToUse}, API端点: ${apiKey === 'ollama' ? 'ollama本地' : apiEndpoint || '默认'}`);

        // 创建流式请求
        const stream = await openai.chat.completions.create({
            model: modelToUse,
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
        const { prompt, systemRole, temperature = 0.3, maxTokens = 3000, apiKey, apiEndpoint, modelName } = req.body;

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

        // 创建OpenAI客户端
        const openai = createOpenAIClient(
            apiKey,
            apiEndpoint ? new URL(apiEndpoint).origin : undefined
        );

        // 确定使用的模型名称
        let modelToUse = modelName || "Qwen/Qwen2.5-Coder-7B-Instruct";

        // 如果是使用ollama，则使用qwen3:8b模型
        if (apiKey === 'ollama' || (!apiKey && !apiEndpoint)) {
            modelToUse = "qwen3:8b";
        }

        console.log(`使用模型: ${modelToUse}, API端点: ${apiKey === 'ollama' ? 'ollama本地' : apiEndpoint || '默认'}`);

        // 创建非流式请求
        const completion = await openai.chat.completions.create({
            model: modelToUse,
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
