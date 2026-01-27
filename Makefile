SHELL := /bin/bash

.SHELLFLAGS = -e -o pipefail -c
.ONESHELL:

IMAGE_NAME=simple-app
CONTAINER_NAME=simple-app

.PHONY: build run rm

build:
	cd ./app
	docker build --build-arg DEPLOY_REF=$(DEPLOY_REF) -t $(IMAGE_NAME) .

run:
	docker run -d \
		--name $(CONTAINER_NAME) \
		-p 5000:5000 \
		$(IMAGE_NAME)

rm:
	docker rm -f $(CONTAINER_NAME) || true

run-listener:
	nohup python3 webhook-listener/webhook-listener.py >> /tmp/webhook.log 2>&1 &

stop-listener:
	kill $$(cat /tmp/server.pid)