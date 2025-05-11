<template>
  <div class="ai-chat-page">
    <!-- 导航侧边栏 -->
    <StudentNavbar />

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 历史对话面板 -->
      <div class="history-panel">
        <h3>历史对话</h3>
        <div class="search-container">
          <t-input
            v-model="searchKeyword"
            placeholder="搜索历史对话"
            clearable
            prefixIcon="search"
            @clear="loadChatHistory"
            @change="searchHistory"
          />
        </div>
        <div id="history-list">
          <div v-if="displayedHistory.length === 0" class="history-item">暂无历史记录</div>
          <div v-for="history in displayedHistory" :key="history.id" class="history-item">
            <div class="title">{{ getFirstUserMessage(history) }}</div>
            <div class="date">{{ new Date(history.created_at).toLocaleString() }}</div>
            <div class="history-controls">
              <t-button theme="primary" size="small" variant="text" @click="loadChat(history.id)">查看</t-button>
              <t-button theme="danger" size="small" variant="text" @click="deleteChat(history.id)">删除</t-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 聊天内容区 -->
      <div class="container">
        <div class="header">
          <div class="header-content">
            <h1>AI对话助手</h1>
            <div class="header-controls">
              <t-radio-group v-model="selectedModelType" @change="switchModel">
                <t-radio-button value="local">本地模型</t-radio-button>
                <t-radio-button value="api">API模型</t-radio-button>
              </t-radio-group>
              <span class="model-name">当前模型: {{ currentModelName }}</span>
              <t-button theme="primary" @click="startNewChat">新对话</t-button>
            </div>
          </div>
        </div>

        <!-- 使用TDesign AI Chat组件 - 参考示例代码 -->
        <div class="chat-wrapper">
          <div class="chat-messages">
            <!-- 动态消息列表 -->
            <div v-if="currentMessages && currentMessages.length > 0">
              <t-chat-item
                v-for="(message, index) in currentMessages"
                :key="index"
                :avatar="message.sender === 'ai' ? '/static/ai-avatar.jpg' : '/static/user-avatar.jpg'"
                :name="message.sender === 'ai' ? 'AI助手' : '用户'"
                :role="message.sender === 'ai' ? 'assistant' : 'user'"
                :content="message.content"
                variant="outline"
              ></t-chat-item>
            </div>
            <!-- 默认欢迎消息 -->
            <div v-else>
              <t-chat-item
                avatar="/static/ai-avatar.jpg"
                name="AI助手"
                role="assistant"
                content="您好！我是AI助手，有什么可以帮您的？"
                variant="outline"
              ></t-chat-item>
            </div>
          </div>

          <!-- 输入框 -->
          <div class="chat-input-container">
            <t-textarea
              ref="chatInput"
              v-model="userMessage"
              :loading="isLoading"
              :disabled="isLoading"
              placeholder="请输入您的问题... (Shift+回车换行，回车发送)"
              @keyup.enter="sendMessage"
              @keydown.enter.prevent
              @enter="sendMessage"
              enterkeyhint="send"
              class="chat-input"
              :autosize="{ minRows: 1, maxRows: 5 }"
            />
            <t-button theme="primary" :loading="isLoading" :disabled="isLoading" @click="sendMessage">
              <template #icon><t-icon name="send" /></template>
              发送
            </t-button>
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
      displayedHistory: [], // 用于显示过滤后的历史记录
      searchKeyword: '', // 搜索关键词
      isLoading: false, // 加载状态
      streamController: null,
      selectedModelType: 'local', // 默认使用本地模型
      currentModelName: 'qwen3:8b', // 默认模型名称
      modelConfig: null, // 存储完整的模型配置
      handleKeyPress: null // 存储键盘事件处理函数
    }
  },
  mounted() {
    // 初始化空数组，确保组件能正确渲染
    this.currentMessages = []

    // 获取配置
    this.getModelConfig()

    // 延迟加载历史记录和开始新对话，确保组件已完全渲染
    this.$nextTick(() => {
      setTimeout(() => {
        this.loadChatHistory()

        // 如果没有历史记录，开始新对话
        if (this.currentMessages.length === 0) {
          this.startNewChat()
        }

        // 添加测试消息，用于调试
        console.log('添加测试消息')
        this.currentMessages = [
          { sender: 'ai', content: '您好！我是AI助手，有什么可以帮您的？' },

        ]
        console.log('当前消息数组:', this.currentMessages)

        // 强制更新视图
        this.$forceUpdate()

        // 添加原生事件监听器
        setTimeout(() => {
          // 获取输入框的DOM元素
          const inputElement = this.$refs.chatInput?.$el?.querySelector('textarea');
          if (inputElement) {
            console.log('找到文本区域元素，添加原生事件监听器');
            // 添加原生事件监听器
            this.handleKeyPress = (event) => {
              if (event.key === 'Enter') {
                if (event.shiftKey) {
                  // Shift+回车插入换行符
                  event.preventDefault();

                  // 获取当前光标位置
                  const cursorPos = inputElement.selectionStart;
                  const textBefore = this.userMessage.substring(0, cursorPos);
                  const textAfter = this.userMessage.substring(cursorPos);

                  // 在光标位置插入换行符
                  this.userMessage = textBefore + '\n' + textAfter;

                  // 设置新的光标位置
                  this.$nextTick(() => {
                    inputElement.selectionStart = inputElement.selectionEnd = cursorPos + 1;
                  });

                  console.log('已插入换行符');
                } else {
                  // 普通回车发送消息
                  event.preventDefault();
                  this.sendMessage(event);
                }
              }
            };
            inputElement.addEventListener('keypress', this.handleKeyPress);
          } else {
            console.error('未找到输入框元素');
          }
        }, 1000);
      }, 500)
    })
  },
  beforeUnmount() {
    // 移除原生事件监听器
    const inputElement = this.$refs.chatInput?.$el?.querySelector('textarea');
    if (inputElement) {
      console.log('移除原生事件监听器');
      // 移除事件监听器
      inputElement.removeEventListener('keypress', this.handleKeyPress);
    }
  },
  watch: {
    // 监听聊天消息变化，自动滚动到底部
    currentMessages: {
      deep: true,
      immediate: true, // 立即触发一次
      handler(newVal) {
        console.log('消息数组变化:', newVal)

        // 确保DOM更新后再滚动
        this.$nextTick(() => {
          setTimeout(() => {
            const chatContent = document.querySelector('.chat-messages');
            if (chatContent) {
              chatContent.scrollTop = chatContent.scrollHeight + 200; // 添加额外偏移，确保消息完全可见
              console.log('滚动到底部, 高度:', chatContent.scrollHeight)
            } else {
              console.error('找不到聊天内容元素')
            }

            // 强制更新视图
            this.$forceUpdate()
          }, 200); // 增加延迟时间，确保DOM已更新
        });
      }
    }
  },
  methods: {
    // 搜索历史记录
    searchHistory() {
      if (!this.searchKeyword.trim()) {
        this.displayedHistory = [...this.chatHistory];
        return;
      }

      const keyword = this.searchKeyword.toLowerCase().trim();
      this.displayedHistory = this.chatHistory.filter(history => {
        // 在消息内容中搜索关键词
        if (history.messages && Array.isArray(history.messages)) {
          return history.messages.some(msg =>
            msg.content.toLowerCase().includes(keyword)
          );
        }
        return false;
      });
    },

    // 开始新对话
    startNewChat() {
      this.currentChatId = null
      this.isNewChat = true

      // 使用直接赋值而不是push，确保响应式更新
      this.currentMessages = [
        { sender: 'ai', content: '您好！我是AI助手，有什么可以帮您的？' }
      ]
      console.log('开始新对话，消息数组:', this.currentMessages)
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
    async sendMessage(event) {
      // 检查是否是回车键事件，并且是否按下了Shift键（Shift+Enter用于换行）
      if (event && event.key === 'Enter' && event.shiftKey) {
        console.log('Shift+Enter被按下，不发送消息');
        return; // 如果是Shift+Enter，不发送消息
      }

      // 添加调试日志
      console.log('sendMessage被调用', event ? event.type : '无事件类型')

      const message = this.userMessage.trim()
      if (!message) return

      console.log('发送消息:', message)

      // 创建新的消息数组，包含用户消息
      const newMessages = [...this.currentMessages, { sender: 'user', content: message }]
      this.currentMessages = newMessages

      this.userMessage = ''
      this.isLoading = true

      // 如果有正在进行的请求，终止它
      if (this.streamController) {
        this.streamController.abort()
      }

      // 创建新的AbortController用于可能需要中断的请求
      this.streamController = new AbortController()

      // 添加一个空的AI消息，用于逐步填充内容
      this.currentMessages = [...this.currentMessages, { sender: 'ai', content: '' }]
      const aiMessageIndex = this.currentMessages.length - 1

      try {
        // 使用EventSource进行SSE连接
        const response = await fetch('/api/chat/message', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            message,
            messageHistory: this.currentMessages.slice(0, -2) // 不包括用户刚发送的消息和空的AI消息
          }),
          signal: this.streamController.signal
        })

        // 确保响应是可读流
        const reader = response.body.getReader()
        const decoder = new TextDecoder()
        let completeResponse = ''

        // 读取流
        let reading = true;
        while (reading) {
          const { value, done } = await reader.read()
          if (done) {
            reading = false;
            break;
          }

          // 解码收到的数据
          const chunk = decoder.decode(value, { stream: true })

          // 处理SSE格式数据
          const lines = chunk.split('\n\n')
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.substring(6))

                if (data.error) {
                  // 处理错误
                  const updatedMessages = [...this.currentMessages]
                  updatedMessages[aiMessageIndex].content = '抱歉，发生了错误。请稍后重试。'
                  this.currentMessages = updatedMessages
                  break
                } else if (data.done) {
                  // 流结束
                  this.isLoading = false

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
                  break
                } else if (data.token) {
                  // 添加新token到当前AI消息
                  completeResponse += data.token

                  // 创建新的消息数组，更新AI消息内容
                  const updatedMessages = [...this.currentMessages]
                  updatedMessages[aiMessageIndex].content = completeResponse
                  this.currentMessages = updatedMessages
                }
              } catch (e) {
                console.error('解析SSE数据出错:', e)
              }
            }
          }
        }
      } catch (error) {
        if (error.name === 'AbortError') {
          console.log('请求被用户取消')
        } else {
          console.error('发送消息失败:', error)
          const updatedMessages = [...this.currentMessages]
          updatedMessages[aiMessageIndex].content = '抱歉，发生了错误。请稍后重试。'
          this.currentMessages = updatedMessages
        }
      } finally {
        this.isLoading = false
        this.streamController = null
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
          // 初始化显示的历史记录
          this.displayedHistory = [...this.chatHistory]

          // 如果有搜索关键词，应用搜索过滤
          if (this.searchKeyword.trim()) {
            this.searchHistory()
          }
        } else {
          console.error('获取的历史记录不是数组格式:', data)
          this.chatHistory = []
          this.displayedHistory = []
        }
      } catch (error) {
        console.error('加载历史记录失败:', error)
        this.chatHistory = []
        this.displayedHistory = []
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
    },

    // 获取当前模型配置
    async getModelConfig() {
      try {
        const response = await fetch('/api/chat/model-config')
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const data = await response.json()
        if (data.success && data.modelInfo) {
          this.selectedModelType = data.modelInfo.modelType
          this.currentModelName = data.modelInfo.currentModel
          this.modelConfig = data.modelInfo.config
          console.log('当前模型配置:', data.modelInfo)
        }
      } catch (error) {
        console.error('获取模型配置失败:', error)
        // 使用默认配置
        this.selectedModelType = 'local'
        this.currentModelName = 'qwen3:8b'
      }
    },

    // 切换模型类型
    async switchModel() {
      try {
        this.typingStatus = '正在切换模型...'

        const response = await fetch('/api/chat/switch-model', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            modelType: this.selectedModelType
          })
        })

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const data = await response.json()
        if (data.success) {
          this.currentModelName = data.modelInfo.currentModel
          this.modelConfig = data.modelInfo.config

          // 显示成功消息
          this.currentMessages.push({
            sender: 'ai',
            content: `已切换到${this.selectedModelType === 'local' ? '本地' : 'API'}模型: ${this.currentModelName}`
          })
        } else {
          throw new Error(data.message || '切换模型失败')
        }
      } catch (error) {
        console.error('切换模型失败:', error)
        this.currentMessages.push({
          sender: 'ai',
          content: `切换模型失败: ${error.message}`
        })

        // 恢复之前的选择
        await this.getModelConfig()
      } finally {
        this.typingStatus = ''
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

.search-container {
  margin-bottom: 15px;
}

.search-container :deep(.t-input) {
  width: 100%;
}

.search-container :deep(.t-input__inner) {
  font-size: 14px;
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
  position: relative;
}

.header {
  margin-bottom: 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 15px;
}

.model-name {
  font-size: 14px;
  color: #666;
  background: #f0f9ff;
  padding: 4px 8px;
  border-radius: 4px;
}

/* 聊天组件样式 */
.chat-wrapper {
  width: 100%;
  height: calc(100vh - 120px);
  display: flex;
  flex-direction: column;
  margin-bottom: 20px;
  overflow: hidden;
  border-radius: 8px;
  border: 1px solid #eee;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background-color: #f9f9f9;
}

/* 设置t-space样式 */
:deep(.t-space) {
  width: 100%;
}

/* 设置t-chat-item样式 */
:deep(.t-chat-item) {
  margin-bottom: 16px;
  width: 100%;
}

:deep(.t-chat-item__content) {
  max-width: 80%;
  word-break: break-word;
}

:deep(.t-chat-item__avatar) {
  flex-shrink: 0;
}

/* 输入框容器样式 */
.chat-input-container {
  display: flex;
  padding: 15px;
  border-top: 1px solid #eee;
  gap: 10px;
  background-color: #fff;
}

.chat-input {
  flex: 1;
}

/* 自定义文本区域样式 */
:deep(.t-textarea) {
  width: 100%;
  resize: none;
  border-radius: 4px;
}

:deep(.t-textarea__inner) {
  min-height: 40px;
  padding: 8px 12px;
  line-height: 1.5;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .history-panel {
    width: 150px;
    left: 50px; /* 适应折叠后的导航栏宽度 */
  }

  .container {
    margin-left: 150px;
  }

  .main-content {
    margin-left: 50px; /* 适应折叠后的导航栏宽度 */
  }

  .header-controls {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}

@media (max-width: 480px) {
  .history-panel {
    width: 100%;
    left: 0;
    z-index: 1000;
    background: rgba(255, 255, 255, 0.95);
    transform: translateX(-100%);
    transition: transform 0.3s ease;
  }

  .history-panel.visible {
    transform: translateX(0);
  }

  .container {
    margin-left: 0;
    padding: 10px;
  }
}
</style>