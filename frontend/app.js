// ==================== GLOBAL STATE ====================

let currentStep = 1;
const totalSteps = 4;
let formData = {
    businessName: '',
    description: '',
    phone: '',
    email: '',
    website: '',
    logo: null,
    theme: 'doctor_piscinas',
    colorPrimary: '#ff006e',
    colorSecondary: '#00d9ff',
    effects: ['particles', 'parallax', 'glow', 'water'],
    services: [],
    integrations: [],
    whatsapp: '',
    social: {},
    installMethod: 'zip',
    ftp: {},
    api: {}
};

// ==================== CONFIGURATION ====================
const API_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:8000'
    : window.location.origin.replace(/:\d+$/, ':8000');

const API_BASE = `${API_URL}/api/v1`;

// ==================== INITIALIZATION ====================

document.addEventListener('DOMContentLoaded', () => {
    console.log('API URL:', API_BASE);
    initializeForm();
    setupEventListeners();
    updatePreview();
});

function initializeForm() {
    // Mostrar primer paso
    showStep(1);
    
    // Inicializar temas
    document.querySelectorAll('.theme-option').forEach(option => {
        option.addEventListener('click', () => {
            document.querySelectorAll('.theme-option').forEach(o => o.classList.remove('selected'));
            option.classList.add('selected');
            formData.theme = option.dataset.theme;
            updatePreview();
        });
    });
    
    // Marcar primer tema como seleccionado
    document.querySelector('[data-theme="doctor_piscinas"]').classList.add('selected');
}

function setupEventListeners() {
    // Servicios
    const serviceInput = document.getElementById('serviceInput');
    if (serviceInput) {
        serviceInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                addService(serviceInput.value);
                serviceInput.value = '';
            }
        });
    }
    
    // Método de instalación
    document.querySelectorAll('input[name="installMethod"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            formData.installMethod = e.target.value;
            updateInstallationFields();
        });
    });
    
    // Colores
    document.querySelector('input[name="colorPrimary"]').addEventListener('change', (e) => {
        formData.colorPrimary = e.target.value;
        updatePreview();
    });
    
    document.querySelector('input[name="colorSecondary"]').addEventListener('change', (e) => {
        formData.colorSecondary = e.target.value;
        updatePreview();
    });
    
    // Efectos
    document.querySelectorAll('input[name="effects"]').forEach(checkbox => {
        checkbox.addEventListener('change', (e) => {
            if (e.target.checked) {
                if (!formData.effects.includes(e.target.value)) {
                    formData.effects.push(e.target.value);
                }
            } else {
                formData.effects = formData.effects.filter(f => f !== e.target.value);
            }
            updatePreview();
        });
    });
    
    // Integraciones
    document.querySelectorAll('input[name="integrations"]').forEach(checkbox => {
        checkbox.addEventListener('change', (e) => {
            if (e.target.checked) {
                if (!formData.integrations.includes(e.target.value)) {
                    formData.integrations.push(e.target.value);
                }
            } else {
                formData.integrations = formData.integrations.filter(i => i !== e.target.value);
            }
            updatePreview();
        });
    });
    
    // Form submit
    document.getElementById('panelForm').addEventListener('submit', (e) => {
        e.preventDefault();
        submitForm();
    });
}

// ==================== FORM NAVIGATION ====================

function showStep(step) {
    // Ocultar todos los pasos
    document.querySelectorAll('.form-step').forEach(s => s.classList.remove('active'));
    
    // Mostrar paso actual
    document.querySelector(`[data-step="${step}"]`).classList.add('active');
    
    // Actualizar botones
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const submitBtn = document.getElementById('submitBtn');
    
    if (step === 1) {
        prevBtn.style.display = 'none';
    } else {
        prevBtn.style.display = 'block';
    }
    
    if (step === totalSteps) {
        nextBtn.style.display = 'none';
        submitBtn.style.display = 'block';
    } else {
        nextBtn.style.display = 'block';
        submitBtn.style.display = 'none';
    }
    
    currentStep = step;
    updateFormData();
}

