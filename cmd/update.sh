#!/bin/bash

source ../.env

read -p "Enter the tag: " TAG

az acr login --name ${AZURE_CONTAINER_REGISTRY}
az containerapp update \
    --name oshigoto-backend \
    --resource-group oshigoto \
    --image ${AZURE_LOGIN_SERVER}/${AZURE_CONTAINER_REGISTRY}:${TAG}
    --cpu 0.5 --memory 1.0Gi \
    --set-env-vars $(eval echo=$(grep -v '^#' ../.env | sed -E 's/(.*)=(.*)/\1=\2/' | xargs))
