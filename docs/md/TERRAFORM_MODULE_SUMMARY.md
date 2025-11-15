# Terraform Module - Complete Reference

**Module #22 | Task Type: `terraform` | Version: 1.0**

## Overview

The **Terraform module** enables Infrastructure as Code (IaC) management through HashiCorp Terraform, allowing you to define, provision, and manage cloud infrastructure using natural language instructions. This module provides a complete Python wrapper around the Terraform CLI.

### Key Capabilities

- **Multi-Cloud Support**: AWS, Azure, GCP, Kubernetes, DigitalOcean, and 1000+ providers
- **Workspace Management**: Environment isolation (dev, staging, prod)
- **State Management**: Full state operations and remote backends
- **Variable Management**: Dynamic variable configuration
- **Plan & Apply**: Preview and apply infrastructure changes
- **Import Resources**: Bring existing infrastructure under Terraform control

---

## Configuration

### Basic Configuration (`aibasic.conf`)

```ini
[terraform]
# Terraform Binary Path (optional - defaults to system PATH)
TERRAFORM_BIN = /usr/local/bin/terraform

# Working Directory (where Terraform configuration files are located)
WORKING_DIR = ./terraform

# Auto-Approve (DANGEROUS - use only for dev/testing)
AUTO_APPROVE = false  # Set to true to skip confirmation prompts

# Parallelism (number of concurrent operations)
PARALLELISM = 10  # Default is 10, adjust based on rate limits

# Default Workspace
DEFAULT_WORKSPACE = default  # or dev, staging, prod

# Backend Configuration (for remote state storage)
BACKEND_TYPE = s3  # Options: s3, azurerm, gcs, local, remote, consul
BACKEND_CONFIG = {"bucket": "my-tf-state", "key": "terraform.tfstate", "region": "us-east-1"}

# Variables (global variables for all Terraform operations)
VARIABLES = {"environment": "dev", "region": "us-east-1"}
```

### Backend Types

| Backend | Use Case | Configuration |
|---------|----------|---------------|
| **s3** | AWS S3 | `{"bucket": "...", "key": "...", "region": "..."}` |
| **azurerm** | Azure Storage | `{"storage_account_name": "...", "container_name": "...", "key": "..."}` |
| **gcs** | Google Cloud Storage | `{"bucket": "...", "prefix": "..."}` |
| **local** | Local filesystem | `{"path": "terraform.tfstate"}` |
| **remote** | Terraform Cloud | `{"organization": "...", "workspaces": {"name": "..."}}` |
| **consul** | HashiCorp Consul | `{"address": "...", "path": "..."}` |

---

## Core Operations

### 1. Initialization

Initialize Terraform working directory with required providers and modules.

```aibasic
10 (terraform) initialize terraform in directory "./terraform"
20 print "Terraform initialized:" and _result
```

**With backend configuration:**

```aibasic
10 set backend_config to dict with "bucket" as "my-tf-state"
20 set backend_config["key"] to "terraform.tfstate"
30 set backend_config["region"] to "us-east-1"
40 (terraform) initialize terraform in directory "./terraform" with backend backend_config
50 print "Terraform initialized with S3 backend"
```

### 2. Validation

Validate Terraform configuration syntax and logic.

```aibasic
10 (terraform) validate terraform configuration
20 print "Validation result:" and _result
```

### 3. Formatting

Format Terraform configuration files to canonical style.

```aibasic
10 (terraform) format terraform configuration files
20 print "Formatted files:" and _result
```

### 4. Planning

Create an execution plan showing what Terraform will do.

```aibasic
10 (terraform) create terraform plan
20 print "Plan:" and _result

# Save plan to file for later apply
30 (terraform) create terraform plan and save to "plan.out"
40 print "Plan saved to file"

# Plan with variables
50 set vars to dict with "instance_type" as "t2.micro" and "region" as "us-east-1"
60 (terraform) plan terraform with variables vars
```

### 5. Apply

Apply infrastructure changes.

```aibasic
# Interactive apply (requires confirmation)
10 (terraform) apply terraform configuration
20 print "Infrastructure deployed:" and _result

# Auto-approve (for automation/CI/CD)
30 (terraform) apply terraform configuration with auto approve

# Apply with variables
40 set vars to dict with "environment" as "production"
50 (terraform) apply terraform with variables vars and auto approve

# Apply saved plan
60 (terraform) apply terraform plan from file "plan.out" with auto approve
```

### 6. Outputs

Retrieve output values from Terraform state.

