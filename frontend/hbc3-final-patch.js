// HBC3 FINAL FUNCTIONAL PATCH
(function () {
  const SAVE_URL = '/generator/save';
  const LIST_URL = '/generator/requests';

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

  async function save(type) {
    updateAll();
    const payload = {
      type: type || 'generated',
      name: formData.businessName || '',
      phone: formData.phone || formData.whatsapp || '',
      email: formData.email || '',
      description: formData.description || '',
      services: Array.isArray(formData.services) ? formData.services.join('\n') : '',
      html: currentHtml()
    };
    const response = await fetch(SAVE_URL, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload)
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail ? JSON.stringify(data.detail) : 'Error de guardado');
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
      if (typeof showNotice === 'function') showNotice('Guardado real: ' + result.path, 'success');
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
      if (typeof showNotice === 'function') showNotice('Presupuesto: ' + result.path, 'success');
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

  window.hbc3List = async function () {
    try {
      const response = await fetch(LIST_URL);
      const data = await response.json();
      if (!response.ok) throw new Error(JSON.stringify(data));
      const rows = (data.items || []).slice(0, 10).map(function (item) {
        return '<li><strong>' + esc(item.type) + '</strong> · ' + esc(item.name) + ' · ' + esc(item.phone || item.email) + '</li>';
      }).join('');
      let modal = document.getElementById('hbc3SavedModal');
      if (!modal) {
        modal = document.createElement('div');
        modal.id = 'hbc3SavedModal';
        modal.className = 'hbc3-auth-modal';
        document.body.appendChild(modal);
      }
      modal.innerHTML = '<div class="hbc3-auth-card"><button type="button" class="hbc3-auth-close" onclick="document.getElementById(\'hbc3SavedModal\').remove()">×</button><h3>Últimos guardados</h3><ul>' + (rows || '<li>No hay registros.</li>') + '</ul></div>';
    } catch (error) {
      alert('No se pudieron leer los guardados: ' + error.message);
    }
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

  document.addEventListener('DOMContentLoaded', function () {
    const nav = document.querySelector('.form-navigation');
    if (nav && !document.getElementById('hbc3BudgetBtn')) {
      const buttons = [
        ['hbc3BudgetBtn', 'Guardar Presupuesto', window.hbc3Budget, 'btn btn-primary'],
        ['hbc3DownloadBtn', 'Descargar HTML', window.hbc3Download, 'btn btn-secondary'],
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

    const login = document.querySelector('.btn-login');
    if (login) {
      const clone = login.cloneNode(true);
      clone.textContent = 'Ver Guardados';
      clone.onclick = window.hbc3List;
      login.replaceWith(clone);
    }

    setTimeout(function () {
      if (typeof updatePreview === 'function') updatePreview();
    }, 250);
  });
})();
