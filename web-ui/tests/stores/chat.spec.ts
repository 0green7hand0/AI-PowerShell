import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useChatStore } from '@/stores/chat'
import * as commandApi from '@/api/command'

vi.mock('@/api/command')

describe('Chat Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('initializes with empty messages', () => {
    const store = useChatStore()
    
    expect(store.messages).toEqual([])
    expect(store.isLoading).toBe(false)
  })

  it('adds user message when sending', async () => {
    const store = useChatStore()
    const mockResponse = {
      command: 'Get-Process',
      confidence: 0.95,
      explanation: 'Get all processes',
      security: {
        level: 'safe',
        warnings: [],
        requiresConfirmation: false
      }
    }
    
    vi.mocked(commandApi.translateCommand).mockResolvedValue(mockResponse)
    
    await store.sendMessage('显示所有进程')
    
    expect(store.messages.length).toBeGreaterThan(0)
    expect(store.messages[0].type).toBe('user')
    expect(store.messages[0].content).toBe('显示所有进程')
  })

  it('adds assistant message with command after translation', async () => {
    const store = useChatStore()
    const mockResponse = {
      command: 'Get-Process',
      confidence: 0.95,
      explanation: 'Get all processes',
      security: {
        level: 'safe',
        warnings: [],
        requiresConfirmation: false
      }
    }
    
    vi.mocked(commandApi.translateCommand).mockResolvedValue(mockResponse)
    
    await store.sendMessage('显示所有进程')
    
    const assistantMessage = store.messages.find(m => m.type === 'assistant')
    expect(assistantMessage).toBeDefined()
    expect(assistantMessage?.command).toBeDefined()
    expect(assistantMessage?.command?.command).toBe('Get-Process')
  })

  it('sets loading state during translation', async () => {
    const store = useChatStore()
    
    vi.mocked(commandApi.translateCommand).mockImplementation(() => 
      new Promise(resolve => setTimeout(() => resolve({
        command: 'Get-Process',
        confidence: 0.95,
        explanation: 'test',
        security: { level: 'safe', warnings: [], requiresConfirmation: false }
      }), 100))
    )
    
    const promise = store.sendMessage('test')
    expect(store.isLoading).toBe(true)
    
    await promise
    expect(store.isLoading).toBe(false)
  })

  it('executes command and adds result message', async () => {
    const store = useChatStore()
    const mockExecuteResponse = {
      output: 'Process list...',
      error: null,
      executionTime: 0.234,
      returnCode: 0
    }
    
    vi.mocked(commandApi.executeCommand).mockResolvedValue(mockExecuteResponse)
    
    await store.executeCommand('Get-Process')
    
    const resultMessage = store.messages.find(m => m.type === 'system')
    expect(resultMessage).toBeDefined()
    expect(resultMessage?.content).toContain('Process list...')
  })

  it('handles translation errors gracefully', async () => {
    const store = useChatStore()
    
    vi.mocked(commandApi.translateCommand).mockRejectedValue(new Error('API Error'))
    
    await store.sendMessage('test')
    
    expect(store.isLoading).toBe(false)
    const errorMessage = store.messages.find(m => m.type === 'system')
    expect(errorMessage?.content).toContain('错误')
  })

  it('clears chat messages', () => {
    const store = useChatStore()
    store.messages = [
      { id: '1', type: 'user', content: 'test', timestamp: new Date() }
    ]
    
    store.clearChat()
    
    expect(store.messages).toEqual([])
  })
})
