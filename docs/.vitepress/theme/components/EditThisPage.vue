<template>
  <div v-if="url" class="edit-callout">
    <a :href="url" target="_blank" rel="noreferrer">✏️ Edit this page on GitHub</a>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useData } from 'vitepress'

const { page, theme } = useData()
const url = computed(() => {
  const patt = theme.value.editLink?.pattern as string | undefined
  const rel = page.value.relativePath
  if (!patt || !rel) return null
  return patt.replace(':path', rel)
})
</script>

<style scoped>
.edit-callout {
  margin: 16px 0;
  padding: 10px 12px;
  border: 1px solid var(--vp-c-border);
  border-radius: 8px;
  background: var(--vp-c-bg-soft);
}
.edit-callout a { text-decoration: none; font-weight: 600; }
</style>

