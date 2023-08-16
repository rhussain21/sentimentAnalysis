#!/bin/bash
IMAGE_NAME=mlapi:latest
APP_NAME=mlapi

echo "==================================================="
echo "START RUN SCRIPT"
echo "==================================================="
echo "STARTING MINIKUBE..."
#minikube start
#minikube start --kubernetes-version=v1.25.4

# Setup your docker daemon to build with Minikube
eval $(minikube -p minikube docker-env)

echo "BUILDING DOCKER IMAGE...\n"
docker build -t ${IMAGE_NAME} .

echo "==================================================="
echo "CREATING K8 NAMESPACE, DEPLOYMENTS, AND SERVICES...\n"
# Apply the k8 namespace
#kubectl create namespace rh1330

#set namespace to w255
kubectl config set-context --current --namespace=rh1330

kubectl apply -k ../.k8s/overlays/dev

IMAGE_PREFIX=rh1330
IMAGE_NAME=project:3c5e581
 ACR_DOMAIN=w255mids.azurecr.io
IMAGE_FQDN="${ACR_DOMAIN}/${IMAGE_PREFIX}/${IMAGE_NAME}"

az acr login --name w255mids
docker build --platform linux/amd64 -t ${IMAGE_NAME} .
docker tag ${IMAGE_NAME} ${IMAGE_FQDN}
docker push ${IMAGE_FQDN}
docker pull ${IMAGE_FQDN}