// #/about: what the project is, how the pipeline works, what the web version covers, how to run it, credits.
import { route, api, app, list, esc } from './core.js';

route('about', async () => {
  const [info, plugins] = await Promise.all([api('/info'), api('/plugins')]);
  app().innerHTML = `
  <p class="kicker">About</p><h1 class="glow">Dynamic Art Generator</h1>
  <p class="lead">${esc(info.summary)}</p>
  <h2>How it works</h2>
  <p>The desktop app (<code>main.py</code>, Tkinter + pygame) reads the microphone in chunks of ${info.chunk_size}
  samples at ${info.sample_rate} Hz. Each chunk becomes a dictionary of <em>audio features</em>: amplitude (RMS),
  beat (energy above its running average by 1.5 standard deviations, at most one per 0.1 s), the dominant frequency, the share of energy in the bass (≤ 250 Hz), mid (250–4000 Hz) and treble
  bands, spectral centroid, roll-off, zero-crossing rate, onset, harmonicity and a tempo estimate
  (<code>utils/audio_utils.py</code> AudioAnalyzer). About ${info.target_fps} times a second the selected plugin gets the
  latest features and <code>dt = 1/60</code> in <code>update()</code>, then draws itself onto an
  ${info.canvas_size.join('×')} surface in <code>render()</code>. Plugins are discovered automatically from
  <code>plugins/</code>; each exposes its parameters through <code>get_parameters()</code>, and the GUI builds a slider
  (0 to twice the starting value) or a checkbox for each.</p>
  <p class="eq">audio chunk → features → plugin.update(features, 1/60) → plugin.render(surface)</p>
  <h2>The web version</h2>
  <ul>
    <li><b>Runs in the browser.</b> All ${plugins.length} plugins are ported to JavaScript (<code>web/static/plugins/</code>)
      on a small pygame-like canvas layer, and the audio analysis is ported line by line. Node tests compare the
      analysis with the Python code on the same signal (agreement to about 1e-12) and each plugin's parameters and
      <code>set_parameter</code> behaviour with the Python plugin; see <a href="#/verify">Verify</a>.</li>
    <li><b>Inputs:</b> the built-in demo signal (the kick, snare and hi-hat of <code>DrumMachine</code> at 120 BPM with
      a gliding tone), an audio file, the microphone (only after you click, never sent anywhere), or the simulated
      features of <code>launcher.py</code>. The studio can also switch to AudioAnalyzer's own (peak) amplitude.</li>
    <li><b>Presets:</b> the ${info.presets} presets of <code>example_presets.json</code> load their plugin and parameters
      (preset keys that are not parameters of the plugin are skipped and listed).</li>
    <li><b>Differences:</b> random numbers come from a seeded generator, not Python's, so runs differ in detail;
      text uses the browser's monospace font instead of pygame's default font; where a plugin drew on a temporary
      transparent surface and blitted it, the port draws with the same transparency directly.</li>
  </ul>
  <h2>Run it yourself</h2>
  <h3>Desktop app</h3>
  <pre>git clone https://github.com/gddickinson/dynamic-art-generator.git
cd dynamic-art-generator
pip install -r requirements.txt      # macOS: brew install portaudio first
python main.py                       # macOS helper: python launcher.py</pre>
  <h3>Web app</h3>
  <pre>pip install -r requirements-web.txt
python run_web.py                    # http://127.0.0.1:8112
python scripts/build_static.py       # the static site in site/</pre>
  <h2>Credits</h2>
  <p>Dynamic Art Generator by George Dickinson, released under the MIT licence. The README names its inspirations:
  1100 AMIANGELIKA (particle-based visual art), physical paint-can pendulum installations and real-time audiovisual
  performance tools. Plugins: ${list(plugins, p => esc(p.name), ', ')}.</p>`;
});
