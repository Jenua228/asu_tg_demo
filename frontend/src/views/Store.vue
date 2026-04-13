<script setup>
import { ref, onMounted, warn, watch, computed, onUnmounted } from 'vue'
import CircleChart from '../components/store/CircleChart.vue'
import BarChart from '../components/store/BarChart.vue'
import { AgGridVue } from 'ag-grid-vue3'
import WorkshopCharts from '../components/store/WorkshopCharts.vue'
import ImageTooltip from '../components/ImageTooltip.vue'
import InventoryModal from '../components/store/InventoryModal.vue'
import OrderModal from '../components/store/OrderModal.vue'
import PdfModal from '../components/store/PdfModal.vue'
import { useI18n } from 'vue-i18n'
import { inventoryApi, inventoryRequestApi, inventoryAlertApi } from '../api'

import InventoryManagement from '../components/store/InventoryManagement.vue'
import InventoryRequestsList from '../components/store/InventoryRequestsList.vue'
import InventoryAlerts from '../components/store/InventoryAlerts.vue'


const { t } = useI18n()

// Вкладки внутри склада ЗИП
const storeTab = ref('inventory') // 'inventory' | 'requests' | 'alerts'
const unreadAlertsCount = ref(0)
let alertsUpdateInterval = null

const props = defineProps({
  data: {
    type: Object,
    required: true,
    default: () => []
}
})


const defaultColDef = {
  flex: 1,
  minWidth: 100,
  sortable: true,
  editable: true,
  filter: true,
  wrapText: true,      // Разрешаем перенос текста
  autoHeight: false,   // Включаем ручное управление высотой
  tooltipComponent: ImageTooltip,
};


const getRowStyle = params => {
  const count = Number(params.data.count);
  const min = Number(params.data.min_sctock);
    if (count < min) { return { backgroundColor: '#ffcccc' }; }
    else { return {backgroundColor: '#fff'} };
};

const columnDefs = computed(() => [
  { headerName: t('reports.tableColumns.id'), field: "Number", width: 40,  minWidth: 30, sort: 'asc', },
  { headerName: t('store.columns.article'), field: "Article" },
  { 
    headerName: t('store.columns.document'), 
    field: "pdfUrl",
    width: 80,
    cellClass: 'grid-cell-centered',
    // Отрисовываем иконку в зависимости от наличия ссылки
    cellRenderer: params => {
      const hasPdf = params.value && params.value.trim().length > 0;
      return hasPdf 
        ? `<span title="Документ прикреплен" style="color: #059669; font-size: 1.2rem;">📄</span>` 
        : `<span title="Нет документа" style="color: #94a3b8; opacity: 0.5;">—</span>`;
    }
  },
  { headerName: t('store.columns.nameRus'), field: "num_rus" , cellClass: 'grid-cell-centered', wrapText: true, },
  { 
    headerName: t('store.columns.nameEng'), 
    field: "num_eng", 
    cellClass: 'grid-cell-centered', 
    tooltipField: "num_eng",
    tooltipComponent: ImageTooltip,
    wrapText: true,
    cellRenderer: params => `<span>${params.value}🖼️</span>`,
    width: 250   
  },
  { 
    headerName: t('store.columns.count'), 
    field: "count", 
    editable: true,
    cellClass: 'grid-cell-centered', 
    type: 'numericColumn',           
    comparator: (valueA, valueB, nodeA, nodeB) => {
      const getDiff = (node) => {
        const count = Number(node.data.count) || 0;
        const min = Number(node.data.min_sctock) || 0;
        return count - min;
      };
      const diffA = getDiff(nodeA);
      const diffB = getDiff(nodeB);
      if (diffA === diffB) return 0;
      return diffA > diffB ? 1 : -1;
    }
  },
  { 
    headerName: t('store.columns.minStock'), 
    field: "min_sctock",
    cellClass: 'grid-cell-centered',
    type: 'numericColumn',
  },
  { headerName: t('store.columns.storageName'), field: "name_storage" },
  { headerName: t('store.columns.comment'),  field: "comment", },
      ])


const projectsByDepartment = [  
  { Number: '1.2.1.1', Article: "468353.055", num_rus: 'Блок распределительный', num_eng: 'Distribution unit', count: '3',  comment: "", imgName: "Distribution unit ШИБФ.468353.055.jpg", min_sctock: '3', pdfUrl: '' },
  { Number: '1.2.2.1', Article: "466217.002", num_rus: 'ЭВМ промышленного назначения TC-1900', num_eng: 'Industrial computer TC-1900', count: '5',  comment: "", imgName: 'Industrial computer ТС-1900 “Тензор” ТСВН.466217.002.jpg', min_sctock: '3', pdfUrl: '' },
  { Number: '1.2.2.2', Article: "466234", num_rus: 'Цифровой мультиметр Truevolt 34461A', num_eng: 'Digital multimeter Truevolt 34461', count: '12',  comment: "", imgName: "Digital multimeter Truevolt 34461A.jpg", min_sctock: '3', pdfUrl: "/doc/ЕФ3.035.074.pdf"},
  { Number: '1.2.3.1', Article: "411218.014", num_rus: 'Аналоговый сигнатурный анализатор АСА', num_eng: 'Analogue signature analyser ACA', count: '8',  comment: "", imgName: "Analogue signature analyser АСА ВЦТП.411218.014.jpg", min_sctock: '3', pdfUrl: "/doc/ЕФ3.035.074 ПЭ3.pdf"},
  { Number: '1.3.1.1', Article: "468354.031", num_rus: 'Панель сопряжения Ц.1Э', num_eng: 'Interface panel DCH', count: '7',  comment: "", imgName: "Interface panel DCH.1Э ШИБФ.468354.031.jpg", min_sctock: '3'},
  { Number: '2.1.1.1', Article: "468353.101", num_rus: 'Мультиадаптер', num_eng: 'Multiadapter', count: '9',  comment: "", imgName: "Multiadapter 468353.101.jpg", min_sctock: '3'},
  { Number: '2.2.1.1', Article: "066419.007", num_rus: 'Устройство сушильно‑вытяжное', num_eng: 'Exhaust drier-device', count: '4',  comment: "", imgName: "Exhaust drier-device ШИБФ.066419.007.jpg", min_sctock: '3', pdfUrl: "/doc/test2.pdf"},
  { Number: '2.2.2.2', Article: "", num_rus: 'Измеритель статического напряжения АТР‑9365', num_eng: 'Static voltage meter АТP-9365', count: '5',  comment: "", imgName: "Static voltage meter АТP‑9365.jpg", min_sctock: '3'},
  { Number: '2.2.2.3', Article: "", num_rus: 'Цифровая система пайки', num_eng: 'Digital soldering system', count: '9',  comment: "", imgName: "Digital heating system НП24-17про.jpg", min_sctock: '3'},
  { Number: '2.2.2.4', Article: "8007-0133", num_rus: 'Многофункциональный цифровой паяльно-ремонтный центр PACE PRC-2000E', num_eng: 'Multifunction digital repair soldering station PACE PRC-2000E', count: '7', min_sctock: '3',  comment: "",  imgName: "Multifunction digital repair soldering station PACE PRC-2000E.jpg"},
  { Number: '3.1.1.1', Article: "", num_rus: 'Аппарат телефонный «ТА-88»', num_eng: 'Telephone set “ТА-88”', count: '5',  comment: "", imgName: "Telephone set “ТА-88” .jpg", min_sctock: '3'},
  { Number: '3.1.1.2', Article: "411212.002", num_rus: 'Измеритель сопротивления заземления ИС-20', num_eng: 'Ground resistance meter IC-20', count: '6',  comment: "", imgName: "Ground resistance meter ИС-20 РАПМ.411212.002.jpg", min_sctock: '3'},
  { Number: '1.1.1.0', Article: "066419.012", num_rus: 'Субблок Н6.17.06.08', num_eng: 'Subblock N6.17.06.08', count: '2',  comment: "", imgName: "sadfg.jpg", min_sctock: '1', pdfUrl: "/doc/Н6.17.06.08-PRD.pdf"},    
  { Number: '1.1.1.1', Article: "133LN1", num_rus: 'Плата 133ЛН1', num_eng: '133ln1', count: '3',  comment: "", imgName: "133ln.jpg", min_sctock: '6', pdfUrl: "/doc/ЕФ3.035.074 СБ.PDF"},
  { Number: '1.1.1.2', Article: "533TL2", num_rus: '533ТЛ2 элемент', num_eng: '533TL2 element', count: '1',  comment: "", imgName: "Image1.jpg", min_sctock: '2'},
  { Number: '3.1.3.1', Article: "687431.003", num_rus: 'Катушка с кабелем ЛВС', num_eng: 'LAN cable spool', count: '9',  comment: "", imgName: "LAN cable spool ШИБФ.687431.003.jpg", min_sctock: '3'},
]

