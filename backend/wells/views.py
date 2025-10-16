# backend/wells/views.py
from django.db.models import Case, When, Value, F, BooleanField
from rest_framework import viewsets
from .models import Well,Task, Tender 
from .serializers import WellSerializer,TaskSerializer, TenderSerializer 
from django.utils import timezone


class WellViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows wells to be viewed.
    """
    queryset = Well.objects.order_by(F('is_active').desc(), F('updated_at').desc())
    serializer_class = WellSerializer

class TaskViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows tasks to be viewed.
    Мы хотим видеть только невыполненные задачи.
    """
    queryset = Task.objects.filter(is_completed=False)
    serializer_class = TaskSerializer

class TenderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TenderSerializer
    
    def get_queryset(self):
        """
        Возвращает тендеры, отсортированные по следующей логике:
        1. Сначала "Активные" тендеры (у которых есть дедлайн в будущем).
           - Внутри этой группы сортируем по дедлайну (от ближайшего к дальнему).
        2. Затем все остальные ("Неактивные").
           - Внутри этой группы сортируем по дате обновления (от нового к старому).
        """
        now = timezone.now()
        
        queryset = Tender.objects.annotate(
            # Создаем флаг "Активный"
            is_active=Case(
                When(deadline__isnull=False, deadline__gt=now, then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            )
        ).order_by(
            F('is_active').desc(), # Сначала активные (True > False при сортировке по убыванию)
            F('deadline').asc(nulls_last=True), # Затем по дедлайну (ближайшие сначала)
            F('updated_at').desc() # В самом конце - по дате обновления
        )
        
        return queryset