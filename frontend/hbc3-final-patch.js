// HBC3 FINAL FUNCTIONAL PATCH
(function () {
  const SAVE_URL = '/generator/save';
  const STORAGE_KEY = 'hbc3_saved_records';
  let lastViewUrl = '';

  function esc(value) {
    return String(value || '').replace(/[&<>"']/g, function (char) {
      return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char];
    });
  }

  function updateAll() {
    if (typeof updateFormData === 'function') updateFormData(true);
  }

  function currentHtml() {
    try {
      if (typeof generatePreviewHTML === 'function') return generatePreviewHTML();
    } catch (error) {}
    const frame = document.getElementById('previewFrame');
    return frame ? (frame.srcdoc || '') : '';
  }

  function selectedPlan() {
    return localStorage.getItem('hbc3_selected_plan') || 'free';
  }

  function remember(result, type) {
    const records = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
    records.unshift({
      id: result.id,
      type: type,
      name: formData.businessName || '',
      view_url: result.view_url || '',
      saved_at: new Date().toLocaleString()
    });
    localStorage.setItem(STORAGE_KEY, JSON.stringify(records.slice(0, 25)));
    lastViewUrl = result.view_url || lastViewUrl;
  }

  async function save(type) {
    updateAll();
    const payload = {
      type: type || 'generated',
      name: formData.businessName || '',
      phone: formData.phone || formData.whatsapp || '',
      email: formData.email || '',
      description: formData.description || '',
      services: Array.isArray(formData.services) ? formData.services.join('\n') : '',
      html: currentHtml(),
      plan: selectedPlan()
    };
    const response = await fetch(SAVE_URL, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload)
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail ? JSON.stringify(data.detail) : 'Error de guardado');
    remember(data, type);
    return data;
  }

  window.submitForm = async function () {
    updateAll();
    if (!formData.businessName) {
      alert('Escribe el nombre del negocio.');
      return;
    }
    const button = document.getElementById('submitBtn');
    const original = button ? button.textContent : 'Generar Panel';
    if (button) {
      button.textContent = 'Generando y guardando...';
      button.disabled = true;
    }
    try {
      if (typeof updatePreview === 'function') updatePreview();
      const result = await save('generated');
      alert('Panel generado y guardado. ID: ' + result.id);
      if (typeof showNotice === 'function') showNotice('Guardado real. Puedes abrir la pantalla.', 'success');
    } catch (error) {
      alert('No se pudo guardar: ' + error.message);
    } finally {
      if (button) {
        button.textContent = original;
        button.disabled = false;
      }
    }
  };

  window.hbc3Budget = async function () {
    updateAll();
    if (!formData.businessName) return alert('Escribe el nombre del negocio.');
    if (!formData.phone && !formData.email && !formData.whatsapp) {
      return alert('Añade teléfono, email o WhatsApp para recibir el presupuesto.');
    }
    try {
      const result = await save('budget');
      alert('Presupuesto registrado. ID: ' + result.id);
      if (typeof showNotice === 'function') showNotice('Presupuesto guardado con evidencia.', 'success');
    } catch (error) {
      alert('No se pudo registrar el presupuesto: ' + error.message);
    }
  };

  window.hbc3Download = function () {
    updateAll();
    const html = currentHtml();
    const blob = new Blob([html], {type: 'text/html'});
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'hbc3-panel-generado.html';
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(function () { URL.revokeObjectURL(link.href); }, 1000);
    if (typeof showNotice === 'function') showNotice('HTML descargado.', 'success');
  };

  window.hbc3OpenPanel = function () {
    if (lastViewUrl) {
      window.open(lastViewUrl, '_blank', 'noopener');
      return;
    }
    const records = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
    if (records[0] && records[0].view_url) {
      window.open(records[0].view_url, '_blank', 'noopener');
      return;
    }
    const html = currentHtml();
    const blob = new Blob([html], {type: 'text/html'});
    const url = URL.createObjectURL(blob);
    window.open(url, '_blank', 'noopener');
    setTimeout(function () { URL.revokeObjectURL(url); }, 30000);
  };

  window.hbc3List = function () {
    const records = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
    const rows = records.map(function (item) {
      const link = item.view_url ? '<a href="' + esc(item.view_url) + '" target="_blank" rel="noopener">Abrir</a>' : '';
      return '<li><strong>' + esc(item.type) + '</strong> · ' + esc(item.name) + ' · ' + esc(item.saved_at) + ' ' + link + '</li>';
    }).join('');
    let modal = document.getElementById('hbc3SavedModal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'hbc3SavedModal';
      modal.className = 'hbc3-auth-modal';
      document.body.appendChild(modal);
    }
    modal.innerHTML = '<div class="hbc3-auth-card"><button type="button" class="hbc3-auth-close" onclick="document.getElementById(\'hbc3SavedModal\').remove()">×</button><h3>Guardados reales</h3><p>Los datos están almacenados en backend. Esta lista recuerda tus enlaces en este navegador.</p><ul>' + (rows || '<li>No hay registros todavía.</li>') + '</ul></div>';
  };

  window.hbc3Call = function () {
    updateAll();
    const phone = formData.phone || formData.whatsapp || '';
    if (!phone) return alert('Añade teléfono.');
    window.location.href = 'tel:' + phone;
  };

  window.hbc3Email = function () {
    updateAll();
    if (!formData.email) return alert('Añade email.');
    window.location.href = 'mailto:' + formData.email + '?subject=Solicitud%20de%20presupuesto';
  };

  window.hbc3WhatsApp = function () {
    updateAll();
    const number = String(formData.whatsapp || formData.phone || '').replace(/\D/g, '');
    if (!number) return alert('Añade WhatsApp o teléfono.');
    window.open('https://wa.me/' + number, '_blank', 'noopener');
  };

  const originalPreview = window.generatePreviewHTML || (typeof generatePreviewHTML === 'function' ? generatePreviewHTML : null);
  if (originalPreview) {
    window.generatePreviewHTML = function () {
      const html = originalPreview();
      const phone = esc(formData.phone || formData.whatsapp || '');
      const email = esc(formData.email || '');
      const whatsapp = String(formData.whatsapp || formData.phone || '').replace(/\D/g, '');
      const actions = `
        <div class="actions" style="grid-template-columns:repeat(2,1fr)">
          <button class="btn btn-primary" onclick="parent.postMessage({type:'hbc3-budget'},'*')">Presupuesto</button>
          <a class="btn btn-secondary" href="https://wa.me/${whatsapp}" target="_blank" rel="noopener">WhatsApp</a>
          <a class="btn btn-secondary" href="tel:${phone}">Llamar</a>
          <a class="btn btn-secondary" href="mailto:${email}?subject=Solicitud%20de%20presupuesto">Email</a>
        </div>`;
      return html.replace(/<div class="actions">[\s\S]*?<\/div>\s*<div class="status">/, actions + '<div class="status">');
    };
  }

  window.addEventListener('message', function (event) {
    if (event && event.data && event.data.type === 'hbc3-budget') window.hbc3Budget();
  });

  function choosePlan(name) {
    localStorage.setItem('hbc3_selected_plan', name);
    if (typeof showNotice === 'function') showNotice('Plan seleccionado: ' + name, 'success');
    const form = document.querySelector('.form-section');
    if (form) form.scrollIntoView({behavior: 'smooth'});
  }

  function showDocs(event) {
    if (event) event.preventDefault();
    let modal = document.getElementById('hbc3DocsModal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'hbc3DocsModal';
      modal.className = 'hbc3-auth-modal';
      document.body.appendChild(modal);
    }
    modal.innerHTML = '<div class="hbc3-auth-card"><button type="button" class="hbc3-auth-close" onclick="document.getElementById(\'hbc3DocsModal\').remove()">×</button><h3>Documentación</h3><ol><li>Completa el negocio.</li><li>Elige tema y servicios.</li><li>Genera y guarda.</li><li>Descarga HTML o abre la pantalla pública.</li></ol></div>';
  }

  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('input[name="phone"], input[name="email"]').forEach(function (input) {
      input.removeAttribute('required');
    });

    const nav = document.querySelector('.form-navigation');
    if (nav && !document.getElementById('hbc3BudgetBtn')) {
      const buttons = [
        ['hbc3BudgetBtn', 'Guardar Presupuesto', window.hbc3Budget, 'btn btn-primary'],
        ['hbc3DownloadBtn', 'Descargar HTML', window.hbc3Download, 'btn btn-secondary'],
        ['hbc3OpenBtn', 'Abrir Pantalla', window.hbc3OpenPanel, 'btn btn-secondary'],
        ['hbc3ListBtn', 'Ver Guardados', window.hbc3List, 'btn btn-secondary']
      ];
      buttons.forEach(function (config) {
        const button = document.createElement('button');
        button.type = 'button';
        button.id = config[0];
        button.textContent = config[1];
        button.onclick = config[2];
        button.className = config[3];
        nav.appendChild(button);
      });
    }

    const headerNav = document.querySelector('.nav');
    if (headerNav && !document.getElementById('hbc3SavedNav')) {
      const saved = document.createElement('button');
      saved.type = 'button';
      saved.id = 'hbc3SavedNav';
      saved.className = 'btn btn-login';
      saved.textContent = 'Ver Guardados';
      saved.onclick = window.hbc3List;
      headerNav.appendChild(saved);
    }

    const docs = document.querySelector('a[href="#docs"]');
    if (docs) docs.addEventListener('click', showDocs);

    document.querySelectorAll('.pricing-card').forEach(function (card) {
      const title = card.querySelector('h3');
      const button = card.querySelector('button');
      if (!title || !button) return;
      button.type = 'button';
      button.onclick = function () { choosePlan(title.textContent.trim().toLowerCase()); };
    });

    setTimeout(function () {
      if (typeof updatePreview === 'function') updatePreview();
    }, 250);
  });
})();
