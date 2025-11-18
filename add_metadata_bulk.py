#!/usr/bin/env python3
"""
Script per aggiungere metadata di base a tutti i moduli AIbasic mancanti.
Genera template metadata che possono essere raffinati manualmente.
"""

import sys
import re
from pathlib import Path

# Module information
MODULES_INFO = {
    'selenium_module.py': {
        'class_name': 'SeleniumModule',
        'name': 'Selenium',
        'task_type': 'selenium',
        'description': 'Web browser automation and testing with multi-browser support',
        'keywords': ['selenium', 'browser', 'web', 'automation', 'testing', 'scraping', 'webdriver'],
        'dependencies': ['selenium>=4.15.0', 'webdriver-manager>=4.0.0'],
        'key_methods': ['navigate', 'click', 'type_text', 'get_text', 'wait_for_element', 'take_screenshot', 'execute_script']
    },
    'postgres_module.py': {
        'class_name': 'PostgresModule',
        'name': 'PostgreSQL',
        'task_type': 'postgres',
        'description': 'PostgreSQL database operations with connection pooling and transaction support',
        'keywords': ['postgres', 'postgresql', 'database', 'sql', 'query', 'pool'],
        'dependencies': ['psycopg2-binary>=2.9.0'],
        'key_methods': ['execute_query', 'execute_query_dict', 'execute_many', 'get_connection', 'release_connection']
    },
    'mysql_module.py': {
        'class_name': 'MySQLModule',
        'name': 'MySQL',
        'task_type': 'mysql',
        'description': 'MySQL/MariaDB database operations with connection pooling',
        'keywords': ['mysql', 'mariadb', 'database', 'sql', 'query', 'pool'],
        'dependencies': ['mysql-connector-python>=8.0.0'],
        'key_methods': ['execute_query', 'execute_query_dict', 'call_procedure', 'get_connection', 'release_connection']
    },
    'mongodb_module.py': {
        'class_name': 'MongoDBModule',
        'name': 'MongoDB',
        'task_type': 'mongodb',
        'description': 'MongoDB NoSQL database operations for document storage',
        'keywords': ['mongodb', 'nosql', 'database', 'document', 'collection'],
        'dependencies': ['pymongo>=4.0.0'],
        'key_methods': ['find', 'find_one', 'insert_one', 'insert_many', 'update_one', 'delete_one']
    },
    'redis_module.py': {
        'class_name': 'RedisModule',
        'name': 'Redis',
        'task_type': 'redis',
        'description': 'Redis in-memory data store and cache operations',
        'keywords': ['redis', 'cache', 'keyvalue', 'inmemory', 'pub', 'sub'],
        'dependencies': ['redis>=4.0.0'],
        'key_methods': ['get', 'set', 'delete', 'exists', 'expire', 'publish', 'subscribe']
    },
    'email_module.py': {
        'class_name': 'EmailModule',
        'name': 'Email',
        'task_type': 'email',
        'description': 'Email sending with SMTP and template support',
        'keywords': ['email', 'smtp', 'mail', 'send', 'notification'],
        'dependencies': [],
        'key_methods': ['send_email', 'send_html_email', 'send_with_attachments']
    },
}

def generate_metadata_methods(info):
    """Generate metadata methods template"""
    methods_list = ', '.join([f"'{m}'" for m in info['key_methods'][:3]])

    template = f'''
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
            "Module uses singleton pattern - one instance shared across operations",
            "Key methods: {methods_list}",
            "See get_methods_info() for detailed parameter documentation",
        ]

    @classmethod
    def get_methods_info(cls):
        """Get information about module methods."""
        from aibasic.modules.module_base import MethodInfo
        # TODO: Document all methods
        return [
            # Example for first method:
            # MethodInfo(
            #     name="{info['key_methods'][0] if info['key_methods'] else 'method_name'}",
            #     description="Method description here",
            #     parameters={{"param1": "Description", "param2": "Description"}},
            #     returns="Return value description",
            #     examples=['({info['task_type']}) example usage']
            # ),
        ]

    @classmethod
    def get_examples(cls):
        """Get AIbasic usage examples."""
        return [
            # TODO: Add real examples
            '10 ({info['task_type']}) example operation',
            '20 ({info['task_type']}) another example',
        ]
'''
    return template

print("=" * 80)
print("METADATA BULK ADDITION SCRIPT")
print("=" * 80)
print(f"\nThis script will add metadata template to {len(MODULES_INFO)} modules")
print("\nModules to process:")
for filename, info in MODULES_INFO.items():
    print(f"  - {filename}: {info['name']} ({info['task_type']})")

print("\n" + "=" * 80)
print("GENERATED TEMPLATE EXAMPLE")
print("=" * 80)
print("\nExample for Selenium module:")
print(generate_metadata_methods(MODULES_INFO['selenium_module.py']))

print("\n" + "=" * 80)
print("NEXT STEPS")
print("=" * 80)
print("""
Per completare l'implementazione:

1. Questo script genera solo i TEMPLATE
2. Bisogna ancora:
   - Aggiungere import: from .module_base import AIbasicModuleBase
   - Modificare class declaration: class XModule(AIbasicModuleBase):
   - Inserire i metodi metadata prima della funzione execute()
   - Completare get_usage_notes() con note reali
   - Documentare TUTTI i metodi in get_methods_info()
   - Aggiungere esempi reali in get_examples()

3. Dato il volume di lavoro (33 moduli x ~10 metodi ciascuno),
   suggerisco di procedere per priorità:

   ALTA PRIORITÀ (fare subito):
   - Selenium, PostgreSQL, MySQL, MongoDB, Redis, Email

   MEDIA PRIORITÀ (fare dopo):
   - Kafka, RabbitMQ, Elasticsearch, Slack, Teams, AWS

   BASSA PRIORITÀ (opzionale):
   - Moduli specializzati meno usati

4. Alternative più efficienti:
   - Generare metadata usando l'analisi del codice sorgente
   - Usare un LLM per documentare automaticamente i metodi
   - Documentare solo i 5-10 metodi più usati per modulo
""")
