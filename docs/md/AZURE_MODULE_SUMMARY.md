# Azure Module - Complete Reference

## Overview

The Azure module enables comprehensive management of Microsoft Azure cloud resources through natural language instructions in AIbasic. It provides a unified interface to interact with Azure Virtual Machines, Storage Accounts, SQL Databases, Cosmos DB, App Services, Container Instances, Key Vault, and more.

**Module Type:** Cloud Services
**Task Type:** `(azure)`
**Python Implementation:** `src/aibasic/modules/azure_module.py`
**Configuration Section:** `[azure]` in `aibasic.conf`

## Key Features

- **Resource Group Management** - Create, list, and delete resource groups
- **Virtual Machine Operations** - Full VM lifecycle (create, start, stop, restart, delete)
- **Storage Services** - Storage Accounts and Blob Storage operations
- **Database Services** - Azure SQL and Cosmos DB management
- **Networking** - Virtual Networks and subnet configuration
- **App Services** - Web application deployment and management
- **Container Services** - Container Instances for containerized workloads
- **Security** - Key Vault for secrets management
- **Serverless** - Azure Functions deployment
- **Authentication** - Service Principal and Managed Identity support
- **Monitoring** - Azure Monitor and Log Analytics integration

## Architecture

The Azure module implements a **singleton pattern** with thread-safe initialization and lazy-loading of Azure service clients. It uses the official Azure SDK for Python with proper authentication and error handling.

### Design Patterns

1. **Singleton Pattern** - Single instance with thread lock (`_lock`) and initialization flag (`_initialized`)
2. **Lazy Loading** - Azure service clients initialized only when first accessed
3. **Configuration Management** - Reads from `aibasic.conf` with environment variable fallbacks
4. **Error Handling** - Comprehensive exception handling with descriptive error messages

### Supported Azure Services

- **Compute** - Virtual Machines (azure-mgmt-compute)
- **Storage** - Storage Accounts, Blob Storage (azure-mgmt-storage)
- **Databases** - SQL Server, SQL Database (azure-mgmt-sql)
- **NoSQL** - Cosmos DB (azure-mgmt-cosmosdb)
- **Networking** - Virtual Networks, Subnets (azure-mgmt-network)
- **Web** - App Service, Function Apps (azure-mgmt-web)
- **Containers** - Container Instances (azure-mgmt-containerinstance)
- **Security** - Key Vault (azure-mgmt-keyvault)
- **Resources** - Resource Groups (azure-mgmt-resource)

## Configuration

### Required Settings

Add these settings to your `aibasic.conf` file:

```ini
[azure]
# Subscription and Tenant
SUBSCRIPTION_ID = xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
TENANT_ID = xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

# Service Principal Authentication (recommended for automation)
CLIENT_ID = xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
CLIENT_SECRET = your-client-secret-here

# Default Location
LOCATION = eastus
```

### Optional Settings

```ini
[azure]
# Resource Naming Convention
RESOURCE_PREFIX = aibasic
ENVIRONMENT = dev

# Default Resource Group
DEFAULT_RESOURCE_GROUP = aibasic-rg

# Storage Settings
DEFAULT_STORAGE_ACCOUNT = aibasicstorage001
DEFAULT_STORAGE_SKU = Standard_LRS

# VM Settings
DEFAULT_VM_SIZE = Standard_B2s
DEFAULT_VM_IMAGE_PUBLISHER = Canonical
DEFAULT_VM_IMAGE_OFFER = 0001-com-ubuntu-server-jammy
DEFAULT_VM_IMAGE_SKU = 22_04-lts-gen2

# Network Settings
DEFAULT_VNET_ADDRESS_SPACE = 10.0.0.0/16
DEFAULT_SUBNET_PREFIX = 10.0.1.0/24

# Tagging Strategy
DEFAULT_TAGS = {"Environment": "dev", "ManagedBy": "AIBasic", "Project": "automation"}
```

### Authentication Methods

#### 1. Service Principal (Recommended for Production)

Create a service principal in Azure:

```bash
az ad sp create-for-rbac --name "aibasic-sp" --role Contributor --scopes /subscriptions/{subscription-id}
```

