#!/usr/bin/env python3
"""
Тестовый скрипт для проверки парсинга профнастила
"""

from business_logic import parse_profnastil_price, is_profnastil_product, process_profnastil_product
from price_parser import parse_excel_rows

def test_profnastil_detection():
    """Тест определения профнастила"""
    print("=== Тест определения профнастила ===")
    
    test_names = [
        "Профнастил С-8",
        "МП-10", 
        "Плоский лист",
        "Кредо GL",  # не профнастил
        "С-20 оцинкованный",
        "Профнастил GL-10"
    ]
    
    for name in test_names:
        is_prof = is_profnastil_product(name)
        print(f"{name}: {'✓ профнастил' if is_prof else '✗ не профнастил'}")

def test_profnastil_price_parsing():
    """Тест парсинга цен профнастила"""
    print("\n=== Тест парсинга цен профнастила ===")
    
    test_prices = [
        "362sf",
        "399оп//439гл/421мп", 
        "450гл/480мп",
        "520двс"
    ]
    
    for price_str in test_prices:
        print(f"\nЦена: {price_str}")
        parsed = parse_profnastil_price(price_str)
        for item in parsed:
            print(f"  - {item['price']} руб, бренд: {item['brand']}, толщина: {item['thickness']}, покрытие: {item['coating']}")

def test_full_processing():
    """Тест полной обработки профнастила"""
    print("\n=== Тест полной обработки ===")
    
    # Имитируем данные из Excel
    test_product = {
        "original_name": "Профнастил С-8",
        "parsed_name": "Профнастил С-8", 
        "unit": "м2",
        "price": 362,
        "brand": "sf",
        "thickness": "0,3",
        "coating": "Цинк",
        "sheet": "Лист1"
    }
    
    variants = process_profnastil_product(test_product)
    print(f"Создано вариантов: {len(variants)}")
    
    for variant in variants:
        print(f"  - {variant['parsed_name']}: {variant['final_price']} руб/м2")
        print(f"    Толщина: {variant['thickness']}, Покрытие: {variant['coating']}")

if __name__ == "__main__":
    test_profnastil_detection()
    test_profnastil_price_parsing()
    test_full_processing()
    print("\n✓ Все тесты завершены")
