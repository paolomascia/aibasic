# Microsoft Teams Module - Complete Summary

## ✅ What Has Been Created

A complete, production-ready Microsoft Teams integration module for AIbasic with full support for messages, alerts, adaptive cards, and notifications.

## 📁 Files Created

### 1. Module Implementation
- **`src/aibasic/modules/teams_module.py`** (850+ lines)
  - Full Microsoft Teams integration
  - Webhook-based messaging (simple)
  - Microsoft Graph API support (advanced)
  - Adaptive cards support
  - Singleton pattern for resource efficiency
  - Automatic retry logic
  - Thread-safe implementation

### 2. Examples
- **`examples/example_teams.aib`**
  - Simple messages
  - Alert messages (info, warning, error, success)
  - Status cards
  - Notifications with facts
  - Data tables
  - Error handling examples

### 3. Documentation
- **`docs/TEAMS_MODULE.md`** (comprehensive guide)
  - Setup instructions
  - Configuration options
  - Usage examples
  - Python API reference
  - Best practices
  - Troubleshooting

### 4. Configuration
- **`aibasic.conf.example`** (updated)
  - Webhook configuration
  - App-based authentication
  - Advanced settings

### 5. Registration
- **`src/aibasic/modules/__init__.py`** (updated)
  - Module registered and exported
  - Available as `TeamsModule`

### 6. Task Types
- **`docs/md/TASK_TYPES.md`** (updated)
  - New task type: `(teams)`
  - Keywords and examples

## 🎯 Features

### Core Functionality

✅ **Simple Messages**
```aibasic
10 (teams) send message to channel
20 (teams) set title to "Pipeline Completed"
30 (teams) set text to "All tasks finished successfully"
40 (teams) set color to "107C10"
```

✅ **Alert Messages**
```aibasic
10 (teams) send alert with message "High CPU usage"
20 (teams) set severity to "warning"
```
- Severity levels: info, warning, error, success
- Automatic color coding

✅ **Status Cards**
```aibasic
10 (teams) send status card
20 (teams) set title to "Backup Job"
30 (teams) set status to "Success"
40 (teams) add detail "Size" with value "150 GB"
```

✅ **Notifications with Facts**
```aibasic
10 (teams) send notification
20 (teams) set title to "Sales Report"
30 (teams) add fact "Revenue" with value "$125,000"
40 (teams) add fact "Orders" with value "342"
```

✅ **Data Tables**
```aibasic
10 (teams) create data table card
20 (teams) set headers to list "Name" "Value" "Status"
30 (teams) add row "Server 1" "98%" "OK"
40 (teams) send card
```

✅ **Adaptive Cards**
- Full support for Microsoft Adaptive Cards
- Custom layouts and interactivity
- Actions and buttons

### Technical Features

✅ **Dual Authentication**
- Incoming Webhooks (simple, recommended)
- Microsoft Graph API (advanced, full access)

✅ **Reliability**
- Automatic retry with exponential backoff
- Configurable timeouts
- Error handling and logging

✅ **Resource Management**
- Singleton pattern (one instance per process)
- Thread-safe operations
- Connection pooling

✅ **Security**
- Secure token management
- Automatic token refresh
- Proxy support

## 📊 Configuration Options

### Webhook Method (Simple)
```ini
[teams]
WEBHOOK_URL = https://your-org.webhook.office.com/webhookb2/...
```

### App-Based Method (Advanced)
```ini
[teams]
TENANT_ID = xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
CLIENT_ID = xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
CLIENT_SECRET = your-client-secret-here
TEAM_ID = xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
CHANNEL_ID = 19:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx@thread.tacv2
```

### Optional Settings
```ini
[teams]
TIMEOUT = 30
MAX_RETRIES = 3
RETRY_BACKOFF = 1.0
PROXY = http://proxy.example.com:8080
```

## 🎨 Message Types and Colors

| Type | Color | Severity | Use Case |
|------|-------|----------|----------|
| Info | Blue (0078D4) | info | General information |
| Warning | Yellow (FFB900) | warning | Non-critical issues |
| Error | Red (E81123) | error | Critical failures |
| Success | Green (107C10) | success | Successful operations |

## 💡 Real-World Use Cases

### 1. ETL Pipeline Monitoring
```aibasic
10 (postgres) extract data
20 (df) transform data
30 (mongodb) load data
40 (teams) send status card with pipeline metrics
```

