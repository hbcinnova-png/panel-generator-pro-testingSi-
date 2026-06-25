// HBC3 final hotfix: keep four preview actions after every refresh and save them.
(function () {
  function esc(value) {
    return String(value || '').replace(/[&<>"']/g, function (char) {
      return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char];
    });
  }

  function decorateHtml(html) {
    if (!html) return html;
    const phone = esc(formData.phone || formData.whatsapp || '');
    const email = esc(formData.email || '');
    const whatsapp = String(formData.whatsapp || formData.phone || '').replace(/\D/g, '');
    const actions = `<div class="actions" style="grid-template-columns:repeat(2,1fr)">
      <button class="btn btn-primary" onclick="parent.postMessage({type:'hbc3-budget'},'*')">Presupuesto</button>
      <a class="btn btn-secondary" href="https://wa.me/${whatsapp}" target="_blank" rel="noopener">WhatsApp</a>
      <a class="btn btn-secondary" href="tel:${phone}">Llamar</a>
      <a class="btn btn-secondary" href="mailto:${email}?subject=Solicitud%20de%20presupuesto">Email</a>
    </div>`;
    return html.replace(
      /<div class="(?:actions|buttons)">[\s\S]*?<\/div>\s*<div class="status">/,
      actions + '<div class="status">'
    );
  }

  function decoratePreview() {
    const frame = document.getElementById('previewFrame');
    if (!frame || !frame.srcdoc) return;
    const updated = decorateHtml(frame.srcdoc);
    if (updated !== frame.srcdoc) frame.srcdoc = updated;
  }

  const originalFetch = window.fetch.bind(window);
  window.fetch = function (url, options) {
    if (String(url).endsWith('/generator/save') && options && options.body) {
      try {
        const body = JSON.parse(options.body);
        body.html = decorateHtml(body.html || document.getElementById('previewFrame')?.srcdoc || '');
        options = Object.assign({}, options, {body: JSON.stringify(body)});
      } catch (_) {}
    }
    return originalFetch(url, options);
  };

  function wrap(name) {
    const original = window[name];
    if (typeof original !== 'function') return;
    window[name] = async function () {
      decoratePreview();
      const result = await original.apply(this, arguments);
      setTimeout(decoratePreview, 20);
      return result;
    };
  }

  document.addEventListener('DOMContentLoaded', function () {
    ['submitForm', 'hbc3Budget', 'hbc3Download'].forEach(wrap);
    document.addEventListener('input', function () { setTimeout(decoratePreview, 25); }, true);
    document.addEventListener('change', function () { setTimeout(decoratePreview, 25); }, true);
    setTimeout(decoratePreview, 350);
  });
})();
