import { config } from '@vue/test-utils'
import { vi } from 'vitest'

// Mock Element Plus components
config.global.stubs = {
  ElButton: true,
  ElInput: true,
  ElDialog: true,
  ElMessage: true,
  ElLoading: true,
  ElProgress: true,
  ElBadge: true,
  ElCard: true,
  ElForm: true,
  ElFormItem: true,
  ElSelect: true,
  ElOption: true,
  ElSwitch: true,
  ElTabs: true,
  ElTabPane: true,
  ElTable: true,
  ElTableColumn: true,
  ElPagination: true,
  ElDropdown: true,
  ElDropdownMenu: true,
  ElDropdownItem: true,
}

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
global.localStorage = localStorageMock as any

// Mock clipboard API
Object.assign(navigator, {
  clipboard: {
    writeText: vi.fn().mockResolvedValue(undefined),
    readText: vi.fn().mockResolvedValue(''),
  },
})
