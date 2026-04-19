# 🚀 Users Service (Microservice)

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Production%20Ready-009688.svg)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Beanie%20ODM-green.svg)](https://www.mongodb.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![HTTPX](https://img.shields.io/badge/HTTPX-Async%20Client-orange.svg)](https://www.python-httpx.org/)
[![Test Coverage](https://img.shields.io/badge/Coverage-100%25-brightgreen.svg)](https://damiankowalczykdk.github.io/auth-microservices-system/users/index.html)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📖 Overview

Users Service is a **FastAPI-based microservice** responsible for user management in a distributed system with an **API Gateway architecture**.

It handles:
- user registration
- account activation
- authentication is fully handled by API Gateway
- MFA (TOTP)
- password reset flow
- user profile management

The service is fully isolated and communicates with API Gateway via **HTTPX client layer**.

---

## 🏗️ Architecture Overview

This service is NOT directly exposed to the client.

It is accessed only through API Gateway:
* **Client → API Gateway → Users Service**


Responsibilities:
- Owns user domain data
- Handles all user-related business logic
- Exposes internal HTTP endpoints for API Gateway
- Uses MongoDB as dedicated database

---

## 🔐 Core Features

### 👤 User Management
- Create user
- Activate account
- Get user by ID
- Delete user (admin only via gateway)

### 🔑 Authentication Flow (via Gateway)
- login (credentials verification)
- MFA verification (if enabled)
- JWT token issuance handled by API Gateway

### 🔐 Security
- Password hashing (Argon2)
- MFA (TOTP)
- Activation codes
- Secure user state handling

---

## ⚡ Performance & Design

- Fully **async FastAPI architecture**
- HTTPX-based service-to-service communication
- Stateless design
- Independent MongoDB database
- Clean separation of concerns

---

## 🧱 Clean Architecture

Structure:

- **API layer** → FastAPI routes
- **Service layer** → business logic
- **Infrastructure layer** → database, external integrations
- **Domain layer** → Pydantic schemas

---

## 💻 Tech Stack

### Backend
- Python 3.13
- FastAPI
- Beanie ODM (MongoDB)
- Pydantic v2
- HTTPX
- PyOTP (MFA)
- Passlib (Argon2 hashing)

### Database
- MongoDB

### Infrastructure
- Docker
- Docker Compose

---

## 🚀 Getting Started

### 1. Environment setup
* **Copy .env_example to .env and adjust values:** 

```bash
cp .env_example .env
```

### Poetry
* **Install dependencies and activate virtual environment:**

```Bash
poetry install
poetry shell
```
---

## 🔌 API Endpoints (Users Service – Internal)

⚠️ This service is NOT exposed directly to clients.  
It is used internally by the API Gateway.

---

## 👤 User Management

| Method | Endpoint    | Query Params    | Body | Description        |
|--------|-------------|-----------------|------|--------------------|
| GET    | /api/users/ | user_id         | -    | Get user by ID     |
| DELETE | /api/users/ | identifier      | -    | Delete user        |

---

## 🔐 Account Flow

| Method | Endpoint                     | Query Params | Body                | Description               |
|--------|------------------------------|--------------|---------------------|---------------------------|
| POST   | /api/users                   | -            | UserCreate          | Create user               |
| PATCH  | /api/users/activation        | code         | -                   | Activate user account     |
| POST   | /api/users/activation/code   | identifier   | -                   | Resend activation code    |
| POST   | /api/users/password/forgot   | identifier   | -                   | Forgot password           |
| POST   | /api/users/password/reset    | -            | UserResetPassword   | Reset password            |

---

## 🔑 Authentication (used by API Gateway)

| Method | Endpoint              | Query Params | Body        | Description            |
|--------|-----------------------|--------------|-------------|------------------------|
| POST   | /api/users/auth       | -            | UserLogin   | Verify credentials     |
| POST   | /api/users/mfa/verify | -            | MfaVerify   | Verify MFA code        |

---

## 🛡️ MFA

| Method | Endpoint               | Query Params | Body | Description |
|--------|------------------------|--------------|------|-------------|
| PATCH  | /api/users/mfa/enable  | user_id      | -    | Enable MFA  |
| PATCH  | /api/users/mfa/disable | user_id      | -    | Disable MFA |

---

## 🧾 Notes

- `identifier` = username or email  
- `code` = activation or MFA code  
- Authentication is handled by API Gateway  
- This service focuses only on user domain logic  

## 📂 Project Structure
```text
tests/
users/
├── api/
│   ├──routes/
│   │     ├── account.py
│   │     └── auth.py
│   ├── dependencies.py
│   └── error_handlers.py
│
├── core/
│   ├── config.py
│   ├── security.py
│   ├── database.py
│   └── exceptions.py
│
├── domain/
│   ├── schemas.py
│   └── models.py
│
├── repositories/
│   └── user_repository.py
│
├── services/
│   ├── account_service.py
│   ├── auth_service.py
│   ├── email_service.py
│
└── main.py
```
---

## 🔗 Relation to API Gateway

This service is consumed by the API Gateway which is responsible for:

- JWT generation and validation
- Request authentication
- Role-based authorization
- Request routing

Users Service focuses purely on domain logic and persistence.