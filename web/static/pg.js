// A small pygame-like drawing layer over a Canvas 2D context, so the plugin ports read like the Python plugins.
//
// Colours are [r, g, b] or [r, g, b, a] with 0..255 components, as in pygame. Alpha rules (pygame semantics):
//   * pygame.draw on the display surface (no per-pixel alpha) IGNORES the colour's alpha and draws opaque. The Gfx the
//     app passes to render() is such a surface: its `alpha` flag is false, so a 4th component is ignored there.
//   * The Python idiom "draw RGBA on a temporary pygame.Surface(..., SRCALPHA), then blit it" blends with alpha. Ports
//     express it as g.blended(): a view of the same canvas that honours alpha (same result, no temporary surface).
//   * g.layer(w, h) is a persistent SRCALPHA surface (alpha honoured); draw on it, then g.blit(layer, x, y).
// Circles with width > 0 are rings of that thickness drawn inward from the radius, as in pygame.
export const TAU = Math.PI * 2;

const clamp255 = v => (v < 0 ? 0 : v > 255 ? 255 : v);

// CSS colour from a pygame colour; alpha honoured only when `useAlpha` is true.
export function css(c, useAlpha = true) {
  const r = clamp255(c[0]) | 0, g = clamp255(c[1]) | 0, b = clamp255(c[2]) | 0;
  if (!useAlpha || c.length < 4) return `rgb(${r},${g},${b})`;
  return `rgba(${r},${g},${b},${(clamp255(c[3]) | 0) / 255})`;
}

// Factory for offscreen canvases (browser: OffscreenCanvas or <canvas>; node tests swap in a mock).
let makeCanvas = (w, h) => {
  if (typeof OffscreenCanvas !== 'undefined') return new OffscreenCanvas(w, h);
  const c = document.createElement('canvas'); c.width = w; c.height = h; return c;
};
export function setCanvasFactory(fn) { makeCanvas = fn; }

export class Gfx {
  // ctx: a CanvasRenderingContext2D; alpha: whether a colour's alpha component is honoured (SRCALPHA surface).
  constructor(ctx, w, h, alpha = false) {
    this.ctx = ctx; this.w = w; this.h = h; this.alpha = alpha;
    this.canvas = ctx.canvas;
  }

  get_width() { return this.w; }
  get_height() { return this.h; }
  get_size() { return [this.w, this.h]; }

  // Same canvas, alpha honoured: the port of "draw on a SRCALPHA temp surface, then blit".
  blended() {
    if (this.alpha) return this;
    if (!this._blended) { this._blended = new Gfx(this.ctx, this.w, this.h, true); }
    return this._blended;
  }

  // A persistent SRCALPHA surface (pygame.Surface(size, pygame.SRCALPHA)).
  layer(w = this.w, h = this.h) {
    const c = makeCanvas(Math.max(1, Math.round(w)), Math.max(1, Math.round(h)));
    return new Gfx(c.getContext('2d'), w, h, true);
  }

  col(c) { return css(c, this.alpha); }

  // surface.fill(color): replaces every pixel (no blending), as pygame does.
  fill(c) {
    const x = this.ctx;
    x.save(); x.setTransform(1, 0, 0, 1, 0, 0);
    x.clearRect(0, 0, this.w, this.h);
    if (!this.alpha || c.length < 4 || c[3] > 0) { x.fillStyle = this.col(c); x.fillRect(0, 0, this.w, this.h); }
    x.restore();
  }

  clear() { this.ctx.clearRect(0, 0, this.w, this.h); }

  circle(c, center, radius, width = 0) {
    if (!(radius > 0)) return;
    const x = this.ctx;
    x.beginPath();
    if (width > 0 && width < radius) {
      x.arc(center[0], center[1], radius - width / 2, 0, TAU);
      x.lineWidth = width; x.strokeStyle = this.col(c); x.stroke();
    } else {
      x.arc(center[0], center[1], radius, 0, TAU);
      x.fillStyle = this.col(c); x.fill();
    }
  }

  ellipse(c, rect, width = 0) {
    const [l, t, w, h] = rect;
    if (!(w > 0 && h > 0)) return;
    const x = this.ctx;
    x.beginPath();
    x.ellipse(l + w / 2, t + h / 2, w / 2, h / 2, 0, 0, TAU);
    if (width > 0) { x.lineWidth = width; x.strokeStyle = this.col(c); x.stroke(); } else { x.fillStyle = this.col(c); x.fill(); }
  }

  line(c, a, b, width = 1) {
    if (width < 1) return;
    const x = this.ctx;
    x.beginPath(); x.moveTo(a[0], a[1]); x.lineTo(b[0], b[1]);
    x.lineWidth = width; x.lineCap = width > 2 ? 'round' : 'butt'; x.strokeStyle = this.col(c); x.stroke();
  }

  aaline(c, a, b) { this.line(c, a, b, 1); }

  lines(c, closed, pts, width = 1) {
    if (pts.length < 2 || width < 1) return;
    const x = this.ctx;
    x.beginPath(); x.moveTo(pts[0][0], pts[0][1]);
    for (let i = 1; i < pts.length; i++) x.lineTo(pts[i][0], pts[i][1]);
    if (closed) x.closePath();
    x.lineWidth = width; x.lineJoin = 'round'; x.strokeStyle = this.col(c); x.stroke();
  }

  polygon(c, pts, width = 0) {
    if (pts.length < 3) return;
    const x = this.ctx;
    x.beginPath(); x.moveTo(pts[0][0], pts[0][1]);
    for (let i = 1; i < pts.length; i++) x.lineTo(pts[i][0], pts[i][1]);
    x.closePath();
    if (width > 0) { x.lineWidth = width; x.lineJoin = 'round'; x.strokeStyle = this.col(c); x.stroke(); } else { x.fillStyle = this.col(c); x.fill(); }
  }

  rect(c, r, width = 0) {
    const x = this.ctx;
    if (width > 0) { x.lineWidth = width; x.strokeStyle = this.col(c); x.strokeRect(r[0] + width / 2, r[1] + width / 2, r[2] - width, r[3] - width); }
    else { x.fillStyle = this.col(c); x.fillRect(r[0], r[1], r[2], r[3]); }
  }

  // pygame.font.Font(None, size).render(text, True, color) blitted with its top-left at (x, y).
  // The default pygame font at `size` is about 0.7*size px tall; `center` anchors the text centre instead.
  text(str, x, y, size, c, { center = false, bold = false } = {}) {
    const g = this.ctx;
    g.font = `${bold ? 'bold ' : ''}${Math.max(6, Math.round(size * 0.7))}px ui-monospace, Menlo, Consolas, monospace`;
    g.textBaseline = center ? 'middle' : 'top'; g.textAlign = center ? 'center' : 'left';
    g.fillStyle = this.col(c); g.fillText(String(str), x, y);
  }

  // surface.blit(src, (x, y)); src is a Gfx layer.
  blit(src, x = 0, y = 0) { this.ctx.drawImage(src.canvas, x, y); }
}