Configure in `aibasic.conf`:

```ini
[azure]
SUBSCRIPTION_ID = your-subscription-id
TENANT_ID = your-tenant-id
CLIENT_ID = service-principal-client-id
CLIENT_SECRET = service-principal-client-secret
```

#### 2. DefaultAzureCredential (For Local Development)

Leave `CLIENT_ID` and `CLIENT_SECRET` blank. The module will use `DefaultAzureCredential` which checks:

1. Environment variables
2. Managed Identity
3. Azure CLI credentials (`az login`)
4. Visual Studio Code credentials
5. Azure PowerShell credentials

```ini
[azure]
SUBSCRIPTION_ID = your-subscription-id
LOCATION = eastus
```

Then authenticate with Azure CLI:

```bash
az login
```

## Core Operations

### Resource Group Management

#### Create Resource Group

```aibasic
10 (azure) create resource group "app-rg" in location "eastus"
20 (azure) create resource group "prod-rg" in location "westus" with tags {"environment": "production", "project": "webapp"}
```

#### List Resource Groups

```aibasic
30 (azure) list all resource groups
```

#### Delete Resource Group

```aibasic
40 (azure) delete resource group "app-rg"
50 (azure) delete resource group "temp-rg" with force True
```

### Virtual Machine Management

#### Create Virtual Machine

```aibasic
10 (azure) create resource group "vm-rg" in location "eastus"
20 (azure) create virtual network "vm-vnet" in resource group "vm-rg" with address_space "10.0.0.0/16" and subnet "default" with address_prefix "10.0.0.0/24"
30 (azure) create virtual machine "web-vm" in resource group "vm-rg" with vm_size "Standard_B2s" and image {"publisher": "Canonical", "offer": "0001-com-ubuntu-server-jammy", "sku": "22_04-lts-gen2", "version": "latest"} and admin_username "azureuser" and admin_password "SecurePassword123!" and network_interface {"vnet_name": "vm-vnet", "subnet_name": "default"}
```

#### List Virtual Machines

```aibasic
40 (azure) list virtual machines in resource group "vm-rg"
50 (azure) list all virtual machines
```

#### VM Operations

```aibasic
60 (azure) start virtual machine "web-vm" in resource group "vm-rg"
70 (azure) stop virtual machine "web-vm" in resource group "vm-rg"
80 (azure) restart virtual machine "web-vm" in resource group "vm-rg"
90 (azure) delete virtual machine "web-vm" in resource group "vm-rg"
```

#### Get VM Details

```aibasic
100 (azure) get virtual machine "web-vm" in resource group "vm-rg"
```

### Storage Account and Blob Storage

#### Create Storage Account

```aibasic
10 (azure) create resource group "storage-rg" in location "eastus"
20 (azure) create storage account "mystorage001" in resource group "storage-rg" with sku {"name": "Standard_LRS"} and kind "StorageV2"
30 (azure) create storage account "premiumstore" in resource group "storage-rg" with sku {"name": "Premium_LRS"} and kind "BlockBlobStorage"
```

#### List Storage Accounts

```aibasic
40 (azure) list storage accounts in resource group "storage-rg"
50 (azure) list all storage accounts
```

#### Get Storage Account Keys

```aibasic
60 (azure) get storage account keys for "mystorage001" in resource group "storage-rg"
```

#### Blob Storage Operations

```aibasic
70 (file) write "data.txt" with content "Hello from AIBasic!"
80 (azure) upload file "data.txt" to blob storage "mystorage001" in container "uploads" as "files/data.txt"
90 (azure) list blobs in storage account "mystorage001" container "uploads"
100 (azure) download blob "files/data.txt" from storage account "mystorage001" container "uploads" to "downloaded.txt"
110 (file) read "downloaded.txt"
```

#### Delete Storage Account

```aibasic
120 (azure) delete storage account "mystorage001" in resource group "storage-rg"
```

### SQL Database Management

#### Create SQL Server

```aibasic
10 (azure) create resource group "sql-rg" in location "eastus"
20 (azure) create sql server "myserver" in resource group "sql-rg" with admin_login "sqladmin" and admin_password "SecurePassword123!"
```

#### Create SQL Database

