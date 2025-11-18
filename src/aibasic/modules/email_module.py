"""
Email Module for SMTP Email Sending

This module provides comprehensive email sending capabilities via SMTP.
Configuration is loaded from aibasic.conf under the [email] section.

Supports:
- Plain text and HTML emails
- Multiple recipients (To, CC, BCC)
- File attachments (any file type)
- Inline images for HTML emails
- Email templates with variables
- SSL/TLS and STARTTLS encryption
- Authentication (username/password)
- Custom headers
- Reply-To and priority settings
- Batch email sending
- Email validation

Features:
- Send simple text emails
- Send HTML emails with styling
- Attach files (documents, images, PDFs, etc.)
- Embed images in HTML content
- Template-based emails with variable substitution
- Multiple recipients management
- Secure SMTP connection (SSL/TLS)
- Email address validation
- Delivery status tracking

Example configuration in aibasic.conf:
    [email]
    SMTP_HOST=smtp.gmail.com
    SMTP_PORT=587
    USE_TLS=true
    USE_SSL=false
    USERNAME=your-email@gmail.com
    PASSWORD=your-app-password

    # Optional settings
    FROM_EMAIL=your-email@gmail.com
    FROM_NAME=My Application
    TIMEOUT=30

Usage in generated code:
    from aibasic.modules import EmailModule

    # Initialize module
    email = EmailModule.from_config('aibasic.conf')

    # Send simple email
    email.send_email(
        to='recipient@example.com',
        subject='Hello',
        body='This is a test email'
    )

    # Send with attachments
    email.send_email(
        to='recipient@example.com',
        subject='Report',
        body='Please find the report attached',
        attachments=['report.pdf', 'data.xlsx']
    )

    # Send HTML email
    email.send_html_email(
        to='recipient@example.com',
        subject='Newsletter',
        html_body='<h1>Welcome!</h1><p>Thank you for subscribing.</p>'
    )

    # Send to multiple recipients
    email.send_email(
        to=['user1@example.com', 'user2@example.com'],
        cc=['manager@example.com'],
        subject='Team Update',
        body='Important announcement'
    )
"""

import configparser
import smtplib
import threading
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders
from email.utils import formataddr, parseaddr
from typing import Optional, List, Union, Dict, Any
import mimetypes
import os
import re
from .module_base import AIbasicModuleBase