```aibasic
# Get all outputs
10 (terraform) get all terraform outputs
20 print "All outputs:" and _result

# Get specific output
30 (terraform) get terraform output "instance_public_ip"
40 set public_ip to _result
50 print "Public IP:" and public_ip

# Get output in JSON format
60 (terraform) get terraform output "database_config" in json format
70 print "Database config:" and _result
```

### 7. Destroy

Destroy managed infrastructure.

```aibasic
# Interactive destroy (requires confirmation)
10 (terraform) destroy terraform infrastructure
20 print "Infrastructure destroyed"

# Auto-approve destroy
30 (terraform) destroy terraform with auto approve

# Destroy with variables
40 set vars to dict with "environment" as "test"
50 (terraform) destroy terraform with variables vars and auto approve
```

---

## Workspace Management

Workspaces allow you to manage multiple environments (dev, staging, prod) from a single configuration.

### List Workspaces

```aibasic
10 (terraform) list all terraform workspaces
20 print "Available workspaces:" and _result
```

### Create Workspace

```aibasic
10 (terraform) create new terraform workspace "staging"
20 print "Created workspace: staging"
```

### Select Workspace

```aibasic
10 (terraform) select terraform workspace "production"
20 print "Switched to workspace: production"
```

### Delete Workspace

```aibasic
10 (terraform) delete terraform workspace "old-env"
20 print "Deleted workspace: old-env"
```

### Complete Workspace Example

```aibasic
10 (terraform) create new terraform workspace "dev"
20 (terraform) select terraform workspace "dev"
30 set dev_vars to dict with "instance_count" as 1 and "instance_type" as "t2.micro"
40 (terraform) apply terraform with variables dev_vars and auto approve
50 print "Dev environment deployed"

60 (terraform) create new terraform workspace "prod"
70 (terraform) select terraform workspace "prod"
80 set prod_vars to dict with "instance_count" as 5 and "instance_type" as "t3.large"
90 (terraform) apply terraform with variables prod_vars and auto approve
100 print "Production environment deployed"
```

---

## State Management

### List State Resources

```aibasic
10 (terraform) list all resources in terraform state
20 print "Resources:" and _result
```

### Show Resource State

```aibasic
10 (terraform) show terraform state for resource "aws_instance.web"
20 print "Instance details:" and _result
```

### Remove from State

Remove a resource from Terraform state without destroying it.

```aibasic
10 (terraform) remove resource "aws_s3_bucket.temp" from terraform state
20 print "Resource removed from state (not destroyed)"
```

### Refresh State

Sync state with real infrastructure.

```aibasic
10 (terraform) refresh terraform state
20 print "State refreshed from real infrastructure"
```

### Show Current State

```aibasic
10 (terraform) show terraform state
20 print "Current state:" and _result
```

---

## Import Existing Resources

Bring existing infrastructure under Terraform control.

```aibasic
10 set resource_address to "aws_instance.existing_server"
20 set resource_id to "i-1234567890abcdef0"
30 (terraform) import terraform resource at resource_address with id resource_id
40 print "Imported existing resource"
```

### Import Examples

**AWS EC2 Instance:**
```aibasic
10 (terraform) import terraform resource at "aws_instance.web" with id "i-1234567890abcdef0"
```

**AWS S3 Bucket:**
```aibasic
10 (terraform) import terraform resource at "aws_s3_bucket.data" with id "my-existing-bucket"
```

**Azure VM:**
```aibasic
10 (terraform) import terraform resource at "azurerm_virtual_machine.main" with id "/subscriptions/.../resourceGroups/.../providers/..."
```

---

## Advanced Features

### Parallelism Control

Control the number of concurrent operations to avoid rate limits.

```aibasic
10 set vars to dict with "region" as "us-east-1"
20 (terraform) plan terraform with variables vars and parallelism 5
30 (terraform) apply terraform with variables vars and parallelism 5 and auto approve
```

### Variable Merging

Combine configuration variables with runtime variables.

```aibasic
# Configuration has default variables
# Runtime variables will be merged
10 set runtime_vars to dict with "environment" as "staging"
20 set runtime_vars["override_value"] to "custom"
30 (terraform) apply terraform with variables runtime_vars and auto approve
```

---

## Complete Examples

### Example 1: AWS Infrastructure Deployment

