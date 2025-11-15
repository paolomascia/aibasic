# Kubernetes Module - Complete Reference

**Module #24 | Task Type: `kubernetes` | Version: 1.0**

## Overview

The **Kubernetes module** provides comprehensive Kubernetes cluster and resource management through the official Kubernetes Python client, enabling you to manage pods, deployments, services, and other resources using natural language instructions.

### Key Capabilities

- **Pod Management**: Create, list, delete, get logs, exec commands
- **Deployment Management**: Create, scale, rollout restart, delete
- **Service Management**: ClusterIP, NodePort, LoadBalancer services
- **ConfigMap & Secret Management**: Configuration and sensitive data
- **Namespace Management**: Multi-tenancy and resource isolation
- **Resource Monitoring**: Logs, events, cluster information
- **Node Management**: Cluster node information and status

---

## Configuration

### Basic Configuration (`aibasic.conf`)

```ini
[kubernetes]
# Kubeconfig File Path
KUBECONFIG_PATH = ~/.kube/config  # Standard kubeconfig location

# Context (cluster to use from kubeconfig)
CONTEXT = default  # Use default context

# Default Namespace
NAMESPACE = default  # Default namespace for operations

# Direct API Server Connection (alternative to kubeconfig)
API_SERVER = https://kubernetes.default.svc  # In-cluster
TOKEN = <service-account-token>  # Service account token

# TLS/SSL Settings
VERIFY_SSL = true  # Verify SSL certificates
CA_CERT = /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
```

---

## Pod Operations

### Create and Manage Pods

```aibasic
# Simple pod
10 (kubernetes) create pod named "nginx-pod" from image "nginx:latest"
20 print "Pod created:" and _result

# Pod with environment variables
30 set env to dict with "DB_HOST" as "postgres.default.svc"
40 set env["DB_PORT"] to "5432"
50 (kubernetes) create pod named "app-pod" from image "myapp:1.0"
60 (kubernetes) with environment env
70 print "Application pod created"

# Pod with ports
80 set ports to list 8080, 8443
90 (kubernetes) create pod named "web-pod" from image "webapp:latest"
100 (kubernetes) with ports ports

# Pod with command
110 (kubernetes) create pod named "worker-pod" from image "worker:latest"
120 (kubernetes) with command list "/app/worker", "--mode=async"
```

### List and Get Pods

```aibasic
# List all pods
10 (kubernetes) list all pods in namespace "default"
20 print "Pods:" and _result

# List with label selector
30 (kubernetes) list all pods with label "app=webapp"
40 print "Web app pods:" and _result

# Get specific pod
50 (kubernetes) get pod "nginx-pod" details
60 print "Pod details:" and _result
```

### Pod Logs and Exec

```aibasic
# Get logs
10 (kubernetes) get logs from pod "app-pod" tail 100 lines
20 print "Logs:" and _result

# Get logs with follow
30 (kubernetes) get logs from pod "app-pod" follow
40 print "Live logs:" and _result

# Execute command
50 (kubernetes) exec command list "whoami" in pod "app-pod"
60 print "User:" and _result

70 (kubernetes) exec command list "ls", "-la", "/app" in pod "app-pod"
80 print "Directory:" and _result
```

### Delete Pods

```aibasic
10 (kubernetes) delete pod "nginx-pod"
20 print "Pod deleted"
```

---

## Deployment Operations

### Create Deployments

```aibasic
# Simple deployment
10 (kubernetes) create deployment named "web-app" from image "nginx:latest"
20 (kubernetes) with 3 replicas
30 print "Deployment created"

# Deployment with environment and ports
40 set env to dict with "REDIS_HOST" as "redis-service"
50 set ports to list 80
60 (kubernetes) create deployment named "api" from image "api:v1.0"
70 (kubernetes) with 5 replicas and environment env and ports ports
80 print "API deployment created"

# Deployment with labels
90 set labels to dict with "app" as "myapp" and "tier" as "frontend"
100 (kubernetes) create deployment named "frontend" from image "frontend:latest"
110 (kubernetes) with 2 replicas and labels labels
```

### Scale Deployments

```aibasic
# Scale up
10 (kubernetes) scale deployment "web-app" to 10 replicas
20 print "Scaled to 10 replicas"

# Scale down
30 (kubernetes) scale deployment "web-app" to 3 replicas
40 print "Scaled to 3 replicas"
```

### Rollout Operations

