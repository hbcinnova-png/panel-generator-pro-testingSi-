from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, Any, List, Optional
from uuid import uuid4
import logging
import json
from enum import Enum

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from twilio.rest import Client as TwilioClient
import requests

from models import Notification, User, NotificationStatus
from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class NotificationType(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"

class NotificationService:
    """Service for sending notifications"""
    
    @staticmethod
    def send_email(
        to_email: str,
        subject: str,
        html_content: str,
        db: Session
    ) -> Notification:
        """Send email notification"""
        
        try:
            if not settings.SENDGRID_API_KEY:
                raise ValueError("SendGrid API key not configured")
            
            message = Mail(
                from_email=settings.ADMIN_EMAIL,
                to_emails=to_email,
                subject=subject,
                html_content=html_content
            )
            
            sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
            response = sg.send(message)
            
            # Create notification record
            notification = Notification(
                id=str(uuid4()),
                type=NotificationType.EMAIL,
                recipient=to_email,
                subject=subject,
                content=html_content,
                status=NotificationStatus.SENT,
                sent_at=datetime.utcnow(),
                created_at=datetime.utcnow()
            )
            
            db.add(notification)
            db.commit()
            
            logger.info(f"Email sent to {to_email}")
            return notification
        
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            raise
    
    @staticmethod
    def send_sms(
        phone_number: str,
        message: str,
        db: Session
    ) -> Notification:
        """Send SMS notification"""
        
        try:
            if not settings.TWILIO_ACCOUNT_SID:
                raise ValueError("Twilio not configured")
            
            client = TwilioClient(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN
            )
            
            sms = client.messages.create(
                body=message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone_number
            )
            
            # Create notification record
            notification = Notification(
                id=str(uuid4()),
                type=NotificationType.SMS,
                recipient=phone_number,
                subject="SMS",
                content=message,
                status=NotificationStatus.SENT,
                sent_at=datetime.utcnow(),
                created_at=datetime.utcnow()
            )
            
            db.add(notification)
            db.commit()
            
            logger.info(f"SMS sent to {phone_number}")
            return notification
        
        except Exception as e:
            logger.error(f"Error sending SMS: {e}")
            raise
    
    @staticmethod
    def send_whatsapp(
        phone_number: str,
        message: str,
        db: Session
    ) -> Notification:
        """Send WhatsApp notification"""
        
        try:
            if not settings.WHATSAPP_BUSINESS_ACCESS_TOKEN:
                raise ValueError("WhatsApp not configured")
            
            url = f"https://graph.instagram.com/v18.0/{settings.WHATSAPP_BUSINESS_PHONE_NUMBER_ID}/messages"
            
            headers = {
                "Authorization": f"Bearer {settings.WHATSAPP_BUSINESS_ACCESS_TOKEN}",
                "Content-Type": "application/json"
            }
            
            data = {
                "messaging_product": "whatsapp",
                "to": phone_number,
                "type": "text",
                "text": {
                    "body": message
                }
            }
            
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            
            # Create notification record
            notification = Notification(
                id=str(uuid4()),
                type=NotificationType.WEBHOOK,
                recipient=phone_number,
                subject="WhatsApp",
                content=message,
                status=NotificationStatus.SENT,
                sent_at=datetime.utcnow(),
                created_at=datetime.utcnow()
            )
            
            db.add(notification)
            db.commit()
            
            logger.info(f"WhatsApp sent to {phone_number}")
            return notification
        
        except Exception as e:
            logger.error(f"Error sending WhatsApp: {e}")
            raise
    
    @staticmethod
    def send_webhook(
        webhook_url: str,
        event: str,
        data: Dict[str, Any],
        db: Session
    ) -> Notification:
        """Send webhook notification"""
        
        try:
            payload = {
                "event": event,
                "data": data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            response = requests.post(
                webhook_url,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            
            # Create notification record
            notification = Notification(
                id=str(uuid4()),
                type=NotificationType.WEBHOOK,
                recipient=webhook_url,
                subject=event,
                content=json.dumps(payload),
                status=NotificationStatus.SENT,
                sent_at=datetime.utcnow(),
                created_at=datetime.utcnow()
            )
            
            db.add(notification)
            db.commit()
            
            logger.info(f"Webhook sent to {webhook_url}")
            return notification
        
        except Exception as e:
            logger.error(f"Error sending webhook: {e}")
            raise
    
    @staticmethod
    def send_panel_created_email(
        user_email: str,
        panel_name: str,
        db: Session
    ) -> Notification:
        """Send panel created email"""
        
        html_content = f"""
        <h2>Panel Created Successfully!</h2>
        <p>Your panel "<strong>{panel_name}</strong>" has been created.</p>
        <p>You can now:</p>
        <ul>
            <li>Customize your panel</li>
            <li>Publish it</li>
            <li>Install it on your WordPress site</li>
        </ul>
        <p>Visit your dashboard to get started!</p>
        """
        
        return NotificationService.send_email(
            user_email,
            f"Panel Created: {panel_name}",
            html_content,
            db
        )
    
    @staticmethod
    def send_installation_ready_email(
        user_email: str,
        panel_name: str,
        download_url: str,
        db: Session
    ) -> Notification:
        """Send installation ready email"""
        
        html_content = f"""
        <h2>Your Panel is Ready to Install!</h2>
        <p>Your panel "<strong>{panel_name}</strong>" is ready for installation.</p>
        <p><a href="{download_url}" style="background: #FF69B4; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Download Plugin</a></p>
        <p>Installation instructions:</p>
        <ol>
            <li>Download the plugin ZIP file</li>
            <li>Go to your WordPress admin</li>
            <li>Upload the plugin</li>
            <li>Activate it</li>
        </ol>
        """
        
        return NotificationService.send_email(
            user_email,
            f"Installation Ready: {panel_name}",
            html_content,
            db
        )
    
    @staticmethod
    def send_payment_confirmation_email(
        user_email: str,
        amount: float,
        plan: str,
        invoice_number: str,
        db: Session
    ) -> Notification:
        """Send payment confirmation email"""
        
        html_content = f"""
        <h2>Payment Confirmed!</h2>
        <p>Thank you for your payment.</p>
        <p><strong>Invoice:</strong> {invoice_number}</p>
        <p><strong>Plan:</strong> {plan}</p>
        <p><strong>Amount:</strong> ${amount:.2f}</p>
        <p>Your subscription is now active. You can start using all features!</p>
        """
        
        return NotificationService.send_email(
            user_email,
            f"Payment Confirmed - Invoice {invoice_number}",
            html_content,
            db
        )
    
    @staticmethod
    def get_notifications(
        user_id: str,
        skip: int = 0,
        limit: int = 10,
        db: Session = None
    ) -> tuple[List[Notification], int]:
        """Get user notifications"""
        
        try:
            query = db.query(Notification).filter(
                Notification.user_id == user_id
            )
            
            total = query.count()
            notifications = query.order_by(
                Notification.created_at.desc()
            ).offset(skip).limit(limit).all()
            
            return notifications, total
        
        except Exception as e:
            logger.error(f"Error getting notifications: {e}")
            raise