const isModalOpen = ref(false)
const isOrderModalOpen = ref(false)
const rowData = ref([])
const isLoadingInventory = ref(false)
const gridApi = ref(null);
const selectedPdfUrl = ref(null); 
const isPdfModalOpen = ref(false);
const isEditPdfMode = ref(false); // Состояние для переключения модалки
const isRowSelected = ref(false); // Выбрана ли хоть одна строка


const localeRu = computed(()  => ({
  // Фильтры
  contains: t('agGrid.contains'),
  notContains: t('agGrid.notContains'),
  equals: t('agGrid.equals'),
  notEqual: t('agGrid.notEqual'),
  startsWith: t('agGrid.startsWith'),
  endsWith: t('agGrid.endsWith'),
  blank: t('agGrid.blank'),
  notBlank: t('agGrid.notBlank'),
  
  // Числовые фильтры
  lessThan: t('agGrid.lessThan'),
  greaterThan: t('agGrid.greaterThan'),
  lessThanOrEqual: t('agGrid.lessThanOrEqual'),
  greaterThanOrEqual: t('agGrid.greaterThanOrEqual'),
  inRange: t('agGrid.inRange'),
  
  // Условия
  andCondition: t('agGrid.andCondition'),
  orCondition: t('agGrid.orCondition'),
  
  // Панель фильтров
  filterOoo: t('agGrid.filterOoo'),
  applyFilter: t('agGrid.applyFilter'),
  resetFilter: t('agGrid.resetFilter'),
  clearFilter: t('agGrid.clearFilter'),
  
  // Пагинация
  page: t('agGrid.page'),
  more: t('agGrid.more'),
  of: t('agGrid.of'),
  to: t('agGrid.to'),
  nextPage: t('agGrid.nextPage'),
  previousPage: t('agGrid.previousPage'),
  firstPage: t('agGrid.firstPage'),
  lastPage: t('agGrid.lastPage'),
  pageSize: t('agGrid.pageSize'),
  pageSizeSelectorLabel: t('agGrid.pageSizeSelectorLabel'),
  
  // Выделение
  selectAll: t('agGrid.selectAll'),
  selectAllSearchResults: t('agGrid.selectAllSearchResults'),
  searchOoo: t('agGrid.searchOoo'),
  noMatches: t('agGrid.noMatches'),
  
  // Прочее
  noRowsToShow: t('agGrid.noRowsToShow'),
  loading: t('agGrid.loading'),
  pinColumn: t('agGrid.pinColumn'),
  autosizeThiscolumn: t('agGrid.autosizeThiscolumn'),
  autosizeAllColumns: t('agGrid.autosizeAllColumns'),
  resetColumns: t('agGrid.resetColumns'),
  copy: t('agGrid.copy'),
  copyWithHeaders: t('agGrid.copyWithHeaders'),
  paste: t('agGrid.paste'),
  export: t('agGrid.export'),
  csvExport: t('agGrid.csvExport'),
  excelExport: t('agGrid.excelExport'),
}))



const onCellValueChanged = async (event) => {
  // Когда пользователь редактирует ячейку таблицы - сохраняем в БД
  const updatedItem = event.data;
  
  try {
    // Преобразуем UI формат → API формат
    const apiPayload = {
      article: updatedItem.Article,
      nameRus: updatedItem.num_rus,
      nameEng: updatedItem.num_eng,
      currentCount: Number(updatedItem.count),
      minStock: Number(updatedItem.min_sctock),
      storageName: updatedItem.name_storage,
      comment: updatedItem.comment || '',
      pdfUrl: updatedItem.pdfUrl || ''
    };
    
    const dbId = updatedItem._dbId || parseInt(updatedItem.Number);
    console.log('📤 Обновляю товар в БД (ID=' + dbId + '):', apiPayload);
    
    // Отправляем PUT запрос
    await inventoryApi.update(dbId, apiPayload);
    console.log('✅ Товар обновлён в БД');
  } catch (error) {
    console.error('❌ Ошибка при сохранении товара:', error);
    alert('Ошибка при сохранении: ' + error.message);
    // Откатываем изменение в UI
    event.api.redrawRows({ rowNodes: [event.node] });
  }
};

