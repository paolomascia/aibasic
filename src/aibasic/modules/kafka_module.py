"""
Apache Kafka Module for Message Publishing and Consumption

This module provides producer and consumer management for Apache Kafka.
Configuration is loaded from aibasic.conf under the [kafka] section.

Supports:
- PLAINTEXT (no authentication)
- SASL_PLAINTEXT (username/password without encryption)
- SASL_SSL (username/password with SSL/TLS)
- SSL (certificate-based authentication)
- Multiple SASL mechanisms: PLAIN, SCRAM-SHA-256, SCRAM-SHA-512, GSSAPI (Kerberos)
- SSL/TLS with certificate verification
- SSL/TLS without certificate verification (for development)
- Producer and Consumer with all Kafka features

Example configuration in aibasic.conf:
    [kafka]
    BOOTSTRAP_SERVERS=localhost:9092

    # Security Protocol: PLAINTEXT, SASL_PLAINTEXT, SASL_SSL, SSL
    SECURITY_PROTOCOL=PLAINTEXT

    # SASL Settings (if using SASL_*)
    SASL_MECHANISM=PLAIN
    SASL_USERNAME=user
    SASL_PASSWORD=password

    # SSL/TLS Settings (if using *_SSL or SSL)
    SSL_CHECK_HOSTNAME=true
    SSL_VERIFY=true
    SSL_CA_CERT=/path/to/ca-cert.pem
    SSL_CLIENT_CERT=/path/to/client-cert.pem
    SSL_CLIENT_KEY=/path/to/client-key.pem

    # Producer Settings
    PRODUCER_ACKS=all
    PRODUCER_COMPRESSION=gzip
    PRODUCER_MAX_REQUEST_SIZE=1048576

    # Consumer Settings
    CONSUMER_GROUP_ID=aibasic-consumer-group
    CONSUMER_AUTO_OFFSET_RESET=earliest
    CONSUMER_ENABLE_AUTO_COMMIT=true

Usage in generated code:
    from aibasic.modules import KafkaModule

    # Initialize module (happens once per program)
    kafka = KafkaModule.from_config(config_path="aibasic.conf")

    # Publish a message
    kafka.publish_message(
        topic='my-topic',
        message={'event': 'user_login', 'user_id': 123},
        key='user_123'
    )

    # Consume messages
    for message in kafka.consume_messages(topics=['my-topic']):
        print(f"Received: {message.value}")
"""

import configparser
import json
import ssl
import threading
from pathlib import Path
from typing import Optional, List, Dict, Any, Union, Callable

from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError


