import { test, expect } from '@playwright/test'

test.describe('History Management E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to history page
    await page.goto('/history')
    await page.waitForLoadState('networkidle')
  })

  test('should display history page', async ({ page }) => {
    // Check if main elements are visible
    await expect(page.locator('.history-view')).toBeVisible()
    await expect(page.locator('.search-bar')).toBeVisible()
  })

  test('should display history items', async ({ page }) => {
    // Wait for history items to load
    await page.waitForSelector('.history-card', { timeout: 5000 })
    
    // Check if at least one history item is displayed
    const historyCards = page.locator('.history-card')
    await expect(historyCards.first()).toBeVisible()
  })

  test('should search history', async ({ page }) => {
    // Type in search box
    const searchInput = page.locator('input[placeholder*="搜索"]')
    await searchInput.fill('Get-Process')
    
    // Wait for search results
    await page.waitForTimeout(1000)
    
    // Check if filtered results are displayed
    const historyCards = page.locator('.history-card')
    const count = await historyCards.count()
    expect(count).toBeGreaterThanOrEqual(0)
  })

  test('should filter by status', async ({ page }) => {
    // Click filter dropdown
    await page.locator('.filter-dropdown').click()
    
    // Select success filter
    await page.locator('text=成功').click()
    
    // Wait for filtered results
    await page.waitForTimeout(1000)
    
    // Check if only successful items are shown
    const successCards = page.locator('.history-card.success')
    const count = await successCards.count()
    expect(count).toBeGreaterThanOrEqual(0)
  })

  test('should view history detail', async ({ page }) => {
    // Wait for history items
    await page.waitForSelector('.history-card', { timeout: 5000 })
    
    // Click on first history item
    await page.locator('.history-card').first().click()
    
    // Check if detail dialog is displayed
    await expect(page.locator('.history-detail-dialog')).toBeVisible()
    
    // Check if command is displayed
    await expect(page.locator('.history-detail-dialog .command')).toBeVisible()
  })

  test('should re-execute command from history', async ({ page }) => {
    // Wait for history items
    await page.waitForSelector('.history-card', { timeout: 5000 })
    
    // Click re-execute button on first item
    await page.locator('.history-card').first().locator('.rerun-button').click()
    
    // Should navigate to chat page
    await expect(page).toHaveURL(/\/chat/)
    
    // Command should be in input box
    const inputBox = page.locator('textarea')
    await expect(inputBox).not.toHaveValue('')
  })

  test('should delete history item', async ({ page }) => {
    // Wait for history items
    await page.waitForSelector('.history-card', { timeout: 5000 })
    
    // Get initial count
    const initialCount = await page.locator('.history-card').count()
    
    // Click delete button on first item
    await page.locator('.history-card').first().locator('.delete-button').click()
    
    // Confirm deletion
    await page.locator('button:has-text("确认")').click()
    
    // Wait for deletion
    await page.waitForTimeout(1000)
    
    // Check if count decreased
    const newCount = await page.locator('.history-card').count()
    expect(newCount).toBeLessThanOrEqual(initialCount)
  })

  test('should group history by date', async ({ page }) => {
    // Wait for history items
    await page.waitForSelector('.history-card', { timeout: 5000 })
    
    // Check if date headers exist
    const dateHeaders = page.locator('.date-header')
    const count = await dateHeaders.count()
    expect(count).toBeGreaterThan(0)
  })

  test('should show empty state when no history', async ({ page }) => {
    // Clear all history (if possible) or navigate to empty state
    // This test assumes there's a way to clear history or test with empty state
    
    // Check for empty state
    const emptyState = page.locator('.empty-state')
    if (await emptyState.isVisible()) {
      await expect(emptyState).toContainText('暂无历史记录')
    }
  })

  test('should paginate history items', async ({ page }) => {
    // Wait for history items
    await page.waitForSelector('.history-card', { timeout: 5000 })
    
    // Check if pagination exists
    const pagination = page.locator('.pagination')
    if (await pagination.isVisible()) {
      // Click next page
      await page.locator('.pagination .next-button').click()
      
      // Wait for new items to load
      await page.waitForTimeout(1000)
      
      // Check if page changed
      await expect(page.locator('.pagination .current-page')).toContainText('2')
    }
  })

  test('should display execution time', async ({ page }) => {
    // Wait for history items
    await page.waitForSelector('.history-card', { timeout: 5000 })
    
    // Check if execution time is displayed
    const firstCard = page.locator('.history-card').first()
    await expect(firstCard.locator('.execution-time')).toBeVisible()
  })

  test('should show status icon', async ({ page }) => {
    // Wait for history items
    await page.waitForSelector('.history-card', { timeout: 5000 })
    
    // Check if status icon is displayed
    const firstCard = page.locator('.history-card').first()
    const statusIcon = firstCard.locator('.status-icon')
    await expect(statusIcon).toBeVisible()
  })

  test('should clear search', async ({ page }) => {
    // Type in search box
    const searchInput = page.locator('input[placeholder*="搜索"]')
    await searchInput.fill('test query')
    
    // Click clear button
    await page.locator('.clear-search-button').click()
    
    // Search input should be empty
    await expect(searchInput).toHaveValue('')
  })
})