// Загрузить товары из БД при монтировании компонента
const loadInventoryFromDB = async () => {
  isLoadingInventory.value = true;
  try {
    const response = await inventoryApi.getAll();
    // Преобразуем ответ БД (camelCase) в формат AG Grid (snake_case)
    rowData.value = response.data.map((item) => ({
      Number: item.id.toString(),
      Article: item.article,
      num_rus: item.nameRus,      // ← Исправил: nameRus → num_rus
      num_eng: item.nameEng,      // ← Исправил: nameEng → num_eng
      count: item.currentCount,   // ← Исправил: currentCount → count
      min_sctock: item.minStock,  // ← Исправил: minStock → min_sctock
      name_storage: item.storageName,  // ← Исправил: storageName → name_storage
      comment: item.comment || '',
      imgName: '',
      pdfUrl: item.pdfUrl || '',
      _dbId: item.id // Сохраняем ID из БД
    }));
    console.log('✅ Товары загружены из БД:', rowData.value.length);
  } catch (error) {
    console.error('❌ Ошибка при загрузке товаров:', error);
    rowData.value = [];
  } finally {
    isLoadingInventory.value = false;
  }
};

const onCellReady = (params) => {
  gridApi.value = params.api;
};

const getRowId = (params) => params.data.Number; 
const handleAddItem = async (item) => {
  try {
    // 1. Преобразуем данные из формата формы в формат API
    const apiPayload = {
      article: item.Article || '',
      nameRus: item.num_rus,
      nameEng: item.num_eng,
      currentCount: Number(item.count) || 0,
      minStock: Number(item.min_sctock) || 0,
      storageName: item.name_storage || 'Склад ЗИП',
      comment: item.comment || '',
      pdfUrl: item.pdfUrl || ''
    };
    
    console.log('📤 Отправляю товар в БД:', apiPayload);
    
    // 2. Сохраняем в БД через API
    const response = await inventoryApi.create(apiPayload);
    const createdItem = response.data;
    
    console.log('✅ Товар сохранён в БД:', createdItem);
    
    // 3. Преобразуем ответ из БД (camelCase) обратно в формат AG Grid (snake_case)
    const gridItem = {
      Number: createdItem.id.toString(),
      Article: createdItem.article,
      num_rus: createdItem.nameRus,  // ← Исправил: nameRus → num_rus
      num_eng: createdItem.nameEng,  // ← Исправил: nameEng → num_eng
      count: createdItem.currentCount,  // ← Исправил: currentCount → count
      min_sctock: createdItem.minStock,  // ← Исправил: minStock → min_sctock
      name_storage: createdItem.storageName,  // ← Исправил: storageName → name_storage
      comment: createdItem.comment || '',
      imgName: '',
      pdfUrl: createdItem.pdfUrl || '',
      _dbId: createdItem.id
    };
    
    // 4. Добавляем в локальный массив для немедленного отображения
    rowData.value = [...rowData.value, gridItem];
    gridApi.value?.applyTransaction({ add: [gridItem] });
    
    alert(t('inventory.itemAdded'));
  } catch (error) {
    console.error('❌ Ошибка при добавлении товара:', error);
    alert(t('inventory.addError') || 'Ошибка при добавлении товара');
  }
};



