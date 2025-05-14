# 数据结构与算法导论 - 实时编程调试反馈学习系统 (Web 端)

本项目是一款创新的 IDE 集成实时编程调试反馈学习系统，专为《数据结构与算法导论》课程设计。该系统深度融合大模型人工智能技术，为学生提供全面的编程学习支持平台。

## 项目概述

本项目由两个主要部分组成：

1. **Web 应用部分（当前文件夹）**：基于 Vue.js 的网页应用，提供学生和教师的学习管理系统
2. **IDE 插件部分（ex1 文件夹）**：基于 VS Code 的扩展，提供编程练习和实时代码分析功能

### 核心功能

1. **IDE 插件设计与开发**：基于 VS Code 的插件，提供实时代码审查、错误提示、代码优化建议等功能
2. **大模型人工智能接口集成**：集成讯飞星火大模型 API 和本地模型，为学生提供精确的问题解答和调试指导
3. **渐进式智能编程辅导**：通过智能审题、代码分析、关键点拨、详细指导和指导代码的五步策略，引导学生主动参与学习
4. **智能错误诊断与调试辅助**：分析学生编程中的错误模式，提供针对性的调试建议和解决方案
5. **个性化学习路径推荐**：大模型分析学生学习行为和表现，生成个性化学习建议和资源推荐
6. **教学数据分析与教师洞察**：收集和分析学生的学习数据，为教师提供宝贵的教学洞察
7. **教学模式探索与总结**：探索系统在不同教学场景下的应用效果，形成系统的集成应用指南

## 技术栈

### 前端

- Vue.js 3
- Element Plus
- TDesign Vue Next
- ECharts
- Axios

### 后端

- Node.js
- Express
- MySQL
- Python

### AI 集成

- 讯飞星火大模型 API
- Ollama 本地模型支持

## 安装与设置

### 前提条件

- Node.js 16+
- Python 3.8+
- MySQL 8.0+
- G++ 编译器（用于 C++代码验证）

### 安装步骤

1. **克隆项目**

```bash
git clone <repository-url>
cd vuetest
```

2. **安装 Node.js 依赖**

```bash
npm install
```

3. **设置 Python 环境**

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows
.\.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

4. **配置数据库**

- 创建 MySQL 数据库
- 修改`server/config.js`中的数据库配置

5. **启动开发服务器**

```bash
# 启动前端开发服务器
npm run serve

# 启动后端服务器
npm run dev
```

## Python 依赖

以下是项目所需的 Python 依赖列表：

```
mysql-connector-python>=8.0.0
requests>=2.25.0
openai>=0.27.0
python-dateutil>=2.8.0
numpy>=1.20.0
pandas>=1.3.0
matplotlib>=3.4.0
scikit-learn>=1.0.0
```

## 项目结构

```
vuetest/
├── public/                 # 静态资源
├── server/                 # 后端服务器
│   ├── config.js           # 服务器配置
│   ├── routes/             # API路由
│   ├── services/           # 服务层
│   └── server.js           # 服务器入口
├── src/                    # 前端源代码
│   ├── assets/             # 静态资源
│   ├── components/         # Vue组件
│   ├── router/             # 路由配置
│   ├── services/           # Python服务脚本
│   ├── scripts/            # 辅助脚本
│   ├── views/              # 页面视图
│   │   ├── student/        # 学生页面
│   │   └── teacher/        # 教师页面
│   ├── App.vue             # 根组件
│   └── main.js             # 入口文件
├── .env                    # 环境变量
├── package.json            # 项目依赖
├── requirements.txt        # Python依赖
└── vue.config.js           # Vue配置
```

## 使用说明

### 学生功能

- 登录系统访问个人学习空间
- 浏览和完成编程练习题目
- 获取 AI 辅助的编程指导和错误诊断
- 查看个人学习分析和推荐
- 学习编程概念和资源

### 教师功能

- 管理课程内容和编程题目
- 查看学生学习数据和进度
- 获取 AI 驱动的教学分析和洞察
- 管理教学资源和内容

## 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 许可证

[MIT License](LICENSE)
