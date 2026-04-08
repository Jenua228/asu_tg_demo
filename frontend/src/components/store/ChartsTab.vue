<script setup>
import { ref, watch, onMounted, computed, toRefs } from 'vue'

const props = defineProps({
sharedData: {
    type: Array,
    required: true,
    validator: value => value.every(item =>
        typeof item === 'object' &&
        'label' in item &&
        'value' in item
        )
},
xAxisTitle: {
    type: String,
    default: 'Categories'
},
yAxisTitle: {
    type: String,
    default: "Values"
},
itemCount1: {
    type: Number,
    default: 5
}
})
const { sharedData, xAxisTitle, yAxisTitle, itemCount1 } = toRefs(props)
const emit = defineEmits(['bar-hover', 'bar-click'])
const itemCount = ref(props.itemCount1);
// для сохранения настроек просмотра
// onMounted(() => {
//   const saved = localStorage.getItem('itemCount')
//     if (saved) {
//         itemCount.value = Number (saved)
//     }
// })
// watch(itemCount, (newCount) => {
//   localStorage.setItem('itemCount', newCount.toString())})

const maxValue = ref(0);
const yAxisTicks = ref([]);
const activeBarIndex = ref(null);
const hoveredBarIndex = ref(null); 
const selectedBar = ref(null);
const selectedBarIndex = ref(null);

const maxItems = computed(() => Math.max(...sharedData.value.map(item => item.value), 10))
const displayedData = computed(() => sharedData.value.filter(item => item.value >= itemCount.value))
const calculateMaxValue = () => {
    if (displayedData.length === 0) {
        return 100;
    }
    maxValue.value = Math.max(...displayedData.value.map(item => item.value), 10);
}
const generateAxisTicks = () => {
    const tickCount = 5;
    const tickStep = maxValue / (tickCount - 1);
    yAxisTicks.value = Array.from({ length: tickCount }, (_, i) => Math.round(tickStep * i)).reverse();
}
const barStyle = (value) => {
    const percentage = (value / maxValue.value) * 100;
    return {
        height: `${percentage}%`,
        backgroundColor: getColor(value)        
    };
    
}
const getColor = (value) => {
    const hue = 120 - (value / maxValue.value) * 1200; //Math.floor(Math.random() * 360);
    return `hsl(${hue}, 70%, 60%)`;
}
const handleBarClick  = (item, index) => {
    // если нужно открывать в компоненте
    activeBarIndex.value = index;
    selectedBar.value = item;
    selectedBarIndex.value = index;
    emit('bar-click', item)
}
const handleBarHover = (item, index, isHovered) => {
    hoveredBarIndex.value = isHovered ? index : null; emit('bar-hover', {item, index, isHovered})
}
onMounted(calculateMaxValue)
onMounted(generateAxisTicks)

watch(maxValue, generateAxisTicks)
watch(() => displayedData, [calculateMaxValue, generateAxisTicks], {deep: true})

</script>

<template> 
 
    <div class="chart-container">
        <div class="controls">
            <label for="itemCount">Минимальное количество: {{ itemCount }}</label>
                <input 
                    id="itemCount"
                    type="range"
                    v-model.number="itemCount"
                    :min="1"
                    :max="maxItems"
                    >
        </div>
       
        <div class="chart  grid-background" ref="chartContainer">
            <div v-for="(item, index) in displayedData"
            :key="index"
            class="bar-container"
            @click="handleBarClick(item, index)"
            @mouseenter="handleBarHover( item, index, true)"
            @mouseleave="handleBarHover( item, index, false)"
            >
                <div class="bar" :style="barStyle(item.value)"
                                :class="{ 'active': activeBarIndex === index, 'hovered': hoveredBarIndex === index}"></div>
                <div class="bar-label">{{ item.label }}</div>
                <div class="bar-value">{{ item.value }}</div>
                <div class="tick-line"></div>
            </div>

            <div class="x-axis">
                <div class="axis-title x-title">{{ xAxisTitle }}</div>
            </div>
        </div>
    </div>
    
    
</template>

