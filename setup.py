#!/usr/bin/env python

"""setup.py: Controls the setup process using setuptools."""

import re

from setuptools import setup

version = re.search(
    r'^__version__\s*=\s*"(.*)"',
    open('uppyyl_state_constructor/version.py').read(),
    re.M
).group(1)

with open("README.md", "rb") as f:
    long_description = f.read().decode("utf-8")

setup(
    name="uppyyl_state_constructor",
    packages=["uppyyl_state_constructor"],
    entry_points={
        "console_scripts": [
            'uppyyl_state_constructor = uppyyl_state_constructor.uppyyl_state_constructor:main',
            'uppyyl-state-constructor = uppyyl_state_constructor.uppyyl_state_constructor:main',
        ]
    },
    version=version,
    description="State Constructor for Uppyyl including a CLI tool.",
    long_description=long_description,
    author="Sascha Lehmann",
    author_email="s.lehmann@tuhh.de",
    url="",
    install_requires=[
        'uppyyl_simulator',
        'numpy==1.18.1',
        'pytest==5.3.5',
        'setuptools==49.3.1',
        'colorama==0.4.3',
        'matplotlib==3.2.1'
    ],
)
