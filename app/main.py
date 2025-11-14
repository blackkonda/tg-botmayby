
# app/main.py
import asyncio
import logging
import os
import sys
import signal

# Добавляем путь для импортов
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from telegram.ext import Application, CommandHandler, CallbackQueryHandler, PreCheckoutQueryHandler, MessageHandler, filters

from app.handlers.commands import CommandHandlers
from app.handlers.payments import PaymentHandlers
from app.config import Config
from app.database import Database  # ДОБАВЛЕН ИМПОРТ

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

class VPNBot:
    def __init__(self):
        self.application = None
        self.command_handlers = None
        self.payment_handlers = None
        self.database = None  # ДОБАВЛЕНО
        self._stop_event = asyncio.Event()
    
    async def initialize(self):
        """Инициализация бота"""
        try:
            logger.info("🚀 Initializing VPN Bot...")
            
            # Инициализируем базу данных ДОБАВЛЕНО
            self.database = Database(Config.DATABASE_PATH)
            self.database.init_db()
            logger.info("✅ Database initialized")
            
            # Создаем application
            self.application = Application.builder().token(Config.BOT_TOKEN).build()
            
            # Передаем базу данных в обработчики ДОБАВЛЕНО
            self.command_handlers = CommandHandlers(self.application, self.database)
            self.payment_handlers = PaymentHandlers()
            
            # Передаем базу данных в bot_data для доступа из обработчиков ДОБАВЛЕНО
            self.application.bot_data['db'] = self.database
            
            # Настраиваем обработчики
            self._setup_handlers()
            
            # Инициализируем application
            await self.application.initialize()
            
            logger.info("✅ Bot initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize bot: {e}")
            raise
    
    def _setup_handlers(self):
        """Настройка обработчиков"""
        # Основные команды
        self.application.add_handler(CommandHandler("start", self.command_handlers.start))
        
        # Callback кнопки основного меню
        self.application.add_handler(CallbackQueryHandler(self.command_handlers.handle_callback))
        
        # Платежи
        self.application.add_handler(PreCheckoutQueryHandler(self.payment_handlers.pre_checkout))
        self.application.add_handler(MessageHandler(
            filters.SUCCESSFUL_PAYMENT, 
            self.payment_handlers.successful_payment
        ))
        
        # АДМИН ОБРАБОТЧИКИ
        if hasattr(self.command_handlers, 'admin_start'):
            self.application.add_handler(CommandHandler("admin", self.command_handlers.admin_start))
            logger.info("✅ Admin command /admin registered")
        
        if hasattr(self.command_handlers, 'admin_stats'):
            self.application.add_handler(CommandHandler("stats", self.command_handlers.admin_stats))
            logger.info("✅ Admin command /stats registered")
        
        # Админ callback обработчики
        if hasattr(self.command_handlers, 'handle_admin_callback'):
            self.application.add_handler(CallbackQueryHandler(
                self.command_handlers.handle_admin_callback, 
                pattern="^admin_"
            ))
            logger.info("✅ Admin callbacks registered")
        
        # Обработчик сообщений для рассылки
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            self.command_handlers.handle_broadcast_message
        ))
        
        # Обработчик отмены
        self.application.add_handler(CommandHandler("cancel", self.command_handlers.handle_cancel))
        
        logger.info("✅ Broadcast and cancel handlers registered")
    
    async def start_polling(self):
        """Запуск polling"""
        try:
            logger.info("🔄 Starting bot polling...")
            
            # Запускаем polling
            await self.application.start()
            await self.application.updater.start_polling(
                allowed_updates=["message", "callback_query", "pre_checkout_query"],
                drop_pending_updates=True
            )
            
            logger.info("✅ Bot is now running and polling for updates!")
            
            # Ждем сигнала остановки
            await self._stop_event.wait()
            
        except Exception as e:
            logger.error(f"❌ Polling error: {e}")
            raise
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Корректное завершение работы"""
        try:
            logger.info("🛑 Shutting down bot...")
            
            if self.application:
                if self.application.updater:
                    await self.application.updater.stop()
                await self.application.stop()
                await self.application.shutdown()
            
            # Закрываем соединение с БД ДОБАВЛЕНО
            if self.database:
                self.database.close()
                logger.info("✅ Database connection closed")
            
            logger.info("✅ Bot shutdown completed")
            
        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")
    
    def run(self):
        """Запуск бота - основная точка входа"""
        try:
            # Настройка обработки сигналов (для корректного завершения)
            try:
                # Для Windows
                if os.name == 'nt':
                    signal.signal(signal.SIGINT, self._signal_handler)
                    signal.signal(signal.SIGTERM, self._signal_handler)
            except (ValueError, RuntimeError):
                # Сигналы могут не работать в некоторых окружениях
                pass
            
            # Запускаем asyncio loop
            asyncio.run(self._async_run())
            
        except KeyboardInterrupt:
            logger.info("⏹️ Bot stopped by user (KeyboardInterrupt)")
        except Exception as e:
            logger.error(f"💥 Bot crashed: {e}")
    
    async def _async_run(self):
        """Асинхронный запуск"""
        try:
            await self.initialize()
            await self.start_polling()
        except Exception as e:
            logger.error(f"💥 Async run error: {e}")
            await self.shutdown()
    
    def _signal_handler(self, signum, frame):
        """Обработчик сигналов для корректного завершения"""
        logger.info(f"📡 Received signal {signum}, shutting down...")
        self._stop_event.set()

def main():
    """Точка входа для запуска бота"""
    bot = VPNBot()
    bot.run()

if __name__ == '__main__':
    main()
