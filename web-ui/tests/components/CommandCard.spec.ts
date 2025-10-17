import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import CommandCard from '@/components/CommandCard.vue'

describe('CommandCard', () => {
  const defaultProps = {
    command: 'Get-Process | Select-Object -First 5',
    confidence: 0.95,
    securityLevel: 'safe' as const,
    explanation: 'Get top 5 processes'
  }

  it('renders command with syntax highlighting', () => {
    const wrapper = mount(CommandCard, {
      props: defaultProps
    })
    
    expect(wrapper.find('.command-card').exists()).toBe(true)
    expect(wrapper.text()).toContain('Get-Process')
  })

  it('displays confidence level correctly', () => {
    const wrapper = mount(CommandCard, {
      props: defaultProps
    })
    
    expect(wrapper.text()).toContain('95%')
  })

  it('shows security badge', () => {
    const wrapper = mount(CommandCard, {
      props: defaultProps
    })
    
    expect(wrapper.findComponent({ name: 'SecurityBadge' }).exists()).toBe(true)
  })

  it('displays explanation text', () => {
    const wrapper = mount(CommandCard, {
      props: defaultProps
    })
    
    expect(wrapper.text()).toContain('Get top 5 processes')
  })

  it('shows warnings when provided', () => {
    const wrapper = mount(CommandCard, {
      props: {
        ...defaultProps,
        warnings: ['This command may take a long time', 'Requires admin privileges']
      }
    })
    
    expect(wrapper.text()).toContain('This command may take a long time')
    expect(wrapper.text()).toContain('Requires admin privileges')
  })

  it('emits copy event when copy button is clicked', async () => {
    const wrapper = mount(CommandCard, {
      props: defaultProps
    })
    
    await wrapper.find('.copy-button').trigger('click')
    
    expect(wrapper.emitted('copy')).toBeTruthy()
    expect(wrapper.emitted('copy')?.[0]).toEqual([defaultProps.command])
  })

  it('emits execute event when execute button is clicked', async () => {
    const wrapper = mount(CommandCard, {
      props: defaultProps
    })
    
    await wrapper.find('.execute-button').trigger('click')
    
    expect(wrapper.emitted('execute')).toBeTruthy()
    expect(wrapper.emitted('execute')?.[0]).toEqual([defaultProps.command])
  })

  it('emits edit event when edit button is clicked', async () => {
    const wrapper = mount(CommandCard, {
      props: defaultProps
    })
    
    await wrapper.find('.edit-button').trigger('click')
    
    expect(wrapper.emitted('edit')).toBeTruthy()
    expect(wrapper.emitted('edit')?.[0]).toEqual([defaultProps.command])
  })

  it('applies danger styling for high security level', () => {
    const wrapper = mount(CommandCard, {
      props: {
        ...defaultProps,
        securityLevel: 'high'
      }
    })
    
    expect(wrapper.find('.command-card.danger').exists()).toBe(true)
  })
})
