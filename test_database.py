#!/usr/bin/env python3
"""
Тестовый скрипт для проверки интеграции с базой данных
"""

from business_logic import get_product_mapping, get_markup_rules, clear_cache
from database import get_db_manager

def test_database_connection():
    """Тест подключения к базе данных"""
    print("=== Тест подключения к базе данных ===")
    
    db = get_db_manager()
    if db.connect():
        print("✓ Подключение к базе данных успешно")
        db.disconnect()
        return True
    else:
        print("✗ Ошибка подключения к базе данных")
        return False

def test_product_categories():
    """Тест получения категорий товаров"""
    print("\n=== Тест получения категорий товаров ===")
    
    try:
        categories = get_product_mapping()
        print(f"Получено категорий: {len(categories)}")
        
        # Показываем несколько примеров
        for i, (name, info) in enumerate(categories.items()):
            if i < 5:  # Показываем первые 5
                print(f"  {name}: category_id={info['category_id']}, unit={info['unit']}")
        
        if len(categories) > 5:
            print(f"  ... и еще {len(categories) - 5} категорий")
        
        return True
        
    except Exception as e:
        print(f"✗ Ошибка получения категорий: {e}")
        return False

def test_markup_rules():
    """Тест получения правил наценок"""
    print("\n=== Тест получения правил наценок ===")
    
    try:
        markups = get_markup_rules()
        print(f"Получено правил наценок: {len(markups)}")
        
        # Показываем все правила
        for markup in markups:
            print(f"  {markup['color']} | {markup['coating']} | {markup['region']} | +{markup['markup']}₽")
        
        return True
        
    except Exception as e:
        print(f"✗ Ошибка получения наценок: {e}")
        return False

def test_cache_functionality():
    """Тест функциональности кэша"""
    print("\n=== Тест кэширования ===")
    
    try:
        # Первый вызов - загрузка из БД
        print("Первый вызов (загрузка из БД)...")
        categories1 = get_product_mapping()
        
        # Второй вызов - из кэша
        print("Второй вызов (из кэша)...")
        categories2 = get_product_mapping()
        
        # Проверяем, что данные одинаковые
        if categories1 == categories2:
            print("✓ Кэширование работает корректно")
        else:
            print("✗ Ошибка кэширования - данные отличаются")
            return False
        
        # Очищаем кэш
        print("Очистка кэша...")
        clear_cache()
        
        # Третий вызов - снова из БД
        print("Третий вызов (после очистки кэша)...")
        categories3 = get_product_mapping()
        
        if categories1 == categories3:
            print("✓ Очистка кэша работает корректно")
            return True
        else:
            print("✗ Ошибка очистки кэша")
            return False
            
    except Exception as e:
        print(f"✗ Ошибка тестирования кэша: {e}")
        return False

def main():
    """Запуск всех тестов"""
    print("Запуск тестов интеграции с базой данных...\n")
    
    tests = [
        ("Подключение к БД", test_database_connection),
        ("Категории товаров", test_product_categories),
        ("Правила наценок", test_markup_rules),
        ("Кэширование", test_cache_functionality),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ Критическая ошибка в тесте '{test_name}': {e}")
            results.append((test_name, False))
    
    # Итоговый отчет
    print("\n" + "="*50)
    print("ИТОГОВЫЙ ОТЧЕТ")
    print("="*50)
    
    passed = 0
    for test_name, result in results:
        status = "✓ ПРОЙДЕН" if result else "✗ ПРОВАЛЕН"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nПройдено тестов: {passed}/{len(results)}")
    
    if passed == len(results):
        print("🎉 Все тесты пройдены успешно!")
    else:
        print("⚠️  Некоторые тесты провалены. Проверьте конфигурацию базы данных.")

if __name__ == "__main__":
    main()