```aibasic
10 print "=== Deploying AWS Infrastructure ==="
20 (terraform) initialize terraform in directory "./terraform/aws"
30 (terraform) validate terraform configuration
40 if _result contains "Error" goto 900
50
60 set aws_vars to dict with "region" as "us-east-1"
70 set aws_vars["instance_type"] to "t3.micro"
80 set aws_vars["key_name"] to "my-key-pair"
90 set aws_vars["environment"] to "production"
100
110 (terraform) plan terraform with variables aws_vars
120 print "Plan created:" and _result
130
140 (terraform) apply terraform with variables aws_vars and auto approve
150 print "Infrastructure deployed!"
160
170 (terraform) get terraform output "instance_public_ip"
180 print "EC2 Public IP:" and _result
190 goto 999
900 print "Validation failed. Check Terraform configuration."
999 print "Complete"
```

### Example 2: Multi-Environment Deployment

```aibasic
10 print "=== Multi-Environment Deployment ==="
20 (terraform) initialize terraform in directory "./terraform"
30
40 # Deploy Development
50 (terraform) select terraform workspace "dev"
60 set dev_vars to dict with "env" as "dev" and "instance_count" as 1
70 (terraform) apply terraform with variables dev_vars and auto approve
80 print "Dev environment deployed"
90
100 # Deploy Staging
110 (terraform) select terraform workspace "staging"
120 set staging_vars to dict with "env" as "staging" and "instance_count" as 2
130 (terraform) apply terraform with variables staging_vars and auto approve
140 print "Staging environment deployed"
150
160 # Deploy Production
170 (terraform) select terraform workspace "prod"
180 set prod_vars to dict with "env" as "prod" and "instance_count" as 5
190 (terraform) apply terraform with variables prod_vars and auto approve
200 print "Production environment deployed"
210
220 print "All environments deployed successfully!"
```

### Example 3: Infrastructure Lifecycle with Error Handling

```aibasic
10 print "=== Infrastructure Lifecycle ==="
20 on error goto 900
30
40 # Validate
50 (terraform) validate terraform configuration
60 if _result contains "Error" goto 910
70
80 # Format
90 (terraform) format terraform configuration files
100
110 # Plan
120 set vars to dict with "environment" as "test"
130 (terraform) plan terraform with variables vars and save to "plan.out"
140
150 # Apply
160 (terraform) apply terraform plan from file "plan.out" with auto approve
170 print "Infrastructure created"
180
190 # Get outputs
200 (terraform) get all terraform outputs
210 print "Outputs:" and _result
220
230 # Simulate usage
240 print "Infrastructure is running... (simulating usage)"
250
260 # Destroy
270 print "Tearing down infrastructure..."
280 (terraform) destroy terraform with variables vars and auto approve
290 print "Infrastructure destroyed"
300 goto 999
900 print "ERROR:" and _last_error
910 print "Validation or deployment failed"
999 print "Complete"
```

### Example 4: Azure Infrastructure with Remote State

```aibasic
10 print "=== Azure Deployment with Remote State ==="
20
30 # Initialize with Azure backend
40 set backend_config to dict with "storage_account_name" as "mytfstate"
50 set backend_config["container_name"] to "tfstate"
60 set backend_config["key"] to "terraform.tfstate"
70 (terraform) initialize terraform in directory "./terraform/azure" with backend backend_config
80
90 # Deploy Azure resources
100 set azure_vars to dict with "location" as "East US"
110 set azure_vars["vm_size"] to "Standard_B2s"
120 set azure_vars["environment"] to "production"
130
140 (terraform) apply terraform with variables azure_vars and auto approve
150 print "Azure infrastructure deployed!"
160
170 (terraform) get terraform output "vm_public_ip"
180 print "VM Public IP:" and _result
```

### Example 5: CI/CD Pipeline Integration

```aibasic
10 print "=== CI/CD Terraform Pipeline ==="
20 on error goto 900
30
40 # Step 1: Validate
50 print "Step 1: Validating configuration..."
60 (terraform) validate terraform configuration
70 if _result contains "Error" goto 900
80 print "✓ Validation passed"
90
100 # Step 2: Format check
110 print "Step 2: Checking formatting..."
120 (terraform) format terraform configuration files
130 print "✓ Format check complete"
140
150 # Step 3: Plan
160 print "Step 3: Creating plan..."
170 set ci_vars to dict with "environment" as "staging" and "version" as "1.0.0"
180 (terraform) plan terraform with variables ci_vars and save to "ci-plan.out"
190 print "✓ Plan created"
200
210 # Step 4: Apply (would require approval in real CI/CD)
220 print "Step 4: Applying changes..."
230 (terraform) apply terraform plan from file "ci-plan.out" with auto approve
240 print "✓ Deployment successful"
250
260 # Step 5: Verify outputs
270 print "Step 5: Verifying deployment..."
280 (terraform) get all terraform outputs
290 print "Outputs:" and _result
300 print "✓ Pipeline complete"
310 goto 999
900 print "❌ Pipeline failed:" and _last_error
910 print "Check logs and retry"
999 print "Pipeline finished"
```

