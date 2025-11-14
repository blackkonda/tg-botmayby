# app/vpn_generator.py
import logging
from app.config import Config

logger = logging.getLogger(__name__)

class VPNGenerator:
    def generate_vless_config(self, user_id: int, uuid: str, server_region: str = "EU"):
        """Генерация VLESS конфигурации"""
        server_ip = Config.VPN_SERVERS.get(server_region, Config.VPN_SERVERS["EU"])
        
        config_template = f"""vless://{uuid}@{server_ip}:443?type=tcp&encryption=none&flow={Config.FLOW}&security=reality&sni={Config.SERVER_NAME}&fp=chrome&pbk={Config.PUBLIC_KEY}&sid={Config.SHORT_ID}#VELTRIX-VPN-{user_id}"""
        
        return {
            'link': config_template,
            'server': server_ip,
            'region': server_region,
            'uuid': uuid
        }
    
    def generate_config_file(self, user_id: int, uuid: str, server_region: str = "EU"):
        """Генерация файла конфигурации"""
        config = self.generate_vless_config(user_id, uuid, server_region)
        
        config_content = f"""# VELTRIX VPN Configuration
# User ID: {user_id}
# Region: {server_region}

{config['link']}

# Instructions:
# 1. Download V2Ray client
# 2. Import this link
# 3. Connect and enjoy!

# Support: @veltrix_support"""
        
        return config_content

vpn_generator = VPNGenerator()
