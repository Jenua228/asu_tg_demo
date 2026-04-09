<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import FlowchartNode from './FlowchartNode.vue'

// Инициализация данных
const nodes = ref([
{ id: '1', type: 'start', title: 'Ремонтный завод', x: 50, y: 340 },
          { id: '2', type: 'process', title: 'Cтационарный комплект ремонтно-технического оборудования «РЕДИКОМ»', x: 300, y: 50 },
          { id: '3', type: 'process', title: 'Технический центр ремонта (ТЦР) гидравлических систем ЗРК «Бук-М2Э»', x: 300, y: 120 },
          { id: '4', type: 'process', title: 'ТЦР дизельных двигателей', x: 300, y: 200 },
          { id: '5', type: 'process', title: 'ТЦР ремонта 9И56, 9И56-8, 9И112М2, 9И113М2, 9И114М2', x: 300, y: 270 },
          { id: '6', type: 'process', title: 'ТЦР ремонта модуля разведки и управления 9С932-1 и ЗСУ-23-4М4 «Шилка-М4»', x: 300, y: 340 },
          { id: '7', type: 'process', title: 'ТЦР ремонта шасси ЗРС «Тор-М1», ЗРК «Тор-М2Э»,ЗРК «Бук-М2Э», ЗРС «Антей-2500», «МРУ-Б»', x: 300, y: 410 },
          { id: '8', type: 'process', title: 'ТЦР ремонта ЗРС «Тор-М1», ЗРК «Тор-М2Э»', x: 300, y: 480 },
          { id: '9', type: 'process', title: 'ТЦР ремонта изделий 9М334', x: 300, y: 550 },
          { id: '10', type: 'process', title: 'ТЦР ремонта изделий 9М82МДЭ, 9М83МЭ, 9М317', x: 300, y: 620 }
])

const connections = ref([
{ id: 'c1', from: '1', to: '2', condition: '' },
        { id: 'c2', from: '1', to: '3', condition: '' },
        { id: 'c3', from: '1', to: '4', condition: 'Да' },
        { id: 'c4', from: '1', to: '5', condition: 'Нет' },
        { id: 'c5', from: '1', to: '6', condition: '' },
        { id: 'c6', from: '1', to: '7', condition: 'После получения' },
        { id: 'c7', from: '1', to: '8', condition: 'Нет' },
        { id: 'c8', from: '1', to: '9', condition: '' },
        { id: 'c9', from: '1', to: '10', condition: 'После получения' },
])

// Выбранные элементы
const selectedNode = ref(null)
const selectedConnection = ref(null)
const selectedNodes = ref([])

// Данные для редактирования
const selectedNodeData = reactive({})
const selectedConnectionData = reactive({})

// Вычисляемые свойства
const flowchart = ref(null)

// Методы для работы с узлами
const addNode = (type) => {
  const newNode = {
    id: `node_${Date.now()}`,
    type,
    title: getDefaultTitle(type),
    description: '',
    x: 200,
    y: 200,
    responsible: '',
    duration: 1
  }
  nodes.value.push(newNode)
}

const getDefaultTitle = (type) => {
  const titles = {
    start: 'Начало процесса',
    process: 'Новый процесс',
    decision: 'Решение',
    end: 'Конец процесса'
  }
  return titles[type] || 'Новый узел'
}

const selectNode = (nodeId, isMulti = false) => {
  if (!isMulti) {
    selectedNodes.value = [nodeId]
    selectedNode.value = nodeId
    selectedConnection.value = null
    
    const node = nodes.value.find(n => n.id === nodeId)
    Object.assign(selectedNodeData, { ...node })
  } else {
    const index = selectedNodes.value.indexOf(nodeId)
    if (index === -1) {
      selectedNodes.value.push(nodeId)
    } else {
      selectedNodes.value.splice(index, 1)
    }
  }
}

const updateNodePosition = (nodeId, x, y) => {
  const node = nodes.value.find(n => n.id === nodeId)
  if (node) {
    node.x = x
    node.y = y
  }
}

const updateNodeData = (nodeId, data) => {
  const node = nodes.value.find(n => n.id === nodeId)
  if (node) {
    Object.assign(node, data)
  }
}

const deleteNode = (nodeId) => {
  nodes.value = nodes.value.filter(n => n.id !== nodeId)
  connections.value = connections.value.filter(
    conn => conn.from !== nodeId && conn.to !== nodeId
  )
  if (selectedNode.value === nodeId) {
    selectedNode.value = null
  }
}

// Методы для работы с соединениями
const addConnection = () => {
  if (selectedNodes.value.length === 2) {
    const newConnection = {
      id: `conn_${Date.now()}`,
      from: selectedNodes.value[0],
      to: selectedNodes.value[1],
      condition: ''
    }
    connections.value.push(newConnection)
    selectedNodes.value = []
  }
}

