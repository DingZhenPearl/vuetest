<template>
  <div class="ai-chat-page">
    <!-- 导航侧边栏 -->
    <StudentNavbar />

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 历史对话面板 -->
      <div class="history-panel">
        <h3>历史对话</h3>
        <div id="history-list">
          <div v-if="chatHistory.length === 0" class="history-item">暂无历史记录</div>
          <div v-for="history in chatHistory" :key="history.id" class="history-item">
            <div class="title">{{ getFirstUserMessage(history) }}</div>
            <div class="date">{{ new Date(history.created_at).toLocaleString() }}</div>
            <div class="history-controls">
              <button @click="loadChat(history.id)">查看</button>
              <button class="delete-btn" @click="deleteChat(history.id)">删除</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 聊天内容区 -->
      <div class="container">
        <div class="header">
          <div class="header-content">
            <h1>AI对话助手</h1>
            <button @click="startNewChat" class="new-chat-btn">新对话</button>
          </div>
        </div>
        
        <!-- 聊天消息容器 -->
        <div id="chat-container" ref="chatContainer" class="chat-container">
          <div v-for="(message, index) in currentMessages" :key="index" 
               :class="['message-container', message.sender === 'user' ? 'user-message-container' : '']">
            <img :src="message.sender === 'ai' ? '/static/ai-avatar.jpg' : '/static/user-avatar.jpg'" 
                 :alt="message.sender === 'ai' ? 'AI头像' : '用户头像'" 
                 class="avatar">
            <div :class="['message-bubble', `${message.sender}-message`]">{{ message.content }}</div>
          </div>
        </div>

        <!-- 底部输入区 -->
        <div class="bottom-container">
          <div class="status" id="status">{{ typingStatus }}</div>
          <div class="input-container">
            <input 
              type="text" 
              v-model="userMessage" 
              @keypress.enter="sendMessage" 
              placeholder="请输入您的问题..." 
              class="user-input">
            <button @click="sendMessage" class="send-btn">发送</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import StudentNavbar from '@/components/student/StudentNavbar.vue'

export default {
  name: 'StudentAiChat',
  components: {
    StudentNavbar
  },
  data() {
    return {
      currentChatId: null,
      currentMessages: [],
      isNewChat: true,
      userMessage: '',
      chatHistory: [],
      typingStatus: ''
    }
  },
  mounted() {
    this.loadChatHistory()
    this.startNewChat()
  },
  updated() {
    this.scrollToBottom()
  },
  methods: {
    scrollToBottom() {
      if (this.$refs.chatContainer) {
        this.$refs.chatContainer.scrollTop = this.$refs.chatContainer.scrollHeight
      }
    },
    
    // 开始新对话
    startNewChat() {
      this.currentMessages = []
      this.currentChatId = null
      this.isNewChat = true
      
      const welcomeMessage = '您好！我是AI助手，有什么可以帮您的？'
      this.currentMessages.push({ sender: 'ai', content: welcomeMessage })
    },
    
    // 显示AI正在输入状态
    showTypingIndicator() {
      this.typingStatus = 'AI正在输入...'
    },
    
    // 隐藏AI正在输入状态
    hideTypingIndicator() {
      this.typingStatus = ''
    },
    
    // 发送消息到服务器
    async sendMessage() {
      const message = this.userMessage.trim()
      if (!message) return
      
      // 添加用户消息到界面
      this.currentMessages.push({ sender: 'user', content: message })
      this.userMessage = ''
      this.showTypingIndicator()
      
      try {
        const response = await fetch('/api/chat/message', { // 更新API路径
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ 
            message,
            messageHistory: this.currentMessages.slice(0, -1)
          })
        })
        
        const data = await response.json()
        
        if (data.success) {
          // 添加AI回复
          this.currentMessages.push({ sender: 'ai', content: data.message })
          
          // 保存或更新聊天记录
          if (this.isNewChat) {
            const result = await this.saveChat()
            if (result && result.success) {
              this.currentChatId = result.id
              this.isNewChat = false
              await this.loadChatHistory()
            }
          } else {
            await this.updateChat()
          }
        } else {
          this.currentMessages.push({ sender: 'ai', content: '抱歉，发生了错误。请稍后重试。' })
        }
      } catch (error) {
        console.error('发送消息失败:', error)
        this.currentMessages.push({ sender: 'ai', content: '抱歉，发生了错误。请稍后重试。' })
      } finally {
        this.hideTypingIndicator()
      }
    },
    
    // 加载聊天历史
    async loadChatHistory() {
      const userEmail = sessionStorage.getItem('userEmail')
      if (!userEmail) {
        console.log('用户未登录')
        return
      }

      try {
        const response = await fetch('/api/chat/history', { // 更新API路径
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ email: userEmail })
        })

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const data = await response.json()
        
        console.log('获取到的聊天记录数据:', data)
        
        if (Array.isArray(data)) {
          this.chatHistory = data
        } else {
          console.error('获取的历史记录不是数组格式:', data)
          this.chatHistory = []
        }
      } catch (error) {
        console.error('加载历史记录失败:', error)
        this.chatHistory = []
      }
    },
    
    // 获取对话中用户的第一条消息作为标题
    getFirstUserMessage(history) {
      let firstUserMessage = '未命名对话'
      if (history.messages && Array.isArray(history.messages)) {
        const firstMsg = history.messages.find(msg => msg.sender === 'user')
        if (firstMsg) {
          firstUserMessage = firstMsg.content.length > 20 
            ? firstMsg.content.substring(0, 20) + '...'
            : firstMsg.content
        }
      }
      return firstUserMessage
    },
    
    // 加载特定的聊天记录
    async loadChat(chatId) {
      try {
        const response = await fetch(`/api/chat/${chatId}`)
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        
        const chat = await response.json()
        
        if (chat && chat.messages) {
          this.currentChatId = chatId
          this.currentMessages = chat.messages
          this.isNewChat = false
        } else {
          console.error('加载的聊天记录格式不正确:', chat)
          this.currentMessages.push({ 
            sender: 'ai', 
            content: '加载历史对话失败，请尝试开始新的对话。' 
          })
        }
      } catch (error) {
        console.error('加载对话失败:', error)
        this.currentMessages.push({ 
          sender: 'ai', 
          content: '加载历史对话失败，请尝试开始新的对话。' 
        })
      }
    },
    
    // 保存新的聊天记录
    async saveChat() {
      const userEmail = sessionStorage.getItem('userEmail')
      try {
        const response = await fetch('/api/chat/save', { // 更新API路径
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            email: userEmail,
            messages: this.currentMessages
          })
        })
        return await response.json()
      } catch (error) {
        console.error('保存对话失败:', error)
        return null
      }
    },
    
    // 更新现有聊天记录
    async updateChat() {
      try {
        await fetch('/api/chat/update', { // 更新API路径
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            chatId: this.currentChatId,
            messages: this.currentMessages
          })
        })
      } catch (error) {
        console.error('更新对话失败:', error)
      }
    },
    
    // 删除聊天记录
    async deleteChat(chatId) {
      if (!confirm('确定要删除这条对话记录吗？')) return
      
      try {
        await fetch(`/api/chat/${chatId}`, {
          method: 'DELETE'
        })
        
        if (chatId === this.currentChatId) {
          this.startNewChat()
        }
        await this.loadChatHistory()
      } catch (error) {
        console.error('删除对话失败:', error)
      }
    }
  }
}
</script>

