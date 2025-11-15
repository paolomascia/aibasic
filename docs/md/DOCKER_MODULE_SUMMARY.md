# Docker Module - Complete Reference

**Module #23 | Task Type: `docker` | Version: 1.0**

## Overview

The **Docker module** provides comprehensive container, image, volume, and network management through the Docker Engine API, enabling you to manage Docker resources using natural language instructions.

### Key Capabilities

- **Container Lifecycle**: Run, start, stop, restart, pause, remove containers
- **Image Management**: Pull, build, push, tag, search, and remove images
- **Volume Operations**: Create, list, inspect, and remove persistent volumes
- **Network Management**: Create networks, connect/disconnect containers
- **Monitoring**: Container logs, stats, and health checks
- **System Operations**: System info, cleanup, and resource pruning

---

## Configuration

### Basic Configuration (`aibasic.conf`)

```ini
[docker]
# Docker Host (socket or TCP)
DOCKER_HOST = unix:///var/run/docker.sock  # Linux/macOS
# DOCKER_HOST = tcp://localhost:2375  # Windows or remote
# DOCKER_HOST = npipe:////./pipe/docker_engine  # Windows named pipe

# TLS/SSL Settings (for remote Docker daemon)
TLS_VERIFY = false  # Enable TLS verification
TLS_CA_CERT = /path/to/ca.pem
TLS_CLIENT_CERT = /path/to/cert.pem
TLS_CLIENT_KEY = /path/to/key.pem

# Connection Settings
TIMEOUT = 60  # API timeout in seconds

# Registry Settings (for push/pull operations)
DEFAULT_REGISTRY = docker.io
REGISTRY_USERNAME = your_dockerhub_username
REGISTRY_PASSWORD = your_dockerhub_password_or_token
```

---

## Container Operations

### Run Container

```aibasic
# Simple run
10 (docker) run container from image "nginx:latest" named "web-server" in detached mode
20 print "Container started:" and _result

# With port mapping
30 set ports to dict with "80/tcp" as 8080
40 (docker) run container from image "nginx:latest" named "nginx-web"
50 (docker) with ports ports in detached mode

# With environment variables
60 set env to dict with "POSTGRES_PASSWORD" as "secret123"
70 set env["POSTGRES_DB"] to "mydb"
80 (docker) run container from image "postgres:15" named "db"
90 (docker) with environment env in detached mode

# With volumes
100 set vols to dict with "data-volume" as dict with "bind" as "/data" and "mode" as "rw"
110 (docker) run container from image "alpine:latest" named "data-container"
120 (docker) with volumes vols in detached mode
```

### Container Lifecycle

```aibasic
# List containers
10 (docker) list all running containers
20 print "Running:" and _result

30 (docker) list all containers including stopped
40 print "All containers:" and _result

# Start/Stop
50 (docker) start container "web-server"
60 (docker) stop container "web-server"
70 (docker) restart container "web-server"

# Pause/Unpause
80 (docker) pause container "web-server"
90 (docker) unpause container "web-server"

# Remove
100 (docker) remove container "web-server"
110 (docker) remove container "web-server" force
```

### Execute Commands

```aibasic
# Execute command
10 (docker) exec command "whoami" in container "web-server"
20 print "User:" and _result

30 (docker) exec command "ls -la /" in container "web-server"
40 print "Files:" and _result

# Interactive execution
50 (docker) exec command "/bin/bash" in container "web-server" with tty
```

### Container Logs and Stats

```aibasic
# Get logs
10 (docker) get logs from container "web-server" tail 50 lines
20 print "Logs:" and _result

30 (docker) get logs from container "web-server" with timestamps
40 print "Timestamped logs:" and _result

# Get stats
50 (docker) get stats from container "web-server"
60 print "Stats:" and _result

# Inspect
70 (docker) inspect container "web-server"
80 print "Details:" and _result
```

---

## Image Management

### Pull and List Images

