#!/bin/bash

# Add script to set up AKS with monitoring and diagnostics
az aks create --resource-group myResourceGroup --name myAKSCluster --enable-monitoring --enable-addons monitoring
az monitor log-analytics workspace create --resource-group myResourceGroup --workspace-name myWorkspace
az monitor diagnostic-settings create --resource myAKSCluster --workspace myWorkspace --logs '[{"category": "kube-apiserver", "enabled": true}]'