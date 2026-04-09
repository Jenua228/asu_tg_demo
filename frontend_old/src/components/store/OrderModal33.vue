<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  modelValue: Boolean,
  inventory: Array,
  currentUser: {
    type: Object,
    default: () => ({
      name: 'Иванов Иван Иванович',
      position: 'Инженер',
      department: 'Ремонтный участок',
      phone: '8(123)-456 78 90',
      email: 'gptp-granit@company.ru'
    })
  }
})

const emit = defineEmits(['update:modelValue', 'submit'])

// Состояния
const isSuccess = ref(false)
const isPrintMode = ref(false)
const showPrintPreview = ref(false)

// Состояния для редактирования полей товаров
const editingItem = ref(null)
const editingField = ref('')

// Данные заявки
const order = ref({
  requestNumber: generateRequestNumber(),
  requestDate: new Date().toLocaleDateString('ru-RU'),
  
  requesterName: props.currentUser.name,
  requesterPosition: props.currentUser.position,
  requesterDepartment: props.currentUser.department,
  
  reason: '',
  items: []
})

// Типы запчастей
const partTypes = ref([
  { id: 'repair', label: 'ремонтные запчасти', checked: true },
  { id: 'spare', label: 'запасные части', checked: false },
  { id: 'consumables', label: 'расходные материалы', checked: false }
])

// Новый товар для добавления
const newItem = ref({
  product: '',
  quantity: 1,
  unit: 'шт'
})

// Генерация номера заявки
function generateRequestNumber() {
  const date = new Date()
  const year = date.getFullYear().toString().slice(-2)
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const random = Math.floor(Math.random() * 100).toString().padStart(2, '0')
  return `ЗНЧ-${day}${month}${year}-${random}`
}

// Функция для сохранения заявки в JSON файл
function saveOrderToJSON(orderData) {
  try {
    // Форматируем данные для сохранения
    const jsonData = {
      meta: {
        version: "1.0",
        generatedAt: new Date().toISOString(),
        documentType: "Заявка на запчасти"
      },
      order: {
        ...orderData,
        // Добавляем timestamp
        timestamp: new Date().toISOString(),
        // Добавляем дату в формате ISO
        requestDateISO: new Date().toISOString()
      }
    }

    // Конвертируем в JSON с красивым форматированием
    const jsonString = JSON.stringify(jsonData, null, 2)
    
    // Создаем Blob с JSON данными
    const blob = new Blob([jsonString], { type: 'application/json;charset=utf-8' })
    
    // Создаем URL для скачивания
    const url = URL.createObjectURL(blob)
    
    // Создаем ссылку для скачивания
    const a = document.createElement('a')
    a.href = url
    a.download = `Заявка_${orderData.requestNumber}_${new Date().toISOString().split('T')[0]}.json`
    
    // Добавляем ссылку на страницу и кликаем
    document.body.appendChild(a)
    a.click()
    
    // Очищаем
    setTimeout(() => {
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    }, 100)
    
    console.log('✅ Заявка сохранена в JSON файл:', orderData.requestNumber)
    return true
  } catch (error) {
    console.error('❌ Ошибка при сохранении JSON:', error)
    alert('Ошибка при сохранении файла. Проверьте консоль для подробностей.')
    return false
  }
}

// Новая функция для скачивания PDF
function downloadPDF() {
  try {
    // Создаем временное окно для генерации HTML
    const printWindow = window.open('', '_blank')
    if (!printWindow) {
      console.warn('Не удалось открыть окно для печати PDF')
      return false
    }
    
    // Записываем HTML в окно
    printWindow.document.write(generateDocumentHTML())
    printWindow.document.close()
    
    // Даем время на загрузку контента
    setTimeout(() => {
      // Инициируем печать для создания PDF
      printWindow.print()
      
      // Закрываем окно после небольшой задержки
      setTimeout(() => {
        printWindow.close()
      }, 1000)
    }, 500)
    
    console.log('✅ PDF заявка создана:', order.value.requestNumber)
    return true
  } catch (error) {
    console.error('❌ Ошибка при создании PDF:', error)
    return false
  }
}

