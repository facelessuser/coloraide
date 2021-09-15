<script src="https://cdn.jsdelivr.net/pyodide/v0.18.0/full/pyodide.js"></script>

<script type="text/javascript">
(() => {
  let pyodide = null;
  let busy = false;
  let requests = 0;
  let lastText = '';
  const reIdNum = /.*?_(\d+)$/;
  let initialized = false;
  // This is the Python payload that will be executed when the user
  // presses the `Run` button. It will execute the code, create a
  // Python console output, find color references, steps, and interpolation
  // references and render the appropriate preview.
  const pycode = `
--8<-- "playground.txt"
`

  async function textResize(inputs) {
    // Resize inputs based on text height.

    inputs.style.height = "5px";
    inputs.style.height = (inputs.scrollHeight) + "px";
  };

  async function pyexecute(current_id) {
    // Execute Python code

    const current_inputs = document.getElementById(`__playground-inputs_${current_id}`);
    current_inputs.setAttribute('readonly', '');
    pyodide.globals.set('id_num', current_id);
    await pyodide.runPythonAsync(pycode);
    current_inputs.removeAttribute('readonly');
  }

  async function load_pyodide() {
    // Load `Pyodide`` and the any default packages we can need and can load.

    if (!initialized) {
      const buttons = document.querySelectorAll('.playground button');
      if (buttons) {
        buttons.forEach((b) => {
          b.setAttribute('disabled', '');
          if (b.classList.contains('playground-edit')) {
            b.innerHTML = 'Loading...';
          }
        });
      }
      initialized = true;
      pyodide = await loadPyodide({indexURL : "https://cdn.jsdelivr.net/pyodide/v0.18.0/full/" });
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

  async function loadExternalSrc() {
    // Load external source to render in a playground.
    // This can be something like a file on a gist we must read in (?source=)
    // or raw code (?code=).

    if (window.location.pathname.endsWith("/playground/")) {
      const pginputs = document.querySelector('.playground-inputs');
      const pg_id = pginputs.id.replace(reIdNum, '$1');
      const pg_results = document.getElementById(`__playground-results_${pg_id}`).querySelector('code');
      let params = new URLSearchParams(window.location.search);
      if (params.has('source')) {
        // A source was specified, so load it.
        pg_results.innerHTML = '';
        pginputs.value = ''
        await load_pyodide();
        try {
          const uri = params.get('source');
          let xhr = new XMLHttpRequest();
          xhr.open("GET", uri, true);
          xhr.onload = function (e) {
            // Try and load the requested content
            if (xhr.readyState === 4) {
              if (xhr.status === 200) {
                pginputs.value = xhr.responseText;
              }
            }
            requests = 1;
            pyexecute(pg_id);
          };
          xhr.send();
        } catch (err) {}
      } else if (params.has('code')) {
        // Raw code provided.
        pg_results.innerHTML = '';
        pginputs.value = ''
        await load_pyodide();
        requests = 1;
        pginputs.value = params.get('code');
        pyexecute(pg_id);
      }
    }
  }

  async function main() {
    // Setup input highlighting and events to run Python code blocks.

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
      const default_text = "# Insert your code here!\ncoloraide.__version__\nColor('red')";

      inputs.addEventListener("input", (e) => {
        // Adjust textarea height on text input.

        textResize(inputs);
      });

      document.addEventListener("keydown", (e) => {
        // Ctrl + Enter in textarea will execute the code.

        if (event.defaultPrevented) {
          return; // Do nothing if the event was already processed
        }

        if (
          e.ctrlKey &&
          e.key === "Enter" &&
          button_edit.classList.contains('hidden') &&
          inputs === document.activeElement
        ) {
          button_run.click();
        } else if (
          e.key === "Escape" &&
          button_edit.classList.contains('hidden') &&
          inputs === document.activeElement
        ) {
          button_cancel.click();
        }
      });

      inputs.addEventListener('touchmove', (e) => {
        // Stop propogation on "touchmove".

        e.stopPropagation();
      });

      button_edit.addEventListener("click", async function(e) {
        // Handle the button click: show source or execute source.

        if (busy) {
          return;
        }

        // Load Piodide and related packages.
        await load_pyodide();

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
        const uri = encodeURIComponent(inputs.value).replace(/[.!'()*]/g, (c) => {
          return '%' + c.charCodeAt(0).toString(16);
        });
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
        requests++;
      });
    });

    await loadExternalSrc();
  }

  // Run main
  main();
})()
</script>
