<template>
  <div class="skeleton-loader" :class="typeClass">
    <!-- Text skeleton -->
    <div v-if="type === 'text'" class="skeleton-text" :style="{ width: width }"></div>
    
    <!-- Card skeleton -->
    <div v-else-if="type === 'card'" class="skeleton-card">
      <div class="skeleton-card-header">
        <div class="skeleton-avatar"></div>
        <div class="skeleton-card-title">
          <div class="skeleton-text" style="width: 60%"></div>
          <div class="skeleton-text" style="width: 40%; height: 12px"></div>
        </div>
      </div>
      <div class="skeleton-card-body">
        <div class="skeleton-text" style="width: 100%"></div>
        <div class="skeleton-text" style="width: 90%"></div>
        <div class="skeleton-text" style="width: 80%"></div>
      </div>
    </div>
    
    <!-- List skeleton -->
    <div v-else-if="type === 'list'" class="skeleton-list">
      <div v-for="i in rows" :key="i" class="skeleton-list-item">
        <div class="skeleton-avatar"></div>
        <div class="skeleton-list-content">
          <div class="skeleton-text" style="width: 70%"></div>
          <div class="skeleton-text" style="width: 50%; height: 12px"></div>
        </div>
      </div>
    </div>
    
    <!-- Avatar skeleton -->
    <div v-else-if="type === 'avatar'" class="skeleton-avatar" :style="{ width: size, height: size }"></div>
    
    <!-- Image skeleton -->
    <div v-else-if="type === 'image'" class="skeleton-image" :style="{ width: width, height: height }"></div>
    
    <!-- Button skeleton -->
    <div v-else-if="type === 'button'" class="skeleton-button" :style="{ width: width }"></div>
    
    <!-- Custom skeleton -->
    <div v-else class="skeleton-custom">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  type?: 'text' | 'card' | 'list' | 'avatar' | 'image' | 'button' | 'custom'
  width?: string
  height?: string
  size?: string
  rows?: number
  animated?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  width: '100%',
  height: '200px',
  size: '40px',
  rows: 3,
  animated: true
})

const typeClass = computed(() => ({
  'skeleton-animated': props.animated
}))
</script>

<style scoped>
.skeleton-loader {
  width: 100%;
}

/* Base skeleton styles */
.skeleton-text,
.skeleton-avatar,
.skeleton-image,
.skeleton-button,
.skeleton-card,
.skeleton-list-item {
  background: linear-gradient(
    90deg,
    var(--color-bg-tertiary) 0%,
    var(--color-border) 50%,
    var(--color-bg-tertiary) 100%
  );
  background-size: 200% 100%;
  border-radius: 4px;
}

.skeleton-animated .skeleton-text,
.skeleton-animated .skeleton-avatar,
.skeleton-animated .skeleton-image,
.skeleton-animated .skeleton-button,
.skeleton-animated .skeleton-card,
.skeleton-animated .skeleton-list-item {
  animation: skeleton-loading 1.5s ease-in-out infinite;
}

/* Text skeleton */
.skeleton-text {
  height: 16px;
  margin-bottom: var(--space-2);
}

/* Card skeleton */
.skeleton-card {
  padding: var(--space-4);
  border-radius: 8px;
}

.skeleton-card-header {
  display: flex;
  gap: var(--space-3);
  margin-bottom: var(--space-4);
}

.skeleton-card-title {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.skeleton-card-body {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

/* List skeleton */
.skeleton-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.skeleton-list-item {
  display: flex;
  gap: var(--space-3);
  padding: var(--space-3);
  border-radius: 8px;
}

.skeleton-list-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

/* Avatar skeleton */
.skeleton-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  flex-shrink: 0;
}

/* Image skeleton */
.skeleton-image {
  border-radius: 8px;
}

/* Button skeleton */
.skeleton-button {
  height: 40px;
  border-radius: 8px;
}

/* Animation */
@keyframes skeleton-loading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

/* Dark theme adjustments */
[data-theme='dark'] .skeleton-text,
[data-theme='dark'] .skeleton-avatar,
[data-theme='dark'] .skeleton-image,
[data-theme='dark'] .skeleton-button,
[data-theme='dark'] .skeleton-card,
[data-theme='dark'] .skeleton-list-item {
  background: linear-gradient(
    90deg,
    #2d2d2d 0%,
    #3a3a3a 50%,
    #2d2d2d 100%
  );
  background-size: 200% 100%;
}
</style>
