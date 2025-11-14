
# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Telegram
    BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token_here")
    PROVIDER_TOKEN = os.getenv("PROVIDER_TOKEN", "your_provider_token")
    
    # Database
    DATABASE_PATH = os.getenv("DATABASE_PATH", "vpn_bot.db")
    
    # Admin
    ADMIN_IDS = [349027214]  # Ваш ID уже указан
    
    # Security
    ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "your_32_bytes_encryption_key!!").encode()
    JWT_SECRET = os.getenv("JWT_SECRET", "your_jwt_secret_min_32_chars")
    HMAC_KEY = os.getenv("HMAC_KEY", "your_hmac_key_for_data_integrity").encode()
    
    # VPN Servers
    VPN_SERVERS = {
        "EU": os.getenv("VPN_EU_SERVER", "194.163.180.12"),
        "US": os.getenv("VPN_US_SERVER", "154.16.202.22"), 
        "ASIA": os.getenv("VPN_ASIA_SERVER", "139.162.123.45")
    }
    
    # Reality Protocol
    PUBLIC_KEY = os.getenv("PUBLIC_KEY", "c4b4f15a5b5a5b5a5b5a5b5a5b5a5b5a5b5a5b5a5b5a5b5a5b5a5b5a5b5a5b")
    SHORT_ID = os.getenv("SHORT_ID", "6ba7b8149abd")
    SERVER_NAME = os.getenv("SERVER_NAME", "www.cloudflare.com")
    FLOW = os.getenv("FLOW", "xtls-rprx-vision")
    
    # Pricing (USD)
    PRICING = {
        "1": 5.00,    # 1 month
        "3": 12.00,   # 3 months
        "6": 20.00,   # 6 months
        "12": 35.00   # 12 months
    }

# ДОБАВЛЕНО: Класс SecurityConfig для encryption.py
class SecurityConfig:
    ARGON2_TIME_COST = 3
    ARGON2_MEMORY_COST = 65536
    ARGON2_PARALLELISM = 1
    JWT_EXPIRATION = 3600  # 1 hour
    JWT_ALGORITHM = "HS256"

def is_admin(user_id: int) -> bool:
    return user_id in Config.ADMIN_IDS
