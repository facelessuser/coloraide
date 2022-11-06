"""Download necessary wheels and build the `coloraide` wheel."""
import sys
import subprocess
import os
import urllib.request
import urllib.error
import glob
import shutil
import re

# Notebook specific wheels
NOTEBOOK_WHEELS = [
    "https://files.pythonhosted.org/packages/6e/33/1ae0f71395e618d6140fbbc9587cc3156591f748226075e0f7d6f9176522/Markdown-3.3.4-py3-none-any.whl",  # noqa: E501
    "https://files.pythonhosted.org/packages/f1/e0/1ed09f66cd1648f8e009120debf9b7d67596fb688e53e71522da1daa02a0/pymdown_extensions-9.5-py3-none-any.whl",  # noqa: E501
]

# Wheels required in addition to the current project
PLAYGROUND_WHEELS = [
    "https://files.pythonhosted.org/packages/5c/8e/1d9017950034297fffa336c72e693a5b51bbf85141b24a763882cf1977b5/Pygments-2.12.0-py3-none-any.whl"  # noqa: E501
]

MKDOCS_YML = 'docs/src/mkdocs.yml'

RE_BUILD = re.compile(r'Successfully built ([-_0-9.a-zA-Z]+?\.whl)')

CONFIG = """\
const colorNotebook = {{
  "playgroundWheels": {}, // eslint-disable-line max-len
  "notebookWheels": {}, // eslint-disable-line max-len
  "defaultPlayground": "import coloraide\\ncoloraide.__version__\\nColor('red')" // eslint-disable-line max-len
}};
"""

OUTPUT = 'docs/src/markdown/playground/'

NOTEBOOK = {}
for url in NOTEBOOK_WHEELS:
    NOTEBOOK[os.path.join(OUTPUT, url.split('/')[-1])] = url

PLAYGROUND = {}
for url in PLAYGROUND_WHEELS:
    PLAYGROUND[os.path.join(OUTPUT, url.split('/')[-1])] = url


def build_package():
    """Build `coloraide` wheel."""
    cmd = [sys.executable, '-m', 'build', '--wheel', '-o', OUTPUT]

    if sys.platform.startswith('win'):
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            startupinfo=startupinfo,
            shell=False,
            env=os.environ.copy()
        )
    else:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            shell=False,
            env=os.environ.copy()
        )
    out, _ = process.communicate()
    m = RE_BUILD.search(out.decode('utf-8'))

    return process.returncode, m.group(1) if m else ''


def download_wheel(url, dest):
    """Download a wheel."""

    print('Downloading: {}'.format(url))
    status = 0
    try:
        response = urllib.request.urlopen(url)
        status = response.status
        if status == 200:
            status = 0
            with open(dest, 'wb') as f:
                print('Writing: {}'.format(dest))
                f.write(response.read())
    except urllib.error.HTTPError as e:
        status = e.status

    if status:
        print('Failed to download, recieved status code {}'.format(status))

    return status


def replace_config(m, config):
    """Replace config."""

    return m.group(1) + config + m.group(3)


if __name__ == "__main__":

    status = 0

    # Clean up all old wheels
    for file in glob.glob(OUTPUT + '*.whl'):
        if file not in NOTEBOOK.keys() and file not in PLAYGROUND.keys():
            os.remove(file)

    # Clean up build directory
    if os.path.exists('build'):
        shutil.rmtree('build')

    # Build wheel
    status, package = build_package()
    if not status:
        # Get dependencies
        for file, url in NOTEBOOK.items():
            if os.path.exists(file):
                print('Skipping: {}'.format(file))
                continue
            status = download_wheel(url, file)
            if status:
                break
    if not status:
        for file, url in PLAYGROUND.items():
            if os.path.exists(file):
                print('Skipping: {}'.format(file))
                continue
            status = download_wheel(url, file)
            if status:
                break

    if not status:
        # Build up a list of wheels needed for playgrounds and notebooks
        playground = [os.path.basename(x) for x in PLAYGROUND.keys()] + [package]
        notebook = [os.path.basename(x) for x in NOTEBOOK.keys()] + playground

        # Create the config that specifies which wheels need to be used
        config = CONFIG.format(str(playground), str(notebook)).replace('\r', '')
        with open('docs/src/js/extra-notebook.js', 'r', encoding='utf-8') as f:
            content = f.read()

        content = re.sub(
            r'(?ms)^(// notebook-config: start\r?\n)(.*)?(^// notebook-config: end\r?\n)',
            lambda x, config=config: replace_config(x, config),
            content
        )

        with open('docs/src/js/extra-notebook.js', 'w', encoding='utf-8') as f:
            f.write(content)

    print("FAILED :(" if status else "SUCCESS :)")
    sys.exit(status)
