from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
import logging

from database import SessionLocal
from models import User
from security import get_current_user
from services.paypal_service import PayPalService
from services.twilio_service import TwilioService
from services.sendgrid_service import SendGridService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/integrations", tags=["integrations"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==================== PAYPAL ====================

@router.post("/paypal/agreements")
async def create_paypal_agreement(
    plan_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crear acuerdo de suscripción en PayPal"""
    try:
        result = PayPalService.create_agreement(current_user, plan_id, db)
        return {"status": "success", "agreement": result}
    except Exception as e:
        logger.error(f"Error creating PayPal agreement: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/paypal/agreements/{token}/execute")
async def execute_paypal_agreement(
    token: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ejecutar acuerdo de suscripción en PayPal"""
    try:
        result = PayPalService.execute_agreement(token, db)
        return {"status": "success", "agreement": result}
    except Exception as e:
        logger.error(f"Error executing PayPal agreement: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/paypal/payments")
async def create_paypal_payment(
    amount: float,
    description: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crear pago único en PayPal"""
    try:
        result = PayPalService.create_payment(current_user, amount, description, db)
        return {"status": "success", "payment": result}
    except Exception as e:
        logger.error(f"Error creating PayPal payment: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/paypal/payments/{payment_id}/execute")
async def execute_paypal_payment(
    payment_id: str,
    payer_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ejecutar pago en PayPal"""
    try:
        result = PayPalService.execute_payment(payment_id, payer_id, db)
        return {"status": "success", "payment": result}
    except Exception as e:
        logger.error(f"Error executing PayPal payment: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# ==================== TWILIO ====================

@router.post("/twilio/sms")
async def send_sms(
    phone_number: str,
    message: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enviar SMS"""
    try:
        result = TwilioService.send_sms(phone_number, message, current_user.id, db)
        return {"status": "success", "sms": result}
    except Exception as e:
        logger.error(f"Error sending SMS: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/twilio/whatsapp")
async def send_whatsapp(
    phone_number: str,
    message: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enviar WhatsApp"""
    try:
        result = TwilioService.send_whatsapp(phone_number, message, current_user.id, db)
        return {"status": "success", "whatsapp": result}
    except Exception as e:
        logger.error(f"Error sending WhatsApp: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/twilio/sms/bulk")
async def send_bulk_sms(
    phone_numbers: list,
    message: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enviar SMS en lote"""
    try:
        result = TwilioService.send_bulk_sms(phone_numbers, message, current_user.id, db)
        return {"status": "success", "bulk_sms": result}
    except Exception as e:
        logger.error(f"Error sending bulk SMS: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/twilio/whatsapp/bulk")
async def send_bulk_whatsapp(
    phone_numbers: list,
    message: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enviar WhatsApp en lote"""
    try:
        result = TwilioService.send_bulk_whatsapp(phone_numbers, message, current_user.id, db)
        return {"status": "success", "bulk_whatsapp": result}
    except Exception as e:
        logger.error(f"Error sending bulk WhatsApp: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# ==================== SENDGRID ====================

@router.post("/sendgrid/email")
async def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enviar email"""
    try:
        result = SendGridService.send_email(to_email, subject, html_content, user_id=current_user.id, db=db)
        return {"status": "success", "email": result}
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/sendgrid/email/bulk")
async def send_bulk_email(
    recipients: list,
    subject: str,
    html_content: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enviar email en lote"""
    try:
        result = SendGridService.send_bulk_email(recipients, subject, html_content, user_id=current_user.id, db=db)
        return {"status": "success", "bulk_email": result}
    except Exception as e:
        logger.error(f"Error sending bulk email: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/sendgrid/email/template")
async def send_template_email(
    to_email: str,
    template_id: str,
    template_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enviar email con template"""
    try:
        result = SendGridService.send_template_email(to_email, template_id, template_data, user_id=current_user.id, db=db)
        return {"status": "success", "email": result}
    except Exception as e:
        logger.error(f"Error sending template email: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/sendgrid/email/password-reset")
async def send_password_reset_email(
    to_email: str,
    reset_link: str,
    user_name: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enviar email de reseteo de contraseña"""
    try:
        result = SendGridService.send_password_reset_email(to_email, reset_link, user_name, user_id=current_user.id, db=db)
        return {"status": "success", "email": result}
    except Exception as e:
        logger.error(f"Error sending password reset email: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/sendgrid/email/welcome")
async def send_welcome_email(
    to_email: str,
    user_name: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enviar email de bienvenida"""
    try:
        result = SendGridService.send_welcome_email(to_email, user_name, user_id=current_user.id, db=db)
        return {"status": "success", "email": result}
    except Exception as e:
        logger.error(f"Error sending welcome email: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/sendgrid/email/invoice")
async def send_invoice_email(
    to_email: str,
    invoice_number: str,
    amount: float,
    invoice_url: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enviar email de factura"""
    try:
        result = SendGridService.send_invoice_email(to_email, invoice_number, amount, invoice_url, user_id=current_user.id, db=db)
        return {"status": "success", "email": result}
    except Exception as e:
        logger.error(f"Error sending invoice email: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
