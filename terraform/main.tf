# Terraform configuration for FusionAiAutoCoder infrastructure

provider "azurerm" {
  features {}
}

# Resource group
resource "azurerm_resource_group" "main" {
  name     = "fusionai-resources"
  location = "West Europe"  # Specifically for NCads_H100_v5 availability
  
  tags = {
    Environment = "Production"
    Project     = "FusionAiAutoCoder"
  }
}

# Virtual network
resource "azurerm_virtual_network" "main" {
  name                = "fusionai-vnet"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
}

# Create subnets
resource "azurerm_subnet" "aks" {
  name                 = "aks-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.1.0/24"]
}

resource "azurerm_subnet" "devbox" {
  name                 = "devbox-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.2.0/24"]
}

# Network security group
resource "azurerm_network_security_group" "main" {
  name                = "fusionai-nsg"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  security_rule {
    name                       = "SSH"
    priority                   = 1001
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
}

# AKS cluster
resource "azurerm_kubernetes_cluster" "main" {
  name                = "fusionai-aks"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  dns_prefix          = "fusionai-aks"
  kubernetes_version  = "1.26.0"

  default_node_pool {
    name       = "default"
    node_count = 1
    vm_size    = "Standard_DS3_v2"  # General compute tasks
    vnet_subnet_id = azurerm_subnet.aks.id
    
    tags = {
      Environment = "Production"
      NodeType    = "General"
    }
  }

  identity {
    type = "SystemAssigned"
  }
  
  network_profile {
    network_plugin    = "azure"
    load_balancer_sku = "standard"
  }
  
  oms_agent {
    log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id
  }
}

# GPU node pool for intensive workloads
resource "azurerm_kubernetes_cluster_node_pool" "gpu" {
  name                  = "gpupool"
  kubernetes_cluster_id = azurerm_kubernetes_cluster.main.id
  vm_size               = "Standard_NCads_H100_v5"
  node_count            = 1

  enable_auto_scaling   = true
  min_count             = 0
  max_count             = 3

  node_labels = {
    "workload" = "ai-processing"
  }

  tags = {
    Environment = "Production"
    Project     = "FusionAiAutoCoder"
  }
}

# Memory-optimized Node Pool
resource "azurerm_kubernetes_cluster_node_pool" "memory" {
  name                  = "mempool"
  kubernetes_cluster_id = azurerm_kubernetes_cluster.main.id
  vm_size              = "Standard_E8s_v3"  # Memory-optimized
  node_count           = 1
  max_count            = 3
  min_count           = 0
  vnet_subnet_id      = azurerm_subnet.aks.id
  
  node_labels = {
    "node-type" = "memory"
    "workload"  = "data-processing"
  }
  
  tags = {
    Environment = "Production"
    NodeType    = "Memory"
  }
}

# Development VM
resource "azurerm_network_interface" "devbox" {
  name                = "devbox-nic"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.devbox.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.devbox.id
  }
}

resource "azurerm_public_ip" "devbox" {
  name                = "devbox-public-ip"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  allocation_method   = "Static"
}

resource "azurerm_linux_virtual_machine" "devbox" {
  name                  = "fusionai-devbox"
  location              = azurerm_resource_group.main.location
  resource_group_name   = azurerm_resource_group.main.name
  network_interface_ids = [azurerm_network_interface.devbox.id]
  size                  = "Standard_B2s"  # Burstable instance for dev
  
  # Enable hibernation
  priority        = "Spot"
  eviction_policy = "Deallocate"

  os_disk {
    name                 = "devbox-osdisk"
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "UbuntuServer"
    sku       = "18.04-LTS"
    version   = "latest"
  }
  
  admin_username = "azureuser"
  
  admin_ssh_key {
    username   = "azureuser"
    public_key = file("~/.ssh/id_rsa.pub")  # Replace with your public key path
  }
  
  custom_data = base64encode(file("${path.module}/../scripts/setup_vm.sh"))
  
  tags = {
    Environment = "Development"
  }
}

# Log Analytics workspace for monitoring
resource "azurerm_log_analytics_workspace" "main" {
  name                = "fusionai-logs"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

# Application Insights
resource "azurerm_application_insights" "main" {
  name                = "fusionai-appinsights"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  application_type    = "web"
  workspace_id        = azurerm_log_analytics_workspace.main.id
}

# Output values
output "aks_cluster_name" {
  value = azurerm_kubernetes_cluster.main.name
}

output "devbox_public_ip" {
  value = azurerm_public_ip.devbox.ip_address
}

output "instrumentation_key" {
  value     = azurerm_application_insights.main.instrumentation_key
  sensitive = true
}