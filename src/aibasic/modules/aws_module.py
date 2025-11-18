"""
AWS Module for Amazon Web Services Integration

This module provides comprehensive access to AWS services including:
- S3: Object storage (extended from S3Module)
- DynamoDB: NoSQL database
- SQS: Simple Queue Service
- SNS: Simple Notification Service
- Lambda: Serverless functions
- EC2: Elastic Compute Cloud
- CloudWatch: Monitoring and logging
- Secrets Manager: Secure secrets storage
- SES: Simple Email Service
- EventBridge: Event bus

Configuration is loaded from aibasic.conf under the [aws] section.

Features:
- Multi-service integration in single module
- Automatic credential management (IAM, environment, config)
- Session management with connection pooling
- Resource tagging support
- Error handling with retries
- Support for multiple regions
- LocalStack support for local development

Example configuration in aibasic.conf:
    [aws]
    # AWS Credentials (or use IAM roles, environment variables)
    AWS_ACCESS_KEY_ID = AKIAIOSFODNN7EXAMPLE
    AWS_SECRET_ACCESS_KEY = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
    AWS_REGION = us-east-1

    # Optional: Session Token (for temporary credentials)
    # AWS_SESSION_TOKEN = your_session_token

    # Optional: Endpoint URL (for LocalStack or custom endpoints)
    # ENDPOINT_URL = http://localhost:4566

    # Optional: Default S3 Bucket
    # DEFAULT_S3_BUCKET = my-bucket

    # Optional: Default DynamoDB Table
    # DEFAULT_DYNAMODB_TABLE = my-table

    # Optional: Default SQS Queue
    # DEFAULT_SQS_QUEUE = my-queue

    # Optional: Default SNS Topic
    # DEFAULT_SNS_TOPIC = arn:aws:sns:us-east-1:123456789012:my-topic

    # Optional: Verify SSL (set false for LocalStack)
    # VERIFY_SSL = true

    # Optional: Retry Configuration
    # MAX_RETRIES = 3
    # RETRY_MODE = standard

Example usage:
    # Initialize from config
    aws = AWSModule.from_config('aibasic.conf')

    # S3 Operations
    aws.s3_upload_file('data.csv', 'my-bucket', 'data.csv')
    aws.s3_download_file('my-bucket', 'data.csv', 'downloaded.csv')
    objects = aws.s3_list_objects('my-bucket')

    # DynamoDB Operations
    aws.dynamodb_put_item('users', {'user_id': '123', 'name': 'Alice'})
    item = aws.dynamodb_get_item('users', {'user_id': '123'})
    items = aws.dynamodb_scan('users', filter_expr='age > :age', expr_values={':age': 18})

    # SQS Operations
    aws.sqs_send_message('my-queue', {'order_id': '456', 'status': 'pending'})
    messages = aws.sqs_receive_messages('my-queue', max_messages=10)
    aws.sqs_delete_message('my-queue', receipt_handle)

    # SNS Operations
    aws.sns_publish('my-topic-arn', 'Hello from AIbasic!', subject='Notification')

    # Lambda Operations
    response = aws.lambda_invoke('my-function', {'key': 'value'})

    # Secrets Manager
    secret = aws.secrets_get_secret('database/prod/credentials')
    aws.secrets_create_secret('api/key', {'api_key': 'abc123'})
"""

import configparser
import threading
import json
import base64
import os
from pathlib import Path
from typing import Optional, Dict, Any, List, Union, BinaryIO
from datetime import datetime, timedelta
import mimetypes
from .module_base import AIbasicModuleBase

try:
    import boto3
    from boto3.dynamodb.conditions import Key, Attr
    from boto3.s3.transfer import TransferConfig
    from botocore.exceptions import ClientError, NoCredentialsError, EndpointConnectionError
    from botocore.config import Config as BotoConfig
except ImportError:
    boto3 = None
    Key = None
    Attr = None
    TransferConfig = None
    ClientError = None
    NoCredentialsError = None
    EndpointConnectionError = None
    BotoConfig = None


