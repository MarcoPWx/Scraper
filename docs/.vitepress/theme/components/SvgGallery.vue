<template>
  <div class="gal">
    <div class="grid">
      <figure v-for="(item, idx) in items" :key="idx">
        <img :src="item.url" :alt="item.name" />
        <figcaption>{{ item.name }}</figcaption>
      </figure>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

// Loads all SVGs in assets/architecture at build time
// Eager + as: 'url' provides URLs ready for <img>
const modules = import.meta.glob('../../assets/architecture/*.svg', { eager: true, as: 'url' }) as Record<string, string>

const items = computed(() => {
  return Object.entries(modules)
    .map(([path, url]) => ({ path, url, name: path.split('/').pop()?.replace('.svg','') || 'diagram' }))
    .sort((a, b) => a.name.localeCompare(b.name))
})
</script>

<style scoped>
.grid { display:grid; grid-template-columns: repeat(auto-fill, minmax(260px,1fr)); gap:16px; }
figure { margin:0; border:1px solid var(--vp-c-border); border-radius:8px; padding:8px; background: var(--vp-c-bg-soft); }
img { width:100%; height:auto; display:block; }
figcaption { font-size:12px; color: var(--vp-c-text-2); margin-top:6px; text-align:center; }
</style>

