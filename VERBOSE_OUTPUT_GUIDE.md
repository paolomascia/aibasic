# Guida Output Verbose del Compilatore AIbasic

## Nuove Funzionalità

Il compilatore AIbasic ora fornisce **output dettagliato e informativo** durante la compilazione, specialmente quando vengono rilevati **task type espliciti** con metadata ricchi.

## Output Migliorato per Task Type Espliciti

Quando il compilatore rileva un'istruzione con task type esplicito (es. `(discord)`, `(telegram)`), ora mostra:

### 1. Informazioni Task Type

```
[TASK TYPE] Explicit: (discord)
[TASK TYPE] Name: Discord
[TASK TYPE] Description: Discord integration via webhooks for notifications, alerts, and team communication
```

### 2. Metadata Modulo (se disponibile)

Per moduli con metadata completo (Discord, Telegram):

```
[METADATA] ✓ Rich module metadata available
[METADATA]   Version: 1.0.0
[METADATA]   Methods: 8
[METADATA]   Usage Notes: 12
[METADATA]   Examples: 11
[METADATA]   Dependencies: requests>=2.31.0
```

### 3. Lista Metodi Disponibili

```
[METADATA]   Available methods:
[METADATA]     - send_message: Send a simple text message to Discord
[METADATA]     - send_embed: Send a rich embed message with formatting
[METADATA]     - create_embed: Create an embed object with title, description, fields...
[METADATA]     - send_notification: Send a pre-formatted notification (info, success...)
[METADATA]     - send_alert: Send an urgent alert with optional mentions
[METADATA]     ... and 3 more
```

### 4. Note d'Uso (Sample)

```
[METADATA]   Sample usage notes:
[METADATA]     • Webhook URL required - get from Discord Server Settings → Integrations
[METADATA]     • Use send_message() for simple text messages (2000 chars max)
[METADATA]     • Use send_embed() for rich formatted messages with colors, fields, images
[METADATA]     ... and 9 more
```

### 5. Esempi AIbasic (Sample)

```
[METADATA]   Sample AIbasic examples:
[METADATA]     10 (discord) send message "Hello from AIbasic!"
[METADATA]     20 (discord) send notification with title "Success" and message "Task completed"
[METADATA]     30 LET embed = (discord) create embed with title "Report" and description...
[METADATA]     ... and 8 more
```

### 6. Prompt Completo Inviato al LLM

Quando un modulo ha metadata ricchi, il compilatore stampa l'intero prompt che viene inviato all'LLM:

```
[PROMPT] Generating rich prompt for task type: (discord)
[PROMPT] Prompt size: 7234 characters
[PROMPT] Module info size: 6395 characters
[PROMPT] Task hint size: 156 characters
[PROMPT] ---
[PROMPT] Full user prompt being sent to LLM:
[PROMPT] ======================================================================
[PROMPT]    1 | You are now compiling ONE AIBasic instruction.
[PROMPT]    2 |
[PROMPT]    3 | Task Type: Discord (discord)
[PROMPT]    4 | Description: Discord integration via webhooks for notifications...
[PROMPT]    5 | Common Libraries: requests
[PROMPT]    6 |
[PROMPT]    7 |
[PROMPT]    8 | ## Discord Module
[PROMPT]    9 |
[PROMPT]   10 | **Description:** Discord integration via webhooks for notifications...
[PROMPT]   11 | **Task Type:** (discord)
[PROMPT]   12 | **Version:** 1.0.0
[PROMPT]   13 |
[PROMPT]   14 | ### Usage Notes:
[PROMPT]   15 | - Webhook URL required - get from Discord Server Settings...
[PROMPT]  ... [continues for entire prompt]
[PROMPT] ======================================================================
[PROMPT] End of prompt
```

## Output per Moduli Legacy

Per moduli che **non hanno ancora** metadata implementati (es. `postgres`, `mysql`):

