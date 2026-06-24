from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
import logging
import zipfile
import os
import ftplib
import requests
from datetime import datetime

from models import Panel, User, InstallationLog, InstallationStatus
from database import get_db
from api_auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/panels", tags=["Installation"])

# ==================== SCHEMAS ====================

class InstallationRequest(BaseModel):
    method: str  # zip, ftp, api, oauth
    ftp_host: Optional[str] = None
    ftp_user: Optional[str] = None
    ftp_password: Optional[str] = None
    wordpress_url: Optional[str] = None
    wordpress_user: Optional[str] = None
    wordpress_password: Optional[str] = None

class InstallationResponse(BaseModel):
    id: str
    status: str
    message: str
    download_url: Optional[str] = None

# ==================== ENDPOINTS ====================

@router.post("/{panel_id}/install", response_model=InstallationResponse)
async def install_panel(
    panel_id: str,
    request: InstallationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Install panel in WordPress"""
    
    panel = db.query(Panel).filter(
        Panel.id == panel_id,
        Panel.user_id == current_user.id
    ).first()
    
    if not panel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Panel not found"
        )
    
    # Create installation log
    install_log = InstallationLog(
        panel_id=panel.id,
        method=request.method,
        status=InstallationStatus.INSTALLING
    )
    db.add(install_log)
    db.commit()
    
    # Update panel status
    panel.installation_status = InstallationStatus.INSTALLING
    panel.installation_method = request.method
    db.commit()
    
    # Execute installation based on method
    if request.method == "zip":
        background_tasks.add_task(
            generate_zip_plugin,
            panel_id,
            install_log.id,
            db
        )
        return {
            "id": install_log.id,
            "status": "installing",
            "message": "Generating plugin ZIP..."
        }
    
    elif request.method == "ftp":
        background_tasks.add_task(
            install_via_ftp,
            panel_id,
            install_log.id,
            request.ftp_host,
            request.ftp_user,
            request.ftp_password,
            db
        )
        return {
            "id": install_log.id,
            "status": "installing",
            "message": "Installing via FTP..."
        }
    
    elif request.method == "api":
        background_tasks.add_task(
            install_via_api,
            panel_id,
            install_log.id,
            request.wordpress_url,
            request.wordpress_user,
            request.wordpress_password,
            db
        )
        return {
            "id": install_log.id,
            "status": "installing",
            "message": "Installing via API..."
        }
    
    elif request.method == "oauth":
        return {
            "id": install_log.id,
            "status": "pending",
            "message": "OAuth installation requires user authorization"
        }
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid installation method"
        )

@router.get("/{panel_id}/install-status")
async def get_installation_status(
    panel_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get installation status"""
    
    panel = db.query(Panel).filter(
        Panel.id == panel_id,
        Panel.user_id == current_user.id
    ).first()
    
    if not panel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Panel not found"
        )
    
    latest_log = db.query(InstallationLog).filter(
        InstallationLog.panel_id == panel.id
    ).order_by(InstallationLog.started_at.desc()).first()
    
    return {
        "status": panel.installation_status,
        "method": panel.installation_method,
        "log": {
            "message": latest_log.log_message if latest_log else None,
            "error": latest_log.error_message if latest_log else None,
            "started_at": latest_log.started_at if latest_log else None,
            "completed_at": latest_log.completed_at if latest_log else None
        }
    }

