<template>
  <div class="recent">
    <template v-if="mode === 'pages'">
      <ul>
        <li v-for="p in pages" :key="p.route">
          <a :href="p.route">{{ p.title }}</a>
          <span class="meta">· {{ new Date(p.updated_at).toLocaleString() }}</span>
        </li>
      </ul>
      <div v-if="error" class="error">Failed to load prebuilt recent pages: {{ error }}</div>
    </template>
    <template v-else>
      <div v-if="error" class="error">Failed to load recent commits (rate limit?).</div>
      <ul v-else>
        <li v-for="c in commits" :key="c.sha">
          <a :href="c.html_url" target="_blank" rel="noreferrer">{{ c.commit.message }}</a>
          <span class="meta">· {{ new Date(c.commit.author.date).toLocaleString() }} by {{ c.commit.author.name }}</span>
        </li>
      </ul>
    </template>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'

type Mode = 'pages' | 'commits'

interface PageItem { route: string; title: string; updated_at: string }
interface Commit {
  sha: string
  html_url: string
  commit: {
    message: string
    author: { name: string; date: string }
  }
}

const mode = ref<Mode>('pages')
const pages = ref<PageItem[]>([])
const commits = ref<Commit[]>([])
const error = ref<string | null>(null)

onMounted(async () => {
  // Prefer local prebuilt JSON if present
  try {
    const res = await fetch('/recent.json', { cache: 'no-cache' })
    if (res.ok) {
      const data = await res.json()
      pages.value = data.items || []
      if (pages.value.length) return
    }
  } catch (e: any) {
    error.value = e?.message || 'error'
  }
  // Fallback to GitHub commits API
  try {
    mode.value = 'commits'
    const url = new URL('https://api.github.com/repos/MarcoPWx/Scraper/commits')
    url.searchParams.set('path', 'docs')
    url.searchParams.set('per_page', '10')
    const res = await fetch(url.toString(), { headers: { 'Accept': 'application/vnd.github+json' } })
    if (!res.ok) throw new Error(`${res.status}`)
    commits.value = await res.json()
  } catch (e: any) {
    error.value = e?.message || 'error'
  }
})
</script>

<style scoped>
.recent ul { margin: 0; padding-left: 16px; }
.meta { color: var(--vp-c-text-2); margin-left: 8px; font-size: 12px; }
.error { color: var(--vp-c-danger-1); }
</style>