function nextStep() {
    if (validateStep(currentStep)) {
        if (currentStep < totalSteps) {
            showStep(currentStep + 1);
        }
    }
}

function previousStep() {
    if (currentStep > 1) {
        showStep(currentStep - 1);
    }
}

function validateStep(step) {
    const form = document.getElementById('panelForm');
    const inputs = form.querySelectorAll(`[data-step="${step}"] input[required], [data-step="${step}"] textarea[required]`);
    
    for (let input of inputs) {
        if (!input.value.trim()) {
            input.focus();
            input.style.borderColor = '#ff0000';
            setTimeout(() => {
                input.style.borderColor = '';
            }, 2000);
            return false;
        }
    }
    
    return true;
}

// ==================== FORM DATA ====================

function updateFormData() {
    const form = document.getElementById('panelForm');
    
    // Paso 1: Información básica
    formData.businessName = form.querySelector('input[name="businessName"]')?.value || '';
    formData.description = form.querySelector('textarea[name="description"]')?.value || '';
    formData.phone = form.querySelector('input[name="phone"]')?.value || '';
    formData.email = form.querySelector('input[name="email"]')?.value || '';
    formData.website = form.querySelector('input[name="website"]')?.value || '';
    
    // Paso 2: Diseño
    formData.colorPrimary = form.querySelector('input[name="colorPrimary"]')?.value || '#ff006e';
    formData.colorSecondary = form.querySelector('input[name="colorSecondary"]')?.value || '#00d9ff';
    
    // Paso 3: Integraciones
    formData.whatsapp = form.querySelector('input[name="whatsapp"]')?.value || '';
    formData.social = {
        facebook: form.querySelector('input[name="facebook"]')?.value || '',
        instagram: form.querySelector('input[name="instagram"]')?.value || '',
        twitter: form.querySelector('input[name="twitter"]')?.value || '',
        linkedin: form.querySelector('input[name="linkedin"]')?.value || ''
    };
    
    // Paso 4: Instalación
    formData.installMethod = form.querySelector('input[name="installMethod"]:checked')?.value || 'zip';
    
    updatePreview();
}

function addService(service) {
    if (service.trim()) {
        formData.services.push(service);
        renderServices();
        updatePreview();
    }
}

function removeService(index) {
    formData.services.splice(index, 1);
    renderServices();
    updatePreview();
}

function renderServices() {
    const list = document.getElementById('servicesList');
    list.innerHTML = formData.services.map((service, index) => `
        <div class="service-tag">
            ${service}
            <button type="button" onclick="removeService(${index})">×</button>
        </div>
    `).join('');
}

function updateInstallationFields() {
    const ftpFields = document.getElementById('ftpFields');
    const apiFields = document.getElementById('apiFields');
    
    ftpFields.classList.add('hidden');
    apiFields.classList.add('hidden');
    
    if (formData.installMethod === 'ftp') {
        ftpFields.classList.remove('hidden');
    } else if (formData.installMethod === 'api' || formData.installMethod === 'oauth') {
        apiFields.classList.remove('hidden');
    }
}

// ==================== PREVIEW ====================

function updatePreview() {
    const previewFrame = document.getElementById('previewFrame');
    const previewHTML = generatePreviewHTML();
    
    previewFrame.srcdoc = previewHTML;
}

