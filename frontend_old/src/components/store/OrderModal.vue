<script setup>
import { ref, computed, watch } from 'vue'
import html2pdf from 'html2pdf.js'
import { useI18n } from 'vue-i18n'
const { t, locale } = useI18n()


const props = defineProps({
  modelValue: Boolean,
  inventory: Array,
  currentUser: {
    type: Object,
    default: () => ({}) // Оставляем пустым или базовым
  }
})


const emit = defineEmits(['update:modelValue', 'submit'])

const isSuccess = ref(false)
const isPrintMode = ref(false)
const showPrintPreview = ref(false)
const isGeneratingPDF = ref(false)
const pdfPreviewUrl = ref(null)
const itemName = ref(null)


const editingItem = ref(null)
const editingField = ref('')

const order = ref({
  requestNumber: generateRequestNumber(),
  requestDate: new Date().toLocaleDateString('ru-RU'),
  requesterName: props.currentUser.name || t('orderModal.defaultName'),
  requesterPosition: props.currentUser.position || t('orderModal.defaultPosition'),
  requesterDepartment: props.currentUser.department || t('orderModal.defaultDepartment'),
  
  reason: '',
  items: []
})

const partTypes = ref([
  { id: 'repair', label: t('orderModal.repair'), checked: true },
  { id: 'spare', label: t('orderModal.spare'), checked: false },
  { id: 'consumables', label: t('orderModal.consumables'), checked: false }
])

const newItem = ref({
  product: '',
  quantity: 1,
  unit: t('orderModal.pcs')
})

function generateRequestNumber() {
  const date = new Date()
  const year = date.getFullYear().toString().slice(-2)
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const random = Math.floor(Math.random() * 100).toString().padStart(2, '0')
  return `${t('orderModal.Req')}-${day}${month}${year}-${random}`
}

function addItem() {
  if (!newItem.value.product) {
    alert(t('orderModal.selectFromList'))
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
    alert(t('orderModal.alertNotFound'))
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
  if (locale === 'ru') {
    itemName.value = selectedProduct.num_rus || 
                   selectedProduct.name || 
                   selectedProduct.Name || 
                   selectedProduct.product_name || 
                   t('orderModal.notSpecifiedt')
  } else {
    itemName.value = selectedProduct.num_eng || 
                   selectedProduct.name || 
                   selectedProduct.Name || 
                   selectedProduct.product_name || 
                   t('orderModal.notSpecifiedt')
  }

    

  
  const article = selectedProduct.Article || 
                  selectedProduct.article || 
                  selectedProduct.code || 
                  `${t('orderModal.productName')}-${itemId.toString().slice(-6)}`
  
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
    unit: 'pcs' 
  }
}

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

function validateForm() {
  if (order.value.items.length === 0) {
    alert(t('orderModal.alertNotProduct'))
    return false
  }
  
  if (!order.value.reason.trim()) {
    alert(t('orderModal.alertNotReason'))
    return false
  }
  
  if (!hasSelectedPartTypes.value) {
    alert(t('orderModal.alertNotType'))
    return false
  }
  
  if (!order.value.requesterName.trim()) {
    alert(t('orderModal.alertNotName'))
    return false
  }
  
  if (!order.value.requesterPosition.trim()) {
    alert(t('orderModal.alertNotPosition'))
    return false
  }
  
  return true
}

async function submitOrder() {
  if (!validateForm()) return

  const orderData = {
    ...order.value,
    partTypes: activePartTypes.value,
    totalItems: totalItems.value,
    selectedPartTypes: partTypes.value.filter(t => t.checked),
    systemInfo: {
      generatedAt: new Date().toISOString(),
      platform: navigator.platform
    }
  }

  saveJSONToLocalStorage(orderData)

  await generatePDF()
  emit('submit', orderData)
  isSuccess.value = true

  setTimeout(() => {
    close()
    isSuccess.value = false
  }, 2000)
}

