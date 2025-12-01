from django.contrib import admin
# ИМПОРТИРУЕМ КЛАССЫ ИЗ NESTED_ADMIN
from django.urls import reverse
from django.utils.html import format_html
import nested_admin

from .models import Well, Task, NVPIncident, Tender, MudParameterLog, DrillingProgram, ProgramSection, DepthIntervalNorms,ChemicalReagent, MudType

@admin.register(ChemicalReagent)
class ChemicalReagentAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

# Регистрируем справочник типов растворов
@admin.register(MudType)
class MudTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    # Используем удобный виджет для выбора реагентов
    filter_horizontal = ('reagents',)


# --- Инлайны для Программы Промывки ---
# Используем nested_admin.NestedTabularInline
class DepthIntervalNormsInline(nested_admin.NestedTabularInline):
    model = DepthIntervalNorms
    extra = 1
    fields = (
        ('start_depth', 'end_depth'),
        'mud_type',('density_min', 'density_max'), ('viscosity_min','viscosity_max'),('plastic_viscosity_min','plastic_viscosity_max'),('yield_point_min','yield_point_max'),('gel_strength_10s_min','gel_strength_10s_max'),('gel_strength_10m_min','gel_strength_10m_max'),('methylene_blue_test_min','methylene_blue_test_max'),('solid_phase_content_min','solid_phase_content_max'),('filtration_min','filtration_max'),('ph_min','ph_max'),('calcium_hardness_min','calcium_hardness_max'),('chlorides_min','chlorides_max'),('potassium_min','potassium_max'),('carbonate_content_min','carbonate_content_max'),('phenolphthalein_alkalinity_min','phenolphthalein_alkalinity_max'),('methyl_orange_alkalinity_min','methyl_orange_alkalinity_max'),('lubricant_min','lubricant_max')
    )

class ProgramSectionInline(nested_admin.NestedTabularInline):
    model = ProgramSection
    extra = 1
    # Вложенность теперь будет работать!
    inlines = [DepthIntervalNormsInline]

class DrillingProgramInline(nested_admin.NestedStackedInline):
    model = DrillingProgram
    inlines = [ProgramSectionInline]
    # Добавляем max_num=1, так как у нас связь OneToOne
    max_num = 1
    can_delete = False


class NVPIncidentInline(nested_admin.NestedTabularInline):
    model = NVPIncident
    extra = 1

# class MudParameterLogInlline(nested_admin.NestedTabularInline):
#     model = MudParameterLog
#     extra = 0
#     readonly_fields = (
#         'measurement_time', 'is_out_of_norm',
#         'density', 'viscosity', 'plastic_viscosity', 'yield_point',
#         'gel_strength_10s', 'gel_strength_10m', 'methylene_blue_test', 'solid_phase_content',
#         'filtration', 'ph', 'calcium_hardness', 'chlorides', 'potassium',
#         'carbonate_content', 'phenolphthalein_alkalinity', 'methyl_orange_alkalinity',
#         'lubricant', 'raw_unparsed_params'
#     )
#     can_delete = False
    
#     def has_add_permission(self, request, obj=None):
#         return False
#     def get_max_num(self, request, obj=None, **kwargs):
#         # obj - это текущий объект скважины
#         if obj:
#             # Возвращаем количество существующих логов, но не более 5
#             return min(obj.mud_logs.count(), 5)
#         # Если объект еще не создан, не показываем ни одной формы
#         return 0
# --- Главный класс админки для Well ---
# Наследуемся от nested_admin.NestedModelAdmin

@admin.register(MudParameterLog)
class MudParameterLogAdmin(admin.ModelAdmin):
    list_display = ('well', 'measurement_time', 'is_out_of_norm', 'density', 'viscosity', 'plastic_viscosity', 'yield_point')
    list_filter = ('well', 'is_out_of_norm', 'measurement_time')
    # Делаем все поля только для чтения, т.к. это лог
    def has_change_permission(self, request, obj=None):
        return False
    def has_add_permission(self, request):
        return False

@admin.register(Well)
class WellAdmin(nested_admin.NestedModelAdmin):
    list_display = ('name', 'is_active', 'current_depth', 'current_section','has_nvp_incidents',  'has_overspending', 'updated_at')
    list_filter = ('is_active', 'current_section',  'has_overspending')
    search_fields = ('name', 'engineers')
    readonly_fields = ('mud_logs_link',)
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'is_active', 'engineers', ('current_depth', 'planned_depth'), 'current_section', 'current_operations')
        }),
        ('Финансовая информация', {
            'fields': ('has_overspending', 'overspending_details')
        }),
        ('Уведомления и Логи', {'fields': ('telegram_chat_id', 'telegram_topic_id', 'mud_logs_link')}),
    )
    inlines = [DrillingProgramInline, NVPIncidentInline]

    def mud_logs_link(self, obj):
        if obj.pk: # Если объект уже сохранен
            count = obj.mud_logs.count()
            url = (
                reverse("admin:wells_mudparameterlog_changelist")
                + f"?well__id__exact={obj.id}"
            )
            return format_html('<a href="{}" target="_blank">Просмотреть {} лог(ов) параметров</a>', url, count)
        return "Сохраните скважину, чтобы увидеть ссылку на логи."
    mud_logs_link.short_description = "История параметров"

    @admin.display(boolean=True, description='Наличие НВП')
    def has_nvp_incidents(self, obj):
        return obj.nvp_incidents.exists()
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'customer', 'deadline', 'is_urgent', 'is_completed')
    list_filter = ('is_urgent', 'is_completed', 'customer')
    search_fields = ('title', 'customer','details')

@admin.register(Tender)
class TenderAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'deadline', 'updated_at')
    list_filter = ('status',)
    search_fields = ('name', 'notes')