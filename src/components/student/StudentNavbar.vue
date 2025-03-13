<template>
  <div :class="['sidebar', { collapsed: isCollapsed }]">
    <!-- 用户信息面板 -->
    <div class="user-panel">
      <div class="user-avatar">{{ getUserInitial() }}</div>
      <div class="user-info" v-show="!isCollapsed">
        <div class="user-name">{{ userName || '用户' }}</div>
        <div class="user-email">{{ userEmail }}</div>
        <div class="user-identifier">ID: {{ shortIdentifier }}</div>
      </div>
      <div class="toggle-btn" @click="toggleSidebar">
        <i :class="isCollapsed ? 'el-icon-s-unfold' : 'el-icon-s-fold'"></i>
      </div>
    </div>
    
    <!-- 主导航菜单 - 包含所有菜单项 -->
    <el-menu 
      class="sidebar-menu"
      background-color="#2c3e50"
      text-color="#e9e9e9"
      active-text-color="#ffd04b"
      :collapse="isCollapsed"
      :collapse-transition="false"
      :router="true"
      :default-active="activeIndex"
      unique-opened>
      
      <!-- 常用功能区 -->
      <div class="menu-section">
        <div class="section-title" v-if="!isCollapsed">常用功能</div>
        
        <el-menu-item index="/student/home" class="menu-item">
          <i class="el-icon-s-home"></i>
          <template v-slot:title>主页</template>
        </el-menu-item>
        
        <el-menu-item index="/student/profile" class="menu-item">
          <i class="el-icon-user"></i>
          <template v-slot:title>个人信息</template>
        </el-menu-item>
      </div>
      
      <!-- 学习中心区 -->
      <div class="menu-section">
        <div class="section-title" v-if="!isCollapsed">学习中心</div>
        
        <el-menu-item index="/student/question" class="menu-item">
          <i class="el-icon-chat-line-round"></i>
          <template v-slot:title>问题求助</template>
        </el-menu-item>
        
        <el-menu-item index="/student/aiChat" class="menu-item">
          <i class="el-icon-cpu"></i>
          <template v-slot:title>AI对话</template>
        </el-menu-item>
        
        <el-menu-item index="/student/exams" class="menu-item">
          <i class="el-icon-notebook-1"></i>
          <template v-slot:title>习题集</template>
        </el-menu-item>
      </div>
      
      <!-- 次要功能 -->
      <div class="menu-section">
        <div class="section-title" v-if="!isCollapsed">更多功能</div>
        
        <el-submenu index="learning" class="menu-item">
          <template v-slot:title>
            <i class="el-icon-reading"></i>
            <span>学习资源</span>
          </template>
          <el-menu-item index="/programming-concepts" @click.prevent="explainProgrammingConcepts">
            <i class="el-icon-edit-outline"></i>
            <span>编程概念</span>
          </el-menu-item>
          <el-menu-item index="/case-analysis" @click.prevent="caseAnalysis">
            <i class="el-icon-document"></i>
            <span>案例分析</span>
          </el-menu-item>
        </el-submenu>
        
        <el-menu-item index="/learning-analysis" @click.prevent="learningBehaviorAnalysis" class="menu-item">
          <i class="el-icon-data-analysis"></i>
          <template v-slot:title>学习分析</template>
        </el-menu-item>
        
        <el-menu-item index="/troubleshooting" @click.prevent="troubleshooting" class="menu-item">
          <i class="el-icon-question"></i>
          <template v-slot:title>疑难解答</template>
        </el-menu-item>
      </div>
      
      <!-- 将退出登录按钮修改为不使用路由导航的方式 -->
      <div class="menu-section logout-section">
        <div class="section-title" v-if="!isCollapsed">系统</div>
        
        <el-menu-item index="logout" class="menu-item" @click="logout">
          <i class="el-icon-switch-button"></i>
          <template v-slot:title>退出登录</template>
        </el-menu-item>
      </div>
    </el-menu>
  </div>
</template>

