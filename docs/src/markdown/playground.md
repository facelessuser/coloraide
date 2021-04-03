# Interactive Sandbox

## Play with Colors

This sandbox is powered by [Pyodide](https://github.com/pyodide/pyodide). You can use the `Color` object and the `NaN`
constant to experiment with color spaces, interpolation, and more. All colors will be gamut mapped into the sRGB color
space for display.

<div id="results"><div class="color-command"><div class="swatch-bar"></div><div class="highlight"><pre><code>Loading...</code></pre></div></div></div>
<textarea id="text"># Insert your code here
Color('red')</textarea>

<style>
#text {
  padding: .7720588235em 1.1764705882em;
  display: block;
  width: 100%;
  min-height: 10em;
  background-color: var(--md-code-bg-color);
  color: var(--md-code-fg-color);
  margin-top: 2px;
}

#results code {
  height: 15em;
}

#results pre {
  margin-bottom: 0;
}

.swatch-bar {
  min-height: calc(3em + 4px);
}
</style>

<script type="text/js-worker" id="pyworker">
self.languagePluginUrl = 'https://cdn.jsdelivr.net/pyodide/v0.17.0a2/full/';
importScripts('https://cdn.jsdelivr.net/pyodide/v0.17.0a2/full/pyodide.js');

const pycode = `
--8<-- "pycode.txt"
`

function analyze(str) {
    code = `
import micropip

${pycode}

text = """
${str.replace('"', '\\"')}
"""

def parse_colors(*args):
    """Get colors."""

    globals()['results'] = color_command_formatter(text)
    print(globals()['results'])

micropip.install('coloraide').add_done_callback(parse_colors)

`
    languagePluginLoader.then(() => {
      return pyodide.loadPackage(['micropip', 'Pygments']);
    }).then(() => {
      console.log(pyodide.runPython(code));
      setTimeout(post, 500);
    });
}

function post() {
   self.postMessage(pyodide.globals.get("results"));
}


self.addEventListener("message", (event) => {
    analyze(event.data);
});
</script>

<script type="text/javascript">
const text = document.getElementById("text");
const results = document.getElementById("results");

const worker = new Worker(window.URL.createObjectURL(new Blob([pyworker.textContent], {type: 'text/javascript'})));
let busy = false;
let requests = 0;

text.addEventListener("input", (e) => {
  if (busy) {
    requests++;
    return;
  }
  requests = 0;
  busy = true;
  worker.postMessage(e.target.value);
});

worker.addEventListener("message", (e) => {
  results.innerHTML = e.data;
  let scrollingElement = results.querySelector('code');
  scrollingElement.scrollTop = scrollingElement.scrollHeight;
  busy = false;
  if (requests) {
    requests = 0;
    busy = true;
    worker.postMessage(text.value);
  }
});

text.focus();
busy = true;
worker.postMessage(text.value);
</script>
