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
app.mount('#app')
