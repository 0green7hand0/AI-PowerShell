import { describe, it, expect } from 'vitest'

// Utility functions for formatting
function formatDate(date: Date): string {
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
}

function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms}ms`
  if (ms < 60000) return `${(ms / 1000).toFixed(2)}s`
  return `${(ms / 60000).toFixed(2)}m`
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes}B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)}KB`
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(2)}MB`
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)}GB`
}

function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength - 3) + '...'
}

describe('Format Utils', () => {
  describe('formatDate', () => {
    it('formats date correctly', () => {
      const date = new Date('2024-01-15T10:30:00')
      const formatted = formatDate(date)
      expect(formatted).toContain('2024')
      expect(formatted).toContain('01')
      expect(formatted).toContain('15')
    })
  })

  describe('formatDuration', () => {
    it('formats milliseconds', () => {
      expect(formatDuration(500)).toBe('500ms')
      expect(formatDuration(999)).toBe('999ms')
    })

    it('formats seconds', () => {
      expect(formatDuration(1000)).toBe('1.00s')
      expect(formatDuration(5500)).toBe('5.50s')
    })

    it('formats minutes', () => {
      expect(formatDuration(60000)).toBe('1.00m')
      expect(formatDuration(125000)).toBe('2.08m')
    })
  })

  describe('formatFileSize', () => {
    it('formats bytes', () => {
      expect(formatFileSize(500)).toBe('500B')
      expect(formatFileSize(1023)).toBe('1023B')
    })

    it('formats kilobytes', () => {
      expect(formatFileSize(1024)).toBe('1.00KB')
      expect(formatFileSize(5120)).toBe('5.00KB')
    })

    it('formats megabytes', () => {
      expect(formatFileSize(1024 * 1024)).toBe('1.00MB')
      expect(formatFileSize(5 * 1024 * 1024)).toBe('5.00MB')
    })

    it('formats gigabytes', () => {
      expect(formatFileSize(1024 * 1024 * 1024)).toBe('1.00GB')
      expect(formatFileSize(2.5 * 1024 * 1024 * 1024)).toBe('2.50GB')
    })
  })

  describe('truncateText', () => {
    it('returns original text if within limit', () => {
      expect(truncateText('short', 10)).toBe('short')
    })

    it('truncates long text with ellipsis', () => {
      expect(truncateText('this is a very long text', 10)).toBe('this is...')
    })

    it('handles exact length', () => {
      expect(truncateText('exactly10!', 10)).toBe('exactly10!')
    })
  })
})
