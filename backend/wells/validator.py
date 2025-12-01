# backend/wells/validator.py
import logging
from .models import Well


logger = logging.getLogger(__name__)

def validate_mud_parameters(well: Well, params: dict, current_depth: float) -> bool:
    """
    Проверяет параметры на соответствие нормам для текущей секции и глубины.
    """
    logger.info(f"--- Запуск валидации для скважины '{well.name}' ---")
    logger.info(f"Получены параметры: {params}")
    logger.info(f"Текущая глубина: {current_depth}м, текущая секция: '{well.current_section}'")

    if not hasattr(well, 'drilling_program'):
        logger.warning("Программа промывки для скважины не найдена. Валидация пропущена.")
        return False # Если программы нет, не проверяем

    try:
        # Находим текущую секцию в программе по типу секции скважины
        current_program_section = well.drilling_program.sections.get(section_type=well.current_section)
        logger.info(f"Найдена секция в программе: '{current_program_section}'")
        # Находим нужный интервал глубин, в который попадает текущий забой
        # lte = Less Than or Equal (<=), gte = Greater Than or Equal (>=)
        interval_norms = current_program_section.intervals.get(
            start_depth__lte=current_depth,
            end_depth__gte=current_depth
        )
        logger.info(f"Найден интервал норм: {interval_norms.start_depth}м - {interval_norms.end_depth}м")
    except Exception as e:
        # Если не найдена секция или интервал, считаем, что отклонений нет
        logger.warning(f"Не удалось найти подходящую норму: {e}. Валидация пропущена.")
        return False

    is_out_of_norm = False
    for param_name, measured_value in params.items():
        if measured_value is None:
            continue

        norm_min = getattr(interval_norms, f"{param_name}_min", None)
        norm_max = getattr(interval_norms, f"{param_name}_max", None)
        
        logger.info(f"Проверка параметра '{param_name}': значение={measured_value}, норма=[{norm_min}, {norm_max}]")


        if (norm_min is not None and measured_value < norm_min):
            logger.warning(f"ОТКЛОНЕНИЕ! '{param_name}' ({measured_value}) < min ({norm_min})")
            is_out_of_norm = True
            break
        
        if (norm_max is not None and measured_value > norm_max):
            logger.warning(f"ОТКЛОНЕНИЕ! '{param_name}' ({measured_value}) > max ({norm_max})")
            is_out_of_norm = True
            break
    
    logger.info(f"--- Результат валидации: is_out_of_norm = {is_out_of_norm} ---")
    
    return is_out_of_norm

def update_well_section_by_depth(well: Well, current_depth: float) -> bool:
    """
    Ищет в программе промывки интервал, соответствующий глубине,
    и обновляет `current_section` у скважины.
    Возвращает True, если секция была найдена и обновлена, иначе False.
    """
    if not hasattr(well, 'drilling_program'):
        return False

    from .models import DepthIntervalNorms
    
    # Ищем во всех интервалах всех секций этой скважины
    interval = DepthIntervalNorms.objects.filter(
        section__program__well=well,
        start_depth__lte=current_depth,
        end_depth__gte=current_depth
    ).first() # first() вернет первый найденный или None

    if interval:
        new_section_type = interval.section.section_type
        # Обновляем, только если секция изменилась
        if well.current_section != new_section_type:
            well.current_section = new_section_type
            well.save(update_fields=['current_section']) # Сохраняем только это поле
            logger.info(f"Секция для скважины '{well.name}' автоматически обновлена на '{new_section_type}'")
        return True
    
    return False