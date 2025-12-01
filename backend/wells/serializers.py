# backend/wells/serializers.py

from rest_framework import serializers
from .models import Well,Task, NVPIncident, Tender 

class NVPIncidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = NVPIncident
        fields = ['id', 'incident_date', 'duration', 'description']

class WellSerializer(serializers.ModelSerializer):
    # Добавляем "человекочитаемое" представление для поля с выбором
    current_section_display = serializers.CharField(source='get_current_section_display', read_only=True)
    nvp_incidents = NVPIncidentSerializer(many=True, read_only=True)
    class Meta:
        model = Well
        fields = [
            'id', 'name', 'is_active', 'engineers', 'current_depth', 'planned_depth', 
            'current_section', 'current_section_display', 'current_operations', 
            'has_overspending', 'overspending_details', 'created_at', 'updated_at',
            'nvp_incidents','last_summary_text' # <-- новое поле
        ] # Включаем все поля из модели в API


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'

class TenderSerializer(serializers.ModelSerializer):
    # Добавляем "человеческое" имя статуса
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Tender
        fields = '__all__'

class WellLinkTelegramSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    telegram_chat_id = serializers.IntegerField() # Используем IntegerField для приема данных
    telegram_topic_id = serializers.IntegerField(required=False, allow_null=True)