```aibasic
30 (azure) create sql database "mydb" on server "myserver" in resource group "sql-rg" with sku {"name": "Basic", "tier": "Basic"}
40 (azure) create sql database "proddb" on server "myserver" in resource group "sql-rg" with sku {"name": "S1", "tier": "Standard", "capacity": 20}
```

#### List SQL Databases

```aibasic
50 (azure) list sql databases on server "myserver" in resource group "sql-rg"
```

### Virtual Network Management

#### Create Virtual Network

```aibasic
10 (azure) create resource group "network-rg" in location "eastus"
20 (azure) create virtual network "app-vnet" in resource group "network-rg" with address_space "10.0.0.0/16" and subnet "default" with address_prefix "10.0.1.0/24"
```

#### Create VNet with Multiple Subnets

```aibasic
30 (azure) create virtual network "multi-vnet" in resource group "network-rg" with address_space "10.1.0.0/16" and subnets [{"name": "web-subnet", "address_prefix": "10.1.1.0/24"}, {"name": "app-subnet", "address_prefix": "10.1.2.0/24"}, {"name": "db-subnet", "address_prefix": "10.1.3.0/24"}]
```

#### List Virtual Networks

```aibasic
40 (azure) list virtual networks in resource group "network-rg"
```

### App Service Management

#### Create App Service Plan

```aibasic
10 (azure) create resource group "webapp-rg" in location "eastus"
20 (azure) create app service plan "webapp-plan" in resource group "webapp-rg" with sku {"name": "B1", "tier": "Basic", "size": "B1"} and is_linux True
```

#### Create Web App

```aibasic
30 (azure) create web app "mywebapp" in resource group "webapp-rg" with app_service_plan "webapp-plan" and runtime_stack {"name": "python", "version": "3.11"}
40 (azure) create web app "nodeapp" in resource group "webapp-rg" with app_service_plan "webapp-plan" and runtime_stack {"name": "node", "version": "18"}
```

#### List Web Apps

```aibasic
50 (azure) list web apps in resource group "webapp-rg"
```

### Container Instances

#### Create Container Instance

```aibasic
10 (azure) create resource group "container-rg" in location "eastus"
20 (azure) create container instance "web-container" in resource group "container-rg" with image "nginx:latest" and cpu 1.0 and memory 1.5 and ports [80, 443]
30 (azure) create container instance "app-container" in resource group "container-rg" with image "myapp:latest" and cpu 2.0 and memory 4.0 and ports [8080] and environment_variables {"DATABASE_URL": "postgresql://...", "API_KEY": "secret"}
```

#### List Container Instances

```aibasic
40 (azure) list container instances in resource group "container-rg"
```

### Key Vault Management

#### Create Key Vault

```aibasic
10 (azure) create resource group "security-rg" in location "eastus"
20 (azure) create key vault "myvault" in resource group "security-rg" with sku {"name": "standard"}
```

#### Set Secret

```aibasic
30 (azure) set key vault secret "database-password" in vault "myvault" with value "SecurePassword123!"
40 (azure) set key vault secret "api-key" in vault "myvault" with value "sk-1234567890abcdef"
```

#### Get Secret

```aibasic
50 (azure) get key vault secret "database-password" from vault "myvault"
```

#### List Secrets

```aibasic
60 (azure) list key vault secrets in vault "myvault"
```

### Cosmos DB Management

#### Create Cosmos DB Account

```aibasic
10 (azure) create resource group "cosmosdb-rg" in location "eastus"
20 (azure) create cosmos db account "mycosmosdb" in resource group "cosmosdb-rg" with kind "GlobalDocumentDB" and locations [{"location": "eastus", "failover_priority": 0}, {"location": "westus", "failover_priority": 1}]
```

#### Create Database and Container

```aibasic
30 (azure) create cosmos db database "app-database" in account "mycosmosdb" in resource group "cosmosdb-rg"
40 (azure) create cosmos db container "users" in database "app-database" account "mycosmosdb" in resource group "cosmosdb-rg" with partition_key "/userId" and throughput 400
```

### Utility Operations

#### Get Subscription Information

```aibasic
10 (azure) get subscription information
```

## Complete Examples

