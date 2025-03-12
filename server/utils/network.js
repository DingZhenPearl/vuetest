/**
 * 网络相关工具函数
 */
const os = require('os');

/**
 * 获取本地网络IP地址
 * @returns {string} IP地址
 */
function getIPAddress() {
    const interfaces = os.networkInterfaces();
    for (const devName in interfaces) {
        const iface = interfaces[devName];
        for (let i = 0; i < iface.length; i++) {
            const alias = iface[i];
            if (alias.family === 'IPv4' && alias.address !== '127.0.0.1' && !alias.internal) {
                return alias.address;
            }
        }
    }
    return '0.0.0.0';
}

module.exports = {
    getIPAddress
};