@router.get("/{panel_id}/download")
async def download_plugin(
    panel_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download plugin ZIP"""
    
    panel = db.query(Panel).filter(
        Panel.id == panel_id,
        Panel.user_id == current_user.id
    ).first()
    
    if not panel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Panel not found"
        )
    
    # Generate plugin ZIP
    zip_path = generate_plugin_zip(panel)
    
    return {
        "download_url": f"/api/v1/panels/{panel_id}/download/file",
        "filename": f"panel-{panel.id}.zip"
    }

# ==================== HELPER FUNCTIONS ====================

def generate_plugin_zip(panel: Panel) -> str:
    """Generate WordPress plugin ZIP file"""
    
    # Create temporary directory
    temp_dir = f"/tmp/panel-{panel.id}"
    os.makedirs(temp_dir, exist_ok=True)
    
    # Create plugin structure
    plugin_dir = f"{temp_dir}/doctor-piscinas-{panel.id}"
    os.makedirs(plugin_dir, exist_ok=True)
    
    # Create main plugin file
    plugin_file = f"{plugin_dir}/plugin.php"
    with open(plugin_file, "w") as f:
        f.write(generate_plugin_php(panel))
    
    # Create CSS file
    css_dir = f"{plugin_dir}/assets/css"
    os.makedirs(css_dir, exist_ok=True)
    css_file = f"{css_dir}/panel.css"
    with open(css_file, "w") as f:
        f.write(generate_plugin_css(panel))
    
    # Create JS file
    js_dir = f"{plugin_dir}/assets/js"
    os.makedirs(js_dir, exist_ok=True)
    js_file = f"{js_dir}/panel.js"
    with open(js_file, "w") as f:
        f.write(generate_plugin_js(panel))
    
    # Create template file
    template_dir = f"{plugin_dir}/templates"
    os.makedirs(template_dir, exist_ok=True)
    template_file = f"{template_dir}/panel.php"
    with open(template_file, "w") as f:
        f.write(generate_panel_template(panel))
    
    # Create README
    readme_file = f"{plugin_dir}/README.md"
    with open(readme_file, "w") as f:
        f.write(f"# {panel.business_name} Panel\n\n{panel.description}\n")
    
    # Create ZIP file
    zip_path = f"/tmp/panel-{panel.id}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(plugin_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, temp_dir)
                zipf.write(file_path, arcname)
    
    return zip_path

def generate_plugin_php(panel: Panel) -> str:
    """Generate main plugin PHP file"""
    
    return f"""<?php
/**
 * Plugin Name: {panel.business_name} Panel
 * Plugin URI: https://panelgenerator.pro
 * Description: {panel.description}
 * Version: {panel.plugin_version}
 * Author: Panel Generator Pro
 * License: GPL v2 or later
 */

if (!defined('ABSPATH')) {{
    exit;
}}

define('PANEL_PLUGIN_DIR', plugin_dir_path(__FILE__));
define('PANEL_PLUGIN_URL', plugin_dir_url(__FILE__));

// Load plugin files
require_once PANEL_PLUGIN_DIR . 'includes/class-panel.php';

// Initialize plugin
function panel_init() {{
    new Panel_Plugin();
}}
add_action('plugins_loaded', 'panel_init');

// Register shortcode
add_shortcode('panel', function() {{
    ob_start();
    include PANEL_PLUGIN_DIR . 'templates/panel.php';
    return ob_get_clean();
}});

// Enqueue scripts and styles
function panel_enqueue_assets() {{
    wp_enqueue_style('panel-style', PANEL_PLUGIN_URL . 'assets/css/panel.css');
    wp_enqueue_script('panel-script', PANEL_PLUGIN_URL . 'assets/js/panel.js', array('jquery'), false, true);
}}
add_action('wp_enqueue_scripts', 'panel_enqueue_assets');

// Activation hook
register_activation_hook(__FILE__, function() {{
    // Create tables, set options, etc.
}});

// Deactivation hook
register_deactivation_hook(__FILE__, function() {{
    // Clean up
}});
?>"""

def generate_plugin_css(panel: Panel) -> str:
    """Generate plugin CSS"""
    
    return f"""/* Panel Styles */

:root {{
    --primary: {panel.color_primary};
    --secondary: {panel.color_secondary};
}}

.panel {{
    background: linear-gradient(135deg, #0d0d0d 0%, #1a1a1a 100%);
    border: 2px solid;
    border-image: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%) 1;
    border-radius: 16px;
    padding: 40px;
    max-width: 500px;
    margin: 0 auto;
    color: white;
    font-family: 'Inter', sans-serif;
}}

.panel-header {{
    text-align: center;
    margin-bottom: 30px;
}}

.panel-title {{
    font-size: 28px;
    font-weight: 700;
    background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 8px;
}}

.panel-description {{
    font-size: 14px;
    color: #aaa;
}}

.panel-services {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin-bottom: 30px;
}}

.service-item {{
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 12px;
    text-align: center;
    font-size: 12px;
    font-weight: 600;
    transition: all 0.3s ease;
}}

.service-item:hover {{
    background: rgba(var(--primary-rgb), 0.1);
    border-color: var(--primary);
    transform: translateY(-2px);
}}

.panel-buttons {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
}}

.btn {{
    padding: 12px;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    font-size: 12px;
    transition: all 0.3s ease;
}}

.btn-primary {{
    background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
    color: white;
}}

.btn-primary:hover {{
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(255, 0, 110, 0.4);
}}

.panel-status {{
    text-align: center;
    margin-top: 20px;
    font-size: 12px;
    color: #00aa44;
}}

@media (max-width: 768px) {{
    .panel {{
        padding: 20px;
    }}
    
    .panel-title {{
        font-size: 20px;
    }}
    
    .panel-services {{
        grid-template-columns: 1fr;
    }}
}}
"""

def generate_plugin_js(panel: Panel) -> str:
    """Generate plugin JavaScript"""
    
    return """// Panel JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const buttons = document.querySelectorAll('.panel .btn');
    
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            const action = this.dataset.action;
            handlePanelAction(action);
        });
    });
});

function handlePanelAction(action) {
    console.log('Panel action:', action);
    
    switch(action) {
        case 'whatsapp':
            openWhatsApp();
            break;
        case 'email':
            openEmail();
            break;
        case 'call':
            makeCall();
            break;
        case 'quote':
            requestQuote();
            break;
    }
}

function openWhatsApp() {
    const phone = document.querySelector('[data-whatsapp]').dataset.whatsapp;
    const message = 'Hola, me gustaría más información sobre tus servicios';
    window.open(`https://wa.me/${phone}?text=${encodeURIComponent(message)}`);
}

function openEmail() {
    const email = document.querySelector('[data-email]').dataset.email;
    window.location.href = `mailto:${email}`;
}

