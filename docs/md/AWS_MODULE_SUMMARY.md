# AWS Module Summary

## Overview

The AWS Module provides comprehensive integration with Amazon Web Services, offering access to multiple AWS services through a unified Python interface. It supports both production AWS environments and local development using LocalStack.

**Module:** `aibasic.modules.AWSModule`
**Task Type:** `(aws)`
**Dependencies:** `boto3>=1.26.0`

## Supported AWS Services

- **S3** - Simple Storage Service (object storage)
- **DynamoDB** - NoSQL database
- **SQS** - Simple Queue Service (message queuing)
- **SNS** - Simple Notification Service (pub/sub)
- **Lambda** - Serverless compute
- **Secrets Manager** - Secure credential storage
- **CloudWatch** - Monitoring and logging
- **SES** - Simple Email Service
- **EventBridge** - Event bus
- **EC2** - Elastic Compute Cloud (future expansion)

## Configuration

### Production AWS Configuration

```ini
[aws]
# AWS Credentials
AWS_ACCESS_KEY_ID = AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_REGION = us-east-1

# Optional: Session Token (for temporary credentials)
# AWS_SESSION_TOKEN = your_session_token

# Default Resources
DEFAULT_S3_BUCKET = my-bucket
DEFAULT_DYNAMODB_TABLE = my-table
DEFAULT_SQS_QUEUE = my-queue
DEFAULT_SNS_TOPIC = arn:aws:sns:us-east-1:123456789012:my-topic

# Retry Configuration
MAX_RETRIES = 3
RETRY_MODE = standard
```

### LocalStack Configuration (Development)

```ini
[aws]
AWS_ACCESS_KEY_ID = test
AWS_SECRET_ACCESS_KEY = test
AWS_REGION = us-east-1
ENDPOINT_URL = http://localhost:4566
VERIFY_SSL = false

DEFAULT_S3_BUCKET = aibasic-bucket
DEFAULT_DYNAMODB_TABLE = users
DEFAULT_SQS_QUEUE = aibasic-queue
DEFAULT_SNS_TOPIC = arn:aws:sns:us-east-1:000000000000:aibasic-notifications
```

## API Reference

### Module Initialization

```python
from aibasic.modules import AWSModule

# From config file
aws = AWSModule.from_config('aibasic.conf')

# Programmatic initialization
aws = AWSModule(
    aws_access_key_id='YOUR_KEY',
    aws_secret_access_key='YOUR_SECRET',
    region_name='us-east-1',
    default_s3_bucket='my-bucket'
)
```

### S3 Operations

#### Upload File
```python
aws.s3_upload_file(
    local_path='data.csv',
    bucket='my-bucket',
    object_key='uploads/data.csv',
    metadata={'uploaded_by': 'aibasic'},
    encryption='AES256'
)
```

#### Download File
```python
aws.s3_download_file(
    bucket='my-bucket',
    object_key='uploads/data.csv',
    local_path='downloaded.csv'
)
```

#### List Objects
```python
objects = aws.s3_list_objects(
    bucket='my-bucket',
    prefix='uploads/',
    max_keys=1000
)
```

#### Generate Presigned URL
```python
url = aws.s3_generate_presigned_url(
    bucket='my-bucket',
    object_key='data.csv',
    expiration=3600,  # 1 hour
    http_method='GET'
)
```

#### Delete Object
```python
aws.s3_delete_object(
    bucket='my-bucket',
    object_key='old-file.csv'
)
```

### DynamoDB Operations

#### Put Item
```python
aws.dynamodb_put_item(
    table_name='users',
    item={
        'user_id': '123',
        'name': 'Alice',
        'email': 'alice@example.com',
        'age': 30
    }
)
```

#### Get Item
```python
item = aws.dynamodb_get_item(
    table_name='users',
    key={'user_id': '123'}
)
```

#### Query Table
```python
from boto3.dynamodb.conditions import Key

items = aws.dynamodb_query(
    table_name='users',
    key_condition_expression=Key('user_id').eq('123')
)
```

#### Scan Table
```python
from boto3.dynamodb.conditions import Attr

items = aws.dynamodb_scan(
    table_name='users',
    filter_expression=Attr('age').gt(25),
    limit=100
)
```

#### Delete Item
```python
aws.dynamodb_delete_item(
    table_name='users',
    key={'user_id': '123'}
)
```

### SQS Operations

#### Send Message
```python
aws.sqs_send_message(
    queue_name='orders-queue',
    message_body={
        'order_id': 'ORD-456',
        'customer': 'Alice',
        'amount': 99.99
    },
    delay_seconds=0
)
```

