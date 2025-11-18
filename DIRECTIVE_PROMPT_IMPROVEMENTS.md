# Miglioramenti al Prompt Direttivo per l'Utilizzo dei Moduli

## Problema Identificato

**Sintomo**: L'LLM riceveva la documentazione completa dei moduli (6,000+ caratteri) ma **generava comunque codice da zero** invece di utilizzare i metodi del modulo.

**Esempio del problema**:
```aibasic
10 (discord) send message "Hello World"
```

**Codice generato (SBAGLIATO)**:
```python
import requests
webhook_url = "https://discord.com/api/webhooks/..."
response = requests.post(webhook_url, json={"content": "Hello World"})
```

**Codice atteso (CORRETTO)**:
```python
from aibasic.modules import DiscordModule
discord = DiscordModule()
result = discord.send_message("Hello World")
```

## Soluzione Implementata

### Prima: Istruzioni Deboli ❌

```
Requirements:
- Use the module's methods as documented above
- Follow the parameter names and types exactly as specified
- Reference the AIbasic examples shown above for correct usage patterns
```

**Problema**: Troppo generico, facilmente ignorato dall'LLM.

### Dopo: Istruzioni Forti e Direttive ✅

```
======================================================================
CRITICAL MODULE USAGE REQUIREMENTS:
======================================================================
1. MANDATORY: Import and use the DiscordModule class
   from aibasic.modules import DiscordModule

2. MANDATORY: Create module instance (use existing if in context):
   discord = DiscordModule()

3. MANDATORY: Call the appropriate method from the module
   - DO NOT write custom code to implement the functionality
   - DO NOT use external libraries directly (requests, discord.py, etc.)
   - MUST use the module's pre-defined methods documented above

4. MANDATORY: Follow the exact method signatures shown in documentation
   - Use the parameter names exactly as documented
   - Pass parameters in the correct format (dict, string, int, etc.)

5. Example pattern (adapt to the specific instruction):
   # Import module
   from aibasic.modules import DiscordModule
   # Get or create instance
   discord = DiscordModule()
   # Call appropriate method
   result = discord.method_name(param1, param2, ...)

6. FORBIDDEN:
   - DO NOT implement webhook calls directly
   - DO NOT use requests.post() or similar
   - DO NOT create custom HTTP clients
   - DO NOT reimplement module functionality

7. The module methods are ALREADY IMPLEMENTED and TESTED
   - Simply call them with correct parameters
   - Trust the module to handle the implementation details

8. For THIS specific instruction: 'send message "Hello World"'
   YOU MUST:
   a) Check if 'discord' is already in context variables
   b) If not, create it: discord = DiscordModule()
   c) Identify which method matches the instruction (refer to methods list above)
   d) Call that method: result = discord.method_name(...)
   e) Store result appropriately

   CORRECT EXAMPLE:
   ```python
   from aibasic.modules import DiscordModule
   discord = DiscordModule()
   result = discord.appropriate_method('param1', param2=value)
   ```

   WRONG EXAMPLE (DO NOT DO THIS):
   ```python
   import requests
   response = requests.post(url, json=data)  # WRONG!
   ```
======================================================================
```

## Tecniche Utilizzate

### 1. **Parole Chiave Forti**
- `MANDATORY` - Non opzionale
- `MUST` - Obbligatorio
- `FORBIDDEN` - Vietato
- `DO NOT` - Esplicito cosa NON fare
- `CRITICAL` - Alta priorità

**Perché funziona**: Crea un forte peso semantico per l'LLM.

### 2. **Lista di Comportamenti Vietati**
```
FORBIDDEN:
- DO NOT implement webhook calls directly
- DO NOT use requests.post() or similar
- DO NOT create custom HTTP clients
- DO NOT reimplement module functionality
```

**Perché funziona**: Elenca esplicitamente gli anti-pattern comuni.

### 3. **Esempi Concreti Corretti e Sbagliati**
```python
# CORRECT EXAMPLE:
from aibasic.modules import DiscordModule
discord = DiscordModule()
result = discord.send_message("Hello")

# WRONG EXAMPLE (DO NOT DO THIS):
import requests
response = requests.post(url, json=data)  # WRONG!
```

**Perché funziona**: Riduce l'ambiguità mostrando pattern specifici.

### 4. **Istruzioni Specifiche per l'Istruzione Corrente**
```
8. For THIS specific instruction: 'send message "Hello World"'
   YOU MUST:
   a) Check if 'discord' is already in context variables
   b) If not, create it: discord = DiscordModule()
   c) Identify which method matches the instruction
   d) Call that method: result = discord.method_name(...)
   e) Store result appropriately
```

**Perché funziona**: Fornisce un piano passo-passo su misura per l'istruzione specifica.

### 5. **Ripetizione dei Concetti Chiave**
- "DO NOT reimplement" ripetuto 3 volte
- "use pre-defined methods" ripetuto 2 volte
- "module's methods" menzionato 4 volte

