(() => {
  let pyodide = null
  let busy = false
  let raw = ""
  let gist = ""
  const reIdNum = /.*?_(\d+)$/
  let initialized = false
  let lastSearch = ""
  // This is the Python payload that will be executed when the user
  // presses the `Run` button. It will execute the code, create a
  // Python console output, find color references, steps, and interpolation
  // references and render the appropriate preview.
  const pycode = "{{pycode}}"
  const defContent = "import coloraide\ncoloraide.__version__\nColor('red')"

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

  const textResize = inpt => {
    // Resize inputs based on text height.

    inpt.style.height = "5px"
    inpt.style.height = `${inpt.scrollHeight}px`
  }

  const encodeuri = uri => {
    // Encode the URI component.

    return encodeURIComponent(uri).replace(/[.!'()*]/g, c => {
      return `%${c.charCodeAt(0).toString(16)}`
    })
  }

  const pyexecute = async currentID => {
    // Execute Python code

    const currentInputs = document.getElementById(`__playground-inputs_${currentID}`)
    currentInputs.setAttribute("readonly", "")
    pyodide.globals.set("id_num", currentID)
    pyodide.globals.set("action", "notebook")
    await pyodide.runPythonAsync(pycode)
    currentInputs.removeAttribute("readonly")
  }

  const pyrender = async text => {
    // Execute Python code

    pyodide.globals.set("content", text)
    pyodide.globals.set("action", "render")
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
        indexURL: "https://cdn.jsdelivr.net/pyodide/v0.18.1/full/",
        fullStdLib: false
      })
      await pyodide.loadPackage(["micropip", "Pygments"])
    }
  }

  const showBusy = (target, label, relative) => {
    const loaderLabel = (typeof label === "undefined" || label === null) ? "Loading..." : label
    const classes = relative ? "loading relative" : "loading"
    const template = document.createElement("template")
    template.innerHTML = `<div class="${classes}"><div class="loader"></div><div>${loaderLabel}</div></div>`
    target.appendChild(template.content.firstChild)
  }

  const hideBusy = target => {
    const loading = target.querySelector(".loading")
    if (loading) {
      target.removeChild(target.querySelector(".loading"))
    }
  }

  const popState = e => {
    if (
      window.location.pathname === "/coloraide/playground/"
    ) {
      const current = decodeURIComponent(new URLSearchParams(window.location.search).toString())
      if (current !== lastSearch) {
        main(false) // eslint-disable-line no-use-before-define
      }
    }
  }

  const interceptClickEvent = e => {
    const target = e.target || e.srcElement
    if (target.tagName === "A" && main) { // eslint-disable-line no-use-before-define
      if (
        target.getAttribute("href") &&
        target.host === window.location.host &&
        window.location.pathname === "/coloraide/playground/" &&
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

      if (notebook && first) {
        document.getElementById("__notebook-input").addEventListener("input", e => {
          // Adjust textarea height on text input.

          textResize(e.target)
        })

        const editPage = document.getElementById("__notebook-edit")
        editPage.addEventListener("click", () => {
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

      buttonEdit.addEventListener("click", async() => {
        // Handle the button click: show source or execute source.

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

        const uri = encodeuri(inputs.value)
        const loc = window.location
        let pathname = "/playground/"
        if (loc.pathname.startsWith("/coloraide/")) {
          pathname = "/coloraide/playground/"
        }
        const path = `${loc.protocol}//${loc.host}${pathname}?code=${uri}`
        if (uri.length > 1000) {
          alert("Code must be under a 1000 characters to generate a URL!") // eslint-disable-line no-alert
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
        busy = false
      })

      buttonCancel.addEventListener("click", () => {
        // Cancel edit.

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
      }
    } else {
      gist = ""
      lastSearch = ""
      init(first)
    }
  }

  // Capture links in notebook pages so that we can make playgound links load instantly
  document.addEventListener("click", interceptClickEvent)

  // Handle history of pages on notebooks as they are loaded dynamically
  window.addEventListener("popstate", popState)

  // Attach main via subscribe (subscribes to Materials on page load and instant page loads)
  window.document$.subscribe(() => {
    main(true)
  })
})()
