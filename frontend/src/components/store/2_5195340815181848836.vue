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
const isGeneratingPDF = ref(false)

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
async function submitOrder() {
  if (!validateForm()) return

  const orderData = {
    ...order.value,
    partTypes: activePartTypes.value,
    totalItems: totalItems.value,
    selectedPartTypes: partTypes.value.filter(t => t.checked),
    systemInfo: {
      generatedAt: new Date().toISOString(),
      userAgent: navigator.userAgent,
      platform: navigator.platform
    }
  }

  // Сохраняем JSON
  const isJsonSaved = saveOrderToJSON(orderData)
  
  if (!isJsonSaved) {
    alert('Не удалось сохранить JSON файл')
    return
  }

  // Скачиваем PDF
  await generatePDF()

  emit('submit', orderData)
  isSuccess.value = true

  setTimeout(() => {
    close()
    isSuccess.value = false
  }, 2000)
}

// Новая функция для генерации PDF (аналог printDocument, но без открытия окон)
async function generatePDF() {
  isGeneratingPDF.value = true
  
  try {
    // Динамически загружаем jsPDF с поддержкой кириллицы
    if (!window.jspdf) {
      await loadJSPDF()
    }
    
    const { jsPDF } = window.jspdf
    
    // Создаем PDF с правильными настройками для русского языка
    const doc = new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: 'a4',
      compress: true
    })
    
    // Устанавливаем шрифт (по умолчанию может не поддерживать кириллицу)
    // Можно использовать стандартные шрифты или загрузить кастомные
    doc.setFont('helvetica', 'normal')
    doc.setFontSize(16)
    
    // Добавляем заголовок
    const title = 'ЗАЯВКА НА ПОСТАВКУ ЗАПАСНЫХ ЧАСТЕЙ'
    const pageWidth = doc.internal.pageSize.width
    const titleWidth = doc.getStringUnitWidth(title) * 16 / doc.internal.scaleFactor
    const titleX = (pageWidth - titleWidth) / 2
    
    doc.text(title, titleX, 20)
    
    doc.setFontSize(10)
    doc.text(`Номер заявки: ${order.value.requestNumber}`, 20, 35)
    doc.text(`Дата составления: ${order.value.requestDate}`, 20, 40)
    
    let y = 50
    
    // 1. Вид запчастей
    doc.setFontSize(12)
    doc.text('1. Вид запчастей:', 20, y)
    y += 8
    doc.setFontSize(10)
    
    // Разбиваем длинный текст на строки
    const partTypesText = activePartTypes.value || 'Не указано'
    const partLines = doc.splitTextToSize(partTypesText, 170)
    partLines.forEach(line => {
      doc.text(line, 20, y)
      y += 6
    })
    y += 10
    
    // 2. Причина заказа
    doc.setFontSize(12)
    doc.text('2. Причина заказа:', 20, y)
    y += 8
    doc.setFontSize(10)
    
    const reasonText = order.value.reason || 'Не указана'
    const reasonLines = doc.splitTextToSize(reasonText, 170)
    reasonLines.forEach(line => {
      doc.text(line, 20, y)
      y += 6
    })
    y += 15
    
    // 3. Список запчастей
    if (order.value.items.length > 0) {
      doc.setFontSize(12)
      doc.text('3. Список запрашиваемых запчастей:', 20, y)
      y += 10
      
      // Таблица
      const tableConfig = {
        startY: y,
        head: [['№', 'Наименование', 'Кол-во', 'Ед.']],
        body: [],
        headStyles: {
          fillColor: [0, 86, 179],
          textColor: 255,
          fontStyle: 'bold'
        },
        columnStyles: {
          0: { cellWidth: 10 },
          1: { cellWidth: 130 },
          2: { cellWidth: 20 },
          3: { cellWidth: 20 }
        },
        margin: { left: 20 }
      }
      
      // Добавляем данные
      order.value.items.forEach((item, index) => {
        const itemName = `${item.article} - ${item.name}`
        const shortName = itemName.length > 60 ? itemName.substring(0, 57) + '...' : itemName
        
        tableConfig.body.push([
          index + 1,
          shortName,
          item.quantity.toString(),
          item.unit
        ])
      })
      
      // Генерируем таблицу
      doc.autoTable(tableConfig)
      
      // Получаем конечную Y позицию после таблицы
      y = doc.lastAutoTable.finalY + 10
      
      // Итоговая информация
      doc.setFontSize(10)
      doc.text(`Итого: ${totalItems.value} ед., ${order.value.items.length} позиций`, 20, y)
      y += 20
    }
    
    // 4. Данные заявителя
    doc.setFontSize(12)
    doc.text('4. Данные заявителя:', 20, y)
    y += 10
    
    doc.setFontSize(10)
    doc.text(`Должность: ${order.value.requesterPosition}`, 20, y)
    y += 7
    doc.text(`ФИО: ${order.value.requesterName}`, 20, y)
    y += 7
    doc.text(`Подразделение: ${order.value.requesterDepartment}`, 20, y)
    y += 15
    
    // Подпись
    doc.setFontSize(10)
    doc.text('Должность, подпись (ФИО) лица, составившего заявку:', 20, y)
    y += 7
    doc.text(`${order.value.requesterPosition} ___________________ ${order.value.requesterName}`, 20, y)
    
    // Футер
    doc.setFontSize(8)
    doc.text(`Дата формирования: ${new Date().toLocaleDateString('ru-RU')}`, 20, 280)
    doc.text('Документ сформирован автоматически', 20, 285)
    
    // Сохраняем PDF
    doc.save(`Заявка_${order.value.requestNumber}.pdf`)
    
    isGeneratingPDF.value = false
    return true
    
  } catch (error) {
    console.error('Ошибка при создании PDF:', error)
    isGeneratingPDF.value = false
    
    // Альтернатива: использовать браузерную печать
    return downloadPDFUsingPrint()
  }
}

