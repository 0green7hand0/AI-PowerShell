<template>
  <div class="log-analytics">
    <h3 class="analytics-title">审计日志分析</h3>

    <div class="analytics-grid">
      <!-- Log Level Distribution -->
      <el-card class="analytics-card">
        <template #header>
          <div class="card-header">
            <span>日志级别分布</span>
            <el-button
              size="small"
              :icon="Refresh"
              :loading="isRefreshing"
              @click="refreshAnalytics"
            />
          </div>
        </template>
        <div class="chart-container">
          <div v-if="!Chart" class="chart-fallback">
            <el-empty description="图表加载失败，显示原始数据" />
            <div class="level-list">
              <div v-for="(count, level) in logCache.levelCounts" :key="level" class="level-item">
                <span class="level-name">{{ level }}</span>
                <span class="level-count">{{ count }}</span>
              </div>
            </div>
          </div>
          <canvas v-else ref="levelChartRef" class="chart" />
        </div>
      </el-card>

      <!-- Source Distribution -->
      <el-card class="analytics-card">
        <template #header>
          <div class="card-header">
            <span>日志来源分布</span>
          </div>
        </template>
        <div class="chart-container">
          <div v-if="!Chart" class="chart-fallback">
            <el-empty description="图表加载失败，显示原始数据" />
            <div class="source-list">
              <div v-for="(count, source) in logCache.sourceCounts" :key="source" class="source-item">
                <span class="source-name">{{ source }}</span>
                <span class="source-count">{{ count }}</span>
              </div>
              <div v-if="Object.keys(logCache.sourceCounts).length === 0" class="source-item">
                <span class="source-name">无数据</span>
                <span class="source-count">0</span>
              </div>
            </div>
          </div>
          <canvas v-else ref="sourceChartRef" class="chart" />
        </div>
      </el-card>

      <!-- Timeline -->
      <el-card class="analytics-card" :body-style="{ padding: '0' }">
        <template #header>
          <div class="card-header">
            <span>日志时间线</span>
            <el-select v-model="timeRange" size="small" @change="updateTimeline">
              <el-option label="最近1小时" value="1h" />
              <el-option label="最近6小时" value="6h" />
              <el-option label="最近24小时" value="24h" />
              <el-option label="最近7天" value="7d" />
            </el-select>
          </div>
        </template>
        <div class="chart-container">
          <div v-if="!Chart" class="chart-fallback">
            <el-empty description="图表加载失败，显示原始数据" />
            <div class="timeline-list">
              <div v-for="(count, hour) in logCache.hourCounts" :key="hour" class="timeline-item">
                <span class="hour-name">{{ hour }}:00</span>
                <span class="hour-count">{{ count }}</span>
              </div>
            </div>
          </div>
          <canvas v-else ref="timelineChartRef" class="chart timeline-chart" />
        </div>
      </el-card>

      <!-- Critical Events -->
      <el-card class="analytics-card">
        <template #header>
          <div class="card-header">
            <span>关键事件</span>
            <el-badge :value="criticalEvents.length" type="danger" />
          </div>
        </template>
        <div class="critical-events">
          <el-empty v-if="criticalEvents.length === 0" description="暂无关键事件" />
          <div v-else>
            <div class="event-list">
              <div
                v-for="event in criticalEvents"
                :key="`${event.timestamp}-${event.message}`"
                class="event-item"
              >
                <div class="event-header">
                  <span class="event-time">{{ formatTimestamp(event.timestamp) }}</span>
                  <span class="event-source">{{ event.source }}</span>
                </div>
                <div class="event-message">
                  {{ event.message }}
                </div>
              </div>
            </div>
            <div v-if="totalPages > 1" class="pagination-container">
              <el-pagination
                v-model:current-page="currentPage"
                v-model:page-size="pageSize"
                :page-sizes="[5, 10, 20]"
                layout="total, sizes, prev, pager, next, jumper"
                :total="totalCriticalEvents"
                @size-change="updateCache"
                @current-change="updateCache"
              />
            </div>
          </div>
        </div>
      </el-card>

      <!-- Log Statistics -->
      <el-card class="analytics-card">
        <template #header>
          <div class="card-header">
            <span>日志统计</span>
          </div>
        </template>
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-value">{{ totalLogs }}</div>
            <div class="stat-label">总日志数</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ errorLogs }}</div>
            <div class="stat-label">错误数</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ warningLogs }}</div>
            <div class="stat-label">警告数</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ uniqueSources }}</div>
            <div class="stat-label">来源数</div>
          </div>
        </div>
      </el-card>

      <!-- Log Activity Heatmap -->
      <el-card class="analytics-card">
        <template #header>
          <div class="card-header">
            <span>日志活动热图</span>
          </div>
        </template>
        <div class="chart-container">
          <div v-if="!Chart" class="chart-fallback">
            <el-empty description="图表加载失败，显示原始数据" />
            <div class="heatmap-list">
              <div v-for="(count, hour) in logCache.hourCounts" :key="hour" class="heatmap-item">
                <span class="hour-name">{{ hour }}:00</span>
                <span class="hour-count">{{ count }}</span>
              </div>
            </div>
          </div>
          <canvas v-else ref="heatmapChartRef" class="chart" />
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import Chart from 'chart.js/auto'
import type { LogEntry } from '../api/logs'
import { formatLogTimestamp } from '../api/logs'

