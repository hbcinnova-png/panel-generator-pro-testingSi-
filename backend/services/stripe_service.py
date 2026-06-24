import stripe
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models import Subscription, Payment, User, Invoice
import os

logger = logging.getLogger(__name__)

# Configurar Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

class StripeService:
    """Servicio completo de integración con Stripe"""
    
    # Planes disponibles
    PLANS = {
        "basic": {
            "name": "Basic",
            "price": 29.99,
            "currency": "usd",
            "interval": "month",
            "stripe_product_id": None,
            "stripe_price_id": None,
            "features": ["5 paneles", "Instalación manual", "Email support"]
        },
        "pro": {
            "name": "Pro",
            "price": 79.99,
            "currency": "usd",
            "interval": "month",
            "stripe_product_id": None,
            "stripe_price_id": None,
            "features": ["50 paneles", "Instalación automática", "Priority support", "Analytics"]
        },
        "enterprise": {
            "name": "Enterprise",
            "price": 199.99,
            "currency": "usd",
            "interval": "month",
            "stripe_product_id": None,
            "stripe_price_id": None,
            "features": ["Paneles ilimitados", "Instalación automática", "24/7 support", "Custom integrations"]
        }
    }
    
    @staticmethod
    def create_stripe_product(plan_key: str) -> Dict[str, str]:
        """Crear producto en Stripe"""
        try:
            plan = StripeService.PLANS[plan_key]
            
            # Crear producto
            product = stripe.Product.create(
                name=plan["name"],
                description=f"Panel Generator Pro - {plan['name']} Plan",
                metadata={"plan_key": plan_key}
            )
            
            # Crear precio
            price = stripe.Price.create(
                product=product.id,
                unit_amount=int(plan["price"] * 100),  # Convertir a centavos
                currency=plan["currency"],
                recurring={
                    "interval": plan["interval"],
                    "interval_count": 1
                },
                metadata={"plan_key": plan_key}
            )
            
            logger.info(f"Stripe product created: {product.id} with price: {price.id}")
            
            return {
                "product_id": product.id,
                "price_id": price.id
            }
        
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating product: {e}")
            raise Exception(f"Error creating Stripe product: {str(e)}")
    
    @staticmethod
    def create_customer(user: User, db: Session) -> str:
        """Crear cliente en Stripe"""
        try:
            # Verificar si ya existe
            if user.stripe_customer_id:
                return user.stripe_customer_id
            
            # Crear cliente
            customer = stripe.Customer.create(
                email=user.email,
                name=user.username,
                metadata={"user_id": user.id}
            )
            
            # Guardar en BD
            user.stripe_customer_id = customer.id
            db.commit()
            
            logger.info(f"Stripe customer created: {customer.id}")
            
            return customer.id
        
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating customer: {e}")
            raise Exception(f"Error creating Stripe customer: {str(e)}")
    
    @staticmethod
    def create_subscription(
        user: User,
        plan: str,
        db: Session
    ) -> Dict[str, Any]:
        """Crear suscripción en Stripe"""
        try:
            # Verificar plan válido
            if plan not in StripeService.PLANS:
                raise ValueError(f"Invalid plan: {plan}")
            
            # Crear cliente si no existe
            customer_id = StripeService.create_customer(user, db)
            
            # Obtener price_id del plan
            plan_data = StripeService.PLANS[plan]
            
            # Crear suscripción
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[
                    {
                        "price": plan_data["stripe_price_id"]
                    }
                ],
                payment_behavior="default_incomplete",
                expand=["latest_invoice.payment_intent"],
                metadata={
                    "user_id": user.id,
                    "plan": plan
                }
            )
            
            # Guardar en BD
            db_subscription = Subscription(
                user_id=user.id,
                plan=plan,
                stripe_subscription_id=subscription.id,
                status=subscription.status,
                price=plan_data["price"],
                currency=plan_data["currency"],
                interval=plan_data["interval"],
                started_at=datetime.utcnow(),
                ends_at=datetime.utcnow() + timedelta(days=30)
            )
            
            db.add(db_subscription)
            db.commit()
            db.refresh(db_subscription)
            
            logger.info(f"Subscription created: {subscription.id}")
            
            return {
                "subscription_id": subscription.id,
                "client_secret": subscription.latest_invoice.payment_intent.client_secret,
                "status": subscription.status
            }
        
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating subscription: {e}")
            raise Exception(f"Error creating subscription: {str(e)}")
    
    @staticmethod
    def create_payment_intent(
        user: User,
        amount: float,
        currency: str = "usd",
        description: str = None,
        db: Session = None
    ) -> Dict[str, str]:
        """Crear payment intent en Stripe"""
        try:
            # Crear cliente si no existe
            customer_id = StripeService.create_customer(user, db)
            
            # Crear payment intent
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Convertir a centavos
                currency=currency,
                customer=customer_id,
                description=description or f"Payment from {user.email}",
                metadata={"user_id": user.id}
            )
            
            # Guardar en BD
            if db:
                payment = Payment(
                    user_id=user.id,
                    stripe_payment_id=intent.id,
                    amount=amount,
                    currency=currency,
                    status=intent.status,
                    description=description
                )
                db.add(payment)
                db.commit()
            
            logger.info(f"Payment intent created: {intent.id}")
            
            return {
                "client_secret": intent.client_secret,
                "payment_id": intent.id
            }
        
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating payment intent: {e}")
            raise Exception(f"Error creating payment intent: {str(e)}")
    
    @staticmethod
    def confirm_payment(payment_intent_id: str, db: Session) -> Dict[str, Any]:
        """Confirmar pago"""
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            if intent.status == "succeeded":
                # Actualizar pago en BD
                payment = db.query(Payment).filter(
                    Payment.stripe_payment_id == payment_intent_id
                ).first()
                
                if payment:
                    payment.status = "succeeded"
                    payment.paid_at = datetime.utcnow()
                    db.commit()
                
                logger.info(f"Payment confirmed: {payment_intent_id}")
                
                return {
                    "status": "succeeded",
                    "payment_id": intent.id,
                    "amount": intent.amount / 100
                }
            
            return {
                "status": intent.status,
                "payment_id": intent.id
            }
        
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error confirming payment: {e}")
            raise Exception(f"Error confirming payment: {str(e)}")
    
    @staticmethod
    def cancel_subscription(subscription_id: str, db: Session) -> Dict[str, Any]:
        """Cancelar suscripción"""
        try:
            subscription = stripe.Subscription.delete(subscription_id)
            
            # Actualizar en BD
            db_subscription = db.query(Subscription).filter(
                Subscription.stripe_subscription_id == subscription_id
            ).first()
            
            if db_subscription:
                db_subscription.status = "canceled"
                db_subscription.canceled_at = datetime.utcnow()
                db.commit()
            
            logger.info(f"Subscription canceled: {subscription_id}")
            
            return {
                "subscription_id": subscription.id,
                "status": subscription.status
            }
        
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error canceling subscription: {e}")
            raise Exception(f"Error canceling subscription: {str(e)}")
    
    @staticmethod
    def update_subscription(
        subscription_id: str,
        new_plan: str,
        db: Session
    ) -> Dict[str, Any]:
        """Actualizar plan de suscripción"""
        try:
            # Verificar plan válido
            if new_plan not in StripeService.PLANS:
                raise ValueError(f"Invalid plan: {new_plan}")
            
            # Obtener suscripción
            subscription = stripe.Subscription.retrieve(subscription_id)
            
            # Obtener price_id del nuevo plan
            plan_data = StripeService.PLANS[new_plan]
            
            # Actualizar suscripción
            updated_subscription = stripe.Subscription.modify(
                subscription_id,
                items=[
                    {
                        "id": subscription["items"]["data"][0].id,
                        "price": plan_data["stripe_price_id"]
                    }
                ]
            )
            
            # Actualizar en BD
            db_subscription = db.query(Subscription).filter(
                Subscription.stripe_subscription_id == subscription_id
            ).first()
            
            if db_subscription:
                db_subscription.plan = new_plan
                db_subscription.price = plan_data["price"]
                db.commit()
            
            logger.info(f"Subscription updated: {subscription_id}")
            
            return {
                "subscription_id": updated_subscription.id,
                "plan": new_plan,
                "status": updated_subscription.status
            }
        
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error updating subscription: {e}")
            raise Exception(f"Error updating subscription: {str(e)}")
    
    @staticmethod
    def get_subscription_status(subscription_id: str) -> Dict[str, Any]:
        """Obtener estado de suscripción"""
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            
            return {
                "subscription_id": subscription.id,
                "status": subscription.status,
                "plan": subscription.metadata.get("plan"),
                "current_period_start": subscription.current_period_start,
                "current_period_end": subscription.current_period_end,
                "cancel_at_period_end": subscription.cancel_at_period_end
            }
        
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error getting subscription: {e}")
            raise Exception(f"Error getting subscription: {str(e)}")
    
    @staticmethod
    def create_invoice(
        user: User,
        amount: float,
        description: str,
        db: Session
    ) -> Dict[str, str]:
        """Crear factura en Stripe"""
        try:
            # Crear cliente si no existe
            customer_id = StripeService.create_customer(user, db)
            
            # Crear factura
            invoice = stripe.Invoice.create(
                customer=customer_id,
                description=description,
                metadata={"user_id": user.id}
            )
            
            # Agregar línea de factura
            stripe.InvoiceItem.create(
                invoice=invoice.id,
                customer=customer_id,
                amount=int(amount * 100),
                currency="usd",
                description=description
            )
            
            # Finalizar factura
            finalized_invoice = stripe.Invoice.finalize_invoice(invoice.id)
            
            # Guardar en BD
            db_invoice = Invoice(
                user_id=user.id,
                stripe_invoice_id=finalized_invoice.id,
                amount=amount,
                description=description,
                status=finalized_invoice.status,
                invoice_number=finalized_invoice.number,
                created_at=datetime.utcnow()
            )
            
            db.add(db_invoice)
            db.commit()
            
            logger.info(f"Invoice created: {finalized_invoice.id}")
            
            return {
                "invoice_id": finalized_invoice.id,
                "invoice_number": finalized_invoice.number,
                "status": finalized_invoice.status,
                "pdf_url": finalized_invoice.invoice_pdf
            }
        
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating invoice: {e}")
            raise Exception(f"Error creating invoice: {str(e)}")
    
    @staticmethod
    def handle_webhook(event: Dict[str, Any], db: Session) -> bool:
        """Manejar webhooks de Stripe"""
        try:
            event_type = event["type"]
            
            if event_type == "payment_intent.succeeded":
                payment_intent = event["data"]["object"]
                
                # Actualizar pago
                payment = db.query(Payment).filter(
                    Payment.stripe_payment_id == payment_intent["id"]
                ).first()
                
                if payment:
                    payment.status = "succeeded"
                    payment.paid_at = datetime.utcnow()
                    db.commit()
                
                logger.info(f"Webhook: Payment succeeded {payment_intent['id']}")
            
            elif event_type == "payment_intent.payment_failed":
                payment_intent = event["data"]["object"]
                
                # Actualizar pago
                payment = db.query(Payment).filter(
                    Payment.stripe_payment_id == payment_intent["id"]
                ).first()
                
                if payment:
                    payment.status = "failed"
                    db.commit()
                
                logger.info(f"Webhook: Payment failed {payment_intent['id']}")
            
            elif event_type == "customer.subscription.created":
                subscription = event["data"]["object"]
                logger.info(f"Webhook: Subscription created {subscription['id']}")
            
            elif event_type == "customer.subscription.updated":
                subscription = event["data"]["object"]
                
                # Actualizar suscripción
                db_subscription = db.query(Subscription).filter(
                    Subscription.stripe_subscription_id == subscription["id"]
                ).first()
                
                if db_subscription:
                    db_subscription.status = subscription["status"]
                    db.commit()
                
                logger.info(f"Webhook: Subscription updated {subscription['id']}")
            
            elif event_type == "customer.subscription.deleted":
                subscription = event["data"]["object"]
                
                # Actualizar suscripción
                db_subscription = db.query(Subscription).filter(
                    Subscription.stripe_subscription_id == subscription["id"]
                ).first()
                
                if db_subscription:
                    db_subscription.status = "canceled"
                    db_subscription.canceled_at = datetime.utcnow()
                    db.commit()
                
                logger.info(f"Webhook: Subscription deleted {subscription['id']}")
            
            elif event_type == "invoice.paid":
                invoice = event["data"]["object"]
                
                # Actualizar factura
                db_invoice = db.query(Invoice).filter(
                    Invoice.stripe_invoice_id == invoice["id"]
                ).first()
                
                if db_invoice:
                    db_invoice.status = "paid"
                    db.commit()
                
                logger.info(f"Webhook: Invoice paid {invoice['id']}")
            
            return True
        
        except Exception as e:
            logger.error(f"Webhook error: {e}")
            return False
    
    @staticmethod
    def verify_webhook_signature(payload: bytes, signature: str) -> bool:
        """Verificar firma de webhook"""
        try:
            stripe.Webhook.construct_event(
                payload,
                signature,
                STRIPE_WEBHOOK_SECRET
            )
            return True
        except ValueError:
            logger.error("Invalid webhook payload")
            return False
        except stripe.error.SignatureVerificationError:
            logger.error("Invalid webhook signature")
            return False