async function generatePDF() {
  isGeneratingPDF.value = true
  
  const element = document.createElement('div')
  element.innerHTML = generateDocumentHTML()
  
  const opt = {
  html2canvas: { 
    scale: 1.5,     
    useCORS: false,  
    logging: false,
    imageTimeout: 0 
  }
}

  try {
    const pdfBlob = await html2pdf().set(opt).from(element).output('blob')
    
    await savePDFToLocalStorage(pdfBlob, order.value.requestNumber)

    isGeneratingPDF.value = false
    return true
  } catch (error) {
    console.error('PDF Generation Error:', error)
    isGeneratingPDF.value = false
    return false
  }
}

function printDocument() {
  const printWindow = window.open('', '_blank')
  if (!printWindow) {
    alert(t('orderModal.alertNotWindow'))
    return false
  }
  
  printWindow.document.write(generateDocumentHTML())
  printWindow.document.close()
  
  setTimeout(() => {
    printWindow.print()
  }, 500)
  
  return true
}

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

function saveJSONToLocalStorage(orderData) {
  try {
    const savedOrders = JSON.parse(localStorage.getItem('savedOrdersJSON') || '[]')
    
    const orderToSave = {
      ...orderData,
      savedAt: new Date().toISOString(),
      storageType: 'json'
    }
    
    savedOrders.push(orderToSave)
    localStorage.setItem('savedOrdersJSON', JSON.stringify(savedOrders.slice(-100)))
    
    return true
  } catch (error) {
    console.error('Error saving JSON to localStorage:', error)
    return false
  }
}

function generateDocumentHTML() {
  return `
    <!DOCTYPE html>
    <html lang="${locale.value}">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>${t('orderModal.title')} ${order.value.requestNumber}</title>
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
        <h1>${t('orderModal.orderZip')}</h1>
        <div class="header-info">
          <div class="info-block">
            <strong>${t('orderModal.orderNumber')}:</strong> ${order.value.requestNumber}
          </div>
          <div class="info-block" style="text-align: right;">
            <strong>${t('orderModal.dateOfDocumentFormation')}:</strong> ${order.value.requestDate}
          </div>
        </div>
      </div>

      <div class="section">
        <div class="section-title">1. ${t('orderModal.typeOfSpareParts')}:</div>
        <div>${activePartTypes.value || t('orderModal.notSpecified')}</div>
      </div>

      <div class="section">
        <div class="section-title">2. ${t('orderModal.reasonForTheOrder')}:</div>
        <div>${order.value.reason || t('orderModal.notSpecified')}</div>
      </div>

      <div class="section">
        <div class="section-title">3. ${t('orderModal.listOfRequestedSpareParts')}:</div>
        <table>
          <thead>
            <tr>
              <th width="30">№</th>
              <th>${t('orderModal.productName')}</th>
              <th width="120">${t('orderModal.model')}</th>
              <th width="120">${t('orderModal.manufacturer')}</th>
              <th width="60">${t('orderModal.number')}</th>
              <th width="50">${t('orderModal.measurement')}</th>
            </tr>
          </thead>
          <tbody>
            ${order.value.items.map((item, index) => `
              <tr>
                <td>${index + 1}</td>
                <td>
                  <div><strong>${t('orderModal.art')}:</strong> ${item.article}</div>
                  <div>${item.name}</div>
                </td>
                <td>
                  <div><strong>${t('orderModal.model')}:</strong> ${item.model || '-'}</div>
                  <div><strong>${t('orderModal.serialNumber')}. №:</strong> ${item.serial || '-'}</div>
                </td>
                <td>${item.manufacturer || '-'}</td>
                <td>${item.quantity}</td>
                <td>${item.unit}</td>
              </tr>
            `).join('')}
          </tbody>
          <tfoot>
            <tr>
              <td colspan="4" style="text-align: right; font-weight: bold;">${t('orderModal.all')}:</td>
              <td style="font-weight: bold;">${totalItems.value}</td>
              <td style="font-weight: bold;">${order.value.items.length} ${t('orderModal.position')}.</td>
            </tr>
          </tfoot>
        </table>
      </div>

      <div class="section">
        <div class="section-title">4. ${t('orderModal.applicantsData')}:</div>
        <table style="border: none;">
          <tr>
            <td style="border: none; width: 150px;"><strong>${t('orderModal.post')}:</strong></td>
            <td style="border: none;">${order.value.requesterPosition}</td>
          </tr>
          <tr>
            <td style="border: none;"><strong>${t('orderModal.fullName')}:</strong></td>
            <td style="border: none;">${order.value.requesterName}</td>
          </tr>
          <tr>
            <td style="border: none;"><strong>${t('orderModal.subdivision')}:</strong></td>
            <td style="border: none;">${order.value.requesterDepartment}</td>
          </tr>
        </table>
      </div>

      <div class="signature-area">
        <div class="signature-line">
          <div class="signature-block">
            <div>${t('orderModal.post')}</div>
            <div class="signature-space"></div>
            <div>${order.value.requesterPosition}</div>
          </div>
          <div class="signature-block">
            <div>${t('orderModal.signature')}</div>
            <div class="signature-space"></div>
            <div>________________</div>
          </div>
          <div class="signature-block">
            <div>${t('orderModal.fullName')}</div>
            <div class="signature-space"></div>
            <div>${order.value.requesterName}</div>
          </div>
        </div>
        
        <div style="margin-top: 40px; font-size: 10pt; color: #666;">
          <div>${t('orderModal.dateOfDocumentFormation')}: ${new Date().toLocaleDateString(locale.value === 'ru'? 'ru-Ru': 'en-US')}</div>
          <div>${t('orderModal.documentIsFormed')}</div>
        </div>
      </div>
    </body>
    </html>
  `
}