interface Props {
  logs: LogEntry[]
}

const props = defineProps<Props>()

// Refs
const levelChartRef = ref<HTMLElement | null>(null)
const sourceChartRef = ref<HTMLElement | null>(null)
const timelineChartRef = ref<HTMLElement | null>(null)
const heatmapChartRef = ref<HTMLElement | null>(null)

// State
const isRefreshing = ref(false)
const timeRange = ref('24h')
let levelChart: any = null
let sourceChart: any = null
let timelineChart: any = null
let heatmapChart: any = null

// Pagination for critical events
const currentPage = ref(1)
const pageSize = ref(5)

// Cache
const logCache = ref({
  levelCounts: {
    DEBUG: 0,
    INFO: 0,
    WARNING: 0,
    ERROR: 0,
    CRITICAL: 0
  },
  sourceCounts: {} as Record<string, number>,
  timelineData: {} as Record<string, number>,
  hourCounts: Array(24).fill(0),
  lastLogLength: 0
})



// Computed
const criticalEvents = computed(() => {
  console.log('=== Critical Events Debug ===')
  console.log('Total logs:', props.logs.length)
  console.log('First 5 logs:', props.logs.slice(0, 5).map(log => ({ level: log.level, message: log.message.substring(0, 50) })))
  
  const filteredEvents = props.logs
    .filter((log) => log.level === 'ERROR' || log.level === 'CRITICAL')
    .reverse()
  
  console.log('Filtered critical events count:', filteredEvents.length)
  console.log('Filtered events:', filteredEvents.slice(0, 5).map(log => ({ level: log.level, message: log.message.substring(0, 50) })))
  console.log('============================')
  
  // Apply pagination
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredEvents.slice(start, end)
})

const totalCriticalEvents = computed(() => {
  return props.logs.filter(log => log.level === 'ERROR' || log.level === 'CRITICAL').length
})

const totalPages = computed(() => {
  return Math.ceil(totalCriticalEvents.value / pageSize.value)
})

const totalLogs = computed(() => props.logs.length)

const errorLogs = computed(() => {
  return props.logs.filter(log => log.level === 'ERROR' || log.level === 'CRITICAL').length
})

const warningLogs = computed(() => {
  return props.logs.filter(log => log.level === 'WARNING').length
})

const uniqueSources = computed(() => {
  const sources = new Set(props.logs.map(log => log.source))
  return sources.size
})

// Methods
const formatTimestamp = (timestamp: string): string => {
  return formatLogTimestamp(timestamp)
}

const loadChartJs = async (): Promise<boolean> => {
  // Chart.js is now imported directly
  return true
}

const createLevelChart = () => {
  if (!levelChartRef.value || !Chart) return

  const canvas = levelChartRef.value as HTMLCanvasElement
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  // Use cached level counts
  const levelCounts = logCache.value.levelCounts

  if (levelChart) {
    // Update existing chart data
    levelChart.data.datasets[0].data = Object.values(levelCounts)
    levelChart.update()
    return
  }

  levelChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
      datasets: [
        {
          data: Object.values(levelCounts),
          backgroundColor: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#dc2626'],
          borderWidth: 1
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom'
        },
        title: {
          display: true,
          text: '日志级别分布'
        },
        tooltip: {
          callbacks: {
            label: function(context: any) {
              const label = context.label || ''
              const value = context.raw || 0
              const total = context.dataset.data.reduce((a: number, b: number) => a + b, 0)
              const percentage = total > 0 ? Math.round((value / total) * 100) : 0
              return `${label}: ${value} (${percentage}%)`
            }
          }
        }
      }
    }
  })
}

