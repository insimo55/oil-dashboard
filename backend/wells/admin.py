# backend/wells/admin.py

from django.contrib import admin
from .models import Well, Task, NVPIncident, Tender 

class NVPIncidentInline(admin.TabularInline):
    model = NVPIncident
    extra = 1 # По умолчанию показывать 1 пустую форму для добавления

@admin.register(Well)
class WellAdmin(admin.ModelAdmin):
    list_display = ('name', 'current_depth', 'current_section','has_nvp_incidents',  'has_overspending', 'updated_at')
    list_filter = ('current_section',  'has_overspending')
    search_fields = ('name', 'engineers')
    inlines = [NVPIncidentInline]
    @admin.display(boolean=True, description='Наличие НВП')
    def has_nvp_incidents(self, obj):
        # obj - это экземпляр скважины (Well)
        # Возвращаем True, если у скважины есть хотя бы один инцидент
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