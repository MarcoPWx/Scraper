<template>
  <div class="dash">
    <div class="summary">
      <div class="card">
        <div class="num">{{ total }}</div>
        <div class="label">Total checklists</div>
      </div>
      <div class="card">
        <div class="num">{{ completed }}</div>
        <div class="label">Total items completed</div>
      </div>
      <div class="card">
        <div class="num">{{ percent }}%</div>
        <div class="label">Overall progress</div>
      </div>
    </div>

    <table v-if="rows.length">
      <thead>
        <tr>
          <th>Checklist</th>
          <th>Done</th>
          <th>Total</th>
          <th>Progress</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="r in rows" :key="r.id">
          <td><code>{{ r.id }}</code></td>
          <td>{{ r.done }}</td>
          <td>{{ r.total }}</td>
          <td>{{ r.pct }}%</td>
        </tr>
      </tbody>
    </table>

    <p v-else class="muted">No mastery data found in localStorage yet. Visit some lessons and check items.</p>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

interface Row { id: string; done: number; total: number; pct: number }
const rows = ref<Row[]>([])

onMounted(() => {
  try {
    const keys = Object.keys(localStorage).filter(k => k.startsWith('mastery:'))
    rows.value = keys.map(k => {
      const arr: boolean[] = JSON.parse(localStorage.getItem(k) || '[]')
      const total = arr.length
      const done = arr.filter(Boolean).length
      const pct = total ? Math.round((done / total) * 100) : 0
      return { id: k.replace('mastery:', ''), done, total, pct }
    }).sort((a, b) => a.id.localeCompare(b.id))
  } catch {
    rows.value = []
  }
})

const total = computed(() => rows.value.length)
const completed = computed(() => rows.value.reduce((s, r) => s + r.done, 0))
const percent = computed(() => {
  const t = rows.value.reduce((s, r) => s + r.total, 0)
  const d = rows.value.reduce((s, r) => s + r.done, 0)
  return t ? Math.round((d / t) * 100) : 0
})
</script>

<style scoped>
.dash { border: 1px solid var(--vp-c-border); border-radius: 8px; padding: 12px; }
.summary { display: flex; gap: 12px; margin-bottom: 12px; }
.card { flex: 1; border: 1px solid var(--vp-c-border); border-radius: 8px; padding: 12px; text-align: center; }
.num { font-size: 20px; font-weight: 700; }
.label { color: var(--vp-c-text-2); font-size: 12px; }
table { width: 100%; border-collapse: collapse; }
th, td { border-top: 1px solid var(--vp-c-divider); padding: 6px 8px; text-align: left; }
.muted { color: var(--vp-c-text-2); }
</style>

