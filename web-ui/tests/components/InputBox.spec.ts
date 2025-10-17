import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import InputBox from '@/components/InputBox.vue'

describe('InputBox', () => {
  it('renders textarea input', () => {
    const wrapper = mount(InputBox, {
      props: {
        placeholder: 'Enter command...',
        maxLength: 1000
      }
    })
    
    expect(wrapper.find('textarea').exists()).toBe(true)
  })

  it('displays placeholder text', () => {
    const placeholder = 'Enter your command here'
    const wrapper = mount(InputBox, {
      props: { placeholder }
    })
    
    expect(wrapper.find('textarea').attributes('placeholder')).toBe(placeholder)
  })

  it('emits input event when text changes', async () => {
    const wrapper = mount(InputBox)
    const textarea = wrapper.find('textarea')
    
    await textarea.setValue('Get-Process')
    
    expect(wrapper.emitted('input')).toBeTruthy()
    expect(wrapper.emitted('input')?.[0]).toEqual(['Get-Process'])
  })

  it('emits submit event when send button is clicked', async () => {
    const wrapper = mount(InputBox)
    const textarea = wrapper.find('textarea')
    
    await textarea.setValue('Get-Process')
    await wrapper.find('.send-button').trigger('click')
    
    expect(wrapper.emitted('submit')).toBeTruthy()
    expect(wrapper.emitted('submit')?.[0]).toEqual(['Get-Process'])
  })

  it('emits submit event on Enter key press', async () => {
    const wrapper = mount(InputBox)
    const textarea = wrapper.find('textarea')
    
    await textarea.setValue('Get-Process')
    await textarea.trigger('keydown', { key: 'Enter', shiftKey: false })
    
    expect(wrapper.emitted('submit')).toBeTruthy()
  })

  it('does not submit on Shift+Enter', async () => {
    const wrapper = mount(InputBox)
    const textarea = wrapper.find('textarea')
    
    await textarea.setValue('Get-Process')
    await textarea.trigger('keydown', { key: 'Enter', shiftKey: true })
    
    expect(wrapper.emitted('submit')).toBeFalsy()
  })

  it('displays character count', async () => {
    const wrapper = mount(InputBox, {
      props: { maxLength: 100 }
    })
    const textarea = wrapper.find('textarea')
    
    await textarea.setValue('Test')
    
    expect(wrapper.text()).toContain('4')
    expect(wrapper.text()).toContain('100')
  })

  it('disables send button when loading', () => {
    const wrapper = mount(InputBox, {
      props: { loading: true }
    })
    
    expect(wrapper.find('.send-button').attributes('disabled')).toBeDefined()
  })

  it('disables send button when input is empty', () => {
    const wrapper = mount(InputBox)
    
    expect(wrapper.find('.send-button').attributes('disabled')).toBeDefined()
  })

  it('clears input after submit', async () => {
    const wrapper = mount(InputBox)
    const textarea = wrapper.find('textarea')
    
    await textarea.setValue('Get-Process')
    await wrapper.find('.send-button').trigger('click')
    
    expect(textarea.element.value).toBe('')
  })
})
