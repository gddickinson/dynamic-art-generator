// Parameter controls built from plugin.getParameters(), as main.DynamicArtGenerator.update_parameter_controls does:
// numbers -> slider from 0 to twice the starting value, booleans -> checkbox, anything else -> text field.
// (On the desktop a parameter whose default is 0 gets a 0..0 slider; here it gets 0..1 so it can be moved.)
import { esc } from './core.js';

export const title = n => n.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
const fmt = v => (Number.isInteger(v) ? String(v) : Math.abs(v) >= 100 ? v.toFixed(1) : v.toFixed(3));

export function buildParams(host, plugin, defaults, onChange) {
  const params = plugin.getParameters();
  host.innerHTML = '';
  for (const [name, value] of Object.entries(params)) {
    const base = defaults && name in defaults ? defaults[name] : value;
    const wrap = document.createElement('div');
    const id = `p-${name}`;
    if (typeof value === 'boolean') {
      wrap.className = 'ctl chk';
      wrap.innerHTML = `<label for="${id}"><input type="checkbox" id="${id}" ${value ? 'checked' : ''}> ${esc(title(name))}</label>`;
      wrap.querySelector('input').addEventListener('change', e => onChange(name, e.target.checked));
    } else if (typeof value === 'number') {
      const max = base > 0 ? base * 2 : base < 0 ? 0 : 1, min = base < 0 ? base * 2 : 0;
      const step = Number.isInteger(base) && Math.abs(max - min) >= 4 ? 1 : (max - min) / 200;
      wrap.className = 'ctl';
      wrap.innerHTML = `<label for="${id}">${esc(title(name))} <b>${fmt(value)}</b></label>
        <input type="range" id="${id}" min="${min}" max="${max}" step="${step}" value="${value}">`;
      const input = wrap.querySelector('input'), out = wrap.querySelector('b');
      input.addEventListener('input', () => {
        const v = +input.value; out.textContent = fmt(v); onChange(name, v);
      });
    } else {
      wrap.className = 'ctl';
      wrap.innerHTML = `<label for="${id}">${esc(title(name))}</label><input type="text" id="${id}" value="${esc(value)}">`;
      wrap.querySelector('input').addEventListener('change', e => onChange(name, e.target.value));
    }
    host.appendChild(wrap);
  }
}

// Sync the controls to the plugin's current values (after set_parameter clamped something, or a preset).
export function syncParams(host, plugin) {
  for (const [name, value] of Object.entries(plugin.getParameters())) {
    const input = host.querySelector(`#p-${CSS.escape(name)}`);
    if (!input) continue;
    if (input.type === 'checkbox') input.checked = !!value;
    else {
      input.value = value;
      const b = input.parentElement.querySelector('b');
      if (b && typeof value === 'number') b.textContent = fmt(value);
    }
  }
}