```aibasic
# Rollout restart
10 (kubernetes) rollout restart deployment "web-app"
20 print "Deployment restarted"

# List deployments
30 (kubernetes) list all deployments
40 print "Deployments:" and _result
```

### Delete Deployments

```aibasic
10 (kubernetes) delete deployment "web-app"
20 print "Deployment deleted"
```

---

## Service Operations

### Create Services

```aibasic
# ClusterIP service
10 set selector to dict with "app" as "web-app"
20 (kubernetes) create service named "web-service" on port 80 target port 80
30 (kubernetes) with type "ClusterIP" and selector selector
40 print "ClusterIP service created"

# LoadBalancer service
50 (kubernetes) create service named "web-lb" on port 80 target port 8080
60 (kubernetes) with type "LoadBalancer" and selector selector
70 print "LoadBalancer service created"

# NodePort service
80 (kubernetes) create service named "web-nodeport" on port 80 target port 8080
90 (kubernetes) with type "NodePort" and selector selector
```

### List and Delete Services

```aibasic
# List services
10 (kubernetes) list all services
20 print "Services:" and _result

# Delete service
30 (kubernetes) delete service "web-service"
40 print "Service deleted"
```

---

## ConfigMap and Secret Operations

### ConfigMap Management

```aibasic
# Create ConfigMap
10 set config_data to dict with "app.properties" as "server.port=8080"
20 set config_data["database.url"] to "postgres://db:5432/mydb"
30 (kubernetes) create configmap named "app-config" with data config_data
40 print "ConfigMap created"

# List ConfigMaps
50 (kubernetes) list all configmaps
60 print "ConfigMaps:" and _result

# Delete ConfigMap
70 (kubernetes) delete configmap "app-config"
```

### Secret Management

```aibasic
# Create Secret
10 set secret_data to dict with "username" as "admin"
20 set secret_data["password"] to "secret123"
30 (kubernetes) create secret named "db-creds" with data secret_data
40 print "Secret created"

# List Secrets
50 (kubernetes) list all secrets
60 print "Secrets:" and _result

# Delete Secret
70 (kubernetes) delete secret "db-creds"
```

---

## Namespace Operations

### Create and Manage Namespaces

```aibasic
# Create namespaces
10 (kubernetes) create namespace "development"
20 (kubernetes) create namespace "staging"
30 (kubernetes) create namespace "production"
40 print "Namespaces created"

# List namespaces
50 (kubernetes) list all namespaces
60 print "Namespaces:" and _result

# Delete namespace
70 (kubernetes) delete namespace "development"
```

---

## Cluster Information

### Get Cluster Info

```aibasic
# Get cluster information
10 (kubernetes) get cluster info
20 print "Cluster info:" and _result

# List nodes
30 (kubernetes) list all nodes
40 print "Nodes:" and _result

# Get specific node
50 (kubernetes) get node "node-1" details
60 print "Node details:" and _result
```

### Events

```aibasic
# List events
10 (kubernetes) list events in namespace "default"
20 print "Events:" and _result
```

---

## Complete Application Example

```aibasic
10 print "=== Deploying Complete Application Stack ==="
20
30 # Create namespace
40 (kubernetes) create namespace "myapp"
50 print "Namespace created"
60
70 # Deploy database
80 set db_env to dict with "POSTGRES_PASSWORD" as "dbpass123"
90 set db_env["POSTGRES_DB"] to "appdb"
100 (kubernetes) create deployment named "postgres" from image "postgres:15"
110 (kubernetes) in namespace "myapp" with 1 replica and environment db_env
120 print "Database deployed"
130
140 # Create database service
150 set db_selector to dict with "app" as "postgres"
160 (kubernetes) create service named "postgres-service" on port 5432 target port 5432
170 (kubernetes) in namespace "myapp" with type "ClusterIP" and selector db_selector
180 print "Database service created"
190
200 # Deploy application
210 set app_env to dict with "DATABASE_URL" as "postgres://postgres-service:5432/appdb"
220 set app_ports to list 8080
230 (kubernetes) create deployment named "webapp" from image "myapp:1.0"
240 (kubernetes) in namespace "myapp" with 3 replicas and environment app_env and ports app_ports
250 print "Application deployed"
260
270 # Create application service
280 set app_selector to dict with "app" as "webapp"
290 (kubernetes) create service named "webapp-service" on port 80 target port 8080
300 (kubernetes) in namespace "myapp" with type "LoadBalancer" and selector app_selector
310 print "Application service created"
320
330 print "Application stack deployed successfully!"
```

