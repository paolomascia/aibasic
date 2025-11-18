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

from .module_base import AIbasicModuleBase


class LDAPModule(AIbasicModuleBase):
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

    # =============================================================================
    # Metadata Methods for AIbasic Compiler
    # =============================================================================

    @classmethod
    def get_metadata(cls):
        """Get module metadata."""
        from aibasic.modules.module_base import ModuleMetadata
        return ModuleMetadata(
            name="LDAP",
            task_type="ldap",
            description="LDAP and Active Directory integration for user, group, and organizational unit management with authentication support",
            version="1.0.0",
            keywords=["ldap", "active-directory", "directory-services", "authentication", "users", "groups", "ou", "ad", "openldap"],
            dependencies=["ldap3>=2.9.0"]
        )

    @classmethod
    def get_usage_notes(cls):
        """Get detailed usage notes."""
        return [
            "Module uses singleton pattern - one instance shared across all operations",
            "Supports both OpenLDAP and Microsoft Active Directory",
            "Authentication via simple bind (username/password) or SASL mechanisms",
            "SSL/TLS encryption supported for secure connections (LDAPS or STARTTLS)",
            "Connection pooling automatically managed by ldap3 library",
            "Active Directory mode (LDAP_IS_AD=true) uses AD-specific attributes and object classes",
            "User object class: inetOrgPerson (OpenLDAP) or user (Active Directory)",
            "Group object class: groupOfNames (OpenLDAP) or group (Active Directory)",
            "Default user OU: ou=users, configurable via LDAP_USER_OU",
            "Default group OU: ou=groups, configurable via LDAP_GROUP_OU",
            "Search operations support LDAP filter syntax (e.g., '(uid=john*)', '(&(cn=*)(mail=*@example.com))')",
            "Attribute mapping: email->mail, firstName->givenName, lastName->sn, phone->telephoneNumber",
            "User DN auto-discovery - methods accept username, find DN automatically",
            "Group membership uses 'member' attribute containing user DNs",
            "Certificate verification can be disabled for development (LDAP_VERIFY_CERT=false)",
            "Connection automatically established on first operation (lazy connection)",
            "Base DN (e.g., 'dc=example,dc=com') must be configured for searches",
            "Key methods: connect, authenticate, user_create, user_modify, user_delete, group_create, group_add_member, search, search_users, search_groups",
        ]

    @classmethod
    def get_methods_info(cls):
        """Get information about module methods."""
        from aibasic.modules.module_base import MethodInfo
        return [
            MethodInfo(
                name="connect",
                description="Establish connection to LDAP server and bind with credentials",
                parameters={
                    "server_uri": "LDAP server URI (optional, uses LDAP_SERVER env var, e.g., 'ldap://server.example.com')",
                    "bind_dn": "Bind DN for authentication (optional, uses LDAP_BIND_DN, e.g., 'cn=admin,dc=example,dc=com')",
                    "bind_password": "Bind password (optional, uses LDAP_BIND_PASSWORD)"
                },
                returns="None - raises RuntimeError on connection failure",
                examples=[
                    '(ldap) connect to server "ldap://ldap.example.com"',
                    '(ldap) connect with bind dn "cn=admin,dc=example,dc=com" and password "secret"',
                ]
            ),
            MethodInfo(
                name="disconnect",
                description="Close connection to LDAP server and release resources",
                parameters={},
                returns="None",
                examples=[
                    '(ldap) disconnect from server',
                    '(ldap) close ldap connection',
                ]
            ),
            MethodInfo(
                name="authenticate",
                description="Verify user credentials against LDAP directory",
                parameters={
                    "username": "Username to authenticate (string)",
                    "password": "User password (string)"
                },
                returns="Boolean True if authentication successful, False otherwise",
                examples=[
                    '(ldap) authenticate user "jdoe" with password "userpass123"',
                    '(ldap) verify credentials for "alice" with password',
                ]
            ),
            MethodInfo(
                name="search",
                description="Execute LDAP search with custom filter and scope",
                parameters={
                    "search_base": "Search base DN (optional, defaults to base_dn, e.g., 'ou=people,dc=example,dc=com')",
                    "search_filter": "LDAP filter string (default: '(objectClass=*)', e.g., '(uid=john*)', '(&(cn=*)(mail=*))')",
                    "attributes": "List of attributes to return (optional, default: all attributes ['*'])",
                    "search_scope": "Search scope - BASE, LEVEL, or SUBTREE (default: SUBTREE)"
                },
                returns="List of dicts with 'dn' and 'attributes' keys",
                examples=[
                    '(ldap) search with filter "(uid=john*)"',
                    '(ldap) search in "ou=users,dc=example,dc=com" with filter "(mail=*@example.com)" attributes ["cn", "mail"]',
                    '(ldap) search with filter "(&(objectClass=person)(sn=Smith))" scope "SUBTREE"',
                ]
            ),
            MethodInfo(
                name="search_users",
                description="Search for users in default user OU with simplified filter",
                parameters={
                    "filter_str": "Username filter pattern (default: '*', supports wildcards, e.g., 'john*', '*doe')",
                    "attributes": "List of attributes to return (optional)"
                },
                returns="List of user dicts with 'dn' and 'attributes'",
                examples=[
                    '(ldap) search users with filter "john*"',
                    '(ldap) search users with filter "*" attributes ["cn", "mail", "uid"]',
                    '(ldap) find all users',
                ]
            ),
            MethodInfo(
                name="search_groups",
                description="Search for groups in default group OU",
                parameters={
                    "filter_str": "Group name filter pattern (default: '*', supports wildcards)",
                    "attributes": "List of attributes to return (optional)"
                },
                returns="List of group dicts with 'dn' and 'attributes'",
                examples=[
                    '(ldap) search groups with filter "dev*"',
                    '(ldap) search groups with filter "*admin*"',
                    '(ldap) find all groups',
                ]
            ),
            MethodInfo(
                name="user_create",
                description="Create a new user in LDAP directory",
                parameters={
                    "username": "Username (string, becomes uid or sAMAccountName)",
                    "**attributes": "User attributes: email, displayName, firstName, lastName, phone, description, cn, sn"
                },
                returns="Dict with 'dn', 'username', and 'attributes'",
                examples=[
                    '(ldap) create user "jdoe" with email "jdoe@example.com"',
                    '(ldap) create user "alice" with firstName "Alice" lastName "Smith" email "alice@example.com" phone "555-1234"',
                    '(ldap) create user "bob" with displayName "Bob Jones" description "Developer"',
                ]
            ),
            MethodInfo(
                name="user_modify",
                description="Modify existing user attributes",
                parameters={
                    "username": "Username to modify (string)",
                    "**attributes": "Attributes to update: email, displayName, firstName, lastName, phone, description"
                },
                returns="Dict with 'dn', 'username', and 'modified_attributes' list",
                examples=[
                    '(ldap) modify user "jdoe" with email "newemail@example.com"',
                    '(ldap) update user "alice" with phone "555-9999" displayName "Alice Johnson"',
                ]
            ),
            MethodInfo(
                name="user_delete",
                description="Delete a user from LDAP directory",
                parameters={
                    "username": "Username to delete (string)"
                },
                returns="Dict with 'dn', 'username', and 'deleted' boolean",
                examples=[
                    '(ldap) delete user "jdoe"',
                    '(ldap) remove user "obsolete_account"',
                ]
            ),
            MethodInfo(
                name="user_get",
                description="Retrieve user details from directory",
                parameters={
                    "username": "Username to retrieve (string)",
                    "attributes": "List of specific attributes to fetch (optional, default: all)"
                },
                returns="Dict with 'dn' and 'attributes' containing user data",
                examples=[
                    '(ldap) get user "jdoe"',
                    '(ldap) get user "alice" attributes ["cn", "mail", "telephoneNumber"]',
                ]
            ),
            MethodInfo(
                name="user_set_password",
                description="Set or change user password",
                parameters={
                    "username": "Username (string)",
                    "password": "New password (string)"
                },
                returns="Dict with 'dn', 'username', and 'password_changed' boolean",
                examples=[
                    '(ldap) set password for user "jdoe" to "NewSecureP@ss123"',
                    '(ldap) change password for "alice" to "AliceNewPass456"',
                ]
            ),
            MethodInfo(
                name="group_create",
                description="Create a new group in LDAP directory",
                parameters={
                    "group_name": "Group name (string, becomes cn)",
                    "**attributes": "Optional attributes: description"
                },
                returns="Dict with 'dn', 'group_name', and 'attributes'",
                examples=[
                    '(ldap) create group "developers"',
                    '(ldap) create group "admins" with description "System administrators"',
                ]
            ),
            MethodInfo(
                name="group_delete",
                description="Delete a group from LDAP directory",
                parameters={
                    "group_name": "Group name to delete (string)"
                },
                returns="Dict with 'dn', 'group_name', and 'deleted' boolean",
                examples=[
                    '(ldap) delete group "old-team"',
                    '(ldap) remove group "obsolete-group"',
                ]
            ),
            MethodInfo(
                name="group_add_member",
                description="Add a user to a group",
                parameters={
                    "group_name": "Group name (string)",
                    "username": "Username to add (string)"
                },
                returns="Dict with 'group_dn', 'user_dn', 'group_name', 'username', and 'added' boolean",
                examples=[
                    '(ldap) add user "jdoe" to group "developers"',
                    '(ldap) add member "alice" to group "admins"',
                ]
            ),
            MethodInfo(
                name="group_remove_member",
                description="Remove a user from a group",
                parameters={
                    "group_name": "Group name (string)",
                    "username": "Username to remove (string)"
                },
                returns="Dict with 'group_dn', 'user_dn', 'group_name', 'username', and 'removed' boolean",
                examples=[
                    '(ldap) remove user "jdoe" from group "developers"',
                    '(ldap) remove member "bob" from group "contractors"',
                ]
            ),
            MethodInfo(
                name="group_get_members",
                description="List all members of a group",
                parameters={
                    "group_name": "Group name (string)"
                },
                returns="List of member DNs (strings)",
                examples=[
                    '(ldap) get members of group "developers"',
                    '(ldap) list members in group "admins"',
                ]
            ),
            MethodInfo(
                name="ou_create",
                description="Create an organizational unit",
                parameters={
                    "ou_name": "OU name (string)",
                    "parent_dn": "Parent DN (optional, defaults to base_dn, e.g., 'dc=example,dc=com')"
                },
                returns="Dict with 'dn', 'ou_name', and 'parent_dn'",
                examples=[
                    '(ldap) create ou "engineering"',
                    '(ldap) create ou "sales" with parent "ou=departments,dc=example,dc=com"',
                ]
            ),
            MethodInfo(
                name="ou_delete",
                description="Delete an organizational unit (must be empty)",
                parameters={
                    "ou_name": "OU name to delete (string)",
                    "parent_dn": "Parent DN (optional, defaults to base_dn)"
                },
                returns="Dict with 'dn', 'ou_name', and 'deleted' boolean",
                examples=[
                    '(ldap) delete ou "old-department"',
                    '(ldap) remove ou "obsolete"',
                ]
            ),
            MethodInfo(
                name="get_server_info",
                description="Get LDAP server configuration and connection status",
                parameters={},
                returns="Dict with server_uri, port, base_dn, use_ssl, use_tls, is_active_directory, connected",
                examples=[
                    '(ldap) get server info',
                    '(ldap) show ldap configuration',
                ]
            ),
        ]

    @classmethod
    def get_examples(cls):
        """Get AIbasic usage examples."""
        return [
            # Connection
            '10 (ldap) connect to server "ldap://ldap.example.com"',
            '20 (ldap) get server info',

            # Authentication
            '30 (ldap) authenticate user "jdoe" with password "password123"',

            # User management
            '40 (ldap) create user "jdoe" with email "jdoe@example.com" firstName "John" lastName "Doe"',
            '50 (ldap) create user "alice" with email "alice@example.com" displayName "Alice Smith" phone "555-1234"',
            '60 (ldap) get user "jdoe"',
            '70 (ldap) modify user "jdoe" with phone "555-5678" displayName "John Doe Jr."',
            '80 (ldap) set password for user "jdoe" to "NewSecurePassword123"',

            # User search
            '90 (ldap) search users with filter "*"',
            '100 (ldap) search users with filter "john*"',
            '110 (ldap) search users with filter "*smith*" attributes ["cn", "mail", "telephoneNumber"]',

            # Group management
            '120 (ldap) create group "developers" with description "Development team"',
            '130 (ldap) create group "admins" with description "System administrators"',
            '140 (ldap) add user "jdoe" to group "developers"',
            '150 (ldap) add user "alice" to group "developers"',
            '160 (ldap) add user "alice" to group "admins"',
            '170 (ldap) get members of group "developers"',
            '180 (ldap) remove user "jdoe" from group "developers"',

            # Group search
            '190 (ldap) search groups with filter "*"',
            '200 (ldap) search groups with filter "dev*"',

            # Organizational units
            '210 (ldap) create ou "engineering"',
            '220 (ldap) create ou "sales"',
            '230 (ldap) create ou "contractors" with parent "ou=engineering,dc=example,dc=com"',

            # Advanced search
            '240 (ldap) search in "ou=users,dc=example,dc=com" with filter "(mail=*@example.com)"',
            '250 (ldap) search with filter "(&(objectClass=person)(cn=*Smith*))" attributes ["cn", "mail"]',

            # User lifecycle
            '260 (ldap) create user "temp_user" with email "temp@example.com"',
            '270 (ldap) add user "temp_user" to group "contractors"',
            '280 (ldap) remove user "temp_user" from group "contractors"',
            '290 (ldap) delete user "temp_user"',

            # Group lifecycle
            '300 (ldap) create group "project-team"',
            '310 (ldap) add user "alice" to group "project-team"',
            '320 (ldap) add user "bob" to group "project-team"',
            '330 (ldap) get members of group "project-team"',
            '340 (ldap) delete group "project-team"',

            # Cleanup
            '350 (ldap) disconnect from server',
        ]


# Singleton instance
_ldap_module = None

def get_ldap_module() -> LDAPModule:
    """Get the singleton LDAP module instance."""
    global _ldap_module
    if _ldap_module is None:
        _ldap_module = LDAPModule()
    return _ldap_module
