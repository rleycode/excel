from typing import List, Dict, Any, Optional
import re
from database import get_db_manager

# Кэш для данных из БД
_product_mapping_cache = None
_markup_rules_cache = None

def get_product_mapping() -> Dict[str, Dict[str, str]]:
    """
    Получает соответствие товаров и категорий из БД с кэшированием
    """
    global _product_mapping_cache
    
    if _product_mapping_cache is None:
        try:
            db = get_db_manager()
            _product_mapping_cache = db.get_product_categories()
        except Exception as e:
            print(f"Ошибка получения категорий из БД: {e}")
            # Fallback на статические данные
            _product_mapping_cache = {
                "Кредо GL": {"unit": "м2", "category_id": "1156"},
                "Монтекристо S": {"unit": "м2", "category_id": "1157"},
                "Классик GL": {"unit": "м2", "category_id": "1158"},
                "Модерн GL": {"unit": "м2", "category_id": "1159"},
                "Квадро Профи GL": {"unit": "м2", "category_id": "1160"},
                "Ламонтерра МП": {"unit": "м2", "category_id": "1161"},
                "Ламонтерра Х МП": {"unit": "м2", "category_id": "1162"},
                "Камея GL": {"unit": "м2", "category_id": "1163"},
                "Квинта+GL": {"unit": "м2", "category_id": "1164"},
                "Трамонтана S МП": {"unit": "м2", "category_id": "1165"},
                "Профнастил С-8": {"unit": "м2", "category_id": "2001"},
                "МП-10": {"unit": "м2", "category_id": "2002"},
                "Профнастил GL-10": {"unit": "м2", "category_id": "2003"},
                "C10": {"unit": "м2", "category_id": "2004"},
                "Профнастил С10 фигурный": {"unit": "м2", "category_id": "2005"},
                "Профнастил С-20": {"unit": "м2", "category_id": "2006"},
                "Профнастил С-21": {"unit": "м2", "category_id": "2007"},
                "С-44": {"unit": "м2", "category_id": "2008"},
                "Профнастил НС-35": {"unit": "м2", "category_id": "2009"},
                "Плоский лист": {"unit": "м2", "category_id": "2010"},
            }
    
    return _product_mapping_cache

def get_markup_rules() -> List[Dict[str, Any]]:
    """
    Получает правила наценок из БД с кэшированием
    """
    global _markup_rules_cache
    
    if _markup_rules_cache is None:
        try:
            db = get_db_manager()
            _markup_rules_cache = db.get_markup_rules()
        except Exception as e:
            print(f"Ошибка получения наценок из БД: {e}")
            # Fallback на статические данные
            _markup_rules_cache = [
                {"color": "1015", "coating": "PE 0,45", "region": "spb_nn_kirov_penza", "markup": 7.0, "unit_markup": 0.7},
                {"color": "1018", "coating": "Satin", "region": "all", "markup": 50.0, "unit_markup": 5.0},
                {"color": "standard", "coating": "PE 0,45 двс", "region": "all", "markup": 50.0, "unit_markup": 5.0},
                {"color": "standard", "coating": "PE 0,7", "region": "all", "markup": 50.0, "unit_markup": 5.0},
                {"color": "standard", "coating": "PE 0,8", "region": "all", "markup": 55.0, "unit_markup": 5.5},
            ]
    
    return _markup_rules_cache

def clear_cache():
    """
    Очищает кэш данных БД (для обновления данных)
    """
    global _product_mapping_cache, _markup_rules_cache
    _product_mapping_cache = None
    _markup_rules_cache = None


# Таблица толщин и покрытий для профнастила
PROFNASTIL_THICKNESS_COATING = {
    # Цинк (Zn) - толщины
    "zn_0.3": {"coating": "Цинк", "thickness": "0,3", "coating_code": "Zn"},
    "zn_0.35": {"coating": "Цинк", "thickness": "0,35", "coating_code": "Zn"},
    "zn_0.4": {"coating": "Цинк", "thickness": "0,4", "coating_code": "Zn"},
    "zn_0.45": {"coating": "Цинк", "thickness": "0,45", "coating_code": "Zn"},
    "zn_0.5": {"coating": "Цинк", "thickness": "0,5", "coating_code": "Zn"},
    "zn_0.55": {"coating": "Цинк", "thickness": "0,55", "coating_code": "Zn"},
    "zn_0.6": {"coating": "Цинк", "thickness": "0,6", "coating_code": "Zn"},
    
    # Полиэстер (PE) - толщины
    "pe_op": {"coating": "Полиэстер", "thickness": "Оп", "coating_code": "PE"},
    "pe_0.35": {"coating": "Полиэстер", "thickness": "0,35", "coating_code": "PE"},
    "pe_0.4": {"coating": "Полиэстер", "thickness": "0,4", "coating_code": "PE"},
    "pe_0.45": {"coating": "Полиэстер", "thickness": "0,45", "coating_code": "PE"},
    "pe_0.5": {"coating": "Полиэстер", "thickness": "0,5", "coating_code": "PE"},
    "pe_0.4_dvs": {"coating": "Полиэстер", "thickness": "0,4двс", "coating_code": "PE"},
    "pe_0.45_dvs": {"coating": "Полиэстер", "thickness": "0,45двс", "coating_code": "PE"},
}


