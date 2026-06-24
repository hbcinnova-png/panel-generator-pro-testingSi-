import pytest
from datetime import datetime
from sqlalchemy.orm import Session
from uuid import uuid4

from services.panel_service import PanelService
from models import Panel, User, PanelStatus

@pytest.fixture
def test_user(db: Session):
    """Create test user"""
    user = User(
        id=str(uuid4()),
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password",
        is_active=True
    )
    db.add(user)
    db.commit()
    return user

@pytest.fixture
def test_panel(db: Session, test_user):
    """Create test panel"""
    panel = Panel(
        id=str(uuid4()),
        user_id=test_user.id,
        name="Test Panel",
        description="Test Description",
        theme="doctor_piscinas",
        config='{"colors": {"primary": "#FF69B4"}}',
        status=PanelStatus.DRAFT,
        created_at=datetime.utcnow()
    )
    db.add(panel)
    db.commit()
    return panel

class TestPanelService:
    """Test PanelService"""
    
    def test_create_panel(self, db: Session, test_user):
        """Test creating panel"""
        
        panel = PanelService.create_panel(
            user_id=test_user.id,
            name="New Panel",
            description="New Description",
            theme="tech_future",
            config={"colors": {"primary": "#00CED1"}},
            db=db
        )
        
        assert panel is not None
        assert panel.name == "New Panel"
        assert panel.user_id == test_user.id
        assert panel.status == PanelStatus.DRAFT
    
    def test_update_panel(self, db: Session, test_user, test_panel):
        """Test updating panel"""
        
        updated_panel = PanelService.update_panel(
            panel_id=test_panel.id,
            user_id=test_user.id,
            update_data={"name": "Updated Panel"},
            db=db
        )
        
        assert updated_panel.name == "Updated Panel"
        assert updated_panel.id == test_panel.id
    
    def test_delete_panel(self, db: Session, test_user, test_panel):
        """Test deleting panel"""
        
        result = PanelService.delete_panel(
            panel_id=test_panel.id,
            user_id=test_user.id,
            db=db
        )
        
        assert result is True
        
        # Verify panel is deleted
        panel = db.query(Panel).filter(Panel.id == test_panel.id).first()
        assert panel is None
    
    def test_get_user_panels(self, db: Session, test_user, test_panel):
        """Test getting user panels"""
        
        panels, total = PanelService.get_user_panels(
            user_id=test_user.id,
            db=db
        )
        
        assert len(panels) > 0
        assert total > 0
    
    def test_publish_panel(self, db: Session, test_user, test_panel):
        """Test publishing panel"""
        
        published_panel = PanelService.publish_panel(
            panel_id=test_panel.id,
            user_id=test_user.id,
            db=db
        )
        
        assert published_panel.status == PanelStatus.PUBLISHED
        assert published_panel.published_at is not None
    
    def test_archive_panel(self, db: Session, test_user, test_panel):
        """Test archiving panel"""
        
        archived_panel = PanelService.archive_panel(
            panel_id=test_panel.id,
            user_id=test_user.id,
            db=db
        )
        
        assert archived_panel.status == PanelStatus.ARCHIVED
    
    def test_get_panel_stats(self, db: Session, test_user, test_panel):
        """Test getting panel statistics"""
        
        stats = PanelService.get_panel_stats(
            panel_id=test_panel.id,
            user_id=test_user.id,
            db=db
        )
        
        assert stats is not None
        assert stats["panel_id"] == test_panel.id
        assert "installations" in stats
        assert "total_views" in stats
    
    def test_validate_panel_invalid_name(self, db: Session, test_panel):
        """Test panel validation with invalid name"""
        
        test_panel.name = "ab"  # Too short
        
        with pytest.raises(ValueError):
            PanelService._validate_panel(test_panel)
    
    def test_validate_panel_no_theme(self, db: Session, test_panel):
        """Test panel validation without theme"""
        
        test_panel.theme = None
        
        with pytest.raises(ValueError):
            PanelService._validate_panel(test_panel)
    
    def test_create_panel_invalid_user(self, db: Session):
        """Test creating panel with invalid user"""
        
        with pytest.raises(Exception):
            PanelService.create_panel(
                user_id="invalid_user",
                name="Test",
                description="Test",
                theme="test",
                config={},
                db=db
            )