const createSourceChart = () => {
  if (!sourceChartRef.value || !Chart) return

  const canvas = sourceChartRef.value as HTMLCanvasElement
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  // Use cached source counts
  const sourceCounts = logCache.value.sourceCounts

  // Get top 5 sources
  const topSources = Object.entries(sourceCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)

  const labels = topSources.map(([source]) => source.length > 15 ? source.substring(0, 12) + '...' : source)
  const data = topSources.map(([, count]) => count)

  // Add fallback for empty data
  if (labels.length === 0) {
    labels.push('无数据')
    data.push(0)
  }

  if (sourceChart) {
    // Update existing chart data
    sourceChart.data.labels = labels
    sourceChart.data.datasets[0].data = data
    sourceChart.update()
    return
  }

  sourceChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        {
          label: '日志数量',
          data,
          backgroundColor: '#3b82f6',
          borderRadius: 4
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        },
        title: {
          display: true,
          text: 'Top 5 日志来源'
        },
        tooltip: {
          callbacks: {
            label: function(context: any) {
              const label = context.label || ''
              const value = context.raw || 0
              return `${label}: ${value}`
            }
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            precision: 0
          }
        }
      }
    }
  })
}

const createTimelineChart = () => {
  if (!timelineChartRef.value || !Chart) return

  const canvas = timelineChartRef.value as HTMLCanvasElement
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  // Group logs by hour
  const now = new Date()
  let hoursToShow = 24

  switch (timeRange.value) {
    case '1h':
      hoursToShow = 1
      break
    case '6h':
      hoursToShow = 6
      break
    case '7d':
      hoursToShow = 168 // 7 days * 24 hours
      break
  }

  const timelineData: Record<string, number> = {}

  // Initialize timeline data
  for (let i = hoursToShow - 1; i >= 0; i--) {
    const hourDate = new Date(now.getTime() - i * 60 * 60 * 1000)
    const hourKey = hourDate.toISOString().slice(0, 13)
    timelineData[hourKey] = 0
  }

  // Use sampled logs for performance
  const sampledLogs = getSampledLogs()
  
  // Count logs per hour
  sampledLogs.forEach((log) => {
    try {
      const logDate = new Date(log.timestamp)
      if (!isNaN(logDate.getTime())) {
        const hourKey = logDate.toISOString().slice(0, 13)
        if (timelineData.hasOwnProperty(hourKey)) {
          timelineData[hourKey]++
        }
      }
    } catch (e) {
      console.error('Error parsing timestamp for timeline:', e)
    }
  })

  const labels = Object.keys(timelineData).map((key) => {
    try {
      // Convert ISO string to Date object
      const date = new Date(key)
      if (!isNaN(date.getTime())) {
        return date.toLocaleTimeString('zh-CN', {
          hour: '2-digit',
          minute: '2-digit'
        })
      } else {
        // Fallback if date is invalid
        return key.split('T')[1] || '未知时间'
      }
    } catch (e) {
      console.error('Error parsing timeline date:', e)
      return key.split('T')[1] || '未知时间'
    }
  })
  const data = Object.values(timelineData)

  if (timelineChart) {
    // Update existing chart data
    timelineChart.data.labels = labels
    timelineChart.data.datasets[0].data = data
    timelineChart.update()
    return
  }

  timelineChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: '日志数量',
          data,
          borderColor: '#3b82f6',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          tension: 0.4,
          fill: true,
          pointBackgroundColor: '#3b82f6',
          pointBorderColor: '#fff',
          pointBorderWidth: 2,
          pointRadius: 4,
          pointHoverRadius: 6
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        },
        title: {
          display: true,
          text: '日志时间线'
        },
        tooltip: {
          mode: 'index',
          intersect: false
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            precision: 0
          }
        },
        x: {
          ticks: {
            maxRotation: 45,
            minRotation: 45
          }
        }
      }
    }
  })
}

