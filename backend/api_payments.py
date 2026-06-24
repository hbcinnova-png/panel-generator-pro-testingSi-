from fastapi import APIRouter, HTTPException, status, Depends, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
import logging
import stripe
try:
    from paypalrestsdk import Payment as PayPalPayment
except Exception as paypal_import_error:
    class PayPalPayment:
        def __init__(self, *args, **kwargs):
            raise RuntimeError(f"PayPal SDK disabled: {paypal_import_error}")

from config import get_settings
from models import User, Subscription, Invoice, SubscriptionPlan, PaymentStatus
from database import get_db
from api_auth import get_current_user

settings = get_settings()
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/payments", tags=["Payments"])

# Configure Stripe
if settings.STRIPE_SECRET_KEY:
    stripe.api_key = settings.STRIPE_SECRET_KEY

# ==================== SCHEMAS ====================

class SubscriptionRequest(BaseModel):
    plan: str  # free, starter, pro, enterprise
    billing_cycle: str = "monthly"  # monthly, yearly

class PaymentMethodRequest(BaseModel):
    token: str
    payment_method: str  # stripe, paypal

class InvoiceResponse(BaseModel):
    id: str
    invoice_number: str
    amount: float
    currency: str
    status: str
    issue_date: datetime
    due_date: Optional[datetime]
    paid_date: Optional[datetime]

# ==================== ENDPOINTS ====================

@router.get("/plans")
async def get_subscription_plans():
    """Get available subscription plans"""
    
    plans = {
        "free": {
            "name": "Free",
            "price": 0,
            "currency": "USD",
            "features": [
                "1 panel",
                "Basic themes",
                "Community support"
            ],
            "limits": {
                "panels": 1,
                "monthly_views": 1000,
                "api_calls": 1000
            }
        },
        "starter": {
            "name": "Starter",
            "price": 29,
            "currency": "USD",
            "billing_cycles": {
                "monthly": 29,
                "yearly": 290
            },
            "features": [
                "5 panels",
                "All themes",
                "Email support",
                "Analytics"
            ],
            "limits": {
                "panels": 5,
                "monthly_views": 10000,
                "api_calls": 10000
            }
        },
        "pro": {
            "name": "Professional",
            "price": 79,
            "currency": "USD",
            "billing_cycles": {
                "monthly": 79,
                "yearly": 790
            },
            "features": [
                "Unlimited panels",
                "Premium themes",
                "Priority support",
                "Advanced analytics",
                "Custom integrations"
            ],
            "limits": {
                "panels": -1,  # unlimited
                "monthly_views": -1,
                "api_calls": 100000
            }
        },
        "enterprise": {
            "name": "Enterprise",
            "price": "Custom",
            "currency": "USD",
            "features": [
                "Everything in Pro",
                "Dedicated support",
                "Custom development",
                "SLA guarantee",
                "White label"
            ],
            "contact": "sales@panelgenerator.pro"
        }
    }
    
    return plans

@router.post("/subscribe")
async def subscribe_to_plan(
    request: SubscriptionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Subscribe to a plan"""
    
    # Get plan details
    plans = {
        "starter": 29,
        "pro": 79,
        "enterprise": 299
    }
    
    if request.plan not in plans:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid plan"
        )
    
    price = plans[request.plan]
    
    # Adjust for yearly billing
    if request.billing_cycle == "yearly":
        price *= 12 * 0.8  # 20% discount for yearly
    
    # Create subscription
    subscription = Subscription(
        user_id=current_user.id,
        plan=request.plan,
        price=price,
        billing_cycle=request.billing_cycle,
        current_period_start=datetime.utcnow(),
        current_period_end=datetime.utcnow() + timedelta(days=365 if request.billing_cycle == "yearly" else 30)
    )
    
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    
    # Update user subscription
    current_user.subscription_plan = request.plan
    db.commit()
    
    logger.info(f"User {current_user.id} subscribed to {request.plan}")
    
    return {
        "subscription_id": subscription.id,
        "plan": subscription.plan,
        "price": subscription.price,
        "billing_cycle": subscription.billing_cycle,
        "status": subscription.status
    }

@router.post("/stripe/create-payment-intent")
async def create_stripe_payment_intent(
    request: SubscriptionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create Stripe payment intent"""
    
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Stripe not configured"
        )
    
    # Get plan price
    plans = {
        "starter": 2900,  # in cents
        "pro": 7900,
        "enterprise": 29900
    }
    
    if request.plan not in plans:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid plan"
        )
    
    amount = plans[request.plan]
    
    try:
        # Create payment intent
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency="usd",
            metadata={
                "user_id": current_user.id,
                "plan": request.plan,
                "billing_cycle": request.billing_cycle
            }
        )
        
        return {
            "client_secret": intent.client_secret,
            "payment_intent_id": intent.id
        }
    
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/stripe/webhook")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle Stripe webhooks"""
    
    if not settings.STRIPE_WEBHOOK_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook secret not configured"
        )
    
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET
        )
    
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payload"
        )
    
    except stripe.error.SignatureVerificationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid signature"
        )
    
    # Handle event
    if event["type"] == "payment_intent.succeeded":
        handle_payment_succeeded(event["data"]["object"], db)
    
    elif event["type"] == "payment_intent.payment_failed":
        handle_payment_failed(event["data"]["object"], db)
    
    elif event["type"] == "customer.subscription.updated":
        handle_subscription_updated(event["data"]["object"], db)
    
    elif event["type"] == "customer.subscription.deleted":
        handle_subscription_deleted(event["data"]["object"], db)
    
    return {"status": "received"}

