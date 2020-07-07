#!/usr/bin/env python

import json
import os

from setuptools import setup, find_packages

_README_FILE = "./README.md"
_REQUIREMENTS_FILE = "./requirements.txt"

with open(_README_FILE, "r") as file:
    long_description = file.read()

with open(_REQUIREMENTS_FILE, "r") as file:
    requirements = file.read().splitlines()

pjoin = os.path.join
here = os.path.abspath(os.path.dirname(__file__))
version_ns = {}
with open(pjoin(here, "phc", "version.py")) as f:
    exec(f.read(), {}, version_ns)

setup(
    name="phc",
    version=version_ns["__version__"],
    description="Python interface for the PHC.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://lifeomic.github.io/phc-sdk-py",
    license="MIT",
    author="LifeOmic Development",
    author_email="development@lifeomic.com",
    packages=find_packages(exclude=("tests")),
    install_requires=requirements,
    include_package_data=True,
    extras_require={"pandas": ["pandas"], "tqdm": ["tqdm"]},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Intended Audience :: Healthcare Industry",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Topic :: Utilities",
    ],
)