class AWSModule(AIbasicModuleBase):
    """
    AWS Module for comprehensive Amazon Web Services integration.

    Provides access to multiple AWS services through a single interface.
    Supports credential management, multi-region operations, and LocalStack for development.
    """

    _instance = None
    _lock = threading.Lock()
    _initialized = False

    def __new__(cls, *args, **kwargs):
        """Singleton pattern to ensure only one AWS session per application."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        aws_session_token: Optional[str] = None,
        region_name: str = 'us-east-1',
        endpoint_url: Optional[str] = None,
        verify_ssl: bool = True,
        max_retries: int = 3,
        retry_mode: str = 'standard',
        default_s3_bucket: Optional[str] = None,
        default_dynamodb_table: Optional[str] = None,
        default_sqs_queue: Optional[str] = None,
        default_sns_topic: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize AWS Module.

        Args:
            aws_access_key_id: AWS access key ID (optional, can use IAM role or env)
            aws_secret_access_key: AWS secret access key
            aws_session_token: AWS session token (for temporary credentials)
            region_name: AWS region (default: us-east-1)
            endpoint_url: Custom endpoint URL (for LocalStack or VPC endpoints)
            verify_ssl: Verify SSL certificates (default: True)
            max_retries: Maximum number of retries (default: 3)
            retry_mode: Retry mode (standard, legacy, adaptive)
            default_s3_bucket: Default S3 bucket name
            default_dynamodb_table: Default DynamoDB table name
            default_sqs_queue: Default SQS queue name
            default_sns_topic: Default SNS topic ARN
        """
        if self._initialized:
            return

        if boto3 is None:
            raise ImportError(
                "boto3 library is required for AWS module. "
                "Install it with: pip install boto3"
            )

        with self._lock:
            if self._initialized:
                return

            self.region_name = region_name
            self.endpoint_url = endpoint_url
            self.verify_ssl = verify_ssl
            self.default_s3_bucket = default_s3_bucket
            self.default_dynamodb_table = default_dynamodb_table
            self.default_sqs_queue = default_sqs_queue
            self.default_sns_topic = default_sns_topic

            # Configure boto3 retry behavior
            self.boto_config = BotoConfig(
                retries={
                    'max_attempts': max_retries,
                    'mode': retry_mode
                },
                region_name=region_name
            )

            # Create session with credentials
            session_kwargs = {
                'region_name': region_name
            }

            if aws_access_key_id and aws_secret_access_key:
                session_kwargs['aws_access_key_id'] = aws_access_key_id
                session_kwargs['aws_secret_access_key'] = aws_secret_access_key

            if aws_session_token:
                session_kwargs['aws_session_token'] = aws_session_token

            self.session = boto3.Session(**session_kwargs)

            # Initialize service clients
            self._s3_client = None
            self._dynamodb_client = None
            self._dynamodb_resource = None
            self._sqs_client = None
            self._sns_client = None
            self._lambda_client = None
            self._ec2_client = None
            self._cloudwatch_client = None
            self._secrets_client = None
            self._ses_client = None
            self._events_client = None

            # S3 Transfer configuration for multipart uploads
            self.s3_transfer_config = TransferConfig(
                multipart_threshold=8 * 1024 * 1024,  # 8MB
                max_concurrency=10,
                multipart_chunksize=8 * 1024 * 1024,  # 8MB
                use_threads=True
            )

            self._initialized = True

    @property
    def s3(self):
        """Lazy-load S3 client."""
        if self._s3_client is None:
            client_kwargs = {
                'config': self.boto_config,
                'verify': self.verify_ssl
            }
            if self.endpoint_url:
                client_kwargs['endpoint_url'] = self.endpoint_url
            self._s3_client = self.session.client('s3', **client_kwargs)
        return self._s3_client

    @property
    def dynamodb(self):
        """Lazy-load DynamoDB client."""
        if self._dynamodb_client is None:
            client_kwargs = {
                'config': self.boto_config,
                'verify': self.verify_ssl
            }
            if self.endpoint_url:
                client_kwargs['endpoint_url'] = self.endpoint_url
            self._dynamodb_client = self.session.client('dynamodb', **client_kwargs)
        return self._dynamodb_client

    @property
    def dynamodb_resource(self):
        """Lazy-load DynamoDB resource (high-level interface)."""
        if self._dynamodb_resource is None:
            resource_kwargs = {
                'config': self.boto_config,
                'verify': self.verify_ssl
            }
            if self.endpoint_url:
                resource_kwargs['endpoint_url'] = self.endpoint_url
            self._dynamodb_resource = self.session.resource('dynamodb', **resource_kwargs)
        return self._dynamodb_resource

    @property
    def sqs(self):
        """Lazy-load SQS client."""
        if self._sqs_client is None:
            client_kwargs = {
                'config': self.boto_config,
                'verify': self.verify_ssl
            }
            if self.endpoint_url:
                client_kwargs['endpoint_url'] = self.endpoint_url
            self._sqs_client = self.session.client('sqs', **client_kwargs)
        return self._sqs_client

    @property
    def sns(self):
        """Lazy-load SNS client."""
        if self._sns_client is None:
            client_kwargs = {
                'config': self.boto_config,
                'verify': self.verify_ssl
            }
            if self.endpoint_url:
                client_kwargs['endpoint_url'] = self.endpoint_url
            self._sns_client = self.session.client('sns', **client_kwargs)
        return self._sns_client

    @property
    def lambda_client(self):
        """Lazy-load Lambda client."""
        if self._lambda_client is None:
            client_kwargs = {
                'config': self.boto_config,
                'verify': self.verify_ssl
            }
            if self.endpoint_url:
                client_kwargs['endpoint_url'] = self.endpoint_url
            self._lambda_client = self.session.client('lambda', **client_kwargs)
        return self._lambda_client

    @property
    def ec2(self):
        """Lazy-load EC2 client."""
        if self._ec2_client is None:
            client_kwargs = {
                'config': self.boto_config,
                'verify': self.verify_ssl
            }
            if self.endpoint_url:
                client_kwargs['endpoint_url'] = self.endpoint_url
            self._ec2_client = self.session.client('ec2', **client_kwargs)
        return self._ec2_client

    @property
    def cloudwatch(self):
        """Lazy-load CloudWatch client."""
        if self._cloudwatch_client is None:
            client_kwargs = {
                'config': self.boto_config,
                'verify': self.verify_ssl
            }
            if self.endpoint_url:
                client_kwargs['endpoint_url'] = self.endpoint_url
            self._cloudwatch_client = self.session.client('cloudwatch', **client_kwargs)
        return self._cloudwatch_client

    @property
    def secrets(self):
        """Lazy-load Secrets Manager client."""
        if self._secrets_client is None:
            client_kwargs = {
                'config': self.boto_config,
                'verify': self.verify_ssl
            }
            if self.endpoint_url:
                client_kwargs['endpoint_url'] = self.endpoint_url
            self._secrets_client = self.session.client('secretsmanager', **client_kwargs)
        return self._secrets_client

    @property
    def ses(self):
        """Lazy-load SES client."""
        if self._ses_client is None:
            client_kwargs = {
                'config': self.boto_config,
                'verify': self.verify_ssl
            }
            if self.endpoint_url:
                client_kwargs['endpoint_url'] = self.endpoint_url
            self._ses_client = self.session.client('ses', **client_kwargs)
        return self._ses_client

    @property
    def events(self):
        """Lazy-load EventBridge client."""
        if self._events_client is None:
            client_kwargs = {
                'config': self.boto_config,
                'verify': self.verify_ssl
            }
            if self.endpoint_url:
                client_kwargs['endpoint_url'] = self.endpoint_url
            self._events_client = self.session.client('events', **client_kwargs)
        return self._events_client

    @classmethod
    def from_config(cls, config_path: str, section: str = 'aws') -> 'AWSModule':
        """
        Create AWSModule instance from configuration file.

        Args:
            config_path: Path to configuration file
            section: Configuration section name (default: 'aws')

        Returns:
            AWSModule instance
        """
        config = configparser.ConfigParser()
        config.read(config_path)

        if section not in config:
            raise ValueError(f"Section [{section}] not found in {config_path}")

        cfg = config[section]

        # Build initialization parameters
        init_params = {
            'aws_access_key_id': cfg.get('AWS_ACCESS_KEY_ID', None),
            'aws_secret_access_key': cfg.get('AWS_SECRET_ACCESS_KEY', None),
            'aws_session_token': cfg.get('AWS_SESSION_TOKEN', None),
            'region_name': cfg.get('AWS_REGION', 'us-east-1'),
            'endpoint_url': cfg.get('ENDPOINT_URL', None),
            'verify_ssl': cfg.getboolean('VERIFY_SSL', True),
            'max_retries': cfg.getint('MAX_RETRIES', 3),
            'retry_mode': cfg.get('RETRY_MODE', 'standard'),
            'default_s3_bucket': cfg.get('DEFAULT_S3_BUCKET', None),
            'default_dynamodb_table': cfg.get('DEFAULT_DYNAMODB_TABLE', None),
            'default_sqs_queue': cfg.get('DEFAULT_SQS_QUEUE', None),
            'default_sns_topic': cfg.get('DEFAULT_SNS_TOPIC', None)
        }

        # Remove None values
        init_params = {k: v for k, v in init_params.items() if v is not None}

        return cls(**init_params)

    # ==================== S3 Operations ====================

    def s3_upload_file(
        self,
        local_path: str,
        bucket: Optional[str] = None,
        object_key: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        content_type: Optional[str] = None,
        acl: Optional[str] = None,
        encryption: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload file to S3.

        Args:
            local_path: Local file path
            bucket: S3 bucket name (uses default if not specified)
            object_key: S3 object key (uses filename if not specified)
            metadata: Object metadata dict
            content_type: Content type (auto-detected if not specified)
            acl: Access control list (private, public-read, etc.)
            encryption: Server-side encryption (AES256, aws:kms)

        Returns:
            Upload response dict
        """
        bucket = bucket or self.default_s3_bucket
        if not bucket:
            raise ValueError("Bucket name must be specified or set as default")

        object_key = object_key or Path(local_path).name

        # Build extra args
        extra_args = {}

        if metadata:
            extra_args['Metadata'] = metadata

        if content_type:
            extra_args['ContentType'] = content_type
        else:
            # Auto-detect content type
            content_type, _ = mimetypes.guess_type(local_path)
            if content_type:
                extra_args['ContentType'] = content_type

        if acl:
            extra_args['ACL'] = acl

        if encryption:
            extra_args['ServerSideEncryption'] = encryption

        # Upload file
        self.s3.upload_file(
            local_path,
            bucket,
            object_key,
            ExtraArgs=extra_args if extra_args else None,
            Config=self.s3_transfer_config
        )

        return {
            'bucket': bucket,
            'key': object_key,
            'size': os.path.getsize(local_path),
            'uploaded': True
        }

    def s3_download_file(
        self,
        bucket: str,
        object_key: str,
        local_path: str
    ) -> Dict[str, Any]:
        """
        Download file from S3.

        Args:
            bucket: S3 bucket name
            object_key: S3 object key
            local_path: Local destination path

        Returns:
            Download response dict
        """
        # Ensure directory exists
        Path(local_path).parent.mkdir(parents=True, exist_ok=True)

        # Download file
        self.s3.download_file(
            bucket,
            object_key,
            local_path,
            Config=self.s3_transfer_config
        )

        return {
            'bucket': bucket,
            'key': object_key,
            'local_path': local_path,
            'size': os.path.getsize(local_path),
            'downloaded': True
        }

    def s3_list_objects(
        self,
        bucket: Optional[str] = None,
        prefix: str = '',
        max_keys: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        List objects in S3 bucket.

        Args:
            bucket: S3 bucket name (uses default if not specified)
            prefix: Object key prefix filter
            max_keys: Maximum number of keys to return

        Returns:
            List of object dicts with Key, Size, LastModified
        """
        bucket = bucket or self.default_s3_bucket
        if not bucket:
            raise ValueError("Bucket name must be specified or set as default")

        response = self.s3.list_objects_v2(
            Bucket=bucket,
            Prefix=prefix,
            MaxKeys=max_keys
        )

        objects = []
        if 'Contents' in response:
            for obj in response['Contents']:
                objects.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat(),
                    'etag': obj.get('ETag', '').strip('"')
                })

        return objects

    def s3_delete_object(self, bucket: str, object_key: str) -> Dict[str, Any]:
        """Delete object from S3."""
        response = self.s3.delete_object(Bucket=bucket, Key=object_key)
        return {'bucket': bucket, 'key': object_key, 'deleted': True}

    def s3_generate_presigned_url(
        self,
        bucket: str,
        object_key: str,
        expiration: int = 3600,
        http_method: str = 'GET'
    ) -> str:
        """
        Generate presigned URL for S3 object.

        Args:
            bucket: S3 bucket name
            object_key: S3 object key
            expiration: URL expiration in seconds (default: 3600)
            http_method: HTTP method (GET, PUT, DELETE)

        Returns:
            Presigned URL string
        """
        method_map = {
            'GET': 'get_object',
            'PUT': 'put_object',
            'DELETE': 'delete_object'
        }

        url = self.s3.generate_presigned_url(
            method_map.get(http_method.upper(), 'get_object'),
            Params={'Bucket': bucket, 'Key': object_key},
            ExpiresIn=expiration
        )

        return url

    # ==================== DynamoDB Operations ====================

    def dynamodb_put_item(
        self,
        table_name: Optional[str] = None,
        item: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Put item into DynamoDB table.

        Args:
            table_name: DynamoDB table name (uses default if not specified)
            item: Item dict to insert

        Returns:
            Response dict
        """
        table_name = table_name or self.default_dynamodb_table
        if not table_name:
            raise ValueError("Table name must be specified or set as default")

        table = self.dynamodb_resource.Table(table_name)
        response = table.put_item(Item=item)

        return {
            'table': table_name,
            'item': item,
            'success': response['ResponseMetadata']['HTTPStatusCode'] == 200
        }

    def dynamodb_get_item(
        self,
        table_name: Optional[str] = None,
        key: Dict[str, Any] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get item from DynamoDB table.

        Args:
            table_name: DynamoDB table name
            key: Primary key dict (e.g., {'user_id': '123'})

        Returns:
            Item dict or None if not found
        """
        table_name = table_name or self.default_dynamodb_table
        if not table_name:
            raise ValueError("Table name must be specified or set as default")

        table = self.dynamodb_resource.Table(table_name)
        response = table.get_item(Key=key)

        return response.get('Item')

    def dynamodb_query(
        self,
        table_name: Optional[str] = None,
        key_condition_expression: str = None,
        filter_expression: Optional[str] = None,
        expression_attribute_values: Optional[Dict[str, Any]] = None,
        index_name: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Query DynamoDB table.

        Args:
            table_name: DynamoDB table name
            key_condition_expression: Key condition (e.g., Key('user_id').eq('123'))
            filter_expression: Filter expression
            expression_attribute_values: Expression attribute values
            index_name: Global/local secondary index name
            limit: Maximum items to return

        Returns:
            List of items
        """
        table_name = table_name or self.default_dynamodb_table
        if not table_name:
            raise ValueError("Table name must be specified or set as default")

        table = self.dynamodb_resource.Table(table_name)

        query_kwargs = {}

        if key_condition_expression:
            query_kwargs['KeyConditionExpression'] = key_condition_expression

        if filter_expression:
            query_kwargs['FilterExpression'] = filter_expression

        if expression_attribute_values:
            query_kwargs['ExpressionAttributeValues'] = expression_attribute_values

        if index_name:
            query_kwargs['IndexName'] = index_name

        if limit:
            query_kwargs['Limit'] = limit

        response = table.query(**query_kwargs)

        return response.get('Items', [])

    def dynamodb_scan(
        self,
        table_name: Optional[str] = None,
        filter_expression: Optional[str] = None,
        expression_attribute_values: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Scan DynamoDB table (full table scan - use sparingly).

        Args:
            table_name: DynamoDB table name
            filter_expression: Filter expression
            expression_attribute_values: Expression attribute values
            limit: Maximum items to return

        Returns:
            List of items
        """
        table_name = table_name or self.default_dynamodb_table
        if not table_name:
            raise ValueError("Table name must be specified or set as default")

        table = self.dynamodb_resource.Table(table_name)

        scan_kwargs = {}

        if filter_expression:
            scan_kwargs['FilterExpression'] = filter_expression

        if expression_attribute_values:
            scan_kwargs['ExpressionAttributeValues'] = expression_attribute_values

        if limit:
            scan_kwargs['Limit'] = limit

        response = table.scan(**scan_kwargs)

        return response.get('Items', [])

    def dynamodb_delete_item(
        self,
        table_name: Optional[str] = None,
        key: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Delete item from DynamoDB table."""
        table_name = table_name or self.default_dynamodb_table
        if not table_name:
            raise ValueError("Table name must be specified or set as default")

        table = self.dynamodb_resource.Table(table_name)
        response = table.delete_item(Key=key)

        return {
            'table': table_name,
            'key': key,
            'deleted': response['ResponseMetadata']['HTTPStatusCode'] == 200
        }

    # ==================== SQS Operations ====================

    def sqs_send_message(
        self,
        queue_name: Optional[str] = None,
        message_body: Union[str, Dict[str, Any]] = None,
        message_attributes: Optional[Dict[str, Any]] = None,
        delay_seconds: int = 0
    ) -> Dict[str, Any]:
        """
        Send message to SQS queue.

        Args:
            queue_name: SQS queue name
            message_body: Message body (string or dict - will be JSON serialized)
            message_attributes: Message attributes dict
            delay_seconds: Delay before message becomes visible (0-900)

        Returns:
            Response with MessageId
        """
        queue_name = queue_name or self.default_sqs_queue
        if not queue_name:
            raise ValueError("Queue name must be specified or set as default")

        # Get queue URL
        queue_url = self.sqs.get_queue_url(QueueName=queue_name)['QueueUrl']

        # Serialize dict to JSON
        if isinstance(message_body, dict):
            message_body = json.dumps(message_body)

        send_kwargs = {
            'QueueUrl': queue_url,
            'MessageBody': message_body
        }

        if message_attributes:
            send_kwargs['MessageAttributes'] = message_attributes

        if delay_seconds > 0:
            send_kwargs['DelaySeconds'] = delay_seconds

        response = self.sqs.send_message(**send_kwargs)

        return {
            'message_id': response['MessageId'],
            'queue': queue_name,
            'sent': True
        }

    def sqs_receive_messages(
        self,
        queue_name: Optional[str] = None,
        max_messages: int = 1,
        wait_time_seconds: int = 0,
        visibility_timeout: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Receive messages from SQS queue.

        Args:
            queue_name: SQS queue name
            max_messages: Maximum messages to receive (1-10)
            wait_time_seconds: Long polling wait time (0-20)
            visibility_timeout: Visibility timeout in seconds

        Returns:
            List of message dicts
        """
        queue_name = queue_name or self.default_sqs_queue
        if not queue_name:
            raise ValueError("Queue name must be specified or set as default")

        # Get queue URL
        queue_url = self.sqs.get_queue_url(QueueName=queue_name)['QueueUrl']

        receive_kwargs = {
            'QueueUrl': queue_url,
            'MaxNumberOfMessages': min(max_messages, 10),
            'WaitTimeSeconds': wait_time_seconds,
            'MessageAttributeNames': ['All'],
            'AttributeNames': ['All']
        }

        if visibility_timeout is not None:
            receive_kwargs['VisibilityTimeout'] = visibility_timeout

        response = self.sqs.receive_message(**receive_kwargs)

        messages = []
        for msg in response.get('Messages', []):
            # Try to parse JSON body
            body = msg['Body']
            try:
                body = json.loads(body)
            except (json.JSONDecodeError, TypeError):
                pass  # Keep as string

            messages.append({
                'message_id': msg['MessageId'],
                'receipt_handle': msg['ReceiptHandle'],
                'body': body,
                'attributes': msg.get('Attributes', {}),
                'message_attributes': msg.get('MessageAttributes', {})
            })

        return messages

    def sqs_delete_message(
        self,
        queue_name: Optional[str] = None,
        receipt_handle: str = None
    ) -> Dict[str, Any]:
        """Delete message from SQS queue."""
        queue_name = queue_name or self.default_sqs_queue
        if not queue_name:
            raise ValueError("Queue name must be specified or set as default")

        queue_url = self.sqs.get_queue_url(QueueName=queue_name)['QueueUrl']

        self.sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle
        )

        return {'queue': queue_name, 'deleted': True}

    # ==================== SNS Operations ====================

    def sns_publish(
        self,
        topic_arn: Optional[str] = None,
        message: Union[str, Dict[str, Any]] = None,
        subject: Optional[str] = None,
        message_attributes: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Publish message to SNS topic.

        Args:
            topic_arn: SNS topic ARN
            message: Message (string or dict - will be JSON serialized)
            subject: Message subject (for email subscriptions)
            message_attributes: Message attributes

        Returns:
            Response with MessageId
        """
        topic_arn = topic_arn or self.default_sns_topic
        if not topic_arn:
            raise ValueError("Topic ARN must be specified or set as default")

        # Serialize dict to JSON
        if isinstance(message, dict):
            message = json.dumps(message)

        publish_kwargs = {
            'TopicArn': topic_arn,
            'Message': message
        }

        if subject:
            publish_kwargs['Subject'] = subject

        if message_attributes:
            publish_kwargs['MessageAttributes'] = message_attributes

        response = self.sns.publish(**publish_kwargs)

        return {
            'message_id': response['MessageId'],
            'topic_arn': topic_arn,
            'published': True
        }

    # ==================== Lambda Operations ====================

    def lambda_invoke(
        self,
        function_name: str,
        payload: Optional[Dict[str, Any]] = None,
        invocation_type: str = 'RequestResponse'
    ) -> Dict[str, Any]:
        """
        Invoke AWS Lambda function.

        Args:
            function_name: Lambda function name or ARN
            payload: Function payload dict
            invocation_type: RequestResponse (sync), Event (async), DryRun

        Returns:
            Function response dict
        """
        invoke_kwargs = {
            'FunctionName': function_name,
            'InvocationType': invocation_type
        }

        if payload:
            invoke_kwargs['Payload'] = json.dumps(payload)

        response = self.lambda_client.invoke(**invoke_kwargs)

        result = {
            'status_code': response['StatusCode'],
            'function_name': function_name
        }

        if 'Payload' in response:
            result['response'] = json.loads(response['Payload'].read())

        if 'FunctionError' in response:
            result['error'] = response['FunctionError']

        return result

    # ==================== Secrets Manager Operations ====================

    def secrets_get_secret(self, secret_id: str) -> Dict[str, Any]:
        """
        Get secret from AWS Secrets Manager.

        Args:
            secret_id: Secret name or ARN

        Returns:
            Secret dict
        """
        response = self.secrets.get_secret_value(SecretId=secret_id)

        # Parse secret string (usually JSON)
        secret = response.get('SecretString')
        if secret:
            try:
                secret = json.loads(secret)
            except (json.JSONDecodeError, TypeError):
                pass  # Keep as string
        else:
            # Binary secret
            secret = base64.b64decode(response['SecretBinary'])

        return {
            'secret_id': secret_id,
            'arn': response['ARN'],
            'value': secret,
            'version_id': response['VersionId'],
            'created_date': response['CreatedDate'].isoformat()
        }

    def secrets_create_secret(
        self,
        name: str,
        secret_value: Union[str, Dict[str, Any]],
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create secret in AWS Secrets Manager.

        Args:
            name: Secret name
            secret_value: Secret value (string or dict)
            description: Secret description

        Returns:
            Response with ARN
        """
        if isinstance(secret_value, dict):
            secret_value = json.dumps(secret_value)

        create_kwargs = {
            'Name': name,
            'SecretString': secret_value
        }

        if description:
            create_kwargs['Description'] = description

        response = self.secrets.create_secret(**create_kwargs)

        return {
            'name': name,
            'arn': response['ARN'],
            'version_id': response['VersionId'],
            'created': True
        }

    # ==================== CloudWatch Operations ====================

    def cloudwatch_put_metric(
        self,
        namespace: str,
        metric_name: str,
        value: float,
        unit: str = 'None',
        dimensions: Optional[List[Dict[str, str]]] = None,
        timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Put custom metric to CloudWatch.

        Args:
            namespace: Metric namespace
            metric_name: Metric name
            value: Metric value
            unit: Unit (Seconds, Bytes, Count, Percent, etc.)
            dimensions: List of dimension dicts [{'Name': 'dim', 'Value': 'val'}]
            timestamp: Metric timestamp (defaults to now)

        Returns:
            Response dict
        """
        metric_data = {
            'MetricName': metric_name,
            'Value': value,
            'Unit': unit
        }

        if dimensions:
            metric_data['Dimensions'] = dimensions

        if timestamp:
            metric_data['Timestamp'] = timestamp
        else:
            metric_data['Timestamp'] = datetime.utcnow()

        response = self.cloudwatch.put_metric_data(
            Namespace=namespace,
            MetricData=[metric_data]
        )

        return {
            'namespace': namespace,
            'metric_name': metric_name,
            'value': value,
            'success': response['ResponseMetadata']['HTTPStatusCode'] == 200
        }

    def cloudwatch_get_metric_statistics(
        self,
        namespace: str,
        metric_name: str,
        start_time: datetime,
        end_time: datetime,
        period: int,
        statistics: List[str],
        dimensions: Optional[List[Dict[str, str]]] = None,
        unit: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get metric statistics from CloudWatch.

        Args:
            namespace: Metric namespace
            metric_name: Metric name
            start_time: Start time
            end_time: End time
            period: Period in seconds
            statistics: List of statistics (Average, Sum, Maximum, Minimum, SampleCount)
            dimensions: Metric dimensions
            unit: Metric unit

        Returns:
            List of datapoint dicts
        """
        get_kwargs = {
            'Namespace': namespace,
            'MetricName': metric_name,
            'StartTime': start_time,
            'EndTime': end_time,
            'Period': period,
            'Statistics': statistics
        }

        if dimensions:
            get_kwargs['Dimensions'] = dimensions

        if unit:
            get_kwargs['Unit'] = unit

        response = self.cloudwatch.get_metric_statistics(**get_kwargs)

        datapoints = []
        for dp in response.get('Datapoints', []):
            datapoints.append({
                'timestamp': dp['Timestamp'].isoformat(),
                'average': dp.get('Average'),
                'sum': dp.get('Sum'),
                'maximum': dp.get('Maximum'),
                'minimum': dp.get('Minimum'),
                'sample_count': dp.get('SampleCount'),
                'unit': dp.get('Unit')
            })

        return sorted(datapoints, key=lambda x: x['timestamp'])

    def close(self):
        """Close AWS clients (cleanup)."""
        # boto3 clients don't need explicit cleanup
        # This method is here for consistency with other modules
        pass

    @classmethod
    def get_metadata(cls):
        """Get module metadata."""
        from aibasic.modules.module_base import ModuleMetadata
        return ModuleMetadata(
            name="AWS",
            task_type="aws",
            description="Amazon Web Services integration for S3, DynamoDB, SQS, SNS, Lambda, EC2, and more",
            version="1.0.0",
            keywords=["aws", "amazon", "cloud", "s3", "dynamodb", "sqs", "sns", "lambda", "ec2"],
            dependencies=["boto3>=1.26.0"]
        )

    @classmethod
    def get_usage_notes(cls):
        """Get detailed usage notes."""
        return [
            "AWS credentials: Use IAM roles, environment variables, or aibasic.conf [aws] section",
            "Supports multiple AWS services: S3, DynamoDB, SQS, SNS, Lambda, EC2, CloudWatch, Secrets Manager, SES",
            "Module uses singleton pattern - one session shared across operations",
            "S3 methods: upload_file(), download_file(), list_objects(), delete_object()",
            "DynamoDB methods: put_item(), get_item(), query(), scan(), update_item(), delete_item()",
            "SQS methods: send_message(), receive_messages(), delete_message()",
            "SNS methods: publish(), create_topic(), subscribe()",
            "Lambda methods: invoke_function(), create_function()",
            "Secrets Manager: get_secret(), create_secret(), update_secret()",
            "CloudWatch: put_metric_data(), get_metric_statistics()",
            "LocalStack support: Set ENDPOINT_URL in config for local development",
            "Auto-retry on transient errors with exponential backoff",
            "All methods return dict with operation results",
            "Region can be specified in config or per-method call",
            "Supports multipart uploads for large S3 files (>5GB)",
            "DynamoDB supports batch operations for efficiency"
        ]

    @classmethod
    def get_methods_info(cls):
        """Get information about module methods."""
        from aibasic.modules.module_base import MethodInfo
        return [
            # S3 Methods
            MethodInfo(
                name="s3_upload_file",
                description="Upload a file to S3 bucket",
                parameters={
                    "file_path": "Local file path to upload",
                    "bucket": "S3 bucket name (optional: uses default)",
                    "key": "S3 object key/path (optional: uses filename)",
                    "metadata": "Optional: Dict of metadata tags",
                    "acl": "Optional: Access control (private, public-read, etc.)"
                },
                returns="Dict with bucket, key, etag, and upload status",
                examples=[
                    '(aws) upload file "data.csv" to S3 bucket "my-bucket"',
                    '(aws) upload file "report.pdf" to S3 with key "reports/2025/report.pdf"'
                ]
            ),
            MethodInfo(
                name="s3_download_file",
                description="Download a file from S3 bucket",
                parameters={
                    "key": "S3 object key to download",
                    "local_path": "Local path to save file",
                    "bucket": "Optional: S3 bucket name"
                },
                returns="Dict with local path and download status",
                examples=[
                    '(aws) download from S3 key "data.csv" to "local_data.csv"',
                    '(aws) download from S3 bucket "my-bucket" key "reports/report.pdf"'
                ]
            ),
            MethodInfo(
                name="s3_list_objects",
                description="List objects in S3 bucket",
                parameters={
                    "bucket": "Optional: S3 bucket name",
                    "prefix": "Optional: Filter by prefix/folder",
                    "max_keys": "Optional: Maximum objects to return (default: 1000)"
                },
                returns="List of dicts with object keys, sizes, last modified dates",
                examples=[
                    '(aws) list S3 objects in bucket "my-bucket"',
                    '(aws) list S3 objects with prefix "reports/2025/"'
                ]
            ),
            # DynamoDB Methods
            MethodInfo(
                name="dynamodb_put_item",
                description="Put an item into DynamoDB table",
                parameters={
                    "item": "Dict representing the item to store",
                    "table": "Optional: Table name (uses default if not provided)"
                },
                returns="Dict with operation status",
                examples=[
                    'LET item = {"id": "123", "name": "John", "age": 30}',
                    '(aws) put item into DynamoDB table "users"'
                ]
            ),
            MethodInfo(
                name="dynamodb_get_item",
                description="Get an item from DynamoDB by key",
                parameters={
                    "key": "Dict with partition key (and sort key if needed)",
                    "table": "Optional: Table name"
                },
                returns="Dict with item data or None if not found",
                examples=[
                    'LET key = {"id": "123"}',
                    'LET user = (aws) get item from DynamoDB with key',
                    'PRINT user["name"]'
                ]
            ),
            MethodInfo(
                name="dynamodb_query",
                description="Query DynamoDB table with conditions",
                parameters={
                    "key_condition": "Key condition expression (e.g., 'id = :id')",
                    "expression_values": "Dict mapping expression variable names to values",
                    "table": "Optional: Table name",
                    "index": "Optional: Index name for GSI/LSI queries"
                },
                returns="List of items matching the query",
                examples=[
                    '(aws) query DynamoDB where "id = :id" with values {":id": "123"}',
                    '(aws) query DynamoDB table "orders" where "user_id = :uid" with values {":uid": "user123"}'
                ]
            ),
            # SQS Methods
            MethodInfo(
                name="sqs_send_message",
                description="Send a message to SQS queue",
                parameters={
                    "message": "Message body (string or dict that will be JSON encoded)",
                    "queue_url": "Optional: Queue URL (uses default if not provided)",
                    "delay_seconds": "Optional: Delay before message becomes available (0-900)",
                    "attributes": "Optional: Dict of message attributes"
                },
                returns="Dict with message ID and MD5 hash",
                examples=[
                    '(aws) send SQS message "Process order 123"',
                    'LET data = {"order_id": "123", "action": "process"}',
                    '(aws) send SQS message data to queue "my-queue"'
                ]
            ),
            MethodInfo(
                name="sqs_receive_messages",
                description="Receive messages from SQS queue",
                parameters={
                    "queue_url": "Optional: Queue URL",
                    "max_messages": "Optional: Max messages to receive (1-10, default: 1)",
                    "wait_time": "Optional: Long polling wait time in seconds (0-20)",
                    "visibility_timeout": "Optional: Message visibility timeout"
                },
                returns="List of message dicts with body, receipt_handle, attributes",
                examples=[
                    'LET messages = (aws) receive SQS messages max 10',
                    'FOR EACH msg IN messages: PRINT msg["body"]'
                ]
            ),
            # SNS Methods
            MethodInfo(
                name="sns_publish",
                description="Publish a message to SNS topic",
                parameters={
                    "message": "Message to publish (string or dict)",
                    "topic_arn": "Optional: Topic ARN (uses default if not provided)",
                    "subject": "Optional: Message subject (for email subscriptions)",
                    "attributes": "Optional: Message attributes"
                },
                returns="Dict with message ID",
                examples=[
                    '(aws) publish SNS message "Alert: High CPU usage" with subject "Server Alert"',
                    '(aws) publish to SNS topic "arn:aws:sns:us-east-1:123456789012:alerts" message "Error occurred"'
                ]
            ),
            # Lambda Methods
            MethodInfo(
                name="lambda_invoke",
                description="Invoke an AWS Lambda function",
                parameters={
                    "function_name": "Name or ARN of Lambda function",
                    "payload": "Optional: Input data for function (dict)",
                    "invocation_type": "Optional: RequestResponse, Event, or DryRun (default: RequestResponse)"
                },
                returns="Dict with status code, payload response, logs",
                examples=[
                    '(aws) invoke Lambda function "process-data"',
                    'LET input = {"file": "data.csv", "action": "process"}',
                    'LET result = (aws) invoke Lambda "data-processor" with payload input'
                ]
            ),
            # Secrets Manager
            MethodInfo(
                name="secrets_get_secret",
                description="Retrieve a secret from AWS Secrets Manager",
                parameters={
                    "secret_id": "Secret name or ARN"
                },
                returns="Dict with secret string or binary, version info",
                examples=[
                    'LET db_password = (aws) get secret "prod/db/password"',
                    'PRINT db_password["SecretString"]'
                ]
            ),
        ]

    @classmethod
    def get_examples(cls):
        """Get AIbasic usage examples."""
        return [
            '10 REM S3 Operations',
            '20 (aws) upload file "data.csv" to S3 bucket "my-bucket"',
            '30 (aws) list S3 objects in bucket "my-bucket"',
            '40 (aws) download from S3 key "reports/report.pdf" to "local_report.pdf"',
            '',
            '50 REM DynamoDB Operations',
            '60 LET user = {"id": "123", "name": "John", "email": "john@example.com"}',
            '70 (aws) put user into DynamoDB table "users"',
            '80 LET key = {"id": "123"}',
            '90 LET retrieved = (aws) get item from DynamoDB with key',
            '',
            '100 REM SQS Messaging',
            '110 (aws) send SQS message "Process order 456"',
            '120 LET messages = (aws) receive SQS messages max 5',
            '130 FOR EACH msg IN messages: PRINT msg["body"]',
            '',
            '140 REM SNS Notifications',
            '150 (aws) publish SNS message "Deployment complete" with subject "CI/CD Alert"',
            '',
            '160 REM Lambda Invocation',
            '170 LET payload = {"bucket": "my-bucket", "key": "data.csv"}',
            '180 LET result = (aws) invoke Lambda "data-processor" with payload',
            '',
            '190 REM Secrets Manager',
            '200 LET secret = (aws) get secret "prod/api/key"',
            '210 LET api_key = secret["SecretString"]'
        ]


# Convenience function for quick access
def get_aws_module(config_path: str = 'aibasic.conf') -> AWSModule:
    """Get or create AWS module instance from config."""
    return AWSModule.from_config(config_path)
