"""
Docker Module for AIBasic

This module provides comprehensive Docker container, image, volume, and network
management capabilities through the Docker Engine API.

Features:
- Container lifecycle management (create, start, stop, restart, remove)
- Image management (pull, build, push, tag, remove)
- Volume management (create, list, remove)
- Network management (create, connect, disconnect, remove)
- Docker Compose support
- Container logs and stats
- Image search and inspection
- Container execution (exec)
- Health checks and monitoring

Dependencies:
- docker>=7.0.0 (Docker SDK for Python)

Configuration (aibasic.conf):
[docker]
DOCKER_HOST = unix:///var/run/docker.sock  # or tcp://localhost:2375
TLS_VERIFY = false
TLS_CA_CERT = /path/to/ca.pem
TLS_CLIENT_CERT = /path/to/cert.pem
TLS_CLIENT_KEY = /path/to/key.pem
TIMEOUT = 60
DEFAULT_REGISTRY = docker.io
REGISTRY_USERNAME = your_username
REGISTRY_PASSWORD = your_password

Author: AIBasic Team
Version: 1.0
"""

import os
import threading
from typing import Optional, Dict, List, Any, Union
import configparser

try:
    import docker
    from docker.types import Mount, LogConfig, RestartPolicy
    from docker.errors import DockerException, ImageNotFound, ContainerError, APIError
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False


from .module_base import AIbasicModuleBase


