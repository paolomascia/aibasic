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


class EmailModule:
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