```aibasic
# Pull image
10 (docker) pull image "alpine" with tag "3.18"
20 print "Image pulled:" and _result

30 (docker) pull image "nginx" with tag "latest"

# Pull all tags
40 (docker) pull image "redis" all tags

# List images
50 (docker) list all images
60 print "Images:" and _result

# Search Docker Hub
70 (docker) search for images with term "redis" limit 10
80 print "Search results:" and _result
```

### Tag and Push Images

```aibasic
# Tag image
10 (docker) tag image "alpine:3.18" as "myrepo/alpine:custom"
20 print "Image tagged"

# Push image (requires authentication)
30 (docker) push image "myrepo/alpine:custom" to registry
40 print "Image pushed"

# Inspect image
50 (docker) inspect image "alpine:3.18"
60 print "Image details:" and _result

# Get image history
70 (docker) get history of image "alpine:3.18"
80 print "History:" and _result
```

### Build Images

```aibasic
# Build from Dockerfile
10 (docker) build image from path "./my-app" with tag "my-app:1.0"
20 print "Image built:" and _result

# Build with build args
30 set buildargs to dict with "VERSION" as "1.0" and "ENV" as "production"
40 (docker) build image from path "./my-app" with tag "my-app:prod"
50 (docker) with buildargs buildargs and dockerfile "Dockerfile.prod"
60 print "Production image built"

# Build with no cache
70 (docker) build image from path "./my-app" with tag "my-app:latest" no cache
```

### Remove Images

```aibasic
# Remove single image
10 (docker) remove image "my-app:old"

# Force remove
20 (docker) remove image "my-app:old" force

# Prune unused images
30 (docker) prune unused images
40 print "Pruned:" and _result
```

---

## Volume Management

### Create and List Volumes

```aibasic
# Create volume
10 (docker) create volume "data-volume"
20 print "Volume created"

# Create with driver options
30 set driver_opts to dict with "type" as "nfs" and "device" as ":/mnt/data"
40 (docker) create volume "nfs-volume" with driver "local" and driver options driver_opts

# List volumes
50 (docker) list all volumes
60 print "Volumes:" and _result

# Inspect volume
70 (docker) inspect volume "data-volume"
80 print "Volume details:" and _result
```

### Use Volumes

```aibasic
# Use volume in container
10 set vols to dict with "data-volume" as dict with "bind" as "/app/data" and "mode" as "rw"
20 (docker) run container from image "alpine:latest" named "app"
30 (docker) with volumes vols and command "sh -c 'echo test > /app/data/file.txt'"
40 print "Data written to volume"

# Read-only volume
50 set ro_vols to dict with "data-volume" as dict with "bind" as "/data" and "mode" as "ro"
60 (docker) run container from image "alpine:latest" with volumes ro_vols
```

### Remove Volumes

```aibasic
# Remove volume
10 (docker) remove volume "data-volume"

# Force remove
20 (docker) remove volume "data-volume" force

# Prune unused volumes
30 (docker) prune unused volumes
40 print "Volumes pruned:" and _result
```

---

## Network Management

### Create and List Networks

```aibasic
# Create network
10 (docker) create network "app-network" with driver "bridge"
20 print "Network created"

# Create with subnet
30 (docker) create network "custom-net" with driver "bridge"
40 (docker) subnet "172.28.0.0/16" gateway "172.28.0.1"

# List networks
50 (docker) list all networks
60 print "Networks:" and _result

# Inspect network
70 (docker) inspect network "app-network"
80 print "Network details:" and _result
```

### Connect Containers

```aibasic
# Connect container to network
10 (docker) connect container "web-server" to network "app-network"
20 print "Container connected"

# Connect with static IP
30 (docker) connect container "app" to network "custom-net" with ip "172.28.0.10"

# Disconnect
40 (docker) disconnect container "web-server" from network "app-network"
50 print "Container disconnected"
```

### Remove Networks

```aibasic
# Remove network
10 (docker) remove network "app-network"

# Prune unused networks
20 (docker) prune unused networks
30 print "Networks pruned:" and _result
```

---

## System Operations

### System Information

