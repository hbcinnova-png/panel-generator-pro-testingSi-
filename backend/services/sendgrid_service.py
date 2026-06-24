from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, Personalization, Category, Attachment
import logging
from typing import Dict, Any, List
from datetime import datetime
from sqlalchemy.orm import Session
from models import Notification
import os
import base64

logger = logging.getLogger(__name__)

# Configurar SendGrid
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL", "noreply@panelgenerator.com")
SENDGRID_FROM_NAME = os.getenv("SENDGRID_FROM_NAME", "Panel Generator Pro")

sg = SendGridAPIClient(SENDGRID_API_KEY)

class SendGridService:
    """Servicio completo de integración con SendGrid"""
    
    @staticmethod
    def send_email(
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str = None,
        user_id: str = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """Enviar email"""
        try:
            message = Mail(
                from_email=Email(SENDGRID_FROM_EMAIL, SENDGRID_FROM_NAME),
                to_emails=To(to_email),
                subject=subject,
                html_content=html_content,
                plain_text_content=text_content
            )
            
            response = sg.send(message)
            
            # Guardar en BD
            if db and user_id:
                notification = Notification(
                    user_id=user_id,
                    type="email",
                    recipient=to_email,
                    message=subject,
                    status="sent",
                    external_id=response.headers.get("X-Message-Id"),
                    sent_at=datetime.utcnow()
                )
                db.add(notification)
                db.commit()
            
            logger.info(f"Email sent to {to_email}: {response.status_code}")
            
            return {
                "status": "sent",
                "email": to_email,
                "message_id": response.headers.get("X-Message-Id"),
                "status_code": response.status_code
            }
        
        except Exception as e:
            logger.error(f"SendGrid error: {e}")
            raise Exception(f"Error sending email: {str(e)}")
    
    @staticmethod
    def send_bulk_email(
        recipients: List[Dict[str, str]],
        subject: str,
        html_content: str,
        text_content: str = None,
        user_id: str = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """Enviar email en lote"""
        try:
            message = Mail(
                from_email=Email(SENDGRID_FROM_EMAIL, SENDGRID_FROM_NAME),
                subject=subject,
                html_content=html_content,
                plain_text_content=text_content
            )
            
            # Agregar personalizaciones
            for recipient in recipients:
                p = Personalization()
                p.add_to(To(recipient["email"], recipient.get("name", "")))
                message.add_personalization(p)
            
            response = sg.send(message)
            
            # Guardar en BD
            if db and user_id:
                for recipient in recipients:
                    notification = Notification(
                        user_id=user_id,
                        type="email",
                        recipient=recipient["email"],
                        message=subject,
                        status="sent",
                        external_id=response.headers.get("X-Message-Id"),
                        sent_at=datetime.utcnow()
                    )
                    db.add(notification)
                db.commit()
            
            logger.info(f"Bulk email sent to {len(recipients)} recipients")
            
            return {
                "status": "sent",
                "recipients": len(recipients),
                "message_id": response.headers.get("X-Message-Id"),
                "status_code": response.status_code
            }
        
        except Exception as e:
            logger.error(f"SendGrid bulk error: {e}")
            raise Exception(f"Error sending bulk email: {str(e)}")
    
    @staticmethod
    def send_email_with_attachment(
        to_email: str,
        subject: str,
        html_content: str,
        attachment_path: str,
        attachment_name: str = None,
        user_id: str = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """Enviar email con adjunto"""
        try:
            message = Mail(
                from_email=Email(SENDGRID_FROM_EMAIL, SENDGRID_FROM_NAME),
                to_emails=To(to_email),
                subject=subject,
                html_content=html_content
            )
            
            # Agregar adjunto
            with open(attachment_path, 'rb') as f:
                file_content = f.read()
            
            attachment = Attachment(
                file_content=base64.b64encode(file_content).decode(),
                file_name=attachment_name or os.path.basename(attachment_path),
                file_type="application/octet-stream"
            )
            message.attachment = attachment
            
            response = sg.send(message)
            
            # Guardar en BD
            if db and user_id:
                notification = Notification(
                    user_id=user_id,
                    type="email",
                    recipient=to_email,
                    message=subject,
                    status="sent",
                    external_id=response.headers.get("X-Message-Id"),
                    sent_at=datetime.utcnow()
                )
                db.add(notification)
                db.commit()
            
            logger.info(f"Email with attachment sent to {to_email}")
            
            return {
                "status": "sent",
                "email": to_email,
                "message_id": response.headers.get("X-Message-Id"),
                "attachment": attachment_name or os.path.basename(attachment_path)
            }
        
        except Exception as e:
            logger.error(f"SendGrid attachment error: {e}")
            raise Exception(f"Error sending email with attachment: {str(e)}")
    
    @staticmethod
    def send_template_email(
        to_email: str,
        template_id: str,
        template_data: Dict[str, Any],
        user_id: str = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """Enviar email con template"""
        try:
            message = Mail(
                from_email=Email(SENDGRID_FROM_EMAIL, SENDGRID_FROM_NAME),
                to_emails=To(to_email)
            )
            
            message.template_id = template_id
            
            # Agregar datos dinámicos
            p = Personalization()
            p.add_to(To(to_email))
            for key, value in template_data.items():
                p.dynamic_template_data = template_data
            message.add_personalization(p)
            
            response = sg.send(message)
            
            # Guardar en BD
            if db and user_id:
                notification = Notification(
                    user_id=user_id,
                    type="email",
                    recipient=to_email,
                    message=f"Template: {template_id}",
                    status="sent",
                    external_id=response.headers.get("X-Message-Id"),
                    sent_at=datetime.utcnow()
                )
                db.add(notification)
                db.commit()
            
            logger.info(f"Template email sent to {to_email}")
            
            return {
                "status": "sent",
                "email": to_email,
                "template_id": template_id,
                "message_id": response.headers.get("X-Message-Id")
            }
        
        except Exception as e:
            logger.error(f"SendGrid template error: {e}")
            raise Exception(f"Error sending template email: {str(e)}")
    
    @staticmethod
    def send_transactional_email(
        to_email: str,
        subject: str,
        html_content: str,
        category: str = "transactional",
        user_id: str = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """Enviar email transaccional"""
        try:
            message = Mail(
                from_email=Email(SENDGRID_FROM_EMAIL, SENDGRID_FROM_NAME),
                to_emails=To(to_email),
                subject=subject,
                html_content=html_content
            )
            
            message.category = Category(category)
            
            response = sg.send(message)
            
            # Guardar en BD
            if db and user_id:
                notification = Notification(
                    user_id=user_id,
                    type="email",
                    recipient=to_email,
                    message=subject,
                    status="sent",
                    external_id=response.headers.get("X-Message-Id"),
                    sent_at=datetime.utcnow()
                )
                db.add(notification)
                db.commit()
            
            logger.info(f"Transactional email sent to {to_email}")
            
            return {
                "status": "sent",
                "email": to_email,
                "message_id": response.headers.get("X-Message-Id"),
                "category": category
            }
        
        except Exception as e:
            logger.error(f"SendGrid transactional error: {e}")
            raise Exception(f"Error sending transactional email: {str(e)}")
    
    @staticmethod
    def send_password_reset_email(
        to_email: str,
        reset_link: str,
        user_name: str = None,
        user_id: str = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """Enviar email de reseteo de contraseña"""
        try:
            html_content = f"""
            <html>
                <body>
                    <h2>Resetear Contraseña</h2>
                    <p>Hola {user_name or 'Usuario'},</p>
                    <p>Haz clic en el siguiente enlace para resetear tu contraseña:</p>
                    <p><a href="{reset_link}">Resetear Contraseña</a></p>
                    <p>Si no solicitaste esto, ignora este email.</p>
                    <p>Panel Generator Pro</p>
                </body>
            </html>
            """
            
            return SendGridService.send_transactional_email(
                to_email=to_email,
                subject="Resetear Contraseña - Panel Generator Pro",
                html_content=html_content,
                category="password_reset",
                user_id=user_id,
                db=db
            )
        
        except Exception as e:
            logger.error(f"SendGrid password reset error: {e}")
            raise Exception(f"Error sending password reset email: {str(e)}")
    
    @staticmethod
    def send_welcome_email(
        to_email: str,
        user_name: str = None,
        user_id: str = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """Enviar email de bienvenida"""
        try:
            html_content = f"""
            <html>
                <body>
                    <h2>Bienvenido a Panel Generator Pro</h2>
                    <p>Hola {user_name or 'Usuario'},</p>
                    <p>Gracias por registrarte en Panel Generator Pro.</p>
                    <p>Ahora puedes comenzar a crear paneles personalizados.</p>
                    <p><a href="https://panelgenerator.com/dashboard">Ir al Dashboard</a></p>
                    <p>Panel Generator Pro</p>
                </body>
            </html>
            """
            
            return SendGridService.send_transactional_email(
                to_email=to_email,
                subject="Bienvenido a Panel Generator Pro",
                html_content=html_content,
                category="welcome",
                user_id=user_id,
                db=db
            )
        
        except Exception as e:
            logger.error(f"SendGrid welcome error: {e}")
            raise Exception(f"Error sending welcome email: {str(e)}")
    
    @staticmethod
    def send_invoice_email(
        to_email: str,
        invoice_number: str,
        amount: float,
        invoice_url: str,
        user_id: str = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """Enviar email de factura"""
        try:
            html_content = f"""
            <html>
                <body>
                    <h2>Tu Factura</h2>
                    <p>Factura: {invoice_number}</p>
                    <p>Monto: ${amount:.2f}</p>
                    <p><a href="{invoice_url}">Descargar Factura</a></p>
                    <p>Panel Generator Pro</p>
                </body>
            </html>
            """
            
            return SendGridService.send_transactional_email(
                to_email=to_email,
                subject=f"Factura {invoice_number} - Panel Generator Pro",
                html_content=html_content,
                category="invoice",
                user_id=user_id,
                db=db
            )
        
        except Exception as e:
            logger.error(f"SendGrid invoice error: {e}")
            raise Exception(f"Error sending invoice email: {str(e)}")
