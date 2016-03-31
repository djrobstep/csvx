#!/usr/bin/env python

import os

from setuptools import setup, find_packages
from setuptools.command.install import install as _install

with open('README.rst') as f:
    readme = f.read()


setup(
    name='csvx',
    version='0.1.1459403998',
    description='csvx: painless csv',
    long_description=readme,
    author='Robert Lechte',
    author_email='robertlechte@gmail.com',
    install_requires=[
        'six'
    ],
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha'
    ]
)
