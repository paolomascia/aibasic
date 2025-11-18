# Implementazione Bulk Metadata per Moduli AIbasic

## Situazione Attuale

**Moduli con metadata completo**: 2/35 (6%)
- ✅ Discord (8 metodi documentati)
- ✅ Telegram (16 metodi documentati)

**Moduli rimanenti**: 33/35 (94%)

## Volume di Lavoro

### Stima per Modulo
- Aggiungere inheritance: `class XModule(AIbasicModuleBase)` - **2 min**
- Implementare `get_metadata()` - **5 min**
- Implementare `get_usage_notes()` (10-15 note) - **15 min**
- Implementare `get_methods_info()` (8-15 metodi) - **60-90 min**
- Implementare `get_examples()` (10-15 esempi) - **20 min**

**Tempo totale per modulo**: ~2-2.5 ore
**Tempo totale per 33 moduli**: ~66-82 ore

## Approcci Possibili

### Opzione 1: Implementazione Manuale Completa
**Pro**: Massima qualità e completezza
**Contro**: 66-82 ore di lavoro ripetitivo
**Quando**: Solo per moduli critici

### Opzione 2: Implementazione a Priorità
**Pro**: Focus sui moduli più usati
**Contro**: Alcuni moduli rimangono senza metadata
**Tempo**: ~20-30 ore per top 10 moduli
**Raccomandato**: ✅ **Questo approccio**

### Opzione 3: Template + Documentazione Minima
**Pro**: Veloce, copre tutti i moduli
**Contro**: Documentazione di base, da raffinare dopo
**Tempo**: ~15-20 ore
**Quando**: Per coverage rapido

### Opzione 4: Generazione Automatica
**Pro**: Molto veloce
**Contro**: Richiede sviluppo script di analisi
**Tempo**: 10 ore sviluppo + 5 ore review
**Quando**: Se si vogliono aggiornare molti moduli frequentemente

## Strategia Raccomandata

### Fase 1: Moduli Critici (ALTA PRIORITÀ)
Implementazione completa per moduli più usati:

1. **PostgreSQL** (postgres_module.py)
   - Metodi: execute_query, execute_query_dict, execute_many, get_connection
   - Tempo: ~2 ore

2. **MySQL** (mysql_module.py)
   - Metodi: execute_query, execute_query_dict, call_procedure
   - Tempo: ~2 ore

3. **MongoDB** (mongodb_module.py)
   - Metodi: find, find_one, insert_one, update_one, delete_one
   - Tempo: ~2 ore

4. **Redis** (redis_module.py)
   - Metodi: get, set, delete, exists, expire
   - Tempo: ~1.5 ore

5. **Email** (email_module.py)
   - Metodi: send_email, send_html_email, send_with_attachments
   - Tempo: ~1.5 ore

6. **Selenium** (selenium_module.py)
   - Metodi: navigate, click, type_text, get_text, wait_for_element (top 10 di ~40)
   - Tempo: ~2 ore

**Totale Fase 1**: ~11 ore → 8 moduli con metadata completo (23%)

### Fase 2: Moduli Importanti (MEDIA PRIORITÀ)

7. **Kafka** - Streaming
8. **RabbitMQ** - Messaging
9. **Elasticsearch** - Search
10. **Slack** - Notifications
11. **Teams** - Notifications
12. **AWS** - Cloud
13. **RestAPI** - HTTP Client
14. **SSH** - Remote execution

**Totale Fase 2**: ~16 ore → 16 moduli totali (46%)

### Fase 3: Moduli Specializzati (BASSA PRIORITÀ)

Rimanenti 19 moduli con template base o documentazione minima.

**Totale Fase 3**: ~10 ore → 35 moduli totali (100%)

**GRAN TOTALE**: ~37 ore per coverage completo

## Template per Implementazione Rapida

### Step 1: Aggiungere Inheritance
```python
# Aggiungere import
from .module_base import AIbasicModuleBase

# Modificare class declaration
class YourModule(AIbasicModuleBase):  # <-- Aggiungere (AIbasicModuleBase)
```

### Step 2: Aggiungere Metodi Metadata (prima di `def execute()`)

```python
    @classmethod
    def get_metadata(cls):
        """Get module metadata."""
        from aibasic.modules.module_base import ModuleMetadata
        return ModuleMetadata(
            name="ModuleName",
            task_type="task_type",
            description="Brief description",
            version="1.0.0",
            keywords=["key1", "key2", "key3"],
            dependencies=["package>=version"]  # o [] se nessuna
        )

    @classmethod
    def get_usage_notes(cls):
        """Get detailed usage notes."""
        return [
            "Note 1 about configuration/setup",
            "Note 2 about main use cases",
            "Note 3 about important methods",
            # ... 10-15 note totali
        ]

    @classmethod
    def get_methods_info(cls):
        """Get information about module methods."""
        from aibasic.modules.module_base import MethodInfo
        return [
            MethodInfo(
                name="method_name",
                description="What it does",
                parameters={
                    "param1": "Description of param1",
                    "param2": "Optional: description (default: value)"
                },
                returns="Description of return value",
                examples=[
                    '(task_type) method_name "param1"',
                    '(task_type) method_name "param1" with param2 "value"'
                ]
            ),
            # ... documentare top 5-10 metodi
        ]

    @classmethod
    def get_examples(cls):
        """Get AIbasic usage examples."""
        return [
            '10 (task_type) basic example',
            '20 (task_type) example with parameters',
            '30 LET result = (task_type) example with return value',
            # ... 10-15 esempi
        ]
```

## Script di Supporto

### check_metadata_coverage.py
Script per verificare quali moduli hanno metadata:

```bash
python check_metadata_coverage.py
```

Output:
```
✅ DiscordModule - Complete (8 methods)
✅ TelegramModule - Complete (16 methods)
⏳ PostgresModule - Template only
⏳ MySQLModule - Template only
❌ SeleniumModule - No metadata
...
```

### generate_metadata_stub.py
Genera stub metadata per un modulo:

```bash
python generate_metadata_stub.py postgres_module.py
```

Genera file con template da completare.

## Decisione Raccomandata

**Per l'utente che vuole risultati rapidi**:

1. **Ora** (30 min): Implemento metadata completo per PostgreSQL
2. **Prossimi giorni** (10 ore): Utente completa top 6 moduli critici
3. **Opzionale** (20+ ore): Utente completa moduli rimanenti quando necessario

**Oppure**:

**Approccio minimalista** (5 ore totali):
- Template base per tutti i 33 moduli
- Documentazione completa solo per Discord e Telegram (già fatto)
- Gli altri moduli funzionano ma con prompt meno ricchi
- Coverage 100% ma qualità variabile

## Cosa Fare Adesso?

**Scelta A**: Procedo con implementazione completa di PostgreSQL (2 ore)
**Scelta B**: Creo template base per tutti i 33 moduli (5 ore)
**Scelta C**: Documento solo metodi principali per top 10 moduli (15 ore)

**Quale approccio preferisci?**

