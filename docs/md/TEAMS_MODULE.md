# Microsoft Teams Module Documentation

## Overview

The Microsoft Teams module enables AIbasic programs to send messages, alerts, and rich adaptive cards to Microsoft Teams channels. It supports both simple webhook-based messaging and full Microsoft Graph API integration.

## Features

✅ **Simple Messages** - Send text messages with titles and colors
✅ **Alert Messages** - Send color-coded alerts (info, warning, error, success)
✅ **Adaptive Cards** - Send rich, interactive cards
✅ **Status Cards** - Send formatted status updates
✅ **Notifications** - Send notifications with key-value facts
✅ **Data Tables** - Display tabular data in cards
✅ **Webhook Support** - Simple incoming webhook integration
✅ **Graph API Support** - Full API access with authentication
✅ **Automatic Retries** - Built-in retry logic for reliability
✅ **Thread Safety** - Singleton pattern for efficient resource usage

## Configuration

### Option 1: Incoming Webhook (Recommended for Getting Started)

```ini
[teams]
WEBHOOK_URL = https://your-org.webhook.office.com/webhookb2/xxx-xxx-xxx/IncomingWebhook/xxx/xxx
```

**How to get a webhook URL:**
1. Go to your Teams channel
2. Click "..." (More options) > Connectors
3. Search for "Incoming Webhook" and click Configure
4. Name your webhook (e.g., "AIbasic Notifications")
5. Optionally upload an icon
6. Click Create
7. Copy the webhook URL provided

### Option 2: App-Based Authentication (Advanced)

```ini
[teams]
TENANT_ID = xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
CLIENT_ID = xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
CLIENT_SECRET = your-client-secret-here
TEAM_ID = xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
CHANNEL_ID = 19:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx@thread.tacv2
```

**How to set up app-based auth:**
1. Register an app in Azure Portal (Azure Active Directory > App registrations)
2. Grant API permissions: `ChannelMessage.Send` (Application permission)
3. Create a client secret (Certificates & secrets > New client secret)
4. Note your Tenant ID, Application (client) ID, and client secret value
5. Find Team ID and Channel ID from Teams channel URL

### Additional Settings

```ini
[teams]
# Connection settings
TIMEOUT = 30
MAX_RETRIES = 3
RETRY_BACKOFF = 1.0

# Proxy (optional)
PROXY = http://proxy.example.com:8080
```

## Task Type

Use the `(teams)` task type hint in your AIbasic programs:

```aibasic
10 (teams) send message to channel
20 (teams) send alert with severity "warning"
30 (teams) send status card
```

## Usage Examples

### 1. Simple Message

```aibasic
10 (teams) send message to channel
20 (teams) set title to "Pipeline Completed"
30 (teams) set text to "The daily ETL pipeline completed successfully"
40 (teams) set color to "107C10"
50 print "Message sent"
```

**Colors:**
- `0078D4` - Blue (default, Teams theme color)
- `107C10` - Green (success)
- `FFB900` - Yellow (warning)
- `E81123` - Red (error)

### 2. Alert Messages

```aibasic
# Warning alert
10 (teams) send alert with message "High CPU usage detected"
20 (teams) set severity to "warning"
30 (teams) set title to "System Alert"

# Error alert
40 (teams) send alert with message "Database connection failed"
50 (teams) set severity to "error"

# Success alert
60 (teams) send alert with message "Backup completed"
70 (teams) set severity to "success"

# Info alert
80 (teams) send alert with message "Maintenance window starting"
90 (teams) set severity to "info"
```

**Severity levels:**
- `info` - Blue, informational
- `warning` - Yellow, warnings
- `error` - Red, errors
- `success` - Green, success messages

### 3. Status Card

```aibasic
10 (teams) send status card
20 (teams) set title to "Database Backup"
30 (teams) set status to "Success"
40 (teams) add detail "Database" with value "production_db"
50 (teams) add detail "Size" with value "150 GB"
60 (teams) add detail "Duration" with value "45 minutes"
70 (teams) add detail "Location" with value "s3://backups/2025-01-20/"
```

**Status values:**
- `Success` - Green
- `Failed` / `Error` - Red
- `Running` - Yellow
- `Pending` - Blue

### 4. Notification with Facts