const createHeatmapChart = () => {
  if (!heatmapChartRef.value || !Chart) return

  const canvas = heatmapChartRef.value as HTMLCanvasElement
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  // Use cached hour counts
  const hourCounts = logCache.value.hourCounts
  const labels = Array.from({ length: 24 }, (_, i) => `${i}:00`)
  const data = hourCounts

  if (heatmapChart) {
    // Update existing chart data
    heatmapChart.data.datasets[0].data = data
    heatmapChart.data.datasets[0].backgroundColor = data.map(count => {
      if (count === 0) return 'rgba(209, 213, 219, 0.3)'
      if (count < 10) return 'rgba(59, 130, 246, 0.5)'
      if (count < 50) return 'rgba(59, 130, 246, 0.8)'
      return 'rgba(59, 130, 246, 1)'
    })
    heatmapChart.update()
    return
  }

  heatmapChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        {
          label: '日志数量',
          data,
          backgroundColor: data.map(count => {
            if (count === 0) return 'rgba(209, 213, 219, 0.3)'
            if (count < 10) return 'rgba(59, 130, 246, 0.5)'
            if (count < 50) return 'rgba(59, 130, 246, 0.8)'
            return 'rgba(59, 130, 246, 1)'
          }),
          borderRadius: 4
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        },
        title: {
          display: true,
          text: '24小时日志活动分布'
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            precision: 0
          }
        },
        x: {
          ticks: {
            maxRotation: 45,
            minRotation: 45
          }
        }
      }
    }
  })
}

const updateCharts = async () => {
  // Update cache first
  updateCache()
  
  const loaded = await loadChartJs()
  if (loaded) {
    console.log('Creating all charts...')
    console.log('Level counts:', logCache.value.levelCounts)
    console.log('Source counts:', logCache.value.sourceCounts)
    console.log('Hour counts:', logCache.value.hourCounts)
    
    createLevelChart()
    console.log('Created level chart')
    
    createSourceChart()
    console.log('Created source chart')
    
    createTimelineChart()
    console.log('Created timeline chart')
    
    createHeatmapChart()
    console.log('Created heatmap chart')
  }
}

// Add data sampling for large datasets
const getSampledLogs = () => {
  const maxLogs = 1000 // Limit to 1000 logs for performance
  if (props.logs.length <= maxLogs) {
    return props.logs
  }
  
  // Sample logs evenly
  const step = Math.ceil(props.logs.length / maxLogs)
  const sampledLogs = []
  for (let i = 0; i < props.logs.length; i += step) {
    sampledLogs.push(props.logs[i])
  }
  return sampledLogs
}

// Cache for parsed timestamps to reduce Date object creation
const timestampCache = new Map<string, number>()

// Parse timestamp efficiently with caching
const parseTimestamp = (timestamp: string): number => {
  if (timestampCache.has(timestamp)) {
    return timestampCache.get(timestamp)!
  }
  
  try {
    let date: Date
    
    // Try different timestamp formats
    if (typeof timestamp === 'string') {
      // Remove extra whitespace
      const trimmedTimestamp = timestamp.trim()
      
      // Try direct parsing
      date = new Date(trimmedTimestamp)
      
      // If parsing fails, try to extract date from common log formats
      if (isNaN(date.getTime())) {
        // Try to match common log timestamp format: "DD/MMM/YYYY:HH:MM:SS"
        const logFormatMatch = trimmedTimestamp.match(/\[(.*?)\]/)
        if (logFormatMatch) {
          date = new Date(logFormatMatch[1])
        }
        // Try to match ISO format: "YYYY-MM-DD HH:MM:SS,SSS"
        if (isNaN(date.getTime())) {
          const isoFormatMatch = trimmedTimestamp.match(/^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})/)
          if (isoFormatMatch) {
            date = new Date(isoFormatMatch[1])
          }
        }
      }
    } else {
      date = new Date(timestamp)
    }
    
    const hours = !isNaN(date.getTime()) ? date.getHours() : -1
    timestampCache.set(timestamp, hours)
    return hours
  } catch (e) {
    console.error('Error parsing timestamp:', e)
    timestampCache.set(timestamp, -1)
    return -1
  }
}