const handleOrderSubmit = async (orderData) => {
  console.log('Заказ оформлен:', orderData);
  
  // Проверяем наличие товаров в заявке
  if (!orderData.items || orderData.items.length === 0) {
    alert(t('inventory.loadError'));
    return;
  }

  try {
    let successCount = 0;
    let errorCount = 0;
    
    // Итерируем по каждому товару в заявке
    for (const orderItem of orderData.items) {
      try {
        // Находим товар в инвентаре по артикулу
        const inventoryItem = rowData.value.find(i => 
          i.Article === orderItem.article || 
          i.num_rus === orderItem.name ||
          i.Number === orderItem.originalProduct?.Number
        );
        
        if (!inventoryItem) {
          console.warn(`⚠️ Товар не найден: ${orderItem.article}`);
          errorCount++;
          continue;
        }

        // Создаём заявку в БД через API
        const requestData = {
          inventoryItemId: parseInt(inventoryItem.Number),
          requestedQuantity: Number(orderItem.quantity),
          reason: 'manual',
          createdBy: orderData.requesterName || 'Пользователь'
        };
        
        const response = await inventoryRequestApi.create(requestData);
        console.log('✅ Заявка создана в БД:', response.data);
        successCount++;
        
        // Уменьшаем запас в локальном массиве
        const itemIndex = rowData.value.findIndex(i => i.Number === inventoryItem.Number);
        if (itemIndex !== -1) {
          const updatedItem = { ...rowData.value[itemIndex] };
          updatedItem.count = Number(updatedItem.count) - Number(orderItem.quantity);
          rowData.value[itemIndex] = updatedItem;
          gridApi.value?.applyTransaction({ update: [updatedItem] });
        }
      } catch (itemError) {
        console.error('Ошибка при создании заявки для товара:', orderItem.article, itemError);
        errorCount++;
      }
    }
    
    // Обновляем таблицу
    gridApi.value?.redrawRows();
    
    // Выводим результат
    if (successCount > 0 && errorCount === 0) {
      // alert(`✅ ${successCount} заявка(и) успешно созданы!`);
      toast.access('Создана новая заявка')
    } else if (successCount > 0) {
      alert(`⚠️ Создано ${successCount} заявок(и), ошибок: ${errorCount}`);
    } else {
      alert(`❌ Ошибка при создании заявок`);
    }
  } catch (error) {
    console.error('Ошибка при обработке заказа:', error);
    alert('Ошибка при обработке заказа: ' + error.message);
  }
};

// Загрузка количества непрочитанных оповещений
const loadUnreadAlertsCount = async () => {
  try {
    const response = await inventoryAlertApi.getUnread()
    unreadAlertsCount.value = response.data.length
  } catch (error) {
    console.error('Ошибка при загрузке непрочитанных оповещений:', error)
  }
}

// Обновление счетчика при прочтении всех оповещений
const onAlertsUpdated = () => {
  unreadAlertsCount.value = 0
}

// Загрузка товаров при монтировании компонента
onMounted(() => {
  loadInventoryFromDB();
  loadUnreadAlertsCount()
  
  // Обновлять количество непрочитанных оповещений каждые 10 секунд
  alertsUpdateInterval = setInterval(() => {
    loadUnreadAlertsCount()
  }, 10000)
});

watch(() => storeTab.value, async () => {
  if (storeTab.value === 'alerts') {
    loadUnreadAlertsCount()
    
    const alertsComponent = document.querySelector('[data-alerts-widget]')
    if (alertsComponent) {
    }
  }
})

// Функция, которая срабатывает при клике на строку или выборе
const onSelectionChanged = (event) => {
  const selectedNodes = event.api.getSelectedNodes();
  
  // 1. Фиксируем сам факт выбора для кнопки "Прикрепить"
  isRowSelected.value = selectedNodes.length > 0;

  if (isRowSelected.value) {
    const data = selectedNodes[0].data;
    // 2. Проверяем наличие PDF для кнопки "Показать"
    if (data.pdfUrl && data.pdfUrl.trim().length > 0) {
      selectedPdfUrl.value = data.pdfUrl;
    } else {
      selectedPdfUrl.value = null;
    }
  } else {
    selectedPdfUrl.value = null;
  }
};

const onCellDoubleClicked = (params) => {
  if (params.colDef.field === 'pdfUrl' && params.value) {
    selectedPdfUrl.value = params.value;
    isPdfModalOpen.value = true;
  }
};

const handleAttachPdf = (newUrl) => {
  const selectedRows = gridApi.value.getSelectedRows();
  if (selectedRows.length > 0) {
    const targetItem = selectedRows[0];
    
    // Обновляем в локальном массиве rowData
    const index = rowData.value.findIndex(i => i.Number === targetItem.Number);
    if (index !== -1) {
      rowData.value[index].pdfUrl = newUrl;
      
      // Обновляем AG Grid
      gridApi.value.applyTransaction({ update: [rowData.value[index]] });
      
      // Обновляем состояние выбранного PDF, чтобы кнопка "Показать" сразу стала активной
      selectedPdfUrl.value = newUrl;
    }
  }
};

