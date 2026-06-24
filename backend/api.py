#!/usr/bin/env python3
"""
Panel Generator System - Professional Backend API
Sistema completo de generación de paneles WordPress con todas las características
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, UploadFile, File
from fastapi.security import OAuth2PasswordBearer, HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, validator
from sqlalchemy import create_engine, Column, String, Integer, DateTime, JSON, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, timedelta
import jwt
import bcrypt
import json
import uuid
import os
from typing import Optional, List, Dict, Any
import aiohttp
import stripe
try:
    from paypalrestsdk import Api
except Exception as paypal_import_error:
    class Api:
        def __init__(self, *args, **kwargs):
            self.disabled = True
            self.error = str(paypal_import_error)
import logging

# Configuración
app = FastAPI(title="Panel Generator API", version="2.0.0")
logger = logging.getLogger(__name__)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/panel_generator")
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
security = HTTPBearer()

# Stripe & PayPal
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
paypal_api = Api({
    'mode': os.getenv("PAYPAL_MODE", "sandbox"),
    'client_id': os.getenv("PAYPAL_CLIENT_ID", ""),
    'client_secret': os.getenv("PAYPAL_CLIENT_SECRET", "")
})

# ==================== DATABASE MODELS ====================

class User(Base):
    """Modelo de usuario con roles y permisos"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    company = Column(String)
    phone = Column(String)
    avatar_url = Column(String)
    role = Column(String, default="user")  # user, premium, admin
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String, nullable=True)
    oauth_providers = Column(JSON, default={})  # Google, Facebook, etc
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    subscription_plan = Column(String, default="free")  # free, starter, pro, enterprise
    subscription_expires = Column(DateTime, nullable=True)
    credits = Column(Float, default=0)
    api_key = Column(String, unique=True, index=True)
    settings = Column(JSON, default={})

class Panel(Base):
    """Modelo de panel generado"""
    __tablename__ = "panels"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True)
    name = Column(String)
    description = Column(String)
    business_name = Column(String)
    business_phone = Column(String)
    business_email = Column(String)
    business_website = Column(String)
    logo_url = Column(String, nullable=True)
    theme = Column(String, default="doctor_piscinas")
    colors = Column(JSON, default={})
    services = Column(JSON, default=[])
    social_links = Column(JSON, default={})
    integrations = Column(JSON, default={})
    settings = Column(JSON, default={})
    status = Column(String, default="draft")  # draft, published, archived
    version = Column(Integer, default=1)
    plugin_url = Column(String, nullable=True)
    installation_method = Column(String, default="zip")  # zip, ftp, api, oauth
    wordpress_url = Column(String, nullable=True)
    wordpress_credentials = Column(JSON, nullable=True)  # Encriptado
    installation_status = Column(String, default="pending")  # pending, installing, installed, failed
    installation_error = Column(String, nullable=True)
    shortcode = Column(String, default="[premium-panel]")
    page_id = Column(String, nullable=True)
    analytics = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)

class Subscription(Base):
    """Modelo de suscripción"""
    __tablename__ = "subscriptions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True)
    plan = Column(String)  # starter, pro, enterprise
    status = Column(String, default="active")
    stripe_subscription_id = Column(String, nullable=True)
    paypal_subscription_id = Column(String, nullable=True)
    billing_cycle = Column(String, default="monthly")  # monthly, yearly
    amount = Column(Float)
    currency = Column(String, default="USD")
    next_billing_date = Column(DateTime)
    auto_renew = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Invoice(Base):
    """Modelo de factura"""
    __tablename__ = "invoices"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True)
    subscription_id = Column(String, nullable=True)
    amount = Column(Float)
    currency = Column(String, default="USD")
    status = Column(String, default="pending")  # pending, paid, failed, cancelled
    invoice_number = Column(String, unique=True)
    stripe_invoice_id = Column(String, nullable=True)
    paypal_invoice_id = Column(String, nullable=True)
    pdf_url = Column(String, nullable=True)
    due_date = Column(DateTime)
    paid_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    """Modelo de auditoría"""
    __tablename__ = "audit_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True)
    panel_id = Column(String, nullable=True, index=True)
    action = Column(String)  # create, update, delete, install, publish
    resource_type = Column(String)  # panel, user, subscription
    resource_id = Column(String)
    changes = Column(JSON)
    ip_address = Column(String)
    user_agent = Column(String)
    status = Column(String, default="success")  # success, error
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

