# 创建虚拟环境
本项目由两个子项目构成，本子项目实现网页的前后端设计，另一个子项目实现vscode插件的设计。

# vuetest

## Project setup
```
npm install
```

### Compiles and hot-reloads for development
```
npm run serve
```

### Compiles and minifies for production
```
npm run build
```

### Lints and fixes files
```
npm run lint
```

### Customize configuration
See [Configuration Reference](https://cli.vuejs.org/config/).

## Python环境设置

本项目同时使用Node.js和Python。Python依赖需要单独安装：

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

# 更新所需依赖
pip freeze > requirements.txt