function generatePreviewHTML() {
    const colors = {
        doctor_piscinas: { primary: '#ff006e', secondary: '#00d9ff' },
        tech_future: { primary: '#00d9ff', secondary: '#a000ff' },
        luxury_gold: { primary: '#ffd700', secondary: '#1a1a1a' },
        nature_green: { primary: '#00aa44', secondary: '#8b7355' },
        gaming_neon: { primary: '#ff00ff', secondary: '#00ffff' }
    };
    
    const themeColors = colors[formData.theme] || colors.doctor_piscinas;
    
    return `
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Preview</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #0d0d0d 0%, #1a1a1a 100%);
            color: white;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .panel {
            width: 100%;
            max-width: 500px;
            background: rgba(20, 20, 20, 0.8);
            border: 2px solid;
            border-image: linear-gradient(135deg, ${themeColors.primary} 0%, ${themeColors.secondary} 100%) 1;
            border-radius: 16px;
            padding: 40px;
            box-shadow: 0 0 40px rgba(${hexToRgb(themeColors.primary).join(',')}, 0.3);
            backdrop-filter: blur(10px);
        }
        
        .panel-header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .panel-title {
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 8px;
            background: linear-gradient(135deg, ${themeColors.primary} 0%, ${themeColors.secondary} 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .panel-description {
            font-size: 14px;
            color: #aaa;
        }
        
        .services {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-bottom: 30px;
        }
        
        .service-item {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(${hexToRgb(themeColors.primary).join(',')}, 0.3);
            border-radius: 8px;
            padding: 12px;
            text-align: center;
            font-size: 12px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .service-item:hover {
            background: rgba(${hexToRgb(themeColors.primary).join(',')}, 0.1);
            border-color: ${themeColors.primary};
            transform: translateY(-2px);
        }
        
        .buttons {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }
        
        .btn {
            padding: 12px;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            font-size: 12px;
            transition: all 0.3s ease;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, ${themeColors.primary} 0%, ${themeColors.secondary} 100%);
            color: white;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(${hexToRgb(themeColors.primary).join(',')}, 0.4);
        }
        
        .btn-secondary {
            background: rgba(${hexToRgb(themeColors.secondary).join(',')}, 0.2);
            color: ${themeColors.secondary};
            border: 1px solid ${themeColors.secondary};
        }
        
        .btn-secondary:hover {
            background: rgba(${hexToRgb(themeColors.secondary).join(',')}, 0.3);
        }
        
        .status {
            text-align: center;
            margin-top: 20px;
            font-size: 12px;
            color: #00aa44;
        }
        
        .status::before {
            content: '●';
            margin-right: 6px;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
    </style>
</head>
<body>
    <div class="panel">
        <div class="panel-header">
            <div class="panel-title">${formData.businessName || 'Tu Negocio'}</div>
            <div class="panel-description">${formData.description || 'Descripción del negocio'}</div>
        </div>
        
        ${formData.services.length > 0 ? `
            <div class="services">
                ${formData.services.slice(0, 4).map(s => `<div class="service-item">${s}</div>`).join('')}
            </div>
        ` : ''}
        
        <div class="buttons">
            <button class="btn btn-primary">Presupuesto</button>
            <button class="btn btn-secondary">WhatsApp</button>
        </div>
        
        <div class="status">Sistema Online</div>
    </div>
</body>
</html>
    `;
}

function hexToRgb(hex) {
    const result = /^#?([a-f\\d]{2})([a-f\\d]{2})([a-f\\d]{2})$/i.exec(hex);
    return result ? [
        parseInt(result[1], 16),
        parseInt(result[2], 16),
        parseInt(result[3], 16)
    ] : [0, 0, 0];
}

// ==================== FORM SUBMISSION ====================

async function submitForm() {
    updateFormData();
    
    // Validar datos
    if (!formData.businessName || !formData.email) {
        alert('Por favor completa todos los campos requeridos');
        return;
    }
    
    // Mostrar loading
    const submitBtn = document.getElementById('submitBtn');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = 'Generando...';
    submitBtn.disabled = true;
    
    try {
        // Enviar al backend
        const response = await fetch(`${API_BASE}/panels`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify(formData)
        });
        
        if (response.ok) {
            const data = await response.json();
            alert('¡Panel generado exitosamente!');
            window.location.href = `/dashboard?id=${data.id}`;
        } else {
            const errorData = await response.json();
            alert(`Error: ${errorData.detail || 'Error al generar el panel'}`);
        }
    } catch (error) {
        console.error('Error:', error);
        alert(`Error: ${error.message}. Verifica que el backend esté disponible en ${API_BASE}`);
    } finally {
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    }
}

// ==================== UTILITIES ====================

function scrollToForm() {
    document.querySelector('.form-section').scrollIntoView({ behavior: 'smooth' });
}
