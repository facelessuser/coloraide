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

<script type="text/javascript">
const text = document.getElementById("text");
const results = document.getElementById("results");

const textAnalyzer = new Worker("../playground.js");
let busy = false;
let requests = 0;

text.addEventListener("input", (e) => {
  if (busy) {
    requests++;
    return;
  }
  busy = true;
  textAnalyzer.postMessage(e.target.value);
});

textAnalyzer.addEventListener("message", (event) => {
  results.innerHTML = event.data;
  let scrollingElement = results.querySelector('code');
  scrollingElement.scrollTop = scrollingElement.scrollHeight;
  busy = false;
  if (requests) {
    requests = 0;
    textAnalyzer.postMessage(text.value);
    busy = true;
  }
});

text.focus();
textAnalyzer.postMessage(text.value);
</script>
