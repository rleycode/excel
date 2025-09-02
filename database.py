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
        
        # SSL настройки
        self.ssl_disabled = os.getenv('DB_SSL_DISABLED', 'false').lower() == 'true'
        self.ssl_ca = os.getenv('DB_SSL_CA_PATH')
        self.ssl_cert = os.getenv('DB_SSL_CERT_PATH')
        self.ssl_key = os.getenv('DB_SSL_KEY_PATH')
        
        # Дополнительные настройки подключения
        self.connection_timeout = int(os.getenv('DB_CONNECTION_TIMEOUT', 30))
        self.autocommit = os.getenv('DB_AUTOCOMMIT', 'true').lower() == 'true'

    def connect(self):
        """Подключение к базе данных с поддержкой SSL"""
        try:
            # Базовые параметры подключения
            connection_config = {
                'host': self.host,
                'port': self.port,
                'user': self.user,
                'password': self.password,
                'database': self.database,
                'charset': 'utf8mb4',
                'collation': 'utf8mb4_unicode_ci',
                'autocommit': self.autocommit,
                'connection_timeout': self.connection_timeout,
                'raise_on_warnings': True,
                'use_unicode': True
            }
            
            # SSL настройки
            if not self.ssl_disabled:
                ssl_config = {}
                if self.ssl_ca:
                    ssl_config['ca'] = self.ssl_ca
                if self.ssl_cert:
                    ssl_config['cert'] = self.ssl_cert
                if self.ssl_key:
                    ssl_config['key'] = self.ssl_key
                
                if ssl_config:
                    connection_config['ssl'] = ssl_config
                else:
                    # Для облачных провайдеров обычно нужно только ssl_disabled=False
                    connection_config['ssl_disabled'] = False
            else:
                connection_config['ssl_disabled'] = True
            
            self.connection = mysql.connector.connect(**connection_config)
            
            if self.connection.is_connected():
                print(f"Подключение к MySQL базе данных '{self.database}' на {self.host} успешно")
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
        SELECT name_ru, category_id, unit 
        FROM category_mapping 
        ORDER BY name_ru
        """
        
        result = self.execute_query(query)
        categories = {}
        
        for row in result:
            categories[row['name_ru']] = {
                'category_id': str(row['category_id']),
                'unit': row['unit']
            }
        
        return categories

    def get_markup_rules(self) -> List[Dict[str, Any]]:
        """Получение правил наценок из БД"""
        query = """
        SELECT color, coating, thickness, markup_price, markup_percent
        FROM color_coating_markup 
        ORDER BY color, coating, thickness
        """
        
        result = self.execute_query(query)
        # Преобразуем в формат, ожидаемый business_logic
        markup_rules = []
        for row in result:
            markup_rules.append({
                'color': row['color'],
                'coating': row['coating'],
                'thickness': row.get('thickness', ''),
                'region': 'all',  # Предполагаем, что все правила применимы везде
                'markup': float(row['markup_price']) if row['markup_price'] else 0.0,
                'unit_markup': float(row['markup_percent']) if row['markup_percent'] else 0.0
            })
        
        return markup_rules

    def create_tables(self):
        """Создание таблиц в базе данных (если они не существуют)"""
        
        # Таблица категорий товаров (соответствует существующей category_mapping)
        create_categories_table = """
        CREATE TABLE IF NOT EXISTS category_mapping (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name_ru VARCHAR(255) NOT NULL,
            unit VARCHAR(10) NOT NULL DEFAULT 'м2',
            category_id VARCHAR(50) NOT NULL,
            INDEX idx_name_ru (name_ru),
            INDEX idx_category_id (category_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """

        # Таблица правил наценок (соответствует существующей color_coating_markup)
        create_markup_table = """
        CREATE TABLE IF NOT EXISTS color_coating_markup (
            id INT AUTO_INCREMENT PRIMARY KEY,
            color VARCHAR(50) NOT NULL,
            coating VARCHAR(100) NOT NULL,
            thickness VARCHAR(20),
            markup_price DECIMAL(10,2),
            markup_percent DECIMAL(5,2),
            INDEX idx_color (color),
            INDEX idx_coating (coating),
            INDEX idx_thickness (thickness)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """

        if self.execute_update(create_categories_table):
            print("Таблица category_mapping создана/обновлена")
        
        if self.execute_update(create_markup_table):
            print("Таблица color_coating_markup создана/обновлена")

    def populate_initial_data(self):
        """Заполнение таблиц начальными данными из предоставленной схемы"""
        
        # Данные категорий товаров (из таблицы category_mapping)
        categories_data = [
            ("Кредо GL", "м2", "1156"),
            ("Классик GL", "м2", "1145"),
            ("Камея GL", "м2", "1155"),
            ("Квинта+GL", "м2", "1157"),
            ("Модерн GL", "м2", "1144"),
            ("Квадро Профи GL", "м2", "1146"),
            ("Ламонтерра МП", "м2", "2262"),
            ("Ламонтерра Х МП", "м2", "2266"),
            ("Монтекристо S", "м2", "2263"),
            ("Монтерроса S МП", "м2", "2265"),
            ("Трамонтана S МП", "м2", "2264"),
            ("Профиль мет. тип \"Монтеррей\"", "м2", "2393"),
            ("Профнастил С-8", "м2", "2291"),
            ("Профнастил C10 фигурный", "м2", "2393"),
            ("Профнастил МП-10", "м2", "1142"),
            ("Профнастил GL-10", "м2", "1142"),
            ("Профнастил C10", "м2", "1142"),
            ("Профнастил С-20", "м2", "1140"),
            ("Профнастил С-21", "м2", "1141"),
            ("Профнастил С-44", "м2", "2258"),
            ("Профнастил НС-35", "м2", "1148"),
            ("Плоский лист", "м2", "1393"),
        ]

        # Базовые данные наценок (примеры для color_coating_markup)
        markup_data = [
            ("1015", "PE 0,45", "0,45", 7.0, 0.7),
            ("1018", "Satin", "0,5", 50.0, 5.0),
            ("standard", "PE 0,45 двс", "0,45", 50.0, 5.0),
            ("standard", "PE 0,7", "0,7", 50.0, 5.0),
            ("standard", "PE 0,8", "0,8", 55.0, 5.5),
        ]

        # Вставка категорий
        insert_category_query = """
        INSERT IGNORE INTO category_mapping (name_ru, unit, category_id) 
        VALUES (%s, %s, %s)
        """
        
        for category in categories_data:
            self.execute_update(insert_category_query, category)

        # Вставка наценок
        insert_markup_query = """
        INSERT IGNORE INTO color_coating_markup (color, coating, thickness, markup_price, markup_percent) 
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
