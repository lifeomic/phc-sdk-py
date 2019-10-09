 default: clean lint test package

.PHONY: clean
clean:
	rm -rf build
	rm -rf dist
	rm -rf phc.egg-info

.PHONY: format
format:
	black .

.PHONY: lint
lint:
	flake8 phc tests

.PHONY: test
# uncomment the following line to enforce test coverage standards
# COVER_MIN_PERCENTAGE=100
COVER=--with-coverage \
	--cover-package=phc \
	--cover-erase \
	--cover-tests \
	--cover-min-percentage=${COVER_MIN_PERCENTAGE} \
	--cover-branches \
	--cover-html
test:
	ENV=TEST nosetests ${COVER} -w phc/tests

.PHONY: package
package:
	python setup.py sdist bdist_wheel

.PHONY: deploy
deploy:
	python -m twine upload dist/*

.PHONY: bootstrap
bootstrap:
	@pip install -r requirements.txt
	@pip install -r requirements-dev.txt