```
[TASK TYPE] Explicit: (postgres)
[TASK TYPE] Name: PostgreSQL Operations
[TASK TYPE] Description: PostgreSQL-specific operations using connection pool module

[METADATA] Using legacy format (no rich metadata)
[METADATA]   Common libraries: psycopg2
```

## Esempio Completo di Compilazione

### Input: `test.aib`
```aibasic
10 (discord) send message "Hello World"
20 (telegram) send notification with title "Test" and level "success"
30 (postgres) query users from database
```

### Output Console:

```
=== AIBASIC COMPILER START ===
Config file: aibasic.conf
Source file: test.aib
Output file: output.py

--- Compiling instruction 10 ---
Text: send message "Hello World"

[TASK TYPE] Explicit: (discord)
[TASK TYPE] Name: Discord
[TASK TYPE] Description: Discord integration via webhooks for notifications, alerts, and team communication

[METADATA] ✓ Rich module metadata available
[METADATA]   Version: 1.0.0
[METADATA]   Methods: 8
[METADATA]   Usage Notes: 12
[METADATA]   Examples: 11
[METADATA]   Dependencies: requests>=2.31.0

[METADATA]   Available methods:
[METADATA]     - send_message: Send a simple text message to Discord
[METADATA]     - send_embed: Send a rich embed message with formatting
[METADATA]     - create_embed: Create an embed object with title, description...
[METADATA]     - send_notification: Send a pre-formatted notification...
[METADATA]     - send_alert: Send an urgent alert with optional mentions
[METADATA]     ... and 3 more

[PROMPT] Generating rich prompt for task type: (discord)
[PROMPT] Prompt size: 7234 characters
[PROMPT] Module info size: 6395 characters
[PROMPT] Task hint size: 156 characters
[PROMPT] ---
[PROMPT] Full user prompt being sent to LLM:
[PROMPT] ======================================================================
[PROMPT]    1 | You are now compiling ONE AIBasic instruction.
[PROMPT]    2 |
[PROMPT]    3 | Task Type: Discord (discord)
... [entire prompt with line numbers]
[PROMPT] ======================================================================
[PROMPT] End of prompt

[INTENT] {'instruction_type': 'action', 'action': 'send', ...}

Raw LLM result:
  {
    "code": "discord.send_message('Hello World')",
    "context_updates": {
      "last_output": "message_result"
    },
    "needs_imports": ["from aibasic.modules import DiscordModule"]
  }

Updated context:
  {
    "description": "Context for AIBasic → Python compilation...",
    "last_output": "message_result",
    "variables": {}
  }

--- Compiling instruction 20 ---
Text: send notification with title "Test" and level "success"

[TASK TYPE] Explicit: (telegram)
[TASK TYPE] Name: Telegram
[TASK TYPE] Description: Telegram Bot API integration for notifications...

[METADATA] ✓ Rich module metadata available
[METADATA]   Version: 1.0.0
[METADATA]   Methods: 16
[METADATA]   Usage Notes: 16
[METADATA]   Examples: 12
[METADATA]   Dependencies: requests>=2.31.0

[METADATA]   Available methods:
[METADATA]     - send_message: Send a text message with optional formatting
[METADATA]     - send_photo: Send a photo from URL or file path
[METADATA]     - send_document: Send a document/file
[METADATA]     - send_video: Send a video file
[METADATA]     - send_location: Send a GPS location
[METADATA]     ... and 11 more

[PROMPT] Generating rich prompt for task type: (telegram)
[PROMPT] Prompt size: 8912 characters
[PROMPT] Module info size: 8279 characters
... [continues]

--- Compiling instruction 30 ---
Text: query users from database

[TASK TYPE] Explicit: (postgres)
[TASK TYPE] Name: PostgreSQL Operations
[TASK TYPE] Description: PostgreSQL-specific operations using connection pool module

[METADATA] Using legacy format (no rich metadata)
[METADATA]   Common libraries: psycopg2

[INTENT] {'instruction_type': 'query', ...}
... [continues with standard compilation output]

=== COMPILATION COMPLETE ===
Output written to: output.py
```

