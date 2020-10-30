#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ATM commitizen just supports bumping via config file. Since we want a more
interactive approach, re-wrote the class with an explicit interface.

VRS=`python -c "from ml_lib import __version__ as v; print(v)"`
python ci_scripts/commitizen_bump.py -P ml_lib/_metadata.py -v $VRS --changelog
--dry_run
"""

import os
import argparse
from packaging.version import Version

#
from commitizen import bump, git, out, cmd, changelog
from commitizen.commands.bump import Bump
from commitizen.commands.changelog import Changelog
from commitizen.cz import registry
from commitizen.exceptions import (
    BumpCommitFailedError,
    BumpTagFailedError,
    DryRunExit,
    ExpectedExit,
    NoCommitsFoundError,
    NoPatternMapError,
    NoneIncrementExit,
    NotAGitProjectError,
)


def get_commiter(commiter_name):
    """"""
    msg_error = (
        "The committer has not been found in the system.\n\n"
        f"Try running 'pip install {commiter_name}'\n"
    )
    assert commiter_name in registry, msg_error
    return registry[commiter_name]


class ConfiglessChangelog(Changelog):
    """
    https://commitizen-tools.github.io/commitizen/
    customization/#custom-changelog-generator

    https://commitizen-tools.github.io/commitizen/changelog/
    """

    def __init__(self, commiter_name="cz_conventional_commits"):
        """"""
        if not git.is_git_project():
            raise NotAGitProjectError()
        self.cz = get_commiter(commiter_name)
        self.commiter_name = commiter_name

    def __call__(
        self,
        chlog_path,
        unreleased_version,
        start_rev=None,
        incremental=False,
        dry_run=False,
        change_type_map=None,
    ):
        """
        :param start_rev: If None, changelog from beginning
        """
        # THE FOLLOWING CODE DOESN'T HAVE SIDE EFFECTS TO FILESYS OR GIT:
        commit_parser = self.cz.commit_parser
        changelog_pattern = self.cz.changelog_pattern
        changelog_meta = {}
        changelog_message_builder_hook = self.cz.changelog_message_builder_hook
        changelog_hook = self.cz.changelog_hook
        if not changelog_pattern or not commit_parser:
            raise NoPatternMapError(
                f"'{self.commiter_name}' rule doesn't support changelog"
            )
        #
        tags = git.get_tags()
        if not tags:
            tags = []
        #
        if incremental:
            changelog_meta = changelog.get_metadata(chlog_path)
            latest_version = changelog_meta.get("latest_version")
            if latest_version:
                start_rev = self._find_incremental_rev(latest_version, tags)
        #
        commits = git.get_commits(start=start_rev, args="--author-date-order")
        if not commits:
            raise NoCommitsFoundError("No commits found")
        #
        tree = changelog.generate_tree_from_commits(
            commits,
            tags,
            commit_parser,
            changelog_pattern,
            unreleased_version,
            change_type_map=change_type_map,
            changelog_message_builder_hook=changelog_message_builder_hook,
        )
        changelog_out = changelog.render_changelog(tree)
        changelog_out = changelog_out.lstrip("\n")
        #
        if dry_run:
            out.write(changelog_out)
            raise DryRunExit()
        #
        # CHANGES TO FILESYSTEM: WRITE TO CHLOG_PATH (AFTER READING)
        lines = []
        if incremental and os.path.isfile(chlog_path):
            with open(chlog_path, "r") as changelog_file:
                lines = changelog_file.readlines()
        #
        with open(chlog_path, "w") as changelog_file:
            partial_changelog = None
            if incremental:
                new_lines = changelog.incremental_build(
                    changelog_out, lines, changelog_meta
                )
                changelog_out = "".join(new_lines)
                partial_changelog = changelog_out
            if changelog_hook:
                changelog_out = changelog_hook(changelog_out, partial_changelog)
            changelog_file.write(changelog_out)
            out.write(f"Wrote changelog to {chlog_path}!\n")


class ConfiglessBump(Bump):
    """
    Adaption of ``commitizen.commands.bump.Bump`` with an explicit interface
    """

    def __init__(self, commiter_name="cz_conventional_commits"):
        """"""
        if not git.is_git_project():
            raise NotAGitProjectError()
        self.cz = get_commiter(commiter_name)

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
        changelog_path=None,
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
        # SIDE EFFECTS TO FILESYSTEM: CREATE CHANGELOG
        if changelog_path is not None:
            try:
                chlogger = ConfiglessChangelog()
                chlogger(changelog_path, "0.4.0", incremental=True, dry_run=dry_run)
                c = cmd.run(f"git add {changelog_path}")
            except Exception as e:
                out.write(f"[ERROR] during changelog creation: {e}")
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
            out.write(f"\n[ERROR] Resetting version files to {current_version}")
            raise e
        # same as git.tag
        tag_msg = "" if changelog_path is None else f"-F {changelog_path}"
        import pdb

        pdb.set_trace()
        c = cmd.run(f"git tag {new_tag_version}" + tag_msg)
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
    parser.add_argument(
        "--changelog",
        action="store_true",
        help="Generate the changelog for the newest version.",
    )
    args = parser.parse_args()
    #
    VERSION = args.current_version
    V_PATHS = [os.path.normpath(p) for p in args.v_paths]
    DRY_RUN = args.dry_run
    CHANGELOG = args.changelog
    #
    chlog_path = "CHANGELOG.md" if CHANGELOG else None
    bumper = ConfiglessBump()
    bumper(VERSION, V_PATHS, dry_run=DRY_RUN, changelog_path=chlog_path)
