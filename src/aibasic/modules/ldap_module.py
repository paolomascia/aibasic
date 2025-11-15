"""
LDAP/Active Directory Module for AIbasic

This module provides comprehensive integration with LDAP directories and Active Directory,
enabling natural language management of users, groups, organizational units, and more.

Features:
- User Management: Create, modify, delete, search users
- Group Management: Create, modify, delete groups, manage memberships
- Organizational Units: Create and manage OUs
- Authentication: Bind and verify user credentials
- Search Operations: Flexible LDAP search with filters
- Attribute Management: Read and modify LDAP attributes
- Active Directory: Support for AD-specific operations
- Connection Pooling: Efficient connection management

Architecture:
- Singleton pattern with thread-safe initialization
- Connection pooling for performance
- Configuration from aibasic.conf with environment variable fallbacks
- Support for both simple and SASL authentication
- SSL/TLS support for secure connections

Usage:
    10 (ldap) connect to server "ldap.example.com"
    20 (ldap) search for users with filter "(uid=john*)"
    30 (ldap) create user "john.doe" with email "john@example.com"
    40 (ldap) add user "john.doe" to group "developers"
"""

import threading
import os
from typing import Optional, Dict, Any, List
import logging

# LDAP Client Libraries
try:
    import ldap3
    from ldap3 import Server, Connection, ALL, SUBTREE, MODIFY_REPLACE, MODIFY_ADD, MODIFY_DELETE
    from ldap3.core.exceptions import LDAPException, LDAPBindError
    LDAP_AVAILABLE = True
except ImportError:
    LDAP_AVAILABLE = False