// Добавление товара (существующая функция без изменений)
function addItem() {
  if (!newItem.value.product) {
    alert('Выберите товар из списка')
    return
  }

  let selectedProduct = null
  
  if (newItem.value.product) {
    selectedProduct = props.inventory.find(item => item.Article === newItem.value.product)
    
    if (!selectedProduct) {
      const index = parseInt(newItem.value.product)
      if (!isNaN(index) && index >= 0 && index < props.inventory.length) {
        selectedProduct = props.inventory[index]
      }
    }
  }
  
  if (!selectedProduct) {
    alert('Товар не найден в каталоге')
    return
  }
  
  let stock = 0;
  const possibleStockFields = ['stock', 'san_xactu', 'quantity', 'count', 'available', 'Stock', 'QTY', 'qty']
  
  for (const field of possibleStockFields) {
    if (selectedProduct[field] !== undefined && selectedProduct[field] !== null) {
      const value = Number(selectedProduct[field])
      if (!isNaN(value)) {
        stock = value
        break
      }
    }
  }

  const itemId = Date.now() + Math.random()
  const itemName = selectedProduct.num_rus || 
                   selectedProduct.name || 
                   selectedProduct.Name || 
                   selectedProduct.product_name || 
                   'Не указано'
  
  const article = selectedProduct.Article || 
                  selectedProduct.article || 
                  selectedProduct.code || 
                  `ТОВАР-${itemId.toString().slice(-6)}`
  
  order.value.items.push({
    id: itemId,
    article: article,
    name: itemName,
    model: selectedProduct.model || selectedProduct.modell || '',
    serial: selectedProduct.serial || selectedProduct.serial_number || '',
    manufacturer: selectedProduct.manufacturer || 
                  selectedProduct.isgotovitelb || 
                  selectedProduct.producer || 
                  selectedProduct.brand || '',
    quantity: newItem.value.quantity,
    unit: newItem.value.unit,
    stock: stock,
    originalProduct: selectedProduct
  })

  newItem.value = { 
    product: '', 
    quantity: 1, 
    unit: 'шт' 
  }
}

// Остальные существующие функции без изменений
function removeItem(id) {
  order.value.items = order.value.items.filter(item => item.id !== id)
}

function validateQuantity(item) {
  if (item.quantity < 1) {
    item.quantity = 1
  }
}

function getStock(product) {
  if (!product) return 0;
  
  const possibleFields = ['stock', 'san_xactu', 'quantity', 'count', 'available', 'Stock', 'QTY', 'qty'];
  
  for (const field of possibleFields) {
    if (product[field] !== undefined && product[field] !== null) {
      const value = Number(product[field]);
      if (!isNaN(value)) {
        return value;
      }
    }
  }
  
  return 0;
}

function startEditing(item, field) {
  editingItem.value = item.id
  editingField.value = field
}

function finishEditing() {
  editingItem.value = null
  editingField.value = ''
}

function handleKeydown(event, item) {
  if (event.key === 'Enter') {
    finishEditing()
  } else if (event.key === 'Escape') {
    editingItem.value = null
    editingField.value = ''
  }
}

function updatePartType(index) {
  partTypes.value[index].checked = !partTypes.value[index].checked
}

const activePartTypes = computed(() => {
  return partTypes.value
    .filter(type => type.checked)
    .map(type => type.label)
    .join(', ')
})

const hasSelectedPartTypes = computed(() => {
  return partTypes.value.some(type => type.checked)
})

const totalItems = computed(() => {
  return order.value.items.reduce((sum, item) => sum + item.quantity, 0)
})

// Валидация формы
function validateForm() {
  if (order.value.items.length === 0) {
    alert('Добавьте хотя бы один товар в заявку')
    return false
  }
  
  if (!order.value.reason.trim()) {
    alert('Укажите причину заказа')
    return false
  }
  
  if (!hasSelectedPartTypes.value) {
    alert('Выберите хотя бы один тип запчастей')
    return false
  }
  
  if (!order.value.requesterName.trim()) {
    alert('Введите ФИО заявителя')
    return false
  }
  
  if (!order.value.requesterPosition.trim()) {
    alert('Введите должность заявителя')
    return false
  }
  
  return true
}

