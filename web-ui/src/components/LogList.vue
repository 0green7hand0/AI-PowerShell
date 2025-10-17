<template>
  <div class="log-list" ref="logListRef">
    <div v-if="logs.length === 0" class="empty-state">
      <el-empty description="暂无日志" />
    </div>

    <div v-else class="log-items">
      <div
        v-for="log in logs"
        :key="`${log.timestamp}-${log.message}`"
        class="log-item"
        :class="`log-level-${log.level.toLowerCase()}`"
      >
        <div class="log-icon">
          <el-icon :class="`icon-${log.level.toLowerCase()}`">
            <component :is="getLogIcon(log.level)" />
          </el-icon>
        </div>

        <div class="log-content">
          <div class="log-header">
            <span class="log-level" :class="`level-${log.level.toLowerCase()}`">
              {{ log.level }}
            </span>
            <span class="log-source">{{ log.source }}</span>
            <span class="log-timestamp">{{ formatTimestamp(log.timestamp) }}</span>
          </div>

          <div class="log-message">
            {{ log.message }}
          </div>
        </div>
      </div>
    </div>

    <!-- Scroll to bottom button -->
    <transition name="fade">
      <el-button
        v-if="showScrollButton"
        class="scroll-to-bottom"
        :icon="Bottom"
        circle
        type="primary"
        @click="scrollToBottom"
      />
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { Bottom } from '@element-plus/icons-vue'
import type { LogEntry, LogLevel } from '../api/logs'
import { formatLogTimestamp } from '../api/logs'

// Icons for different log levels
import {
  InfoFilled,
  WarningFilled,
  CircleCloseFilled,
  QuestionFilled
} from '@element-plus/icons-vue'

interface Props {
  logs: LogEntry[]
  autoScroll?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  autoScroll: true
})

const logListRef = ref<HTMLElement | null>(null)
const showScrollButton = ref(false)
const isUserScrolling = ref(false)

/**
 * Get icon component for log level
 */
const getLogIcon = (level: LogLevel) => {
  const iconMap: Record<LogLevel, any> = {
    DEBUG: QuestionFilled,
    INFO: InfoFilled,
    WARNING: WarningFilled,
    ERROR: CircleCloseFilled,
    CRITICAL: CircleCloseFilled
  }
  return iconMap[level] || InfoFilled
}

/**
 * Format timestamp for display
 */
const formatTimestamp = (timestamp: string): string => {
  return formatLogTimestamp(timestamp)
}

/**
 * Scroll to bottom of log list
 */
const scrollToBottom = () => {
  if (logListRef.value) {
    logListRef.value.scrollTop = logListRef.value.scrollHeight
    showScrollButton.value = false
  }
}

/**
 * Check if user is near bottom
 */
const isNearBottom = (): boolean => {
  if (!logListRef.value) return false
  
  const { scrollTop, scrollHeight, clientHeight } = logListRef.value
  const threshold = 100 // pixels from bottom
  
  return scrollHeight - scrollTop - clientHeight < threshold
}

/**
 * Handle scroll event
 */
const handleScroll = () => {
  if (!logListRef.value) return
  
  const nearBottom = isNearBottom()
  showScrollButton.value = !nearBottom
  
  // If user scrolls away from bottom, disable auto-scroll temporarily
  if (!nearBottom) {
    isUserScrolling.value = true
  } else {
    isUserScrolling.value = false
  }
}

/**
 * Watch for new logs and auto-scroll if enabled
 */
watch(() => props.logs.length, async () => {
  if (props.autoScroll && !isUserScrolling.value) {
    await nextTick()
    scrollToBottom()
  } else if (!isNearBottom()) {
    showScrollButton.value = true
  }
})

/**
 * Watch for autoScroll prop changes
 */
watch(() => props.autoScroll, (newValue) => {
  if (newValue) {
    isUserScrolling.value = false
    scrollToBottom()
  }
})

/**
 * Setup scroll listener
 */
onMounted(() => {
  if (logListRef.value) {
    logListRef.value.addEventListener('scroll', handleScroll)
  }
  
  // Initial scroll to bottom
  if (props.autoScroll) {
    nextTick(() => scrollToBottom())
  }
})

/**
 * Cleanup scroll listener
 */
onUnmounted(() => {
  if (logListRef.value) {
    logListRef.value.removeEventListener('scroll', handleScroll)
  }
})
</script>

<style scoped>
.log-list {
  position: relative;
  height: 100%;
  overflow-y: auto;
  background-color: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 300px;
}

.log-items {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.log-item {
  display: flex;
  gap: var(--space-3);
  padding: var(--space-3);
  background-color: var(--color-bg-primary);
  border-left: 3px solid transparent;
  border-radius: var(--radius-md);
  transition: all var(--duration-fast) var(--ease-in-out);
  animation: slideIn var(--duration-normal) var(--ease-out);
}

.log-item:hover {
  background-color: var(--color-bg-tertiary);
  box-shadow: var(--shadow-sm);
}

/* Log level colors */
.log-item.log-level-debug {
  border-left-color: #3b82f6;
}

.log-item.log-level-info {
  border-left-color: var(--color-success);
}

.log-item.log-level-warning {
  border-left-color: var(--color-warning);
}

.log-item.log-level-error {
  border-left-color: var(--color-danger);
}

.log-item.log-level-critical {
  border-left-color: #dc2626;
  background-color: rgba(220, 38, 38, 0.05);
}

.log-icon {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-debug {
  color: #3b82f6;
}

.icon-info {
  color: var(--color-success);
}

.icon-warning {
  color: var(--color-warning);
}

.icon-error {
  color: var(--color-danger);
}

.icon-critical {
  color: #dc2626;
}

.log-content {
  flex: 1;
  min-width: 0;
}

.log-header {
  display: flex;
  gap: var(--space-3);
  align-items: center;
  margin-bottom: var(--space-1);
  flex-wrap: wrap;
}

.log-level {
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  text-transform: uppercase;
}

.level-debug {
  background-color: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.level-info {
  background-color: rgba(16, 185, 129, 0.1);
  color: var(--color-success);
}

.level-warning {
  background-color: rgba(245, 158, 11, 0.1);
  color: var(--color-warning);
}

.level-error {
  background-color: rgba(239, 68, 68, 0.1);
  color: var(--color-danger);
}

.level-critical {
  background-color: rgba(220, 38, 38, 0.1);
  color: #dc2626;
}

.log-source {
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
  font-family: var(--font-mono);
}

.log-timestamp {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
  margin-left: auto;
}

.log-message {
  font-size: var(--text-sm);
  color: var(--color-text-primary);
  line-height: var(--leading-relaxed);
  word-break: break-word;
  font-family: var(--font-mono);
}

.scroll-to-bottom {
  position: absolute;
  bottom: var(--space-6);
  right: var(--space-6);
  box-shadow: var(--shadow-lg);
  z-index: 10;
}

/* Animations */
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--duration-normal) var(--ease-in-out);
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Scrollbar styling */
.log-list::-webkit-scrollbar {
  width: 8px;
}

.log-list::-webkit-scrollbar-track {
  background: var(--color-bg-tertiary);
  border-radius: var(--radius-sm);
}

.log-list::-webkit-scrollbar-thumb {
  background: var(--color-border-hover);
  border-radius: var(--radius-sm);
}

.log-list::-webkit-scrollbar-thumb:hover {
  background: var(--color-text-tertiary);
}

/* Responsive */
@media (max-width: 768px) {
  .log-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-1);
  }

  .log-timestamp {
    margin-left: 0;
  }
}
</style>
