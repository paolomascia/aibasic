# JWT Module - Complete Reference

## Overview

The **JWT module** provides comprehensive JSON Web Token (JWT) capabilities for modern token-based authentication and authorization. This module enables secure stateless authentication, session management, and claims-based authorization using industry-standard JWT tokens with support for multiple signing algorithms.

**Module Type:** `(jwt)`
**Primary Use Cases:** API authentication, stateless sessions, microservices auth, mobile app authentication, SSO, OAuth2 integration, token-based authorization

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

- **Token Creation**: Generate JWT tokens with custom claims and expiration
- **Token Verification**: Validate tokens with signature and claim verification
- **Multiple Algorithms**: Support for HMAC (HS256/384/512) and RSA/ECDSA (RS256/384/512, ES256/384/512)
- **Access Tokens**: Short-lived tokens for API access
- **Refresh Tokens**: Long-lived tokens for obtaining new access tokens
- **Custom Claims**: Add arbitrary claims to tokens
- **Token Expiration**: Automatic expiration handling
- **Token Pair Generation**: Create access/refresh token pairs
- **Audience/Issuer Validation**: Verify token audience and issuer
- **Token Decoding**: Decode tokens without verification for inspection

### Supported Operations

| Category | Operations |
|----------|-----------|
| **Token Creation** | Create token, access token, refresh token, token pairs |
| **Token Verification** | Verify signature, validate claims, check expiration |
| **Token Management** | Refresh tokens, decode tokens, check expiration |
| **Claims** | Standard claims (sub, exp, iat, iss, aud), custom claims |
| **Algorithms** | HS256/384/512, RS256/384/512, ES256/384/512 |

---

## Configuration

### Basic Configuration (aibasic.conf)

```ini
[jwt]
SECRET_KEY = your-secret-key-here-change-in-production
ALGORITHM = HS256
ISSUER = aibasic-app
AUDIENCE = aibasic-users
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7
PRIVATE_KEY_PATH =
PUBLIC_KEY_PATH =
```

### Configuration Parameters

| Parameter | Description | Default | Required |
|-----------|-------------|---------|----------|
| `SECRET_KEY` | Secret key for HMAC algorithms | - | Yes (for HS*) |
| `ALGORITHM` | Signing algorithm | `HS256` | No |
| `ISSUER` | Token issuer identifier | `aibasic-app` | No |
| `AUDIENCE` | Token audience identifier | `aibasic-users` | No |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime (minutes) | `15` | No |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifetime (days) | `7` | No |
| `PRIVATE_KEY_PATH` | Path to RSA/ECDSA private key | - | Yes (for RS*/ES*) |
| `PUBLIC_KEY_PATH` | Path to RSA/ECDSA public key | - | Yes (for RS*/ES*) |

### Environment Variables

All configuration parameters can be overridden with environment variables:

```bash
export JWT_SECRET_KEY=your-secret-key
export JWT_ALGORITHM=RS256
export JWT_ISSUER=my-app
export JWT_AUDIENCE=my-users
export JWT_PRIVATE_KEY_PATH=/path/to/private.pem
export JWT_PUBLIC_KEY_PATH=/path/to/public.pem
```

### Supported Algorithms

**HMAC (Symmetric)**
- `HS256` - HMAC with SHA-256 (default)
- `HS384` - HMAC with SHA-384
- `HS512` - HMAC with SHA-512

**RSA (Asymmetric)**
- `RS256` - RSA with SHA-256
- `RS384` - RSA with SHA-384
- `RS512` - RSA with SHA-512

**ECDSA (Asymmetric)**
- `ES256` - ECDSA with SHA-256
- `ES384` - ECDSA with SHA-384
- `ES512` - ECDSA with SHA-512

---

## Basic Operations

### Token Creation

```basic
REM Create basic token
10 (jwt) create token with subject "user123" and expires_in 3600

REM Create access token (15 min default)
20 (jwt) create access token for user "john.doe"

REM Create refresh token (7 days default)
30 (jwt) create refresh token for user "john.doe"

REM Create token with custom claims
40 (jwt) create token with subject "user123" and claims {"role": "admin", "email": "admin@example.com"}
```

### Token Verification

```basic
REM Verify token
10 (jwt) verify token "eyJhbGc..."

REM Verify token with specific audience
20 (jwt) verify token "eyJhbGc..." with audience "api-users"

REM Verify token without expiration check
30 (jwt) verify token "eyJhbGc..." with verify_exp false
```

### Token Decoding

```basic
REM Decode token without verification (for inspection)
10 (jwt) decode token "eyJhbGc..." without verification

REM Get token expiration
20 (jwt) get expiration from token "eyJhbGc..."

REM Check if token is expired
30 (jwt) check if token "eyJhbGc..." is expired
```

### Token Refresh