// Отправка заявки (обновленная функция - теперь скачивает PDF сразу)
function submitOrder() {
  if (!validateForm()) return

  const orderData = {
    ...order.value,
    partTypes: activePartTypes.value,
    totalItems: totalItems.value,
    selectedPartTypes: partTypes.value.filter(t => t.checked),
    // Добавляем системную информацию
    systemInfo: {
      generatedAt: new Date().toISOString(),
      userAgent: navigator.userAgent,
      platform: navigator.platform
    }
  }

  console.log("📋 ЗАЯВКА НА ЗАПЧАСТИ:", orderData)

  // Сохраняем в JSON файл
  const isJsonSaved = saveOrderToJSON(orderData)
  
  // Скачиваем PDF (используем существующую функцию printDocument, но без показа окна)
  const isPdfGenerated = generatePDF()
  
  if (!isJsonSaved) {
    alert('Не удалось сохранить JSON файл. Пожалуйста, попробуйте снова.')
    return
  }
  
  if (!isPdfGenerated) {
    console.warn('PDF не был сгенерирован, но JSON сохранен')
  }

  // Эмит события для родительского компонента
  emit('submit', orderData)

  // Показ успеха
  isSuccess.value = true

  // Закрытие через 3 секунды (даем время на скачивание)
  setTimeout(() => {
    close()
    isSuccess.value = false
  }, 3000)
}

// Новая функция для генерации PDF с использованием html2pdf.js
function generatePDF() {
  try {
    // Импортируем html2pdf.js динамически
    import('html2pdf.js').then((html2pdf) => {
      // Создаем элемент для рендеринга HTML
      const element = document.createElement('div');
      element.style.position = 'fixed';
      element.style.top = '-9999px';
      element.style.left = '-9999px';
      element.innerHTML = generateDocumentHTML();
      document.body.appendChild(element);
      
      // Опции для генерации PDF
      const opt = {
        margin: [10, 10, 10, 10],
        filename: `Заявка_${order.value.requestNumber}.pdf`,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2, useCORS: true },
        jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
      };
      
      // Генерируем PDF
      html2pdf()
        .set(opt)
        .from(element)
        .save()
        .then(() => {
          // Удаляем временный элемент
          document.body.removeChild(element);
        })
        .catch(err => {
          console.error('❌ Ошибка при генерации PDF:', err);
          document.body.removeChild(element);
        });
    });
    
    return true;
  } catch (error) {
    console.error('❌ Ошибка при генерации PDF:', error);
    return false;
  }
}

// Альтернативный метод печати (если первый не сработал)
function printDocumentDirect() {
  try {
    // Создаем iframe для печати
    const iframe = document.createElement('iframe')
    iframe.style.position = 'fixed'
    iframe.style.right = '0'
    iframe.style.bottom = '0'
    iframe.style.width = '0'
    iframe.style.height = '0'
    iframe.style.border = 'none'
    document.body.appendChild(iframe)
    
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document
    iframeDoc.write(generateDocumentHTML())
    iframeDoc.close()
    
    setTimeout(() => {
      iframe.contentWindow.focus()
      iframe.contentWindow.print()
      
      // Удаляем iframe после печати
      setTimeout(() => {
        document.body.removeChild(iframe)
      }, 1000)
    }, 500)
    
    return true
  } catch (error) {
    console.error('❌ Ошибка при альтернативной печати:', error)
    return false
  }
}

// Существующая функция printDocument (оставляем для кнопки "Печать")
function printDocument() {
  const printWindow = window.open('', '_blank')
  if (!printWindow) {
    alert('Пожалуйста, разрешите всплывающие окна для печати')
    return false
  }
  
  printWindow.document.write(generateDocumentHTML())
  printWindow.document.close()
  
  // Даем время на загрузку контента
  setTimeout(() => {
    printWindow.print()
    // Не закрываем сразу, чтобы пользователь мог настроить параметры печати
  }, 500)
  
  return true
}

// Новая функция для сохранения в JSON без скачивания (может пригодиться)
function saveToLocalStorage() {
  try {
    const orders = JSON.parse(localStorage.getItem('savedOrders') || '[]')
    orders.push({
      ...order.value,
      partTypes: activePartTypes.value,
      savedAt: new Date().toISOString()
    })
    localStorage.setItem('savedOrders', JSON.stringify(orders))
    console.log('✅ Заявка сохранена в localStorage')
  } catch (error) {
    console.error('❌ Ошибка сохранения в localStorage:', error)
  }
}

