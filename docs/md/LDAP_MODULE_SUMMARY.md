# LDAP Module - Complete Reference

## Overview

The **LDAP module** provides comprehensive LDAP (Lightweight Directory Access Protocol) and Active Directory integration for user management, authentication, and directory services operations.

**Module Type:** `(ldap)`
**Primary Use Cases:** User/group management, authentication, Active Directory integration, organizational structure, SSO

---

## Key Features

- User Management (create, modify, delete, search)
- Group Management (create, modify, members)
- Authentication (bind, verify credentials)
- Organizational Units (OU) management
- Active Directory compatibility
- LDAP search with filters
- TLS/SSL support
- Connection pooling

---

## Configuration

```ini
[ldap]
SERVER = ldap.example.com
PORT = 389
BASE_DN = dc=example,dc=com
BIND_DN = cn=admin,dc=example,dc=com
BIND_PASSWORD = admin_password
USE_SSL = false
USE_TLS = true
USER_OU = ou=users
GROUP_OU = ou=groups
IS_AD = false
```

---

## Basic Operations

### User Management

```basic
REM Create user
10 (ldap) create user "jdoe" with attributes {"cn": "John Doe", "mail": "john@example.com", "userPassword": "secret"}

REM Modify user
20 (ldap) modify user "jdoe" set {"mail": "john.doe@example.com", "telephoneNumber": "+1234567890"}

REM Delete user
30 (ldap) delete user "jdoe"

REM Search users
40 (ldap) search users with filter "(mail=*@example.com)"
```

### Authentication

```basic
REM Authenticate user
10 (ldap) authenticate user "jdoe" with password "secret"
20 IF RESULT THEN
30   PRINT "Login successful"
40 ELSE
50   PRINT "Login failed"
60 END IF
```

### Group Management

```basic
REM Create group
10 (ldap) create group "developers" with attributes {"description": "Development team"}

REM Add user to group
20 (ldap) add user "jdoe" to group "developers"

REM Remove user from group
30 (ldap) remove user "jdoe" from group "developers"
```

---

## Module Information

- **Module Name**: LDAPModule
- **Task Type**: `(ldap)`
- **Dependencies**: `ldap3>=2.9.1`

---

*For more examples, see [example_ldap.aib](../../examples/example_ldap.aib)*