const selectConnection = (connId) => {
  selectedConnection.value = connId
  selectedNode.value = null
  
  const conn = connections.value.find(c => c.id === connId)
  if (conn) {
    Object.assign(selectedConnectionData, { ...conn })
  }
}

const updateSelectedConnection = () => {
  const conn = connections.value.find(c => c.id === selectedConnection.value)
  if (conn) {
    Object.assign(conn, { ...selectedConnectionData })
  }
}

const deleteSelected = () => {
  if (selectedNode.value) {
    deleteNode(selectedNode.value)
  } else if (selectedConnection.value) {
    connections.value = connections.value.filter(
      c => c.id !== selectedConnection.value
    )
    selectedConnection.value = null
  }
}

// Расчет пути для соединений
const calculatePath = (connection) => {
  const fromNode = nodes.value.find(n => n.id === connection.from)
  const toNode = nodes.value.find(n => n.id === connection.to)
  
  if (!fromNode || !toNode) return ''
  
  const startX = fromNode.x + 150
  const startY = fromNode.y + 50
  const endX = toNode.x
  const endY = toNode.y + 50
  
  const midX = (startX + endX) / 2
  
  return `M ${startX} ${startY} C ${midX} ${startY}, ${midX} ${endY}, ${endX} ${endY}`
}

// Обновление выбранного узла
const updateSelectedNode = () => {
  const node = nodes.value.find(n => n.id === selectedNode.value)
  if (node) {
    Object.assign(node, { ...selectedNodeData })
  }
}

const deselectAll = () => {
  selectedNode.value = null
  selectedConnection.value = null
  selectedNodes.value = []
}

// Сохранение/загрузка
const saveFlowchart = () => {
  const data = {
    nodes: nodes.value,
    connections: connections.value
  }
  localStorage.setItem('flowchart_data', JSON.stringify(data))
  alert('Блок-схема сохранена!')
}

const loadFlowchart = () => {
  const saved = localStorage.getItem('flowchart_data')
  if (saved) {
    const data = JSON.parse(saved)
    nodes.value = data.nodes
    connections.value = data.connections
    alert('Блок-схема загружена!')
  }
}

