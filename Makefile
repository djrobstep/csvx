.PHONY: docs

# test commands and arguments
tcommand = PYTHONPATH=. py.test -x
tmessy = -svv
targs = --cov-report term-missing --cov csvx

init: pip

pip:
	pip install -r requirements-dev.txt

pipupgrade:
	pip install --upgrade pip
	pip install --upgrade -r requirements-dev.txt

pipreqs:
	pip install -r requirements.txt

pipeditable:
	pip install -e .

tox:
	tox tests/unit

test:
	$(tcommand) $(targs) tests/unit

stest:
	$(tcommand) $(tmessy) $(targs) tests/unit

docs:
	cd docs && make clean && make html

opendocs:
	BROWSER=firefox python -c 'import os;import webbrowser;webbrowser.open_new_tab("file://" + os.getcwd() + "/docs/_build/html/index.html")'


clean:
	git clean -fXd
	find . -name \*.pyc -delete


fmt:
	yapf --recursive --in-place csvx
	yapf --recursive --in-place tests/unit


lint:
	flake8 csvx

tidy: clean fmt lint

all: pipupgrade clean fmt lint tox

publish:
	python setup.py register
	python setup.py sdist bdist_wheel --universal upload
