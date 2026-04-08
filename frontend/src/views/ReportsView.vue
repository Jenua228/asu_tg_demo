<template>
  <div class="reports-view">
    <AgGridDemo @navigate-to-detail="$emit('navigate-to-detail', $event)" />
  </div>
</template>

<script setup>
import AgGridDemo from '../components/AgGridDemo.vue'

defineEmits(['navigate-to-detail'])
</script>

<style scoped>
.reports-view {
  padding: 16px;
  height: 100%;
  display: flex;
  flex-direction: column;
}
</style>
