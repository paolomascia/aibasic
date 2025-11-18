# Telegram Module - Complete Reference

## Overview

The **Telegram module** provides comprehensive Telegram bot integration via Bot API for notifications, alerts, and team communication.

**Module Type**: `(telegram)`
**Primary Use Cases**: Notifications, alerts, monitoring, bot automation, team communication

---

## Configuration

```ini
[telegram]
BOT_TOKEN = 123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
CHAT_ID =
PARSE_MODE = Markdown
DISABLE_NOTIFICATION = false
DISABLE_WEB_PAGE_PREVIEW = false
```

**Setup Steps:**
1. Message @BotFather on Telegram
2. Send `/newbot` command
3. Follow instructions to create your bot
4. Copy the bot token
5. Send a message to your bot
6. Visit `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
7. Find your chat ID in the JSON response

---

## Basic Operations

```basic
REM Send simple message
10 (telegram) send message "Hello from AIbasic!"

REM Send notification
20 (telegram) send notification with title "Success" and message "Operation completed" and level "success"

REM Send alert
30 (telegram) send alert "Server CPU high!"

REM Send status update
40 (telegram) send status update for service "Web Server" with status "online"

REM Send log message
50 (telegram) send log with level "ERROR" and message "Failed to connect" and source "app.py"
```

---

## Message Formatting

### Markdown

```basic
10 (telegram) send message "*Bold* _italic_ `code` ```code block```"
20 (telegram) send message "[Link text](https://example.com)"
```

### HTML

```basic
10 (telegram) send message "<b>Bold</b> <i>italic</i> <code>code</code>" with parse_mode "HTML"
```

---

## Media Support

```basic
REM Send photo
10 (telegram) send photo "https://example.com/image.jpg" with caption "Photo caption"

REM Send document
20 (telegram) send document "report.pdf" with caption "Monthly report"

REM Send video
30 (telegram) send video "demo.mp4" with caption "Product demo"

REM Send location
40 (telegram) send location 40.7128 -74.0060
```

---

## Message Management

```basic
REM Send and edit
10 LET response = (telegram) send message "Original"
20 LET msg_id = response["result"]["message_id"]
30 (telegram) edit message msg_id with text "Edited!"

REM Pin message
40 (telegram) pin message msg_id

REM Delete message
50 (telegram) delete message msg_id
```

---

## Notifications & Alerts

```basic
REM Info notification (ℹ️ blue)
10 (telegram) send notification with title "Info" and message "Update available" and level "info"

REM Success notification (✅ green)
20 (telegram) send notification with title "Success" and message "Deployment complete" and level "success"

REM Warning notification (⚠️ orange)
30 (telegram) send notification with title "Warning" and message "Disk space low" and level "warning"

REM Error notification (❌ red)
40 (telegram) send notification with title "Error" and message "Connection failed" and level "error"

REM Alert with mentions
50 LET users = ["username1", "username2"]
60 (telegram) send alert "Urgent!" with mention_users users
```

---

## Common Use Cases

### Error Monitoring

```basic
10 ON ERROR GOTO 100
20 REM ... code ...

100 LET msg = "Error: " + STR(_last_error) + "\nLine: " + STR(_last_error_line)
110 (telegram) send notification with title "Application Error" and message msg and level "error"
120 (telegram) send alert "Critical error detected!"
```

### Server Health Monitoring

```basic
10 LET msg = "*CPU:* 45%\n*Memory:* 62%\n*Disk:* 78%\n*Status:* 🟢 Healthy"
20 (telegram) send notification with title "Health Report" and message msg and level "info"

30 IF disk > 75 THEN
40   (telegram) send notification with title "Disk Warning" and message "Disk at " + STR(disk) + "%" and level "warning"
50 END IF
```

### Deployment Notifications

```basic
10 LET msg = "*Environment:* Production\n*Version:* v2.5.0\n*Deployer:* CI/CD"
20 (telegram) send notification with title "Deployment Started" and message msg and level "info"

30 REM ... deployment ...

40 LET msg = "*Duration:* 2 min\n*Status:* ✅ Success"
50 (telegram) send notification with title "Deployment Complete" and message msg and level "success"
```

### Backup Status

```basic
10 LET msg = "*Database:* prod_db\n*Size:* 2.5 GB\n*Duration:* 12 min\n*Status:* ✅ Success"
20 (telegram) send notification with title "Backup Complete" and message msg and level "success"
```

---

## Best Practices

1. **Use Markdown for simple formatting**
2. **Keep messages under 4096 characters**
3. **Use silent notifications for non-urgent messages**
4. **Pin important messages in groups**
5. **Store bot token securely** (never commit to git)
6. **Use chat actions for better UX** (typing, uploading)

---

## Message Limits

- **Text**: 4096 characters max
- **Caption**: 1024 characters max
- **File size**: 50 MB (documents), 10 MB (photos)

---

## Rate Limits

- **Messages**: 30 per second per chat
- **Bulk**: 20 per minute to different chats
- **Groups**: 20 per minute

---

## Module Information

- **Module Name**: TelegramModule
- **Task Type**: `(telegram)`
- **Dependencies**: `requests>=2.31.0` (already included)
- **API Version**: Bot API 7.0+
- **Documentation**: https://core.telegram.org/bots/api
