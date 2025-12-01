# backend/wells/models.py

from django.db import models

# Создаем класс "Choices" для удобного хранения вариантов секций
class WellSection(models.TextChoices):
    DIRECTION = 'Направление', 'Направление'
    CONDUCTOR = 'Кондуктор', 'Кондуктор'
    SURFACE_CASING = 'Тех.колонна (промеж.)', 'Техническая колонна (промежуточная)'
    INTERMEDIATE_CASING = 'Экс. колонна', 'Эксплуатационная колонна'
    PRODUCTION_CASING = 'Экс. хвостовик', 'Эксплуатационный хвостовик'

class Well(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название скважины/куста")
    is_active = models.BooleanField(default=True, verbose_name="Объект в работе")
    engineers = models.TextField(verbose_name="ФИО инженеров", blank=True)
    
    current_depth = models.FloatField(default=0, verbose_name="Текущий забой (м)")
    planned_depth = models.FloatField(default=0, verbose_name="Плановый забой (м)")
    
    current_section = models.CharField(
        max_length=50,
        choices=WellSection.choices,
        default=WellSection.DIRECTION,
        verbose_name="Текущая секция"
    )
    
    current_operations = models.TextField(verbose_name="Текущие работы", blank=True)
    
    last_summary_text = models.TextField(verbose_name="Последняя сводка", blank=True, null=True)
    # has_nvp = models.BooleanField(default=False, verbose_name="Были ли НВП по нашей вине")
    # nvp_details = models.TextField(verbose_name="Информация по НВП", blank=True, null=True)
    
    has_overspending = models.BooleanField(default=False, verbose_name="Есть ли перерасход")
    overspending_details = models.TextField(verbose_name="Информация по перерасходу", blank=True, null=True)

    telegram_chat_id = models.BigIntegerField(verbose_name="Telegram Chat ID для оповещений", null=True, blank=True, help_text="ID группы, куда отправлять тревоги.")
    telegram_topic_id = models.BigIntegerField(verbose_name="Telegram Topic ID для оповещений", null=True, blank=True, help_text="ID темы (топика) внутри группы.")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Скважина"
        verbose_name_plural = "Скважины"
        ordering = ['-updated_at']


# НОВАЯ МОДЕЛЬ ДЛЯ ИНЦИДЕНТОВ НВП
class NVPIncident(models.Model):
    well = models.ForeignKey(Well, on_delete=models.CASCADE, related_name='nvp_incidents', verbose_name="Скважина")
    incident_date = models.DateField(verbose_name="Дата инцидента")
    duration = models.CharField(max_length=100, verbose_name="Потерянное время (текст)", blank=True)
    description = models.TextField(verbose_name="Описание инцидента")

    def __str__(self):
        return f"НВП на {self.well.name} от {self.incident_date}"

    class Meta:
        verbose_name = "Инцидент НВП"
        verbose_name_plural = "Инциденты НВП"
        ordering = ['-incident_date'] # Сортируем от новых к старым

class Task(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название задачи")
    customer = models.CharField(max_length=255, verbose_name="Заказчик/Контекст", blank=True)
    deadline = models.DateTimeField(verbose_name="Срок выполнения")
    
    details = models.TextField(verbose_name="Подробная информация", blank=True, null=True)
    
    is_completed = models.BooleanField(default=False, verbose_name="Выполнена")
    is_urgent = models.BooleanField(default=False, verbose_name="Срочная")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
        ordering = ['deadline'] # Сортируем по сроку выполнения


class Tender(models.Model):
    class Status(models.TextChoices):
        PENDING_UPLOAD = 'PENDING', 'К загрузке'
        TECH_SUBMITTED = 'TECH', 'Тех. часть загружена'
        COMMERCIAL_SUBMITTED = 'COMMERCIAL', 'Ком. часть загружена'
        COMMERCIAL_CONVERSATION = 'CONVERSATION', 'Переговоры по ком.части'
        WON = 'WON', 'Выигран'
        LOST = 'LOST', 'Проигран'
        ARCHIVED = 'ARCHIVED', 'В архиве'

    name = models.CharField(max_length=255, verbose_name="Наименование тендера")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING_UPLOAD,
        verbose_name="Этап"
    )
    deadline = models.DateTimeField(
        verbose_name="Срок загрузки",
        blank=True,
        null=True  # Разрешаем не указывать дедлайн для статусов, где он не нужен
    )
    notes = models.TextField(verbose_name="Пояснение", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тендер"
        verbose_name_plural = "Тендеры"
        ordering = ['-updated_at']

class MudParameterLog(models.Model):
    well = models.ForeignKey(Well, on_delete=models.CASCADE, related_name='mud_logs', verbose_name="Скважина")
    measurement_time = models.DateTimeField(auto_now_add=True, verbose_name="Время замера")
    
    # Основные параметры
    density = models.FloatField(verbose_name="Плотность (Пл)", null=True, blank=True)
    viscosity = models.FloatField(verbose_name="Условная вязкость (УВ)", null=True, blank=True)
    plastic_viscosity = models.FloatField(verbose_name="Пластическая вязкость (ПВ)", null=True, blank=True)
    yield_point = models.FloatField(verbose_name="ДНС", null=True, blank=True)
    
    # СНС (два значения)
    gel_strength_10s = models.FloatField(verbose_name="СНС (10 сек)", null=True, blank=True)
    gel_strength_10m = models.FloatField(verbose_name="СНС (10 мин)", null=True, blank=True)
    
    methylene_blue_test = models.FloatField(verbose_name="МБТ (содержание коллоидов)", null=True, blank=True)
    solid_phase_content = models.FloatField(verbose_name="Твердая фаза (ТФ)", null=True, blank=True)
    filtration = models.FloatField(verbose_name="Фильтрация (Ф)", null=True, blank=True)
    ph = models.FloatField(verbose_name="pH", null=True, blank=True)
    
    # Ионные параметры
    calcium_hardness = models.FloatField(verbose_name="Жесткость по Кальцию (Ca)", null=True, blank=True)
    chlorides = models.FloatField(verbose_name="Хлориды (CL)", null=True, blank=True)
    potassium = models.FloatField(verbose_name="Ионы Калия (K+)", null=True, blank=True)
    
    # Карбонаты
    carbonate_content = models.FloatField(verbose_name="Содержание карбоната кальция (Мел, CaCO3)", null=True, blank=True)
    
    # Щелочность (два значения)
    phenolphthalein_alkalinity = models.FloatField(verbose_name="Фенолфталеиновая щелочность (Pf, карбонатная щелочность)", null=True, blank=True)
    methyl_orange_alkalinity = models.FloatField(verbose_name="Метилоранжевая щелочность (Mf, общая щелочность)", null=True, blank=True)
    
    # Добавки
    lubricant = models.FloatField(verbose_name="Смазка", null=True, blank=True)
    
    # Флаг для будущей валидации
    is_out_of_norm = models.BooleanField(default=False, verbose_name="Выход за пределы нормы")

    # Поле для хранения необработанных/неопознанных параметров
    raw_unparsed_params = models.TextField(verbose_name="Неразобранные параметры", blank=True, null=True)

    def __str__(self):
        return f"Параметры для {self.well.name} от {self.measurement_time.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ['-measurement_time']



class DrillingProgram(models.Model):
    well = models.OneToOneField(Well, on_delete=models.CASCADE, related_name='drilling_program', verbose_name="Скважина")
    name = models.CharField(max_length=255, verbose_name="Название программы (например, 'Программа промывки от 20.10.2025')")

    def __str__(self):
        return self.name

# Модель 2: Секция внутри программы (Кондуктор, ЭК и т.д.)
class ProgramSection(models.Model):
    program = models.ForeignKey(DrillingProgram, on_delete=models.CASCADE, related_name='sections')
    # Используем наш уже существующий WellSection
    section_type = models.CharField(max_length=50, choices=WellSection.choices, verbose_name="Тип секции")

    def __str__(self):
        return f"Секция '{self.get_section_type_display()}'"




class ChemicalReagent(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Название реагента")
    description = models.TextField(verbose_name="Описание/Назначение", blank=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Химреагент"
        verbose_name_plural = "Справочник химреагентов"
        ordering = ['name']


class MudType(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Название типа раствора")
    # Связь "многие-ко-многим" с реагентами
    reagents = models.ManyToManyField(
        ChemicalReagent,
        blank=True,
        verbose_name="Состав (химреагенты)"
    )

    def __str__(self):
        return self.name
        
    class Meta:
        verbose_name = "Тип бурового раствора"
        verbose_name_plural = "Справочник типов растворов"
        ordering = ['name']
# Модель 3: "Строка" в таблице с нормами для конкретного интервала
class DepthIntervalNorms(models.Model):
    section = models.ForeignKey(ProgramSection, on_delete=models.CASCADE, related_name='intervals')
    start_depth = models.FloatField(verbose_name="Начало интервала (м)")
    end_depth = models.FloatField(verbose_name="Конец интервала (м)")
    
    mud_type = models.ForeignKey(
        MudType,
        on_delete=models.SET_NULL, # Если тип удалят, поле станет пустым
        null=True,
        blank=True,
        verbose_name="Тип раствора"
    )

    # Здесь храним все min/max. Названия полей должны совпадать с MudParameterLog
    density_min = models.FloatField(null=True, blank=True)
    density_max = models.FloatField(null=True, blank=True)
    
    viscosity_min = models.FloatField(null=True, blank=True)
    viscosity_max = models.FloatField(null=True, blank=True)
    
    plastic_viscosity_min = models.FloatField(null=True, blank=True)
    plastic_viscosity_max = models.FloatField(null=True, blank=True)

    yield_point_min = models.FloatField(null=True, blank=True)
    yield_point_max = models.FloatField(null=True, blank=True)

    gel_strength_10s_min = models.FloatField(null=True, blank=True)
    gel_strength_10s_max = models.FloatField(null=True, blank=True)

    gel_strength_10m_min = models.FloatField(null=True, blank=True)
    gel_strength_10m_max = models.FloatField(null=True, blank=True)

    methylene_blue_test_min = models.FloatField(null=True, blank=True)
    methylene_blue_test_max = models.FloatField(null=True, blank=True)

    solid_phase_content_min = models.FloatField(null=True, blank=True)
    solid_phase_content_max = models.FloatField(null=True, blank=True)

    filtration_min = models.FloatField(null=True, blank=True)
    filtration_max = models.FloatField(null=True, blank=True)

    ph_min = models.FloatField(null=True, blank=True)
    ph_max = models.FloatField(null=True, blank=True)

    calcium_hardness_min = models.FloatField(null=True, blank=True)
    calcium_hardness_max = models.FloatField(null=True, blank=True)

    chlorides_min = models.FloatField(null=True, blank=True)
    chlorides_max = models.FloatField(null=True, blank=True)

    potassium_min = models.FloatField(null=True, blank=True)
    potassium_max = models.FloatField(null=True, blank=True)

    carbonate_content_min = models.FloatField(null=True, blank=True)
    carbonate_content_max = models.FloatField(null=True, blank=True)

    phenolphthalein_alkalinity_min = models.FloatField(null=True, blank=True)
    phenolphthalein_alkalinity_max = models.FloatField(null=True, blank=True)

    methyl_orange_alkalinity_min = models.FloatField(null=True, blank=True)
    methyl_orange_alkalinity_max = models.FloatField(null=True, blank=True)

    lubricant_min = models.FloatField(null=True, blank=True)
    lubricant_max = models.FloatField(null=True, blank=True)


    def __str__(self):
        return f"Интервал {self.start_depth}м - {self.end_depth}м"