### Example 1: Deploy Multi-Tier Web Application

```aibasic
REM ============================================================================
REM Deploy a complete multi-tier web application on Azure
REM ============================================================================

10 (print) "Deploying multi-tier application to Azure..."

REM Create resource group
20 (azure) create resource group "webapp-rg" in location "eastus" with tags {"environment": "production", "project": "webapp"}

REM Create virtual network with subnets
30 (azure) create virtual network "app-vnet" in resource group "webapp-rg" with address_space "10.0.0.0/16" and subnets [{"name": "web-subnet", "address_prefix": "10.0.1.0/24"}, {"name": "app-subnet", "address_prefix": "10.0.2.0/24"}, {"name": "db-subnet", "address_prefix": "10.0.3.0/24"}]

REM Create storage account for application data
40 (azure) create storage account "webappstore001" in resource group "webapp-rg" with sku {"name": "Standard_GRS"} and kind "StorageV2"

REM Create SQL database
50 (azure) create sql server "webapp-sql" in resource group "webapp-rg" with admin_login "appadmin" and admin_password "SecurePassword123!"
60 (sleep) 60
70 (azure) create sql database "webapp-db" on server "webapp-sql" in resource group "webapp-rg" with sku {"name": "S1", "tier": "Standard"}

REM Create Key Vault for secrets
80 (azure) create key vault "webapp-vault" in resource group "webapp-rg" with sku {"name": "standard"}
90 (sleep) 30
100 (azure) set key vault secret "db-connection-string" in vault "webapp-vault" with value "Server=webapp-sql.database.windows.net;Database=webapp-db;User=appadmin;Password=SecurePassword123!"

REM Deploy web application
110 (azure) create app service plan "webapp-plan" in resource group "webapp-rg" with sku {"name": "P1v2", "tier": "PremiumV2"} and is_linux False
120 (azure) create web app "mywebapp" in resource group "webapp-rg" with app_service_plan "webapp-plan" and runtime_stack {"name": "dotnet", "version": "7.0"}

130 (print) "Multi-tier application deployed successfully!"
```

### Example 2: Container-Based Microservices

```aibasic
REM ============================================================================
REM Deploy containerized microservices on Azure Container Instances
REM ============================================================================

10 (print) "Deploying containerized microservices..."

REM Create resource group
20 (azure) create resource group "microservices-rg" in location "eastus"

REM Deploy API service
30 (azure) create container instance "api-service" in resource group "microservices-rg" with image "myapi:latest" and cpu 2.0 and memory 4.0 and ports [8080] and environment_variables {"DB_HOST": "db.example.com", "REDIS_URL": "redis://cache"}

REM Deploy worker service
40 (azure) create container instance "worker-service" in resource group "microservices-rg" with image "myworker:latest" and cpu 1.0 and memory 2.0 and environment_variables {"QUEUE_URL": "amqp://queue", "LOG_LEVEL": "INFO"}

REM Deploy web frontend
50 (azure) create container instance "web-frontend" in resource group "microservices-rg" with image "nginx:latest" and cpu 1.0 and memory 1.5 and ports [80, 443]

60 (print) "Microservices deployed successfully!"
```

### Example 3: Data Analytics Platform

```aibasic
REM ============================================================================
REM Deploy data analytics platform with storage and Cosmos DB
REM ============================================================================

10 (print) "Deploying data analytics platform..."

REM Create resource group
20 (azure) create resource group "analytics-rg" in location "eastus"

REM Create storage account for data lake
30 (azure) create storage account "datalake001" in resource group "analytics-rg" with sku {"name": "Standard_LRS"} and kind "StorageV2" and hierarchical_namespace True

REM Create Cosmos DB for real-time analytics
40 (azure) create cosmos db account "analytics-cosmos" in resource group "analytics-rg" with kind "GlobalDocumentDB" and locations [{"location": "eastus", "failover_priority": 0}]
50 (sleep) 120
60 (azure) create cosmos db database "analytics-db" in account "analytics-cosmos" in resource group "analytics-rg"
70 (azure) create cosmos db container "events" in database "analytics-db" account "analytics-cosmos" in resource group "analytics-rg" with partition_key "/eventType" and throughput 1000

REM Upload sample data
80 (file) write "sample-data.json" with content '{"eventType": "pageview", "userId": "12345", "timestamp": "2025-01-15T10:00:00Z"}'
90 (azure) upload file "sample-data.json" to blob storage "datalake001" in container "raw-data" as "events/2025/01/sample.json"

100 (print) "Data analytics platform deployed successfully!"
```

