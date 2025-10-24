#!/bin/bash
# ============================================================================
# ChromaDB Azure VM Deployment Script
# ============================================================================
# This script automates the deployment of ChromaDB on Azure VM using Terraform

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$SCRIPT_DIR"
TFVARS_FILE="$TERRAFORM_DIR/terraform.tfvars"

# Functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check if Azure CLI is installed
    if ! command -v az &> /dev/null; then
        log_error "Azure CLI is not installed. Please install it first:"
        echo "https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
        exit 1
    fi

    # Check if Terraform is installed
    if ! command -v terraform &> /dev/null; then
        log_error "Terraform is not installed. Please install it first:"
        echo "https://learn.hashicorp.com/tutorials/terraform/install-cli"
        exit 1
    fi

    # Check if logged into Azure
    if ! az account show &> /dev/null; then
        log_error "Not logged into Azure. Please run 'az login' first."
        exit 1
    fi

    # Check if SSH key exists
    if [ ! -f ~/.ssh/id_rsa.pub ]; then
        log_warning "SSH public key not found at ~/.ssh/id_rsa.pub"
        read -p "Do you want to generate a new SSH key? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            ssh-keygen -t rsa -b 4096 -C "chromadb-azure" -f ~/.ssh/id_rsa -N ""
            log_success "SSH key generated successfully"
        else
            log_error "SSH key is required for VM access"
            exit 1
        fi
    fi

    log_success "All prerequisites met"
}

setup_tfvars() {
    if [ ! -f "$TFVARS_FILE" ]; then
        log_info "Creating terraform.tfvars file..."

        # Get user's public IP
        log_info "Getting your public IP address..."
        USER_IP=$(curl -s ifconfig.me)
        if [ -z "$USER_IP" ]; then
            log_warning "Could not determine your public IP automatically"
            USER_IP="0.0.0.0/0"
        else
            USER_IP="$USER_IP/32"
            log_info "Detected your public IP: $USER_IP"
        fi

        # Create tfvars file
        cat > "$TFVARS_FILE" << EOF
# ChromaDB Azure VM Configuration
# Generated on $(date)

# Basic configuration
resource_group_name = "rg-chromadb-prod"
location           = "West Europe"
vm_name            = "vm-chromadb"
vm_size            = "Standard_B2s"
admin_username     = "azureuser"

# SSH configuration
ssh_public_key_path = "~/.ssh/id_rsa.pub"

# Security: Your IP address for SSH access
allowed_ssh_ips = ["$USER_IP"]

# ChromaDB configuration
chromadb_port = 8000

# Tags
environment  = "production"
project_name = "job-finder"
EOF

        log_success "Created terraform.tfvars file"
        log_warning "Please review and edit $TFVARS_FILE if needed"

        read -p "Press Enter to continue or Ctrl+C to exit and edit the file..."
    else
        log_info "Using existing terraform.tfvars file"
    fi
}

deploy() {
    log_info "Starting ChromaDB deployment..."

    cd "$TERRAFORM_DIR"

    # Initialize Terraform
    log_info "Initializing Terraform..."
    terraform init

    # Validate configuration
    log_info "Validating Terraform configuration..."
    terraform validate

    # Plan deployment
    log_info "Planning deployment..."
    terraform plan -var-file="$TFVARS_FILE"

    # Confirm deployment
    echo
    log_warning "This will create Azure resources that may incur costs!"
    read -p "Do you want to proceed with the deployment? (y/n): " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Apply deployment
        log_info "Deploying ChromaDB infrastructure..."
        terraform apply -var-file="$TFVARS_FILE" -auto-approve

        # Get outputs
        log_success "Deployment completed successfully!"
        echo
        log_info "Connection details:"
        terraform output

        # Wait for ChromaDB to be ready
        log_info "Waiting for ChromaDB to be ready (this may take a few minutes)..."
        CHROMADB_IP=$(terraform output -raw chromadb_public_ip)

        # Wait up to 10 minutes for ChromaDB to start
        for i in {1..60}; do
            if curl -s -f "http://$CHROMADB_IP:8000/api/v1/heartbeat" >/dev/null 2>&1; then
                log_success "ChromaDB is ready and responding!"
                break
            fi

            if [ $i -eq 60 ]; then
                log_warning "ChromaDB might still be starting. Check manually with:"
                echo "curl http://$CHROMADB_IP:8000/api/v1/heartbeat"
            else
                echo -n "."
                sleep 10
            fi
        done

        echo
        log_success "🎉 ChromaDB deployment completed!"
        echo
        echo "Access your ChromaDB server:"
        echo "  API: http://$CHROMADB_IP:8000"
        echo "  Health: http://$CHROMADB_IP/health"
        echo "  SSH: ssh azureuser@$CHROMADB_IP"
        echo
        echo "Python connection:"
        echo "  import chromadb"
        echo "  client = chromadb.HttpClient(host='$CHROMADB_IP', port=8000)"

    else
        log_info "Deployment cancelled"
        exit 0
    fi
}

destroy() {
    log_warning "This will destroy all ChromaDB infrastructure!"
    read -p "Are you sure you want to destroy everything? (y/n): " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cd "$TERRAFORM_DIR"
        log_info "Destroying infrastructure..."
        terraform destroy -var-file="$TFVARS_FILE" -auto-approve
        log_success "Infrastructure destroyed successfully"
    else
        log_info "Destruction cancelled"
    fi
}

status() {
    cd "$TERRAFORM_DIR"

    if [ ! -f "terraform.tfstate" ]; then
        log_info "No infrastructure deployed yet"
        return
    fi

    log_info "Current infrastructure status:"
    terraform show

    # Try to check ChromaDB status
    if terraform output chromadb_public_ip >/dev/null 2>&1; then
        CHROMADB_IP=$(terraform output -raw chromadb_public_ip)
        echo
        log_info "Testing ChromaDB connectivity..."

        if curl -s -f "http://$CHROMADB_IP:8000/api/v1/heartbeat" >/dev/null 2>&1; then
            log_success "ChromaDB is running and accessible"
        else
            log_warning "ChromaDB is not responding (might be starting up)"
        fi
    fi
}

# Main script
case "${1:-deploy}" in
    "deploy"|"apply")
        check_prerequisites
        setup_tfvars
        deploy
        ;;
    "destroy")
        destroy
        ;;
    "status"|"show")
        status
        ;;
    "plan")
        cd "$TERRAFORM_DIR"
        setup_tfvars
        terraform plan -var-file="$TFVARS_FILE"
        ;;
    "init")
        cd "$TERRAFORM_DIR"
        terraform init
        ;;
    "help"|"--help"|"-h")
        echo "ChromaDB Azure VM Deployment Script"
        echo
        echo "Usage: $0 [command]"
        echo
        echo "Commands:"
        echo "  deploy    Deploy ChromaDB infrastructure (default)"
        echo "  destroy   Destroy all infrastructure"
        echo "  status    Show current infrastructure status"
        echo "  plan      Show deployment plan without applying"
        echo "  init      Initialize Terraform"
        echo "  help      Show this help message"
        echo
        echo "Prerequisites:"
        echo "  - Azure CLI installed and logged in (az login)"
        echo "  - Terraform installed"
        echo "  - SSH key pair (will be generated if missing)"
        ;;
    *)
        log_error "Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac
