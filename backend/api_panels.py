from fastapi import APIRouter, HTTPException, status, Depends, Query
from pydantic import BaseModel, validator
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
import logging

from models import Panel, User, PanelStatus, InstallationStatus, AuditLog
from database import get_db
from api_auth import get_current_user, get_current_admin
from security import sanitize_input

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/panels", tags=["Panels"])

# ==================== SCHEMAS ====================

class PanelCreate(BaseModel):
    name: str
    business_name: str
    description: Optional[str] = None
    theme: str = "doctor_piscinas"
    color_primary: str = "#ff006e"
    color_secondary: str = "#00d9ff"
    effects: List[str] = ["particles", "parallax", "glow", "water"]
    services: List[str] = []
    integrations: List[str] = []
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    whatsapp: Optional[str] = None
    social: dict = {}
    installation_method: str = "zip"
    
    @validator('name')
    def name_valid(cls, v):
        if len(v) < 3:
            raise ValueError('Name must be at least 3 characters')
        return sanitize_input(v)
    
    @validator('business_name')
    def business_name_valid(cls, v):
        if len(v) < 2:
            raise ValueError('Business name must be at least 2 characters')
        return sanitize_input(v)

class PanelUpdate(BaseModel):
    name: Optional[str] = None
    business_name: Optional[str] = None
    description: Optional[str] = None
    theme: Optional[str] = None
    color_primary: Optional[str] = None
    color_secondary: Optional[str] = None
    effects: Optional[List[str]] = None
    services: Optional[List[str]] = None
    integrations: Optional[List[str]] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    whatsapp: Optional[str] = None
    social: Optional[dict] = None

class PanelResponse(BaseModel):
    id: str
    user_id: str
    name: str
    business_name: str
    description: Optional[str]
    theme: str
    color_primary: str
    color_secondary: str
    status: str
    installation_status: str
    views: int
    clicks: int
    conversions: int
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class PanelListResponse(BaseModel):
    total: int
    page: int
    per_page: int
    items: List[PanelResponse]

# ==================== ENDPOINTS ====================

@router.post("", response_model=PanelResponse, status_code=status.HTTP_201_CREATED)
async def create_panel(
    request: PanelCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new panel"""
    
    # Check user credits
    if current_user.subscription_plan == "free" and current_user.credits <= 0:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Insufficient credits"
        )
    
    # Create panel
    panel = Panel(
        user_id=current_user.id,
        name=request.name,
        business_name=request.business_name,
        description=request.description,
        theme=request.theme,
        color_primary=request.color_primary,
        color_secondary=request.color_secondary,
        effects=request.effects,
        services=request.services,
        integrations=request.integrations,
        phone=request.phone,
        email=request.email,
        website=request.website,
        whatsapp=request.whatsapp,
        social=request.social,
        installation_method=request.installation_method
    )
    
    db.add(panel)
    db.commit()
    db.refresh(panel)
    
    # Log action
    audit_log = AuditLog(
        user_id=current_user.id,
        action="create",
        resource_type="panel",
        resource_id=panel.id,
        changes={"created": True}
    )
    db.add(audit_log)
    db.commit()
    
    logger.info(f"Panel created: {panel.id} by user {current_user.id}")
    
    return panel

@router.get("", response_model=PanelListResponse)
async def list_panels(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List user's panels"""
    
    query = db.query(Panel).filter(Panel.user_id == current_user.id)
    
    if status:
        query = query.filter(Panel.status == status)
    
    total = query.count()
    
    panels = query.offset((page - 1) * per_page).limit(per_page).all()
    
    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "items": panels
    }

