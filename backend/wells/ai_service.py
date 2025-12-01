# backend/wells/ai_service.py
import logging
import google.generativeai as genai
from django.conf import settings
from .models import Well

logger = logging.getLogger(__name__)

def get_ai_analysis(well: Well) -> str | None:
    """
    Формирует промпт, отправляет его в Google Gemini и возвращает анализ.
    """
    api_key = settings.GOOGLE_API_KEY
    if not api_key:
        logger.warning("GOOGLE_API_KEY не настроен. AI-анализ пропущен.")
        return None

    try:
        # --- Шаг 1: Конфигурация клиента Google AI ---
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest')

        # --- Шаг 2: Сбор данных и формирование промпта ---
        # (Этот блок остается ТОЧНО ТАКИМ ЖЕ, как и для OpenAI)
        
        last_logs = well.mud_logs.all()[:5]
        if len(last_logs) < 2:
            return None

        current_norms = None
        try:
            section = well.drilling_program.sections.get(section_type=well.current_section)
            current_norms = section.intervals.get(
                start_depth__lte=well.current_depth,
                end_depth__gte=well.current_depth
            )
        except Exception:
            pass

        prompt_parts = []
        prompt_parts.append("Ты — опытный инженер по буровым растворам. Проведи краткий анализ ситуации на скважине и дай рекомендации. Отвечай кратко, по делу, используя Markdown для форматирования.")
        
        prompt_parts.append("\n**Вводные данные:**")
        prompt_parts.append(f"- Скважина: {well.name}")
        prompt_parts.append(f"- Текущий забой: {well.current_depth} м")
        prompt_parts.append(f"- Текущая секция: {well.get_current_section_display()}")

        if current_norms:
            prompt_parts.append("\n**Плановые параметры (нормы):**")
            if current_norms.density_min is not None:
                prompt_parts.append(f"- Плотность: {current_norms.density_min}-{current_norms.density_max}")
            if current_norms.viscosity_min is not None:
                prompt_parts.append(f"- Вязкость: {current_norms.viscosity_min}-{current_norms.viscosity_max}")

        prompt_parts.append("\n**Последние замеры (от самого свежего к старому):**")
        for i, log in enumerate(last_logs):
            log_line = f"- Замер {i+1} ({log.measurement_time.strftime('%H:%M')}):"
            # Динамически собираем все параметры для этого замера
            param_strings = []
            # Словарь: поле в модели -> сокращение в промпте
            param_map = {
                'density': 'Пл', 'viscosity': 'УВ', 'plastic_viscosity': 'ПВ',
                'yield_point': 'ДНС', 'gel_strength_10s': 'СНС 10с', 'gel_strength_10m': 'СНС 10м',
                'filtration': 'Ф', 'ph': 'pH', 'calcium_hardness': 'Ca',
                'chlorides': 'CL', 'potassium': 'K+', 'carbonate_content': 'Мел',
                'lubricant': 'Смазка', 'methylene_blue_test': 'МБТ', 'solid_phase_content': 'ТФ',
                'phenolphthalein_alkalinity': 'Pf', 'methyl_orange_alkalinity': 'Mf'
            }
            for field, abbr in param_map.items():
                value = getattr(log, field)
                if value is not None:
                    param_strings.append(f" {abbr}={value}")
            
            log_line += ";".join(param_strings)
            prompt_parts.append(log_line)
        prompt_parts.append("\n**Твоя задача:**\n1. **Анализ трендов:** Опиши динамику ключевых параметров (например, 'Плотность стабильно растет').\n2. **Оценка рисков:** Укажи на 1-2 главных риска (например, 'Риск осыпей из-за роста хлоридов').\n3. **Рекомендации:** Дай 1-2 четкие рекомендации по стабилизации раствора.")
        
        final_prompt = "\n".join(prompt_parts)

        # --- Шаг 3: Отправка запроса в Google Gemini ---
        
        logger.info("Отправка запроса на AI-анализ (Google Gemini)...")
        # Для Gemini мы просто отправляем текст
        response = model.generate_content(final_prompt)
        
        # API Gemini может заблокировать ответ по соображениям безопасности,
        # поэтому нужна проверка `prompt_feedback`.
        if not response.parts:
             if response.prompt_feedback and response.prompt_feedback.block_reason:
                 block_reason = response.prompt_feedback.block_reason.name
                 logger.error(f"Ответ от Gemini заблокирован по причине: {block_reason}")
                 return "⚠️ _AI-анализ не был выполнен: ответ модели был заблокирован по соображениям безопасности._"
             else:
                 logger.error("Ответ от Gemini пуст без явной причины.")
                 return None
        
        ai_response = response.text
        logger.info("AI-анализ (Google Gemini) успешно получен.")
        
        return f"🤖 **Комментарий AI-ассистента (Gemini):**\n{ai_response}"

    except Exception as e:
        logger.error(f"Ошибка при обращении к Google Gemini API: {e}")
        return None