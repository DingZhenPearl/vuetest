/**
 * Python脚本执行服务
 */
const { spawn } = require('child_process');
const path = require('path');

/**
 * 执行Python脚本并返回结果
 * @param {string} scriptName - Python脚本文件名
 * @param {Array} args - 传递给Python脚本的参数
 * @returns {Promise} 脚本执行结果的Promise对象
 */
function executePythonScript(scriptName, args) {
    // 使用相对路径从服务器脚本位置查找Python脚本
    const scriptPath = path.join(__dirname, '..', '..', 'src', 'services', scriptName);
    
    return new Promise((resolve, reject) => {
        const pythonProcess = spawn('python', [scriptPath, ...args]);
        let result = '';
        let error = '';

        pythonProcess.stdout.on('data', (data) => {
            result += data.toString();
        });

        pythonProcess.stderr.on('data', (data) => {
            error += data.toString();
        });

        pythonProcess.on('close', (code) => {
            if (code !== 0) {
                reject(error || 'Python脚本执行失败');
            } else {
                try {
                    resolve(JSON.parse(result));
                } catch {
                    resolve(result);
                }
            }
        });
    });
}

module.exports = {
    executePythonScript
};