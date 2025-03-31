#!/bin/bash
# AKS Setup Script for FusionAiAutoCoder

set -e

echo "Setting up AKS cluster for FusionAiAutoCoder..."

# Variables
RESOURCE_GROUP="fusionai-resources"
CLUSTER_NAME="fusionai-aks"
LOCATION="westeurope"
KUBERNETES_VERSION="1.26.0"

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "Azure CLI not found. Please install it first."
    exit 1
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "kubectl not found. Please install it first."
    exit 1
fi

# Login to Azure (uncomment if not already logged in)
# az login

# Create resource group if it doesn't exist
if ! az group show --name $RESOURCE_GROUP &> /dev/null; then
    echo "Creating resource group $RESOURCE_GROUP..."
    az group create --name $RESOURCE_GROUP --location $LOCATION
fi

# Create AKS cluster
echo "Creating AKS cluster $CLUSTER_NAME..."
az aks create \
    --resource-group $RESOURCE_GROUP \
    --name $CLUSTER_NAME \
    --node-count 1 \
    --enable-addons monitoring \
    --kubernetes-version $KUBERNETES_VERSION \
    --generate-ssh-keys \
    --vm-set-type VirtualMachineScaleSets \
    --load-balancer-sku standard \
    --enable-cluster-autoscaler \
    --min-count 1 \
    --max-count 3

# Get credentials for kubectl
echo "Getting credentials for kubectl..."
az aks get-credentials --resource-group $RESOURCE_GROUP --name $CLUSTER_NAME --overwrite-existing

# Create GPU node pool
echo "Creating GPU node pool..."
az aks nodepool add \
    --resource-group $RESOURCE_GROUP \
    --cluster-name $CLUSTER_NAME \
    --name gpupool \
    --node-count 1 \
    --node-vm-size Standard_NC24ads_A100_v4 \
    --enable-cluster-autoscaler \
    --min-count 0 \
    --max-count 3 \
    --node-taints gpu=true:NoSchedule \
    --labels workload=ai-processing

# Create memory-optimized node pool
echo "Creating memory-optimized node pool..."
az aks nodepool add \
    --resource-group $RESOURCE_GROUP \
    --cluster-name $CLUSTER_NAME \
    --name mempool \
    --node-count 1 \
    --node-vm-size Standard_E8s_v3 \
    --enable-cluster-autoscaler \
    --min-count 0 \
    --max-count 3 \
    --labels workload=data-processing

# Install NVIDIA device plugin
echo "Installing NVIDIA device plugin..."
kubectl create namespace gpu-resources
kubectl apply -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v0.14.0/nvidia-device-plugin.yml

# Deploy monitoring resources
echo "Deploying monitoring resources..."
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml

# Create namespace for FusionAiAutoCoder
echo "Creating namespace for FusionAiAutoCoder..."
kubectl create namespace fusionai

# Deploy storage class
echo "Deploying storage class..."
cat <<EOF | kubectl apply -f -
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fusionai-storage
provisioner: kubernetes.io/azure-disk
parameters:
  storageaccounttype: Premium_LRS
  kind: Managed
reclaimPolicy: Retain
allowVolumeExpansion: true
EOF

echo "AKS setup complete! You can now deploy FusionAiAutoCoder to the cluster."
echo "Use: kubectl config use-context $CLUSTER_NAME"