from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
import pyotp
import qrcode
from io import BytesIO
import base64
from cryptography.fernet import Fernet
from config import get_settings

settings = get_settings()

# ==================== PASSWORD HASHING ====================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# ==================== JWT TOKENS ====================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

# ==================== 2FA ====================

def generate_2fa_secret() -> str:
    return pyotp.random_base32()

def get_2fa_qr_code(email: str, secret: str) -> str:
    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(
        name=email,
        issuer_name=settings.APP_NAME
    )
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"

def verify_2fa_token(secret: str, token: str) -> bool:
    totp = pyotp.TOTP(secret)
    return totp.verify(token)

# ==================== ENCRYPTION ====================

cipher_suite = Fernet(Fernet.generate_key() if len(settings.ENCRYPTION_KEY) < 32 else settings.ENCRYPTION_KEY.encode()[:32])

def encrypt_data(data: str) -> str:
    f = Fernet(base64.urlsafe_b64encode(settings.ENCRYPTION_KEY.encode()[:32].ljust(32)[:32]))
    return f.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data: str) -> str:
    f = Fernet(base64.urlsafe_b64encode(settings.ENCRYPTION_KEY.encode()[:32].ljust(32)[:32]))
    return f.decrypt(encrypted_data.encode()).decode()

# ==================== RATE LIMITING ====================

from collections import defaultdict
import time

rate_limit_store = defaultdict(list)

def check_rate_limit(client_id: str) -> bool:
    if not settings.RATE_LIMIT_ENABLED:
        return True
    
    now = time.time()
    cutoff = now - settings.RATE_LIMIT_PERIOD
    
    # Limpiar requests antiguos
    rate_limit_store[client_id] = [
        req_time for req_time in rate_limit_store[client_id]
        if req_time > cutoff
    ]
    
    # Verificar límite
    if len(rate_limit_store[client_id]) >= settings.RATE_LIMIT_REQUESTS:
        return False
    
    # Agregar nuevo request
    rate_limit_store[client_id].append(now)
    return True

# ==================== CSRF PROTECTION ====================

import secrets

csrf_tokens = {}

def generate_csrf_token() -> str:
    token = secrets.token_urlsafe(32)
    csrf_tokens[token] = datetime.utcnow() + timedelta(hours=1)
    return token

def verify_csrf_token(token: str) -> bool:
    if token not in csrf_tokens:
        return False
    
    if csrf_tokens[token] < datetime.utcnow():
        del csrf_tokens[token]
        return False
    
    return True

# ==================== SECURITY HEADERS ====================

def get_security_headers() -> dict:
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'",
    }

# ==================== INPUT VALIDATION ====================

import re

def validate_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password: str) -> tuple[bool, str]:
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain lowercase letter"
    
    if not re.search(r'[0-9]', password):
        return False, "Password must contain number"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain special character"
    
    return True, "Password is valid"

def validate_phone(phone: str) -> bool:
    pattern = r'^\+?1?\d{9,15}$'
    return re.match(pattern, phone.replace(" ", "").replace("-", "")) is not None

def sanitize_input(data: str) -> str:
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", ';', '&', '|', '`']
    for char in dangerous_chars:
        data = data.replace(char, '')
    return data.strip()

# ==================== SQL INJECTION PREVENTION ====================

def validate_sql_input(input_str: str) -> bool:
    dangerous_patterns = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
        r"(--|;|\/\*|\*\/)",
        r"('|\")\s*(OR|AND)\s*('|\")",
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, input_str, re.IGNORECASE):
            return False
    
    return True
