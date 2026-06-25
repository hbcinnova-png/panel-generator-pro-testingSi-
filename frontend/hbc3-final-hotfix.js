// HBC3 FINAL PREMIUM HOTFIX
// Convierte la vista generada en un panel premium real Doctor Piscinas / Panteras.
// Mantiene el Generador v4 y reemplaza solo el resultado generado + acciones.
(function () {
  const STORAGE_KEY = 'hbc3_saved_records';

  function esc(value) {
    return String(value || '').replace(/[&<>"']/g, function (char) {
      return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char];
    });
  }

  function rawData() {
    if (typeof updateFormData === 'function') updateFormData(true);
    const fd = window.formData || {};
    const services = Array.isArray(fd.services) && fd.services.length
      ? fd.services
      : ['Reparación', 'Alquiler', 'Diagnóstico IA', 'Gestión'];
    return {
      name: fd.businessName || 'Doctor Piscinas',
      title: fd.businessName || 'Reparación Piscinas Poliéster',
      description: fd.description || 'Control total, clientes felices, piscinas perfectas.',
      phone: fd.phone || fd.whatsapp || '600000000',
      email: fd.email || 'contacto@empresa.com',
      whatsapp: fd.whatsapp || fd.phone || '600000000',
      services,
      primary: fd.colorPrimary || '#ff2b91',
      secondary: fd.colorSecondary || '#00d9ff',
      theme: fd.theme || 'doctor_piscinas_premium_panteras'
    };
  }

  function digits(value) {
    const n = String(value || '').replace(/\D/g, '');
    if (n.length === 9) return '34' + n;
    return n || '34600000000';
  }

  function premiumPanelHtml() {
    const d = rawData();
    const business = esc(d.name);
    const title = esc(d.title);
    const description = esc(d.description);
    const phone = esc(d.phone);
    const email = esc(d.email);
    const wa = digits(d.whatsapp || d.phone);
    const serviceCards = d.services.slice(0, 4).map(function (service, index) {
      const icons = ['🔧','🏊','⚡','📊'];
      const subtitles = ['Soluciones profesionales', 'Piscinas y climatización', 'Análisis inteligente', 'Control total'];
      return `<article class="svc-card"><span>${icons[index] || '✨'}</span><b>${esc(service)}</b><small>${subtitles[index] || 'Servicio premium'}</small></article>`;
    }).join('');

    return `<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>${title}</title>
<style>
:root{--pink:${esc(d.primary)};--cyan:${esc(d.secondary)};--green:#16ff8f;--gold:#ffd166;--bg:#050817;--glass:rgba(12,22,42,.72);--line:rgba(255,255,255,.16)}
*{box-sizing:border-box}body{margin:0;min-height:100vh;color:#fff;font-family:Inter,Arial,sans-serif;background:radial-gradient(circle at 20% 15%,rgba(255,43,145,.28),transparent 25%),radial-gradient(circle at 80% 15%,rgba(0,217,255,.22),transparent 28%),linear-gradient(135deg,#030516,#071c33 60%,#020612);overflow-x:hidden}.stage{position:relative;min-height:100vh;padding:22px 26px 26px}.pool{position:absolute;inset:auto 0 0;height:45%;background:radial-gradient(ellipse at center,rgba(0,217,255,.3),transparent 58%);filter:blur(2px);opacity:.9}.topbar{position:relative;z-index:2;display:grid;grid-template-columns:1fr auto 1fr;gap:16px;align-items:center;margin-bottom:26px}.brand,.status,.premium,.menu{border:1px solid var(--line);background:rgba(8,16,33,.76);box-shadow:0 0 28px rgba(0,217,255,.14);backdrop-filter:blur(16px);border-radius:24px;padding:14px 18px}.brand{display:flex;gap:12px;align-items:center;font-weight:900}.brand .paw{width:38px;height:38px;border-radius:50%;display:grid;place-items:center;background:linear-gradient(135deg,var(--pink),var(--cyan));box-shadow:0 0 24px var(--pink)}.status{display:flex;gap:18px;align-items:center;min-width:330px;justify-content:center}.dot{width:12px;height:12px;border-radius:50%;background:var(--green);box-shadow:0 0 18px var(--green)}.premium{justify-self:end;color:var(--gold);font-weight:900}.menu{justify-self:end;width:58px;height:58px;display:grid;place-items:center;font-size:30px}.layout{position:relative;z-index:2;display:grid;grid-template-columns:150px 1fr;gap:22px;max-width:1500px;margin:0 auto}.sidebar{border:1px solid var(--line);background:rgba(6,13,28,.72);border-radius:26px;padding:16px 12px;height:max-content;box-shadow:0 0 30px rgba(255,43,145,.18)}.navbtn{display:flex;gap:10px;align-items:center;width:100%;margin:8px 0;padding:12px;border-radius:16px;background:transparent;border:1px solid transparent;color:#dce7ff;text-align:left;font-weight:800}.navbtn.active,.navbtn:hover{border-color:rgba(255,43,145,.7);background:linear-gradient(135deg,rgba(255,43,145,.38),rgba(0,217,255,.12));box-shadow:0 0 22px rgba(255,43,145,.25)}.hero{position:relative;min-height:520px;border:1px solid var(--line);border-radius:40px;padding:34px 42px;background:linear-gradient(135deg,rgba(96,18,67,.74),rgba(7,52,68,.78));box-shadow:0 25px 90px rgba(0,0,0,.45);overflow:hidden}.hero:before{content:"";position:absolute;inset:60px 15% auto 15%;height:330px;border:3px solid rgba(0,217,255,.72);border-left-color:rgba(255,43,145,.72);border-radius:50% 50% 45% 45%;box-shadow:0 0 44px rgba(0,217,255,.35),inset 0 0 48px rgba(255,43,145,.15);transform:skewX(-14deg)}.mascot{position:absolute;top:74px;width:170px;height:310px;border-radius:90px 90px 40px 40px;display:flex;align-items:center;justify-content:center;font-size:96px;filter:drop-shadow(0 0 25px currentColor);background:linear-gradient(180deg,rgba(255,255,255,.15),rgba(255,255,255,.02));border:1px solid rgba(255,255,255,.18)}.mascot.left{left:42px;color:var(--pink)}.mascot.right{right:42px;color:var(--cyan)}.mascot small{position:absolute;bottom:32px;font-size:14px;font-weight:900;color:#fff;background:rgba(0,0,0,.28);padding:8px 10px;border-radius:999px}.center{position:relative;z-index:1;text-align:center;max-width:720px;margin:0 auto}.crown{color:var(--gold);font-weight:900;letter-spacing:.18em}.title{font-size:clamp(42px,7vw,78px);line-height:.96;margin:16px 0 12px;font-weight:1000;text-shadow:0 0 30px rgba(0,217,255,.25)}.title span{display:block;background:linear-gradient(135deg,#fff,var(--pink),var(--cyan));-webkit-background-clip:text;background-clip:text;color:transparent}.subtitle{font-size:22px;color:#eef6ff}.actions{display:grid;grid-template-columns:repeat(4,1fr);gap:18px;margin:36px auto 0;max-width:830px}.action{display:grid;gap:5px;place-items:center;min-height:120px;border-radius:24px;text-decoration:none;color:#fff;font-weight:900;border:1px solid rgba(255,255,255,.18);background:rgba(255,255,255,.08);box-shadow:0 0 28px rgba(0,0,0,.25);cursor:pointer}.action i{font-size:34px;font-style:normal}.action small{font-weight:700;opacity:.86}.action.primary{background:linear-gradient(135deg,var(--pink),var(--cyan));box-shadow:0 0 36px rgba(255,43,145,.35)}.action.wa{box-shadow:0 0 32px rgba(22,255,143,.25);border-color:rgba(22,255,143,.45)}.action.call{box-shadow:0 0 32px rgba(0,217,255,.25);border-color:rgba(0,217,255,.45)}.action.mail{box-shadow:0 0 32px rgba(179,80,255,.28);border-color:rgba(179,80,255,.45)}.cards{display:grid;grid-template-columns:1.1fr 1fr 1.1fr .9fr;gap:16px;margin-top:18px}.card,.svc-card,.assistant,.promo{border:1px solid var(--line);border-radius:24px;background:rgba(9,19,40,.72);box-shadow:0 0 30px rgba(0,217,255,.09);padding:18px}.svc-row{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-top:16px}.svc-card{display:grid;place-items:center;text-align:center;min-height:100px}.svc-card span{font-size:28px}.svc-card b{color:#dffbff}.svc-card small{color:#b9c7d9}.metric{font-size:34px;font-weight:1000}.green{color:var(--green)}.chart{height:88px;margin-top:12px;background:linear-gradient(135deg,transparent,rgba(255,43,145,.15));border-radius:18px;position:relative}.chart:after{content:"";position:absolute;inset:20px 16px;background:linear-gradient(140deg,transparent 10%,var(--pink) 11%,transparent 13%,transparent 35%,var(--cyan) 36%,transparent 38%,transparent 62%,var(--pink) 63%,transparent 65%)}.tasks li{display:flex;justify-content:space-between;gap:10px;margin:9px 0;padding:8px;border-radius:12px;background:rgba(255,255,255,.06);list-style:none}.tasks ul{padding:0;margin:8px 0 0}.tag{font-size:12px;color:var(--green);border:1px solid rgba(22,255,143,.35);border-radius:999px;padding:3px 8px}.assistant{text-align:center}.robot{font-size:52px}.ask{display:inline-block;margin-top:14px;background:linear-gradient(135deg,var(--pink),#b14cff);padding:12px 22px;border-radius:999px;color:#fff;text-decoration:none;font-weight:900}.footer{position:relative;z-index:2;margin:18px auto 0;max-width:1500px;display:grid;grid-template-columns:1fr repeat(4,auto);gap:16px;align-items:center;border:1px solid var(--line);border-radius:22px;padding:14px 18px;background:rgba(7,17,35,.82)}.ok{color:var(--green);font-weight:900}.toast{position:fixed;left:50%;bottom:22px;transform:translateX(-50%);background:rgba(8,16,33,.94);border:1px solid var(--line);padding:13px 18px;border-radius:999px;box-shadow:0 0 35px rgba(0,217,255,.22);z-index:50;display:none}.toast.show{display:block}.budget-modal{position:fixed;inset:0;background:rgba(0,0,0,.68);display:none;align-items:center;justify-content:center;z-index:60;padding:20px}.budget-card{max-width:520px;width:100%;border:1px solid var(--line);border-radius:28px;background:#0b1428;padding:24px;box-shadow:0 0 45px rgba(255,43,145,.2)}.budget-card input,.budget-card textarea{width:100%;margin:8px 0 12px;border-radius:14px;border:1px solid var(--line);background:#050b17;color:#fff;padding:12px}.budget-card button{border:0;border-radius:14px;padding:12px 16px;margin-right:8px;color:#fff;font-weight:900;background:linear-gradient(135deg,var(--pink),var(--cyan))}@media(max-width:950px){.stage{padding:18px 12px}.topbar{grid-template-columns:1fr}.premium,.menu{justify-self:stretch}.layout{grid-template-columns:1fr}.sidebar{display:grid;grid-template-columns:repeat(3,1fr);gap:6px}.navbtn{font-size:12px}.hero{padding:26px 18px}.hero:before{inset:88px 6% auto 6%;height:260px}.mascot{display:none}.actions{grid-template-columns:1fr 1fr;gap:12px}.svc-row,.cards{grid-template-columns:1fr}.footer{grid-template-columns:1fr 1fr}.status{min-width:0}}
</style>
</head>
<body>
<div class="stage">
  <div class="pool"></div>
  <header class="topbar">
    <div class="brand"><span class="paw">🐾</span><span>${business}</span></div>
    <div class="status"><span>🕒 ${new Date().toLocaleDateString('es-ES')}</span><span class="dot"></span><span><b>Sistema Online</b><br><small>Todos los servicios activos</small></span></div>
    <div class="premium">👑 Plan PREMIUM</div>
  </header>
  <main class="layout">
    <nav class="sidebar">
      <button class="navbtn active" onclick="hbcTab('Inicio')">🏠 Inicio</button><button class="navbtn" onclick="hbcTab('Clientes')">👥 Clientes</button><button class="navbtn" onclick="hbcTab('Servicios')">🛠️ Servicios</button><button class="navbtn" onclick="hbcTab('Presupuestos')">📄 Presupuestos</button><button class="navbtn" onclick="hbcTab('Citas')">📅 Citas</button><button class="navbtn" onclick="hbcTab('Marketing')">📣 Marketing</button><button class="navbtn" onclick="hbcTab('Reportes')">📊 Reportes</button><button class="navbtn" onclick="hbcTab('Facturación')">⚙️ Facturación</button>
    </nav>
    <section>
      <section class="hero">
        <div class="mascot left">🐆<small>Pantera Rosa</small></div><div class="mascot right">🐆<small>Pantera Turquesa</small></div>
        <div class="center"><div class="crown">👑 PREMIUM</div><h1 class="title"><span>${title}</span></h1><p class="subtitle">${description}</p>
          <div class="actions">
            <button class="action primary" onclick="openBudget()"><i>📄</i>Presupuesto<small>Registro real</small></button>
            <a class="action wa" href="https://wa.me/${wa}" target="_blank" rel="noopener"><i>🟢</i>WhatsApp<small>Chatea ahora</small></a>
            <a class="action call" href="tel:${phone}"><i>📞</i>Llamar<small>Contacto directo</small></a>
            <a class="action mail" href="mailto:${email}?subject=Solicitud%20de%20presupuesto%20${encodeURIComponent(d.name)}"><i>✉️</i>Email<small>Escríbenos</small></a>
          </div>
        </div>
      </section>
      <div class="svc-row">${serviceCards}</div>
      <section class="cards">
        <article class="card"><b>Clientes Activos</b><div class="metric">1.248 <small class="green">+12%</small></div><div class="chart"></div></article>
        <article class="card"><b>Servicios Hoy</b><div class="metric">23</div><div class="tasks"><ul><li>Mantenimiento <span class="tag">En progreso</span></li><li>Limpieza Profunda <span class="tag">En progreso</span></li><li>Reparación Filtro <span class="tag">Programado</span></li></ul></div></article>
        <article class="card"><b>Ingresos del mes</b><div class="metric">24.680€ <small class="green">+18%</small></div><div class="chart"></div></article>
        <article class="assistant"><div class="robot">🤖</div><b>Asistente IA</b><p><span class="dot"></span> Online</p><a class="ask" href="mailto:${email}?subject=Consulta%20IA%20Doctor%20Piscinas">¡Pregúntame!</a></article>
      </section>
    </section>
  </main>
  <footer class="footer"><span class="ok">✅ Estado general del sistema</span><span>🔧 23 servicios</span><span>📅 5 citas</span><span>📄 3 pendientes</span><span>⚠️ 0 incidencias</span></footer>
</div>
<div class="budget-modal" id="budgetModal"><div class="budget-card"><h2>Presupuesto ${business}</h2><p>Solicitud guardable en backend y preparada para contacto.</p><input id="clientName" placeholder="Nombre del cliente"><input id="clientPhone" placeholder="Teléfono"><textarea id="clientMsg" placeholder="Describe la piscina o reparación"></textarea><button onclick="sendBudget()">Guardar presupuesto</button><button onclick="closeBudget()" style="background:#26344d">Cerrar</button></div></div><div class="toast" id="toast">Acción ejecutada</div>
<script>
const panelData={name:${JSON.stringify(d.name)},phone:${JSON.stringify(d.phone)},email:${JSON.stringify(d.email)},whatsapp:${JSON.stringify(d.whatsapp)},services:${JSON.stringify(d.services)}};
function toast(msg){const t=document.getElementById('toast');t.textContent=msg;t.classList.add('show');setTimeout(()=>t.classList.remove('show'),2600)}
function hbcTab(name){toast('Abriendo '+name+' · módulo activo')}
function openBudget(){document.getElementById('budgetModal').style.display='flex'}
function closeBudget(){document.getElementById('budgetModal').style.display='none'}
async function sendBudget(){const payload={type:'budget-request',name:panelData.name,phone:document.getElementById('clientPhone').value||panelData.phone,email:panelData.email,description:document.getElementById('clientMsg').value||'Solicitud de presupuesto desde panel premium',services:(panelData.services||[]).join('\\n'),html:document.documentElement.outerHTML,plan:'premium'};try{const r=await fetch('/generator/save',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});const j=await r.json();if(!r.ok)throw new Error(JSON.stringify(j));toast('Presupuesto guardado: '+j.id);closeBudget()}catch(e){toast('No se pudo guardar. Abriendo email.');location.href='mailto:'+panelData.email+'?subject=Solicitud de presupuesto&body='+encodeURIComponent(payload.description)}}
</script>
</body>
</html>`;
  }

  function installPremiumPreview() {
    window.generatePreviewHTML = premiumPanelHtml;
    window.hbc3PremiumPanelHtml = premiumPanelHtml;
  }

  function setPreviewPremium() {
    installPremiumPreview();
    const frame = document.getElementById('previewFrame');
    if (frame) frame.srcdoc = premiumPanelHtml();
  }

  const originalFetch = window.fetch.bind(window);
  window.fetch = function (url, options) {
    if (String(url).endsWith('/generator/save') && options && options.body) {
      try {
        const body = JSON.parse(options.body);
        body.html = premiumPanelHtml();
        body.type = body.type || 'generated-premium';
        body.plan = body.plan || 'premium';
        options = Object.assign({}, options, {body: JSON.stringify(body)});
      } catch (_) {}
    }
    return originalFetch(url, options);
  };

  function wrapAction(name) {
    const original = window[name];
    if (typeof original !== 'function') return;
    window[name] = async function () {
      setPreviewPremium();
      const result = await original.apply(this, arguments);
      setTimeout(setPreviewPremium, 80);
      return result;
    };
  }

  function injectPremiumThemeOption() {
    const selector = document.querySelector('.theme-selector');
    if (!selector || document.querySelector('[data-theme="doctor_piscinas_premium_panteras"]')) return;
    const option = document.createElement('div');
    option.className = 'theme-option selected';
    option.dataset.theme = 'doctor_piscinas_premium_panteras';
    option.innerHTML = '<div class="theme-preview" style="background:linear-gradient(135deg,#ff2b91,#00d9ff,#16ff8f)"></div><span>Doctor Piscinas Premium Panteras</span>';
    option.onclick = function () {
      document.querySelectorAll('.theme-option').forEach(el => el.classList.remove('selected'));
      option.classList.add('selected');
      if (window.formData) window.formData.theme = 'doctor_piscinas_premium_panteras';
      setPreviewPremium();
    };
    selector.prepend(option);
  }

  document.addEventListener('DOMContentLoaded', function () {
    installPremiumPreview();
    ['submitForm', 'hbc3Budget', 'hbc3Download', 'hbc3OpenPanel'].forEach(wrapAction);
    injectPremiumThemeOption();
    document.addEventListener('input', function () { setTimeout(setPreviewPremium, 40); }, true);
    document.addEventListener('change', function () { setTimeout(setPreviewPremium, 40); }, true);
    setTimeout(function () {
      injectPremiumThemeOption();
      setPreviewPremium();
    }, 350);
  });
})();