#### Receive Messages
```python
messages = aws.sqs_receive_messages(
    queue_name='orders-queue',
    max_messages=10,
    wait_time_seconds=5,  # Long polling
    visibility_timeout=30
)

for msg in messages:
    print(f"Message: {msg['body']}")
    # Process message...
    aws.sqs_delete_message(
        queue_name='orders-queue',
        receipt_handle=msg['receipt_handle']
    )
```

### SNS Operations

#### Publish Message
```python
aws.sns_publish(
    topic_arn='arn:aws:sns:us-east-1:123456789012:notifications',
    message='System alert: High CPU usage',
    subject='Alert'
)
```

#### Publish JSON Message
```python
aws.sns_publish(
    topic_arn='arn:aws:sns:us-east-1:123456789012:events',
    message={
        'event': 'order_created',
        'order_id': 'ORD-789',
        'timestamp': '2025-01-15T10:30:00Z'
    }
)
```

### Lambda Operations

#### Invoke Function (Synchronous)
```python
response = aws.lambda_invoke(
    function_name='my-data-processor',
    payload={
        'input_file': 'data.csv',
        'output_format': 'json'
    },
    invocation_type='RequestResponse'
)

print(response['response'])
```

#### Invoke Function (Asynchronous)
```python
aws.lambda_invoke(
    function_name='send-notification',
    payload={'to': 'user@example.com'},
    invocation_type='Event'
)
```

### Secrets Manager Operations

#### Get Secret
```python
secret = aws.secrets_get_secret('database/prod/credentials')
db_password = secret['value']['password']
```

#### Create Secret
```python
aws.secrets_create_secret(
    name='api/production/key',
    secret_value={
        'api_key': 'sk-abc123',
        'api_secret': 'secret456'
    },
    description='Production API credentials'
)
```

### CloudWatch Operations

#### Put Metric
```python
aws.cloudwatch_put_metric(
    namespace='MyApp/Orders',
    metric_name='OrderCount',
    value=150,
    unit='Count',
    dimensions=[
        {'Name': 'Environment', 'Value': 'Production'}
    ]
)
```

#### Get Metric Statistics
```python
from datetime import datetime, timedelta

datapoints = aws.cloudwatch_get_metric_statistics(
    namespace='MyApp/Orders',
    metric_name='OrderCount',
    start_time=datetime.utcnow() - timedelta(hours=1),
    end_time=datetime.utcnow(),
    period=300,  # 5 minutes
    statistics=['Average', 'Sum', 'Maximum']
)
```

## Usage Examples

### Example 1: S3 File Processing Pipeline

```python
from aibasic.modules import AWSModule

aws = AWSModule.from_config('aibasic.conf')

# Upload file to S3
aws.s3_upload_file(
    local_path='data.csv',
    bucket='data-bucket',
    object_key='incoming/data.csv'
)

# Trigger Lambda to process file
response = aws.lambda_invoke(
    function_name='process-csv',
    payload={
        's3_bucket': 'data-bucket',
        's3_key': 'incoming/data.csv'
    }
)

print(f"Processing result: {response['response']}")
```

### Example 2: DynamoDB CRUD Operations

```python
# Create user
aws.dynamodb_put_item(
    table_name='users',
    item={
        'user_id': 'U001',
        'name': 'Alice',
        'email': 'alice@example.com',
        'created_at': '2025-01-15T10:00:00Z'
    }
)

# Read user
user = aws.dynamodb_get_item(
    table_name='users',
    key={'user_id': 'U001'}
)

# Update user (put with same key)
aws.dynamodb_put_item(
    table_name='users',
    item={
        'user_id': 'U001',
        'name': 'Alice Smith',
        'email': 'alice.smith@example.com',
        'updated_at': '2025-01-15T11:00:00Z'
    }
)

# Delete user
aws.dynamodb_delete_item(
    table_name='users',
    key={'user_id': 'U001'}
)
```

### Example 3: SQS Message Queue Processing

```python
# Send message to queue
aws.sqs_send_message(
    queue_name='tasks-queue',
    message_body={
        'task_id': 'T001',
        'type': 'data_processing',
        'priority': 'high'
    }
)

# Process messages
while True:
    messages = aws.sqs_receive_messages(
        queue_name='tasks-queue',
        max_messages=10,
        wait_time_seconds=20  # Long polling
    )

    if not messages:
        break

    for msg in messages:
        try:
            # Process message
            process_task(msg['body'])

            # Delete after successful processing
            aws.sqs_delete_message(
                queue_name='tasks-queue',
                receipt_handle=msg['receipt_handle']
            )
        except Exception as e:
            print(f"Error processing message: {e}")
            # Message will become visible again after timeout
```

### Example 4: Event-Driven Architecture

