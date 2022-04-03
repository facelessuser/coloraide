"""Download necessary wheels and build the `coloraide` wheel."""
import sys
import subprocess
import os
import urllib.request
import urllib.error
import glob
import shutil

urls = [
    "https://files.pythonhosted.org/packages/6e/33/1ae0f71395e618d6140fbbc9587cc3156591f748226075e0f7d6f9176522/Markdown-3.3.4-py3-none-any.whl",  # noqa: E501
    "https://files.pythonhosted.org/packages/9a/9a/36f71797fbaf1f4b6cb8debe1ab6d3ec969e8dbc651181f131a16b794d80/pymdown_extensions-9.0-py3-none-any.whl",  # noqa: E501
]


def get_version():
    """Get version and version_info without importing the entire module."""

    import importlib.util

    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'coloraide', '__meta__.py')
    spec = importlib.util.spec_from_file_location("__meta__", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    vi = module.__version_info__
    return vi._get_canonical()


# Keep a compatible version in the repository so we can always release docs.
# If we ever have a breaking change, we can patch `coloraide-extras` before
# the release, locally upload it and then make a release.
# Afterwards, once `coloraide` is available, we can release the official
# `coloraide-extras`. This prevents our documentation from ever breaking.
EXTRA_VERSION = '0.3.0'
EXTRA_WHEEL = 'coloraide_extras-{}-py3-none-any.whl'.format(EXTRA_VERSION)
keep = {EXTRA_WHEEL}
EXTRAS = "https://raw.githubusercontent.com/facelessuser/coloraide/{{}}/docs/src/markdown/playground/{}".format(
    EXTRA_WHEEL
)
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


if __name__ == "__main__":
    # Clean up all old wheels
    for file in glob.glob(output + '*.whl'):
        if file not in externals.keys() and os.path.basename(file) not in keep:
            os.remove(file)

    # Clean up build directory
    if os.path.exists('build'):
        shutil.rmtree('build')

    # Build `coloraide` wheel
    if build_coloraide():
        sys.exit(1)

    # Get dependencies
    for file, url in externals.items():
        if os.path.exists(file):
            print('Skipping: {}'.format(file))
            continue
        status = download_wheel(url, file)
        if status:
            sys.exit(status)

    # Get coloraide-extras. If we can't find it in the version's tag,
    # tag may not be created with this version, particularly during development,
    # attempt on master
    extras = EXTRAS.format(get_version())
    extra_output = os.path.join(output, extras.split('/')[-1])
    if not os.path.exists(extra_output):
        status = download_wheel(extras, extra_output)
        if status:
            print(
                (
                    'Could not find ColorAide Extras at tag {},'
                    'tag may not have been created yet, try to grab latest on master'
                ).format(get_version())
            )
            extras = EXTRAS.format('master')
            extra_output = os.path.join(output, extras.split('/')[-1])
            status = download_wheel(extras, extra_output)
            if status:
                print('No available ColorAide Extras on master')
    else:
        status = 0
        print('Skipping: {}'.format(extra_output))

    print("FAILED :(" if status else "SUCCESS :)")

    sys.exit(status)
