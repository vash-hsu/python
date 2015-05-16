
UNITTESTS=$(shell find . -type f -iname 'test_*.py')
MAINS=$(shell find . -type f -iname 'Range*.py')

all: sonar

.PHONY: clean sonar main test coverage cov

main:
	for target in ${MAINS}; do\
		echo $$target; \
		$$target ; \
	done

test:
	for target in ${UNITTESTS}; do\
		echo $$target; \
		$$target ; \
	done

cov: coverage

coverage:
	coverage erase
	for target in ${UNITTESTS}; do\
		coverage run -a --branch $$target ; \
	done
	for target in ${MAINS}; do\
		coverage run -a --branch $$target ; \
	done
	coverage report
	coverage html
	coverage xml -i

sonar:
	sonar-runner -X

clean:
	rm -rf *.pyc
	rm -rf htmlcov .coverage coverage.xml