<script>
export default {
  name: 'StudentNavbar',
  data() {
    return {
      userEmail: '',
      userName: '',
      userIdentifier: '',
      isCollapsed: false,
      activeIndex: '/student/home'
    }
  },
  computed: {
    // 生成一个短版本的标识符用于显示
    shortIdentifier() {
      if (!this.userIdentifier) return '';
      return this.userIdentifier.substring(0, 8);
    }
  },
  created() {
    // 从本地存储或URL参数获取用户信息
    this.userEmail = localStorage.getItem('userEmail') || '';
    this.userName = localStorage.getItem('username') || '';
    this.userIdentifier = localStorage.getItem('userIdentifier') || 
                          this.$route.query.uid || '';
    
    // 设置当前激活的导航项
    this.activeIndex = this.$route.path;
    
    // 检查是否需要在小屏幕上默认折叠
    this.checkScreenWidth();
    
    // 监听屏幕尺寸变化
    window.addEventListener('resize', this.checkScreenWidth);
  },
  beforeUnmount() {
    // 移除事件监听
    window.removeEventListener('resize', this.checkScreenWidth);
  },
  methods: {
    checkScreenWidth() {
      this.isCollapsed = window.innerWidth <= 768;
    },
    toggleSidebar() {
      this.isCollapsed = !this.isCollapsed;
    },
    explainProgrammingConcepts() {
      this.$message({
        message: '编程概念讲解功能即将上线，敬请期待！',
        type: 'info'
      });
    },
    caseAnalysis() {
      this.$message({
        message: '实战案例分析功能即将上线，敬请期待！',
        type: 'info'
      });
    },
    troubleshooting() {
      this.$message({
        message: '疑难解答功能即将上线，敬请期待！',
        type: 'info'
      });
    },
    learningBehaviorAnalysis() {
      this.$message({
        message: '学习行为分析功能即将上线，敬请期待！',
        type: 'info'
      });
    },
    logout() {
      console.log("退出登录");  // 添加调试日志
      
      // 获取当前用户角色，用于跳转时携带
      const userRole = localStorage.getItem('userRole') || 'student';
      
      // 清除本地存储中的用户信息
      localStorage.removeItem('userEmail');
      localStorage.removeItem('username');
      localStorage.removeItem('userRole');
      
      // 跳转到登录页面，并携带角色信息作为查询参数
      this.$router.push({
        path: '/logIn',
        query: { role: userRole }
      });
    },
    getUserInitial() {
      if (this.userName && this.userName.length > 0) {
        return this.userName.charAt(0).toUpperCase();
      }
      return 'U';
    }
  }
}
</script>

<style scoped>
.sidebar {
  height: 100vh;
  position: fixed;
  left: 0;
  top: 0;
  width: 250px;
  background-color: #2c3e50;
  color: #e9e9e9;
  display: flex;
  flex-direction: column;
  transition: all 0.3s;
  overflow: hidden;
  box-shadow: 2px 0 6px rgba(0, 0, 0, 0.1);
  z-index: 999;
}

.sidebar.collapsed {
  width: 64px;
}

/* 用户信息面板 */
.user-panel {
  padding: 15px;
  background-color: #1a2940;
  display: flex;
  align-items: center;
  height: 64px;
  box-sizing: border-box;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: #42b983;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 20px;
  margin-right: 10px;
  flex-shrink: 0;
}

.user-info {
  flex-grow: 1;
  overflow: hidden;
}

.user-name {
  font-weight: bold;
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-email {
  font-size: 12px;
  opacity: 0.8;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-identifier {
  font-size: 11px;
  color: #8aa9c2;
  margin-top: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.toggle-btn {
  font-size: 16px;
  cursor: pointer;
  padding: 5px;
  transition: all 0.3s;
  margin-left: auto;
}

.toggle-btn:hover {
  color: #ffd04b;
}

/* 菜单区域 */
.sidebar-menu {
  flex-grow: 1;
  border-right: none;
  overflow-y: auto;
  overflow-x: hidden;
}

.menu-section {
  margin-bottom: 5px;
  position: relative;
  padding-top: 10px;
}

.section-title {
  padding: 0 20px;
  font-size: 12px;
  color: #a0a0a0;
  margin-bottom: 8px;
  position: relative;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.section-title:after {
  content: '';
  position: absolute;
  left: 20px;
  right: 20px;
  bottom: -4px;
  height: 1px;
  background: rgba(255, 255, 255, 0.08);
}

.menu-item {
  position: relative;
}

.menu-item .is-active {
  background-color: #1a2940 !important;
}

/* 底部登出按钮 */
.menu-footer {
  padding: 10px 0;
  background-color: #1a2940;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.logout-btn {
  display: flex;
  align-items: center;
  padding: 10px 20px;
  color: #e9e9e9;
  transition: all 0.3s;
  cursor: pointer;
  height: auto;
  line-height: normal;
}

.logout-btn i {
  margin-right: 10px;
  font-size: 16px;
  color: #ff6b6b;
}

.logout-btn:hover {
  background-color: #c0392b;
}

/* 自定义菜单项样式 */
.custom-menu-item {
  display: flex;
  align-items: center;
  padding: 14px 20px;
  cursor: pointer;
  color: #e9e9e9;
  transition: all 0.3s;
}

.custom-menu-item:hover {
  background-color: #c0392b;
}

.custom-menu-item i {
  font-size: 16px;
  color: #ff6b6b;
  margin-right: 10px;
}

.menu-title {
  margin-left: 5px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .sidebar:not(.collapsed) {
    transform: translateX(0);
    width: 250px;
  }
  
  .sidebar.collapsed {
    width: 0;
  }

  .user-panel {
    justify-content: center;
  }
}
</style>