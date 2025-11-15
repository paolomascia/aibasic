"""
Google Cloud Platform (GCP) Module for AIbasic

This module provides comprehensive integration with Google Cloud Platform services,
enabling natural language management of GCP resources including Compute Engine,
Cloud Storage, Cloud SQL, BigQuery, Cloud Functions, and more.

Features:
- Compute Engine: VM instance management
- Cloud Storage: Bucket and object operations
- Cloud SQL: Database instance management
- BigQuery: Dataset and table operations
- Cloud Functions: Serverless function deployment
- Cloud Run: Container deployment
- Pub/Sub: Message queue operations
- Secret Manager: Secrets management
- IAM: Identity and access management

Architecture:
- Singleton pattern with thread-safe initialization
- Lazy-loading of GCP service clients
- Configuration from aibasic.conf with environment variable fallbacks
- Service account or application default credentials authentication

Usage:
    10 (gcp) create compute instance "web-server" in zone "us-central1-a"
    20 (gcp) create storage bucket "my-bucket" in location "us-central1"
    30 (gcp) upload file "data.txt" to bucket "my-bucket"
"""

import threading
import os
from typing import Optional, Dict, Any, List
from pathlib import Path

# GCP Client Libraries
try:
    from google.cloud import compute_v1
    from google.cloud import storage
    from google.cloud import sql_v1
    from google.cloud import bigquery
    from google.cloud import functions_v1
    from google.cloud import run_v2
    from google.cloud import pubsub_v1
    from google.cloud import secretmanager_v1
    from google.cloud import iam_credentials_v1
    from google.oauth2 import service_account
    from google.auth import default as default_credentials
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_AVAILABLE = False


