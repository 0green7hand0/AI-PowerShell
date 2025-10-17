import { defineStore } from 'pinia'
import { ref } from 'vue'
import { commandApi } from '../api/command'
import { historyApi } from '../api/history'
import { ElMessage } from 'element-plus'

export interface Message {
  id: string
  type: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
  command?: {
    command: string
    confidence: number
    explanation: string
    security: {
      level: 'safe' | 'low' | 'medium' | 'high' | 'critical'
      warnings: string[]
      requiresConfirmation: boolean
    }
  }
  result?: {
    output: string
    error: string | null
    executionTime: number
    success: boolean
  }
}

export const useChatStore = defineStore('chat', () => {
  // State
  const messages = ref<Message[]>([])
  const currentInput = ref('')
  const isLoading = ref(false)
  const isExecuting = ref(false)
  const sessionId = ref(crypto.randomUUID())

  // Helper function to add a message
  const addMessage = (message: Omit<Message, 'id' | 'timestamp'>) => {
    messages.value.push({
      ...message,
      id: crypto.randomUUID(),
      timestamp: new Date()
    })
  }

  /**
   * Send a message and translate it to a PowerShell command
   * Requirements: 2.5, 2.6
   */
  const sendMessage = async (input: string): Promise<void> => {
    if (!input.trim()) {
      ElMessage.warning('请输入内容')
      return
    }

    // Add user message
    addMessage({
      type: 'user',
      content: input
    })

    // Set loading state
    isLoading.value = true

    try {
      // Call translate API
      const response = await commandApi.translate({
        input,
        context: {
          sessionId: sessionId.value,
          history: messages.value.slice(-5).map(m => ({
            type: m.type,
            content: m.content
          }))
        }
      })

      if (response.success) {
        // Add assistant message with command
        addMessage({
          type: 'assistant',
          content: response.data.explanation || '命令已生成',
          command: {
            command: response.data.command,
            confidence: response.data.confidence,
            explanation: response.data.explanation,
            security: {
              level: response.data.security.level as any,
              warnings: response.data.security.warnings,
              requiresConfirmation: response.data.security.requiresConfirmation
            }
          }
        })

        ElMessage.success('命令翻译成功')
      } else {
        throw new Error('翻译失败')
      }
    } catch (error: any) {
      console.error('Failed to translate command:', error)
      
      // Add error message
      addMessage({
        type: 'system',
        content: `翻译失败: ${error.message || '未知错误'}`
      })

      ElMessage.error('命令翻译失败')
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Execute a PowerShell command
   * Requirements: 2.6, 2.14
   */
  const executeCommand = async (command: string, messageId?: string): Promise<void> => {
    if (!command.trim()) {
      ElMessage.warning('命令不能为空')
      return
    }

    // Set executing state
    isExecuting.value = true

    // Add system message indicating execution started
    const executingMessageId = crypto.randomUUID()
    addMessage({
      type: 'system',
      content: '正在执行命令...'
    })

    try {
      // Call execute API
      const response = await commandApi.execute({
        command,
        sessionId: sessionId.value,
        timeout: 30
      })

      // Remove the "executing" message
      messages.value = messages.value.filter(m => m.content !== '正在执行命令...')

      if (response.success) {
        const success = response.data.returnCode === 0 && !response.data.error

        // Update the message with command result if messageId provided
        if (messageId) {
          const message = messages.value.find(m => m.id === messageId)
          if (message) {
            message.result = {
              output: response.data.output || '',
              error: response.data.error,
              executionTime: response.data.executionTime,
              success
            }
          }
        } else {
          // Add new message with result
          addMessage({
            type: 'assistant',
            content: success ? '命令执行成功' : '命令执行失败',
            result: {
              output: response.data.output || '',
              error: response.data.error,
              executionTime: response.data.executionTime,
              success
            }
          })
        }

        if (success) {
          ElMessage.success('命令执行成功')
        } else {
          ElMessage.warning('命令执行完成，但有错误')
        }
      } else {
        throw new Error('执行失败')
      }
    } catch (error: any) {
      console.error('Failed to execute command:', error)

      // Remove the "executing" message
      messages.value = messages.value.filter(m => m.content !== '正在执行命令...')

      // Add error message
      addMessage({
        type: 'system',
        content: `执行失败: ${error.message || '未知错误'}`
      })

      ElMessage.error('命令执行失败')
    } finally {
      isExecuting.value = false
    }
  }

  /**
   * Load chat history from the backend
   * Requirements: 2.14
   */
  const loadHistory = async (limit: number = 20): Promise<void> => {
    isLoading.value = true

    try {
      const response = await historyApi.getHistory({
        page: 1,
        limit
      })

      if (response.success && response.data.items.length > 0) {
        // Convert history items to messages
        const historyMessages: Message[] = []

        response.data.items.reverse().forEach(item => {
          // Add user input message
          historyMessages.push({
            id: crypto.randomUUID(),
            type: 'user',
            content: item.userInput,
            timestamp: new Date(item.timestamp)
          })

          // Add assistant message with command and result
          historyMessages.push({
            id: item.id,
            type: 'assistant',
            content: item.success ? '命令执行成功' : '命令执行失败',
            timestamp: new Date(item.timestamp),
            command: {
              command: item.command,
              confidence: 0.9, // History doesn't store confidence
              explanation: '',
              security: {
                level: 'safe',
                warnings: [],
                requiresConfirmation: false
              }
            },
            result: {
              output: item.output || '',
              error: item.error,
              executionTime: item.executionTime,
              success: item.success
            }
          })
        })

        // Prepend history messages to current messages
        messages.value = [...historyMessages, ...messages.value]

        ElMessage.success(`已加载 ${response.data.items.length} 条历史记录`)
      }
    } catch (error: any) {
      console.error('Failed to load history:', error)
      ElMessage.error('加载历史记录失败')
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Clear all messages and start a new session
   */
  const clearChat = () => {
    messages.value = []
    sessionId.value = crypto.randomUUID()
    currentInput.value = ''
    ElMessage.info('对话已清空')
  }

  return {
    // State
    messages,
    currentInput,
    isLoading,
    isExecuting,
    sessionId,

    // Actions
    sendMessage,
    executeCommand,
    loadHistory,
    clearChat,
    addMessage
  }
})