## Best Practices

### Security

1. **Use Service Principal Authentication** for production deployments
2. **Store secrets in Key Vault** - Never hardcode credentials
3. **Enable Azure Monitor** and Log Analytics for monitoring
4. **Implement Network Security Groups** to restrict access
5. **Use Managed Identities** when possible instead of service principals
6. **Enable encryption** at rest and in transit for all services
7. **Implement RBAC** (Role-Based Access Control) with least privilege

### Resource Management

1. **Use Resource Groups** to organize related resources
2. **Tag all resources** for cost tracking and management
3. **Use consistent naming conventions** (e.g., `{project}-{environment}-{resource}`)
4. **Implement resource locks** to prevent accidental deletion
5. **Monitor costs** with Azure Cost Management
6. **Clean up unused resources** regularly

### High Availability

1. **Use Availability Zones** for critical workloads
2. **Implement geo-replication** for databases (Standard_GRS, RA-GRS)
3. **Configure auto-scaling** for App Services and VMs
4. **Use Load Balancers** for distributing traffic
5. **Implement health checks** and monitoring

### Performance

1. **Choose appropriate VM sizes** based on workload
2. **Use Premium Storage** for I/O intensive workloads
3. **Enable CDN** for static content
4. **Implement caching** with Redis or Azure Cache
5. **Use Cosmos DB** for globally distributed applications

### Cost Optimization

1. **Start with smaller SKUs** and scale up as needed
2. **Use Reserved Instances** for long-running VMs
3. **Implement auto-shutdown** for dev/test VMs
4. **Use Azure Cost Management** to monitor spending
5. **Leverage Azure Hybrid Benefit** if you have existing licenses

## Error Handling

The Azure module raises `RuntimeError` exceptions with descriptive messages for all errors:

```aibasic
10 ON ERROR GOTO 100
20 (azure) create virtual machine "test-vm" in resource group "nonexistent-rg"
30 (print) "VM created successfully"
40 GOTO 999

100 REM Error handler
110 (print) "Error occurred during Azure operation"
120 (log) "Azure error: Check resource group exists"

999 (print) "Script completed"
```

## Troubleshooting

### Authentication Issues

**Problem:** `DefaultAzureCredential failed to retrieve token`

**Solution:**
1. Run `az login` to authenticate with Azure CLI
2. Or configure Service Principal in `aibasic.conf`
3. Check that SUBSCRIPTION_ID and TENANT_ID are correct

### Resource Already Exists

**Problem:** `Resource with name 'xxx' already exists`

**Solution:**
1. Use unique names for resources
2. Add prefixes or suffixes (timestamps, environment)
3. Delete existing resource first

### Timeout Errors

**Problem:** Operations timeout during resource creation

**Solution:**
1. Add `(sleep)` commands between operations
2. Increase timeout in Azure SDK configuration
3. Check Azure service health status

### Permission Denied

**Problem:** `Insufficient permissions to perform operation`

**Solution:**
1. Verify Service Principal has Contributor role
2. Check RBAC permissions on subscription/resource group
3. Ensure correct SUBSCRIPTION_ID is configured

## Integration with Other Modules

### Azure + Terraform

```aibasic
10 (terraform) initialize terraform in directory "./terraform"
20 (terraform) apply terraform configuration with auto approve
30 (sleep) 60
40 (azure) list all resource groups
50 (azure) get virtual machine "terraform-vm" in resource group "terraform-rg"
```

### Azure + Docker

```aibasic
10 (docker) build image from "./app" tagged "myapp:latest"
20 (docker) push image "myapp:latest" to registry "myregistry.azurecr.io"
30 (azure) create container instance "app" in resource group "containers-rg" with image "myregistry.azurecr.io/myapp:latest"
```

### Azure + PostgreSQL + S3

