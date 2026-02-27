# Azure Infrastructure Deployment

This directory contains Bicep templates for deploying the HAM Agent infrastructure to Azure.

## Prerequisites

- Azure CLI installed
- Azure subscription
- Appropriate permissions to create resources

## Structure

- `main.bicep` - Main deployment template
- `modules/` - Modular Bicep templates for each service

## Deployment

### Development Environment

```bash
az deployment sub create \
  --location eastus \
  --template-file main.bicep \
  --parameters environment=dev \
  --parameters appName=ham-agent
```

### Production Environment

```bash
az deployment sub create \
  --location eastus \
  --template-file main.bicep \
  --parameters environment=prod \
  --parameters appName=ham-agent
```

## Resources Created

- Resource Group
- PostgreSQL Flexible Server
- Azure Cache for Redis
- Azure Key Vault
- Container Apps Environment
- Log Analytics Workspace
- Container Apps (Backend & Frontend)

## Post-Deployment

After deployment:

1. Store secrets in Key Vault
2. Update container app images with actual builds
3. Configure custom domains
4. Set up monitoring alerts
5. Configure database migrations

## Cost Optimization

- Dev environment uses burstable SKUs
- Production uses appropriate scaling
- Resources can be stopped/started as needed