class EmailModule(AIbasicModuleBase):
    """
    SMTP email sending module with full attachment support.

    Supports plain text, HTML, attachments, templates, and batch sending.
    """

    _instance = None
    _lock = threading.Lock()

    def __init__(
        self,
        smtp_host: str,
        smtp_port: int = 587,
        username: Optional[str] = None,
        password: Optional[str] = None,
        use_tls: bool = True,
        use_ssl: bool = False,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
        timeout: int = 30
    ):
        """
        Initialize the EmailModule.

        Args:
            smtp_host: SMTP server hostname
            smtp_port: SMTP server port (587 for TLS, 465 for SSL, 25 for plain)
            username: SMTP authentication username
            password: SMTP authentication password
            use_tls: Use STARTTLS encryption (default True)
            use_ssl: Use SSL encryption (default False)
            from_email: Default sender email address
            from_name: Default sender name
            timeout: Connection timeout in seconds
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.use_ssl = use_ssl
        self.from_email = from_email or username
        self.from_name = from_name
        self.timeout = timeout

        # Validate configuration
        if not smtp_host:
            raise ValueError("SMTP host is required")

        if use_tls and use_ssl:
            raise ValueError("Cannot use both TLS and SSL. Choose one.")

        print(f"[EmailModule] Configured SMTP: {smtp_host}:{smtp_port}")
        if use_ssl:
            print("[EmailModule] Using SSL encryption")
        elif use_tls:
            print("[EmailModule] Using TLS encryption")
        if from_email:
            print(f"[EmailModule] Default sender: {from_email}")

    @classmethod
    def from_config(cls, config_path: str = "aibasic.conf") -> 'EmailModule':
        """
        Create an EmailModule from configuration file.
        Uses singleton pattern to ensure only one instance exists.

        Args:
            config_path: Path to aibasic.conf file

        Returns:
            EmailModule instance
        """
        with cls._lock:
            if cls._instance is None:
                config = configparser.ConfigParser()
                path = Path(config_path)

                if not path.exists():
                    raise FileNotFoundError(f"Configuration file not found: {config_path}")

                config.read(path)

                if 'email' not in config:
                    raise KeyError("Missing [email] section in aibasic.conf")

                email_config = config['email']

                # Required
                smtp_host = email_config.get('SMTP_HOST')
                if not smtp_host:
                    raise ValueError("SMTP_HOST is required in [email] section")

                # Connection
                smtp_port = email_config.getint('SMTP_PORT', 587)
                use_tls = email_config.getboolean('USE_TLS', True)
                use_ssl = email_config.getboolean('USE_SSL', False)
                timeout = email_config.getint('TIMEOUT', 30)

                # Authentication
                username = email_config.get('USERNAME', None)
                password = email_config.get('PASSWORD', None)

                # Sender
                from_email = email_config.get('FROM_EMAIL', username)
                from_name = email_config.get('FROM_NAME', None)

                cls._instance = cls(
                    smtp_host=smtp_host,
                    smtp_port=smtp_port,
                    username=username,
                    password=password,
                    use_tls=use_tls,
                    use_ssl=use_ssl,
                    from_email=from_email,
                    from_name=from_name,
                    timeout=timeout
                )

            return cls._instance

    # ==================== SMTP Connection ====================

    def _connect(self) -> smtplib.SMTP:
        """Create and configure SMTP connection."""
        if self.use_ssl:
            # SSL connection
            smtp = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, timeout=self.timeout)
        else:
            # Regular or TLS connection
            smtp = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=self.timeout)
            smtp.ehlo()

            if self.use_tls:
                smtp.starttls()
                smtp.ehlo()

        # Authenticate if credentials provided
        if self.username and self.password:
            smtp.login(self.username, self.password)

        return smtp

    # ==================== Email Sending ====================

    def send_email(
        self,
        to: Union[str, List[str]],
        subject: str,
        body: str,
        cc: Optional[Union[str, List[str]]] = None,
        bcc: Optional[Union[str, List[str]]] = None,
        attachments: Optional[List[str]] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
        reply_to: Optional[str] = None,
        priority: str = 'normal'
    ) -> Dict[str, Any]:
        """
        Send a plain text email.

        Args:
            to: Recipient email(s)
            subject: Email subject
            body: Plain text email body
            cc: CC recipient(s)
            bcc: BCC recipient(s)
            attachments: List of file paths to attach
            from_email: Sender email (overrides default)
            from_name: Sender name (overrides default)
            reply_to: Reply-To email address
            priority: Email priority ('low', 'normal', 'high')

        Returns:
            Dict with send status and details
        """
        # Create message
        msg = MIMEMultipart()

        # Set headers
        sender_email = from_email or self.from_email
        sender_name = from_name or self.from_name

        if sender_name:
            msg['From'] = formataddr((sender_name, sender_email))
        else:
            msg['From'] = sender_email

        msg['Subject'] = subject

        # Recipients
        to_list = [to] if isinstance(to, str) else to
        msg['To'] = ', '.join(to_list)

        all_recipients = to_list.copy()

        if cc:
            cc_list = [cc] if isinstance(cc, str) else cc
            msg['Cc'] = ', '.join(cc_list)
            all_recipients.extend(cc_list)

        if bcc:
            bcc_list = [bcc] if isinstance(bcc, str) else bcc
            all_recipients.extend(bcc_list)

        # Optional headers
        if reply_to:
            msg['Reply-To'] = reply_to

        # Priority
        if priority == 'high':
            msg['X-Priority'] = '1'
            msg['X-MSMail-Priority'] = 'High'
        elif priority == 'low':
            msg['X-Priority'] = '5'
            msg['X-MSMail-Priority'] = 'Low'

        # Attach body
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        # Attach files
        if attachments:
            for filepath in attachments:
                self._attach_file(msg, filepath)

        # Send email
        try:
            smtp = self._connect()
            smtp.send_message(msg, sender_email, all_recipients)
            smtp.quit()

            print(f"[EmailModule] Email sent successfully to {len(all_recipients)} recipient(s)")

            return {
                'success': True,
                'recipients': len(all_recipients),
                'to': to_list,
                'subject': subject,
                'attachments': len(attachments) if attachments else 0
            }

        except Exception as e:
            print(f"[EmailModule] Failed to send email: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def send_html_email(
        self,
        to: Union[str, List[str]],
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
        cc: Optional[Union[str, List[str]]] = None,
        bcc: Optional[Union[str, List[str]]] = None,
        attachments: Optional[List[str]] = None,
        inline_images: Optional[Dict[str, str]] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
        reply_to: Optional[str] = None,
        priority: str = 'normal'
    ) -> Dict[str, Any]:
        """
        Send an HTML email.

        Args:
            to: Recipient email(s)
            subject: Email subject
            html_body: HTML email body
            text_body: Plain text fallback (optional)
            cc: CC recipient(s)
            bcc: BCC recipient(s)
            attachments: List of file paths to attach
            inline_images: Dict of {cid: filepath} for embedded images
            from_email: Sender email
            from_name: Sender name
            reply_to: Reply-To address
            priority: Email priority

        Returns:
            Dict with send status
        """
        # Create message
        msg = MIMEMultipart('alternative')

        # Set headers (same as send_email)
        sender_email = from_email or self.from_email
        sender_name = from_name or self.from_name

        if sender_name:
            msg['From'] = formataddr((sender_name, sender_email))
        else:
            msg['From'] = sender_email

        msg['Subject'] = subject

        # Recipients
        to_list = [to] if isinstance(to, str) else to
        msg['To'] = ', '.join(to_list)

        all_recipients = to_list.copy()

        if cc:
            cc_list = [cc] if isinstance(cc, str) else cc
            msg['Cc'] = ', '.join(cc_list)
            all_recipients.extend(cc_list)

        if bcc:
            bcc_list = [bcc] if isinstance(bcc, str) else bcc
            all_recipients.extend(bcc_list)

        if reply_to:
            msg['Reply-To'] = reply_to

        # Priority
        if priority == 'high':
            msg['X-Priority'] = '1'
        elif priority == 'low':
            msg['X-Priority'] = '5'

        # Attach plain text version if provided
        if text_body:
            msg.attach(MIMEText(text_body, 'plain', 'utf-8'))

        # Attach HTML version
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))

        # Attach inline images
        if inline_images:
            for cid, filepath in inline_images.items():
                self._attach_inline_image(msg, filepath, cid)

        # Attach files
        if attachments:
            for filepath in attachments:
                self._attach_file(msg, filepath)

        # Send email
        try:
            smtp = self._connect()
            smtp.send_message(msg, sender_email, all_recipients)
            smtp.quit()

            print(f"[EmailModule] HTML email sent successfully to {len(all_recipients)} recipient(s)")

            return {
                'success': True,
                'recipients': len(all_recipients),
                'to': to_list,
                'subject': subject,
                'html': True
            }

        except Exception as e:
            print(f"[EmailModule] Failed to send HTML email: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    # ==================== Template-Based Email ====================

    def send_template_email(
        self,
        to: Union[str, List[str]],
        subject: str,
        template: str,
        variables: Dict[str, str],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send email using template with variable substitution.

        Args:
            to: Recipient email(s)
            subject: Email subject (can include {variables})
            template: Email body template with {variable} placeholders
            variables: Dict of {variable_name: value}
            **kwargs: Additional arguments passed to send_email()

        Returns:
            Dict with send status
        """
        # Substitute variables in subject
        formatted_subject = subject.format(**variables)

        # Substitute variables in template
        formatted_body = template.format(**variables)

        # Determine if HTML
        is_html = '<html' in template.lower() or '<body' in template.lower()

        if is_html:
            return self.send_html_email(
                to=to,
                subject=formatted_subject,
                html_body=formatted_body,
                **kwargs
            )
        else:
            return self.send_email(
                to=to,
                subject=formatted_subject,
                body=formatted_body,
                **kwargs
            )

    # ==================== Batch Email Sending ====================

    def send_batch_emails(
        self,
        emails: List[Dict[str, Any]],
        delay: float = 0
    ) -> Dict[str, Any]:
        """
        Send multiple emails in batch.

        Args:
            emails: List of email dicts with 'to', 'subject', 'body', etc.
            delay: Delay between emails in seconds

        Returns:
            Dict with batch send statistics
        """
        import time

        sent = 0
        failed = 0
        errors = []

        for i, email_data in enumerate(emails):
            try:
                result = self.send_email(**email_data)
                if result.get('success'):
                    sent += 1
                else:
                    failed += 1
                    errors.append({'email': i, 'error': result.get('error')})

                # Delay between emails (avoid spam filters)
                if delay > 0 and i < len(emails) - 1:
                    time.sleep(delay)

            except Exception as e:
                failed += 1
                errors.append({'email': i, 'error': str(e)})

        print(f"[EmailModule] Batch send complete: {sent} sent, {failed} failed")

        return {
            'total': len(emails),
            'sent': sent,
            'failed': failed,
            'errors': errors if errors else None
        }

    # ==================== Attachment Handling ====================

    def _attach_file(self, msg: MIMEMultipart, filepath: str) -> None:
        """Attach a file to email message."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Attachment not found: {filepath}")

        filename = os.path.basename(filepath)

        # Guess MIME type
        mime_type, _ = mimetypes.guess_type(filepath)
        if mime_type is None:
            mime_type = 'application/octet-stream'

        maintype, subtype = mime_type.split('/', 1)

        # Read file
        with open(filepath, 'rb') as f:
            part = MIMEBase(maintype, subtype)
            part.set_payload(f.read())

        # Encode
        encoders.encode_base64(part)

        # Add header
        part.add_header(
            'Content-Disposition',
            f'attachment; filename= {filename}'
        )

        msg.attach(part)

    def _attach_inline_image(self, msg: MIMEMultipart, filepath: str, cid: str) -> None:
        """Attach inline image for HTML email."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Image not found: {filepath}")

        with open(filepath, 'rb') as f:
            img = MIMEImage(f.read())

        img.add_header('Content-ID', f'<{cid}>')
        img.add_header('Content-Disposition', 'inline', filename=os.path.basename(filepath))

        msg.attach(img)

    # ==================== Utility Methods ====================

    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate email address format.

        Args:
            email: Email address to validate

        Returns:
            True if valid, False otherwise
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def extract_email(email_string: str) -> str:
        """
        Extract email address from string like "Name <email@example.com>".

        Args:
            email_string: Email string

        Returns:
            Email address
        """
        name, email = parseaddr(email_string)
        return email

    def test_connection(self) -> bool:
        """
        Test SMTP connection.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            smtp = self._connect()
            smtp.quit()
            print("[EmailModule] SMTP connection test: SUCCESS")
            return True
        except Exception as e:
            print(f"[EmailModule] SMTP connection test: FAILED - {e}")
            return False

    def get_config_info(self) -> Dict[str, Any]:
        """
        Get current configuration information.

        Returns:
            Dict with config details
        """
        return {
            'smtp_host': self.smtp_host,
            'smtp_port': self.smtp_port,
            'use_tls': self.use_tls,
            'use_ssl': self.use_ssl,
            'from_email': self.from_email,
            'from_name': self.from_name,
            'authenticated': bool(self.username and self.password)
        }

    @classmethod
    def get_metadata(cls):
        """Get module metadata."""
        from aibasic.modules.module_base import ModuleMetadata
        return ModuleMetadata(
            name="Email",
            task_type="email",
            description="SMTP email sending with support for plain text, HTML, attachments, inline images, templates, and batch sending",
            version="1.0.0",
            keywords=["email", "smtp", "send-email", "html-email", "attachment", "mime", "mail", "newsletter", "notification"],
            dependencies=[]  # Uses Python standard library only
        )

    @classmethod
    def get_usage_notes(cls):
        """Get detailed usage notes."""
        return [
            "Module uses singleton pattern via from_config() - one instance per application",
            "Configuration loaded from [email] section in aibasic.conf",
            "Supports both STARTTLS (port 587, use_tls=true) and SSL (port 465, use_ssl=true) encryption",
            "Cannot use both TLS and SSL simultaneously - choose one based on server requirements",
            "Common SMTP ports: 587 (TLS), 465 (SSL), 25 (plain, not recommended)",
            "Gmail requires 'App Passwords' instead of regular passwords (2FA must be enabled)",
            "Recipients can be single email string or list of email strings",
            "CC and BCC recipients are supported - BCC recipients won't appear in headers",
            "Attachments accept file paths as strings - any file type supported",
            "HTML emails support inline images using Content-ID (cid:image_id) references",
            "Templates use Python format strings with {variable} placeholders",
            "Priority setting adds X-Priority headers ('low', 'normal', 'high')",
            "Reply-To header allows specifying different reply address from sender",
            "Batch sending supports optional delay between emails to avoid spam filters",
            "Email validation uses regex pattern - validates format only, not deliverability",
            "Module automatically detects MIME types for attachments",
            "HTML emails can include plain text fallback for better compatibility",
            "Sender name and email can be overridden per message or use defaults from config"
        ]

    @classmethod
    def get_methods_info(cls):
        """Get information about module methods."""
        from aibasic.modules.module_base import MethodInfo
        return [
            MethodInfo(
                name="send_email",
                description="Send a plain text email with optional attachments and multiple recipients",
                parameters={
                    "to": "Recipient email address or list of addresses",
                    "subject": "Email subject line",
                    "body": "Plain text email body content",
                    "cc": "CC recipient(s) - optional, string or list",
                    "bcc": "BCC recipient(s) - optional, string or list (hidden from other recipients)",
                    "attachments": "List of file paths to attach (optional, supports any file type)",
                    "from_email": "Sender email address (optional, overrides default)",
                    "from_name": "Sender display name (optional, overrides default)",
                    "reply_to": "Reply-To email address (optional)",
                    "priority": "Email priority - 'low', 'normal', or 'high' (default: 'normal')"
                },
                returns="Dictionary with success status, recipient count, and details",
                examples=[
                    '(email) send email to "user@example.com" subject "Hello" body "This is a test message"',
                    '(email) send email to ["alice@example.com", "bob@example.com"] subject "Team Update" body "Meeting at 3pm"',
                    '(email) send email to "client@example.com" subject "Report" body "Please find attached" attachments ["report.pdf", "data.xlsx"]',
                    '(email) send email to "user@example.com" cc "manager@example.com" subject "Request" body "Approval needed"'
                ]
            ),
            MethodInfo(
                name="send_html_email",
                description="Send an HTML email with styling, optional plain text fallback, and inline images",
                parameters={
                    "to": "Recipient email address or list of addresses",
                    "subject": "Email subject line",
                    "html_body": "HTML content with tags and styling",
                    "text_body": "Plain text fallback for non-HTML clients (optional)",
                    "cc": "CC recipient(s) - optional",
                    "bcc": "BCC recipient(s) - optional",
                    "attachments": "List of file paths to attach (optional)",
                    "inline_images": "Dictionary of {cid: filepath} for embedded images (optional, use as <img src='cid:image_id'>)",
                    "from_email": "Sender email (optional, overrides default)",
                    "from_name": "Sender name (optional, overrides default)",
                    "reply_to": "Reply-To address (optional)",
                    "priority": "Email priority (optional, default: 'normal')"
                },
                returns="Dictionary with success status and details",
                examples=[
                    '(email) send html email to "user@example.com" subject "Newsletter" html_body "<h1>Welcome!</h1><p>Thanks for subscribing.</p>"',
                    '(email) send html email to "customer@example.com" subject "Receipt" html_body "<html><body><h2>Order #123</h2><p>Total: $99.99</p></body></html>"',
                    '(email) send html email to "user@example.com" subject "Report" html_body "<h1>Report</h1><img src=\'cid:logo\'>" inline_images {"logo": "logo.png"}',
                    '(email) send html email to ["user1@example.com", "user2@example.com"] subject "Announcement" html_body "<p>Important update</p>" priority "high"'
                ]
            ),
            MethodInfo(
                name="send_template_email",
                description="Send email using template with variable substitution for personalized messages",
                parameters={
                    "to": "Recipient email address or list of addresses",
                    "subject": "Email subject (can include {variable} placeholders)",
                    "template": "Email body template with {variable} placeholders (auto-detects HTML)",
                    "variables": "Dictionary mapping variable names to values",
                    "**kwargs": "Additional arguments passed to send_email() or send_html_email()"
                },
                returns="Dictionary with success status",
                examples=[
                    '(email) send template email to "user@example.com" subject "Hello {name}" template "Dear {name}, Welcome to {company}!" variables {"name": "John", "company": "Acme Corp"}',
                    '(email) send template email to "customer@example.com" subject "Order {order_id}" template "Order {order_id} total: ${total}" variables {"order_id": "12345", "total": "99.99"}',
                    '(email) send template email to "user@example.com" subject "Welcome" template "<html><body><h1>Hello {name}!</h1></body></html>" variables {"name": "Alice"}'
                ]
            ),
            MethodInfo(
                name="send_batch_emails",
                description="Send multiple emails in batch with optional delay to avoid spam filters",
                parameters={
                    "emails": "List of email dictionaries, each with 'to', 'subject', 'body', etc.",
                    "delay": "Delay between emails in seconds (default: 0, recommended: 1-2 for large batches)"
                },
                returns="Dictionary with total, sent, failed counts and error details",
                examples=[
                    '(email) send batch emails [{"to": "user1@example.com", "subject": "Hello", "body": "Message 1"}, {"to": "user2@example.com", "subject": "Hello", "body": "Message 2"}]',
                    '(email) send batch emails from list with delay 1.5',
                    '(email) send 100 emails with delay 2 seconds'
                ]
            ),
            MethodInfo(
                name="validate_email",
                description="Validate email address format using regex (static method, validates format only)",
                parameters={
                    "email": "Email address string to validate"
                },
                returns="Boolean: True if format is valid, False otherwise",
                examples=[
                    '(email) validate email "user@example.com"',
                    '(email) check if email "invalid@" is valid',
                    '(email) validate email address "test.user+tag@domain.co.uk"'
                ]
            ),
            MethodInfo(
                name="extract_email",
                description="Extract email address from formatted string like 'Name <email@example.com>' (static method)",
                parameters={
                    "email_string": "Email string with optional display name"
                },
                returns="Email address string without display name",
                examples=[
                    '(email) extract email from "John Doe <john@example.com>"',
                    '(email) extract email address from "user@example.com"',
                    '(email) parse email from "Alice Smith <alice.smith@company.com>"'
                ]
            ),
            MethodInfo(
                name="test_connection",
                description="Test SMTP connection to verify configuration and credentials",
                parameters={},
                returns="Boolean: True if connection successful, False otherwise",
                examples=[
                    '(email) test connection',
                    '(email) test smtp connection',
                    '(email) verify email server connection'
                ]
            ),
            MethodInfo(
                name="get_config_info",
                description="Get current email configuration details",
                parameters={},
                returns="Dictionary with SMTP host, port, encryption, sender info, and authentication status",
                examples=[
                    '(email) get config info',
                    '(email) show email configuration',
                    '(email) display smtp settings'
                ]
            )
        ]

    @classmethod
    def get_examples(cls):
        """Get AIbasic usage examples."""
        return [
            # Basic email sending
            '10 (email) send email to "user@example.com" subject "Test" body "This is a test message"',
            '20 (email) send email to "client@example.com" subject "Hello" body "Nice to meet you!"',

            # Multiple recipients
            '30 (email) send email to ["alice@example.com", "bob@example.com"] subject "Team Meeting" body "Meeting at 3pm in conference room"',
            '40 (email) send email to "user@example.com" cc "manager@example.com" subject "Request" body "Please review this request"',
            '50 (email) send email to "team@example.com" cc ["manager@example.com", "director@example.com"] subject "Update" body "Project status update"',
            '60 (email) send email to "public@example.com" bcc ["admin@example.com", "log@example.com"] subject "Announcement" body "Public announcement"',

            # Attachments
            '70 (email) send email to "client@example.com" subject "Report" body "Please find the report attached" attachments ["report.pdf"]',
            '80 (email) send email to "user@example.com" subject "Documents" body "Attached files" attachments ["contract.pdf", "invoice.xlsx", "summary.docx"]',
            '90 (email) send email to "team@example.com" subject "Data" body "Analysis results" attachments ["data.csv", "charts.png"]',

            # HTML emails
            '100 (email) send html email to "user@example.com" subject "Welcome" html_body "<h1>Welcome!</h1><p>Thank you for signing up.</p>"',
            '110 (email) send html email to "customer@example.com" subject "Order Confirmation" html_body "<html><body><h2>Order #12345</h2><p>Total: $99.99</p><p>Shipping to: 123 Main St</p></body></html>"',
            '120 (email) send html email to "subscriber@example.com" subject "Newsletter" html_body "<h1>Monthly Newsletter</h1><ul><li>News 1</li><li>News 2</li></ul>"',

            # HTML with inline images
            '130 (email) send html email to "user@example.com" subject "Logo Test" html_body "<html><body><img src=\'cid:logo\'/><p>Our company</p></body></html>" inline_images {"logo": "logo.png"}',
            '140 (email) send html email to "customer@example.com" subject "Product" html_body "<h2>New Product</h2><img src=\'cid:product\'/>" inline_images {"product": "product.jpg"}',

            # Priority and reply-to
            '150 (email) send email to "urgent@example.com" subject "URGENT" body "Immediate action required" priority "high"',
            '160 (email) send email to "user@example.com" subject "Survey" body "Please reply to support" reply_to "support@example.com"',
            '170 (email) send email to "team@example.com" subject "FYI" body "For your information" priority "low"',

            # Template emails
            '180 (email) send template email to "john@example.com" subject "Hello {name}" template "Dear {name}, Welcome to {company}!" variables {"name": "John", "company": "Acme Corp"}',
            '190 (email) send template email to "customer@example.com" subject "Order {order_id}" template "Your order {order_id} for ${amount} has been confirmed" variables {"order_id": "12345", "amount": "99.99"}',
            '200 (email) send template email to "user@example.com" subject "Welcome {username}" template "<html><body><h1>Hello {username}!</h1><p>Thanks for joining {site}</p></body></html>" variables {"username": "alice", "site": "Example.com"}',

            # Batch sending
            '210 (email) send batch emails [{"to": "user1@example.com", "subject": "Hello", "body": "Message 1"}, {"to": "user2@example.com", "subject": "Hello", "body": "Message 2"}]',
            '220 (email) send batch emails from email_list with delay 1',
            '230 (email) send batch emails to customers with delay 2',

            # Utility methods
            '240 (email) validate email "user@example.com"',
            '250 (email) validate email "invalid-email"',
            '260 (email) extract email from "John Doe <john@example.com>"',
            '270 (email) test connection',
            '280 (email) get config info',

            # Advanced combinations
            '290 (email) send html email to "vip@example.com" subject "Exclusive Offer" html_body "<h1>Special Deal</h1><p>Just for you!</p>" attachments ["coupon.pdf"] priority "high"',
            '300 (email) send email to "client@example.com" cc "sales@example.com" bcc "log@example.com" subject "Proposal" body "Please review" attachments ["proposal.pdf", "pricing.xlsx"] reply_to "sales@example.com"'
        ]
