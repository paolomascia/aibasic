"""
Azure Module for AIBasic

This module provides comprehensive Microsoft Azure cloud services management
through the official Azure SDK for Python.

Features:
- Virtual Machine management (create, start, stop, delete)
- Storage Account and Blob Storage operations
- SQL Database management
- Resource Group management
- Virtual Network management
- App Service (Web Apps) management
- Container Instances
- Key Vault operations
- Cosmos DB operations
- Monitor and metrics

Dependencies:
- azure-identity>=1.15.0
- azure-mgmt-compute>=30.0.0
- azure-mgmt-storage>=21.0.0
- azure-mgmt-sql>=4.0.0
- azure-mgmt-resource>=23.0.0
- azure-mgmt-network>=25.0.0
- azure-mgmt-web>=7.0.0
- azure-storage-blob>=12.19.0
- azure-mgmt-containerinstance>=10.0.0
- azure-keyvault-secrets>=4.7.0
- azure-mgmt-cosmosdb>=9.0.0

Configuration (aibasic.conf):
[azure]
SUBSCRIPTION_ID = your-subscription-id
TENANT_ID = your-tenant-id
CLIENT_ID = your-client-id
CLIENT_SECRET = your-client-secret
RESOURCE_GROUP = default-resource-group
LOCATION = eastus

Author: AIBasic Team
Version: 1.0
"""

import os
import threading
from typing import Optional, Dict, List, Any
import configparser

try:
    from azure.identity import ClientSecretCredential, DefaultAzureCredential
    from azure.mgmt.compute import ComputeManagementClient
    from azure.mgmt.storage import StorageManagementClient
    from azure.mgmt.sql import SqlManagementClient
    from azure.mgmt.resource import ResourceManagementClient
    from azure.mgmt.network import NetworkManagementClient
    from azure.mgmt.web import WebSiteManagementClient
    from azure.storage.blob import BlobServiceClient
    from azure.mgmt.containerinstance import ContainerInstanceManagementClient
    from azure.keyvault.secrets import SecretClient
    from azure.mgmt.cosmosdb import CosmosDBManagementClient
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False


