#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ATM commitizen just supports bumping via config file. Since we want a more
interactive approach

python ci_scripts/commitizen_bump.py --dry_run --yes --changelog -P ml_lib/_metadata.py -v 0.1.0
"""

import os
import argparse
from packaging.version import Version

from commitizen import bump, git, out  # , cmd, factory, git, out

# from commitizen.config import BaseConfig, TomlConfig
from commitizen.commands.bump import Bump
from commitizen.cz import registry

from commitizen.exceptions import (
    BumpCommitFailedError,
    BumpTagFailedError,
    DryRunExit,
    ExpectedExit,
    NoCommitsFoundError,
    NoneIncrementExit,
    # NoPatternMapError,
    NotAGitProjectError,
    # NoVersionSpecifiedError,
)


class ConfiglessBump(Bump):
    """
    Adaption of ``commitizen.commands.bump.Bump`` with an explicit interface
    """

    def __init__(self, commiter_name="cz_conventional_commits"):
        """"""
        if not git.is_git_project():
            raise NotAGitProjectError()
        self.cz = self._get_commiter(commiter_name)

    def _get_commiter(self, commiter_name):
        """"""
        msg_error = (
            "The committer has not been found in the system.\n\n"
            f"Try running 'pip install {commiter_name}'\n"
        )
        assert commiter_name in registry, msg_error
        return registry[commiter_name]

    def __call__(
        self,
        current_version,
        version_filepaths=[],
        increment=None,
        prerelease=None,
        dry_run=False,
        autoconfirm_initial_tag=True,
        tag_format=None,
        bump_commit_message=None,
        check_consistency=True,
        update_files_only=False,
        no_verify=False,
        # changelog_path=None,
    ):
        """
        :param str current_version: Semantic version e.g. '0.1.0'
        :param str changelog_path: If given, save changelog there

        """
        # THE FOLLOWING CODE DOESN'T HAVE SIDE EFFECTS TO FILESYS OR GIT:
        current_version_instance = Version(current_version)
        current_tag_version = bump.create_tag(current_version, tag_format=tag_format)
        #
        is_initial = self.is_initial_tag(current_tag_version, autoconfirm_initial_tag)
        if is_initial:
            commits = git.get_commits()
        else:
            commits = git.get_commits(current_tag_version)
        #
        if not commits and not current_version_instance.is_prerelease:
            raise NoCommitsFoundError("[NO_COMMITS_FOUND]\n" "No new commits found.")
        #
        if increment is None:
            increment = self.find_increment(commits)
        #
        if prerelease is not None and current_version_instance.is_prerelease:
            increment = None
        #
        new_version = bump.generate_version(
            current_version, increment, prerelease=prerelease
        )
        new_tag_version = bump.create_tag(new_version, tag_format=tag_format)
        message = bump.create_commit_message(
            current_version, new_version, bump_commit_message
        )
        # Report found information
        out.write(
            f"{message}\n"
            f"tag to create: {new_tag_version}\n"
            f"increment detected: {increment}\n"
        )
        #
        if increment is None and new_tag_version == current_tag_version:
            raise NoneIncrementExit()
        #
        if dry_run:
            raise DryRunExit()
        # SIDE EFFECTS TO FILESYSTEM: UPDATE TAG IN VERSION_FILEPATHS
        bump.update_version_in_files(
            current_version,
            new_version.public,
            version_filepaths,
            check_consistency=check_consistency,
        )
        if update_files_only:
            out.write(
                "[update_files_only=True]: Done updating files "
                + f"{version_filepaths}. "
            )
            raise ExpectedExit()
        # # SIDE EFFECTS TO FILESYSTEM: CREATE CHANGELOG
        # if self.changelog:
        #     changelog_cmd = Changelog(
        #         self.config,
        #         {
        #             "unreleased_version": new_tag_version,
        #             "incremental": True,
        #             "dry_run": dry_run,
        #         },
        #     )
        #     changelog_cmd()
        #     c = cmd.run(f"git add {changelog_cmd.file_name}")
        #
        # SIDE EFFECTS TO GIT: TAG AND COMMIT
        try:
            commit_args = "-a"
            if no_verify:
                commit_args += " --no-verify"
            c = git.commit(message, args=commit_args)
            if c.return_code != 0:
                raise BumpCommitFailedError(f'git.commit error: "{c.err.strip()}"')
        except Exception as e:
            # If commit went bad (e.g. due to pre-commit errors), roll
            # back the version updates in filesystem to prevent future
            # "inconsistency errors". Swapping seems to do the trick.
            bump.update_version_in_files(
                new_version.public,  # swapped!
                current_version,  # swapped!
                version_filepaths,
                check_consistency=check_consistency,
            )
            raise e
        #
        c = git.tag(new_tag_version)
        if c.return_code != 0:
            raise BumpTagFailedError(c.err)
        out.success("Done!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Bump with custom filepaths")
    parser.add_argument(
        "-v",
        "--current_version",
        type=str,
        required=True,
        help="Semantic version like 1.0.23",
    )
    parser.add_argument(
        "-P",
        "--v_paths",
        nargs="+",
        required=True,
        type=str,
        help="Paths to the to-be-updated version files",
    )
    parser.add_argument(
        "--dry_run",
        action="store_true",
        help="If given, the command will print but not change anything.",
    )
    # parser.add_argument(
    #     "--changelog",
    #     action="store_true",
    #     help="Generate the changelog for the newest version.",
    # )
    # parser.add_argument(
    #     "--check_consistency",
    #     action="store_true",
    #     help="check consistency among versions defined in version files.",
    # )

    args = parser.parse_args()
    #
    VERSION = args.current_version
    V_PATHS = [os.path.normpath(p) for p in args.v_paths]
    #
    DRY_RUN = args.dry_run
    # CHANGELOG = args.changelog

    bumper = ConfiglessBump()
    bumper(VERSION, V_PATHS, dry_run=DRY_RUN)

    # metapath = "~/git_work/python_ml_template/ml_lib/_metadata.py"
    # ConfiglessBump()("0.1.0", [metapath])

    # # CHECK_CONSISTENCY = args.check_consistency
    # # Update config and args with our custom args
    # CONFIG = NoFileConfig()
    # CONFIG._settings["version_files"].extend(V_PATHS)
    # CONFIG.update({"version": VERSION})
    # ARGUMENTS = {
    #     "tag_format": None,
    #     "prerelease": None,
    #     "increment": None,
    #     "bump_message": None,
    #     "changelog": CHANGELOG,
    #     "no_verify": False,
    #     "check_consistency": True,
    #     # 'name': None,
    #     # 'debug': False,
    #     "dry_run": DRY_RUN,
    #     "files_only": False,
    #     "yes": YES,  # yes!
    # }

    # # Run the bump action
    # # import pdb; pdb.set_trace()
    # bmp = Bump(config=CONFIG, arguments=ARGUMENTS)
    # bmp()