class KafkaModule:
    """
    Apache Kafka producer and consumer manager.

    Supports all authentication methods and flexible SSL/TLS configuration.
    """

    _instance = None
    _lock = threading.Lock()

    def __init__(
        self,
        bootstrap_servers: str,
        security_protocol: str = 'PLAINTEXT',
        sasl_mechanism: Optional[str] = None,
        sasl_username: Optional[str] = None,
        sasl_password: Optional[str] = None,
        ssl_check_hostname: bool = True,
        ssl_verify: bool = True,
        ssl_ca_cert: Optional[str] = None,
        ssl_client_cert: Optional[str] = None,
        ssl_client_key: Optional[str] = None,
        producer_acks: str = 'all',
        producer_compression: Optional[str] = None,
        producer_max_request_size: int = 1048576,
        consumer_group_id: str = 'aibasic-consumer-group',
        consumer_auto_offset_reset: str = 'earliest',
        consumer_enable_auto_commit: bool = True
    ):
        """
        Initialize the Kafka module.

        Args:
            bootstrap_servers: Kafka bootstrap servers (comma-separated)
            security_protocol: PLAINTEXT, SASL_PLAINTEXT, SASL_SSL, or SSL
            sasl_mechanism: PLAIN, SCRAM-SHA-256, SCRAM-SHA-512, GSSAPI
            sasl_username: Username for SASL authentication
            sasl_password: Password for SASL authentication
            ssl_check_hostname: Check SSL hostname
            ssl_verify: Verify SSL certificates (set False for self-signed)
            ssl_ca_cert: Path to CA certificate file
            ssl_client_cert: Path to client certificate file
            ssl_client_key: Path to client key file
            producer_acks: Producer acknowledgment mode (0, 1, all)
            producer_compression: Producer compression (gzip, snappy, lz4, zstd)
            producer_max_request_size: Maximum request size in bytes
            consumer_group_id: Consumer group ID
            consumer_auto_offset_reset: earliest, latest, none
            consumer_enable_auto_commit: Auto-commit offsets
        """
        self.bootstrap_servers = bootstrap_servers.split(',')
        self.security_protocol = security_protocol
        self.sasl_mechanism = sasl_mechanism
        self.sasl_username = sasl_username
        self.sasl_password = sasl_password
        self.ssl_check_hostname = ssl_check_hostname
        self.ssl_verify = ssl_verify
        self.ssl_ca_cert = ssl_ca_cert
        self.ssl_client_cert = ssl_client_cert
        self.ssl_client_key = ssl_client_key

        # Producer settings
        self.producer_acks = producer_acks
        self.producer_compression = producer_compression
        self.producer_max_request_size = producer_max_request_size

        # Consumer settings
        self.consumer_group_id = consumer_group_id
        self.consumer_auto_offset_reset = consumer_auto_offset_reset
        self.consumer_enable_auto_commit = consumer_enable_auto_commit

        self._producer = None
        self._consumers = {}  # topic -> consumer mapping

        # Build common config
        self._common_config = self._build_common_config()

        print(f"[KafkaModule] Initialized: {bootstrap_servers} ({security_protocol})")
        if not ssl_verify and 'SSL' in security_protocol:
            print("[KafkaModule] ⚠️  SSL certificate verification DISABLED")

    def _build_common_config(self) -> Dict[str, Any]:
        """Build common configuration for producer and consumer."""
        config = {
            'bootstrap_servers': self.bootstrap_servers,
            'security_protocol': self.security_protocol,
        }

        # SASL configuration
        if 'SASL' in self.security_protocol:
            if not self.sasl_mechanism:
                raise ValueError("SASL_MECHANISM required when using SASL authentication")

            config['sasl_mechanism'] = self.sasl_mechanism
            config['sasl_plain_username'] = self.sasl_username
            config['sasl_plain_password'] = self.sasl_password

        # SSL configuration
        if 'SSL' in self.security_protocol:
            # SSL context configuration
            ssl_context = None
            if not self.ssl_verify:
                # Create context that doesn't verify certificates
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                config['ssl_context'] = ssl_context
            else:
                # Use default context with verification
                if self.ssl_ca_cert:
                    ssl_context = ssl.create_default_context(cafile=self.ssl_ca_cert)
                    config['ssl_context'] = ssl_context
                else:
                    config['ssl_cafile'] = self.ssl_ca_cert

            # Client certificates
            if self.ssl_client_cert:
                config['ssl_certfile'] = self.ssl_client_cert
            if self.ssl_client_key:
                config['ssl_keyfile'] = self.ssl_client_key

            config['ssl_check_hostname'] = self.ssl_check_hostname

        return config

    @classmethod
    def from_config(cls, config_path: str = "aibasic.conf") -> 'KafkaModule':
        """
        Create a KafkaModule from configuration file.
        Uses singleton pattern to ensure only one instance exists.

        Args:
            config_path: Path to aibasic.conf file

        Returns:
            KafkaModule instance

        Raises:
            FileNotFoundError: If config file doesn't exist
            KeyError: If required configuration is missing
        """
        with cls._lock:
            if cls._instance is None:
                config = configparser.ConfigParser()
                path = Path(config_path)

                if not path.exists():
                    raise FileNotFoundError(f"Configuration file not found: {config_path}")

                config.read(path)

                if 'kafka' not in config:
                    raise KeyError("Missing [kafka] section in aibasic.conf")

                kafka_config = config['kafka']

                # Required
                bootstrap_servers = kafka_config.get('BOOTSTRAP_SERVERS')
                if not bootstrap_servers:
                    raise KeyError("Missing required kafka configuration: BOOTSTRAP_SERVERS")

                # Security
                security_protocol = kafka_config.get('SECURITY_PROTOCOL', 'PLAINTEXT')
                sasl_mechanism = kafka_config.get('SASL_MECHANISM', None)
                sasl_username = kafka_config.get('SASL_USERNAME', None)
                sasl_password = kafka_config.get('SASL_PASSWORD', None)

                # SSL
                ssl_check_hostname = kafka_config.getboolean('SSL_CHECK_HOSTNAME', True)
                ssl_verify = kafka_config.getboolean('SSL_VERIFY', True)
                ssl_ca_cert = kafka_config.get('SSL_CA_CERT', None)
                ssl_client_cert = kafka_config.get('SSL_CLIENT_CERT', None)
                ssl_client_key = kafka_config.get('SSL_CLIENT_KEY', None)

                # Producer
                producer_acks = kafka_config.get('PRODUCER_ACKS', 'all')
                producer_compression = kafka_config.get('PRODUCER_COMPRESSION', None)
                producer_max_request_size = kafka_config.getint('PRODUCER_MAX_REQUEST_SIZE', 1048576)

                # Consumer
                consumer_group_id = kafka_config.get('CONSUMER_GROUP_ID', 'aibasic-consumer-group')
                consumer_auto_offset_reset = kafka_config.get('CONSUMER_AUTO_OFFSET_RESET', 'earliest')
                consumer_enable_auto_commit = kafka_config.getboolean('CONSUMER_ENABLE_AUTO_COMMIT', True)

                cls._instance = cls(
                    bootstrap_servers=bootstrap_servers,
                    security_protocol=security_protocol,
                    sasl_mechanism=sasl_mechanism,
                    sasl_username=sasl_username,
                    sasl_password=sasl_password,
                    ssl_check_hostname=ssl_check_hostname,
                    ssl_verify=ssl_verify,
                    ssl_ca_cert=ssl_ca_cert,
                    ssl_client_cert=ssl_client_cert,
                    ssl_client_key=ssl_client_key,
                    producer_acks=producer_acks,
                    producer_compression=producer_compression,
                    producer_max_request_size=producer_max_request_size,
                    consumer_group_id=consumer_group_id,
                    consumer_auto_offset_reset=consumer_auto_offset_reset,
                    consumer_enable_auto_commit=consumer_enable_auto_commit
                )

            return cls._instance

    def _get_producer(self) -> KafkaProducer:
        """Get or create Kafka producer."""
        if self._producer is None:
            producer_config = self._common_config.copy()
            producer_config.update({
                'acks': self.producer_acks,
                'max_request_size': self.producer_max_request_size,
                'value_serializer': lambda v: json.dumps(v).encode('utf-8') if isinstance(v, dict) else v if isinstance(v, bytes) else str(v).encode('utf-8'),
            })

            if self.producer_compression:
                producer_config['compression_type'] = self.producer_compression

            self._producer = KafkaProducer(**producer_config)
            print("[KafkaModule] Producer created")

        return self._producer

    def publish_message(
        self,
        topic: str,
        message: Union[str, dict, bytes],
        key: Optional[str] = None,
        partition: Optional[int] = None,
        headers: Optional[List[tuple]] = None
    ):
        """
        Publish a message to a Kafka topic.

        Args:
            topic: Topic name
            message: Message value (str, dict, or bytes)
            key: Message key (for partitioning)
            partition: Specific partition to send to
            headers: List of (key, value) tuples for message headers

        Example:
            kafka.publish_message(
                topic='events',
                message={'user_id': 123, 'action': 'login'},
                key='user_123',
                headers=[('source', b'web-app')]
            )
        """
        producer = self._get_producer()

        # Prepare key
        key_bytes = key.encode('utf-8') if key else None

        # Send message
        future = producer.send(
            topic,
            value=message,
            key=key_bytes,
            partition=partition,
            headers=headers
        )

        # Wait for result
        try:
            record_metadata = future.get(timeout=10)
            print(f"[KafkaModule] Message published to {record_metadata.topic}:{record_metadata.partition} @ {record_metadata.offset}")
        except KafkaError as e:
            print(f"[KafkaModule] ❌ Failed to publish message: {e}")
            raise

    def publish_batch(
        self,
        topic: str,
        messages: List[Union[str, dict, bytes]],
        keys: Optional[List[str]] = None
    ):
        """
        Publish multiple messages in a batch.

        Args:
            topic: Topic name
            messages: List of messages
            keys: Optional list of keys (same length as messages)

        Example:
            kafka.publish_batch(
                topic='events',
                messages=[
                    {'user_id': 1, 'action': 'login'},
                    {'user_id': 2, 'action': 'logout'}
                ],
                keys=['user_1', 'user_2']
            )
        """
        producer = self._get_producer()

        if keys and len(keys) != len(messages):
            raise ValueError("Keys list must have same length as messages list")

        futures = []
        for i, message in enumerate(messages):
            key = keys[i] if keys else None
            key_bytes = key.encode('utf-8') if key else None

            future = producer.send(topic, value=message, key=key_bytes)
            futures.append(future)

        # Wait for all
        for future in futures:
            try:
                future.get(timeout=10)
            except KafkaError as e:
                print(f"[KafkaModule] ❌ Failed to publish message: {e}")

        print(f"[KafkaModule] Batch of {len(messages)} messages published to {topic}")

    def flush_producer(self):
        """Flush any pending messages in the producer."""
        if self._producer:
            self._producer.flush()
            print("[KafkaModule] Producer flushed")

    def consume_messages(
        self,
        topics: List[str],
        callback: Optional[Callable] = None,
        max_messages: Optional[int] = None,
        timeout_ms: int = 1000
    ):
        """
        Consume messages from Kafka topics.

        Args:
            topics: List of topic names to subscribe to
            callback: Optional callback function(message) to process each message
            max_messages: Maximum number of messages to consume (None = infinite)
            timeout_ms: Consumer poll timeout in milliseconds

        Yields:
            ConsumerRecord objects if no callback provided

        Example:
            # With callback
            def process(msg):
                print(f"Received: {msg.value}")

            kafka.consume_messages(['my-topic'], callback=process, max_messages=100)

            # As iterator
            for message in kafka.consume_messages(['my-topic'], max_messages=10):
                print(message.value)
        """
        consumer_config = self._common_config.copy()
        consumer_config.update({
            'group_id': self.consumer_group_id,
            'auto_offset_reset': self.consumer_auto_offset_reset,
            'enable_auto_commit': self.consumer_enable_auto_commit,
            'value_deserializer': lambda m: json.loads(m.decode('utf-8')) if m else None,
        })

        consumer = KafkaConsumer(*topics, **consumer_config)
        print(f"[KafkaModule] Consuming from topics: {topics}")

        try:
            count = 0
            for message in consumer:
                if callback:
                    callback(message)
                else:
                    yield message

                count += 1
                if max_messages and count >= max_messages:
                    break

        except KeyboardInterrupt:
            print("\n[KafkaModule] Consumer stopped by user")
        finally:
            consumer.close()
            print("[KafkaModule] Consumer closed")

    def get_topic_metadata(self, topic: str) -> Dict[str, Any]:
        """
        Get metadata for a topic.

        Args:
            topic: Topic name

        Returns:
            dict: Topic metadata including partitions
        """
        producer = self._get_producer()
        metadata = producer.partitions_for(topic)

        return {
            "topic": topic,
            "partitions": list(metadata) if metadata else []
        }

    def close(self):
        """Close producer and all consumers."""
        if self._producer:
            self._producer.close()
            print("[KafkaModule] Producer closed")

        for consumer in self._consumers.values():
            consumer.close()
        self._consumers.clear()
        print("[KafkaModule] All consumers closed")

    def get_connection_info(self) -> Dict[str, Any]:
        """
        Get current connection information.

        Returns:
            dict: Connection details
        """
        return {
            "bootstrap_servers": self.bootstrap_servers,
            "security_protocol": self.security_protocol,
            "sasl_mechanism": self.sasl_mechanism,
            "ssl_verify": self.ssl_verify,
            "consumer_group_id": self.consumer_group_id
        }

    def __del__(self):
        """Destructor to ensure connections are closed."""
        self.close()
