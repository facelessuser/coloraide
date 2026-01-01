"""Download necessary wheels and build the `coloraide` wheel."""
import sys
import subprocess
import os
import urllib.request
import urllib.error
import glob
import shutil
import re
import hashlib

# Notebook specific wheels
NOTEBOOK_WHEELS = [
    "https://files.pythonhosted.org/packages/70/81/54e3ce63502cd085a0c556652a4e1b919c45a446bd1e5300e10c44c8c521/markdown-3.10-py3-none-any.whl",  # noqa: E501
    "https://files.pythonhosted.org/packages/ea/10/47caf89cbb52e5bb764696fd52a8c591a2f0e851a93270c05a17f36000b5/pymdown_extensions-10.20-py3-none-any.whl"  # noqa: E501
]

NOTEBOOK_PYODIDE_PKGS = [
    'pyyaml'
]

# Wheels required in addition to the current project
PLAYGROUND_WHEELS = [
    "https://files.pythonhosted.org/packages/c7/21/705964c7812476f378728bdf590ca4b771ec72385c533964653c68e86bdc/pygments-2.19.2-py3-none-any.whl"  # noqa: E501
]

PLAYGROUND_PYODIDE_PKGS = ['micropip']

ZENSICAL_YML = 'docs/src/zensical.yml'

RE_CONFIG = re.compile(r'playground-config.*?\.js')
RE_BUILD = re.compile(r'Successfully built ([-_0-9.a-zA-Z]+?\.whl)')

CONFIG = """\
var colorNotebook = {{
    "playgroundWheels": {},
    "notebookWheels": {},
    "defaultPlayground": "import coloraide\\ncoloraide.__version__\\nColor('red')"
}}
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

    print(f'Downloading: {url}')
    status = 0
    try:
        response = urllib.request.urlopen(url)
        status = response.status
        if status == 200:
            status = 0
            with open(dest, 'wb') as f:
                print(f'Writing: {dest}')
                f.write(response.read())
    except urllib.error.HTTPError as e:
        status = e.status

    if status:
        print(f'Failed to download, recieved status code {status}')

    return status


if __name__ == "__main__":

    status = 0

    # Clean up all old wheels
    for file in glob.glob(OUTPUT + '*.whl'):
        if file not in NOTEBOOK.keys() and file not in PLAYGROUND.keys():
            os.remove(file)

    for file in glob.glob('docs/theme/playground-config*.js'):
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
                print(f'Skipping: {file}')
                continue
            status = download_wheel(url, file)
            if status:
                break
    if not status:
        for file, url in PLAYGROUND.items():
            if os.path.exists(file):
                print(f'Skipping: {file}')
                continue
            status = download_wheel(url, file)
            if status:
                break

    if not status:
        # Build up a list of wheels needed for playgrounds and notebooks
        playground = PLAYGROUND_PYODIDE_PKGS + [os.path.basename(x) for x in PLAYGROUND.keys()] + [package]
        notebook = NOTEBOOK_PYODIDE_PKGS + [os.path.basename(x) for x in NOTEBOOK.keys()] + playground

        # Create the config that specifies which wheels need to be used
        config = CONFIG.format(str(playground), str(notebook)).replace('\r', '').encode('utf-8')
        m = hashlib.sha256()
        m.update(b'playground-config.js')
        m.update(b':')
        m.update(config)
        hsh = m.hexdigest()[0:8]
        with open(f'docs/theme/playground-config-{hsh}.js', 'wb') as f:
            f.write(config)

        for demo in ['colorpicker', '3d_models']:
            colorpicker = ''
            with open(f'docs/src/markdown/examples/{demo}.html') as f:
                colorpicker = re.sub(r"(?m)(^[ ]*let package = ').*?(')", fr'\1{package}\2', f.read())
            if colorpicker:
                with open(f'docs/src/markdown/examples/{demo}.html', 'w') as f:
                    f.write(colorpicker)

        # Update `mkdocs` source to reference wheel config
        with open(ZENSICAL_YML, 'rb') as f:
            mkdocs = f.read().decode('utf-8')
        mkdocs = RE_CONFIG.sub(f'playground-config-{hsh}.js', mkdocs)
        with open(ZENSICAL_YML, 'wb') as f:
            f.write(mkdocs.encode('utf-8'))

    print("FAILED :(" if status else "SUCCESS :)")
    sys.exit(status)
