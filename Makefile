# Required executables
ifeq (, $(shell which python3))
 $(error "No python3 on PATH.")
endif
ifeq (, $(shell which pipenv))
 $(error "No pipenv on PATH.")
endif

# Suppress warning if pipenv is started inside .venv
export PIPENV_VERBOSITY = 1
# Use relative .venv folder instead of home-folder based
export PIPENV_VENV_IN_PROJECT = 1
# Ignore existing venvs
export PIPENV_IGNORE_VIRTUALENVS = 0
# Make sure we are running with an explicit encoding
export LC_ALL = C
export LANG = C.UTF-8
# Set configuration folder to venv
export PYPE_CONFIG_FOLDER = $(shell pwd)/.venv/.pype-cli
# Process variables
VERSION = $(shell python3 setup.py --version)
PY_FILES := setup.py octo_infra_aws tests

all: venv build

venv:
	@echo Initialize virtualenv, i.e., install required packages etc.
	pipenv sync --dev

install:
	pipenv install --dev

update:
	pipenv update --dev

shell:
	@echo Initialize virtualenv and open a new shell using it
	pipenv shell

clean:
	@echo Clean project base
	find . -type d \
	-name ".tox" -o \
	-name ".ropeproject" -o \
	-name ".mypy_cache" -o \
	-name ".pytest_cache" -o \
	-name "__pycache__" -o \
	-iname "*.egg-info" -o \
	-name "build" -o \
	-name "dist" \
	-path ./.venv -prune \
	|xargs rm -rfv

test:
	@echo Run all tests in default virtualenv
	pipenv run py.test tests

testall:
	@echo Run all tests against all virtualenvs defined in tox.ini
	pipenv run tox -c setup.cfg tests

isort:
	@echo Check for incorrectly sorted imports
	pipenv run isort --check-only $(PY_FILES)

isort-apply:
	@echo Check for incorrectly sorted imports
	pipenv run isort $(PY_FILES)

build: test isort
	@echo Run setup.py-based build process to package application
	pipenv run python setup.py bdist_wheel

publish:
	@echo Release to pypi.org and create git tag
	pipenv run twine upload --repository-url https://upload.pypi.org/legacy/ --skip-existing dist/*
