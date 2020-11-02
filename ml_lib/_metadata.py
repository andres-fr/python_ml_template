#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
Library metadata. Advantages of keeping it on a separate file:
1. Single, centralized input for this data. Everything else should
   get the information from here.
2. Easily available to the python code AND to any other tool due to
   simple format.
3. setup.py can read it without importing the lib. This is
   very important  https://stackoverflow.com/a/2073599

Usage:
------

The version number is usually managed by an automated tool that
increments it upon releases. The other fields can be manually updated
whenever necessary.
"""

# Version automatically managed. Edit only to set initial value
VERSION = "0.7.1"
AUTHOR = "aferro"  # multiple authors: enumeration separated by ", "
EMAIL = "andres.fernandez@surrey.ac.uk"
LICENSE = "MIT"
SHORT_DESCRIPTION = "A nice library."
URL = "https://github.com/andres-fr/python_ml_template"
