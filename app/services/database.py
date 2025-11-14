
# services/database.py
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = "vpn_bot.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Таблица пользователей
        c.execute('''
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
        c.execute('''
            CREATE TABLE IF NOT EXISTS user_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action_type TEXT,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Таблица подписок
        c.execute('''
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                plan_type TEXT,
                expiry_date TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Таблица логов бота
        c.execute('''
            CREATE TABLE IF NOT EXISTS bot_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level TEXT,
                message TEXT,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    
    def add_user(self, user_id: int, username: str = None, first_name: str = None, 
                 last_name: str = None, language_code: str = None):
        """Добавление/обновление пользователя"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            INSERT OR REPLACE INTO users 
            (user_id, username, first_name, last_name, language_code, last_active)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (user_id, username, first_name, last_name, language_code))
        
        conn.commit()
        conn.close()
    
    def log_user_action(self, user_id: int, action_type: str, details: Dict = None):
        """Логирование действий пользователя"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        details_json = json.dumps(details) if details else None
        
        c.execute('''
            INSERT INTO user_actions (user_id, action_type, details)
            VALUES (?, ?, ?)
        ''', (user_id, action_type, details_json))
        
        # Обновляем last_active
        c.execute('''
            UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE user_id = ?
        ''', (user_id,))
        
        conn.commit()
        conn.close()
    
    def log_bot_event(self, level: str, message: str, details: Dict = None):
        """Логирование событий бота"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        details_json = json.dumps(details) if details else None
        
        c.execute('''
            INSERT INTO bot_logs (level, message, details)
            VALUES (?, ?, ?)
        ''', (level, message, details_json))
        
        conn.commit()
        conn.close()
    
    def get_basic_stats(self) -> Dict:
        """Получение базовой статистики"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Общее количество пользователей
        c.execute('SELECT COUNT(*) FROM users')
        total_users = c.fetchone()[0]
        
        # Активные пользователи (за последние 7 дней)
        c.execute('''
            SELECT COUNT(*) FROM users 
            WHERE last_active >= datetime('now', '-7 days')
        ''')
        active_users = c.fetchone()[0]
        
        # Новые пользователи за сегодня
        c.execute('''
            SELECT COUNT(*) FROM users 
            WHERE DATE(created_at) = DATE('now')
        ''')
        new_users_today = c.fetchone()[0]
        
        # Активные подписки
        c.execute('''
            SELECT COUNT(*) FROM subscriptions 
            WHERE is_active = 1 AND expiry_date > datetime('now')
        ''')
        active_subscriptions = c.fetchone()[0]
        
        conn.close()
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "new_users_today": new_users_today,
            "active_subscriptions": active_subscriptions
        }
    
    def get_detailed_stats(self, days: int = 30) -> Dict:
        """Детальная статистика за период"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Статистика по дням
        c.execute('''
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as new_users,
                COUNT(CASE WHEN last_active >= datetime(created_at) THEN 1 END) as active_users
            FROM users 
            WHERE created_at >= datetime('now', ?)
            GROUP BY DATE(created_at)
            ORDER BY date DESC
        ''', (f'-{days} days',))
        
        daily_stats = []
        for row in c.fetchall():
            daily_stats.append({
                "date": row[0],
                "new_users": row[1],
                "active_users": row[2]
            })
        
        # Популярные действия
        c.execute('''
            SELECT action_type, COUNT(*) as count 
            FROM user_actions 
            WHERE created_at >= datetime('now', ?)
            GROUP BY action_type 
            ORDER BY count DESC 
            LIMIT 10
        ''', (f'-{days} days',))
        
        action_stats = []
        for row in c.fetchall():
            action_stats.append({
                "action_type": row[0],
                "count": row[1]
            })
        
        conn.close()
        
        return {
            "daily_stats": daily_stats,
            "action_stats": action_stats
        }
    
    def get_all_users(self) -> List[Dict]:
        """Получение списка всех пользователей"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            SELECT 
                user_id, username, first_name, last_name, 
                created_at, last_active, is_banned
            FROM users 
            ORDER BY created_at DESC
        ''')
        
        users = []
        for row in c.fetchall():
            users.append({
                "user_id": row[0],
                "username": row[1],
                "first_name": row[2],
                "last_name": row[3],
                "created_at": row[4],
                "last_active": row[5],
                "is_banned": bool(row[6])
            })
        
        conn.close()
        return users
    
    def get_bot_logs(self, limit: int = 100, level: str = None) -> List[Dict]:
        """Получение логов бота"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        if level:
            c.execute('''
                SELECT level, message, details, created_at 
                FROM bot_logs 
                WHERE level = ?
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (level, limit))
        else:
            c.execute('''
                SELECT level, message, details, created_at 
                FROM bot_logs 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
        
        logs = []
        for row in c.fetchall():
            logs.append({
                "level": row[0],
                "message": row[1],
                "details": row[2],
                "created_at": row[3]
            })
        
        conn.close()
        return logs
    
    def broadcast_message(self, message: str) -> List[int]:
        """Получение списка пользователей для рассылки"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            SELECT user_id FROM users WHERE is_banned = 0
        ''')
        
        user_ids = [row[0] for row in c.fetchall()]
        conn.close()
        return user_ids
