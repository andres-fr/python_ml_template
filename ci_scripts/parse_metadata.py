#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
The file ``_metadata.py`` is a good way to have a centralized, Python-friendly,
parser-friendly place for all the package's metadata.

This (rudimentary) script makes easier to retrieve that metadata from CLI.

Usage example::
  python ci_scripts/parse_metadata.py -p ml_lib/_metadata.py -f VERSION
"""

import os
import argparse


def parse_file(metadata_path):
    """
    For every line that contains a ``=``, remove the comments and
    return the segments before and after the ``=`` as a dictionary of
    (trimmed) strings.
    """
    with open(os.path.join(metadata_path), "r") as f:
        metadata = [line.split("=") for line in f.readlines() if "=" in line]
        metadata = {k.strip(): v.split("#")[0].strip() for k, v in metadata}
        return metadata


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Configure Sphinx Docs")
    parser.add_argument(
        "-p",
        "--metadata_path",
        type=str,
        required=True,
        help="Path of the Python metadata file.",
    )
    parser.add_argument(
        "-f",
        "--field_name",
        type=str,
        required=True,
        help="metadatafield name to be retrieved",
    )

    args = parser.parse_args()
    #
    METADATA_PATH = os.path.normpath(args.metadata_path)
    FIELD_NAME = args.field_name

    metadata = parse_file(METADATA_PATH)
    print(metadata[FIELD_NAME])
