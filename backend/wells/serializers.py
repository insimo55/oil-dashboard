# backend/wells/serializers.py

from rest_framework import serializers
from .models import Well,Task 

class WellSerializer(serializers.ModelSerializer):
    # Добавляем "человекочитаемое" представление для поля с выбором
    current_section_display = serializers.CharField(source='get_current_section_display', read_only=True)
    
    class Meta:
        model = Well
        fields = '__all__' # Включаем все поля из модели в API


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'