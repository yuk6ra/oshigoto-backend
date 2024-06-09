include .env

push-cloud:
	az acr login --name $(AZURE_CONTAINER_REGISTRY)
	docker build -t $(AZURE_LOGIN_SERVER)/$(AZURE_CONTAINER_REGISTRY):latest .
	docker push $(AZURE_LOGIN_SERVER)/$(AZURE_CONTAINER_REGISTRY):latest

azure-update-app:
	az acr login --name $(AZURE_CONTAINER_REGISTRY)
	az containerapp update \
		--name oshigoto-backend \
		--resource-group oshigoto \
		--image $(AZURE_LOGIN_SERVER)/$(AZURE_CONTAINER_REGISTRY):latest \
		--cpu 0.5 --memory 1.0Gi

start:
	fastapi dev api/main.py

.PHONY: push-cloud