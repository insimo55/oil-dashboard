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
    
    # has_nvp = models.BooleanField(default=False, verbose_name="Были ли НВП по нашей вине")
    # nvp_details = models.TextField(verbose_name="Информация по НВП", blank=True, null=True)
    
    has_overspending = models.BooleanField(default=False, verbose_name="Есть ли перерасход")
    overspending_details = models.TextField(verbose_name="Информация по перерасходу", blank=True, null=True)

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