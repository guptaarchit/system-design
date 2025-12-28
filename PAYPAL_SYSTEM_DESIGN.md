# PayPal System Design Document

## Table of Contents
1. [Overview](#overview)
2. [Requirements](#requirements)
3. [System Architecture](#system-architecture)
4. [Database Design](#database-design)
5. [API Design](#api-design)
6. [Payment Processing Flow](#payment-processing-flow)
7. [Fraud Detection & Risk Management](#fraud-detection--risk-management)
8. [Wallet & Balance Management](#wallet--balance-management)
9. [Merchant Integration](#merchant-integration)
10. [Scalability Considerations](#scalability-considerations)
11. [Caching Strategy](#caching-strategy)
12. [Load Balancing](#load-balancing)
13. [Security](#security)
14. [Compliance & Regulations](#compliance--regulations)
15. [Monitoring & Analytics](#monitoring--analytics)
16. [Deployment Strategy](#deployment-strategy)
17. [Capacity Planning](#capacity-planning)
18. [Technology Stack](#technology-stack)
19. [Failure Scenarios & Handling](#failure-scenarios--handling)
20. [Trade-offs & Design Decisions](#trade-offs--design-decisions)
21. [Interview Discussion Points](#interview-discussion-points)

---

## Overview

PayPal is a global digital payment platform that enables individuals and businesses to send, receive, and manage money online. The system must handle millions of transactions daily, ensure financial security, detect fraud, support multiple currencies, and provide seamless user experience across web and mobile platforms.

**Key Features:**
- Send and receive money
- Online payment processing
- Merchant payment integration
- Multi-currency support
- Digital wallet with balance management
- Recurring payments and subscriptions
- Invoice generation
- Payment disputes and resolution
- Fraud detection and prevention
- Bank account and card linking
- International money transfers
- Business account management

---

## Requirements

### Functional Requirements

1. **User Account Management**
   - User registration and authentication (email, phone, 2FA)
   - Profile management
   - KYC (Know Your Customer) verification
   - Account types (Personal, Business, Premier)
   - Multiple linked payment methods (cards, bank accounts)

2. **Payment Processing**
   - Send money to other PayPal users
   - Receive money from other users
   - Process payments for merchants
   - Support multiple payment methods (PayPal balance, cards, bank accounts)
   - Handle payment failures and retries
   - Support partial payments
   - Payment scheduling and recurring payments

3. **Wallet & Balance Management**
   - Maintain account balance
   - Add/withdraw funds
   - Transfer funds between accounts
   - Multi-currency wallet support
   - Currency conversion
   - Transaction history

4. **Merchant Integration**
   - Payment gateway APIs
   - Webhook notifications
   - Payment buttons and checkout flows
   - Subscription management
   - Invoice generation
   - Refund processing

5. **Fraud Detection**
   - Real-time fraud scoring
   - Transaction risk assessment
   - Account security monitoring
   - Suspicious activity detection
   - Automated fraud prevention

6. **Dispute Management**
   - Payment disputes creation
   - Dispute resolution workflow
   - Chargeback handling
   - Refund processing

### Non-Functional Requirements

1. **Scalability**
   - Support 400M+ active users globally
   - Handle 20M+ transactions per day
   - Process 10,000+ transactions per second (peak)
   - 99.99% uptime (financial system requirement)
   - Multi-region deployment

2. **Performance**
   - Payment processing: < 2 seconds end-to-end
   - API response time: < 200ms (p95)
   - Balance queries: < 100ms
   - Transaction history: < 500ms
   - 99th percentile latency < 1s

3. **Security**
   - PCI DSS compliance (Payment Card Industry Data Security Standard)
   - End-to-end encryption
   - Fraud detection accuracy: > 99.5%
   - Zero tolerance for data breaches
   - Multi-factor authentication
   - Audit logging for all financial transactions

4. **Reliability**
   - Zero data loss for transactions
   - Transaction atomicity guarantees
   - Idempotent operations
   - Eventual consistency acceptable for non-critical data
   - Strong consistency for balance and critical transactions

5. **Compliance**
   - PCI DSS Level 1 compliance
   - GDPR compliance
   - Regional financial regulations (US, EU, etc.)
   - Anti-money laundering (AML) compliance
   - Tax reporting requirements

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                             │
│  (Web App, Mobile Apps, Merchant SDKs, API Clients)             │
└────────────────┬────────────────────────────────────────────────┘
                 │ HTTPS/TLS
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CDN & Edge Network                            │
│              (CloudFlare, AWS CloudFront)                       │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API Gateway / Load Balancer                   │
│              (Kong, AWS API Gateway, NGINX)                     │
│              - Rate Limiting                                    │
│              - Authentication                                   │
│              - Request Routing                                  │
└────────────┬────────────────────────────────────┬────────────────┘
             │                                    │
             ▼                                    ▼
┌────────────────────────────┐      ┌────────────────────────────┐
│   Payment Service          │      │   User Service             │
│   - Process Payments       │      │   - Account Management     │
│   - Transaction Handling   │      │   - Authentication         │
└────────────┬───────────────┘      └────────────┬───────────────┘
             │                                    │
             ▼                                    ▼
┌────────────────────────────┐      ┌────────────────────────────┐
│   Wallet Service           │      │   Fraud Detection Service  │
│   - Balance Management     │      │   - Risk Scoring           │
│   - Currency Conversion    │      │   - Pattern Detection      │
└────────────┬───────────────┘      └────────────┬───────────────┘
             │                                    │
             ▼                                    ▼
┌────────────────────────────────────────────────────────────────┐
│                      Core Services Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Transaction │  │   Merchant   │  │   Dispute    │         │
│  │   Service    │  │   Service    │  │   Service    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────┬────────────────────┬────────────────────┬──────────────────┘
     │                    │                    │
     ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  Message Queue  │  │   Cache Layer   │  │   Event Bus     │
│  (Kafka/RabbitMQ│  │    (Redis)      │  │   (Kafka)       │
└─────────────────┘  └─────────────────┘  └─────────────────┘
     │                    │                    │
     ▼                    ▼                    ▼
┌────────────────────────────────────────────────────────────────┐
│                      Data Layer                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Transaction │  │    User      │  │   Wallet     │         │
│  │     DB       │  │     DB       │  │     DB       │         │
│  │ (PostgreSQL) │  │ (PostgreSQL) │  │ (PostgreSQL) │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Audit Log  │  │   Analytics  │  │   Search     │         │
│  │     DB       │  │     DB       │  │     DB       │         │
│  │  (Cassandra) │  │  (ClickHouse)│  │ (Elasticsearch│        │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────────────────────────────────────────────┘
     │                    │                    │
     ▼                    ▼                    ▼
┌────────────────────────────────────────────────────────────────┐
│                    External Services                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Banking    │  │   Card       │  │   Currency   │         │
│  │   Networks   │  │   Networks   │  │   Exchange   │         │
│  │  (ACH, SWIFT)│  │  (Visa, MC)  │  │   APIs       │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────────────────────────────────────────────┘
```

### Component Details

#### 1. API Gateway
- **Purpose**: Single entry point for all client requests
- **Responsibilities**:
  - Request routing to appropriate services
  - Authentication and authorization
  - Rate limiting and throttling
  - Request/response transformation
  - API versioning
  - SSL/TLS termination

#### 2. Payment Service
- **Purpose**: Core payment processing engine
- **Responsibilities**:
  - Payment authorization
  - Payment capture
  - Refund processing
  - Payment status management
  - Transaction orchestration

#### 3. Wallet Service
- **Purpose**: Manage user balances and wallets
- **Responsibilities**:
  - Balance updates (atomic operations)
  - Multi-currency support
  - Currency conversion
  - Balance queries
  - Fund transfers between accounts

#### 4. Fraud Detection Service
- **Purpose**: Real-time fraud detection and prevention
- **Responsibilities**:
  - Transaction risk scoring
  - Pattern detection (ML models)
  - Account security monitoring
  - Automated fraud prevention
  - Manual review queue management

#### 5. Transaction Service
- **Purpose**: Transaction lifecycle management
- **Responsibilities**:
  - Transaction creation and tracking
  - Transaction history
  - Transaction search and filtering
  - Transaction reporting

#### 6. Merchant Service
- **Purpose**: Merchant account and integration management
- **Responsibilities**:
  - Merchant onboarding
  - API key management
  - Webhook delivery
  - Merchant dashboard
  - Settlement processing

#### 7. User Service
- **Purpose**: User account management
- **Responsibilities**:
  - User registration and authentication
  - Profile management
  - KYC verification
  - Payment method management
  - Account settings

---

## Database Design

### 1. Users Table

```sql
CREATE TABLE users (
    user_id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    password_hash VARCHAR(255) NOT NULL,
    account_type VARCHAR(20) NOT NULL, -- PERSONAL, BUSINESS, PREMIER
    status VARCHAR(20) NOT NULL, -- ACTIVE, SUSPENDED, CLOSED, VERIFICATION_PENDING
    kyc_status VARCHAR(20) NOT NULL, -- NOT_STARTED, PENDING, VERIFIED, REJECTED
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_login_at TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);
```

### 2. Wallets Table

```sql
CREATE TABLE wallets (
    wallet_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    currency_code VARCHAR(3) NOT NULL, -- USD, EUR, GBP, etc.
    balance DECIMAL(20, 2) NOT NULL DEFAULT 0.00,
    available_balance DECIMAL(20, 2) NOT NULL DEFAULT 0.00, -- Balance minus holds
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    UNIQUE KEY unique_user_currency (user_id, currency_code),
    INDEX idx_user_id (user_id),
    INDEX idx_currency (currency_code)
);
```

### 3. Transactions Table

```sql
CREATE TABLE transactions (
    transaction_id BIGSERIAL PRIMARY KEY,
    transaction_uuid VARCHAR(36) UNIQUE NOT NULL, -- UUID for external reference
    payer_id BIGINT NOT NULL,
    payee_id BIGINT NOT NULL,
    amount DECIMAL(20, 2) NOT NULL,
    currency_code VARCHAR(3) NOT NULL,
    transaction_type VARCHAR(20) NOT NULL, -- PAYMENT, REFUND, TRANSFER, WITHDRAWAL, DEPOSIT
    status VARCHAR(20) NOT NULL, -- PENDING, PROCESSING, COMPLETED, FAILED, CANCELLED, REFUNDED
    payment_method VARCHAR(20) NOT NULL, -- PAYPAL_BALANCE, CREDIT_CARD, DEBIT_CARD, BANK_ACCOUNT
    payment_method_id BIGINT, -- Reference to payment_methods table
    merchant_id BIGINT, -- NULL for P2P transactions
    description TEXT,
    fraud_score DECIMAL(5, 2), -- 0.00 to 100.00
    fraud_status VARCHAR(20), -- APPROVED, REVIEW, REJECTED
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP,
    FOREIGN KEY (payer_id) REFERENCES users(user_id),
    FOREIGN KEY (payee_id) REFERENCES users(user_id),
    FOREIGN KEY (merchant_id) REFERENCES merchants(merchant_id),
    INDEX idx_payer_id (payer_id),
    INDEX idx_payee_id (payee_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    INDEX idx_transaction_uuid (transaction_uuid),
    INDEX idx_merchant_id (merchant_id)
) PARTITION BY RANGE (created_at); -- Partition by month for scalability
```

### 4. Payment Methods Table

```sql
CREATE TABLE payment_methods (
    payment_method_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    type VARCHAR(20) NOT NULL, -- CREDIT_CARD, DEBIT_CARD, BANK_ACCOUNT
    provider VARCHAR(50), -- VISA, MASTERCARD, BANK_NAME
    last_four_digits VARCHAR(4),
    expiry_date DATE, -- For cards
    billing_address_id BIGINT,
    is_default BOOLEAN DEFAULT FALSE,
    status VARCHAR(20) NOT NULL, -- ACTIVE, EXPIRED, REMOVED
    token VARCHAR(255) NOT NULL, -- Encrypted token (PCI compliance)
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status)
);
```

### 5. Transaction Holds Table

```sql
CREATE TABLE transaction_holds (
    hold_id BIGSERIAL PRIMARY KEY,
    transaction_id BIGINT NOT NULL,
    wallet_id BIGINT NOT NULL,
    amount DECIMAL(20, 2) NOT NULL,
    status VARCHAR(20) NOT NULL, -- PENDING, RELEASED, CAPTURED
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id),
    FOREIGN KEY (wallet_id) REFERENCES wallets(wallet_id),
    INDEX idx_transaction_id (transaction_id),
    INDEX idx_wallet_id (wallet_id),
    INDEX idx_expires_at (expires_at)
);
```

### 6. Merchants Table

```sql
CREATE TABLE merchants (
    merchant_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    business_name VARCHAR(255) NOT NULL,
    business_type VARCHAR(50),
    tax_id VARCHAR(50),
    status VARCHAR(20) NOT NULL, -- ACTIVE, SUSPENDED, CLOSED
    api_key VARCHAR(255) UNIQUE NOT NULL,
    webhook_url VARCHAR(500),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    INDEX idx_user_id (user_id),
    INDEX idx_api_key (api_key)
);
```

### 7. Disputes Table

```sql
CREATE TABLE disputes (
    dispute_id BIGSERIAL PRIMARY KEY,
    transaction_id BIGINT NOT NULL,
    initiator_id BIGINT NOT NULL, -- User who initiated dispute
    dispute_type VARCHAR(20) NOT NULL, -- CHARGEBACK, REFUND_REQUEST, UNAUTHORIZED
    reason TEXT NOT NULL,
    status VARCHAR(20) NOT NULL, -- OPEN, UNDER_REVIEW, RESOLVED, CLOSED
    resolution VARCHAR(20), -- REFUNDED, DENIED, PARTIAL_REFUND
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    resolved_at TIMESTAMP,
    FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id),
    FOREIGN KEY (initiator_id) REFERENCES users(user_id),
    INDEX idx_transaction_id (transaction_id),
    INDEX idx_status (status)
);
```

### 8. Audit Log Table

```sql
CREATE TABLE audit_logs (
    log_id BIGSERIAL PRIMARY KEY,
    entity_type VARCHAR(50) NOT NULL, -- TRANSACTION, USER, WALLET
    entity_id BIGINT NOT NULL,
    action VARCHAR(50) NOT NULL, -- CREATED, UPDATED, DELETED, APPROVED, REJECTED
    user_id BIGINT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    changes JSONB, -- Before/after state
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    INDEX idx_entity (entity_type, entity_id),
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
) PARTITION BY RANGE (created_at);
```

### Database Sharding Strategy

For scalability, we'll shard by `user_id`:
- **Shard Key**: `user_id % num_shards`
- **Sharding Approach**: Horizontal sharding with consistent hashing
- **Cross-shard Transactions**: Use distributed transaction coordinator (2PC or Saga pattern)

---

## API Design

### RESTful API Endpoints

#### Authentication APIs

```
POST   /api/v1/auth/register
POST   /api/v1/auth/login
POST   /api/v1/auth/logout
POST   /api/v1/auth/refresh-token
POST   /api/v1/auth/verify-2fa
```

#### User APIs

```
GET    /api/v1/users/{user_id}
PUT    /api/v1/users/{user_id}
GET    /api/v1/users/{user_id}/profile
PUT    /api/v1/users/{user_id}/profile
POST   /api/v1/users/{user_id}/kyc-verification
```

#### Payment APIs

```
POST   /api/v1/payments
GET    /api/v1/payments/{payment_id}
POST   /api/v1/payments/{payment_id}/capture
POST   /api/v1/payments/{payment_id}/refund
GET    /api/v1/payments/{payment_id}/status
```

#### Wallet APIs

```
GET    /api/v1/wallets
GET    /api/v1/wallets/{wallet_id}
GET    /api/v1/wallets/{wallet_id}/balance
POST   /api/v1/wallets/{wallet_id}/deposit
POST   /api/v1/wallets/{wallet_id}/withdraw
GET    /api/v1/wallets/{wallet_id}/transactions
```

#### Transaction APIs

```
GET    /api/v1/transactions
GET    /api/v1/transactions/{transaction_id}
POST   /api/v1/transactions/search
GET    /api/v1/transactions/{transaction_id}/receipt
```

#### Payment Method APIs

```
GET    /api/v1/payment-methods
POST   /api/v1/payment-methods
DELETE /api/v1/payment-methods/{payment_method_id}
PUT    /api/v1/payment-methods/{payment_method_id}/default
```

#### Merchant APIs

```
POST   /api/v1/merchants/payments
GET    /api/v1/merchants/{merchant_id}/payments
POST   /api/v1/merchants/{merchant_id}/webhooks
GET    /api/v1/merchants/{merchant_id}/settlements
```

### API Request/Response Examples

#### Create Payment

**Request:**
```json
POST /api/v1/payments
{
  "payer_id": "user_123",
  "payee_id": "user_456",
  "amount": 100.00,
  "currency": "USD",
  "payment_method": "PAYPAL_BALANCE",
  "description": "Payment for services",
  "merchant_id": "merchant_789" // Optional
}
```

**Response:**
```json
{
  "payment_id": "pay_abc123",
  "status": "PROCESSING",
  "amount": 100.00,
  "currency": "USD",
  "created_at": "2024-01-15T10:30:00Z",
  "links": [
    {
      "rel": "self",
      "href": "/api/v1/payments/pay_abc123"
    },
    {
      "rel": "status",
      "href": "/api/v1/payments/pay_abc123/status"
    }
  ]
}
```

#### Get Transaction History

**Request:**
```json
GET /api/v1/transactions?user_id=user_123&limit=50&offset=0&status=COMPLETED
```

**Response:**
```json
{
  "transactions": [
    {
      "transaction_id": "txn_xyz789",
      "type": "PAYMENT",
      "amount": 100.00,
      "currency": "USD",
      "status": "COMPLETED",
      "payer": {
        "user_id": "user_123",
        "name": "John Doe"
      },
      "payee": {
        "user_id": "user_456",
        "name": "Jane Smith"
      },
      "created_at": "2024-01-15T10:30:00Z",
      "completed_at": "2024-01-15T10:30:02Z"
    }
  ],
  "pagination": {
    "total": 150,
    "limit": 50,
    "offset": 0,
    "has_more": true
  }
}
```

---

## Payment Processing Flow

### 1. P2P Payment Flow (User to User)

```
┌──────────┐         ┌──────────────┐         ┌──────────────┐
│  Payer   │────────▶│  API Gateway │────────▶│ Payment      │
│  Client  │         │              │         │ Service      │
└──────────┘         └──────────────┘         └──────┬───────┘
                                                      │
                                                      ▼
                                            ┌─────────────────┐
                                            │ Fraud Detection  │
                                            │ Service          │
                                            └────────┬─────────┘
                                                     │
                                                     ▼
                                            ┌─────────────────┐
                                            │ Risk Score      │
                                            │ < 50: Approve   │
                                            │ 50-80: Review   │
                                            │ > 80: Reject    │
                                            └────────┬─────────┘
                                                     │
                                                     ▼
                                            ┌─────────────────┐
                                            │ Wallet Service   │
                                            │ - Check Balance  │
                                            │ - Create Hold    │
                                            └────────┬─────────┘
                                                     │
                                                     ▼
                                            ┌─────────────────┐
                                            │ Transaction DB  │
                                            │ - Create Txn    │
                                            │ - Update Status │
                                            └────────┬─────────┘
                                                     │
                                                     ▼
                                            ┌─────────────────┐
                                            │ Wallet Service   │
                                            │ - Debit Payer   │
                                            │ - Credit Payee  │
                                            └────────┬─────────┘
                                                     │
                                                     ▼
                                            ┌─────────────────┐
                                            │ Notification    │
                                            │ Service         │
                                            └─────────────────┘
```

**Step-by-Step Process:**

1. **Payment Request**: Payer initiates payment via client app
2. **Authentication**: API Gateway validates authentication token
3. **Fraud Check**: Payment Service calls Fraud Detection Service
   - Real-time risk scoring
   - Pattern matching against known fraud patterns
   - Velocity checks (transaction frequency)
   - Device fingerprinting
4. **Balance Check**: Wallet Service checks payer's balance
5. **Hold Creation**: Create transaction hold (reserve funds)
6. **Transaction Creation**: Create transaction record with status "PROCESSING"
7. **Fund Transfer**: 
   - Debit payer's wallet (atomic operation)
   - Credit payee's wallet (atomic operation)
8. **Status Update**: Update transaction status to "COMPLETED"
9. **Notifications**: Send notifications to both payer and payee
10. **Webhook**: If merchant payment, send webhook notification

### 2. Card Payment Flow

```
┌──────────┐         ┌──────────────┐         ┌──────────────┐
│  Client  │────────▶│ Payment      │────────▶│ Card         │
│          │         │ Service      │         │ Processor    │
└──────────┘         └──────┬───────┘         │ (Visa/MC)    │
                            │                 └──────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │ Fraud        │
                    │ Detection    │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ Authorization│
                    │ Hold         │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ Capture      │
                    │ (if approved)│
                    └──────────────┘
```

**Process:**
1. User selects card as payment method
2. Payment Service tokenizes card (PCI compliance)
3. Fraud check performed
4. Authorization request sent to card network
5. If authorized, create authorization hold
6. Capture funds (immediate or delayed)
7. Update transaction status
8. Credit payee's wallet

### 3. Bank Transfer Flow

```
┌──────────┐         ┌──────────────┐         ┌──────────────┐
│  Client  │────────▶│ Payment      │────────▶│ Banking      │
│          │         │ Service      │         │ Network      │
└──────────┘         └──────┬───────┘         │ (ACH/SWIFT)  │
                            │                 └──────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │ Queue for    │
                    │ Batch        │
                    │ Processing   │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ Settlement   │
                    │ Service      │
                    └──────────────┘
```

**Process:**
1. User initiates bank transfer
2. Payment Service validates bank account
3. Transaction queued for batch processing
4. Settlement Service processes in batches (typically daily)
5. Funds transferred via ACH or SWIFT
6. Status updated when settlement completes

---

## Fraud Detection & Risk Management

### Fraud Detection Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Transaction Request                       │
└───────────────────────┬───────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              Fraud Detection Service                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Rule Engine  │  │ ML Models    │  │ Real-time    │     │
│  │ - Velocity   │  │ - Anomaly    │  │ Analytics    │     │
│  │ - Amount     │  │   Detection  │  │ - Patterns   │     │
│  │ - Geography  │  │ - Clustering │  │ - Trends     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└───────────────────────┬───────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              Risk Score Calculation                          │
│  Score = (Rule Score × 0.4) + (ML Score × 0.6)             │
└───────────────────────┬───────────────────────────────────────┘
                        │
                        ▼
            ┌───────────┴───────────┐
            │                       │
            ▼                       ▼
    ┌──────────────┐        ┌──────────────┐
    │ Score < 50   │        │ Score ≥ 50   │
    │ APPROVE      │        │ REVIEW/REJECT│
    └──────────────┘        └──────────────┘
```

### Fraud Detection Rules

1. **Velocity Checks**
   - Number of transactions in last hour/day
   - Transaction amount patterns
   - Geographic velocity (multiple locations quickly)

2. **Amount Checks**
   - Unusually large amounts
   - Amounts just below reporting thresholds
   - Rapidly increasing amounts

3. **Device & Behavior**
   - Device fingerprinting
   - IP address reputation
   - Browser/OS anomalies
   - Typing patterns

4. **Account History**
   - New account with high-value transactions
   - Account age and verification status
   - Previous fraud flags

5. **Pattern Detection**
   - Known fraud patterns (ML)
   - Anomaly detection
   - Clustering analysis

### ML Models

- **Supervised Learning**: Historical fraud data training
- **Unsupervised Learning**: Anomaly detection
- **Real-time Scoring**: < 100ms response time
- **Model Updates**: Daily retraining with new data

### Fraud Response Actions

- **Score < 30**: Auto-approve
- **Score 30-50**: Approve with monitoring
- **Score 50-70**: Manual review queue
- **Score 70-90**: Hold transaction, require additional verification
- **Score > 90**: Auto-reject, flag account

---

## Wallet & Balance Management

### Balance Management Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Wallet Service                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Balance      │  │ Currency     │  │ Transaction  │     │
│  │ Manager      │  │ Converter    │  │ Coordinator  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└───────────────────────┬───────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              Distributed Lock Manager                        │
│              (Redis/Zookeeper)                              │
└───────────────────────┬───────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              Wallet Database (Sharded)                      │
│              Strong Consistency                             │
└─────────────────────────────────────────────────────────────┘
```

### Balance Operations

#### Atomic Balance Update

```python
def transfer_funds(payer_wallet_id, payee_wallet_id, amount, currency):
    # Acquire distributed locks
    payer_lock = acquire_lock(f"wallet:{payer_wallet_id}")
    payee_lock = acquire_lock(f"wallet:{payee_wallet_id}")
    
    try:
        # Start transaction
        with db.transaction():
            # Check payer balance
            payer_wallet = get_wallet(payer_wallet_id, currency)
            if payer_wallet.available_balance < amount:
                raise InsufficientFundsError()
            
            # Debit payer
            update_wallet_balance(
                payer_wallet_id, 
                amount=-amount, 
                currency=currency
            )
            
            # Credit payee
            update_wallet_balance(
                payee_wallet_id, 
                amount=amount, 
                currency=currency
            )
            
            # Log transaction
            create_transaction_record(...)
            
    finally:
        release_lock(payer_lock)
        release_lock(payee_lock)
```

### Multi-Currency Support

- **Wallet per Currency**: Each user has separate wallet per currency
- **Currency Conversion**: Real-time exchange rates from external APIs
- **Conversion Fees**: Applied during currency conversion
- **Exchange Rate Cache**: 5-minute TTL for exchange rates

### Balance Consistency

- **Strong Consistency**: Required for balance operations
- **Distributed Locks**: Prevent race conditions
- **Idempotency**: All operations are idempotent
- **Event Sourcing**: Optional for audit trail

---

## Merchant Integration

### Payment Gateway Integration

#### Checkout Flow

```
┌──────────┐         ┌──────────────┐         ┌──────────────┐
│ Customer │────────▶│   Merchant   │────────▶│   PayPal      │
│          │         │   Website    │         │   Checkout    │
└──────────┘         └──────────────┘         └──────┬───────┘
                                                     │
                                                     ▼
                                            ┌─────────────────┐
                                            │ Payment         │
                                            │ Processing      │
                                            └──────┬─────────┘
                                                   │
                                                   ▼
                                            ┌─────────────────┐
                                            │ Webhook         │
                                            │ Notification    │
                                            └─────────────────┘
```

### Merchant APIs

#### Create Payment (Merchant)

```json
POST /api/v1/merchants/payments
Headers:
  Authorization: Bearer {merchant_api_key}
  
Body:
{
  "amount": 100.00,
  "currency": "USD",
  "description": "Order #12345",
  "return_url": "https://merchant.com/success",
  "cancel_url": "https://merchant.com/cancel",
  "webhook_url": "https://merchant.com/webhook",
  "metadata": {
    "order_id": "12345",
    "customer_id": "cust_789"
  }
}
```

#### Webhook Notification

```json
POST {merchant_webhook_url}
Headers:
  X-PayPal-Signature: {signature}
  X-PayPal-Event-Type: payment.completed
  
Body:
{
  "event_id": "evt_abc123",
  "event_type": "payment.completed",
  "payment_id": "pay_xyz789",
  "amount": 100.00,
  "currency": "USD",
  "status": "COMPLETED",
  "created_at": "2024-01-15T10:30:00Z",
  "metadata": {
    "order_id": "12345"
  }
}
```

### Settlement Process

- **Batch Processing**: Daily settlement runs
- **Settlement Window**: Typically T+1 (next day)
- **Settlement Currency**: Merchant's preferred currency
- **Fees Deduction**: Transaction fees deducted before settlement
- **Bank Transfer**: Funds transferred to merchant's bank account

---

## Scalability Considerations

### Horizontal Scaling

1. **Stateless Services**: All services are stateless
2. **Load Balancing**: Multiple instances behind load balancers
3. **Database Sharding**: Shard by user_id
4. **Read Replicas**: Multiple read replicas for read-heavy operations
5. **Caching**: Aggressive caching for frequently accessed data

### Vertical Scaling

- **Database Optimization**: Indexing, query optimization
- **Connection Pooling**: Efficient database connection management
- **Async Processing**: Non-blocking I/O for better throughput

### Partitioning Strategy

- **Users Table**: Shard by `user_id % num_shards`
- **Transactions Table**: Partition by `created_at` (monthly partitions)
- **Audit Logs**: Partition by `created_at` (daily partitions)

### Caching Strategy

- **User Sessions**: Redis (TTL: 24 hours)
- **Wallet Balances**: Redis (TTL: 5 minutes, invalidate on update)
- **Exchange Rates**: Redis (TTL: 5 minutes)
- **Merchant API Keys**: Redis (TTL: 1 hour)
- **Transaction History**: Cache recent transactions (last 100)

---

## Caching Strategy

### Cache Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                         │
└───────────────────────┬───────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              L1 Cache (In-Memory)                           │
│              - User Sessions                                 │
│              - Frequently accessed data                      │
│              TTL: 1-5 minutes                               │
└───────────────────────┬───────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              L2 Cache (Redis Cluster)                        │
│              - Wallet Balances                              │
│              - User Profiles                                 │
│              - Exchange Rates                                │
│              - Transaction History (recent)                 │
│              TTL: 5-60 minutes                               │
└───────────────────────┬───────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              Database                                        │
└─────────────────────────────────────────────────────────────┘
```

### Cache Invalidation

- **Write-Through**: Update cache and database simultaneously
- **Write-Behind**: Update cache first, async database update
- **Cache-Aside**: Application manages cache (read from cache, write to DB, update cache)
- **TTL-Based**: Automatic expiration

### Cache Patterns

1. **Cache-Aside Pattern**: For read-heavy data
2. **Write-Through Pattern**: For critical data (balances)
3. **Write-Behind Pattern**: For non-critical updates
4. **Refresh-Ahead Pattern**: Pre-warm cache before expiration

---

## Load Balancing

### Load Balancing Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                    DNS Load Balancer                         │
│              (Geographic Distribution)                        │
└───────────────────────┬───────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              Application Load Balancer                       │
│              (Layer 7 - NGINX/HAProxy)                      │
│              - SSL Termination                               │
│              - Request Routing                               │
│              - Health Checks                                 │
└───────────────────────┬───────────────────────────────────────┘
                        │
                        ▼
        ┌───────────────┴───────────────┐
        │                               │
        ▼                               ▼
┌──────────────┐              ┌──────────────┐
│   Service    │              │   Service    │
│  Instance 1  │              │  Instance 2  │
└──────────────┘              └──────────────┘
```

### Load Balancing Algorithms

- **Round Robin**: Equal distribution
- **Least Connections**: Route to server with fewest connections
- **Weighted Round Robin**: Based on server capacity
- **IP Hash**: Sticky sessions based on client IP
- **Geographic**: Route based on user location

### Health Checks

- **Endpoint**: `/health`
- **Interval**: Every 10 seconds
- **Timeout**: 5 seconds
- **Failure Threshold**: 3 consecutive failures
- **Recovery Threshold**: 2 consecutive successes

---

## Security

### Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Security Layers                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Network      │  │ Application  │  │ Data         │     │
│  │ Security     │  │ Security     │  │ Security     │     │
│  │ - DDoS       │  │ - AuthN/AuthZ│  │ - Encryption │     │
│  │ - WAF        │  │ - Rate Limit │  │ - Tokenization│    │
│  │ - Firewall   │  │ - Input Valid│  │ - Masking    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### Authentication & Authorization

1. **Multi-Factor Authentication (MFA)**
   - SMS-based OTP
   - Authenticator app (TOTP)
   - Hardware security keys

2. **OAuth 2.0 / JWT**
   - Access tokens (short-lived: 15 minutes)
   - Refresh tokens (long-lived: 7 days)
   - Token rotation

3. **API Keys**
   - Merchant API keys
   - Scoped permissions
   - Rate limiting per key

### Data Protection

1. **Encryption**
   - **In Transit**: TLS 1.3 for all communications
   - **At Rest**: AES-256 encryption for sensitive data
   - **Database**: Transparent Data Encryption (TDE)

2. **PCI DSS Compliance**
   - Card data tokenization
   - No storage of full card numbers
   - Secure card data handling
   - Regular security audits

3. **Data Masking**
   - Mask sensitive data in logs
   - PII encryption
   - Access controls for sensitive data

### Security Measures

1. **Rate Limiting**
   - Per user: 100 requests/minute
   - Per IP: 1000 requests/minute
   - Per API key: Based on plan

2. **Input Validation**
   - Sanitize all inputs
   - SQL injection prevention
   - XSS prevention
   - CSRF protection

3. **Audit Logging**
   - All financial transactions logged
   - Authentication events logged
   - Access to sensitive data logged
   - Immutable audit trail

4. **Intrusion Detection**
   - Real-time monitoring
   - Anomaly detection
   - Automated threat response

---

## Compliance & Regulations

### Regulatory Compliance

1. **PCI DSS (Payment Card Industry Data Security Standard)**
   - Level 1 compliance required
   - Annual audits
   - Secure card data handling
   - Network security requirements

2. **GDPR (General Data Protection Regulation)**
   - User data privacy rights
   - Data portability
   - Right to be forgotten
   - Consent management

3. **AML (Anti-Money Laundering)**
   - Transaction monitoring
   - Suspicious activity reporting
   - KYC requirements
   - Record keeping

4. **Regional Regulations**
   - **US**: FinCEN, OFAC compliance
   - **EU**: PSD2 (Payment Services Directive)
   - **UK**: FCA regulations
   - Country-specific requirements

### Compliance Features

1. **KYC (Know Your Customer)**
   - Identity verification
   - Document verification
   - Address verification
   - Business verification (for merchants)

2. **Transaction Monitoring**
   - Large transaction reporting
   - Suspicious pattern detection
   - Regulatory reporting

3. **Data Retention**
   - Transaction records: 7 years
   - Audit logs: 7 years
   - User data: Per GDPR requirements

---

## Monitoring & Analytics

### Monitoring Stack

```
┌─────────────────────────────────────────────────────────────┐
│                    Monitoring Architecture                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Metrics      │  │ Logging      │  │ Tracing      │     │
│  │ (Prometheus) │  │ (ELK Stack)  │  │ (Jaeger)     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Alerting     │  │ Dashboards   │  │ Analytics    │     │
│  │ (PagerDuty)  │  │ (Grafana)   │  │ (ClickHouse) │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### Key Metrics

1. **Business Metrics**
   - Transaction volume (per second/minute/hour)
   - Transaction success rate
   - Revenue metrics
   - Active users
   - Payment method distribution

2. **Technical Metrics**
   - API latency (p50, p95, p99)
   - Error rates (4xx, 5xx)
   - Throughput (requests per second)
   - Database query performance
   - Cache hit rates

3. **Security Metrics**
   - Fraud detection rate
   - Failed authentication attempts
   - Suspicious activity alerts
   - Security incidents

### Alerting

- **Critical Alerts**: Payment processing failures, database outages
- **Warning Alerts**: High latency, increased error rates
- **Info Alerts**: Deployment notifications, scheduled maintenance

---

## Deployment Strategy

### Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Production Environment                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Region 1     │  │ Region 2     │  │ Region 3     │     │
│  │ (US-East)    │  │ (EU-West)    │  │ (AP-South)   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### Deployment Strategy

1. **Blue-Green Deployment**
   - Zero-downtime deployments
   - Instant rollback capability
   - Traffic switching via load balancer

2. **Canary Deployments**
   - Gradual rollout (5% → 25% → 50% → 100%)
   - Monitor metrics before full rollout
   - Automatic rollback on errors

3. **Feature Flags**
   - Gradual feature rollout
   - A/B testing capability
   - Instant feature toggling

### CI/CD Pipeline

```
Code Commit → Build → Unit Tests → Integration Tests → 
Security Scan → Build Docker Image → Deploy to Staging → 
E2E Tests → Deploy to Production (Canary) → Monitor → 
Full Rollout
```

---

## Capacity Planning

### Traffic Estimates

- **Daily Active Users**: 50M (12.5% of 400M total users)
- **Peak Transactions per Second**: 10,000 TPS
- **Average Transaction Size**: $50
- **Daily Transaction Volume**: 20M transactions/day
- **Peak Hour Traffic**: 3x average = 30,000 TPS

### Storage Estimates

- **User Data**: 400M users × 5KB = 2TB
- **Transaction Data**: 20M/day × 365 days × 1KB = 7.3TB/year
- **Audit Logs**: 100M events/day × 365 days × 500 bytes = 18.25TB/year
- **Total Storage (5 years)**: ~150TB

### Compute Estimates

- **API Servers**: 1000 instances (auto-scaling)
- **Database Servers**: 100 primary + 300 replicas
- **Cache Servers**: 50 Redis clusters
- **Message Queue**: 20 Kafka brokers

### Network Bandwidth

- **Average Request Size**: 2KB
- **Average Response Size**: 5KB
- **Peak Requests**: 10,000 TPS
- **Peak Bandwidth**: 10,000 × 7KB = 70MB/s = 560Mbps per region
- **Total Bandwidth**: ~2Gbps (with redundancy)

---

## Technology Stack

### Backend Services

- **Language**: Java, Go, Python
- **Frameworks**: Spring Boot, Gin, FastAPI
- **API Gateway**: Kong, AWS API Gateway
- **Service Mesh**: Istio (optional)

### Databases

- **Primary Database**: PostgreSQL (ACID transactions)
- **Time-Series Data**: TimescaleDB (for analytics)
- **Search**: Elasticsearch
- **Analytics**: ClickHouse
- **Audit Logs**: Cassandra

### Caching & Messaging

- **Cache**: Redis Cluster
- **Message Queue**: Apache Kafka, RabbitMQ
- **Event Streaming**: Kafka

### Infrastructure

- **Cloud Provider**: AWS, GCP, or Azure
- **Container Orchestration**: Kubernetes
- **Service Discovery**: Consul, Eureka
- **Configuration Management**: etcd, Consul

### Monitoring & Observability

- **Metrics**: Prometheus, CloudWatch
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **Tracing**: Jaeger, Zipkin
- **APM**: New Relic, Datadog

### Security

- **Secrets Management**: HashiCorp Vault, AWS Secrets Manager
- **WAF**: AWS WAF, CloudFlare
- **DDoS Protection**: CloudFlare, AWS Shield

---

## Failure Scenarios & Handling

### Failure Scenarios

1. **Database Failure**
   - **Impact**: Cannot process transactions
   - **Mitigation**: 
     - Database replication (primary + replicas)
     - Automatic failover to replica
     - Cross-region replication
   - **Recovery**: RTO < 5 minutes, RPO < 1 minute

2. **Payment Service Failure**
   - **Impact**: Payment processing unavailable
   - **Mitigation**:
     - Multiple service instances
     - Circuit breaker pattern
     - Graceful degradation
   - **Recovery**: RTO < 2 minutes

3. **Fraud Detection Service Failure**
   - **Impact**: Cannot assess transaction risk
   - **Mitigation**:
     - Fallback to rule-based scoring
     - Queue transactions for later review
     - Manual review queue
   - **Recovery**: RTO < 10 minutes

4. **Network Partition**
   - **Impact**: Service unavailability
   - **Mitigation**:
     - Multi-region deployment
     - Regional failover
     - Read-only mode during partition
   - **Recovery**: RTO < 15 minutes

5. **Cache Failure**
   - **Impact**: Increased database load
   - **Mitigation**:
     - Cache cluster (multiple nodes)
     - Fallback to database
     - Degraded performance acceptable
   - **Recovery**: RTO < 5 minutes

### Circuit Breaker Pattern

```python
class PaymentService:
    def __init__(self):
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            timeout=60,
            expected_exception=PaymentServiceException
        )
    
    @circuit_breaker
    def process_payment(self, payment_request):
        try:
            return self._process_payment(payment_request)
        except PaymentServiceException:
            # Fallback to queue for later processing
            self.queue_payment(payment_request)
            raise
```

### Retry Strategy

- **Exponential Backoff**: 1s, 2s, 4s, 8s, 16s
- **Max Retries**: 3 attempts
- **Idempotency**: All operations are idempotent
- **Dead Letter Queue**: Failed transactions after max retries

---

## Trade-offs & Design Decisions

### 1. Consistency vs Availability

**Decision**: Strong consistency for financial data (balances, transactions)

**Trade-off**:
- **Pros**: Data accuracy, no inconsistencies
- **Cons**: Lower availability during network partitions, higher latency

**Rationale**: Financial data requires accuracy. Users can tolerate brief unavailability but not incorrect balances.

### 2. Synchronous vs Asynchronous Processing

**Decision**: Synchronous for critical paths, asynchronous for non-critical

**Trade-off**:
- **Synchronous**: Payment processing, balance updates
- **Asynchronous**: Notifications, analytics, reporting

**Rationale**: Users expect immediate payment confirmation. Other operations can be async.

### 3. SQL vs NoSQL

**Decision**: SQL (PostgreSQL) for transactional data, NoSQL for analytics

**Trade-off**:
- **SQL**: ACID guarantees, complex queries, joins
- **NoSQL**: Better scalability, simpler queries

**Rationale**: Financial transactions require ACID properties. Analytics can use NoSQL for better performance.

### 4. Monolith vs Microservices

**Decision**: Microservices architecture

**Trade-off**:
- **Pros**: Independent scaling, technology diversity, fault isolation
- **Cons**: Increased complexity, network latency, distributed transactions

**Rationale**: Different services have different scaling needs (fraud detection vs user service).

### 5. Cache Strategy

**Decision**: Cache-Aside with TTL-based expiration

**Trade-off**:
- **Pros**: Simple, flexible, good for read-heavy workloads
- **Cons**: Cache misses cause database load, eventual consistency

**Rationale**: Balance between performance and complexity. Write-through too complex for all use cases.

### 6. Database Sharding

**Decision**: Shard by user_id with consistent hashing

**Trade-off**:
- **Pros**: Horizontal scalability, load distribution
- **Cons**: Cross-shard queries complex, rebalancing needed

**Rationale**: Most queries are user-specific. Cross-shard transactions handled via coordinator.

---

## Interview Discussion Points

### Key Topics to Discuss

1. **Payment Processing Flow**
   - How do you ensure atomicity in fund transfers?
   - How do you handle payment failures and retries?
   - What happens if a payment is partially processed?

2. **Fraud Detection**
   - How do you balance fraud detection accuracy with user experience?
   - What ML models would you use for fraud detection?
   - How do you handle false positives/negatives?

3. **Scalability**
   - How would you scale to handle 10x traffic?
   - What are the bottlenecks in your design?
   - How do you handle database scaling?

4. **Consistency**
   - How do you ensure balance consistency across services?
   - What consistency model do you use for different data types?
   - How do you handle distributed transactions?

5. **Security**
   - How do you protect against common attacks (SQL injection, XSS)?
   - How do you ensure PCI DSS compliance?
   - How do you handle sensitive data (card numbers, passwords)?

6. **Reliability**
   - How do you ensure zero data loss?
   - What's your disaster recovery plan?
   - How do you handle service failures?

7. **Performance**
   - How do you optimize for low latency?
   - What caching strategies do you use?
   - How do you handle database query optimization?

### Common Interview Questions

**Q: How would you design a system to process 1 million payments per second?**

**A:**
- Horizontal scaling with multiple payment service instances
- Database sharding and read replicas
- In-memory caching for frequently accessed data
- Async processing for non-critical operations
- Message queues for load distribution
- CDN for static content
- Optimized database queries and indexing

**Q: How do you ensure a payment is not processed twice?**

**A:**
- Idempotency keys in payment requests
- Database unique constraints on transaction IDs
- Distributed locks for critical operations
- Idempotent API design (same request = same result)

**Q: How do you handle currency conversion?**

**A:**
- Real-time exchange rates from external APIs
- Cache exchange rates (5-minute TTL)
- Conversion fees applied during conversion
- Multi-currency wallets per user
- Atomic conversion operations

**Q: How do you detect and prevent fraud?**

**A:**
- Real-time risk scoring (rule-based + ML)
- Pattern detection and anomaly detection
- Velocity checks and geographic analysis
- Device fingerprinting
- Manual review queue for high-risk transactions
- Continuous model retraining

**Q: How do you ensure data consistency in a distributed system?**

**A:**
- Strong consistency for financial data (2PC or Saga pattern)
- Eventual consistency for non-critical data
- Distributed locks for balance updates
- Idempotent operations
- Event sourcing for audit trail

---

## High-Level Design (HLD)

### System Overview

PayPal follows a microservices architecture optimized for financial transactions:

1. **Client Layer**: Web, mobile apps, merchant SDKs
2. **API Gateway**: Authentication, rate limiting, routing
3. **Core Services**: Payment, wallet, fraud detection, transaction services
4. **Data Layer**: PostgreSQL for transactions, Cassandra for audit logs
5. **External Services**: Banking networks, card networks, currency exchange

### Service Decomposition

**Core Services:**
- **Payment Service**: Payment processing, authorization, capture
- **Wallet Service**: Balance management, currency conversion
- **Fraud Detection Service**: Real-time risk scoring, pattern detection
- **Transaction Service**: Transaction lifecycle, history, reporting
- **Merchant Service**: Merchant integration, webhooks, settlements

---

## Low-Level Design (LLD)

### Payment Processing Implementation

```python
class PaymentService:
    def __init__(self, wallet_service, fraud_service, transaction_service):
        self.wallet = wallet_service
        self.fraud = fraud_service
        self.transaction = transaction_service
    
    def process_payment(self, payment_request: dict) -> dict:
        # Fraud check
        fraud_score = self.fraud.assess_risk(payment_request)
        if fraud_score > 70:
            return {'success': False, 'reason': 'fraud_detected', 'fraud_score': fraud_score}
        
        # Create transaction
        transaction = self.transaction.create_transaction(payment_request)
        
        # Process payment based on method
        if payment_request['payment_method'] == 'PAYPAL_BALANCE':
            result = self.process_wallet_payment(transaction)
        elif payment_request['payment_method'] in ['CREDIT_CARD', 'DEBIT_CARD']:
            result = self.process_card_payment(transaction)
        else:
            result = self.process_bank_payment(transaction)
        
        # Update transaction status
        self.transaction.update_status(transaction.id, result['status'])
        
        return result
    
    def process_wallet_payment(self, transaction: dict) -> dict:
        # Acquire locks
        payer_lock = self.acquire_lock(f"wallet:{transaction.payer_id}")
        payee_lock = self.acquire_lock(f"wallet:{transaction.payee_id}")
        
        try:
            # Check balance
            balance = self.wallet.get_balance(transaction.payer_id, transaction.currency)
            if balance < transaction.amount:
                return {'success': False, 'reason': 'insufficient_funds'}
            
            # Transfer funds (atomic)
            self.wallet.transfer(
                transaction.payer_id,
                transaction.payee_id,
                transaction.amount,
                transaction.currency
            )
            
            return {'success': True, 'status': 'completed'}
        finally:
            self.release_lock(payer_lock)
            self.release_lock(payee_lock)
```

### Fraud Detection Implementation

```python
class FraudDetectionService:
    def __init__(self, ml_client, rule_engine):
        self.ml = ml_client
        self.rules = rule_engine
    
    def assess_risk(self, transaction: dict) -> float:
        # Rule-based scoring
        rule_score = self.rules.evaluate(transaction)
        
        # ML-based scoring
        ml_score = self.ml.score(transaction)
        
        # Combined score
        risk_score = (rule_score * 0.4) + (ml_score * 0.6)
        
        return risk_score
```

---

## Fault Tolerance

### Payment Service Resilience

**Idempotency:**
- Idempotency keys for all payments
- Prevent duplicate processing
- Store idempotency keys in Redis

**Transaction Safety:**
- Distributed transactions (2PC or Saga)
- Rollback on failure
- Compensating transactions

### Database Resilience

**Replication:**
- PostgreSQL primary-replica setup
- Synchronous replication for critical data
- Automatic failover

---

## Optimizations

### Caching Strategy

**Balance Cache:**
- Cache wallet balances
- TTL: 5 minutes
- Invalidate on update

**Exchange Rate Cache:**
- Cache exchange rates
- TTL: 5 minutes
- Reduce API calls

### Database Optimization

**Indexing:**
- Index on transaction fields
- Partition by time
- Optimize queries

---

## Failure Safety

### Payment Failure

**Scenario: Payment Processing Fails**
- **Impact**: Payment not completed
- **Mitigation**:
  - Retry with exponential backoff
  - Idempotent operations
  - Compensating transactions
- **Recovery**:
  - Retry payment
  - Verify transaction status
  - Notify user

### Fraud Detection Failure

**Scenario: Fraud Service Unavailable**
- **Impact**: Cannot assess risk
- **Mitigation**:
  - Fallback to rule-based scoring
  - Queue for manual review
  - Allow with monitoring
- **Recovery**:
  - Service recovers
  - Process queued transactions
  - Verify fraud scores

---

## Scalability

### Horizontal Scaling

**Service Scaling:**
- Stateless service instances
- Load balancer distributes requests
- Scale independently

**Database Scaling:**
- Sharding by user_id
- Read replicas
- Partition transactions by time

### Performance Scaling

**Throughput Scaling:**
- Increase service instances
- Optimize database queries
- Use caching

**Latency Optimization:**
- Reduce database queries
- Cache frequently accessed data
- Optimize payment processing

---

## Conclusion

This system design for PayPal covers the essential components needed to build a scalable, secure, and reliable payment processing platform. Key highlights:

1. **Scalability**: Horizontal scaling, database sharding, caching
2. **Security**: PCI DSS compliance, encryption, fraud detection
3. **Reliability**: Strong consistency, fault tolerance, disaster recovery
4. **Performance**: Low latency, high throughput, efficient caching
5. **Compliance**: Regulatory requirements, audit logging, KYC

The design prioritizes data accuracy and security while maintaining high availability and performance. Trade-offs are made thoughtfully, with strong consistency for financial data and eventual consistency for non-critical operations.

---

**Document Version**: 1.0  
**Last Updated**: January 2024  
**Author**: System Design Team

