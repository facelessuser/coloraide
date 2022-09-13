(() => {
  let pyodide = null
  let busy = false
  let raw = ""
  let gist = ""
  let editTemp = {}
  const reIdNum = /.*?_(\d+)$/
  let initialized = false
  let lastSearch = ""
  let fake = false
  const tabStart = /^( {1,4}|\t)/
  // This is the Python payload that will be executed when the user
  // presses the `Run` button. It will execute the code, create a
  // Python console output, find color references, steps, and interpolation
  // references and render the appropriate preview.
  const pycode = `
{{pycode}}

import micropip
from js import location

action = globals().get('action')
if action == 'notebook':
    callback = render_notebook
else:
    callback = render_console

base = location.pathname.lstrip('/').split('/')[0]
await micropip.install([location.origin + '/{}/playground/{}'.format(base, w) for w in wheels])
callback()
`

  const defContent = window.color_notebook.default_playground

  const getContent = content => {
    return `
!!! new "This notebook is powered by [Pyodide](https://github.com/pyodide/pyodide). \
Learn more [here](\
?notebook=https://gist.githubusercontent.com/facelessuser/7c819668b5eb248ecb9ac608d91391cf/raw/playground.md\
). Preview, convert, interpolate, and explore!"

\`\`\`\`\`\`\`\`playground
${content}
\`\`\`\`\`\`\`\`
`
  }

  const fakeDOMContentLoaded = () => {
    // Send a fake `DOMContentLoaded`
    fake = true
    window.document.dispatchEvent(new Event("DOMContentLoaded", {
      bubbles: true,
      cancelable: true
    }))
  }

  const textResize = inpt => {
    // Resize inputs based on text height.

    const scrollLeft = window.pageXOffset ||
      (document.documentElement || document.body.parentNode || document.body).scrollLeft

    const scrollTop  = window.pageYOffset ||
      (document.documentElement || document.body.parentNode || document.body).scrollTop

    inpt.style.height = "5px"
    inpt.style.height = `${inpt.scrollHeight}px`

    window.scrollTo(scrollLeft, scrollTop)
  }

  const encodeuri = uri => {
    // Encode the URI component.

    return encodeURIComponent(uri).replace(/[.!'()*]/g, c => {
      return `%${c.charCodeAt(0).toString(16)}`
    })
  }

  const pyexecute = async currentID => {
    // Execute Python code inside a playground

    const currentInputs = document.getElementById(`__playground-inputs_${currentID}`)
    currentInputs.setAttribute("readonly", "")
    pyodide.globals.set("id_num", currentID)
    pyodide.globals.set("action", "playground")
    pyodide.globals.set('wheels', window.color_notebook.playground_wheels)
    await pyodide.runPythonAsync(pycode)
    currentInputs.removeAttribute("readonly")
  }

  const pyrender = async text => {
    // Render an entire notebook page

    pyodide.globals.set("content", text)
    pyodide.globals.set("action", "notebook")
    pyodide.globals.set('wheels', window.color_notebook.notebook_wheels)
    await pyodide.runPythonAsync(pycode)
    const src = document.getElementById("__notebook-input")
    if (src) {
      raw = text
      src.value = text
    }
    if (window.location.hash) {
      // Force jumping to hashes
      window.location.href = window.location.href // eslint-disable-line no-self-assign
    }
  }

  const setupPyodide = async() => {
    // Load `Pyodide` and the any default packages we can need and can load.

    if (!initialized) {
      initialized = true
      pyodide = await loadPyodide({ // eslint-disable-line no-undef
        indexURL: "https://cdn.jsdelivr.net/pyodide/v0.20.0/full/",
        fullStdLib: false
      })
      await pyodide.loadPackage(["micropip"])
    }
  }

  const showBusy = (target, label, relative) => {
    // Show busy indicator

    const loaderLabel = (typeof label === "undefined" || label === null) ? "Loading..." : label
    const classes = relative ? "loading relative" : "loading"
    const template = document.createElement("template")
    template.innerHTML = `<div class="${classes}"><div class="loader"></div><div>${loaderLabel}</div></div>`
    target.appendChild(template.content.firstChild)
  }

  const hideBusy = target => {
    // Hide busy indicator

    const loading = target.querySelector(".loading")
    if (loading) {
      target.removeChild(target.querySelector(".loading"))
    }
  }

  const popState = () => {
    // Handle notebook history

    const base = window.location.pathname.split('/')[1]
    if (
      window.location.pathname === `/${base}/playground/`
    ) {
      const current = decodeURIComponent(new URLSearchParams(window.location.search).toString())
      if (current !== lastSearch) {
        main(false) // eslint-disable-line no-use-before-define
      }
    }
  }

  const interceptClickEvent = e => {
    // Catch links to other notebook pages and handle them

    const base = window.location.pathname.split('/')[1]
    const target = e.target || e.srcElement
    if (target.tagName === "A" && main) { // eslint-disable-line no-use-before-define
      if (
        target.getAttribute("href") &&
        target.host === window.location.host &&
        window.location.pathname === `/${base}/playground/"` &&
        window.location.pathname === target.pathname &&
        window.location.search !== target.search
      ) {
        e.preventDefault()
        const search = new URLSearchParams(target.search)
        const state = {}
        for (const [key, value] of search) {
          state[key] = value
        }
        history.pushState(state, "", target.href)
        main(false) // eslint-disable-line no-use-before-define
      }
    }
  }

  const handleTab = e => {
    // Prevent tab from tabbing out.

    if (e.key === 'Tab') {
      const target = e.target

      if (target.selectionStart !== target.selectionEnd) {
        e.preventDefault()

        let start = target.selectionStart
        let end = target.selectionEnd

        const text = target.value

        while (start > 0 && text[start - 1] !== '\n') {
          start--
        }
        while (end > 0 && text[end - 1] !== '\n' && end < text.length) {
          end++
        }

        let lines = text.substr(start, end - start).split('\n')

        for (let i = 0; i < lines.length; i++) {

          // Don't indent last line if cursor at start of line
          if (i === lines.length - 1 && lines[i].length === 0) {
            continue
          }

          // Indent or deindent
          if (e.shiftKey) {
            lines[i] = lines[i].replace(tabStart, '')
          } else {
            lines[i] = `    ${lines[i]}`
          }
        }
        lines = lines.join('\n')

        // Update the text area
        target.value = text.substr(0, start) + lines + text.substr(end)
        target.selectionStart = start
        target.selectionEnd = start + lines.length
      }
    }
  }

  const init = async first => {
    // Setup input highlighting and events to run Python code blocks.

    const notebook = document.getElementById("__notebook-source")
    const playgrounds = document.querySelectorAll(".playground")
    playgrounds.forEach(pg => {

      const currentID = pg.id.replace(reIdNum, "$1")
      const inputs = document.getElementById(`__playground-inputs_${currentID}`)
      const results = document.getElementById(`__playground-results_${currentID}`)
      const pgcode = document.getElementById(`__playground-code_${currentID}`)
      const buttonEdit = document.querySelector(`button#__playground-edit_${currentID}`)
      const buttonShare = document.querySelector(`button#__playground-share_${currentID}`)
      const buttonRun = document.querySelector(`button#__playground-run_${currentID}`)
      const buttonCancel = document.querySelector(`button#__playground-cancel_${currentID}`)

      inputs.addEventListener("input", () => {
        // Adjust textarea height on text input.

        textResize(inputs)
      })

      inputs.addEventListener('keydown', handleTab)

      if (notebook && first) {
        const notebookInput = document.getElementById("__notebook-input")

        notebookInput.addEventListener("input", e => {
          // Adjust textarea height on text input.

          textResize(e.target)
        })

        notebookInput.addEventListener('keydown', handleTab)

        const editPage = document.getElementById("__notebook-edit")
        editPage.addEventListener("click", () => {
          editTemp[notebookInput.id] = notebookInput.value
          document.getElementById("__notebook-render").classList.toggle("hidden")
          document.getElementById("__notebook-source").classList.toggle("hidden")
          textResize(document.getElementById("__notebook-input"))
        })

        document.getElementById("__notebook-md-gist").addEventListener("click", async e => {
          let uri = prompt("Please enter link to the Markdown page source:", gist) // eslint-disable-line no-alert
          if (uri !== null) {
            uri = encodeuri(uri)
            e.preventDefault()
            history.pushState({notebook: uri}, "", `?${new URLSearchParams(`notebook=${uri}`).toString()}`)
            main(false) // eslint-disable-line no-use-before-define
          }
        })

        document.getElementById("__notebook-py-gist").addEventListener("click", async e => {
          let uri = prompt("Please enter the link to the Python code source:", gist) // eslint-disable-line no-alert
          if (uri !== null) {
            uri = encodeuri(uri)
            e.preventDefault()
            history.pushState({source: uri}, "", `?${new URLSearchParams(`source=${uri}`).toString()}`)
            main(false) // eslint-disable-line no-use-before-define
          }
        })

        document.getElementById("__notebook-input").value = raw
        document.getElementById("__notebook-cancel").addEventListener("click", () => {
          notebookInput.value = editTemp[notebookInput.id]
          delete editTemp[notebookInput.id]
          document.getElementById("__notebook-render").classList.toggle("hidden")
          document.getElementById("__notebook-source").classList.toggle("hidden")
        })

        document.getElementById("__notebook-submit").addEventListener("click", async() => {
          const render = document.getElementById("__notebook-render")
          raw = document.getElementById("__notebook-input").value
          render.classList.toggle("hidden")
          document.getElementById("__notebook-source").classList.toggle("hidden")
          const article = document.querySelector("article")
          showBusy(article, "Loading Notebook...")
          render.innerHTML = ""
          editTemp = {}
          await setupPyodide()
          await pyrender(raw)
          await init()
          hideBusy(article)
        })
      }

      inputs.addEventListener("touchmove", e => {
        // Stop propagation on "touchmove".

        e.stopPropagation()
      })

      results.addEventListener("click", e => {
        // Handle clicks on results and copies color from single color swatch when clicked.

        const el = e.target
        if (el.matches('span.swatch-color')) {
          let content = ''
          const parent = el.parentNode
          if (!parent.matches('span.swatch-gradient')) {
            content = parent.getAttribute('title').replace('Copy to clipboard', '')
            content = content.replace('\n', '')
            if (window.clipboardData && window.clipboardData.setData) {
              // Old `IE`` handling, do we really need this?
              return window.clipboardData.setData("Text", content)
            } else if (document.queryCommandSupported && document.queryCommandSupported("copy")) {
              const textarea = document.createElement("textarea")
              textarea.textContent = content
              textarea.style.position = "fixed"
              document.body.appendChild(textarea)
              textarea.select()
              try {
                return document.execCommand("copy")
              } catch (ex) {
                return prompt("Copy to clipboard: Ctrl+C, Enter", content) // eslint-disable-line no-alert
              } finally {
                document.body.removeChild(textarea)
              }
            }
          }
        }
      })

      buttonEdit.addEventListener("click", async() => {
        // Handle the button click: show source or execute source.

        editTemp[currentID] = inputs.value
        pgcode.classList.toggle("hidden")
        results.classList.toggle("hidden")
        buttonRun.classList.toggle("hidden")
        buttonCancel.classList.toggle("hidden")
        buttonEdit.classList.toggle("hidden")
        buttonShare.classList.toggle("hidden")
        textResize(inputs)
        inputs.focus()
      })

      buttonShare.addEventListener("click", async() => {
        // Handle the share click: copy URL with code as parameter.

        const base = window.location.pathname.split('/')[1]
        const uri = encodeuri(inputs.value)
        const loc = window.location
        let pathname = "/playground/"
        if (loc.pathname.startsWith(`/${base}/`)) {
          pathname = `/${base}/playground/`
        }
        const path = `${loc.protocol}//${loc.host}${pathname}?code=${uri}`
        if (path.length > 2000) {
          alert( // eslint-disable-line no-alert
            "Code must be small enough to generate a shareable URL under 2000 characters!"
          )
        } else {
          navigator.clipboard.writeText(path).then(async() => {
            alert("Link copied to clipboard :)") // eslint-disable-line no-alert
          }, async() => {
            alert("Failed to copy link clipboard!") // eslint-disable-line no-alert
          })
        }
      })

      buttonRun.addEventListener("click", async() => {
        // Handle the button click: show source or execute source.

        if (busy) {
          return
        }

        busy = true
        // Load Pyodide and related packages.
        const form = pgcode.querySelector("form")
        showBusy(form, null, true)
        const buttons = document.querySelectorAll(".playground .playground-run")
        if (buttons) {
          buttons.forEach(b => {
            b.setAttribute("disabled", "")
          })
        }
        await setupPyodide()
        results.querySelector("code").innerHTML = ""
        await pyexecute(currentID)
        if (buttons) {
          buttons.forEach(b => {
            b.removeAttribute("disabled")
          })
        }
        hideBusy(form)
        pgcode.classList.toggle("hidden")
        results.classList.toggle("hidden")
        buttonEdit.classList.toggle("hidden")
        buttonShare.classList.toggle("hidden")
        buttonRun.classList.toggle("hidden")
        buttonCancel.classList.toggle("hidden")

        delete editTemp[currentID]
        busy = false
      })

      buttonCancel.addEventListener("click", () => {
        // Cancel edit.

        inputs.value = editTemp[currentID]
        delete editTemp[currentID]
        pgcode.classList.toggle("hidden")
        results.classList.toggle("hidden")
        buttonEdit.classList.toggle("hidden")
        buttonShare.classList.toggle("hidden")
        buttonRun.classList.toggle("hidden")
        buttonCancel.classList.toggle("hidden")
      })
    })
  }

  const main = async first => {
    // Load external source to render in a playground.
    // This can be something like a file on a gist we must read in (?source=)
    // or raw code (?code=).

    editTemp = {}

    if (window.location.pathname.endsWith("/playground/")) {
      const params = new URLSearchParams(window.location.search)
      const loadMsg = "Loading Pyodide..."
      const pageMsg = "Loading Notebook..."
      const uri = params.has("source") ? params.get("source") : params.get("notebook")
      const article = document.querySelector("article")
      if (uri !== null && uri.trim()) {
        // A source was specified, so load it.
        showBusy(article, loadMsg)
        await setupPyodide()
        hideBusy(article)
        showBusy(article, pageMsg)
        try {
          const gistType = params.has("source") ? "source" : "notebook"
          lastSearch = decodeURIComponent(params.toString())
          let value = ""
          const xhr = new XMLHttpRequest()
          gist = uri
          xhr.open("GET", uri, true)
          xhr.onload = async() => {
            // Try and load the requested content
            if (xhr.readyState === 4) {
              if (xhr.status === 200) {
                value = xhr.responseText
              }
            }

            if (gistType === "source") {
              value = getContent(value)
            }
            await pyrender(value)
            await init(first)
            hideBusy(article)
            fakeDOMContentLoaded()
          }
          xhr.send()
        } catch (err) {} // eslint-disable-line no-empty
      } else {
        gist = ""
        const content = getContent(params.has("code") ? params.get("code") : defContent)
        lastSearch = decodeURIComponent(params.toString())
        showBusy(article, loadMsg)
        await setupPyodide()
        hideBusy(article)
        showBusy(article, pageMsg)
        await pyrender(content)
        await init(first)
        hideBusy(article)
        fakeDOMContentLoaded()
      }
    } else {
      gist = ""
      lastSearch = ""
      init(first)
    }
  }

  // Capture links in notebook pages so that we can make playgound links load instantly
  document.addEventListener("click", interceptClickEvent)

  // Handle history of notebook pages as they are loaded dynamically
  window.addEventListener("popstate", popState)

  // Before leaving, turn off fake, just in case we navigated away before finished
  window.addEventListener("unload", () => {
    fake = true
  })

  // Attach main via subscribe (subscribes to Materials on page load and instant page loads)
  window.document$.subscribe(() => {
    // To get other libraries to to reload, we may create a fake `DOMContentLoaded`
    // No need to process these events.
    if (fake) {
      fake = false
      return
    }
    main(true)
  })
})()