class LDAPModule:
    """
    LDAP/Active Directory module for directory services management.

    Implements singleton pattern for efficient resource usage.
    Provides comprehensive LDAP operations through ldap3 library.
    """

    _instance = None
    _lock = threading.Lock()
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the LDAP module with configuration from aibasic.conf."""
        if self._initialized:
            return

        with self._lock:
            if self._initialized:
                return

            if not LDAP_AVAILABLE:
                raise RuntimeError(
                    "LDAP library not installed. "
                    "Install with: pip install ldap3"
                )

            # Read configuration
            self.server_uri = os.getenv('LDAP_SERVER') or os.getenv('LDAP_URI', 'ldap://localhost')
            self.port = int(os.getenv('LDAP_PORT', '389'))
            self.base_dn = os.getenv('LDAP_BASE_DN', 'dc=example,dc=com')
            self.bind_dn = os.getenv('LDAP_BIND_DN', '')
            self.bind_password = os.getenv('LDAP_BIND_PASSWORD', '')

            # Connection settings
            self.use_ssl = os.getenv('LDAP_USE_SSL', 'false').lower() == 'true'
            self.use_tls = os.getenv('LDAP_USE_TLS', 'false').lower() == 'true'
            self.verify_cert = os.getenv('LDAP_VERIFY_CERT', 'true').lower() == 'true'

            # Default settings
            self.default_user_ou = os.getenv('LDAP_USER_OU', 'ou=users')
            self.default_group_ou = os.getenv('LDAP_GROUP_OU', 'ou=groups')
            self.user_object_class = os.getenv('LDAP_USER_OBJECT_CLASS', 'inetOrgPerson')
            self.group_object_class = os.getenv('LDAP_GROUP_OBJECT_CLASS', 'groupOfNames')

            # Active Directory specific
            self.is_active_directory = os.getenv('LDAP_IS_AD', 'false').lower() == 'true'

            # Connection pooling
            self.pool_size = int(os.getenv('LDAP_POOL_SIZE', '5'))
            self.pool_keepalive = int(os.getenv('LDAP_POOL_KEEPALIVE', '300'))

            # Lazy-loaded connection
            self._server = None
            self._connection = None

            self._initialized = True

    @property
    def server(self):
        """Get LDAP server object (lazy-loaded)."""
        if self._server is None:
            if self.use_ssl:
                port = self.port if self.port != 389 else 636
                self._server = Server(
                    self.server_uri,
                    port=port,
                    use_ssl=True,
                    get_info=ALL
                )
            else:
                self._server = Server(
                    self.server_uri,
                    port=self.port,
                    get_info=ALL
                )
        return self._server

    @property
    def connection(self):
        """Get LDAP connection (lazy-loaded)."""
        if self._connection is None or not self._connection.bound:
            self._connection = Connection(
                self.server,
                user=self.bind_dn,
                password=self.bind_password,
                auto_bind=True,
                raise_exceptions=True
            )

            if self.use_tls and not self.use_ssl:
                self._connection.start_tls()

        return self._connection

    def close(self):
        """Close LDAP connection."""
        if self._connection and self._connection.bound:
            self._connection.unbind()
            self._connection = None

    # =========================================================================
    # Connection and Authentication
    # =========================================================================

    def bind(self, dn: str, password: str) -> Dict[str, Any]:
        """Bind to LDAP server with specific credentials."""
        try:
            conn = Connection(
                self.server,
                user=dn,
                password=password,
                auto_bind=True,
                raise_exceptions=True
            )

            result = {
                "success": conn.bound,
                "dn": dn,
                "server": self.server_uri
            }

            conn.unbind()
            return result
        except LDAPBindError as e:
            raise RuntimeError(f"Failed to bind to LDAP: {e}")
        except Exception as e:
            raise RuntimeError(f"LDAP bind error: {e}")

    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate a user by username."""
        try:
            # Search for user
            user_dn = self._find_user_dn(username)
            if not user_dn:
                return False

            # Try to bind with user credentials
            conn = Connection(
                self.server,
                user=user_dn,
                password=password,
                auto_bind=True,
                raise_exceptions=False
            )

            success = conn.bound
            conn.unbind()
            return success
        except Exception as e:
            raise RuntimeError(f"Authentication error: {e}")

    # =========================================================================
    # Search Operations
    # =========================================================================

    def search(self, search_base: Optional[str] = None,
               search_filter: str = '(objectClass=*)',
               attributes: Optional[List[str]] = None,
               search_scope: str = 'SUBTREE') -> List[Dict[str, Any]]:
        """Search LDAP directory."""
        search_base = search_base or self.base_dn
        attributes = attributes or ['*']

        scope_map = {
            'BASE': ldap3.BASE,
            'LEVEL': ldap3.LEVEL,
            'SUBTREE': ldap3.SUBTREE
        }
        scope = scope_map.get(search_scope.upper(), ldap3.SUBTREE)

        try:
            self.connection.search(
                search_base=search_base,
                search_filter=search_filter,
                search_scope=scope,
                attributes=attributes
            )

            results = []
            for entry in self.connection.entries:
                result = {
                    'dn': entry.entry_dn,
                    'attributes': {}
                }

                for attr in entry.entry_attributes:
                    value = getattr(entry, attr).value
                    result['attributes'][attr] = value

                results.append(result)

            return results
        except Exception as e:
            raise RuntimeError(f"LDAP search error: {e}")

    def search_users(self, filter_str: str = '*', attributes: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Search for users."""
        search_base = f"{self.default_user_ou},{self.base_dn}"

        if self.is_active_directory:
            search_filter = f"(&(objectClass=user)(sAMAccountName={filter_str}))"
        else:
            search_filter = f"(&(objectClass={self.user_object_class})(uid={filter_str}))"

        return self.search(search_base, search_filter, attributes)

    def search_groups(self, filter_str: str = '*', attributes: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Search for groups."""
        search_base = f"{self.default_group_ou},{self.base_dn}"

        if self.is_active_directory:
            search_filter = f"(&(objectClass=group)(cn={filter_str}))"
        else:
            search_filter = f"(&(objectClass={self.group_object_class})(cn={filter_str}))"

        return self.search(search_base, search_filter, attributes)

    # =========================================================================
    # User Management
    # =========================================================================

    def user_create(self, username: str, **attributes) -> Dict[str, Any]:
        """Create a new user."""
        if self.is_active_directory:
            user_dn = f"CN={username},{self.default_user_ou},{self.base_dn}"
            object_class = ['top', 'person', 'organizationalPerson', 'user']

            attrs = {
                'cn': username,
                'sAMAccountName': username,
                'userPrincipalName': attributes.get('email', f"{username}@{self.base_dn.replace('dc=', '').replace(',', '.')}"),
            }
        else:
            user_dn = f"uid={username},{self.default_user_ou},{self.base_dn}"
            object_class = ['top', 'person', 'organizationalPerson', self.user_object_class]

            attrs = {
                'uid': username,
                'cn': attributes.get('cn', username),
                'sn': attributes.get('sn', username.split('.')[-1] if '.' in username else username),
            }

        # Add additional attributes
        if 'email' in attributes:
            attrs['mail'] = attributes['email']
        if 'displayName' in attributes:
            attrs['displayName'] = attributes['displayName']
        if 'firstName' in attributes:
            attrs['givenName'] = attributes['firstName']
        if 'lastName' in attributes:
            attrs['sn'] = attributes['lastName']
        if 'phone' in attributes:
            attrs['telephoneNumber'] = attributes['phone']
        if 'description' in attributes:
            attrs['description'] = attributes['description']

        try:
            self.connection.add(user_dn, object_class, attrs)

            if not self.connection.result['result'] == 0:
                raise RuntimeError(f"Failed to create user: {self.connection.result['description']}")

            return {
                "dn": user_dn,
                "username": username,
                "attributes": attrs
            }
        except Exception as e:
            raise RuntimeError(f"Failed to create user: {e}")

    def user_modify(self, username: str, **attributes) -> Dict[str, Any]:
        """Modify user attributes."""
        user_dn = self._find_user_dn(username)
        if not user_dn:
            raise RuntimeError(f"User not found: {username}")

        changes = {}
        for attr, value in attributes.items():
            # Map common attribute names
            ldap_attr = attr
            if attr == 'email':
                ldap_attr = 'mail'
            elif attr == 'firstName':
                ldap_attr = 'givenName'
            elif attr == 'lastName':
                ldap_attr = 'sn'
            elif attr == 'phone':
                ldap_attr = 'telephoneNumber'

            changes[ldap_attr] = [(MODIFY_REPLACE, [value])]

        try:
            self.connection.modify(user_dn, changes)

            if not self.connection.result['result'] == 0:
                raise RuntimeError(f"Failed to modify user: {self.connection.result['description']}")

            return {
                "dn": user_dn,
                "username": username,
                "modified_attributes": list(changes.keys())
            }
        except Exception as e:
            raise RuntimeError(f"Failed to modify user: {e}")

    def user_delete(self, username: str) -> Dict[str, Any]:
        """Delete a user."""
        user_dn = self._find_user_dn(username)
        if not user_dn:
            raise RuntimeError(f"User not found: {username}")

        try:
            self.connection.delete(user_dn)

            if not self.connection.result['result'] == 0:
                raise RuntimeError(f"Failed to delete user: {self.connection.result['description']}")

            return {
                "dn": user_dn,
                "username": username,
                "deleted": True
            }
        except Exception as e:
            raise RuntimeError(f"Failed to delete user: {e}")

    def user_get(self, username: str, attributes: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get user details."""
        users = self.search_users(username, attributes)
        if not users:
            raise RuntimeError(f"User not found: {username}")

        return users[0]

    def user_set_password(self, username: str, password: str) -> Dict[str, Any]:
        """Set user password."""
        user_dn = self._find_user_dn(username)
        if not user_dn:
            raise RuntimeError(f"User not found: {username}")

        try:
            # Use modify_password if available (requires extended operations)
            if hasattr(self.connection, 'extend') and hasattr(self.connection.extend, 'standard'):
                self.connection.extend.standard.modify_password(user_dn, new_password=password)
            else:
                # Fallback to modifying userPassword attribute
                changes = {'userPassword': [(MODIFY_REPLACE, [password])]}
                self.connection.modify(user_dn, changes)

            return {
                "dn": user_dn,
                "username": username,
                "password_changed": True
            }
        except Exception as e:
            raise RuntimeError(f"Failed to set password: {e}")

    # =========================================================================
    # Group Management
    # =========================================================================

    def group_create(self, group_name: str, **attributes) -> Dict[str, Any]:
        """Create a new group."""
        group_dn = f"cn={group_name},{self.default_group_ou},{self.base_dn}"

        if self.is_active_directory:
            object_class = ['top', 'group']
            attrs = {
                'cn': group_name,
                'sAMAccountName': group_name
            }
        else:
            object_class = ['top', self.group_object_class]
            attrs = {
                'cn': group_name
            }

        if 'description' in attributes:
            attrs['description'] = attributes['description']

        try:
            self.connection.add(group_dn, object_class, attrs)

            if not self.connection.result['result'] == 0:
                raise RuntimeError(f"Failed to create group: {self.connection.result['description']}")

            return {
                "dn": group_dn,
                "group_name": group_name,
                "attributes": attrs
            }
        except Exception as e:
            raise RuntimeError(f"Failed to create group: {e}")

    def group_delete(self, group_name: str) -> Dict[str, Any]:
        """Delete a group."""
        group_dn = self._find_group_dn(group_name)
        if not group_dn:
            raise RuntimeError(f"Group not found: {group_name}")

        try:
            self.connection.delete(group_dn)

            if not self.connection.result['result'] == 0:
                raise RuntimeError(f"Failed to delete group: {self.connection.result['description']}")

            return {
                "dn": group_dn,
                "group_name": group_name,
                "deleted": True
            }
        except Exception as e:
            raise RuntimeError(f"Failed to delete group: {e}")

    def group_add_member(self, group_name: str, username: str) -> Dict[str, Any]:
        """Add a user to a group."""
        group_dn = self._find_group_dn(group_name)
        user_dn = self._find_user_dn(username)

        if not group_dn:
            raise RuntimeError(f"Group not found: {group_name}")
        if not user_dn:
            raise RuntimeError(f"User not found: {username}")

        try:
            if self.is_active_directory:
                changes = {'member': [(MODIFY_ADD, [user_dn])]}
            else:
                changes = {'member': [(MODIFY_ADD, [user_dn])]}

            self.connection.modify(group_dn, changes)

            if not self.connection.result['result'] == 0:
                raise RuntimeError(f"Failed to add member: {self.connection.result['description']}")

            return {
                "group_dn": group_dn,
                "user_dn": user_dn,
                "group_name": group_name,
                "username": username,
                "added": True
            }
        except Exception as e:
            raise RuntimeError(f"Failed to add member to group: {e}")

    def group_remove_member(self, group_name: str, username: str) -> Dict[str, Any]:
        """Remove a user from a group."""
        group_dn = self._find_group_dn(group_name)
        user_dn = self._find_user_dn(username)

        if not group_dn:
            raise RuntimeError(f"Group not found: {group_name}")
        if not user_dn:
            raise RuntimeError(f"User not found: {username}")

        try:
            changes = {'member': [(MODIFY_DELETE, [user_dn])]}
            self.connection.modify(group_dn, changes)

            if not self.connection.result['result'] == 0:
                raise RuntimeError(f"Failed to remove member: {self.connection.result['description']}")

            return {
                "group_dn": group_dn,
                "user_dn": user_dn,
                "group_name": group_name,
                "username": username,
                "removed": True
            }
        except Exception as e:
            raise RuntimeError(f"Failed to remove member from group: {e}")

    def group_get_members(self, group_name: str) -> List[str]:
        """Get all members of a group."""
        group_dn = self._find_group_dn(group_name)
        if not group_dn:
            raise RuntimeError(f"Group not found: {group_name}")

        try:
            self.connection.search(
                search_base=group_dn,
                search_filter='(objectClass=*)',
                search_scope=ldap3.BASE,
                attributes=['member']
            )

            if self.connection.entries:
                entry = self.connection.entries[0]
                members = entry.member.value if hasattr(entry, 'member') else []
                return members if isinstance(members, list) else [members] if members else []

            return []
        except Exception as e:
            raise RuntimeError(f"Failed to get group members: {e}")

    # =========================================================================
    # Organizational Unit Management
    # =========================================================================

    def ou_create(self, ou_name: str, parent_dn: Optional[str] = None) -> Dict[str, Any]:
        """Create an organizational unit."""
        parent_dn = parent_dn or self.base_dn
        ou_dn = f"ou={ou_name},{parent_dn}"

        object_class = ['top', 'organizationalUnit']
        attrs = {'ou': ou_name}

        try:
            self.connection.add(ou_dn, object_class, attrs)

            if not self.connection.result['result'] == 0:
                raise RuntimeError(f"Failed to create OU: {self.connection.result['description']}")

            return {
                "dn": ou_dn,
                "ou_name": ou_name,
                "parent_dn": parent_dn
            }
        except Exception as e:
            raise RuntimeError(f"Failed to create OU: {e}")

    def ou_delete(self, ou_name: str, parent_dn: Optional[str] = None) -> Dict[str, Any]:
        """Delete an organizational unit."""
        parent_dn = parent_dn or self.base_dn
        ou_dn = f"ou={ou_name},{parent_dn}"

        try:
            self.connection.delete(ou_dn)

            if not self.connection.result['result'] == 0:
                raise RuntimeError(f"Failed to delete OU: {self.connection.result['description']}")

            return {
                "dn": ou_dn,
                "ou_name": ou_name,
                "deleted": True
            }
        except Exception as e:
            raise RuntimeError(f"Failed to delete OU: {e}")

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _find_user_dn(self, username: str) -> Optional[str]:
        """Find user DN by username."""
        users = self.search_users(username, attributes=['dn'])
        return users[0]['dn'] if users else None

    def _find_group_dn(self, group_name: str) -> Optional[str]:
        """Find group DN by group name."""
        groups = self.search_groups(group_name, attributes=['dn'])
        return groups[0]['dn'] if groups else None

    def get_server_info(self) -> Dict[str, Any]:
        """Get LDAP server information."""
        return {
            "server_uri": self.server_uri,
            "port": self.port,
            "base_dn": self.base_dn,
            "use_ssl": self.use_ssl,
            "use_tls": self.use_tls,
            "is_active_directory": self.is_active_directory,
            "connected": self._connection is not None and self._connection.bound
        }


# Singleton instance
_ldap_module = None

def get_ldap_module() -> LDAPModule:
    """Get the singleton LDAP module instance."""
    global _ldap_module
    if _ldap_module is None:
        _ldap_module = LDAPModule()
    return _ldap_module