// Альтернативный способ - использовать браузерную печать для генерации PDF
function downloadPDFUsingPrint() {
  try {
    const printContent = generateDocumentHTML()
    const printWindow = window.open('', '_blank')
    
    printWindow.document.open()
    printWindow.document.write(printContent)
    printWindow.document.close()
    
    // Даем время на загрузку
    setTimeout(() => {
      printWindow.print()
      
      // Закрываем окно через 1 секунду
      setTimeout(() => {
        printWindow.close()
      }, 1000)
    }, 500)
    
    return true
  } catch (error) {
    console.error('Ошибка при печати:', error)
    return false
  }
}

// Функция загрузки jsPDF
function loadJSPDF() {
  return new Promise((resolve, reject) => {
    if (window.jspdf) {
      resolve()
      return
    }
    
    // Используем более новую версию с поддержкой autoTable
    const script = document.createElement('script')
    script.src = 'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js'
    script.onload = () => {
      // Загружаем плагин для таблиц
      const autoTableScript = document.createElement('script')
      autoTableScript.src = 'https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.5.28/jspdf.plugin.autotable.min.js'
      autoTableScript.onload = resolve
      autoTableScript.onerror = reject
      document.head.appendChild(autoTableScript)
    }
    script.onerror = reject
    document.head.appendChild(script)
  })
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

// Новая функция для сохранения PDF в localStorage
function savePDFToLocalStorage(pdfBlob, requestNumber) {
  return new Promise((resolve, reject) => {
    try {
      const reader = new FileReader()
      
      reader.onload = function() {
        try {
          const pdfBase64 = reader.result.split(',')[1]
          const savedOrders = JSON.parse(localStorage.getItem('savedOrdersWithPDF') || '[]')
          
          const orderToSave = {
            requestNumber,
            pdfBase64,
            savedAt: new Date().toISOString()
          }
          
          savedOrders.push(orderToSave)
          localStorage.setItem('savedOrdersWithPDF', JSON.stringify(savedOrders.slice(-50)))
          
          resolve(true)
        } catch (error) {
          reject(error)
        }
      }
      
      reader.onerror = reject
      reader.readAsDataURL(pdfBlob)
    } catch (error) {
      reject(error)
    }
  })
}

// Новая функция для сохранения в JSON в localStorage
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
    <div v-if="modelValue" class="modal-overlay" @click.self="close">
      <div :class="['modal-content', { 'print-mode': isPrintMode }]">
        <!-- Успешное оформление -->
        <div v-if="isSuccess" class="success-overlay">
          <div class="success-message">
            <div class="check-icon">✅</div>
            <h3>Заявка оформлена успешно!</h3>
            <p class="request-number">Номер заявки: {{ order.requestNumber }}</p>
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
                              placeholder="Введите серийный номер"
                              autofocus
                            >
                          </div>
                          <div 
                            v-else 
                            class="display-field clickable"
                            @click="startEditing(item, 'serial')"
                          >
                            <span :class="{ 'placeholder': !item.serial }">
                              {{ item.serial || 'Нажмите для ввода' }}
                            </span>
                          </div>
                        </div>
                      </div>
                    </td>
                    <td>
                      <div class="manufacturer-info editable-field">
                        <!-- Редактирование изготовителя -->
                        <div class="editable-row">
                          <div 
                            v-if="editingItem === item.id && editingField === 'manufacturer'" 
                            class="editing-field"
                          >
                            <input
                              type="text"
                              v-model="item.manufacturer"
                              @blur="finishEditing"
                              @keydown="handleKeydown($event, item)"
                              class="editable-input-cell"
                              placeholder="Введите наименование изготовителя"
                              autofocus
                            >
                          </div>
                          <div 
                            v-else 
                            class="display-field clickable"
                            @click="startEditing(item, 'manufacturer')"
                          >
                            <span :class="{ 'placeholder': !item.manufacturer }">
                              {{ item.manufacturer || 'Нажмите для ввода' }}
                            </span>
                          </div>
                        </div>
                      </div>
                    </td>
                    <td class="text-center">
                      <input 
                        type="number" 
                        v-model.number="item.quantity" 
                        min="1"
                        class="quantity-input"
                        @change="validateQuantity(item)">
                    </td>
                    <td class="text-center">
                      <select v-model="item.unit" class="unit-select">
                        <option value="шт">шт</option>
                        <option value="кг">кг</option>
                        <option value="м">м</option>
                        <option value="л">л</option>
                        <option value="уп">уп</option>
                        <option value="компл">компл</option>
                      </select>
                    </td>
                    <td class="text-center">
                      <span :class="['stock-badge', { 'low-stock': item.stock < item.quantity }]">
                        {{ item.stock }}
                      </span>
                    </td>
                    <td class="text-center">
                      <button @click="removeItem(item.id)" class="btn-remove" title="Удалить">
                        ×
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
              
              <div class="items-summary">
                <div class="summary-item">
                  <span>Всего позиций:</span>
                  <strong>{{ order.items.length }}</strong>
                </div>
                <div class="summary-item">
                  <span>Общее количество:</span>
                  <strong>{{ totalItems }} ед.</strong>
                </div>
              </div>
            </div>
            
            <div v-else class="empty-state">
              <div class="empty-icon">📋</div>
              <p>Нет добавленных товаров</p>
              <p class="empty-hint">Выберите товары из списка выше</p>
            </div>
          </div>

          <!-- Подпись (редактируемая) -->
          <div class="signature-section">
            <div class="signature-fields">
              <div class="field-group">
                <label>Должность:</label>
                <input 
                  type="text" 
                  v-model="order.requesterPosition" 
                  class="signature-input"
                  placeholder="Введите должность">
              </div>
              <div class="field-group">
                <label>ФИО заявителя:</label>
                <input 
                  type="text" 
                  v-model="order.requesterName" 
                  class="signature-input"
                  placeholder="Введите ФИО">
              </div>
              <div class="field-group">
                <label>Подразделение:</label>
                <input 
                  type="text" 
                  v-model="order.requesterDepartment" 
                  class="signature-input"
                  placeholder="Введите подразделение">
              </div>
            </div>
            
            <div class="signature-row">
              <div class="signature-label">Должность, подпись (ФИО) лица, составившего заявку:</div>
              <div class="signature-value">
                <span class="signature-text">{{ order.requesterPosition }}</span>
                <span class="signature-line">___________________</span>
                <span class="signature-text">{{ order.requesterName }}</span>
              </div>
            </div>
          </div>

          <!-- Кнопки действий -->
          <div class="modal-actions">
            <button @click="showPrintPreviewModal" class="btn-print" title="Показать предпросмотр печати">
              🖨️ Печать
            </button>
            
            <div class="action-buttons">
              <button @click="close" class="btn-cancel">
                Отмена
              </button>
              
              <button @click="submitOrder" class="btn-submit" :disabled="order.items.length === 0">
                📥 Оформить заявку
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Модальное окно предпросмотра печати -->
    <div v-if="showPrintPreview" class="print-preview-overlay" @click.self="closePrintPreview">
      <div class="print-preview-modal">
        <div class="print-preview-header">
          <h2>Предпросмотр документа для печати</h2>
          <button @click="closePrintPreview" class="btn-close-preview" title="Закрыть">
            ×
          </button>
        </div>
        
        <div class="print-preview-content">
          <iframe 
            :srcdoc="generateDocumentHTML()" 
            class="preview-iframe"
            title="Предпросмотр документа"
          ></iframe>
        </div>
        
        <div class="print-preview-actions">
          <button @click="downloadDocument" class="btn-download">
            📥 Скачать HTML
          </button>
          <div class="preview-action-buttons">
            <button @click="closePrintPreview" class="btn-preview-cancel">
              Назад
            </button>
            <button @click="printDocument" class="btn-preview-print">
              🖨️ Печатать (PDF)
            </button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
/* Добавляем стили для сообщения о скачивании */
.download-info {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 6px;
  border: 1px solid #ddd;
  text-align: left;
  margin: 15px 0;
  max-width: 400px;
}

.download-info p {
  margin: 5px 0;
  font-size: 14px;
  color: #333;
}

.download-hint {
  font-size: 12px;
  color: #666;
  font-style: italic;
  margin-top: 10px !important;
  padding-top: 10px;
  border-top: 1px solid #eee;
}

.btn-submit {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Остальные стили остаются без изменений */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 10000;
  padding: 20px;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 100%;
  max-width: 1100px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 100%;
  max-width: 1100px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}

.print-mode {
  max-width: 210mm;
  max-height: none;
  margin: 0;
  box-shadow: none;
  border: 1px solid #ccc;
}

/* Шапка заявки */
.request-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 20px;
  border-bottom: 2px solid #000;
  background: #f8f9fa;
}

