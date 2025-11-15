"""
MQTT (Message Queuing Telemetry Transport) Module for AIBasic

This module provides comprehensive MQTT messaging capabilities including:
- Broker Connection: Connect to MQTT brokers with authentication
- Publish Messages: Send messages to topics
- Subscribe to Topics: Receive messages from topics
- QoS Support: Quality of Service levels 0, 1, 2
- Retained Messages: Store last message on broker
- Last Will and Testament: Automatic disconnect messages
- TLS/SSL Support: Secure connections
- Callback Handlers: Custom message handlers

Configuration in aibasic.conf:
    [mqtt]
    BROKER = mqtt.example.com
    PORT = 1883
    USERNAME = mqtt_user
    PASSWORD = mqtt_password
    CLIENT_ID = aibasic_client
    KEEPALIVE = 60
    USE_TLS = false
    QOS = 1
"""

import os
import threading
import time
from typing import Dict, Any, Optional, Callable, List
import json

try:
    import paho.mqtt.client as mqtt
except ImportError:
    raise ImportError(
        "MQTT module requires paho-mqtt. "
        "Install with: pip install paho-mqtt"
    )


class MQTTModule:
    """
    MQTT module for IoT and pub/sub messaging.

    Implements singleton pattern for efficient resource usage.
    Provides comprehensive MQTT operations through paho-mqtt library.
    """

    _instance = None
    _lock = threading.Lock()
    _initialized = False

    def __new__(cls, config: Optional[Dict[str, Any]] = None):
        """Singleton pattern implementation."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize MQTT module with configuration.

        Args:
            config: Configuration dictionary from aibasic.conf
        """
        if self._initialized:
            return

        with self._lock:
            if self._initialized:
                return

            self.config = config or {}

            # Broker settings
            self.broker = self.config.get('BROKER') or os.getenv('MQTT_BROKER', 'localhost')
            self.port = int(self.config.get('PORT') or os.getenv('MQTT_PORT', '1883'))

            # Authentication
            self.username = self.config.get('USERNAME') or os.getenv('MQTT_USERNAME')
            self.password = self.config.get('PASSWORD') or os.getenv('MQTT_PASSWORD')

            # Client settings
            self.client_id = self.config.get('CLIENT_ID') or os.getenv('MQTT_CLIENT_ID', f'aibasic_{int(time.time())}')
            self.keepalive = int(self.config.get('KEEPALIVE') or os.getenv('MQTT_KEEPALIVE', '60'))
            self.clean_session = self.config.get('CLEAN_SESSION', 'true').lower() == 'true'

            # QoS (Quality of Service)
            self.default_qos = int(self.config.get('QOS') or os.getenv('MQTT_QOS', '1'))

            # TLS/SSL settings
            self.use_tls = self.config.get('USE_TLS', 'false').lower() == 'true'
            self.ca_certs = self.config.get('CA_CERTS') or os.getenv('MQTT_CA_CERTS')
            self.certfile = self.config.get('CERTFILE') or os.getenv('MQTT_CERTFILE')
            self.keyfile = self.config.get('KEYFILE') or os.getenv('MQTT_KEYFILE')

            # Last Will and Testament
            self.lwt_topic = self.config.get('LWT_TOPIC') or os.getenv('MQTT_LWT_TOPIC')
            self.lwt_payload = self.config.get('LWT_PAYLOAD') or os.getenv('MQTT_LWT_PAYLOAD', 'offline')
            self.lwt_qos = int(self.config.get('LWT_QOS') or os.getenv('MQTT_LWT_QOS', '1'))
            self.lwt_retain = self.config.get('LWT_RETAIN', 'false').lower() == 'true'

            # Client instance (lazy-loaded)
            self._client = None
            self._connected = False
            self._subscriptions = {}
            self._message_callbacks = {}

            self._initialized = True

    @property
    def client(self):
        """Get MQTT client (lazy-loaded)."""
        if self._client is None:
            try:
                # Create client
                self._client = mqtt.Client(
                    client_id=self.client_id,
                    clean_session=self.clean_session,
                    protocol=mqtt.MQTTv311
                )

                # Set callbacks
                self._client.on_connect = self._on_connect
                self._client.on_disconnect = self._on_disconnect
                self._client.on_message = self._on_message
                self._client.on_publish = self._on_publish
                self._client.on_subscribe = self._on_subscribe

                # Set authentication
                if self.username and self.password:
                    self._client.username_pw_set(self.username, self.password)

                # Set Last Will and Testament
                if self.lwt_topic:
                    self._client.will_set(
                        self.lwt_topic,
                        payload=self.lwt_payload,
                        qos=self.lwt_qos,
                        retain=self.lwt_retain
                    )

                # Configure TLS/SSL
                if self.use_tls:
                    self._client.tls_set(
                        ca_certs=self.ca_certs,
                        certfile=self.certfile,
                        keyfile=self.keyfile
                    )

            except Exception as e:
                raise RuntimeError(f"Failed to create MQTT client: {e}")

        return self._client

    def _on_connect(self, client, userdata, flags, rc):
        """Callback when client connects to broker."""
        if rc == 0:
            self._connected = True
            print(f"Connected to MQTT broker: {self.broker}:{self.port}")

            # Resubscribe to topics after reconnection
            for topic, qos in self._subscriptions.items():
                client.subscribe(topic, qos)
        else:
            self._connected = False
            error_messages = {
                1: "Connection refused - incorrect protocol version",
                2: "Connection refused - invalid client identifier",
                3: "Connection refused - server unavailable",
                4: "Connection refused - bad username or password",
                5: "Connection refused - not authorized"
            }
            error_msg = error_messages.get(rc, f"Connection failed with code {rc}")
            print(f"MQTT connection failed: {error_msg}")

    def _on_disconnect(self, client, userdata, rc):
        """Callback when client disconnects from broker."""
        self._connected = False
        if rc != 0:
            print(f"Unexpected disconnection from MQTT broker (code {rc})")

    def _on_message(self, client, userdata, message):
        """Callback when message is received."""
        topic = message.topic
        payload = message.payload.decode('utf-8')

        # Call custom callback if registered for this topic
        if topic in self._message_callbacks:
            callback = self._message_callbacks[topic]
            callback(topic, payload)
        else:
            print(f"Received message on topic '{topic}': {payload}")

    def _on_publish(self, client, userdata, mid):
        """Callback when message is published."""
        pass  # Can be extended for publish confirmation tracking

    def _on_subscribe(self, client, userdata, mid, granted_qos):
        """Callback when subscription is confirmed."""
        pass  # Can be extended for subscription confirmation tracking

    def connect(self, broker: Optional[str] = None, port: Optional[int] = None):
        """
        Connect to MQTT broker.

        Args:
            broker: MQTT broker hostname (optional, uses config if not provided)
            port: MQTT broker port (optional, uses config if not provided)
        """
        try:
            broker = broker or self.broker
            port = port or self.port

            self.client.connect(broker, port, self.keepalive)
            self.client.loop_start()

            # Wait for connection
            timeout = 10
            start_time = time.time()
            while not self._connected and (time.time() - start_time) < timeout:
                time.sleep(0.1)

            if not self._connected:
                raise RuntimeError("Connection timeout")

        except Exception as e:
            raise RuntimeError(f"Failed to connect to MQTT broker: {e}")

    def disconnect(self):
        """Disconnect from MQTT broker."""
        try:
            if self._client and self._connected:
                self.client.loop_stop()
                self.client.disconnect()
                self._connected = False
        except Exception as e:
            raise RuntimeError(f"Failed to disconnect from MQTT broker: {e}")

    def publish(self, topic: str, payload: str, qos: Optional[int] = None, retain: bool = False):
        """
        Publish message to topic.

        Args:
            topic: Topic to publish to
            payload: Message payload (will be converted to string)
            qos: Quality of Service (0, 1, or 2)
            retain: Whether broker should retain message
        """
        try:
            if not self._connected:
                self.connect()

            qos = qos if qos is not None else self.default_qos

            # Convert payload to string if needed
            if isinstance(payload, dict):
                payload = json.dumps(payload)
            elif not isinstance(payload, str):
                payload = str(payload)

            result = self.client.publish(topic, payload, qos=qos, retain=retain)

            if result.rc != mqtt.MQTT_ERR_SUCCESS:
                raise RuntimeError(f"Publish failed with code {result.rc}")

            return result.mid

        except Exception as e:
            raise RuntimeError(f"Failed to publish message: {e}")

    def subscribe(self, topic: str, qos: Optional[int] = None, callback: Optional[Callable] = None):
        """
        Subscribe to topic.

        Args:
            topic: Topic to subscribe to (supports wildcards + and #)
            qos: Quality of Service (0, 1, or 2)
            callback: Optional callback function(topic, payload)
        """
        try:
            if not self._connected:
                self.connect()

            qos = qos if qos is not None else self.default_qos

            result = self.client.subscribe(topic, qos)

            if result[0] != mqtt.MQTT_ERR_SUCCESS:
                raise RuntimeError(f"Subscribe failed with code {result[0]}")

            # Store subscription
            self._subscriptions[topic] = qos

            # Register callback if provided
            if callback:
                self._message_callbacks[topic] = callback

        except Exception as e:
            raise RuntimeError(f"Failed to subscribe to topic: {e}")

    def unsubscribe(self, topic: str):
        """
        Unsubscribe from topic.

        Args:
            topic: Topic to unsubscribe from
        """
        try:
            if not self._connected:
                raise RuntimeError("Not connected to MQTT broker")

            result = self.client.unsubscribe(topic)

            if result[0] != mqtt.MQTT_ERR_SUCCESS:
                raise RuntimeError(f"Unsubscribe failed with code {result[0]}")

            # Remove subscription
            if topic in self._subscriptions:
                del self._subscriptions[topic]
            if topic in self._message_callbacks:
                del self._message_callbacks[topic]

        except Exception as e:
            raise RuntimeError(f"Failed to unsubscribe from topic: {e}")

    def publish_json(self, topic: str, data: Dict[str, Any], qos: Optional[int] = None, retain: bool = False):
        """
        Publish JSON data to topic.

        Args:
            topic: Topic to publish to
            data: Dictionary to serialize as JSON
            qos: Quality of Service (0, 1, or 2)
            retain: Whether broker should retain message
        """
        try:
            payload = json.dumps(data)
            return self.publish(topic, payload, qos, retain)
        except Exception as e:
            raise RuntimeError(f"Failed to publish JSON message: {e}")

    def wait_for_messages(self, timeout: Optional[int] = None):
        """
        Wait for incoming messages.

        Args:
            timeout: Timeout in seconds (None for indefinite)
        """
        try:
            if not self._connected:
                raise RuntimeError("Not connected to MQTT broker")

            if timeout:
                time.sleep(timeout)
            else:
                # Wait indefinitely
                while self._connected:
                    time.sleep(1)

        except KeyboardInterrupt:
            print("Message waiting interrupted")

    def is_connected(self) -> bool:
        """
        Check if client is connected to broker.

        Returns:
            True if connected, False otherwise
        """
        return self._connected

    def get_subscriptions(self) -> Dict[str, int]:
        """
        Get current subscriptions.

        Returns:
            Dictionary of topic: qos pairs
        """
        return self._subscriptions.copy()

    def set_last_will(self, topic: str, payload: str, qos: int = 1, retain: bool = False):
        """
        Set Last Will and Testament message.
        Must be called before connecting.

        Args:
            topic: LWT topic
            payload: LWT message
            qos: LWT QoS
            retain: Whether to retain LWT message
        """
        if self._connected:
            raise RuntimeError("Cannot set LWT while connected. Disconnect first.")

        self.lwt_topic = topic
        self.lwt_payload = payload
        self.lwt_qos = qos
        self.lwt_retain = retain

        # Update client if already created
        if self._client:
            self._client.will_set(topic, payload, qos, retain)

    def publish_retained(self, topic: str, payload: str, qos: Optional[int] = None):
        """
        Publish retained message (shorthand for publish with retain=True).

        Args:
            topic: Topic to publish to
            payload: Message payload
            qos: Quality of Service
        """
        return self.publish(topic, payload, qos, retain=True)

    def clear_retained(self, topic: str):
        """
        Clear retained message on topic by publishing empty payload.

        Args:
            topic: Topic to clear
        """
        return self.publish(topic, "", retain=True)

    def close(self):
        """Close MQTT connection and cleanup resources."""
        self.disconnect()
        self._client = None
        self._subscriptions.clear()
        self._message_callbacks.clear()


# Module metadata
__all__ = ['MQTTModule']