// Update cache function to use sampled logs
const updateCache = () => {
  if (props.logs.length === logCache.value.lastLogLength) {
    return // No changes, use cached data
  }
  
  // Clear timestamp cache for new data
  timestampCache.clear()
  
  // Use sampled logs for performance
  const sampledLogs = getSampledLogs()
  
  // Reset caches
  logCache.value.levelCounts = {
    DEBUG: 0,
    INFO: 0,
    WARNING: 0,
    ERROR: 0,
    CRITICAL: 0
  }
  logCache.value.sourceCounts = {}
  logCache.value.hourCounts = Array(24).fill(0)
  
  // Calculate counts
  sampledLogs.forEach((log) => {
    // Level counts
    if (logCache.value.levelCounts.hasOwnProperty(log.level)) {
      logCache.value.levelCounts[log.level as keyof typeof logCache.value.levelCounts]++
    }
    
    // Source counts
    logCache.value.sourceCounts[log.source] = (logCache.value.sourceCounts[log.source] || 0) + 1
    
    // Hour counts with cached timestamp parsing
    const hour = parseTimestamp(log.timestamp)
    if (hour >= 0 && hour < 24) {
      logCache.value.hourCounts[hour]++
    }
  })
  
  logCache.value.lastLogLength = props.logs.length
}

const refreshAnalytics = async () => {
  isRefreshing.value = true
  try {
    await updateCharts()
  } finally {
    isRefreshing.value = false
  }
}

const updateTimeline = () => {
  createTimelineChart()
}



// Watch for logs changes
watch(
  () => props.logs.length,
  () => {
    // Debounce chart updates to avoid performance issues
    if ((window as any).chartUpdateTimeout) {
      clearTimeout((window as any).chartUpdateTimeout)
    }
    (window as any).chartUpdateTimeout = setTimeout(() => {
      updateCharts()
    }, 300)
  }
)

// Lifecycle
onMounted(async () => {
  await loadChartJs()
  updateCharts()
})

onUnmounted(() => {
  if (levelChart) levelChart.destroy()
  if (sourceChart) sourceChart.destroy()
  if (timelineChart) timelineChart.destroy()
  if (heatmapChart) heatmapChart.destroy()
  if ((window as any).chartUpdateTimeout) {
    clearTimeout((window as any).chartUpdateTimeout)
  }
})
</script>

<style scoped>
.log-analytics {
  margin-bottom: var(--space-6);
}

.analytics-title {
  font-size: var(--text-xl);
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
  margin-bottom: var(--space-4);
}

.analytics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: var(--space-4);
}

.analytics-card {
  transition: all var(--duration-fast) var(--ease-in-out);
}

.analytics-card:hover {
  box-shadow: var(--shadow-md);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  position: relative;
  height: 300px;
  padding: var(--space-4);
}

.chart {
  width: 100%;
  height: 100%;
}

.chart-loading {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-fallback {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-4);
  text-align: center;
}

.source-list,
.level-list {
  width: 100%;
  margin-top: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.source-item,
.level-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-2);
  background-color: var(--color-bg-light);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
}

.source-name,
.level-name {
  font-weight: var(--font-medium);
  color: var(--color-text-primary);
}

.source-count,
.level-count {
  font-weight: var(--font-bold);
  color: var(--color-primary);
}

.timeline-list,
.heatmap-list {
  width: 100%;
  margin-top: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.timeline-item,
.heatmap-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-2);
  background-color: var(--color-bg-light);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
}

.hour-name {
  font-weight: var(--font-medium);
  color: var(--color-text-primary);
}

.hour-count {
  font-weight: var(--font-bold);
  color: var(--color-primary);
}

.timeline-chart {
  height: 250px;
}

.critical-events {
  max-height: 300px;
  overflow-y: auto;
}

.event-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.event-item {
  padding: var(--space-3);
  background-color: rgba(239, 68, 68, 0.05);
  border-left: 3px solid var(--color-danger);
  border-radius: var(--radius-md);
}

.event-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-1);
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
}

.event-message {
  font-size: var(--text-sm);
  color: var(--color-text-primary);
  line-height: var(--leading-relaxed);
}

.pagination-container {
  margin-top: var(--space-4);
  display: flex;
  justify-content: center;
  padding: var(--space-2);
  background-color: var(--color-bg-light);
  border-radius: var(--radius-md);
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-4);
  padding: var(--space-4);
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-3);
  background-color: var(--color-bg-light);
  border-radius: var(--radius-md);
  transition: all var(--duration-fast) var(--ease-in-out);
}

.stat-item:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.stat-value {
  font-size: var(--text-2xl);
  font-weight: var(--font-bold);
  color: var(--color-text-primary);
  margin-bottom: var(--space-1);
}

.stat-label {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  text-align: center;
}

/* Responsive */
@media (max-width: 768px) {
  .analytics-grid {
    grid-template-columns: 1fr;
  }

  .chart-container {
    height: 250px;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
