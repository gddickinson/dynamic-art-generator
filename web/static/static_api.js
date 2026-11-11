// Static-site data layer: answers api('/...') from the JSON files exported by scripts/build_static.py (every GET in
// STATIC_ENDPOINTS of web/app.py). The art and audio analysis run in JS, so nothing needs the server.
const files = new Map();

export async function staticApi(path, body) {
  if (body) throw new Error('This needs the local Python server (see the README, "Run the web app").');
  const rel = path.split('?')[0].replace(/^\/+/, '');
  if (!files.has(rel)) {
    files.set(rel, fetch('api/' + rel + '.json').then(r => {
      if (!r.ok) throw new Error(`${r.status} ${rel}`);
      return r.json();
    }));
  }
  return files.get(rel);
}
