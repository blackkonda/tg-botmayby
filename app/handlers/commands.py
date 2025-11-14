
# app/handlers/commands.py
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, Application
from app.handlers.payments import PaymentHandlers
from app.config import is_admin

logger = logging.getLogger(__name__)

class CommandHandlers:

    def __init__(self, application: Application, database=None):
        self.app = application
        self.payment_handlers = PaymentHandlers()
        self.db = database
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start - главное меню"""
        user = update.effective_user
        
        # Сохраняем пользователя в БД
        if self.db:
            self.db.add_user(
                user_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                language_code=user.language_code
            )
            self.db.log_user_action(user.id, "start_command")
        
        # Главное меню - КНОПКИ В 2 РЯДА
        keyboard = [
            # Первый ряд: 2 кнопки
            [
                InlineKeyboardButton("🛡️ Купить VPN", callback_data="buy_vpn"),
                InlineKeyboardButton("🚀 Скорость", callback_data="speed_test")
            ],
            # Второй ряд: 2 кнопки  
            [
                InlineKeyboardButton("⚙️ Настройки", callback_data="settings"),
                InlineKeyboardButton("🤝 Партнерка", callback_data="affiliate")
            ],
            # Третий ряд: 2 кнопки
            [
                InlineKeyboardButton("🎁 Бесплатно", callback_data="free_trial"),
                InlineKeyboardButton("ℹ️ Информация", callback_data="info")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = (
            "🔒 <b>VELTRIX VPN - ПРЕМИУМ ЗАЩИТА 2025</b>\n\n"
            "• 🚀 <b>500+ Мбит/с</b> скорость\n"
            "• 🌍 <b>3 региона</b> (EU, US, ASIA)\n"  
            "• 🛡️ <b>Reality Protocol</b> - невидимость\n"
            "• 📱 <b>0 логов</b> - полная анонимность\n"
            "• 🔄 <b>Авто-обновление</b> конфигов\n\n"
            "Выберите действие:"
        )
        
        await update.message.reply_text(
            welcome_text,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка callback запросов от кнопок"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        callback_data = query.data
        
        # Логируем действие
        if self.db:
            self.db.log_user_action(user_id, f"callback_{callback_data}")
        
        if callback_data == "buy_vpn":
            await self.show_pricing(query, context)
        elif callback_data == "speed_test":
            await self.speed_test(query, context)
        elif callback_data == "settings":
            await self.show_settings(query, context)
        elif callback_data == "affiliate":
            await self.show_affiliate(query, context)
        elif callback_data == "free_trial":
            await self.free_trial(query, context)
        elif callback_data == "info":
            await self.show_info(query, context)
        elif callback_data == "back_to_main":
            await self.back_to_main(query, context)
        elif callback_data.startswith("plan_"):
            await self.handle_plan_selection(query, context)
        # Админ callback - ДОБАВЛЕНО
        elif callback_data.startswith("admin_"):
            await self.handle_admin_callback(update, context)
    
    async def show_pricing(self, query, context: ContextTypes.DEFAULT_TYPE):
        """Показ тарифов"""
        keyboard = [
            [InlineKeyboardButton("1 месяц - 150р", callback_data="plan_1")],
            [InlineKeyboardButton("3 месяца - 350р", callback_data="plan_3")],
            [InlineKeyboardButton("6 месяцев - 700р", callback_data="plan_6")],
            [InlineKeyboardButton("12 месяцев - 1400р", callback_data="plan_12")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = (
            "💰 <b>ВЫБЕРИТЕ ТАРИФ</b>\n\n"
            "• 📅 <b>1 месяц</b> - 150р\n"
            "• 💰 <b>3 месяца</b> - 350р (экономия 100р)\n"
            "• 🚀 <b>6 месяцев</b> - 700р (экономия 200р)\n"
            "• 👑 <b>12 месяцев</b> - 1400р (экономия 400р)\n\n"
            "Все тарифы включают:\n"
            "• 🛡️ Полный доступ ко всем серверам\n"
            "• 📊 100GB трафика в месяц\n"
            "• 🔄 Авто-обновление конфигов\n"
            "• 🆓 Техническая поддержка 24/7"
        )
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')
    
    async def handle_plan_selection(self, query, context: ContextTypes.DEFAULT_TYPE):
        """Обработка выбора тарифа"""
        await self.payment_handlers.handle_plan_selection(query, context)
    
    async def speed_test(self, query, context: ContextTypes.DEFAULT_TYPE):
        """Проверка скорости"""
        text = (
            "🚀 <b>ПРОВЕРКА СКОРОСТИ</b>\n\n"
            "Для точного теста скорости:\n"
            "1. 📱 Отключите VPN\n"
            "2. 🔄 Закройте все приложения\n"
            "3. 📶 Подключитесь к Wi-Fi\n"
            "4. 🧪 Запустите тест на speedtest.net\n\n"
            "Наши серверы обеспечивают:\n"
            "• ⬇️ <b>500+ Мбит/с</b> скачивание\n"
            "• ⬆️ <b>300+ Мбит/с</b> загрузка\n"
            "• 📍 <b>5-20 мс</b> пинг (EU)\n\n"
            "После подключения к VPN скорость может снизиться на 5%"
        )
        
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')
    
    async def show_affiliate(self, query, context: ContextTypes.DEFAULT_TYPE):
        """Партнерская программа"""
        user_id = query.from_user.id
        
        text = (
            "🤝 <b>ПАРТНЕРСКАЯ ПРОГРАММА</b>\n\n"
            "Приводите друзей и получайте <b>20%</b> с каждой их оплаты!\n\n"
            "🎯 <b>Как это работает:</b>\n"
            "1. 🔗 Ваша реферальная ссылка:\n"
            f"   <code>https://t.me/{(await context.bot.get_me()).username}?start={user_id}</code>\n\n"
            "2. 👥 Друг переходит по ссылке и покупает VPN\n"
            "3. 💰 Вы получаете 20% от его платежей\n\n"
            "💵 <b>Вывод средств:</b> от $10 на карту или крипто"
        )
        
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')
    
    async def show_settings(self, query, context: ContextTypes.DEFAULT_TYPE):
        """Настройки"""
        user_id = query.from_user.id
        
        text = (
            f"⚙️ <b>ВАШИ НАСТРОЙКИ</b>\n\n"
            f"• 👤 ID: <code>{user_id}</code>\n"
            f"• 🛡️ Статус: 🔴 НЕТ ПОДПИСКИ\n\n"
            f"🔧 <b>Купите подписку для доступа к настройкам</b>"
        )
        
        keyboard = [
            [InlineKeyboardButton("🛡️ Купить VPN", callback_data="buy_vpn")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')
    
    async def free_trial(self, query, context: ContextTypes.DEFAULT_TYPE):
        """Бесплатная пробная версия"""
        text = (
            "🎁 <b>БЕСПЛАТНЫЙ ТЕСТОВЫЙ ПЕРИОД</b>\n\n"
            "К сожалению, бесплатный тестовый период временно недоступен.\n\n"
            "Но мы предлагаем:\n"
            "• 💰 <b>Гарантия возврата</b> в течение 3 дней\n"
            "• 🚀 <b>Максимальная скорость</b> с первой минуты\n"
            "• 🌍 <b>Все регионы</b> доступны сразу\n\n"
            "Попробуйте наш самый дешевый тариф всего за $5!"
        )
        
        keyboard = [
            [InlineKeyboardButton("🛡️ Купить VPN", callback_data="buy_vpn")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')
    
    async def show_info(self, query, context: ContextTypes.DEFAULT_TYPE):
        """Информация о сервисе"""
        text = (
            "ℹ️ <b>ИНФОРМАЦИЯ О VELTRIX VPN</b>\n\n"
            "🔒 <b>Безопасность:</b>\n"
            "• 🛡️ Reality Protocol - обход блокировок\n"
            "• 🔐 Zero-Logs - никаких логов\n"
            "• 🌐 TLS 1.3 + HTTPS\n"
            "• 💻 256-битное шифрование\n\n"
            "🚀 <b>Технологии 2025:</b>\n"
            "• 📡 VLESS + gRPC транспортировка\n"
            "• 🌍 3 дата-центра (EU, US, ASIA)\n"
            "• ⚡ 10+ Gbps каналы\n\n"
            "💬 <b>Поддержка:</b> @veltrix_support"
        )
        
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')
    
    async def back_to_main(self, query, context: ContextTypes.DEFAULT_TYPE):
        """Возврат в главное меню"""
        # Главное меню - КНОПКИ В 2 РЯДА (такие же как в start)
        keyboard = [
            [
                InlineKeyboardButton("🛡️ Купить VPN", callback_data="buy_vpn"),
                InlineKeyboardButton("🚀 Скорость", callback_data="speed_test")
            ],
            [
                InlineKeyboardButton("⚙️ Настройки", callback_data="settings"),
                InlineKeyboardButton("🤝 Партнерка", callback_data="affiliate")
            ],
            [
                InlineKeyboardButton("🎁 Бесплатно", callback_data="free_trial"),
                InlineKeyboardButton("ℹ️ Информация", callback_data="info")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = (
            "🔒 <b>VELTRIX VPN - ПРЕМИУМ ЗАЩИТА 2025</b>\n\n"
            "Выберите действие:"
        )
        
        await query.edit_message_text(
            welcome_text,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )

    # АДМИН ФУНКЦИИ
    async def admin_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /admin - главное меню админки"""
        if not is_admin(update.effective_user.id):
            await update.message.reply_text("❌ У вас нет прав доступа к админ панели")
            return
        
        keyboard = [
            [InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")],
            [InlineKeyboardButton("👥 Управление пользователями", callback_data="admin_users")],
            [InlineKeyboardButton("📢 Рассылка", callback_data="admin_broadcast")],
            [InlineKeyboardButton("📋 Логи бота", callback_data="admin_logs")],
            [InlineKeyboardButton("⚙️ Настройки", callback_data="admin_settings")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = (
            "🛠️ <b>Панель администратора</b>\n\n"
            "Выберите раздел для управления ботом:"
        )
        
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='HTML')

    async def admin_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /stats - статистика бота"""
        if not is_admin(update.effective_user.id):
            return
        
        try:
            if self.db:
                stats = self.db.get_basic_stats()
                
                text = (
                    "📊 <b>Статистика бота</b>\n\n"
                    f"👥 <b>Всего пользователей:</b> {stats['total_users']}\n"
                    f"🟢 <b>Активных (7 дней):</b> {stats['active_users']}\n"
                    f"🆕 <b>Новых сегодня:</b> {stats['new_users_today']}\n"
                    f"🔐 <b>Активных подписок:</b> {stats['active_subscriptions']}\n\n"
                    "⚡ <i>Админ панель успешно подключена!</i>"
                )
            else:
                text = (
                    "📊 <b>Статистика бота</b>\n\n"
                    "👥 <b>Всего пользователей:</b> информация в разработке\n"
                    "🟢 <b>Активных пользователей:</b> информация в разработке\n"
                    "🆕 <b>Новых сегодня:</b> информация в разработке\n\n"
                    "⚡ <i>Админ панель успешно подключена!</i>"
                )
            
            await update.message.reply_text(text, parse_mode='HTML')
            
        except Exception as e:
            logger.error(f"Stats error: {e}")
            await update.message.reply_text("❌ Ошибка получения статистики")

    async def handle_admin_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка callback от админ кнопок"""
        query = update.callback_query
        user_id = query.from_user.id
        
        if not is_admin(user_id):
            await query.answer("❌ Нет прав доступа", show_alert=True)
            return
        
        await query.answer()
        callback_data = query.data
        
        if callback_data == "admin_stats":
            await self.show_admin_stats(query, context)
        elif callback_data == "admin_users":
            await self.show_admin_users(query, context)
        elif callback_data == "admin_broadcast":
            await self.show_broadcast_menu(query, context)
        elif callback_data == "admin_logs":
            await self.show_logs_menu(query, context)
        elif callback_data == "admin_detailed_stats":
            await self.show_detailed_stats(query, context)
        elif callback_data == "admin_back":
            await self.show_admin_main_menu(query, context)
        elif callback_data == "admin_start_broadcast":
            await self.start_broadcast(query, context)
        elif callback_data.startswith("admin_logs_"):
            level = callback_data.split("_")[2]
            await self.show_bot_logs(query, context, level)
        else:
            await query.edit_message_text(f"🛠️ Функция в разработке: {callback_data}")

    async def show_admin_main_menu(self, query, context: ContextTypes.DEFAULT_TYPE):
        """Главное меню админки"""
        keyboard = [
            [InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")],
            [InlineKeyboardButton("👥 Управление пользователями", callback_data="admin_users")],
            [InlineKeyboardButton("📢 Рассылка", callback_data="admin_broadcast")],
            [InlineKeyboardButton("📋 Логи бота", callback_data="admin_logs")],
            [InlineKeyboardButton("⚙️ Настройки", callback_data="admin_settings")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = "🛠️ <b>Панель администратора</b>\n\nВыберите раздел:"
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')

    async def show_admin_stats(self, query, context: ContextTypes.DEFAULT_TYPE):
        """Показ статистики"""
        try:
            if self.db:
                stats = self.db.get_basic_stats()
                
                text = (
                    "📊 <b>Статистика бота</b>\n\n"
                    f"👥 <b>Всего пользователей:</b> {stats['total_users']}\n"
                    f"🟢 <b>Активных (7 дней):</b> {stats['active_users']}\n"
                    f"🆕 <b>Новых сегодня:</b> {stats['new_users_today']}\n"
                    f"🔐 <b>Активных подписок:</b> {stats['active_subscriptions']}\n\n"
                    "<i>Для детальной статистики нажмите кнопку ниже</i>"
                )
            else:
                text = (
                    "📊 <b>Статистика бота</b>\n\n"
                    "👥 <b>Всего пользователей:</b> информация в разработке\n"
                    "🟢 <b>Активных пользователей:</b> информация в разработке\n"
                    "🆕 <b>Новых сегодня:</b> информация в разработке\n\n"
                    "🔧 <i>Для подключения статистики нужна база данных</i>"
                )
            
            keyboard = [
                [InlineKeyboardButton("📈 Детальная статистика", callback_data="admin_detailed_stats")],
                [InlineKeyboardButton("🔄 Обновить", callback_data="admin_stats")],
                [InlineKeyboardButton("🔙 Назад", callback_data="admin_back")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')
            
        except Exception as e:
            logger.error(f"Stats error: {e}")
            await query.edit_message_text("❌ Ошибка получения статистики")

    async def show_detailed_stats(self, query, context: ContextTypes.DEFAULT_TYPE):
        """Детальная статистика"""
        try:
            if self.db:
                detailed_stats = self.db.get_detailed_stats(30)
                
                text = "📈 <b>Детальная статистика (30 дней)</b>\n\n"
                
                if detailed_stats['action_stats']:
                    text += "<b>🎯 Популярные действия:</b>\n"
                    for action in detailed_stats['action_stats']:
                        text += f"• {action['action_type']}: {action['count']}\n"
                    text += "\n"
                
                if detailed_stats['daily_stats']:
                    text += "<b>📅 Активность по дням (последние 7):</b>\n"
                    for day in detailed_stats['daily_stats'][:7]:
                        text += f"• {day['date']}: +{day['new_users']} новых, {day['active_users']} активных\n"
            else:
                text = "❌ База данных не подключена"
            
            keyboard = [
                [InlineKeyboardButton("📊 Общая статистика", callback_data="admin_stats")],
                [InlineKeyboardButton("🔙 Назад", callback_data="admin_back")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')
            
        except Exception as e:
            logger.error(f"Detailed stats error: {e}")
            await query.edit_message_text("❌ Ошибка получения детальной статистики")

    async def show_admin_users(self, query, context: ContextTypes.DEFAULT_TYPE):
        """Управление пользователями"""
        try:
            if self.db:
                users = self.db.get_all_users()
                total_users = len(users)
                
                text = (
                    f"👥 <b>Управление пользователями</b>\n\n"
                    f"📊 Всего пользователей: <b>{total_users}</b>\n\n"
                    "<b>Последние 5 пользователей:</b>\n"
                )
                
                for user in users[:5]:
                    status = "🚫" if user['is_banned'] else "🟢"
                    username = f"@{user['username']}" if user['username'] else "Без username"
                    text += f"{status} {user['user_id']} | {username}\n"
            else:
                text = "❌ База данных не подключена"
            
            keyboard = [
                [InlineKeyboardButton("📋 Полный список", callback_data="admin_user_list")],
                [InlineKeyboardButton("🔍 Поиск пользователя", callback_data="admin_user_search")],
                [InlineKeyboardButton("🔙 Назад", callback_data="admin_back")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')
            
        except Exception as e:
            logger.error(f"Users error: {e}")
            await query.edit_message_text("❌ Ошибка получения списка пользователей")

    async def show_broadcast_menu(self, query, context: ContextTypes.DEFAULT_TYPE):
        """Меню рассылки"""
        try:
            if self.db:
                users_count = len(self.db.broadcast_message("test"))
                
                text = (
                    "📢 <b>Массовая рассылка</b>\n\n"
                    f"👥 <b>Получатели:</b> {users_count} пользователей\n\n"
                    "<b>Инструкция:</b>\n"
                    "1. Нажмите «Начать рассылку»\n"
                    "2. Отправьте сообщение для рассылки\n"
                    "3. Бот отправит его всем пользователям\n\n"
                    "⚠️ <i>Рассылка может занять несколько минут</i>"
                )
            else:
                text = "❌ База данных не подключена"
            
            keyboard = [
                [InlineKeyboardButton("🚀 Начать рассылку", callback_data="admin_start_broadcast")],
                [InlineKeyboardButton("🔙 Назад", callback_data="admin_back")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')
            
        except Exception as e:
            logger.error(f"Broadcast menu error: {e}")
            await query.edit_message_text("❌ Ошибка подготовки рассылки")

    async def start_broadcast(self, query, context: ContextTypes.DEFAULT_TYPE):
        """Начало рассылки"""
        if not self.db:
            await query.answer("❌ База данных не подключена", show_alert=True)
            return
        
        context.user_data['awaiting_broadcast'] = True
        
        text = (
            "📢 <b>Начало рассылки</b>\n\n"
            "Отправьте сообщение которое хотите разослать всем пользователям:\n\n"
            "💡 <i>Поддерживается HTML разметка</i>\n"
            "❌ Для отмены отправьте /cancel"
        )
        
        keyboard = [[InlineKeyboardButton("🔙 Отмена", callback_data="admin_broadcast")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')

    async def show_logs_menu(self, query, context: ContextTypes.DEFAULT_TYPE):
        """Меню логов"""
        text = (
            "📋 <b>Логи бота</b>\n\n"
            "Выберите тип логов для просмотра:\n\n"
            "• 📝 <b>INFO</b> - информационные сообщения\n"
            "• ⚠️ <b>WARNING</b> - предупреждения\n"
            "• ❌ <b>ERROR</b> - ошибки\n"
            "• 🔧 <b>DEBUG</b> - отладочная информация"
        )
        
        keyboard = [
            [InlineKeyboardButton("📝 INFO", callback_data="admin_logs_INFO")],
            [InlineKeyboardButton("⚠️ WARNING", callback_data="admin_logs_WARNING")],
            [InlineKeyboardButton("❌ ERROR", callback_data="admin_logs_ERROR")],
            [InlineKeyboardButton("🔧 DEBUG", callback_data="admin_logs_DEBUG")],
            [InlineKeyboardButton("📊 Все логи", callback_data="admin_logs_ALL")],
            [InlineKeyboardButton("🔙 Назад", callback_data="admin_back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')

    async def show_bot_logs(self, query, context: ContextTypes.DEFAULT_TYPE, level: str):
        """Показ логов бота"""
        try:
            if not self.db:
                await query.edit_message_text("❌ База данных не подключена")
                return
            
            if level == "ALL":
                logs = self.db.get_bot_logs(limit=20)
                title = "Все логи"
            else:
                logs = self.db.get_bot_logs(limit=20, level=level)
                title = f"Логи {level}"
            
            if not logs:
                text = f"📋 <b>{title}</b>\n\nЛоги не найдены"
            else:
                text = f"📋 <b>{title}</b> (последние 20)\n\n"
                for log in logs:
                    level_emoji = {
                        "INFO": "📝",
                        "WARNING": "⚠️", 
                        "ERROR": "❌",
                        "DEBUG": "🔧"
                    }.get(log['level'], "📄")
                    
                    text += f"{level_emoji} <b>{log['level']}</b> | {log['created_at']}\n"
                    text += f"<code>{log['message'][:100]}</code>\n\n"
            
            keyboard = [
                [InlineKeyboardButton("📋 Меню логов", callback_data="admin_logs")],
                [InlineKeyboardButton("🔙 Назад", callback_data="admin_back")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')
            
        except Exception as e:
            logger.error(f"Logs error: {e}")
            await query.edit_message_text("❌ Ошибка получения логов")

    # ДОБАВЛЕНЫ НЕДОСТАЮЩИЕ МЕТОДЫ ДЛЯ ОБРАБОТКИ СООБЩЕНИЙ И ОТМЕНЫ
    async def handle_broadcast_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка сообщения для рассылки (только для админов)"""
        user_id = update.effective_user.id
        
        if not is_admin(user_id):
            return  # Игнорируем сообщения от не-админов
        
        # Проверяем, находится ли админ в режиме рассылки
        if context.user_data.get('awaiting_broadcast'):
            message_text = update.message.text
            context.user_data['awaiting_broadcast'] = False
            
            # Сохраняем сообщение для рассылки
            context.user_data['broadcast_message'] = message_text
            
            # Создаем кнопку для подтверждения рассылки
            keyboard = [
                [
                    InlineKeyboardButton("✅ Отправить рассылку", callback_data="admin_confirm_broadcast"),
                    InlineKeyboardButton("❌ Отменить", callback_data="admin_broadcast")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"📢 <b>Подтверждение рассылки</b>\n\n"
                f"Сообщение для рассылки:\n\n"
                f"<i>{message_text[:200]}...</i>\n\n"
                f"👥 <b>Получателей:</b> {len(self.db.get_all_users()) if self.db else 'N/A'}\n\n"
                f"Подтвердите отправку:",
                reply_markup=reply_markup,
                parse_mode='HTML'
            )

    async def handle_cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /cancel для отмены текущих действий"""
        user_id = update.effective_user.id
        
        # Проверяем права администратора
        if not is_admin(user_id):
            await update.message.reply_text("❌ Эта команда доступна только администраторам.")
            return
        
        # Очищаем user_data от данных рассылки
        if 'awaiting_broadcast' in context.user_data:
            context.user_data.pop('awaiting_broadcast')
            context.user_data.pop('broadcast_message', None)
            await update.message.reply_text("✅ Режим рассылки отменен.")
        elif 'broadcast_message' in context.user_data:
            context.user_data.pop('broadcast_message')
            await update.message.reply_text("✅ Сообщение для рассылки удалено.")
        else:
            await update.message.reply_text("ℹ️ Нечего отменять.")

# ФУНКЦИИ ДЛЯ РАССЫЛКИ (оставляем как есть)
async def handle_broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка сообщения для рассылки"""
    if not is_admin(update.effective_user.id):
        return
    
    if not context.user_data.get('awaiting_broadcast'):
        return
    
    message_text = update.message.text
    context.user_data['awaiting_broadcast'] = False
    
    # Получаем базу данных из bot_data
    db = context.bot_data.get('db')
    if not db:
        await update.message.reply_text("❌ База данных не подключена")
        return
    
    # Логируем начало рассылки
    db.log_bot_event("INFO", "Broadcast started", {
        "admin_id": update.effective_user.id,
        "message_length": len(message_text)
    })
    
    # Получаем список пользователей
    user_ids = db.broadcast_message(message_text)
    total_users = len(user_ids)
    
    # Отправляем подтверждение
    await update.message.reply_text(
        f"📢 <b>Рассылка начата!</b>\n\n"
        f"👥 Получателей: {total_users}\n"
        f"📝 Длина сообщения: {len(message_text)} символов\n\n"
        f"⏳ <i>Рассылка может занять несколько минут...</i>",
        parse_mode='HTML'
    )
    
    # Запускаем рассылку в фоне
    asyncio.create_task(send_broadcast(context.bot, user_ids, message_text, db))

async def send_broadcast(bot, user_ids, message, db):
    """Асинхронная отправка рассылки"""
    successful = 0
    failed = 0
    
    for user_id in user_ids:
        try:
            await bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode='HTML'
            )
            successful += 1
        except Exception as e:
            failed += 1
            db.log_bot_event("ERROR", f"Broadcast failed for user {user_id}", {"error": str(e)})
        
        # Задержка чтобы не превысить лимиты Telegram
        await asyncio.sleep(0.1)
    
    # Логируем результат
    db.log_bot_event("INFO", "Broadcast completed", {
        "successful": successful,
        "failed": failed,
        "total": len(user_ids)
    })

async def handle_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка отмены действий"""
    if 'awaiting_broadcast' in context.user_data:
        context.user_data['awaiting_broadcast'] = False
        await update.message.reply_text("❌ Рассылка отменена")
