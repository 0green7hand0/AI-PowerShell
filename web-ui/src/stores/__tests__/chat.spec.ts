import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useChatStore } from '../chat'
import { commandApi } from '../../api/command'
import { historyApi } from '../../api/history'

// Mock the APIs
vi.mock('../../api/command')
vi.mock('../../api/history')
vi.mock('element-plus', () => ({
  ElMessage: {
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn(),
    info: vi.fn()
  }
}))

describe('ChatStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('Initial State', () => {
    it('should initialize with empty messages', () => {
      const store = useChatStore()
      expect(store.messages).toEqual([])
    })

    it('should initialize with empty currentInput', () => {
      const store = useChatStore()
      expect(store.currentInput).toBe('')
    })

    it('should initialize with isLoading false', () => {
      const store = useChatStore()
      expect(store.isLoading).toBe(false)
    })

    it('should initialize with isExecuting false', () => {
      const store = useChatStore()
      expect(store.isExecuting).toBe(false)
    })

    it('should initialize with a sessionId', () => {
      const store = useChatStore()
      expect(store.sessionId).toBeTruthy()
      expect(typeof store.sessionId).toBe('string')
    })
  })

  describe('sendMessage', () => {
    it('should add user message and translate command', async () => {
      const store = useChatStore()
      const mockResponse = {
        success: true,
        data: {
          command: 'Get-Process',
          confidence: 0.95,
          explanation: 'Get all processes',
          security: {
            level: 'safe',
            warnings: [],
            requiresConfirmation: false
          }
        }
      }

      vi.mocked(commandApi.translate).mockResolvedValue(mockResponse)

      await store.sendMessage('显示所有进程')

      expect(store.messages).toHaveLength(2)
      expect(store.messages[0].type).toBe('user')
      expect(store.messages[0].content).toBe('显示所有进程')
      expect(store.messages[1].type).toBe('assistant')
      expect(store.messages[1].command?.command).toBe('Get-Process')
    })

    it('should not send empty message', async () => {
      const store = useChatStore()
      await store.sendMessage('')
      expect(store.messages).toHaveLength(0)
    })

    it('should handle translation error', async () => {
      const store = useChatStore()
      vi.mocked(commandApi.translate).mockRejectedValue(new Error('API Error'))

      await store.sendMessage('test input')

      expect(store.messages).toHaveLength(2)
      expect(store.messages[1].type).toBe('system')
      expect(store.messages[1].content).toContain('翻译失败')
    })

    it('should set loading state during translation', async () => {
      const store = useChatStore()
      const mockResponse = {
        success: true,
        data: {
          command: 'Get-Date',
          confidence: 0.9,
          explanation: 'Get current date',
          security: {
            level: 'safe',
            warnings: [],
            requiresConfirmation: false
          }
        }
      }

      let loadingDuringCall = false
      vi.mocked(commandApi.translate).mockImplementation(async () => {
        loadingDuringCall = store.isLoading
        return mockResponse
      })

      await store.sendMessage('显示时间')

      expect(loadingDuringCall).toBe(true)
      expect(store.isLoading).toBe(false)
    })
  })

  describe('executeCommand', () => {
    it('should execute command and add result', async () => {
      const store = useChatStore()
      const mockResponse = {
        success: true,
        data: {
          output: 'Command output',
          error: null,
          executionTime: 0.5,
          returnCode: 0
        }
      }

      vi.mocked(commandApi.execute).mockResolvedValue(mockResponse)

      await store.executeCommand('Get-Process')

      const resultMessage = store.messages.find(m => m.result !== undefined)
      expect(resultMessage).toBeDefined()
      expect(resultMessage?.result?.output).toBe('Command output')
      expect(resultMessage?.result?.success).toBe(true)
    })

    it('should not execute empty command', async () => {
      const store = useChatStore()
      await store.executeCommand('')
      expect(store.messages).toHaveLength(0)
    })

    it('should handle execution error', async () => {
      const store = useChatStore()
      vi.mocked(commandApi.execute).mockRejectedValue(new Error('Execution failed'))

      await store.executeCommand('Get-Process')

      const errorMessage = store.messages.find(m => m.content.includes('执行失败'))
      expect(errorMessage).toBeDefined()
    })

    it('should set executing state during execution', async () => {
      const store = useChatStore()
      const mockResponse = {
        success: true,
        data: {
          output: 'output',
          error: null,
          executionTime: 0.5,
          returnCode: 0
        }
      }

      let executingDuringCall = false
      vi.mocked(commandApi.execute).mockImplementation(async () => {
        executingDuringCall = store.isExecuting
        return mockResponse
      })

      await store.executeCommand('Get-Date')

      expect(executingDuringCall).toBe(true)
      expect(store.isExecuting).toBe(false)
    })

    it('should handle command with non-zero return code', async () => {
      const store = useChatStore()
      const mockResponse = {
        success: true,
        data: {
          output: '',
          error: 'Command failed',
          executionTime: 0.3,
          returnCode: 1
        }
      }

      vi.mocked(commandApi.execute).mockResolvedValue(mockResponse)

      await store.executeCommand('Invalid-Command')

      const resultMessage = store.messages.find(m => m.result !== undefined)
      expect(resultMessage?.result?.success).toBe(false)
      expect(resultMessage?.result?.error).toBe('Command failed')
    })
  })

  describe('loadHistory', () => {
    it('should load history and convert to messages', async () => {
      const store = useChatStore()
      const mockHistory = {
        success: true,
        data: {
          items: [
            {
              id: '1',
              userInput: 'test input',
              command: 'Get-Process',
              success: true,
              output: 'output',
              error: null,
              executionTime: 0.5,
              timestamp: new Date().toISOString()
            }
          ],
          total: 1,
          page: 1,
          limit: 20
        }
      }

      vi.mocked(historyApi.getHistory).mockResolvedValue(mockHistory as any)

      await store.loadHistory()

      expect(store.messages.length).toBeGreaterThan(0)
      expect(store.messages[0].type).toBe('user')
      expect(store.messages[0].content).toBe('test input')
      expect(store.messages[1].type).toBe('assistant')
      expect(store.messages[1].command?.command).toBe('Get-Process')
    })

    it('should handle empty history', async () => {
      const store = useChatStore()
      const mockHistory = {
        success: true,
        data: {
          items: [],
          total: 0,
          page: 1,
          limit: 20
        }
      }

      vi.mocked(historyApi.getHistory).mockResolvedValue(mockHistory as any)

      await store.loadHistory()

      expect(store.messages).toHaveLength(0)
    })

    it('should handle history loading error', async () => {
      const store = useChatStore()
      vi.mocked(historyApi.getHistory).mockRejectedValue(new Error('API Error'))

      await store.loadHistory()

      expect(store.messages).toHaveLength(0)
    })

    it('should prepend history to existing messages', async () => {
      const store = useChatStore()
      
      // Add a current message
      store.addMessage({
        type: 'user',
        content: 'current message'
      })

      const mockHistory = {
        success: true,
        data: {
          items: [
            {
              id: '1',
              userInput: 'old input',
              command: 'Get-Date',
              success: true,
              output: 'output',
              error: null,
              executionTime: 0.3,
              timestamp: new Date().toISOString()
            }
          ],
          total: 1,
          page: 1,
          limit: 20
        }
      }

      vi.mocked(historyApi.getHistory).mockResolvedValue(mockHistory as any)

      await store.loadHistory()

      expect(store.messages.length).toBeGreaterThan(1)
      expect(store.messages[0].content).toBe('old input')
      expect(store.messages[store.messages.length - 1].content).toBe('current message')
    })
  })

  describe('clearChat', () => {
    it('should clear all messages', () => {
      const store = useChatStore()
      store.addMessage({ type: 'user', content: 'test' })
      
      store.clearChat()

      expect(store.messages).toHaveLength(0)
    })

    it('should generate new sessionId', () => {
      const store = useChatStore()
      const oldSessionId = store.sessionId

      store.clearChat()

      expect(store.sessionId).not.toBe(oldSessionId)
    })

    it('should clear currentInput', () => {
      const store = useChatStore()
      store.currentInput = 'test input'

      store.clearChat()

      expect(store.currentInput).toBe('')
    })
  })

  describe('addMessage', () => {
    it('should add message with id and timestamp', () => {
      const store = useChatStore()
      
      store.addMessage({
        type: 'user',
        content: 'test message'
      })

      expect(store.messages).toHaveLength(1)
      expect(store.messages[0].id).toBeTruthy()
      expect(store.messages[0].timestamp).toBeInstanceOf(Date)
    })

    it('should add message with command data', () => {
      const store = useChatStore()
      
      store.addMessage({
        type: 'assistant',
        content: 'Command generated',
        command: {
          command: 'Get-Process',
          confidence: 0.95,
          explanation: 'Get all processes',
          security: {
            level: 'safe',
            warnings: [],
            requiresConfirmation: false
          }
        }
      })

      expect(store.messages[0].command).toBeDefined()
      expect(store.messages[0].command?.command).toBe('Get-Process')
    })
  })
})
