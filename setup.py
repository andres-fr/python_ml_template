#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is an adaption of the typical setup.py file, following the principle
of removing most of the repo-specific contents. I.e., it can be used in
multiple repos with minimal modifications. This makes it suitable for
templating.

This design may seem unnecessary, but seems to be the only one that allows for
a python-sourced, unique-location, setuptools-compatible, parameterless tracking
of metadata like lib name or (most importantly) version. For more info see::

  https://stackoverflow.com/a/2073599

Usage example::
  python setup.py sdist bdist_wheel -p ml_lib/ -m ml_lib/_metadata.py \
    -I ml_lib/data LICENSE -E tests tests.*
"""

import sys
import os
import argparse
from setuptools import setup, find_packages
from ci_scripts.parse_metadata import parse_file


# ##############################################################################
# # HELPERS
# ##############################################################################


def get_files_recursive(path):
    """
    Usually we want to recursively include a folder with non-Python data into
    the Python distribution. This can be done with MANIFEST.in, but we prefer
    a centralized and automated way of resolving the paths. I.e. if the library
    name changes, no inconsistent MANIFEST is left behind. For that, we gather
    the paths with this function(source: https://stackoverflow.com/a/36693250).

    :param str dir_path: Path to the directory that will be recursively
      traversed.
    :returns: A list of all the paths to files in the ``dir_path`` as strings.
    """
    if os.path.isfile(path):
        return [os.path.join("..", path)]
    # else
    paths = []
    for (pth, _, filenames) in os.walk(path):  # ignore directories
        for filename in filenames:
            paths.append(os.path.join("..", pth, filename))
    return paths


# ##############################################################################
# # CONFIG/GLOBALS
# # Instead of hardcoding all of them, pass them as CLI parameters (this makes
# # CI more flexible, and less boilerplate for Cookiecutter etc)
# ##############################################################################
parser = argparse.ArgumentParser("A regular setup.py command with added flags")
# these arguments replace the static config-based ones
parser.add_argument(
    "-p",
    "--package_name",
    type=str,
    required=True,
    help="Name of the Python library to be packaged. Must be in same directory",
)

parser.add_argument(
    "-m",
    "--metadata_path",
    type=str,
    required=True,
    help="Path to the Python file with metadata variables to be parsed",
)
parser.add_argument(
    "-I",
    "--include_files",
    nargs="+",
    type=str,
    default=[],
    help="Paths to the extra files to be included (e. g. LICENSE)",
)
parser.add_argument(
    "-E",
    "--exclude_packages",
    nargs="+",
    type=str,
    default=["tests.*", "tests", "*.tests", "*.tests.*"],
    help="Patterns to be excluded from the package, usually tests. See default",
)

args, unknown_args = parser.parse_known_args()
sys.argv = sys.argv[0:1] + unknown_args  # pass the remaining args to setup
#
PACKAGE_NAME = args.package_name
METADATA_PATH = os.path.normpath(args.metadata_path)
EXTRA_FILES = sum([get_files_recursive(f) for f in args.include_files], [])
EXCLUDE_PACKAGES = args.exclude_packages

# The "Rigid" part: we still assume a certain metadata structure
METADATA = parse_file(METADATA_PATH)
METADATA = {k: v.replace('"', "") for k, v in METADATA.items()}
with open("README.md", encoding="utf-8") as fh:
    LONG_DESCRIPTION = fh.read()

# ##############################################################################
# # SETUP
# #############################################################################
setup(
    name=PACKAGE_NAME,
    version=METADATA["VERSION"],
    author=METADATA["AUTHOR"],
    author_email=METADATA["EMAIL"],
    url=METADATA["URL"],
    description=METADATA["SHORT_DESCRIPTION"],
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    license=METADATA["LICENSE"],
    python_requires=">=3.6",
    install_requires=[
        # "pyyaml",
        # "numpy",
        # "scipy",
        # "pandas",
        # "torch",
        # "pytorch-lightning>=0.8,<0.10.0",
        # "torch_optimizer",
        # "soundfile",
        # "pb_bss_eval",
        # "torch_stoi",
    ],
    # extras_require={
    #     "tests": ["pytest"],
    # },
    # entry_points={
    #     "console_scripts": [
    #         "asteroid-upload=asteroid.scripts.asteroid_cli:upload",
    #         "asteroid-infer=asteroid.scripts.asteroid_cli:infer",
    #     ],
    # },
    packages=find_packages(exclude=EXCLUDE_PACKAGES),
    include_package_data=True,
    package_data={"": EXTRA_FILES},
    classifiers=[
        # "Development Status :: 4 - Beta",
        # "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        # "Programming Language :: Python :: 3.7",
        # "Programming Language :: Python :: 3.8",
        # "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
