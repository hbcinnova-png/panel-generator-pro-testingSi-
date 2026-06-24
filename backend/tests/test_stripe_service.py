import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from services.stripe_service import StripeService
from models import User, Subscription, Payment, Invoice

@pytest.fixture
def mock_user():
    """Mock de usuario"""
    user = Mock(spec=User)
    user.id = "test-user-123"
    user.email = "test@example.com"
    user.username = "testuser"
    user.stripe_customer_id = None
    return user

@pytest.fixture
def mock_db():
    """Mock de base de datos"""
    db = Mock()
    return db

class TestStripeService:
    """Tests para StripeService"""
    
    @patch('services.stripe_service.stripe.Product.create')
    @patch('services.stripe_service.stripe.Price.create')
    def test_create_stripe_product(self, mock_price_create, mock_product_create):
        """Test crear producto en Stripe"""
        # Mock
        mock_product = Mock()
        mock_product.id = "prod_123"
        mock_product_create.return_value = mock_product
        
        mock_price = Mock()
        mock_price.id = "price_123"
        mock_price_create.return_value = mock_price
        
        # Ejecutar
        result = StripeService.create_stripe_product("basic")
        
        # Verificar
        assert result["product_id"] == "prod_123"
        assert result["price_id"] == "price_123"
        mock_product_create.assert_called_once()
        mock_price_create.assert_called_once()
    
    @patch('services.stripe_service.stripe.Customer.create')
    def test_create_customer(self, mock_customer_create, mock_user, mock_db):
        """Test crear cliente en Stripe"""
        # Mock
        mock_customer = Mock()
        mock_customer.id = "cus_123"
        mock_customer_create.return_value = mock_customer
        
        # Ejecutar
        result = StripeService.create_customer(mock_user, mock_db)
        
        # Verificar
        assert result == "cus_123"
        mock_customer_create.assert_called_once()
        mock_db.commit.assert_called_once()
    
    @patch('services.stripe_service.stripe.Subscription.create')
    @patch('services.stripe_service.StripeService.create_customer')
    def test_create_subscription(self, mock_create_customer, mock_sub_create, mock_user, mock_db):
        """Test crear suscripción"""
        # Mock
        mock_create_customer.return_value = "cus_123"
        
        mock_subscription = Mock()
        mock_subscription.id = "sub_123"
        mock_subscription.status = "active"
        mock_subscription.latest_invoice = Mock()
        mock_subscription.latest_invoice.payment_intent = Mock()
        mock_subscription.latest_invoice.payment_intent.client_secret = "secret_123"
        mock_sub_create.return_value = mock_subscription
        
        # Ejecutar
        result = StripeService.create_subscription("basic", mock_user, mock_db)
        
        # Verificar
        assert result["subscription_id"] == "sub_123"
        assert result["status"] == "active"
        assert result["client_secret"] == "secret_123"
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called()
    
    @patch('services.stripe_service.stripe.PaymentIntent.create')
    @patch('services.stripe_service.StripeService.create_customer')
    def test_create_payment_intent(self, mock_create_customer, mock_intent_create, mock_user, mock_db):
        """Test crear payment intent"""
        # Mock
        mock_create_customer.return_value = "cus_123"
        
        mock_intent = Mock()
        mock_intent.id = "pi_123"
        mock_intent.client_secret = "secret_123"
        mock_intent_create.return_value = mock_intent
        
        # Ejecutar
        result = StripeService.create_payment_intent(
            user=mock_user,
            amount=29.99,
            db=mock_db
        )
        
        # Verificar
        assert result["payment_id"] == "pi_123"
        assert result["client_secret"] == "secret_123"
        mock_intent_create.assert_called_once()
    
    @patch('services.stripe_service.stripe.PaymentIntent.retrieve')
    def test_confirm_payment(self, mock_retrieve, mock_db):
        """Test confirmar pago"""
        # Mock
        mock_intent = Mock()
        mock_intent.id = "pi_123"
        mock_intent.status = "succeeded"
        mock_intent.amount = 2999
        mock_retrieve.return_value = mock_intent
        
        mock_payment = Mock(spec=Payment)
        mock_db.query.return_value.filter.return_value.first.return_value = mock_payment
        
        # Ejecutar
        result = StripeService.confirm_payment("pi_123", mock_db)
        
        # Verificar
        assert result["status"] == "succeeded"
        assert result["payment_id"] == "pi_123"
        assert result["amount"] == 29.99
    
    @patch('services.stripe_service.stripe.Subscription.delete')
    def test_cancel_subscription(self, mock_delete, mock_db):
        """Test cancelar suscripción"""
        # Mock
        mock_subscription = Mock()
        mock_subscription.id = "sub_123"
        mock_subscription.status = "canceled"
        mock_delete.return_value = mock_subscription
        
        mock_db_sub = Mock(spec=Subscription)
        mock_db.query.return_value.filter.return_value.first.return_value = mock_db_sub
        
        # Ejecutar
        result = StripeService.cancel_subscription("sub_123", mock_db)
        
        # Verificar
        assert result["subscription_id"] == "sub_123"
        assert result["status"] == "canceled"
        mock_delete.assert_called_once_with("sub_123")
    
    @patch('services.stripe_service.stripe.Subscription.retrieve')
    @patch('services.stripe_service.stripe.Subscription.modify')
    def test_update_subscription(self, mock_modify, mock_retrieve, mock_db):
        """Test actualizar suscripción"""
        # Mock
        mock_sub = Mock()
        mock_sub.__getitem__ = Mock(side_effect=lambda x: Mock() if x == "items" else None)
        mock_sub["items"]["data"] = [Mock(id="si_123")]
        mock_retrieve.return_value = mock_sub
        
        mock_updated = Mock()
        mock_updated.id = "sub_123"
        mock_updated.status = "active"
        mock_modify.return_value = mock_updated
        
        mock_db_sub = Mock(spec=Subscription)
        mock_db.query.return_value.filter.return_value.first.return_value = mock_db_sub
        
        # Ejecutar
        result = StripeService.update_subscription("sub_123", "pro", mock_db)
        
        # Verificar
        assert result["subscription_id"] == "sub_123"
        assert result["plan"] == "pro"
        assert result["status"] == "active"
    
    @patch('services.stripe_service.stripe.Subscription.retrieve')
    def test_get_subscription_status(self, mock_retrieve):
        """Test obtener estado de suscripción"""
        # Mock
        mock_subscription = Mock()
        mock_subscription.id = "sub_123"
        mock_subscription.status = "active"
        mock_subscription.metadata = {"plan": "pro"}
        mock_subscription.current_period_start = 1234567890
        mock_subscription.current_period_end = 1234654290
        mock_subscription.cancel_at_period_end = False
        mock_retrieve.return_value = mock_subscription
        
        # Ejecutar
        result = StripeService.get_subscription_status("sub_123")
        
        # Verificar
        assert result["subscription_id"] == "sub_123"
        assert result["status"] == "active"
        assert result["plan"] == "pro"
    
    @patch('services.stripe_service.stripe.Invoice.create')
    @patch('services.stripe_service.stripe.InvoiceItem.create')
    @patch('services.stripe_service.stripe.Invoice.finalize_invoice')
    @patch('services.stripe_service.StripeService.create_customer')
    def test_create_invoice(self, mock_create_customer, mock_finalize, mock_item_create, mock_invoice_create, mock_user, mock_db):
        """Test crear factura"""
        # Mock
        mock_create_customer.return_value = "cus_123"
        
        mock_invoice = Mock()
        mock_invoice.id = "in_123"
        mock_invoice_create.return_value = mock_invoice
        
        mock_finalized = Mock()
        mock_finalized.id = "in_123"
        mock_finalized.number = "INV-001"
        mock_finalized.status = "open"
        mock_finalized.invoice_pdf = "https://example.com/invoice.pdf"
        mock_finalize.return_value = mock_finalized
        
        # Ejecutar
        result = StripeService.create_invoice(
            user=mock_user,
            amount=29.99,
            description="Test invoice",
            db=mock_db
        )
        
        # Verificar
        assert result["invoice_id"] == "in_123"
        assert result["invoice_number"] == "INV-001"
        assert result["status"] == "open"
    
    def test_handle_webhook_payment_succeeded(self, mock_db):
        """Test manejar webhook de pago exitoso"""
        # Mock
        event = {
            "type": "payment_intent.succeeded",
            "data": {
                "object": {
                    "id": "pi_123"
                }
            }
        }
        
        mock_payment = Mock(spec=Payment)
        mock_db.query.return_value.filter.return_value.first.return_value = mock_payment
        
        # Ejecutar
        result = StripeService.handle_webhook(event, mock_db)
        
        # Verificar
        assert result is True
        assert mock_payment.status == "succeeded"
    
    def test_handle_webhook_subscription_created(self, mock_db):
        """Test manejar webhook de suscripción creada"""
        # Mock
        event = {
            "type": "customer.subscription.created",
            "data": {
                "object": {
                    "id": "sub_123"
                }
            }
        }
        
        # Ejecutar
        result = StripeService.handle_webhook(event, mock_db)
        
        # Verificar
        assert result is True
    
    def test_handle_webhook_subscription_updated(self, mock_db):
        """Test manejar webhook de suscripción actualizada"""
        # Mock
        event = {
            "type": "customer.subscription.updated",
            "data": {
                "object": {
                    "id": "sub_123",
                    "status": "active"
                }
            }
        }
        
        mock_subscription = Mock(spec=Subscription)
        mock_db.query.return_value.filter.return_value.first.return_value = mock_subscription
        
        # Ejecutar
        result = StripeService.handle_webhook(event, mock_db)
        
        # Verificar
        assert result is True
        assert mock_subscription.status == "active"
    
    @patch('services.stripe_service.stripe.Webhook.construct_event')
    def test_verify_webhook_signature_valid(self, mock_construct):
        """Test verificar firma válida"""
        # Mock
        mock_construct.return_value = {"type": "test"}
        
        # Ejecutar
        result = StripeService.verify_webhook_signature(b"payload", "signature")
        
        # Verificar
        assert result is True
    
    @patch('services.stripe_service.stripe.Webhook.construct_event')
    def test_verify_webhook_signature_invalid(self, mock_construct):
        """Test verificar firma inválida"""
        # Mock
        import stripe
        mock_construct.side_effect = stripe.error.SignatureVerificationError("Invalid", "sig")
        
        # Ejecutar
        result = StripeService.verify_webhook_signature(b"payload", "invalid_sig")
        
        # Verificar
        assert result is False