.header-left {
  flex: 1;
}

.company-name {
  font-size: 18px;
  font-weight: 700;
  text-transform: uppercase;
  margin-bottom: 8px;
  color: #000;
}

.header-right {
  text-align: right;
}

.request-number-display {
  font-size: 16px;
  font-weight: 700;
  color: #0056b3;
  margin-bottom: 4px;
}

.request-date {
  font-size: 14px;
  color: #555;
}

/* Типы запчастей с исправленными чекбоксами */
.part-types-section {
  padding: 15px 20px;
  border-bottom: 1px solid #ddd;
}

.section-title {
  font-weight: 600;
  margin-bottom: 10px;
  color: #333;
  font-size: 14px;
}

.checkboxes {
  display: flex;
  gap: 20px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.checkbox-item {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  user-select: none;
  padding: 5px 10px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.checkbox-item:hover {
  background-color: #f0f8ff;
}

.checkbox-custom {
  width: 20px;
  height: 20px;
  border: 2px solid #0056b3;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  transition: all 0.2s;
}

.checkbox-custom.checked {
  background: #0056b3;
  border-color: #0056b3;
}

.checkmark {
  color: white;
  font-weight: bold;
  font-size: 14px;
}

.checkbox-text {
  font-size: 14px;
  color: #333;
}

.selected-types {
  padding: 8px 12px;
  background: #e8f4ff;
  border-radius: 4px;
  font-size: 14px;
  margin-top: 5px;
}

/* Причина заказа */
.reason-section {
  padding: 15px 20px;
  border-bottom: 1px solid #ddd;
}

.reason-input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-family: inherit;
  font-size: 14px;
  resize: vertical;
  background: white;
}

.reason-input:focus {
  border-color: #0056b3;
  outline: none;
  box-shadow: 0 0 0 2px rgba(0, 86, 179, 0.2);
}

/* Секция товаров */
.items-section {
  padding: 15px 20px;
}

/* Форма добавления товара */
.add-item-form {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 6px;
  margin-bottom: 20px;
  border: 1px solid #ddd;
}

.form-row {
  display: flex;
  gap: 10px;
  align-items: flex-end;
  flex-wrap: wrap;
}

.form-group {
  flex: 1;
  min-width: 200px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 12px;
  font-weight: 600;
  color: #555;
}

.form-group input,
.form-group select {
  padding: 8px 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 14px;
  background: white;
}

.form-group input:focus,
.form-group select:focus {
  border-color: #0056b3;
  outline: none;
}

.btn-add-item {
  background: #0056b3;
  color: white;
  border: none;
  padding: 8px 20px;
  border-radius: 4px;
  font-weight: 600;
  cursor: pointer;
  height: 36px;
  white-space: nowrap;
}

.btn-add-item:hover {
  background: #004494;
}

/* Таблица товаров */
.items-table-container {
  margin-top: 20px;
  overflow-x: auto;
}

.items-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  min-width: 900px;
}

