import { ref, computed } from 'vue'

export const useDashboardStore = () => {
  // Данные из бэкенда
  const workshops = ref([
    {
      id: 1,
      name: 'Стационарный КРДО «РЕДИКОМ»',
      workload: 85,
      sections: [
        { id: 101, name: 'Участок ремонта цифровых сменных элементов РЭА', workload: 90, capacity: 100, currentLoad: 60 },
        { id: 102, name: 'Участок ремонта цифроаналоговых, аналоговых и высокочастотных сменных элементов РЭА', workload: 80, capacity: 100, currentLoad: 80 },
        { id: 103, name: 'Участок ремонта источников вторичного питания РЭА', workload: 80, capacity: 100, currentLoad: 80 },
        { id: 104, name: 'Участок ремонта СВЧ аппаратуры', workload: 85, capacity: 100, currentLoad: 85 }
      ],
      warehouse: {
        id: 1001,
        name: 'Мобильный ремонтно-диагностический комплекс РДК-1',
        capacity: 1000,
        currentStock: 750,
        materials: [
          { id: 1, name: 'Коммутатор ZELAX ZES-2028GPS-AC220', quantity: 1, unit: 'шт' },
          { id: 2, name: 'Шкаф', quantity: 5, unit: 'шт' },
          { id: 3, name: 'Латунь пруток', quantity: 250, unit: 'кг' }
        ]
      },
      color: '#4CAF50'
    },
    {
      id: 2,
      name: 'ТЦР ремонта гидравлических систем ЗРК «Бук-М2Э»',
      workload: 65,
      sections: [
        { id: 201, name: 'Участок дефектации, разборки, сборки и настройки', workload: 70, capacity: 100, currentLoad: 70 },
        { id: 202, name: 'Участок сборки, испытаний гидравлических частей и цилиндров', workload: 60, capacity: 80, currentLoad: 48 },
        { id: 203, name: 'Участок ремонта, изготовления трубопроводов и проверки на герметичность', workload: 60, capacity: 80, currentLoad: 48 },
        { id: 204, name: 'Слесарный участок', workload: 60, capacity: 80, currentLoad: 48 },
        { id: 205, name: 'Участок испытания привода вращения', workload: 65, capacity: 100, currentLoad: 65 },
        { id: 206, name: 'Участок ремонта, настройки гидроцилиндров и гидравлических замков', workload: 65, capacity: 100, currentLoad: 65 }
      ],
      warehouse: {
        id: 1002,
        name: 'Склад комплектующих',
        capacity: 800,
        currentStock: 520,
        materials: [
          { id: 4, name: 'Подшипники', quantity: 1500, unit: 'шт' },
          { id: 5, name: 'Болты М8', quantity: 8000, unit: 'шт' },
          { id: 6, name: 'Гайки М8', quantity: 8500, unit: 'шт' }
        ]
      },
      color: '#2196F3'
    },
    {
      id: 3,
      name: 'ТЦР ремонта СЧ изделий 9И56, 9И56-8, 9И112М2, 9И113М2, 9И114М2',
      workload: 45,
      sections: [
        { id: 301, name: 'Подготовка Участок', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 302, name: 'Участок дефектации', workload: 40, capacity: 100, currentLoad: 40 },
        { id: 303, name: 'Участок разборки', workload: 40, capacity: 100, currentLoad: 40 },
        { id: 304, name: 'Участок входного контроля подшипниковой заготовки', workload: 40, capacity: 100, currentLoad: 40 },
        { id: 305, name: 'Слесарный участок', workload: 40, capacity: 100, currentLoad: 40 },
        { id: 306, name: 'Участок механической обработки', workload: 40, capacity: 100, currentLoad: 40 },
        { id: 307, name: 'Участок балансировки', workload: 40, capacity: 100, currentLoad: 40 },
        { id: 308, name: 'Участок съёма металла при балансировке', workload: 40, capacity: 100, currentLoad: 40 },
        { id: 309, name: 'Участок доводки и притирки', workload: 40, capacity: 100, currentLoad: 40 },
        { id: 310, name: 'Участок сварки и пайки', workload: 40, capacity: 100, currentLoad: 40 },
        { id: 311, name: 'Участок ремонта топливорегулирующей аппаратуры (ТРА)', workload: 40, capacity: 100, currentLoad: 40 },
        { id: 312, name: 'Участок общей сборки', workload: 40, capacity: 100, currentLoad: 40 },
        { id: 313, name: 'Участок контроля', workload: 40, capacity: 100, currentLoad: 40 },
        { id: 314, name: 'Участок контроля электроблоков и ремонта кабелей', workload: 40, capacity: 100, currentLoad: 40 },
        { id: 315, name: 'Участок специальных испытаний после доводки', workload: 40, capacity: 100, currentLoad: 40 },
        { id: 316, name: 'Участок выдачи из ремонта', workload: 40, capacity: 100, currentLoad: 40 },
        { id: 317, name: 'Диспетчерская', workload: 45, capacity: 100, currentLoad: 45 }
      ],
      warehouse: {
        id: 1003,
        name: 'Склад ЛКМ',
        capacity: 500,
        currentStock: 280,
        materials: [
          { id: 7, name: 'Краска грунт', quantity: 120, unit: 'л' },
          { id: 8, name: 'Эмаль', quantity: 100, unit: 'л' },
          { id: 9, name: 'Растворитель', quantity: 60, unit: 'л' }
        ]
      },
      color: '#FF9800'
    },
    {
      id: 4,
      name: 'ТЦР дизельных двигателей',
      workload: 45,
      sections: [
        { id: 401, name: 'Пост приема в ремонт', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 402, name: 'Пост дефектации двигателя', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 403, name: 'Пост разборки двигателя', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 404, name: 'Пост ремонта навесного оборудования', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 405, name: 'Пост ремонта электрооборудования', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 406, name: 'Пост ремонта топливной аппаратуры', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 407, name: 'Пост устранения дефектов', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 408, name: 'Участок подкрашивания ДВС', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 409, name: 'Участок ремонта шатуно-поршневой группы', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 410, name: 'Участок ремонта клапанов', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 411, name: 'Участок ремонта ГБЦ и рубашки охлаждения', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 412, name: 'Участок ремонта картера и БЦ', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 413, name: 'Участок ремонта валов', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 414, name: 'Пост сборки двигателя', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 415, name: 'Пост комплектации', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 416, name: 'Участок сдачи блоков и узлов ОТК', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 417, name: 'Инструментальная', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 418, name: 'Диспетчерская', workload: 50, capacity: 100, currentLoad: 50 },
      ],
      warehouse: {
        id: 1004,
        name: 'Склад ЛКМ',
        capacity: 500,
        currentStock: 280,
        materials: [
          { id: 7, name: 'Краска грунт', quantity: 120, unit: 'л' },
        ]
      },
      color: '#FF9800'
    },
    {
      id: 5,
      name: 'ТЦР ремонта модуля разведки и управления 9С932-1 и ЗСУ-23-4М4 «Шилка-М4»',
      workload: 90,
      sections: [   
        { id: 501, name: 'Участок диагностики изделия', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 502, name: 'Площадка для размещения подвижного оборудования', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 503, name: 'Участок ремонта изделия', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 504, name: 'Слесарно-сборочный участок', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 505, name: 'Электромонтажный участок #1', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 506, name: 'Электромонтажный участок #2', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 507, name: 'Слесарный участок', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 508, name: 'Инженерный участок', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 509, name: 'Участок настроечно-регулировочных работ', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 510, name: 'Участок ремонта мачт и кондиционеров', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 511, name: 'Участок проверки, сборки, ремонта и настройки блоков', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 512, name: 'Командный пункт', workload: 50, capacity: 100, currentLoad: 50 },    
      ],
      warehouse: {
        id: 1005,
        name: 'Склад ЛКМ',
        capacity: 500,
        currentStock: 280,
        materials: [
          { id: 7, name: 'Краска грунт', quantity: 120, unit: 'л' },
        ]
      },
      color: '#FF9800'
    },
    {
      id: 6,
      name: 'ТЦР ремонта шасси ЗРК «Тор-М1», ЗРК «Тор-М2Э», ЗРК «Бук-М2Э», ЗРК «Антей-2500», МРУ-Б',
      workload: 45,
      sections: [
        { id: 601, name: 'Участок дефектации, разборки-сборки и испытаний ГМ, Мт-Лбу (5 зон и площадок)', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 602, name: 'Участок дефектации, разборки-сборки и испытаний СГШ(4 зоны и площадки)', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 603, name: 'Участок обслуживания АКБ', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 604, name: 'Участок ремонта узлов СГШ', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 605, name: 'Участок заправки баллов ППО', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 606, name: 'Слесарно-сборочный участок', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 607, name: 'Участок ремонта узлов шасси МТ-Лбу', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 608, name: 'Участок испытания электрооборудования, проверки жгутов, ремонта блока управления ГМТ, щитка двигателя', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 609, name: 'Участок испытаний топливных баков и радиаторов', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 610, name: 'Участок испытаний (боксы 1-3)', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 611, name: 'Сварочный участок', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 612, name: 'Участок сдачи готовой продукции', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 613, name: 'Кладовая приспособлений инструмента, участок хранения ЗИП', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 614, name: 'Зоны хранения крупногабаритного ЗИП (2 зоны)', workload: 50, capacity: 100, currentLoad: 50 },
      ],
      warehouse: {
        id: 1006,
        name: 'Кладовая приспособлений инструмента, участок хранения ЗИП',
        capacity: 500,
        currentStock: 280,
        materials: [
          { id: 7, name: 'Краска грунт', quantity: 120, unit: 'л' },
        ]
      },
      color: '#FF9800'
    },
    {
      id: 7,
      name: 'ТЦР ремонта шасси ЗРК «Тор-М1», ЗРК «Тор-М2Э», ЗРК «Бук-М2Э», ЗРК «Антей-2500», МРУ-Б',
      workload: 75,
      sections: [
        { id: 701, name: 'Пост приема в ремонт', workload: 65, capacity: 100, currentLoad: 50 },
        { id: 702, name: 'Пост дефектации двигателя', workload: 70, capacity: 100, currentLoad: 50 },
        { id: 703, name: 'Пост разборки двигателя', workload: 80, capacity: 100, currentLoad: 50 },
        { id: 704, name: 'Пост ремонта навесного оборудования', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 705, name: 'Пост ремонта электрооборудования', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 706, name: 'Пост ремонта топливной аппаратуры', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 707, name: 'Пост устранения дефектов', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 708, name: 'Участок подкрашивания ДВС', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 709, name: 'Участок ремонта шатуно-поршневой группы', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 710, name: 'Участок ремонта клапанов', workload: 40, capacity: 100, currentLoad: 50 },
        { id: 711, name: 'Участок ремонта ГБЦ и рубашки охлаждения', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 712, name: 'Участок ремонта картера и БЦ', workload: 80, capacity: 100, currentLoad: 50 },
        { id: 713, name: 'Участок ремонта валов', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 714, name: 'Пост сборки двигателя', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 715, name: 'Пост комплектации', workload: 30, capacity: 100, currentLoad: 50 },
        { id: 716, name: 'Участок сдачи блоков и узлов ОТК', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 717, name: 'Инструментальная', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 718, name: 'Диспетчерская', workload: 50, capacity: 100, currentLoad: 50 },
      ],
      warehouse: {
        id: 1007,
        name: 'Склад ЛКМ',
        capacity: 500,
        currentStock: 280,
        materials: [
          { id: 7, name: 'Краска грунт', quantity: 120, unit: 'л' },
        ]
      },
      color: '#FF9800'
    },
    {
      id: 8,
      name: 'ТЦР ремонта ЗРК «Тор-М2Э»',
      workload: 45,
      sections: [
        { id: 801, name: 'Участок сборки-разборки изделий', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 802, name: 'Участок диагностики и ремонта антенного поста', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 803, name: 'Участок диагностики и ремонта электронных и электромеханических блоков', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 804, name: 'Участок диагностики и ремонта цифровых, высокочастотных и аналоговых панелей', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 805, name: 'Электромонтажный участок для ремонта блоков и жгутов', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 806, name: 'Химическая лаборатория', workload: 70, capacity: 100, currentLoad: 50 },
        { id: 807, name: 'Камера окраски (агрегатное помещение)', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 808, name: 'Камера дождевания (агрегатное помещение)', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 809, name: 'Отделение подкраски корпусов, блоков, панелей', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 810, name: 'Склад ЛВЖ', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 811, name: 'Склад химических материалов', workload: 80, capacity: 100, currentLoad: 50 },
        { id: 812, name: 'Кладовая инструментов и приспособлений', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 813, name: 'Кладовая средств измерений', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 814, name: 'Склад узлов, блоков, комплектующих изделий', workload: 40, capacity: 100, currentLoad: 50 },
        { id: 815, name: 'Кладовая материалов и малогабаритного ЗИП', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 816, name: 'Административные помещения (4 помещения)', workload: 30, capacity: 100, currentLoad: 50 },
      ],
      warehouse: {
        id: 1008,
        name: 'Склад ЛКМ',
        capacity: 500,
        currentStock: 280,
        materials: [
          { id: 7, name: 'Краска грунт', quantity: 120, unit: 'л' },
        ]
      },
      color: '#FF9800'
    },
    {
      id: 9,
      name: 'ТЦР ремонта изделий 9М82МДЭ, 9М83МЭ, 9М317',
      workload: 65,
      sections: [
        { id: 901, name: 'Участок дефектации, разборки, сборки и контроля изделий', workload: 30, capacity: 100, currentLoad: 50 },
        { id: 902, name: 'Участок мелкой сборки (в том числе снаряжения/расснаряжения изделий)', workload: 20, capacity: 100, currentLoad: 50 },
        { id: 903, name: 'Участок упаковки изделий и составных частей', workload: 40, capacity: 100, currentLoad: 50 },
        { id: 904, name: 'Участок выполнения ремонтных работ', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 905, name: 'Участок проверки бортовой аппаратуры до и после ремонта', workload: 70, capacity: 100, currentLoad: 50 },
        { id: 906, name: 'Участок испытания на герметичность', workload: 60, capacity: 100, currentLoad: 50 },
        { id: 907, name: 'Участок входного контроля, дефектации и проверки', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 908, name: 'Участок технической документации', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 909, name: 'Склад инструмента и приспособлений', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 910, name: 'Участок хранения оснастки, инструмента и приспособлений', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 911, name: 'Склад (участок) хранения изделий до и после ремонта', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 912, name: 'Склад готовых изделий (запасных частей)', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 913, name: 'Склад ЗИП-Р', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 914, name: 'Склад ЛКП и ЛВЖ', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 915, name: 'Склад хранения забракованных комплектующих, пироэлементов, из состава ЗУР', workload: 50, capacity: 100, currentLoad: 50 },
        { id: 916, name: 'Командный пункт', workload: 50, capacity: 100, currentLoad: 50 },
      ],
      warehouse: {
        id: 1009,
        name: 'Склад ЛКМ',
        capacity: 500,
        currentStock: 280,
        materials: [
          { id: 7, name: 'Краска грунт', quantity: 120, unit: 'л' },
        ]
      },
      color: '#FF9800'
    },
  ])

  const equipment = ref([
    { id: 1001, name: 'Токарный станок ЧПУ', type: 'Станок', workshopId: 1, sectionId: 101, status: 'operational', maintenanceStart: '2024-01-15', maintenanceEnd: '2024-01-20', workload: 95, lastService: '2023-12-15', nextService: '2024-02-15' },
    { id: 1002, name: 'Фрезерный станок', type: 'Станок', workshopId: 1, sectionId: 102, status: 'maintenance', maintenanceStart: '2024-01-10', maintenanceEnd: '2024-01-25', workload: 75, lastService: '2023-12-20', nextService: '2024-02-20' },
    { id: 1003, name: 'Шлифовальный станок', type: 'Станок', workshopId: 1, sectionId: 103, status: 'repair', maintenanceStart: '2024-01-05', maintenanceEnd: '2024-01-30', workload: 85, lastService: '2023-12-10', nextService: '2024-02-10' },
    { id: 2001, name: 'Конвейерная линия', type: 'Конвейер', workshopId: 2, sectionId: 201, status: 'operational', maintenanceStart: '2024-02-01', maintenanceEnd: '2024-02-05', workload: 60, lastService: '2023-12-25', nextService: '2024-03-01' },
    { id: 2002, name: 'Робот-сборщик', type: 'Робот', workshopId: 2, sectionId: 201, status: 'idle', maintenanceStart: '2024-01-25', maintenanceEnd: '2024-02-05', workload: 40, lastService: '2023-12-30', nextService: '2024-02-28' },
    { id: 3001, name: 'Покрасочная камера', type: 'Камера', workshopId: 3, sectionId: 302, status: 'operational', maintenanceStart: '2024-02-10', maintenanceEnd: '2024-02-15', workload: 50, lastService: '2024-01-05', nextService: '2024-03-10' },
  ])

  const maintenanceTasks = ref([
    { id: 1, equipmentId: 1002, equipmentName: 'Фрезерный станок', workshopId: 1, type: 'preventive', startDate: '2024-01-10', endDate: '2024-01-25', duration: 15, status: 'in-progress', assignedTo: 'Иванов А.П.' },
    { id: 2, equipmentId: 1003, equipmentName: 'Шлифовальный станок', workshopId: 1, type: 'emergency', startDate: '2024-01-05', endDate: '2024-01-30', duration: 25, status: 'in-progress', assignedTo: 'Петров С.И.' },
    { id: 3, equipmentId: 2002, equipmentName: 'Робот-сборщик', workshopId: 2, type: 'scheduled', startDate: '2024-01-25', endDate: '2024-02-05', duration: 11, status: 'planned', assignedTo: 'Сидоров В.М.' },
    { id: 4, equipmentId: 3001, equipmentName: 'Покрасочная камера', workshopId: 3, type: 'preventive', startDate: '2024-02-10', endDate: '2024-02-15', duration: 5, status: 'planned', assignedTo: 'Кузнецов А.В.' },
  ])

  // Выбранный цех для деталей
  const selectedWorkshop = ref(null)

  // Компьютед свойства
  const totalWorkload = computed(() => {
    return workshops.value.reduce((sum, workshop) => sum + workshop.workload, 0) / workshops.value.length
  })

  const equipmentByWorkshop = computed(() => {
    const map = new Map()
    equipment.value.forEach(item => {
      if (!map.has(item.workshopId)) {
        map.set(item.workshopId, [])
      }
      map.get(item.workshopId).push(item)
    })
    return map
  })

  // Методы
  const getColorForWorkload = (workload) => {
    if (workload >= 80) return '#f44336'
    if (workload >= 60) return '#ff9800'
    if (workload >= 40) return '#4CAF50'
    return '#2196F3'
  }

  const selectWorkshop = (workshop) => {
    selectedWorkshop.value = workshop
  }

  const getWorkshopEquipment = (workshopId) => {
    return equipment.value.filter(eq => eq.workshopId === workshopId)
  }

  const getWorkshopTasks = (workshopId) => {
    return maintenanceTasks.value.filter(task => task.workshopId === workshopId)
  }

  return {
    workshops,
    equipment,
    maintenanceTasks,
    selectedWorkshop,
    totalWorkload,
    equipmentByWorkshop,
    
    getColorForWorkload,
    selectWorkshop,
    getWorkshopEquipment,
    getWorkshopTasks
  }
}