// Entry point: registers the lazily loaded pages, sets the footer mode text, draws the background and starts the router.
import { start, route, lazy, app, isStatic, $ } from './core.js';
import { startBackground } from './background.js';

const PAGES = { 'home.js': ['home'], 'studio.js': ['studio'], 'plugins_page.js': ['plugins'], 'verify.js': ['verify'], 'about.js': ['about'] };
lazy(Object.fromEntries(Object.entries(PAGES).flatMap(([file, names]) => names.map(n => [n, () => import('./' + file)]))));

route('notfound', () => { app().innerHTML = '<h1>Not found</h1><p><a href="#/">Back to the start</a></p>'; });

$('#mode').textContent = isStatic() ? 'static site: the art runs in your browser' : 'local app (Python server)';
startBackground($('#bg'));
start();
