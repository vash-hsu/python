PYTHONPATH=$(shell pwd)
UNITTESTS=$(shell find tests/ -type f -iname 'test_*.py')
MAINS=$(shell find sec -type f -iname '*.py')

all: cov sonar

.PHONY: clean sonar main test coverage cov

main:
	@for target in ${MAINS}; do\
		echo $$target; \
		$$target ; \
	done

test:
	@for target in ${UNITTESTS}; do\
		echo $$target; \
		PYTHONPATH=${PYTHONPATH} $$target ; \
	done

cov:
	-nosetests tests/unit/test* --with-coverage --cover-erase --cover-inclusive \
	--cover-package=sec --cover-tests --cover-branches --cover-html \
	--cover-xml --cover-xml-file=coverage_unittest.xml \
	--with-xunit --xunit-file=nosetests_unittest.xml


coverage:
	@coverage erase
	@for target in ${UNITTESTS}; do\
		PYTHONPATH=${PYTHONPATH} coverage run -a --branch $$target ; \
	done
	@for target in ${MAINS}; do\
		PYTHONPATH=${PYTHONPATH} coverage run -a --branch $$target ; \
	done
	@coverage report
	@coverage html

sonar: cov
	sonar-runner -X

clean:
	rm -rf *.pyc
	find . -name *.pyc | xargs rm -rf
	rm -rf htmlcov cover .coverage coverage*.xml
	rm -rf tests/*/cover tests/*/.coverage tests/*/coverage*.xml
	rm -f coverage*.xml nosetests*.xml
	rm -rf cover