.items-table th {
  background: #0056b3;
  color: white;
  font-weight: 600;
  text-align: left;
  padding: 10px;
  border: 1px solid #003d82;
  white-space: nowrap;
}

.items-table td {
  padding: 8px 10px;
  border: 1px solid #ddd;
  vertical-align: top;
}

.items-table tbody tr:nth-child(even) {
  background: #f8f9fa;
}

.items-table tbody tr:hover {
  background: #e8f4ff;
}

.text-center {
  text-align: center;
}

/* Стили для редактируемых полей в таблице */
.editable-field {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.editable-row {
  display: flex;
  align-items: center;
  gap: 8px;
  min-height: 24px;
}

.field-label {
  font-size: 11px;
  color: #666;
  min-width: 50px;
  font-weight: 600;
}

.clickable {
  cursor: pointer;
  padding: 2px 6px;
  border-radius: 3px;
  border: 1px solid transparent;
  transition: all 0.2s;
  flex: 1;
  min-height: 22px;
  display: flex;
  align-items: center;
}

.clickable:hover {
  background-color: #f0f8ff;
  border-color: #0056b3;
}

.placeholder {
  color: #999;
  font-style: italic;
}

.editable-input-cell {
  width: 100%;
  padding: 4px 8px;
  border: 1px solid #0056b3;
  border-radius: 4px;
  font-size: 12px;
  background: white;
  box-shadow: 0 0 0 2px rgba(0, 86, 179, 0.1);
}

.editable-input-cell:focus {
  outline: none;
  box-shadow: 0 0 0 2px rgba(0, 86, 179, 0.2);
}

.editing-field {
  flex: 1;
}

.display-field {
  flex: 1;
}

.product-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.product-article {
  font-size: 11px;
  color: #666;
  font-family: monospace;
}

.product-name {
  font-size: 14px;
  color: #333;
}

.model-info, .manufacturer-info {
  font-size: 13px;
  color: #444;
}

.quantity-input {
  width: 70px;
  padding: 4px 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  text-align: center;
}

.unit-select {
  padding: 4px 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 12px;
  background: white;
}

.stock-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
  background: #d4edda;
  color: #155724;
  min-width: 50px;
}

