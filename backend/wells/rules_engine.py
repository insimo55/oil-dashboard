# backend/wells/rules_engine.py
import logging
from django.db import models
from .models import MudParameterLog, Well

logger = logging.getLogger(__name__)

# --- Новая структура для возврата результатов ---
# Мы будем возвращать словарь, где ключи - это уровни тревоги
# 'critical' - красная зона, 'warning' - желтая зона
def get_default_alerts_dict():
    return {'critical': [], 'warning': []}

# --- Правила (теперь возвращают кортеж: уровень, сообщение) ---

def check_bicarbonate_risk(params: MudParameterLog) -> tuple[str, str] | None:
    """
    Проверяет риск бикарбонатного загрязнения.
    Возвращает кортеж ('critical', "сообщение") или None.
    """
    pf = params.phenolphthalein_alkalinity
    mf = params.methyl_orange_alkalinity

    if pf is not None and mf is not None:
        if pf == 0 or (2 * pf < mf):
            message = (
                "🚨 <b>Критический риск: Бикарбонатное загрязнение!</b>\n"
                f"<i>(Условие: Pf=0 или 2*Pf < Mf. Факт: Pf={pf}, Mf={mf})</i>\n"
                "<b>Возможные последствия:</b> Снижение pH, увеличение водоотдачи."
            )
            return ('critical', message)
    return None

def check_basic_norms(params: MudParameterLog, norms) -> dict:
    """
    Проверяет выход за min/max нормы с учетом допусков.
    Возвращает словарь {'critical': [...], 'warning': [...]}.
    """
    alerts = get_default_alerts_dict()
    
    TOLERANCES = {
        'density': 0.02,
    }

    param_fields = [f for f in MudParameterLog._meta.get_fields() if isinstance(f, models.FloatField)]

    for field in param_fields:
        param_name = field.name
        measured_value = getattr(params, param_name)
        if measured_value is None: continue

        norm_min = getattr(norms, f"{param_name}_min", None)
        norm_max = getattr(norms, f"{param_name}_max", None)
        tolerance = TOLERANCES.get(param_name, 0)
        verbose_name = field.verbose_name

        # Проверяем только если есть хотя бы одна граница
        if norm_min is not None or norm_max is not None:
            # Определяем "жесткие" и "мягкие" границы
            hard_min = (norm_min - tolerance) if norm_min is not None else None
            hard_max = (norm_max + tolerance) if norm_max is not None else None
            soft_min = norm_min
            soft_max = norm_max

            # --- Логика трехуровневой проверки ---
            if (hard_min is not None and measured_value < hard_min):
                msg = (f"🔴 <b>КРИТИЧЕСКОЕ ОТКЛОНЕНИЕ (НИЖЕ НОРМЫ):</b> {verbose_name}\n"
                       f"<i>Факт: <b>{measured_value}</b>, Норма: [{norm_min}-{norm_max}], Допуск: {tolerance}</i>")
                alerts['critical'].append(msg)
            elif (soft_min is not None and measured_value < soft_min):
                msg = (f"🟡 <b>Предупреждение (выход за норму):</b> {verbose_name}\n"
                       f"<i>Факт: <b>{measured_value}</b> (в допуске), Норма: {norm_min}</i>")
                alerts['warning'].append(msg)
            
            if (hard_max is not None and measured_value > hard_max):
                msg = (f"🔴 <b>КРИТИЧЕСКОЕ ОТКЛОНЕНИЕ (ВЫШЕ НОРМЫ):</b> {verbose_name}\n"
                       f"<i>Факт: <b>{measured_value}</b>, Норма: [{norm_min}-{norm_max}], Допуск: {tolerance}</i>")
                alerts['critical'].append(msg)
            elif (soft_max is not None and measured_value > soft_max):
                msg = (f"🟡 <b>Предупреждение (выход за норму):</b> {verbose_name}\n"
                       f"<i>Факт: <b>{measured_value}</b> (в допуске), Норма: {soft_max}</i>")
                alerts['warning'].append(msg)

    return alerts

# --- Главный "Оркестратор" ---
def run_all_rules(log_entry: MudParameterLog) -> dict:
    """
    Запускает все проверки и возвращает словарь сгруппированных тревог.
    """
    logger.info(f"Запуск движка правил для замера ID {log_entry.id}...")
    final_alerts = get_default_alerts_dict()
    well = log_entry.well

    # 1. Запускаем сложные правила
    bicarbonate_result = check_bicarbonate_risk(log_entry)
    if bicarbonate_result:
        level, message = bicarbonate_result
        final_alerts[level].append(message)

    # 2. Запускаем проверку по базовым нормам
    try:
        # Вот правильная логика поиска
        current_program_section = log_entry.well.drilling_program.sections.get(section_type=log_entry.well.current_section)
        interval_norms = current_program_section.intervals.get(
            start_depth__lte=log_entry.well.current_depth,
            end_depth__gte=log_entry.well.current_depth
        )
        
        basic_alerts = check_basic_norms(log_entry, interval_norms)
        final_alerts['critical'].extend(basic_alerts['critical'])
        final_alerts['warning'].extend(basic_alerts['warning'])
        
    except Exception as e:
        # Логируем конкретную ошибку
        logger.warning(f"Нормы для скважины {well.name} не найдены. Ошибка: {e}")

    logger.info(f"Движок правил обнаружил {len(final_alerts['critical'])} крит. и {len(final_alerts['warning'])} предупр. тревог.")
    return final_alerts