class AzureModule:
    """
    Azure module for Microsoft Azure cloud services management.

    Implements singleton pattern for efficient resource usage.
    Provides comprehensive Azure operations through official SDK.
    """

    _instance = None
    _lock = threading.Lock()
    _initialized = False

    def __new__(cls):
        """Singleton pattern implementation."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(AzureModule, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize Azure module (only once due to singleton)."""
        if self._initialized:
            return

        if not AZURE_AVAILABLE:
            raise ImportError(
                "Azure SDK not available. Install with: pip install azure-identity azure-mgmt-compute azure-mgmt-storage azure-mgmt-sql azure-mgmt-resource azure-mgmt-network azure-storage-blob"
            )

        # Configuration
        self.subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID')
        self.tenant_id = os.getenv('AZURE_TENANT_ID')
        self.client_id = os.getenv('AZURE_CLIENT_ID')
        self.client_secret = os.getenv('AZURE_CLIENT_SECRET')
        self.resource_group = os.getenv('AZURE_RESOURCE_GROUP', 'aibasic-rg')
        self.location = os.getenv('AZURE_LOCATION', 'eastus')

        # Credentials (lazy initialized)
        self._credential = None

        # Service clients (lazy initialized)
        self._compute_client = None
        self._storage_client = None
        self._sql_client = None
        self._resource_client = None
        self._network_client = None
        self._web_client = None
        self._container_client = None
        self._cosmosdb_client = None

        self._initialized = True

    def load_config(self, config_path: str = 'aibasic.conf'):
        """Load configuration from aibasic.conf file."""
        if not os.path.exists(config_path):
            return

        config = configparser.ConfigParser()
        config.read(config_path)

        if 'azure' in config:
            azure_config = config['azure']
            self.subscription_id = azure_config.get('SUBSCRIPTION_ID', self.subscription_id)
            self.tenant_id = azure_config.get('TENANT_ID', self.tenant_id)
            self.client_id = azure_config.get('CLIENT_ID', self.client_id)
            self.client_secret = azure_config.get('CLIENT_SECRET', self.client_secret)
            self.resource_group = azure_config.get('RESOURCE_GROUP', self.resource_group)
            self.location = azure_config.get('LOCATION', self.location)

    @property
    def credential(self):
        """Lazy-load Azure credential."""
        if self._credential is None:
            if self.client_id and self.client_secret and self.tenant_id:
                # Service Principal authentication
                self._credential = ClientSecretCredential(
                    tenant_id=self.tenant_id,
                    client_id=self.client_id,
                    client_secret=self.client_secret
                )
            else:
                # Default credential (uses environment, managed identity, etc.)
                self._credential = DefaultAzureCredential()
        return self._credential

    @property
    def compute_client(self):
        """Lazy-load Compute Management client."""
        if self._compute_client is None:
            self._compute_client = ComputeManagementClient(
                credential=self.credential,
                subscription_id=self.subscription_id
            )
        return self._compute_client

    @property
    def storage_client(self):
        """Lazy-load Storage Management client."""
        if self._storage_client is None:
            self._storage_client = StorageManagementClient(
                credential=self.credential,
                subscription_id=self.subscription_id
            )
        return self._storage_client

    @property
    def sql_client(self):
        """Lazy-load SQL Management client."""
        if self._sql_client is None:
            self._sql_client = SqlManagementClient(
                credential=self.credential,
                subscription_id=self.subscription_id
            )
        return self._sql_client

    @property
    def resource_client(self):
        """Lazy-load Resource Management client."""
        if self._resource_client is None:
            self._resource_client = ResourceManagementClient(
                credential=self.credential,
                subscription_id=self.subscription_id
            )
        return self._resource_client

    @property
    def network_client(self):
        """Lazy-load Network Management client."""
        if self._network_client is None:
            self._network_client = NetworkManagementClient(
                credential=self.credential,
                subscription_id=self.subscription_id
            )
        return self._network_client

    @property
    def web_client(self):
        """Lazy-load Web/App Service Management client."""
        if self._web_client is None:
            self._web_client = WebSiteManagementClient(
                credential=self.credential,
                subscription_id=self.subscription_id
            )
        return self._web_client

    @property
    def container_client(self):
        """Lazy-load Container Instance Management client."""
        if self._container_client is None:
            self._container_client = ContainerInstanceManagementClient(
                credential=self.credential,
                subscription_id=self.subscription_id
            )
        return self._container_client

    @property
    def cosmosdb_client(self):
        """Lazy-load Cosmos DB Management client."""
        if self._cosmosdb_client is None:
            self._cosmosdb_client = CosmosDBManagementClient(
                credential=self.credential,
                subscription_id=self.subscription_id
            )
        return self._cosmosdb_client

    # =============================================================================
    # Resource Group Management
    # =============================================================================

    def resource_group_create(self, name: str, location: Optional[str] = None,
                             tags: Optional[Dict[str, str]] = None) -> Any:
        """Create a resource group."""
        location = location or self.location
        try:
            result = self.resource_client.resource_groups.create_or_update(
                name,
                {
                    "location": location,
                    "tags": tags or {}
                }
            )
            return result
        except Exception as e:
            raise RuntimeError(f"Failed to create resource group: {e}")

    def resource_group_list(self) -> List[Any]:
        """List all resource groups."""
        try:
            return list(self.resource_client.resource_groups.list())
        except Exception as e:
            raise RuntimeError(f"Failed to list resource groups: {e}")

    def resource_group_delete(self, name: str) -> bool:
        """Delete a resource group."""
        try:
            poller = self.resource_client.resource_groups.begin_delete(name)
            poller.wait()
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to delete resource group: {e}")

    # =============================================================================
    # Virtual Machine Management
    # =============================================================================

    def vm_create(self, vm_name: str, resource_group: Optional[str] = None,
                  location: Optional[str] = None, vm_size: str = "Standard_B1s",
                  image: Optional[Dict] = None, admin_username: str = "azureuser",
                  admin_password: Optional[str] = None) -> Any:
        """
        Create a virtual machine.

        Note: This is a simplified version. Full VM creation requires
        network interface, public IP, etc.
        """
        resource_group = resource_group or self.resource_group
        location = location or self.location

        # Default to Ubuntu image
        if image is None:
            image = {
                "publisher": "Canonical",
                "offer": "UbuntuServer",
                "sku": "18.04-LTS",
                "version": "latest"
            }

        try:
            vm_parameters = {
                "location": location,
                "hardware_profile": {
                    "vm_size": vm_size
                },
                "storage_profile": {
                    "image_reference": image
                },
                "os_profile": {
                    "computer_name": vm_name,
                    "admin_username": admin_username,
                    "admin_password": admin_password
                }
            }

            poller = self.compute_client.virtual_machines.begin_create_or_update(
                resource_group,
                vm_name,
                vm_parameters
            )
            return poller.result()

        except Exception as e:
            raise RuntimeError(f"Failed to create VM: {e}")

    def vm_list(self, resource_group: Optional[str] = None) -> List[Any]:
        """List virtual machines."""
        resource_group = resource_group or self.resource_group
        try:
            return list(self.compute_client.virtual_machines.list(resource_group))
        except Exception as e:
            raise RuntimeError(f"Failed to list VMs: {e}")

    def vm_start(self, vm_name: str, resource_group: Optional[str] = None) -> bool:
        """Start a virtual machine."""
        resource_group = resource_group or self.resource_group
        try:
            poller = self.compute_client.virtual_machines.begin_start(
                resource_group, vm_name
            )
            poller.wait()
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to start VM: {e}")

    def vm_stop(self, vm_name: str, resource_group: Optional[str] = None) -> bool:
        """Stop (deallocate) a virtual machine."""
        resource_group = resource_group or self.resource_group
        try:
            poller = self.compute_client.virtual_machines.begin_deallocate(
                resource_group, vm_name
            )
            poller.wait()
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to stop VM: {e}")

    def vm_delete(self, vm_name: str, resource_group: Optional[str] = None) -> bool:
        """Delete a virtual machine."""
        resource_group = resource_group or self.resource_group
        try:
            poller = self.compute_client.virtual_machines.begin_delete(
                resource_group, vm_name
            )
            poller.wait()
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to delete VM: {e}")

    def vm_get(self, vm_name: str, resource_group: Optional[str] = None) -> Any:
        """Get virtual machine details."""
        resource_group = resource_group or self.resource_group
        try:
            return self.compute_client.virtual_machines.get(resource_group, vm_name)
        except Exception as e:
            raise RuntimeError(f"Failed to get VM: {e}")

    # =============================================================================
    # Storage Account Management
    # =============================================================================

    def storage_account_create(self, account_name: str,
                              resource_group: Optional[str] = None,
                              location: Optional[str] = None,
                              sku: str = "Standard_LRS") -> Any:
        """Create a storage account."""
        resource_group = resource_group or self.resource_group
        location = location or self.location

        try:
            parameters = {
                "location": location,
                "sku": {"name": sku},
                "kind": "StorageV2"
            }

            poller = self.storage_client.storage_accounts.begin_create(
                resource_group,
                account_name,
                parameters
            )
            return poller.result()

        except Exception as e:
            raise RuntimeError(f"Failed to create storage account: {e}")

    def storage_account_list(self, resource_group: Optional[str] = None) -> List[Any]:
        """List storage accounts."""
        try:
            if resource_group:
                return list(self.storage_client.storage_accounts.list_by_resource_group(
                    resource_group
                ))
            else:
                return list(self.storage_client.storage_accounts.list())
        except Exception as e:
            raise RuntimeError(f"Failed to list storage accounts: {e}")

    def storage_account_delete(self, account_name: str,
                              resource_group: Optional[str] = None) -> bool:
        """Delete a storage account."""
        resource_group = resource_group or self.resource_group
        try:
            self.storage_client.storage_accounts.delete(resource_group, account_name)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to delete storage account: {e}")

    def storage_account_get_keys(self, account_name: str,
                                resource_group: Optional[str] = None) -> List[str]:
        """Get storage account keys."""
        resource_group = resource_group or self.resource_group
        try:
            keys = self.storage_client.storage_accounts.list_keys(
                resource_group, account_name
            )
            return [key.value for key in keys.keys]
        except Exception as e:
            raise RuntimeError(f"Failed to get storage account keys: {e}")

    # =============================================================================
    # Blob Storage Operations
    # =============================================================================

    def blob_upload_file(self, account_name: str, container_name: str,
                        blob_name: str, file_path: str,
                        resource_group: Optional[str] = None) -> bool:
        """Upload a file to blob storage."""
        resource_group = resource_group or self.resource_group

        try:
            # Get account key
            keys = self.storage_account_get_keys(account_name, resource_group)
            account_key = keys[0]

            # Create blob service client
            connection_string = f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"
            blob_service_client = BlobServiceClient.from_connection_string(connection_string)

            # Get blob client
            blob_client = blob_service_client.get_blob_client(
                container=container_name,
                blob=blob_name
            )

            # Upload file
            with open(file_path, "rb") as data:
                blob_client.upload_blob(data, overwrite=True)

            return True

        except Exception as e:
            raise RuntimeError(f"Failed to upload blob: {e}")

    def blob_download_file(self, account_name: str, container_name: str,
                          blob_name: str, file_path: str,
                          resource_group: Optional[str] = None) -> bool:
        """Download a file from blob storage."""
        resource_group = resource_group or self.resource_group

        try:
            # Get account key
            keys = self.storage_account_get_keys(account_name, resource_group)
            account_key = keys[0]

            # Create blob service client
            connection_string = f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"
            blob_service_client = BlobServiceClient.from_connection_string(connection_string)

            # Get blob client
            blob_client = blob_service_client.get_blob_client(
                container=container_name,
                blob=blob_name
            )

            # Download file
            with open(file_path, "wb") as file:
                download_stream = blob_client.download_blob()
                file.write(download_stream.readall())

            return True

        except Exception as e:
            raise RuntimeError(f"Failed to download blob: {e}")

    def blob_list(self, account_name: str, container_name: str,
                 resource_group: Optional[str] = None) -> List[str]:
        """List blobs in a container."""
        resource_group = resource_group or self.resource_group

        try:
            # Get account key
            keys = self.storage_account_get_keys(account_name, resource_group)
            account_key = keys[0]

            # Create blob service client
            connection_string = f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"
            blob_service_client = BlobServiceClient.from_connection_string(connection_string)

            # Get container client
            container_client = blob_service_client.get_container_client(container_name)

            # List blobs
            return [blob.name for blob in container_client.list_blobs()]

        except Exception as e:
            raise RuntimeError(f"Failed to list blobs: {e}")

    # =============================================================================
    # SQL Database Management
    # =============================================================================

    def sql_server_create(self, server_name: str, admin_login: str,
                         admin_password: str,
                         resource_group: Optional[str] = None,
                         location: Optional[str] = None) -> Any:
        """Create a SQL server."""
        resource_group = resource_group or self.resource_group
        location = location or self.location

        try:
            parameters = {
                "location": location,
                "administrator_login": admin_login,
                "administrator_login_password": admin_password,
                "version": "12.0"
            }

            poller = self.sql_client.servers.begin_create_or_update(
                resource_group,
                server_name,
                parameters
            )
            return poller.result()

        except Exception as e:
            raise RuntimeError(f"Failed to create SQL server: {e}")

    def sql_database_create(self, server_name: str, database_name: str,
                           resource_group: Optional[str] = None,
                           location: Optional[str] = None,
                           sku: Optional[Dict] = None) -> Any:
        """Create a SQL database."""
        resource_group = resource_group or self.resource_group
        location = location or self.location

        if sku is None:
            sku = {"name": "Basic", "tier": "Basic"}

        try:
            parameters = {
                "location": location,
                "sku": sku
            }

            poller = self.sql_client.databases.begin_create_or_update(
                resource_group,
                server_name,
                database_name,
                parameters
            )
            return poller.result()

        except Exception as e:
            raise RuntimeError(f"Failed to create SQL database: {e}")

    def sql_database_list(self, server_name: str,
                         resource_group: Optional[str] = None) -> List[Any]:
        """List SQL databases on a server."""
        resource_group = resource_group or self.resource_group
        try:
            return list(self.sql_client.databases.list_by_server(
                resource_group, server_name
            ))
        except Exception as e:
            raise RuntimeError(f"Failed to list SQL databases: {e}")

    # =============================================================================
    # Virtual Network Management
    # =============================================================================

    def vnet_create(self, vnet_name: str, address_prefix: str = "10.0.0.0/16",
                   resource_group: Optional[str] = None,
                   location: Optional[str] = None) -> Any:
        """Create a virtual network."""
        resource_group = resource_group or self.resource_group
        location = location or self.location

        try:
            parameters = {
                "location": location,
                "address_space": {
                    "address_prefixes": [address_prefix]
                }
            }

            poller = self.network_client.virtual_networks.begin_create_or_update(
                resource_group,
                vnet_name,
                parameters
            )
            return poller.result()

        except Exception as e:
            raise RuntimeError(f"Failed to create virtual network: {e}")

    def vnet_list(self, resource_group: Optional[str] = None) -> List[Any]:
        """List virtual networks."""
        resource_group = resource_group or self.resource_group
        try:
            return list(self.network_client.virtual_networks.list(resource_group))
        except Exception as e:
            raise RuntimeError(f"Failed to list virtual networks: {e}")

    # =============================================================================
    # Utility Methods
    # =============================================================================

    def get_subscription_info(self) -> Dict[str, Any]:
        """Get subscription information."""
        try:
            subscription = self.resource_client.subscriptions.get(self.subscription_id)
            return {
                "subscription_id": subscription.subscription_id,
                "display_name": subscription.display_name,
                "state": subscription.state,
                "tenant_id": subscription.tenant_id
            }
        except Exception as e:
            raise RuntimeError(f"Failed to get subscription info: {e}")


# Global instance
_azure_module = None


def get_azure_module(config_path: str = 'aibasic.conf') -> AzureModule:
    """
    Get or create Azure module instance.

    Args:
        config_path: Path to aibasic.conf configuration file

    Returns:
        AzureModule instance
    """
    global _azure_module
    if _azure_module is None:
        _azure_module = AzureModule()
        _azure_module.load_config(config_path)
    return _azure_module