function makeCall() {
    const phone = document.querySelector('[data-phone]').dataset.phone;
    window.location.href = `tel:${phone}`;
}

function requestQuote() {
    alert('Solicitud de presupuesto enviada');
}
"""

def generate_panel_template(panel: Panel) -> str:
    """Generate panel template"""
    
    services_html = "\n".join([
        f'<div class="service-item">{service}</div>'
        for service in panel.services[:4]
    ])
    
    return f"""<div class="panel">
    <div class="panel-header">
        <div class="panel-title">{panel.business_name}</div>
        <div class="panel-description">{panel.description}</div>
    </div>
    
    <div class="panel-services">
        {services_html}
    </div>
    
    <div class="panel-buttons">
        <button class="btn btn-primary" data-action="quote">Presupuesto</button>
        <button class="btn btn-secondary" data-action="whatsapp" data-whatsapp="{panel.whatsapp}">WhatsApp</button>
    </div>
    
    <div class="panel-status">● Sistema Online</div>
</div>
"""

async def generate_zip_plugin(panel_id: str, log_id: str, db: Session):
    """Generate ZIP plugin in background"""
    
    try:
        panel = db.query(Panel).filter(Panel.id == panel_id).first()
        if not panel:
            return
        
        zip_path = generate_plugin_zip(panel)
        
        # Update log
        log = db.query(InstallationLog).filter(InstallationLog.id == log_id).first()
        if log:
            log.status = InstallationStatus.INSTALLED
            log.log_message = f"Plugin generated successfully at {zip_path}"
            log.completed_at = datetime.utcnow()
            db.commit()
        
        # Update panel
        panel.installation_status = InstallationStatus.INSTALLED
        db.commit()
        
        logger.info(f"ZIP plugin generated for panel {panel_id}")
    
    except Exception as e:
        logger.error(f"Error generating ZIP plugin: {e}")
        log = db.query(InstallationLog).filter(InstallationLog.id == log_id).first()
        if log:
            log.status = InstallationStatus.FAILED
            log.error_message = str(e)
            log.completed_at = datetime.utcnow()
            db.commit()

async def install_via_ftp(panel_id: str, log_id: str, ftp_host: str, ftp_user: str, ftp_password: str, db: Session):
    """Install via FTP in background"""
    
    try:
        panel = db.query(Panel).filter(Panel.id == panel_id).first()
        if not panel:
            return
        
        # Connect to FTP
        ftp = ftplib.FTP(ftp_host, ftp_user, ftp_password)
        
        # Generate and upload plugin
        zip_path = generate_plugin_zip(panel)
        
        with open(zip_path, 'rb') as f:
            ftp.storbinary(f'STOR /wp-content/plugins/panel-{panel_id}.zip', f)
        
        ftp.quit()
        
        # Update log
        log = db.query(InstallationLog).filter(InstallationLog.id == log_id).first()
        if log:
            log.status = InstallationStatus.INSTALLED
            log.log_message = "Plugin installed successfully via FTP"
            log.completed_at = datetime.utcnow()
            db.commit()
        
        # Update panel
        panel.installation_status = InstallationStatus.INSTALLED
        db.commit()
        
        logger.info(f"Panel {panel_id} installed via FTP")
    
    except Exception as e:
        logger.error(f"Error installing via FTP: {e}")
        log = db.query(InstallationLog).filter(InstallationLog.id == log_id).first()
        if log:
            log.status = InstallationStatus.FAILED
            log.error_message = str(e)
            log.completed_at = datetime.utcnow()
            db.commit()

async def install_via_api(panel_id: str, log_id: str, wordpress_url: str, wordpress_user: str, wordpress_password: str, db: Session):
    """Install via WordPress API in background"""
    
    try:
        panel = db.query(Panel).filter(Panel.id == panel_id).first()
        if not panel:
            return
        
        # Generate plugin ZIP
        zip_path = generate_plugin_zip(panel)
        
        # Upload via WordPress REST API
        with open(zip_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(
                f"{wordpress_url}/wp-json/wp/v2/plugins",
                files=files,
                auth=(wordpress_user, wordpress_password)
            )
        
        if response.status_code == 201:
            # Update log
            log = db.query(InstallationLog).filter(InstallationLog.id == log_id).first()
            if log:
                log.status = InstallationStatus.INSTALLED
                log.log_message = "Plugin installed successfully via API"
                log.completed_at = datetime.utcnow()
                db.commit()
            
            # Update panel
            panel.installation_status = InstallationStatus.INSTALLED
            panel.wordpress_url = wordpress_url
            db.commit()
            
            logger.info(f"Panel {panel_id} installed via API")
        else:
            raise Exception(f"API error: {response.status_code}")
    
    except Exception as e:
        logger.error(f"Error installing via API: {e}")
        log = db.query(InstallationLog).filter(InstallationLog.id == log_id).first()
        if log:
            log.status = InstallationStatus.FAILED
            log.error_message = str(e)
            log.completed_at = datetime.utcnow()
            db.commit()