class Notification(Base):
    """Modelo de notificación"""
    __tablename__ = "notifications"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True)
    type = Column(String)  # email, sms, push, webhook
    subject = Column(String)
    message = Column(String)
    data = Column(JSON, default={})
    status = Column(String, default="pending")  # pending, sent, failed
    sent_at = Column(DateTime, nullable=True)
    error = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Webhook(Base):
    """Modelo de webhook"""
    __tablename__ = "webhooks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True)
    url = Column(String)
    events = Column(JSON)  # panel.created, panel.published, etc
    secret = Column(String)
    is_active = Column(Boolean, default=True)
    retry_count = Column(Integer, default=3)
    created_at = Column(DateTime, default=datetime.utcnow)

# ==================== SCHEMAS ====================

class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: str
    company: str
    phone: str
    
    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v

class UserLogin(BaseModel):
    email: str
    password: str
    two_factor_code: Optional[str] = None

class PanelCreate(BaseModel):
    name: str
    description: str
    business_name: str
    business_phone: str
    business_email: EmailStr
    business_website: Optional[str] = None
    logo_url: Optional[str] = None
    theme: str = "doctor_piscinas"
    colors: Dict[str, str] = {}
    services: List[Dict[str, Any]] = []
    social_links: Dict[str, str] = {}
    integrations: Dict[str, Dict[str, str]] = {}

class PanelUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    theme: Optional[str] = None
    colors: Optional[Dict[str, str]] = None
    services: Optional[List[Dict[str, Any]]] = None
    social_links: Optional[Dict[str, str]] = None
    integrations: Optional[Dict[str, Dict[str, str]]] = None

class InstallationConfig(BaseModel):
    method: str  # zip, ftp, api, oauth
    wordpress_url: Optional[str] = None
    ftp_host: Optional[str] = None
    ftp_user: Optional[str] = None
    ftp_password: Optional[str] = None
    wordpress_user: Optional[str] = None
    wordpress_password: Optional[str] = None

class WebhookCreate(BaseModel):
    url: str
    events: List[str]

# ==================== UTILITY FUNCTIONS ====================

def hash_password(password: str) -> str:
    """Hash contraseña"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    """Verificar contraseña"""
    return bcrypt.checkpw(password.encode(), hashed.encode())

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crear JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(SessionLocal)):
    """Obtener usuario actual"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def get_db():
    """Obtener sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==================== ENDPOINTS ====================

# Auth Endpoints
@app.post("/api/v1/auth/register")
async def register(user: UserRegister, db: Session = Depends(get_db)):
    """Registrar nuevo usuario"""
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    
    new_user = User(
        id=str(uuid.uuid4()),
        email=user.email,
        username=user.username,
        hashed_password=hash_password(user.password),
        full_name=user.full_name,
        company=user.company,
        phone=user.phone,
        api_key=str(uuid.uuid4())
    )
    db.add(new_user)
    db.commit()
    
    return {
        "id": new_user.id,
        "email": new_user.email,
        "username": new_user.username,
        "message": "User registered successfully"
    }

@app.post("/api/v1/auth/login")
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login usuario"""
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if user.two_factor_enabled:
        # Verificar 2FA
        if not credentials.two_factor_code:
            raise HTTPException(status_code=403, detail="2FA required")
    
    user.last_login = datetime.utcnow()
    db.commit()
    
    access_token = create_access_token(data={"sub": user.id})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "role": user.role
        }
    }