```aibasic
10 (teams) send notification
20 (teams) set title to "Sales Report"
30 (teams) set text to "Daily sales summary"
40 (teams) add fact "Total Sales" with value "$125,000"
50 (teams) add fact "Orders" with value "342"
60 (teams) add fact "Average Order" with value "$365"
70 (teams) add fact "Top Product" with value "Laptop Pro"
```

### 5. Data Table Card

```aibasic
10 (teams) create data table card
20 (teams) set title to "Top 5 Customers"
30 (teams) set headers to list "Customer" "Revenue" "Orders"
40 (teams) add row "Acme Corp" "$50,000" "45"
50 (teams) add row "Global Tech" "$38,500" "32"
60 (teams) add row "Pacific Trade" "$29,000" "28"
70 (teams) add row "Euro Systems" "$22,500" "19"
80 (teams) add row "Asia Imports" "$18,750" "15"
90 (teams) send card
```

### 6. Pipeline Status with Error Handling

```aibasic
10 on error goto 900

20 set pipeline_name to "Daily ETL Pipeline"
30 set pipeline_status to "Running"
40 set records_processed to 125000

50 (teams) send status card
60 (teams) set title to pipeline_name
70 (teams) set status to pipeline_status
80 (teams) add detail "Records Processed" with value records_processed
90 (teams) add detail "Start Time" with value "2025-01-20 02:00:00"

100 goto 999

900 print "ERROR: Failed to send notification"
910 print "Error:" and _last_error
920 (teams) send alert with message "Pipeline notification failed"
930 (teams) set severity to "error"

999 print "Complete"
```

### 7. Real-World Example: ETL Pipeline Monitoring

```aibasic
10 on error goto 900

# Extract
20 (postgres) query "SELECT * FROM orders WHERE date = today"
30 set order_count to row count

# Send start notification
40 (teams) send notification
50 (teams) set title to "ETL Pipeline Started"
60 (teams) add fact "Orders to Process" with value order_count
70 (teams) add fact "Start Time" with value current_time

# Transform and Load
80 (df) process data
90 (mongodb) insert documents

# Send success notification
100 (teams) send status card
110 (teams) set title to "ETL Pipeline"
120 (teams) set status to "Success"
130 (teams) add detail "Orders Processed" with value order_count
140 (teams) add detail "Duration" with value "2 minutes"

150 goto 999

# Error handler
900 (teams) send alert with message "ETL pipeline failed"
910 (teams) set severity to "error"
920 (teams) add detail "Error" with value _last_error
930 (teams) add detail "Line" with value _last_error_line

999 print "ETL pipeline complete"
```

## Python API

For advanced use cases, you can use the Teams module directly in Python:

```python
from aibasic.modules import TeamsModule

# Initialize with webhook
teams = TeamsModule(
    webhook_url="https://your-webhook-url"
)

# Send simple message
teams.send_message(
    title="Pipeline Completed",
    text="All tasks finished successfully",
    color="107C10"
)

# Send alert
teams.send_alert(
    message="High memory usage detected",
    severity="warning",
    title="System Alert"
)

# Send status card
teams.send_status_card(
    title="Backup Job",
    status="Success",
    details={
        "Database": "production",
        "Size": "150 GB",
        "Duration": "45 min"
    }
)

# Send notification with facts
teams.send_notification(
    title="Sales Summary",
    text="Q1 2025 Results",
    facts=[
        {"name": "Revenue", "value": "$1.2M"},
        {"name": "Growth", "value": "+15%"}
    ]
)

# Send adaptive card
card = {
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "type": "AdaptiveCard",
    "version": "1.4",
    "body": [
        {
            "type": "TextBlock",
            "text": "Custom Card",
            "weight": "Bolder",
            "size": "Large"
        }
    ]
}
teams.send_adaptive_card(card)
```

## Adaptive Cards

For complex card layouts, you can create custom adaptive cards:

```python
card = {
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "type": "AdaptiveCard",
    "version": "1.4",
    "body": [
        {
            "type": "TextBlock",
            "text": "Build Status",
            "weight": "Bolder",
            "size": "Large"
        },
        {
            "type": "FactSet",
            "facts": [
                {"title": "Branch", "value": "main"},
                {"title": "Commit", "value": "abc123"},
                {"title": "Duration", "value": "5m 23s"}
            ]
        }
    ],
    "actions": [
        {
            "type": "Action.OpenUrl",
            "title": "View Build",
            "url": "https://ci.example.com/build/123"
        }
    ]
}
```

