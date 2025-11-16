# Compression Module - Complete Reference

## Overview

The **Compression module** provides comprehensive file compression and decompression capabilities.

**Module Type**: `(compress)`
**Primary Use Cases**: File compression, archiving, backup, data transfer optimization

---

## Configuration

```ini
[compress]
DEFAULT_FORMAT = zip
COMPRESSION_LEVEL = 6
```

---

## Basic Operations

```basic
REM Compress files to ZIP
10 (compress) create zip "archive.zip" from files ["file1.txt", "file2.txt", "document.pdf"]

REM Extract ZIP
20 (compress) extract zip "archive.zip" to "extracted/"

REM Compress to GZIP
30 (compress) compress file "large_file.txt" to "large_file.txt.gz" with format "gzip"

REM Decompress GZIP
40 (compress) decompress file "large_file.txt.gz" to "large_file.txt"

REM Create TAR.GZ
50 (compress) create tar.gz "backup.tar.gz" from directory "data/"

REM Supported formats: ZIP, GZIP, BZIP2, TAR, TAR.GZ, TAR.BZ2, 7Z
```

---

## Module Information

- **Module Name**: CompressionModule
- **Task Type**: `(compress)`
- **Dependencies**: `py7zr>=0.20.0` (for 7Z), built-in for others
