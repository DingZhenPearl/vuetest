/**
 * 插件服务路由
 * 处理VS Code插件的API请求
 */
const express = require('express');
const router = express.Router();
const { generateStreamingGuidance, generateGuidance } = require('../plugin-services/progressiveGuideService');

/**
 * 渐进式编程辅导 - 流式API
 * 接收提示词，返回流式AI响应
 */
router.post('/progressive-guide/stream', generateStreamingGuidance);

/**
 * 渐进式编程辅导 - 非流式API（备用）
 * 接收提示词，返回完整AI响应
 */
router.post('/progressive-guide', generateGuidance);

/**
 * 健康检查端点
 */
router.get('/health', (req, res) => {
    res.json({ status: 'ok', service: 'plugin-api' });
});

module.exports = router;
