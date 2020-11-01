#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ATM commitizen just supports changelog via config file. Since we want a more
interactive approach, re-wrote the class with an explicit interface.
This can be used in the CI runners that have been triggered by a tag, to
generate the CHANGELOG based on that tag and then upload the corresponding
release. Usage example::

  python ci_scripts/commitizen_changelog.py

This will automatically grab the latest tag and save it to CHANGELOG.md
"""

import os
import argparse
from packaging.version import Version

#
from commitizen import git, out, changelog
from commitizen.commands.changelog import Changelog
from commitizen.cz import registry
from commitizen.exceptions import (
    DryRunExit,
    NoCommitsFoundError,
    NoPatternMapError,
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
        latest_version,
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
            latest_version,
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser("A Config-less Changelog")
    parser.add_argument(
        "-v",
        "--last_version",
        default=None,
        help="Last chlog version",
    )
    parser.add_argument(
        "-o",
        "--out_path",
        type=str,
        default="CHANGELOG.md",
        help="Output path for the changelog file",
    )
    # Incremental currently buggy! generates whole file if no preexisting chlog,
    # and logs but-last release as last one if no new tag.
    # parser.add_argument(
    #     "--incremental",
    #     action="store_true",
    #     help="If given, changelog will only contain changes since last tag.",
    # )
    # parser.add_argument(
    #     "-w",
    #     "--first_version",
    #     type=str,
    #     required=True,
    #     help="First chlog version",
    # )
    parser.add_argument(
        "--dry_run",
        action="store_true",
        help="If given, the command will print but not change anything.",
    )

    args = parser.parse_args()
    #
    OUT_PATH = args.out_path
    LAST_VERSION = args.last_version
    # FIRST_VERSION = args.first_version
    # INCREMENTAL = args.incremental
    DRY_RUN = args.dry_run
    #
    print(git.get_tags())
    print(git.get_commits())
    if LAST_VERSION is None:
        sorted_versions = sorted(
            (t.name for t in git.get_tags()), key=lambda elt: Version(elt)
        )
        LAST_VERSION = sorted_versions[-1]
    #
    chlogger = ConfiglessChangelog()
    chlogger(OUT_PATH, LAST_VERSION, dry_run=DRY_RUN)