---

## Best Practices

### 1. Use Namespaces for Isolation

```aibasic
10 (kubernetes) create namespace "production"
20 (kubernetes) create deployment named "app" from image "app:v1.0"
30 (kubernetes) in namespace "production" with 5 replicas
```

### 2. Set Resource Limits (Requires Advanced Pod Spec)

```aibasic
# Note: Resource limits require more complex pod specification
# Use Deployment spec with resource requests/limits in production
```

### 3. Use ConfigMaps for Configuration

```aibasic
10 set config to dict with "log.level" as "INFO"
20 (kubernetes) create configmap named "app-config" with data config
30 # Mount ConfigMap in pod (requires advanced spec)
```

### 4. Use Secrets for Sensitive Data

```aibasic
10 set creds to dict with "api-key" as "secret123"
20 (kubernetes) create secret named "api-creds" with data creds
30 # Mount Secret in pod (requires advanced spec)
```

### 5. Implement Health Checks

```aibasic
# Liveness and readiness probes require advanced deployment spec
# Best practice: Define in YAML and apply with kubectl
```

### 6. Use Labels for Organization

```aibasic
10 set labels to dict with "app" as "myapp" and "env" as "prod" and "version" as "v1.0"
20 (kubernetes) create deployment with labels labels
```

### 7. Monitor with Logs and Events

```aibasic
10 (kubernetes) get logs from pod "app-pod" tail 100 lines
20 (kubernetes) list events in namespace "production"
```

---

## Security Considerations

### 1. Use RBAC

```aibasic
# Configure proper Role-Based Access Control
# Use service accounts with limited permissions
```

### 2. Network Policies

```aibasic
# Implement network policies to restrict pod-to-pod communication
# Requires NetworkPolicy resources
```

### 3. Secret Encryption

```aibasic
# Use encryption at rest for Secrets
# Enable encryption in etcd
```

### 4. Pod Security Standards

```aibasic
# Enforce Pod Security Standards
# Use Pod Security Admission
```

---

## Troubleshooting

### Common Issues

#### 1. "Unable to connect to cluster"

**Problem**: Kubeconfig not found or invalid context

**Solution**:
```aibasic
# Check kubeconfig path in configuration
# Verify context exists
10 (kubernetes) list all namespaces  # This will fail if config is wrong
```

#### 2. "Namespace not found"

**Problem**: Operating in non-existent namespace

**Solution**:
```aibasic
10 (kubernetes) create namespace "myapp"
20 # Then create resources in that namespace
```

#### 3. "Insufficient permissions"

**Problem**: Service account lacks RBAC permissions

**Solution**: Grant proper RBAC roles/bindings

---

## Module Integration Examples

### Kubernetes + Docker

```aibasic
# Build image with Docker, deploy with Kubernetes
10 (docker) build image from path "./app" with tag "myapp:v1.0"
20 (docker) push image "myapp:v1.0"
30 (kubernetes) create deployment named "myapp" from image "myapp:v1.0"
40 (kubernetes) with 3 replicas
```

### Kubernetes + PostgreSQL

```aibasic
# Deploy database with Kubernetes, connect from app
10 (kubernetes) create deployment named "postgres" from image "postgres:15"
20 (kubernetes) get service "postgres-service" details
30 set db_host to _result["spec"]["clusterIP"]
40 (postgres) connect to database at db_host
```

---

## Reference

### Task Type
- **Code**: `kubernetes`
- **Purpose**: Kubernetes cluster and resource management

### Dependencies
- `kubernetes>=28.0.0` (Official Kubernetes Python client)
- Kubernetes cluster access (kubeconfig or in-cluster config)

### Configuration File
- Section: `[kubernetes]`
- File: `aibasic.conf`

### Example File
- Location: `examples/example_kubernetes.aib`
- 20 complete examples

---

## Additional Resources

- **Kubernetes Documentation**: https://kubernetes.io/docs
- **Kubectl Cheat Sheet**: https://kubernetes.io/docs/reference/kubectl/cheatsheet/
- **Python Client**: https://github.com/kubernetes-client/python
- **Best Practices**: https://kubernetes.io/docs/concepts/configuration/overview/

---

**Module #24 | AIbasic v1.0 | Kubernetes Cluster Management Module**
