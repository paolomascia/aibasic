# 🧠 AIBasic Compiler

AIBasic is a natural-language-based scripting language designed to let you write numbered instructions like:

```text
10 read the file customers.csv
20 remove the column email
30 save the dataframe to customers_clean.csv
```

The **AIBasic Compiler** converts these natural instructions into executable **Python code** using:
- a plugin system (for common operations like CSV, DataFrame, REST API)
- and an LLM backend (for more complex or unknown operations)

---

## 🚀 Project Structure

```text
aibasic-compiler/
├── src/
│   └── aibasic/
│       ├── __init__.py
│       ├── compiler.py         ← main compiler engine
│       ├── intent.py           ← intent detection / NLP preprocessor
│       └── plugins/
│           ├── csv_plugin.py
│           ├── df_plugin.py
│           ├── rest_plugin.py
│           └── ...
├── examples/
│   ├── 01_csv_basic.aib
│   ├── 02_df_cleaning.aib
│   └── ...
├── aibasic.conf
├── tests/
│   ├── __init__.py
│   └── test_intent.py
└── README.md
```

---

## ⚙️ 1. Configuration

Before running the compiler, configure the LLM connection inside `aibasic.conf`.

Example:

```ini
API_URL=https://api.openai.com/v1/chat/completions
API_TOKEN=sk-your-token-here
API_VERSION=2025-03-01
MODEL=gpt-5
```

> 💡 Never commit this file to Git — it’s ignored via `.gitignore`.  
> For public repos, create a `aibasic.conf.example` with fake credentials.

---

## 📦 2. Install & Setup

### Option A — Quick local use

```bash
pip install -r requirements.txt
```

### Option B — Developer mode (recommended)

From the project root:

```bash
pip install -e .
```

This lets you run the compiler anywhere using the `aibasic` command.

---

## 🧠 3. Run the Compiler

You can run the compiler in two ways:

### ▶️ A. Using the CLI module directly

```bash
python -m aibasic.cli -c aibasic.conf -i examples/01_csv_basic.aib -o output.py
```

### ▶️ B. Using the Python file directly (if no CLI installed)

```bash
python src/aibasic/compiler.py -c aibasic.conf -i examples/01_csv_basic.aib -o output.py
```

### ▶️ C. Using the installed command (after `pip install -e .`)

```bash
aibasic -c aibasic.conf -i examples/01_csv_basic.aib -o output.py
```

---

## 🧩 4. Mock Mode (No API Calls)

If you want to test the compiler without using the LLM API (faster, offline):

```bash
aibasic -c aibasic.conf -i examples/01_csv_basic.aib -o output.py --mock
```

The compiler will only use the built-in **plugins** (CSV, DataFrame, REST, etc.).

---

## 🏷️ 5. Task Types (New Feature!)

AIBasic now supports **explicit task types** to help the compiler generate more accurate code. Task types are **optional** and can be specified using the format `(task_type)`.

**Example with task types:**

```text
10 (csv) read the file customers.csv
20 (df) filter rows where age > 30
30 (api) call the weather API for New York
40 (excel) create Excel report with results
```

**Without task types** (auto-detection):

```text
10 read the file customers.csv
20 filter rows where age > 30
30 call the weather API for New York
40 create Excel report with results
```

## 🔀 6. Jump/Goto Support (New Feature!)

AIBasic now supports **conditional and unconditional jumps** for control flow, similar to classic BASIC:

**Unconditional jumps:**
```text
10 set x to 0
20 print x
30 goto 50
40 print "This is skipped"
50 print "Jumped here!"
```

**Conditional jumps:**
```text
10 set counter to 0
20 print counter
30 increment counter by 1
40 if counter is less than 5 jump to line 20
50 print "Loop complete!"
```

**Jump syntax options:**
- `goto <line>` - Unconditional jump
- `jump to <line>` - Unconditional jump
- `if <condition> jump to line <line>` - Conditional jump
- `if <condition> goto <line>` - Conditional jump

**Error handling:**
- `on error goto <line>` - Set error handler that catches exceptions
- Access error details via `_last_error` and `_last_error_line`
- Update error handlers dynamically throughout program execution

**Subroutines:**
- `call <line>` - Call a subroutine and save return address
- `return` - Return from subroutine to calling location
- Supports nested subroutine calls with automatic call stack management
- Perfect for creating reusable code blocks and libraries

The compiler automatically generates efficient Python code with function-based dispatch, try-except blocks for error handling, and call stack management for subroutines.

📖 **See [examples/example_jumps.aib](examples/example_jumps.aib) for complete examples** including:
- Simple loops with goto
- Conditional branching
- Multiple conditions
- While-like loops
- Early exit patterns
- Nested conditions
- Error handling with recovery
- Multiple error handlers
- Subroutines and nested calls

📖 **See [TASK_TYPES.md](TASK_TYPES.md) for the complete list of 36 available task types** including:
- Data: `csv`, `excel`, `json`, `xml`, `db`, **`postgres`**, **`mysql`**, **`mongodb`**, **`cassandra`** (with modules)
- Messaging: **`rabbitmq`**, **`kafka`** (with modules), `stream`
- Cache: **`redis`** (with module)
- Search: **`opensearch`** (with module)
- Security: **`vault`** (with module)
- Storage: **`s3`** (with module - AWS S3, MinIO, DigitalOcean Spaces)
- Network: `api`, `web`, **`ssh`** (with module)
- Processing: `df`, `math`, `plot`
- Files: `fs`, `text`, **`compress`** (with module), `pdf`, **`email`** (with module)
- And many more!

