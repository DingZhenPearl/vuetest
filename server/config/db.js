/**
 * 数据库配置文件
 */

// MySQL配置示例（实际连接参数已在Python脚本中定义）
const dbConfig = {
    // 保留与Python脚本一致的配置信息
    user_auth_db: {
        host: 'localhost',
        user: 'root',
        password: 'sushiding',
        database: 'user_auth_db'
    },
    chat_history_db: {
        host: 'localhost',
        user: 'root',
        password: 'sushiding',
        database: 'chat_history'
    }
};

module.exports = dbConfig;