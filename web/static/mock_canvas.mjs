// Node-test helper (not shipped on the static site): a mock 2D context that counts drawing calls and fails on any
// non-finite number passed to it, plus a Gfx factory using it.
import { Gfx, setCanvasFactory } from './pg.js';

export class MockCtx {
  constructor(w = 800, h = 600) {
    this.canvas = { width: w, height: h, getContext: () => this };
    this.calls = 0; this.bad = [];
    const methods = ['beginPath', 'arc', 'ellipse', 'moveTo', 'lineTo', 'closePath', 'stroke', 'fill', 'fillRect',
      'strokeRect', 'clearRect', 'fillText', 'drawImage', 'save', 'restore', 'setTransform', 'translate', 'rotate',
      'scale', 'quadraticCurveTo', 'bezierCurveTo', 'rect', 'createLinearGradient', 'createRadialGradient',
      'getImageData', 'putImageData', 'createImageData', 'measureText', 'setLineDash', 'clip', 'strokeText'];
    for (const m of methods) {
      this[m] = (...args) => {
        this.calls++;
        args.forEach((a, i) => { if (typeof a === 'number' && !Number.isFinite(a)) this.bad.push(`${m} arg ${i} = ${a}`); });
        if (m === 'createLinearGradient' || m === 'createRadialGradient') return { addColorStop: () => {} };
        if (m === 'measureText') return { width: 10 };
        if (m === 'getImageData' || m === 'createImageData') return { data: new Uint8ClampedArray(4 * args[2] * args[3]), width: args[2], height: args[3] };
        return undefined;
      };
    }
    for (const p of ['fillStyle', 'strokeStyle']) {
      let v = '';
      Object.defineProperty(this, p, {
        get: () => v,
        set: s => { if (typeof s === 'string' && /NaN|Infinity|undefined/.test(s)) this.bad.push(`${p} = ${s}`); v = s; },
      });
    }
    let lw = 1;
    Object.defineProperty(this, 'lineWidth', {
      get: () => lw, set: s => { if (!Number.isFinite(s)) this.bad.push(`lineWidth = ${s}`); lw = s; },
    });
  }
}

const made = [];
setCanvasFactory((w, h) => { const c = new MockCtx(w, h); made.push(c); return c.canvas; });

// A display-surface Gfx over a fresh mock context; `all()` lists every mock made so far (layers included).
export function mockGfx(w = 800, h = 600) {
  const ctx = new MockCtx(w, h); made.push(ctx);
  return new Gfx(ctx, w, h, false);
}
export const allMocks = () => made;