Learn more about adaptive cards at [adaptivecards.io](https://adaptivecards.io)

## Best Practices

### 1. Use Webhooks for Simple Use Cases
Incoming webhooks are easier to set up and sufficient for most notification needs.

### 2. Use Appropriate Severity Levels
- `info` - General information, updates
- `warning` - Issues that need attention but aren't critical
- `error` - Critical failures that require immediate action
- `success` - Confirmations of successful operations

### 3. Include Relevant Context
Always include enough information in notifications:
```aibasic
10 (teams) send status card
20 (teams) set title to "Backup Job"
30 (teams) set status to "Failed"
40 (teams) add detail "Server" with value "db-prod-01"
50 (teams) add detail "Error" with value error_message
60 (teams) add detail "Timestamp" with value current_time
70 (teams) add detail "Contact" with value "ops-team@company.com"
```

### 4. Use Error Handling
Always wrap Teams operations in error handlers:
```aibasic
10 on error goto 900
20 (teams) send message
...
900 print "Teams notification failed:" and _last_error
```

### 5. Rate Limiting
Be mindful of rate limits:
- Webhook: ~100 messages per minute per webhook
- Graph API: Varies by license, typically 4 requests/second

### 6. Message Threading
For related messages, consider using threaded conversations in Graph API mode.

## Troubleshooting

### Webhook Returns 400 Error
- Check webhook URL is correct
- Verify JSON payload is valid
- Ensure webhook hasn't been deleted in Teams

### Graph API Authentication Fails
- Verify tenant ID, client ID, client secret
- Check app permissions in Azure Portal
- Ensure admin consent has been granted

### Messages Not Appearing
- Check channel exists and webhook is configured
- Verify team/channel IDs are correct
- Check Teams notifications aren't disabled

### Timeout Errors
- Increase timeout setting in configuration
- Check network connectivity
- Verify proxy settings if using proxy

## Security Considerations

### Webhook URLs
- ⚠️ Webhook URLs are sensitive - treat like passwords
- Don't commit webhook URLs to source control
- Use environment variables or secure config management
- Rotate webhooks if compromised

### Client Secrets
- ⚠️ Never commit client secrets to source control
- Use Azure Key Vault or similar for secret storage
- Rotate secrets regularly
- Use managed identities when possible

### Message Content
- Don't include sensitive data in messages
- Use secure references instead of actual secrets
- Be aware messages are stored in Teams

## Integration with Other Modules

### Teams + Database Monitoring

```aibasic
10 (postgres) query "SELECT COUNT(*) FROM failed_jobs"
20 if row_count > 10 jump to line 100
30 goto 999

100 (teams) send alert with message "High failure rate detected"
110 (teams) set severity to "error"
120 (teams) add detail "Failed Jobs" with value row_count

999 print "Monitor complete"
```

### Teams + S3 Backup Notifications

```aibasic
10 (s3) upload file "backup.tar.gz" to bucket "backups"
20 (s3) get object size
30 (teams) send status card
40 (teams) set title to "Backup Completed"
50 (teams) add detail "File" with value "backup.tar.gz"
60 (teams) add detail "Size" with value object_size
```

### Teams + Error Notification Pipeline

```aibasic
10 on error goto 900

20 (postgres) complex query
30 (df) data transformation
40 (mongodb) bulk insert

50 (teams) send alert with message "Pipeline succeeded"
60 (teams) set severity to "success"
70 goto 999

900 (teams) send alert with message "Pipeline failed"
910 (teams) set severity to "error"
920 (teams) add detail "Error" with value _last_error
930 (teams) add detail "Line" with value _last_error_line

999 print "Done"
```

## Resources

- [Microsoft Teams Webhooks](https://docs.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/what-are-webhooks-and-connectors)
- [Adaptive Cards Designer](https://adaptivecards.io/designer/)
- [Microsoft Graph API](https://docs.microsoft.com/en-us/graph/api/channel-post-messages)
- [Teams App Registration](https://docs.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app)

---

**AIbasic v1.0** - Microsoft Teams Module Documentation
