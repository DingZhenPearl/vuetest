/**
 * 编程数据处理服务
 */
const { executePythonScript } = require('./python');

/**
 * 提交编程数据到数据库
 * @param {Object} data - 编程数据对象
 * @returns {Promise} 处理结果
 */
async function submitCodingData(data) {
  try {
    // 将对象转换为字符串，以便传递给Python
    const dataJsonString = JSON.stringify(data);
    
    // 调用Python脚本存储数据
    const result = await executePythonScript('coding_data.py', [
      'submit_data',
      dataJsonString
    ]);
    
    return result;
  } catch (error) {
    console.error('调用Python脚本失败:', error);
    throw new Error(`处理编程数据失败: ${error.message}`);
  }
}

/**
 * 获取学生编程统计数据
 * @param {string} studentId - 学生ID
 * @returns {Promise} 学生编程统计数据
 */
async function getStudentCodingStats(studentId) {
  try {
    const result = await executePythonScript('coding_data.py', [
      'get_student_stats',
      studentId
    ]);
    
    return result;
  } catch (error) {
    console.error('获取学生编程统计失败:', error);
    throw new Error(`获取学生编程统计失败: ${error.message}`);
  }
}

/**
 * 获取班级编程统计数据
 * @param {string} className - 班级名称
 * @returns {Promise} 班级编程统计数据
 */
async function getClassCodingStats(className) {
  try {
    const result = await executePythonScript('coding_data.py', [
      'get_class_stats',
      className
    ]);
    
    return result;
  } catch (error) {
    console.error('获取班级统计失败:', error);
    throw new Error(`获取班级统计失败: ${error.message}`);
  }
}

/**
 * 获取特定题目的统计数据
 * @param {string} problemId - 题目ID
 * @returns {Promise} 题目提交统计数据
 */
async function getProblemStats(problemId) {
  try {
    const result = await executePythonScript('coding_data.py', [
      'get_problem_stats',
      problemId
    ]);
    
    return result;
  } catch (error) {
    console.error('获取题目统计失败:', error);
    throw new Error(`获取题目统计失败: ${error.message}`);
  }
}

module.exports = {
  submitCodingData,
  getStudentCodingStats,
  getClassCodingStats,
  getProblemStats
};