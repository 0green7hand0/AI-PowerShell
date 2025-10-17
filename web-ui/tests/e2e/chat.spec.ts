import { test, expect } from '@playwright/test'

test.describe('Chat Interface E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to chat page
    await page.goto('/')
    await page.waitForLoadState('networkidle')
  })

  test('should display chat interface', async ({ page }) => {
    // Check if main elements are visible
    await expect(page.locator('.chat-view')).toBeVisible()
    await expect(page.locator('.input-box')).toBeVisible()
    await expect(page.locator('.send-button')).toBeVisible()
  })

  test('should send message and receive response', async ({ page }) => {
    // Type message
    const inputBox = page.locator('textarea[placeholder*="输入"]')
    await inputBox.fill('显示当前时间')
    
    // Send message
    await page.locator('.send-button').click()
    
    // Wait for user message to appear
    await expect(page.locator('.message-card.user').last()).toContainText('显示当前时间')
    
    // Wait for AI response
    await expect(page.locator('.message-card.assistant').last()).toBeVisible({ timeout: 10000 })
    
    // Check if command card is displayed
    await expect(page.locator('.command-card').last()).toBeVisible()
  })

  test('should display command with syntax highlighting', async ({ page }) => {
    // Send message
    const inputBox = page.locator('textarea[placeholder*="输入"]')
    await inputBox.fill('显示所有进程')
    await page.locator('.send-button').click()
    
    // Wait for command card
    await page.waitForSelector('.command-card', { timeout: 10000 })
    
    // Check if code block exists
    const codeBlock = page.locator('.code-block').last()
    await expect(codeBlock).toBeVisible()
    
    // Check if syntax highlighting is applied
    await expect(codeBlock.locator('code')).toHaveClass(/hljs/)
  })

  test('should show security badge', async ({ page }) => {
    // Send message
    const inputBox = page.locator('textarea[placeholder*="输入"]')
    await inputBox.fill('显示当前时间')
    await page.locator('.send-button').click()
    
    // Wait for command card
    await page.waitForSelector('.command-card', { timeout: 10000 })
    
    // Check if security badge is displayed
    await expect(page.locator('.security-badge').last()).toBeVisible()
  })

  test('should copy command to clipboard', async ({ page }) => {
    // Grant clipboard permissions
    await page.context().grantPermissions(['clipboard-read', 'clipboard-write'])
    
    // Send message
    const inputBox = page.locator('textarea[placeholder*="输入"]')
    await inputBox.fill('显示当前时间')
    await page.locator('.send-button').click()
    
    // Wait for command card
    await page.waitForSelector('.command-card', { timeout: 10000 })
    
    // Click copy button
    await page.locator('.copy-button').last().click()
    
    // Verify toast notification
    await expect(page.locator('.toast')).toContainText('复制成功')
  })

  test('should execute command', async ({ page }) => {
    // Send message
    const inputBox = page.locator('textarea[placeholder*="输入"]')
    await inputBox.fill('显示当前时间')
    await page.locator('.send-button').click()
    
    // Wait for command card
    await page.waitForSelector('.command-card', { timeout: 10000 })
    
    // Click execute button
    await page.locator('.execute-button').last().click()
    
    // Wait for execution result
    await expect(page.locator('.execution-result').last()).toBeVisible({ timeout: 15000 })
  })

  test('should show loading state during translation', async ({ page }) => {
    // Type message
    const inputBox = page.locator('textarea[placeholder*="输入"]')
    await inputBox.fill('显示CPU使用率')
    
    // Send message
    await page.locator('.send-button').click()
    
    // Check loading state
    await expect(page.locator('.loading-spinner')).toBeVisible()
    
    // Wait for response
    await page.waitForSelector('.command-card', { timeout: 10000 })
    
    // Loading should be gone
    await expect(page.locator('.loading-spinner')).not.toBeVisible()
  })

  test('should handle empty input', async ({ page }) => {
    // Try to send empty message
    const sendButton = page.locator('.send-button')
    
    // Button should be disabled
    await expect(sendButton).toBeDisabled()
  })

  test('should support multiline input with Shift+Enter', async ({ page }) => {
    const inputBox = page.locator('textarea[placeholder*="输入"]')
    
    // Type first line
    await inputBox.fill('第一行')
    
    // Press Shift+Enter
    await inputBox.press('Shift+Enter')
    
    // Type second line
    await inputBox.press('第')
    await inputBox.press('二')
    await inputBox.press('行')
    
    // Check if textarea contains both lines
    const value = await inputBox.inputValue()
    expect(value).toContain('第一行')
    expect(value).toContain('第二行')
  })

  test('should scroll to latest message', async ({ page }) => {
    // Send multiple messages
    const inputBox = page.locator('textarea[placeholder*="输入"]')
    
    for (let i = 0; i < 3; i++) {
      await inputBox.fill(`消息 ${i + 1}`)
      await page.locator('.send-button').click()
      await page.waitForTimeout(2000)
    }
    
    // Check if latest message is visible
    const lastMessage = page.locator('.message-card').last()
    await expect(lastMessage).toBeInViewport()
  })

  test('should display confidence level', async ({ page }) => {
    // Send message
    const inputBox = page.locator('textarea[placeholder*="输入"]')
    await inputBox.fill('显示当前时间')
    await page.locator('.send-button').click()
    
    // Wait for command card
    await page.waitForSelector('.command-card', { timeout: 10000 })
    
    // Check if confidence is displayed
    await expect(page.locator('.confidence').last()).toBeVisible()
    await expect(page.locator('.confidence').last()).toContainText('%')
  })

  test('should show warning for high-risk commands', async ({ page }) => {
    // Send dangerous command
    const inputBox = page.locator('textarea[placeholder*="输入"]')
    await inputBox.fill('删除所有文件')
    await page.locator('.send-button').click()
    
    // Wait for command card
    await page.waitForSelector('.command-card', { timeout: 10000 })
    
    // Check if warning is displayed
    const securityBadge = page.locator('.security-badge').last()
    await expect(securityBadge).toHaveClass(/danger|high|critical/)
  })

  test('should clear input after sending', async ({ page }) => {
    const inputBox = page.locator('textarea[placeholder*="输入"]')
    
    // Type and send message
    await inputBox.fill('测试消息')
    await page.locator('.send-button').click()
    
    // Input should be cleared
    await expect(inputBox).toHaveValue('')
  })
})
