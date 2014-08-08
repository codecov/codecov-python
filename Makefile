upload:
	python setup.py sdist upload

reinstall:
	pip uninstall -y codecov
	python setup.py install
