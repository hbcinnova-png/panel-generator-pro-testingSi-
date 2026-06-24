from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import json
import logging
from uuid import uuid4

from models import (
    Panel, User, Installation, Subscription, AuditLog,
    PanelStatus, InstallationStatus
)

logger = logging.getLogger(__name__)

class PanelService:
    """Service for panel operations"""
    
    @staticmethod
    def create_panel(
        user_id: str,
        name: str,
        description: str,
        theme: str,
        config: Dict[str, Any],
        db: Session
    ) -> Panel:
        """Create new panel"""
        
        try:
            panel = Panel(
                id=str(uuid4()),
                user_id=user_id,
                name=name,
                description=description,
                theme=theme,
                config=json.dumps(config),
                status=PanelStatus.DRAFT,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.add(panel)
            db.commit()
            db.refresh(panel)
            
            # Log action
            PanelService._log_action(
                db, user_id, "panel_created", panel.id, 
                {"name": name, "theme": theme}
            )
            
            logger.info(f"Panel created: {panel.id} by user {user_id}")
            return panel
        
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating panel: {e}")
            raise
    
    @staticmethod
    def update_panel(
        panel_id: str,
        user_id: str,
        update_data: Dict[str, Any],
        db: Session
    ) -> Panel:
        """Update panel"""
        
        try:
            panel = db.query(Panel).filter(
                and_(Panel.id == panel_id, Panel.user_id == user_id)
            ).first()
            
            if not panel:
                raise ValueError("Panel not found")
            
            # Track changes
            changes = {}
            for key, value in update_data.items():
                if hasattr(panel, key):
                    old_value = getattr(panel, key)
                    if old_value != value:
                        changes[key] = {"old": old_value, "new": value}
                        setattr(panel, key, value)
            
            panel.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(panel)
            
            # Log action
            PanelService._log_action(
                db, user_id, "panel_updated", panel.id, changes
            )
            
            logger.info(f"Panel updated: {panel.id}")
            return panel
        
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating panel: {e}")
            raise
    
    @staticmethod
    def delete_panel(panel_id: str, user_id: str, db: Session) -> bool:
        """Delete panel"""
        
        try:
            panel = db.query(Panel).filter(
                and_(Panel.id == panel_id, Panel.user_id == user_id)
            ).first()
            
            if not panel:
                raise ValueError("Panel not found")
            
            # Check if panel has active installations
            active_installations = db.query(Installation).filter(
                and_(
                    Installation.panel_id == panel_id,
                    Installation.status == InstallationStatus.ACTIVE
                )
            ).count()
            
            if active_installations > 0:
                raise ValueError("Cannot delete panel with active installations")
            
            db.delete(panel)
            db.commit()
            
            # Log action
            PanelService._log_action(
                db, user_id, "panel_deleted", panel_id, {}
            )
            
            logger.info(f"Panel deleted: {panel_id}")
            return True
        
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting panel: {e}")
            raise
    
    @staticmethod
    def get_user_panels(
        user_id: str,
        skip: int = 0,
        limit: int = 10,
        status: Optional[str] = None,
        db: Session = None
    ) -> tuple[List[Panel], int]:
        """Get user panels with pagination"""
        
        try:
            query = db.query(Panel).filter(Panel.user_id == user_id)
            
            if status:
                query = query.filter(Panel.status == status)
            
            total = query.count()
            panels = query.order_by(
                Panel.created_at.desc()
            ).offset(skip).limit(limit).all()
            
            return panels, total
        
        except Exception as e:
            logger.error(f"Error getting user panels: {e}")
            raise
    
    @staticmethod
    def publish_panel(panel_id: str, user_id: str, db: Session) -> Panel:
        """Publish panel"""
        
        try:
            panel = db.query(Panel).filter(
                and_(Panel.id == panel_id, Panel.user_id == user_id)
            ).first()
            
            if not panel:
                raise ValueError("Panel not found")
            
            # Validate panel before publishing
            PanelService._validate_panel(panel)
            
            panel.status = PanelStatus.PUBLISHED
            panel.published_at = datetime.utcnow()
            panel.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(panel)
            
            # Log action
            PanelService._log_action(
                db, user_id, "panel_published", panel_id, {}
            )
            
            logger.info(f"Panel published: {panel_id}")
            return panel
        
        except Exception as e:
            db.rollback()
            logger.error(f"Error publishing panel: {e}")
            raise
    
    @staticmethod
    def archive_panel(panel_id: str, user_id: str, db: Session) -> Panel:
        """Archive panel"""
        
        try:
            panel = db.query(Panel).filter(
                and_(Panel.id == panel_id, Panel.user_id == user_id)
            ).first()
            
            if not panel:
                raise ValueError("Panel not found")
            
            panel.status = PanelStatus.ARCHIVED
            panel.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(panel)
            
            # Log action
            PanelService._log_action(
                db, user_id, "panel_archived", panel_id, {}
            )
            
            logger.info(f"Panel archived: {panel_id}")
            return panel
        
        except Exception as e:
            db.rollback()
            logger.error(f"Error archiving panel: {e}")
            raise
    
    @staticmethod
    def get_panel_stats(panel_id: str, user_id: str, db: Session) -> Dict[str, Any]:
        """Get panel statistics"""
        
        try:
            panel = db.query(Panel).filter(
                and_(Panel.id == panel_id, Panel.user_id == user_id)
            ).first()
            
            if not panel:
                raise ValueError("Panel not found")
            
            # Get installation count
            installation_count = db.query(Installation).filter(
                Installation.panel_id == panel_id
            ).count()
            
            # Get active installations
            active_installations = db.query(Installation).filter(
                and_(
                    Installation.panel_id == panel_id,
                    Installation.status == InstallationStatus.ACTIVE
                )
            ).count()
            
            # Get views (from audit logs)
            views = db.query(AuditLog).filter(
                and_(
                    AuditLog.resource_id == panel_id,
                    AuditLog.action == "panel_viewed"
                )
            ).count()
            
            # Get last 7 days views
            week_ago = datetime.utcnow() - timedelta(days=7)
            views_7d = db.query(AuditLog).filter(
                and_(
                    AuditLog.resource_id == panel_id,
                    AuditLog.action == "panel_viewed",
                    AuditLog.created_at >= week_ago
                )
            ).count()
            
            return {
                "panel_id": panel_id,
                "name": panel.name,
                "status": panel.status,
                "created_at": panel.created_at,
                "published_at": panel.published_at,
                "installations": installation_count,
                "active_installations": active_installations,
                "total_views": views,
                "views_7d": views_7d,
                "theme": panel.theme
            }
        
        except Exception as e:
            logger.error(f"Error getting panel stats: {e}")
            raise
    
    @staticmethod
    def _validate_panel(panel: Panel) -> bool:
        """Validate panel before publishing"""
        
        if not panel.name or len(panel.name) < 3:
            raise ValueError("Panel name must be at least 3 characters")
        
        if not panel.theme:
            raise ValueError("Panel theme is required")
        
        try:
            config = json.loads(panel.config)
            if not config:
                raise ValueError("Panel configuration is empty")
        except json.JSONDecodeError:
            raise ValueError("Invalid panel configuration")
        
        return True
    
    @staticmethod
    def _log_action(
        db: Session,
        user_id: str,
        action: str,
        resource_id: str,
        details: Dict[str, Any]
    ) -> None:
        """Log action to audit log"""
        
        try:
            audit_log = AuditLog(
                id=str(uuid4()),
                user_id=user_id,
                action=action,
                resource_id=resource_id,
                details=json.dumps(details),
                created_at=datetime.utcnow()
            )
            
            db.add(audit_log)
            db.commit()
        
        except Exception as e:
            logger.error(f"Error logging action: {e}")
            # Don't raise, just log
