#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script configures a sphinx docs directory from scratch,
using the RTD theme. It is intended to provide CI (e.g. GitHub Actions) with
all it needs to create and release the autodocs, so that the developers don't
have to install the doc-related dependencies like sphinx.

Still, the docs can be manually built if desired and the dependencies are
installed (See below).


.. warning::

  The script DELETES any preexisting contents in the given output directory.

.. info::

  Why does this script exist? This is the result of testing the whole CI
  pipeline from zero, and incrementally adding functionality to this script
  that would be very cumbersome via CLI. We end up pythoning everything.

Usage Example:
==============

In the repo root dir:

.. code-block:: python

  python ci_scripts/sphinx_docs.py -p ml_lib/ -a "aferro" -v "0.1.0" -L -H

Corresponding shell commands are:

.. code-block:: bash

  rm -r docs
  sphinx-quickstart -l en  -p ml_lib -a aferro -v 0.1.0 -r 0.1.0 \
        --ext-githubpages --ext-autodoc --ext-mathjax --ext-viewcode\
        --extensions=sphinx_rtd_theme,sphinx.ext.graphviz docs/
  sphinx-apidoc -o docs/ ml_lib/
  # and optionally
  sphinx-build -M html docs docs/_build
  sphinx-build -M latexpdf docs docs/_build
"""

import sys
import os
import shutil  # to remove folder recursively
import argparse

import sphinx.cmd.quickstart as sphinx_quickstart
import sphinx.ext.apidoc as sphinx_apidoc
import sphinx.cmd.make_mode as sphinx_build

REMOVE_LINE = "html_theme = 'alabaster'\n"
EXTRA_BEGIN = "html_theme = 'sphinx_rtd_theme'"
# Remove blank pages from latex https://stackoverflow.com/a/5741112/4511978
EXTRA_END = "\nlatex_elements = {'extraclassoptions': 'openany,oneside'}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Configure Sphinx Docs")
    parser.add_argument(
        "-p",
        "--package_path",
        type=str,
        required=True,
        help="Path of the Python package to document.",
    )
    parser.add_argument(
        "-a",
        "--author_name",
        type=str,
        required=True,
        help="Can contain whitespaces if quoted.",
    )
    parser.add_argument(
        "-v", "--version", type=str, required=True, help="Version like 0.1.0"
    )
    parser.add_argument(
        "-o",
        "--docs_directory",
        type=str,
        default="docs",
        help="Output path. PREEXISTING WILL BE DELETED.",
    )
    parser.add_argument(
        "-H",
        "--build_html",
        action="store_true",
        help="If given, it will build a HTML.",
    )
    parser.add_argument(
        "-L",
        "--build_latexpdf",
        action="store_true",
        help="If given, it will build a LaTeX PDF.",
    )

    parser.add_argument(
        "-Y",
        "--skip_confirm",
        action="store_true",
        help="If given, delete docs_directory without asking",
    )

    args = parser.parse_args()
    #
    PACKAGE_PATH = os.path.normpath(args.package_path)
    AUTHOR = args.author_name
    VERSION = args.version
    OUT_DIR = args.docs_directory
    BUILD_HTML = args.build_html
    BUILD_PDF = args.build_latexpdf
    SKIP_CONFIRM = args.skip_confirm

    # The GitHub Actions VMs don't include the local path into Pythonpath
    # This causes sphinx apidocs to not find the code. We add one dir above
    # the package to make sure the code gets found
    PACKAGE_PATH = os.path.abspath(PACKAGE_PATH)
    PACKAGE_NAME = os.path.basename(PACKAGE_PATH)
    PACKAGE_PARENT = os.path.abspath(os.path.join(PACKAGE_PATH, os.pardir))
    if PACKAGE_PARENT not in sys.path:
        sys.path.append(PACKAGE_PARENT)

    # Delete outdir if preexisting and create anew
    if not SKIP_CONFIRM:
        answer = input(f"WARNING: delete all contents in {OUT_DIR}? (y/Y): ")
        if answer.lower() != "y":
            print("exiting...")
            sys.exit(0)
    shutil.rmtree(OUT_DIR, ignore_errors=True)
    os.mkdir(OUT_DIR)
    print(f"Replaced {OUT_DIR}!")

    # call sphinx-quickstart with the given arguments
    quickstart_argv = [
        "-q",
        "-l",
        "en",
        "-p",
        PACKAGE_NAME,
        "-a",
        AUTHOR,
        "-v",
        VERSION,
        "-r",
        VERSION,
        # "--makefile", "--batchfile",
        # instead of ext-imgmath?
        "--ext-autodoc",
        "--ext-viewcode",
        "--ext-doctest",
        "--ext-mathjax",
        "--ext-githubpages",
        "--extensions=sphinx_rtd_theme,sphinx.ext.graphviz,sphinx.ext.autodoc",
        OUT_DIR,
    ]

    sphinx_quickstart.main(argv=quickstart_argv)

    # Some parameters are unfortunately hardcoded, so dirty editing:
    conf_py = os.path.join(OUT_DIR, "conf.py")
    with open(conf_py, "r+") as f:  # open in read/write mode:
        lines = f.readlines()
    os.remove(conf_py)
    # remove line, append text at beginning and at end:
    try:
        lines.pop(lines.index(REMOVE_LINE))
    except ValueError:
        print("WARNING: EXPECTED LINE DIDN'T EXIST:", REMOVE_LINE)
    lines.insert(1, EXTRA_BEGIN + "\n")
    lines.append(EXTRA_END + "\n")
    # rewrite edited file to its original path
    with open(conf_py, "w") as f:
        f.writelines(lines)

    # Another dirty hack: the cleanest way to create a fresh apidoc is removing
    # the existing index.rst and running apidoc:
    os.remove(os.path.join(OUT_DIR, "index.rst"))
    apidoc_argv = ["-o", OUT_DIR, "-F", PACKAGE_NAME]
    sphinx_apidoc.main(argv=apidoc_argv)

    # Optionally build the docs:
    build_output = os.path.join(OUT_DIR, "_build")
    if BUILD_HTML:
        build_pdf_args = ["html", OUT_DIR, build_output]
        sphinx_build.run_make_mode(args=build_pdf_args)
    if BUILD_PDF:
        build_pdf_args = ["latexpdf", OUT_DIR, build_output]
        sphinx_build.run_make_mode(args=build_pdf_args)