```python
# Send event to SNS topic
aws.sns_publish(
    topic_arn='arn:aws:sns:us-east-1:123456789012:events',
    message={
        'event_type': 'user_signup',
        'user_id': 'U789',
        'timestamp': '2025-01-15T12:00:00Z'
    }
)

# SNS will fan out to multiple subscribers:
# - SQS queue for async processing
# - Lambda function for real-time processing
# - Email notification to admin
```

### Example 5: Secure Configuration Management

```python
# Store database credentials securely
aws.secrets_create_secret(
    name='database/prod/master',
    secret_value={
        'username': 'admin',
        'password': 'SuperSecret123!',
        'host': 'db.example.com',
        'port': 5432
    }
)

# Retrieve credentials in application
secret = aws.secrets_get_secret('database/prod/master')
db_config = secret['value']

# Connect to database using retrieved credentials
# (use with PostgreSQL module, etc.)
```

### Example 6: CloudWatch Monitoring

```python
import time

# Send custom metrics
for i in range(10):
    aws.cloudwatch_put_metric(
        namespace='MyApp/Performance',
        metric_name='ResponseTime',
        value=245 + i * 10,
        unit='Milliseconds'
    )
    time.sleep(1)

# Query metrics
from datetime import datetime, timedelta

stats = aws.cloudwatch_get_metric_statistics(
    namespace='MyApp/Performance',
    metric_name='ResponseTime',
    start_time=datetime.utcnow() - timedelta(minutes=5),
    end_time=datetime.utcnow(),
    period=60,
    statistics=['Average', 'Maximum', 'Minimum']
)

for point in stats:
    print(f"Time: {point['timestamp']}, Avg: {point['average']}ms")
```

### Example 7: Complete Order Processing Workflow

```python
# 1. Receive order from SQS
messages = aws.sqs_receive_messages(
    queue_name='orders-queue',
    max_messages=1
)

if messages:
    order = messages[0]['body']

    # 2. Store order in DynamoDB
    aws.dynamodb_put_item(
        table_name='orders',
        item=order
    )

    # 3. Archive order to S3
    import json
    order_json = json.dumps(order)
    aws.s3_upload_file(
        local_path='/tmp/order.json',
        bucket='order-archive',
        object_key=f"orders/{order['order_id']}.json"
    )

    # 4. Send notification via SNS
    aws.sns_publish(
        topic_arn='arn:aws:sns:us-east-1:123456789012:orders',
        message=f"Order {order['order_id']} processed",
        subject='Order Confirmation'
    )

    # 5. Log metric to CloudWatch
    aws.cloudwatch_put_metric(
        namespace='MyApp/Orders',
        metric_name='OrdersProcessed',
        value=1,
        unit='Count'
    )

    # 6. Delete message from queue
    aws.sqs_delete_message(
        queue_name='orders-queue',
        receipt_handle=messages[0]['receipt_handle']
    )
```

### Example 8: Lambda Data Processing

```python
# Upload source data
aws.s3_upload_file(
    local_path='raw_data.csv',
    bucket='data-pipeline',
    object_key='raw/data.csv'
)

# Invoke Lambda for ETL
response = aws.lambda_invoke(
    function_name='etl-processor',
    payload={
        'source_bucket': 'data-pipeline',
        'source_key': 'raw/data.csv',
        'target_bucket': 'data-pipeline',
        'target_key': 'processed/data.parquet',
        'format': 'parquet'
    }
)

# Check processing result
if response['status_code'] == 200:
    result = response['response']
    print(f"Processed {result['records_processed']} records")
else:
    print(f"Error: {response.get('error')}")
```

## Best Practices

### 1. Credential Management

**DO:**
- Use IAM roles when running on EC2/ECS/Lambda
- Use environment variables for CI/CD pipelines
- Store credentials in Secrets Manager or Parameter Store
- Use temporary credentials (STS) when possible
- Enable MFA for production accounts

**DON'T:**
- Hardcode credentials in code
- Commit credentials to version control
- Share credentials across teams
- Use root account credentials

### 2. S3 Best Practices

- Use server-side encryption (SSE-S3 or SSE-KMS)
- Enable versioning for critical data
- Implement lifecycle policies for cost optimization
- Use multipart upload for large files (>100MB)
- Set appropriate bucket policies and ACLs
- Enable CloudTrail for audit logging

### 3. DynamoDB Best Practices

- Design partition keys to distribute load evenly
- Use sort keys for efficient queries
- Implement Global Secondary Indexes (GSI) for additional query patterns
- Use batch operations for multiple items
- Enable point-in-time recovery for production tables
- Monitor capacity and enable auto-scaling

### 4. SQS Best Practices

- Use long polling (WaitTimeSeconds > 0) to reduce costs
- Set appropriate visibility timeout (2-3x processing time)
- Implement dead-letter queues for failed messages
- Use FIFO queues when order matters
- Delete messages after successful processing
- Handle duplicate messages idempotently

### 5. Lambda Best Practices

