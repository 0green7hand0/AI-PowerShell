import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import SecurityBadge from '@/components/SecurityBadge.vue'

describe('SecurityBadge', () => {
  it('renders safe badge with correct color', () => {
    const wrapper = mount(SecurityBadge, {
      props: {
        level: 'safe',
        size: 'medium'
      }
    })
    
    expect(wrapper.find('.security-badge').exists()).toBe(true)
    expect(wrapper.find('.security-badge.safe').exists()).toBe(true)
    expect(wrapper.text()).toContain('安全')
  })

  it('renders warning badge with correct color', () => {
    const wrapper = mount(SecurityBadge, {
      props: {
        level: 'medium',
        size: 'medium'
      }
    })
    
    expect(wrapper.find('.security-badge.medium').exists()).toBe(true)
    expect(wrapper.text()).toContain('警告')
  })

  it('renders danger badge with correct color', () => {
    const wrapper = mount(SecurityBadge, {
      props: {
        level: 'high',
        size: 'medium'
      }
    })
    
    expect(wrapper.find('.security-badge.high').exists()).toBe(true)
    expect(wrapper.text()).toContain('危险')
  })

  it('renders critical badge with correct color', () => {
    const wrapper = mount(SecurityBadge, {
      props: {
        level: 'critical',
        size: 'medium'
      }
    })
    
    expect(wrapper.find('.security-badge.critical').exists()).toBe(true)
    expect(wrapper.text()).toContain('严重')
  })

  it('applies correct size class', () => {
    const wrapper = mount(SecurityBadge, {
      props: {
        level: 'safe',
        size: 'small'
      }
    })
    
    expect(wrapper.find('.security-badge.small').exists()).toBe(true)
  })

  it('defaults to medium size when not specified', () => {
    const wrapper = mount(SecurityBadge, {
      props: {
        level: 'safe'
      }
    })
    
    expect(wrapper.find('.security-badge.medium').exists()).toBe(true)
  })
})
