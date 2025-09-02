# Настройка удаленной базы данных

## Рекомендуемые облачные провайдеры

### 1. PlanetScale (Рекомендуется)
- **Бесплатный план**: 1 база данных, 1 GB хранилища
- **Преимущества**: Serverless, автоматическое масштабирование, веб-интерфейс
- **Регистрация**: https://planetscale.com/

#### Настройка PlanetScale:
1. Создайте аккаунт на PlanetScale
2. Создайте новую базу данных `excel-parser`
3. Получите строку подключения из Dashboard
4. Обновите `.env` файл:

```env
DB_HOST=aws.connect.psdb.cloud
DB_PORT=3306
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=excel-parser
DB_SSL_DISABLED=false
```

### 2. Railway
- **Бесплатный план**: $5 кредитов в месяц
- **Преимущества**: Простое развертывание, автоматические бэкапы
- **Регистрация**: https://railway.app/

#### Настройка Railway:
1. Создайте проект на Railway
2. Добавьте MySQL сервис
3. Скопируйте данные подключения из Variables
4. Обновите `.env` файл

### 3. Aiven
- **Бесплатный план**: 1 месяц бесплатно
- **Преимущества**: Управляемый MySQL, SSL по умолчанию
- **Регистрация**: https://aiven.io/

## Настройка локального файла .env

После получения данных от провайдера, обновите файл `.env`:

```env
# Удаленная база данных
DB_HOST=your-database-host.com
DB_PORT=3306
DB_USER=your_username
DB_PASSWORD=your_secure_password
DB_NAME=excel_parser_db

# SSL настройки (обычно для облачных БД)
DB_SSL_DISABLED=false
```

## Инициализация удаленной базы данных

После настройки подключения:

1. **Установите зависимости**:
```bash
pip install mysql-connector-python python-dotenv
```

2. **Инициализируйте базу данных**:
```bash
python init_database.py
```

3. **Протестируйте подключение**:
```bash
python test_database.py
```

## Безопасность

### Рекомендации:
- ✅ Используйте SSL подключения (DB_SSL_DISABLED=false)
- ✅ Создайте отдельного пользователя БД с ограниченными правами
- ✅ Используйте сложные пароли
- ✅ Не коммитьте файл `.env` в Git (уже в .gitignore)

### Создание пользователя БД с ограниченными правами:
```sql
CREATE USER 'excel_parser'@'%' IDENTIFIED BY 'secure_password';
GRANT SELECT, INSERT, UPDATE, DELETE ON excel_parser_db.* TO 'excel_parser'@'%';
FLUSH PRIVILEGES;
```

## Альтернативы для разработки

### SQLite (для локальной разработки)
Если хотите избежать настройки MySQL, можно использовать SQLite:

1. Установите: `pip install sqlite3`
2. Создайте `database_sqlite.py` с аналогичным интерфейсом
3. Переключайтесь между БД через переменную окружения

### Docker MySQL (локально)
```bash
docker run --name mysql-excel -e MYSQL_ROOT_PASSWORD=password -e MYSQL_DATABASE=excel_parser_db -p 3306:3306 -d mysql:8.0
```

## Миграция данных

Если у вас уже есть данные в локальной БД:

1. **Экспорт данных**:
```bash
mysqldump -u root -p excel_parser_db > backup.sql
```

2. **Импорт в удаленную БД**:
```bash
mysql -h remote-host -u username -p excel_parser_db < backup.sql
```

## Мониторинг и логи

Система автоматически логирует:
- ✅ Успешные подключения
- ✅ Ошибки подключения
- ✅ Время выполнения запросов
- ✅ Использование кэша

Проверьте логи в консоли при запуске приложения.