```basic
REM Refresh access token using refresh token
10 (jwt) refresh access token using refresh_token "eyJhbGc..."
```

### Token Pairs

```basic
REM Create access + refresh token pair
10 (jwt) create token pair for user "john.doe"

REM Returns both access_token and refresh_token
```

---

## Advanced Features

### Custom Claims and RBAC

```basic
REM Create token with role-based claims
10 (jwt) create access token for user "admin@example.com" with claims {"role": "admin", "permissions": ["read", "write", "delete"], "department": "IT"}

REM Verify and extract claims
20 (jwt) verify token "eyJhbGc..." and extract claims
```

### Multi-Tenant Applications

```basic
REM Create tenant-specific tokens
10 (jwt) create access token for user "user@tenant1.com" with claims {"tenant_id": "tenant-001", "plan": "enterprise"}

REM Verify tenant from token
20 (jwt) verify token "eyJhbGc..." and check tenant_id claim
```

### Session Management

```basic
REM Complete login flow
10 (jwt) create token pair for user "john.doe" with claims {"session_id": "sess-12345", "ip": "192.168.1.1"}

REM Token refresh flow
20 (jwt) verify refresh token "eyJhbGc..."
30 (jwt) refresh access token using refresh_token "eyJhbGc..."
```

### RSA Key-Based Signing

```basic
REM Generate RSA keys (using openssl):
REM openssl genrsa -out private.pem 2048
REM openssl rsa -in private.pem -pubout -out public.pem

REM Configure JWT module for RSA
10 SET JWT_ALGORITHM="RS256"
20 SET JWT_PRIVATE_KEY_PATH="/path/to/private.pem"
30 SET JWT_PUBLIC_KEY_PATH="/path/to/public.pem"

REM Create token with RSA signature
40 (jwt) create access token for user "john.doe"
```

---

## Common Use Cases

### 1. REST API Authentication

```basic
REM API authentication flow
10 REM User login endpoint
20 (jwt) create token pair for user "api.user@example.com" with claims {"role": "api_client", "scope": "read write"}

30 REM Store tokens
40 LET access_token = RESULT["access_token"]
50 LET refresh_token = RESULT["refresh_token"]

60 REM API request with access token
70 (restapi) GET "https://api.example.com/users" with headers {"Authorization": "Bearer " + access_token}

80 REM Refresh flow when access token expires
90 (jwt) refresh access token using refresh_token
```

### 2. Microservices Authentication

```basic
REM Service-to-service authentication
10 REM Auth service creates token
20 (jwt) create access token for service "payment-service" with claims {"service": "payment", "environment": "production", "permissions": ["process_payments", "refunds"]}

30 REM Payment service verifies incoming request
40 (jwt) verify token from request header
50 IF RESULT["service"] = "payment" THEN
60   REM Process request
70 ELSE
80   REM Reject unauthorized request
90 END IF
```

### 3. Mobile App Authentication

```basic
REM Mobile app login flow
10 REM User authenticates with username/password
20 (jwt) create token pair for user "mobile.user@example.com" with claims {"device_id": "device-12345", "platform": "ios", "app_version": "2.1.0"}

30 LET access_token = RESULT["access_token"]
40 LET refresh_token = RESULT["refresh_token"]

50 REM Store refresh token securely (keychain/keystore)
60 REM Use access token for API calls
70 (restapi) GET "https://api.example.com/profile" with headers {"Authorization": "Bearer " + access_token}

80 REM Background token refresh
90 (jwt) refresh access token using refresh_token
```

### 4. SSO (Single Sign-On)

```basic
REM SSO across multiple applications
10 REM Central auth server creates SSO token
20 (jwt) create access token for user "sso.user@corp.com" with claims {"sso_session": "sso-98765", "applications": ["app1", "app2", "app3"], "role": "employee"}

30 REM App1 validates SSO token
40 (jwt) verify token with audience "app1"

50 REM App2 validates same SSO token
60 (jwt) verify token with audience "app2"
```

### 5. E-commerce Platform

```basic
REM E-commerce customer authentication
10 (jwt) create token pair for user "customer@shop.com" with claims {"customer_id": "cust-12345", "cart_id": "cart-67890", "membership": "gold", "discount_tier": "10"}

20 LET access_token = RESULT["access_token"]

30 REM Shopping cart operations
40 (restapi) POST "https://api.shop.com/cart/add" with headers {"Authorization": "Bearer " + access_token} and data {"product_id": "prod-123", "quantity": 2}

50 REM Checkout with customer claims
60 (jwt) verify token and apply membership discount from claims
```

### 6. Healthcare Platform (HIPAA)

```basic
REM Healthcare provider authentication
10 (jwt) create access token for user "dr.smith@hospital.com" with claims {"provider_id": "prov-456", "department": "cardiology", "access_level": "physician", "license": "MD-123456"}

20 REM Verify provider access to patient records
30 (jwt) verify token
40 IF RESULT["access_level"] = "physician" THEN
50   REM Grant access to medical records
60 ELSE
70   REM Deny access
80 END IF
```

