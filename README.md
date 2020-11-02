[![CI](https://github.com/andres-fr/python_ml_template/workflows/CI/badge.svg)](https://github.com/andres-fr/python_ml_template/actions?query=workflow%3ACI)
[![docs badge](https://img.shields.io/badge/docs-latest-blue)](https://andres-fr.github.io/python_ml_template/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)


# python_ml_template

### Install actions:

* `pip install ???`
* `pre-commit install --install-hooks -t pre-commit -t commit-msg`
* `git config branch.master.mergeOptions "--squash`
* Activate gh-pages web

### Added:

* Utest: python -m unittest
* utest with py coverage: coverage run -m unittest
* flake8
* __all__
* using pre-commit, added commitizen to pre-commit (remember to `pre-commit install --install-hooks -t pre-commit -t commit-msg`). This enforces "conventional commits" style: https://www.conventionalcommits.org/en/v1.0.0/#summary To commit, reecommended to `pip install commitizen` and then commit using: `cz c` (or `cz c --retry` if the last one failed).

* docs from scratch:
  1. Add docs folder and requirements.txt with `sphinx` and `sphinx-rtd-theme`
* Centralized version and metadata. Setup works with very few parameters

* To enforce squash merging to master, issue `git config branch.master.mergeOptions "--squash"` (info: https://stackoverflow.com/a/37828622)

* GH pages action. Make sure that the repo server has publishing enabled, otherwise it will error.

* Pypi: need a regular and a test account. Create a token for GH actions (if global only need to do this once). Then, in the GH repo, add that token under secrets->pypi. https://pypi.org/manage/account/token/


### Ignored for the moment:
* TUT __init__ check_installation
* autoimports in each __init__
* dcase test tools
* pylintrc?
* custom "asteroid" sphinx theme
* mypy (not needed in research code)
* gitignore.io
* dependabot https://dependabot.com/github-actions/
* Ignore commits in changelog: https://github.com/conventional-changelog/conventional-changelog/issues/342

### TODO:


* Fix tagging: tags read changelog as a txt, not markdown. So what we actually need is a RELEASE. possible steps?
  1. Remove the -F message from the tag
  2. in the CI runner, for tagged runs, create the CHANGELOG and convert the tag into a release?
  3. Still we need to deploy to pip and conda forge.

* change docstring style to napoleon. add doctest
* badges
* Follow-tags not following tags??

1. Once tags fixed, start clean repo without other contribs
2. CML+ Complete ML project
3. Generalize runner to GPU, home and GitLab