class DockerModule(AIbasicModuleBase):
    """
    Docker module for container and image management.

    Implements singleton pattern for efficient resource usage.
    Provides comprehensive Docker operations through Docker SDK.
    """

    _instance = None
    _lock = threading.Lock()
    _initialized = False

    def __new__(cls):
        """Singleton pattern implementation."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(DockerModule, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize Docker module (only once due to singleton)."""
        if self._initialized:
            return

        if not DOCKER_AVAILABLE:
            raise ImportError(
                "Docker SDK not available. Install with: pip install docker>=7.0.0"
            )

        # Configuration
        self.docker_host = os.getenv('DOCKER_HOST', 'unix:///var/run/docker.sock')
        self.tls_verify = os.getenv('DOCKER_TLS_VERIFY', 'false').lower() == 'true'
        self.tls_ca_cert = os.getenv('DOCKER_TLS_CA_CERT')
        self.tls_client_cert = os.getenv('DOCKER_TLS_CLIENT_CERT')
        self.tls_client_key = os.getenv('DOCKER_TLS_CLIENT_KEY')
        self.timeout = int(os.getenv('DOCKER_TIMEOUT', '60'))
        self.default_registry = os.getenv('DOCKER_REGISTRY', 'docker.io')
        self.registry_username = os.getenv('DOCKER_REGISTRY_USERNAME')
        self.registry_password = os.getenv('DOCKER_REGISTRY_PASSWORD')

        # Docker client (lazy initialized)
        self._client = None

        self._initialized = True

    def load_config(self, config_path: str = 'aibasic.conf'):
        """Load configuration from aibasic.conf file."""
        if not os.path.exists(config_path):
            return

        config = configparser.ConfigParser()
        config.read(config_path)

        if 'docker' in config:
            docker_config = config['docker']
            self.docker_host = docker_config.get('DOCKER_HOST', self.docker_host)
            self.tls_verify = docker_config.get('TLS_VERIFY', str(self.tls_verify)).lower() == 'true'
            self.tls_ca_cert = docker_config.get('TLS_CA_CERT', self.tls_ca_cert)
            self.tls_client_cert = docker_config.get('TLS_CLIENT_CERT', self.tls_client_cert)
            self.tls_client_key = docker_config.get('TLS_CLIENT_KEY', self.tls_client_key)
            self.timeout = int(docker_config.get('TIMEOUT', self.timeout))
            self.default_registry = docker_config.get('DEFAULT_REGISTRY', self.default_registry)
            self.registry_username = docker_config.get('REGISTRY_USERNAME', self.registry_username)
            self.registry_password = docker_config.get('REGISTRY_PASSWORD', self.registry_password)

    @property
    def client(self):
        """Lazy-load Docker client."""
        if self._client is None:
            try:
                # Build TLS configuration if needed
                tls_config = None
                if self.tls_verify:
                    tls_config = docker.tls.TLSConfig(
                        ca_cert=self.tls_ca_cert,
                        client_cert=(self.tls_client_cert, self.tls_client_key),
                        verify=True
                    )

                # Create Docker client
                self._client = docker.DockerClient(
                    base_url=self.docker_host,
                    tls=tls_config,
                    timeout=self.timeout
                )

                # Test connection
                self._client.ping()

            except Exception as e:
                raise ConnectionError(f"Failed to connect to Docker daemon: {e}")

        return self._client

    # =============================================================================
    # Container Management
    # =============================================================================

    def container_run(self, image: str, name: Optional[str] = None,
                     command: Optional[Union[str, List[str]]] = None,
                     environment: Optional[Dict[str, str]] = None,
                     ports: Optional[Dict[str, int]] = None,
                     volumes: Optional[Dict[str, Dict[str, str]]] = None,
                     detach: bool = True, remove: bool = False,
                     network: Optional[str] = None, **kwargs) -> Any:
        """
        Run a container from an image.

        Args:
            image: Image name (e.g., 'nginx:latest')
            name: Container name
            command: Command to run
            environment: Environment variables dict
            ports: Port mappings {'80/tcp': 8080}
            volumes: Volume mappings {'/host/path': {'bind': '/container/path', 'mode': 'rw'}}
            detach: Run in background
            remove: Remove container when stopped
            network: Network to connect to
            **kwargs: Additional Docker run arguments

        Returns:
            Container object
        """
        try:
            container = self.client.containers.run(
                image=image,
                name=name,
                command=command,
                environment=environment,
                ports=ports,
                volumes=volumes,
                detach=detach,
                remove=remove,
                network=network,
                **kwargs
            )
            return container
        except Exception as e:
            raise RuntimeError(f"Failed to run container: {e}")

    def container_create(self, image: str, name: Optional[str] = None,
                        command: Optional[Union[str, List[str]]] = None,
                        **kwargs) -> Any:
        """Create a container without starting it."""
        try:
            container = self.client.containers.create(
                image=image,
                name=name,
                command=command,
                **kwargs
            )
            return container
        except Exception as e:
            raise RuntimeError(f"Failed to create container: {e}")

    def container_start(self, container_id: str) -> bool:
        """Start a container."""
        try:
            container = self.client.containers.get(container_id)
            container.start()
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to start container: {e}")

    def container_stop(self, container_id: str, timeout: int = 10) -> bool:
        """Stop a container."""
        try:
            container = self.client.containers.get(container_id)
            container.stop(timeout=timeout)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to stop container: {e}")

    def container_restart(self, container_id: str, timeout: int = 10) -> bool:
        """Restart a container."""
        try:
            container = self.client.containers.get(container_id)
            container.restart(timeout=timeout)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to restart container: {e}")

    def container_remove(self, container_id: str, force: bool = False,
                        volumes: bool = False) -> bool:
        """Remove a container."""
        try:
            container = self.client.containers.get(container_id)
            container.remove(force=force, v=volumes)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to remove container: {e}")

    def container_list(self, all: bool = False, filters: Optional[Dict] = None) -> List[Any]:
        """List containers."""
        try:
            return self.client.containers.list(all=all, filters=filters)
        except Exception as e:
            raise RuntimeError(f"Failed to list containers: {e}")

    def container_logs(self, container_id: str, tail: int = 100,
                      follow: bool = False, timestamps: bool = False) -> str:
        """Get container logs."""
        try:
            container = self.client.containers.get(container_id)
            logs = container.logs(
                tail=tail,
                follow=follow,
                timestamps=timestamps
            )
            return logs.decode('utf-8') if isinstance(logs, bytes) else logs
        except Exception as e:
            raise RuntimeError(f"Failed to get container logs: {e}")

    def container_stats(self, container_id: str, stream: bool = False) -> Dict:
        """Get container stats."""
        try:
            container = self.client.containers.get(container_id)
            stats = container.stats(stream=stream)
            if not stream:
                return stats
            return next(stats)  # Return first stats object
        except Exception as e:
            raise RuntimeError(f"Failed to get container stats: {e}")

    def container_exec(self, container_id: str, command: Union[str, List[str]],
                      detach: bool = False, tty: bool = False) -> Union[str, bool]:
        """Execute a command in a running container."""
        try:
            container = self.client.containers.get(container_id)
            result = container.exec_run(command, detach=detach, tty=tty)
            if detach:
                return True
            return result.output.decode('utf-8') if isinstance(result.output, bytes) else result.output
        except Exception as e:
            raise RuntimeError(f"Failed to execute command in container: {e}")

    def container_inspect(self, container_id: str) -> Dict:
        """Inspect a container."""
        try:
            container = self.client.containers.get(container_id)
            return container.attrs
        except Exception as e:
            raise RuntimeError(f"Failed to inspect container: {e}")

    def container_pause(self, container_id: str) -> bool:
        """Pause a container."""
        try:
            container = self.client.containers.get(container_id)
            container.pause()
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to pause container: {e}")

    def container_unpause(self, container_id: str) -> bool:
        """Unpause a container."""
        try:
            container = self.client.containers.get(container_id)
            container.unpause()
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to unpause container: {e}")

    def container_kill(self, container_id: str, signal: str = 'SIGKILL') -> bool:
        """Kill a container."""
        try:
            container = self.client.containers.get(container_id)
            container.kill(signal=signal)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to kill container: {e}")

    def container_rename(self, container_id: str, new_name: str) -> bool:
        """Rename a container."""
        try:
            container = self.client.containers.get(container_id)
            container.rename(new_name)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to rename container: {e}")

    # =============================================================================
    # Image Management
    # =============================================================================

    def image_pull(self, repository: str, tag: str = 'latest',
                   all_tags: bool = False) -> Any:
        """Pull an image from registry."""
        try:
            image = self.client.images.pull(
                repository=repository,
                tag=tag,
                all_tags=all_tags
            )
            return image
        except Exception as e:
            raise RuntimeError(f"Failed to pull image: {e}")

    def image_build(self, path: str, tag: Optional[str] = None,
                   dockerfile: str = 'Dockerfile',
                   buildargs: Optional[Dict[str, str]] = None,
                   nocache: bool = False, rm: bool = True) -> Any:
        """Build an image from a Dockerfile."""
        try:
            image, build_logs = self.client.images.build(
                path=path,
                tag=tag,
                dockerfile=dockerfile,
                buildargs=buildargs,
                nocache=nocache,
                rm=rm
            )
            return image
        except Exception as e:
            raise RuntimeError(f"Failed to build image: {e}")

    def image_push(self, repository: str, tag: str = 'latest',
                   auth_config: Optional[Dict] = None) -> bool:
        """Push an image to registry."""
        try:
            if auth_config is None and self.registry_username and self.registry_password:
                auth_config = {
                    'username': self.registry_username,
                    'password': self.registry_password
                }

            self.client.images.push(
                repository=repository,
                tag=tag,
                auth_config=auth_config
            )
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to push image: {e}")

    def image_tag(self, image: str, repository: str, tag: str = 'latest') -> bool:
        """Tag an image."""
        try:
            img = self.client.images.get(image)
            img.tag(repository=repository, tag=tag)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to tag image: {e}")

    def image_remove(self, image: str, force: bool = False,
                    noprune: bool = False) -> bool:
        """Remove an image."""
        try:
            self.client.images.remove(image=image, force=force, noprune=noprune)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to remove image: {e}")

    def image_list(self, all: bool = False, filters: Optional[Dict] = None) -> List[Any]:
        """List images."""
        try:
            return self.client.images.list(all=all, filters=filters)
        except Exception as e:
            raise RuntimeError(f"Failed to list images: {e}")

    def image_search(self, term: str, limit: int = 25) -> List[Dict]:
        """Search for images on Docker Hub."""
        try:
            return self.client.images.search(term=term, limit=limit)
        except Exception as e:
            raise RuntimeError(f"Failed to search images: {e}")

    def image_inspect(self, image: str) -> Dict:
        """Inspect an image."""
        try:
            img = self.client.images.get(image)
            return img.attrs
        except Exception as e:
            raise RuntimeError(f"Failed to inspect image: {e}")

    def image_history(self, image: str) -> List[Dict]:
        """Get image history."""
        try:
            img = self.client.images.get(image)
            return img.history()
        except Exception as e:
            raise RuntimeError(f"Failed to get image history: {e}")

    def image_prune(self, filters: Optional[Dict] = None) -> Dict:
        """Remove unused images."""
        try:
            return self.client.images.prune(filters=filters)
        except Exception as e:
            raise RuntimeError(f"Failed to prune images: {e}")

    # =============================================================================
    # Volume Management
    # =============================================================================

    def volume_create(self, name: Optional[str] = None,
                     driver: str = 'local',
                     driver_opts: Optional[Dict] = None,
                     labels: Optional[Dict] = None) -> Any:
        """Create a volume."""
        try:
            volume = self.client.volumes.create(
                name=name,
                driver=driver,
                driver_opts=driver_opts,
                labels=labels
            )
            return volume
        except Exception as e:
            raise RuntimeError(f"Failed to create volume: {e}")

    def volume_remove(self, name: str, force: bool = False) -> bool:
        """Remove a volume."""
        try:
            volume = self.client.volumes.get(name)
            volume.remove(force=force)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to remove volume: {e}")

    def volume_list(self, filters: Optional[Dict] = None) -> List[Any]:
        """List volumes."""
        try:
            return self.client.volumes.list(filters=filters)
        except Exception as e:
            raise RuntimeError(f"Failed to list volumes: {e}")

    def volume_inspect(self, name: str) -> Dict:
        """Inspect a volume."""
        try:
            volume = self.client.volumes.get(name)
            return volume.attrs
        except Exception as e:
            raise RuntimeError(f"Failed to inspect volume: {e}")

    def volume_prune(self, filters: Optional[Dict] = None) -> Dict:
        """Remove unused volumes."""
        try:
            return self.client.volumes.prune(filters=filters)
        except Exception as e:
            raise RuntimeError(f"Failed to prune volumes: {e}")

    # =============================================================================
    # Network Management
    # =============================================================================

    def network_create(self, name: str, driver: str = 'bridge',
                      options: Optional[Dict] = None,
                      ipam: Optional[Any] = None,
                      check_duplicate: bool = True,
                      internal: bool = False,
                      labels: Optional[Dict] = None,
                      enable_ipv6: bool = False) -> Any:
        """Create a network."""
        try:
            network = self.client.networks.create(
                name=name,
                driver=driver,
                options=options,
                ipam=ipam,
                check_duplicate=check_duplicate,
                internal=internal,
                labels=labels,
                enable_ipv6=enable_ipv6
            )
            return network
        except Exception as e:
            raise RuntimeError(f"Failed to create network: {e}")

    def network_remove(self, name: str) -> bool:
        """Remove a network."""
        try:
            network = self.client.networks.get(name)
            network.remove()
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to remove network: {e}")

    def network_list(self, names: Optional[List[str]] = None,
                    ids: Optional[List[str]] = None,
                    filters: Optional[Dict] = None) -> List[Any]:
        """List networks."""
        try:
            return self.client.networks.list(names=names, ids=ids, filters=filters)
        except Exception as e:
            raise RuntimeError(f"Failed to list networks: {e}")

    def network_inspect(self, name: str) -> Dict:
        """Inspect a network."""
        try:
            network = self.client.networks.get(name)
            return network.attrs
        except Exception as e:
            raise RuntimeError(f"Failed to inspect network: {e}")

    def network_connect(self, network_name: str, container_id: str,
                       aliases: Optional[List[str]] = None,
                       ipv4_address: Optional[str] = None,
                       ipv6_address: Optional[str] = None) -> bool:
        """Connect a container to a network."""
        try:
            network = self.client.networks.get(network_name)
            network.connect(
                container=container_id,
                aliases=aliases,
                ipv4_address=ipv4_address,
                ipv6_address=ipv6_address
            )
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to connect container to network: {e}")

    def network_disconnect(self, network_name: str, container_id: str,
                          force: bool = False) -> bool:
        """Disconnect a container from a network."""
        try:
            network = self.client.networks.get(network_name)
            network.disconnect(container=container_id, force=force)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to disconnect container from network: {e}")

    def network_prune(self, filters: Optional[Dict] = None) -> Dict:
        """Remove unused networks."""
        try:
            return self.client.networks.prune(filters=filters)
        except Exception as e:
            raise RuntimeError(f"Failed to prune networks: {e}")

    # =============================================================================
    # System and Info
    # =============================================================================

    def system_info(self) -> Dict:
        """Get Docker system information."""
        try:
            return self.client.info()
        except Exception as e:
            raise RuntimeError(f"Failed to get system info: {e}")

    def system_version(self) -> Dict:
        """Get Docker version."""
        try:
            return self.client.version()
        except Exception as e:
            raise RuntimeError(f"Failed to get version: {e}")

    def system_df(self) -> Dict:
        """Get Docker disk usage."""
        try:
            return self.client.df()
        except Exception as e:
            raise RuntimeError(f"Failed to get disk usage: {e}")

    def system_ping(self) -> bool:
        """Ping Docker daemon."""
        try:
            return self.client.ping()
        except Exception as e:
            raise RuntimeError(f"Failed to ping Docker daemon: {e}")

    def system_prune(self, all: bool = False, volumes: bool = False,
                    filters: Optional[Dict] = None) -> Dict:
        """Prune unused Docker objects."""
        try:
            # Prune containers
            container_prune = self.client.containers.prune(filters=filters)

            # Prune images
            image_filters = filters.copy() if filters else {}
            if all:
                image_filters['dangling'] = False
            image_prune = self.client.images.prune(filters=image_filters)

            # Prune networks
            network_prune = self.client.networks.prune(filters=filters)

            # Prune volumes
            volume_prune = {}
            if volumes:
                volume_prune = self.client.volumes.prune(filters=filters)

            return {
                'containers': container_prune,
                'images': image_prune,
                'networks': network_prune,
                'volumes': volume_prune
            }
        except Exception as e:
            raise RuntimeError(f"Failed to prune system: {e}")

    # =============================================================================
    # Utility Methods
    # =============================================================================

    def close(self):
        """Close Docker client connection."""
        if self._client:
            self._client.close()
            self._client = None

    # =============================================================================
    # Metadata Methods for AIbasic Compiler
    # =============================================================================

    @classmethod
    def get_metadata(cls):
        """Get module metadata."""
        from aibasic.modules.module_base import ModuleMetadata
        return ModuleMetadata(
            name="Docker",
            task_type="docker",
            description="Docker container, image, volume, and network management through Docker Engine API",
            version="1.0.0",
            keywords=["docker", "container", "image", "volume", "network", "containerization", "dockerfile", "registry"],
            dependencies=["docker>=7.0.0"]
        )

    @classmethod
    def get_usage_notes(cls):
        """Get detailed usage notes."""
        return [
            "Module uses singleton pattern - one instance per application",
            "Requires Docker daemon running (Docker Desktop on Windows/Mac, Docker Engine on Linux)",
            "Docker client connects via unix socket (Linux/Mac) or named pipe (Windows)",
            "TCP connection supported for remote Docker hosts with optional TLS",
            "Container operations: run, start, stop, restart, remove, exec, logs, stats",
            "Image operations: pull, build, push, tag, remove, search, inspect",
            "Volume operations: create, remove, list, inspect for persistent data",
            "Network operations: create, connect, disconnect for container networking",
            "All operations use Docker SDK for Python (official Docker library)",
            "Detach mode runs containers in background (detach=True)",
            "Port mappings format: {'80/tcp': 8080} maps container port 80 to host port 8080",
            "Volume mounts format: {'/host/path': {'bind': '/container/path', 'mode': 'rw'}}",
            "Environment variables passed as dict: {'VAR': 'value'}",
            "Container logs support tail, follow, and timestamp options",
            "System prune removes unused containers, images, networks, and volumes",
            "Key methods: container_run, container_list, image_pull, image_build, volume_create, network_create",
        ]

    @classmethod
    def get_methods_info(cls):
        """Get information about module methods."""
        from aibasic.modules.module_base import MethodInfo
        return [
            MethodInfo(
                name="container_run",
                description="Run a container from an image with full configuration options",
                parameters={
                    "image": "Image name and tag (e.g., 'nginx:latest', 'ubuntu:22.04')",
                    "name": "Container name (optional, Docker generates if omitted)",
                    "command": "Command to run (string or list, optional, uses image default)",
                    "environment": "Environment variables dict (optional, e.g., {'DB_HOST': 'localhost'})",
                    "ports": "Port mappings dict (optional, e.g., {'80/tcp': 8080})",
                    "volumes": "Volume mounts dict (optional, e.g., {'/host': {'bind': '/container', 'mode': 'rw'}})",
                    "detach": "Run in background (default: True)",
                    "remove": "Auto-remove container when stopped (default: False)",
                    "network": "Network to connect to (optional, e.g., 'bridge', 'host')"
                },
                returns="Container object if detach=True, otherwise container output",
                examples=[
                    '(docker) run container "nginx:latest" with name "web-server" ports {"80/tcp": 8080} detach True',
                    '(docker) run container "ubuntu:22.04" command "echo Hello" detach False',
                    '(docker) run container "postgres:15" environment {"POSTGRES_PASSWORD": "secret"} volumes {"/data": {"bind": "/var/lib/postgresql/data"}}',
                ]
            ),
            MethodInfo(
                name="container_start",
                description="Start a stopped container",
                parameters={
                    "container_id": "Container ID or name (string)"
                },
                returns="Boolean True on success, raises RuntimeError on failure",
                examples=[
                    '(docker) start container "web-server"',
                    '(docker) start container by id "a1b2c3d4"',
                ]
            ),
            MethodInfo(
                name="container_stop",
                description="Stop a running container gracefully with timeout",
                parameters={
                    "container_id": "Container ID or name (string)",
                    "timeout": "Seconds to wait before force kill (default: 10)"
                },
                returns="Boolean True on success",
                examples=[
                    '(docker) stop container "web-server"',
                    '(docker) stop container "app" timeout 30',
                ]
            ),
            MethodInfo(
                name="container_restart",
                description="Restart a container (stop then start)",
                parameters={
                    "container_id": "Container ID or name (string)",
                    "timeout": "Seconds to wait before force kill (default: 10)"
                },
                returns="Boolean True on success",
                examples=[
                    '(docker) restart container "web-server"',
                    '(docker) restart container "api-server" timeout 15',
                ]
            ),
            MethodInfo(
                name="container_remove",
                description="Remove a container (must be stopped unless force=True)",
                parameters={
                    "container_id": "Container ID or name (string)",
                    "force": "Force remove running container (default: False)",
                    "volumes": "Remove associated anonymous volumes (default: False)"
                },
                returns="Boolean True on success",
                examples=[
                    '(docker) remove container "old-server"',
                    '(docker) remove container "temp" force True volumes True',
                ]
            ),
            MethodInfo(
                name="container_list",
                description="List containers (running by default, all with all=True)",
                parameters={
                    "all": "Include stopped containers (default: False)",
                    "filters": "Filter dict (optional, e.g., {'status': 'running', 'name': 'web'})"
                },
                returns="List of Container objects with attributes: id, name, status, image",
                examples=[
                    '(docker) list containers',
                    '(docker) list all containers',
                    '(docker) list containers with filters {"status": "exited"}',
                ]
            ),
            MethodInfo(
                name="container_logs",
                description="Get container logs with optional tail, follow, and timestamps",
                parameters={
                    "container_id": "Container ID or name (string)",
                    "tail": "Number of lines from end (default: 100, 'all' for everything)",
                    "follow": "Stream logs in real-time (default: False)",
                    "timestamps": "Include timestamps (default: False)"
                },
                returns="String with container logs",
                examples=[
                    '(docker) get logs from container "web-server" tail 50',
                    '(docker) get logs from container "app" timestamps True',
                ]
            ),
            MethodInfo(
                name="container_exec",
                description="Execute a command inside a running container",
                parameters={
                    "container_id": "Container ID or name (string)",
                    "command": "Command to execute (string or list, e.g., 'ls -la' or ['ls', '-la'])",
                    "detach": "Run in background (default: False)",
                    "tty": "Allocate pseudo-TTY (default: False)"
                },
                returns="Command output as string if detach=False, otherwise True",
                examples=[
                    '(docker) exec in container "web-server" command "cat /etc/nginx/nginx.conf"',
                    '(docker) exec in container "db" command ["mysqldump", "-u", "root", "mydb"]',
                ]
            ),
            MethodInfo(
                name="image_pull",
                description="Pull an image from Docker registry (Docker Hub by default)",
                parameters={
                    "repository": "Repository name (e.g., 'nginx', 'ubuntu', 'myuser/myimage')",
                    "tag": "Image tag (default: 'latest')",
                    "all_tags": "Pull all tags (default: False)"
                },
                returns="Image object",
                examples=[
                    '(docker) pull image "nginx" tag "latest"',
                    '(docker) pull image "postgres" tag "15-alpine"',
                    '(docker) pull image "python" tag "3.11-slim"',
                ]
            ),
            MethodInfo(
                name="image_build",
                description="Build an image from a Dockerfile",
                parameters={
                    "path": "Build context path (directory containing Dockerfile)",
                    "tag": "Tag for the image (optional, e.g., 'myapp:v1.0')",
                    "dockerfile": "Dockerfile name (default: 'Dockerfile')",
                    "buildargs": "Build arguments dict (optional, e.g., {'VERSION': '1.0'})",
                    "nocache": "Don't use cache (default: False)",
                    "rm": "Remove intermediate containers (default: True)"
                },
                returns="Image object",
                examples=[
                    '(docker) build image from "." tag "myapp:v1.0"',
                    '(docker) build image from "/app" dockerfile "Dockerfile.prod" nocache True',
                    '(docker) build image from "." tag "app:latest" buildargs {"NODE_ENV": "production"}',
                ]
            ),
            MethodInfo(
                name="image_push",
                description="Push an image to Docker registry",
                parameters={
                    "repository": "Repository name (e.g., 'myuser/myimage')",
                    "tag": "Image tag (default: 'latest')",
                    "auth_config": "Auth dict with username/password (optional, uses config if omitted)"
                },
                returns="Boolean True on success",
                examples=[
                    '(docker) push image "myuser/myapp" tag "v1.0"',
                    '(docker) push image "registry.example.com/app" tag "latest"',
                ]
            ),
            MethodInfo(
                name="image_list",
                description="List Docker images on the system",
                parameters={
                    "all": "Include intermediate images (default: False)",
                    "filters": "Filter dict (optional, e.g., {'dangling': True})"
                },
                returns="List of Image objects with attributes: id, tags, size",
                examples=[
                    '(docker) list images',
                    '(docker) list all images',
                ]
            ),
            MethodInfo(
                name="volume_create",
                description="Create a Docker volume for persistent data storage",
                parameters={
                    "name": "Volume name (optional, Docker generates if omitted)",
                    "driver": "Volume driver (default: 'local')",
                    "driver_opts": "Driver options dict (optional)",
                    "labels": "Labels dict (optional)"
                },
                returns="Volume object",
                examples=[
                    '(docker) create volume "db-data"',
                    '(docker) create volume "app-config" labels {"env": "prod"}',
                ]
            ),
            MethodInfo(
                name="volume_list",
                description="List Docker volumes",
                parameters={
                    "filters": "Filter dict (optional)"
                },
                returns="List of Volume objects with attributes: name, driver, mountpoint",
                examples=[
                    '(docker) list volumes',
                ]
            ),
            MethodInfo(
                name="network_create",
                description="Create a Docker network for container communication",
                parameters={
                    "name": "Network name (string)",
                    "driver": "Network driver (default: 'bridge', options: 'host', 'overlay', 'macvlan')",
                    "internal": "Internal network, no external access (default: False)",
                    "enable_ipv6": "Enable IPv6 (default: False)"
                },
                returns="Network object",
                examples=[
                    '(docker) create network "app-network"',
                    '(docker) create network "backend" driver "bridge" internal True',
                ]
            ),
            MethodInfo(
                name="network_connect",
                description="Connect a container to a network",
                parameters={
                    "network_name": "Network name (string)",
                    "container_id": "Container ID or name (string)",
                    "aliases": "Network aliases list (optional)",
                    "ipv4_address": "Static IPv4 address (optional)",
                    "ipv6_address": "Static IPv6 address (optional)"
                },
                returns="Boolean True on success",
                examples=[
                    '(docker) connect container "web-server" to network "app-network"',
                    '(docker) connect container "api" to network "backend" aliases ["api-service"]',
                ]
            ),
        ]

    @classmethod
    def get_examples(cls):
        """Get AIbasic usage examples."""
        return [
            # Container lifecycle
            '10 (docker) pull image "nginx" tag "latest"',
            '20 (docker) run container "nginx:latest" name "web" ports {"80/tcp": 8080} detach True',
            '30 (docker) list containers',
            '40 (docker) get logs from container "web" tail 100',
            '50 (docker) stop container "web"',
            '60 (docker) start container "web"',
            '70 (docker) restart container "web"',
            '80 (docker) remove container "web" force True',

            # Image management
            '90 (docker) pull image "postgres" tag "15-alpine"',
            '100 (docker) build image from "." tag "myapp:v1.0"',
            '110 (docker) list images',
            '120 (docker) push image "myuser/myapp" tag "v1.0"',
            '130 (docker) remove image "old-image:v0.1"',

            # Container with environment and volumes
            '140 (docker) run container "postgres:15" name "db" environment {"POSTGRES_PASSWORD": "secret", "POSTGRES_DB": "mydb"} volumes {"/var/lib/postgres": {"bind": "/var/lib/postgresql/data"}} ports {"5432/tcp": 5432}',

            # Execute commands
            '150 (docker) exec in container "web" command "nginx -s reload"',
            '160 (docker) exec in container "db" command "pg_dump -U postgres mydb"',

            # Volume management
            '170 (docker) create volume "db-data"',
            '180 (docker) list volumes',
            '190 (docker) run container "mysql:8" volumes {"db-data": {"bind": "/var/lib/mysql"}}',

            # Network management
            '200 (docker) create network "app-network"',
            '210 (docker) run container "nginx" network "app-network"',
            '220 (docker) connect container "api-server" to network "app-network"',
            '230 (docker) list networks',

            # System operations
            '240 (docker) system info',
            '250 (docker) system version',
        ]


# Global instance
_docker_module = None


def get_docker_module(config_path: str = 'aibasic.conf') -> DockerModule:
    """
    Get or create Docker module instance.

    Args:
        config_path: Path to aibasic.conf configuration file

    Returns:
        DockerModule instance
    """
    global _docker_module
    if _docker_module is None:
        _docker_module = DockerModule()
        _docker_module.load_config(config_path)
    return _docker_module
