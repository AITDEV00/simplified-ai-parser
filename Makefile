IMAGE_NAME = simplified-ai-parser
DOCKER_USER = jya0
DATE = $(shell date +%Y-%m-%d)
FULL_IMAGE_NAME = $(DOCKER_USER)/$(IMAGE_NAME):$(DATE)

.PHONY: all build tag push

all: build tag push

build:
	docker build -t $(IMAGE_NAME) .

tag:
	docker tag $(IMAGE_NAME) $(FULL_IMAGE_NAME)

push:
	docker push $(FULL_IMAGE_NAME)
