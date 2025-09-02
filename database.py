#!/usr/bin/env python3
"""
Модуль для работы с MySQL базой данных
"""

import mysql.connector
from mysql.connector import Error
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = int(os.getenv('DB_PORT', 3306))
        self.user = os.getenv('DB_USER')
        self.password = os.getenv('DB_PASSWORD')
        self.database = os.getenv('DB_NAME')

    def connect(self):
        """Подключение к базе данных"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci'
            )
            if self.connection.is_connected():
                print(f"Подключение к MySQL базе данных '{self.database}' успешно")
                return True
        except Error as e:
            print(f"Ошибка подключения к MySQL: {e}")
            return False

    def disconnect(self):
        """Отключение от базы данных"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Соединение с MySQL закрыто")

    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Выполнение SELECT запроса"""
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return []

        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params)
            result = cursor.fetchall()
            cursor.close()
            return result
        except Error as e:
            print(f"Ошибка выполнения запроса: {e}")
            return []

    def execute_update(self, query: str, params: tuple = None) -> bool:
        """Выполнение INSERT/UPDATE/DELETE запроса"""
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return False

        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"Ошибка выполнения обновления: {e}")
            self.connection.rollback()
            return False

    def get_product_categories(self) -> Dict[str, Dict[str, str]]:
        """Получение соответствия товаров и категорий из БД"""
        query = """
        SELECT product_name, category_id, unit 
        FROM product_categories 
        WHERE is_active = 1
        ORDER BY product_name
        """
        
        result = self.execute_query(query)
        categories = {}
        
        for row in result:
            categories[row['product_name']] = {
                'category_id': str(row['category_id']),
                'unit': row['unit']
            }
        
        return categories

    def get_markup_rules(self) -> List[Dict[str, Any]]:
        """Получение правил наценок из БД"""
        query = """
        SELECT color, coating, region, markup, unit_markup
        FROM markup_rules 
        WHERE is_active = 1 
        AND (region = 'all' OR region = 'spb_nn_kirov_penza')
        ORDER BY color, coating, region
        """
        
        result = self.execute_query(query)
        return result

    def create_tables(self):
        """Создание таблиц в базе данных"""
        
        # Таблица категорий товаров
        create_categories_table = """
        CREATE TABLE IF NOT EXISTS product_categories (
            id INT AUTO_INCREMENT PRIMARY KEY,
            product_name VARCHAR(255) NOT NULL UNIQUE,
            category_id VARCHAR(50) NOT NULL,
            unit VARCHAR(10) NOT NULL DEFAULT 'м2',
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_product_name (product_name),
            INDEX idx_category_id (category_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """

        # Таблица правил наценок
        create_markup_table = """
        CREATE TABLE IF NOT EXISTS markup_rules (
            id INT AUTO_INCREMENT PRIMARY KEY,
            color VARCHAR(50) NOT NULL,
            coating VARCHAR(100) NOT NULL,
            region VARCHAR(100) NOT NULL,
            markup DECIMAL(10,2) NOT NULL,
            unit_markup DECIMAL(10,2) NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_color (color),
            INDEX idx_coating (coating),
            INDEX idx_region (region)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """

        if self.execute_update(create_categories_table):
            print("Таблица product_categories создана/обновлена")
        
        if self.execute_update(create_markup_table):
            print("Таблица markup_rules создана/обновлена")

    def populate_initial_data(self):
        """Заполнение таблиц начальными данными"""
        
        # Данные категорий товаров
        categories_data = [
            ("Кредо GL", "1156", "м2"),
            ("Монтекристо S", "1157", "м2"),
            ("Классик GL", "1158", "м2"),
            ("Модерн GL", "1159", "м2"),
            ("Квадро Профи GL", "1160", "м2"),
            ("Ламонтерра МП", "1161", "м2"),
            ("Ламонтерра Х МП", "1162", "м2"),
            ("Камея GL", "1163", "м2"),
            ("Квинта+GL", "1164", "м2"),
            ("Трамонтана S МП", "1165", "м2"),
            ("Профнастил С-8", "2001", "м2"),
            ("МП-10", "2002", "м2"),
            ("Профнастил GL-10", "2003", "м2"),
            ("C10", "2004", "м2"),
            ("Профнастил С10 фигурный", "2005", "м2"),
            ("Профнастил С-20", "2006", "м2"),
            ("Профнастил С-21", "2007", "м2"),
            ("С-44", "2008", "м2"),
            ("Профнастил НС-35", "2009", "м2"),
            ("Плоский лист", "2010", "м2"),
        ]

        # Данные наценок
        markup_data = [
            ("1015", "PE 0,45", "spb_nn_kirov_penza", 7.0, 0.7),
            ("1018", "Satin", "all", 50.0, 5.0),
            ("standard", "PE 0,45 двс", "all", 50.0, 5.0),
            ("standard", "PE 0,7", "all", 50.0, 5.0),
            ("standard", "PE 0,8", "all", 55.0, 5.5),
        ]

        # Вставка категорий
        insert_category_query = """
        INSERT IGNORE INTO product_categories (product_name, category_id, unit) 
        VALUES (%s, %s, %s)
        """
        
        for category in categories_data:
            self.execute_update(insert_category_query, category)

        # Вставка наценок
        insert_markup_query = """
        INSERT IGNORE INTO markup_rules (color, coating, region, markup, unit_markup) 
        VALUES (%s, %s, %s, %s, %s)
        """
        
        for markup in markup_data:
            self.execute_update(insert_markup_query, markup)

        print("Начальные данные загружены в базу данных")

# Глобальный экземпляр менеджера БД
db_manager = DatabaseManager()

def get_db_manager() -> DatabaseManager:
    """Получение экземпляра менеджера БД"""
    return db_manager
