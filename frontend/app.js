// ==================== HBC3 FRONTEND FIX ====================
// Fixes:
// - dynamic backend URL resolution for Codespaces/local deployments
// - supports localStorage API_BASE/api_url overrides
// - never sends Authorization: Bearer null
// - sends integrations with string values compatible with backend/api.py Pydantic schema

let currentStep = 1;
const totalSteps = 4;

const formData = {
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

let authState = {
    token: localStorage.getItem('token') || '',
    user: safeJsonParse(localStorage.getItem('user')) || null
};

function normalizeApiOrigin(value) {
    if (!value) return '';
    return String(value).trim().replace(/\/$/, '').replace(/\/api\/v1\/?$/, '');
}

function resolveApiOrigin() {
    const explicit = normalizeApiOrigin(
        localStorage.getItem('API_BASE') ||
        localStorage.getItem('api_url') ||
        window.HBC3_API_BASE ||
        window.HBC3_API_ORIGIN
    );
    if (explicit) return explicit;

    const { protocol, hostname, origin } = window.location;

    if (hostname === 'localhost' || hostname === '127.0.0.1') {
        return 'http://localhost:8000';
    }

    if (hostname.includes('github.dev') || hostname.includes('app.github.dev')) {
        return origin.replace(/-3000\./, '-8000.').replace(/:3000$/, ':8000');
    }

    if (window.location.port === '3000') {
        return `${protocol}//${hostname}:8000`;
    }

    return origin;
}

const API_ORIGIN = resolveApiOrigin();
const API_BASE = `${API_ORIGIN}/api/v1`;

console.log('HBC3 API ORIGIN:', API_ORIGIN);
console.log('HBC3 API BASE:', API_BASE);

document.addEventListener('DOMContentLoaded', () => {
    initializeForm();
    setupEventListeners();
    setupAuthUi();
    updateAuthUi();
    updatePreview();
});

function initializeForm() {
    showStep(1);

    document.querySelectorAll('.theme-option').forEach(option => {
        option.addEventListener('click', () => {
            document.querySelectorAll('.theme-option').forEach(o => o.classList.remove('selected'));
            option.classList.add('selected');
            formData.theme = option.dataset.theme || 'doctor_piscinas';
            updateThemeColors(formData.theme);
            updatePreview();
        });
    });

    const defaultTheme = document.querySelector('[data-theme="doctor_piscinas"]');
    if (defaultTheme) defaultTheme.classList.add('selected');
}

function setupEventListeners() {
    const serviceInput = document.getElementById('serviceInput');
    if (serviceInput) {
        serviceInput.addEventListener('keypress', (event) => {
            if (event.key === 'Enter') {
                event.preventDefault();
                addService(serviceInput.value);
                serviceInput.value = '';
            }
        });
    }

    document.querySelectorAll('input[name="installMethod"]').forEach(radio => {
        radio.addEventListener('change', (event) => {
            formData.installMethod = event.target.value;
            updateInstallationFields();
            updatePreview();
        });
    });

    document.querySelectorAll('input[name="colorPrimary"], input[name="colorSecondary"]').forEach(input => {
        input.addEventListener('change', (event) => {
            formData[event.target.name] = event.target.value;
            updatePreview();
        });
    });

    document.querySelectorAll('input[name="effects"], input[name="integrations"]').forEach(input => {
        input.addEventListener('change', () => {
            updateFormData(false);
            updatePreview();
        });
    });

    const form = document.getElementById('panelForm');
    if (form) {
        form.addEventListener('input', debounce(() => {
            updateFormData(false);
            updatePreview();
        }, 150));

        form.addEventListener('submit', (event) => {
            event.preventDefault();
            submitForm();
        });
    }
}

function setupAuthUi() {
    const loginBtn = document.querySelector('.btn-login');
    if (loginBtn) {
        loginBtn.type = 'button';
        loginBtn.addEventListener('click', openAuthModal);
    }

    if (document.getElementById('authModal')) return;

    const modal = document.createElement('div');
    modal.id = 'authModal';
    modal.className = 'hbc3-auth-modal hidden';
    modal.innerHTML = `
        <div class="hbc3-auth-card">
            <button type="button" class="hbc3-auth-close" onclick="closeAuthModal()">×</button>
            <h3>Acceso HBC3</h3>
            <p>Inicia sesión para guardar el panel en backend. Sin acceso, la pantalla se genera localmente.</p>
            <label>Email</label>
            <input id="authEmail" type="email" placeholder="correo@empresa.com" autocomplete="email">
            <label>Contraseña</label>
            <input id="authPassword" type="password" placeholder="Contraseña" autocomplete="current-password">
            <div class="hbc3-auth-actions">
                <button type="button" class="btn btn-primary" onclick="loginUser()">Entrar</button>
                <button type="button" class="btn btn-secondary" onclick="logoutUser()">Salir</button>
            </div>
            <div id="authStatus" class="hbc3-auth-status"></div>
        </div>
    `;
    document.body.appendChild(modal);

    const style = document.createElement('style');
    style.textContent = `
        .hidden{display:none!important;}
        .hbc3-auth-modal{position:fixed;inset:0;z-index:9999;background:rgba(0,0,0,.65);display:flex;align-items:center;justify-content:center;padding:20px;}
        .hbc3-auth-card{width:100%;max-width:420px;background:#fff;border-radius:18px;padding:24px;box-shadow:0 24px 80px rgba(0,0,0,.35);position:relative;}
        .hbc3-auth-card h3{margin-bottom:10px;}
        .hbc3-auth-card p{margin-bottom:18px;color:#555;}
        .hbc3-auth-card label{display:block;margin:12px 0 6px;font-weight:700;}
        .hbc3-auth-card input{width:100%;padding:12px;border:1px solid #ddd;border-radius:10px;}
        .hbc3-auth-close{position:absolute;top:12px;right:14px;border:none;background:transparent;font-size:28px;cursor:pointer;}
        .hbc3-auth-actions{display:flex;gap:10px;margin-top:18px;}
        .hbc3-auth-status{margin-top:12px;font-size:13px;color:#555;}
    `;
    document.head.appendChild(style);
}

function openAuthModal() {
    document.getElementById('authModal')?.classList.remove('hidden');
}

function closeAuthModal() {
    document.getElementById('authModal')?.classList.add('hidden');
}

async function loginUser() {
    const email = document.getElementById('authEmail')?.value?.trim();
    const password = document.getElementById('authPassword')?.value || '';
    const status = document.getElementById('authStatus');

    if (!email || !password) {
        if (status) status.textContent = 'Completa email y contraseña.';
        return;
    }

    try {
        if (status) status.textContent = 'Conectando...';
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        const data = await safeJson(response);
        if (!response.ok || !data?.access_token) {
            throw new Error(data?.detail || 'No se pudo iniciar sesión');
        }

        authState.token = data.access_token;
        authState.user = data.user || null;
        localStorage.setItem('token', authState.token);
        localStorage.setItem('user', JSON.stringify(authState.user));
        updateAuthUi();
        closeAuthModal();
        showNotice('Sesión iniciada. Ahora el panel se guardará en backend.', 'success');
    } catch (error) {
        if (status) status.textContent = `Error: ${error.message}`;
    }
}

function logoutUser() {
    authState.token = '';
    authState.user = null;
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    updateAuthUi();
    showNotice('Sesión cerrada. Se usará generación local de pantalla.', 'info');
}

function updateAuthUi() {
    const loginBtn = document.querySelector('.btn-login');
    if (!loginBtn) return;
    loginBtn.textContent = authState.token ? 'Sesión activa' : 'Iniciar Sesión';
    loginBtn.classList.toggle('is-authenticated', Boolean(authState.token));
}

function showStep(step) {
    document.querySelectorAll('.form-step').forEach(item => item.classList.remove('active'));
    document.querySelector(`[data-step="${step}"]`)?.classList.add('active');

    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const submitBtn = document.getElementById('submitBtn');

    if (prevBtn) prevBtn.style.display = step === 1 ? 'none' : 'block';
    if (nextBtn) nextBtn.style.display = step === totalSteps ? 'none' : 'block';
    if (submitBtn) submitBtn.style.display = step === totalSteps ? 'block' : 'none';

    currentStep = step;
    updateFormData(false);
}

function nextStep() {
    if (validateStep(currentStep) && currentStep < totalSteps) showStep(currentStep + 1);
}

function previousStep() {
    if (currentStep > 1) showStep(currentStep - 1);
}

function validateStep(step) {
    const form = document.getElementById('panelForm');
    if (!form) return true;

    const inputs = form.querySelectorAll(`[data-step="${step}"] input[required], [data-step="${step}"] textarea[required]`);
    for (const input of inputs) {
        if (!input.value.trim()) {
            input.focus();
            input.style.borderColor = '#ff0000';
            setTimeout(() => { input.style.borderColor = ''; }, 2000);
            return false;
        }
    }
    return true;
}

function updateFormData(refreshPreview = true) {
    const form = document.getElementById('panelForm');
    if (!form) return;

    formData.businessName = form.querySelector('input[name="businessName"]')?.value || '';
    formData.description = form.querySelector('textarea[name="description"]')?.value || '';
    formData.phone = form.querySelector('input[name="phone"]')?.value || '';
    formData.email = form.querySelector('input[name="email"]')?.value || '';
    formData.website = form.querySelector('input[name="website"]')?.value || '';
    formData.colorPrimary = form.querySelector('input[name="colorPrimary"]')?.value || '#ff006e';
    formData.colorSecondary = form.querySelector('input[name="colorSecondary"]')?.value || '#00d9ff';
    formData.effects = Array.from(form.querySelectorAll('input[name="effects"]:checked')).map(item => item.value);
    formData.integrations = Array.from(form.querySelectorAll('input[name="integrations"]:checked')).map(item => item.value);
    formData.whatsapp = form.querySelector('input[name="whatsapp"]')?.value || '';
    formData.social = {
        facebook: form.querySelector('input[name="facebook"]')?.value || '',
        instagram: form.querySelector('input[name="instagram"]')?.value || '',
        twitter: form.querySelector('input[name="twitter"]')?.value || '',
        linkedin: form.querySelector('input[name="linkedin"]')?.value || ''
    };
    formData.installMethod = form.querySelector('input[name="installMethod"]:checked')?.value || 'zip';

    if (refreshPreview) updatePreview();
}

function addService(service) {
    const clean = String(service || '').trim();
    if (!clean) return;
    formData.services.push(clean);
    renderServices();
    updatePreview();
}

function removeService(index) {
    formData.services.splice(index, 1);
    renderServices();
    updatePreview();
}

function renderServices() {
    const list = document.getElementById('servicesList');
    if (!list) return;
    list.innerHTML = formData.services.map((service, index) => `
        <div class="service-tag">
            ${escapeHtml(service)}
            <button type="button" onclick="removeService(${index})">×</button>
        </div>
    `).join('');
}

function updateInstallationFields() {
    const ftpFields = document.getElementById('ftpFields');
    const apiFields = document.getElementById('apiFields');
    if (ftpFields) ftpFields.classList.add('hidden');
    if (apiFields) apiFields.classList.add('hidden');
    if (formData.installMethod === 'ftp') ftpFields?.classList.remove('hidden');
    if (['api', 'oauth'].includes(formData.installMethod)) apiFields?.classList.remove('hidden');
}

function updateThemeColors(theme) {
    const colors = getThemeColors(theme);
    formData.colorPrimary = colors.primary;
    formData.colorSecondary = colors.secondary;
    const primaryInput = document.querySelector('input[name="colorPrimary"]');
    const secondaryInput = document.querySelector('input[name="colorSecondary"]');
    if (primaryInput) primaryInput.value = colors.primary;
    if (secondaryInput) secondaryInput.value = colors.secondary;
}

function updatePreview() {
    const previewFrame = document.getElementById('previewFrame');
    if (!previewFrame) return;
    previewFrame.srcdoc = generatePreviewHTML();
}

function generatePreviewHTML() {
    const themeColors = getThemeColors(formData.theme);
    const services = formData.services.length ? formData.services : ['Servicio principal', 'Presupuesto rápido', 'Contacto directo', 'Panel privado'];
    const primaryRgb = hexToRgb(themeColors.primary).join(',');
    const secondaryRgb = hexToRgb(themeColors.secondary).join(',');
    const title = escapeHtml(formData.businessName || 'Tu Negocio');
    const description = escapeHtml(formData.description || 'Pantalla premium generada por HBC3');
    const phone = escapeHtml(formData.phone || formData.whatsapp || '+34 XXX XXX XXX');

    return `<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${title}</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        body{font-family:Inter,Arial,sans-serif;min-height:100vh;background:radial-gradient(circle at 20% 20%,rgba(${primaryRgb},.35),transparent 28%),radial-gradient(circle at 90% 10%,rgba(${secondaryRgb},.28),transparent 30%),linear-gradient(135deg,#071018,#101827 55%,#02040a);color:#fff;display:flex;align-items:center;justify-content:center;padding:22px;overflow:hidden}
        .water{position:fixed;inset:auto -10% -25% -10%;height:45vh;background:linear-gradient(180deg,rgba(${secondaryRgb},.02),rgba(${secondaryRgb},.22));filter:blur(1px);animation:wave 7s ease-in-out infinite alternate;border-radius:50% 50% 0 0}
        .panel{position:relative;width:min(560px,100%);padding:34px;border-radius:28px;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.20);box-shadow:0 24px 90px rgba(0,0,0,.45),0 0 60px rgba(${primaryRgb},.18);backdrop-filter:blur(18px);overflow:hidden}
        .badge{display:inline-flex;gap:8px;align-items:center;padding:8px 12px;border-radius:999px;background:rgba(${primaryRgb},.15);border:1px solid rgba(${primaryRgb},.45);font-size:12px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;margin-bottom:18px}
        .title{font-size:clamp(30px,7vw,48px);line-height:1;font-weight:900;letter-spacing:-.04em;background:linear-gradient(135deg,#fff,${themeColors.secondary});-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:14px}
        .desc{font-size:15px;line-height:1.55;color:rgba(255,255,255,.78);margin-bottom:24px}
        .services{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:24px 0}
        .service{padding:14px 12px;border-radius:16px;background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.14);font-weight:800;font-size:13px;text-align:center}
        .actions{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:24px}
        .btn{border:none;border-radius:16px;padding:15px 14px;font-weight:900;cursor:pointer;font-size:14px;text-decoration:none;text-align:center;color:#fff}
        .btn-primary{background:linear-gradient(135deg,${themeColors.primary},${themeColors.secondary});box-shadow:0 12px 30px rgba(${primaryRgb},.35)}
        .btn-secondary{background:rgba(255,255,255,.08);border:1px solid rgba(${secondaryRgb},.55);color:${themeColors.secondary}}
        .status{margin-top:20px;color:#6aff9d;font-size:12px;font-weight:800;display:flex;gap:8px;align-items:center;justify-content:center}
        @keyframes wave{from{transform:translateY(0) rotate(-1deg)}to{transform:translateY(-18px) rotate(1deg)}}
        @media(max-width:480px){.panel{padding:24px}.services,.actions{grid-template-columns:1fr}.title{font-size:34px}}
    </style>
</head>
<body>
    <div class="water"></div>
    <main class="panel">
        <div class="badge">HBC3 · Pantalla activa</div>
        <h1 class="title">${title}</h1>
        <p class="desc">${description}</p>
        <section class="services">
            ${services.slice(0, 4).map(s => `<div class="service">${escapeHtml(s)}</div>`).join('')}
        </section>
        <div class="actions">
            <a class="btn btn-primary" href="mailto:${encodeURIComponent(formData.email || '')}">Presupuesto</a>
            <a class="btn btn-secondary" href="https://wa.me/${normalizePhone(formData.whatsapp || formData.phone)}" target="_blank" rel="noopener">WhatsApp</a>
        </div>
        <div class="status">Sistema Online · ${phone}</div>
    </main>
</body>
</html>`;
}

function getThemeColors(theme) {
    const colors = {
        doctor_piscinas: { primary: '#ff006e', secondary: '#00d9ff' },
        tech_future: { primary: '#00d9ff', secondary: '#a000ff' },
        luxury_gold: { primary: '#ffd700', secondary: '#1a1a1a' },
        nature_green: { primary: '#00aa44', secondary: '#8b7355' },
        gaming_neon: { primary: '#ff00ff', secondary: '#00ffff' }
    };
    return colors[theme] || colors.doctor_piscinas;
}

function hexToRgb(hex) {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex || '');
    return result ? [parseInt(result[1], 16), parseInt(result[2], 16), parseInt(result[3], 16)] : [0, 0, 0];
}

