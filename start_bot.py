# start_bot.py
import sys
import os

# Добавляем текущую директорию в путь Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """Основная точка входа"""
    try:
        from app.main import VPNBot
        
        print("🚀 Запуск VPN Бота...")
        print("📡 Инициализация...")
        
        bot = VPNBot()
        bot.run()
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("🔧 Проверьте структуру файлов и наличие __init__.py")
    except Exception as e:
        print(f"💥 Критическая ошибка: {e}")

if __name__ == '__main__':
    main()
