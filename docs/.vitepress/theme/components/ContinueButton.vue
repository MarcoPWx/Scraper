<template>
  <a :href="href" class="continue">
    ▶ Continue where you left off
  </a>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const href = computed(() => {
  try {
    return (
      localStorage.getItem('lastMasterclassLesson') ||
      localStorage.getItem('lastVisitedLesson') ||
      '/lessons/00-intro'
    )
  } catch {
    return '/lessons/00-intro'
  }
})
</script>

<style scoped>
.continue { display:inline-block; padding: 8px 12px; border-radius: 8px; background: var(--vp-c-brand-1); color: white; text-decoration: none; font-weight: 600; }
.continue:hover { opacity: 0.9; }
</style>

