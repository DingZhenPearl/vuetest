<template>
  <div :class="['sidebar', { collapsed: isCollapse }]">
    <!-- 用户信息面板 -->
    <div class="user-panel">
      <div class="user-avatar">{{ getUserInitial() }}</div>
      <div class="user-info" v-show="!isCollapse">
        <div class="user-name">{{ userName || '教师' }}</div>
        <div class="user-email">{{ userEmail }}</div>
        <div class="user-identifier">ID: {{ shortIdentifier }}</div>
      </div>
      <div class="toggle-btn" @click="toggleCollapse">
        <i :class="isCollapse ? 'el-icon-s-unfold' : 'el-icon-s-fold'"></i>
      </div>
    </div>

    <!-- 小屏幕下的悬浮展开按钮 -->
    <div class="mobile-toggle-btn" @click="toggleCollapse" v-if="isMobileView">
      <i class="el-icon-s-unfold"></i>
    </div>

    <!-- 主导航菜单 -->
    <el-menu
      class="sidebar-menu"
      background-color="#263445"
      text-color="#e9e9e9"
      active-text-color="#ffd04b"
      :collapse="isCollapse"
      :collapse-transition="false"
      :router="true"
      :default-active="activeIndex"
      unique-opened>

      <!-- 常用功能区 -->
      <div class="menu-section">
        <div class="section-title" v-if="!isCollapse">常用功能</div>

        <el-menu-item index="/teacher/home" class="menu-item">
          <i class="el-icon-s-home"></i>
          <template #title>首页</template>
        </el-menu-item>

        <el-menu-item index="/teacher/answer" class="menu-item">
          <i class="el-icon-chat-line-round"></i>
          <template #title>学生提问</template>
        </el-menu-item>
      </div>

      <!-- 教学管理区 -->
      <div class="menu-section">
        <div class="section-title" v-if="!isCollapse">教学管理</div>



        <el-menu-item index="/teacher/grades" class="menu-item">
          <i class="el-icon-s-data"></i>
          <template #title>成绩管理</template>
        </el-menu-item>

        <el-menu-item index="/teacher/python" class="menu-item">
          <i class="el-icon-s-management"></i>
          <template #title>数据管理</template>
        </el-menu-item>

        <el-menu-item index="/teacher/problems" class="menu-item">
          <i class="el-icon-edit-outline"></i>
          <template #title>出题管理</template>
        </el-menu-item>
      </div>

      <!-- 分析工具 -->
      <div class="menu-section">
        <div class="section-title" v-if="!isCollapse">分析工具</div>

        <el-menu-item index="/teacher/teaching-analysis" class="menu-item">
          <i class="el-icon-data-analysis"></i>
          <template #title>教学分析</template>
        </el-menu-item>

        <el-menu-item index="/teacher/coding-analysis" class="menu-item">
          <i class="el-icon-s-data"></i>
          <template #title>编程数据分析</template>
        </el-menu-item>

        <el-menu-item index="/teacher/analysis" class="menu-item">
          <i class="el-icon-s-marketing"></i>
          <template #title>学习行为分析</template>
        </el-menu-item>

        <el-submenu index="advanced-analysis" class="menu-item">
          <template #title>
            <i class="el-icon-data-analysis"></i>
            <span>高级分析</span>
          </template>
          <el-menu-item index="/data-visualization" @click.prevent="showAlert('数据分析可视化')">
            <i class="el-icon-pie-chart"></i>
            <span>数据可视化</span>
          </el-menu-item>
          <el-menu-item index="/feedback-report" @click.prevent="showAlert('教学反馈报告')">
            <i class="el-icon-document"></i>
            <span>反馈报告</span>
          </el-menu-item>
        </el-submenu>
      </div>

      <!-- 系统设置 -->
      <div class="menu-section">
        <div class="section-title" v-if="!isCollapse">系统设置</div>

        <el-menu-item index="/permission-management" @click.prevent="showAlert('权限管理')" class="menu-item">
          <i class="el-icon-lock"></i>
          <template #title>权限管理</template>
        </el-menu-item>

        <el-menu-item index="/system-settings" @click.prevent="showAlert('系统设置')" class="menu-item">
          <i class="el-icon-setting"></i>
          <template #title>系统设置</template>
        </el-menu-item>
      </div>

      <!-- 将退出登录按钮修改为不使用路由导航的方式 -->
      <div class="menu-section logout-section">
        <div class="section-title" v-if="!isCollapse">系统</div>

        <el-menu-item index="logout" class="menu-item" @click="logout">
          <i class="el-icon-switch-button"></i>
          <template #title>退出登录</template>
        </el-menu-item>
      </div>
    </el-menu>
  </div>
