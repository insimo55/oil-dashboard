# backend/wells/views.py
import re
import logging
from django.db.models import Case, When, Value, F, BooleanField
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action
from .models import Well,Task, Tender, MudParameterLog
from .serializers import WellSerializer,TaskSerializer, TenderSerializer, WellLinkTelegramSerializer 
from django.utils import timezone
from rest_framework.response import Response
from .parser import parse_summary, parse_mud_parameters
from .validator import validate_mud_parameters, update_well_section_by_depth
from .rules_engine import run_all_rules 
from .notifications import send_telegram_alert 
from .ai_service import get_ai_analysis
class WellViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows wells to be viewed.
    """
    queryset = Well.objects.order_by(F('is_active').desc(), F('updated_at').desc())
    serializer_class = WellSerializer

    @action(detail=False, methods=['post'], url_path='process-summary')
    def process_summary(self, request):
        summary_text = request.data.get('text')
        telegram_chat_id = request.data.get('chat_id')
        telegram_topic_id = request.data.get('topic_id')

        if not summary_text:
            return Response({'error': 'No text provided'}, status=status.HTTP_400_BAD_REQUEST)

        # --- Шаг 1: Парсим все данные ---
        parsed_data = parse_summary(summary_text)
        
        well_name = parsed_data.get('name')
        if not well_name:
            return Response({'error': 'Could not find well name in summary'}, status=status.HTTP_400_BAD_REQUEST)

        # --- Шаг 2: Находим или создаем скважину ---
        well, created = Well.objects.get_or_create(name=well_name)
        
        # --- Шаг 3: Собираем все обновления в один пакет ---
        fields_to_update = []

        # Обновляем поля из парсера
        for key, value in parsed_data.items():
            if key != 'name' and hasattr(well, key):
                setattr(well, key, value)
                fields_to_update.append(key)
        
        # Логика авто-привязки
        if telegram_chat_id and not well.telegram_chat_id:
            well.telegram_chat_id = telegram_chat_id
            well.telegram_topic_id = telegram_topic_id
            fields_to_update.extend(['telegram_chat_id', 'telegram_topic_id'])
        
        # Логика авто-обновления секции (из Варианта 1)
        current_depth_from_parser = parsed_data.get('current_depth')
        if current_depth_from_parser is not None:
            # Эта функция сама делает save, так что ее нужно доработать
            # Давай пока закомментируем ее и посмотрим, решит ли это проблему
            # update_well_section_by_depth(well, current_depth_from_parser) 
            pass # Мы вернемся к этому

        # --- Шаг 4: Делаем ОДНО сохранение, если были изменения ---
        if fields_to_update:
            well.save(update_fields=list(set(fields_to_update))) # set() убирает дубликаты

        # --- Шаг 5: Обработка параметров раствора ---
        mud_params_text_match = re.search(r'Параметры бурового раствора:\s*(.*)', summary_text, re.DOTALL | re.IGNORECASE)
        if mud_params_text_match:
            mud_params_text = mud_params_text_match.group(1)
            parsed_mud_params = parse_mud_parameters(mud_params_text)
            
            if parsed_mud_params:
                current_depth = parsed_data.get('current_depth', well.current_depth)
                has_deviation = validate_mud_parameters(well, parsed_mud_params, current_depth)
                parsed_mud_params['is_out_of_norm'] = has_deviation
                
                log_entry = MudParameterLog.objects.create(well=well, **parsed_mud_params)
                    # 1. Запускаем движок правил на только что созданном логе
                alerts_dict  = run_all_rules(log_entry)
                
                # 2. Если есть хоть одна тревога, формируем и отправляем уведомление
                if alerts_dict['critical'] or alerts_dict['warning']:
                    
                    header = f"🔔 <b>Оповещение {well.name}</b>\n\n"
                    
                    message_parts = []
                    if alerts_dict['warning']:
                        message_parts.extend(alerts_dict['warning'])
                    if alerts_dict['critical']:
                        message_parts.extend(alerts_dict['critical'])

                    full_message = header + "\n\n".join(message_parts)

                    # --- ИЗМЕНЕНИЯ ЗДЕСЬ ---
                    # Запускаем AI-анализ ТОЛЬКО если есть КРИТИЧЕСКИЕ тревоги
                    if alerts_dict['critical']:
                        logging.info(f"Обнаружены критические тревоги, запускаем AI-анализ для скважины {well.name}...")
                        ai_comment = get_ai_analysis(well)
                        if ai_comment:
                            full_message += "\n\n" + ai_comment
                    # --------------------------
                    
                    # Отправляем финальное сообщение (с комментарием AI или без)
                    logging.info("--- ГОТОВИМСЯ ОТПРАВИТЬ В TELEGRAM ---")
                    logging.info(repr(full_message))
                    logging.info("-------------------------------------")
                    send_telegram_alert(well, full_message)
                else:
                    logging.info("Движок правил сработал, но не сгенерировал текста для тревог. Уведомление не отправлено.")

        serializer = self.get_serializer(well)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='link-telegram')
    def link_telegram(self, request):
        serializer = WellLinkTelegramSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        well_name = data.get('name')
        
        try:
            # Ищем скважину по имени. `__iexact` - поиск без учета регистра
            well_to_update = Well.objects.get(name__iexact=well_name)
        except Well.DoesNotExist:
            return Response({'error': f"Скважина с именем '{well_name}' не найдена."}, status=status.HTTP_404_NOT_FOUND)
        
        # Обновляем поля и сохраняем
        well_to_update.telegram_chat_id = data.get('telegram_chat_id')
        well_to_update.telegram_topic_id = data.get('telegram_topic_id')
        well_to_update.save(update_fields=['telegram_chat_id', 'telegram_topic_id'])
        
        return Response({
            'status': 'success',
            'message': f"Скважина '{well_to_update.name}' успешно привязана к чату."
        }, status=status.HTTP_200_OK)

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