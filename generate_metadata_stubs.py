#!/usr/bin/env python3
"""
Script to generate metadata method stubs for all AIbasic modules.
This creates a template that can be customized for each module.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Modules that already have metadata implemented
COMPLETED_MODULES = ['DiscordModule', 'TelegramModule']

# Module information - will be used to generate appropriate metadata
MODULE_INFO = {
    'SeleniumModule': {
        'name': 'Selenium',
        'task_type': 'selenium',
        'description': 'Web browser automation and testing with multi-browser support',
        'keywords': ['selenium', 'browser', 'web', 'automation', 'testing', 'scraping'],
        'dependencies': ['selenium>=4.15.0', 'webdriver-manager>=4.0.0']
    },
    'PostgresModule': {
        'name': 'PostgreSQL',
        'task_type': 'postgres',
        'description': 'PostgreSQL database operations with connection pooling',
        'keywords': ['postgres', 'postgresql', 'database', 'sql', 'query'],
        'dependencies': ['psycopg2-binary>=2.9.0']
    },
    'MySQLModule': {
        'name': 'MySQL',
        'task_type': 'mysql',
        'description': 'MySQL/MariaDB database operations with connection pooling',
        'keywords': ['mysql', 'mariadb', 'database', 'sql', 'query'],
        'dependencies': ['mysql-connector-python>=8.0.0']
    },
    'MongoDBModule': {
        'name': 'MongoDB',
        'task_type': 'mongodb',
        'description': 'MongoDB NoSQL database operations',
        'keywords': ['mongodb', 'nosql', 'database', 'document'],
        'dependencies': ['pymongo>=4.0.0']
    },
    'CassandraModule': {
        'name': 'Cassandra',
        'task_type': 'cassandra',
        'description': 'Apache Cassandra distributed NoSQL database',
        'keywords': ['cassandra', 'nosql', 'distributed', 'cql'],
        'dependencies': ['cassandra-driver>=3.25.0']
    },
    'RedisModule': {
        'name': 'Redis',
        'task_type': 'redis',
        'description': 'Redis in-memory data store and cache',
        'keywords': ['redis', 'cache', 'keyvalue', 'inmemory'],
        'dependencies': ['redis>=4.0.0']
    },
    'ElasticsearchModule': {
        'name': 'Elasticsearch',
        'task_type': 'elasticsearch',
        'description': 'Elasticsearch search and analytics engine',
        'keywords': ['elasticsearch', 'search', 'analytics', 'indexing'],
        'dependencies': ['elasticsearch>=8.0.0']
    },
    'KafkaModule': {
        'name': 'Kafka',
        'task_type': 'kafka',
        'description': 'Apache Kafka message streaming platform',
        'keywords': ['kafka', 'streaming', 'messaging', 'events'],
        'dependencies': ['kafka-python>=2.0.0']
    },
    'RabbitMQModule': {
        'name': 'RabbitMQ',
        'task_type': 'rabbitmq',
        'description': 'RabbitMQ message broker for async communication',
        'keywords': ['rabbitmq', 'messaging', 'queue', 'amqp'],
        'dependencies': ['pika>=1.2.0']
    },
    'EmailModule': {
        'name': 'Email',
        'task_type': 'email',
        'description': 'Email sending with SMTP and template support',
        'keywords': ['email', 'smtp', 'mail', 'notification'],
        'dependencies': []  # Uses built-in smtplib
    },
    'SlackModule': {
        'name': 'Slack',
        'task_type': 'slack',
        'description': 'Slack integration for team notifications',
        'keywords': ['slack', 'notification', 'webhook', 'chat'],
        'dependencies': ['requests>=2.31.0']
    },
    'TeamsModule': {
        'name': 'Teams',
        'task_type': 'teams',
        'description': 'Microsoft Teams integration for notifications',
        'keywords': ['teams', 'microsoft', 'notification', 'webhook'],
        'dependencies': ['requests>=2.31.0']
    },
    'AWSModule': {
        'name': 'AWS',
        'task_type': 'aws',
        'description': 'Amazon Web Services cloud integration',
        'keywords': ['aws', 'cloud', 'amazon', 's3', 'ec2'],
        'dependencies': ['boto3>=1.26.0']
    },
    'AzureModule': {
        'name': 'Azure',
        'task_type': 'azure',
        'description': 'Microsoft Azure cloud integration',
        'keywords': ['azure', 'cloud', 'microsoft'],
        'dependencies': ['azure-identity>=1.12.0', 'azure-mgmt-compute>=29.0.0']
    },
    'GCPModule': {
        'name': 'GCP',
        'task_type': 'gcp',
        'description': 'Google Cloud Platform integration',
        'keywords': ['gcp', 'google', 'cloud'],
        'dependencies': ['google-cloud-storage>=2.7.0']
    },
    'DockerModule': {
        'name': 'Docker',
        'task_type': 'docker',
        'description': 'Docker container management',
        'keywords': ['docker', 'container', 'containerization'],
        'dependencies': ['docker>=6.0.0']
    },
    'KubernetesModule': {
        'name': 'Kubernetes',
        'task_type': 'kubernetes',
        'description': 'Kubernetes cluster management',
        'keywords': ['kubernetes', 'k8s', 'orchestration', 'container'],
        'dependencies': ['kubernetes>=25.0.0']
    },
    'TerraformModule': {
        'name': 'Terraform',
        'task_type': 'terraform',
        'description': 'Infrastructure as Code with Terraform',
        'keywords': ['terraform', 'iac', 'infrastructure'],
        'dependencies': []  # Uses terraform CLI
    },
}

def generate_metadata_template(module_name, info):
    """Generate metadata methods template for a module."""
    return f'''
    @classmethod
    def get_metadata(cls):
        """Get module metadata."""
        from aibasic.modules.module_base import ModuleMetadata
        return ModuleMetadata(
            name="{info['name']}",
            task_type="{info['task_type']}",
            description="{info['description']}",
            version="1.0.0",
            keywords={info['keywords']},
            dependencies={info['dependencies']}
        )

    @classmethod
    def get_usage_notes(cls):
        """Get detailed usage notes."""
        return [
            "TODO: Add usage notes for {info['name']} module",
            "Describe connection/setup requirements",
            "List main use cases and methods",
            "Include best practices and limitations"
        ]

    @classmethod
    def get_methods_info(cls):
        """Get information about module methods."""
        from aibasic.modules.module_base import MethodInfo
        return [
            # TODO: Add MethodInfo for each public method
            # Example:
            # MethodInfo(
            #     name="method_name",
            #     description="Method description",
            #     parameters={{"param": "description"}},
            #     returns="Return value description",
            #     examples=["example usage"]
            # )
        ]

    @classmethod
    def get_examples(cls):
        """Get AIbasic usage examples."""
        return [
            # TODO: Add AIbasic code examples
            '10 ({info['task_type']}) example operation'
        ]
'''

# Generate report
print("=== Metadata Implementation Status ===\n")
print(f"Completed modules: {', '.join(COMPLETED_MODULES)}\n")
print("Modules needing metadata:")

for module_name, info in MODULE_INFO.items():
    if module_name not in COMPLETED_MODULES:
        print(f"\n### {module_name} ({info['task_type']})")
        print(f"Description: {info['description']}")
        print("\nGenerated template:")
        print(generate_metadata_template(module_name, info))
        print("-" * 80)