### Example 6: Disaster Recovery Setup

```aibasic
10 print "=== Disaster Recovery Multi-Region Setup ==="
20
30 # Primary Region (us-east-1)
40 print "Deploying primary region..."
50 (terraform) select terraform workspace "primary"
60 set primary_vars to dict with "region" as "us-east-1" and "is_primary" as true
70 (terraform) initialize terraform in directory "./terraform/dr"
80 (terraform) apply terraform with variables primary_vars and auto approve
90 (terraform) get terraform output "primary_endpoint"
100 set primary_endpoint to _result
110 print "Primary region deployed:" and primary_endpoint
120
130 # DR Region (us-west-2)
140 print "Deploying DR region..."
150 (terraform) select terraform workspace "dr"
160 set dr_vars to dict with "region" as "us-west-2" and "is_primary" as false
170 set dr_vars["primary_endpoint"] to primary_endpoint
180 (terraform) initialize terraform in directory "./terraform/dr"
190 (terraform) apply terraform with variables dr_vars and auto approve
200 (terraform) get terraform output "dr_endpoint"
210 print "DR region deployed:" and _result
220
230 print "Disaster recovery setup complete!"
```

---

## Best Practices

### 1. Always Validate Before Apply

```aibasic
10 (terraform) validate terraform configuration
20 if _result contains "Error" goto 900
30 (terraform) apply terraform with auto approve
```

### 2. Use Workspaces for Environment Separation

```aibasic
10 (terraform) create new terraform workspace "dev"
20 (terraform) create new terraform workspace "staging"
30 (terraform) create new terraform workspace "prod"
```

### 3. Store State Remotely for Team Collaboration

```aibasic
10 set backend_config to dict with "bucket" as "company-tf-state"
20 set backend_config["key"] to "terraform.tfstate"
30 set backend_config["region"] to "us-east-1"
40 (terraform) initialize terraform with backend backend_config
```

### 4. Use Variables for Flexibility

```aibasic
10 set vars to dict with "environment" as "production"
20 set vars["region"] to "us-east-1"
30 set vars["instance_type"] to "t3.large"
40 (terraform) apply terraform with variables vars and auto approve
```

### 5. Review Plans Before Applying

```aibasic
10 (terraform) create terraform plan and save to "plan.out"
20 (terraform) show terraform plan from file "plan.out"
30 print "Review plan above before applying"
40 # In production, require manual approval here
50 (terraform) apply terraform plan from file "plan.out" with auto approve
```

### 6. Handle Errors Gracefully

```aibasic
10 on error goto 900
20 (terraform) apply terraform with auto approve
30 print "Success!"
40 goto 999
900 print "Error occurred:" and _last_error
910 print "Rolling back or notifying team..."
999 print "Complete"
```

### 7. Clean Up Temporary Resources

```aibasic
10 (terraform) select terraform workspace "test"
20 (terraform) destroy terraform with auto approve
30 (terraform) delete terraform workspace "test"
```

---

## Security Considerations

### 1. Never Hardcode Credentials

❌ **Bad:**
```aibasic
10 set vars to dict with "db_password" as "hardcoded_password"
```

✅ **Good:**
```aibasic
10 (vault) get secret "database/credentials"
20 set vars to dict with "db_password" as _result["password"]
```

### 2. Use Auto-Approve Cautiously

- **Development**: OK to use auto-approve
- **Staging**: Use with caution
- **Production**: NEVER use auto-approve

### 3. Encrypt Remote State

Always use encrypted backends:
- AWS S3: Enable server-side encryption
- Azure Storage: Enable encryption at rest
- GCS: Enable encryption by default

### 4. Limit Parallelism for Rate Limits

```aibasic
10 (terraform) apply terraform with parallelism 3 and auto approve
```

---

## Troubleshooting

### Common Issues

#### 1. "Terraform not found"

**Problem**: Terraform binary not in PATH

**Solution**: Set TERRAFORM_BIN in configuration:
```ini
[terraform]
TERRAFORM_BIN = /usr/local/bin/terraform
```

#### 2. "Backend initialization failed"

**Problem**: Backend configuration incorrect or inaccessible

