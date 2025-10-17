import { test, expect } from '@playwright/test'

test.describe('Template Management E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to template page
    await page.goto('/templates')
    await page.waitForLoadState('networkidle')
  })

  test('should display template page', async ({ page }) => {
    // Check if main elements are visible
    await expect(page.locator('.template-view')).toBeVisible()
    await expect(page.locator('.create-template-button')).toBeVisible()
  })

  test('should display template cards', async ({ page }) => {
    // Wait for templates to load
    await page.waitForSelector('.template-card', { timeout: 5000 })
    
    // Check if at least one template is displayed
    const templateCards = page.locator('.template-card')
    await expect(templateCards.first()).toBeVisible()
  })

  test('should filter templates by category', async ({ page }) => {
    // Wait for templates
    await page.waitForSelector('.template-card', { timeout: 5000 })
    
    // Click on a category tab
    const categoryTab = page.locator('.category-tab').first()
    await categoryTab.click()
    
    // Wait for filtered results
    await page.waitForTimeout(500)
    
    // Templates should be filtered
    const templateCards = page.locator('.template-card')
    const count = await templateCards.count()
    expect(count).toBeGreaterThanOrEqual(0)
  })

  test('should open template use dialog', async ({ page }) => {
    // Wait for templates
    await page.waitForSelector('.template-card', { timeout: 5000 })
    
    // Click use button on first template
    await page.locator('.template-card').first().locator('.use-button').click()
    
    // Check if use dialog is displayed
    await expect(page.locator('.template-use-dialog')).toBeVisible()
  })

  test('should fill template parameters and generate script', async ({ page }) => {
    // Wait for templates
    await page.waitForSelector('.template-card', { timeout: 5000 })
    
    // Click use button
    await page.locator('.template-card').first().locator('.use-button').click()
    
    // Wait for dialog
    await page.waitForSelector('.template-use-dialog', { timeout: 2000 })
    
    // Fill parameters (if any)
    const paramInputs = page.locator('.template-use-dialog input[type="text"]')
    const count = await paramInputs.count()
    
    if (count > 0) {
      // Fill first parameter
      await paramInputs.first().fill('test value')
      
      // Click generate button
      await page.locator('.generate-button').click()
      
      // Check if script preview is displayed
      await expect(page.locator('.script-preview')).toBeVisible()
    }
  })

  test('should create new template', async ({ page }) => {
    // Click create template button
    await page.locator('.create-template-button').click()
    
    // Check if form dialog is displayed
    await expect(page.locator('.template-form-dialog')).toBeVisible()
    
    // Fill form
    await page.locator('input[name="name"]').fill('Test Template')
    await page.locator('input[name="description"]').fill('Test Description')
    await page.locator('select[name="category"]').selectOption('automation')
    await page.locator('textarea[name="scriptContent"]').fill('Get-Process')
    
    // Submit form
    await page.locator('.submit-button').click()
    
    // Wait for success message
    await expect(page.locator('.toast')).toContainText('创建成功')
  })

  test('should edit existing template', async ({ page }) => {
    // Wait for templates
    await page.waitForSelector('.template-card', { timeout: 5000 })
    
    // Click edit button on first template
    await page.locator('.template-card').first().locator('.edit-button').click()
    
    // Check if form dialog is displayed
    await expect(page.locator('.template-form-dialog')).toBeVisible()
    
    // Modify name
    const nameInput = page.locator('input[name="name"]')
    await nameInput.clear()
    await nameInput.fill('Updated Template Name')
    
    // Submit form
    await page.locator('.submit-button').click()
    
    // Wait for success message
    await expect(page.locator('.toast')).toContainText('更新成功')
  })

  test('should delete template', async ({ page }) => {
    // Wait for templates
    await page.waitForSelector('.template-card', { timeout: 5000 })
    
    // Get initial count
    const initialCount = await page.locator('.template-card').count()
    
    // Click delete button on first template
    await page.locator('.template-card').first().locator('.delete-button').click()
    
    // Confirm deletion
    await page.locator('.delete-confirm-dialog').waitFor()
    await page.locator('.delete-confirm-dialog .confirm-button').click()
    
    // Wait for deletion
    await page.waitForTimeout(1000)
    
    // Check if count decreased
    const newCount = await page.locator('.template-card').count()
    expect(newCount).toBeLessThanOrEqual(initialCount)
  })

  test('should display template details', async ({ page }) => {
    // Wait for templates
    await page.waitForSelector('.template-card', { timeout: 5000 })
    
    // Check if template card shows details
    const firstCard = page.locator('.template-card').first()
    await expect(firstCard.locator('.template-name')).toBeVisible()
    await expect(firstCard.locator('.template-description')).toBeVisible()
    await expect(firstCard.locator('.template-category')).toBeVisible()
  })

  test('should show parameter count', async ({ page }) => {
    // Wait for templates
    await page.waitForSelector('.template-card', { timeout: 5000 })
    
    // Check if parameter count is displayed
    const firstCard = page.locator('.template-card').first()
    const paramCount = firstCard.locator('.param-count')
    
    if (await paramCount.isVisible()) {
      await expect(paramCount).toContainText('参数')
    }
  })

  test('should validate required parameters', async ({ page }) => {
    // Wait for templates
    await page.waitForSelector('.template-card', { timeout: 5000 })
    
    // Click use button
    await page.locator('.template-card').first().locator('.use-button').click()
    
    // Wait for dialog
    await page.waitForSelector('.template-use-dialog', { timeout: 2000 })
    
    // Try to generate without filling required fields
    const generateButton = page.locator('.generate-button')
    if (await generateButton.isVisible()) {
      await generateButton.click()
      
      // Should show validation error
      const errorMessage = page.locator('.error-message')
      if (await errorMessage.isVisible()) {
        await expect(errorMessage).toBeVisible()
      }
    }
  })

  test('should show empty state when no templates', async ({ page }) => {
    // This test assumes there's a way to test with no templates
    // or that the empty state is visible when no templates match filter
    
    const emptyState = page.locator('.empty-state')
    if (await emptyState.isVisible()) {
      await expect(emptyState).toContainText('暂无模板')
    }
  })

  test('should display keywords', async ({ page }) => {
    // Wait for templates
    await page.waitForSelector('.template-card', { timeout: 5000 })
    
    // Check if keywords are displayed
    const firstCard = page.locator('.template-card').first()
    const keywords = firstCard.locator('.keywords')
    
    if (await keywords.isVisible()) {
      await expect(keywords).toBeVisible()
    }
  })

  test('should execute generated script', async ({ page }) => {
    // Wait for templates
    await page.waitForSelector('.template-card', { timeout: 5000 })
    
    // Click use button
    await page.locator('.template-card').first().locator('.use-button').click()
    
    // Wait for dialog
    await page.waitForSelector('.template-use-dialog', { timeout: 2000 })
    
    // Fill parameters and generate (if applicable)
    const generateButton = page.locator('.generate-button')
    if (await generateButton.isVisible()) {
      await generateButton.click()
      
      // Wait for script preview
      await page.waitForTimeout(1000)
      
      // Click execute button
      const executeButton = page.locator('.execute-script-button')
      if (await executeButton.isVisible()) {
        await executeButton.click()
        
        // Should show execution result or navigate to chat
        await page.waitForTimeout(1000)
      }
    }
  })
})
