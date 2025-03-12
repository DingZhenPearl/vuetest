/**
 * AI聊天服务配置
 */
const OpenAI = require('openai');

// 初始化OpenAI客户端
const openai = new OpenAI({
    apiKey: 'ipzotlGevNqQsafvWSXi:cooExiNRkHtQtHkkIqNk',
    baseURL: 'https://spark-api-open.xf-yun.com/v1'
});

/**
 * 生成AI回复
 * @param {Array} messages - 消息历史数组
 * @returns {Promise<string>} AI的回复内容
 */
async function generateAIResponse(messages) {
    try {
        const completion = await openai.chat.completions.create({
            model: "lite",
            messages: messages,
        });

        return completion.choices[0].message.content;
    } catch (error) {
        console.error('AI服务错误:', error);
        throw new Error('AI服务调用失败');
    }
}

module.exports = {
    openai,
    generateAIResponse
};