class GCPModule:
    """
    Google Cloud Platform module for managing GCP resources.

    Implements singleton pattern for efficient resource usage.
    Provides comprehensive GCP operations through official Google Cloud SDK.
    """

    _instance = None
    _lock = threading.Lock()
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the GCP module with configuration from aibasic.conf."""
        if self._initialized:
            return

        with self._lock:
            if self._initialized:
                return

            if not GOOGLE_CLOUD_AVAILABLE:
                raise RuntimeError(
                    "Google Cloud libraries not installed. "
                    "Install with: pip install google-cloud-compute google-cloud-storage "
                    "google-cloud-sql google-cloud-bigquery google-cloud-functions "
                    "google-cloud-run google-cloud-pubsub google-cloud-secret-manager"
                )

            # Read configuration
            self.project_id = os.getenv('GCP_PROJECT_ID') or os.getenv('GOOGLE_CLOUD_PROJECT')
            self.credentials_path = os.getenv('GCP_CREDENTIALS_PATH') or os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            self.region = os.getenv('GCP_REGION', 'us-central1')
            self.zone = os.getenv('GCP_ZONE', 'us-central1-a')

            # Default resource settings
            self.default_machine_type = os.getenv('GCP_DEFAULT_MACHINE_TYPE', 'e2-medium')
            self.default_disk_size = int(os.getenv('GCP_DEFAULT_DISK_SIZE', '10'))
            self.default_network = os.getenv('GCP_DEFAULT_NETWORK', 'default')

            # Lazy-loaded clients
            self._credentials = None
            self._compute_client = None
            self._storage_client = None
            self._sql_admin_client = None
            self._bigquery_client = None
            self._functions_client = None
            self._run_client = None
            self._pubsub_publisher = None
            self._pubsub_subscriber = None
            self._secretmanager_client = None

            self._initialized = True

    @property
    def credentials(self):
        """Get GCP credentials (lazy-loaded)."""
        if self._credentials is None:
            if self.credentials_path and os.path.exists(self.credentials_path):
                self._credentials = service_account.Credentials.from_service_account_file(
                    self.credentials_path
                )
            else:
                # Use Application Default Credentials (ADC)
                self._credentials, _ = default_credentials()
        return self._credentials

    @property
    def compute_client(self):
        """Get Compute Engine instances client (lazy-loaded)."""
        if self._compute_client is None:
            self._compute_client = compute_v1.InstancesClient(credentials=self.credentials)
        return self._compute_client

    @property
    def storage_client(self):
        """Get Cloud Storage client (lazy-loaded)."""
        if self._storage_client is None:
            self._storage_client = storage.Client(
                project=self.project_id,
                credentials=self.credentials
            )
        return self._storage_client

    @property
    def sql_admin_client(self):
        """Get Cloud SQL Admin client (lazy-loaded)."""
        if self._sql_admin_client is None:
            self._sql_admin_client = sql_v1.SqlInstancesServiceClient(credentials=self.credentials)
        return self._sql_admin_client

    @property
    def bigquery_client(self):
        """Get BigQuery client (lazy-loaded)."""
        if self._bigquery_client is None:
            self._bigquery_client = bigquery.Client(
                project=self.project_id,
                credentials=self.credentials
            )
        return self._bigquery_client

    @property
    def functions_client(self):
        """Get Cloud Functions client (lazy-loaded)."""
        if self._functions_client is None:
            self._functions_client = functions_v1.CloudFunctionsServiceClient(credentials=self.credentials)
        return self._functions_client

    @property
    def run_client(self):
        """Get Cloud Run client (lazy-loaded)."""
        if self._run_client is None:
            self._run_client = run_v2.ServicesClient(credentials=self.credentials)
        return self._run_client

    @property
    def pubsub_publisher(self):
        """Get Pub/Sub publisher client (lazy-loaded)."""
        if self._pubsub_publisher is None:
            self._pubsub_publisher = pubsub_v1.PublisherClient(credentials=self.credentials)
        return self._pubsub_publisher

    @property
    def pubsub_subscriber(self):
        """Get Pub/Sub subscriber client (lazy-loaded)."""
        if self._pubsub_subscriber is None:
            self._pubsub_subscriber = pubsub_v1.SubscriberClient(credentials=self.credentials)
        return self._pubsub_subscriber

    @property
    def secretmanager_client(self):
        """Get Secret Manager client (lazy-loaded)."""
        if self._secretmanager_client is None:
            self._secretmanager_client = secretmanager_v1.SecretManagerServiceClient(credentials=self.credentials)
        return self._secretmanager_client

    # =========================================================================
    # Compute Engine Operations
    # =========================================================================

    def compute_instance_create(self, name: str, zone: Optional[str] = None,
                               machine_type: Optional[str] = None,
                               disk_image: str = 'projects/debian-cloud/global/images/family/debian-11',
                               disk_size_gb: Optional[int] = None,
                               network: Optional[str] = None,
                               labels: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Create a Compute Engine VM instance."""
        zone = zone or self.zone
        machine_type = machine_type or self.default_machine_type
        disk_size_gb = disk_size_gb or self.default_disk_size
        network = network or self.default_network

        instance = compute_v1.Instance()
        instance.name = name
        instance.machine_type = f"zones/{zone}/machineTypes/{machine_type}"

        # Boot disk
        disk = compute_v1.AttachedDisk()
        disk.boot = True
        disk.auto_delete = True
        initialize_params = compute_v1.AttachedDiskInitializeParams()
        initialize_params.source_image = disk_image
        initialize_params.disk_size_gb = disk_size_gb
        disk.initialize_params = initialize_params
        instance.disks = [disk]

        # Network interface
        network_interface = compute_v1.NetworkInterface()
        network_interface.name = network
        access_config = compute_v1.AccessConfig()
        access_config.name = "External NAT"
        access_config.type_ = "ONE_TO_ONE_NAT"
        network_interface.access_configs = [access_config]
        instance.network_interfaces = [network_interface]

        # Labels
        if labels:
            instance.labels = labels

        request = compute_v1.InsertInstanceRequest(
            project=self.project_id,
            zone=zone,
            instance_resource=instance
        )

        try:
            operation = self.compute_client.insert(request=request)
            return {"status": "creating", "operation": operation.name, "instance": name}
        except Exception as e:
            raise RuntimeError(f"Failed to create compute instance: {e}")

    def compute_instance_list(self, zone: Optional[str] = None) -> List[Dict[str, Any]]:
        """List Compute Engine instances in a zone."""
        zone = zone or self.zone

        request = compute_v1.ListInstancesRequest(
            project=self.project_id,
            zone=zone
        )

        try:
            instances = []
            for instance in self.compute_client.list(request=request):
                instances.append({
                    "name": instance.name,
                    "machine_type": instance.machine_type.split('/')[-1],
                    "status": instance.status,
                    "zone": zone,
                    "internal_ip": instance.network_interfaces[0].network_i_p if instance.network_interfaces else None,
                    "external_ip": instance.network_interfaces[0].access_configs[0].nat_i_p if instance.network_interfaces and instance.network_interfaces[0].access_configs else None
                })
            return instances
        except Exception as e:
            raise RuntimeError(f"Failed to list compute instances: {e}")

    def compute_instance_start(self, name: str, zone: Optional[str] = None) -> Dict[str, Any]:
        """Start a Compute Engine instance."""
        zone = zone or self.zone

        request = compute_v1.StartInstanceRequest(
            project=self.project_id,
            zone=zone,
            instance=name
        )

        try:
            operation = self.compute_client.start(request=request)
            return {"status": "starting", "operation": operation.name}
        except Exception as e:
            raise RuntimeError(f"Failed to start compute instance: {e}")

    def compute_instance_stop(self, name: str, zone: Optional[str] = None) -> Dict[str, Any]:
        """Stop a Compute Engine instance."""
        zone = zone or self.zone

        request = compute_v1.StopInstanceRequest(
            project=self.project_id,
            zone=zone,
            instance=name
        )

        try:
            operation = self.compute_client.stop(request=request)
            return {"status": "stopping", "operation": operation.name}
        except Exception as e:
            raise RuntimeError(f"Failed to stop compute instance: {e}")

    def compute_instance_delete(self, name: str, zone: Optional[str] = None) -> Dict[str, Any]:
        """Delete a Compute Engine instance."""
        zone = zone or self.zone

        request = compute_v1.DeleteInstanceRequest(
            project=self.project_id,
            zone=zone,
            instance=name
        )

        try:
            operation = self.compute_client.delete(request=request)
            return {"status": "deleting", "operation": operation.name}
        except Exception as e:
            raise RuntimeError(f"Failed to delete compute instance: {e}")

    # =========================================================================
    # Cloud Storage Operations
    # =========================================================================

    def storage_bucket_create(self, name: str, location: Optional[str] = None,
                             storage_class: str = 'STANDARD') -> Dict[str, Any]:
        """Create a Cloud Storage bucket."""
        location = location or self.region

        try:
            bucket = self.storage_client.bucket(name)
            bucket.storage_class = storage_class
            bucket = self.storage_client.create_bucket(bucket, location=location)
            return {
                "name": bucket.name,
                "location": bucket.location,
                "storage_class": bucket.storage_class,
                "time_created": str(bucket.time_created)
            }
        except Exception as e:
            raise RuntimeError(f"Failed to create storage bucket: {e}")

    def storage_bucket_list(self) -> List[Dict[str, Any]]:
        """List all Cloud Storage buckets."""
        try:
            buckets = []
            for bucket in self.storage_client.list_buckets():
                buckets.append({
                    "name": bucket.name,
                    "location": bucket.location,
                    "storage_class": bucket.storage_class,
                    "time_created": str(bucket.time_created)
                })
            return buckets
        except Exception as e:
            raise RuntimeError(f"Failed to list storage buckets: {e}")

    def storage_bucket_delete(self, name: str, force: bool = False) -> Dict[str, Any]:
        """Delete a Cloud Storage bucket."""
        try:
            bucket = self.storage_client.bucket(name)

            if force:
                # Delete all objects first
                blobs = list(bucket.list_blobs())
                for blob in blobs:
                    blob.delete()

            bucket.delete()
            return {"status": "deleted", "bucket": name}
        except Exception as e:
            raise RuntimeError(f"Failed to delete storage bucket: {e}")

    def storage_upload_file(self, bucket_name: str, source_file: str,
                           destination_blob: str) -> Dict[str, Any]:
        """Upload a file to Cloud Storage."""
        try:
            bucket = self.storage_client.bucket(bucket_name)
            blob = bucket.blob(destination_blob)
            blob.upload_from_filename(source_file)

            return {
                "bucket": bucket_name,
                "blob": destination_blob,
                "size": blob.size,
                "md5_hash": blob.md5_hash
            }
        except Exception as e:
            raise RuntimeError(f"Failed to upload file to storage: {e}")

    def storage_download_file(self, bucket_name: str, source_blob: str,
                             destination_file: str) -> Dict[str, Any]:
        """Download a file from Cloud Storage."""
        try:
            bucket = self.storage_client.bucket(bucket_name)
            blob = bucket.blob(source_blob)
            blob.download_to_filename(destination_file)

            return {
                "bucket": bucket_name,
                "blob": source_blob,
                "destination": destination_file,
                "size": blob.size
            }
        except Exception as e:
            raise RuntimeError(f"Failed to download file from storage: {e}")

    def storage_list_blobs(self, bucket_name: str, prefix: Optional[str] = None) -> List[Dict[str, Any]]:
        """List blobs in a Cloud Storage bucket."""
        try:
            bucket = self.storage_client.bucket(bucket_name)
            blobs = []

            for blob in bucket.list_blobs(prefix=prefix):
                blobs.append({
                    "name": blob.name,
                    "size": blob.size,
                    "content_type": blob.content_type,
                    "time_created": str(blob.time_created),
                    "updated": str(blob.updated)
                })

            return blobs
        except Exception as e:
            raise RuntimeError(f"Failed to list blobs: {e}")

    # =========================================================================
    # Cloud SQL Operations
    # =========================================================================

    def cloudsql_instance_create(self, name: str, database_version: str = 'MYSQL_8_0',
                                tier: str = 'db-f1-micro', region: Optional[str] = None) -> Dict[str, Any]:
        """Create a Cloud SQL instance."""
        region = region or self.region

        instance = sql_v1.DatabaseInstance()
        instance.name = name
        instance.database_version = database_version
        instance.region = region

        settings = sql_v1.Settings()
        settings.tier = tier
        instance.settings = settings

        request = sql_v1.InsertRequest(
            project=self.project_id,
            body=instance
        )

        try:
            operation = self.sql_admin_client.insert(request=request)
            return {"status": "creating", "instance": name, "operation": operation.name}
        except Exception as e:
            raise RuntimeError(f"Failed to create Cloud SQL instance: {e}")

    def cloudsql_instance_list(self) -> List[Dict[str, Any]]:
        """List Cloud SQL instances."""
        request = sql_v1.ListRequest(project=self.project_id)

        try:
            response = self.sql_admin_client.list(request=request)
            instances = []

            for instance in response.items or []:
                instances.append({
                    "name": instance.name,
                    "database_version": instance.database_version,
                    "state": instance.state,
                    "region": instance.region,
                    "tier": instance.settings.tier if instance.settings else None
                })

            return instances
        except Exception as e:
            raise RuntimeError(f"Failed to list Cloud SQL instances: {e}")

    def cloudsql_instance_delete(self, name: str) -> Dict[str, Any]:
        """Delete a Cloud SQL instance."""
        request = sql_v1.DeleteRequest(
            project=self.project_id,
            instance=name
        )

        try:
            operation = self.sql_admin_client.delete(request=request)
            return {"status": "deleting", "instance": name, "operation": operation.name}
        except Exception as e:
            raise RuntimeError(f"Failed to delete Cloud SQL instance: {e}")

    # =========================================================================
    # BigQuery Operations
    # =========================================================================

    def bigquery_dataset_create(self, dataset_id: str, location: Optional[str] = None) -> Dict[str, Any]:
        """Create a BigQuery dataset."""
        location = location or self.region

        try:
            dataset = bigquery.Dataset(f"{self.project_id}.{dataset_id}")
            dataset.location = location
            dataset = self.bigquery_client.create_dataset(dataset)

            return {
                "dataset_id": dataset.dataset_id,
                "location": dataset.location,
                "created": str(dataset.created)
            }
        except Exception as e:
            raise RuntimeError(f"Failed to create BigQuery dataset: {e}")

    def bigquery_dataset_list(self) -> List[Dict[str, Any]]:
        """List BigQuery datasets."""
        try:
            datasets = []
            for dataset in self.bigquery_client.list_datasets():
                datasets.append({
                    "dataset_id": dataset.dataset_id,
                    "project": dataset.project,
                    "full_id": dataset.full_dataset_id
                })
            return datasets
        except Exception as e:
            raise RuntimeError(f"Failed to list BigQuery datasets: {e}")

    def bigquery_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute a BigQuery query."""
        try:
            query_job = self.bigquery_client.query(query)
            results = query_job.result()

            rows = []
            for row in results:
                rows.append(dict(row))

            return rows
        except Exception as e:
            raise RuntimeError(f"Failed to execute BigQuery query: {e}")

    # =========================================================================
    # Pub/Sub Operations
    # =========================================================================

    def pubsub_topic_create(self, topic_id: str) -> Dict[str, Any]:
        """Create a Pub/Sub topic."""
        topic_path = self.pubsub_publisher.topic_path(self.project_id, topic_id)

        try:
            topic = self.pubsub_publisher.create_topic(request={"name": topic_path})
            return {"name": topic.name, "topic_id": topic_id}
        except Exception as e:
            raise RuntimeError(f"Failed to create Pub/Sub topic: {e}")

    def pubsub_topic_list(self) -> List[Dict[str, Any]]:
        """List Pub/Sub topics."""
        project_path = f"projects/{self.project_id}"

        try:
            topics = []
            for topic in self.pubsub_publisher.list_topics(request={"project": project_path}):
                topics.append({
                    "name": topic.name,
                    "topic_id": topic.name.split('/')[-1]
                })
            return topics
        except Exception as e:
            raise RuntimeError(f"Failed to list Pub/Sub topics: {e}")

    def pubsub_publish(self, topic_id: str, message: str, **attributes) -> Dict[str, Any]:
        """Publish a message to a Pub/Sub topic."""
        topic_path = self.pubsub_publisher.topic_path(self.project_id, topic_id)

        try:
            data = message.encode('utf-8')
            future = self.pubsub_publisher.publish(topic_path, data, **attributes)
            message_id = future.result()

            return {"message_id": message_id, "topic": topic_id}
        except Exception as e:
            raise RuntimeError(f"Failed to publish message: {e}")

    def pubsub_subscription_create(self, subscription_id: str, topic_id: str) -> Dict[str, Any]:
        """Create a Pub/Sub subscription."""
        subscription_path = self.pubsub_subscriber.subscription_path(self.project_id, subscription_id)
        topic_path = self.pubsub_publisher.topic_path(self.project_id, topic_id)

        try:
            subscription = self.pubsub_subscriber.create_subscription(
                request={"name": subscription_path, "topic": topic_path}
            )
            return {"name": subscription.name, "topic": subscription.topic}
        except Exception as e:
            raise RuntimeError(f"Failed to create Pub/Sub subscription: {e}")

    # =========================================================================
    # Secret Manager Operations
    # =========================================================================

    def secret_create(self, secret_id: str, value: str) -> Dict[str, Any]:
        """Create a secret in Secret Manager."""
        parent = f"projects/{self.project_id}"

        try:
            # Create secret
            secret = secretmanager_v1.Secret()
            secret.replication = secretmanager_v1.Replication()
            secret.replication.automatic = secretmanager_v1.Replication.Automatic()

            create_request = secretmanager_v1.CreateSecretRequest(
                parent=parent,
                secret_id=secret_id,
                secret=secret
            )

            created_secret = self.secretmanager_client.create_secret(request=create_request)

            # Add version with value
            version_parent = created_secret.name
            payload = secretmanager_v1.SecretPayload()
            payload.data = value.encode('utf-8')

            version_request = secretmanager_v1.AddSecretVersionRequest(
                parent=version_parent,
                payload=payload
            )

            version = self.secretmanager_client.add_secret_version(request=version_request)

            return {
                "secret": created_secret.name,
                "version": version.name
            }
        except Exception as e:
            raise RuntimeError(f"Failed to create secret: {e}")

    def secret_get(self, secret_id: str, version: str = 'latest') -> str:
        """Get a secret value from Secret Manager."""
        name = f"projects/{self.project_id}/secrets/{secret_id}/versions/{version}"

        try:
            response = self.secretmanager_client.access_secret_version(request={"name": name})
            return response.payload.data.decode('utf-8')
        except Exception as e:
            raise RuntimeError(f"Failed to get secret: {e}")

    def secret_list(self) -> List[Dict[str, Any]]:
        """List secrets in Secret Manager."""
        parent = f"projects/{self.project_id}"

        try:
            secrets = []
            for secret in self.secretmanager_client.list_secrets(request={"parent": parent}):
                secrets.append({
                    "name": secret.name,
                    "secret_id": secret.name.split('/')[-1],
                    "created": str(secret.create_time)
                })
            return secrets
        except Exception as e:
            raise RuntimeError(f"Failed to list secrets: {e}")

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def get_project_info(self) -> Dict[str, Any]:
        """Get project information."""
        return {
            "project_id": self.project_id,
            "region": self.region,
            "zone": self.zone,
            "credentials_configured": self._credentials is not None or self.credentials_path is not None
        }


# Singleton instance
_gcp_module = None

def get_gcp_module() -> GCPModule:
    """Get the singleton GCP module instance."""
    global _gcp_module
    if _gcp_module is None:
        _gcp_module = GCPModule()
    return _gcp_module
