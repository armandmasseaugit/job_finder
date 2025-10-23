# ============================================================================
# ChromaDB Azure VM Deployment Guide
# ============================================================================

This directory contains Terraform configuration to deploy ChromaDB on an Azure VM.

## 📋 Prerequisites

1. **Azure CLI** installed and authenticated:
   ```bash
   az login
   az account show  # Verify correct subscription
   ```

2. **Terraform** installed (version >= 1.0):
   ```bash
   terraform --version
   ```

3. **SSH Key Pair** (if you don't have one):
   ```bash
   ssh-keygen -t rsa -b 4096 -C "your-email@example.com"
   ```

## 🚀 Quick Start

### 1. Initialize Terraform
```bash
cd terraform
terraform init
```

### 2. Review and Customize Variables
Edit `variables.tf` or create `terraform.tfvars`:
```hcl
# terraform.tfvars
resource_group_name = "rg-chromadb-prod":
location           = "West Europe"
vm_name            = "vm-chromadb"
vm_size            = "Standard_B2s"
admin_username     = "azureuser"
ssh_public_key_path = "~/.ssh/id_rsa.pub"
allowed_ssh_ips    = ["YOUR_IP_ADDRESS/32"]  # Replace with your IP
```

### 3. Plan the Deployment
```bash
terraform plan
```

### 4. Deploy the Infrastructure
```bash
terraform apply
```

### 5. Get Connection Details
```bash
terraform output
```

## 🏗️ Infrastructure Components

- **Resource Group**: Container for all resources
- **Virtual Network**: 10.0.0.0/16 with subnet 10.0.1.0/24
- **Network Security Group**: Firewall rules for SSH (22), HTTP (80), ChromaDB (8000)
- **Public IP**: Static IP with DNS label
- **Virtual Machine**: Ubuntu 22.04 LTS with Standard_B2s size
- **ChromaDB Installation**: Automated via cloud-init script

## 🔧 ChromaDB Configuration

The VM automatically installs and configures:
- ChromaDB server running on port 8000
- Systemd service for automatic startup
- Nginx reverse proxy for health checks
- Persistent storage in `/var/lib/chromadb/data`
- Logging to `/var/log/chromadb/`

## 🔗 Connection

After deployment, you can connect to ChromaDB:

### Python
```python
import chromadb

# Get IP from terraform output
client = chromadb.HttpClient(host='YOUR_VM_IP', port=8000)
print("Status:", client.heartbeat())
```

### Kedro Catalog
Add to `conf/base/catalog.yml`:
```yaml
chromadb_client:
  type: kedro_datasets.api.APIDataset
  url: http://YOUR_VM_IP:8000
  method: GET
  data_type: json
```

## 🔍 Monitoring & Maintenance

### SSH into the VM
```bash
ssh azureuser@YOUR_VM_IP
```

### Check ChromaDB Status
```bash
sudo systemctl status chromadb
sudo journalctl -u chromadb -f  # View logs
```

### Restart ChromaDB
```bash
sudo systemctl restart chromadb
```

### Health Check
```bash
curl http://YOUR_VM_IP:8000/api/v1/heartbeat
curl http://YOUR_VM_IP/health
```

## 💰 Cost Optimization

- **VM Size**: Standard_B2s (~€30-40/month)
- **Storage**: Standard HDD for cost efficiency
- **Auto-shutdown**: Consider Azure Auto-shutdown for development

## 🛡️ Security

1. **Restrict SSH Access**: Update `allowed_ssh_ips` with your IP
2. **Firewall**: Only necessary ports (22, 80, 8000) are open
3. **Updates**: VM automatically updates on first boot
4. **Authentication**: ChromaDB runs without authentication (add if needed)

## 🗑️ Cleanup

To destroy all resources:
```bash
terraform destroy
```

## 📝 Customization

### Change VM Size
Edit `variables.tf` or use terraform.tfvars:
```hcl
vm_size = "Standard_B4ms"  # 4 vCPUs, 16 GB RAM
```

### Different Azure Region
```hcl
location = "East US"
```

### Custom Installation Script
Modify `install_chromadb.sh` and update:
```hcl
custom_data_script = "./my_custom_script.sh"
```

## 🆘 Troubleshooting

### ChromaDB Not Starting
```bash
# Check logs
sudo journalctl -u chromadb -n 50

# Check configuration
sudo cat /opt/chromadb/config.yaml

# Manual start for debugging
sudo -u chromadb /opt/chromadb/start.sh
```

### Network Issues
```bash
# Check if port is open
sudo netstat -tlnp | grep 8000

# Test local connection
curl localhost:8000/api/v1/heartbeat

# Check firewall
sudo ufw status
```

### VM Issues
```bash
# Check cloud-init logs
sudo tail -f /var/log/cloud-init-output.log

# Check system status
sudo systemctl list-failed
```

## 📚 Next Steps

1. **Update Kedro Catalog**: Point to new ChromaDB instance
2. **Test Job Pipeline**: Run embedding pipeline with new ChromaDB
3. **Configure Backups**: Set up Azure Backup for VM
4. **Monitor Performance**: Set up Azure Monitor alerts
5. **Scale**: Consider Azure Container Instances for auto-scaling
