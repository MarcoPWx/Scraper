<template>
  <div class="mc">
    <div class="mc-head">
      <strong>Mastery Checklist</strong>
      <span class="mc-progress" v-if="items.length">{{ percent }}%</span>
    </div>
    <ul class="mc-list">
      <li v-for="(label, i) in items" :key="i">
        <label>
          <input type="checkbox" :checked="state[i]" @change="toggle(i, ($event.target as HTMLInputElement).checked)" />
          <span>{{ label }}</span>
        </label>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'

interface Props {
  id: string
  items: string[]
}

const props = defineProps<Props>()
const key = `mastery:${props.id}`
const state = ref<boolean[]>([])

const load = () => {
  try {
    const raw = localStorage.getItem(key)
    const parsed: boolean[] | null = raw ? JSON.parse(raw) : null
    state.value = props.items.map((_, i) => parsed?.[i] ?? false)
  } catch {
    state.value = props.items.map(() => false)
  }
}

const save = () => {
  try { localStorage.setItem(key, JSON.stringify(state.value)) } catch {}
}

onMounted(load)
watch(() => props.items.length, load)
watch(state, save, { deep: true })

const toggle = (index: number, checked: boolean) => {
  state.value[index] = checked
}

const percent = computed(() => {
  if (!state.value.length) return 0
  const done = state.value.filter(Boolean).length
  return Math.round((done / state.value.length) * 100)
})
</script>

<style scoped>
.mc { border: 1px solid var(--vp-c-border); border-radius: 8px; padding: 12px; }
.mc-head { display:flex; justify-content:space-between; align-items:center; margin-bottom:8px; }
.mc-progress { background: var(--vp-c-brand-soft); color: var(--vp-c-brand-1); padding: 2px 8px; border-radius: 999px; font-size: 12px; }
.mc-list { list-style: none; padding: 0; margin: 0; }
.mc-list li { margin: 6px 0; }
label { display:flex; gap: 8px; align-items: center; }
</style>

