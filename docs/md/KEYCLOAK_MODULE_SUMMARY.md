# Keycloak Module - Complete Reference

## Overview

The **Keycloak module** provides comprehensive Identity and Access Management (IAM) capabilities through integration with Keycloak, the open-source identity and access management solution. This module enables complete user lifecycle management, role-based access control (RBAC), Single Sign-On (SSO), and OAuth2/OIDC authentication flows.

**Module Type:** `(keycloak)`
**Primary Use Cases:** Identity management, SSO, OAuth2/OIDC, user authentication, role management, multi-tenant applications

---

## Table of Contents

1. [Features](#features)
2. [Configuration](#configuration)
3. [Basic Operations](#basic-operations)
4. [Advanced Features](#advanced-features)
5. [Common Use Cases](#common-use-cases)
6. [Best Practices](#best-practices)
7. [Security Considerations](#security-considerations)
8. [Troubleshooting](#troubleshooting)

---

## Features

### Core Capabilities

- **Realm Management**: Create, configure, and delete realms for multi-tenant isolation
- **User Management**: Complete user lifecycle (create, update, delete, search, password management)
- **Role Management**: Define and assign roles with hierarchical role composition
- **Group Management**: Organize users in hierarchical groups with inherited permissions
- **Client Management**: Register OAuth2/OIDC clients for applications
- **Authentication**: User login, token generation (access, refresh, ID tokens)
- **Token Operations**: Token validation, refresh, and revocation
- **Multi-Realm Support**: Switch between realms dynamically
- **SSO/Federation**: Single Sign-On and identity federation capabilities

### Supported Operations

| Category | Operations |
|----------|-----------|
| **Realms** | Create, get, delete, switch |
| **Users** | Create, update, delete, search, list, set password |
| **Roles** | Create, get, delete, list, assign to users, remove from users |
| **Groups** | Create, get, delete, add users, remove users, hierarchies |
| **Clients** | Create, get, delete (OAuth2/OIDC) |
| **Authentication** | Login, token refresh, logout |

---

## Configuration

### Basic Configuration (aibasic.conf)

```ini
[keycloak]
SERVER_URL = http://localhost:8080
REALM_NAME = master
ADMIN_USERNAME = admin
ADMIN_PASSWORD = admin
CLIENT_ID = admin-cli
CLIENT_SECRET =
VERIFY_SSL = true
TIMEOUT = 30
POOL_SIZE = 10
MAX_RETRIES = 3
```

### Configuration Parameters

| Parameter | Description | Default | Required |
|-----------|-------------|---------|----------|
| `SERVER_URL` | Keycloak server URL | - | Yes |
| `REALM_NAME` | Default realm name | `master` | Yes |
| `ADMIN_USERNAME` | Admin username | - | Yes |
| `ADMIN_PASSWORD` | Admin password | - | Yes |
| `CLIENT_ID` | Admin client ID | `admin-cli` | No |
| `CLIENT_SECRET` | Client secret (if required) | - | No |
| `VERIFY_SSL` | Verify SSL certificates | `true` | No |
| `TIMEOUT` | Request timeout (seconds) | `30` | No |
| `POOL_SIZE` | Connection pool size | `10` | No |
| `MAX_RETRIES` | Max retry attempts | `3` | No |

### Environment Variables

All configuration parameters can be overridden with environment variables:

```bash
export KEYCLOAK_SERVER_URL=http://localhost:8080
export KEYCLOAK_REALM_NAME=my-realm
export KEYCLOAK_ADMIN_USERNAME=admin
export KEYCLOAK_ADMIN_PASSWORD=secret
```

---

## Basic Operations

### Realm Management

```basic
REM Create a new realm
10 (keycloak) create realm "my-app-realm" with displayName "My Application Realm" and enabled true

REM Switch to a realm
20 (keycloak) switch to realm "my-app-realm"

REM Get realm information
30 (keycloak) get realm "my-app-realm"

REM Delete realm
40 (keycloak) delete realm "my-app-realm"
```

### User Management

```basic
REM Create user
10 (keycloak) create user "john.doe" with email "john.doe@example.com" and firstName "John" and lastName "Doe" and enabled true

REM Set password
20 (keycloak) set password for user "john.doe" to "SecurePass123!" with temporary false

REM Update user
30 (keycloak) update user "john.doe" with email "john@example.com" and enabled true

REM Get user details
40 (keycloak) get user "john.doe"

REM List all users
50 (keycloak) list all users

REM Search users
60 (keycloak) search users with username "john*"

REM Delete user
70 (keycloak) delete user "john.doe"
```

### Role Management

```basic
REM Create role
10 (keycloak) create role "admin" with description "Administrator role with full access"

REM Assign role to user
20 (keycloak) assign role "admin" to user "john.doe"

REM Get user roles
30 (keycloak) get roles for user "john.doe"

REM Remove role from user
40 (keycloak) remove role "admin" from user "john.doe"

REM List all roles
50 (keycloak) list all roles

REM Delete role
60 (keycloak) delete role "admin"
```

### Group Management

```basic
REM Create group
10 (keycloak) create group "Engineering" with attributes {"department": "engineering", "location": "HQ"}

REM Create sub-group
20 (keycloak) create group "Frontend-Team" with parent "Engineering"

REM Add user to group
30 (keycloak) add user "john.doe" to group "Engineering"

REM Remove user from group
40 (keycloak) remove user "john.doe" from group "Engineering"

REM Get group details
50 (keycloak) get group "Engineering"

REM Delete group
60 (keycloak) delete group "Engineering"
```

### Client Management

```basic
REM Create OAuth2/OIDC client
10 (keycloak) create client "web-app" with clientId "web-app-client" and publicClient true and redirectUris ["http://localhost:3000/*"]

REM Create confidential client
20 (keycloak) create client "api-service" with clientId "api-service-client" and publicClient false and serviceAccountsEnabled true

REM Get client details
30 (keycloak) get client "web-app"

REM Delete client
40 (keycloak) delete client "web-app"
```

### Authentication

```basic
REM Authenticate user
10 (keycloak) authenticate user "john.doe" with password "SecurePass123!" in realm "my-app-realm"

REM Tokens (access, refresh, ID) are automatically managed
```

---

## Advanced Features

### Multi-Realm Management

```basic
REM Create separate realms for different environments
10 (keycloak) switch to realm "master"
20 (keycloak) create realm "dev-realm" with displayName "Development" and enabled true
30 (keycloak) create realm "prod-realm" with displayName "Production" and enabled true

REM Configure dev realm
40 (keycloak) switch to realm "dev-realm"
50 (keycloak) create user "dev-admin" with email "admin@dev.com" and enabled true
```

### User Onboarding Workflow

```basic
REM Complete user onboarding
10 (keycloak) create user "alice.johnson" with email "alice@example.com" and firstName "Alice" and lastName "Johnson" and enabled true
20 (keycloak) set password for user "alice.johnson" to "Welcome123!" with temporary true
30 (keycloak) assign role "developer" to user "alice.johnson"
40 (keycloak) add user "alice.johnson" to group "Engineering"
```

### Hierarchical Groups

```basic
REM Create department structure
10 (keycloak) create group "IT-Department"
20 (keycloak) create group "Infrastructure" with parent "IT-Department"
30 (keycloak) create group "Development" with parent "IT-Department"
40 (keycloak) create group "Security" with parent "IT-Department"
```

---

## Common Use Cases

### 1. E-commerce Platform

```basic
REM Setup e-commerce IAM
10 (keycloak) create realm "ecommerce" with displayName "E-Commerce Platform" and enabled true
20 (keycloak) switch to realm "ecommerce"

REM Create roles
30 (keycloak) create role "customer" with description "Regular customer"
40 (keycloak) create role "vendor" with description "Product vendor"
50 (keycloak) create role "admin" with description "Platform admin"

REM Create customer
60 (keycloak) create user "customer1" with email "customer@email.com" and enabled true
70 (keycloak) assign role "customer" to user "customer1"
```

### 2. Multi-Tenant SaaS Application

```basic
REM Create SaaS platform realm
10 (keycloak) create realm "saas-platform" with displayName "SaaS Platform" and enabled true
20 (keycloak) switch to realm "saas-platform"

REM Create tenant groups (isolation per tenant)
30 (keycloak) create group "Tenant-Acme" with attributes {"tenantId": "acme-001", "plan": "enterprise"}
40 (keycloak) create group "Admins" with parent "Tenant-Acme"
50 (keycloak) create group "Users" with parent "Tenant-Acme"

REM Create tenant admin
60 (keycloak) create user "admin@acme.com" with email "admin@acme.com" and enabled true
70 (keycloak) assign role "tenant-admin" to user "admin@acme.com"
80 (keycloak) add user "admin@acme.com" to group "Admins"
```

### 3. Enterprise SSO

```basic
REM Setup enterprise SSO
10 (keycloak) create realm "enterprise" with displayName "Enterprise Corp" and enabled true
20 (keycloak) switch to realm "enterprise"

REM Create department groups
30 (keycloak) create group "HR-Department"
40 (keycloak) create group "IT-Department"
50 (keycloak) create group "Finance-Department"

REM Create enterprise roles
60 (keycloak) create role "employee" with description "Base employee role"
70 (keycloak) create role "manager" with description "Department manager"
```

### 4. Healthcare System (HIPAA-Compliant)

```basic
REM Setup healthcare realm
10 (keycloak) create realm "healthcare" with displayName "Healthcare System" and enabled true
20 (keycloak) switch to realm "healthcare"

REM Create healthcare roles
30 (keycloak) create role "physician" with description "Licensed physician"
40 (keycloak) create role "nurse" with description "Registered nurse"
50 (keycloak) create role "patient" with description "Patient access"

REM Create physician account
60 (keycloak) create user "dr.smith" with email "dr.smith@hospital.com" and enabled true
70 (keycloak) assign role "physician" to user "dr.smith"
```

---

## Best Practices

### Security

1. **Use HTTPS**: Always use TLS/SSL in production
2. **Strong Passwords**: Implement password policies (complexity, expiration)
3. **MFA**: Enable Multi-Factor Authentication for sensitive accounts
4. **Service Accounts**: Use dedicated service accounts with minimal permissions
5. **Realm-Specific Admins**: Avoid using master realm admin in production
6. **Rate Limiting**: Implement brute force detection and rate limiting
7. **Audit Logging**: Enable comprehensive audit logs and event listeners

### Architecture

1. **Realm Isolation**: Use separate realms for different environments (dev, staging, prod)
2. **Group Hierarchies**: Organize users with hierarchical groups
3. **Role Composition**: Use composite roles for complex permission sets
4. **Client Secrets**: Rotate client secrets regularly
5. **Token Lifetimes**: Set appropriate token expiration times

### Performance

1. **Connection Pooling**: Configure appropriate pool sizes
2. **Caching**: Enable caching for frequently accessed data
3. **Database Tuning**: Optimize Keycloak database for production load
4. **Load Balancing**: Use load balancers for high availability

### Operational

1. **Regular Backups**: Backup Keycloak database and configuration
2. **Monitoring**: Monitor authentication rates, failures, and performance
3. **Updates**: Keep Keycloak up-to-date with security patches
4. **Disaster Recovery**: Have a disaster recovery plan

---

## Security Considerations

### Authentication Security

- Use strong password policies (minimum length, complexity, history)
- Enable account lockout after failed login attempts
- Implement CAPTCHA for login pages
- Use MFA (TOTP, WebAuthn, SMS) for sensitive accounts
- Set appropriate session timeouts

### Token Security

- Use short-lived access tokens (5-15 minutes)
- Use refresh tokens for extended sessions
- Implement token revocation
- Validate all token claims on every request
- Use HTTPS for all token transmission

### Authorization Security

- Follow principle of least privilege
- Use groups and roles for access control
- Regularly audit user permissions
- Implement attribute-based access control (ABAC) where needed
- Review and remove inactive accounts

### Network Security

- Use TLS/SSL for all connections
- Implement network segmentation
- Use firewalls to restrict access
- Enable DDoS protection
- Monitor for suspicious activity

---

## Troubleshooting

### Common Issues

**Connection Errors**

```
Issue: "Failed to connect to Keycloak"
Solution:
- Verify SERVER_URL is correct
- Check network connectivity
- Verify Keycloak is running
- Check firewall rules
```

**Authentication Failures**

```
Issue: "Authentication failed"
Solution:
- Verify admin credentials
- Check realm name is correct
- Verify user exists in correct realm
- Check account is not locked
```

**Permission Errors**

```
Issue: "Insufficient permissions"
Solution:
- Verify admin user has required roles
- Check realm-specific permissions
- Verify client has correct scopes
```

**SSL/TLS Errors**

```
Issue: "SSL certificate verification failed"
Solution:
- Set VERIFY_SSL = false for development
- Install proper CA certificates for production
- Use valid SSL certificates
```

### Debug Mode

Enable debug logging in your application to troubleshoot issues:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Performance Issues

```
Issue: Slow response times
Solution:
- Increase connection pool size
- Check Keycloak database performance
- Review network latency
- Enable caching
- Check server resources (CPU, memory)
```

---

## Integration Examples

### With LDAP/Active Directory

```basic
REM Users can be federated from LDAP/AD
REM Configure user federation in Keycloak admin console
REM Then authenticate against federated users
10 (keycloak) authenticate user "ldap.user" with password "password" in realm "enterprise"
```

### With OAuth2 Applications

```basic
REM Register OAuth2 client
10 (keycloak) create client "my-oauth-app" with clientId "oauth-client" and publicClient true and redirectUris ["https://app.example.com/callback"]

REM Users authenticate via OAuth2 flow
```

### With Microservices

```basic
REM Create service account client
10 (keycloak) create client "microservice-a" with clientId "service-a" and publicClient false and serviceAccountsEnabled true

REM Service uses client credentials flow
```

---

## API Reference

### Realm Methods

- `realm_create(name, display_name, enabled)` - Create realm
- `realm_get(name)` - Get realm details
- `realm_delete(name)` - Delete realm
- `set_realm(name)` - Switch active realm

### User Methods

- `user_create(username, email, first_name, last_name, enabled)` - Create user
- `user_get(username)` - Get user details
- `user_update(username, **attributes)` - Update user
- `user_delete(username)` - Delete user
- `user_set_password(username, password, temporary)` - Set password
- `user_list()` - List all users

### Role Methods

- `role_create(name, description)` - Create role
- `role_get(name)` - Get role details
- `role_delete(name)` - Delete role
- `role_list()` - List all roles
- `user_assign_role(username, role_name)` - Assign role
- `user_remove_role(username, role_name)` - Remove role
- `user_get_roles(username)` - Get user roles

### Group Methods

- `group_create(name, attributes, parent)` - Create group
- `group_get(name)` - Get group details
- `group_delete(name)` - Delete group
- `group_add_user(group_name, username)` - Add user to group
- `group_remove_user(group_name, username)` - Remove user from group

### Client Methods

- `client_create(name, client_id, **config)` - Create client
- `client_get(name)` - Get client details
- `client_delete(name)` - Delete client

### Authentication Methods

- `authenticate(username, password, realm)` - Authenticate user
- `token_refresh(refresh_token)` - Refresh access token
- `logout(refresh_token)` - Logout user

---

## Additional Resources

- **Keycloak Documentation**: https://www.keycloak.org/documentation
- **OAuth2 Specification**: https://oauth.net/2/
- **OpenID Connect**: https://openid.net/connect/
- **Best Practices**: https://www.keycloak.org/docs/latest/server_admin/#_best_practices

---

## Module Information

- **Module Name**: KeycloakModule
- **Task Type**: `(keycloak)`
- **Dependencies**: `python-keycloak>=3.0.0`
- **Python Version**: 3.7+
- **AIbasic Version**: 1.0+

---

*For more examples, see [example_keycloak.aib](../../examples/example_keycloak.aib)*
