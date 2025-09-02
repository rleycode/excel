#!/usr/bin/env python3
"""
Тест улучшенного парсинга названий товаров
"""

from name_parser import extract_individual_products

def test_name_parsing():
    """Тестирует разделение составных названий"""
    print("=== Тест разделения составных названий ===")
    
    test_cases = [
        "Квинта+GL(1210,1150)/   Трамонтана S МП(1195,1155)",
        "Профнастил GL-10 (1180,1150),C10(1154,1100)sf", 
        "Профнастил С-21 (1051,1000),    С-44(1047,1000)",
        "Ламонтерра МП(1190,1100) Ламонтерра Х МП(1190.1100)",
        "Кредо GL(1190,1125)//Монтекристо S"
    ]
    
    for name in test_cases:
        print(f"\nИсходное название:")
        print(f"  {name}")
        
        parsed = extract_individual_products(name)
        print(f"Разделено на {len(parsed)} товар(ов):")
        for i, product in enumerate(parsed, 1):
            print(f"  {i}. {product}")

if __name__ == "__main__":
    test_name_parsing()
