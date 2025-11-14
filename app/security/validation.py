# security/validation.py
import re
import ipaddress
from typing import Optional

class InputValidator:
    @staticmethod
    def validate_user_id(user_id: int) -> bool:
        """Валидация ID пользователя"""
        return isinstance(user_id, int) and user_id > 0
    
    @staticmethod
    def validate_uuid(uuid: str) -> bool:
        """Валидация UUID"""
        if not uuid or len(uuid) != 43:  # token_urlsafe(32) produces 43 chars
            return False
        return bool(re.match(r'^[a-zA-Z0-9_-]+$', uuid))
    
    @staticmethod
    def validate_ip_address(ip: str) -> bool:
        """Валидация IP адреса"""
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """Санитизация пользовательского ввода"""
        if not text:
            return ""
        # Удаляем потенциально опасные символы
        return re.sub(r'[<>"\'&]', '', text).strip()

validator = InputValidator()
