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

/**
 * Error handling helper
 */
const handleError = (error: unknown, message: string, action?: () => void) => {
  console.error(`Failed to ${message}:`, error)

  if (action) {
    action()
  }

  ElMessage.error(`${message}失败`)
}

/**
 * Success message helper
 */
const handleSuccess = (message: string) => {
  ElMessage.success(message)
}

/**
 * Warning message helper
 */
const handleWarning = (message: string) => {
  ElMessage.warning(message)
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
   * Add error message
   */
  const addErrorMessage = (content: string) => {
    addMessage({
      type: 'system',
      content
    })
  }

  /**
   * Remove message by content
   */
  const removeMessageByContent = (content: string) => {
    messages.value = messages.value.filter((m) => m.content !== content)
  }

  /**
   * Send a message and translate it to a PowerShell command
   * Requirements: 2.5, 2.6
   */
  const sendMessage = async (input: string): Promise<void> => {
    if (!input.trim()) {
      handleWarning('请输入内容')
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
          history: messages.value
            .filter((m) => m.type === 'user' && m.command)
            .slice(-5)
            .map((m) => ({
              input: m.content,
              command: m.command?.command || '',
              timestamp: m.timestamp.toISOString()
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

        handleSuccess('命令翻译成功')
      } else {
        throw new Error('翻译失败')
      }
    } catch (error: any) {
      handleError(error, '翻译', () => {
        addErrorMessage(`翻译失败: ${error.message || '未知错误'}`)
      })
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
      handleWarning('命令不能为空')
      return
    }

    // Set executing state
    isExecuting.value = true

    // Add system message indicating execution started
    const executingMessage = '正在执行命令...'
    addMessage({
      type: 'system',
      content: executingMessage
    })

    try {
      // Call execute API
      const response = await commandApi.execute({
        command,
        sessionId: sessionId.value,
        timeout: 30
      })

      // Remove the "executing" message
      removeMessageByContent(executingMessage)

      if (response.success) {
        const success = response.data.returnCode === 0 && !response.data.error

        // Update the message with command result if messageId provided
        if (messageId) {
          const message = messages.value.find((m) => m.id === messageId)
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
          handleSuccess('命令执行成功')
        } else {
          handleWarning('命令执行完成，但有错误')
        }
      } else {
        throw new Error('执行失败')
      }
    } catch (error: any) {
      handleError(error, '执行', () => {
        removeMessageByContent(executingMessage)
        addErrorMessage(`执行失败: ${error.message || '未知错误'}`)
      })
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

        response.data.items.reverse().forEach((item) => {
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
              error: item.error || null,
              executionTime: item.executionTime,
              success: item.success
            }
          })
        })

        // Prepend history messages to current messages
        messages.value = [...historyMessages, ...messages.value]

        handleSuccess(`已加载 ${response.data.items.length} 条历史记录`)
      }
    } catch (error: any) {
      handleError(error, '加载历史记录')
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
    handleSuccess('对话已清空')
  }

  /**
   * Regenerate command based on user feedback
   * Requirements: AI command improvement
   */
  const regenerateCommand = async (messageId: string): Promise<void> => {
    const message = messages.value.find((m) => m.id === messageId)
    if (!message || !message.command) {
      handleWarning('找不到要重新生成的命令')
      return
    }

    // Find the user input that generated this command
    const userMessageIndex = messages.value.findIndex((m) => m.id === messageId)
    const userMessage = messages.value[userMessageIndex - 1]
    
    if (!userMessage || userMessage.type !== 'user') {
      handleWarning('找不到对应的用户输入')
      return
    }

    // Set loading state
    isLoading.value = true

    // Add system message indicating regeneration
    addMessage({
      type: 'system',
      content: '正在根据反馈重新生成命令...'
    })

    try {
      // Call translate API with feedback context
      const response = await commandApi.translate({
        input: userMessage.content,
        context: {
          sessionId: sessionId.value,
          history: messages.value
            .filter((m) => m.type === 'user' && m.command)
            .slice(-5)
            .map((m) => ({
              input: m.content,
              command: m.command?.command || '',
              timestamp: m.timestamp.toISOString()
            }))
        },
        feedback: {
          previousCommand: message.command.command,
          feedback: 'incorrect',
          explanation: '用户认为生成的命令不正确，请重新生成更准确的命令'
        }
      })

      // Remove the "regenerating" message
      removeMessageByContent('正在根据反馈重新生成命令...')

      if (response.success) {
        // Update the existing message with new command
        message.command = {
          command: response.data.command,
          confidence: response.data.confidence,
          explanation: response.data.explanation,
          security: {
            level: response.data.security.level as any,
            warnings: response.data.security.warnings,
            requiresConfirmation: response.data.security.requiresConfirmation
          }
        }
        message.content = response.data.explanation || '命令已重新生成'

        handleSuccess('命令已重新生成')
      } else {
        throw new Error('重新生成失败')
      }
    } catch (error: any) {
      handleError(error, '重新生成', () => {
        addErrorMessage(`重新生成失败: ${error.message || '未知错误'}`)
      })
    } finally {
      isLoading.value = false
    }
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
    regenerateCommand,
    addMessage
  }
})