// Функция для открытия модалки в режиме редактирования
const openAttachModal = () => {
  isEditPdfMode.value = true;
  isPdfModalOpen.value = true;
};

</script>

<template>
  <div class="manager-dashboard">
    <!-- Заголовок с управлением вкладками -->
    <div class="header">
      <h2>{{ $t('store.title') }}</h2>
      
      <!-- Вкладки управления -->
      <div class="store-tabs">
        <button 
          class="store-tab"
          :class="{ active: storeTab === 'inventory' }"
          @click="storeTab = 'inventory'"
        >
          📋 {{ t('inventory.currentStock') }}
        </button>
        <button 
          class="store-tab"
          :class="{ active: storeTab === 'requests' }"
          @click="storeTab = 'requests'"
        >
          📦 {{ t('inventory.requestsTitle') }}
        </button>
        <button 
          class="store-tab"
          :class="{ active: storeTab === 'alerts' }"
          @click="storeTab = 'alerts'"
        >
          🔔 {{ t('inventory.alertsTitle') }}
          <span v-if="unreadAlertsCount > 0" class="alert-badge">
            {{ unreadAlertsCount }}
          </span>
        </button>
      </div>
      
      <!-- Кнопки действий (только для вкладки inventory) -->
      <div class="header-actions" v-if="storeTab === 'inventory'">
        <button 
          class="btn btn-edit" 
          :class="{ 'btn-pdf-active': isRowSelected }" 
          :disabled="!isRowSelected" 
          @click="openAttachModal"
        >
          {{ $t('store.attachDocument') }}
        </button>

        <button 
        class="btn btn-pdf" :class="{ 'btn-pdf-active': selectedPdfUrl }" 
        :disabled="!selectedPdfUrl" @click="isPdfModalOpen = true" >
          {{ $t('store.showDocument') }}
        </button>

        <button class="btn btn-add" @click="isModalOpen = true" >{{ $t('store.addInventory') }}</button>
        <InventoryModal v-model="isModalOpen" @add="handleAddItem" />

        <button class="btn btn-ofer" @click="isOrderModalOpen = true" >{{ $t('store.createOrder') }}</button>
        <OrderModal v-model="isOrderModalOpen" :inventory="rowData" @submit="handleOrderSubmit" />
      </div>
    </div>

    <!-- Содержимое вкладок -->
    <!-- Вкладка 1: Таблица товаров (существующее) -->
    <div v-if="storeTab === 'inventory'" class="tab-content inventory-tab">


      <div class="ag-grid-wrapper">
      <ag-grid-vue
        class="ag-theme-alpine"
        :localeText="localeRu"
        style="width: 100%; height: 80vh;"
        :headerHeight="40"
        :rowHeight="65"
        :suppressCellFocus="true"
        :stopEditingWhenCellsLoseFocus= "true"
        :enableBrowserTooltips="false"
        :tooltipShowDelay="100" 
        :getRowId="getRowId"
        :columnDefs="columnDefs"
        :getRowStyle="getRowStyle"
        :rowData="rowData"
        :defaultColDef="defaultColDef"
        rowSelection="single"
        :isRowSelectable="isRowSelectable"
        :animateRows="true"
        :pagination="true"
        :paginationPageSize="15"
        :paginationPageSizeSelector="[5, 10, 25, 50]"
        @grid-ready="onCellReady"
        @selection-changed="onSelectionChanged"
        @cell-double-clicked="onCellDoubleClicked"
        @cell-value-changed="onCellValueChanged"
      />
    </div>
    </div>

    <!-- Вкладка 2: Заявки на пополнение -->
    <div v-if="storeTab === 'requests'" class="tab-content requests-tab">
      <InventoryRequestsList @back-to-inventory="storeTab = 'inventory'" />
    </div>

    <!-- Вкладка 3: Оповещения -->
    <div v-if="storeTab === 'alerts'" class="tab-content alerts-tab">
      <InventoryAlerts @alerts-updated="onAlertsUpdated" />
    </div>

    <!-- Modals -->
    <PdfModal 
      v-model="isPdfModalOpen" 
      :pdfUrl="selectedPdfUrl"
      :isEditMode="isEditPdfMode"
      @update-pdf="handleAttachPdf"
      @update:modelValue="(val) => { if(!val) isEditPdfMode = false }"/>
  </div>