<style scoped>
.chart-container {
    font-family: Arial, Helvetica, sans-serif;
    min-width: 900px;
    margin: 0 auto;
    padding: 10px;
    overflow: auto;
    
}
.controls {
    margin-bottom: 20px;
    display: flex;
    flex-direction: column;
    gap: 10px;
}

input[type="range"] {
    width: 100%;
}
.grid-container {
    display: flex;
    position: relative;
    width: 100%;
    height: 100%;
    background-color: #f0f0f0;
    overflow: hidden;
    z-index: 2;

    
}
.grid-container::before {
    display: flex;
    content: ""; 
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 100%;
    background: linear-gradient(to bottom, transparent 0%, transparent calc(100% / 10 - 1px), black calc(100% / 10 -1px), black calc(100% / 10), transparent calc(100% /10), transparent 100%);
    background-size:100% calc(100% / 10)100%;
    z-index: 2;
    /* rotate: 180deg; */
}
.grid-container::after {
    display: flex;
    content: ""; 
    position: absolute;
    top: 0;
    left: 0;
    bottom: 0;
    width: 100%;
    background: linear-gradient(to right, transparent 0%, transparent calc(100% / 10 - 1px), black calc(100% / 10 -1px), black calc(100% / 10), transparent 100%);
    background-size: calc(100% / 10)100%;
    z-index: 2;
    /* rotate: 180deg; */
}
.grid-background {
    position: absolute;
    top: 0%;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 2;
    background-image: linear-gradient(to bottom, rgb(209, 204, 204) 1px, transparent 1px);
    background-size: 100 calc(100% / 10);
    background-image: linear-gradient(to right,rgb(209, 204, 204) 1px, transparent 1px), linear-gradient(to bottom, rgb(209, 204, 204) 1px, transparent 1px);
    background-size: calc(100% / 10)100%, 100% calc(100% / 10);
}


.chart {
    display: flex;
    height: 500px;
    align-items: flex-end;
    justify-content: space-around;
    gap: 10px;
    padding: 0 20px 40px 20px;
    border: 1px solid #eee;
    border-radius: 8px;
    background-color: #f9f9f9e1;
    flex-grow: 1;
    position: relative;
    transform: rotate(180deg);

    /* rotate: 180deg; */
}
y-axis {
    width: 40px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding-right: 10 px;
}
y-tick {
    display: flex;
    align-items: center;
    height: 0;
    position: relative;
}
.tick-value {
    font-size: 12 px;
    color: #665;
}
.tick-line {
    flex-grow: 1;
    height: 1px;
    background-color: #1d1414;
    margin-left: 5px;
}

.x-axis {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 20px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.axis-title {
    font-size: 16px;
    font-weight: bold;
    color: #665;
    text-align: center;
}
.y-title {
    position: absolute;
    top: 50%;
    left: -30px;
    transform: rotate(-90deg) translateX(-50%);
    transform-origin: left center;
    width: 100%;
        
}
.x-title {
    position: absolute;
    bottom: -25%;
    left: 50%;
    transform: translateX(-50%);
    transform: rotate(180deg);

    /* rotate: 180deg; */
}

.bar-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    flex: 1;
    gap: 5px;
    height: 100%;
    min-width: 40px;
    cursor: pointer;
    transition: transform 0.2s;
}
.bar-container:hover {
    transform: translateX(-2px);
}
.bar {
    width: 100%;
    max-width: 60px;
    transition: height 0.3s ease;
    border-radius: 4px 4px 0 0;
    background-color: #42b983;
    transform: rotate(180deg);

    /* rotate: 180deg; */
}
.bar.active {
    filter: brightness(0.3);
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
}
.bar.hovered {
    filter: brightness(0.3);
    transform: scaleX(1.05);
}
.bar-label {
    font-size: 12px;
    text-align: center;
    margin-top: 5px;
    word-break: break-word;
    max-width: 100%;
    transform: rotate(180deg);

    /* rotate: 180deg; */
}
.bar-value {
    font-size: 12px;
    font-weight: bold;
    margin-top: 5px;
    transform: rotate(180deg);

    /* rotate: 180deg; */
}
.selection-info {
    margin-top: 20 px;
    padding: 15 px;
    background-color: #f5f5f5;
    border-radius: 8px;
}
</style>