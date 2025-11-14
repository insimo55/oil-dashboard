# backend/wells/views.py
from django.db.models import Case, When, Value, F, BooleanField
from rest_framework import viewsets, status
from rest_framework.decorators import action
from .models import Well,Task, Tender 
from .serializers import WellSerializer,TaskSerializer, TenderSerializer 
from django.utils import timezone
from rest_framework.response import Response
from .parser import parse_summary

class WellViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows wells to be viewed.
    """
    queryset = Well.objects.order_by(F('is_active').desc(), F('updated_at').desc())
    serializer_class = WellSerializer

    @action(detail=False, methods=['post'], url_path='process-summary')
    def process_summary(self, request):
        """
        Принимает текстовую сводку, парсит ее, находит или создает скважину
        и обновляет ее данные.
        """
        summary_text = request.data.get('text')
        if not summary_text:
            return Response({'error': 'No text provided'}, status=status.HTTP_400_BAD_REQUEST)

        parsed_data = parse_summary(summary_text)
        
        well_name = parsed_data.get('name')
        if not well_name:
            return Response({'error': 'Could not find well name in summary'}, status=status.HTTP_400_BAD_REQUEST)

        # Находим скважину по имени или создаем новую
        well, created = Well.objects.get_or_create(name=well_name)
        
        # Обновляем поля объекта данными из парсера
        # Удаляем 'name' из данных, чтобы не обновлять его
        update_data = parsed_data
        if 'name' in update_data:
            del update_data['name']
            
        for key, value in update_data.items():
            setattr(well, key, value)
        well.save()

        serializer = self.get_serializer(well)
        return Response(serializer.data, status=status.HTTP_200_OK)

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