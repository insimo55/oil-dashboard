# backend/wells/views.py
from django.db.models import Case, When, Value, F
from rest_framework import viewsets
from .models import Well,Task, Tender 
from .serializers import WellSerializer,TaskSerializer, TenderSerializer 


class WellViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows wells to be viewed.
    """
    queryset = Well.objects.all()
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
        # Реализуем сложную сортировку
        # Сначала "К загрузке", потом остальные
        # Внутри "К загрузке" - по ближайшему дедлайну
        return Tender.objects.annotate(
            status_order=Case(
                When(status='PENDING', then=Value(1)),
                default=Value(2)
            )
        ).order_by('status_order', 'deadline')