// Новая функция для создания HTML документа (оставляем без изменений)
function generateDocumentHTML() {
  return `
    <!DOCTYPE html>
    <html lang="ru">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Заявка ${order.value.requestNumber}</title>
      <style>
        body {
          font-family: 'Times New Roman', Times, serif;
          font-size: 12pt;
          margin: 0;
          padding: 20mm;
          color: black;
        }
        .header {
          text-align: center;
          margin-bottom: 30px;
        }
        .header h1 {
          font-size: 16pt;
          font-weight: bold;
          margin-bottom: 10px;
          text-transform: uppercase;
        }
        .header-info {
          display: flex;
          justify-content: space-between;
          margin-top: 20px;
          border-top: 1px solid black;
          padding-top: 10px;
        }
        .info-block {
          width: 45%;
        }
        .section {
          margin-bottom: 25px;
        }
        .section-title {
          font-weight: bold;
          margin-bottom: 10px;
          border-bottom: 1px solid #ccc;
          padding-bottom: 5px;
        }
        table {
          width: 100%;
          border-collapse: collapse;
          margin: 10px 0;
        }
        th, td {
          border: 1px solid black;
          padding: 8px;
          text-align: left;
          vertical-align: top;
        }
        th {
          background-color: #f0f0f0;
          font-weight: bold;
        }
        .signature-area {
          margin-top: 60px;
        }
        .signature-line {
          display: flex;
          justify-content: space-between;
          margin-top: 40px;
          padding-top: 20px;
          border-top: 1px solid black;
        }
        .signature-block {
          text-align: center;
          width: 30%;
        }
        .signature-space {
          height: 40px;
          border-bottom: 1px solid black;
          margin: 10px 0;
        }
        .page-break {
          page-break-before: always;
        }
        @media print {
          body {
            padding: 0;
          }
        }
      </style>
    </head>
    <body>
      <div class="header">
        <h1>ЗАЯВКА НА ПОСТАВКУ ЗАПАСНЫХ ЧАСТЕЙ</h1>
        <div class="header-info">
          <div class="info-block">
            <strong>Номер заявки:</strong> ${order.value.requestNumber}
          </div>
          <div class="info-block" style="text-align: right;">
            <strong>Дата составления:</strong> ${order.value.requestDate}
          </div>
        </div>
      </div>

      <div class="section">
        <div class="section-title">1. Вид запчастей:</div>
        <div>${activePartTypes.value || 'Не указано'}</div>
      </div>

      <div class="section">
        <div class="section-title">2. Причина заказа:</div>
        <div>${order.value.reason || 'Не указана'}</div>
      </div>

      <div class="section">
        <div class="section-title">3. Список запрашиваемых запчастей:</div>
        <table>
          <thead>
            <tr>
              <th width="30">№</th>
              <th>Наименование товара</th>
              <th width="120">Модель</th>
              <th width="120">Изготовитель</th>
              <th width="60">Кол-во</th>
              <th width="50">Ед.</th>
            </tr>
          </thead>
          <tbody>
            ${order.value.items.map((item, index) => `
              <tr>
                <td>${index + 1}</td>
                <td>
                  <div><strong>Арт:</strong> ${item.article}</div>
                  <div>${item.name}</div>
                </td>
                <td>
                  <div><strong>Модель:</strong> ${item.model || '-'}</div>
                  <div><strong>Сер. №:</strong> ${item.serial || '-'}</div>
                </td>
                <td>${item.manufacturer || '-'}</td>
                <td>${item.quantity}</td>
                <td>${item.unit}</td>
              </tr>
            `).join('')}
          </tbody>
          <tfoot>
            <tr>
              <td colspan="4" style="text-align: right; font-weight: bold;">Итого:</td>
              <td style="font-weight: bold;">${totalItems.value}</td>
              <td style="font-weight: bold;">${order.value.items.length} поз.</td>
            </tr>
          </tfoot>
        </table>
      </div>

      <div class="section">
        <div class="section-title">4. Данные заявителя:</div>
        <table style="border: none;">
          <tr>
            <td style="border: none; width: 150px;"><strong>Должность:</strong></td>
            <td style="border: none;">${order.value.requesterPosition}</td>
          </tr>
          <tr>
            <td style="border: none;"><strong>ФИО:</strong></td>
            <td style="border: none;">${order.value.requesterName}</td>
          </tr>
          <tr>
            <td style="border: none;"><strong>Подразделение:</strong></td>
            <td style="border: none;">${order.value.requesterDepartment}</td>
          </tr>
        </table>
      </div>

      <div class="signature-area">
        <div class="signature-line">
          <div class="signature-block">
            <div>Должность</div>
            <div class="signature-space"></div>
            <div>${order.value.requesterPosition}</div>
          </div>
          <div class="signature-block">
            <div>Подпись</div>
            <div class="signature-space"></div>
            <div>________________</div>
          </div>
          <div class="signature-block">
            <div>ФИО</div>
            <div class="signature-space"></div>
            <div>${order.value.requesterName}</div>
          </div>
        </div>
        
        <div style="margin-top: 40px; font-size: 10pt; color: #666;">
          <div>Дата формирования документа: ${new Date().toLocaleDateString('ru-RU')}</div>
          <div>Документ сформирован автоматически</div>
        </div>
      </div>
    </body>
    </html>
  `
}