// Шаблоны
const loadTemplate = (templateName) => {
  const templates = {


    RZ: {
      nodes: [
        { id: '1', type: 'start', title: 'Ремонтный завод', x: 50, y: 340 },
          { id: '2', type: 'process', title: 'Cтационарный комплект ремонтно-технического оборудования «РЕДИКОМ»', x: 300, y: 50 },
          { id: '3', type: 'process', title: 'Технический центр ремонта (ТЦР) гидравлических систем ЗРК «Бук-М2Э»', x: 300, y: 120 },
          { id: '4', type: 'process', title: 'ТЦР дизельных двигателей', x: 300, y: 200 },
          { id: '5', type: 'process', title: 'ТЦР ремонта 9И56, 9И56-8, 9И112М2, 9И113М2, 9И114М2', x: 300, y: 270 },
          { id: '6', type: 'process', title: 'ТЦР ремонта модуля разведки и управления 9С932-1 и ЗСУ-23-4М4 «Шилка-М4»', x: 300, y: 340 },
          { id: '7', type: 'process', title: 'ТЦР ремонта шасси ЗРС «Тор-М1», ЗРК «Тор-М2Э»,ЗРК «Бук-М2Э», ЗРС «Антей-2500», «МРУ-Б»', x: 300, y: 410 },
          { id: '8', type: 'process', title: 'ТЦР ремонта ЗРС «Тор-М1», ЗРК «Тор-М2Э»', x: 300, y: 480 },
          { id: '9', type: 'process', title: 'ТЦР ремонта изделий 9М334', x: 300, y: 550 },
          { id: '10', type: 'process', title: 'ТЦР ремонта изделий 9М82МДЭ, 9М83МЭ, 9М317', x: 300, y: 620 }
      ],
      connections: [
        { id: 'c1', from: '1', to: '2', condition: '' },
        { id: 'c2', from: '1', to: '3', condition: '' },
        { id: 'c3', from: '1', to: '4', condition: 'Да' },
        { id: 'c4', from: '1', to: '5', condition: 'Нет' },
        { id: 'c5', from: '1', to: '6', condition: '' },
        { id: 'c6', from: '1', to: '7', condition: 'После получения' },
        { id: 'c7', from: '1', to: '8', condition: 'Нет' },
        { id: 'c8', from: '1', to: '9', condition: '' },
        { id: 'c9', from: '1', to: '10', condition: 'После получения' },
      ]
    },

    redikom: {
      nodes: [
      { id: '1', type: 'start', title: 'КРДО "Редиком"', x: 10, y: 420, description: 'ШИБФ.468927.107 - 1шт.'},
    { id: '2', type: 'process', title: 'Участок ремонта цифроаналоговых, аналоговых и высокочастотных сменных элементов РЭА', x: 210, y: 120, description: 'ШИБФ.468224.054 - 1 этап 1шт.' },
      { id: '3', type: 'process', title: 'АРМ контроля и диагностики цифровых, аналоговых и высокочастотных СЭ РЭА АРМ2-1', x: 550, y: 20, description: 'ШИБФ.468229.126 - 1 этап - 1шт.'},
        { id: '17', type: 'process', title: 'СКДА-2: система контроля и диагностики автоматизированная ', x: 950, y: 20, description: 'ШИБФ.468229.122 - 1 этап - 1шт.'},
      { id: '4', type: 'process', title: 'СКДА-1: система контроля и диагностики автоматизированная', x: 550, y: 120, description: 'ШИБФ.468229.121 - 1 этап - 1шт.'},
      { id: '5', type: 'process', title: 'Комплект технологического оборудования и инструмента', x: 550, y: 220, description: 'ШИБФ.442614.031 - 1 этап - 1шт.'},
    { id: '6', type: 'process', title: 'Участок ремонта цифровых сменных элементов РЭА', x: 210, y: 420,  description:'ШИБФ.468224.053 -ам 1 этап '},
      { id: '7', type: 'process', title: 'Автоматизированное рабочее место контроля и диагностики цифровых СЭ РЭА АРМ1-1', x: 550, y: 320,  description:'ШИБФ.468229.125 - 1 этап - 1 шт.'},
        { id: '8', type: 'process', title: 'Комплект технологического оборудования и инструмента', x: 950, y: 120,  description:'ШИБФ.442614.028 - 1 этап - 1 шт.'},
        { id: '9', type: 'process', title: 'Комплект вспомогательного инвентаря', x: 950, y: 220,  description:'ШИБФ.442614.041 - 1 этап - 1 шт.'},
        { id: '10', type: 'process', title: 'СКДА-2: система контроля и диагностики автоматизированная ', x: 950, y: 320,  description:'ШИБФ.468229.122 - 1 этап - 1 шт.'},
        { id: '11', type: 'process', title: 'Шкаф', x: 950, y: 420,  description:'ШИБФ.301444.018 - 1 этап - 4 шт.'},
        { id: '12', type: 'process', title: 'Стол универсальный', x: 950, y: 520,  description:'ШИБФ.301313.071 - 1 этап - 1 шт.'},
      { id: '13', type: 'process', title: 'Рабочее место проведения радиомонтажных работ РМ1-1', x: 550, y: 420,  description:'ШИБФ.468924.074 - 1 этап - 1 шт.'},
      { id: '14', type: 'process', title: 'Рабочее место проведения слесарно-механических работ РМ1-2', x: 550, y: 520,  description:'ШИБФ.468924.075 - 1 этап - 1 шт.'},
    { id: '15', type: 'process', title: 'Участок ремонта СВЧ аппаратуры', x: 210, y: 620, description:'ШИБФ.468224.055 - 1 этап - 1 шт.'},
      { id: '18', type: 'process', title: 'Автоматизированное рабочее место контроля и диагностики СВЧ аппаратуры АРМ3-1', x: 550, y: 620, description:'ШИБФ.468229.127 - 1 этап - 1 шт.'},
      { id: '19', type: 'process', title: 'Рабочее место для ремонта высокочастотного оборудования РМ3-1', x: 550, y: 720, description:'ШИБФ.468924.078 - 1 этап - 1 шт.'},
        { id: '20', type: 'process', title: 'Комплект технологического оборудования и инструмента', x: 950, y: 620, description:'ШИБФ.442614.035 - 1 этап - 1 шт.'},
        { id: '21', type: 'process', title: 'Комплект вспомогательного инвентаря', x: 950, y: 720, description:'ШИБФ.442614.041 - 1 этап - 1 шт.'},
    { id: '16', type: 'process', title: 'Участок ремонта источников вторичного питания РЭА', x: 210, y: 720 , description:'ШИБФ.468224.056 - 1 этап - 1 шт.'},
      ],
      connections: [
      { id: '', from: '1', to: '2', condition: '' },
  { id: '', from: '1', to: '6', condition: '' },
  // { id: '', from: '1', to: '13', condition: '' },
  // { id: '', from: '1', to: '14', condition: '' },
  { id: '', from: '1', to: '15', condition: '' },
  { id: '', from: '1', to: '16', condition: '' },

  { id: '', from: '2', to: '3', condition: '' },
  { id: '', from: '2', to: '4', condition: '' },
  { id: '', from: '2', to: '5', condition: '' },

  { id: '', from: '3', to: '17', condition: '' },

  
  { id: '', from: '6', to: '7', condition: '' },
  { id: '', from: '6', to: '13', condition: '' },
  { id: '', from: '6', to: '14', condition: '' },

  { id: '', from: '7', to: '8', condition: '' },
  { id: '', from: '7', to: '9', condition: '' },
  { id: '', from: '7', to: '10', condition: '' },
  { id: '', from: '7', to: '11', condition: '' },
  { id: '', from: '7', to: '12', condition: '' },

  { id: '', from: '15', to: '18', condition: '' },
  { id: '', from: '15', to: '19', condition: '' },

  { id: '', from: '19', to: '20', condition: '' },
  { id: '', from: '19', to: '21', condition: '' },
      ]
    },

    byk: {
      nodes: [
      { id: '1', type: 'start', title: 'ТЦР ремонта гидравлических систем ЗРК «Бук-М2Э»', x: 30, y: 190 },
        { id: '2', type: 'process', title: 'Участок дефектации, разборки, сборки и настройки', x: 420, y: 50 },
        { id: '3', type: 'process', title: 'Участок сборки, испытаний гидравлических частей и цилиндров', x: 420, y: 120 },
        { id: '4', type: 'process', title: 'Участок ремонта, настройки гидроцилиндров и гидравлических замков', x: 420, y: 190 },
        { id: '5', type: 'process', title: 'Участок ремонта, изготовления трубопроводов и проверки на герметичность', x: 420, y: 260 },
        { id: '6', type: 'process', title: 'Слесарный участок', x: 420, y: 330 }
      ],
      connections: [
      { id: 'c1', from: '1', to: '2', condition: '' },
        { id: 'c2', from: '1', to: '3', condition: '' },
        { id: 'c3', from: '1', to: '4', condition: 'Да' },
        { id: 'c4', from: '1', to: '5', condition: 'Нет' },
        { id: 'c5', from: '1', to: '6', condition: '' },
        { id: 'c6', from: '1', to: '7', condition: 'После получения' },
        { id: 'c7', from: '1', to: '8', condition: 'Нет' },
        { id: 'c8', from: '1', to: '9', condition: '' },
        { id: 'c9', from: '1', to: '10', condition: 'После получения' },
      ]
    },


    TCR_9I56: {
      nodes: [
        { id: '1', type: 'start', title: 'ТЦР ремонта 9И56, 9И56-8, 9И112М2, 9И113М2, 9И114М2', x: 40, y: 365 },
          { id: '2', type: 'process', title: 'Участок приема в ремонт', x: 460, y: 50 },
          { id: '3', type: 'process', title: 'Участок дефектации', x: 460, y: 120 },
          { id: '4', type: 'process', title: 'Участок разборки', x: 460, y: 190 },
          { id: '5', type: 'process', title: 'Участок входного контроля подшипниковой заготовки', x: 460, y: 260 },
          { id: '6', type: 'process', title: 'Слесарный участок', x: 460, y: 330 },
          { id: '7', type: 'process', title: 'Участок механической обработки', x: 460, y: 400 },
          { id: '8', type: 'process', title: 'Участок балансировки', x: 460, y: 470 },
          { id: '9', type: 'process', title: 'Участок съёма металла при балансировке', x: 460, y: 540 },
          { id: '10', type: 'process', title: 'Участок доводки и притирки', x: 460, y: 610 },
          { id: '11', type: 'process', title: 'Участок сварки и пайки', x: 460, y: 690 },
      ],
      connections: [
      { id: 'c1', from: '1', to: '2', condition: '' },
        { id: 'c2', from: '1', to: '3', condition: '' },
        { id: 'c3', from: '1', to: '4', condition: 'Да' },
        { id: 'c4', from: '1', to: '5', condition: 'Нет' },
        { id: 'c5', from: '1', to: '6', condition: '' },
        { id: 'c6', from: '1', to: '7', condition: 'После получения' },
        { id: 'c7', from: '1', to: '8', condition: 'Нет' },
        { id: 'c8', from: '1', to: '9', condition: '' },
        { id: 'c9', from: '1', to: '10', condition: 'После получения' },
        { id: 'c10', from: '1', to: '11', condition: 'После получения' },
      ]
    },

    dizel: {
      nodes: [
      { id: '1', type: 'start', title: 'ТЦР дизельных двигателей', x: 40, y: 365 },
        { id: '2', type: 'process', title: 'Пост приема в ремонт', x: 460, y: 50 },
        { id: '3', type: 'process', title: 'Пост дефектации двигателя', x: 460, y: 120 },
        { id: '4', type: 'process', title: 'Пост разборки двигателя', x: 460, y: 190 },
        { id: '5', type: 'process', title: 'Пост ремонта навесного оборудования', x: 460, y: 260 },
        { id: '6', type: 'process', title: 'Пост ремонта электрооборудования', x: 460, y: 330 },
        { id: '7', type: 'process', title: 'Пост ремонта топливной аппаратуры', x: 460, y: 400 },
        { id: '8', type: 'process', title: 'Пост устранения дефектов', x: 460, y: 470 },
        { id: '9', type: 'process', title: 'Участок подкрашивания ДВС', x: 460, y: 540 },
        { id: '10', type: 'process', title: 'Участок ремонта шатуно-поршневой группы', x: 460, y: 610 },
        { id: '11', type: 'process', title: 'Участок ремонта клапанов', x: 460, y: 690 },
      ],
      connections: [
      { id: 'c1', from: '1', to: '2', condition: '' },
        { id: 'c2', from: '1', to: '3', condition: '' },
        { id: 'c3', from: '1', to: '4', condition: 'Да' },
        { id: 'c4', from: '1', to: '5', condition: 'Нет' },
        { id: 'c5', from: '1', to: '6', condition: '' },
        { id: 'c6', from: '1', to: '7', condition: 'После получения' },
        { id: 'c7', from: '1', to: '8', condition: 'Нет' },
        { id: 'c8', from: '1', to: '9', condition: '' },
        { id: 'c9', from: '1', to: '10', condition: 'После получения' },
        { id: 'c10', from: '1', to: '11', condition: 'После получения' },
      ]
    },

    TCR_scout: {
      nodes: [
      { id: '1', type: 'start', title: 'ТЦР ремонта модуля разведки и управления 9С932-1 и ЗСУ-23-4М4 «Шилка-М4»', x: 40, y: 260 },
        { id: '2', type: 'process', title: 'Участок диагностики изделия', x: 400, y: 50 },
        { id: '3', type: 'process', title: 'Площадка для размещения подвижного оборудования', x: 400, y: 120 },
        { id: '4', type: 'process', title: 'Участок ремонта изделия', x: 400, y: 190 },
        { id: '5', type: 'process', title: 'Слесарно-сборочный участок', x: 400, y: 260 },
        { id: '6', type: 'process', title: 'Электромонтажный участок (2 участка)', x: 400, y: 330 },
        { id: '7', type: 'process', title: 'Слесарный участок', x: 400, y: 400 },
        { id: '8', type: 'process', title: 'Инженерный участок', x: 400, y: 470 }
      ],
      connections: [
      { id: 'c1', from: '1', to: '2', condition: '' },
        { id: 'c2', from: '1', to: '3', condition: '' },
        { id: 'c3', from: '1', to: '4', condition: 'Да' },
        { id: 'c4', from: '1', to: '5', condition: 'Нет' },
        { id: 'c5', from: '1', to: '6', condition: '' },
        { id: 'c6', from: '1', to: '7', condition: 'После получения' },
        { id: 'c7', from: '1', to: '8', condition: 'Нет' }
      ]
    },

    TCR_shassis: {
      nodes: [
      { id: '1', type: 'start', title: 'ТЦР ремонта шасси ЗРК «Тор-М1», ЗРК «Тор-М2Э», ЗРК «Бук-М2Э»', x: 40, y: 365 },
        { id: '2', type: 'process', title: 'Участок дефектации, разборки-сборки и испытаний ГМ, Мт-Лбу (5 зон и площадок)', x: 500, y: 50 },
        { id: '3', type: 'process', title: 'Участок дефектации, разборки-сборки и испытаний СГШ', x: 500, y: 120 },
        { id: '4', type: 'process', title: 'Участок обслуживания АКБ', x: 500, y: 190 },
        { id: '5', type: 'process', title: 'Участок ремонта узлов СГШ', x: 500, y: 260 },
        { id: '6', type: 'process', title: 'Участок заправки баллов ППО', x: 500, y: 330 },
        { id: '7', type: 'process', title: 'Слесарно-сборочный участок', x: 500, y: 400 },
        { id: '8', type: 'process', title: 'Участок ремонта узлов шасси МТ-Лбу', x: 500, y: 470 },
        { id: '9', type: 'process', title: 'Сварочный участок', x: 500, y: 540 },
        { id: '10', type: 'process', title: 'Участок сдачи готовой продукции', x: 500, y: 610 },
        { id: '11', type: 'process', title: 'Зоны хранения крупногабаритного ЗИП', x: 500, y: 690 },
      ],
      connections: [
      { id: 'c1', from: '1', to: '2', condition: '' },
        { id: 'c2', from: '1', to: '3', condition: '' },
        { id: 'c3', from: '1', to: '4', condition: 'Да' },
        { id: 'c4', from: '1', to: '5', condition: 'Нет' },
        { id: 'c5', from: '1', to: '6', condition: '' },
        { id: 'c6', from: '1', to: '7', condition: 'После получения' },
        { id: 'c7', from: '1', to: '8', condition: 'Нет' },
        { id: 'c8', from: '1', to: '9', condition: '' },
        { id: 'c9', from: '1', to: '10', condition: 'После получения' },
        { id: 'c10', from: '1', to: '11', condition: 'После получения' },
      ]
    },

    TCR_zrk_tor: {
      nodes: [
      { id: '1', type: 'start', title: 'ТЦР ремонта ЗРК «Тор-М2Э»', x: 40, y: 435 },
        { id: '2', type: 'process', title: 'Участок сборки-разборки изделий', x: 350, y: 50 },
        { id: '3', type: 'process', title: 'Участок диагностики и ремонта антенного поста', x: 350, y: 120 },
        { id: '4', type: 'process', title: 'Участок диагностики и ремонта электронных и электромеханических блоков', x: 350, y: 190 },
        { id: '5', type: 'process', title: 'Участок диагностики и ремонта цифровых, высокочастотных и аналоговых панелей', x: 350, y: 260 },
        { id: '6', type: 'process', title: 'Электромонтажный участок для ремонта блоков и жгутов', x: 350, y: 330 },
        { id: '7', type: 'process', title: 'Химическая лаборатория', x: 350, y: 400 },
        { id: '8', type: 'process', title: 'Камера окраски (агрегатное помещение)', x: 350, y: 470 },
        { id: '9', type: 'process', title: 'Камера дождевания (агрегатное помещение)', x: 350, y: 540 },
        { id: '10', type: 'process', title: 'Отделение подкраски корпусов, блоков, панелей', x: 350, y: 610 },
        { id: '11', type: 'process', title: 'Склад ЛВЖ', x: 350, y: 690 },
        { id: '12', type: 'process', title: 'Склад химических материалов', x: 350, y: 760 },
        { id: '13', type: 'process', title: 'Кладовая инструментов и приспособлений', x: 350, y: 830 },
        { id: '14', type: 'process', title: 'Кладовая средств измерений', x: 700, y: 830 },
      ],
      connections: [
      { id: 'c1', from: '1', to: '2', condition: '' },
        { id: 'c2', from: '1', to: '3', condition: '' },
        { id: 'c3', from: '1', to: '4', condition: 'Да' },
        { id: 'c4', from: '1', to: '5', condition: 'Нет' },
        { id: 'c5', from: '1', to: '6', condition: '' },
        { id: 'c6', from: '1', to: '7', condition: 'После получения' },
        { id: 'c7', from: '1', to: '8', condition: 'Нет' },
        { id: 'c8', from: '1', to: '9', condition: '' },
        { id: 'c9', from: '1', to: '10', condition: 'После получения' },
        { id: 'c10', from: '1', to: '11', condition: 'После получения' },
        { id: 'c11', from: '1', to: '12', condition: '' },
        { id: 'c12', from: '1', to: '13', condition: 'После получения' },
        { id: 'c13', from: '1', to: '14', condition: 'После получения' },
      ]
    },

    TCR_9M334: {
      nodes: [
      { id: '1', type: 'start', title: 'ТЦР ремонта изделий 9М334', x: 40, y: 120 },
        { id: '2', type: 'process', title: 'Пультовая автоматизированной контрольно-испытательной станции (АКИС)', x: 350, y: 50 },
        { id: '3', type: 'process', title: 'Помещение для хранения ЗИП', x: 350, y: 120 },
        { id: '4', type: 'process', title: 'Административные помещения (3 помещения)', x: 350, y: 190 },
      ],
      connections: [
      { id: 'c1', from: '1', to: '2', condition: '' },
        { id: 'c2', from: '1', to: '3', condition: '' },
        { id: 'c3', from: '1', to: '4', condition: 'Да' },
      ]
    },

    TCR_9M82: {
      nodes: [
      { id: '1', type: 'start', title: 'ТЦР ремонта изделий 9М82МДЭ, 9М83МЭ, 9М317', x: 40, y: 365 },
        { id: '2', type: 'process', title: 'Участок дефектации, разборки, сборки и контроля изделий', x: 420, y: 50 },
        { id: '3', type: 'process', title: 'Участок мелкой сборки (в том числе снаряжения/расснаряжения изделий)', x: 420, y: 120 },
        { id: '4', type: 'process', title: 'Участок упаковки изделий и составных частей', x: 420, y: 190 },
        { id: '5', type: 'process', title: 'Участок выполнения ремонтных работ', x: 420, y: 260 },
        { id: '6', type: 'process', title: 'Участок проверки бортовой аппаратуры до и после ремонта', x: 420, y: 330 },
        { id: '7', type: 'process', title: 'Участок испытания на герметичность', x: 420, y: 400 },
        { id: '8', type: 'process', title: 'Участок входного контроля, дефектации и проверки', x: 420, y: 470 },
        { id: '9', type: 'process', title: 'Участок технической документации', x: 420, y: 540 },
        { id: '10', type: 'process', title: 'Склад инструмента и приспособлений', x: 420, y: 610 },
        { id: '11', type: 'process', title: 'Участок хранения оснастки, инструмента и приспособлений', x: 420, y: 690 }
      ],
      connections: [
      { id: 'c1', from: '1', to: '2', condition: '' },
        { id: 'c2', from: '1', to: '3', condition: '' },
        { id: 'c3', from: '1', to: '4', condition: 'Да' },
        { id: 'c4', from: '1', to: '5', condition: 'Нет' },
        { id: 'c5', from: '1', to: '6', condition: '' },
        { id: 'c6', from: '1', to: '7', condition: 'После получения' },
        { id: 'c7', from: '1', to: '8', condition: 'Нет' },
        { id: 'c8', from: '1', to: '9', condition: '' },
        { id: 'c9', from: '1', to: '10', condition: 'После получения' },
        { id: 'c10', from: '1', to: '11', condition: 'После получения' }
      ]
    },
  }
  
  if (templates[templateName]) {
    nodes.value = templates[templateName].nodes
    connections.value = templates[templateName].connections
    deselectAll()
  }
}

