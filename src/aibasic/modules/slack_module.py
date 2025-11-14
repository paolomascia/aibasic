"""
Slack Module for AIbasic

This module provides integration with Slack for sending messages, notifications,
and interactive blocks to channels and users.

Supported operations:
- Send messages to channels
- Send direct messages
- Send rich block messages
- Upload files
- Update messages
- Delete messages
- React to messages
- Send threaded messages

Configuration (aibasic.conf):
[slack]
# Option 1: Incoming Webhook (Simple)
WEBHOOK_URL = https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX

# Option 2: Bot Token (Advanced - full API access)
BOT_TOKEN = xoxb-your-bot-token-here
DEFAULT_CHANNEL = #general

# Optional settings
TIMEOUT = 30
MAX_RETRIES = 3
RETRY_BACKOFF = 1.0
PROXY = http://proxy.example.com:8080

Author: AIbasic Team
Version: 1.0
"""

import json
import logging
import threading
import time
from typing import Optional, Dict, Any, List, Union
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SlackModule:
    """
    Slack integration module.

    Supports both webhook-based and bot token authentication.
    Implements singleton pattern for efficient resource management.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        """Singleton pattern implementation."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        webhook_url: Optional[str] = None,
        bot_token: Optional[str] = None,
        default_channel: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        retry_backoff: float = 1.0,
        proxy: Optional[str] = None,
    ):
        """
        Initialize Slack module.

        Args:
            webhook_url: Slack incoming webhook URL (for simple messaging)
            bot_token: Slack bot token (for full API access)
            default_channel: Default channel for messages (e.g., #general, @username)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_backoff: Backoff factor for retries
            proxy: Optional proxy URL
        """
        # Prevent re-initialization
        if hasattr(self, '_initialized') and self._initialized:
            return

        self.webhook_url = webhook_url
        self.bot_token = bot_token
        self.default_channel = default_channel
        self.timeout = timeout
        self.api_base_url = "https://slack.com/api"

        # Create session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=retry_backoff,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        if proxy:
            self.session.proxies = {
                'http': proxy,
                'https': proxy
            }

        # Set default headers for bot token
        if self.bot_token:
            self.session.headers.update({
                'Authorization': f'Bearer {self.bot_token}',
                'Content-Type': 'application/json'
            })

        self._initialized = True
        logger.info("Slack module initialized")

    def _api_call(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make a Slack API call.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            data: Request payload
            files: Files to upload

        Returns:
            API response data

        Raises:
            Exception: If API call fails
        """
        url = f"{self.api_base_url}/{endpoint}"

        try:
            if files:
                # For file uploads, don't use JSON content-type
                response = self.session.request(
                    method,
                    url,
                    data=data,
                    files=files,
                    timeout=self.timeout
                )
            else:
                response = self.session.request(
                    method,
                    url,
                    json=data,
                    timeout=self.timeout
                )

            response.raise_for_status()
            result = response.json()

            # Check Slack API response
            if not result.get('ok', False):
                error = result.get('error', 'Unknown error')
                logger.error(f"Slack API error: {error}")
                raise Exception(f"Slack API error: {error}")

            logger.info(f"Slack API call successful: {endpoint}")
            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"Slack API request failed: {e}")
            raise Exception(f"Slack API request failed: {e}")

    def send_message(
        self,
        text: str,
        channel: Optional[str] = None,
        username: Optional[str] = None,
        icon_emoji: Optional[str] = None,
        icon_url: Optional[str] = None,
        thread_ts: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Send a message to a Slack channel.

        Args:
            text: Message text (supports Slack markdown)
            channel: Target channel (uses default if not specified)
            username: Bot username to display
            icon_emoji: Bot icon emoji (e.g., ":robot_face:")
            icon_url: Bot icon URL
            thread_ts: Thread timestamp (for threaded messages)
            attachments: Message attachments (legacy format)

        Returns:
            Response data from Slack API

        Raises:
            Exception: If message sending fails
        """
        if self.webhook_url:
            return self._send_webhook_message(
                text, username, icon_emoji, icon_url, attachments
            )
        else:
            return self._send_api_message(
                text, channel, username, icon_emoji, icon_url, thread_ts, attachments
            )

    def _send_webhook_message(
        self,
        text: str,
        username: Optional[str] = None,
        icon_emoji: Optional[str] = None,
        icon_url: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Send message using incoming webhook."""
        payload = {
            "text": text
        }

        if username:
            payload["username"] = username
        if icon_emoji:
            payload["icon_emoji"] = icon_emoji
        if icon_url:
            payload["icon_url"] = icon_url
        if attachments:
            payload["attachments"] = attachments

        try:
            response = self.session.post(
                self.webhook_url,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()

            logger.info("Message sent successfully via webhook")
            return {"status": "success", "response": response.text}

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send webhook message: {e}")
            raise Exception(f"Failed to send message: {e}")

    def _send_api_message(
        self,
        text: str,
        channel: Optional[str] = None,
        username: Optional[str] = None,
        icon_emoji: Optional[str] = None,
        icon_url: Optional[str] = None,
        thread_ts: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Send message using Slack API."""
        if not self.bot_token:
            raise ValueError("Bot token required for API messaging")

        channel = channel or self.default_channel
        if not channel:
            raise ValueError("Channel is required")

        payload = {
            "channel": channel,
            "text": text
        }

        if username:
            payload["username"] = username
        if icon_emoji:
            payload["icon_emoji"] = icon_emoji
        if icon_url:
            payload["icon_url"] = icon_url
        if thread_ts:
            payload["thread_ts"] = thread_ts
        if attachments:
            payload["attachments"] = attachments

        return self._api_call("POST", "chat.postMessage", payload)

    def send_blocks(
        self,
        blocks: List[Dict[str, Any]],
        channel: Optional[str] = None,
        text: Optional[str] = None,
        thread_ts: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send a message with Block Kit blocks.

        Args:
            blocks: List of block elements
            channel: Target channel
            text: Fallback text
            thread_ts: Thread timestamp (for replies)

        Returns:
            API response
        """
        if self.webhook_url:
            return self._send_webhook_blocks(blocks, text)
        else:
            return self._send_api_blocks(blocks, channel, text, thread_ts)

    def _send_webhook_blocks(
        self,
        blocks: List[Dict[str, Any]],
        text: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send blocks via webhook."""
        payload = {
            "blocks": blocks,
            "text": text or "New message"
        }

        try:
            response = self.session.post(
                self.webhook_url,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()

            logger.info("Blocks sent successfully via webhook")
            return {"status": "success", "response": response.text}

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send blocks: {e}")
            raise Exception(f"Failed to send blocks: {e}")

    def _send_api_blocks(
        self,
        blocks: List[Dict[str, Any]],
        channel: Optional[str] = None,
        text: Optional[str] = None,
        thread_ts: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send blocks via API."""
        if not self.bot_token:
            raise ValueError("Bot token required for API messaging")

        channel = channel or self.default_channel
        if not channel:
            raise ValueError("Channel is required")

        payload = {
            "channel": channel,
            "blocks": blocks,
            "text": text or "New message"
        }

        if thread_ts:
            payload["thread_ts"] = thread_ts

        return self._api_call("POST", "chat.postMessage", payload)

    def send_alert(
        self,
        message: str,
        severity: str = "warning",
        title: Optional[str] = None,
        channel: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send an alert message with color coding.

        Args:
            message: Alert message
            severity: Alert severity (info, warning, error, success)
            title: Optional alert title
            channel: Target channel

        Returns:
            Response data
        """
        # Map severity to colors
        color_map = {
            "info": "#36a64f",      # Green
            "warning": "#ffcc00",   # Yellow
            "error": "#ff0000",     # Red
            "success": "#36a64f",   # Green
            "danger": "#ff0000"     # Red (alias)
        }

        color = color_map.get(severity.lower(), "#36a64f")
        alert_title = title or f"{severity.upper()} Alert"

        attachment = {
            "color": color,
            "title": alert_title,
            "text": message,
            "footer": "AIbasic",
            "ts": int(time.time())
        }

        return self.send_message(
            text=f"*{alert_title}*\n{message}",
            channel=channel,
            attachments=[attachment]
        )

    def send_status_message(
        self,
        title: str,
        status: str,
        fields: Optional[List[Dict[str, str]]] = None,
        channel: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a status message with fields.

        Args:
            title: Message title
            status: Status value
            fields: List of field dicts with "title" and "value"
            channel: Target channel

        Returns:
            Response data
        """
        # Determine color based on status
        status_colors = {
            "success": "#36a64f",
            "failed": "#ff0000",
            "error": "#ff0000",
            "running": "#ffcc00",
            "pending": "#0078D4"
        }
        color = status_colors.get(status.lower(), "#36a64f")

        attachment = {
            "color": color,
            "title": title,
            "text": f"Status: *{status}*",
            "footer": "AIbasic",
            "ts": int(time.time())
        }

        if fields:
            attachment["fields"] = [
                {
                    "title": field.get("title", ""),
                    "value": field.get("value", ""),
                    "short": field.get("short", True)
                }
                for field in fields
            ]

        return self.send_message(
            text=f"*{title}* - {status}",
            channel=channel,
            attachments=[attachment]
        )

    def send_rich_message(
        self,
        title: str,
        text: str,
        color: str = "#36a64f",
        fields: Optional[List[Dict[str, str]]] = None,
        footer: Optional[str] = None,
        footer_icon: Optional[str] = None,
        image_url: Optional[str] = None,
        thumb_url: Optional[str] = None,
        channel: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a rich formatted message with attachment.

        Args:
            title: Message title
            text: Message text
            color: Attachment color (hex)
            fields: List of fields
            footer: Footer text
            footer_icon: Footer icon URL
            image_url: Image URL
            thumb_url: Thumbnail URL
            channel: Target channel

        Returns:
            Response data
        """
        attachment = {
            "color": color,
            "title": title,
            "text": text,
            "ts": int(time.time())
        }

        if fields:
            attachment["fields"] = fields
        if footer:
            attachment["footer"] = footer
        if footer_icon:
            attachment["footer_icon"] = footer_icon
        if image_url:
            attachment["image_url"] = image_url
        if thumb_url:
            attachment["thumb_url"] = thumb_url

        return self.send_message(
            text=f"*{title}*",
            channel=channel,
            attachments=[attachment]
        )

    def upload_file(
        self,
        file_path: str,
        channels: Optional[Union[str, List[str]]] = None,
        title: Optional[str] = None,
        initial_comment: Optional[str] = None,
        thread_ts: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload a file to Slack.

        Args:
            file_path: Path to file to upload
            channels: Target channel(s)
            title: File title
            initial_comment: Initial comment
            thread_ts: Thread timestamp

        Returns:
            API response

        Raises:
            Exception: If file upload fails
        """
        if not self.bot_token:
            raise ValueError("Bot token required for file uploads")

        channels = channels or self.default_channel
        if not channels:
            raise ValueError("Channel is required for file upload")

        if isinstance(channels, list):
            channels = ",".join(channels)

        data = {
            "channels": channels
        }

        if title:
            data["title"] = title
        if initial_comment:
            data["initial_comment"] = initial_comment
        if thread_ts:
            data["thread_ts"] = thread_ts

        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                return self._api_call("POST", "files.upload", data=data, files=files)

        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            raise Exception(f"File not found: {file_path}")
        except Exception as e:
            logger.error(f"Failed to upload file: {e}")
            raise Exception(f"Failed to upload file: {e}")

    def update_message(
        self,
        channel: str,
        timestamp: str,
        text: str,
        blocks: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Update an existing message.

        Args:
            channel: Channel ID
            timestamp: Message timestamp
            text: New message text
            blocks: New blocks (optional)

        Returns:
            API response
        """
        if not self.bot_token:
            raise ValueError("Bot token required for message updates")

        payload = {
            "channel": channel,
            "ts": timestamp,
            "text": text
        }

        if blocks:
            payload["blocks"] = blocks

        return self._api_call("POST", "chat.update", payload)

    def delete_message(
        self,
        channel: str,
        timestamp: str
    ) -> Dict[str, Any]:
        """
        Delete a message.

        Args:
            channel: Channel ID
            timestamp: Message timestamp

        Returns:
            API response
        """
        if not self.bot_token:
            raise ValueError("Bot token required for message deletion")

        payload = {
            "channel": channel,
            "ts": timestamp
        }

        return self._api_call("POST", "chat.delete", payload)

    def add_reaction(
        self,
        channel: str,
        timestamp: str,
        emoji: str
    ) -> Dict[str, Any]:
        """
        Add a reaction to a message.

        Args:
            channel: Channel ID
            timestamp: Message timestamp
            emoji: Emoji name (without colons, e.g., "thumbsup")

        Returns:
            API response
        """
        if not self.bot_token:
            raise ValueError("Bot token required for reactions")

        payload = {
            "channel": channel,
            "timestamp": timestamp,
            "name": emoji
        }

        return self._api_call("POST", "reactions.add", payload)

    def create_section_block(
        self,
        text: str,
        text_type: str = "mrkdwn"
    ) -> Dict[str, Any]:
        """
        Create a section block.

        Args:
            text: Block text
            text_type: Text type (mrkdwn or plain_text)

        Returns:
            Section block dict
        """
        return {
            "type": "section",
            "text": {
                "type": text_type,
                "text": text
            }
        }

    def create_divider_block(self) -> Dict[str, Any]:
        """Create a divider block."""
        return {"type": "divider"}

    def create_header_block(self, text: str) -> Dict[str, Any]:
        """Create a header block."""
        return {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": text
            }
        }

    def create_fields_block(
        self,
        fields: List[str]
    ) -> Dict[str, Any]:
        """
        Create a section block with fields.

        Args:
            fields: List of field texts

        Returns:
            Section block with fields
        """
        return {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": field
                }
                for field in fields
            ]
        }

    def close(self):
        """Close the Slack module and cleanup resources."""
        if hasattr(self, 'session'):
            self.session.close()
        logger.info("Slack module closed")

    def __del__(self):
        """Cleanup on deletion."""
        self.close()


# Global instance
_slack_instance = None


def get_slack_module(**config) -> SlackModule:
    """
    Get or create Slack module instance.

    Args:
        **config: Configuration parameters

    Returns:
        SlackModule instance
    """
    global _slack_instance
    if _slack_instance is None:
        _slack_instance = SlackModule(**config)
    return _slack_instance


# Example usage
if __name__ == "__main__":
    # Example with webhook
    slack = SlackModule(
        webhook_url="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
    )

    # Send simple message
    slack.send_message("Hello from AIbasic!")

    # Send alert
    slack.send_alert(
        message="High CPU usage detected on server-01",
        severity="warning",
        title="System Alert"
    )

    # Send status message
    slack.send_status_message(
        title="Database Backup",
        status="Success",
        fields=[
            {"title": "Database", "value": "production_db", "short": True},
            {"title": "Size", "value": "150 GB", "short": True},
            {"title": "Duration", "value": "45 minutes", "short": True}
        ]
    )

    # Send rich message
    slack.send_rich_message(
        title="Sales Report",
        text="Daily sales summary for January 20, 2025",
        color="#36a64f",
        fields=[
            {"title": "Total Sales", "value": "$125,000", "short": True},
            {"title": "Orders", "value": "342", "short": True}
        ]
    )

    # Send blocks
    blocks = [
        slack.create_header_block("Pipeline Status"),
        slack.create_divider_block(),
        slack.create_section_block("*Status:* Success :white_check_mark:"),
        slack.create_fields_block([
            "*Records Processed:* 125,000",
            "*Duration:* 2 hours",
            "*Errors:* 0",
            "*Success Rate:* 100%"
        ])
    ]
    slack.send_blocks(blocks, text="Pipeline completed")
