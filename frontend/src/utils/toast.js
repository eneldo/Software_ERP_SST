// ============================================================
// TOAST NOTIFICATION SYSTEM - ERP SST PRO
// Reemplaza alert() nativas con notificaciones enterprise.
// ============================================================

let _container = null;
let _counter = 0;

function getContainer() {
  if (_container) return _container;
  _container = document.createElement("div");
  _container.id = "erp-sst-toast-container";
  _container.style.cssText =
    "position:fixed;top:16px;right:16px;z-index:99999;display:flex;flex-direction:column;gap:8px;pointer-events:none;max-width:400px;";
  document.body.appendChild(_container);
  return _container;
}

const STYLES = {
  success: { bg: "#dcfce7", border: "#16a34a", icon: "\u2714", color: "#166534" },
  error: { bg: "#fee2e2", border: "#dc2626", icon: "\u2718", color: "#991b1b" },
  warning: { bg: "#fef3c7", border: "#d97706", icon: "\u26a0", color: "#92400e" },
  info: { bg: "#dbeafe", border: "#2563eb", icon: "\u2139", color: "#1e40af" },
};

function toast(type = "info", title = "", message = "", duration = 5000) {
  const id = `toast-${++_counter}`;
  const s = STYLES[type] || STYLES.info;

  const el = document.createElement("div");
  el.id = id;
  el.style.cssText = `
    pointer-events:auto;background:${s.bg};border-left:4px solid ${s.border};
    color:${s.color};padding:12px 16px;border-radius:8px;box-shadow:0 4px 12px rgba(0,0,0,.15);
    font-family:system-ui,-apple-system,sans-serif;font-size:14px;display:flex;gap:10px;
    align-items:flex-start;animation:erp-toast-in .3s ease;cursor:pointer;min-width:280px;
  `;
  el.innerHTML = `
    <span style="font-size:18px;line-height:1">${s.icon}</span>
    <div style="flex:1;min-width:0">
      <div style="font-weight:600;margin-bottom:2px">${escapeHtml(title)}</div>
      ${message ? `<div style="opacity:.85;font-size:13px;word-break:break-word">${escapeHtml(message)}</div>` : ""}
    </div>
    <span style="opacity:.5;cursor:pointer;font-size:16px;line-height:1" data-close>&times;</span>
  `;

  el.addEventListener("click", (e) => {
    if (e.target.dataset.close !== undefined || e.target === el) removeToast(el);
  });

  getContainer().appendChild(el);

  if (duration > 0) {
    setTimeout(() => removeToast(el), duration);
  }

  return id;
}

function removeToast(el) {
  if (!el || !el.parentNode) return;
  el.style.animation = "erp-toast-out .3s ease forwards";
  setTimeout(() => el.remove(), 300);
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

if (!document.getElementById("erp-sst-toast-styles")) {
  const style = document.createElement("style");
  style.id = "erp-sst-toast-styles";
  style.textContent = `
    @keyframes erp-toast-in { from { opacity:0; transform:translateX(40px); } to { opacity:1; transform:translateX(0); } }
    @keyframes erp-toast-out { from { opacity:1; transform:translateX(0); } to { opacity:0; transform:translateX(40px); } }
  `;
  document.head.appendChild(style);
}

export const toastSuccess = (title, msg, dur) => toast("success", title, msg, dur);
export const toastError = (title, msg, dur) => toast("error", title, msg, dur);
export const toastWarning = (title, msg, dur) => toast("warning", title, msg, dur);
export const toastInfo = (title, msg, dur) => toast("info", title, msg, dur);

export function confirmAction(message = "¿Está seguro?") {
  return window.confirm(message);
}

export default toast;
