<template>
  <div :class="['security-badge', `security-${level}`, `size-${size}`]">
    <el-icon class="badge-icon">
      <component :is="iconComponent" />
    </el-icon>
    <span class="badge-text">{{ levelText }}</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { CircleCheck, Warning, WarningFilled } from '@element-plus/icons-vue'
import type { SecurityLevel } from '../api/command'

/**
 * SecurityBadge - Security level indicator component
 * 
 * Displays security level with color-coded badge and icon.
 * Supports different sizes.
 * 
 * Requirements: 2.11
 */

interface Props {
  level: SecurityLevel
  size?: 'small' | 'medium' | 'large'
}

const props = withDefaults(defineProps<Props>(), {
  size: 'medium'
})

/**
 * Get icon component based on security level
 */
const iconComponent = computed(() => {
  switch (props.level) {
    case 'safe':
      return CircleCheck
    case 'low':
      return Warning
    case 'medium':
      return Warning
    case 'high':
      return WarningFilled
    case 'critical':
      return WarningFilled
    default:
      return Warning
  }
})

/**
 * Get display text for security level
 */
const levelText = computed(() => {
  const textMap: Record<SecurityLevel, string> = {
    safe: '安全',
    low: '低风险',
    medium: '中风险',
    high: '高风险',
    critical: '严重风险'
  }
  return textMap[props.level] || '未知'
})
</script>

<style scoped>
.security-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-md);
  font-weight: var(--font-medium);
  transition: all var(--duration-fast) var(--ease-in-out);
}

/* Size variants */
.size-small {
  font-size: var(--text-xs);
  padding: 2px var(--space-2);
}

.size-small .badge-icon {
  font-size: 12px;
}

.size-medium {
  font-size: var(--text-sm);
  padding: var(--space-1) var(--space-3);
}

.size-medium .badge-icon {
  font-size: 14px;
}

.size-large {
  font-size: var(--text-base);
  padding: var(--space-2) var(--space-4);
}

.size-large .badge-icon {
  font-size: 16px;
}

/* Security level colors */
.security-safe {
  background-color: rgba(16, 185, 129, 0.1);
  color: var(--color-success);
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.security-low {
  background-color: rgba(59, 130, 246, 0.1);
  color: var(--color-info);
  border: 1px solid rgba(59, 130, 246, 0.3);
}

.security-medium {
  background-color: rgba(245, 158, 11, 0.1);
  color: var(--color-warning);
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.security-high {
  background-color: rgba(239, 68, 68, 0.1);
  color: var(--color-danger);
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.security-critical {
  background-color: rgba(220, 38, 38, 0.15);
  color: #dc2626;
  border: 1px solid rgba(220, 38, 38, 0.4);
  font-weight: var(--font-bold);
}

.badge-icon {
  flex-shrink: 0;
}

.badge-text {
  white-space: nowrap;
}

/* Dark theme adjustments */
[data-theme="dark"] .security-safe {
  background-color: rgba(16, 185, 129, 0.15);
}

[data-theme="dark"] .security-low {
  background-color: rgba(59, 130, 246, 0.15);
}

[data-theme="dark"] .security-medium {
  background-color: rgba(245, 158, 11, 0.15);
}

[data-theme="dark"] .security-high {
  background-color: rgba(239, 68, 68, 0.15);
}

[data-theme="dark"] .security-critical {
  background-color: rgba(220, 38, 38, 0.2);
}
</style>
