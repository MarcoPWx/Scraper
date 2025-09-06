<template>
  <div class="board">
    <div class="toolbar">
      <button class="btn" @click="refresh">Update Now</button>
      <label>Milestone: <input v-model="milestone" placeholder="name or *" /></label>
      <label>Label filter: <input v-model="labelFilter" placeholder="comma-separated" /></label>
      <span v-if="updatedAt" class="meta">Last fetched: {{ new Date(updatedAt).toLocaleString() }}</span>
      <span v-if="error" class="error">Fetch failed ({{ error }}). Using cache if available.</span>
    </div>
    <div class="cols">
      <div class="col" v-for="col in columns" :key="col.id">
        <h3>{{ col.title }}</h3>
        <ul>
          <li v-for="i in col.items" :key="i.id">
            <a :href="i.html_url" target="_blank" rel="noreferrer">#{{ i.number }} — {{ i.title }}</a>
            <div class="labels">
              <span class="label" v-for="l in i.labels" :key="l.id">{{ l.name }}</span>
            </div>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

interface Label { id: number; name: string }
interface Milestone { title: string | null }
interface Issue {
  id: number
  number: number
  title: string
  html_url: string
  labels: Label[]
  state: 'open' | 'closed'
  milestone: Milestone | null
  pull_request?: any
}

const props = withDefaults(defineProps<{
  owner?: string
  repo?: string
  state?: 'open' | 'closed' | 'all'
  statusLabels?: string[] // e.g., ['status:todo','status:doing','status:done']
}>(), {
  owner: 'MarcoPWx',
  repo: 'Scraper',
  state: 'open',
  statusLabels: ['status:todo', 'status:doing', 'status:done']
})

const all = ref<Issue[]>([])
const error = ref<string | null>(null)
const updatedAt = ref<number | null>(null)
const milestone = ref<string>('*')
const labelFilter = ref<string>('task')

const cacheKey = `gh:board:${props.owner}:${props.repo}:${props.state}`

async function fetchIssuesPage(page: number): Promise<Issue[]> {
  const url = new URL(`https://api.github.com/repos/${props.owner}/${props.repo}/issues`)
  url.searchParams.set('state', props.state)
  url.searchParams.set('per_page', '100')
  url.searchParams.set('page', String(page))
  const res = await fetch(url.toString(), { headers: { 'Accept': 'application/vnd.github+json' } })
  if (!res.ok) throw new Error(`${res.status}`)
  const data: Issue[] = await res.json()
  return data.filter(i => !('pull_request' in i))
}

async function refresh() {
  try {
    error.value = null
    // fetch up to 3 pages (300 issues) for safety
    const pages = await Promise.all([1,2,3].map(p => fetchIssuesPage(p)))
    all.value = pages.flat()
    updatedAt.value = Date.now()
    localStorage.setItem(cacheKey, JSON.stringify({ all: all.value, updatedAt: updatedAt.value }))
  } catch (e: any) {
    error.value = e?.message || 'error'
  }
}

onMounted(async () => {
  try {
    const raw = localStorage.getItem(cacheKey)
    if (raw) {
      const { all: cached, updatedAt: ts } = JSON.parse(raw)
      all.value = cached || []
      updatedAt.value = ts || null
    }
  } catch {}
  await refresh()
})

const columns = computed(() => {
  const m = milestone.value?.trim()
  const labels = labelFilter.value.split(',').map(s => s.trim()).filter(Boolean)
  const filtered = all.value.filter(i => {
    const milestoneOk = !m || m === '*' || (i.milestone?.title || '').toLowerCase() === m.toLowerCase()
    const labelsOk = !labels.length || labels.every(l => i.labels.some(L => L.name.toLowerCase() === l.toLowerCase()))
    return milestoneOk && labelsOk
  })
  const map: Record<string, Issue[]> = {}
  props.statusLabels.forEach(l => { map[l] = [] })
  const other: Issue[] = []
  for (const issue of filtered) {
    const status = issue.labels.map(l => l.name).find(n => props.statusLabels.includes(n))
    if (status) map[status].push(issue)
    else other.push(issue)
  }
  const cols = props.statusLabels.map((l, idx) => ({ id: l, title: l.replace('status:','').toUpperCase(), items: map[l] }))
  if (other.length) cols.push({ id: 'other', title: 'OTHER', items: other })
  return cols
})
</script>

<style scoped>
.board { border: 1px solid var(--vp-c-border); border-radius: 8px; padding: 12px; }
.toolbar { display:flex; gap:12px; align-items:center; margin-bottom:8px; flex-wrap: wrap; }
.btn { background: var(--vp-c-brand-1); color:#fff; border:none; border-radius:6px; padding:6px 10px; cursor:pointer; }
.btn:hover { opacity:.9; }
.cols { display:grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.col { background: var(--vp-c-bg-soft); border:1px solid var(--vp-c-border); border-radius:8px; padding: 8px; }
.col h3 { margin-top:0; font-size:14px; }
.col ul { margin:0; padding-left: 16px; }
.label { display:inline-block; background: var(--vp-c-default-soft); color: var(--vp-c-text-1); padding: 1px 6px; border-radius:999px; margin-right:4px; font-size:12px; }
.meta { color: var(--vp-c-text-2); font-size:12px; }
.error { color: var(--vp-c-danger-1); }
</style>

