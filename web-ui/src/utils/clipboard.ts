import { ElMessage } from 'element-plus'

/**
 * Copy text to clipboard
 */
export const copyToClipboard = async (text: string): Promise<boolean> => {
  try {
    await navigator.clipboard.writeText(text)
    ElMessage.success('已复制到剪贴板')
    return true
  } catch (error) {
    console.error('Failed to copy to clipboard:', error)
    ElMessage.error('复制失败')
    return false
  }
}