### 2. System Alerts
```aibasic
10 (ssh) check server health
20 if cpu_usage > 90 jump to line 100
30 goto 999

100 (teams) send alert with severity "error"
110 (teams) set message to "High CPU usage detected"
```

### 3. Report Distribution
```aibasic
10 (excel) create sales report
20 (s3) upload to storage
30 (teams) send notification with download link
```

### 4. Backup Notifications
```aibasic
10 (postgres) backup database
20 (s3) upload backup file
30 (teams) send status card
40 (teams) add detail "Size" with value backup_size
50 (teams) add detail "Location" with value s3_url
```

### 5. Error Notifications
```aibasic
10 on error goto 900
20 (api) call external service
...
900 (teams) send alert with severity "error"
910 (teams) add detail "Error" with value _last_error
920 (teams) add detail "Line" with value _last_error_line
```

## 📚 Python API

Direct Python usage for advanced scenarios:

```python
from aibasic.modules import TeamsModule

teams = TeamsModule(webhook_url="https://...")

# Simple message
teams.send_message(
    title="Deployment Complete",
    text="Version 1.0 deployed to production",
    color="107C10"
)

# Alert
teams.send_alert(
    message="Database latency increased",
    severity="warning"
)

# Status card
teams.send_status_card(
    title="Backup Job",
    status="Success",
    details={
        "Database": "production",
        "Size": "150 GB",
        "Duration": "45 minutes"
    }
)

# Notification with facts
teams.send_notification(
    title="Q1 Results",
    text="Quarterly metrics",
    facts=[
        {"name": "Revenue", "value": "$1.2M"},
        {"name": "Growth", "value": "+15%"}
    ]
)

# Custom adaptive card
card = {
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "type": "AdaptiveCard",
    "version": "1.4",
    "body": [...]
}
teams.send_adaptive_card(card)
```

## 🔧 Integration with Other Modules

### Teams + PostgreSQL
```aibasic
10 (postgres) query "SELECT COUNT(*) FROM errors"
20 if error_count > 100 jump to line 100
100 (teams) send alert with severity "error"
```

### Teams + MongoDB
```aibasic
10 (mongodb) aggregate pipeline
20 (teams) create data table with results
```

### Teams + S3
```aibasic
10 (s3) upload backup
20 (teams) send notification
30 (teams) add fact "Location" with value s3_url
```

### Teams + Vault
```aibasic
10 (vault) read secret "api-key"
20 (api) call external service with key
30 (teams) send status card with API results
```

## 🚀 Quick Start

### Step 1: Get Webhook URL
1. Open Teams channel
2. Click "..." → Connectors
3. Configure "Incoming Webhook"
4. Copy webhook URL

### Step 2: Configure AIbasic
```ini
[teams]
WEBHOOK_URL = paste-your-webhook-url-here
```

### Step 3: Send Your First Message
```aibasic
10 (teams) send message to channel
20 (teams) set title to "Hello from AIbasic!"
30 (teams) set text to "This is my first Teams notification"
40 print "Message sent!"
```

### Step 4: Run
```bash
python src/aibasic/aibasicc.py -c aibasic.conf -i test.aib -o test.py
python test.py
```

## 📖 Resources

- **Setup Guide**: `docs/TEAMS_MODULE.md`
- **Example Code**: `examples/example_teams.aib`
- **Configuration**: `aibasic.conf.example` → `[teams]` section
- **Task Types**: `docs/md/TASK_TYPES.md` → `teams` task type

### External Resources
- [Microsoft Teams Webhooks](https://docs.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/what-are-webhooks-and-connectors)
- [Adaptive Cards Designer](https://adaptivecards.io/designer/)
- [Microsoft Graph API](https://docs.microsoft.com/en-us/graph/api/channel-post-messages)

## ✨ Summary

The Microsoft Teams module provides:

- ✅ **Complete Integration** - Full Teams messaging capabilities
- ✅ **Multiple Methods** - Webhook and Graph API support
- ✅ **Rich Content** - Messages, alerts, cards, tables
- ✅ **Production Ready** - Retry logic, error handling, logging
- ✅ **Easy to Use** - Natural language AIbasic syntax
- ✅ **Well Documented** - Examples, guides, API reference
- ✅ **Secure** - Token management, authentication options

**Total:** 15 modules now available in AIbasic v1.0! 🎉

---

**AIbasic v1.0** - Microsoft Teams Module Complete
