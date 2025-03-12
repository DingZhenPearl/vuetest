<template>
  <div class="teacher-python-container">
    <!-- 导航组件 -->
    <TeacherNavbar />
    
    <!-- 主内容区 -->
    <div class="main-content">
      <h2>教学数据管理</h2>
      
      <div class="controls">
        <button @click="runPythonScript" class="action-button" :disabled="isLoading">
          {{ isLoading ? '处理中...' : '分析学生编程数据' }}
        </button>
      </div>
      
      <div class="result-container">
        <h3>执行结果：</h3>
        <pre 
          :class="['result-output', { error: resultError, success: !resultError && result }]" 
          v-if="result || resultError"
        >{{ resultError || result }}</pre>
        <div v-else class="empty-result">尚未执行分析，点击按钮开始分析学生数据。</div>
      </div>
    </div>
  </div>
</template>

<script>
import TeacherNavbar from '@/components/teacher/TeacherNavbar.vue';

export default {
  name: 'TeacherPython',
  components: {
    TeacherNavbar
  },
  data() {
    return {
      isLoading: false,
      result: '',
      resultError: null
    }
  },
  methods: {
    async runPythonScript() {
      this.isLoading = true;
      this.result = '';
      this.resultError = null;
      
      try {
        const response = await fetch('/api/python/run', { // 更新API路径
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          }
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
          this.result = data.result;
        } else {
          this.resultError = `错误：${data.result}`;
        }
      } catch (error) {
        console.error('请求失败:', error);
        this.resultError = `请求失败：${error.message}`;
      } finally {
        this.isLoading = false;
      }
    }
  }
}
</script>

<style scoped>
.teacher-python-container {
  display: flex;
}

.main-content {
  padding: 20px;
  background-color: #f4f4f4;
  min-height: 100vh;
  margin-left: 250px; /* 与侧边栏宽度相同 */
  width: calc(100% - 250px);
  box-sizing: border-box;
}

h2 {
  margin-bottom: 20px;
  color: #2c3e50;
}

.controls {
  margin-bottom: 20px;
}

.action-button {
  padding: 10px 20px;
  background-color: #3498db;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s;
}

.action-button:hover {
  background-color: #2980b9;
}

.action-button:disabled {
  background-color: #95a5a6;
  cursor: not-allowed;
}

.result-container {
  background-color: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.result-output {
  white-space: pre-wrap;
  background-color: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
  font-family: monospace;
  overflow-x: auto;
  max-height: 500px;
  overflow-y: auto;
}

.result-output.success {
  color: #2ecc71;
}

.result-output.error {
  color: #e74c3c;
}

.empty-result {
  color: #7f8c8d;
  padding: 15px;
  text-align: center;
  font-style: italic;
}
</style>