# backend/wells/views.py

from rest_framework import viewsets
from .models import Well,Task 
from .serializers import WellSerializer,TaskSerializer 


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