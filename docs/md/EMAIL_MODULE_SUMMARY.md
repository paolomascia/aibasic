# Email Module - Complete Reference

## Overview

The **Email module** provides comprehensive email sending capabilities with SMTP support.

**Module Type**: `(email)`
**Primary Use Cases**: Notifications, alerts, reports, newsletters, transactional emails

---

## Configuration

```ini
[email]
SMTP_HOST = smtp.gmail.com
SMTP_PORT = 587
USERNAME = your_email@gmail.com
PASSWORD = your_password
FROM_EMAIL = noreply@example.com
USE_TLS = true
```

---

## Basic Operations

```basic
REM Send simple email
10 (email) send to "user@example.com" subject "Welcome" body "Welcome to our service!"

REM Send with HTML
20 (email) send to "user@example.com" subject "Report" html "<h1>Monthly Report</h1><p>Details...</p>"

REM Send with attachment
30 (email) send to "user@example.com" subject "Invoice" body "See attached" with attachment "invoice.pdf"

REM Send to multiple recipients
40 (email) send to "user1@example.com, user2@example.com" subject "Announcement" body "..."
```

---

## Module Information

- **Module Name**: EmailModule
- **Task Type**: `(email)`
- **Dependencies**: Built-in (`smtplib`)