async function submitForm() {
    updateFormData(false);

    if (!formData.businessName || !formData.email) {
        showNotice('Completa nombre del negocio y email.', 'error');
        return;
    }

    const submitBtn = document.getElementById('submitBtn');
    const originalText = submitBtn?.textContent || 'Generar Panel';
    if (submitBtn) {
        submitBtn.textContent = 'Generando...';
        submitBtn.disabled = true;
    }

    try {
        if (!authState.token) {
            const localPanel = createLocalPanel();
            showNotice('Pantalla generada en modo local. Inicia sesión para guardarla en backend.', 'success');
            openGeneratedPanel(localPanel.html);
            return;
        }

        const response = await fetch(`${API_BASE}/panels`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authState.token}`
            },
            body: JSON.stringify(buildBackendPayload())
        });

        const data = await safeJson(response);
        if (!response.ok) {
            if (response.status === 401 || response.status === 403) {
                logoutUser();
                const localPanel = createLocalPanel();
                showNotice('Sesión caducada. Pantalla generada en modo local.', 'error');
                openGeneratedPanel(localPanel.html);
                return;
            }
            throw new Error(data?.detail || 'Error al generar el panel');
        }

        showNotice('Panel guardado en backend correctamente.', 'success');
        if (data?.id) window.location.href = `/dashboard?id=${encodeURIComponent(data.id)}`;
    } catch (error) {
        console.error('HBC3 generation error:', error);
        const localPanel = createLocalPanel();
        showNotice('Backend no disponible. Pantalla generada localmente.', 'error');
        openGeneratedPanel(localPanel.html);
    } finally {
        if (submitBtn) {
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        }
    }
}

function buildBackendPayload() {
    return {
        name: formData.businessName,
        description: formData.description,
        business_name: formData.businessName,
        business_phone: formData.phone,
        business_email: formData.email,
        business_website: formData.website || null,
        logo_url: null,
        theme: formData.theme,
        colors: {
            primary: formData.colorPrimary,
            secondary: formData.colorSecondary
        },
        services: formData.services.map(name => ({ name })),
        social_links: cleanStringMap(formData.social),
        integrations: buildIntegrationsPayload()
    };
}

function buildIntegrationsPayload() {
    const integrations = {};
    formData.integrations.forEach(name => {
        integrations[name] = { enabled: 'true' };
    });
    if (formData.whatsapp) {
        integrations.whatsapp = {
            ...(integrations.whatsapp || {}),
            enabled: 'true',
            phone: String(formData.whatsapp)
        };
    }
    if (formData.email) {
        integrations.email = {
            ...(integrations.email || {}),
            enabled: integrations.email?.enabled || 'true',
            address: String(formData.email)
        };
    }
    return integrations;
}

function cleanStringMap(value) {
    return Object.fromEntries(
        Object.entries(value || {})
            .filter(([, item]) => item !== null && item !== undefined && String(item).trim() !== '')
            .map(([key, item]) => [key, String(item)])
    );
}

function createLocalPanel() {
    const html = generatePreviewHTML();
    const id = `local-${Date.now()}`;
    localStorage.setItem(`panel-${id}`, JSON.stringify({ id, createdAt: new Date().toISOString(), data: formData, html }));
    return { id, html };
}

function openGeneratedPanel(html) {
    const blob = new Blob([html], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    window.open(url, '_blank', 'noopener');
    setTimeout(() => URL.revokeObjectURL(url), 30000);
}

function scrollToForm() {
    document.querySelector('.form-section')?.scrollIntoView({ behavior: 'smooth' });
}

function safeJsonParse(value) {
    try { return value ? JSON.parse(value) : null; } catch { return null; }
}

async function safeJson(response) {
    try { return await response.json(); } catch { return null; }
}

function escapeHtml(value) {
    return String(value ?? '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

function normalizePhone(phone) {
    const clean = String(phone || '').replace(/[^0-9]/g, '');
    return clean || '34000000000';
}

function debounce(fn, wait) {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => fn(...args), wait);
    };
}

function showNotice(message, type = 'info') {
    let notice = document.getElementById('hbc3Notice');
    if (!notice) {
        notice = document.createElement('div');
        notice.id = 'hbc3Notice';
        notice.style.cssText = 'position:fixed;left:50%;bottom:22px;transform:translateX(-50%);z-index:10000;max-width:92vw;padding:14px 18px;border-radius:14px;color:#fff;font-weight:800;box-shadow:0 14px 40px rgba(0,0,0,.25);transition:.25s;';
        document.body.appendChild(notice);
    }
    const colors = { success: '#00aa44', error: '#d93025', info: '#2563eb' };
    notice.style.background = colors[type] || colors.info;
    notice.textContent = message;
    notice.style.opacity = '1';
    setTimeout(() => { notice.style.opacity = '0'; }, 4500);
}

window.nextStep = nextStep;
window.previousStep = previousStep;
window.removeService = removeService;
window.scrollToForm = scrollToForm;
window.loginUser = loginUser;
window.logoutUser = logoutUser;
window.closeAuthModal = closeAuthModal;