</template>

<script>
export default {
  name: 'TeacherNavbar',
  data() {
    return {
      userEmail: '',
      userName: '',
      userIdentifier: '',
      isCollapse: false,
      activeIndex: '/teacher/home',
      windowWidth: window.innerWidth
    }
  },
  computed: {
    shortIdentifier() {
      if (!this.userIdentifier) return '';
      return this.userIdentifier.substring(0, 8);
    },
    // 判断是否为移动视图
    isMobileView() {
      return this.windowWidth <= 768;
    }
  },
  created() {
    // 从 sessionStorage 获取用户信息
    this.userEmail = sessionStorage.getItem('userEmail') || '';
    this.userName = sessionStorage.getItem('username') || '';
    this.userIdentifier = sessionStorage.getItem('userIdentifier') ||
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
      this.windowWidth = window.innerWidth;
      this.isCollapse = window.innerWidth <= 768;
    },
    toggleCollapse() {
      this.isCollapse = !this.isCollapse;
    },
    showAlert(featureName) {
      this.$message({
        message: `${featureName}功能正在开发中，敬请期待！`,
        type: 'info'
      });
    },
    logout() {
      console.log("退出登录");

      const userRole = sessionStorage.getItem('userRole') || 'teacher';

      // 清除 sessionStorage 中的用户信息
      sessionStorage.removeItem('userEmail');
      sessionStorage.removeItem('username');
      sessionStorage.removeItem('userRole');
      sessionStorage.removeItem('userIdentifier');

      this.$router.push({
        path: '/logIn',
        query: { role: userRole }
      });
    },
    getUserInitial() {
      if (this.userName && this.userName.length > 0) {
        return this.userName.charAt(0).toUpperCase();
      }
      return 'T';
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
  background-color: #263445;
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
  background-color: #1f2d40;
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
  background-color: #3498db;
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
  border-radius: 4px;
}

.toggle-btn:hover {
  color: #ffd04b;
  background-color: rgba(255, 255, 255, 0.1);
}

/* 菜单区域 */
.sidebar-menu {
  flex-grow: 1;
  border-right: none;
  overflow-y: auto;
  overflow-x: hidden;
  display: flex;
  flex-direction: column;
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

.menu-item.is-active {
  background-color: #1f2d40 !important;
}

/* 退出登录按钮样式 */
.logout-section {
  margin-top: auto;  /* 将退出部分推到底部 */
  padding-bottom: 10px;
}

.logout-btn {
  color: #e9e9e9;
}

.logout-btn i {
  margin-right: 10px;
  font-size: 16px;
  color: #ff6b6b;
}

.logout-btn:hover {
  background-color: #c0392b !important;
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

/* 悬浮展开按钮 */
.mobile-toggle-btn {
  display: none; /* 默认隐藏 */
  position: fixed;
  left: 10px;
  top: 10px;
  width: 40px;
  height: 40px;
  background-color: #263445;
  color: white;
  border-radius: 50%;
  box-shadow: 0 2px 8px rgba(0,0,0,0.3);
  z-index: 1001;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
}

.mobile-toggle-btn:hover {
  background-color: #344b66;
  transform: scale(1.05);
}

.mobile-toggle-btn i {
  font-size: 20px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .sidebar:not(.collapsed) {
    transform: translateX(0);
    width: 250px;
  }

  .sidebar.collapsed {
    width: 50px; /* 不完全隐藏，保留一个小的宽度 */
  }

  .user-panel {
    justify-content: center;
  }

  /* 添加悬浮展开按钮 */
  .sidebar.collapsed .toggle-btn {
    position: absolute;
    right: 5px;
    top: 15px;
    background-color: #263445;
    border-radius: 50%;
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    z-index: 1000;
  }

  /* 当导航栏折叠时，确保菜单项图标居中 */
  .sidebar.collapsed .el-menu-item i {
    margin: 0 auto;
  }

  /* 确保内容区域适应折叠的侧边栏 */
  .main-content {
    margin-left: 50px;
  }

  /* 在极小屏幕上显示悬浮按钮 */
  @media (max-width: 480px) {
    .sidebar.collapsed {
      width: 0; /* 在极小屏幕上完全隐藏 */
    }

    .mobile-toggle-btn {
      display: flex; /* 显示悬浮按钮 */
    }
  }
}
</style>