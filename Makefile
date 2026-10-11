SHELL := /bin/bash

DOCKER_NAMESPACE=lorenzetti
SETUP_SCRIPT=../kernel/GaugiKernel/cmake/lzt_setup.sh

all: build_sources

build_sources:
	mkdir -p build
	cd build && cmake .. && make -j$$(nproc 2>/dev/null || echo 4) && cp ${SETUP_SCRIPT} . && cd ..

test-units:
	@echo "=== Running Package Unit Tests ==="
	source build/lzt_setup.sh && python3 -m unittest discover -s kernel/GaugiKernel/tests -p "test_*.py" -v
	source build/lzt_setup.sh && python3 -m unittest discover -s events/CaloCell/tests -p "test_*.py" -v
	source build/lzt_setup.sh && python3 -m unittest discover -s events/CaloCluster/tests -p "test_*.py" -v
	source build/lzt_setup.sh && python3 -m unittest discover -s events/CaloHit/tests -p "test_*.py" -v
	source build/lzt_setup.sh && python3 -m unittest discover -s events/CaloRings/tests -p "test_*.py" -v
	source build/lzt_setup.sh && python3 -m unittest discover -s events/Egamma/tests -p "test_*.py" -v
	source build/lzt_setup.sh && python3 -m unittest discover -s events/EventInfo/tests -p "test_*.py" -v
	source build/lzt_setup.sh && python3 -m unittest discover -s events/SpacePoint/tests -p "test_*.py" -v
	source build/lzt_setup.sh && python3 -m unittest discover -s events/TruthParticle/tests -p "test_*.py" -v

test-integration:
	@echo "=== Running Root Integration Tests ==="
	source build/lzt_setup.sh && python3 -m unittest discover -s tests -p "test_*.py" -v

test: test-units test-integration

.PHONY: all build_sources test test-units test-integration docs doc_clean doc_venv_clean

VENV_DOC = doc/venv_doc

docs:
	@if [ ! -d "$(VENV_DOC)" ]; then \
		echo "Creating virtual environment for documentation..."; \
		virtualenv -p python $(VENV_DOC); \
		$(VENV_DOC)/bin/python -m pip install -r doc/requirements_doc.txt --no-cache-dir; \
	fi
	mkdir -p doc/doxygen/xml doc/source/api doc/source/cxx doc/source/tutorials && \
	cp notebooks/*.ipynb doc/source/tutorials/ && \
	printf "Python API\n==========\n\n.. toctree::\n   :maxdepth: 2\n\n   modules\n" > doc/source/api/index.rst && \
	printf "C++ API\n=======\n\n.. toctree::\n   :maxdepth: 2\n\n   kernel\n   events\n   generator\n   geometry\n   reconstruction\n" > doc/source/cxx/index.rst && \
	cd doc && doxygen Doxyfile && cd .. && \
	$(VENV_DOC)/bin/python doc/setup_doc_env.py && \
	$(VENV_DOC)/bin/python -m sphinx.ext.apidoc -o doc/source/api doc/mock_site_packages -f && \
	$(VENV_DOC)/bin/python doc/generate_cxx_rst.py && \
	$(VENV_DOC)/bin/python -m sphinx.cmd.build -E -b html doc/source doc/build/html

doc_clean:
	rm -rf doc/build doc/doxygen doc/source/api doc/source/cxx doc/source/tutorials doc/mock_site_packages
	rm -rf $(VENV_DOC)