@router.get("/invoices")
async def get_invoices(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user invoices"""
    
    invoices = db.query(Invoice).filter(
        Invoice.user_id == current_user.id
    ).order_by(Invoice.issue_date.desc()).all()
    
    return [
        {
            "id": inv.id,
            "invoice_number": inv.invoice_number,
            "amount": inv.amount,
            "currency": inv.currency,
            "status": inv.status,
            "issue_date": inv.issue_date,
            "due_date": inv.due_date,
            "paid_date": inv.paid_date
        }
        for inv in invoices
    ]

@router.get("/invoices/{invoice_id}")
async def get_invoice(
    invoice_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get invoice details"""
    
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.user_id == current_user.id
    ).first()
    
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    return {
        "id": invoice.id,
        "invoice_number": invoice.invoice_number,
        "amount": invoice.amount,
        "currency": invoice.currency,
        "status": invoice.status,
        "description": invoice.description,
        "items": invoice.items,
        "issue_date": invoice.issue_date,
        "due_date": invoice.due_date,
        "paid_date": invoice.paid_date
    }

@router.get("/subscription")
async def get_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current subscription"""
    
    subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.status == "active"
    ).first()
    
    if not subscription:
        return {
            "plan": "free",
            "status": "active"
        }
    
    return {
        "id": subscription.id,
        "plan": subscription.plan,
        "price": subscription.price,
        "currency": subscription.currency,
        "billing_cycle": subscription.billing_cycle,
        "status": subscription.status,
        "current_period_start": subscription.current_period_start,
        "current_period_end": subscription.current_period_end,
        "cancel_at": subscription.cancel_at
    }

# ==================== HELPER FUNCTIONS ====================

def handle_payment_succeeded(payment_intent: dict, db: Session):
    """Handle successful payment"""
    
    user_id = payment_intent["metadata"]["user_id"]
    plan = payment_intent["metadata"]["plan"]
    billing_cycle = payment_intent["metadata"]["billing_cycle"]
    
    # Create subscription
    subscription = Subscription(
        user_id=user_id,
        plan=plan,
        stripe_subscription_id=payment_intent["id"],
        price=payment_intent["amount"] / 100,
        currency=payment_intent["currency"],
        billing_cycle=billing_cycle,
        status="active",
        current_period_start=datetime.utcnow(),
        current_period_end=datetime.utcnow() + timedelta(days=365 if billing_cycle == "yearly" else 30)
    )
    
    db.add(subscription)
    
    # Create invoice
    invoice = Invoice(
        user_id=user_id,
        subscription_id=subscription.id,
        invoice_number=f"INV-{datetime.utcnow().timestamp()}",
        stripe_invoice_id=payment_intent["id"],
        amount=payment_intent["amount"] / 100,
        currency=payment_intent["currency"],
        status=PaymentStatus.COMPLETED,
        paid_date=datetime.utcnow()
    )
    
    db.add(invoice)
    db.commit()
    
    logger.info(f"Payment succeeded for user {user_id}")

def handle_payment_failed(payment_intent: dict, db: Session):
    """Handle failed payment"""
    
    logger.error(f"Payment failed: {payment_intent['id']}")

def handle_subscription_updated(subscription: dict, db: Session):
    """Handle subscription update"""
    
    logger.info(f"Subscription updated: {subscription['id']}")

def handle_subscription_deleted(subscription: dict, db: Session):
    """Handle subscription deletion"""
    
    logger.info(f"Subscription deleted: {subscription['id']}")
