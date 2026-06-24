from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import uuid4
import json
import logging
import zipfile
import io
import os

from models import Installation, Panel, User, InstallationStatus, AuditLog

logger = logging.getLogger(__name__)

class InstallationService:
    """Service for panel installation"""
    
    @staticmethod
    def create_installation(
        panel_id: str,
        user_id: str,
        method: str,  # zip, ftp, api, oauth
        wordpress_url: str,
        db: Session
    ) -> Installation:
        """Create installation record"""
        
        try:
            installation = Installation(
                id=str(uuid4()),
                panel_id=panel_id,
                user_id=user_id,
                method=method,
                wordpress_url=wordpress_url,
                status=InstallationStatus.PENDING,
                created_at=datetime.utcnow()
            )
            
            db.add(installation)
            db.commit()
            db.refresh(installation)
            
            logger.info(f"Installation created: {installation.id}")
            return installation
        
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating installation: {e}")
            raise
    
    @staticmethod
    def generate_plugin_zip(panel: Panel, db: Session) -> bytes:
        """Generate WordPress plugin ZIP"""
        
        try:
            config = json.loads(panel.config)
            
            # Create ZIP in memory
            zip_buffer = io.BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # Plugin main file
                plugin_file = InstallationService._generate_plugin_php(panel)
                zip_file.writestr(f"{panel.id}/plugin.php", plugin_file)
                
                # CSS file
                css_file = InstallationService._generate_plugin_css(config)
                zip_file.writestr(f"{panel.id}/style.css", css_file)
                
                # JS file
                js_file = InstallationService._generate_plugin_js(panel, config)
                zip_file.writestr(f"{panel.id}/script.js", js_file)
                
                # HTML template
                html_file = InstallationService._generate_plugin_html(panel, config)
                zip_file.writestr(f"{panel.id}/template.php", html_file)
                
                # README
                readme_file = InstallationService._generate_readme(panel)
                zip_file.writestr(f"{panel.id}/README.md", readme_file)
            
            zip_buffer.seek(0)
            return zip_buffer.getvalue()
        
        except Exception as e:
            logger.error(f"Error generating plugin ZIP: {e}")
            raise
    
    @staticmethod
    def _generate_plugin_php(panel: Panel) -> str:
        """Generate plugin PHP file"""
        
        return f'''<?php
/**
 * Plugin Name: {panel.name} Panel
 * Description: {panel.description}
 * Version: 1.0.0
 * Author: Panel Generator Pro
 * License: GPL v2 or later
 */

if (!defined('ABSPATH')) {{
    exit;
}}

define('PANEL_PLUGIN_DIR', plugin_dir_path(__FILE__));
define('PANEL_PLUGIN_URL', plugin_dir_url(__FILE__));

class PanelPlugin {{
    public function __construct() {{
        add_action('wp_enqueue_scripts', array($this, 'enqueue_scripts'));
        add_shortcode('panel_{panel.id}', array($this, 'render_panel'));
    }}
    
    public function enqueue_scripts() {{
        wp_enqueue_style('panel-style', PANEL_PLUGIN_URL . 'style.css');
        wp_enqueue_script('panel-script', PANEL_PLUGIN_URL . 'script.js', array('jquery'), '1.0.0', true);
    }}
    
    public function render_panel() {{
        ob_start();
        include PANEL_PLUGIN_DIR . 'template.php';
        return ob_get_clean();
    }}
}}

new PanelPlugin();
?>'''
    
    @staticmethod
    def _generate_plugin_css(config: Dict[str, Any]) -> str:
        """Generate plugin CSS"""
        
        primary_color = config.get('primary_color', '#FF69B4')
        secondary_color = config.get('secondary_color', '#00CED1')
        
        return f'''/* Panel Generator Pro - {config.get('name', 'Panel')} */

:root {{
    --primary-color: {primary_color};
    --secondary-color: {secondary_color};
    --text-color: #333;
    --bg-color: #fff;
}}

.panel-container {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    border-radius: 10px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}}

.panel-header {{
    text-align: center;
    color: white;
    margin-bottom: 30px;
}}

.panel-header h1 {{
    font-size: 2.5em;
    margin: 0;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}}

.panel-content {{
    background: white;
    padding: 30px;
    border-radius: 8px;
    margin-bottom: 20px;
}}

.panel-button {{
    display: inline-block;
    padding: 12px 24px;
    margin: 10px;
    background: var(--primary-color);
    color: white;
    text-decoration: none;
    border-radius: 5px;
    transition: all 0.3s ease;
    border: none;
    cursor: pointer;
    font-size: 1em;
}}

.panel-button:hover {{
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0,0,0,0.3);
}}

@media (max-width: 768px) {{
    .panel-container {{
        padding: 15px;
    }}
    
    .panel-header h1 {{
        font-size: 1.8em;
    }}
    
    .panel-content {{
        padding: 15px;
    }}
}}
'''
    
    @staticmethod
    def _generate_plugin_js(panel: Panel, config: Dict[str, Any]) -> str:
        """Generate plugin JavaScript"""
        
        return f'''// Panel Generator Pro - {config.get('name', 'Panel')}

(function($) {{
    $(document).ready(function() {{
        console.log('Panel {panel.id} loaded');
        
        // Initialize panel
        initPanel();
        
        // Event handlers
        $('.panel-button').on('click', function(e) {{
            e.preventDefault();
            handleButtonClick($(this));
        }});
    }});
    
    function initPanel() {{
        // Add animations
        $('.panel-container').fadeIn(500);
    }}
    
    function handleButtonClick($button) {{
        var action = $button.data('action');
        
        switch(action) {{
            case 'contact':
                handleContact();
                break;
            case 'quote':
                handleQuote();
                break;
            default:
                console.log('Action: ' + action);
        }}
    }}
    
    function handleContact() {{
        alert('Contact form would open here');
    }}
    
    function handleQuote() {{
        alert('Quote form would open here');
    }}
}})(jQuery);
'''
    
    @staticmethod
    def _generate_plugin_html(panel: Panel, config: Dict[str, Any]) -> str:
        """Generate plugin HTML template"""
        
        return f'''<?php
// Panel Template - {panel.name}
?>

<div class="panel-container">
    <div class="panel-header">
        <h1>{panel.name}</h1>
        <p>{panel.description}</p>
    </div>
    
    <div class="panel-content">
        <p>Welcome to {panel.name}!</p>
        
        <div class="panel-actions">
            <button class="panel-button" data-action="contact">
                Contact Us
            </button>
            <button class="panel-button" data-action="quote">
                Get Quote
            </button>
        </div>
    </div>
</div>
'''
    
    @staticmethod
    def _generate_readme(panel: Panel) -> str:
        """Generate README file"""
        
        return f'''# {panel.name} Panel

Generated by Panel Generator Pro

## Installation

1. Upload the plugin folder to `/wp-content/plugins/`
2. Activate the plugin in WordPress admin
3. Use the shortcode `[panel_{panel.id}]` to display the panel

## Usage

Add this shortcode to any page or post:

```
[panel_{panel.id}]
```

## Features

- Responsive design
- Animated effects
- Professional styling
- Easy customization

## Support

For support, visit: https://panelgenerator.pro

## License

GPL v2 or later
'''
    
    @staticmethod
    def update_installation_status(
        installation_id: str,
        status: str,
        db: Session
    ) -> Installation:
        """Update installation status"""
        
        try:
            installation = db.query(Installation).filter(
                Installation.id == installation_id
            ).first()
            
            if not installation:
                raise ValueError("Installation not found")
            
            installation.status = status
            installation.updated_at = datetime.utcnow()
            
            if status == InstallationStatus.ACTIVE:
                installation.activated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(installation)
            
            logger.info(f"Installation status updated: {installation_id} -> {status}")
            return installation
        
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating installation status: {e}")
            raise
    
    @staticmethod
    def get_installation_status(
        installation_id: str,
        db: Session
    ) -> Dict[str, Any]:
        """Get installation status"""
        
        try:
            installation = db.query(Installation).filter(
                Installation.id == installation_id
            ).first()
            
            if not installation:
                raise ValueError("Installation not found")
            
            return {
                "id": installation.id,
                "panel_id": installation.panel_id,
                "method": installation.method,
                "status": installation.status,
                "wordpress_url": installation.wordpress_url,
                "created_at": installation.created_at,
                "activated_at": installation.activated_at,
                "updated_at": installation.updated_at
            }
        
        except Exception as e:
            logger.error(f"Error getting installation status: {e}")
            raise
