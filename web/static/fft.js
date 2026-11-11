// |rfft(x)|: magnitudes of the real FFT (numpy.fft.rfft) for a power-of-two length, iterative radix-2 (from the kaleidoscope web port).
const tables = new Map();

function table(n) {
  if (!tables.has(n)) {
    const cos = new Float64Array(n / 2), sin = new Float64Array(n / 2), rev = new Uint32Array(n);
    for (let k = 0; k < n / 2; k++) { cos[k] = Math.cos(2 * Math.PI * k / n); sin[k] = Math.sin(2 * Math.PI * k / n); }
    const bits = Math.log2(n);
    for (let i = 0; i < n; i++) {
      let r = 0;
      for (let b = 0; b < bits; b++) r |= ((i >> b) & 1) << (bits - 1 - b);
      rev[i] = r;
    }
    tables.set(n, { cos, sin, rev });
  }
  return tables.get(n);
}

export function rfftAbs(x) {
  const n = x.length;
  if (n & (n - 1)) throw new Error('rfftAbs: length must be a power of two');
  const { cos, sin, rev } = table(n);
  const re = new Float64Array(n), im = new Float64Array(n);
  for (let i = 0; i < n; i++) re[rev[i]] = x[i];
  for (let size = 2; size <= n; size *= 2) {
    const half = size / 2, step = n / size;
    for (let start = 0; start < n; start += size) {
      for (let k = 0; k < half; k++) {
        const wr = cos[k * step], wi = -sin[k * step];
        const a = start + k, b = a + half;
        const tr = re[b] * wr - im[b] * wi, ti = re[b] * wi + im[b] * wr;
        re[b] = re[a] - tr; im[b] = im[a] - ti;
        re[a] += tr; im[a] += ti;
      }
    }
  }
  const out = new Float64Array(n / 2 + 1);
  for (let k = 0; k <= n / 2; k++) out[k] = Math.hypot(re[k], im[k]);
  return out;
}
