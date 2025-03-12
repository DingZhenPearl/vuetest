/**
 * 教学互动平台服务器 - 主入口
 * 经过模块化重构，代码更加清晰可维护
 */

// 导入核心模块
const express = require('express');
const path = require('path');

// 导入自定义模块
const setupMiddlewares = require('./middlewares');
const { getIPAddress } = require('./utils/network');

// 导入路由模块
const authRoutes = require('./routes/auth');
const chatRoutes = require('./routes/chat');
const questionsRoutes = require('./routes/questions');
const pythonRoutes = require('./routes/python');

// 初始化Express应用
const app = express();
const port = 3000;

// 定义静态文件路径
const staticRoot = path.resolve(path.join(__dirname, '..', 'dist'));
console.log('静态文件路径:', staticRoot);

// 配置中间件
setupMiddlewares(app, staticRoot);

// 注册路由
// 认证路由
app.use('/', authRoutes);
// API路由 - 聊天功能
app.use('/api', chatRoutes);
// API路由 - 问答系统
app.use('/api', questionsRoutes);
// API路由 - Python脚本执行
app.use('/', pythonRoutes);

// 基本路由 - 首页
app.get('/', (req, res) => {
    res.sendFile(path.join(staticRoot, 'index.html'));
});

// 放在所有API路由之后，添加Vue SPA支持
// 所有未匹配的路由都发送index.html
app.get('*', (req, res, next) => {
    // 排除API和静态文件路径
    if (req.path.startsWith('/api') || req.path === '/login' || req.path === '/register' || req.path.includes('.')) {
        return next();
    }
    res.sendFile(path.join(staticRoot, 'index.html'));
});

// 启动服务器
app.listen(port, '0.0.0.0', () => {
    console.log(`服务器运行在 http://localhost:${port}`);
    console.log(`可通过本地网络IP访问：http://${getIPAddress()}:${port}`);
});