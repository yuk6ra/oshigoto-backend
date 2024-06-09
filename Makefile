include .env

TAG?=latest

push-cloud:
	az acr login --name $(AZURE_CONTAINER_REGISTRY)
	docker build -t $(AZURE_LOGIN_SERVER)/$(AZURE_CONTAINER_REGISTRY):$(TAG) .
	docker push $(AZURE_LOGIN_SERVER)/$(AZURE_CONTAINER_REGISTRY):$(TAG)

update:
	cmd/update.sh

start:
	fastapi dev api/main.py

.PHONY: push-cloud