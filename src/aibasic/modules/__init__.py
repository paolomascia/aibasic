"""
AIBasic Modules

This package contains reusable modules that can be used by AIBasic programs.
Each module provides specific functionality (database connections, APIs, etc.)
and can be initialized from aibasic.conf configuration.
"""

from .postgres_module import PostgresModule
from .mysql_module import MySQLModule
from .rabbitmq_module import RabbitMQModule
from .kafka_module import KafkaModule
from .redis_module import RedisModule
from .opensearch_module import OpenSearchModule
from .compression_module import CompressionModule
from .vault_module import VaultModule
from .cassandra_module import CassandraModule
from .email_module import EmailModule
from .mongodb_module import MongoDBModule
from .s3_module import S3Module
from .restapi_module import RestAPIModule
from .ssh_module import SSHModule

__all__ = ['PostgresModule', 'MySQLModule', 'RabbitMQModule', 'KafkaModule', 'RedisModule', 'OpenSearchModule', 'CompressionModule', 'VaultModule', 'CassandraModule', 'EmailModule', 'MongoDBModule', 'S3Module', 'RestAPIModule', 'SSHModule']
