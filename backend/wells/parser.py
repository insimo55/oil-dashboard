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


def parse_mud_parameters(text: str) -> dict:
    """Парсит блок с параметрами бурового раствора с принудительным порядком для ТФ и Ф."""
    
    processed_text = re.sub(r'СL', 'CL', text, flags=re.IGNORECASE)
    remaining_text = processed_text
    found_params = {}

    def clean_value(val_str):
        if not val_str or not val_str.strip(): return None
        try: return float(val_str.strip().replace(',', '.'))
        except ValueError: return None

    # --- ШАГ 1: Приоритетный парсинг "проблемных" параметров ---

    # Сначала ищем и вырезаем "ТФ"
    tf_match = re.search(r'ТФ\s*-\s*([\d,.]+)', remaining_text, re.IGNORECASE)
    if tf_match:
        value = clean_value(tf_match.group(1))
        if value is not None:
            found_params['solid_phase_content'] = value
        remaining_text = remaining_text.replace(tf_match.group(0), '', 1)

    # Теперь ищем "Ф" в оставшемся тексте
    f_match = re.search(r'Ф\s*-\s*([\d,.]+)', remaining_text, re.IGNORECASE)
    if f_match:
        value = clean_value(f_match.group(1))
        if value is not None:
            found_params['filtration'] = value
        remaining_text = remaining_text.replace(f_match.group(0), '', 1)

    # --- ШАГ 2: Парсинг остальных простых параметров ---

    # В patterns УБИРАЕМ 'solid_phase_content' и 'filtration', так как мы их уже обработали
    patterns = {
        # Теперь ключ - это название поля в модели, а значение - список возможных имен параметра в тексте
        'density': ['Пл', 'пл', 'ПЛ'],
        'viscosity': ['УВ', 'ув', 'Ув'],
        'plastic_viscosity': ['ПВ', 'пв', 'Пв'],
        'yield_point': ['ДНС', 'днс'],
        'filtration': ['Ф', 'ф', 'фильтрация'],
        'ph': ['ph', 'PH', 'Ph'],
        'calcium_hardness': ['Ca', 'жесткость'],
        'chlorides': ['CL'],
        'carbonate_content': ['мел', 'CaCO3'],
        'potassium': ['К\+', 'k','K'], # Плюс нужно экранировать
        'lubricant': ['смазка'],
        'methylene_blue_test': ['Мбт', 'MBT','mbt'],
        'solid_phase_content': ['ТФ'],
    }

    for field, names in patterns.items():
        # Создаем динамическое регулярное выражение, которое ищет любое из имен
        # Пример: (Пл|УВ|ПВ)\s*-\s*([\d,.]+)
        # `\b` - граница слова, чтобы "Ф" не нашлось внутри "ТФ"
        regex = r'\b(' + '|'.join(names) + r')\b\s*-\s*([\d,.]+)(?=\s*,|\s+[a-zA-Zа-яА-Я]|;|$)'
        
        # re.findall найдет ВСЕ вхождения этого паттерна в тексте
        matches = re.findall(regex, remaining_text, re.IGNORECASE)
        
        for match in matches:
            param_name_found = match[0].lower()
            param_value_str = match[1]
            
            # Определяем, какому полю в модели соответствует найденное имя
            current_field = None
            for f, n_list in patterns.items():
                if param_name_found in [n.lower().replace(r'\+', '+') for n in n_list]:
                    current_field = f
                    break
            
            if current_field:
                value = clean_value(param_value_str)
                if value is not None:
                    found_params[current_field] = value
                    # Вырезаем найденный фрагмент, чтобы не обрабатывать его снова
                    # Мы ищем оригинальный фрагмент с помощью более точного re.search
                    full_match_obj = re.search(re.escape(match[0]) + r'\s*-\s*' + re.escape(match[1]), remaining_text, re.IGNORECASE)
                    if full_match_obj:
                        remaining_text = remaining_text.replace(full_match_obj.group(0), '', 1)

    # --- ШАГ 3: Парсинг сложных параметров (СНС, Pf/Mf) ---

    sns_pattern = r'СНС\s*-\s*([\d,.]+)\s*/\s*([\d,.]+)'
    pfmf_pattern = r'Pf/mf\s*-\s*([\d,.]*)\s*/\s*([\d,.]*)'
    # --- Парсинг СНС ---
    sns_match = re.search(sns_pattern, remaining_text, re.IGNORECASE)
    if sns_match:
        val1, val2 = clean_value(sns_match.group(1)), clean_value(sns_match.group(2))
        if val1 is not None: found_params['gel_strength_10s'] = val1
        if val2 is not None: found_params['gel_strength_10m'] = val2
        remaining_text = remaining_text.replace(sns_match.group(0), '', 1)

    # --- Парсинг Pf/Mf ---
    pfmf_match = re.search(pfmf_pattern, remaining_text, re.IGNORECASE)
    if pfmf_match:
        val1, val2 = clean_value(pfmf_match.group(1)), clean_value(pfmf_match.group(2))
        if val1 is not None: found_params['phenolphthalein_alkalinity'] = val1
        if val2 is not None: found_params['methyl_orange_alkalinity'] = val2
        remaining_text = remaining_text.replace(pfmf_match.group(0), '', 1)
    
    # Собираем остатки
    unparsed_text = re.sub(r'[\s;-]+', ' ', remaining_text).strip()
    if unparsed_text:
        found_params['raw_unparsed_params'] = unparsed_text

    return found_params