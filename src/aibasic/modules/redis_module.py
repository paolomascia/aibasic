"""
Redis Module for Caching and Key-Value Store

This module provides connection management for Redis.
Configuration is loaded from aibasic.conf under the [redis] section.

Supports:
- No authentication (default)
- Password authentication (AUTH)
- ACL username/password authentication (Redis 6+)
- SSL/TLS connections
- SSL/TLS without certificate verification (for development)
- Connection pooling
- All Redis data types: strings, hashes, lists, sets, sorted sets
- Pub/Sub messaging
- Transactions
- Pipelining

Example configuration in aibasic.conf:
    [redis]
    HOST=localhost
    PORT=6379
    DB=0
    PASSWORD=secret

    # SSL/TLS Settings (optional)
    USE_SSL=false
    SSL_VERIFY=true
    SSL_CA_CERT=/path/to/ca.pem
    SSL_CLIENT_CERT=/path/to/client-cert.pem
    SSL_CLIENT_KEY=/path/to/client-key.pem

    # ACL (Redis 6+)
    USERNAME=default

    # Connection Pool
    MAX_CONNECTIONS=50
    SOCKET_TIMEOUT=5
    SOCKET_CONNECT_TIMEOUT=5

Usage in generated code:
    from aibasic.modules import RedisModule

    # Initialize module (happens once per program)
    redis = RedisModule.from_config(config_path="aibasic.conf")

    # Basic operations
    redis.set('key', 'value', ex=3600)
    value = redis.get('key')

    # Hash operations
    redis.hset('user:123', mapping={'name': 'Alice', 'age': 30})
    user = redis.hgetall('user:123')

    # List operations
    redis.lpush('queue', 'task1', 'task2')
    task = redis.rpop('queue')
"""

import configparser
import json
import ssl
import threading
from pathlib import Path
from typing import Optional, Dict, Any, List, Union

import redis
from redis import Redis, ConnectionPool


