<template>
    <div class="charts-container">

        <!-- Круговая диаграмма -->

          <div class="pie-chart-container">
            <svg :width="300" :height="300" class="pie-chart">
              <g :transform="`translate(150, 150)`">
                <path
                  v-for="(workshop, index) in workshops"
                  :key="workshop.id"
                  :d="getPieSegment(workshop.workload, index)"
                  :fill="workshop.color || getColorForWorkload(workshop.workload)"
                  class="pie-segment"
                  @click="$emit('workshop-select', workshop)"
                  @mouseenter="hoveredWorkshop = workshop"
                  @mouseleave="hoveredWorkshop = null"
                />
                <circle cx="0" cy="0" r="60" fill="white" />
                <text
                  v-if="hoveredWorkshop"
                  text-anchor="middle"
                  font-size="14"
                  fill="#333"
                >
                  {{ hoveredWorkshop.name }}
                </text>
                <text
                  v-if="hoveredWorkshop"
                  text-anchor="middle"
                  y="20"
                  font-size="18"
                  font-weight="bold"
                  :fill="getColorForWorkload(hoveredWorkshop.workload)"
                >
                  {{ hoveredWorkshop.workload }}%
                </text>
              </g>
            </svg>
          </div>
          <div class="legend">
            <div
              v-for="workshop in workshops"
              :key="workshop.id"
              class="legend-item"
              @click="$emit('workshop-select', workshop)"
            >
              <div
                class="legend-color"
                :style="{ backgroundColor: workshop.color || getColorForWorkload(workshop.workload) }"
              ></div>
              <span class="legend-name">{{ workshop.name }}</span>
              <span class="legend-value">{{ workshop.workload }}%</span>
            </div>
          </div>
  
  
        <!-- Столбчатая диаграмма -->
   
      </div>

  </template>
  
  <script setup>
  import { ref } from 'vue'
  
  const props = defineProps({
    workshops: {
      type: Array,
      default: () => []
    },
    totalWorkload: {
      type: Number,
      default: 0
    }
  })
  console.log(props.workshops)
  
  const emit = defineEmits(['workshop-select'])
  
  const hoveredWorkshop = ref(null)
  const hoveredSection = ref(null)
  
  const getColorForWorkload = (workload) => {
    if (workload >= 80) return '#f44336'
    if (workload >= 60) return '#ff9800'
    if (workload >= 40) return '#4CAF50'
    return '#2196F3'
  }
  
  const getPieSegment = (percentage, index) => {
    const total = props.workshops.reduce((sum, w) => sum + w.workload, 0)
    const startAngle = props.workshops
      .slice(0, index)
      .reduce((sum, w) => sum + (w.workload / total) * 360, 0)
    const angle = (percentage / total) * 360
    
    const startRad = (startAngle - 90) * Math.PI / 180
    const endRad = (startAngle + angle - 90) * Math.PI / 180
    
    const x1 = 100 * Math.cos(startRad)
    const y1 = 100 * Math.sin(startRad)
    const x2 = 100 * Math.cos(endRad)
    const y2 = 100 * Math.sin(endRad)
    
    const largeArc = angle > 180 ? 1 : 0
    
    return `M 0 0 L ${x1} ${y1} A 100 100 0 ${largeArc} 1 ${x2} ${y2} Z`
  }
  </script>
  
  <style scoped>
  .charts-container {
    background: white;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    margin-bottom: 24px;
  }
  
  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
  }
  
  .header h2 {
    margin: 0;
    color: #333;
    font-size: 24px;
  }
  
  .total-workload {
    font-size: 16px;
    color: #666;
  }
  
  .total-workload span {
    font-weight: bold;
    font-size: 20px;
  }
  
  .charts-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
  }
  
  .chart-card {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 20px;
  }
  
  .chart-card h3 {
    margin: 0 0 16px 0;
    color: #444;
    font-size: 18px;
  }
  
  .pie-chart-container {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-bottom: 16px;
  }
  
  .pie-segment {
    cursor: pointer;
    transition: opacity 0.3s;
  }
  
  .pie-segment:hover {
    opacity: 0.8;
  }
  
  .legend {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  
  .legend-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 6px 12px;
    border-radius: 6px;
    cursor: pointer;
    transition: background-color 0.3s;
  }
  
  .legend-item:hover {
    background-color: rgba(0, 0, 0, 0.05);
  }
  
  .legend-color {
    width: 16px;
    height: 16px;
    border-radius: 4px;
  }
  
  .legend-name {
    flex: 1;
    font-size: 14px;
    color: #333;
  }
  
  .legend-value {
    font-weight: bold;
    color: #333;
  }
  
  .bar-chart-container {
    overflow-x: auto;
  }
  
  .bar {
    cursor: pointer;
    transition: opacity 0.3s;
  }
  
  .bar:hover {
    opacity: 0.9;
  }
  
  .tooltip {
    margin-top: 16px;
    padding: 8px 12px;
    background: #333;
    color: white;
    border-radius: 4px;
    font-size: 14px;
    animation: fadeIn 0.3s;
  }
  
  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }
  
  @media (max-width: 1024px) {
    .charts-grid {
      grid-template-columns: 1fr;
    }
  }
  </style>