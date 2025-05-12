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

    console.log(`执行Python脚本: ${scriptPath}`);
    console.log(`参数: ${args.join(', ')}`);

    return new Promise((resolve, reject) => {
        // 设置环境变量以确保Python正确处理UTF-8编码
        const env = Object.assign({}, process.env, {
            PYTHONIOENCODING: 'utf-8',
            PYTHONLEGACYWINDOWSSTDIO: 'utf-8'
        });

        const pythonProcess = spawn('python', [scriptPath, ...args], { env });
        let result = '';
        let error = '';

        pythonProcess.stdout.on('data', (data) => {
            result += data.toString('utf-8');
        });

        pythonProcess.stderr.on('data', (data) => {
            error += data.toString('utf-8');
            console.log(`Python脚本错误输出: ${data.toString('utf-8')}`);
        });

        pythonProcess.on('close', (code) => {
            console.log(`Python脚本执行完成，退出码: ${code}`);
            if (code !== 0) {
                console.error(`Python脚本执行失败: ${error}`);
                reject(error || 'Python脚本执行失败');
            } else {
                try {
                    // 尝试解析最后一个有效的JSON对象
                    const jsonLines = result.split(/\r?\n/).filter(line => line.trim());
                    let parsedResult;

                    if (jsonLines.length > 0) {
                        // 使用最后一个可能的JSON行
                        const lastJsonLine = jsonLines[jsonLines.length - 1];
                        try {
                            parsedResult = JSON.parse(lastJsonLine);
                            console.log('成功解析Python脚本输出为JSON');
                        } catch (e) {
                            console.warn(`解析最后一行JSON失败: ${e.message}`);
                            // 尝试解析整个输出
                            parsedResult = JSON.parse(result);
                        }
                    } else {
                        parsedResult = JSON.parse(result);
                    }

                    resolve(parsedResult);
                } catch (e) {
                    console.warn(`解析Python脚本输出为JSON失败: ${e.message}`);
                    console.log(`原始输出: ${result}`);
                    // 如果无法解析为JSON，返回一个默认的成功响应
                    resolve({
                        success: false,
                        message: '无法解析Python脚本输出',
                        rawOutput: result
                    });
                }
            }
        });
    });
}

module.exports = {
    executePythonScript
};