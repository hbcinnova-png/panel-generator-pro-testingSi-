// HBC3 FINAL FUNCTIONAL PATCH
// Restores full original UI while connecting generation to the public HBC3 backend.
(function () {
  const SAVE_URL = 'https://hbc3-executor.onrender.com/generator/save';

  function getPanelHtml() {
    try {
      if (typeof generatePreviewHTML === 'function') return generatePreviewHTML();
    } catch (e) {}
    const frame = document.getElementById('previewFrame');
    return frame ? (frame.srcdoc || '') : '';
  }

  async function hbc3Save(type) {
    if (typeof updateFormData === 'function') updateFormData(true);
    const payload = {
      type: type || 'generated',
      name: formData.businessName || '',
      phone: formData.phone || formData.whatsapp || '',
      email: formData.email || '',
      description: formData.description || '',
      services: Array.isArray(formData.services) ? formData.services.join('\n') : '',
      html: getPanelHtml()
    };
    const response = await fetch(SAVE_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await response.json();
    if (!response.ok) throw new Error(JSON.stringify(data));
    return data;
  }

  window.submitForm = async function () {
    if (typeof updateFormData === 'function') updateFormData(true);
    if (!formData.businessName || !formData.email) {
      alert('Completa nombre del negocio y email.');
      return;
    }
    const submitBtn = document.getElementById('submitBtn');
    const original = submitBtn ? submitBtn.textContent : 'Generar Panel';
    if (submitBtn) { submitBtn.textContent = 'Generando y guardando...'; submitBtn.disabled = true; }
    try {
      const data = await hbc3Save('generated');
      alert('Panel generado y guardado en backend. ID: ' + data.id);
      if (typeof showNotice === 'function') showNotice('Guardado real: ' + data.path, 'success');
    } catch (error) {
      alert('Error guardando: ' + error.message);
    } finally {
      if (submitBtn) { submitBtn.textContent = original; submitBtn.disabled = false; }
    }
  };

  window.hbc3Budget = async function () {
    try {
      const data = await hbc3Save('budget');
      alert('Presupuesto guardado en backend. ID: ' + data.id);
      if (typeof showNotice === 'function') showNotice('Presupuesto guardado: ' + data.path, 'success');
    } catch (error) {
      alert('Error presupuesto: ' + error.message);
    }
  };

  window.hbc3Download = function () {
    const html = getPanelHtml();
    const blob = new Blob([html], { type: 'text/html' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'hbc3-panel-generado.html';
    document.body.appendChild(link);
    link.click();
    link.remove();
    if (typeof showNotice === 'function') showNotice('HTML descargado.', 'success');
  };

  window.hbc3Call = function () {
    const phone = formData.phone || formData.whatsapp || '';
    if (!phone) return alert('Añade teléfono.');
    window.location.href = 'tel:' + phone;
  };

  window.hbc3Email = function () {
    if (!formData.email) return alert('Añade email.');
    window.location.href = 'mailto:' + formData.email + '?subject=Solicitud de presupuesto';
  };

  window.hbc3WhatsApp = function () {
    const number = String(formData.whatsapp || formData.phone || '').replace(/\D/g, '');
    if (!number) return alert('Añade WhatsApp o teléfono.');
    window.open('https://wa.me/' + number, '_blank');
  };

  document.addEventListener('DOMContentLoaded', function () {
    const nav = document.querySelector('.form-navigation');
    if (nav && !document.getElementById('hbc3BudgetBtn')) {
      const budget = document.createElement('button');
      budget.type = 'button';
      budget.id = 'hbc3BudgetBtn';
      budget.className = 'btn btn-primary';
      budget.textContent = 'Guardar Presupuesto';
      budget.onclick = window.hbc3Budget;
      const download = document.createElement('button');
      download.type = 'button';
      download.id = 'hbc3DownloadBtn';
      download.className = 'btn btn-secondary';
      download.textContent = 'Descargar HTML';
      download.onclick = window.hbc3Download;
      nav.appendChild(budget);
      nav.appendChild(download);
    }
  });
})();
