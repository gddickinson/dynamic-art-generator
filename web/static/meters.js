// A strip showing the audio features the plugin receives: amplitude, beat flash, dominant frequency, bass/mid/treble.
export function drawMeters(canvas, f) {
  const g = canvas.getContext('2d'), W = canvas.width, H = canvas.height;
  g.fillStyle = '#0a0d1a'; g.fillRect(0, 0, W, H);
  g.font = '12px ui-monospace, Menlo, monospace'; g.textBaseline = 'top';
  const bar = (x, w, label, v, max, color, text) => {
    g.fillStyle = '#94a3c6'; g.fillText(label, x, 8);
    g.fillStyle = '#1a2240'; g.fillRect(x, 28, w, 14);
    g.fillStyle = color; g.fillRect(x, 28, w * Math.max(0, Math.min(1, v / max)), 14);
    g.fillStyle = '#e8f1ff'; g.fillText(text, x, 48);
  };
  const a = f.amplitude || 0, df = f.dominant_frequency || 0, b = f.frequency_bands || { bass: 0, mid: 0, treble: 0 };
  bar(12, 150, 'amplitude', a, 1, '#ffb23f', a.toFixed(3));
  g.fillStyle = '#94a3c6'; g.fillText('beat', 180, 8);
  g.fillStyle = f.beat_detected ? '#ff4f8b' : '#1a2240'; g.beginPath(); g.arc(196, 36, 9, 0, 7); g.fill();
  bar(230, 160, 'dominant freq', df, 4000, '#7d6bff', `${df.toFixed(0)} Hz`);
  bar(410, 115, 'bass', b.bass, 1, '#ff4f8b', b.bass.toFixed(2));
  bar(540, 115, 'mid', b.mid, 1, '#ffb23f', b.mid.toFixed(2));
  bar(670, 115, 'treble', b.treble, 1, '#3de7ff', b.treble.toFixed(2));
}