onMounted(() => {
  // Загрузка сохраненных данных при монтировании
  const saved = localStorage.getItem('flowchart_data')
  if (saved) {
    try {
      const data = JSON.parse(saved)
      nodes.value = data.nodes || nodes.value
      connections.value = data.connections || connections.value
    } catch (e) {
      console.error('Ошибка загрузки данных:', e)
    }
  }
})
</script>

<template>
  <div class="flowchart-container">
    <div class="toolbar">
      <button @click="addNode('process')" class="tool-btn">
        <span>+ {{ $t('flowchart.process') }}</span>
      </button>
      <button @click="addNode('decision')" class="tool-btn">
        <span>+ {{ $t('flowchart.decision') }}</span>
      </button>
      <button @click="addNode('start')" class="tool-btn">
        <span>+ {{ $t('flowchart.start') }}</span>
      </button>
      <button @click="addNode('end')" class="tool-btn">
        <span>+ {{ $t('flowchart.end') }}</span>
      </button>
      <button @click="addConnection" class="tool-btn" :disabled="selectedNodes.length !== 2">
        <span>{{ $t('flowchart.connect') }}</span>
      </button>
      <button @click="deleteSelected" class="tool-btn delete-btn" :disabled="!selectedNode">
        <span>{{ $t('flowchart.delete') }}</span>
      </button>
      <button @click="saveFlowchart" class="tool-btn save-btn">
        <span>{{ $t('flowchart.save') }}</span>
      </button>
      <button @click="loadFlowchart" class="tool-btn load-btn">
        <span>{{ $t('flowchart.load') }}</span>
      </button>
    </div>

    <div class="flowchart" ref="flowchart" @click="deselectAll">
      <!-- Соединения -->
      <svg class="connections-layer">
        <path
          v-for="conn in connections"
          :key="conn.id"
          :d="calculatePath(conn)"
          class="connection"
          :class="{ selected: selectedConnection === conn.id }"
          @click.stop="selectConnection(conn.id)"
        />
      </svg>

      <!-- Узлы -->
      <FlowchartNode
        v-for="node in nodes"
        :key="node.id"
        :node="node"
        :isSelected="selectedNode === node.id"
        @select="selectNode"
        @update:position="updateNodePosition"
        @update:data="updateNodeData"
        @delete="deleteNode"
      />
    </div>

    <!-- Панель редактирования -->
    <div class="edit-panel" v-if="selectedNode || selectedConnection">
      <h3>{{ $t('block.editAction') }}</h3>
      
      <div v-if="selectedNode">
        <div class="form-group">
          <label>{{ $t('flowchart.title') }}:</label>
          <input 
            type="text" 
            v-model="selectedNodeData.title"
            @input="updateSelectedNode"
          />
        </div>
        
        <div class="form-group">
          <label>{{ $t('taskModal.description') }}:</label>
          <textarea 
            v-model="selectedNodeData.description"
            @input="updateSelectedNode"
            rows="3"
          />
        </div>
        
        <div class="form-group">
          <label>{{ $t('connectionPopup.type') }}</label>
          <select v-model="selectedNodeData.type" @change="updateSelectedNode">
            <option value="start">{{ $t('flowchart.start') }}</option>
            <option value="process">{{ $t('flowchart.process') }}</option>
            <option value="decision">{{ $t('flowchart.decision') }}</option>
            <option value="end">{{ $t('flowchart.end') }}</option>
          </select>
        </div>
        
        <div class="form-group">
          <label>{{ $t('flowchart.responsible') }}</label>
          <input 
            type="text" 
            v-model="selectedNodeData.responsible"
            @input="updateSelectedNode"
          />
        </div>
        
        <div class="form-group">
          <label>{{ $t('flowchart.deadline') }}</label>
          <input 
            type="number" 
            v-model="selectedNodeData.duration"
            @input="updateSelectedNode"
            min="0"
          />
        </div>
      </div>
      
      <div v-if="selectedConnection" class="connection-edit">
        <div class="form-group">
          <label>{{ $t('flowchart.transferCondition') }}</label>
          <input 
            type="text" 
            v-model="selectedConnectionData.condition"
            @input="updateSelectedConnection"
          />
        </div>
      </div>
    </div>

    <!-- Предустановленные шаблоны -->
    <div class="templates">
      <h4>{{ $t('flowchart.templates') }}</h4>
      <div class="template-buttons">
        <button @click="loadTemplate('RZ')" class="template-btn">
          РЗ
        </button>
        <button @click="loadTemplate('redikom')" class="template-btn">
          КРДО «РЕДИКОМ»:
        </button>
        <button @click="loadTemplate('byk')" class="template-btn">
          ТЦР ремонта гидравлических систем ЗРК «Бук-М2Э»;
        </button>
        <button @click="loadTemplate('TCR_9I56')" class="template-btn">
          ТЦР ремонта 9И56, 9И56-8
        </button>
        <button @click="loadTemplate('dizel')" class="template-btn">
          ТЦР дизельных двигателей
        </button>
        <button @click="loadTemplate('TCR_scout')" class="template-btn">
          ТЦР ремонта модуля разведки «Шилка-М4»
        </button>
        <button @click="loadTemplate('TCR_shassis')" class="template-btn">
          ТЦР ремонта шасси
        </button>
        <button @click="loadTemplate('TCR_zrk_tor')" class="template-btn">
          ТЦР ремонта ЗРК «Тор-М2Э»
        </button>
        <button @click="loadTemplate('TCR_9M334')" class="template-btn">
          ТЦР ремонта изделий 9М334
        </button>
        <button @click="loadTemplate('TCR_9M82')" class="template-btn">
          ТЦР ремонта изделий 9М82МДЭ, 9М83МЭ, 9М317
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.flowchart-container {
  display: flex;
  flex-direction: column;
  widows: 1000px;
  height: 1100px;
  background: #f5f7fa;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.toolbar {
  display: flex;
  gap: 10px;
  padding: 15px;
  background: white;
  border-bottom: 1px solid #e0e0e0;
  flex-wrap: wrap;
}

