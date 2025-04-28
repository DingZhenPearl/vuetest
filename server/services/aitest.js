/**
 * AI聊天服务配置
 */
const OpenAI = require('openai');

// 初始化OpenAI客户端
const openai = new OpenAI({
    apiKey: 'sk-jvemhtlzzpiaawbmveoqgzohziojbngggfrtvhtxxszyxzzy',
    baseURL: 'https://api.siliconflow.cn/v1/'
});

/**
 * 生成AI回复
 * @param {Array} messages - 消息历史数组
 * @returns {Promise<string>} AI的回复内容
 */
async function generateAIResponse(messages) {
    try {
        const completion = await openai.chat.completions.create({
            model: "Qwen/Qwen2.5-Coder-7B-Instruct",
            messages: messages,
        });

        return completion.choices[0].message.content;
    } catch (error) {
        console.error('AI服务错误:', error);
        throw new Error('AI服务调用失败');
    }
}

/**
 * 生成流式AI回复
 * @param {Array} messages - 消息历史数组
 * @param {Function} onToken - 每次收到新token时的回调
 * @param {Function} onComplete - 完成时的回调
 */
async function generateStreamingResponse(messages, onToken, onComplete) {
    try {
        const stream = await openai.chat.completions.create({
            model: "Qwen/Qwen2.5-Coder-7B-Instruct",
            messages: messages,
            stream: true,
        });

        let responseText = '';
        
        // 处理流式响应
        for await (const part of stream) {
            const content = part.choices[0]?.delta?.content || '';
            if (content) {
                responseText += content;
                onToken(content);
            }
        }
        
        // 流结束
        onComplete(responseText);
    } catch (error) {
        console.error('AI流式服务错误:', error);
        throw new Error('AI流式服务调用失败');
    }
}

module.exports = {
    openai,
    generateAIResponse,
    generateStreamingResponse
};