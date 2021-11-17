"""Download necessary wheels and build the `coloraide` wheel."""
import sys
import subprocess
import os
import urllib.request
import glob
import shutil

urls = [
    "https://files.pythonhosted.org/packages/6e/33/1ae0f71395e618d6140fbbc9587cc3156591f748226075e0f7d6f9176522/Markdown-3.3.4-py3-none-any.whl",  # noqa: E501
    "https://files.pythonhosted.org/packages/9a/9a/36f71797fbaf1f4b6cb8debe1ab6d3ec969e8dbc651181f131a16b794d80/pymdown_extensions-9.0-py3-none-any.whl"  # noqa: E501
]
output = 'docs/src/markdown/playground/'
externals = {}
for url in urls:
    externals[os.path.join(output, url.split('/')[-1])] = url


def build_coloraide():
    """Build `coloraide` wheel."""
    cmd = [sys.executable, '-m', 'build', '--wheel', '-o', output]

    if sys.platform.startswith('win'):
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        process = subprocess.Popen(
            cmd,
            startupinfo=startupinfo,
            shell=False,
            env=os.environ.copy()
        )
    else:
        process = subprocess.Popen(
            cmd,
            shell=False,
            env=os.environ.copy()
        )
    process.communicate()

    return process.returncode


def download_wheel(url, dest):
    """Download a wheel."""

    print('Downloading: {}'.format(url))
    response = urllib.request.urlopen(url)
    if response.status != 200:
        print('Failed to download!')
        return 1
    with open(file, 'wb') as f:
        print('Writing: {}'.format(dest))
        f.write(response.read())


if __name__ == "__main__":
    # Clean up all old wheels
    for file in glob.glob(output + '*.whl'):
        if file not in externals.keys():
            os.remove(file)

    # Clean up build directory
    if os.path.exists('build'):
        shutil.rmtree('build')

    # Build `coloraide` wheel
    if build_coloraide():
        sys.exit(1)

    for file, url in externals.items():
        if download_wheel(url, file):
            sys.exit(1)

    sys.exit(0)
