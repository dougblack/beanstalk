.PHONY: install clean

clean:
	rm -rf venv/

venv:
	virtualenv -p python3 venv

install: venv
	. venv/bin/activate; python setup.py install
