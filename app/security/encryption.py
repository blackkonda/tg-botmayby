# app/security/encryption.py
import secrets
import hashlib
import hmac
import jwt
from cryptography.fernet import Fernet
from datetime import datetime, timedelta
from app.config import Config, SecurityConfig  # ИСПРАВЛЕН ИМПОРТ

class SecurityManager:
    def __init__(self):
        self.fernet = Fernet(Config.ENCRYPTION_KEY)
    
    def generate_secure_uuid(self) -> str:
        """Генерация криптографически безопасного UUID"""
        return secrets.token_urlsafe(32)
    
    def encrypt_data(self, data: str) -> str:
        """Шифрование данных для хранения в БД"""
        return self.fernet.encrypt(data.encode()).decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Дешифрование данных из БД"""
        return self.fernet.decrypt(encrypted_data.encode()).decode()
    
    def create_hmac_signature(self, data: str) -> str:
        """Создание HMAC подписи для проверки целостности данных"""
        return hmac.new(
            Config.HMAC_KEY,
            data.encode(),
            hashlib.sha256
        ).hexdigest()
    
    def verify_hmac_signature(self, data: str, signature: str) -> bool:
        """Проверка HMAC подписи"""
        expected_signature = self.create_hmac_signature(data)
        return hmac.compare_digest(expected_signature, signature)
    
    def create_jwt_token(self, user_id: int, payload: dict = None) -> str:
        """Создание JWT токена"""
        if payload is None:
            payload = {}
        
        payload.update({
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(seconds=SecurityConfig.JWT_EXPIRATION),
            'iat': datetime.utcnow()
        })
        
        return jwt.encode(payload, Config.JWT_SECRET, algorithm=SecurityConfig.JWT_ALGORITHM)
    
    def verify_jwt_token(self, token: str) -> dict:
        """Проверка JWT токена"""
        try:
            return jwt.decode(token, Config.JWT_SECRET, algorithms=[SecurityConfig.JWT_ALGORITHM])
        except jwt.ExpiredSignatureError:
            raise ValueError("Token expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")

security = SecurityManager()
