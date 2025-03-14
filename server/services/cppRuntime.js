/**
 * C++代码运行时服务
 */
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const { v4: uuidv4 } = require('uuid');
const os = require('os');

// 临时文件存放目录
const TEMP_DIR = os.tmpdir();

/**
 * 编译并执行C++代码
 * @param {string} code - C++代码内容
 * @param {string} input - 程序输入
 * @returns {Promise<Object>} 运行结果，包含输出和错误信息
 */
async function compileAndRunCpp(code, input = '') {
  // 生成唯一标识符，用于临时文件名
  const fileId = uuidv4();
  const cppFilePath = path.join(TEMP_DIR, `${fileId}.cpp`);
  const exeFilePath = path.join(TEMP_DIR, `${fileId}.exe`);
  const inputFilePath = input ? path.join(TEMP_DIR, `${fileId}.in`) : null;

  try {
    // 保存C++代码到临时文件
    await fs.promises.writeFile(cppFilePath, code);
    
    // 如果有输入，保存到输入文件
    if (input && input.trim()) {
      await fs.promises.writeFile(inputFilePath, input);
    }

    // 编译代码
    const compilationResult = await compileCode(cppFilePath, exeFilePath);
    if (compilationResult.error) {
      return {
        success: false,
        compilationError: compilationResult.error,
        message: '编译失败'
      };
    }

    // 运行程序
    const runResult = await runExecutable(exeFilePath, inputFilePath);
    return {
      success: !runResult.error,
      output: runResult.stdout,
      error: runResult.error,
      message: runResult.error ? '运行错误' : '执行成功'
    };
  } catch (error) {
    return {
      success: false,
      error: error.message,
      message: '系统错误'
    };
  } finally {
    // 清理临时文件
    cleanupFiles([cppFilePath, exeFilePath, inputFilePath].filter(Boolean));
  }
}

/**
 * 编译C++代码
 * @param {string} cppFilePath - C++源文件路径
 * @param {string} exeFilePath - 可执行文件输出路径
 * @returns {Promise<Object>} 编译结果
 */
function compileCode(cppFilePath, exeFilePath) {
  return new Promise((resolve) => {
    // 使用g++编译
    const compiler = spawn('g++', [cppFilePath, '-o', exeFilePath, '-std=c++11']);
    let compileError = '';

    compiler.stderr.on('data', (data) => {
      compileError += data.toString();
    });

    compiler.on('close', (code) => {
      if (code === 0) {
        resolve({ success: true });
      } else {
        resolve({ success: false, error: compileError });
      }
    });
  });
}

/**
 * 运行编译后的可执行文件
 * @param {string} exeFilePath - 可执行文件路径
 * @param {string} inputFilePath - 输入文件路径
 * @returns {Promise<Object>} 运行结果
 */
function runExecutable(exeFilePath, inputFilePath) {
  return new Promise((resolve) => {
    let stdout = '';
    let stderr = '';
    
    // 设置运行选项
    const options = {
      timeout: 5000 // 5秒超时
    };
    
    // 如果有输入文件，则从文件读取输入
    const childProcess = inputFilePath
      ? spawn(exeFilePath, [], {
          ...options,
          stdio: ['pipe', 'pipe', 'pipe']
        })
      : spawn(exeFilePath, [], options);
    
    // 如果有输入文件，将内容通过管道传递给程序
    if (inputFilePath) {
      const inputStream = fs.createReadStream(inputFilePath);
      inputStream.pipe(childProcess.stdin);
    }

    childProcess.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    childProcess.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    childProcess.on('error', (error) => {
      resolve({ stdout, error: error.message });
    });

    childProcess.on('close', (code) => {
      if (code === 0) {
        resolve({ stdout, stderr: '' });
      } else {
        resolve({ stdout, error: stderr || `进程退出，错误码: ${code}` });
      }
    });
  });
}

/**
 * 清理临时文件
 * @param {Array<string>} filePaths - 需要删除的文件路径
 */
function cleanupFiles(filePaths) {
  filePaths.forEach(filePath => {
    if (filePath) {
      fs.unlink(filePath, () => {}); // 忽略错误
    }
  });
}

/**
 * 验证C++代码是否符合样例
 * @param {string} code - C++代码内容
 * @param {string} inputExample - 输入样例
 * @param {string} expectedOutput - 预期输出
 * @returns {Promise<Object>} 验证结果
 */
async function validateCppCode(code, inputExample, expectedOutput) {
  const result = await compileAndRunCpp(code, inputExample);
  
  if (!result.success) {
    return result;
  }

  // 比较输出结果与预期输出
  // 标准化输出（去除末尾空行和空白字符）
  const normalizedOutput = result.output.trim().replace(/\r\n/g, '\n');
  const normalizedExpected = expectedOutput.trim().replace(/\r\n/g, '\n');

  const isCorrect = normalizedOutput === normalizedExpected;
  
  return {
    ...result,
    isCorrect,
    message: isCorrect ? '测试通过' : '测试失败，输出与预期不符',
    actualOutput: normalizedOutput,
    expectedOutput: normalizedExpected
  };
}

module.exports = {
  compileAndRunCpp,
  validateCppCode
};
