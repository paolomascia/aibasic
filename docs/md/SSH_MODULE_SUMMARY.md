# SSH/SFTP Module - Complete Reference

## Overview

The **SSH module** provides comprehensive SSH and SFTP capabilities for remote server operations.

**Module Type**: `(ssh)`
**Primary Use Cases**: Remote command execution, file transfer, server automation, deployment

---

## Configuration

```ini
[ssh]
HOST = server.example.com
PORT = 22
USERNAME = admin
PASSWORD = secret
KEY_FILE = /path/to/private_key
```

---

## Basic Operations

```basic
REM Execute remote command
10 (ssh) execute command "ls -la /var/www"

REM Upload file
20 (ssh) upload file "local.txt" to "/remote/path/file.txt"

REM Download file
30 (ssh) download "/remote/path/file.txt" to "local.txt"

REM Multiple commands
40 (ssh) execute command "cd /var/www && git pull && systemctl restart nginx"
```

---

## Module Information

- **Module Name**: SSHModule
- **Task Type**: `(ssh)`
- **Dependencies**: `paramiko>=3.0.0`