```aibasic
# Get Docker info
10 (docker) get system info
20 print "Docker info:" and _result

# Get Docker version
30 (docker) get docker version
40 print "Version:" and _result

# Get disk usage
50 (docker) get disk usage
60 print "Disk usage:" and _result

# Ping daemon
70 (docker) ping docker daemon
80 print "Daemon is running:" and _result
```

### System Cleanup

```aibasic
# Prune containers
10 (docker) prune unused containers
20 print "Containers pruned:" and _result

# Prune images
30 (docker) prune unused images
40 print "Images pruned:" and _result

# Prune volumes
50 (docker) prune unused volumes
60 print "Volumes pruned:" and _result

# Prune networks
70 (docker) prune unused networks
80 print "Networks pruned:" and _result

# Prune everything
90 (docker) prune all system resources including volumes
100 print "System cleaned:" and _result
```

---

## Complete Examples

### Example 1: Multi-Container Application

```aibasic
10 print "=== Deploying Multi-Container App ==="
20
30 # Create network
40 (docker) create network "webapp-network"
50 print "Network created"
60
70 # Start database
80 set db_env to dict with "POSTGRES_PASSWORD" as "dbpass"
90 set db_env["POSTGRES_DB"] to "appdb"
100 (docker) run container from image "postgres:15" named "app-db"
110 (docker) with environment db_env in network "webapp-network" in detached mode
120 print "Database started"
130
140 # Start web app
150 set web_ports to dict with "80/tcp" as 8080
160 (docker) run container from image "nginx:latest" named "app-web"
170 (docker) with ports web_ports in network "webapp-network" in detached mode
180 print "Web app started on http://localhost:8080"
190
200 # Monitor
210 (docker) list all running containers
220 print "Running containers:" and _result
```

### Example 2: Development Environment

```aibasic
10 print "=== Setting Up Development Environment ==="
20 on error goto 900
30
40 # Pull required images
50 (docker) pull image "node" with tag "18-alpine"
60 (docker) pull image "redis" with tag "latest"
70 (docker) pull image "postgres" with tag "15"
80 print "Images pulled"
90
100 # Create network and volumes
110 (docker) create network "dev-network"
120 (docker) create volume "dev-data"
130 (docker) create volume "dev-cache"
140
150 # Start services
160 (docker) run container from image "redis:latest" named "dev-redis"
170 (docker) in network "dev-network" in detached mode
180
190 set db_env to dict with "POSTGRES_PASSWORD" as "devpass"
200 set db_vols to dict with "dev-data" as dict with "bind" as "/var/lib/postgresql/data" and "mode" as "rw"
210 (docker) run container from image "postgres:15" named "dev-db"
220 (docker) with environment db_env and volumes db_vols
230 (docker) in network "dev-network" in detached mode
240
250 print "Development environment ready!"
260 goto 999
900 print "ERROR:" and _last_error
910 print "Cleanup and retry"
999 print "Setup complete"
```

### Example 3: CI/CD Pipeline

```aibasic
10 print "=== CI/CD Pipeline: Build and Test ==="
20 on error goto 900
30
40 # Build application image
50 print "Step 1: Building image..."
60 (docker) build image from path "./app" with tag "my-app:test"
70 print "✓ Image built"
80
90 # Run tests
100 print "Step 2: Running tests..."
110 (docker) run container from image "my-app:test" named "test-runner"
120 (docker) with command "npm test" and remove after exit
130 print "✓ Tests passed"
140
150 # Tag for production
160 print "Step 3: Tagging for production..."
170 (docker) tag image "my-app:test" as "my-app:latest"
180 (docker) tag image "my-app:test" as "myrepo/my-app:1.0.0"
190 print "✓ Images tagged"
200
210 # Push to registry (optional)
220 # (docker) push image "myrepo/my-app:1.0.0"
230
240 print "Pipeline succeeded!"
250 goto 999
900 print "❌ Pipeline failed:" and _last_error
910 print "Rolling back..."
920 (docker) remove image "my-app:test" force
999 print "Pipeline complete"
```

---

## Best Practices

### 1. Always Use Detached Mode for Services

```aibasic
10 (docker) run container from image "nginx:latest" named "web" in detached mode
```

