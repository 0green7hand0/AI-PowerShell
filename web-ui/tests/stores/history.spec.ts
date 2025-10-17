import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useHistoryStore } from '@/stores/history'
import * as historyApi from '@/api/history'

vi.mock('@/api/history')

describe('History Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('initializes with empty items', () => {
    const store = useHistoryStore()
    
    expect(store.items).toEqual([])
    expect(store.total).toBe(0)
    expect(store.currentPage).toBe(1)
  })

  it('fetches history items', async () => {
    const store = useHistoryStore()
    const mockData = {
      items: [
        {
          id: '1',
          userInput: 'test',
          command: 'Get-Process',
          success: true,
          timestamp: new Date(),
          executionTime: 0.1
        }
      ],
      total: 1,
      page: 1,
      limit: 20
    }
    
    vi.mocked(historyApi.getHistory).mockResolvedValue(mockData)
    
    await store.fetchHistory()
    
    expect(store.items).toEqual(mockData.items)
    expect(store.total).toBe(1)
  })

  it('searches history with query', async () => {
    const store = useHistoryStore()
    const mockData = {
      items: [
        {
          id: '1',
          userInput: 'search term',
          command: 'Get-Process',
          success: true,
          timestamp: new Date(),
          executionTime: 0.1
        }
      ],
      total: 1,
      page: 1,
      limit: 20
    }
    
    vi.mocked(historyApi.getHistory).mockResolvedValue(mockData)
    
    await store.searchHistory('search term')
    
    expect(store.searchQuery).toBe('search term')
    expect(historyApi.getHistory).toHaveBeenCalledWith(1, 20, 'search term')
  })

  it('deletes history item', async () => {
    const store = useHistoryStore()
    store.items = [
      {
        id: '1',
        userInput: 'test',
        command: 'Get-Process',
        success: true,
        timestamp: new Date(),
        executionTime: 0.1
      }
    ]
    
    vi.mocked(historyApi.deleteHistory).mockResolvedValue(undefined)
    
    await store.deleteHistory('1')
    
    expect(store.items.length).toBe(0)
    expect(historyApi.deleteHistory).toHaveBeenCalledWith('1')
  })

  it('handles pagination', async () => {
    const store = useHistoryStore()
    const mockData = {
      items: [],
      total: 100,
      page: 2,
      limit: 20
    }
    
    vi.mocked(historyApi.getHistory).mockResolvedValue(mockData)
    
    await store.fetchHistory(2)
    
    expect(store.currentPage).toBe(2)
    expect(historyApi.getHistory).toHaveBeenCalledWith(2, 20, '')
  })
})
