<script src="https://cdn.jsdelivr.net/pyodide/v0.18.1/full/pyodide.js"></script>

<script type="text/javascript">
(() => {
  let pyodide = null;
  let busy = false;
  let requests = 0;
  let lastText = '';
  let raw = '';
  let gist = '';
  let gistType = '';
  const reIdNum = /.*?_(\d+)$/;
  let initialized = false;
  // This is the Python payload that will be executed when the user
  // presses the `Run` button. It will execute the code, create a
  // Python console output, find color references, steps, and interpolation
  // references and render the appropriate preview.
  const pycode = `
--8<-- "playground.txt"
`
  const defContent = `import coloraide
coloraide.__version__
Color('red')`;


  function getContent(content) {
      return `
!!! new "This notebook is powered by [Pyodide](https://github.com/pyodide/pyodide). \
Learn more [here](?notebook=https://gist.githubusercontent.com/facelessuser/7c819668b5eb248ecb9ac608d91391cf/raw/playground.md). \
Preview, convert, interpolate, and explore!"

\`\`\`\`\`\`\`\`playground
${content}
\`\`\`\`\`\`\`\`
`;
  }

  async function textResize(inpt) {
    // Resize inputs based on text height.

    inpt.style.height = "5px";
    inpt.style.height = (inpt.scrollHeight) + "px";
  };

  function encodeuri(uri) {
    // Encode the URI component.

    return encodeURIComponent(uri).replace(/[.!'()*]/g, (c) => {
      return '%' + c.charCodeAt(0).toString(16);
    });
  };

  async function pyexecute(current_id) {
    // Execute Python code

    const current_inputs = document.getElementById(`__playground-inputs_${current_id}`);
    current_inputs.setAttribute('readonly', '');
    pyodide.globals.set('id_num', current_id);
    pyodide.globals.set('action', 'notebook');
    await pyodide.runPythonAsync(pycode);
    current_inputs.removeAttribute('readonly');
  }

  async function pyrender(text) {
    // Execute Python code

    pyodide.globals.set('content', text);
    pyodide.globals.set('action', 'render');
    await pyodide.runPythonAsync(pycode);
    src = document.getElementById('__notebook-input');
    if (src) {
      raw = text;
      src.value = text;
    }
    if (window.location.hash) {
      window.location.href = window.location.href;
    }
  }

  async function load_pyodide(button_notify) {
    // Load `Pyodide` and the any default packages we can need and can load.

    const buttons = document.querySelectorAll('.playground button');

    if (!initialized) {
      if (button_notify) {
        if (buttons) {
          buttons.forEach((b) => {
            b.setAttribute('disabled', '');
            if (b.classList.contains('playground-edit')) {
              b.innerHTML = 'Loading...';
            }
          });
        }
      }
      initialized = true;
      pyodide = await loadPyodide({indexURL : "https://cdn.jsdelivr.net/pyodide/v0.18.1/full/" });
      await pyodide.loadPackage(['micropip', 'Pygments']);
      if (buttons) {
        buttons.forEach((b) => {
          b.removeAttribute('disabled');
          if (b.classList.contains('playground-edit')) {
            b.innerHTML = 'Edit';
          }
        });
      }
    }
  }

  async function showBusy(label) {
    if (!label) {
      label = 'Loading Pyodide...';
    }
    var template = document.createElement('template');
    template.innerHTML = `<div class="loading"><div class="loader"></div><div>${label}</div></div>`;
    document.querySelector('article').appendChild(template.content.firstChild);
  }

  async function hideBusy() {
    const spinner = document.querySelector('article .loading');
    spinner.parentNode.removeChild(spinner);
  }

  async function init(first) {
    // Setup input highlighting and events to run Python code blocks.

    requests = 0;

    const notebook = document.getElementById(`__notebook-source`);
    const playgrounds = document.querySelectorAll('.playground');
    playgrounds.forEach(async function(pg) {

      const current_id = pg.id.replace(reIdNum, '$1');
      const inputs = document.getElementById(`__playground-inputs_${current_id}`);
      const results = document.getElementById(`__playground-results_${current_id}`);
      const pgcode = document.getElementById(`__playground-code_${current_id}`);
      const button_edit = document.querySelector(`button#__playground-edit_${current_id}`);
      const button_share = document.querySelector(`button#__playground-share_${current_id}`);
      const button_run = document.querySelector(`button#__playground-run_${current_id}`);
      const button_cancel = document.querySelector(`button#__playground-cancel_${current_id}`);

      inputs.addEventListener("input", (e) => {
        // Adjust textarea height on text input.

        textResize(inputs);
      });

      if (notebook && first) {
        document.getElementById('__notebook-input').addEventListener("input", (e) => {
          // Adjust textarea height on text input.

          textResize(e.target);
        });

        const edit_page = document.getElementById('__notebook-edit');
        edit_page.addEventListener("click", async function(e) {
          document.getElementById('__notebook-render').classList.toggle('hidden');
          document.getElementById('__notebook-source').classList.toggle('hidden');
          textResize(document.getElementById('__notebook-input'));
        });

        document.getElementById('__notebook-md-gist').addEventListener("click", function(e) {
          let uri = prompt("Please enter Markdown page source:", gist);
          if (uri != null) {
            uri = encodeuri(uri);
            const relativePathQuery = window.location.pathname + '?' + new URLSearchParams('notebook=' + uri).toString();
            history.pushState(null, '', relativePathQuery);
            setTimeout(() => {main(false);}, 0);
          }
        });

        document.getElementById('__notebook-py-gist').addEventListener("click", function(e) {
          let uri = prompt("Please enter Python code source:", gist);
          if (uri != null) {
            uri = encodeuri(uri);
            const relativePathQuery = window.location.pathname + '?' + new URLSearchParams('source=' + uri).toString();
            history.pushState(null, '', relativePathQuery);
            setTimeout(() => {main(false);}, 0);
            return true;
          }
          return false;
        });

        document.getElementById('__notebook-input').value = raw;
        document.getElementById('__notebook-cancel').addEventListener("click", async function(e) {
          document.getElementById('__notebook-render').classList.toggle('hidden');
          document.getElementById('__notebook-source').classList.toggle('hidden');
        });

        document.getElementById('__notebook-submit').addEventListener("click", async function(e) {
          const render = document.getElementById('__notebook-render');
          raw = document.getElementById('__notebook-input').value;
          render.classList.toggle('hidden');
          document.getElementById('__notebook-source').classList.toggle('hidden');
          await showBusy("Loading Notebook...");
          render.innerHTML = '';
          await load_pyodide();
          await pyrender(raw);
          await init();
          await hideBusy();
        });
      }

      inputs.addEventListener('touchmove', (e) => {
        // Stop propagation on "touchmove".

        e.stopPropagation();
      });

      button_edit.addEventListener("click", async function(e) {
        // Handle the button click: show source or execute source.

        if (busy) {
          return;
        }

        // Load Pyodide and related packages.
        await showBusy();
        await load_pyodide(true);
        await hideBusy();

        busy = true;
        lastText = inputs.value;
        pgcode.classList.toggle('hidden');
        results.classList.toggle('hidden');
        button_run.classList.toggle('hidden');
        button_cancel.classList.toggle('hidden');
        button_edit.classList.toggle('hidden');
        button_share.classList.toggle('hidden');
        textResize(inputs);
        inputs.focus();
        busy = false;
      });

      button_share.addEventListener("click", (e) => {
        // Handle the share click: copy URL with code as parameter.

        if (busy) {
          return;
        }

        busy = true;
        const uri = encodeuri(inputs.value);
        const loc = window.location;
        let pathname = '/playground/';
        if (loc.pathname.startsWith('/coloraide/')) {
          pathname = '/coloraide/playground/'
        }
        const path = loc.protocol + '//' + loc.host + pathname + '?code=' + uri;
        if (uri.length > 1000) {
          alert('Code must be under a 1000 characters to generate a URL!');
        } else {
          navigator.clipboard.writeText(path).then(function() {
            alert('Link copied to clipboard :)');
          }, function() {
            alert('Failed to copy link clipboard!');
          });
        }
        busy = false;
      });

      button_run.addEventListener("click", async function(e) {
        // Handle the button click: show source or execute source.

        if (busy) {
          return;
        }

        busy = true;
        results.querySelector('code').innerHTML = '';
        pyexecute(current_id);
        pgcode.classList.toggle('hidden');
        results.classList.toggle('hidden');
        button_edit.classList.toggle('hidden');
        button_share.classList.toggle('hidden');
        button_run.classList.toggle('hidden');
        button_cancel.classList.toggle('hidden');
        busy = false;
      });

      button_cancel.addEventListener("click", (e) => {
        // Cancel edit.

        if (busy) {
          return;
        }

        busy = true;
        inputs.value = lastText;
        pgcode.classList.toggle('hidden');
        results.classList.toggle('hidden');
        button_edit.classList.toggle('hidden');
        button_share.classList.toggle('hidden');
        button_run.classList.toggle('hidden');
        button_cancel.classList.toggle('hidden');
        busy = false;
      });
    });
  }

  async function main(first) {
    // Load external source to render in a playground.
    // This can be something like a file on a gist we must read in (?source=)
    // or raw code (?code=).

    if (window.location.pathname.endsWith("/playground/")) {
      let params = new URLSearchParams(window.location.search);
      const msg = initialized ? 'Loading Notebook...' : 'Loading Pyodide...';
      const uri = params.has('source') ? params.get('source') : params.get('notebook');
      if (uri != null && uri.trim()) {
        // A source was specified, so load it.
        await showBusy(msg);
        await load_pyodide();
        try {
          const uri = params.has('source') ? params.get('source') : params.get('notebook');
          const gistType = params.has('source') ? 'source' : 'notebook';
          let value = '';
          let xhr = new XMLHttpRequest();
          gist = uri;
          xhr.open("GET", uri, true);
          xhr.onload = async function (e) {
            // Try and load the requested content
            if (xhr.readyState === 4) {
              if (xhr.status === 200) {
                value = xhr.responseText;
              }
            }

            requests = 1;
            if (gistType === 'source') {
              await pyrender(getContent(value));
            } else {
              await pyrender(value);
            }
            await hideBusy();
            await init(first);
          };
          xhr.send();
        } catch (err) {}
      } else if (params.has('code')) {
        gist = '';
        gistType = '';
        await showBusy(msg);
        await load_pyodide();
        await pyrender(getContent(params.get('code')));
        await hideBusy();
        await init(first);
      } else {
        gist = '';
        gistType = '';
        await showBusy(msg);
        await load_pyodide();
        await pyrender(getContent(defContent));
        await hideBusy();
        await init(first);
      }
    } else {
      await init(first);
    }
  }

  // Run main
  document.addEventListener("DOMContentLoaded", async function() {main(true);});
})()
</script>
