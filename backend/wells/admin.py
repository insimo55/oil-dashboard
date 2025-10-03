# backend/wells/admin.py

from django.contrib import admin
from .models import Well, Task 

@admin.register(Well)
class WellAdmin(admin.ModelAdmin):
    list_display = ('name', 'current_depth', 'current_section', 'has_nvp', 'has_overspending', 'updated_at')
    list_filter = ('current_section', 'has_nvp', 'has_overspending')
    search_fields = ('name', 'engineers')

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'customer', 'deadline', 'is_urgent', 'is_completed')
    list_filter = ('is_urgent', 'is_completed', 'customer')
    search_fields = ('title', 'customer')