// Seedable stand-in for Python's `random` / `np.random` calls used by the plugins (one shared mulberry32 stream).
// The browser seeds it from the clock; tests seed it for reproducible runs. Only the distributions match Python, not
// the exact numbers (Python uses the Mersenne Twister).
let a = 1;

export function seed(s) { a = (s >>> 0) || 1; }

// random.random(): uniform in [0, 1).
export function random() {
  a |= 0; a = (a + 0x6D2B79F5) | 0;
  let t = Math.imul(a ^ (a >>> 15), 1 | a);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
}

// random.uniform(a, b) and np.random.uniform(a, b).
export const uniform = (lo, hi) => lo + (hi - lo) * random();

// random.randint(a, b): integer in [a, b], both ends included.
export const randint = (lo, hi) => lo + Math.floor(random() * (hi - lo + 1));

// random.choice(seq).
export const choice = seq => seq[Math.floor(random() * seq.length)];

// random.gauss(mu, sigma) / np.random.normal(mu, sigma) (Box-Muller).
export function gauss(mu = 0, sigma = 1) {
  let u = 0;
  while (u === 0) u = random();
  return mu + sigma * Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * random());
}
