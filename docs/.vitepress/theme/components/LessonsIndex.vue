<template>
  <div class="lessons-index">
    <ul>
      <li v-for="e in entries" :key="e.route">
        <a :href="e.route">{{ e.title }}</a>
        <span class="spacer"></span>
        <ProgressPill :id="e.id" />
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

// Import all lessons markdown so we can read their frontmatter and build routes
// Path is relative to this file: docs/.vitepress/theme/components -> ../../lessons/*.md
const mods = import.meta.glob('../../lessons/*.md', { eager: true }) as Record<string, any>

const entries = computed(() => {
  return Object.entries(mods)
    .map(([path, mod]) => {
      const name = path.split('/').pop()?.replace('.md', '') || ''
      if (!name || name === 'TEMPLATE_MINILAB') return null
      const route = `/lessons/${name}`
      const title = mod?.frontmatter?.title || name
      const id = mod?.frontmatter?.lessonId || `lessons/${name}`
      return { route, title, id }
    })
    .filter(Boolean)
    // Sort numerically by leading number if present (00, 01, 02...), else by title
    .sort((a: any, b: any) => {
      const an = a.route.match(/\/(\d{2})/)?.[1]
      const bn = b.route.match(/\/(\d{2})/)?.[1]
      if (an && bn) return Number(an) - Number(bn)
      return a.title.localeCompare(b.title)
    })
})
</script>

<style scoped>
.lessons-index ul { list-style: none; padding: 0; margin: 0; }
.lessons-index li { display: flex; align-items: center; gap: 8px; padding: 6px 0; border-top: 1px solid var(--vp-c-divider); }
.lessons-index li:first-child { border-top: none; }
.spacer { flex: 1; }
</style>