<style scoped>
.ai-chat-page {
  display: flex;
  min-height: 100vh;
}

/* 历史记录面板样式 */
.history-panel {
  position: fixed;
  left: 250px;
  top: 0;
  width: 200px;
  height: 100vh;
  background: #f8f9fa;
  border-right: 1px solid #ddd;
  padding: 15px;
  overflow-y: auto;
  box-sizing: border-box;
  z-index: 900;
}

.history-item {
  padding: 10px;
  margin-bottom: 8px;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
  border: 1px solid #e0e0e0;
}

.history-item:hover {
  background: #e3f2fd;
}

.history-item .title {
  font-weight: bold;
  margin-bottom: 5px;
  font-size: 14px;
}

.history-item .date {
  font-size: 12px;
  color: #666;
}

.history-controls {
  display: flex;
  gap: 5px;
  margin-top: 5px;
}

.history-controls button {
  padding: 3px 8px;
  font-size: 12px;
  border: none;
  border-radius: 3px;
  cursor: pointer;
}

.delete-btn {
  background: #ff4444;
  color: white;
}

/* 主内容区样式 */
.main-content {
  margin-left: 250px;
  width: 100%;
}

.container {
  margin-left: 200px;
  height: 100vh;
  display: flex;
  flex-direction: column;
  padding: 20px;
  box-sizing: border-box;
}

.header {
  margin-bottom: 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.new-chat-btn {
  padding: 8px 16px;
  background: #2c3e50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.new-chat-btn:hover {
  background: #34495e;
}

.chat-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: white;
  border-radius: 8px;
  margin-bottom: 20px;
  height: calc(100vh - 180px);
}

.bottom-container {
  position: fixed;
  bottom: 20px;
  left: 470px;
  right: 20px;
  background: white;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
  z-index: 800;
}

.status {
  font-size: 12px;
  color: #666;
  margin-bottom: 5px;
  height: 15px;
}

.input-container {
  display: flex;
  gap: 10px;
}

.user-input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.send-btn {
  padding: 10px 20px;
  background: #2c3e50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.send-btn:hover {
  background: #34495e;
}

/* 消息样式 */
.message-container {
  display: flex;
  align-items: start;
  margin-bottom: 15px;
}

.message-container.user-message-container {
  flex-direction: row-reverse;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  margin: 0 10px;
}

.message-bubble {
  background: #f1f1f1;
  padding: 10px 15px;
  border-radius: 8px;
  max-width: 70%;
}

.ai-message {
  background: #e3f2fd;
}

.user-message {
  background: #dcf8c6;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .history-panel {
    width: 150px;
  }
  
  .container {
    margin-left: 150px;
  }
  
  .bottom-container {
    left: 420px;
  }
}
</style>