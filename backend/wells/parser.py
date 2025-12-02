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
    """Надёжный парсер параметров бурового раствора."""

    # Нормализуем CL
    remaining_text = re.sub(r'СL', 'CL', text, flags=re.IGNORECASE)

    found = {}

    # Удаление мусора
    def clean_value(v: str):
        if not v:
            return None

        v = v.strip().replace(',', '.')

        # Оставляем только цифры и одну точку
        cleaned = ''
        dot = False
        for ch in v:
            if ch.isdigit():
                cleaned += ch
            elif ch == '.':
                if not dot:
                    cleaned += '.'
                    dot = True

        if not cleaned or cleaned == '.':
            return None

        try:
            return float(cleaned)
        except:
            return None

    # ========== ШАГ 1. ТФ ==========
    tf_match = re.search(r'\bТФ\b\s*-+\s*([\d.,]+)', remaining_text, re.IGNORECASE)
    if tf_match:
        found['solid_phase_content'] = clean_value(tf_match.group(1))
        remaining_text = remaining_text.replace(tf_match.group(0), '')

    # ========== ШАГ 2. Ф ==========
    f_match = re.search(r'\bФ\b\s*-+\s*([\d.,]+)', remaining_text, re.IGNORECASE)
    if f_match:
        found['filtration'] = clean_value(f_match.group(1))
        remaining_text = remaining_text.replace(f_match.group(0), '')

    # ========== ШАГ 3. ДНС (устойчивый) ==========
    dns_match = re.search(r'\bДН[СC]\b\s*-*\s*([\d.,]+)', remaining_text, re.IGNORECASE)
    if dns_match:
        found['yield_point'] = clean_value(dns_match.group(1))
        remaining_text = remaining_text.replace(dns_match.group(0), '')

    # ========== ШАГ 4. Остальные простые параметры ==========
    patterns = {
        'density': ['Пл'],
        'viscosity': ['УВ'],
        'plastic_viscosity': ['ПВ'],
        'ph': ['PH', 'ph'],
        'chlorides': ['CL'],
        'calcium_hardness': ['Ca'],
        'carbonate_content': ['мел', 'CaCO3'],
        'potassium': ['К+', 'K'],
        'lubricant': ['смазка'],
        'methylene_blue_test': ['МБТ', 'MBT'],
    }

    for field, names in patterns.items():
        regex = r'\b(' + '|'.join(names) + r')\b\s*-+\s*([\d.,]+)'
        matches = re.findall(regex, remaining_text, re.IGNORECASE)
        for m in matches:
            value = clean_value(m[1])
            if value is not None:
                found[field] = value

        # Удаляем все найденные
        remaining_text = re.sub(regex, '', remaining_text, flags=re.IGNORECASE)

    # ========== ШАГ 5. СНС ==========
    sns_match = re.search(r'СНС\s*-*\s*([\d.,]+)\s*/\s*([\d.,]+)', remaining_text, re.IGNORECASE)
    if sns_match:
        found['gel_strength_10s'] = clean_value(sns_match.group(1))
        found['gel_strength_10m'] = clean_value(sns_match.group(2))
        remaining_text = remaining_text.replace(sns_match.group(0), '')

    # ========== ШАГ 6. Pf/Mf ==========
    pfmf_match = re.search(r'Pf/mf\s*-*\s*([\d.,]*)\s*/\s*([\d.,]*)', remaining_text, re.IGNORECASE)
    if pfmf_match:
        a, b = clean_value(pfmf_match.group(1)), clean_value(pfmf_match.group(2))
        if a is not None:
            found['phenolphthalein_alkalinity'] = a
        if b is not None:
            found['methyl_orange_alkalinity'] = b
        remaining_text = remaining_text.replace(pfmf_match.group(0), '')

    # Остаток
    rest = re.sub(r'[;,\s]+', ' ', remaining_text).strip()
    if rest:
        found['raw_unparsed_params'] = rest

    return found