from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, JSON, ForeignKey, Enum, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

Base = declarative_base()

# ==================== ENUMS ====================

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"
    CUSTOMER = "customer"

class SubscriptionPlan(str, enum.Enum):
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class PanelStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class InstallationStatus(str, enum.Enum):
    PENDING = "pending"
    INSTALLING = "installing"
    INSTALLED = "installed"
    FAILED = "failed"

class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

# ==================== MODELS ====================

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    company = Column(String(255))
    phone = Column(String(20))
    avatar_url = Column(String(500))
    
    # Account settings
    role = Column(Enum(UserRole), default=UserRole.USER)
    subscription_plan = Column(Enum(SubscriptionPlan), default=SubscriptionPlan.FREE)
    credits = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # 2FA
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String(255))
    
    # OAuth
    google_id = Column(String(255))
    facebook_id = Column(String(255))
    github_id = Column(String(255))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    panels = relationship("Panel", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    invoices = relationship("Invoice", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    webhooks = relationship("Webhook", back_populates="user", cascade="all, delete-orphan")

class Panel(Base):
    __tablename__ = "panels"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    # Basic info
    name = Column(String(255), nullable=False)
    business_name = Column(String(255), nullable=False)
    description = Column(Text)
    logo_url = Column(String(500))
    
    # Design
    theme = Column(String(100), default="doctor_piscinas")
    color_primary = Column(String(7), default="#ff006e")
    color_secondary = Column(String(7), default="#00d9ff")
    effects = Column(JSON, default=["particles", "parallax", "glow", "water"])
    
    # Content
    services = Column(JSON, default=[])
    integrations = Column(JSON, default=[])
    phone = Column(String(20))
    email = Column(String(255))
    website = Column(String(500))
    whatsapp = Column(String(20))
    social = Column(JSON, default={})
    
    # Status
    status = Column(Enum(PanelStatus), default=PanelStatus.DRAFT)
    installation_status = Column(Enum(InstallationStatus), default=InstallationStatus.PENDING)
    installation_method = Column(String(50))  # zip, ftp, api, oauth
    
    # Installation details
    wordpress_url = Column(String(500))
    wordpress_user = Column(String(255))
    plugin_version = Column(String(20), default="1.0.0")
    
    # Statistics
    views = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="panels")
    installation_logs = relationship("InstallationLog", back_populates="panel", cascade="all, delete-orphan")

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    plan = Column(Enum(SubscriptionPlan), nullable=False)
    stripe_subscription_id = Column(String(255), unique=True)
    paypal_subscription_id = Column(String(255), unique=True)
    
    price = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    billing_cycle = Column(String(50), default="monthly")  # monthly, yearly
    
    status = Column(String(50), default="active")
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    cancel_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")
    invoices = relationship("Invoice", back_populates="subscription", cascade="all, delete-orphan")

class Invoice(Base):
    __tablename__ = "invoices"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    subscription_id = Column(String(36), ForeignKey("subscriptions.id"))
    
    invoice_number = Column(String(50), unique=True, nullable=False)
    stripe_invoice_id = Column(String(255), unique=True)
    paypal_invoice_id = Column(String(255), unique=True)
    
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    
    description = Column(Text)
    items = Column(JSON)
    
    issue_date = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime)
    paid_date = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="invoices")
    subscription = relationship("Subscription", back_populates="invoices")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), index=True)
    
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String(36))
    
    changes = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50))  # email, sms, push, webhook
    
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="notifications")

class Webhook(Base):
    __tablename__ = "webhooks"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    url = Column(String(500), nullable=False)
    event_type = Column(String(100), nullable=False)  # panel.created, panel.updated, etc.
    is_active = Column(Boolean, default=True)
    
    secret = Column(String(255), nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="webhooks")

class InstallationLog(Base):
    __tablename__ = "installation_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    panel_id = Column(String(36), ForeignKey("panels.id"), nullable=False, index=True)
    
    method = Column(String(50))  # zip, ftp, api, oauth
    status = Column(Enum(InstallationStatus), default=InstallationStatus.PENDING)
    
    log_message = Column(Text)
    error_message = Column(Text)
    
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    panel = relationship("Panel", back_populates="installation_logs")
