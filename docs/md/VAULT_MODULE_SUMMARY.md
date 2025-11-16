# HashiCorp Vault Module - Complete Reference

## Overview

The **Vault module** provides comprehensive HashiCorp Vault integration for secrets management.

**Module Type**: `(vault)`
**Primary Use Cases**: Secrets storage, API keys, passwords, certificates, encryption keys

---

## Configuration

```ini
[vault]
VAULT_ADDR = http://localhost:8200
VAULT_TOKEN = your_token
MOUNT_POINT = secret
KV_VERSION = 2
```

---

## Basic Operations

```basic
REM Store secret
10 (vault) write secret "database/postgres" with data {"username": "admin", "password": "secret123"}

REM Read secret
20 (vault) read secret "database/postgres"
30 LET db_password = RESULT["password"]

REM Delete secret
40 (vault) delete secret "database/postgres"

REM List secrets
50 (vault) list secrets at path "database/"
```

---

## Module Information

- **Module Name**: VaultModule
- **Task Type**: `(vault)`
- **Dependencies**: `hvac>=1.2.0`
