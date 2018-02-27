.PHONY: install clean

clean:
	rm -rf venv/
	rm -rf *.egg-info/
	rm -rf dist/

venv:
	virtualenv -p python3 venv

install: venv
	. venv/bin/activate; python setup.py install

run:
	../run