</template>
  
<style scoped>
.manager-dashboard {
  padding: 20px;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between; /* Разносит заголовок и группу кнопок по краям */
  padding: 0 40px;                /* Горизонтальные отступы внутри хедера */
  height: auto;
  min-height: 80px;
  border-radius: 30px;
  background-color: #fff;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  border: 1px solid #eef0f2;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 15px;
}

.header h2 {
  margin: 0;
  font-size: 28px;
  color: #1e293b;
  flex: 1;
  min-width: 200px;
}

/* Вкладки внутри склада */
.store-tabs {
  display: flex;
  gap: 8px;
  align-items: center;
  justify-content: center;
  flex: 1;
}

.store-tab {
  padding: 8px 16px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  background: #f1f5f9;
  color: #475569;
  font-weight: 500;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  position: relative;
}

.store-tab:hover {
  background: #e2e8f0;
  color: #1e293b;
}

.store-tab.active {
  background: #10b981;
  color: white;
  border-color: #059669;
  box-shadow: 0 2px 6px rgba(16, 185, 129, 0.3);
}

.alert-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 22px;
  height: 22px;
  padding: 0 6px;
  margin-left: 6px;
  background: #ef4444;
  color: white;
  border-radius: 11px;
  font-size: 11px;
  font-weight: bold;
  box-shadow: 0 2px 4px rgba(239, 68, 68, 0.3);
}

/* Контент вкладок */
.tab-content {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(5px); }
  to { opacity: 1; transform: translateY(0); }
}

.requests-tab, .alerts-tab {
  padding: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}


/* Контейнер для кнопок */
.header-actions {
  display: flex;
  gap: 20px; /* Расстояние между кнопками */
}

/* Закругление краев и мягкая тень для обертки */
.ag-grid-wrapper {
  border-radius: 30px;
  overflow-y: auto;
  /* box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05); */
  border: 1px solid #acacac;
}


/* Стилизация заголовков: делаем их жирнее и чуть меньше */
.ag-header-cell-label {
  text-transform: uppercase;
  font-size: 13px;
  letter-spacing: 0.5px;
}

/* Центрирование данных в ячейках */
:deep(.grid-cell-centered) {
  display: flex !important;
  justify-content: center !important;
  align-items: center !important;
  text-align: center !important;
}

:deep(.ag-right-aligned-cell) {
  text-align: center !important;
  justify-content: center !important;
}

.ag-tooltip-custom {
  /* display: flex; */
  width: 200px;
  height: 300px;
  height: auto;
  margin-bottom: 8px;
  border-radius: 2px;
}

.btn {
  padding: 12px 24px;
  font-size: 15px;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  border: none;
}

/* Button styles */
.btn-add {
  border: 1px solid #00000079;
  background-color: #5bc06398
}
.btn-add:hover {
  background-color: #5bc063
}

.btn-edit {
  border: 1px solid #00000079;
  background-color: #d86a0388
}
.btn-edit:hover {
  background-color: #d86a03de
}

.btn-ofer {
  border: 1px solid #00000079;
  background-color: #005fcc79
}
.btn-ofer:hover {
  background-color: #0063d4cb
}

.btn-ofer-list {
  border: 1px solid #00000079;
  background-color: #02408852
}

.btn-ofer-list:hover {
  background-color: #02418898
}
.btn-cap {
  display: flex;
  margin-bottom: 20px;
  gap: 70px;
}

.header .btn {
  padding: 12px 24px;
  font-size: 16px;
  border-radius: 12px;
  font-weight: 600;
  transition: all 0.2s;
  cursor: pointer;
}

/* Стили для кнопки "Показать документ" */
.btn-pdf {
  background-color: #94a3b8; /* Серый по умолчанию */
  transition: all 0.3s ease;
  cursor: not-allowed;
  padding: 10px 20px; /* Приводим в соответствие с другими кнопками */
  border-radius: 8px;
  font-weight: 600;
}

.btn-pdf-active {
  background-color: #f1dd01 ;
  cursor: pointer;
  border: 1px solid #00000079;

}

</style>