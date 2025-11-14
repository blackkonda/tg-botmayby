from app.security.encryption import security
from app.security.validation import validator
from config import Config

class VPNGenerator:
    @staticmethod
    def generate_vless_config(user_id: int, uuid: str, server_region: str = "EU") -> str:
        """Генерация VLESS конфигурации по стандартам 2025"""
        
        if not validator.validate_user_id(user_id) or not validator.validate_uuid(uuid):
            raise ValueError("Invalid user ID or UUID")
        
        server_ip = Config.VPN_SERVERS.get(server_region, Config.VPN_SERVERS["EU"])
        
        # Современные параметры Reality 2025
        params = {
            'type': 'grpc',
            'encryption': 'none',
            'security': 'reality',
            'pbk': Config.PUBLIC_KEY,
            'sni': Config.SERVER_NAME,
            'sid': Config.SHORT_ID,
            'spx': '/',
            'fp': 'chrome',
            'flow': Config.FLOW,
            'alpn': 'h2,http/1.1',
            'serviceName': 'Gost',
            'mode': 'gun'
        }
        
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        
        # Форматирование ссылки
        vless_link = f"vless://{uuid}@{server_ip}:443?{query_string}#VeltrixVPN_{server_region}"
        
        # Создаем подпись для проверки целостности
        signature = security.create_hmac_signature(vless_link)
        
        return {
            'link': vless_link,
            'signature': signature,
            'region': server_region,
            'expiry': None  # Будет заполнено из БД
        }
    
    @staticmethod
    def generate_qr_code_data(vless_link: str) -> str:
        """Генерация данных для QR кода"""
        # В реальной реализации здесь будет генерация QR кода
        return f"QR Code for: {vless_link}"

vpn_generator = VPNGenerator()