### 7. Financial Services Platform

```basic
REM Financial advisor authentication
10 (jwt) create access token for user "advisor@bank.com" with claims {"advisor_id": "adv-789", "branch": "NY-001", "certifications": ["CFP", "CFA"], "access": ["accounts", "transactions", "reports"]}

20 REM Verify token for sensitive operations
30 (jwt) verify token
40 IF "CFA" IN RESULT["certifications"] THEN
50   REM Allow investment advice
60 END IF
```

### 8. IoT Device Authentication

```basic
REM IoT device registration
10 (jwt) create access token for device "sensor-001" with claims {"device_id": "sensor-001", "type": "temperature", "location": "warehouse-A", "expires_in": 86400}

20 LET device_token = RESULT

30 REM Device sends telemetry
40 (mqtt) publish to "sensors/temperature" with payload {"temp": 22.5, "token": device_token}

50 REM Server verifies device token
60 (jwt) verify token from message
```

### 9. Educational Platform

```basic
REM Student authentication
10 (jwt) create access token for user "student@university.edu" with claims {"student_id": "stu-12345", "courses": ["CS101", "MATH202"], "year": 2, "enrollment_status": "active"}

20 REM Verify access to course materials
30 (jwt) verify token
40 IF "CS101" IN RESULT["courses"] THEN
50   REM Grant access to CS101 materials
60 END IF
```

### 10. Multi-Tenant SaaS Platform

```basic
REM Tenant admin authentication
10 (jwt) create access token for user "admin@tenant1.com" with claims {"tenant_id": "tenant-001", "role": "admin", "plan": "enterprise", "features": ["advanced_analytics", "api_access", "sso"]}

20 REM Verify tenant isolation
30 (jwt) verify token
40 LET tenant_id = RESULT["tenant_id"]
50 REM Query only this tenant's data
60 (postgres) SELECT * FROM users WHERE tenant_id = tenant_id
```

---

## Best Practices

### Security

1. **Use Strong Secret Keys**: Generate cryptographically secure random keys (32+ bytes)
2. **Use Asymmetric Algorithms for Production**: Prefer RS256/ES256 over HS256 for better security
3. **Short Access Token Lifetime**: Keep access tokens short-lived (5-15 minutes)
4. **Secure Refresh Tokens**: Store refresh tokens securely, rotate regularly
5. **Validate All Claims**: Always verify issuer, audience, and expiration
6. **HTTPS Only**: Transmit tokens only over HTTPS
7. **Avoid Sensitive Data**: Don't store passwords or sensitive data in tokens
8. **Token Revocation**: Implement token blacklisting for compromised tokens

### Token Management

1. **Token Expiration**: Set appropriate expiration times
   - Access tokens: 5-15 minutes
   - Refresh tokens: 7-30 days
2. **Token Refresh Strategy**: Implement automatic refresh before expiration
3. **Token Storage**:
   - Frontend: Memory or sessionStorage (never localStorage for refresh tokens)
   - Mobile: Secure keychain/keystore
   - Backend: Encrypted database or secure key-value store
4. **Token Rotation**: Rotate refresh tokens on each use

### Algorithm Selection

1. **Development**: HS256 (simple, symmetric)
2. **Production**: RS256 or ES256 (asymmetric, better security)
3. **Microservices**: RS256 (public key can be shared safely)
4. **High Security**: ES256 (smaller keys, faster verification)

### Claims Design

1. **Minimal Claims**: Include only necessary claims
2. **Standard Claims**: Use standard claims (sub, iss, aud, exp, iat)
3. **Custom Claims**: Namespace custom claims to avoid conflicts
4. **No PII**: Avoid personally identifiable information
5. **Versioning**: Include token version for format changes

### Key Management

1. **Key Rotation**: Rotate keys periodically (every 90 days)
2. **Key Storage**: Store private keys securely (environment variables, vault)
3. **Key Backup**: Maintain secure backups of keys
4. **Key Length**: Use adequate key lengths (RSA 2048+, ECDSA 256+)

---

## Security Considerations

### Token Security

- **Never expose secret keys**: Keep SECRET_KEY and private keys confidential
- **Validate signatures**: Always verify token signatures
- **Check expiration**: Validate exp claim on every request
- **Verify issuer/audience**: Prevent token misuse across services
- **Use secure transmission**: HTTPS only, never in URLs
- **Implement token revocation**: Blacklist compromised tokens

### Attack Prevention

**JWT Forgery**
- Use strong signing algorithms (RS256/ES256)
- Validate signature on every request
- Keep private keys secure

**Token Theft**
- Use HTTPS for transmission
- Implement token expiration
- Rotate refresh tokens
- Monitor for unusual token usage

