<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: String,
  data: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['bar-click'])

const maxValue = computed(() => {
  return Math.max(...props.data.map(item => item.value), 1)
})

const yTicks = computed(() => {
  const ticks = []
  const step = Math.ceil(maxValue.value / 5)
  for (let i = 0; i <= maxValue.value; i += step) {
    ticks.push(i)
  }
  return ticks.reverse()
})

const onBarClick = (bar) => {
  emit('bar-click', bar)
}
</script>

<template>
  <div class="chart-card">
    <h3>{{ title }}</h3>
    <hr>
    <div class="bar-chart-container">
      <div class="bars">
        <div
          v-for="(bar, index) in data"
          :key="index"
          class="bar-wrapper"
          @click="onBarClick(bar)"
        >
          <div class="bar-container">
            <div
              class="bar"
              :style="{
                height: `${(bar.value / maxValue) * 100}%`,
                backgroundColor: bar.color || '#007bff'
              }"
              :title="`${bar.label}: ${bar.value}`"
            >
              <span class="bar-value">{{ bar.value }}</span>
            </div>
          </div>
          <div class="bar-x-label">{{ bar.label }}</div>
        </div>
      </div>
      <div class="y-axis">
        <div v-for="tick in yTicks" :key="tick" class="y-tick">
          {{ tick }}
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.bar-chart-container {
  display: flex;
  margin-top: 20px;
  height: 300px;
}

.bars {
  display: flex;
  flex: 1;
  align-items: flex-end;
  justify-content: space-around;
  border-bottom: 2px solid #ddd;
  border-left: 2px solid #ddd;
  padding: 0 20px;
  position: relative;
}

.bar-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 60px;
  cursor: pointer;
  transition: transform 0.2s;
}

.bar-wrapper:hover {
  transform: translateY(-5px);
}

.bar-container {
  height: 200px;
  display: flex;
  align-items: flex-end;
  width: 100%;
}

.bar {
  width: 40px;
  border-radius: 4px 4px 0 0;
  position: relative;
  transition: height 0.3s ease;
}

.bar-value {
  position: absolute;
  top: -25px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 12px;
  font-weight: bold;
  color: #333;
}

.bar-label {
  position: absolute;
  top: -45px;
  font-size: 12px;
  text-align: center;
  width: 100%;
}

.bar-x-label {
  margin-top: 10px;
  font-size: 12px;
  text-align: center;
  color: #667;
}

.y-axis {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding-right: 10px;
  margin-bottom: 30px;
}

.y-tick {
  font-size: 12px;
  color: #667;
  text-align: right;
}
</style>