.stock-badge.low-stock {
  background: #f8d7da;
  color: #721c24;
}

.btn-remove {
  background: #dc3545;
  color: white;
  border: none;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
  transition: background-color 0.2s;
}

.btn-remove:hover {
  background: #c82333;
}

.items-summary {
  display: flex;
  justify-content: flex-end;
  gap: 30px;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #ddd;
  font-size: 14px;
}

.summary-item {
  display: flex;
  gap: 10px;
  align-items: center;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #6c757d;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px dashed #ddd;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 15px;
  opacity: 0.5;
}

.empty-hint {
  font-size: 14px;
  color: #999;
  margin-top: 5px;
}

/* Подпись с редактируемыми полями */
.signature-section {
  padding: 20px;
  border-top: 1px solid #ddd;
  margin-top: 20px;
}

.signature-fields {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #ddd;
}

.field-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.field-group label {
  font-size: 12px;
  font-weight: 600;
  color: #555;
}

.signature-input {
  padding: 8px 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 14px;
  background: white;
}

.signature-input:focus {
  border-color: #0056b3;
  outline: none;
}

.signature-row {
  margin-top: 20px;
}

.signature-label {
  font-weight: 600;
  margin-bottom: 8px;
  color: #333;
  font-size: 14px;
}

.signature-value {
  padding-top: 40px;
  border-top: 1px solid #000;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 15px;
  flex-wrap: wrap;
}

.signature-text {
  font-weight: 600;
  color: #000;
}

.signature-line {
  color: #666;
  letter-spacing: 2px;
}

/* Кнопки действий */
.modal-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-top: 1px solid #ddd;
  background: #f8f9fa;
  border-radius: 0 0 8px 8px;
}

.btn-print {
  background: #6c757d;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: background-color 0.2s;
}

.btn-print:hover {
  background: #5a6268;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.btn-cancel {
  background: #6c757d;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-cancel:hover {
  background: #5a6268;
}

.btn-submit {
  background: #28a745;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-submit:hover:not(:disabled) {
  background: #218838;
}

.btn-submit:disabled {
  background: #b5d6c0;
  cursor: not-allowed;
  opacity: 0.7;
}

