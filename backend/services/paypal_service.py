try:
    import paypalrestsdk
except Exception as paypal_import_error:
    class _DisabledPayPal:
        def configure(self, *args, **kwargs):
            return None
        def __getattr__(self, name):
            raise RuntimeError(f"PayPal SDK disabled: {paypal_import_error}")
    paypalrestsdk = _DisabledPayPal()
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models import Subscription, Payment, User, Invoice
import os

logger = logging.getLogger(__name__)

# Configurar PayPal
paypalrestsdk.configure({
    "mode": os.getenv("PAYPAL_MODE", "sandbox"),
    "client_id": os.getenv("PAYPAL_CLIENT_ID"),
    "client_secret": os.getenv("PAYPAL_CLIENT_SECRET")
})

class PayPalService:
    """Servicio completo de integración con PayPal"""
    
    PLANS = {
        "basic": {
            "name": "Basic",
            "price": 29.99,
            "currency": "USD",
            "interval": "MONTH",
            "frequency": 1,
            "cycles": 0,
            "features": ["5 paneles", "Instalación manual", "Email support"]
        },
        "pro": {
            "name": "Pro",
            "price": 79.99,
            "currency": "USD",
            "interval": "MONTH",
            "frequency": 1,
            "cycles": 0,
            "features": ["50 paneles", "Instalación automática", "Priority support", "Analytics"]
        },
        "enterprise": {
            "name": "Enterprise",
            "price": 199.99,
            "currency": "USD",
            "interval": "MONTH",
            "frequency": 1,
            "cycles": 0,
            "features": ["Paneles ilimitados", "Instalación automática", "24/7 support", "Custom integrations"]
        }
    }
    
    @staticmethod
    def create_plan(plan_key: str) -> Dict[str, str]:
        """Crear plan en PayPal"""
        try:
            plan_data = PayPalService.PLANS[plan_key]
            
            plan = paypalrestsdk.Plan({
                "name": plan_data["name"],
                "description": f"Panel Generator Pro - {plan_data['name']} Plan",
                "type": "REGULAR",
                "payment_definitions": [
                    {
                        "name": "Regular Payment Definition",
                        "type": "REGULAR",
                        "frequency": plan_data["interval"],
                        "frequency_interval": str(plan_data["frequency"]),
                        "amount": {
                            "value": str(plan_data["price"]),
                            "currency": plan_data["currency"]
                        },
                        "cycles": str(plan_data["cycles"]),
                        "charge_models": [
                            {
                                "type": "TAX",
                                "amount": {
                                    "value": "0",
                                    "currency": plan_data["currency"]
                                }
                            }
                        ]
                    }
                ],
                "merchant_preferences": {
                    "setup_fee": {
                        "value": "0",
                        "currency": plan_data["currency"]
                    },
                    "return_url": os.getenv("PAYPAL_RETURN_URL"),
                    "cancel_url": os.getenv("PAYPAL_CANCEL_URL"),
                    "notify_url": os.getenv("PAYPAL_NOTIFY_URL"),
                    "max_fail_attempts": "3",
                    "initial_fail_amount_action": "CANCEL"
                }
            })
            
            if plan.create():
                logger.info(f"PayPal plan created: {plan.id}")
                return {"plan_id": plan.id}
            else:
                logger.error(f"PayPal error: {plan.error}")
                raise Exception(f"Error creating PayPal plan: {plan.error}")
        
        except Exception as e:
            logger.error(f"PayPal error creating plan: {e}")
            raise Exception(f"Error creating PayPal plan: {str(e)}")
    
    @staticmethod
    def create_agreement(user: User, plan_id: str, db: Session) -> Dict[str, Any]:
        """Crear acuerdo de suscripción en PayPal"""
        try:
            agreement = paypalrestsdk.Agreement({
                "name": f"Subscription for {user.email}",
                "description": f"Panel Generator Pro Subscription",
                "start_date": (datetime.utcnow() + timedelta(minutes=5)).isoformat() + "Z",
                "agreement_type": "REGULAR",
                "payer": {
                    "payment_method": "paypal",
                    "payer_info": {
                        "email": user.email
                    }
                },
                "plan": {
                    "id": plan_id
                }
            })
            
            if agreement.create():
                # Guardar en BD
                db_subscription = Subscription(
                    user_id=user.id,
                    plan=plan_id,
                    stripe_subscription_id=agreement.id,
                    status="pending",
                    price=PayPalService.PLANS.get(plan_id, {}).get("price", 0),
                    currency="USD",
                    interval="MONTH",
                    started_at=datetime.utcnow(),
                    ends_at=datetime.utcnow() + timedelta(days=30)
                )
                db.add(db_subscription)
                db.commit()
                
                logger.info(f"PayPal agreement created: {agreement.id}")
                
                return {
                    "agreement_id": agreement.id,
                    "approval_url": agreement.links[1]["href"],
                    "status": "pending"
                }
            else:
                logger.error(f"PayPal error: {agreement.error}")
                raise Exception(f"Error creating agreement: {agreement.error}")
        
        except Exception as e:
            logger.error(f"PayPal error creating agreement: {e}")
            raise Exception(f"Error creating agreement: {str(e)}")
    
    @staticmethod
    def execute_agreement(token: str, db: Session) -> Dict[str, Any]:
        """Ejecutar acuerdo de suscripción"""
        try:
            agreement = paypalrestsdk.Agreement.find(token)
            
            if agreement.execute():
                # Actualizar en BD
                db_subscription = db.query(Subscription).filter(
                    Subscription.stripe_subscription_id == token
                ).first()
                
                if db_subscription:
                    db_subscription.status = "active"
                    db.commit()
                
                logger.info(f"PayPal agreement executed: {token}")
                
                return {
                    "agreement_id": agreement.id,
                    "status": "active"
                }
            else:
                logger.error(f"PayPal error: {agreement.error}")
                raise Exception(f"Error executing agreement: {agreement.error}")
        
        except Exception as e:
            logger.error(f"PayPal error executing agreement: {e}")
            raise Exception(f"Error executing agreement: {str(e)}")
    
    @staticmethod
    def create_payment(user: User, amount: float, description: str, db: Session) -> Dict[str, str]:
        """Crear pago único en PayPal"""
        try:
            payment = paypalrestsdk.Payment({
                "intent": "sale",
                "payer": {
                    "payment_method": "paypal"
                },
                "transactions": [
                    {
                        "amount": {
                            "total": str(amount),
                            "currency": "USD",
                            "details": {
                                "subtotal": str(amount)
                            }
                        },
                        "description": description,
                        "invoice_number": f"INV-{user.id}-{datetime.utcnow().timestamp()}",
                        "item_list": {
                            "items": [
                                {
                                    "name": description,
                                    "sku": f"SKU-{user.id}",
                                    "price": str(amount),
                                    "currency": "USD",
                                    "quantity": 1
                                }
                            ]
                        }
                    }
                ],
                "redirect_urls": {
                    "return_url": os.getenv("PAYPAL_RETURN_URL"),
                    "cancel_url": os.getenv("PAYPAL_CANCEL_URL")
                }
            })
            
            if payment.create():
                # Guardar en BD
                db_payment = Payment(
                    user_id=user.id,
                    stripe_payment_id=payment.id,
                    amount=amount,
                    currency="USD",
                    status="created",
                    description=description
                )
                db.add(db_payment)
                db.commit()
                
                logger.info(f"PayPal payment created: {payment.id}")
                
                return {
                    "payment_id": payment.id,
                    "approval_url": payment.links[1]["href"],
                    "status": "created"
                }
            else:
                logger.error(f"PayPal error: {payment.error}")
                raise Exception(f"Error creating payment: {payment.error}")
        
        except Exception as e:
            logger.error(f"PayPal error creating payment: {e}")
            raise Exception(f"Error creating payment: {str(e)}")
    
    @staticmethod
    def execute_payment(payment_id: str, payer_id: str, db: Session) -> Dict[str, Any]:
        """Ejecutar pago en PayPal"""
        try:
            payment = paypalrestsdk.Payment.find(payment_id)
            
            if payment.execute({"payer_id": payer_id}):
                # Actualizar en BD
                db_payment = db.query(Payment).filter(
                    Payment.stripe_payment_id == payment_id
                ).first()
                
                if db_payment:
                    db_payment.status = "completed"
                    db_payment.paid_at = datetime.utcnow()
                    db.commit()
                
                logger.info(f"PayPal payment executed: {payment_id}")
                
                return {
                    "payment_id": payment.id,
                    "status": "completed"
                }
            else:
                logger.error(f"PayPal error: {payment.error}")
                raise Exception(f"Error executing payment: {payment.error}")
        
        except Exception as e:
            logger.error(f"PayPal error executing payment: {e}")
            raise Exception(f"Error executing payment: {str(e)}")
    
    @staticmethod
    def cancel_agreement(agreement_id: str, db: Session) -> Dict[str, Any]:
        """Cancelar acuerdo de suscripción"""
        try:
            agreement = paypalrestsdk.Agreement.find(agreement_id)
            
            if agreement.suspend("Canceling subscription"):
                # Actualizar en BD
                db_subscription = db.query(Subscription).filter(
                    Subscription.stripe_subscription_id == agreement_id
                ).first()
                
                if db_subscription:
                    db_subscription.status = "canceled"
                    db_subscription.canceled_at = datetime.utcnow()
                    db.commit()
                
                logger.info(f"PayPal agreement canceled: {agreement_id}")
                
                return {
                    "agreement_id": agreement.id,
                    "status": "canceled"
                }
            else:
                logger.error(f"PayPal error: {agreement.error}")
                raise Exception(f"Error canceling agreement: {agreement.error}")
        
        except Exception as e:
            logger.error(f"PayPal error canceling agreement: {e}")
            raise Exception(f"Error canceling agreement: {str(e)}")
    
    @staticmethod
    def get_agreement_status(agreement_id: str) -> Dict[str, Any]:
        """Obtener estado de acuerdo"""
        try:
            agreement = paypalrestsdk.Agreement.find(agreement_id)
            
            return {
                "agreement_id": agreement.id,
                "status": agreement.state,
                "description": agreement.description
            }
        
        except Exception as e:
            logger.error(f"PayPal error getting agreement: {e}")
            raise Exception(f"Error getting agreement: {str(e)}")