### 🔌 New: Modules System

Some task types use **AIBasic modules** - reusable components that provide persistent functionality:

**PostgreSQL Module** (`postgres` task type):
```ini
# Configure in aibasic.conf
[postgres]
HOST = localhost
PORT = 5432
DATABASE = mydb
USER = postgres
PASSWORD = secret
```

**MySQL/MariaDB Module** (`mysql` task type):
```ini
# Configure in aibasic.conf
[mysql]
HOST = localhost
PORT = 3306
DATABASE = mydb
USER = root
PASSWORD = secret
```

**RabbitMQ Module** (`rabbitmq` task type):
```ini
# Configure in aibasic.conf
[rabbitmq]
HOST = localhost
PORT = 5672
VHOST = /
USERNAME = guest
PASSWORD = guest
USE_SSL = false
SSL_VERIFY = true  # Set to false for self-signed certs (dev only)
```

**Kafka Module** (`kafka` task type):
```ini
# Configure in aibasic.conf
[kafka]
BOOTSTRAP_SERVERS = localhost:9092
SECURITY_PROTOCOL = PLAINTEXT
SSL_VERIFY = true  # Set to false for self-signed certs (dev only)
```

**Redis Module** (`redis` task type):
```ini
# Configure in aibasic.conf
[redis]
HOST = localhost
PORT = 6379
DB = 0
PASSWORD = secret
USE_SSL = false
SSL_VERIFY = true  # Set to false for self-signed certs (dev only)
```

**OpenSearch Module** (`opensearch` task type):
```ini
# Configure in aibasic.conf
[opensearch]
HOST = localhost
PORT = 9200
USERNAME = admin
PASSWORD = admin
USE_SSL = false
VERIFY_CERTS = true  # Set to false for self-signed certs (dev only)
# For AWS OpenSearch Service:
# USE_AWS_AUTH = true
# AWS_REGION = us-east-1
```

**Example Usage:**
```aibasic
10 (postgres) query all customers from postgres
20 (mysql) insert into mysql table users values ('Alice', 30)
30 (rabbitmq) publish message to rabbitmq exchange events
40 (kafka) publish event to kafka topic user_events
50 (redis) cache result in redis with key customers:all for 3600 seconds
60 (opensearch) index document in opensearch index products
70 (opensearch) search opensearch for products matching "laptop"
80 (mysql) call mysql stored procedure get_monthly_report
```

Modules provide:
- Connection pooling and resource management
- Persistent state across instructions
- Configuration-driven behavior
- Thread-safe operations

📖 See [modules/README.md](src/aibasic/modules/README.md) for details on creating custom modules.

---

## 🧱 6. Example

**Input file** (`examples/01_csv_basic.aib`):

```text
10 read the file customers.csv into a dataframe
20 remove the column email
30 save the dataframe to customers_clean.csv
```

**Command:**
```bash
python -m aibasic.cli -c aibasic.conf -i examples/01_csv_basic.aib -o output.py
```

**Output file** (`output.py`):

```python
import pandas as pd

# 10 read the file customers.csv into a dataframe
df = pd.read_csv("customers.csv")

# 20 remove the column email
df = df.drop(columns=["email"])

# 30 save the dataframe to customers_clean.csv
df.to_csv("customers_clean.csv", index=False)
```

---

## 🔍 7. Testing

Run unit tests using **pytest**:

```bash
pytest -v
```

Example test file: `tests/test_intent.py`

```python
from aibasic.intent import determine_intent

def test_load_csv_intent():
    hint = determine_intent("read the file customers.csv into a dataframe")
    assert hint.intent == "load_csv"
    assert hint.filename == "customers.csv"
```

---

## 🧠 8. Project Philosophy

AIBasic aims to make programming as close to human reasoning as possible:

> “Write what you mean — let the compiler figure out the code.”

Each line is:
1. An **instruction** in plain English (or your language)
2. Translated by **plugins or an LLM**
3. Stored with a **context** that grows across steps

This allows incremental compilation where every instruction knows the previous state of your data.

---

## 🧰 9. Useful Commands Summary

| Action | Command |
|--------|----------|
| Compile a `.aib` program | `aibasic -c aibasic.conf -i examples/01_csv_basic.aib -o output.py` |
| Run without LLM (mock) | `aibasic --mock -c aibasic.conf -i examples/... -o output.py` |
| Run via module | `python -m aibasic.cli -c aibasic.conf -i ... -o ...` |
| Install locally | `pip install -e .` |
| Run tests | `pytest` |

---

## 🧩 10. Example Plugins

Plugins are located under `src/aibasic/plugins/`.  
Each plugin can intercept a certain type of instruction and directly produce code without calling the LLM.

Examples:
- `csv_plugin.py` → handles CSV read/write
- `df_plugin.py` → handles DataFrame transformations
- `rest_plugin.py` → handles REST API calls

You can easily add your own by creating a new file and registering it in the plugin registry.

---

## 🧠 11. Future Plans

- Add multilingual support for instructions (Italian, Spanish, etc.)
- Add local embedding model for smarter intent detection
- Integrate with Jupyter for interactive code generation
- Add dependency graph and flow visualization

---

## 📄 12. License

MIT License © 2025  
Developed by **[Your Name / Team]**
