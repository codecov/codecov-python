deploy:
	git tag -a v$(python -c 'import codecov;print(codecov.version)') -m ""
	git push origin v$(python -c 'import codecov;print(codecov.version)')
	python setup.py sdist bdist_wheel bdist_egg
	python -m twine upload dist/*

reinstall:
	pip uninstall -y codecov
	python setup.py install

test:
	py.test tests/test.py --cov=codecov

format:
	black . -v -t py38 --check --diff

compare:
	hub compare $(shell git tag --sort=refname | tail -1)...master

testsuite:
	curl -X POST https://circleci.com/api/v1/project/codecov/testsuite/tree/master?circle-token=$(CIRCLE_TOKEN)\
	     --header "Content-Type: application/json"\
	     --data "{\"build_parameters\": {\"TEST_LANG\": \"python\",\
	                                     \"TEST_SLUG\": \"$(CIRCLE_PROJECT_USERNAME)/$(CIRCLE_PROJECT_REPONAME)\",\
	                                     \"TEST_SHA\": \"$(CIRCLE_SHA1)\"}}"
