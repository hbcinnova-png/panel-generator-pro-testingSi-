from twilio.rest import Client
import logging
from typing import Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from models import Notification
import os

logger = logging.getLogger(__name__)

# Configurar Twilio
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

class TwilioService:
    """Servicio completo de integración con Twilio"""
    
    @staticmethod
    def send_sms(phone_number: str, message: str, user_id: str, db: Session) -> Dict[str, Any]:
        """Enviar SMS"""
        try:
            message_obj = client.messages.create(
                body=message,
                from_=TWILIO_PHONE_NUMBER,
                to=phone_number
            )
            
            # Guardar en BD
            notification = Notification(
                user_id=user_id,
                type="sms",
                recipient=phone_number,
                message=message,
                status="sent",
                external_id=message_obj.sid,
                sent_at=datetime.utcnow()
            )
            db.add(notification)
            db.commit()
            
            logger.info(f"SMS sent: {message_obj.sid}")
            
            return {
                "message_id": message_obj.sid,
                "status": message_obj.status,
                "phone": phone_number
            }
        
        except Exception as e:
            logger.error(f"Twilio SMS error: {e}")
            raise Exception(f"Error sending SMS: {str(e)}")
    
    @staticmethod
    def send_whatsapp(phone_number: str, message: str, user_id: str, db: Session) -> Dict[str, Any]:
        """Enviar WhatsApp"""
        try:
            message_obj = client.messages.create(
                body=message,
                from_=f"whatsapp:{TWILIO_WHATSAPP_NUMBER}",
                to=f"whatsapp:{phone_number}"
            )
            
            # Guardar en BD
            notification = Notification(
                user_id=user_id,
                type="whatsapp",
                recipient=phone_number,
                message=message,
                status="sent",
                external_id=message_obj.sid,
                sent_at=datetime.utcnow()
            )
            db.add(notification)
            db.commit()
            
            logger.info(f"WhatsApp sent: {message_obj.sid}")
            
            return {
                "message_id": message_obj.sid,
                "status": message_obj.status,
                "phone": phone_number
            }
        
        except Exception as e:
            logger.error(f"Twilio WhatsApp error: {e}")
            raise Exception(f"Error sending WhatsApp: {str(e)}")
    
    @staticmethod
    def send_whatsapp_template(phone_number: str, template_name: str, variables: Dict[str, str], user_id: str, db: Session) -> Dict[str, Any]:
        """Enviar WhatsApp con template"""
        try:
            message_obj = client.messages.create(
                from_=f"whatsapp:{TWILIO_WHATSAPP_NUMBER}",
                to=f"whatsapp:{phone_number}",
                content_sid=template_name,
                content_variables=str(variables)
            )
            
            # Guardar en BD
            notification = Notification(
                user_id=user_id,
                type="whatsapp_template",
                recipient=phone_number,
                message=f"Template: {template_name}",
                status="sent",
                external_id=message_obj.sid,
                sent_at=datetime.utcnow()
            )
            db.add(notification)
            db.commit()
            
            logger.info(f"WhatsApp template sent: {message_obj.sid}")
            
            return {
                "message_id": message_obj.sid,
                "status": message_obj.status,
                "phone": phone_number
            }
        
        except Exception as e:
            logger.error(f"Twilio WhatsApp template error: {e}")
            raise Exception(f"Error sending WhatsApp template: {str(e)}")
    
    @staticmethod
    def get_message_status(message_id: str) -> Dict[str, Any]:
        """Obtener estado de mensaje"""
        try:
            message = client.messages(message_id).fetch()
            
            return {
                "message_id": message.sid,
                "status": message.status,
                "from": message.from_,
                "to": message.to,
                "date_sent": message.date_sent,
                "date_created": message.date_created
            }
        
        except Exception as e:
            logger.error(f"Twilio error getting message: {e}")
            raise Exception(f"Error getting message: {str(e)}")
    
    @staticmethod
    def send_bulk_sms(phone_numbers: list, message: str, user_id: str, db: Session) -> Dict[str, Any]:
        """Enviar SMS en lote"""
        try:
            results = []
            
            for phone_number in phone_numbers:
                try:
                    message_obj = client.messages.create(
                        body=message,
                        from_=TWILIO_PHONE_NUMBER,
                        to=phone_number
                    )
                    
                    # Guardar en BD
                    notification = Notification(
                        user_id=user_id,
                        type="sms",
                        recipient=phone_number,
                        message=message,
                        status="sent",
                        external_id=message_obj.sid,
                        sent_at=datetime.utcnow()
                    )
                    db.add(notification)
                    
                    results.append({
                        "phone": phone_number,
                        "message_id": message_obj.sid,
                        "status": "sent"
                    })
                
                except Exception as e:
                    results.append({
                        "phone": phone_number,
                        "status": "failed",
                        "error": str(e)
                    })
            
            db.commit()
            
            logger.info(f"Bulk SMS sent: {len(results)} messages")
            
            return {
                "total": len(phone_numbers),
                "sent": len([r for r in results if r["status"] == "sent"]),
                "failed": len([r for r in results if r["status"] == "failed"]),
                "results": results
            }
        
        except Exception as e:
            logger.error(f"Twilio bulk SMS error: {e}")
            raise Exception(f"Error sending bulk SMS: {str(e)}")
    
    @staticmethod
    def send_bulk_whatsapp(phone_numbers: list, message: str, user_id: str, db: Session) -> Dict[str, Any]:
        """Enviar WhatsApp en lote"""
        try:
            results = []
            
            for phone_number in phone_numbers:
                try:
                    message_obj = client.messages.create(
                        body=message,
                        from_=f"whatsapp:{TWILIO_WHATSAPP_NUMBER}",
                        to=f"whatsapp:{phone_number}"
                    )
                    
                    # Guardar en BD
                    notification = Notification(
                        user_id=user_id,
                        type="whatsapp",
                        recipient=phone_number,
                        message=message,
                        status="sent",
                        external_id=message_obj.sid,
                        sent_at=datetime.utcnow()
                    )
                    db.add(notification)
                    
                    results.append({
                        "phone": phone_number,
                        "message_id": message_obj.sid,
                        "status": "sent"
                    })
                
                except Exception as e:
                    results.append({
                        "phone": phone_number,
                        "status": "failed",
                        "error": str(e)
                    })
            
            db.commit()
            
            logger.info(f"Bulk WhatsApp sent: {len(results)} messages")
            
            return {
                "total": len(phone_numbers),
                "sent": len([r for r in results if r["status"] == "sent"]),
                "failed": len([r for r in results if r["status"] == "failed"]),
                "results": results
            }
        
        except Exception as e:
            logger.error(f"Twilio bulk WhatsApp error: {e}")
            raise Exception(f"Error sending bulk WhatsApp: {str(e)}")
