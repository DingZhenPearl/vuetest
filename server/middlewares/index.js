/**
 * 中间件配置
 */
const cors = require('cors');
const bodyParser = require('body-parser');
const express = require('express');
const path = require('path');

/**
 * 应用中间件到Express应用
 * @param {Object} app - Express应用实例
 * @param {String} staticRoot - 静态文件根目录
 */
function setupMiddlewares(app, staticRoot) {
    // CORS配置
    app.use(cors({
        origin: '*',
        methods: ['GET', 'POST', 'PUT', 'DELETE'],
        allowedHeaders: ['Content-Type']
    }));
    
    // 解析JSON请求体
    app.use(bodyParser.json());
    
    // 静态文件服务
    app.use(express.static(staticRoot));
    
    console.log('中间件配置完成');
}

module.exports = setupMiddlewares;