def extract_base_name(product_name: str) -> str:
    """
    Извлекает базовое название товара (до скобок и спецсимволов)
    """
    # Убираем размеры в скобках
    name = re.sub(r'\([^)]*\)', '', product_name)
    # Убираем лишние пробелы
    name = re.sub(r'\s+', ' ', name).strip()
    return name

def find_product_mapping(product_name: str) -> Optional[Dict[str, Any]]:
    """
    Находит соответствие товара в таблице категорий из БД
    """
    base_name = extract_base_name(product_name)
    product_mapping = get_product_mapping()
    
    # Точное совпадение
    if base_name in product_mapping:
        return product_mapping[base_name]
    
    # Частичное совпадение
    for key, value in product_mapping.items():
        if key in base_name or base_name in key:
            return value
    
    return None

def get_applicable_markups(product_name: str, coating: str = None) -> List[Dict[str, Any]]:
    """
    Возвращает применимые наценки для товара из БД
    Фильтрует только наценки для Дружный (НН) или всех регионов
    """
    applicable = []
    markup_rules = get_markup_rules()
    
    for markup in markup_rules:
        # Проверяем регион - только "all" или регионы, включающие НН (Дружный)
        region = markup["region"]
        if region not in ["all", "spb_nn_kirov_penza"]:
            continue
            
        # Проверяем, подходит ли покрытие
        if coating and markup["coating"] not in coating:
            continue
            
        applicable.append(markup)
    
    return applicable

def parse_profnastil_price(price_str: str) -> List[Dict[str, Any]]:
    """
    Парсит сложные цены профнастила с определением толщины и покрытия
    Пример: "362 sf" -> [{"price": 362, "brand": "sf", "thickness": "0,3", "coating": "Цинк"}]
    Пример: "399оп//439гл/421мп" -> [{"price": 399, "brand": "оп", ...}, {"price": 439, "brand": "гл", ...}]
    """
    results = []
    
    # Разделяем по // и /
    parts = re.split(r'[/]{1,2}', price_str)
    
    for part in parts:
        part = part.strip()
        if not part or part == "-":
            continue
            
        # Ищем цену и бренд
        match = re.match(r'(\d+)\s*([а-яa-z]*)', part, re.IGNORECASE)
        if match:
            price = int(match.group(1))
            brand = match.group(2).lower() if match.group(2) else None
            
            # Определяем толщину и покрытие по бренду
            thickness, coating = determine_thickness_coating(brand, price)
            
            results.append({
                "price": price,
                "brand": brand,
                "thickness": thickness,
                "coating": coating
            })
    
    return results

def determine_thickness_coating(brand: str, price: int) -> tuple:
    """
    Определяет толщину и покрытие по бренду и цене
    """
    if not brand:
        return "0,35", "Цинк"  # По умолчанию
    
    brand = brand.lower()
    
    # Определяем покрытие
    if brand in ["оп", "op"]:
        coating = "Полиэстер"
        thickness = "Оп"
    elif brand in ["sf"]:
        coating = "Цинк"
        # Для sf определяем толщину по цене (примерная логика)
        if price < 380:
            thickness = "0,3"
        elif price < 400:
            thickness = "0,35"
        elif price < 450:
            thickness = "0,4"
        elif price < 500:
            thickness = "0,45"
        elif price < 550:
            thickness = "0,5"
        else:
            thickness = "0,55"
    elif brand in ["гл", "gl"]:
        coating = "Полиэстер"
        # Для гл определяем толщину по цене
        if price < 400:
            thickness = "0,35"
        elif price < 450:
            thickness = "0,4"
        elif price < 500:
            thickness = "0,45"
        else:
            thickness = "0,5"
    elif brand in ["мп", "mp"]:
        coating = "Полиэстер"
        # Для мп определяем толщину по цене
        if price < 400:
            thickness = "0,35"
        elif price < 450:
            thickness = "0,4"
        elif price < 500:
            thickness = "0,45"
        else:
            thickness = "0,5"
    elif "двс" in brand or "dvs" in brand:
        coating = "Полиэстер"
        thickness = "0,4двс" if "0.4" in brand or price < 550 else "0,45двс"
    else:
        coating = "Цинк"
        thickness = "0,35"
    
    return thickness, coating

