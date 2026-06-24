import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from services.paypal_service import PayPalService
from services.twilio_service import TwilioService
from services.sendgrid_service import SendGridService
from models import User, Subscription, Payment, Notification

@pytest.fixture
def mock_user():
    user = Mock(spec=User)
    user.id = "test-user-123"
    user.email = "test@example.com"
    user.username = "testuser"
    return user

@pytest.fixture
def mock_db():
    db = Mock()
    return db

class TestPayPalService:
    """Tests para PayPalService"""
    
    @patch('services.paypal_service.paypalrestsdk.Plan')
    def test_create_plan(self, mock_plan_class):
        """Test crear plan en PayPal"""
        mock_plan = Mock()
        mock_plan.id = "plan_123"
        mock_plan.create.return_value = True
        mock_plan_class.return_value = mock_plan
        
        result = PayPalService.create_plan("basic")
        
        assert result["plan_id"] == "plan_123"
        mock_plan.create.assert_called_once()
    
    @patch('services.paypal_service.paypalrestsdk.Agreement')
    @patch('services.paypal_service.PayPalService.create_customer')
    def test_create_agreement(self, mock_create_customer, mock_agreement_class, mock_user, mock_db):
        """Test crear acuerdo de suscripción"""
        mock_agreement = Mock()
        mock_agreement.id = "agreement_123"
        mock_agreement.create.return_value = True
        mock_agreement.links = [None, {"href": "https://approval.url"}]
        mock_agreement_class.return_value = mock_agreement
        
        result = PayPalService.create_agreement(mock_user, "plan_123", mock_db)
        
        assert result["agreement_id"] == "agreement_123"
        assert "approval_url" in result
        mock_db.add.assert_called_once()
    
    @patch('services.paypal_service.paypalrestsdk.Agreement')
    def test_execute_agreement(self, mock_agreement_class, mock_db):
        """Test ejecutar acuerdo"""
        mock_agreement = Mock()
        mock_agreement.id = "agreement_123"
        mock_agreement.execute.return_value = True
        mock_agreement_class.find.return_value = mock_agreement
        
        mock_db_sub = Mock(spec=Subscription)
        mock_db.query.return_value.filter.return_value.first.return_value = mock_db_sub
        
        result = PayPalService.execute_agreement("token_123", mock_db)
        
        assert result["agreement_id"] == "agreement_123"
        assert result["status"] == "active"
    
    @patch('services.paypal_service.paypalrestsdk.Payment')
    def test_create_payment(self, mock_payment_class, mock_user, mock_db):
        """Test crear pago único"""
        mock_payment = Mock()
        mock_payment.id = "payment_123"
        mock_payment.create.return_value = True
        mock_payment.links = [None, {"href": "https://approval.url"}]
        mock_payment_class.return_value = mock_payment
        
        result = PayPalService.create_payment(mock_user, 29.99, "Test payment", mock_db)
        
        assert result["payment_id"] == "payment_123"
        assert "approval_url" in result
        mock_db.add.assert_called_once()
    
    @patch('services.paypal_service.paypalrestsdk.Payment')
    def test_execute_payment(self, mock_payment_class, mock_db):
        """Test ejecutar pago"""
        mock_payment = Mock()
        mock_payment.id = "payment_123"
        mock_payment.execute.return_value = True
        mock_payment_class.find.return_value = mock_payment
        
        mock_db_payment = Mock(spec=Payment)
        mock_db.query.return_value.filter.return_value.first.return_value = mock_db_payment
        
        result = PayPalService.execute_payment("payment_123", "payer_123", mock_db)
        
        assert result["payment_id"] == "payment_123"
        assert result["status"] == "completed"

