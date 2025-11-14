# app/handlers/payments.py
import logging
from telegram import Update, LabeledPrice
from telegram.ext import ContextTypes
from app.config import Config

logger = logging.getLogger(__name__)

class PaymentHandlers:
    async def handle_plan_selection(self, query, context: ContextTypes.DEFAULT_TYPE):
        """Обработка выбора тарифного плана"""
        try:
            months = int(query.data.split("_")[1])
            price = Config.PRICING[str(months)]
            
            # Создаем инвойс
            prices = [LabeledPrice(f"VPN Подписка - {months} мес", int(price * 100))]
            
            # Простой payload (временное решение)
            payload = f"plan_{months}_user_{query.from_user.id}"
            
            await context.bot.send_invoice(
                chat_id=query.from_user.id,
                title=f"🔒 VELTRIX VPN - {months} месяцев",
                description=f"Премиум VPN доступ на {months} месяцев\n• 100GB трафика\n• 3 региона\n• Поддержка 24/7",
                payload=payload,
                provider_token=Config.PROVIDER_TOKEN,
                currency="USD",
                prices=prices,
                start_parameter=f"vpn_subscription_{months}",
            )
            
        except Exception as e:
            logger.error(f"Error creating invoice: {e}")
            await query.message.reply_text("❌ Ошибка создания счета. Попробуйте позже.")
    
    async def pre_checkout(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Предварительная проверка платежа"""
        query = update.pre_checkout_query
        
        try:
            # Простая проверка payload
            if query.invoice_payload.startswith('plan_'):
                await query.answer(ok=True)
            else:
                await query.answer(ok=False, error_message="Неверные данные платежа")
                
        except Exception as e:
            logger.error(f"Pre-checkout error: {e}")
            await query.answer(ok=False, error_message="Ошибка обработки платежа")
    
    async def successful_payment(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка успешного платежа"""
        try:
            user = update.effective_user
            payment = update.message.successful_payment
            
            # Извлекаем информацию из payload
            payload_parts = payment.invoice_payload.split('_')
            months = int(payload_parts[1])
            
            success_text = (
                f"✅ <b>ОПЛАТА УСПЕШНА!</b>\n\n"
                f"• 👤 Пользователь: {user.first_name}\n"
                f"• 📅 Срок: <b>{months} месяцев</b>\n"
                f"• 💰 Сумма: <b>${payment.total_amount / 100:.2f}</b>\n\n"
                f"🔄 <b>Ваш VPN конфиг готовится...</b>\n"
                f"Мы пришлем его в течение 5 минут.\n\n"
                f"💬 При проблемах: @veltrix_support"
            )
            
            await update.message.reply_text(success_text, parse_mode='HTML')
            
            # Здесь будет логика генерации и отправки VPN конфига
            logger.info(f"Successful payment: user {user.id}, {months} months, ${payment.total_amount / 100}")
            
        except Exception as e:
            logger.error(f"Payment processing error: {e}")
            await update.message.reply_text(
                "❌ Ошибка обработки платежа. Обратитесь в поддержку: @veltrix_support"
            )
