<template>
  <!-- ag-tooltip-custom — стандартный класс AG Grid для кастомных тултипов -->
  <div class="custom-tooltip ag-tooltip-custom">
    <div class="image-container">
      <!-- Путь формируется от корня папки public -->
      <img :src="`/store/${params.data.imgName}`" alt="Preview" class="tolltip-image" />
    </div>
    <div class="tooltip-text">{{ params.value }}</div>
  </div>
</template>

<script setup>
const props = defineProps(['params']);
</script>

<style>
.custom-tooltip {

  transform: translateX(20vh);
}

.tolltip-image{
  max-width: 400px;
  height: auto;
  display: block;
  object-fit: contain;
}

.image-container img {
  display: block;
  max-width: 400px;
  height: auto;
  padding: 12px;
  border: 1px solid #babed7;
  border-radius: 4px;
  background: #ffffff;

  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
  margin-bottom: 8px;
  border-radius: 2px;
}

.tooltip-text {
  color: #33333300;
}
</style>
