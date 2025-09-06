<template>
  <span class="pill">{{ percent }}%</span>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'

interface Props { id: string; items?: number }
const props = defineProps<Props>()
const key = `mastery:${props.id}`
const percent = ref(0)

const calc = () => {
  try {
    const raw = localStorage.getItem(key)
    if (!raw) { percent.value = 0; return }
    const arr: boolean[] = JSON.parse(raw)
    const total = props.items ?? arr.length
    const done = arr.filter(Boolean).length
    percent.value = total > 0 ? Math.round((done / total) * 100) : 0
  } catch { percent.value = 0 }
}

onMounted(calc)
watch(() => props.id, calc)

</script>

<style scoped>
.pill { display:inline-flex; align-items:center; justify-content:center; min-width:36px; padding:2px 8px; border-radius:999px; background: var(--vp-c-brand-soft); color: var(--vp-c-brand-1); font-weight:600; font-size:12px; }
</style>

