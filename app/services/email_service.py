from flask import current_app, render_template
from flask_mail import Mail, Message
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.mail = None
        
    def init_app(self, app):
        """Flask uygulamasıyla email servisini başlat"""
        if app.config.get('MAIL_SERVER'):
            self.mail = Mail(app)
            logger.info("Email service initialized")
        else:
            logger.warning("Email service not configured")
    
    def send_reservation_confirmation(self, customer_email: str, customer_name: str, 
                                    reservation_details: dict) -> bool:
        """Rezervasyon onay maili gönder"""
        if not self.mail:
            logger.warning("Email service not configured")
            return False
            
        try:
            subject = "Rezervasyon Onayı - Restaurant Lezzet"
            
            # HTML template kullan
            html_body = render_template(
                'emails/reservation_confirmation.html',
                customer_name=customer_name,
                reservation=reservation_details
            )
            
            # Yedek metin içeriği
            text_body = f"""
Sayın {customer_name},

Restaurant Lezzet rezervasyon onayınız:

Tarih: {reservation_details.get('date')}
Saat: {reservation_details.get('time')}
Kişi Sayısı: {reservation_details.get('party_size')}
Masa: {reservation_details.get('table')}

Rezervasyon Kodu: {reservation_details.get('id')}

Teşekkür ederiz!
Restaurant Lezzet Ekibi
"""
            
            msg = Message(
                subject=subject,
                sender=current_app.config['MAIL_USERNAME'],
                recipients=[customer_email]
            )
            msg.body = text_body
            msg.html = html_body
            
            self.mail.send(msg)
            logger.info(f"Confirmation email sent to {customer_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send confirmation email to {customer_email}: {e}")
            return False
    
    def send_reservation_reminder(self, customer_email: str, customer_name: str,
                                reservation_details: dict) -> bool:
        """Rezervasyon hatırlatma maili gönder"""
        if not self.mail:
            logger.warning("Email service not configured")
            return False
            
        try:
            subject = "Rezervasyon Hatırlatması - Restaurant Lezzet"
            
            text_body = f"""
Sayın {customer_name},

Yarın Restaurant Lezzet'te rezervasyonunuz bulunmaktadır:

Tarih: {reservation_details.get('date')}
Saat: {reservation_details.get('time')}
Kişi Sayısı: {reservation_details.get('party_size')}
Masa: {reservation_details.get('table')}

Rezervasyon Kodu: {reservation_details.get('id')}

Sizi aramızda görmekten mutluluk duyarız!

Restaurant Lezzet Ekibi
(0212) 123 45 67
"""
            
            msg = Message(
                subject=subject,
                sender=current_app.config['MAIL_USERNAME'],
                recipients=[customer_email]
            )
            msg.body = text_body
            
            self.mail.send(msg)
            logger.info(f"Reminder email sent to {customer_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send reminder email to {customer_email}: {e}")
            return False
    
    def send_cancellation_notification(self, customer_email: str, customer_name: str,
                                     reservation_details: dict) -> bool:
        """Rezervasyon iptal bildirimi gönder"""
        if not self.mail:
            logger.warning("Email service not configured")
            return False
            
        try:
            subject = "Rezervasyon İptal Bildirimi - Restaurant Lezzet"
            
            text_body = f"""
Sayın {customer_name},

Aşağıdaki rezervasyonunuz iptal edilmiştir:

Tarih: {reservation_details.get('date')}
Saat: {reservation_details.get('time')}
Kişi Sayısı: {reservation_details.get('party_size')}

Rezervasyon Kodu: {reservation_details.get('id')}

Herhangi bir sorunuz için bizimle iletişime geçebilirsiniz.

Restaurant Lezzet Ekibi
(0212) 123 45 67
"""
            
            msg = Message(
                subject=subject,
                sender=current_app.config['MAIL_USERNAME'],
                recipients=[customer_email]
            )
            msg.body = text_body
            
            self.mail.send(msg)
            logger.info(f"Cancellation email sent to {customer_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send cancellation email to {customer_email}: {e}")
            return False

# Global instance
email_service = EmailService()