### 2. Name Your Containers

```aibasic
10 (docker) run container from image "redis:latest" named "app-cache" in detached mode
```

### 3. Use Environment Variables for Configuration

```aibasic
10 set env to dict with "DATABASE_URL" as "postgres://..."
20 set env["API_KEY"] to "secret-key"
30 (docker) run container with environment env
```

### 4. Implement Health Checks

```aibasic
10 (docker) run container from image "nginx:latest" named "web"
20 (docker) with healthcheck "curl -f http://localhost/ || exit 1"
30 (docker) interval 30s timeout 3s retries 3
```

### 5. Set Resource Limits

```aibasic
10 (docker) run container from image "app:latest" named "app"
20 (docker) with memory limit "512m" and cpu shares 512
```

### 6. Use Volumes for Persistent Data

```aibasic
10 (docker) create volume "app-data"
20 set vols to dict with "app-data" as dict with "bind" as "/data" and "mode" as "rw"
30 (docker) run container with volumes vols
```

### 7. Regular Cleanup

```aibasic
10 (docker) prune unused containers
20 (docker) prune unused images
30 (docker) prune unused volumes
40 (docker) prune unused networks
```

### 8. Use Restart Policies

```aibasic
10 (docker) run container from image "app:latest" named "app"
20 (docker) with restart policy "always" in detached mode
```

---

## Security Considerations

### 1. Never Run as Root

```aibasic
# Use user parameter when running containers
10 (docker) run container from image "app:latest" with user "1000:1000"
```

### 2. Limit Container Capabilities

```aibasic
# Drop unnecessary capabilities
10 (docker) run container with cap drop "ALL" and cap add "NET_BIND_SERVICE"
```

### 3. Use Read-Only Filesystems

```aibasic
10 set vols to dict with "data" as dict with "bind" as "/data" and "mode" as "ro"
20 (docker) run container with volumes vols and read only filesystem
```

### 4. Secure Registry Communication

```ini
[docker]
TLS_VERIFY = true
TLS_CA_CERT = /path/to/ca.pem
TLS_CLIENT_CERT = /path/to/cert.pem
TLS_CLIENT_KEY = /path/to/key.pem
```

---

## Troubleshooting

### Common Issues

#### 1. "Cannot connect to Docker daemon"

**Problem**: Docker daemon not running or socket not accessible

**Solution**:
```aibasic
# Check Docker daemon
10 (docker) ping docker daemon
20 if _result is false print "Docker daemon not running"
```

#### 2. "Port already in use"

**Problem**: Port mapping conflicts

**Solution**: Change port mapping or stop conflicting container

#### 3. "No space left on device"

**Problem**: Disk full

**Solution**:
```aibasic
10 (docker) prune all system resources including volumes
```

#### 4. "Image not found"

**Problem**: Image doesn't exist locally

**Solution**:
```aibasic
10 (docker) pull image "nginx" with tag "latest"
```

---

## Module Integration Examples

### Docker + PostgreSQL

```aibasic
# Deploy database with Docker, then connect with PostgreSQL module
10 (docker) run container from image "postgres:15" named "db"
20 (docker) with ports {"5432/tcp": 5433} in detached mode
30 (postgres) connect to database at "localhost:5433"
40 (postgres) execute query "CREATE TABLE users (id SERIAL, name VARCHAR(100))"
```

### Docker + Terraform

```aibasic
# Deploy infrastructure with Terraform, run app in Docker
10 (terraform) apply terraform configuration
20 (terraform) get terraform output "app_image"
30 set app_image to _result
40 (docker) run container from image app_image in detached mode
```

---

## Reference

### Task Type
- **Code**: `docker`
- **Purpose**: Container and image management

### Dependencies
- `docker>=7.0.0` (Docker SDK for Python)
- Docker Engine installed and running

### Configuration File
- Section: `[docker]`
- File: `aibasic.conf`

### Example File
- Location: `examples/example_docker.aib`
- 22 complete examples

---

**Module #23 | AIbasic v1.0 | Docker Container Management Module**