@router.get("/{panel_id}", response_model=PanelResponse)
async def get_panel(
    panel_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get panel details"""
    
    panel = db.query(Panel).filter(
        Panel.id == panel_id,
        Panel.user_id == current_user.id
    ).first()
    
    if not panel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Panel not found"
        )
    
    return panel

@router.put("/{panel_id}", response_model=PanelResponse)
async def update_panel(
    panel_id: str,
    request: PanelUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update panel"""
    
    panel = db.query(Panel).filter(
        Panel.id == panel_id,
        Panel.user_id == current_user.id
    ).first()
    
    if not panel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Panel not found"
        )
    
    # Track changes
    changes = {}
    
    if request.name is not None:
        changes["name"] = (panel.name, request.name)
        panel.name = request.name
    
    if request.business_name is not None:
        changes["business_name"] = (panel.business_name, request.business_name)
        panel.business_name = request.business_name
    
    if request.description is not None:
        changes["description"] = (panel.description, request.description)
        panel.description = request.description
    
    if request.theme is not None:
        changes["theme"] = (panel.theme, request.theme)
        panel.theme = request.theme
    
    if request.color_primary is not None:
        changes["color_primary"] = (panel.color_primary, request.color_primary)
        panel.color_primary = request.color_primary
    
    if request.color_secondary is not None:
        changes["color_secondary"] = (panel.color_secondary, request.color_secondary)
        panel.color_secondary = request.color_secondary
    
    if request.effects is not None:
        changes["effects"] = (panel.effects, request.effects)
        panel.effects = request.effects
    
    if request.services is not None:
        changes["services"] = (panel.services, request.services)
        panel.services = request.services
    
    if request.integrations is not None:
        changes["integrations"] = (panel.integrations, request.integrations)
        panel.integrations = request.integrations
    
    if request.phone is not None:
        changes["phone"] = (panel.phone, request.phone)
        panel.phone = request.phone
    
    if request.email is not None:
        changes["email"] = (panel.email, request.email)
        panel.email = request.email
    
    if request.website is not None:
        changes["website"] = (panel.website, request.website)
        panel.website = request.website
    
    if request.whatsapp is not None:
        changes["whatsapp"] = (panel.whatsapp, request.whatsapp)
        panel.whatsapp = request.whatsapp
    
    if request.social is not None:
        changes["social"] = (panel.social, request.social)
        panel.social = request.social
    
    db.commit()
    db.refresh(panel)
    
    # Log action
    audit_log = AuditLog(
        user_id=current_user.id,
        action="update",
        resource_type="panel",
        resource_id=panel.id,
        changes=changes
    )
    db.add(audit_log)
    db.commit()
    
    logger.info(f"Panel updated: {panel.id}")
    
    return panel

@router.delete("/{panel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_panel(
    panel_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete panel"""
    
    panel = db.query(Panel).filter(
        Panel.id == panel_id,
        Panel.user_id == current_user.id
    ).first()
    
    if not panel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Panel not found"
        )
    
    # Log action
    audit_log = AuditLog(
        user_id=current_user.id,
        action="delete",
        resource_type="panel",
        resource_id=panel.id,
        changes={"deleted": True}
    )
    db.add(audit_log)
    
    db.delete(panel)
    db.commit()
    
    logger.info(f"Panel deleted: {panel.id}")

@router.post("/{panel_id}/publish", response_model=PanelResponse)
async def publish_panel(
    panel_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Publish panel"""
    
    panel = db.query(Panel).filter(
        Panel.id == panel_id,
        Panel.user_id == current_user.id
    ).first()
    
    if not panel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Panel not found"
        )
    
    panel.status = PanelStatus.PUBLISHED
    panel.published_at = datetime.utcnow()
    
    db.commit()
    db.refresh(panel)
    
    # Log action
    audit_log = AuditLog(
        user_id=current_user.id,
        action="publish",
        resource_type="panel",
        resource_id=panel.id,
        changes={"status": ("draft", "published")}
    )
    db.add(audit_log)
    db.commit()
    
    logger.info(f"Panel published: {panel.id}")
    
    return panel

@router.post("/{panel_id}/archive", response_model=PanelResponse)
async def archive_panel(
    panel_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Archive panel"""
    
    panel = db.query(Panel).filter(
        Panel.id == panel_id,
        Panel.user_id == current_user.id
    ).first()
    
    if not panel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Panel not found"
        )
    
    panel.status = PanelStatus.ARCHIVED
    
    db.commit()
    db.refresh(panel)
    
    logger.info(f"Panel archived: {panel.id}")
    
    return panel

@router.get("/{panel_id}/stats")
async def get_panel_stats(
    panel_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get panel statistics"""
    
    panel = db.query(Panel).filter(
        Panel.id == panel_id,
        Panel.user_id == current_user.id
    ).first()
    
    if not panel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Panel not found"
        )
    
    conversion_rate = (panel.conversions / panel.clicks * 100) if panel.clicks > 0 else 0
    
    return {
        "views": panel.views,
        "clicks": panel.clicks,
        "conversions": panel.conversions,
        "conversion_rate": round(conversion_rate, 2),
        "ctr": round((panel.clicks / panel.views * 100), 2) if panel.views > 0 else 0
    }
