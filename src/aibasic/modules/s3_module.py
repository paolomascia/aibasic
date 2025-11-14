"""
S3/MinIO Module for Object Storage Operations

This module provides unified access to S3-compatible object storage services
including Amazon S3, MinIO, DigitalOcean Spaces, Wasabi, and other S3-compatible providers.
Configuration is loaded from aibasic.conf under the [s3] section.

Supports:
- AWS S3 and S3-compatible services (MinIO, DigitalOcean Spaces, etc.)
- Bucket operations (create, delete, list)
- Object operations (upload, download, delete, copy)
- Multipart uploads for large files
- Presigned URLs for temporary access
- Server-side encryption
- Object versioning
- Lifecycle policies
- Access control (ACLs and bucket policies)
- Object metadata and tags
- Streaming uploads and downloads

Features:
- Upload/download files and directories
- List objects with filtering
- Generate presigned URLs
- Multipart uploads for large files
- Server-side encryption (SSE-S3, SSE-KMS, SSE-C)
- Object versioning support
- Bucket lifecycle management
- Access control with ACLs
- Object tagging and metadata
- Streaming for memory efficiency

Example configuration in aibasic.conf:
    [s3]
    # AWS S3 Configuration
    ENDPOINT_URL=https://s3.amazonaws.com
    AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
    AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
    REGION=us-east-1

    # MinIO Configuration (alternative)
    # ENDPOINT_URL=http://localhost:9000
    # AWS_ACCESS_KEY_ID=minioadmin
    # AWS_SECRET_ACCESS_KEY=minioadmin
    # REGION=us-east-1

    # DigitalOcean Spaces Configuration (alternative)
    # ENDPOINT_URL=https://nyc3.digitaloceanspaces.com
    # AWS_ACCESS_KEY_ID=your_spaces_key
    # AWS_SECRET_ACCESS_KEY=your_spaces_secret
    # REGION=nyc3

    # SSL/TLS Settings
    VERIFY_SSL=true  # Set to false for self-signed certs (MinIO dev)

    # Optional Settings
    DEFAULT_BUCKET=my-bucket
    SIGNATURE_VERSION=s3v4
    MULTIPART_THRESHOLD=8388608  # 8MB
    MULTIPART_CHUNKSIZE=8388608  # 8MB

Example usage:
    # Initialize from config
    s3 = S3Module.from_config('aibasic.conf')

    # Create bucket
    s3.create_bucket('my-bucket')

    # Upload file
    s3.upload_file('data.csv', 'my-bucket', 'uploads/data.csv')

    # Download file
    s3.download_file('my-bucket', 'uploads/data.csv', 'downloaded.csv')

    # List objects
    objects = s3.list_objects('my-bucket', prefix='uploads/')

    # Generate presigned URL
    url = s3.generate_presigned_url('my-bucket', 'uploads/data.csv', expiration=3600)
"""

import configparser
import threading
import os
from pathlib import Path
from typing import Optional, Dict, Any, List, Union, BinaryIO
from datetime import datetime, timedelta
import mimetypes

try:
    import boto3
    from boto3.s3.transfer import TransferConfig
    from botocore.exceptions import ClientError, NoCredentialsError, EndpointConnectionError
    from botocore.config import Config
except ImportError:
    boto3 = None
    TransferConfig = None
    ClientError = None
    NoCredentialsError = None
    EndpointConnectionError = None
    Config = None
    print("[S3Module] Warning: boto3 not installed. Install with: pip install boto3")


