# app/database.py
import sqlite3
import logging
from datetime import datetime, timedelta
import secrets

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path="vpn_bot.db"):
        self.db_path = db_path
        self.conn = None
    
    def init_db(self):
        """Инициализация базы данных"""
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            
            # Создаем таблицы
            cursor = self.conn.cursor()
            
            # Таблица пользователей
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    language_code TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_banned BOOLEAN DEFAULT FALSE
                )
            ''')
            
            # Таблица действий пользователей
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action_type TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Таблица подписок
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS subscriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    uuid TEXT UNIQUE NOT NULL,
                    expiry TIMESTAMP NOT NULL,
                    traffic_used INTEGER DEFAULT 0,
                    traffic_limit INTEGER DEFAULT 107374182400,
                    server_region TEXT DEFAULT 'EU',
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Таблица логов бота
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bot_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    level TEXT,
                    message TEXT,
                    extra_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Таблица платежей
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    amount DECIMAL(10,2),
                    currency TEXT DEFAULT 'USD',
                    months INTEGER,
                    telegram_payload TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            self.conn.commit()
            logger.info("✅ Database tables created successfully")
            
        except Exception as e:
            logger.error(f"❌ Database initialization error: {e}")
            raise
    
    def add_user(self, user_id, username=None, first_name=None, last_name=None, language_code=None):
        """Добавление пользователя"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO users 
                (user_id, username, first_name, last_name, language_code, last_active)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (user_id, username, first_name, last_name, language_code))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Add user error: {e}")
            return False
    
    def log_user_action(self, user_id, action_type):
        """Логирование действия пользователя"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO user_actions (user_id, action_type)
                VALUES (?, ?)
            ''', (user_id, action_type))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Log action error: {e}")
            return False
    
    def get_basic_stats(self):
        """Получение базовой статистики"""
        try:
            cursor = self.conn.cursor()
            
            # Всего пользователей
            cursor.execute("SELECT COUNT(*) as count FROM users")
            total_users = cursor.fetchone()[0]
            
            # Активные пользователи (последние 7 дней)
            cursor.execute('''
                SELECT COUNT(DISTINCT user_id) as count 
                FROM user_actions 
                WHERE created_at > datetime('now', '-7 days')
            ''')
            active_users = cursor.fetchone()[0]
            
            # Новые пользователи сегодня
            cursor.execute('''
                SELECT COUNT(*) as count 
                FROM users 
                WHERE date(created_at) = date('now')
            ''')
            new_users_today = cursor.fetchone()[0]
            
            # Активные подписки
            cursor.execute('''
                SELECT COUNT(*) as count 
                FROM subscriptions 
                WHERE expiry > datetime('now') AND is_active = TRUE
            ''')
            active_subscriptions = cursor.fetchone()[0]
            
            return {
                'total_users': total_users,
                'active_users': active_users,
                'new_users_today': new_users_today,
                'active_subscriptions': active_subscriptions
            }
        except Exception as e:
            logger.error(f"Get stats error: {e}")
            return {
                'total_users': 0,
                'active_users': 0,
                'new_users_today': 0,
                'active_subscriptions': 0
            }
    
    def get_all_users(self):
        """Получение всех пользователей"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT user_id, username, is_banned FROM users")
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Get all users error: {e}")
            return []
    
    def broadcast_message(self, message):
        """Получение списка пользователей для рассылки"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT user_id FROM users WHERE is_banned = FALSE")
            return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Broadcast error: {e}")
            return []
    
    def log_bot_event(self, level, message, extra_data=None):
        """Логирование события бота"""
        try:
            cursor = self.conn.cursor()
            extra_str = str(extra_data) if extra_data else None
            cursor.execute('''
                INSERT INTO bot_logs (level, message, extra_data)
                VALUES (?, ?, ?)
            ''', (level, message, extra_str))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Log bot event error: {e}")
            return False
    
    def get_bot_logs(self, limit=20, level=None):
        """Получение логов бота"""
        try:
            cursor = self.conn.cursor()
            if level and level != "ALL":
                cursor.execute('''
                    SELECT level, message, created_at 
                    FROM bot_logs 
                    WHERE level = ? 
                    ORDER BY created_at DESC 
                    LIMIT ?
                ''', (level, limit))
            else:
                cursor.execute('''
                    SELECT level, message, created_at 
                    FROM bot_logs 
                    ORDER BY created_at DESC 
                    LIMIT ?
                ''', (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Get bot logs error: {e}")
            return []
    
    def get_detailed_stats(self, days=30):
        """Получение детальной статистики"""
        try:
            cursor = self.conn.cursor()
            
            # Статистика по действиям
            cursor.execute('''
                SELECT action_type, COUNT(*) as count 
                FROM user_actions 
                WHERE created_at > datetime('now', '-' || ? || ' days')
                GROUP BY action_type 
                ORDER BY count DESC
            ''', (days,))
            action_stats = [dict(row) for row in cursor.fetchall()]
            
            # Статистика по дням
            cursor.execute('''
                SELECT 
                    date(created_at) as date,
                    COUNT(DISTINCT user_id) as active_users,
                    COUNT(*) as new_users
                FROM users 
                WHERE created_at > datetime('now', '-' || ? || ' days')
                GROUP BY date(created_at)
                ORDER BY date DESC
            ''', (days,))
            daily_stats = [dict(row) for row in cursor.fetchall()]
            
            return {
                'action_stats': action_stats,
                'daily_stats': daily_stats
            }
        except Exception as e:
            logger.error(f"Get detailed stats error: {e}")
            return {'action_stats': [], 'daily_stats': []}
    
    def close(self):
        """Закрытие соединения с БД"""
        if self.conn:
            self.conn.close()