**Replay Attacks**
- Include jti (JWT ID) claim for one-time use tokens
- Track used tokens in cache
- Use short expiration times

**Algorithm Confusion**
- Explicitly specify algorithm in verification
- Disable algorithm "none"
- Validate algorithm matches expected

### Compliance

**GDPR**
- Minimize PII in tokens
- Implement right to erasure (revoke tokens)
- Log token access for audit trails

**HIPAA (Healthcare)**
- Encrypt tokens at rest
- Audit all token access
- Implement strict expiration
- Use asymmetric algorithms

**PCI DSS (Financial)**
- Never store payment data in tokens
- Use strong encryption
- Implement token monitoring
- Regular security audits

---

## Troubleshooting

### Common Issues

**Invalid Signature**

```
Issue: "Signature verification failed"
Solution:
- Verify SECRET_KEY matches between creation and verification
- For RS*/ES*, ensure public/private key pair is correct
- Check algorithm configuration matches
- Verify token hasn't been tampered with
```

**Token Expired**

```
Issue: "Token has expired"
Solution:
- Check token expiration time
- Implement token refresh flow
- Verify server time is synchronized (NTP)
- Adjust ACCESS_TOKEN_EXPIRE_MINUTES if too short
```

**Invalid Algorithm**

```
Issue: "Algorithm not allowed"
Solution:
- Verify ALGORITHM setting matches token
- For RS*/ES*, ensure PRIVATE_KEY_PATH and PUBLIC_KEY_PATH are set
- Check private/public key format (PEM)
```

**Invalid Issuer/Audience**

```
Issue: "Invalid issuer" or "Invalid audience"
Solution:
- Verify ISSUER matches between creation and verification
- Check AUDIENCE setting
- Ensure tokens are used for correct service
```

**Key File Not Found**

```
Issue: "Private key file not found"
Solution:
- Verify PRIVATE_KEY_PATH and PUBLIC_KEY_PATH are correct
- Check file permissions (readable)
- Use absolute paths
- Verify key format is PEM
```

### Debug Mode

Enable debug logging to troubleshoot issues:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Token Inspection

Decode token without verification to inspect claims:

```basic
10 (jwt) decode token "eyJhbGc..." without verification
20 PRINT RESULT
```

Or use online tool: https://jwt.io (never paste production tokens!)

---

## API Reference

### Token Creation Methods

- `create_token(subject, claims, expires_delta)` - Create token with custom claims
- `create_access_token(subject, additional_claims)` - Create access token
- `create_refresh_token(subject, additional_claims)` - Create refresh token
- `create_token_pair(subject, additional_claims)` - Create access + refresh tokens

### Token Verification Methods

- `verify_token(token, verify_exp, audience)` - Verify and decode token
- `decode_token(token, verify)` - Decode token (optionally without verification)
- `is_token_expired(token)` - Check if token is expired
- `get_token_expiration(token)` - Get token expiration timestamp

### Token Management Methods

- `refresh_access_token(refresh_token)` - Create new access token from refresh token
- `get_token_claims(token)` - Extract claims from token

---

## Integration Examples

### With REST API Module

```basic
REM Protected API endpoint
10 (jwt) verify token from request header "Authorization"
20 IF RESULT THEN
30   (restapi) GET "https://api.example.com/data" with headers {"Authorization": "Bearer " + token}
40 END IF
```

### With Keycloak Module

```basic
REM Keycloak authentication with JWT
10 (keycloak) authenticate user "john.doe" with password "pass"
20 LET keycloak_token = RESULT["access_token"]
30 REM Verify Keycloak token
40 (jwt) verify token keycloak_token
```

### With PostgreSQL Module

```basic
REM Database operations with JWT claims
10 (jwt) verify token from request
20 LET user_id = RESULT["sub"]
30 (postgres) SELECT * FROM users WHERE id = user_id
```

### With Redis Module

```basic
REM Token blacklisting with Redis
10 (jwt) verify token
20 LET token_id = RESULT["jti"]
30 (redis) GET "blacklist:" + token_id
40 IF RESULT THEN
50   REM Token is blacklisted
60 END IF
```

---

## Additional Resources

- **JWT Specification**: https://datatracker.ietf.org/doc/html/rfc7519
- **JWT.io**: https://jwt.io (token debugger)
- **PyJWT Documentation**: https://pyjwt.readthedocs.io
- **OWASP JWT Security**: https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html

---

## Module Information

- **Module Name**: JWTModule
- **Task Type**: `(jwt)`
- **Dependencies**: `PyJWT[crypto]>=2.8.0`, `cryptography>=41.0.0`
- **Python Version**: 3.7+
- **AIbasic Version**: 1.0+

---

*For more examples, see [example_jwt.aib](../../examples/example_jwt.aib)*
