<script setup>
import { computed, ref } from 'vue';
import { AgGridVue } from 'ag-grid-vue3';
import PdfModal from './PdfModal.vue'; 
import { useI18n } from 'vue-i18n'
import {isOrderList} from './Const'
import { onMounted } from 'vue';


const STORAGE_KEY_DATA = 'savedOrdersJSON';
const STORAGE_KEY_PDF = 'savedOrdersWithPDF';
// --- Переменные состояния ---
const gridApi = ref(null);
const selectedPdfUrl = ref(null); 
const isPdfModalOpen = ref(false);
const isEditPdfMode = ref(false);
const isRowSelected = ref(false);
const isAddModalOpen = ref(false); // Для модалки добавления
const { t } = useI18n()

// --- Данные для таблицы (Замените своими данными) ---
const rowData = ref([]);

// --- Настройки AG Grid ---

const defaultColDef = {
  flex: 1,
  minWidth: 100,
  sortable: true,
  filter: true,
  wrapText: true,
  autoHeight: false,
};

const columnDefs = computed(() => [
  { headerName: t('orderList.columns.id'), field: "id", width: 70 },
  { headerName: t('orderList.columns.reason'), field: "reason" },
  
  { headerName: t('orderList.columns.FIO'), field: "FIO" },
  { headerName: t('orderList.columns.position'), field: "position" },
  { headerName: t('orderList.columns.data'), field: "date" },
  
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
  { 
    headerName: t('orderList.columns.quantity'), 
    field: "quantity", 
    cellClass: 'grid-cell-centered', 
    type: 'numericColumn'
  },
  
  {
    headerName: t('documents.columns.actions'),
    width: 100,
    lockPosition: 'right', // Закрепляем справа
    cellClass: 'grid-cell-centered',
    cellRenderer: (params) => {
      const button = document.createElement('button');
      button.innerText = t('documents.delete');
      button.classList.add('btn', 'btn-delete-row'); // Используем стили кнопок
      
      // При клике вызываем нашу функцию удаления, передавая ID строки
      button.addEventListener('click', () => {
        if (confirm(`Вы уверены, что хотите удалить заявку №${params.data.id}?`)) {
          deleteDocument(params.data.id);
        }
      });
      
      return button;
    }
  },
]);

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

// --- Функции-обработчики ---

const onGridReady = (params) => {
  gridApi.value = params.api;
};

const getRowId = (params) => params.data.id; 

const onSelectionChanged = (event) => {
  const selectedNodes = event.api.getSelectedNodes();
  isRowSelected.value = selectedNodes.length > 0;

  if (isRowSelected.value) {
    const data = selectedNodes[0].data;
    if (data.pdfUrl && data.pdfUrl.trim().length > 0) {
      selectedPdfUrl.value = data.pdfUrl;
    } else {
      selectedPdfUrl.value = null;
    }
  } else {
    selectedPdfUrl.value = null;
  }
};

const handleAttachPdf = (newUrl) => {
  const selectedNodes = gridApi.value.getSelectedNodes();
  
  if (selectedNodes.length > 0) {
    const selectedNode = selectedNodes[0]; // Берем первый (единственный) выбранный узел
    
    // Создаем НОВЫЙ объект данных на основе существующего, меняем только URL
    const updatedData = { ...selectedNode.data, pdfUrl: newUrl };
    
    // 1. Обновляем данные в реактивном массиве Vue (это для реактивности вне AG Grid)
    // Убедитесь, что rowData — это ref([...])
    const index = rowData.value.findIndex(i => i.id === updatedData.id);
    if (index !== -1) {
      rowData.value.splice(index, 1, updatedData);
    }
    
    // 2. Уведомляем AG Grid об обновлении, передавая НОВЫЙ объект данных.
    // Благодаря функции getRowId (которая использует ID), AG Grid понимает, что это UPDATE, а не ADD.
    gridApi.value.applyTransaction({ update: [updatedData] });

    // Обновляем выбранный URL для кнопки "Просмотр"
    selectedPdfUrl.value = newUrl;
    isEditPdfMode.value = false; // Закрываем модалку в режиме просмотра
  }
};

const openAttachModal = () => {
  isEditPdfMode.value = true;
  isPdfModalOpen.value = true;
};

// Функция добавления нового документа (если используете DocumentAddModal)

const handleAddNewDocument = (newDoc) => {
  const id = rowData.value.length > 0 ? Math.max(...rowData.value.map(d => d.id)) + 1 : 1;
  const docWithId = { ...newDoc, id };
  rowData.value = [...rowData.value, docWithId];
  gridApi.value?.applyTransaction({ add: [docWithId] });
};


const deleteDocument = (id) => {
  // В нашем случае id — это и есть requestNumber (мы присвоили его в loadDataFromStorage)
  const requestNumberToDelete = id;

  // 1. Удаление из визуальной части (Vue и AG Grid)
  const itemToDelete = rowData.value.find(item => item.id === requestNumberToDelete);
  if (itemToDelete) {
    // Обновляем реактивный массив
    rowData.value = rowData.value.filter(item => item.id !== requestNumberToDelete);
    // Уведомляем сетку
    gridApi.value?.applyTransaction({ remove: [itemToDelete] });
  }

  // 2. Удаление из LocalStorage
  try {
    // Чистим основной файл с данными
    const orders = JSON.parse(localStorage.getItem(STORAGE_KEY_DATA) || '[]');
    const filteredOrders = orders.filter(order => order.requestNumber !== requestNumberToDelete);
    localStorage.setItem(STORAGE_KEY_DATA, JSON.stringify(filteredOrders));

    // Чистим файл с PDF
    const pdfs = JSON.parse(localStorage.getItem(STORAGE_KEY_PDF) || '[]');
    const filteredPdfs = pdfs.filter(p => p.requestNumber !== requestNumberToDelete);
    localStorage.setItem(STORAGE_KEY_PDF, JSON.stringify(filteredPdfs));

    console.log(`Заявка ${requestNumberToDelete} удалена из системы и хранилища.`);
  } catch (e) {
    console.error("Ошибка при удалении из localStorage:", e);
  }

  // 3. Сбрасываем состояние выбора, если удалили активную строку
  if (selectedPdfUrl.value && itemToDelete?.pdfUrl === selectedPdfUrl.value) {
    selectedPdfUrl.value = null;
    isRowSelected.value = false;
  }
};

