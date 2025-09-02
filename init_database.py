#!/usr/bin/env python3
"""
Скрипт для инициализации базы данных MySQL
Создает таблицы и заполняет их начальными данными
"""

from database import get_db_manager

def main():
    """Инициализация базы данных"""
    print("Инициализация базы данных...")
    
    db = get_db_manager()
    
    # Подключаемся к базе данных
    if not db.connect():
        print("Ошибка подключения к базе данных")
        return False
    
    try:
        # Создаем таблицы
        print("Создание таблиц...")
        db.create_tables()
        
        # Заполняем начальными данными
        print("Заполнение начальными данными...")
        db.populate_initial_data()
        
        print("База данных успешно инициализирована!")
        return True
        
    except Exception as e:
        print(f"Ошибка инициализации базы данных: {e}")
        return False
    
    finally:
        db.disconnect()

if __name__ == "__main__":
    main()
