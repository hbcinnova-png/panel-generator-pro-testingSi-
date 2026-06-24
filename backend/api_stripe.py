from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime
import logging
import json

from database import SessionLocal
from models import User, Subscription, Payment
from security import get_current_user
from services.stripe_service import StripeService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/stripe", tags=["stripe"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==================== SUBSCRIPTIONS ====================

@router.post("/subscriptions")
async def create_subscription(
    plan: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crear suscripción"""
    try:
        result = StripeService.create_subscription(
            user=current_user,
            plan=plan,
            db=db
        )
        
        return {
            "status": "success",
            "subscription": result
        }
    
    except Exception as e:
        logger.error(f"Error creating subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/subscriptions")
async def get_subscriptions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener suscripciones del usuario"""
    try:
        subscriptions = db.query(Subscription).filter(
            Subscription.user_id == current_user.id
        ).all()
        
        return {
            "subscriptions": [
                {
                    "id": s.id,
                    "plan": s.plan,
                    "status": s.status,
                    "price": s.price,
                    "currency": s.currency,
                    "started_at": s.started_at,
                    "ends_at": s.ends_at,
                    "stripe_subscription_id": s.stripe_subscription_id
                }
                for s in subscriptions
            ]
        }
    
    except Exception as e:
        logger.error(f"Error getting subscriptions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting subscriptions"
        )

@router.get("/subscriptions/{subscription_id}/status")
async def get_subscription_status(
    subscription_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener estado de suscripción"""
    try:
        subscription = db.query(Subscription).filter(
            (Subscription.id == subscription_id) & 
            (Subscription.user_id == current_user.id)
        ).first()
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found"
            )
        
        status_info = StripeService.get_subscription_status(
            subscription.stripe_subscription_id
        )
        
        return status_info
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting subscription status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting subscription status"
        )

@router.post("/subscriptions/{subscription_id}/update")
async def update_subscription(
    subscription_id: str,
    new_plan: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualizar plan de suscripción"""
    try:
        subscription = db.query(Subscription).filter(
            (Subscription.id == subscription_id) & 
            (Subscription.user_id == current_user.id)
        ).first()
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found"
            )
        
        result = StripeService.update_subscription(
            subscription_id=subscription.stripe_subscription_id,
            new_plan=new_plan,
            db=db
        )
        
        return {
            "status": "success",
            "subscription": result
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/subscriptions/{subscription_id}/cancel")
async def cancel_subscription(
    subscription_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancelar suscripción"""
    try:
        subscription = db.query(Subscription).filter(
            (Subscription.id == subscription_id) & 
            (Subscription.user_id == current_user.id)
        ).first()
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found"
            )
        
        result = StripeService.cancel_subscription(
            subscription_id=subscription.stripe_subscription_id,
            db=db
        )
        
        return {
            "status": "success",
            "subscription": result
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error canceling subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# ==================== PAYMENTS ====================

@router.post("/payments/intent")
async def create_payment_intent(
    amount: float,
    description: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crear payment intent"""
    try:
        result = StripeService.create_payment_intent(
            user=current_user,
            amount=amount,
            description=description,
            db=db
        )
        
        return {
            "status": "success",
            "payment": result
        }
    
    except Exception as e:
        logger.error(f"Error creating payment intent: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/payments/{payment_id}/confirm")
async def confirm_payment(
    payment_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Confirmar pago"""
    try:
        result = StripeService.confirm_payment(
            payment_intent_id=payment_id,
            db=db
        )
        
        return {
            "status": "success",
            "payment": result
        }
    
    except Exception as e:
        logger.error(f"Error confirming payment: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/payments")
async def get_payments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener pagos del usuario"""
    try:
        payments = db.query(Payment).filter(
            Payment.user_id == current_user.id
        ).all()
        
        return {
            "payments": [
                {
                    "id": p.id,
                    "amount": p.amount,
                    "currency": p.currency,
                    "status": p.status,
                    "description": p.description,
                    "created_at": p.created_at,
                    "paid_at": p.paid_at
                }
                for p in payments
            ]
        }
    
    except Exception as e:
        logger.error(f"Error getting payments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting payments"
        )

# ==================== INVOICES ====================

@router.post("/invoices")
async def create_invoice(
    amount: float,
    description: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crear factura"""
    try:
        result = StripeService.create_invoice(
            user=current_user,
            amount=amount,
            description=description,
            db=db
        )
        
        return {
            "status": "success",
            "invoice": result
        }
    
    except Exception as e:
        logger.error(f"Error creating invoice: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/invoices")
async def get_invoices(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener facturas del usuario"""
    try:
        from models import Invoice
        
        invoices = db.query(Invoice).filter(
            Invoice.user_id == current_user.id
        ).all()
        
        return {
            "invoices": [
                {
                    "id": i.id,
                    "invoice_number": i.invoice_number,
                    "amount": i.amount,
                    "status": i.status,
                    "description": i.description,
                    "created_at": i.created_at,
                    "pdf_url": i.pdf_url
                }
                for i in invoices
            ]
        }
    
    except Exception as e:
        logger.error(f"Error getting invoices: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting invoices"
        )

# ==================== WEBHOOKS ====================

@router.post("/webhooks")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Manejar webhooks de Stripe"""
    try:
        payload = await request.body()
        sig_header = request.headers.get("stripe-signature")
        
        # Verificar firma
        if not StripeService.verify_webhook_signature(payload, sig_header):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid signature"
            )
        
        # Parsear evento
        event = json.loads(payload)
        
        # Manejar evento
        success = StripeService.handle_webhook(event, db)
        
        if success:
            return {"status": "success"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Webhook processing failed"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook processing error"
        )

# ==================== PLANS ====================

@router.get("/plans")
async def get_plans():
    """Obtener planes disponibles"""
    try:
        plans = StripeService.PLANS
        
        return {
            "plans": [
                {
                    "key": key,
                    "name": plan["name"],
                    "price": plan["price"],
                    "currency": plan["currency"],
                    "interval": plan["interval"],
                    "features": plan["features"]
                }
                for key, plan in plans.items()
            ]
        }
    
    except Exception as e:
        logger.error(f"Error getting plans: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting plans"
        )
