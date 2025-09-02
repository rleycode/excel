# Настройка MySQL на Ubuntu сервере для Excel Parser

## 1. Подготовка MySQL на Ubuntu сервере

### Подключитесь к серверу по SSH:
```bash
ssh username@your-server-ip
```

### Войдите в MySQL как root:
```bash
sudo mysql -u root -p
```

## 2. Создание базы данных и пользователя

```sql
-- Создаем базу данных
CREATE DATABASE excel_parser_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Создаем пользователя для удаленного подключения
CREATE USER 'excel_parser_user'@'%' IDENTIFIED BY 'your_secure_password_here';

-- Даем права на базу данных
GRANT ALL PRIVILEGES ON excel_parser_db.* TO 'excel_parser_user'@'%';

-- Применяем изменения
FLUSH PRIVILEGES;

-- Проверяем созданного пользователя
SELECT User, Host FROM mysql.user WHERE User = 'excel_parser_user';

-- Выходим
EXIT;
```

## 3. Настройка MySQL для удаленных подключений

### Редактируем конфигурацию MySQL:
```bash
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf
```

### Найдите и измените строку:
```ini
# Было:
bind-address = 127.0.0.1

# Стало (для всех IP):
bind-address = 0.0.0.0

# Или для конкретного IP:
bind-address = your-server-ip
```

### Перезапустите MySQL:
```bash
sudo systemctl restart mysql
sudo systemctl status mysql
```

## 4. Настройка файрвола (если используется UFW)

```bash
# Разрешаем подключения к MySQL
sudo ufw allow 3306/tcp

# Или только с конкретного IP
sudo ufw allow from your-client-ip to any port 3306

# Проверяем статус
sudo ufw status
```

## 5. Обновите .env файл на локальной машине

```env
# Замените на реальные данные
DB_HOST=your-server-ip-or-domain.com
DB_PORT=3306
DB_USER=excel_parser_user
DB_PASSWORD=your_secure_password_here
DB_NAME=excel_parser_db
DB_SSL_DISABLED=true
```

## 6. Тестирование подключения

### С сервера (локально):
```bash
mysql -u excel_parser_user -p excel_parser_db
```

### С вашей машины (удаленно):
```bash
mysql -h your-server-ip -u excel_parser_user -p excel_parser_db
```

### Или через Python скрипт:
```bash
python test_database.py
```

## 7. Инициализация таблиц

После успешного подключения:
```bash
python init_database.py
```

## 8. Безопасность (рекомендации)

### Создайте пользователя только с необходимыми правами:
```sql
-- Более безопасный вариант с ограниченными правами
REVOKE ALL PRIVILEGES ON excel_parser_db.* FROM 'excel_parser_user'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON excel_parser_db.* TO 'excel_parser_user'@'%';
FLUSH PRIVILEGES;
```

### Ограничьте доступ по IP:
```sql
-- Удаляем пользователя с доступом отовсюду
DROP USER 'excel_parser_user'@'%';

-- Создаем пользователя только для вашего IP
CREATE USER 'excel_parser_user'@'your-client-ip' IDENTIFIED BY 'password';
GRANT SELECT, INSERT, UPDATE, DELETE ON excel_parser_db.* TO 'excel_parser_user'@'your-client-ip';
FLUSH PRIVILEGES;
```

## 9. Мониторинг подключений

### Проверка активных подключений:
```sql
SHOW PROCESSLIST;
```

### Проверка логов MySQL:
```bash
sudo tail -f /var/log/mysql/error.log
```

## 10. Возможные проблемы и решения

### Ошибка "Access denied":
- Проверьте пароль и имя пользователя
- Убедитесь, что пользователь создан для правильного хоста

### Ошибка "Can't connect":
- Проверьте bind-address в конфигурации
- Проверьте файрвол
- Убедитесь, что MySQL запущен

### Ошибка "Host is not allowed":
- Пересоздайте пользователя с правильным хостом
- Проверьте настройки файрвола

### Проверка статуса MySQL:
```bash
sudo systemctl status mysql
sudo netstat -tlnp | grep :3306
```

## 11. Бэкап и восстановление

### Создание бэкапа:
```bash
mysqldump -u excel_parser_user -p excel_parser_db > backup_$(date +%Y%m%d).sql
```

### Восстановление:
```bash
mysql -u excel_parser_user -p excel_parser_db < backup_20241202.sql
```