```aibasic
10 (postgres) connect to database and query "SELECT * FROM users"
20 (csv) save query results to "users.csv"
30 (azure) upload file "users.csv" to blob storage "backup001" in container "database-backups"
40 (print) "Database backup uploaded to Azure Blob Storage"
```

## Module API Reference

### Class: AzureModule

**Location:** `src/aibasic/modules/azure_module.py`

#### Properties

- `credential` - Azure authentication credential (lazy-loaded)
- `resource_client` - Resource management client (lazy-loaded)
- `compute_client` - Compute management client (lazy-loaded)
- `storage_client` - Storage management client (lazy-loaded)
- `sql_client` - SQL management client (lazy-loaded)
- `network_client` - Network management client (lazy-loaded)
- `web_client` - Web/App Service management client (lazy-loaded)
- `container_client` - Container Instance management client (lazy-loaded)
- `keyvault_client` - Key Vault management client (lazy-loaded)
- `cosmosdb_client` - Cosmos DB management client (lazy-loaded)

#### Methods

##### Resource Groups

- `resource_group_create(name, location, tags=None)` - Create resource group
- `resource_group_list()` - List all resource groups
- `resource_group_delete(name)` - Delete resource group
- `get_subscription_info()` - Get subscription information

##### Virtual Machines

- `vm_create(name, resource_group, **kwargs)` - Create virtual machine
- `vm_list(resource_group=None)` - List virtual machines
- `vm_start(name, resource_group)` - Start virtual machine
- `vm_stop(name, resource_group)` - Stop virtual machine
- `vm_restart(name, resource_group)` - Restart virtual machine
- `vm_delete(name, resource_group)` - Delete virtual machine
- `vm_get(name, resource_group)` - Get VM details

##### Storage

- `storage_account_create(name, resource_group, **kwargs)` - Create storage account
- `storage_account_list(resource_group=None)` - List storage accounts
- `storage_account_delete(name, resource_group)` - Delete storage account
- `storage_account_get_keys(name, resource_group)` - Get access keys
- `blob_upload_file(storage_account, container, blob_name, file_path)` - Upload blob
- `blob_download_file(storage_account, container, blob_name, file_path)` - Download blob
- `blob_list(storage_account, container)` - List blobs

##### SQL Database

- `sql_server_create(name, resource_group, **kwargs)` - Create SQL server
- `sql_database_create(name, server, resource_group, **kwargs)` - Create database
- `sql_database_list(server, resource_group)` - List databases

##### Virtual Networks

- `vnet_create(name, resource_group, **kwargs)` - Create virtual network
- `vnet_list(resource_group=None)` - List virtual networks

## Dependencies

The Azure module requires the following Python packages (automatically installed via `requirements.txt`):

```
azure-mgmt-compute>=30.0.0
azure-mgmt-storage>=21.0.0
azure-mgmt-resource>=23.0.0
azure-mgmt-network>=25.0.0
azure-mgmt-sql>=4.0.0
azure-mgmt-web>=7.0.0
azure-mgmt-containerinstance>=10.0.0
azure-mgmt-keyvault>=10.0.0
azure-mgmt-cosmosdb>=9.0.0
azure-identity>=1.12.0
```

## Additional Resources

- **Azure SDK for Python Documentation:** https://docs.microsoft.com/python/azure/
- **Azure Portal:** https://portal.azure.com
- **Azure CLI Documentation:** https://docs.microsoft.com/cli/azure/
- **Azure Architecture Center:** https://docs.microsoft.com/azure/architecture/
- **Azure Pricing Calculator:** https://azure.microsoft.com/pricing/calculator/
- **Example File:** `examples/example_azure.aib` (22 complete examples)

## Version History

- **v1.0** (2025-01-15) - Initial release
  - Resource Group management
  - Virtual Machine operations
  - Storage Account and Blob Storage
  - SQL Database management
  - Virtual Network management
  - App Service deployment
  - Container Instances
  - Key Vault secrets management
  - Cosmos DB support
  - Service Principal and DefaultAzureCredential authentication

---

**Module:** Azure (Module #25)
**Task Types:** 46 total (azure is task type #46)
**Total Modules:** 25
