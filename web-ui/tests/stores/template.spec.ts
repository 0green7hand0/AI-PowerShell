import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useTemplateStore } from '@/stores/template'
import * as templateApi from '@/api/template'

vi.mock('@/api/template')

describe('Template Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('initializes with empty templates', () => {
    const store = useTemplateStore()
    
    expect(store.templates).toEqual([])
    expect(store.selectedTemplate).toBeNull()
  })

  it('fetches templates', async () => {
    const store = useTemplateStore()
    const mockTemplates = [
      {
        id: '1',
        name: 'Backup Script',
        description: 'Backup files',
        category: 'automation',
        scriptContent: 'Copy-Item...',
        parameters: [],
        keywords: ['backup'],
        createdAt: new Date(),
        updatedAt: new Date()
      }
    ]
    
    vi.mocked(templateApi.getTemplates).mockResolvedValue(mockTemplates)
    
    await store.fetchTemplates()
    
    expect(store.templates).toEqual(mockTemplates)
  })

  it('creates new template', async () => {
    const store = useTemplateStore()
    const newTemplate = {
      name: 'New Template',
      description: 'Test',
      category: 'automation',
      scriptContent: 'Get-Process',
      parameters: [],
      keywords: []
    }
    
    const createdTemplate = {
      id: '1',
      ...newTemplate,
      createdAt: new Date(),
      updatedAt: new Date()
    }
    
    vi.mocked(templateApi.createTemplate).mockResolvedValue(createdTemplate)
    
    await store.createTemplate(newTemplate)
    
    expect(store.templates).toContainEqual(createdTemplate)
  })

  it('updates existing template', async () => {
    const store = useTemplateStore()
    store.templates = [
      {
        id: '1',
        name: 'Old Name',
        description: 'Test',
        category: 'automation',
        scriptContent: 'Get-Process',
        parameters: [],
        keywords: [],
        createdAt: new Date(),
        updatedAt: new Date()
      }
    ]
    
    const updates = { name: 'New Name' }
    const updatedTemplate = { ...store.templates[0], ...updates }
    
    vi.mocked(templateApi.updateTemplate).mockResolvedValue(updatedTemplate)
    
    await store.updateTemplate('1', updates)
    
    expect(store.templates[0].name).toBe('New Name')
  })

  it('deletes template', async () => {
    const store = useTemplateStore()
    store.templates = [
      {
        id: '1',
        name: 'Template',
        description: 'Test',
        category: 'automation',
        scriptContent: 'Get-Process',
        parameters: [],
        keywords: [],
        createdAt: new Date(),
        updatedAt: new Date()
      }
    ]
    
    vi.mocked(templateApi.deleteTemplate).mockResolvedValue(undefined)
    
    await store.deleteTemplate('1')
    
    expect(store.templates.length).toBe(0)
  })

  it('generates script from template', async () => {
    const store = useTemplateStore()
    const params = { sourcePath: 'C:\\Data', targetPath: 'D:\\Backup' }
    const generatedScript = 'Copy-Item -Path C:\\Data -Destination D:\\Backup'
    
    vi.mocked(templateApi.generateScript).mockResolvedValue(generatedScript)
    
    const result = await store.generateScript('1', params)
    
    expect(result).toBe(generatedScript)
    expect(templateApi.generateScript).toHaveBeenCalledWith('1', params)
  })

  it('gets unique categories from templates', () => {
    const store = useTemplateStore()
    store.templates = [
      {
        id: '1',
        name: 'T1',
        description: 'Test',
        category: 'automation',
        scriptContent: '',
        parameters: [],
        keywords: [],
        createdAt: new Date(),
        updatedAt: new Date()
      },
      {
        id: '2',
        name: 'T2',
        description: 'Test',
        category: 'monitoring',
        scriptContent: '',
        parameters: [],
        keywords: [],
        createdAt: new Date(),
        updatedAt: new Date()
      },
      {
        id: '3',
        name: 'T3',
        description: 'Test',
        category: 'automation',
        scriptContent: '',
        parameters: [],
        keywords: [],
        createdAt: new Date(),
        updatedAt: new Date()
      }
    ]
    
    expect(store.categories).toEqual(['automation', 'monitoring'])
  })
})