async function showPrintPreviewModal() {
  isGeneratingPDF.value = true
  showPrintPreview.value = true
  
  const element = document.createElement('div')
  element.innerHTML = generateDocumentHTML()
  
  const opt = {
    margin: 5,
    image: { type: 'jpeg', quality: 1.0 },
    html2canvas: { 
      scale: 2,         
      useCORS: true,
      logging: false
    },
    jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
  }

  try {
    const pdfBlob = await html2pdf().set(opt).from(element).output('blob')
    if (pdfPreviewUrl.value) URL.revokeObjectURL(pdfPreviewUrl.value)
    
    const blobUrl = URL.createObjectURL(pdfBlob)
    pdfPreviewUrl.value = `${blobUrl}#view=FitH` 
    
  } catch (error) {
    console.error('PDF Preview Error:', error)
  } finally {
    isGeneratingPDF.value = false
  }
}


function closePrintPreview() {
  showPrintPreview.value = false
  if (pdfPreviewUrl.value) {
    URL.revokeObjectURL(pdfPreviewUrl.value)
    pdfPreviewUrl.value = null
  }
}

function close() {
  emit('update:modelValue', false)
  
  order.value = {
    requestNumber: generateRequestNumber(),
    requestDate: new Date().toLocaleDateString('en-US'),
    
    requesterName: order.value.requesterName,
    requesterPosition: order.value.requesterPosition,
    requesterDepartment: order.value.requesterDepartment,
    
    reason: '',
    items: []
  }
  
  newItem.value = { product: '', quantity: 1, unit: 'pcs' }
  
  partTypes.value = [
    { id: 'repair', label: t('orderModal.repair'), checked: true },
    { id: 'spare', label: t('orderModal.spare'), checked: false },
    { id: 'consumables', label: t('orderModal.consumables'), checked: false }
  ]
  
  showPrintPreview.value = false
}

watch(() => props.modelValue, (isOpen) => {
  if (isOpen) {
    order.value.requestDate = new Date().toLocaleDateString(locale.value === 'ru'? 'ru-Ru': 'en-US')
    order.value.requestNumber = generateRequestNumber()
  }
})
</script>

