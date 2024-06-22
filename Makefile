include .env

TAG?=latest

push-cloud:
	az acr login --name $(AZURE_CONTAINER_REGISTRY)
	docker build -t $(AZURE_LOGIN_SERVER)/$(AZURE_CONTAINER_REGISTRY):$(TAG) .
	docker push $(AZURE_LOGIN_SERVER)/$(AZURE_CONTAINER_REGISTRY):$(TAG)

example-env:
	cmd/example-env.sh

update:
	cmd/update.sh

start:
	fastapi dev app/api/main.py

.PHONY: push-cloud