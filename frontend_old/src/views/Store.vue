<script setup>
import { ref, onMounted, warn, watch, computed } from 'vue'
import CircleChart from '../components/store/CircleChart.vue'
import BarChart from '../components/store/BarChart.vue'
import { AgGridVue } from 'ag-grid-vue3'
import WorkshopCharts from '../components/store/WorkshopCharts.vue'
import ImageTooltip from '../components/ImageTooltip.vue'
import InventoryModal from '../components/store/InventoryModal.vue'
import OrderModal from '../components/store/OrderModal.vue'
import PdfModal from '../components/store/PdfModal.vue'
import OrderList from '../components/store/OrderList.vue'
import { useI18n } from 'vue-i18n'
import {isOrderList} from '../components/store/Const'


const { t } = useI18n()

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
const rowData = ref([...projectsByDepartment])
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



const onCellValueChanged = (event) => {
  event.api.redrawRows({ rowNodes: [event.node] });
};


const onGridReady = (params) => {
  gridApi.value = params.api;
};

const getRowId = (params) => params.data.Number; 
const handleAddItem = (item) => {
  // Добавляем в массив для реактивности
  rowData.value = [...rowData.value, item];
  
  // Принудительно добавляем строку через API для мгновенного отображения
  gridApi.value?.applyTransaction({ add: [item] });
};



const handleOrderSubmit = (orderData) => {
  console.log('Заказ оформлен:', orderData);
  
  // Находим объект в нашем реактивном массиве
  const itemIndex = rowData.value.findIndex(i => i.Article === orderData.selectedProduct);
  
  if (itemIndex !== -1) {
    // 1. Обновляем данные в массиве (создаем копию объекта для реактивности)
    const updatedItem = { ...rowData.value[itemIndex] };
    updatedItem.count = Number(updatedItem.count) - Number(orderData.count);
    
    // 2. Заменяем в массиве
    rowData.value[itemIndex] = updatedItem;

    // 3. Уведомляем AG Grid об изменениях через транзакцию (самый безопасный способ)
    gridApi.value?.applyTransaction({ update: [updatedItem] });

    // 4. Принудительно обновляем стили строк (чтобы сработал красный фон)
    gridApi.value?.redrawRows();
  }
  gridApi.value?.applyColumnState({
    defaultState: { sort: null } // сброс (опционально)
    });
  gridApi.value?.onSortChanged();
};


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
  <div v-if="isOrderList==false">

  <div class="manager-dashboard">
    <div class="header">
      <h2>{{ $t('store.title') }}</h2>
      <div class="header-actions">
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
        
        <button class="btn btn-ofer-list" @click="isOrderList = true" >{{ $t('store.OrderList') }}</button>

      </div>
    </div>
    <div class="btn-cap">
      <!-- <button class="btn btn-edit" @click="addRow" >Редактировать</button> -->
    </div>


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
        @grid-ready="onGridReady"
        @selection-changed="onSelectionChanged"
        @cell-double-clicked="onCellDoubleClicked"
        @cell-value-changed="onCellValueChanged"
      />
    </div>
  </div>
    <PdfModal 
      v-model="isPdfModalOpen" 
      :pdfUrl="selectedPdfUrl"
      :isEditMode="isEditPdfMode"
      @update-pdf="handleAttachPdf"
      @update:modelValue="(val) => { if(!val) isEditPdfMode = false }" 
/>
    </div>
  <OrderList v-if="isOrderList === true" />
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
  height: 100px;
  border-radius: 30px;
  background-color: #fff;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  border: 1px solid #eef0f2;
  margin-bottom: 20px;
}

.header h2 {
  margin: 0;
  font-size: 28px;
  color: #1e293b;
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