## Benefici dell'Output Verbose

### 1. **Debugging Facilitato**
- Vedi esattamente quali metadata il compilatore sta usando
- Verifica se il modulo ha metadata ricchi o usa formato legacy
- Ispeziona il prompt completo inviato all'LLM

### 2. **Trasparenza**
- Chiaro quando vengono usati metadata dinamici vs hardcoded
- Visibilità completa su metodi disponibili e come usarli
- Comprensione di cosa viene chiesto all'LLM

### 3. **Educativo**
- Impara quali metodi sono disponibili per ogni modulo
- Vedi esempi di utilizzo direttamente durante la compilazione
- Capisci la differenza tra moduli con/senza metadata

### 4. **Verifica Implementazione**
- Conferma che i metadata dei moduli vengono caricati
- Verifica che il prompt contenga la documentazione completa
- Identifica moduli che necessitano ancora di implementazione metadata

## Test dell'Output Verbose

### Test Script
```bash
python test_verbose_output.py
```

Questo script mostra l'output verbose per vari tipi di istruzioni senza effettivamente chiamare l'API LLM.

### Output Atteso
```
✓ Discord module: Mostra metadata completo (8 metodi, 12 note, 11 esempi)
✓ Telegram module: Mostra metadata completo (16 metodi, 16 note, 12 esempi)
✓ PostgreSQL module: Mostra formato legacy (nessun metadata ancora)
✓ Auto-detection: Funziona per istruzioni senza task type esplicito
```

## Interpretare l'Output

### Simboli Chiave

| Simbolo/Tag | Significato |
|-------------|-------------|
| `[TASK TYPE]` | Informazioni sul tipo di task rilevato |
| `[METADATA] ✓` | Metadata ricchi disponibili |
| `[METADATA]` (no ✓) | Formato legacy, nessun metadata |
| `[PROMPT]` | Informazioni sul prompt generato |
| `[INTENT]` | Intent rilevato dall'analizzatore |
| `[CONTROL]` | Strutture di controllo (jump, call, return) |

### Righe Importanti da Cercare

1. **`[METADATA] ✓ Rich module metadata available`**
   - ✅ Indica che il modulo ha implementazione completa
   - Il prompt sarà ricco di documentazione

2. **`[METADATA] Using legacy format`**
   - ⚠️ Modulo non ha ancora metadata
   - Il prompt sarà meno dettagliato

3. **`[PROMPT] Prompt size: XXXX characters`**
   - Più grande = più informazioni per l'LLM
   - Discord/Telegram: ~7,000-9,000 caratteri
   - Legacy: ~500-1,000 caratteri

## Controllo Output Verbose

### Disabilitare l'Output del Prompt (Futuro)

Se l'output del prompt completo è troppo verboso, si può aggiungere un flag al compilatore:

```bash
# Con prompt completo (default)
python src/aibasic/aibasicc.py -c config.conf -i input.aib -o output.py

# Senza prompt completo (futuro)
python src/aibasic/aibasicc.py -c config.conf -i input.aib -o output.py --quiet-prompt
```

*Nota: Il flag --quiet-prompt non è ancora implementato*

## Riepilogo

✅ **Implementato**:
- Output dettagliato per task type espliciti
- Informazioni metadata modulo (quando disponibile)
- Lista metodi, note d'uso, esempi
- Prompt completo con numeri di riga
- Distinzione chiara tra metadata ricchi e legacy

✅ **Testato**:
- Discord module: Output completo e dettagliato
- Telegram module: Output completo e dettagliato
- PostgreSQL module: Output legacy corretto
- Auto-detection: Funziona correttamente

📊 **Risultato**:
Il compilatore ora fornisce **visibilità completa** sul processo di compilazione, rendendo facile capire:
- Quali metadata vengono usati
- Quali informazioni riceve l'LLM
- Quali moduli hanno implementazione completa
- Come ottimizzare le istruzioni AIbasic

---

**Data implementazione**: 2025-01-17
**Status**: ✅ Operativo
