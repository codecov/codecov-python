upload:
	python setup.py sdist upload

test:
	pip uninstall -y codecov
	python setup.py install
	codecov stevepeak inquiry 0996a2d6d04f869d6fd943bc441c57ba75ac452d \
		--token=c5d94669-c417-4076-be4b-c900368bb185 \
		--url http://localhost:5000 \
		--xml tests/xml/stevepeak-inquiry-coverage.xml