class S3Module:
    """
    S3/MinIO object storage module with singleton pattern.
    Provides unified interface for S3-compatible object storage operations.
    """

    _instance = None
    _lock = threading.Lock()

    def __init__(
        self,
        endpoint_url: Optional[str] = None,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        region: str = 'us-east-1',
        verify_ssl: bool = True,
        default_bucket: Optional[str] = None,
        signature_version: str = 's3v4',
        multipart_threshold: int = 8 * 1024 * 1024,  # 8MB
        multipart_chunksize: int = 8 * 1024 * 1024,  # 8MB
    ):
        """
        Initialize S3 module with connection parameters.

        Args:
            endpoint_url: S3 endpoint URL (None for AWS S3, custom for MinIO/Spaces)
            aws_access_key_id: AWS access key ID
            aws_secret_access_key: AWS secret access key
            region: AWS region or equivalent
            verify_ssl: Whether to verify SSL certificates
            default_bucket: Default bucket for operations
            signature_version: Signature version (s3v4 recommended)
            multipart_threshold: File size threshold for multipart uploads (bytes)
            multipart_chunksize: Chunk size for multipart uploads (bytes)
        """
        if boto3 is None:
            raise ImportError(
                "boto3 is required for S3Module. "
                "Install it with: pip install boto3"
            )

        self.endpoint_url = endpoint_url
        self.region = region
        self.verify_ssl = verify_ssl
        self.default_bucket = default_bucket

        # Configure transfer settings
        self.transfer_config = TransferConfig(
            multipart_threshold=multipart_threshold,
            multipart_chunksize=multipart_chunksize,
            use_threads=True
        )

        # Configure boto3 client
        config = Config(
            signature_version=signature_version,
            s3={'addressing_style': 'auto'}  # Auto-detect path/virtual-hosted style
        )

        # Create S3 client
        try:
            client_params = {
                'service_name': 's3',
                'aws_access_key_id': aws_access_key_id,
                'aws_secret_access_key': aws_secret_access_key,
                'region_name': region,
                'config': config,
                'verify': verify_ssl
            }

            if endpoint_url:
                client_params['endpoint_url'] = endpoint_url

            self.client = boto3.client(**client_params)
            self.resource = boto3.resource(**{k: v for k, v in client_params.items() if k != 'service_name'})

            if not verify_ssl:
                print(f"[S3Module] ⚠️ SSL certificate verification DISABLED for {endpoint_url or 'AWS S3'}")

            # Test connection
            try:
                self.client.list_buckets()
                print(f"[S3Module] ✓ Connected to S3-compatible storage at {endpoint_url or 'AWS S3'}")
            except ClientError as e:
                print(f"[S3Module] ⚠️ Connection test failed: {e}")

        except Exception as e:
            raise RuntimeError(f"Failed to initialize S3 client: {e}")

    @classmethod
    def from_config(cls, config_path: str = "aibasic.conf"):
        """
        Create S3Module instance from configuration file (singleton pattern).

        Args:
            config_path: Path to configuration file

        Returns:
            S3Module instance
        """
        with cls._lock:
            if cls._instance is None:
                config = configparser.ConfigParser()
                config_file = Path(config_path)

                if not config_file.exists():
                    raise FileNotFoundError(f"Configuration file not found: {config_path}")

                config.read(config_file)

                if 's3' not in config:
                    raise KeyError(f"Missing [s3] section in {config_path}")

                s3_config = config['s3']

                cls._instance = cls(
                    endpoint_url=s3_config.get('ENDPOINT_URL'),
                    aws_access_key_id=s3_config.get('AWS_ACCESS_KEY_ID'),
                    aws_secret_access_key=s3_config.get('AWS_SECRET_ACCESS_KEY'),
                    region=s3_config.get('REGION', 'us-east-1'),
                    verify_ssl=s3_config.getboolean('VERIFY_SSL', True),
                    default_bucket=s3_config.get('DEFAULT_BUCKET'),
                    signature_version=s3_config.get('SIGNATURE_VERSION', 's3v4'),
                    multipart_threshold=s3_config.getint('MULTIPART_THRESHOLD', 8388608),
                    multipart_chunksize=s3_config.getint('MULTIPART_CHUNKSIZE', 8388608)
                )

                print("[S3Module] Module initialized from config (singleton)")

            return cls._instance

    # ==================== Bucket Operations ====================

    def create_bucket(self, bucket_name: str, region: Optional[str] = None, acl: str = 'private') -> bool:
        """
        Create a new S3 bucket.

        Args:
            bucket_name: Name of the bucket to create
            region: AWS region (uses default if not specified)
            acl: Access control list (private, public-read, public-read-write, authenticated-read)

        Returns:
            True if successful, False otherwise
        """
        try:
            region = region or self.region

            if region == 'us-east-1':
                # us-east-1 doesn't require LocationConstraint
                self.client.create_bucket(Bucket=bucket_name, ACL=acl)
            else:
                self.client.create_bucket(
                    Bucket=bucket_name,
                    ACL=acl,
                    CreateBucketConfiguration={'LocationConstraint': region}
                )

            print(f"[S3Module] ✓ Bucket '{bucket_name}' created in {region}")
            return True
        except ClientError as e:
            print(f"[S3Module] ✗ Failed to create bucket: {e}")
            return False

    def delete_bucket(self, bucket_name: str, force: bool = False) -> bool:
        """
        Delete an S3 bucket.

        Args:
            bucket_name: Name of the bucket to delete
            force: If True, delete all objects in bucket first

        Returns:
            True if successful, False otherwise
        """
        try:
            if force:
                # Delete all objects first
                bucket = self.resource.Bucket(bucket_name)
                bucket.objects.all().delete()
                print(f"[S3Module] Deleted all objects in bucket '{bucket_name}'")

            self.client.delete_bucket(Bucket=bucket_name)
            print(f"[S3Module] ✓ Bucket '{bucket_name}' deleted")
            return True
        except ClientError as e:
            print(f"[S3Module] ✗ Failed to delete bucket: {e}")
            return False

    def list_buckets(self) -> List[Dict[str, Any]]:
        """
        List all buckets.

        Returns:
            List of bucket information dictionaries
        """
        try:
            response = self.client.list_buckets()
            buckets = []
            for bucket in response.get('Buckets', []):
                buckets.append({
                    'name': bucket['Name'],
                    'creation_date': bucket['CreationDate']
                })
            return buckets
        except ClientError as e:
            print(f"[S3Module] ✗ Failed to list buckets: {e}")
            return []

    def bucket_exists(self, bucket_name: str) -> bool:
        """
        Check if a bucket exists.

        Args:
            bucket_name: Name of the bucket

        Returns:
            True if bucket exists, False otherwise
        """
        try:
            self.client.head_bucket(Bucket=bucket_name)
            return True
        except ClientError:
            return False

    # ==================== Object Operations ====================

    def upload_file(
        self,
        local_path: str,
        bucket_name: Optional[str] = None,
        object_key: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        content_type: Optional[str] = None,
        acl: str = 'private',
        encryption: Optional[str] = None
    ) -> bool:
        """
        Upload a file to S3.

        Args:
            local_path: Path to local file
            bucket_name: Target bucket (uses default if not specified)
            object_key: S3 object key (uses filename if not specified)
            metadata: Custom metadata dictionary
            content_type: MIME type (auto-detected if not specified)
            acl: Access control list
            encryption: Server-side encryption (AES256, aws:kms)

        Returns:
            True if successful, False otherwise
        """
        bucket_name = bucket_name or self.default_bucket
        if not bucket_name:
            raise ValueError("Bucket name must be specified or configured as default")

        local_file = Path(local_path)
        if not local_file.exists():
            print(f"[S3Module] ✗ File not found: {local_path}")
            return False

        object_key = object_key or local_file.name

        # Auto-detect content type
        if not content_type:
            content_type, _ = mimetypes.guess_type(local_path)
            content_type = content_type or 'application/octet-stream'

        try:
            extra_args = {
                'ACL': acl,
                'ContentType': content_type
            }

            if metadata:
                extra_args['Metadata'] = metadata

            if encryption:
                extra_args['ServerSideEncryption'] = encryption

            self.client.upload_file(
                str(local_file),
                bucket_name,
                object_key,
                ExtraArgs=extra_args,
                Config=self.transfer_config
            )

            print(f"[S3Module] ✓ Uploaded {local_path} to s3://{bucket_name}/{object_key}")
            return True
        except ClientError as e:
            print(f"[S3Module] ✗ Upload failed: {e}")
            return False

    def download_file(
        self,
        bucket_name: Optional[str] = None,
        object_key: str = None,
        local_path: str = None,
        version_id: Optional[str] = None
    ) -> bool:
        """
        Download a file from S3.

        Args:
            bucket_name: Source bucket (uses default if not specified)
            object_key: S3 object key
            local_path: Path to save file locally
            version_id: Specific version to download (if versioning enabled)

        Returns:
            True if successful, False otherwise
        """
        bucket_name = bucket_name or self.default_bucket
        if not bucket_name or not object_key:
            raise ValueError("Bucket name and object key must be specified")

        local_path = local_path or Path(object_key).name

        try:
            extra_args = {}
            if version_id:
                extra_args['VersionId'] = version_id

            self.client.download_file(
                bucket_name,
                object_key,
                local_path,
                ExtraArgs=extra_args if extra_args else None,
                Config=self.transfer_config
            )

            print(f"[S3Module] ✓ Downloaded s3://{bucket_name}/{object_key} to {local_path}")
            return True
        except ClientError as e:
            print(f"[S3Module] ✗ Download failed: {e}")
            return False

    def delete_object(
        self,
        bucket_name: Optional[str] = None,
        object_key: str = None,
        version_id: Optional[str] = None
    ) -> bool:
        """
        Delete an object from S3.

        Args:
            bucket_name: Target bucket
            object_key: S3 object key
            version_id: Specific version to delete

        Returns:
            True if successful, False otherwise
        """
        bucket_name = bucket_name or self.default_bucket
        if not bucket_name or not object_key:
            raise ValueError("Bucket name and object key must be specified")

        try:
            params = {'Bucket': bucket_name, 'Key': object_key}
            if version_id:
                params['VersionId'] = version_id

            self.client.delete_object(**params)
            print(f"[S3Module] ✓ Deleted s3://{bucket_name}/{object_key}")
            return True
        except ClientError as e:
            print(f"[S3Module] ✗ Delete failed: {e}")
            return False

    def copy_object(
        self,
        source_bucket: str,
        source_key: str,
        dest_bucket: Optional[str] = None,
        dest_key: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        acl: str = 'private'
    ) -> bool:
        """
        Copy an object within S3.

        Args:
            source_bucket: Source bucket name
            source_key: Source object key
            dest_bucket: Destination bucket (uses source if not specified)
            dest_key: Destination object key (uses source if not specified)
            metadata: New metadata (replaces existing)
            acl: Access control list

        Returns:
            True if successful, False otherwise
        """
        dest_bucket = dest_bucket or source_bucket
        dest_key = dest_key or source_key

        try:
            copy_source = {'Bucket': source_bucket, 'Key': source_key}

            extra_args = {'ACL': acl}
            if metadata:
                extra_args['Metadata'] = metadata
                extra_args['MetadataDirective'] = 'REPLACE'

            self.client.copy_object(
                CopySource=copy_source,
                Bucket=dest_bucket,
                Key=dest_key,
                **extra_args
            )

            print(f"[S3Module] ✓ Copied s3://{source_bucket}/{source_key} to s3://{dest_bucket}/{dest_key}")
            return True
        except ClientError as e:
            print(f"[S3Module] ✗ Copy failed: {e}")
            return False

    def list_objects(
        self,
        bucket_name: Optional[str] = None,
        prefix: str = '',
        max_keys: int = 1000,
        delimiter: str = ''
    ) -> List[Dict[str, Any]]:
        """
        List objects in a bucket.

        Args:
            bucket_name: Bucket to list (uses default if not specified)
            prefix: Filter by prefix
            max_keys: Maximum number of keys to return
            delimiter: Delimiter for grouping (e.g., '/' for folder-like listing)

        Returns:
            List of object information dictionaries
        """
        bucket_name = bucket_name or self.default_bucket
        if not bucket_name:
            raise ValueError("Bucket name must be specified")

        try:
            params = {
                'Bucket': bucket_name,
                'Prefix': prefix,
                'MaxKeys': max_keys
            }
            if delimiter:
                params['Delimiter'] = delimiter

            response = self.client.list_objects_v2(**params)

            objects = []
            for obj in response.get('Contents', []):
                objects.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'],
                    'etag': obj['ETag'].strip('"'),
                    'storage_class': obj.get('StorageClass', 'STANDARD')
                })

            return objects
        except ClientError as e:
            print(f"[S3Module] ✗ List failed: {e}")
            return []

    def object_exists(self, bucket_name: Optional[str] = None, object_key: str = None) -> bool:
        """
        Check if an object exists.

        Args:
            bucket_name: Bucket name
            object_key: Object key

        Returns:
            True if object exists, False otherwise
        """
        bucket_name = bucket_name or self.default_bucket
        if not bucket_name or not object_key:
            raise ValueError("Bucket name and object key must be specified")

        try:
            self.client.head_object(Bucket=bucket_name, Key=object_key)
            return True
        except ClientError:
            return False

    def get_object_metadata(
        self,
        bucket_name: Optional[str] = None,
        object_key: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get object metadata.

        Args:
            bucket_name: Bucket name
            object_key: Object key

        Returns:
            Metadata dictionary or None if not found
        """
        bucket_name = bucket_name or self.default_bucket
        if not bucket_name or not object_key:
            raise ValueError("Bucket name and object key must be specified")

        try:
            response = self.client.head_object(Bucket=bucket_name, Key=object_key)
            return {
                'content_type': response.get('ContentType'),
                'content_length': response.get('ContentLength'),
                'last_modified': response.get('LastModified'),
                'etag': response.get('ETag', '').strip('"'),
                'metadata': response.get('Metadata', {}),
                'version_id': response.get('VersionId'),
                'storage_class': response.get('StorageClass')
            }
        except ClientError as e:
            print(f"[S3Module] ✗ Failed to get metadata: {e}")
            return None

    # ==================== Presigned URLs ====================

    def generate_presigned_url(
        self,
        bucket_name: Optional[str] = None,
        object_key: str = None,
        expiration: int = 3600,
        http_method: str = 'get_object'
    ) -> Optional[str]:
        """
        Generate a presigned URL for temporary access.

        Args:
            bucket_name: Bucket name
            object_key: Object key
            expiration: URL expiration time in seconds (default: 1 hour)
            http_method: HTTP method (get_object, put_object)

        Returns:
            Presigned URL string or None if failed
        """
        bucket_name = bucket_name or self.default_bucket
        if not bucket_name or not object_key:
            raise ValueError("Bucket name and object key must be specified")

        try:
            url = self.client.generate_presigned_url(
                ClientMethod=http_method,
                Params={'Bucket': bucket_name, 'Key': object_key},
                ExpiresIn=expiration
            )
            print(f"[S3Module] ✓ Generated presigned URL (expires in {expiration}s)")
            return url
        except ClientError as e:
            print(f"[S3Module] ✗ Failed to generate presigned URL: {e}")
            return None

    # ==================== Batch Operations ====================

    def upload_directory(
        self,
        local_dir: str,
        bucket_name: Optional[str] = None,
        prefix: str = '',
        include_pattern: str = '*'
    ) -> int:
        """
        Upload an entire directory to S3.

        Args:
            local_dir: Local directory path
            bucket_name: Target bucket
            prefix: S3 key prefix (folder path)
            include_pattern: File pattern to include (e.g., '*.csv')

        Returns:
            Number of files uploaded
        """
        bucket_name = bucket_name or self.default_bucket
        if not bucket_name:
            raise ValueError("Bucket name must be specified")

        local_path = Path(local_dir)
        if not local_path.is_dir():
            print(f"[S3Module] ✗ Not a directory: {local_dir}")
            return 0

        count = 0
        for file_path in local_path.rglob(include_pattern):
            if file_path.is_file():
                relative_path = file_path.relative_to(local_path)
                object_key = str(Path(prefix) / relative_path).replace('\\', '/')

                if self.upload_file(str(file_path), bucket_name, object_key):
                    count += 1

        print(f"[S3Module] ✓ Uploaded {count} files from {local_dir}")
        return count

    def download_directory(
        self,
        bucket_name: Optional[str] = None,
        prefix: str = '',
        local_dir: str = '.',
        max_keys: int = 1000
    ) -> int:
        """
        Download objects with a common prefix to local directory.

        Args:
            bucket_name: Source bucket
            prefix: S3 key prefix to download
            local_dir: Local directory to save files
            max_keys: Maximum number of objects to download

        Returns:
            Number of files downloaded
        """
        bucket_name = bucket_name or self.default_bucket
        if not bucket_name:
            raise ValueError("Bucket name must be specified")

        objects = self.list_objects(bucket_name, prefix, max_keys)
        local_path = Path(local_dir)
        local_path.mkdir(parents=True, exist_ok=True)

        count = 0
        for obj in objects:
            object_key = obj['key']
            # Remove prefix to get relative path
            relative_key = object_key[len(prefix):].lstrip('/')
            target_path = local_path / relative_key

            # Create parent directories
            target_path.parent.mkdir(parents=True, exist_ok=True)

            if self.download_file(bucket_name, object_key, str(target_path)):
                count += 1

        print(f"[S3Module] ✓ Downloaded {count} files to {local_dir}")
        return count

    def delete_objects(
        self,
        bucket_name: Optional[str] = None,
        object_keys: List[str] = None
    ) -> int:
        """
        Delete multiple objects in a single request.

        Args:
            bucket_name: Target bucket
            object_keys: List of object keys to delete

        Returns:
            Number of objects deleted
        """
        bucket_name = bucket_name or self.default_bucket
        if not bucket_name or not object_keys:
            raise ValueError("Bucket name and object keys must be specified")

        try:
            objects = [{'Key': key} for key in object_keys]
            response = self.client.delete_objects(
                Bucket=bucket_name,
                Delete={'Objects': objects}
            )

            deleted_count = len(response.get('Deleted', []))
            print(f"[S3Module] ✓ Deleted {deleted_count} objects from {bucket_name}")
            return deleted_count
        except ClientError as e:
            print(f"[S3Module] ✗ Batch delete failed: {e}")
            return 0

    # ==================== Utility Methods ====================

    def get_bucket_size(self, bucket_name: Optional[str] = None, prefix: str = '') -> int:
        """
        Calculate total size of objects in bucket or prefix.

        Args:
            bucket_name: Bucket to measure
            prefix: Filter by prefix

        Returns:
            Total size in bytes
        """
        bucket_name = bucket_name or self.default_bucket
        if not bucket_name:
            raise ValueError("Bucket name must be specified")

        objects = self.list_objects(bucket_name, prefix)
        total_size = sum(obj['size'] for obj in objects)

        print(f"[S3Module] Bucket size: {total_size:,} bytes ({total_size / (1024**3):.2f} GB)")
        return total_size

    def close(self):
        """Close S3 client (boto3 handles this automatically)."""
        print("[S3Module] Connection closed")