- Keep functions small and focused
- Set appropriate timeout and memory limits
- Use environment variables for configuration
- Enable CloudWatch Logs for debugging
- Implement proper error handling
- Use async invocation for fire-and-forget operations

### 6. Cost Optimization

- Use S3 lifecycle policies to move old data to cheaper storage (Glacier)
- Delete unused resources (old snapshots, detached volumes)
- Use Reserved Instances or Savings Plans for predictable workloads
- Monitor costs with CloudWatch and Budgets
- Use LocalStack for development/testing

### 7. Security

- Follow principle of least privilege for IAM policies
- Enable CloudTrail for all regions
- Use VPC endpoints for private connectivity
- Encrypt data at rest and in transit
- Regularly rotate credentials
- Enable AWS Config for compliance

## LocalStack for Local Development

LocalStack provides a local AWS cloud stack for testing and development.

### Starting LocalStack with Docker

```bash
cd docker
docker-compose up -d localstack
```

### LocalStack Features

- **Services Emulated:** S3, DynamoDB, SQS, SNS, Lambda, Secrets Manager, CloudWatch, SES, EventBridge
- **Endpoint:** http://localhost:4566
- **Credentials:** test/test (any value works)
- **No AWS charges** - completely local

### Using AWS CLI with LocalStack

```bash
# Set endpoint for LocalStack
aws --endpoint-url=http://localhost:4566 s3 ls

# Create bucket
aws --endpoint-url=http://localhost:4566 s3 mb s3://test-bucket

# Upload file
aws --endpoint-url=http://localhost:4566 s3 cp file.txt s3://test-bucket/
```

### LocalStack Initialization

The Docker setup includes initialization scripts that create:
- S3 buckets: `aibasic-bucket`, `aibasic-uploads`, `aibasic-data`, `aibasic-logs`
- DynamoDB tables: `users`, `orders`, `events`
- SQS queues: `aibasic-queue`, `orders-queue`, `events-queue`, `tasks-queue`
- SNS topics: `aibasic-notifications`, `aibasic-alerts`, `aibasic-events`
- Lambda functions: `aibasic-test-function`
- Secrets: `database/dev/credentials`, `api/dev/key`

## Troubleshooting

### Connection Issues

**Problem:** Cannot connect to AWS services

**Solutions:**
1. Check AWS credentials are configured correctly
2. Verify region is set properly
3. Check network connectivity and firewall rules
4. For LocalStack, ensure container is running: `docker ps | grep localstack`

### Permission Errors

**Problem:** Access Denied errors

**Solutions:**
1. Verify IAM user/role has necessary permissions
2. Check bucket policies and ACLs for S3
3. Verify queue policies for SQS
4. Review CloudWatch Logs for detailed error messages

### Timeout Issues

**Problem:** Operations timing out

**Solutions:**
1. Increase timeout in configuration
2. Check network latency
3. For Lambda, increase function timeout
4. Use exponential backoff for retries

### LocalStack Issues

**Problem:** LocalStack services not working

**Solutions:**
1. Check LocalStack container logs: `docker logs aibasic-localstack`
2. Verify endpoint URL is correct: `http://localhost:4566`
3. Ensure VERIFY_SSL is set to false
4. Restart LocalStack: `docker-compose restart localstack`

## Additional Resources

### AWS Documentation
- [AWS SDK for Python (Boto3)](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [AWS S3 Developer Guide](https://docs.aws.amazon.com/s3/index.html)
- [DynamoDB Developer Guide](https://docs.aws.amazon.com/dynamodb/index.html)
- [SQS Developer Guide](https://docs.aws.amazon.com/sqs/index.html)
- [Lambda Developer Guide](https://docs.aws.amazon.com/lambda/index.html)

### LocalStack
- [LocalStack Documentation](https://docs.localstack.cloud/)
- [LocalStack GitHub](https://github.com/localstack/localstack)

### Best Practices
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
- [AWS Security Best Practices](https://aws.amazon.com/security/best-practices/)
- [AWS Cost Optimization](https://aws.amazon.com/pricing/cost-optimization/)

## Summary

The AWS Module provides comprehensive, production-ready integration with Amazon Web Services. It supports multiple AWS services through a unified Python interface, works seamlessly with LocalStack for local development, and follows AWS best practices for security, performance, and cost optimization.

**Key Benefits:**
- **Multi-service support** - Access 10+ AWS services from one module
- **Local development** - Test with LocalStack before deploying to AWS
- **Production ready** - Built-in retry logic, connection pooling, error handling
- **Cost effective** - Use LocalStack to reduce AWS charges during development
- **Secure** - Support for IAM roles, encryption, credential management
- **Scalable** - Designed for high-throughput applications

For complete examples, see `examples/example_aws.aib`.
