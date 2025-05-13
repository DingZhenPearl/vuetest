/**
 * 教学互动平台服务器 - 主入口
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

const profileRoutes = require('./routes/profile');
const profilesRoutes = require('./routes/profiles'); // 新增个人信息管理路由
const problemsRoutes = require('./routes/problems'); // 确保此行存在
const codingRoutes = require('./routes/coding'); // 添加编程路由
const teachingRoutes = require('./routes/teaching'); // 新增教学分析路由
const pluginRoutes = require('./routes/plugin-routes'); // 插件服务路由
const learningRoutes = require('./routes/learning'); // 学习分析和推荐路由
const teachingContentRoutes = require('./routes/teaching-content'); // 教学内容管理路由
const aiAnalysisRoutes = require('./routes/ai-analysis'); // AI分析路由

// 初始化Express应用
const app = express();
const port = process.env.PORT || 3000;

// 定义静态文件路径
const staticRoot = path.resolve(path.join(__dirname, '..', 'dist'));
console.log('静态文件路径:', staticRoot);

// 配置中间件
setupMiddlewares(app, staticRoot);

// 注册路由
app.use('/api/auth', authRoutes);
app.use('/api/chat', chatRoutes);
app.use('/api/questions', questionsRoutes);

app.use('/api/profile', profileRoutes);
app.use('/api/profiles', profilesRoutes); // 注册个人信息管理路由
app.use('/api/problems', problemsRoutes); // 确保此行存在
app.use('/api/coding', codingRoutes); // 添加编程路由
app.use('/api/teaching', teachingRoutes); // 注册教学分析路由
app.use('/api/plugin', pluginRoutes); // 注册插件服务路由
app.use('/api/learning', learningRoutes); // 注册学习分析和推荐路由
app.use('/api/teaching-content', teachingContentRoutes); // 注册教学内容管理路由
app.use('/api/teaching', aiAnalysisRoutes); // 注册AI分析路由（挂载在teaching路径下）

// 基本路由 - 首页
app.get('/', (req, res) => {
    res.sendFile(path.join(staticRoot, 'index.html'));
});

// 放在所有API路由之后，添加Vue SPA支持
// 所有未匹配的路由都发送index.html
app.get('*', (req, res, next) => {
    // 排除API和静态文件路径
    if (req.path.startsWith('/api') || req.path.includes('.')) {
        return next();
    }
    res.sendFile(path.join(staticRoot, 'index.html'));
});

// 启动服务器
app.listen(port, '0.0.0.0', () => {
    console.log(`服务器运行在 http://localhost:${port}`);
    console.log(`可通过本地网络IP访问：http://${getIPAddress()}:${port}`);
});