**Perché funziona**: La ripetizione rinforza i concetti nell'attenzione dell'LLM.

### 6. **Separazione Visiva**
```
======================================================================
CRITICAL MODULE USAGE REQUIREMENTS:
======================================================================
```

**Perché funziona**: Fa risaltare la sezione importante nel contesto del prompt.

### 7. **Numerazione e Struttura**
- 8 punti numerati
- Sottopunti con lettere (a, b, c...)
- Sezioni chiare (MANDATORY, FORBIDDEN, EXAMPLES)

**Perché funziona**: Facilita la comprensione e il seguimento delle istruzioni.

## Confronto Dimensioni Prompt

### Prima
```
Task hint: ~150 caratteri
Module info: ~6,400 caratteri
Requirements: ~300 caratteri
-------------------------
TOTALE: ~6,850 caratteri
```

### Dopo
```
Task hint: ~150 caratteri
Module info: ~6,400 caratteri
Requirements: ~2,200 caratteri (7x più grande)
-------------------------
TOTALE: ~8,750 caratteri (+27%)
```

**Trade-off**: +27% di dimensione prompt, ma **molto più efficace** nel guidare l'LLM.

## Impatto Atteso

### Prima (comportamento osservato)
```python
# LLM spesso generava:
import requests
webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
payload = {"content": "Hello World"}
response = requests.post(webhook_url, json=payload)
```
❌ Reimplementa la funzionalità
❌ Usa direttamente requests
❌ Ignora il modulo documentato

### Dopo (comportamento atteso)
```python
# LLM dovrebbe generare:
from aibasic.modules import DiscordModule
discord = DiscordModule()
result = discord.send_message("Hello World")
```
✅ Usa il modulo
✅ Chiama il metodo appropriato
✅ Codice semplice e corretto

## Quando si Applica

Questa sezione direttiva viene aggiunta SOLO quando:
1. Il task type è esplicito (es. `(discord)`)
2. Il modulo ha metadata ricchi (`module_metadata` presente)

**Moduli con metadata** (ottengono istruzioni direttive):
- ✅ Discord
- ✅ Telegram

**Moduli senza metadata** (usano formato legacy):
- ⏳ PostgreSQL
- ⏳ MySQL
- ⏳ Tutti gli altri 32 moduli

## Test

### Verifica Prompt
```bash
python test_directive_prompt.py
```

Mostra:
- ✅ Sezione CRITICAL MODULE USAGE REQUIREMENTS completa
- ✅ Confronto BEFORE/AFTER
- ✅ Esempi CORRECT vs WRONG
- ✅ Spiegazione perché dovrebbe funzionare meglio

### Test Reale Compilazione
```bash
# Crea test file
echo '10 (discord) send message "Test"' > test.aib

# Compila
python src/aibasic/aibasicc.py -c aibasic.conf -i test.aib -o output.py

# Verifica output
cat output.py | grep "DiscordModule"  # Dovrebbe trovarlo
cat output.py | grep "requests.post"  # NON dovrebbe trovarlo
```

## Metriche di Successo

### Obiettivi
1. ✅ **80%+ del codice generato** usa i metodi del modulo
2. ✅ **<20% del codice** reimplementa funzionalità
3. ✅ **Import corretti** (`from aibasic.modules import ...`)
4. ✅ **Nessun uso diretto** di `requests`, `discord.py`, ecc.

### Come Misurare
Compilare 20 istruzioni Discord/Telegram e contare:
- Quante usano `DiscordModule()`/`TelegramModule()`
- Quante usano `requests.post()` direttamente
- Quante chiamano metodi del modulo

**Target**: >16/20 (80%) usano correttamente i moduli

## Prossimi Passi

### Se funziona bene ✅
1. Mantenere questo formato per tutti i futuri moduli con metadata
2. Aggiornare moduli esistenti per seguire questo pattern
3. Documentare come best practice

### Se necessita ulteriori miglioramenti ⚠️
1. Aggiungere più esempi specifici per ogni metodo
2. Includere estratti di codice dei metodi del modulo
3. Aumentare ancora di più la ripetizione dei concetti chiave
4. Aggiungere penalità esplicite ("violando queste regole produrrai codice non funzionante")

## Conclusione

Il prompt è stato **radicalmente migliorato** con:
- ✅ Istruzioni 7x più lunghe e dettagliate
- ✅ Linguaggio imperativo (MANDATORY, FORBIDDEN)
- ✅ Esempi concreti corretti e sbagliati
- ✅ Step-by-step per l'istruzione specifica
- ✅ Ripetizione di concetti chiave
- ✅ Separazione visiva forte

**Aspettativa**: L'LLM dovrebbe ora **consistentemente** utilizzare i metodi del modulo invece di reimplementare la funzionalità da zero.

---

**Data implementazione**: 2025-01-17
**File modificato**: `src/aibasic/aibasicc.py` (linee 887-945)
**Status**: ✅ Implementato, in attesa di test reali
