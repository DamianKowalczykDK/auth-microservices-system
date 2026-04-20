# 🚀 API Gateway (Microservice)

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Production%20Ready-009688.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![HTTPX](https://img.shields.io/badge/HTTPX-Async%20Client-orange.svg)](https://www.python-httpx.org/)
[![Test Coverage](https://img.shields.io/badge/Coverage-100%25-brightgreen.svg)](https://damiankowalczykdk.github.io/auth-microservices-system/apigateway/index.html)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📖 Overview

API Gateway is the **entry point** to the system and the only service exposed to external clients.

It is responsible for:
- authentication and authorization
- JWT token issuing and validation
- request routing to internal services
- enforcing access control (RBAC)
- session lifecycle management

The gateway communicates with internal services (e.g. Users Service) via **HTTPX async client**.

---

## 🏗️ Architecture Overview

The system follows API Gateway pattern:

**Client → API Gateway → Internal Services**

Responsibilities:
- validates incoming requests
- authenticates users
- generates JWT tokens
- forwards requests to Users Service
- enforces roles and permissions

The gateway **does NOT access database directly**.

---

## 🔐 Core Features

### 🔑 Authentication
- Login (username/email + password)
- JWT Access Token
- Refresh Token (HTTP-only cookies)
- Token validation middleware

### 🛡️ Authorization
- Role-Based Access Control (RBAC)
- Protected routes
- Dependency-based authorization (FastAPI Depends)

### 🔐 MFA Support
- MFA challenge handling
- MFA verification flow
- Delegation to Users Service

### 🔄 Session Management
- Refresh token rotation
- Logout (token invalidation)
- Stateless access token validation

---

## ⚡ Performance & Design

- Fully **async FastAPI architecture**
- HTTPX async client for service communication
- Non-blocking I/O
- Centralized error handling
- Clean separation of concerns

---

## 🧱 Clean Architecture

Structure:

- **API layer** → FastAPI routes
- **Service layer** → authentication & business logic
- **Client layer** → communication with Users Service
- **Core layer** → security, config, exceptions

---

### Infrastructure
- Docker
- Docker Compose

---

## 🚀 Getting Started

### 1. Environment setup
* **Copy .env.example to .env and adjust values:** 

```bash
cp .env.example .env
```

### Poetry
* **Install dependencies and activate virtual environment:**

```Bash
poetry install
poetry shell
```
---

## 🔌 API Endpoints (Public – exposed to client)

---

## 🔑 Authentication
> ⚠️ Login and MFA use **application/x-www-form-urlencoded (form-data)**
---
## 🔒 Authorization
> 🔐 All protected endpoints require:
>    Authorization: Bearer <access_token>

| Method | Endpoint          | Query Params | Body      | Description                |
|--------|-------------------|--------------|-----------|----------------------------|
| POST   | /api/auth         | -            | UserLogin | Login user (form-data)     |
| POST   | /api/auth/mfa     | -            | MfaVerify | Verify MFA code (form-data)|
| POST   | /api/auth/refresh | -            | -         | Refresh access token       |
| POST   | /api/auth/logout  | -            | -         | Logout user                |

---

## 👤 Account (Registration & Recovery)

| Method | Endpoint                      | Query Params | Body              | Description               |
|--------|-------------------------------|--------------|-------------------|---------------------------|
| POST   | /api/accounts                 | -            | UserCreate        | Register user             |
| PATCH  | /api/accounts/activation      | code         | -                 | Activate account          |
| POST   | /api/accounts/activation/code | identifier   | -                 | Resend activation code    |
| POST   | /api/accounts/password/forgot | identifier   | -                 | Forgot password           |
| POST   | /api/accounts/password/reset  | -            | UserResetPassword | Reset password            |

---
## 👤 User

| Method | Endpoint               | Query Params | Role  | Description                   |
|--------|------------------------|--------------|-------|-------------------------------|
| GET    | /api/user              | -            | user  | Get current user profile      |
| PATCH  | /api/users/mfa/enable  | -            | user  | Enable MFA (current user)     |
| PATCH  | /api/users/mfa/disable | -            | user  | Disable MFA (current user)    |

---
## 👤 Admin

| Method | Endpoint               | Query Params | Role  | Description                   |
|--------|------------------------|--------------|-------|-------------------------------|
| DELETE | /api/admin/users       | identifier   | admin | Delete user (by identifier)   |

---

## 🧾 Notes

- Authentication is handled via JWT tokens  
- Refresh token is stored in **HTTP-only cookie**  
- API Gateway is the only public entry point  
- Internal services are NOT exposed externally  

---

## 📂 Project Structure

```text
tests/
apigateway/
├── api/
│   ├── routes/
│   │   ├── account.py
│   │   ├── admin.py
│   │   ├── auth.py
│   │   └── user.py
│   └── dependencies.py
│
├── core/
│   ├── config.py
│   ├── http_client.py
│   └── security.py
│
├── clients/
│   └── users_client.py
│
├── services/
│   ├── account_service.py
│   ├── admin_service.py
│   ├── auth_service.py
│   └── user_service.py
│
├── domain/
│   ├── types.py
│   └── schemas.py
│
└── main.py
```
---
## 🔗 Relation to Users Service

API Gateway communicates with Users Service for:

- user authentication (credentials verification)  
- MFA verification  
- user management operations  

---

### Gateway responsibilities:

- JWT issuing & validation  
- access control  
- request routing  

---

### Users Service responsibilities:

- user data  
- business logic  
- persistence (MongoDB)  