// Показать предпросмотр печати
function showPrintPreviewModal() {
  showPrintPreview.value = true
}

// Закрыть предпросмотр
function closePrintPreview() {
  showPrintPreview.value = false
}

// Скачать документ как HTML
function downloadDocument() {
  const blob = new Blob([generateDocumentHTML()], { type: 'text/html' })
  const url = URL.createObjectURL(blob)
  
  const a = document.createElement('a')
  a.href = url
  a.download = `Заявка_${order.value.requestNumber}.html`
  document.body.appendChild(a)
  a.click()
  
  setTimeout(() => {
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }, 100)
}

// Закрытие окна
function close() {
  emit('update:modelValue', false)
  
  // Сброс данных (кроме пользовательских настроек)
  order.value = {
    requestNumber: generateRequestNumber(),
    requestDate: new Date().toLocaleDateString('ru-RU'),
    
    // Сохраняем данные заявителя
    requesterName: order.value.requesterName,
    requesterPosition: order.value.requesterPosition,
    requesterDepartment: order.value.requesterDepartment,
    
    reason: '',
    items: []
  }
  
  newItem.value = { product: '', quantity: 1, unit: 'шт' }
  
  // Сбрасываем чекбоксы к начальному состоянию
  partTypes.value = [
    { id: 'repair', label: 'ремонтные запчасти', checked: true },
    { id: 'spare', label: 'запасные части', checked: false },
    { id: 'consumables', label: 'расходные материалы', checked: false }
  ]
  
  // Закрываем предпросмотр если открыт
  showPrintPreview.value = false
}

// Автоматическое заполнение даты
watch(() => props.modelValue, (isOpen) => {
  if (isOpen) {
    order.value.requestDate = new Date().toLocaleDateString('ru-RU')
    order.value.requestNumber = generateRequestNumber()
  }
})
</script>