**Solution**: Verify backend configuration:
```aibasic
10 set backend_config to dict with "bucket" as "correct-bucket-name"
20 (terraform) initialize terraform with backend backend_config
```

#### 3. "State locked"

**Problem**: Another Terraform operation is in progress

**Solution**: Wait for other operation to complete, or manually unlock (use with caution)

#### 4. "Resource already exists"

**Problem**: Trying to create a resource that already exists

**Solution**: Import existing resource:
```aibasic
10 (terraform) import terraform resource at "aws_instance.web" with id "i-existing"
```

#### 5. "Plan shows unexpected changes"

**Problem**: State out of sync with real infrastructure

**Solution**: Refresh state:
```aibasic
10 (terraform) refresh terraform state
20 (terraform) plan terraform
```

---

## Module Integration Examples

### Example: Terraform + PostgreSQL

Deploy database infrastructure and populate it:

```aibasic
10 # Deploy PostgreSQL RDS with Terraform
20 (terraform) apply terraform with auto approve
30 (terraform) get terraform output "db_endpoint"
40 set db_endpoint to _result
50
60 # Connect to deployed database
70 (postgres) connect to database at db_endpoint
80 (postgres) execute query "CREATE TABLE users (id SERIAL PRIMARY KEY, name VARCHAR(100))"
90 print "Database deployed and initialized"
```

### Example: Terraform + S3

Deploy S3 bucket and upload files:

```aibasic
10 # Deploy S3 bucket with Terraform
20 (terraform) apply terraform with auto approve
30 (terraform) get terraform output "bucket_name"
40 set bucket_name to _result
50
60 # Upload files to deployed bucket
70 (s3) upload file "data.csv" to bucket bucket_name
80 print "Bucket deployed and populated"
```

### Example: Terraform + Slack

Deploy infrastructure and notify team:

```aibasic
10 # Deploy infrastructure
20 (terraform) apply terraform with auto approve
30 (terraform) get all terraform outputs
40 set outputs to _result
50
60 # Notify team on Slack
70 (slack) send message to channel "#devops"
80 (slack) set text to "Infrastructure deployed successfully!"
90 (slack) add field "Environment" with value "production"
100 (slack) add field "Outputs" with value outputs
```

---

## Performance Tips

1. **Use Parallelism**: Adjust based on provider rate limits
   ```aibasic
   10 (terraform) apply terraform with parallelism 10 and auto approve
   ```

2. **Targeted Operations**: Apply changes to specific resources
   ```aibasic
   10 (terraform) apply terraform targeting resource "aws_instance.web" with auto approve
   ```

3. **Selective Refresh**: Refresh only when necessary
   ```aibasic
   10 (terraform) plan terraform with refresh false
   ```

4. **Workspace Isolation**: Use separate workspaces to avoid lock contention
   ```aibasic
   10 (terraform) select terraform workspace "team-a"
   ```

---

## Supported Terraform Providers

The Terraform module supports **all Terraform providers** (1000+), including:

### Cloud Providers
- **AWS** (Amazon Web Services)
- **Azure** (Microsoft Azure)
- **GCP** (Google Cloud Platform)
- **DigitalOcean**
- **Linode**
- **Oracle Cloud**
- **IBM Cloud**
- **Alibaba Cloud**

### Infrastructure
- **Kubernetes**
- **Docker**
- **VMware vSphere**
- **OpenStack**

### SaaS/PaaS
- **Cloudflare**
- **Datadog**
- **PagerDuty**
- **GitHub**
- **GitLab**

### Databases
- **MongoDB Atlas**
- **Snowflake**
- **Databricks**

---

## Reference

### Task Type
- **Code**: `terraform`
- **Purpose**: Infrastructure as Code (IaC) management

### Dependencies
- `python-terraform>=0.10.1`
- Terraform CLI (must be installed separately)

### Configuration File
- Section: `[terraform]`
- File: `aibasic.conf`

### Example File
- Location: `examples/example_terraform.aib`
- 22 complete examples covering all major use cases

---

## Version History

**v1.0 (Current)**
- Initial release
- Full Terraform CLI wrapper
- Workspace management
- State operations
- Multi-cloud support
- Backend configuration
- Variable management

---

## Additional Resources

- **Terraform Documentation**: https://www.terraform.io/docs
- **Terraform Registry**: https://registry.terraform.io
- **Best Practices**: https://www.terraform.io/docs/cloud/guides/recommended-practices
- **Example Repository**: `examples/example_terraform.aib`

---

**Module #22 | AIbasic v1.0 | Infrastructure as Code Module**
