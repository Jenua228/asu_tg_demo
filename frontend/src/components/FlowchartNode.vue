<template>
    <div
      class="flowchart-node"
      :class="[node.type, { selected: isSelected }]"
      :style="{
        left: node.x + 'px',
        top: node.y + 'px',
        zIndex: isSelected ? 100 : 1
      }"
      @mousedown="startDrag"
      @click.stop="select"
      @dblclick.stop="edit"
    >
      <div class="node-header">
        <div class="node-icon">
          <span v-if="node.type === 'start'">▶</span>
          <span v-else-if="node.type === 'end'">◼</span>
          <span v-else-if="node.type === 'decision'">?</span>
          <span v-else>⚙</span>
        </div>
        <div class="node-title">{{ node.title }}</div>
        <button class="node-delete" @click.stop="$emit('delete', node.id)">×</button>
      </div>
      
      <div class="node-content">
        <div v-if="node.description" class="node-description">
          {{ node.description }}
        </div>
        <div class="node-info">
          <div v-if="node.responsible" class="info-item">
            <small>Ответственный:</small>
            <span>{{ node.responsible }}</span>
          </div>
          <div v-if="node.duration" class="info-item">
            <small>Срок:</small>
            <span>{{ node.duration }} дн.</span>
          </div>
        </div>
      </div>
      
      <div class="node-ports">
        <div class="port port-in" @mousedown.stop="startConnection"></div>
        <div class="port port-out" @mousedown.stop="startConnection"></div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue'
  
  const props = defineProps({
    node: {
      type: Object,
      required: true
    },
    isSelected: {
      type: Boolean,
      default: false
    }
  })
  
  const emit = defineEmits([
    'select',
    'update:position',
    'update:data',
    'delete'
  ])
  
  const isDragging = ref(false)
  const dragStartX = ref(0)
  const dragStartY = ref(0)
  
  const select = (e) => {
    const isMulti = e.ctrlKey || e.metaKey
    emit('select', props.node.id, isMulti)
  }
  
  const edit = () => {
    // Двойной клик для редактирования
    const newTitle = prompt('Введите новое название:', props.node.title)
    if (newTitle !== null) {
      emit('update:data', props.node.id, { title: newTitle })
    }
  }
  
  const startDrag = (e) => {
    if (e.button !== 0) return // Только левая кнопка мыши
    
    isDragging.value = true
    dragStartX.value = e.clientX - props.node.x
    dragStartY.value = e.clientY - props.node.y
    
    const onMouseMove = (e) => {
      if (!isDragging.value) return
      const newX = e.clientX - dragStartX.value
      const newY = e.clientY - dragStartY.value
      emit('update:position', props.node.id, newX, newY)
    }
    
    const onMouseUp = () => {
      isDragging.value = false
      document.removeEventListener('mousemove', onMouseMove)
      document.removeEventListener('mouseup', onMouseUp)
    }
    
    document.addEventListener('mousemove', onMouseMove)
    document.addEventListener('mouseup', onMouseUp)
    
    e.preventDefault()
  }
  
  const startConnection = (e) => {
    // Начало создания соединения
    e.stopPropagation()
    select(e)
  }
  </script>
  
  <style scoped>
  .flowchart-node {
    position: absolute;
    max-width: 300px;
    min-height: 60px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    cursor: move;
    transition: all 0.3s;
    user-select: none;
  }
  
  .flowchart-node:hover {
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    transform: translateY(-1px);
  }
  
  .flowchart-node.selected {
    box-shadow: 0 0 0 2px #2196f3, 0 4px 8px rgba(0,0,0,0.2);
    z-index: 100;
  }
  
  /* Стили для разных типов узлов */
  .flowchart-node.start {
    border-left: 4px solid #4caf50;
  }
  
  .flowchart-node.end {
    border-left: 4px solid #f44336;
  }
  
  .flowchart-node.process {
    border-left: 4px solid #2196f3;
  }
  
  .flowchart-node.decision {
    border-left: 4px solid #ff9800;
    background: linear-gradient(135deg, #fff8e1 0%, #ffffff 100%);
  }
  
  .node-header {
    display: flex;
    align-items: center;
    padding: 8px 10px;
    background: #f8f9fa;
    border-bottom: 1px solid #eee;
    border-radius: 8px 8px 0 0;
  }
  
  .node-icon {
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 8px;
    font-size: 12px;
  }
  
  .node-title {
    flex: 1;
    font-weight: 600;
    font-size: 12px;
    color: #333;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  
  .node-delete {
    width: 18px;
    height: 18px;
    border: none;
    background: #ff5252;
    color: white;
    border-radius: 50%;
    cursor: pointer;
    font-size: 12px;
    line-height: 1;
    opacity: 0;
    transition: opacity 0.3s;
  }
  
  .flowchart-node:hover .node-delete {
    opacity: 1;
  }
  
  .node-delete:hover {
    background: #ff1744;
  }
  
  .node-content {
    padding: 10px;
  }
  
  .node-description {
    font-size: 11px;
    color: #666;
    margin-bottom: 8px;
    line-height: 1.3;
  }
  
  .node-info {
    font-size: 10px;
    color: #888;
  }
  
  .info-item {
    display: flex;
    justify-content: space-between;
    margin-bottom: 2px;
  }
  
  .node-ports {
    position: absolute;
    top: 50%;
    left: 0;
    right: 0;
    transform: translateY(-50%);
    display: flex;
    justify-content: space-between;
    pointer-events: none;
  }
  
  .port {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: #2196f3;
    border: 2px solid white;
    box-shadow: 0 0 0 1px #2196f3;
    pointer-events: all;
    cursor: crosshair;
  }
  
  .port-in {
    transform: translateX(-50%);
  }
  
  .port-out {
    transform: translateX(50%);
  }
  </style>