<template>
  <Teleport to="body">
    <!-- Основное модальное окно создания заявки -->
    <div v-if="modelValue" class="modal-overlay2" @click.self="close">
      <div :class="['modal-content', { 'print-mode': isPrintMode }]">
        <!-- Успешное оформление -->
        <div v-if="isSuccess" class="success-overlay">
          <div class="success-message">
            <div class="check-icon">✅</div>
            <h3>Заявка оформлена успешно!</h3>
            <p class="request-number">Номер заявки: {{ order.requestNumber }}</p>
            <div class="download-info">
              <p>✅ JSON файл скачан</p>
              <p>✅ PDF файл готов к сохранению</p>
              <p class="download-hint">В диалоговом окне выберите "Сохранить как PDF"</p>
            </div>
            <button @click="close" class="btn-close-success">Закрыть</button>
          </div>
        </div>

        <!-- Основная форма -->
        <div v-else>
          <!-- Шапка заявки -->
          <div class="request-header">
            <div class="header-left">
              <div class="company-name">ЗАЯВКА НА ПОСТАВКУ ЗАПАСНЫХ ЧАСТЕЙ</div>
            </div>
            <div class="header-right">
              <div class="request-number-display">{{ order.requestNumber }}</div>
              <div class="request-date">Дата составления: {{ order.requestDate }}</div>
            </div>
          </div>

          <!-- Типы запчастей (исправленные чекбоксы) -->
          <div class="part-types-section">
            <div class="section-title">Вид ремонтных запчастей/деталей/узлов/придатков/запасных частей/запас/(нужное подчеркнуть)</div>
            <div class="checkboxes">
              <div 
                v-for="(type, index) in partTypes" 
                :key="type.id"
                class="checkbox-item"
                @click="updatePartType(index)"
              >
                <div class="checkbox-custom" :class="{ checked: type.checked }">
                  <span v-if="type.checked" class="checkmark">✓</span>
                </div>
                <span class="checkbox-text">{{ type.label }}</span>
              </div>
            </div>
            <div class="selected-types">
              Выбрано: <strong>{{ activePartTypes || 'ничего не выбрано' }}</strong>
            </div>
          </div>

          <!-- Причина заказа -->
          <div class="reason-section">
            <div class="section-title">Причина заказа (ремонт оборудования, пополнение запасов и т.д.):</div>
            <textarea 
              v-model="order.reason" 
              class="reason-input" 
              placeholder="Опишите причину заказа запчастей..."
              rows="3"></textarea>
          </div>

          <!-- Таблица товаров -->
          <div class="items-section">
            <div class="section-title">Список запрашиваемых запчастей:</div>
            
            <!-- Форма добавления товара -->
            <div class="add-item-form">
              <div class="form-row">
                <div class="form-group">
                  <label>Товар (артикул + наименование)</label>
                  <select v-model="newItem.product" class="custom-select">
                    <option value="" disabled>Выберите товар из списка...</option>
                    <option 
                      v-for="(item, index) in inventory" 
                      :key="item.Article || `item-${index}`" 
                      :value="item.Article || index"
                    >
                      {{ item.Article ? `[${item.Article}] ` : '' }}
                      {{ item.num_rus || item.name || item.Name || 'Товар без названия' }}
                      <template v-if="getStock(item) > 0"> (в наличии: {{ getStock(item) }})</template>
                      <template v-else> (нет в наличии)</template>
                    </option>
                  </select>
                </div>
                
                <div class="form-group">
                  <label>Количество</label>
                  <input v-model.number="newItem.quantity" type="number" min="1" max="1000">
                </div>
                
                <div class="form-group">
                  <label>Единица измерения</label>
                  <select v-model="newItem.unit" class="custom-select">
                    <option value="шт">шт</option>
                    <option value="кг">кг</option>
                    <option value="м">м</option>
                    <option value="л">л</option>
                    <option value="уп">упаковка</option>
                    <option value="компл">комплект</option>
                  </select>
                </div>
                
                <button @click="addItem" class="btn-add-item">
                  Добавить +
                </button>
              </div>
            </div>

            <!-- Таблица добавленных товаров -->
            <div v-if="order.items.length > 0" class="items-table-container">
              <table class="items-table">
                <thead>
                  <tr>
                    <th width="30">№</th>
                    <th>Наименование товара</th>
                    <th width="150">Модель, серийный номер</th>
                    <th width="150">Наименование изготовителя</th>
                    <th width="80">Кол-во</th>
                    <th width="60">Ед.</th>
                    <th width="100">Остаток на складе</th>
                    <th width="50"></th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(item, index) in order.items" :key="item.id">
                    <td class="text-center">{{ index + 1 }}</td>
                    <td>
                      <div class="product-info">
                        <div class="product-article">Арт: {{ item.article }}</div>
                        <div class="product-name">{{ item.name }}</div>
                      </div>
                    </td>
                    <td>
                      <div class="model-info editable-field">
                        <!-- Редактирование модели -->
                        <div class="editable-row">
                          <span class="field-label">Модель:</span>
                          <div 
                            v-if="editingItem === item.id && editingField === 'model'" 
                            class="editing-field"
                          >
                            <input
                              type="text"
                              v-model="item.model"
                              @blur="finishEditing"
                              @keydown="handleKeydown($event, item)"
                              class="editable-input-cell"
                              placeholder="Введите модель"
                              autofocus
                            >
                          </div>
                          <div 
                            v-else 
                            class="display-field clickable"
                            @click="startEditing(item, 'model')"
                          >
                            <span :class="{ 'placeholder': !item.model }">
                              {{ item.model || 'Нажмите для ввода' }}
                            </span>
                          </div>
                        </div>
                        
                        <!-- Редактирование серийного номера -->
                        <div class="editable-row">
                          <span class="field-label">Сер. №:</span>
                          <div 
                            v-if="editingItem === item.id && editingField === 'serial'" 
                            class="editing-field"
                          >
                            <input
                              type="text"
                              v-model="item.serial"
                              @blur="finishEditing"
                              @keydown="handleKeydown($event, item)"
                              class="editable-input-cell"
                              placeholder