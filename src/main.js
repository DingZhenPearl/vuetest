import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

// 引入TDesign
import TDesign from 'tdesign-vue-next'
import 'tdesign-vue-next/es/style/index.css'

// 引入TDesign Chat组件
import TDesignChat from '@tdesign-vue-next/chat'
import '@tdesign-vue-next/chat/dist/tdesign-vue-chat.css'

const app = createApp(App)
app.use(router)
app.use(ElementPlus)
app.use(TDesign)
app.use(TDesignChat)

// 添加全局方法，用于清除缓存
app.config.globalProperties.$clearCache = function(studentId) {
  if (!studentId) return;

  try {
    // 清除所有缓存数据
    localStorage.removeItem(`recommendations_${studentId}`);
    localStorage.removeItem(`progress_data_${studentId}`);
    localStorage.removeItem(`activities_${studentId}`);
    localStorage.removeItem(`user_stats_${studentId}`);
    console.log('已清除所有缓存数据');
  } catch (error) {
    console.error('清除缓存数据失败:', error);
  }
}

app.mount('#app')
