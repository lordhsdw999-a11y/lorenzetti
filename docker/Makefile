SHELL := /bin/bash

DOCKER_NAMESPACE=lorenzetti
ROOT_VERSION=v6-34-00
GEANT4_VERSION=v11.2.2
FASTJET_VERSION=3.4.0
HEPMC_VERSION=3.3.0
PYTHIA8_VERSION=8313
SIF_IMAGE=lorenzetti_latest.sif
DEF_FILE=Singularity.def

.PHONY: all build build_docker build_singularity pull push clean

all: build_singularity

# Build Docker image
build_docker:
	docker build --progress=plain --compress \
				 --build-arg ROOT_VERSION=${ROOT_VERSION} \
				 --build-arg GEANT4_VERSION=${GEANT4_VERSION} \
				 --build-arg FASTJET_VERSION=${FASTJET_VERSION} \
				 --build-arg PYTHIA8_VERSION=${PYTHIA8_VERSION} \
				 --build-arg HEPMC_VERSION=${HEPMC_VERSION} \
				 -t ${DOCKER_NAMESPACE}/lorenzetti:latest .

build: build_docker

# Build Singularity SIF image directly from Singularity.def file
build_singularity:
	export SINGULARITY_TMPDIR=/tmp && \
	export SINGULARITY_CACHEDIR=/tmp/singularity_cache && \
	singularity build --fakeroot \
					  --build-arg ROOT_VERSION=${ROOT_VERSION} \
					  --build-arg GEANT4_VERSION=${GEANT4_VERSION} \
					  --build-arg FASTJET_VERSION=${FASTJET_VERSION} \
					  --build-arg HEPMC_VERSION=${HEPMC_VERSION} \
					  --build-arg PYTHIA8_VERSION=${PYTHIA8_VERSION} \
					  ${SIF_IMAGE} ${DEF_FILE}

# Pull pre-built image from Docker Hub and convert to SIF
pull:
	export SINGULARITY_TMPDIR=/tmp && \
	export SINGULARITY_CACHEDIR=/tmp/singularity_cache && \
	singularity pull --tmpdir /tmp docker://${DOCKER_NAMESPACE}/lorenzetti:latest

push:
	docker push ${DOCKER_NAMESPACE}/lorenzetti:latest

clean:
	docker system prune -a
	rm -rf /tmp/singularity_cache