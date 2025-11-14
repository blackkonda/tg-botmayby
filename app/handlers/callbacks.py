from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from app.services.database import db
from app.services.vpn_generator import vpn_generator

class CallbackHandlers:
    async def free_trial(self, query, context):
        """Бесплатная пробная версия"""
        user_id = query.from_user.id
        
        # Получаем или создаем подписку
        subscription = await db.get_user_subscription(user_id)
        
        if subscription:
            vpn_config = vpn_generator.generate_vless_config(user_id, subscription['uuid'])
            
            text = (
                f"🎁 <b>ВАШ БЕСПЛАТНЫЙ ДОСТУП</b>\n\n"
                f"• ⏰ Действует до: <b>{subscription['expiry'].strftime('%d.%m.%Y %H:%M')}</b>\n"
                f"• 📊 Трафик: <b>5GB</b>\n"
                f"• 🌍 Регион: <b>{subscription['server_region']}</b>\n\n"
                f"🔗 <b>Ваша ссылка:</b>\n"
                f"<code>{vpn_config['link']}</code>\n\n"
                f"💡 После окончания пробного периода подписка автоматически не продлевается"
            )
        else:
            text = "❌ Ошибка получения пробной версии. Попробуйте позже."
        
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')
    
    async def speed_test(self, query, context):
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
            "После подключения к VPN скорость может снизиться на 10-15%"
        )
        
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')
    
    async def show_affiliate(self, query, context):
        """Партнерская программа"""
        user_id = query.from_user.id
        
        text = (
            "🤝 <b>ПАРТНЕРСКАЯ ПРОГРАММА</b>\n\n"
            "Приводите друзей и получайте <b>20%</b> с каждой их оплаты!\n\n"
            "🎯 <b>Как это работает:</b>\n"
            "1. 🔗 Ваша реферальная ссылка:\n"
            f"   <code>https://t.me/{(await context.bot.get_me()).username}?start={user_id}</code>\n\n"
            "2. 👥 Друг переходит по ссылке и покупает VPN\n"
            "3. 💰 Вы получаете 20% от его платежей\n"
            "4. 📊 Статистика в реальном времени\n\n"
            "💵 <b>Вывод средств:</b> от $10 на карту или крипто\n"
            "📈 <b>Статистика:</b> 0 приглашенных | $0 заработано"
        )
        
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')
    
    async def show_settings(self, query, context):
        """Настройки"""
        user_id = query.from_user.id
        subscription = await db.get_user_subscription(user_id)
        
        if subscription:
            status = "🟢 АКТИВНА" if subscription['expiry'] > datetime.now() else "🔴 ИСТЕКЛА"
            text = (
                f"⚙️ <b>ВАШИ НАСТРОЙКИ</b>\n\n"
                f"• 👤 ID: <code>{user_id}</code>\n"
                f"• 🛡️ Статус: {status}\n"
                f"• 📅 Окончание: {subscription['expiry'].strftime('%d.%m.%Y %H:%M')}\n"
                f"• 📊 Трафик: {subscription['traffic_used']/1024/1024/1024:.2f}GB / {subscription['traffic_limit']/1024/1024/1024:.2f}GB\n"
                f"• 🌍 Регион: {subscription['server_region']}\n\n"
                f"🔧 <b>Доступные действия:</b>"
            )
            
            keyboard = [
                [InlineKeyboardButton("🔄 Сменить регион", callback_data="change_region")],
                [InlineKeyboardButton("📊 Сбросить статистику", callback_data="reset_stats")],
                [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]
            ]
        else:
            text = "❌ Подписка не найдена"
            keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')
    
    async def show_info(self, query, context):
        """Информация о сервисе"""
        text = (
            "ℹ️ <b>ИНФОРМАЦИЯ О VELTRIX VPN</b>\n\n"
            "🔒 <b>Безопасность:</b>\n"
            "• 🛡️ Reality Protocol - обход блокировок\n"
            "• 🔐 Zero-Logs - никаких логов\n"
            "• 🌐 TLS 1.3 + HTTPS\n"
            "• 💻 256-битное шифрование\n\n"
            "🚀 <b>Технологии:</b>\n"
            "• 📡 VLESS + gRPC транспортировка\n"
            "• 🌍 3 дата-центра (EU, US, ASIA)\n"
            "• ⚡ 10+ Gbps каналы\n"
            "• 🔄 Авто-балансировка нагрузки\n\n"
            "📱 <b>Поддерживаемые платформы:</b>\n"
            "• Android: V2RayNG, NekoBox\n"
            "• iOS: FoXray, Stash\n"
            "• Windows: NekoRay, v2rayN\n"
            "• macOS: V2RayU, Qv2ray\n\n"
            "💬 <b>Поддержка:</b> @veltrix_support\n"
            "🌐 <b>Сайт:</b> veltrix-vpn.com"
        )
        
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')
    
    async def back_to_main(self, query, context):
        """Возврат в главное меню"""
        await self.start(query, context)