# Panel Endpoints
@app.post("/api/v1/panels")
async def create_panel(
    panel: PanelCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Crear nuevo panel"""
    new_panel = Panel(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        name=panel.name,
        description=panel.description,
        business_name=panel.business_name,
        business_phone=panel.business_phone,
        business_email=panel.business_email,
        business_website=panel.business_website,
        logo_url=panel.logo_url,
        theme=panel.theme,
        colors=panel.colors,
        services=panel.services,
        social_links=panel.social_links,
        integrations=panel.integrations
    )
    db.add(new_panel)
    db.commit()
    
    # Auditoría
    audit = AuditLog(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        panel_id=new_panel.id,
        action="create",
        resource_type="panel",
        resource_id=new_panel.id,
        changes=panel.dict()
    )
    db.add(audit)
    db.commit()
    
    # Generar plugin en background
    background_tasks.add_task(generate_plugin, new_panel.id, current_user.id)
    
    return {
        "id": new_panel.id,
        "name": new_panel.name,
        "status": new_panel.status,
        "created_at": new_panel.created_at
    }

@app.get("/api/v1/panels/{panel_id}")
async def get_panel(
    panel_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener panel específico"""
    panel = db.query(Panel).filter(
        Panel.id == panel_id,
        Panel.user_id == current_user.id
    ).first()
    
    if not panel:
        raise HTTPException(status_code=404, detail="Panel not found")
    
    return panel

@app.get("/api/v1/panels")
async def list_panels(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10
):
    """Listar paneles del usuario"""
    panels = db.query(Panel).filter(
        Panel.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return panels

@app.put("/api/v1/panels/{panel_id}")
async def update_panel(
    panel_id: str,
    panel_update: PanelUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualizar panel"""
    panel = db.query(Panel).filter(
        Panel.id == panel_id,
        Panel.user_id == current_user.id
    ).first()
    
    if not panel:
        raise HTTPException(status_code=404, detail="Panel not found")
    
    update_data = panel_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(panel, field, value)
    
    panel.updated_at = datetime.utcnow()
    panel.version += 1
    db.commit()
    
    return panel

@app.delete("/api/v1/panels/{panel_id}")
async def delete_panel(
    panel_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Eliminar panel"""
    panel = db.query(Panel).filter(
        Panel.id == panel_id,
        Panel.user_id == current_user.id
    ).first()
    
    if not panel:
        raise HTTPException(status_code=404, detail="Panel not found")
    
    db.delete(panel)
    db.commit()
    
    return {"message": "Panel deleted"}

# Installation Endpoints
@app.post("/api/v1/panels/{panel_id}/install")
async def install_panel(
    panel_id: str,
    config: InstallationConfig,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Instalar panel en WordPress"""
    panel = db.query(Panel).filter(
        Panel.id == panel_id,
        Panel.user_id == current_user.id
    ).first()
    
    if not panel:
        raise HTTPException(status_code=404, detail="Panel not found")
    
    panel.installation_method = config.method
    panel.wordpress_url = config.wordpress_url
    panel.installation_status = "installing"
    db.commit()
    
    # Instalar en background
    background_tasks.add_task(
        install_wordpress_plugin,
        panel.id,
        config.dict()
    )
    
    return {"status": "installing", "panel_id": panel.id}

@app.get("/api/v1/panels/{panel_id}/install-status")
async def get_install_status(
    panel_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener estado de instalación"""
    panel = db.query(Panel).filter(
        Panel.id == panel_id,
        Panel.user_id == current_user.id
    ).first()
    
    if not panel:
        raise HTTPException(status_code=404, detail="Panel not found")
    
    return {
        "status": panel.installation_status,
        "error": panel.installation_error,
        "plugin_url": panel.plugin_url
    }

# Subscription Endpoints
@app.post("/api/v1/subscriptions")
async def create_subscription(
    plan: str,
    billing_cycle: str = "monthly",
    payment_method: str = "stripe",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crear suscripción"""
    plans = {
        "starter": {"monthly": 29, "yearly": 290},
        "pro": {"monthly": 99, "yearly": 990},
        "enterprise": {"monthly": 299, "yearly": 2990}
    }
    
    if plan not in plans:
        raise HTTPException(status_code=400, detail="Invalid plan")
    
    amount = plans[plan][billing_cycle]
    
    if payment_method == "stripe":
        # Crear sesión Stripe
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": f"{plan.capitalize()} Plan"},
                    "unit_amount": int(amount * 100),
                },
                "quantity": 1,
            }],
            mode="subscription",
            success_url="https://yourdomain.com/success",
            cancel_url="https://yourdomain.com/cancel",
        )
        return {"checkout_url": session.url}
    
    return {"message": "Subscription created"}

# Webhook Endpoints
@app.post("/api/v1/webhooks")
async def create_webhook(
    webhook: WebhookCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crear webhook"""
    new_webhook = Webhook(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        url=webhook.url,
        events=webhook.events,
        secret=str(uuid.uuid4())
    )
    db.add(new_webhook)
    db.commit()
    
    return {"id": new_webhook.id, "secret": new_webhook.secret}

# ==================== BACKGROUND TASKS ====================

async def generate_plugin(panel_id: str, user_id: str):
    """Generar plugin en background"""
    try:
        db = SessionLocal()
        panel = db.query(Panel).filter(
            Panel.id == panel_id,
            Panel.user_id == user_id
        ).first()
        
        if not panel:
            logger.error(f"Panel {panel_id} not found")
            return {"status": "error", "message": "Panel not found"}
        
        # Import installation service
        from services.installation_service import InstallationService
        
        # Generate plugin ZIP
        plugin_zip = InstallationService.generate_plugin_zip(panel, db)
        
        # Save to file
        zip_path = f"/tmp/panel-{panel_id}.zip"
        with open(zip_path, 'wb') as f:
            f.write(plugin_zip)
        
        # Update panel status
        panel.installation_status = "generated"
        panel.installation_method = "zip"
        db.commit()
        
        logger.info(f"Plugin generated for panel {panel_id}: {zip_path}")
        return {"status": "success", "path": zip_path}
    
    except Exception as e:
        logger.error(f"Error generating plugin: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        db.close()

async def install_wordpress_plugin(panel_id: str, config: dict):
    """Instalar plugin en WordPress"""
    try:
        db = SessionLocal()
        panel = db.query(Panel).filter(Panel.id == panel_id).first()
        
        if not panel:
            logger.error(f"Panel {panel_id} not found")
            return {"status": "error", "message": "Panel not found"}
        
        # Import installation service
        from services.installation_service import InstallationService
        
        # Generate plugin
        plugin_zip = InstallationService.generate_plugin_zip(panel, db)
        zip_path = f"/tmp/panel-{panel_id}.zip"
        
        with open(zip_path, 'wb') as f:
            f.write(plugin_zip)
        
        # If WordPress URL provided, attempt installation
        if config.get('wordpress_url'):
            wordpress_url = config['wordpress_url']
            wordpress_user = config.get('wordpress_user')
            wordpress_password = config.get('wordpress_password')
            
            # Upload via WordPress REST API
            plugin_upload_url = f"{wordpress_url}/wp-json/wp/v2/plugins"
            
            with open(zip_path, 'rb') as f:
                files = {'plugin': f}
                headers = {}
                if wordpress_user and wordpress_password:
                    import base64
                    auth = base64.b64encode(f"{wordpress_user}:{wordpress_password}".encode()).decode()
                    headers['Authorization'] = f'Basic {auth}'
                
                response = requests.post(
                    plugin_upload_url,
                    files=files,
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code in [200, 201]:
                    logger.info(f"Plugin installed successfully on {wordpress_url}")
                else:
                    logger.warning(f"Plugin upload returned status {response.status_code}")
        
        # Update panel status
        panel.installation_status = "installed"
        db.commit()
        
        logger.info(f"Plugin installation completed for panel {panel_id}")
        return {"status": "success", "message": "Plugin installed successfully"}
    
    except Exception as e:
        logger.error(f"Error installing plugin: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        db.close()

# ==================== HEALTH CHECK ====================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "version": "2.0.0"}

if __name__ == "__main__":
    import uvicorn

# HBC3 repair_agents router
try:
    from backend.repair_agents.router import router as repair_router
except ModuleNotFoundError:
    from repair_agents.router import router as repair_router
    uvicorn.run(app, host="0.0.0.0", port=8000)

# HBC3 repair_agents router
app.include_router(
    repair_router,
    prefix="/api/v1/repair",
    tags=["repair_agents"],
)

# HBC3 repair_agents router
app.include_router(
    repair_router,
    prefix="/api/v1/repair",
    tags=["repair_agents"],
)