.tool-btn {
  padding: 8px 16px;
  background: #4a76a8;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 14px;
}

.tool-btn:hover:not(:disabled) {
  background: #3a6690;
  transform: translateY(-1px);
}

.tool-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.delete-btn {
  background: #e53935;
}

.save-btn {
  background: #43a047;
}

.load-btn {
  background: #fb8c00;
}

.flowchart {
  /* flex: 1; */
  position: relative;
  overflow: auto;
  height: 95%;
  width: 98%;
  background: 
    linear-gradient(90deg, #f0f0f0 1px, transparent 1px),
    linear-gradient(#f0f0f0 1px, transparent 1px);
  background-size: 20px 20px;
}

.connections-layer {
  position: relative;
  overflow: auto;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.connection {
  fill: none;
  stroke: #666;
  stroke-width: 2;
  pointer-events: stroke;
}

.connection.selected {
  stroke: #2196f3;
  stroke-width: 3;
}

.edit-panel {
  position: fixed;
  right: 20px;
  top: 100px;
  width: 300px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  padding: 20px;
  z-index: 1000;
}

.edit-panel h3 {
  margin-top: 0;
  color: #333;
  border-bottom: 2px solid #4a76a8;
  padding-bottom: 10px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  color: #555;
  font-weight: 500;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: #4a76a8;
}

.templates {
  padding: 15px;
  background: white;
  border-top: 1px solid #e0e0e0;
}

.templates h4 {
  margin-top: 0;
  margin-bottom: 10px;
  color: #333;
}

.template-buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.template-btn {
  padding: 6px 12px;
  background: #78909c;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  transition: background 0.3s;
}

.template-btn:hover {
  background: #607d8b;
}
</style>