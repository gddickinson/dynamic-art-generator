// Subtle animated background: a slow Lissajous trail, like a faint pendulum drawing. Off under prefers-reduced-motion.
export function startBackground(canvas) {
  if (!canvas || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const g = canvas.getContext('2d');
  const fit = () => { canvas.width = innerWidth; canvas.height = innerHeight; };
  fit(); addEventListener('resize', fit);
  let t = 0;
  const step = () => {
    g.fillStyle = 'rgba(5,6,12,0.04)'; g.fillRect(0, 0, canvas.width, canvas.height);
    const w = canvas.width, h = canvas.height;
    for (let i = 0; i < 4; i++) {
      const s = t + i * 0.01;
      const x = w / 2 + w * 0.38 * Math.sin(s * 0.7) * Math.cos(s * 0.13), y = h / 2 + h * 0.36 * Math.sin(s * 1.1 + 1);
      g.fillStyle = `hsla(${(s * 20) % 360},90%,60%,0.5)`; g.beginPath(); g.arc(x, y, 1.6, 0, 7); g.fill();
    }
    t += 0.01;
    if (!document.hidden) requestAnimationFrame(step); else setTimeout(() => requestAnimationFrame(step), 500);
  };
  requestAnimationFrame(step);
}
