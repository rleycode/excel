#!/usr/bin/env python3
"""
Скрипт для отладки API ошибки
"""

from excel_parser import parse_excel_file
from price_parser import parse_excel_rows
from business_logic import apply_business_rules

def debug_pipeline():
    """Тестирует весь пайплайн обработки"""
    print("=== Отладка пайплайна обработки ===")
    
    # Создаем тестовые данные, имитирующие Excel
    test_data = {
        "Лист1": [
            ["Профнастил С-8", "м2", "362sf"],
            ["Кредо GL", "м2", "738гл/775мп"],
            ["МП-10", "м2", "399оп//439гл/421мп"]
        ]
    }
    
    try:
        print("1. Тестовые данные созданы")
        print(f"   Листов: {len(test_data)}")
        print(f"   Строк: {sum(len(sheet) for sheet in test_data.values())}")
        
        print("\n2. Парсинг строк...")
        normalized = parse_excel_rows(test_data)
        print(f"   Товаров после парсинга: {len(normalized)}")
        
        for product in normalized[:3]:  # Показываем первые 3
            print(f"   - {product['parsed_name']}: {product['price']} руб")
            if 'thickness' in product:
                print(f"     Толщина: {product['thickness']}, Покрытие: {product['coating']}")
        
        print("\n3. Применение бизнес-правил...")
        enriched = apply_business_rules(normalized)
        print(f"   Вариантов после обогащения: {len(enriched)}")
        
        for variant in enriched[:3]:  # Показываем первые 3
            print(f"   - {variant['parsed_name']}: {variant['final_price']} руб")
            print(f"     Категория: {variant.get('category_id', 'N/A')}")
            if 'thickness' in variant:
                print(f"     Толщина: {variant['thickness']}, Покрытие: {variant['coating']}")
        
        print("\n✓ Пайплайн работает корректно")
        return True
        
    except Exception as e:
        print(f"\n✗ Ошибка в пайплайне: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_pipeline()
