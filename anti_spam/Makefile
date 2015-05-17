PYTHONPATH=$(shell pwd)

all: cov sonar

.PHONY: clean sonar main test coverage cov

cov:
	-nosetests email_reader.py --with-coverage --cover-erase \
	--cover-inclusive \
	--cover-tests --cover-branches \
	--cover-html --cover-xml --cover-xml-file=coverage_unittest.xml \
	--with-xunit --xunit-file=nosetests_unittest.xml

sonar: 
	sonar-runner -X

clean:
	rm -rf *.pyc
	find . -name *.pyc | xargs rm -rf
	rm -rf htmlcov .coverage coverage.xml
	rm -f coverage*.xml nosetests*.xml
	rm -rf cover
