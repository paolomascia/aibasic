# Slack Module Documentation

## Overview

The Slack module enables AIbasic programs to send messages, alerts, rich blocks, and files to Slack channels and users. It supports both simple webhook-based messaging and full Slack API integration.

## Features

✅ **Simple Messages** - Send text messages to channels
✅ **Alert Messages** - Send color-coded alerts (info, warning, error, success)
✅ **Rich Messages** - Send messages with attachments and fields
✅ **Block Kit** - Send interactive Block Kit messages
✅ **File Uploads** - Upload files to channels
✅ **Message Updates** - Update existing messages
✅ **Reactions** - Add emoji reactions to messages
✅ **Threaded Messages** - Reply in threads
✅ **Webhook Support** - Simple incoming webhook integration
✅ **Bot Token Support** - Full API access with bot tokens
✅ **Automatic Retries** - Built-in retry logic for reliability
✅ **Thread Safety** - Singleton pattern for efficient resource usage

## Configuration

### Option 1: Incoming Webhook (Recommended for Getting Started)

```ini
[slack]
WEBHOOK_URL = https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX
```

**How to get a webhook URL:**
1. Go to https://api.slack.com/messaging/webhooks
2. Click "Create your Slack app"
3. Choose "From scratch", name your app, select workspace
4. Go to "Incoming Webhooks" and activate it
5. Click "Add New Webhook to Workspace"
6. Select a channel and authorize
7. Copy the webhook URL

### Option 2: Bot Token (Advanced)

```ini
[slack]
BOT_TOKEN = xoxb-your-bot-token-here
DEFAULT_CHANNEL = #general
```

**How to set up bot token:**
1. Go to https://api.slack.com/apps
2. Create new app or select existing
3. Go to "OAuth & Permissions"
4. Add bot token scopes:
   - `chat:write` - Send messages
   - `files:write` - Upload files
   - `reactions:write` - Add reactions
   - `chat:write.customize` - Customize username/icon
5. Install app to workspace
6. Copy Bot User OAuth Token (starts with xoxb-)

### Additional Settings

```ini
[slack]
# Connection settings
TIMEOUT = 30
MAX_RETRIES = 3
RETRY_BACKOFF = 1.0

# Proxy (optional)
PROXY = http://proxy.example.com:8080
```

## Task Type

Use the `(slack)` task type hint in your AIbasic programs:

```aibasic
10 (slack) send message to channel "#general"
20 (slack) send alert with severity "warning"
30 (slack) upload file to channel
```

## Usage Examples

### 1. Simple Message

```aibasic
10 (slack) send message to channel "#general"
20 (slack) set text to "Hello from AIbasic! Pipeline completed successfully."
30 print "Message sent"
```

### 2. Message with Custom Icon

```aibasic
10 (slack) send message to channel "#notifications"
20 (slack) set text to "Deployment to production completed"
30 (slack) set username to "Deploy Bot"
40 (slack) set icon emoji to ":rocket:"
```

**Common emojis:**
- `:white_check_mark:` - Checkmark
- `:warning:` - Warning sign
- `:x:` - X mark
- `:rocket:` - Rocket
- `:robot_face:` - Robot
- `:chart_with_upwards_trend:` - Chart

### 3. Alert Messages

```aibasic
# Warning alert
10 (slack) send alert with message "High CPU usage detected"
20 (slack) set severity to "warning"
30 (slack) set title to "System Alert"
40 (slack) set channel to "#alerts"

# Error alert
50 (slack) send alert with message "Database connection failed"
60 (slack) set severity to "error"

# Success alert
70 (slack) send alert with message "Backup completed"
80 (slack) set severity to "success"
```

**Severity levels:**
- `info` - Green
- `warning` - Yellow
- `error` / `danger` - Red
- `success` - Green

### 4. Status Message with Fields

```aibasic
10 (slack) send status message
20 (slack) set title to "Database Backup"
30 (slack) set status to "Success"
40 (slack) add field "Database" with value "production_db"
50 (slack) add field "Size" with value "150 GB"
60 (slack) add field "Duration" with value "45 minutes"
70 (slack) add field "Location" with value "s3://backups/"
80 (slack) set channel to "#backups"
```

### 5. Rich Message with Attachment

```aibasic
10 (slack) send rich message
20 (slack) set title to "Sales Report - Q1 2025"
30 (slack) set text to "Quarterly sales performance"
40 (slack) set color to "#36a64f"
50 (slack) add field "Revenue" with value "$1,250,000"
60 (slack) add field "Orders" with value "3,420"
70 (slack) add field "Growth" with value "+15%"
80 (slack) set footer to "Sales Analytics"
90 (slack) set channel to "#sales"
```

