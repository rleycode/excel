import re
from typing import List, Dict, Any
from name_parser import parse_names, extract_individual_products
from business_logic import parse_profnastil_price, is_profnastil_product

def parse_prices(price_str: str) -> List[Dict[str, Any]]:
    """
    Разбирает строку вида '738гл/775мп' → [{'price': 738, 'brand': 'гл'}, {'price': 775, 'brand': 'мп'}]
    """
    prices = []
    for part in re.split(r"[\/]+", price_str):
        part = part.strip()
        if not part or part == "-":
            continue
        match = re.match(r"(\d+)([а-яa-z]*)", part, re.IGNORECASE)
        if match:
            prices.append({
                "price": int(match.group(1)),
                "brand": match.group(2).lower() if match.group(2) else None
            })
    return prices


def match_names_and_prices(name_str: str, price_str: str) -> List[Dict[str, Any]]:
    """
    Связывает названия и цены из одной строки Excel
    """
    names = parse_names(name_str)
    prices = parse_prices(price_str)
    
    results = []
    for i, price_data in enumerate(prices):
        name = names[i] if i < len(names) else names[0] if names else name_str
        results.append({
            "name": name,
            "price": price_data["price"],
            "brand": price_data["brand"]
        })
    return results

def parse_excel_rows(excel_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Обрабатывает все строки из Excel и возвращает нормализованный список товаров
    """
    products = []
    
    for sheet_name, sheet_data in excel_data.items():
        if not sheet_data:
            continue
            
        for row in sheet_data:
            if len(row) < 3:
                continue
                
            name = str(row[0]).strip() if row[0] else ""
            unit = str(row[1]).strip() if row[1] else ""
            price = str(row[2]).strip() if row[2] else ""
            
            if not name or not price or price == "-" or not re.search(r'\d', price):
                continue
                
            # Проверяем, есть ли в цене суффиксы брендов (гл, мп, sf, оп)
            if re.search(r'\d+(гл|мп|sf|оп|двс)', price):
                # Проверяем, является ли товар профнастилом
                if is_profnastil_product(name):
                    # Специальная обработка профнастила с толщиной и покрытием
                    profnastil_prices = parse_profnastil_price(price)
                    names = extract_individual_products(name)
                    
                    for i, price_data in enumerate(profnastil_prices):
                        parsed_name = names[i] if i < len(names) else names[0] if names else name
                        products.append({
                            "original_name": name,
                            "parsed_name": parsed_name,
                            "unit": unit,
                            "price": price_data["price"],
                            "brand": price_data["brand"],
                            "thickness": price_data["thickness"],
                            "coating": price_data["coating"],
                            "sheet": sheet_name
                        })
                else:
                    # Обычная обработка с брендами
                    parsed_products = match_names_and_prices(name, price)
                    
                    for product in parsed_products:
                        products.append({
                            "original_name": name,
                            "parsed_name": product["name"],
                            "unit": unit,
                            "price": product["price"],
                            "brand": product["brand"],
                            "sheet": sheet_name
                        })
            else:
                # Простая цена - берем первое число
                price_match = re.search(r'(\d+)', price)
                if price_match:
                    price_value = int(price_match.group(1))
                    
                    # Разделяем составные названия
                    names = extract_individual_products(name)
                    for parsed_name in names:
                        products.append({
                            "original_name": name,
                            "parsed_name": parsed_name,
                            "unit": unit,
                            "price": price_value,
                            "brand": None,
                            "sheet": sheet_name
                        })
    
    return products
