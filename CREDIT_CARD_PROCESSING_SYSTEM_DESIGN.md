# Credit Card Processing System Design

## Table of Contents
1. [Overview](#overview)
2. [Requirements](#requirements)
3. [System Architecture](#system-architecture)
4. [Database Design](#database-design)
5. [API Design](#api-design)
6. [Payment Flow](#payment-flow)
7. [Tokenization](#tokenization)
8. [Fraud Detection](#fraud-detection)
9. [PCI-DSS Compliance](#pci-dss-compliance)
10. [Scalability Considerations](#scalability-considerations)
11. [Optimizations](#optimizations)
12. [Caching Strategy](#caching-strategy)
13. [Load Balancing](#load-balancing)
14. [Security](#security)
15. [Monitoring & Analytics](#monitoring--analytics)
16. [Deployment Strategy](#deployment-strategy)
17. [Capacity Planning](#capacity-planning)
18. [Technology Stack](#technology-stack)
19. [Failure Scenarios & Handling](#failure-scenarios--handling)
20. [Trade-offs & Design Decisions](#trade-offs--design-decisions)
21. [Interview Discussion Points](#interview-discussion-points)

---

## Overview

A secure credit card processing system that handles payment transactions, tokenization, fraud detection, and PCI-DSS compliance. The system must process millions of transactions securely, prevent fraud, and ensure regulatory compliance.

**Key Features:**
- Payment processing (authorization, capture, refund)
- Tokenization (PCI compliance)
- Fraud detection
- Multi-gateway support
- Payment method storage
- Recurring payments
- 3D Secure authentication
- Chargeback management

---

## Requirements

### Functional Requirements

1. **Payment Processing**
   - Authorize payments
   - Capture authorized payments
   - Refund payments
   - Void transactions
   - Partial refunds

2. **Tokenization**
   - Convert card to token
   - Store tokens securely
   - Detokenize for processing
   - Token lifecycle management

3. **Payment Methods**
   - Store payment methods
   - Update payment methods
   - Delete payment methods
   - Set default payment method

4. **Fraud Detection**
   - Real-time fraud scoring
   - Risk assessment
   - Block suspicious transactions
   - Manual review queue

5. **3D Secure**
   - 3DS authentication
   - Challenge flow
   - Authentication result handling

6. **Recurring Payments**
   - Setup recurring payments
   - Process scheduled payments
   - Update payment methods
   - Cancel subscriptions

### Non-Functional Requirements

1. **Security**
   - PCI-DSS Level 1 compliance
   - End-to-end encryption
   - No card data storage
   - Secure tokenization

2. **Performance**
   - Authorization: < 2 seconds
   - Tokenization: < 100ms
   - Fraud check: < 500ms
   - 99th percentile latency < 3s

3. **Availability**
   - 99.99% uptime
   - Multi-gateway failover
   - Zero data loss
   - Automatic failover

4. **Scalability**
   - Handle 10M+ transactions/day
   - Support multiple payment gateways
   - Horizontal scaling

---

## System Architecture

### High-Level Design (HLD)

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Merchant Applications                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │Merchant 1│  │Merchant 2│  │Merchant 3│  │Merchant N│   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼───────────┘
        │             │             │             │
        └─────────────┴─────────────┴─────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│              API Gateway (PCI-Compliant)                    │
│              (Tokenization, Encryption)                       │
└───────────────────────────┬─────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Region 1   │  │   Region 2   │  │   Region N   │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                  │
       ▼                 ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│              Payment Processing Services                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │Payment   │  │Tokenization│ │  Fraud   │  │ 3D Secure│   │
│  │Service   │  │ Service  │  │ Detection│  │ Service  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │Recurring│  │Chargeback│  │Reporting │  │Notification│ │
│  │ Service │  │ Service  │  │ Service  │  │ Service  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼───────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│              Payment Gateway Layer                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Stripe   │  │  PayPal  │  │  Square  │  │  Adyen   │   │
│  │ Gateway  │  │ Gateway  │  │ Gateway  │  │ Gateway  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼───────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│              Database Layer                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │PostgreSQL│  │PostgreSQL│  │  Redis   │  │  Kafka   │   │
│  │(Tokens)  │  │(Transactions)│ │(Cache)  │  │(Events)  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### HLD Component Breakdown

**1. API Gateway Layer**
- **Tokenization Gateway**: Handles card tokenization requests
- **Payment Gateway**: Routes payment requests
- **Rate Limiting**: Prevents abuse
- **Authentication**: Validates API keys

**2. Core Services Layer**
- **Tokenization Service**: Converts cards to tokens, manages token vault
- **Payment Service**: Processes payments, manages transaction lifecycle
- **Fraud Detection Service**: Real-time fraud scoring and risk assessment
- **3D Secure Service**: Handles 3DS authentication flows

**3. Gateway Layer**
- **Gateway Adapter**: Abstracts payment gateway differences
- **Gateway Router**: Routes to appropriate gateway
- **Gateway Failover**: Handles gateway failures

**4. Data Layer**
- **Transaction DB**: Stores transaction records
- **Token Vault**: Encrypted storage for card data
- **Cache**: Caches payment methods and fraud scores
- **Event Stream**: Publishes payment events

### Component Details

#### 1. Tokenization Service
- **Responsibilities**:
  - Convert card to token
  - Store tokens securely
  - Detokenize for processing
  - Token lifecycle management

#### 2. Payment Service
- **Responsibilities**:
  - Process payments
  - Route to payment gateways
  - Handle responses
  - Manage transaction state

#### 3. Fraud Detection Service
- **Responsibilities**:
  - Real-time fraud scoring
  - Risk assessment
   - Block suspicious transactions
   - ML-based detection

#### 4. 3D Secure Service
- **Responsibilities**:
  - Handle 3DS authentication
  - Challenge flow
  - Result processing

---

## Database Design

### PostgreSQL Schema

#### Payment Methods Table
```sql
CREATE TABLE payment_methods (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    token VARCHAR(255) UNIQUE NOT NULL,  -- Payment token (not card number)
    type VARCHAR(50) NOT NULL,  -- 'card', 'paypal', etc.
    last_four_digits VARCHAR(4),
    expiry_month INT,
    expiry_year INT,
    card_brand VARCHAR(50),  -- 'visa', 'mastercard', etc.
    is_default BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_user_id (user_id),
    INDEX idx_token (token)
) ENGINE=InnoDB;
```

#### Transactions Table
```sql
CREATE TABLE transactions (
    id BIGSERIAL PRIMARY KEY,
    transaction_id VARCHAR(255) UNIQUE NOT NULL,
    merchant_id BIGINT NOT NULL,
    user_id BIGINT,
    payment_method_id BIGINT,
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(50) NOT NULL,  -- 'pending', 'authorized', 'captured', 'failed', 'refunded'
    payment_gateway VARCHAR(50),  -- 'stripe', 'paypal', etc.
    gateway_transaction_id VARCHAR(255),
    fraud_score DECIMAL(5, 2),
    fraud_status VARCHAR(50),  -- 'approved', 'review', 'rejected'
    three_ds_status VARCHAR(50),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (merchant_id) REFERENCES merchants(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (payment_method_id) REFERENCES payment_methods(id),
    INDEX idx_merchant_id (merchant_id),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB;
```

#### Token Vault Table (Encrypted)
```sql
CREATE TABLE token_vault (
    id BIGSERIAL PRIMARY KEY,
    token VARCHAR(255) UNIQUE NOT NULL,
    encrypted_card_data BYTEA NOT NULL,  -- Encrypted card data
    encryption_key_id VARCHAR(255),  -- Key management reference
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    INDEX idx_token (token),
    INDEX idx_expires_at (expires_at)
) ENGINE=InnoDB;
```

---

## API Design

### Payment APIs

**Create Payment**
```
POST /api/v1/payments
Content-Type: application/json

Request:
{
    "amount": 100.00,
    "currency": "USD",
    "payment_method_token": "tok_visa_1234",
    "merchant_id": "merchant_123",
    "description": "Order #12345"
}

Response:
{
    "success": true,
    "transaction_id": "txn_abc123",
    "status": "authorized",
    "amount": 100.00,
    "currency": "USD",
    "fraud_score": 0.15,
    "fraud_status": "approved"
}
```

**Capture Payment**
```
POST /api/v1/payments/{transaction_id}/capture
Content-Type: application/json

Request:
{
    "amount": 100.00  // Optional, for partial capture
}

Response:
{
    "success": true,
    "transaction_id": "txn_abc123",
    "status": "captured",
    "captured_amount": 100.00
}
```

**Refund Payment**
```
POST /api/v1/payments/{transaction_id}/refund
Content-Type: application/json

Request:
{
    "amount": 50.00,  // Optional, for partial refund
    "reason": "customer_request"
}

Response:
{
    "success": true,
    "refund_id": "refund_xyz789",
    "refunded_amount": 50.00,
    "remaining_amount": 50.00
}
```

### Tokenization APIs

**Create Token**
```
POST /api/v1/tokens
Content-Type: application/json

Request:
{
    "card_number": "4111111111111111",
    "expiry_month": 12,
    "expiry_year": 2025,
    "cvv": "123",
    "cardholder_name": "John Doe"
}

Response:
{
    "success": true,
    "token": "tok_visa_1234",
    "last_four": "1111",
    "card_brand": "visa",
    "expires_at": "2025-12-31T23:59:59Z"
}
```

---

## Payment Flow

### Authorization Flow

```
Merchant Requests Payment
    │
    ▼
Payment Service
    │
    ├─ Validate Request
    ├─ Get Payment Method Token
    │
    ▼
Fraud Detection Service
    │
    ├─ Calculate Fraud Score
    ├─ Check Risk Rules
    │
    ├─ If High Risk → Reject or Review
    │
    └─ If Low Risk → Continue
        │
        ▼
    3D Secure Service (If Required)
        │
        ├─ Check if 3DS Required
        ├─ Initiate Authentication
        └─ Handle Challenge Flow
        │
        ▼
    Payment Gateway (Stripe/PayPal)
        │
        ├─ Authorize Payment
        ├─ Return Authorization Result
        │
        ▼
    Payment Service
        │
        ├─ Record Transaction
        ├─ Update Status
        └─ Publish Event (Kafka)
        │
        ▼
    Return Result to Merchant
```

### Tokenization Flow

```
Card Data Received
    │
    ▼
Tokenization Service
    │
    ├─ Validate Card Data
    ├─ Encrypt Card Data
    │   │
    │   └─ Use Encryption Key (KMS)
    │
    ├─ Generate Token
    │   │
    │   └─ Random, Unique Token
    │
    ├─ Store in Token Vault
    │   │
    │   └─ token → encrypted_card_data
    │
    └─ Return Token to Merchant
        │
        └─ Never return card data
```

---

## Tokenization

### Token Generation

**Requirements:**
- Unique tokens
- Non-guessable
- No card data in token
- Secure storage

**Implementation:**
```python
class TokenizationService:
    def create_token(self, card_data):
        # Validate card
        if not self.validate_card(card_data):
            raise InvalidCardError()
        
        # Encrypt card data
        encrypted_data = self.encrypt_card_data(card_data)
        
        # Generate token
        token = self.generate_unique_token()
        
        # Store in vault
        self.token_vault.store(token, encrypted_data)
        
        # Return token (never card data)
        return {
            'token': token,
            'last_four': card_data['card_number'][-4:],
            'card_brand': self.detect_card_brand(card_data['card_number']),
            'expires_at': self.calculate_expiry()
        }
    
    def detokenize(self, token):
        # Get encrypted data from vault
        encrypted_data = self.token_vault.get(token)
        
        if not encrypted_data:
            raise TokenNotFoundError()
        
        # Decrypt card data
        card_data = self.decrypt_card_data(encrypted_data)
        
        return card_data
```

---

## Fraud Detection

### Fraud Detection Pipeline

```
Transaction Received
    │
    ▼
Fraud Detection Service
    │
    ├─ Feature Extraction
    │   ├─ Transaction amount
    │   ├─ User history
    │   ├─ Device fingerprint
    │   ├─ IP geolocation
    │   └─ Behavioral patterns
    │
    ▼
ML Model Scoring
    │
    ├─ Real-time Model
    │   └─ Fast, lightweight
    │
    └─ Deep Learning Model (Async)
        └─ More accurate, slower
    │
    ▼
Risk Rules Engine
    │
    ├─ Rule-based Checks
    │   ├─ Velocity checks
    │   ├─ Amount thresholds
    │   └─ Geographic checks
    │
    ▼
Final Decision
    │
    ├─ Score < 0.3 → Approve
    ├─ Score 0.3-0.7 → Review
    └─ Score > 0.7 → Reject
```

---

## PCI-DSS Compliance

### Compliance Requirements

1. **No Card Data Storage**
   - Never store raw card numbers
   - Use tokenization
   - Encrypt if storage needed

2. **Encryption**
   - Encrypt data in transit (TLS 1.3)
   - Encrypt data at rest (AES-256)
   - Key management (HSM/KMS)

3. **Access Control**
   - Least privilege access
   - Audit logging
   - Multi-factor authentication

4. **Network Security**
   - Firewall rules
   - Network segmentation
   - Intrusion detection

---

## Low-Level Design (LLD)

### Payment Service LLD

```python
class PaymentService:
    def __init__(self, config: dict):
        self.tokenization_service = TokenizationService(config.tokenization)
        self.fraud_service = FraudDetectionService(config.fraud)
        self.three_ds_service = ThreeDSecureService(config.three_ds)
        self.gateway_router = GatewayRouter(config.gateways)
        self.transaction_store = TransactionStore()
        self.event_publisher = EventPublisher(config.kafka)
        self.cache = RedisCache()
        self.idempotency_store = IdempotencyStore()
    
    def process_payment(self, request: PaymentRequest) -> PaymentResponse:
        # Check idempotency
        idempotency_key = request.idempotency_key
        if idempotency_key:
            cached_response = self.idempotency_store.get(idempotency_key)
            if cached_response:
                return cached_response
        
        # Create transaction record
        transaction = self._create_transaction(request)
        
        try:
            # Step 1: Detokenize payment method
            card_data = self.tokenization_service.detokenize(request.payment_method_token)
            
            # Step 2: Fraud detection
            fraud_result = self.fraud_service.check_fraud(transaction, card_data)
            
            if fraud_result.status == 'rejected':
                transaction.status = 'failed'
                transaction.failure_reason = 'fraud_detected'
                self.transaction_store.save(transaction)
                return PaymentResponse(success=False, transaction_id=transaction.id)
            
            # Step 3: 3D Secure (if required)
            if self._requires_3ds(transaction, fraud_result):
                three_ds_result = self.three_ds_service.authenticate(transaction, card_data)
                if not three_ds_result.success:
                    transaction.status = 'failed'
                    transaction.failure_reason = '3ds_failed'
                    self.transaction_store.save(transaction)
                    return PaymentResponse(success=False, transaction_id=transaction.id)
            
            # Step 4: Process payment with gateway
            gateway_response = self.gateway_router.process(transaction, card_data)
            
            # Step 5: Update transaction
            transaction.status = gateway_response.status
            transaction.gateway_transaction_id = gateway_response.gateway_id
            transaction.fraud_score = fraud_result.score
            self.transaction_store.save(transaction)
            
            # Step 6: Publish event
            self.event_publisher.publish('payment.processed', transaction)
            
            # Step 7: Cache idempotency
            if idempotency_key:
                self.idempotency_store.set(idempotency_key, gateway_response, ttl=3600)
            
            return PaymentResponse(
                success=gateway_response.success,
                transaction_id=transaction.id,
                status=transaction.status
            )
        
        except Exception as e:
            logger.error(f"Error processing payment: {e}")
            transaction.status = 'failed'
            transaction.failure_reason = str(e)
            self.transaction_store.save(transaction)
            raise
```

### Tokenization Service LLD

```python
class TokenizationService:
    def __init__(self, config: dict):
        self.token_vault = TokenVault(config.vault_config)
        self.encryption_service = EncryptionService(config.encryption)
        self.key_manager = KeyManager(config.kms)
        self.token_generator = TokenGenerator()
        self.cache = RedisCache()
    
    def create_token(self, card_data: dict) -> TokenResponse:
        # Validate card data
        if not self._validate_card(card_data):
            raise InvalidCardError()
        
        # Encrypt card data
        encryption_key_id = self.key_manager.get_current_key_id()
        encrypted_data = self.encryption_service.encrypt(
            card_data,
            key_id=encryption_key_id
        )
        
        # Generate unique token
        token = self.token_generator.generate()
        
        # Store in vault
        self.token_vault.store(
            token=token,
            encrypted_data=encrypted_data,
            encryption_key_id=encryption_key_id,
            metadata={
                'last_four': card_data['card_number'][-4:],
                'card_brand': self._detect_brand(card_data['card_number']),
                'expiry_month': card_data['expiry_month'],
                'expiry_year': card_data['expiry_year']
            }
        )
        
        # Cache token metadata
        self.cache.set(
            f"token:{token}",
            {
                'last_four': card_data['card_number'][-4:],
                'card_brand': self._detect_brand(card_data['card_number'])
            },
            ttl=86400  # 24 hours
        )
        
        return TokenResponse(
            token=token,
            last_four=card_data['card_number'][-4:],
            card_brand=self._detect_brand(card_data['card_number']),
            expires_at=self._calculate_expiry()
        )
    
    def detokenize(self, token: str) -> dict:
        # Check cache first
        cached = self.cache.get(f"token:{token}")
        if cached:
            # Still need to get full card data from vault
            pass
        
        # Get from vault
        vault_entry = self.token_vault.get(token)
        if not vault_entry:
            raise TokenNotFoundError()
        
        # Decrypt card data
        card_data = self.encryption_service.decrypt(
            vault_entry['encrypted_data'],
            key_id=vault_entry['encryption_key_id']
        )
        
        return card_data
```

### Fraud Detection Service LLD

```python
class FraudDetectionService:
    def __init__(self, config: dict):
        self.ml_model = FraudMLModel(config.model_path)
        self.rule_engine = RuleEngine(config.rules)
        self.feature_extractor = FeatureExtractor()
        self.cache = RedisCache()
        self.history_store = TransactionHistoryStore()
    
    def check_fraud(self, transaction: Transaction, card_data: dict) -> FraudResult:
        # Extract features
        features = self.feature_extractor.extract(transaction, card_data)
        
        # Check cache
        cache_key = self._generate_cache_key(features)
        cached_result = self.cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Get transaction history
        history = self.history_store.get_history(
            user_id=transaction.user_id,
            card_last_four=card_data['card_number'][-4:],
            hours=24
        )
        
        # Add history features
        features.update(self._extract_history_features(history))
        
        # ML model scoring
        ml_score = self.ml_model.predict(features)
        
        # Rule-based checks
        rule_result = self.rule_engine.evaluate(transaction, features)
        
        # Combine results
        final_score = self._combine_scores(ml_score, rule_result)
        
        # Determine status
        if final_score < 0.3:
            status = 'approved'
        elif final_score < 0.7:
            status = 'review'
        else:
            status = 'rejected'
        
        result = FraudResult(
            score=final_score,
            status=status,
            ml_score=ml_score,
            rule_result=rule_result
        )
        
        # Cache result
        self.cache.set(cache_key, result, ttl=300)  # 5 minutes
        
        return result
```

### Gateway Router LLD

```python
class GatewayRouter:
    def __init__(self, config: dict):
        self.gateways = {
            'stripe': StripeGateway(config.stripe),
            'paypal': PayPalGateway(config.paypal),
            'square': SquareGateway(config.square)
        }
        self.routing_rules = RoutingRules(config.routing)
        self.circuit_breakers = {
            name: CircuitBreaker(failure_threshold=5, timeout=60)
            for name in self.gateways.keys()
        }
        self.health_monitor = GatewayHealthMonitor()
    
    def process(self, transaction: Transaction, card_data: dict) -> GatewayResponse:
        # Select gateway
        gateway_name = self.routing_rules.select_gateway(transaction)
        gateway = self.gateways[gateway_name]
        
        # Check circuit breaker
        if self.circuit_breakers[gateway_name].is_open():
            # Try fallback gateway
            gateway_name = self._get_fallback_gateway(gateway_name)
            gateway = self.gateways[gateway_name]
        
        # Process with gateway
        try:
            response = self.circuit_breakers[gateway_name].call(
                gateway.authorize,
                transaction,
                card_data
            )
            
            # Update health
            self.health_monitor.record_success(gateway_name)
            
            return response
        
        except GatewayError as e:
            # Update health
            self.health_monitor.record_failure(gateway_name)
            
            # Try fallback
            if gateway_name != self._get_fallback_gateway(gateway_name):
                return self.process(transaction, card_data)  # Retry with fallback
            
            raise
```

## Scalability Considerations

### 1. Horizontal Scaling

**Payment Services:**
- **Stateless Design**: No shared state between instances
- **Load Balancer**: Distributes traffic across instances
- **Auto-Scaling**: Scale based on request rate
- **Container Orchestration**: Kubernetes for deployment
- **Scaling**: Add instances as traffic increases

**Tokenization Service:**
- **Stateless**: Token vault is external
- **Connection Pooling**: Pool database connections
- **Caching**: Cache token metadata
- **Scaling**: Scale independently based on tokenization load

**Fraud Detection Service:**
- **Model Serving**: Deploy ML models on separate servers
- **Batch Processing**: Process fraud checks in batches
- **Caching**: Cache fraud scores
- **Scaling**: Scale based on transaction volume

### 2. Database Scaling

**Transaction Database:**
- **Sharding**: Shard by merchant_id or transaction_id
- **Read Replicas**: Deploy read replicas for queries
- **Partitioning**: Partition by date for old transactions
- **Caching**: Cache recent transactions

**Token Vault:**
- **Encryption**: Encrypt at application level
- **Sharding**: Shard by token hash
- **Replication**: Replicate for high availability
- **Backup**: Regular encrypted backups

### 3. Gateway Failover

**Multi-Gateway Support:**
- **Primary Gateway**: Stripe (primary)
- **Secondary Gateway**: PayPal (fallback)
- **Tertiary Gateway**: Square (last resort)
- **Automatic Failover**: Switch on failure
- **Load Balancing**: Distribute load across gateways
- **Health Monitoring**: Monitor gateway health
- **Circuit Breaker**: Prevent cascading failures

### 4. Caching Strategy

**Cache Layers:**
- **L1 Cache**: In-memory cache (Redis)
- **L2 Cache**: Application cache
- **Cache Invalidation**: Invalidate on updates
- **Cache Warming**: Pre-warm frequently accessed data

**Cached Data:**
- Payment method tokens
- Fraud scores
- Gateway responses
- Merchant configurations

### 5. Message Queue Scaling

**Event Streaming:**
- **Kafka**: High-throughput event streaming
- **Partitioning**: Partition by transaction_id
- **Consumer Groups**: Parallel processing
- **Replication**: Replicate for durability

---

## Optimizations

### Performance Optimizations

#### 1. Payment Processing Optimization

**Batch Processing:**

```python
class BatchPaymentProcessor:
    def __init__(self, batch_size: int = 100, flush_interval: float = 1.0):
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.batch = []
        self.last_flush = time.time()
    
    async def process_payment_batched(self, payment: Payment):
        self.batch.append(payment)
        
        if len(self.batch) >= self.batch_size:
            await self.flush()
        elif time.time() - self.last_flush > self.flush_interval:
            await self.flush()
    
    async def flush(self):
        if not self.batch:
            return
        
        # Process batch in parallel
        tasks = [self.process_single_payment(p) for p in self.batch]
        await asyncio.gather(*tasks)
        
        self.batch.clear()
        self.last_flush = time.time()
```

**Connection Pooling:**

```python
class PaymentConnectionPool:
    def __init__(self, max_connections: int = 50):
        self.pool = asyncio.Queue(maxsize=max_connections)
        self.connections = set()
    
    async def get_connection(self):
        if not self.pool.empty():
            return await self.pool.get()
        
        conn = await self.create_payment_gateway_connection()
        self.connections.add(conn)
        return conn
    
    async def return_connection(self, conn):
        await self.pool.put(conn)
```

#### 2. Tokenization Optimization

**Token Cache:**

```python
class TokenCacheOptimizer:
    def __init__(self):
        self.cache = LRUCache(max_size=100000, ttl=3600)
    
    async def tokenize_with_cache(self, card_data: str) -> str:
        # Check cache first
        cache_key = hashlib.sha256(card_data.encode()).hexdigest()
        cached_token = self.cache.get(cache_key)
        if cached_token:
            return cached_token
        
        # Tokenize
        token = await self.tokenize(card_data)
        
        # Cache token
        self.cache.set(cache_key, token)
        
        return token
```

#### 3. Fraud Detection Optimization

**Model Caching:**

```python
class FraudModelCache:
    def __init__(self):
        self.model_cache = {}
        self.score_cache = LRUCache(max_size=10000, ttl=300)
    
    async def detect_fraud_cached(self, transaction: dict) -> float:
        # Cache fraud scores for similar transactions
        cache_key = self.get_transaction_signature(transaction)
        cached_score = self.score_cache.get(cache_key)
        if cached_score:
            return cached_score
        
        # Run fraud detection
        score = await self.run_fraud_detection(transaction)
        
        # Cache score
        self.score_cache.set(cache_key, score)
        
        return score
```

---

## Caching Strategy

### Cache Architecture

```
Payment Request
    │
    ▼
Redis Cache
    │
    ├─ Cache Payment Method (Tokens)
    ├─ Cache Fraud Scores
    └─ Cache Gateway Responses
```

### Cache Keys

```
payment_method:{token} → Payment method data
fraud_score:{transaction_id} → Fraud score
gateway_response:{transaction_id} → Gateway response
```

---

## Security

### 1. Encryption

**Encryption in Transit:**
- TLS 1.3 for all communications
- Certificate pinning

**Encryption at Rest:**
- AES-256 encryption
- Key management (AWS KMS, HSM)

### 2. Token Security

**Token Requirements:**
- Cryptographically secure random
- No card data in token
- Token rotation
- Expiration

---

## Monitoring & Analytics

### Key Metrics

**Performance Metrics:**
- Payment latency
- Authorization success rate
- Fraud detection latency

**Business Metrics:**
- Transaction volume
- Success rate
- Fraud rate
- Chargeback rate

---

## Deployment Strategy

### Infrastructure

**Cloud Provider**: AWS, GCP, or Azure

**Components:**
- **Compute**: Kubernetes (EKS/GKE)
- **Database**: PostgreSQL (RDS)
- **Cache**: Redis (ElastiCache)
- **Key Management**: AWS KMS or HSM

---

## Capacity Planning

### Storage Estimates

**Transactions:**
- 10M transactions/day × 365 days = 3.65B transactions/year
- 3.65B × 1 KB = 3.65 TB/year

**Tokens:**
- 100M active tokens × 500 bytes = 50 GB

**Total Storage: ~3.7 TB/year**

### Compute Requirements

**Payment Services:**
- 10M transactions/day = 116 transactions/sec average
- Peak: 116 × 10 = 1,160 transactions/sec
- Each transaction: ~1 second (with fraud check)
- Required servers: 1,160 servers
- With caching: **580 servers**

---

## Technology Stack

### Recommended Stack

**Compute:**
- **Language**: Java or Go
- **Orchestration**: Kubernetes

**Database:**
- **PostgreSQL** (RDS)

**Cache:**
- **Redis** (ElastiCache)

**Payment Gateways:**
- **Stripe**, **PayPal**, **Square**

**Key Management:**
- **AWS KMS** or **HSM**

---

## Fault Tolerance

### Payment Service Fault Tolerance

**1. Idempotency**
```python
class IdempotencyStore:
    def __init__(self, redis: RedisClient):
        self.redis = redis
    
    def get(self, idempotency_key: str) -> Optional[PaymentResponse]:
        key = f"idempotency:{idempotency_key}"
        cached = self.redis.get(key)
        if cached:
            return json.loads(cached)
        return None
    
    def set(self, idempotency_key: str, response: PaymentResponse, ttl: int = 3600):
        key = f"idempotency:{idempotency_key}"
        self.redis.setex(key, ttl, json.dumps(response))
```

**2. Transaction State Management**
- **State Machine**: Use state machine for transaction states
- **State Persistence**: Persist state at each step
- **State Recovery**: Recover from saved state on failure
- **Compensation**: Rollback on failure

**3. Retry Logic**
```python
class RetryHandler:
    def __init__(self, max_retries: int = 3, backoff_factor: float = 2.0):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
    
    def execute(self, func, *args, **kwargs):
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except RetryableError as e:
                if attempt == self.max_retries - 1:
                    raise
                wait_time = self.backoff_factor ** attempt
                time.sleep(wait_time)
            except NonRetryableError:
                raise
```

### Gateway Fault Tolerance

**1. Circuit Breaker Pattern**
```python
class GatewayCircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'closed'  # closed, open, half_open
    
    def call(self, gateway_func, *args, **kwargs):
        if self.state == 'open':
            if time.time() - self.last_failure_time > self.timeout:
                self.state = 'half_open'
            else:
                raise CircuitBreakerOpenError()
        
        try:
            result = gateway_func(*args, **kwargs)
            self._on_success()
            return result
        except GatewayError as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        self.failure_count = 0
        self.state = 'closed'
    
    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = 'open'
```

**2. Gateway Failover**
```python
class GatewayFailover:
    def __init__(self, gateways: list):
        self.gateways = gateways  # Ordered by priority
        self.current_gateway = 0
        self.circuit_breakers = {
            name: GatewayCircuitBreaker()
            for name in self.gateways
        }
    
    def process(self, transaction: Transaction, card_data: dict):
        for i, gateway_name in enumerate(self.gateways):
            gateway = self.gateways[gateway_name]
            circuit_breaker = self.circuit_breakers[gateway_name]
            
            if circuit_breaker.is_open():
                continue
            
            try:
                return circuit_breaker.call(
                    gateway.authorize,
                    transaction,
                    card_data
                )
            except GatewayError:
                if i < len(self.gateways) - 1:
                    continue  # Try next gateway
                raise AllGatewaysFailedError()
```

**3. Gateway Health Monitoring**
- **Health Checks**: Periodic health checks
- **Response Time Monitoring**: Monitor response times
- **Error Rate Monitoring**: Track error rates
- **Automatic Failover**: Switch on health degradation

### Tokenization Fault Tolerance

**1. Token Vault Redundancy**
```python
class TokenVault:
    def __init__(self, config: dict):
        self.primary_db = PostgreSQLClient(config.primary)
        self.replica_db = PostgreSQLClient(config.replica)
        self.backup_storage = S3Client(config.backup)
    
    def store(self, token: str, encrypted_data: bytes, **kwargs):
        # Write to primary
        try:
            self.primary_db.insert('token_vault', {
                'token': token,
                'encrypted_data': encrypted_data,
                **kwargs
            })
        except Exception as e:
            logger.error(f"Error writing to primary: {e}")
            raise
    
    def get(self, token: str):
        # Try primary first
        try:
            return self.primary_db.query(
                "SELECT * FROM token_vault WHERE token = %s",
                (token,)
            )
        except Exception:
            # Fallback to replica
            return self.replica_db.query(
                "SELECT * FROM token_vault WHERE token = %s",
                (token,)
            )
```

**2. Encryption Key Management**
- **Key Rotation**: Rotate encryption keys periodically
- **Key Backup**: Backup encryption keys securely
- **Key Recovery**: Recover keys from backup
- **HSM Integration**: Use HSM for key storage

**3. Token Expiration**
- **Token TTL**: Set expiration on tokens
- **Token Refresh**: Refresh tokens before expiration
- **Token Cleanup**: Clean up expired tokens

### Fraud Detection Fault Tolerance

**1. Fallback Strategies**
```python
class FraudDetectionService:
    def check_fraud(self, transaction: Transaction, card_data: dict):
        try:
            # Try ML model
            return self.ml_model.predict(transaction, card_data)
        except MLModelError:
            # Fallback to rule-based
            return self.rule_engine.evaluate(transaction, card_data)
        except Exception:
            # Fallback to cached score
            cached = self.cache.get(f"fraud:{transaction.id}")
            if cached:
                return cached
            
            # Default: approve low-risk transactions
            return FraudResult(score=0.2, status='approved')
```

**2. Model Serving Redundancy**
- **Multiple Model Servers**: Deploy multiple model servers
- **Load Balancing**: Distribute requests
- **Model Versioning**: Support multiple model versions
- **Fallback Models**: Use simpler models as fallback

**3. Feature Store Resilience**
- **Feature Caching**: Cache computed features
- **Feature Fallback**: Use default values on failure
- **Feature Store Replication**: Replicate feature store

## Failure Safety

### Failure Scenarios & Handling

### 1. Payment Gateway Failure

**Scenario:** All payment gateways fail.

**Impact:** Cannot process payments.

**Mitigation:**
- **Multi-Gateway**: Failover to secondary/tertiary gateways
- **Retry Logic**: Retry with exponential backoff
- **Queue**: Queue payments, process when gateway recovers
- **Circuit Breaker**: Prevent cascading failures
- **Health Monitoring**: Monitor gateway health
- **Graceful Degradation**: Return clear error messages

**Recovery:**
- **Automatic Retry**: Retry queued payments when gateway recovers
- **Notification**: Notify operations team
- **Manual Intervention**: Manual processing if needed

### 2. Fraud Detection Failure

**Scenario:** Fraud detection service fails.

**Impact:** Cannot assess risk.

**Mitigation:**
- **Fallback**: Use cached fraud scores
- **Default Strategy**: Approve low-risk transactions (< $100)
- **Manual Review**: Flag high-value transactions for review
- **Rule-Based Fallback**: Use rule-based checks
- **Service Redundancy**: Deploy multiple fraud detection instances

**Recovery:**
- **Service Restart**: Automatically restart service
- **Model Reload**: Reload ML models
- **Feature Store Recovery**: Recover feature store

### 3. Token Vault Failure

**Scenario:** Token vault database fails.

**Impact:** Cannot detokenize tokens.

**Mitigation:**
- **Replication**: Database replication with automatic failover
- **Backup**: Daily encrypted backups
- **Read Replicas**: Serve from read replicas
- **Caching**: Cache token metadata
- **Backup Vault**: Maintain backup token vault

**Recovery:**
- **Failover**: Automatically failover to replica
- **Data Recovery**: Restore from backup if needed
- **Token Re-creation**: Re-create tokens if necessary

### 4. Database Failure

**Scenario:** Transaction database fails.

**Impact:** Cannot store or retrieve transactions.

**Mitigation:**
- **Replication**: Primary-replica setup
- **Backup**: Regular backups
- **Read Replicas**: Serve reads from replicas
- **Caching**: Cache recent transactions
- **Event Sourcing**: Use event log for recovery

**Recovery:**
- **Automatic Failover**: Promote replica to primary
- **Data Recovery**: Restore from backup
- **Event Replay**: Replay events to rebuild state

### 5. Network Partition

**Scenario:** Network splits into partitions.

**Impact:** Services in different partitions cannot communicate.

**Mitigation:**
- **Multi-Region**: Deploy in multiple regions
- **Partition Detection**: Detect partitions
- **Graceful Degradation**: Continue operation in partitions
- **Data Reconciliation**: Reconcile after merge

**Recovery:**
- **Merge Handling**: Handle partition merge
- **Data Reconciliation**: Reconcile conflicting data
- **Event Replay**: Replay events to sync state

### 6. Encryption Key Loss

**Scenario:** Encryption keys are lost or compromised.

**Impact:** Cannot decrypt token vault data.

**Mitigation:**
- **Key Backup**: Backup keys securely (HSM)
- **Key Rotation**: Rotate keys periodically
- **Key Escrow**: Escrow keys with trusted third party
- **Key Recovery**: Recover keys from backup

**Recovery:**
- **Key Restoration**: Restore keys from backup
- **Data Re-encryption**: Re-encrypt data with new keys
- **Token Re-creation**: Re-create tokens if needed

### Recovery Mechanisms

**1. Transaction Recovery**
```python
class TransactionRecovery:
    def __init__(self, transaction_store: TransactionStore, event_log: EventLog):
        self.transaction_store = transaction_store
        self.event_log = event_log
    
    def recover_transaction(self, transaction_id: str):
        # Get transaction state
        transaction = self.transaction_store.get(transaction_id)
        
        # Get events
        events = self.event_log.get_events(transaction_id)
        
        # Replay events to rebuild state
        for event in events:
            self._apply_event(transaction, event)
        
        # Save recovered transaction
        self.transaction_store.save(transaction)
    
    def recover_failed_transactions(self):
        # Find transactions in pending state
        pending_transactions = self.transaction_store.get_pending()
        
        for transaction in pending_transactions:
            # Check if transaction should be retried
            if self._should_retry(transaction):
                self._retry_transaction(transaction)
```

**2. Data Consistency**
- **Event Sourcing**: Use event log for audit trail
- **Saga Pattern**: Use saga for distributed transactions
- **Compensation**: Compensate on failure
- **Idempotency**: Make operations idempotent

**3. Service Recovery**
- **Health Checks**: Monitor service health
- **Automatic Restart**: Restart failed services
- **Gradual Recovery**: Gradually increase traffic
- **State Restoration**: Restore service state

---

## Trade-offs & Design Decisions

### 1. Tokenization: In-House vs Third-Party

**Decision:** In-house tokenization.

**Trade-offs:**

| Approach | Pros | Cons |
|----------|------|------|
| **In-House** | Control, cost | Compliance burden |
| **Third-Party** | Less compliance | Higher cost, dependency |

**Why In-House:**
- **Control**: Full control over security
- **Cost**: Lower long-term cost
- **Compliance**: Can achieve PCI-DSS compliance

### 2. Fraud Detection: Real-time vs Batch

**Decision:** Real-time with async deep learning.

**Trade-offs:**

| Approach | Pros | Cons |
|----------|------|------|
| **Real-time** | Fast decisions | Less accurate |
| **Batch** | More accurate | Slower |

**Why Hybrid:**
- **Real-time**: Fast model for immediate decision
- **Async**: Deep learning for accuracy improvement

---

## Interview Discussion Points

### Key Questions to Address

1. **"How do you ensure PCI-DSS compliance?"**
   - **Answer**: 
     - Never store raw card data
     - Use tokenization
     - Encrypt data at rest and in transit
     - Key management (HSM/KMS)
     - Access controls and audit logging

2. **"How do you prevent fraud?"**
   - **Answer**:
     - Real-time ML-based fraud detection
     - Rule-based checks
     - Behavioral analysis
     - Device fingerprinting
     - Velocity checks

3. **"How do you handle payment gateway failures?"**
   - **Answer**:
     - Multi-gateway support
     - Automatic failover
     - Retry logic
     - Queue payments for later processing

4. **"How do you ensure transaction consistency?"**
   - **Answer**:
     - Idempotent transactions
     - Distributed transactions (2PC)
     - Compensation transactions
     - Event sourcing for audit

5. **"How do you handle chargebacks?"**
   - **Answer**:
     - Track chargeback events
     - Dispute management system
     - Evidence collection
     - Automated response

---

## References

- [Stripe Architecture](https://stripe.com/docs)
- [PCI-DSS Requirements](https://www.pcisecuritystandards.org/)
- [System Design Primer](https://github.com/donnemartin/system-design-primer)

