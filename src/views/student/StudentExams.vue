<template>
  <div class="student-exams">
    <h1>习题集</h1>
    
    <div class="exam-filters">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索习题集"
        prefix-icon="el-icon-search"
        clearable
        class="search-input"
      />
      <el-select v-model="filterStatus" placeholder="筛选状态" clearable>
        <el-option label="全部" value="" />
        <el-option label="未开始" value="notStarted" />
        <el-option label="进行中" value="inProgress" />
        <el-option label="已完成" value="completed" />
      </el-select>
    </div>

    <el-table :data="filteredExams" style="width: 100%" v-loading="loading">
      <el-table-column prop="title" label="习题集名称" />
      <el-table-column prop="description" label="描述" />
      <el-table-column prop="deadline" label="截止日期" />
      <el-table-column prop="status" label="状态">
        <template #default="scope">
          <el-tag :type="getStatusType(scope.row.status)">{{ getStatusText(scope.row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="scope">
          <el-button size="mini" type="primary" @click="openInVSCode(scope.row)">
            在VSCode中打开
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
export default {
  name: 'StudentExams',
  data() {
    return {
      loading: false,
      searchKeyword: '',
      filterStatus: '',
      exams: [
        {
          id: 1,
          title: 'JavaScript基础练习',
          description: '包含JS基本语法和函数练习',
          deadline: '2025-03-25',
          status: 'notStarted',
          examId: 'javascript-basics',
          examLocalPath: null  // 将在运行时确定
        },
        {
          id: 2,
          title: 'Vue组件开发实战',
          description: '创建和使用Vue组件的综合练习',
          deadline: '2025-04-10',
          status: 'inProgress',
          examId: 'vue-components',
          examLocalPath: null  // 将在运行时确定
        },
        {
          id: 3,
          title: 'React入门习题',
          description: 'React基础知识和钩子函数应用',
          deadline: '2025-04-15',
          status: 'completed',
          examId: 'react-basics',
          examLocalPath: null  // 将在运行时确定
        }
      ]
    }
  },
  computed: {
    filteredExams() {
      return this.exams.filter(exam => {
        // 筛选关键词
        const matchesKeyword = this.searchKeyword === '' || 
          exam.title.toLowerCase().includes(this.searchKeyword.toLowerCase()) ||
          exam.description.toLowerCase().includes(this.searchKeyword.toLowerCase());
        
        // 筛选状态
        const matchesStatus = this.filterStatus === '' || exam.status === this.filterStatus;
        
        return matchesKeyword && matchesStatus;
      });
    }
  },
  methods: {
    openInVSCode(exam) {
      // 首先尝试打开一个新的VSCode窗口
      const openNewWindow = () => {
        window.location.href = 'vscode://vscode.new';
      };
      
      // 如果有本地路径可用，则尝试打开该路径
      const openWithPath = (localPath) => {
        if (localPath) {
          window.location.href = `vscode://file/${localPath}`;
        } else {
          openNewWindow();
        }
      };

      // 尝试检查本地存储中是否有该习题集的路径记录
      const savedPath = localStorage.getItem(`exam-path-${exam.examId}`);
      
      if (savedPath) {
        openWithPath(savedPath);
      } else {
        // 可以在这里添加一个对话框，让用户选择或确认习题集存放路径
        // 简单实现：直接打开新窗口
        openNewWindow();
        
        // 显示提示，指导用户如何保存代码
        this.$notify({
          title: '打开新VSCode窗口',
          message: '请在VSCode中创建习题集目录，然后保存代码',
          type: 'info',
          duration: 5000
        });
      }
      
      // 记录当前打开的习题集
      localStorage.setItem('lastOpenedExam', exam.id);
    },
    getStatusType(status) {
      switch(status) {
        case 'notStarted': return 'info';
        case 'inProgress': return 'warning';
        case 'completed': return 'success';
        default: return 'info';
      }
    },
    getStatusText(status) {
      switch(status) {
        case 'notStarted': return '未开始';
        case 'inProgress': return '进行中';
        case 'completed': return '已完成';
        default: return '未知';
      }
    }
  }
}
</script>

<style scoped>
.student-exams {
  padding: 20px;
}

h1 {
  margin-bottom: 20px;
}

.exam-filters {
  display: flex;
  margin-bottom: 20px;
  gap: 10px;
}

.search-input {
  width: 250px;
}
</style>