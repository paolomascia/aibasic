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
from .teams_module import TeamsModule
from .slack_module import SlackModule
from .clickhouse_module import ClickHouseModule
from .neo4j_module import Neo4jModule
from .elasticsearch_module import ElasticsearchModule
from .timescaledb_module import TimescaleDBModule
from .aws_module import AWSModule
from .terraform_module import TerraformModule
from .docker_module import DockerModule
from .kubernetes_module import KubernetesModule
from .azure_module import AzureModule
from .gcp_module import GCPModule
from .ldap_module import LDAPModule
from .keycloak_module import KeycloakModule
from .jwt_module import JWTModule
from .mqtt_module import MQTTModule
from .prometheus_module import PrometheusModule
from .scylladb_module import ScyllaDBModule
from .selenium_module import SeleniumModule

__all__ = ['PostgresModule', 'MySQLModule', 'RabbitMQModule', 'KafkaModule', 'RedisModule', 'OpenSearchModule', 'CompressionModule', 'VaultModule', 'CassandraModule', 'EmailModule', 'MongoDBModule', 'S3Module', 'RestAPIModule', 'SSHModule', 'TeamsModule', 'SlackModule', 'ClickHouseModule', 'Neo4jModule', 'ElasticsearchModule', 'TimescaleDBModule', 'AWSModule', 'TerraformModule', 'DockerModule', 'KubernetesModule', 'AzureModule', 'GCPModule', 'LDAPModule', 'KeycloakModule', 'JWTModule', 'MQTTModule', 'PrometheusModule', 'ScyllaDBModule', 'SeleniumModule']
