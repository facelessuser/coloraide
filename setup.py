#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup package."""
from setuptools import setup, find_packages
import os
import imp
import traceback


def get_version():
    """Get version and version_info without importing the entire module."""

    path = os.path.join(os.path.dirname(__file__), 'coloraide')
    fp, pathname, desc = imp.find_module('__meta__', [path])
    try:
        vi = imp.load_module('__meta__', fp, pathname, desc).__version_info__
        return vi._get_canonical(), vi._get_dev_status()
    except Exception:
        print(traceback.format_exc())
    finally:
        fp.close()


def get_requirements(req):
    """Load list of dependencies."""

    install_requires = []
    with open(req) as f:
        for line in f:
            if not line.startswith("#"):
                install_requires.append(line.strip())
    return install_requires


def get_description():
    """Get long description."""

    with open("README.md", 'r') as f:
        desc = f.read()
    return desc


VER, DEVSTATUS = get_version()

setup(
    name='coloraide',
    python_requires=">=3.6",
    version=VER,
    keywords='css color',
    description='A color library for CSS colors.',
    long_description=get_description(),
    long_description_content_type='text/markdown',
    author='Isaac Muse',
    author_email='Isaac.Muse@gmail.com',
    url='https://github.com/facelessuser/coloraide',
    packages=find_packages(exclude=['tests', 'tools']),
    install_requires=get_requirements("requirements/project.txt"),
    license='MIT License',
    classifiers=[
        'Development Status :: %s' % DEVSTATUS,
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
