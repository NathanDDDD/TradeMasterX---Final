import os
import requests
from trademasterx.utils.logger import get_logger
from trademasterx.utils.mini_log import log_event

class AlertSystem:
    """Alert system for critical trading events."""
    
    def __init__(self):
        self.logger = get_logger("AlertSystem")
        self.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.email_enabled = os.getenv('EMAIL_ALERTS', 'false').lower() == 'true'
        
    def send_telegram_alert(self, message):
        """Send alert via Telegram bot."""
        if not (self.telegram_bot_token and self.telegram_chat_id):
            self.logger.warning("Telegram credentials not configured")
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            data = {
                "chat_id": self.telegram_chat_id,
                "text": f"🚨 TradeMasterX Alert:\n{message}",
                "parse_mode": "HTML"
            }
            response = requests.post(url, data=data, timeout=10)
            if response.status_code == 200:
                self.logger.info("Telegram alert sent successfully")
                log_event(f"Telegram alert sent: {message[:50]}...")
                return True
            else:
                self.logger.error(f"Telegram alert failed: {response.status_code}")
                return False
        except Exception as e:
            self.logger.error(f"Telegram alert error: {e}")
            return False
    
    def emergency_stop_alert(self):
        """Send emergency stop alert."""
        message = "🚨 EMERGENCY STOP ACTIVATED!\nAll trading has been immediately halted."
        return self.send_telegram_alert(message)
    
    def trade_executed_alert(self, symbol, side, amount, price):
        """Send trade execution alert."""
        message = f"📈 Trade Executed:\n{symbol} {side.upper()}\nAmount: {amount}\nPrice: ${price}"
        return self.send_telegram_alert(message)
    
    def error_alert(self, error_message):
        """Send error alert."""
        message = f"⚠️ System Error:\n{error_message}"
        return self.send_telegram_alert(message)
    
    def system_status_alert(self, status):
        """Send system status alert."""
        message = f"📊 System Status:\n{status}"
        return self.send_telegram_alert(message)
    
    def test_alert(self):
        """Send test alert to verify configuration."""
        message = "🧪 Test Alert: TradeMasterX alert system is working correctly!"
        return self.send_telegram_alert(message) 