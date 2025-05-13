/**
 * AI聊天服务配置
 */
const OpenAI = require('openai');
const fs = require('fs');
const path = require('path');

// 配置文件路径
const CONFIG_PATH = path.join(__dirname, '../config/ai_config.json');

// 默认配置
let aiConfig = {
    modelType: 'api', // 'local' 或 'api'
    localModel: {
        apiKey: 'ollama',
        baseURL: 'http://localhost:11434/v1/',
        model: 'qwen3:8b'
    },
    apiModel: {
        apiKey: 'ipzotlGevNqQsafvWSXi:cooExiNRkHtQtHkkIqNk',
        baseURL: 'https://spark-api-open.xf-yun.com/v1/',
        model: 'lite'
    }
};

// 确保配置目录存在
function ensureConfigDir() {
    const configDir = path.join(__dirname, '../config');
    if (!fs.existsSync(configDir)) {
        fs.mkdirSync(configDir, { recursive: true });
    }
}

// 加载配置
function loadConfig() {
    try {
        ensureConfigDir();
        if (fs.existsSync(CONFIG_PATH)) {
            const configData = fs.readFileSync(CONFIG_PATH, 'utf8');
            aiConfig = JSON.parse(configData);
            console.log('已加载AI配置:', aiConfig.modelType);
        } else {
            // 如果配置文件不存在，创建默认配置
            saveConfig(aiConfig);
        }
    } catch (error) {
        console.error('加载AI配置失败:', error);
    }
}

// 保存配置
function saveConfig(config) {
    try {
        ensureConfigDir();
        fs.writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2), 'utf8');
        aiConfig = config;
        console.log('已保存AI配置:', config.modelType);
    } catch (error) {
        console.error('保存AI配置失败:', error);
    }
}

// 初始加载配置
loadConfig();

// 获取当前OpenAI客户端配置
function getCurrentConfig() {
    if (aiConfig.modelType === 'local') {
        return {
            apiKey: aiConfig.localModel.apiKey,
            baseURL: aiConfig.localModel.baseURL,
            model: aiConfig.localModel.model
        };
    } else {
        return {
            apiKey: aiConfig.apiModel.apiKey,
            baseURL: aiConfig.apiModel.baseURL,
            model: aiConfig.apiModel.model
        };
    }
}

// 创建OpenAI客户端
function createOpenAIClient() {
    const config = getCurrentConfig();
    return new OpenAI({
        apiKey: config.apiKey,
        baseURL: config.baseURL
    });
}

// 初始化OpenAI客户端
let openai = createOpenAIClient();

// 切换模型类型
function switchModelType(type) {
    if (type !== 'local' && type !== 'api') {
        throw new Error('无效的模型类型，必须是 "local" 或 "api"');
    }

    aiConfig.modelType = type;
    saveConfig(aiConfig);

    // 重新创建客户端
    openai = createOpenAIClient();

    return getCurrentModelInfo();
}

// 获取当前模型信息
function getCurrentModelInfo() {
    return {
        modelType: aiConfig.modelType,
        currentModel: getCurrentConfig().model,
        config: aiConfig
    };
}

/**
 * 生成AI回复
 * @param {Array} messages - 消息历史数组
 * @returns {Promise<string>} AI的回复内容
 */
async function generateAIResponse(messages) {
    try {
        const config = getCurrentConfig();
        const completion = await openai.chat.completions.create({
            model: config.model,
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
        const config = getCurrentConfig();
        const stream = await openai.chat.completions.create({
            model: config.model,
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
    generateStreamingResponse,
    switchModelType,
    getCurrentModelInfo,
    saveConfig
};