class TestTwilioService:
    """Tests para TwilioService"""
    
    @patch('services.twilio_service.client.messages.create')
    def test_send_sms(self, mock_create, mock_db):
        """Test enviar SMS"""
        mock_message = Mock()
        mock_message.sid = "msg_123"
        mock_message.status = "sent"
        mock_create.return_value = mock_message
        
        result = TwilioService.send_sms("+1234567890", "Test message", "user_123", mock_db)
        
        assert result["message_id"] == "msg_123"
        assert result["status"] == "sent"
        mock_db.add.assert_called_once()
    
    @patch('services.twilio_service.client.messages.create')
    def test_send_whatsapp(self, mock_create, mock_db):
        """Test enviar WhatsApp"""
        mock_message = Mock()
        mock_message.sid = "msg_123"
        mock_message.status = "sent"
        mock_create.return_value = mock_message
        
        result = TwilioService.send_whatsapp("+1234567890", "Test message", "user_123", mock_db)
        
        assert result["message_id"] == "msg_123"
        assert result["status"] == "sent"
        mock_db.add.assert_called_once()
    
    @patch('services.twilio_service.client.messages.create')
    def test_send_bulk_sms(self, mock_create, mock_db):
        """Test enviar SMS en lote"""
        mock_message = Mock()
        mock_message.sid = "msg_123"
        mock_create.return_value = mock_message
        
        result = TwilioService.send_bulk_sms(
            ["+1234567890", "+0987654321"],
            "Test message",
            "user_123",
            mock_db
        )
        
        assert result["total"] == 2
        assert result["sent"] == 2
        assert len(result["results"]) == 2
    
    @patch('services.twilio_service.client.messages.create')
    def test_send_bulk_whatsapp(self, mock_create, mock_db):
        """Test enviar WhatsApp en lote"""
        mock_message = Mock()
        mock_message.sid = "msg_123"
        mock_create.return_value = mock_message
        
        result = TwilioService.send_bulk_whatsapp(
            ["+1234567890", "+0987654321"],
            "Test message",
            "user_123",
            mock_db
        )
        
        assert result["total"] == 2
        assert result["sent"] == 2

class TestSendGridService:
    """Tests para SendGridService"""
    
    @patch('services.sendgrid_service.sg.send')
    def test_send_email(self, mock_send, mock_db):
        """Test enviar email"""
        mock_response = Mock()
        mock_response.status_code = 202
        mock_response.headers = {"X-Message-Id": "msg_123"}
        mock_send.return_value = mock_response
        
        result = SendGridService.send_email(
            "test@example.com",
            "Test Subject",
            "<html>Test</html>",
            user_id="user_123",
            db=mock_db
        )
        
        assert result["status"] == "sent"
        assert result["email"] == "test@example.com"
        mock_db.add.assert_called_once()
    
    @patch('services.sendgrid_service.sg.send')
    def test_send_bulk_email(self, mock_send, mock_db):
        """Test enviar email en lote"""
        mock_response = Mock()
        mock_response.status_code = 202
        mock_response.headers = {"X-Message-Id": "msg_123"}
        mock_send.return_value = mock_response
        
        recipients = [
            {"email": "test1@example.com", "name": "User 1"},
            {"email": "test2@example.com", "name": "User 2"}
        ]
        
        result = SendGridService.send_bulk_email(
            recipients,
            "Test Subject",
            "<html>Test</html>",
            user_id="user_123",
            db=mock_db
        )
        
        assert result["status"] == "sent"
        assert result["recipients"] == 2
    
    @patch('services.sendgrid_service.sg.send')
    def test_send_template_email(self, mock_send, mock_db):
        """Test enviar email con template"""
        mock_response = Mock()
        mock_response.status_code = 202
        mock_response.headers = {"X-Message-Id": "msg_123"}
        mock_send.return_value = mock_response
        
        result = SendGridService.send_template_email(
            "test@example.com",
            "template_123",
            {"name": "Test User"},
            user_id="user_123",
            db=mock_db
        )
        
        assert result["status"] == "sent"
        assert result["template_id"] == "template_123"
    
    @patch('services.sendgrid_service.sg.send')
    def test_send_password_reset_email(self, mock_send, mock_db):
        """Test enviar email de reseteo"""
        mock_response = Mock()
        mock_response.status_code = 202
        mock_response.headers = {"X-Message-Id": "msg_123"}
        mock_send.return_value = mock_response
        
        result = SendGridService.send_password_reset_email(
            "test@example.com",
            "https://reset.link",
            "Test User",
            user_id="user_123",
            db=mock_db
        )
        
        assert result["status"] == "sent"
    
    @patch('services.sendgrid_service.sg.send')
    def test_send_welcome_email(self, mock_send, mock_db):
        """Test enviar email de bienvenida"""
        mock_response = Mock()
        mock_response.status_code = 202
        mock_response.headers = {"X-Message-Id": "msg_123"}
        mock_send.return_value = mock_response
        
        result = SendGridService.send_welcome_email(
            "test@example.com",
            "Test User",
            user_id="user_123",
            db=mock_db
        )
        
        assert result["status"] == "sent"
    
    @patch('services.sendgrid_service.sg.send')
    def test_send_invoice_email(self, mock_send, mock_db):
        """Test enviar email de factura"""
        mock_response = Mock()
        mock_response.status_code = 202
        mock_response.headers = {"X-Message-Id": "msg_123"}
        mock_send.return_value = mock_response
        
        result = SendGridService.send_invoice_email(
            "test@example.com",
            "INV-001",
            79.99,
            "https://invoice.url",
            user_id="user_123",
            db=mock_db
        )
        
        assert result["status"] == "sent"
