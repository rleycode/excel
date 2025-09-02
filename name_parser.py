import re

def parse_names(name_str: str):
    """
    Разбивает строку названий по различным разделителям
    Поддерживает: //, /, запятые между названиями товаров
    """
    # Сначала разделяем по //
    if "//" in name_str:
        names = re.split(r"//", name_str)
        return [n.strip() for n in names if n.strip()]
    
    # Затем пробуем разделить по запятым между разными товарами
    # Ищем паттерны вида "Название1(...), Название2(...)"
    comma_split = re.split(r',\s*(?=[А-ЯЁ][а-яё\s\-\+]+(?:\([^)]+\))?)', name_str)
    if len(comma_split) > 1:
        return [n.strip() for n in comma_split if n.strip()]
    
    # Если не удалось разделить, возвращаем как есть
    return [name_str.strip()]

def extract_individual_products(name_str: str):
    """
    Извлекает отдельные товары из составного названия
    Примеры:
    - "Квинта+GL(1210,1150)/ Трамонтана S МП(1195,1155)" → ["Квинта+GL(1210,1150)", "Трамонтана S МП(1195,1155)"]
    - "Профнастил GL-10 (1180,1150),C10(1154,1100)sf" → ["Профнастил GL-10 (1180,1150)", "C10(1154,1100)sf"]
    """
    # Убираем лишние пробелы
    name_str = re.sub(r'\s+', ' ', name_str.strip())
    
    # Паттерн 1: разделение по / с пробелами
    if re.search(r'/\s+[А-ЯЁ]', name_str):
        parts = re.split(r'/\s+', name_str)
        return [p.strip() for p in parts if p.strip()]
    
    # Паттерн 2: разделение по запятой перед заглавной буквой (новый товар)
    if re.search(r',\s*[А-ЯЁC][А-Яа-яё0-9\-\+]*\s*\(', name_str):
        parts = re.split(r',\s*(?=[А-ЯЁC][А-Яа-яё0-9\-\+]*\s*\()', name_str)
        return [p.strip() for p in parts if p.strip()]
    
    # Паттерн 4: разделение по повторяющимся названиям товаров (например, "Ламонтерра ... Ламонтерра")
    # Специальная обработка для случаев с "Х" в названии
    if 'Х' in name_str and '(' in name_str:
        # Ищем паттерн: "Название(...) Название Х (...)"
        parts = re.split(r'\s+(?=\w+\s+Х\s+\w+\s*\()', name_str)
        if len(parts) == 2:
            return [p.strip() for p in parts if p.strip()]
    
    # Общий паттерн для разделения товаров с координатами
    # Ищем паттерн: "Название1(...) Название2(...)" 
    pattern = r'([А-ЯЁ][а-яё\s\-\+]*\([^)]+\))\s+([А-ЯЁ][а-яё\s\-\+]*\([^)]+\))'
    match = re.search(pattern, name_str)
    if match:
        # Проверяем, что это разные товары
        name1 = match.group(1).strip()
        name2 = match.group(2).strip()
        
        # Извлекаем базовые названия без координат
        name1_base = re.sub(r'\([^)]+\)', '', name1).strip()
        name2_base = re.sub(r'\([^)]+\)', '', name2).strip()
        
        # Если базовые названия разные или одно содержит "Х", разделяем
        if name1_base != name2_base or 'Х' in name_str:
            return [name1, name2]
    
    # Паттерн 3: разделение по //, если есть
    if "//" in name_str:
        parts = name_str.split("//")
        return [p.strip() for p in parts if p.strip()]
    
    # Если не удалось разделить, возвращаем как есть
    return [name_str.strip()]