**Color codes:**
- `#36a64f` - Green
- `#ffcc00` - Yellow/Warning
- `#ff0000` - Red/Error
- `#0078D4` - Blue/Info

### 6. Block Kit Messages

```aibasic
10 (slack) create block message
20 (slack) add header block with text "Pipeline Report"
30 (slack) add divider block
40 (slack) add section block with text "*Status:* Success :white_check_mark:"
50 (slack) add fields block with values:
60 (slack) field "*Records:* 125,000"
70 (slack) field "*Duration:* 2 hours"
80 (slack) field "*Errors:* 0"
90 (slack) field "*Success Rate:* 100%"
100 (slack) send blocks to channel "#pipelines"
```

### 7. File Upload

```aibasic
10 (slack) upload file "report.csv"
20 (slack) set title to "Daily Sales Report"
30 (slack) set initial comment to "Today's sales data"
40 (slack) set channel to "#reports"
50 print "File uploaded"
```

### 8. Threaded Message

```aibasic
10 (slack) send message to channel "#support"
20 (slack) set text to "Ticket #12345 resolved"
30 save message timestamp to thread_ts

40 (slack) send message to channel "#support"
50 (slack) set text to "Resolution: Reset user password"
60 (slack) set thread timestamp to thread_ts
```

### 9. Error Handling Example

```aibasic
10 on error goto 900

20 (postgres) query "SELECT COUNT(*) FROM orders"
30 set order_count to result

40 if order_count > 1000 jump to line 100

50 (slack) send alert with message "Low order count"
60 (slack) set severity to "warning"
70 goto 999

100 (slack) send message to channel "#sales"
110 (slack) set text to "Orders processed:" and order_count
120 goto 999

900 print "ERROR:" and _last_error
910 (slack) send alert with message "Pipeline failed"
920 (slack) set severity to "error"
930 (slack) add field "Error" with value _last_error
940 (slack) add field "Line" with value _last_error_line

999 print "Complete"
```

### 10. Real-World ETL Pipeline Monitoring

```aibasic
10 on error goto 900

# Send start notification
20 (slack) send message to channel "#pipelines"
30 (slack) set text to ":hourglass: ETL Pipeline starting..."

# Extract
40 (postgres) query "SELECT * FROM orders"
50 set orders_count to row count

# Transform
60 (df) process data
70 (df) calculate metrics

# Load
80 (mongodb) insert documents

# Success notification
90 (slack) send status message
100 (slack) set title to "ETL Pipeline - SUCCESS"
110 (slack) set status to "Success"
120 (slack) add field "Orders" with value orders_count
130 (slack) add field "Duration" with value "2m 15s"
140 (slack) set channel to "#pipelines"

150 goto 999

# Error handler
900 (slack) send alert with message "ETL Pipeline Failed"
910 (slack) set severity to "error"
920 (slack) add field "Error" with value _last_error
930 (slack) add field "Line" with value _last_error_line
940 (slack) set channel to "#alerts"

999 print "Pipeline complete"
```

## Python API

For advanced use cases, use the Slack module directly in Python:

```python
from aibasic.modules import SlackModule

# Initialize with webhook
slack = SlackModule(
    webhook_url="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
)

# Send simple message
slack.send_message("Hello from AIbasic!")

# Send alert
slack.send_alert(
    message="High memory usage detected",
    severity="warning",
    title="System Alert",
    channel="#alerts"
)

# Send status message
slack.send_status_message(
    title="Backup Job",
    status="Success",
    fields=[
        {"title": "Database", "value": "production"},
        {"title": "Size", "value": "150 GB"}
    ],
    channel="#backups"
)

# Send rich message
slack.send_rich_message(
    title="Sales Summary",
    text="Q1 2025 Results",
    color="#36a64f",
    fields=[
        {"title": "Revenue", "value": "$1.2M", "short": True},
        {"title": "Growth", "value": "+15%", "short": True}
    ]
)

# Send blocks
blocks = [
    slack.create_header_block("Pipeline Status"),
    slack.create_divider_block(),
    slack.create_section_block("*Status:* Success"),
    slack.create_fields_block([
        "*Records:* 125,000",
        "*Duration:* 2 hours"
    ])
]
slack.send_blocks(blocks, text="Pipeline completed")

# Upload file
slack.upload_file(
    file_path="report.pdf",
    channels="#reports",
    title="Daily Report",
    initial_comment="Here's today's report"
)
```