<template>
  <Teleport to="body">
    <div v-if="modelValue" class="modal-overlay2" @click.self="close">
      <div :class="['modal-content', { 'print-mode': isPrintMode }]">
        <div v-if="isSuccess" class="success-overlay">
          <div class="success-message">
            <div class="check-icon">✅</div>
            <h3>{{ $t('orderModal.success') }}</h3>
            <p class="request-number">{{ $t('orderModal.orderNumber') }}: {{ order.requestNumber }}</p>
            <button @click="close" class="btn-close-success">Close</button>
          </div>
        </div>

        <div v-else>
          <div class="request-header">
            <div class="header-left">
              <div class="company-name">{{ $t('orderModal.orderZip') }}</div>
            </div>
            <div class="header-right">
              <div class="request-number-display">{{ order.requestNumber }}</div>
              <div class="request-date">{{ $t('orderModal.dateOfComposition') }}: {{ order.requestDate }}</div>
            </div>
          </div>

          <div class="part-types-section">
            <div class="section-title">{{ $t('orderModal.selectType') }}</div>
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
              {{ $t('orderModal.Selected') }}: <strong>{{ activePartTypes || t('orderModal.nothingSelected') }}</strong>
            </div>
          </div>

          <div class="reason-section">
            <div class="section-title">{{ $t('orderModal.sectionTitle') }}:</div>
            <textarea 
              v-model="order.reason" 
              class="reason-input" 
              :placeholder= "$t('orderModal.sectionOrder')"
              rows="3"></textarea>
          </div>

          <div class="items-section">
            <div class="section-title">{{ $t('orderModal.listOfRequestedSpareParts') }}:</div>
            
            <div class="add-item-form">
              <div class="form-row">
                <div class="form-group">
                  <label>{{ $t('orderModal.selectProduct') }}</label>
                  <select v-model="newItem.product" class="custom-select">
                    <option value="" disabled>{{ $t('orderModal.selectFromList') }}</option>
                    <option 
                      v-for="(item, index) in inventory" 
                      :key="item.Article || `item-${index}`" 
                      :value="item.Article || index"
                      v-show ="locale === 'ru'"
                    >
                      {{ item.Article ? `[${item.Article}] ` : '' }}
                      {{ item.num_rus || item.name || item.Name || t('orderModal.ProductNoName') }}
                      <template v-if="getStock(item) > 0"> ({{ $t('orderModal.inStock') }}: {{ getStock(item) }})</template>
                      <template v-else> ({{ $t('orderModal.outOfStock') }})</template>
                    </option>
                    <option 
                      v-for="(item, index) in inventory" 
                      :key="item.Article || `item-${index}`" 
                      :value="item.Article || index"
                      v-show="locale === 'en'"
                    >
                      {{ item.Article ? `[${item.Article}] ` : '' }}
                      {{ num_eng || item.name || item.Name || t('orderModal.ProductNoName') }}
                      <template v-if="getStock(item) > 0"> ({{ $t('orderModal.inStock') }}: {{ getStock(item) }})</template>
                      <template v-else> ({{ $t('orderModal.outOfStock') }})</template>
                    </option>
                  </select>
                </div>
                
                <div class="form-group">
                  <label>{{ $t('orderModal.quantityOrdf') }}</label>
                  <input v-model.number="newItem.quantity" type="number" min="1" max="1000">
                </div>
                
                <div class="form-group">
                  <label>{{ $t('orderModal.measurement') }}</label>
                  <select v-model="newItem.unit" class="custom-select">
                    <option value="pcs">{{ $t('orderModal.ps') }}</option>
                    <option value="kg">{{ $t('orderModal.kg') }}</option>
                    <option value="m">{{ $t('orderModal.m') }}</option>
                    <option value="l">{{ $t('orderModal.l') }}</option>
                    <option value="pack">{{ $t('orderModal.pack') }}</option>
                    <option value="set">{{ $t('orderModal.set') }}</option>
                  </select>
                </div>
                
                <button @click="addItem" class="btn-add-item">
                  {{ $t('orderModal.add') }}
                </button>
              </div>
            </div>

            <div v-if="order.items.length > 0" class="items-table-container">
              <table class="items-table">
                <thead>
                  <tr>
                    <th width="30">№</th>
                    <th>{{ $t('orderModal.productName') }}</th>
                    <th width="150">{{ $t('orderModal.modelSer') }}</th>
                    <th width="150">{{ $t('orderModal.manufacturer') }}</th>
                    <th width="80">{{ $t('orderModal.quantity') }}</th>
                    <th width="60">{{ $t('orderModal.Unit') }}</th>
                    <th width="100">{{ $t('orderModal.add') }}</th>
                    <th width="50"></th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(item, index) in order.items" :key="item.id">
                    <td class="text-center">{{ index + 1 }}</td>
                    <td>
                      <div class="product-info">
                        <div class="product-article">{{ $t('orderModal.art') }}: {{ item.article }}</div>
                        <div class="product-name">{{ item.name }}</div>
                      </div>
                    </td>
                    <td>
                      <div class="model-info editable-field">
                        <div class="editable-row">
                          <span class="field-label">{{ $t('orderModal.model') }}:</span>
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
                              v-bind= "$t('orderModal.enterModel')"
                              autofocus
                            >
                          </div>
                          <div 
                            v-else 
                            class="display-field clickable"
                            @click="startEditing(item, 'model')"
                          >
                            <span :class="{ 'placeholder': !item.model }">
                              {{ item.model || t('orderModal.click') }}
                            </span>
                          </div>
                        </div>
                        
                        <div class="editable-row">
                          <span class="field-label">{{ $t('orderModal.serialNumber') }}. №:</span>
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
                              :placeholder="$t('orderModal.serialNumber')"
                              autofocus
                            >
                          </div>
                          <div 
                            v-else 
                            class="display-field clickable"
                            @click="startEditing(item, 'serial')"
                          >
                            <span :class="{ 'placeholder': !item.serial }">
                              {{ item.serial || t('orderModal.click') }}
                            </span>
                          </div>
                        </div>
                      </div>
                    </td>
                    <td>
                      <div class="manufacturer-info editable-field">
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
                              placeholder="$t('orderModal.enterManufacturer')"
                              autofocus
                            >
                          </div>
                          <div 
                            v-else 
                            class="display-field clickable"
                            @click="startEditing(item, 'manufacturer')"
                          >
                            <span :class="{ 'placeholder': !item.manufacturer }">
                              {{ item.manufacturer || t('orderModal.click') }}
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
                        <option value="pcs">pcs</option>
                        <option value="kg">kg</option>
                        <option value="m">m</option>
                        <option value="l">l</option>
                        <option value="pack">pack</option>
                        <option value="set">set</option>
                      </select>
                    </td>
                    <td class="text-center">
                      <span :class="['stock-badge', { 'low-stock': item.stock < item.quantity }]">
                        {{ item.stock }}
                      </span>
                    </td>
                    <td class="text-center">
                      <button @click="removeItem(item.id)" class="btn-remove" :title="t('orderModal.remove')">
                        ×
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
              
              <div class="items-summary">
                <div class="summary-item">
                  <span>{{ $t('orderModal.totalPositions') }}:</span>
                  <strong>{{ order.items.length }}</strong>
                </div>
                <div class="summary-item">
                  <span>{{ $t('orderModal.totalQuantity') }}:</span>
                  <strong>{{ totalItems }} {{ $t('orderModal.units') }}</strong>
                </div>
              </div>
            </div>
            
            <div v-else class="empty-state">
              <div class="empty-icon">📋</div>
              <p>{{ $t('orderModal.noAdded') }}</p>
              <p class="empty-hint">{{ $t('orderModal.selectProducts') }}</p>
            </div>
          </div>

          <div class="signature-section">
            <div class="signature-fields">
              <div class="field-group">
                <label>{{ $t('orderModal.post') }}:</label>
                <input 
                  type="text" 
                  v-model="order.requesterPosition" 
                  class="signature-input"
                  :placeholder="$t('orderModal.enterPost')" >
              </div>
              <div class="field-group">
                <label>{{ $t('orderModal.alertNotName') }}:</label>
                <input 
                  type="text" 
                  v-model="order.requesterName" 
                  class="signature-input"
                  placeholder="Enter name">
              </div>
              <div class="field-group">
                <label>{{ $t('orderModal.subdivision') }}:</label>
                <input 
                  type="text" 
                  v-model="order.requesterDepartment" 
                  class="signature-input"
                  :placeholder="$t('orderModal.subdivision')">
              </div>
            </div>
            
            <div class="signature-row">
              <div class="signature-label">{{ $t('orderModal.positionSignature') }}:</div>
              <div class="signature-value">
                <span class="signature-text">{{ order.requesterPosition }}</span>
                <span class="signature-line">___________________</span>
                <span class="signature-text">{{ order.requesterName }}</span>
              </div>
            </div>
          </div>

          <div class="modal-actions">
            <button @click="showPrintPreviewModal" class="btn-print" :title="$t('orderModal.subdivision')">
              🖨️ {{ $t('orderModal.print') }}
            </button>
            
            <div class="action-buttons">
              <button @click="close" class="btn-cancel">
                {{ $t('orderModal.cancel') }}
              </button>
              
              <button @click="submitOrder" class="btn-submit" :disabled="order.items.length === 0">
                📥 {{ $t('orderModal.submit') }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showPrintPreview" class="print-preview-overlay" @click.self="closePrintPreview">
      <div class="print-preview-modal">
        <div class="print-preview-header">
          <h2>{{ $t('orderModal.previewOfTheDocumentForPrinting') }}</h2>
          <button @click="closePrintPreview" class="btn-close-preview" title="Close">
            ×
          </button>
        </div>
        
        <div class="print-preview-content">
          <div v-if="isGeneratingPDF" class="preview-loading">
            {{ $t('orderModal.generatingPDF') }}
          </div>
          <iframe 
            v-else-if="pdfPreviewUrl"
            :src="pdfPreviewUrl" 
            class="preview-iframe"
            :title="$t('orderModal.PDF')"
          ></iframe>
        </div>
        
        <div class="print-preview-actions">
          <div class="preview-action-buttons">
            <button @click="closePrintPreview" class="btn-preview-cancel">
              {{ $t('orderModal.Back') }}
            </button>
            <button @click="printDocument" class="btn-preview-print">
              🖨️ {{ $t('orderModal.printPDF') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.modal-overlay2 {
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

.print-mode {
  max-width: 210mm;
  max-height: none;
  margin: 0;
  box-shadow: none;
  border: 1px solid #ccc;
}

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

.items-section {
  padding: 15px 20px;
}

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

.preview-loading {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  font-weight: 600;
  color: #666;
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

.print-preview-overlay {
  position: fixed;
  top: 0;
  /* left: 0; */
  width: 100%;
  height: 100vh;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(5px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 10001;
  padding: 20px;
}

.print-preview-modal {
  background: #525659; /* Темный фон, как в Adobe/Chrome PDF viewer */
  width: 95vw;         /* 95% ширины экрана */
  max-width: 1200px;   /* Ограничение для очень широких мониторов */
  height: 90vh;        /* 90% высоты экрана */
  display: flex;
  flex-direction: column;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.4);
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

/* Контейнер для iframe */
.print-preview-content {
  flex: 1;             /* Занимает всё свободное пространство */
  background: #f5f5f5;
  display: flex;
  justify-content: center;
  align-items: flex-start; /* Начинаем с верха страницы */
  overflow: auto;      /* Скролл, если страница не влезает */
  padding: 0;
}

/* Сам iframe */
.preview-iframe {
  width: 100%;
  height: 100%;
  border: none;
  display: block;
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

@media print {
  .modal-overlay2 {
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