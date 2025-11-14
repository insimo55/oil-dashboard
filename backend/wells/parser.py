# backend/wells/parser.py
import re
from datetime import datetime

def parse_summary(text: str) -> dict:
    """
    Парсит текстовую сводку и возвращает словарь с извлеченными данными.
    """
    data = {}

    # Регулярные выражения для извлечения ключевых данных.
    # Они настроены на твой формат сводки.
    
    # 1. Название скважины (идентификатор)
    well_name_match = re.search(r'Куст\s*(\d+)[^\d]{0,10}(скв\.?|скважина)\s*(\d+)', text, re.IGNORECASE)
    if well_name_match:
        well_num = well_name_match.group(1)
        well_bore_num = well_name_match.group(3)

    # формируем единый нормализованный формат
        data['name'] = f"Куст {well_num} скважина {well_bore_num}"

    # 2. Инженеры
    engineers_match = re.search(r'Инженер по бр:\s*(.*)', text, re.IGNORECASE)
    if engineers_match:
        raw_engineers_str = engineers_match.group(1).strip()
        cleaned_engineers_str = re.sub(r'\s*[/,;]\s*', ', ', raw_engineers_str)
        data['engineers'] = cleaned_engineers_str

    # 3. Проектный забой
    planned_depth_match = re.search(r'Проектный забой:\s*([\d.,]+)', text)
    if planned_depth_match:
        # Заменяем запятую на точку для правильного преобразования в число
        depth_str = planned_depth_match.group(1).replace(',', '.')
        data['planned_depth'] = float(depth_str)

    # 4. Текущий забой
    current_depth_match = re.search(r'Текущий забой:\s*([\d.,]+)', text)
    if current_depth_match:
        depth_str = current_depth_match.group(1).replace(',', '.')
        data['current_depth'] = float(depth_str)
        
    # 5. Текущие работы
    current_ops_match = re.search(r'Текущие работы:\s*(.*)', text)
    if current_ops_match:
        data['current_operations'] = current_ops_match.group(1).strip()
        

    # Добавляем полный текст сводки для сохранения в БД
    data['last_summary_text'] = text

    return data