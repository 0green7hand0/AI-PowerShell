<template>
  <div class="code-block">
    <!-- Header -->
    <div class="code-header">
      <span class="language-label">{{ language }}</span>
      <el-button
        v-if="copyable"
        text
        size="small"
        @click="handleCopy"
        class="copy-button"
      >
        <el-icon><DocumentCopy /></el-icon>
        {{ copied ? '已复制' : '复制' }}
      </el-button>
    </div>

    <!-- Code Content -->
    <div class="code-content">
      <pre v-if="showLineNumbers" class="line-numbers"><code v-for="(line, index) in lines" :key="index">{{ index + 1 }}</code></pre>
      <pre class="code-text"><code ref="codeElement" :class="`language-${language}`">{{ code }}</code></pre>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import { DocumentCopy } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import hljs from 'highlight.js/lib/core'
import powershell from 'highlight.js/lib/languages/powershell'
import bash from 'highlight.js/lib/languages/bash'
import javascript from 'highlight.js/lib/languages/javascript'
import python from 'highlight.js/lib/languages/python'
import json from 'highlight.js/lib/languages/json'
import yaml from 'highlight.js/lib/languages/yaml'
import markdown from 'highlight.js/lib/languages/markdown'

/**
 * CodeBlock - Code display component with syntax highlighting
 * 
 * Integrates Highlight.js for syntax highlighting and provides
 * copy-to-clipboard functionality.
 * 
 * Requirements: 2.16, 2.18
 */

// Register languages
hljs.registerLanguage('powershell', powershell)
hljs.registerLanguage('bash', bash)
hljs.registerLanguage('javascript', javascript)
hljs.registerLanguage('python', python)
hljs.registerLanguage('json', json)
hljs.registerLanguage('yaml', yaml)
hljs.registerLanguage('markdown', markdown)

interface Props {
  code: string
  language?: string
  showLineNumbers?: boolean
  copyable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  language: 'powershell',
  showLineNumbers: false,
  copyable: true
})

const codeElement = ref<HTMLElement | null>(null)
const copied = ref(false)

/**
 * Compute lines for line numbers
 */
const lines = computed(() => {
  return props.code.split('\n')
})

/**
 * Apply syntax highlighting
 */
const highlightCode = () => {
  if (codeElement.value) {
    // Remove existing highlighting
    codeElement.value.removeAttribute('data-highlighted')
    
    // Apply new highlighting
    hljs.highlightElement(codeElement.value)
  }
}

/**
 * Handle copy to clipboard
 * Requirements: 2.18
 */
const handleCopy = async () => {
  try {
    await navigator.clipboard.writeText(props.code)
    copied.value = true
    ElMessage.success('已复制到剪贴板')
    
    setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch (error) {
    console.error('Failed to copy:', error)
    ElMessage.error('复制失败')
  }
}

/**
 * Highlight on mount and when code changes
 */
onMounted(() => {
  highlightCode()
})

watch(() => props.code, () => {
  highlightCode()
})
</script>

<style scoped>
.code-block {
  background-color: var(--hljs-bg);
  border-radius: var(--radius-md);
  overflow: hidden;
  border: 1px solid var(--color-border);
  transition: background-color var(--duration-normal) var(--ease-in-out);
}

.code-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-2) var(--space-3);
  background-color: var(--hljs-header-bg);
  border-bottom: 1px solid var(--hljs-header-border);
  transition: all var(--duration-normal) var(--ease-in-out);
}

.language-label {
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  color: var(--hljs-line-number-fg);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.copy-button {
  color: var(--color-text-secondary);
  transition: color var(--duration-fast) var(--ease-in-out);
}

.copy-button:hover {
  color: var(--color-text-primary);
}

.code-content {
  display: flex;
  overflow-x: auto;
  max-height: 500px;
  overflow-y: auto;
}

.line-numbers {
  margin: 0;
  padding: var(--space-3) var(--space-2);
  background-color: var(--hljs-line-number-bg);
  border-right: 1px solid var(--hljs-header-border);
  user-select: none;
  text-align: right;
  min-width: 40px;
  transition: background-color var(--duration-normal) var(--ease-in-out);
}

.line-numbers code {
  display: block;
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  line-height: 1.5;
  color: var(--hljs-line-number-fg);
}

.code-text {
  flex: 1;
  margin: 0;
  padding: var(--space-3);
  overflow-x: auto;
  background-color: var(--hljs-bg);
  transition: background-color var(--duration-normal) var(--ease-in-out);
}

.code-text code {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  line-height: 1.5;
  color: var(--hljs-fg);
  white-space: pre;
  display: block;
}

/* Custom scrollbar for code content */
.code-content::-webkit-scrollbar {
  height: 8px;
  width: 8px;
}

.code-content::-webkit-scrollbar-track {
  background: var(--hljs-scrollbar-bg);
}

.code-content::-webkit-scrollbar-thumb {
  background: var(--hljs-scrollbar-thumb);
  border-radius: var(--radius-sm);
}

.code-content::-webkit-scrollbar-thumb:hover {
  background: var(--color-border-hover);
}

/* Responsive */
@media (max-width: 768px) {
  .code-text code {
    font-size: var(--text-xs);
  }

  .line-numbers code {
    font-size: var(--text-xs);
  }
}
</style>
