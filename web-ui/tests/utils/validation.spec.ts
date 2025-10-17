import { describe, it, expect } from 'vitest'
import { 
  validateEmail, 
  validateRequired, 
  validateMinLength,
  validateMaxLength,
  sanitizeInput 
} from '@/utils/validation'

describe('Validation Utils', () => {
  describe('validateEmail', () => {
    it('validates correct email addresses', () => {
      expect(validateEmail('test@example.com')).toBe(true)
      expect(validateEmail('user.name@domain.co.uk')).toBe(true)
      expect(validateEmail('user+tag@example.com')).toBe(true)
    })

    it('rejects invalid email addresses', () => {
      expect(validateEmail('invalid')).toBe(false)
      expect(validateEmail('invalid@')).toBe(false)
      expect(validateEmail('@example.com')).toBe(false)
      expect(validateEmail('test@')).toBe(false)
    })

    it('handles empty input', () => {
      expect(validateEmail('')).toBe(false)
    })
  })

  describe('validateRequired', () => {
    it('validates non-empty strings', () => {
      expect(validateRequired('test')).toBe(true)
      expect(validateRequired('a')).toBe(true)
    })

    it('rejects empty strings', () => {
      expect(validateRequired('')).toBe(false)
      expect(validateRequired('   ')).toBe(false)
    })
  })

  describe('validateMinLength', () => {
    it('validates strings meeting minimum length', () => {
      expect(validateMinLength('test', 3)).toBe(true)
      expect(validateMinLength('test', 4)).toBe(true)
    })

    it('rejects strings below minimum length', () => {
      expect(validateMinLength('ab', 3)).toBe(false)
      expect(validateMinLength('', 1)).toBe(false)
    })
  })

  describe('validateMaxLength', () => {
    it('validates strings within maximum length', () => {
      expect(validateMaxLength('test', 5)).toBe(true)
      expect(validateMaxLength('test', 4)).toBe(true)
    })

    it('rejects strings exceeding maximum length', () => {
      expect(validateMaxLength('testing', 5)).toBe(false)
    })
  })

  describe('sanitizeInput', () => {
    it('removes HTML tags', () => {
      expect(sanitizeInput('<script>alert("xss")</script>')).toBe('alert("xss")')
      expect(sanitizeInput('<b>bold</b>')).toBe('bold')
    })

    it('escapes special characters', () => {
      const input = '<div>Test & "quotes"</div>'
      const result = sanitizeInput(input)
      expect(result).not.toContain('<')
      expect(result).not.toContain('>')
    })

    it('handles empty input', () => {
      expect(sanitizeInput('')).toBe('')
    })

    it('preserves normal text', () => {
      expect(sanitizeInput('normal text')).toBe('normal text')
    })
  })
})
