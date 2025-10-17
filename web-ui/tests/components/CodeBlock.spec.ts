import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import CodeBlock from '@/components/CodeBlock.vue'

describe('CodeBlock', () => {
  it('renders code with correct language', () => {
    const code = 'Get-Process | Select-Object -First 5'
    const wrapper = mount(CodeBlock, {
      props: {
        code,
        language: 'powershell',
        copyable: true
      }
    })
    
    expect(wrapper.find('.code-block').exists()).toBe(true)
    expect(wrapper.find('code').text()).toContain('Get-Process')
  })

  it('shows copy button when copyable is true', () => {
    const wrapper = mount(CodeBlock, {
      props: {
        code: 'test code',
        language: 'powershell',
        copyable: true
      }
    })
    
    expect(wrapper.find('.copy-button').exists()).toBe(true)
  })

  it('hides copy button when copyable is false', () => {
    const wrapper = mount(CodeBlock, {
      props: {
        code: 'test code',
        language: 'powershell',
        copyable: false
      }
    })
    
    expect(wrapper.find('.copy-button').exists()).toBe(false)
  })

  it('copies code to clipboard when copy button is clicked', async () => {
    const code = 'Get-Process'
    const wrapper = mount(CodeBlock, {
      props: {
        code,
        language: 'powershell',
        copyable: true
      }
    })
    
    await wrapper.find('.copy-button').trigger('click')
    
    expect(navigator.clipboard.writeText).toHaveBeenCalledWith(code)
  })

  it('shows line numbers when showLineNumbers is true', () => {
    const wrapper = mount(CodeBlock, {
      props: {
        code: 'line1\nline2\nline3',
        language: 'powershell',
        showLineNumbers: true
      }
    })
    
    expect(wrapper.find('.line-numbers').exists()).toBe(true)
  })

  it('displays language label', () => {
    const wrapper = mount(CodeBlock, {
      props: {
        code: 'test',
        language: 'powershell'
      }
    })
    
    expect(wrapper.find('.language-label').text()).toBe('powershell')
  })
})
