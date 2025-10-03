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
    
    has_nvp = models.BooleanField(default=False, verbose_name="Были ли НВП по нашей вине")
    nvp_details = models.TextField(verbose_name="Информация по НВП", blank=True, null=True)
    
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

class Task(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название задачи")
    customer = models.CharField(max_length=255, verbose_name="Заказчик/Контекст", blank=True)
    deadline = models.DateTimeField(verbose_name="Срок выполнения")
    
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