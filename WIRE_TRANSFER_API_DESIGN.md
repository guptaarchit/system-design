# Design and Implement a Wire Transfer API

## Table of Contents
1. [Overview](#overview)
2. [Requirements](#requirements)
3. [System Architecture](#system-architecture)
4. [Database Design](#database-design)
5. [API Design](#api-design)
6. [Transfer Flow](#transfer-flow)
7. [Security & Compliance](#security--compliance)
8. [Scalability Considerations](#scalability-considerations)
9. [Monitoring & Analytics](#monitoring--analytics)
10. [Capacity Planning](#capacity-planning)
11. [Technology Stack](#technology-stack)
12. [Failure Scenarios & Handling](#failure-scenarios--handling)
13. [Interview Discussion Points](#interview-discussion-points)

---

## Overview

A wire transfer API system that enables secure money transfers between bank accounts. The system must handle high-value transactions, ensure security and compliance (AML, KYC), provide transaction tracking, and integrate with banking networks.

**Key Features:**
- Initiate wire transfers
- Transfer validation
- Fraud detection
- Transaction tracking
- Compliance checks (AML, KYC)
- Multi-currency support
- Transfer status updates
- Settlement processing

---

## Requirements

### Functional Requirements

1. **Transfer Management**
   - Initiate wire transfers
   - Validate transfer details
   - Process transfers
   - Track transfer status

2. **Security**
   - Authentication and authorization
   - Fraud detection
   - Transaction limits
   - Audit logging

3. **Compliance**
   - AML (Anti-Money Laundering) checks
   - KYC (Know Your Customer) verification
   - Regulatory reporting
   - Transaction monitoring

4. **Integration**
   - Bank network integration (SWIFT, ACH)
   - Real-time status updates
   - Settlement processing

### Non-Functional Requirements

1. **Scalability**
   - Handle 1M+ transfers per day
   - Support high-value transfers
   - Horizontal scaling

2. **Performance**
   - Transfer initiation: < 500ms
   - Validation: < 200ms
   - Status query: < 100ms

3. **Reliability**
   - 99.99% uptime
   - No transaction loss
   - Strong consistency for balances

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                             │
│  (API Clients, Web Apps, Mobile Apps)                          │
└────────────────┬────────────────────────────────────────────────┘
                 │ HTTPS/TLS
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API Gateway                                   │
│  - Authentication                                               │
│  - Rate Limiting                                                │
│  - Request Validation                                           │
└────────────┬────────────────────────────────────┬────────────────┘
             │                                    │
             ▼                                    ▼
┌────────────────────────────┐      ┌────────────────────────────┐
│   Transfer Service         │      │   Validation Service       │
│   - Initiate Transfers     │      │   - Account Validation     │
│   - Process Transfers      │      │   - Balance Checks         │
└────────────┬───────────────┘      └────────────┬───────────────┘
             │                                    │
             ▼                                    ▼
┌────────────────────────────┐      ┌────────────────────────────┐
│   Fraud Detection          │      │   Compliance Service       │
│   Service                  │      │   - AML Checks             │
│   - Risk Scoring           │      │   - KYC Verification        │
└────────────┬───────────────┘      └────────────┬───────────────┘
             │                                    │
             ▼                                    ▼
┌────────────────────────────────────────────────────────────────┐
│                    Banking Integration                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   SWIFT      │  │   ACH        │  │   Real-time  │         │
│  │   Network    │  │   Network    │  │   Payments   │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Data Layer                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Transfers  │  │   Accounts   │  │   Audit Log  │         │
│  │     DB       │  │     DB       │  │     DB       │         │
│  │ (PostgreSQL) │  │ (PostgreSQL) │  │ (Cassandra)  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────────────────────────────────────────────┘
```

---

## Database Design

### Transfers Table

```sql
CREATE TABLE transfers (
    transfer_id BIGSERIAL PRIMARY KEY,
    transfer_reference VARCHAR(255) UNIQUE NOT NULL,
    from_account_id BIGINT NOT NULL,
    to_account_id BIGINT NOT NULL,
    amount DECIMAL(20, 2) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    status VARCHAR(20) DEFAULT 'pending', -- pending, processing, completed, failed, cancelled
    transfer_type VARCHAR(20) NOT NULL, -- domestic, international, same_bank
    network VARCHAR(20), -- SWIFT, ACH, internal
    initiated_by BIGINT NOT NULL,
    fraud_score DECIMAL(5, 2),
    compliance_status VARCHAR(20) DEFAULT 'pending', -- pending, approved, rejected
    initiated_at TIMESTAMP DEFAULT NOW(),
    processed_at TIMESTAMP,
    completed_at TIMESTAMP,
    failed_at TIMESTAMP,
    failure_reason TEXT,
    FOREIGN KEY (from_account_id) REFERENCES accounts(account_id),
    FOREIGN KEY (to_account_id) REFERENCES accounts(account_id),
    INDEX idx_status (status),
    INDEX idx_from_account (from_account_id),
    INDEX idx_to_account (to_account_id),
    INDEX idx_reference (transfer_reference)
);
```

### Accounts Table

```sql
CREATE TABLE accounts (
    account_id BIGSERIAL PRIMARY KEY,
    account_number VARCHAR(50) UNIQUE NOT NULL,
    routing_number VARCHAR(50),
    bank_name VARCHAR(255),
    account_type VARCHAR(20), -- checking, savings
    currency VARCHAR(3) DEFAULT 'USD',
    balance DECIMAL(20, 2) DEFAULT 0.00,
    status VARCHAR(20) DEFAULT 'active', -- active, frozen, closed
    kyc_status VARCHAR(20) DEFAULT 'pending', -- pending, verified, rejected
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_account_number (account_number)
);
```

---

## API Design

### Transfer APIs

```
POST   /api/v1/transfers
GET    /api/v1/transfers/{transfer_id}
GET    /api/v1/transfers?account_id={account_id}&status={status}
POST   /api/v1/transfers/{transfer_id}/cancel
```

### Create Transfer Request

```json
POST /api/v1/transfers
{
  "from_account_id": 123,
  "to_account_id": 456,
  "amount": 10000.00,
  "currency": "USD",
  "transfer_type": "domestic",
  "description": "Payment for services",
  "reference": "INV-2024-001"
}
```

**Response:**
```json
{
  "transfer_id": "transfer_abc123",
  "transfer_reference": "WT-2024-001234",
  "status": "pending",
  "initiated_at": "2024-01-15T10:00:00Z",
  "estimated_completion": "2024-01-15T14:00:00Z"
}
```

---

## Transfer Flow

### Transfer Process

1. **Validate request** → Check authentication, account ownership
2. **Validate accounts** → Verify account existence and status
3. **Check balance** → Ensure sufficient funds
4. **Fraud detection** → Score transaction risk
5. **Compliance check** → AML/KYC verification
6. **Create transfer** → Record in database
7. **Reserve funds** → Hold funds in sender account
8. **Route to network** → Send to appropriate banking network
9. **Process settlement** → Complete transfer
10. **Update status** → Mark as completed
11. **Send notifications** → Notify both parties

### Transfer Validation

```python
class TransferValidator:
    def validate_transfer(self, transfer_request: dict) -> tuple[bool, str]:
        # Validate amount
        if transfer_request['amount'] <= 0:
            return False, "Amount must be positive"
        
        if transfer_request['amount'] > self.get_max_limit(transfer_request['from_account_id']):
            return False, "Amount exceeds transfer limit"
        
        # Validate accounts
        from_account = self.get_account(transfer_request['from_account_id'])
        to_account = self.get_account(transfer_request['to_account_id'])
        
        if not from_account or from_account.status != 'active':
            return False, "Invalid sender account"
        
        if not to_account or to_account.status != 'active':
            return False, "Invalid recipient account"
        
        # Check balance
        if from_account.balance < transfer_request['amount']:
            return False, "Insufficient funds"
        
        return True, "Valid"
```

---

## Security & Compliance

### Fraud Detection

```python
class FraudDetector:
    def score_transfer(self, transfer: dict) -> float:
        score = 0.0
        
        # Amount-based scoring
        if transfer['amount'] > 100000:
            score += 20
        
        # Velocity check
        recent_transfers = self.get_recent_transfers(transfer['from_account_id'], hours=24)
        if len(recent_transfers) > 10:
            score += 30
        
        # Geographic check
        if self.is_suspicious_location(transfer):
            score += 25
        
        # Account age
        account_age = self.get_account_age(transfer['from_account_id'])
        if account_age < 30:  # days
            score += 15
        
        return min(100.0, score)
```

### Compliance Checks

```python
class ComplianceChecker:
    def check_aml(self, transfer: dict) -> bool:
        # Check against sanctions list
        if self.is_sanctioned_entity(transfer['to_account_id']):
            return False
        
        # Check transaction patterns
        if self.has_suspicious_pattern(transfer):
            return False
        
        return True
    
    def check_kyc(self, account_id: int) -> bool:
        account = self.get_account(account_id)
        return account.kyc_status == 'verified'
```

---

## High-Level Design (HLD)

### System Overview

The Wire Transfer API is a secure, high-performance financial system that enables money transfers between bank accounts. It ensures security, compliance (AML/KYC), fraud detection, and reliable transaction processing.

### HLD Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Client Layer                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                      │
│  │   API    │  │   Web    │  │  Mobile  │                      │
│  │ Clients  │  │   App    │  │   App    │                      │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘                      │
└───────┼─────────────┼───────────────┼──────────────────────────┘
        │             │               │
        └─────────────┴───────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│              API Gateway / Load Balancer                        │
│  - Authentication                                               │
│  - Rate limiting                                               │
│  - Request validation                                          │
│  - SSL/TLS termination                                         │
└───────────────────────────┬─────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│   Region 1    │  │   Region 2    │  │   Region N    │
│  (US-East)    │  │  (EU-West)    │  │  (AP-South)  │
└───────┬───────┘  └───────┬───────┘  └───────┬───────┘
        │                   │                   │
        ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────────────────┐
│              Application Services Layer                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ Transfer │  │Validation│  │  Fraud   │  │Compliance│       │
│  │ Service  │  │ Service  │  │Detection │  │ Service  │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │Settlement│  │  Audit   │  │Notification│ │  Routing │       │
│  │ Service  │  │ Service  │  │ Service  │  │ Service  │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
└───────┼─────────────┼──────────────┼──────────────┼────────┘
        │             │               │              │
        ▼             ▼               ▼              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Caching Layer                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │  Redis   │  │  Redis   │  │  Redis   │  │  Redis   │       │
│  │(Balances)│ │(Limits)  │ │(Sessions)│ │(Rate Limit)│      │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
└───────┼─────────────┼──────────────┼──────────────┼────────┘
        │             │               │              │
        ▼             ▼               ▼              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Database Layer                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │PostgreSQL│  │PostgreSQL│  │Cassandra │  │PostgreSQL│      │
│  │(Transfers)│ │(Accounts)│ │(Audit Log)│ │(Compliance)│     │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘      │
└───────┼─────────────┼──────────────┼──────────────┼────────┘
        │             │               │              │
        ▼             ▼               ▼              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Banking Integration                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │  SWIFT   │  │   ACH    │  │ Real-time│  │  Payment │      │
│  │ Network  │  │ Network  │  │ Payments │  │ Gateway  │      │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘      │
└─────────────────────────────────────────────────────────────────┘
```

### Design Principles

- **Security First**: End-to-end encryption, fraud detection
- **Compliance**: AML/KYC checks, regulatory reporting
- **Reliability**: No transaction loss, strong consistency
- **Performance**: Sub-500ms transfer initiation
- **Auditability**: Complete audit trail

---

## Low-Level Design (LLD)

### Transfer Service (Detailed Implementation)

```python
class TransferService:
    def __init__(self):
        self.validator = TransferValidator()
        self.fraud_detector = FraudDetector()
        self.compliance_checker = ComplianceChecker()
        self.settlement_service = SettlementService()
        self.db = DatabasePool()
        self.redis = RedisCluster()
        self.distributed_lock = DistributedLockManager()
    
    async def initiate_transfer(
        self, 
        transfer_request: TransferRequest
    ) -> TransferResult:
        """Initiate a wire transfer with full validation"""
        
        # Step 1: Validate request
        validation_result = await self.validator.validate(transfer_request)
        if not validation_result.is_valid:
            return TransferResult(
                status='rejected',
                reason=validation_result.reason
            )
        
        # Step 2: Check balance (with lock)
        account_lock_key = f"account_lock:{transfer_request.from_account_id}"
        async with self.distributed_lock.acquire(account_lock_key, timeout=10):
            balance = await self.get_account_balance(
                transfer_request.from_account_id
            )
            
            if balance < transfer_request.amount:
                return TransferResult(
                    status='rejected',
                    reason='Insufficient funds'
                )
            
            # Step 3: Reserve funds
            await self.reserve_funds(
                transfer_request.from_account_id,
                transfer_request.amount
            )
        
        # Step 4: Fraud detection
        fraud_score = await self.fraud_detector.score_transfer(
            transfer_request
        )
        
        if fraud_score > 70:  # High risk threshold
            await self.release_reservation(
                transfer_request.from_account_id,
                transfer_request.amount
            )
            return TransferResult(
                status='rejected',
                reason='Fraud detection triggered',
                fraud_score=fraud_score
            )
        
        # Step 5: Compliance check
        compliance_result = await self.compliance_checker.check(
            transfer_request
        )
        
        if not compliance_result.approved:
            await self.release_reservation(
                transfer_request.from_account_id,
                transfer_request.amount
            )
            return TransferResult(
                status='rejected',
                reason='Compliance check failed',
                compliance_details=compliance_result.details
            )
        
        # Step 6: Create transfer record
        transfer = await self.create_transfer_record(transfer_request)
        
        # Step 7: Process settlement (async)
        asyncio.create_task(
            self.settlement_service.process_settlement(transfer)
        )
        
        # Step 8: Audit log
        await self.audit_service.log_transfer(transfer)
        
        return TransferResult(
            status='pending',
            transfer_id=transfer.transfer_id,
            estimated_completion=transfer.estimated_completion
        )
    
    async def reserve_funds(self, account_id: int, amount: float):
        """Reserve funds for transfer"""
        # Update balance atomically
        await self.db.execute(
            """
            UPDATE accounts 
            SET balance = balance - $1,
                reserved_balance = reserved_balance + $1
            WHERE account_id = $2
            """,
            amount, account_id
        )
        
        # Update cache
        await self.redis.decrby(
            f"balance:{account_id}",
            amount
        )
```

### Fraud Detection Service (Detailed)

```python
class FraudDetector:
    def __init__(self):
        self.ml_model = FraudDetectionModel()
        self.rule_engine = RuleEngine()
        self.db = DatabasePool()
    
    async def score_transfer(
        self, 
        transfer: TransferRequest
    ) -> float:
        """Calculate fraud risk score"""
        
        # Rule-based checks
        rule_score = await self.rule_engine.evaluate(transfer)
        
        # ML-based scoring
        features = await self.extract_features(transfer)
        ml_score = self.ml_model.predict(features)
        
        # Combine scores
        final_score = (rule_score * 0.4) + (ml_score * 0.6)
        
        return min(100.0, max(0.0, final_score))
    
    async def extract_features(self, transfer: TransferRequest) -> dict:
        """Extract features for ML model"""
        # Get account history
        recent_transfers = await self.db.fetch(
            """
            SELECT amount, created_at, status
            FROM transfers
            WHERE from_account_id = $1
            AND created_at > NOW() - INTERVAL '30 days'
            ORDER BY created_at DESC
            LIMIT 100
            """,
            transfer.from_account_id
        )
        
        # Calculate features
        features = {
            'amount': transfer.amount,
            'amount_to_balance_ratio': (
                transfer.amount / 
                await self.get_account_balance(transfer.from_account_id)
            ),
            'transfer_count_24h': len([
                t for t in recent_transfers 
                if (datetime.now() - t.created_at).total_seconds() < 86400
            ]),
            'total_amount_24h': sum(
                t.amount for t in recent_transfers
                if (datetime.now() - t.created_at).total_seconds() < 86400
            ),
            'is_new_account': await self.is_new_account(
                transfer.from_account_id
            ),
            'is_suspicious_location': await self.is_suspicious_location(
                transfer.to_account_id
            ),
            'account_age_days': await self.get_account_age(
                transfer.from_account_id
            )
        }
        
        return features
```

### Compliance Service (Detailed)

```python
class ComplianceChecker:
    def __init__(self):
        self.sanctions_list = SanctionsListService()
        self.aml_service = AMLService()
        self.kyc_service = KYCService()
    
    async def check(
        self, 
        transfer: TransferRequest
    ) -> ComplianceResult:
        """Perform compliance checks"""
        
        # Check sanctions list
        if await self.sanctions_list.is_sanctioned(
            transfer.to_account_id
        ):
            return ComplianceResult(
                approved=False,
                reason='Recipient on sanctions list'
            )
        
        # Check KYC status
        kyc_status = await self.kyc_service.get_status(
            transfer.from_account_id
        )
        
        if kyc_status != 'verified':
            return ComplianceResult(
                approved=False,
                reason=f'KYC status: {kyc_status}'
            )
        
        # AML check
        aml_result = await self.aml_service.check_transaction(transfer)
        
        if not aml_result.passed:
            return ComplianceResult(
                approved=False,
                reason='AML check failed',
                details=aml_result.details
            )
        
        return ComplianceResult(approved=True)
```

---

## Fault Tolerance

### Fault Tolerance Strategy

The system ensures transaction integrity and availability even when components fail.

### Component-Level Fault Tolerance

#### 1. Database Failure Tolerance

**Transaction Safety:**
```python
class FaultTolerantTransferService:
    async def initiate_transfer(self, transfer_request):
        # Use database transaction
        async with self.db.transaction():
            try:
                # Create transfer record
                transfer = await self.create_transfer(transfer_request)
                
                # Reserve funds
                await self.reserve_funds(
                    transfer_request.from_account_id,
                    transfer_request.amount
                )
                
                # Commit transaction
                await self.db.commit()
                
                return transfer
            except Exception as e:
                # Rollback on any error
                await self.db.rollback()
                raise
```

**Read Replicas:**
```python
class FaultTolerantDatabase:
    async def get_account_balance(self, account_id):
        # Try primary first
        try:
            return await self.primary.fetchval(
                "SELECT balance FROM accounts WHERE account_id = $1",
                account_id
            )
        except DatabaseError:
            # Fallback to replica
            return await self.replica.fetchval(
                "SELECT balance FROM accounts WHERE account_id = $1",
                account_id
            )
```

#### 2. External Service Failure Tolerance

**Banking Network Fallback:**
```python
class FaultTolerantSettlementService:
    async def process_settlement(self, transfer):
        # Try primary network
        try:
            return await self.swift_network.settle(transfer)
        except NetworkError:
            # Fallback to ACH
            try:
                return await self.ach_network.settle(transfer)
            except NetworkError:
                # Queue for retry
                await self.retry_queue.enqueue('settle', transfer)
                return SettlementResult(status='queued')
```

#### 3. Fraud Detection Failure Tolerance

**Fallback to Rules:**
```python
class FaultTolerantFraudDetector:
    async def score_transfer(self, transfer):
        # Try ML model
        try:
            return await self.ml_model.score(transfer)
        except ModelError:
            # Fallback to rule-based
            return await self.rule_engine.score(transfer)
```

---

## Failure Safety

### Failure Safety Principles

1. **No Transaction Loss**: All transfers persisted before processing
2. **Idempotency**: Operations can be safely retried
3. **Consistency**: Strong consistency for balances
4. **Recovery**: Automatic recovery from failures

### Critical Failure Scenarios

#### 1. Database Failure During Transfer

**Problem:** Database fails while processing transfer.

**Solution:** Two-phase commit with compensation.

```python
class FailureSafeTransferService:
    async def initiate_transfer(self, transfer_request):
        # Phase 1: Create transfer record (pending)
        transfer = await self.create_transfer_record(
            transfer_request,
            status='pending'
        )
        
        # Phase 2: Reserve funds
        try:
            await self.reserve_funds(
                transfer_request.from_account_id,
                transfer_request.amount
            )
            
            # Update transfer status
            await self.update_transfer_status(
                transfer.transfer_id,
                'processing'
            )
        except DatabaseError:
            # Compensation: Mark transfer as failed
            await self.update_transfer_status(
                transfer.transfer_id,
                'failed',
                reason='Database error'
            )
            raise
```

#### 2. Settlement Failure

**Problem:** Settlement fails after funds reserved.

**Solution:** Automatic retry with timeout.

```python
class FailureSafeSettlementService:
    async def process_settlement(self, transfer):
        max_retries = 3
        retry_delay = 60  # seconds
        
        for attempt in range(max_retries):
            try:
                result = await self.settle_transfer(transfer)
                
                if result.success:
                    # Update transfer status
                    await self.update_transfer_status(
                        transfer.transfer_id,
                        'completed'
                    )
                    return result
            except SettlementError as e:
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay * (attempt + 1))
                    continue
                else:
                    # Final failure: Reverse transfer
                    await self.reverse_transfer(transfer)
                    raise
```

#### 3. Double-Spending Prevention

**Problem:** Concurrent transfers causing double-spending.

**Solution:** Distributed locks and optimistic locking.

```python
class DoubleSpendingPrevention:
    async def reserve_funds(self, account_id, amount):
        # Acquire distributed lock
        lock_key = f"account:{account_id}"
        
        async with self.distributed_lock.acquire(lock_key):
            # Check balance with version
            account = await self.db.fetchrow(
                """
                SELECT balance, version 
                FROM accounts 
                WHERE account_id = $1
                FOR UPDATE
                """,
                account_id
            )
            
            if account.balance < amount:
                raise InsufficientFundsError()
            
            # Update with version check
            result = await self.db.execute(
                """
                UPDATE accounts 
                SET balance = balance - $1,
                    version = version + 1
                WHERE account_id = $2
                AND version = $3
                """,
                amount, account_id, account.version
            )
            
            if result.rowcount == 0:
                raise ConcurrentModificationError()
```

---

## Optimizations

### Performance Optimizations

#### 1. Balance Caching

**Cache Account Balances:**
```python
class OptimizedBalanceService:
    def __init__(self):
        self.redis = RedisCluster()
        self.cache_ttl = 60  # seconds
    
    async def get_account_balance(self, account_id):
        # Check cache
        cache_key = f"balance:{account_id}"
        cached = await self.redis.get(cache_key)
        
        if cached:
            return float(cached)
        
        # Fetch from database
        balance = await self.db.fetchval(
            "SELECT balance FROM accounts WHERE account_id = $1",
            account_id
        )
        
        # Cache balance
        await self.redis.setex(cache_key, self.cache_ttl, balance)
        
        return balance
    
    async def update_balance(self, account_id, delta):
        # Update database
        await self.db.execute(
            "UPDATE accounts SET balance = balance + $1 WHERE account_id = $2",
            delta, account_id
        )
        
        # Invalidate cache
        await self.redis.delete(f"balance:{account_id}")
```

#### 2. Batch Processing

**Batch Compliance Checks:**
```python
class BatchedComplianceChecker:
    async def check_batch(self, transfers):
        # Batch check sanctions list
        account_ids = [t.to_account_id for t in transfers]
        sanctions = await self.sanctions_list.batch_check(account_ids)
        
        # Batch check KYC
        from_account_ids = [t.from_account_id for t in transfers]
        kyc_statuses = await self.kyc_service.batch_get_status(
            from_account_ids
        )
        
        # Process results
        results = []
        for transfer in transfers:
            if sanctions.get(transfer.to_account_id):
                results.append(ComplianceResult(approved=False))
            elif kyc_statuses.get(transfer.from_account_id) != 'verified':
                results.append(ComplianceResult(approved=False))
            else:
                results.append(ComplianceResult(approved=True))
        
        return results
```

#### 3. Database Query Optimization

**Connection Pooling:**
```python
class OptimizedDatabase:
    def __init__(self):
        self.pool = asyncpg.create_pool(
            database_url,
            min_size=20,
            max_size=100,
            max_queries=100000
        )
```

**Read Replicas:**
```python
async def get_transfer_history(self, account_id):
    # Use read replica for read operations
    async with self.read_replica_pool.acquire() as conn:
        return await conn.fetch(
            "SELECT * FROM transfers WHERE from_account_id = $1",
            account_id
        )
```

---

## Scalability Considerations

### Horizontal Scaling Strategy

#### 1. Service Scaling

**Stateless Services:**
- All state in database
- Multiple instances behind load balancer
- Auto-scaling based on load

#### 2. Database Scaling

**Sharding:**
- Shard by account_id
- Consistent hashing
- Read replicas for reads

#### 3. Queue Scaling

**Kafka Partitioning:**
- Partition by account_id
- Parallel processing
- Consumer groups

### Capacity Planning

**Traffic Estimates:**
- 1M transfers/day
- 100 transfers/second (peak)
- Average transfer: $10,000
- Daily volume: $10B

**Storage Estimates:**
- Transfer records: 1M/day × 2KB = 2GB/day
- Audit logs: 1M/day × 1KB = 1GB/day
- Total: ~3GB/day = ~1TB/year

**Compute Estimates:**
- Transfer processing: 100 req/sec × 500ms = 50 concurrent operations
- Fraud detection: 100 req/sec × 200ms = 20 concurrent operations
- Total: ~70 concurrent operations

---

## Capacity Planning

- **Transfers per Day**: 1M transfers/day
- **Peak Rate**: 100 transfers/second
- **Average Transfer**: $10,000
- **Daily Volume**: $10B
- **Storage**: ~1TB/year
- **Compute**: ~100 servers

---

## Technology Stack

- **Backend**: Java, Go
- **Database**: PostgreSQL (with replication)
- **Message Queue**: Kafka
- **Cache**: Redis
- **Banking Integration**: SWIFT, ACH APIs
- **Monitoring**: Prometheus, Grafana

---

## Interview Discussion Points

1. **Security**: How do you prevent fraud?
   - ML-based fraud detection
   - Rule-based checks
   - Velocity monitoring
   - Anomaly detection

2. **Compliance**: How do you ensure AML/KYC compliance?
   - Sanctions list checking
   - KYC verification
   - AML transaction monitoring
   - Regulatory reporting

3. **Reliability**: How do you ensure no transaction loss?
   - Database transactions
   - Two-phase commit
   - Compensation logic
   - Audit trail

4. **Performance**: How do you handle high-volume transfers?
   - Horizontal scaling
   - Database sharding
   - Caching
   - Batch processing

---

**Document Version**: 2.0  
**Last Updated**: January 2024

