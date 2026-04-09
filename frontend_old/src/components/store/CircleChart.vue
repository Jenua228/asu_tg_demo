<template>
    <div class="chart-card">
      <h3>{{ title }}</h3>
      <div class="chart-container">
        <svg width="200" height="200" viewBox="0 0 200 200">
          <!-- Фон круга -->
          <circle cx="100" cy="100" r="90" fill="#f0f0f0" />
          
          <!-- Основной сегмент -->
          <circle
            cx="100"
            cy="100"
            r="85"
            fill="none"
            stroke="#007bff"
            :stroke-width="30"
            :stroke-dasharray="circumference"
            :stroke-dashoffset="dashOffset"
            stroke-linecap="round"
            transform="rotate(-90 100 100)"
          />
          
          <!-- Центральный текст -->
          <text x="100" y="100" text-anchor="middle" dy="5" font-size="20">
            {{ percentage }}%
          </text>
          <text x="100" y="125" text-anchor="middle" dy="5" font-size="12" fill="#666">
            {{ label }}
          </text>
        </svg>
        
        <div class="chart-legend">
          <div class="legend-item">
            <span class="legend-color" style="background-color: #007bff;"></span>
            <span>Выполнено: {{ value }} из {{ total }}</span>
          </div>
          <div class="legend-item">
            <span class="legend-color" style="background-color: #f0f0f0;"></span>
            <span>Осталось: {{ total - value }}</span>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { computed } from 'vue'
  
  const props = defineProps({
    title: String,
    value: Number,
    total: Number,
    label: {
      type: String,
      default: 'Выполнено'
    }
  })
  
  const percentage = computed(() => {
    return Math.round((props.value / props.total) * 100)
  })
  
  const circumference = computed(() => {
    return 2 * Math.PI * 90 // 2πr
  })
  
  const dashOffset = computed(() => {
    return circumference.value * (1 - props.value / props.total)
  })
  </script>
  
  <style scoped>
  .chart-card {
    background: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
  
  .chart-container {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 30px;
    margin-top: 15px;
  }
  
  .chart-legend {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  
  .legend-item {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  
  .legend-color {
    width: 20px;
    height: 20px;
    border-radius: 4px;
  }
  </style>
  