/* Успешное оформление */
.success-overlay {
  padding: 40px 20px;
  text-align: center;
}

.success-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.success-message .check-icon {
  font-size: 64px;
  animation: scaleIn 0.5s ease;
}

@keyframes scaleIn {
  from {
    transform: scale(0);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

.success-message h3 {
  font-size: 24px;
  font-weight: 700;
  color: #28a745;
  margin: 0;
}

.request-number {
  font-size: 18px;
  font-weight: 600;
  color: #0056b3;
  background: #e8f4ff;
  padding: 10px 20px;
  border-radius: 6px;
}

.btn-close-success {
  background: #0056b3;
  color: white;
  border: none;
  padding: 12px 32px;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  margin-top: 20px;
  transition: background-color 0.2s;
}

.btn-close-success:hover {
  background: #004494;
}

/* Модальное окно предпросмотра печати */
.print-preview-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(5px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 10001;
  padding: 20px;
}

.print-preview-modal {
  background: white;
  border-radius: 10px;
  width: 100%;
  max-width: 1000px;
  max-height: 95vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3);
  overflow: hidden;
}

.print-preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background: linear-gradient(to right, #0056b3, #003d82);
  color: white;
}

.print-preview-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.btn-close-preview {
  background: none;
  border: none;
  color: white;
  font-size: 28px;
  cursor: pointer;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color 0.2s;
}

.btn-close-preview:hover {
  background: rgba(255, 255, 255, 0.2);
}

.print-preview-content {
  flex: 1;
  padding: 0;
  overflow: hidden;
  background: #f5f5f5;
}

.preview-iframe {
  width: 100%;
  height: 100%;
  min-height: 900px;
  border: none;
  background: white;
}

.print-preview-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background: #f8f9fa;
  border-top: 1px solid #ddd;
}

.btn-download {
  background: #17a2b8;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: background-color 0.2s;
}

.btn-download:hover {
  background: #138496;
}

.preview-action-buttons {
  display: flex;
  gap: 10px;
}

.btn-preview-cancel {
  background: #6c757d;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-preview-cancel:hover {
  background: #5a6268;
}

.btn-preview-print {
  background: #28a745;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: background-color 0.2s;
}

.btn-preview-print:hover {
  background: #218838;
}

/* Стили для печати */
@media print {
  .modal-overlay {
    position: static;
    background: none;
    backdrop-filter: none;
    padding: 0;
  }
  
  .modal-content {
    max-width: 100%;
    max-height: none;
    box-shadow: none;
    border: none;
    border-radius: 0;
  }
  
  .modal-actions,
  .btn-print,
  .btn-add-item,
  .btn-remove,
  .add-item-form,
  .editable-input,
  .signature-input,
  .quantity-input,
  .unit-select,
  .checkbox-item,
  .checkboxes,
  .selected-types,
  .clickable,
  .editable-input-cell {
    display: none !important;
  }
  
  .section-title,
  .signature-label {
    color: #000 !important;
  }
  
  .items-table {
    page-break-inside: avoid;
  }
  
  .signature-section {
    page-break-inside: avoid;
  }
  
  .part-types-section,
  .reason-section,
  .items-section {
    background: none !important;
    border: 1px solid #000 !important;
    margin-bottom: 10px;
  }
}

/* Адаптивность */
@media (max-width: 768px) {
  .modal-content {
    max-height: 85vh;
    margin: 10px;
  }
  
  .request-header {
    flex-direction: column;
    gap: 10px;
  }
  
  .header-right {
    text-align: left;
  }
  
  .form-row {
    flex-direction: column;
  }
  
  .form-group {
    min-width: 100%;
  }
  
  .items-table {
    font-size: 11px;
  }
  
  .modal-actions {
    flex-direction: column;
    gap: 10px;
  }
  
  .action-buttons {
    width: 100%;
    justify-content: space-between;
  }
  
  .signature-fields {
    grid-template-columns: 1fr;
  }
  
  .editable-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 2px;
  }
  
  .field-label {
    min-width: auto;
    font-size: 10px;
  }
  
  .editable-input-cell {
    font-size: 11px;
  }
  
  .print-preview-modal {
    max-height: 85vh;
  }
  
  .print-preview-header h2 {
    font-size: 16px;
  }
  
  .print-preview-actions {
    flex-direction: column;
    gap: 10px;
    align-items: stretch;
  }
  
  .preview-action-buttons {
    width: 100%;
    justify-content: space-between;
  }
}
</style>