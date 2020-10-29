[![CI](https://github.com/andres-fr/pymltemplate2/workflows/CI/badge.svg)](https://github.com/andres-fr/pymltemplate2/actions?query=workflow%3ACI)


# python_ml_template

### Install actions:

* `pip install ???`
* `pre-commit install --install-hooks -t pre-commit -t commit-msg`


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


### Ignored for the moment:
* TUT __init__ check_installation
* autoimports in each __init__
* dcase test tools
* pylintrc?
* custom "asteroid" sphinx theme
* mypy (not needed in research code)
* gitignore.io
* dependabot https://dependabot.com/github-actions/

### TODO:

* Tagging still not working. If CI does it all, how is my client expected to update the version? I think I should manually release, and semi-automate it via pre-commit. Rethink process. Also auto-release to Pypi and GH releases. Also where does CHANGELOG go?
* change docstring style to napoleon. add doctest
* badges

1. Once tags fixed, start clean repo without other contribs
2. CML+ Complete ML project
3. Generalize runner to GPU, home and GitLab
