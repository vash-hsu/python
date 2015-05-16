PYTHONPATH=$(shell pwd)
UNITTESTS=$(shell find . -type f -iname 'test_*.py')
MAINS=$(shell find . -type f -iname 'Range*.py')

all: main test coverage sonar

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
	nosetests tests/unit/test_Range.py --with-coverage --cover-erase  --cover-tests --cover-branches --cover-html --cover-xml --cover-xml-file=coverage_unittest.xml --with-xunit --xunit-file=nosetests_unittest.xml


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
	find . -name *.pyc | xargs rm
	rm -rf htmlcov .coverage coverage.xml
	rm -f coverage*.xml nosetests*.xml
	rm -rf cover