def is_profnastil_product(product_name: str) -> bool:
    """
    Проверяет, является ли товар профнастилом
    """
    name_lower = product_name.lower()
    
    # Точные совпадения для профнастила
    profnastil_exact = [
        "профнастил", "плоский лист", "мп-10", "с-8", "с-20", "с-21", 
        "с-44", "нс-35", "gl-10", "c10"
    ]
    
    # Проверяем точные совпадения
    for keyword in profnastil_exact:
        if keyword in name_lower:
            return True
    
    # Исключаем товары, которые точно НЕ профнастил
    exclude_keywords = ["кредо", "монтекристо", "классик", "модерн", "квадро", "камея", "квинта", "ламонтерра", "трамонтана"]
    for exclude in exclude_keywords:
        if exclude in name_lower:
            return False
    
    return False

def process_profnastil_product(product: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Обрабатывает товары профнастила с определением толщины и покрытия
    """
    variants = []
    
    # Находим категорию товара
    mapping = find_product_mapping(product["parsed_name"])
    if not mapping:
        return variants
    
    # Если есть информация о толщине и покрытии из парсинга цен
    if "thickness" in product and "coating" in product:
        thickness = product["thickness"]
        coating = product["coating"]
        
        # Создаем вариант с определенной толщиной и покрытием
        variant = {
            "original_name": product["original_name"],
            "parsed_name": product["parsed_name"],
            "category_id": mapping["category_id"],
            "unit": mapping["unit"],
            "base_price": product["price"],
            "final_price": product["price"],  # Для профнастила пока без наценок
            "markup": 0,
            "thickness": thickness,
            "coating": coating,
            "brand": product.get("brand"),
            "sheet": product.get("sheet"),
            "product_type": "profnastil"
        }
        variants.append(variant)
    else:
        # Если нет информации о толщине/покрытии, создаем базовый вариант
        variant = {
            "original_name": product["original_name"],
            "parsed_name": product["parsed_name"],
            "category_id": mapping["category_id"],
            "unit": mapping["unit"],
            "base_price": product["price"],
            "final_price": product["price"],
            "markup": 0,
            "thickness": "0,35",  # По умолчанию
            "coating": "Цинк",    # По умолчанию
            "brand": product.get("brand"),
            "sheet": product.get("sheet"),
            "product_type": "profnastil"
        }
        variants.append(variant)
    
    return variants

def process_standard_product(product: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Обрабатывает обычные товары (не профнастил)
    """
    variants = []
    
    # Находим категорию товара
    mapping = find_product_mapping(product["parsed_name"])
    if not mapping:
        return variants
        
    # Находим применимые наценки
    markups = get_applicable_markups(product["parsed_name"], product.get("coating"))
    
    # Создаем варианты товара с разными цветами/покрытиями
    for markup in markups:
        final_price = product["price"] + markup["markup"]
        
        variant = {
            "original_name": product["original_name"],
            "parsed_name": product["parsed_name"],
            "category_id": mapping["category_id"],
            "unit": mapping["unit"],
            "base_price": product["price"],
            "final_price": final_price,
            "markup": markup["markup"],
            "color": markup["color"],
            "coating": markup["coating"],
            "region": markup["region"],
            "brand": product.get("brand"),
            "sheet": product.get("sheet"),
            "product_type": "standard"
        }
        
        variants.append(variant)
    
    return variants

def apply_business_rules(products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Применяет бизнес-правила: категории, наценки, создание вариантов по цветам
    Специальная обработка для профнастила с толщиной и покрытием
    """
    enriched_products = []
    
    for product in products:
        # Проверяем, является ли товар профнастилом
        if is_profnastil_product(product["parsed_name"]):
            # Специальная обработка профнастила
            profnastil_variants = process_profnastil_product(product)
            enriched_products.extend(profnastil_variants)
        else:
            # Обычная обработка товаров
            standard_variants = process_standard_product(product)
            enriched_products.extend(standard_variants)
    
    return enriched_products