const onCellDoubleClicked = (params) => {
  // Проверяем, что клик был по колонке "pdfUrl" И что у этой строки есть ссылка
  if (params.colDef.field === 'pdfUrl' && params.value) {
    selectedPdfUrl.value = params.value;
    isEditPdfMode.value = false; // Убеждаемся, что открываем в режиме просмотра, а не редактирования
    isPdfModalOpen.value = true;
  }
};


onMounted(() => {
  loadDataFromStorage();
});

const loadDataFromStorage = () => {
  try {
    const rawData = JSON.parse(localStorage.getItem(STORAGE_KEY_DATA) || '[]');
    const rawPdfs = JSON.parse(localStorage.getItem(STORAGE_KEY_PDF) || '[]');

    // Обрабатываем первый файл и подтягиваем PDF из второго
    const mergedData = rawData.map(order => {
      // 1. Ищем PDF по совпадающему requestNumber
      const pdfEntry = rawPdfs.find(p => p.requestNumber === order.requestNumber);
      
      // 2. Считаем общее количество (quantity) всех позиций в заказе
      const totalQuantity = Array.isArray(order.items) 
        ? order.items.reduce((sum, item) => sum + (Number(item.quantity) || 0), 0)
        : 0;

      return {
        id: order.requestNumber, // ID для AG Grid
        reason: order.reason,
        FIO: order.requesterName,
        position: order.requesterPosition,
        date: order.requestDate,
        quantity: totalQuantity, // Сумма всех quantity из items
        pdfUrl: pdfEntry ? pdfEntry.pdfBase64 : null, // Приклеиваем PDF
        note: order.partTypes
      };
    });

    // Загружаем результат в таблицу
    rowData.value = mergedData;

  } catch (e) {
    console.error("Ошибка парсинга данных из Storage:", e);
  }
};

// Функция открытия (вызывается из кнопки "Просмотр документа")
const openPdf = () => {
  if (!selectedPdfUrl.value) return;

  try {
    // Очистка строки от префикса, если он есть
    const base64Clean = selectedPdfUrl.value.includes(',') 
      ? selectedPdfUrl.value.split(',')[1] 
      : selectedPdfUrl.value;

    const byteCharacters = atob(base64Clean);
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const blob = new Blob([new Uint8Array(byteNumbers)], { type: 'application/pdf' });
    const url = URL.createObjectURL(blob);
    window.open(url, '_blank');
  } catch (e) {
    alert("Не удалось открыть PDF: данные повреждены или имеют неверный формат.");
  }
};
</script>

<template>
  <div class="manager-dashboard">
    <div class="header">
      <h2>{{ $t('orderList.title') }}</h2>
      <div class="header-actions">      
                  <button 
            class="btn btn-pdf" 
            :class="{ 'btn-pdf-active': selectedPdfUrl }" 
            :disabled="!selectedPdfUrl" 
            @click="openPdf"
          >
          {{ $t('orderList.view') }}
        </button>
  
        <!-- <button class="btn btn-ofer" :class="{ 'btn-pdf-active': isRowSelected }" :disabled="!isRowSelected" @click="openAttachModal">
          {{ $t('documents.attachChange') }}
        </button> -->

        <button class="btn btn-ofer-list" @click="isOrderList = false" >{{ $t('orderList.StoreZIP') }}</button>
      </div>
    </div>

    <div class="ag-grid-wrapper">
      <ag-grid-vue
        class="ag-theme-alpine"
        :rowData="rowData"
        :columnDefs="columnDefs"
        :defaultColDef="defaultColDef"
        :suppressCellFocus="true"
        :stopEditingWhenCellsLoseFocus= "true"
        rowSelection="single"
        @selection-changed="onSelectionChanged"
        @grid-ready="onGridReady"
        @cell-double-clicked="onCellDoubleClicked"
        :getRowId="getRowId"
        style="height: 78vh; width: 100%;"
        :pagination="true"
        :paginationPageSize="15"
        :tooltipShowDelay="100" 
        :paginationPageSizeSelector="[5, 10, 25, 50]"
        :localeText="localeRu"
      />
    </div>

    <PdfModal 
      v-model="isPdfModalOpen" 
      :pdfUrl="selectedPdfUrl"
      :isEditMode="isEditPdfMode"
      @update-pdf="handleAttachPdf"
      @update:modelValue="(val) => { if(!val) isEditPdfMode = false }" 
    />

    <DocumentAddModal v-model="isAddModalOpen" @add="handleAddNewDocument" />
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
  background-color: #005fcc98
}
.btn-ofer:hover {
  background-color: #0063d4cb
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
  background-color: #f1dd01 ; /* Ярко-красный (горит) */
  cursor: pointer;
  border: 1px solid #00000079;

}

.btn-delete-row {
  background-color: #ef4444; /* Красный цвет */
  color: white;
  padding: 6px 10px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 12px;
  border: none;
}

.btn-delete-row:hover {
    background-color: #dc2626;
}


.btn-ofer-list {
  border: 1px solid #00000079;
  background-color: #02408852
}

.btn-ofer-list:hover {
  background-color: #02418898
}
</style>