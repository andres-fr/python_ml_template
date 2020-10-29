#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
python ci_scripts/commitizen_bump.py --dry_run --yes --changelog -P ml_lib/_metadata.py -v 0.1.0
"""

import os
import argparse


from commitizen.config import BaseConfig, TomlConfig
from commitizen.commands.bump import Bump


class NoFileConfig(TomlConfig):
    """
    Like super but all file-related ops have been removed.
    """

    def __init__(self):
        """"""
        BaseConfig.__init__(self)

    def init_empty_config_content(self):
        """"""
        pass

    def set_key(self, key, value):
        """"""
        return self


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Bump with custom filepaths")

    # these arguments replace the static config-based ones
    parser.add_argument(
        "-P",
        "--v_paths",
        nargs="+",
        required=True,
        type=str,
        help="Paths to the to-be-updated version files",
    )
    parser.add_argument(
        "-v",
        "--current_version",
        type=str,
        required=True,
        help="Semantic version like 1.0.23",
    )
    # these arguments are simple wrappers
    parser.add_argument(
        "--dry_run",
        action="store_true",
        help="If given, the command will print but not change anything.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="If given, the command will automatically take yes as the answer.",
    )
    parser.add_argument(
        "--changelog",
        action="store_true",
        help="Generate the changelog for the newest version.",
    )
    # parser.add_argument(
    #     "--check_consistency",
    #     action="store_true",
    #     help="check consistency among versions defined in version files.",
    # )

    args = parser.parse_args()
    #
    V_PATHS = [os.path.normpath(p) for p in args.v_paths]
    VERSION = args.current_version
    #
    DRY_RUN = args.dry_run
    YES = args.yes
    CHANGELOG = args.changelog
    # CHECK_CONSISTENCY = args.check_consistency
    # Update config and args with our custom args
    CONFIG = NoFileConfig()
    CONFIG._settings["version_files"].extend(V_PATHS)
    CONFIG.update({"version": VERSION})
    ARGUMENTS = {
        "tag_format": None,
        "prerelease": None,
        "increment": None,
        "bump_message": None,
        "changelog": CHANGELOG,
        "no_verify": False,
        "check_consistency": True,
        # 'name': None,
        # 'debug': False,
        "dry_run": DRY_RUN,
        "files_only": False,
        "yes": YES,  # yes!
    }

    # Run the bump action
    # import pdb; pdb.set_trace()
    bmp = Bump(config=CONFIG, arguments=ARGUMENTS)
    bmp()
