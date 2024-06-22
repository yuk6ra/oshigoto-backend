#!/bin/bash

source .env

read -p "Enter the tag: " TAG
env_vars=$(grep -v '^#' .env | xargs)
az acr login --name ${AZURE_CONTAINER_REGISTRY}
az containerapp update \
    --name oshigoto-backend \
    --resource-group oshigoto \
    --image ${AZURE_LOGIN_SERVER}/${AZURE_CONTAINER_REGISTRY}:${TAG} \
    --cpu 0.5 --memory 1.0Gi \
    --set-env-vars $env_vars