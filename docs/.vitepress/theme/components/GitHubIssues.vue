<template>
  <div class="gh-issues">
    <div class="toolbar">
      <button class="btn" @click="refresh">Update Now</button>
      <span v-if="updatedAt" class="meta">Last fetched: {{ new Date(updatedAt).toLocaleString() }}</span>
      <span v-if="error" class="error">Fetch failed ({{ error }}). Using cached if available.</span>
    </div>
    <div class="lists">
      <div class="list" v-if="epics.length">
        <h3>Epics ({{ epics.length }})</h3>
        <ul>
          <li v-for="i in epics" :key="i.id">
            <a :href="i.html_url" target="_blank" rel="noreferrer">#{{ i.number }} — {{ i.title }}</a>
            <span class="labels">
              <span class="label" v-for="l in i.labels" :key="l.id">{{ l.name }}</span>
            </span>
            <span class="meta">· {{ new Date(i.updated_at).toLocaleString() }}</span>
          </li>
        </ul>
      </div>
      <div class="list" v-if="tasks.length">
        <h3>Tasks ({{ tasks.length }})</h3>
        <ul>
          <li v-for="i in tasks" :key="i.id">
            <a :href="i.html_url" target="_blank" rel="noreferrer">#{{ i.number }} — {{ i.title }}</a>
            <span class="labels">
              <span class="label" v-for="l in i.labels" :key="l.id">{{ l.name }}</span>
            </span>
            <span class="meta">· {{ new Date(i.updated_at).toLocaleString() }}</span>
          </li>
        </ul>
      </div>
      <div class="list" v-if="!error && !epics.length && !tasks.length">
        <p>No issues found with the requested labels.</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'

interface Label { id: number; name: string }
interface Issue {
  id: number
  number: number
  title: string
  html_url: string
  labels: Label[]
  updated_at: string
  pull_request?: any
}

const props = withDefaults(defineProps<{
  owner?: string
  repo?: string
  epicLabel?: string
  taskLabel?: string
  state?: 'open' | 'closed' | 'all'
}>(), {
  owner: 'MarcoPWx',
  repo: 'Scraper',
  epicLabel: 'epic',
  taskLabel: 'task',
  state: 'open'
})

const epics = ref<Issue[]>([])
const tasks = ref<Issue[]>([])
const error = ref<string | null>(null)
const updatedAt = ref<number | null>(null)

const cacheKey = `gh:issues:${props.owner}:${props.repo}:${props.epicLabel}:${props.taskLabel}:${props.state}`

async function fetchIssues(label: string): Promise<Issue[]> {
  const url = new URL(`https://api.github.com/repos/${props.owner}/${props.repo}/issues`)
  url.searchParams.set('state', props.state)
  url.searchParams.set('per_page', '100')
  url.searchParams.set('labels', label)
  const res = await fetch(url.toString(), { headers: { 'Accept': 'application/vnd.github+json' } })
  if (!res.ok) throw new Error(`${res.status}`)
  const data: Issue[] = await res.json()
  return data.filter(i => !('pull_request' in i))
}

async function refresh() {
  try {
    error.value = null
    const [e, t] = await Promise.all([
      fetchIssues(props.epicLabel),
      fetchIssues(props.taskLabel)
    ])
    epics.value = e
    tasks.value = t
    updatedAt.value = Date.now()
    localStorage.setItem(cacheKey, JSON.stringify({ e, t, updatedAt: updatedAt.value }))
  } catch (e: any) {
    error.value = e?.message || 'error'
  }
}

onMounted(async () => {
  try {
    const raw = localStorage.getItem(cacheKey)
    if (raw) {
      const { e, t, updatedAt: ts } = JSON.parse(raw)
      epics.value = e || []
      tasks.value = t || []
      updatedAt.value = ts || null
    }
  } catch {}
  await refresh()
})
</script>

<style scoped>
.gh-issues { border: 1px solid var(--vp-c-border); border-radius: 8px; padding: 12px; }
.toolbar { display:flex; gap:12px; align-items:center; margin-bottom:8px; }
.btn { background: var(--vp-c-brand-1); color:#fff; border:none; border-radius:6px; padding:6px 10px; cursor:pointer; }
.btn:hover { opacity: .9; }
.list + .list { margin-top: 16px; }
.list h3 { margin: 0 0 8px; }
.list ul { margin: 0; padding-left: 16px; }
.label { display:inline-block; background: var(--vp-c-default-soft); color: var(--vp-c-text-1); padding: 1px 6px; border-radius: 999px; margin-left: 6px; font-size: 12px; }
.meta { color: var(--vp-c-text-2); margin-left: 6px; font-size: 12px; }
.error { color: var(--vp-c-danger-1); }
</style>