## Block Kit Builder

Create complex layouts with Block Kit:

**Header Block:**
```python
{"type": "header", "text": {"type": "plain_text", "text": "Title"}}
```

**Section Block:**
```python
{"type": "section", "text": {"type": "mrkdwn", "text": "*Bold* text"}}
```

**Divider:**
```python
{"type": "divider"}
```

**Fields:**
```python
{
    "type": "section",
    "fields": [
        {"type": "mrkdwn", "text": "*Field 1:* Value"},
        {"type": "mrkdwn", "text": "*Field 2:* Value"}
    ]
}
```

Learn more at [Block Kit Builder](https://app.slack.com/block-kit-builder)

## Best Practices

### 1. Use Webhooks for Simple Notifications
Incoming webhooks are easier to set up and sufficient for most notification needs.

### 2. Choose Appropriate Severity Levels
- `info` - General updates, informational messages
- `warning` - Issues that need attention
- `error` - Critical failures
- `success` - Successful operations

### 3. Include Context in Alerts
```aibasic
10 (slack) send alert with message "Database backup failed"
20 (slack) add field "Server" with value "db-prod-01"
30 (slack) add field "Error" with value error_message
40 (slack) add field "Time" with value timestamp
50 (slack) add field "Contact" with value "@ops-team"
```

### 4. Use Error Handling
```aibasic
10 on error goto 900
20 (slack) send message
...
900 print "Slack notification failed:" and _last_error
```

### 5. Use Markdown Formatting
Slack supports markdown-like formatting:
- `*bold*` - **bold**
- `_italic_` - *italic*
- `~strike~` - ~~strikethrough~~
- `` `code` `` - `code`
- ` ```code block``` ` - code block
- `<url|text>` - [text](url)

### 6. Rate Limiting
Be mindful of rate limits:
- Webhook: 1 message per second
- Bot token: Varies by method (typically 1-20 requests/second)

## Troubleshooting

### Webhook Returns "invalid_payload"
- Check JSON payload is valid
- Verify webhook URL is correct
- Ensure text field is not empty

### Bot Token Authentication Fails
- Verify token starts with `xoxb-`
- Check token hasn't been revoked
- Verify app is installed to workspace

### Messages Not Appearing
- Check channel exists and bot has access
- Verify channel name includes # for public channels
- For private channels, invite bot first

### File Upload Fails
- Ensure `files:write` scope is granted
- Check file exists and is readable
- Verify file size is under 1GB

## Security Considerations

### Webhook URLs
- ⚠️ Webhook URLs are sensitive - treat like passwords
- Don't commit to source control
- Use environment variables
- Rotate if compromised

### Bot Tokens
- ⚠️ Never commit tokens to source control
- Use secure storage (Vault, AWS Secrets Manager)
- Rotate regularly
- Use minimal required scopes

### Message Content
- Don't include sensitive data
- Be aware messages are searchable
- Use secure references instead of actual secrets

## Integration with Other Modules

### Slack + Database Monitoring

```aibasic
10 (postgres) query "SELECT COUNT(*) FROM failed_jobs"
20 if row_count > 10 jump to line 100
30 goto 999

100 (slack) send alert with message "High failure rate"
110 (slack) add field "Failed Jobs" with value row_count

999 print "Complete"
```

### Slack + S3 Backup Notifications

```aibasic
10 (s3) upload file "backup.tar.gz"
20 (s3) get object size
30 (slack) send status message
40 (slack) set title to "Backup Complete"
50 (slack) add field "Size" with value object_size
```

### Slack + Multi-Service Pipeline

```aibasic
10 on error goto 900

20 (postgres) extract data
30 (df) transform data
40 (mongodb) load data
50 (s3) archive results

60 (slack) send status message
70 (slack) set status to "Success"
80 (slack) add field "Records" with value record_count

90 goto 999

900 (slack) send alert with severity "error"
910 (slack) add field "Error" with value _last_error

999 print "Done"
```

## Resources

- [Slack API Documentation](https://api.slack.com/)
- [Block Kit Builder](https://app.slack.com/block-kit-builder)
- [Incoming Webhooks](https://api.slack.com/messaging/webhooks)
- [Message Formatting](https://api.slack.com/reference/surfaces/formatting)

---

**AIbasic v1.0** - Slack Module Documentation
