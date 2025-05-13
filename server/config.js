/**
 * 服务器配置文件
 */

// 从环境变量中获取配置，如果不存在则使用默认值
const config = {
  // 服务器配置
  PORT: process.env.PORT || 3000,

  // 数据库配置
  DB_HOST: process.env.DB_HOST || 'localhost',
  DB_USER: process.env.DB_USER || 'root',
  DB_PASSWORD: process.env.DB_PASSWORD || '',
  DB_NAME: process.env.DB_NAME || 'edu_platform',

  // AI API配置 - 讯飞星火大模型
  AI_API_URL: process.env.AI_API_URL || 'https://spark-api-open.xf-yun.com/v1/chat/completions',
  AI_API_KEY: process.env.AI_API_KEY || 'ipzotlGevNqQsafvWSXi:cooExiNRkHtQtHkkIqNk',
  AI_MODEL: process.env.AI_MODEL || 'lite',

  // 文件上传配置
  UPLOAD_DIR: process.env.UPLOAD_DIR || 'uploads',
  MAX_FILE_SIZE: process.env.MAX_FILE_SIZE || 10 * 1024 * 1024, // 10MB

  // JWT配置
  JWT_SECRET: process.env.JWT_SECRET || 'your-secret-key',
  JWT_EXPIRES_IN: process.env.JWT_EXPIRES_IN || '24h',

  // 跨域配置
  CORS_ORIGIN: process.env.CORS_ORIGIN || '*',

  // 日志配置
  LOG_LEVEL: process.env.LOG_LEVEL || 'info',
};

module.exports = config;
