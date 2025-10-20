# ============================================================================
# ChromaDB Azure VM Infrastructure
# ============================================================================
# This Terraform configuration creates:
# - Azure Resource Group
# - Virtual Network with public subnet
# - Network Security Group with ChromaDB port (8000)
# - Virtual Machine with ChromaDB server
# - Public IP for external access

terraform {
  required_version = ">= 1.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

# Configure the Microsoft Azure Provider
provider "azurerm" {
  features {}
}

# Variables
variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
  default     = "rg-job-finder-chromadb"
}

variable "location" {
  description = "Azure location"
  type        = string
  default     = "France Central"
}

variable "vm_size" {
  description = "Size of the VM"
  type        = string
  default     = "Standard_B2s"  # 2 vCPUs, 4GB RAM - good for ChromaDB
}

variable "admin_username" {
  description = "Admin username for the VM"
  type        = string
  default     = "azureuser"
}

variable "ssh_public_key_path" {
  description = "Path to SSH public key"
  type        = string
  default     = "~/.ssh/azure_rsa.pub"
}

variable "allowed_ip_ranges" {
  description = "IP ranges allowed to access ChromaDB"
  type        = list(string)
  default     = ["0.0.0.0/0"]  # Change this to your IP for security
}

# Data source for SSH public key
locals {
  ssh_public_key = file(var.ssh_public_key_path)
}

# Resource Group
resource "azurerm_resource_group" "chromadb" {
  name     = var.resource_group_name
  location = var.location

  tags = {
    Environment = "production"
    Project     = "job-finder"
    Component   = "chromadb"
  }
}

# Virtual Network
resource "azurerm_virtual_network" "chromadb" {
  name                = "vnet-chromadb"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.chromadb.location
  resource_group_name = azurerm_resource_group.chromadb.name

  tags = azurerm_resource_group.chromadb.tags
}

# Subnet
resource "azurerm_subnet" "chromadb" {
  name                 = "subnet-chromadb"
  resource_group_name  = azurerm_resource_group.chromadb.name
  virtual_network_name = azurerm_virtual_network.chromadb.name
  address_prefixes     = ["10.0.1.0/24"]
}

# Public IP
resource "azurerm_public_ip" "chromadb" {
  name                = "pip-chromadb"
  location            = azurerm_resource_group.chromadb.location
  resource_group_name = azurerm_resource_group.chromadb.name
  allocation_method   = "Static"
  sku                = "Standard"

  tags = azurerm_resource_group.chromadb.tags
}

# Network Security Group
resource "azurerm_network_security_group" "chromadb" {
  name                = "nsg-chromadb"
  location            = azurerm_resource_group.chromadb.location
  resource_group_name = azurerm_resource_group.chromadb.name

  # SSH access
  security_rule {
    name                       = "SSH"
    priority                   = 1001
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefixes    = var.allowed_ip_ranges
    destination_address_prefix = "*"
  }

  # ChromaDB access
  security_rule {
    name                       = "ChromaDB"
    priority                   = 1002
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "8000"
    source_address_prefixes    = var.allowed_ip_ranges
    destination_address_prefix = "*"
  }

  # HTTP access (for health checks)
  security_rule {
    name                       = "HTTP"
    priority                   = 1003
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "80"
    source_address_prefixes    = var.allowed_ip_ranges
    destination_address_prefix = "*"
  }

  tags = azurerm_resource_group.chromadb.tags
}

# Network Interface
resource "azurerm_network_interface" "chromadb" {
  name                = "nic-chromadb"
  location            = azurerm_resource_group.chromadb.location
  resource_group_name = azurerm_resource_group.chromadb.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.chromadb.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.chromadb.id
  }

  tags = azurerm_resource_group.chromadb.tags
}

# Associate Network Security Group to Network Interface
resource "azurerm_network_interface_security_group_association" "chromadb" {
  network_interface_id      = azurerm_network_interface.chromadb.id
  network_security_group_id = azurerm_network_security_group.chromadb.id
}

# Virtual Machine
resource "azurerm_linux_virtual_machine" "chromadb" {
  name                = "vm-chromadb"
  location            = azurerm_resource_group.chromadb.location
  resource_group_name = azurerm_resource_group.chromadb.name
  size                = var.vm_size
  admin_username      = var.admin_username

  # Disable password authentication
  disable_password_authentication = true

  network_interface_ids = [
    azurerm_network_interface.chromadb.id,
  ]

  admin_ssh_key {
    username   = var.admin_username
    public_key = local.ssh_public_key
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "StandardSSD_LRS"
    disk_size_gb         = 64  # 64GB should be enough for ChromaDB data
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts-gen2"
    version   = "latest"
  }

  # Install ChromaDB using custom script
  custom_data = base64encode(file("${path.module}/install_chromadb.sh"))

  tags = azurerm_resource_group.chromadb.tags
}

# Outputs
output "chromadb_public_ip" {
  description = "Public IP address of the ChromaDB server"
  value       = azurerm_public_ip.chromadb.ip_address
}

output "chromadb_url" {
  description = "ChromaDB server URL"
  value       = "http://${azurerm_public_ip.chromadb.ip_address}:8000"
}

output "ssh_connection" {
  description = "SSH connection command"
  value       = "ssh ${var.admin_username}@${azurerm_public_ip.chromadb.ip_address}"
}

output "resource_group_name" {
  description = "Resource group name"
  value       = azurerm_resource_group.chromadb.name
}