class RedisModule:
    """
    Redis connection manager with pooling and full SSL/TLS support.

    Supports all Redis operations and authentication methods.
    """

    _instance = None
    _lock = threading.Lock()

    def __init__(
        self,
        host: str = 'localhost',
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        username: Optional[str] = None,
        use_ssl: bool = False,
        ssl_verify: bool = True,
        ssl_ca_cert: Optional[str] = None,
        ssl_client_cert: Optional[str] = None,
        ssl_client_key: Optional[str] = None,
        max_connections: int = 50,
        socket_timeout: int = 5,
        socket_connect_timeout: int = 5,
        decode_responses: bool = True
    ):
        """
        Initialize the Redis module.

        Args:
            host: Redis host
            port: Redis port (default 6379, 6380 for SSL)
            db: Database number (0-15)
            password: Password for AUTH command
            username: Username for ACL (Redis 6+)
            use_ssl: Enable SSL/TLS connection
            ssl_verify: Verify SSL certificates (set False for self-signed)
            ssl_ca_cert: Path to CA certificate file
            ssl_client_cert: Path to client certificate file
            ssl_client_key: Path to client key file
            max_connections: Maximum connections in pool
            socket_timeout: Socket timeout in seconds
            socket_connect_timeout: Socket connect timeout in seconds
            decode_responses: Decode responses to strings (vs bytes)
        """
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.username = username
        self.use_ssl = use_ssl
        self.ssl_verify = ssl_verify
        self.max_connections = max_connections
        self.decode_responses = decode_responses

        # Build connection parameters
        connection_params = {
            'host': host,
            'port': port,
            'db': db,
            'password': password,
            'username': username,
            'max_connections': max_connections,
            'socket_timeout': socket_timeout,
            'socket_connect_timeout': socket_connect_timeout,
            'decode_responses': decode_responses,
        }

        # SSL/TLS configuration
        if use_ssl:
            connection_params['ssl'] = True

            # SSL certificate verification
            if not ssl_verify:
                # Skip certificate verification
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                connection_params['ssl_cert_reqs'] = ssl.CERT_NONE
                print("[RedisModule] ⚠️  SSL certificate verification DISABLED")
            else:
                # Verify certificates
                if ssl_ca_cert:
                    connection_params['ssl_ca_certs'] = ssl_ca_cert

                connection_params['ssl_cert_reqs'] = ssl.CERT_REQUIRED

            # Client certificates
            if ssl_client_cert:
                connection_params['ssl_certfile'] = ssl_client_cert
            if ssl_client_key:
                connection_params['ssl_keyfile'] = ssl_client_key

        # Create connection pool
        self.pool = ConnectionPool(**connection_params)
        self.client = Redis(connection_pool=self.pool)

        # Test connection
        try:
            self.client.ping()
            auth_info = f"{username}@" if username else ""
            print(f"[RedisModule] Connected to Redis: {auth_info}{host}:{port}/{db}")
        except Exception as e:
            raise RuntimeError(f"Failed to connect to Redis: {e}")

    @classmethod
    def from_config(cls, config_path: str = "aibasic.conf") -> 'RedisModule':
        """
        Create a RedisModule from configuration file.
        Uses singleton pattern to ensure only one pool exists.

        Args:
            config_path: Path to aibasic.conf file

        Returns:
            RedisModule instance

        Raises:
            FileNotFoundError: If config file doesn't exist
            KeyError: If required configuration is missing
        """
        with cls._lock:
            if cls._instance is None:
                config = configparser.ConfigParser()
                path = Path(config_path)

                if not path.exists():
                    raise FileNotFoundError(f"Configuration file not found: {config_path}")

                config.read(path)

                if 'redis' not in config:
                    raise KeyError("Missing [redis] section in aibasic.conf")

                redis_config = config['redis']

                # Connection
                host = redis_config.get('HOST', 'localhost')
                port = redis_config.getint('PORT', 6379)
                db = redis_config.getint('DB', 0)
                password = redis_config.get('PASSWORD', None)
                username = redis_config.get('USERNAME', None)

                # SSL/TLS
                use_ssl = redis_config.getboolean('USE_SSL', False)
                ssl_verify = redis_config.getboolean('SSL_VERIFY', True)
                ssl_ca_cert = redis_config.get('SSL_CA_CERT', None)
                ssl_client_cert = redis_config.get('SSL_CLIENT_CERT', None)
                ssl_client_key = redis_config.get('SSL_CLIENT_KEY', None)

                # Pool settings
                max_connections = redis_config.getint('MAX_CONNECTIONS', 50)
                socket_timeout = redis_config.getint('SOCKET_TIMEOUT', 5)
                socket_connect_timeout = redis_config.getint('SOCKET_CONNECT_TIMEOUT', 5)
                decode_responses = redis_config.getboolean('DECODE_RESPONSES', True)

                cls._instance = cls(
                    host=host,
                    port=port,
                    db=db,
                    password=password,
                    username=username,
                    use_ssl=use_ssl,
                    ssl_verify=ssl_verify,
                    ssl_ca_cert=ssl_ca_cert,
                    ssl_client_cert=ssl_client_cert,
                    ssl_client_key=ssl_client_key,
                    max_connections=max_connections,
                    socket_timeout=socket_timeout,
                    socket_connect_timeout=socket_connect_timeout,
                    decode_responses=decode_responses
                )

            return cls._instance

    # ==================== String Operations ====================

    def set(self, key: str, value: Any, ex: Optional[int] = None, px: Optional[int] = None, nx: bool = False, xx: bool = False) -> bool:
        """Set key to value with optional expiration."""
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        return self.client.set(key, value, ex=ex, px=px, nx=nx, xx=xx)

    def get(self, key: str) -> Optional[str]:
        """Get value of key."""
        value = self.client.get(key)
        if value and self.decode_responses:
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        return value

    def mset(self, mapping: Dict[str, Any]) -> bool:
        """Set multiple keys to multiple values."""
        processed = {k: json.dumps(v) if isinstance(v, (dict, list)) else v for k, v in mapping.items()}
        return self.client.mset(processed)

    def mget(self, keys: List[str]) -> List[Optional[str]]:
        """Get values of multiple keys."""
        return self.client.mget(keys)

    def incr(self, key: str, amount: int = 1) -> int:
        """Increment key by amount."""
        return self.client.incr(key, amount)

    def decr(self, key: str, amount: int = 1) -> int:
        """Decrement key by amount."""
        return self.client.decr(key, amount)

    # ==================== Hash Operations ====================

    def hset(self, key: str, field: str = None, value: Any = None, mapping: Dict = None) -> int:
        """Set hash field to value or set multiple fields."""
        if mapping:
            return self.client.hset(key, mapping=mapping)
        return self.client.hset(key, field, value)

    def hget(self, key: str, field: str) -> Optional[str]:
        """Get value of hash field."""
        return self.client.hget(key, field)

    def hgetall(self, key: str) -> Dict:
        """Get all fields and values in hash."""
        return self.client.hgetall(key)

    def hdel(self, key: str, *fields: str) -> int:
        """Delete one or more hash fields."""
        return self.client.hdel(key, *fields)

    def hincrby(self, key: str, field: str, amount: int = 1) -> int:
        """Increment hash field by amount."""
        return self.client.hincrby(key, field, amount)

    # ==================== List Operations ====================

    def lpush(self, key: str, *values: Any) -> int:
        """Push values to the left of list."""
        return self.client.lpush(key, *values)

    def rpush(self, key: str, *values: Any) -> int:
        """Push values to the right of list."""
        return self.client.rpush(key, *values)

    def lpop(self, key: str) -> Optional[str]:
        """Pop value from left of list."""
        return self.client.lpop(key)

    def rpop(self, key: str) -> Optional[str]:
        """Pop value from right of list."""
        return self.client.rpop(key)

    def lrange(self, key: str, start: int, end: int) -> List[str]:
        """Get range of elements from list."""
        return self.client.lrange(key, start, end)

    def llen(self, key: str) -> int:
        """Get length of list."""
        return self.client.llen(key)

    # ==================== Set Operations ====================

    def sadd(self, key: str, *members: Any) -> int:
        """Add members to set."""
        return self.client.sadd(key, *members)

    def srem(self, key: str, *members: Any) -> int:
        """Remove members from set."""
        return self.client.srem(key, *members)

    def smembers(self, key: str) -> set:
        """Get all members of set."""
        return self.client.smembers(key)

    def sismember(self, key: str, member: Any) -> bool:
        """Check if member is in set."""
        return self.client.sismember(key, member)

    # ==================== Sorted Set Operations ====================

    def zadd(self, key: str, mapping: Dict[str, float]) -> int:
        """Add members with scores to sorted set."""
        return self.client.zadd(key, mapping)

    def zrange(self, key: str, start: int, end: int, withscores: bool = False) -> List:
        """Get range of members from sorted set."""
        return self.client.zrange(key, start, end, withscores=withscores)

    def zrem(self, key: str, *members: Any) -> int:
        """Remove members from sorted set."""
        return self.client.zrem(key, *members)

    def zscore(self, key: str, member: Any) -> Optional[float]:
        """Get score of member in sorted set."""
        return self.client.zscore(key, member)

    # ==================== Key Operations ====================

    def delete(self, *keys: str) -> int:
        """Delete one or more keys."""
        return self.client.delete(*keys)

    def exists(self, *keys: str) -> int:
        """Check if keys exist."""
        return self.client.exists(*keys)

    def expire(self, key: str, seconds: int) -> bool:
        """Set expiration on key in seconds."""
        return self.client.expire(key, seconds)

    def ttl(self, key: str) -> int:
        """Get time to live of key in seconds."""
        return self.client.ttl(key)

    def keys(self, pattern: str = '*') -> List[str]:
        """Get all keys matching pattern."""
        return self.client.keys(pattern)

    def scan(self, cursor: int = 0, match: str = None, count: int = 10):
        """Scan keys incrementally."""
        return self.client.scan(cursor, match, count)

    # ==================== Pub/Sub Operations ====================

    def publish(self, channel: str, message: Any) -> int:
        """Publish message to channel."""
        if isinstance(message, (dict, list)):
            message = json.dumps(message)
        return self.client.publish(channel, message)

    def subscribe(self, *channels: str):
        """Subscribe to channels (returns pubsub object)."""
        pubsub = self.client.pubsub()
        pubsub.subscribe(*channels)
        return pubsub

    # ==================== Transaction/Pipeline Operations ====================

    def pipeline(self, transaction: bool = True):
        """Create a pipeline for batch operations."""
        return self.client.pipeline(transaction=transaction)

    # ==================== Utility Operations ====================

    def flushdb(self):
        """Delete all keys in current database."""
        return self.client.flushdb()

    def flushall(self):
        """Delete all keys in all databases."""
        return self.client.flushall()

    def ping(self) -> bool:
        """Ping Redis server."""
        return self.client.ping()

    def info(self, section: str = None) -> Dict:
        """Get Redis server information."""
        return self.client.info(section)

    def dbsize(self) -> int:
        """Get number of keys in current database."""
        return self.client.dbsize()

    def close(self):
        """Close connection pool."""
        if self.pool:
            self.pool.disconnect()
            print("[RedisModule] Connection pool closed")

    def get_connection_info(self) -> Dict[str, Any]:
        """
        Get current connection information.

        Returns:
            dict: Connection details
        """
        return {
            "host": self.host,
            "port": self.port,
            "db": self.db,
            "username": self.username,
            "use_ssl": self.use_ssl,
            "ssl_verify": self.ssl_verify,
            "max_connections": self.max_connections
        }

    def __del__(self):
        """Destructor to ensure connection is closed."""
        self.close()
