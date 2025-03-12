/**
 * Python脚本执行相关路由
 */
const express = require('express');
const router = express.Router();
const path = require('path');
const { spawn } = require('child_process');

/**
 * 执行Python脚本测试
 */
router.post('/run', (req, res) => {
    // 使用相对路径定位analyse.py
    const scriptPath = path.join(__dirname, '..', '..', 'src', 'services', 'analyse.py');
    
    const pythonProcess = spawn('python', [scriptPath]);
    let result = '';
    let error = '';

    pythonProcess.stdout.on('data', (data) => {
        result += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
        error += data.toString();
    });

    pythonProcess.on('close', (code) => {
        if (code !== 0 || error) {
            res.status(500).json({ status: 'error', result: error });
        } else {
            res.json({ status: 'success', result: result.trim() });
        }
    });
});

module.exports = router;