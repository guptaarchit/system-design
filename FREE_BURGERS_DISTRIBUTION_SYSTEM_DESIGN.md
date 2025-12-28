# Design Backend for an App to Distribute 6 Million Free Burgers in One Hour

## Table of Contents
1. [Overview](#overview)
2. [Requirements](#requirements)
3. [System Architecture](#system-architecture)
4. [Database Design](#database-design)
5. [API Design](#api-design)
6. [Claim Flow](#claim-flow)
7. [Rate Limiting & Throttling](#rate-limiting--throttling)
8. [Scalability Considerations](#scalability-considerations)
9. [Caching Strategy](#caching-strategy)
10. [Load Balancing](#load-balancing)
11. [Security](#security)
12. [Monitoring & Analytics](#monitoring--analytics)
13. [Capacity Planning](#capacity-planning)
14. [Technology Stack](#technology-stack)
15. [Failure Scenarios & Handling](#failure-scenarios--handling)
16. [Trade-offs & Design Decisions](#trade-offs--design-decisions)
17. [Interview Discussion Points](#interview-discussion-points)

---

## Overview

A backend system to distribute 6 million free burgers within a 1-hour window. The system must handle massive concurrent traffic, prevent abuse, ensure fair distribution, manage inventory, and coordinate with restaurants for redemption.

**Key Features:**
- High-concurrency claim system
- Inventory management
- Fraud prevention
- Rate limiting per user
- Geographic distribution
- Restaurant coordination
- Real-time availability updates
- Claim validation and redemption

---

## Requirements

### Functional Requirements

1. **Burger Claims**
   - Users can claim free burgers
   - One burger per user
   - Real-time availability
   - Geographic distribution

2. **Inventory Management**
   - Track available burgers
   - Allocate burgers to restaurants
   - Real-time inventory updates

3. **Fraud Prevention**
   - One claim per user
   - Device/IP validation
   - Account verification

4. **Restaurant Integration**
   - Restaurant registration
   - Redemption code generation
   - Redemption tracking

### Non-Functional Requirements

1. **Scalability**
   - Handle 100K+ concurrent users
   - Process 10K+ claims per second
   - 6M burgers in 1 hour = 1,667 claims/second average
   - Peak: 3x average = 5K claims/second

2. **Performance**
   - Claim processing: < 200ms (p95)
   - Availability check: < 50ms
   - 99.9% uptime

3. **Reliability**
   - No double claims
   - Fair distribution
   - No data loss

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                             │
│  (Mobile Apps, Web Apps)                                        │
└────────────────┬────────────────────────────────────────────────┘
                 │ HTTPS
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CDN & Load Balancer                           │
│              (CloudFlare, AWS ALB)                              │
└────────────┬────────────────────────────────────┬────────────────┘
             │                                    │
             ▼                                    ▼
┌────────────────────────────┐      ┌────────────────────────────┐
│   Claim Service            │      │   Inventory Service        │
│   - Process Claims         │      │   - Track Availability     │
│   - Validate Users         │      │   - Allocate Burgers       │
└────────────┬───────────────┘      └────────────┬───────────────┘
             │                                    │
             ▼                                    ▼
┌────────────────────────────┐      ┌────────────────────────────┐
│   Fraud Detection          │      │   Rate Limiting Service     │
│   Service                  │      │   - Per User Limits         │
│   - Duplicate Detection    │      │   - Global Limits           │
└────────────┬───────────────┘      └────────────┬───────────────┘
             │                                    │
             ▼                                    ▼
┌────────────────────────────────────────────────────────────────┐
│                    Message Queue                                 │
│              (Kafka)                                            │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Processing Layer                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Claim      │  │   Code      │  │   Notification│        │
│  │   Processor  │  │   Generator │  │   Service    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────┬────────────────────┬────────────────────┬──────────────────┘
     │                    │                    │
     ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  Cache Layer    │  │   Database      │  │   Restaurant    │
│  (Redis)        │  │  (PostgreSQL)   │  │   API           │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

### HLD Component Breakdown

**1. Client Layer**
- **Mobile Apps**: iOS/Android apps for users
- **Web Apps**: Web interface for users

**2. API Gateway Layer**
- **CDN**: CloudFlare for static assets
- **Load Balancer**: AWS ALB for traffic distribution

**3. Service Layer**
- **Claim Service**: Processes burger claims
- **Inventory Service**: Tracks burger availability
- **Fraud Detection Service**: Detects duplicate claims
- **Rate Limiting Service**: Enforces rate limits

**4. Processing Layer**
- **Claim Processor**: Processes claims asynchronously
- **Code Generator**: Generates redemption codes
- **Notification Service**: Sends notifications

**5. Data Layer**
- **Redis**: Availability cache, rate limits, locks
- **PostgreSQL**: Claims, inventory, users
- **Kafka**: Event streaming

---

## Low-Level Design (LLD)

### Claim Service LLD

```python
class ClaimService:
    def __init__(self, db: Database, inventory_service: InventoryService,
                 fraud_service: FraudDetectionService, rate_limiter: RateLimiter,
                 lock_manager: LockManager):
        self.db = db
        self.inventory_service = inventory_service
        self.fraud_service = fraud_service
        self.rate_limiter = rate_limiter
        self.lock_manager = lock_manager
    
    def claim_burger(self, user_id: int, location_id: int) -> dict:
        # Check rate limits
        if not self.rate_limiter.check_rate_limit(user_id):
            raise RateLimitExceededError()
        
        # Check fraud
        if self.fraud_service.is_duplicate(user_id):
            raise DuplicateClaimError()
        
        # Acquire distributed lock
        lock_key = f"claim_lock:{user_id}"
        
        with self.lock_manager.acquire(lock_key, timeout=5):
            # Double-check if already claimed
            existing_claim = self.db.query(
                "SELECT claim_id FROM claims WHERE user_id = %s",
                (user_id,)
            )
            if existing_claim:
                raise AlreadyClaimedError()
            
            # Check inventory
            if not self.inventory_service.has_available_burgers(location_id):
                raise OutOfStockError()
            
            # Reserve burger
            burger_id = self.inventory_service.reserve_burger(location_id)
            
            # Generate redemption code
            redemption_code = self._generate_code()
            
            # Create claim
            claim = Claim.create(
                user_id=user_id,
                burger_id=burger_id,
                redemption_code=redemption_code,
                location_id=location_id,
                status='claimed'
            )
            
            # Publish event
            self.event_publisher.publish('burger.claimed', {
                'claim_id': claim.id,
                'user_id': user_id,
                'redemption_code': redemption_code
            })
            
            return {
                'claim_id': claim.id,
                'redemption_code': redemption_code,
                'expires_at': claim.expires_at
            }
```

### Inventory Service LLD

```python
class InventoryService:
    def __init__(self, db: Database, cache: RedisCache, lock_manager: LockManager):
        self.db = db
        self.cache = cache
        self.lock_manager = lock_manager
    
    def has_available_burgers(self, location_id: int) -> bool:
        # Check cache first
        cache_key = f"availability:{location_id}"
        cached = self.cache.get(cache_key)
        
        if cached is not None:
            return int(cached) > 0
        
        # Query database
        count = self.db.query(
            "SELECT COUNT(*) FROM inventory WHERE location_id = %s AND status = 'available'",
            (location_id,)
        )
        
        available = count > 0
        
        # Update cache
        self.cache.set(cache_key, count, ttl=1)  # 1 second TTL
        
        return available
    
    def reserve_burger(self, location_id: int) -> int:
        lock_key = f"inventory_lock:{location_id}"
        
        with self.lock_manager.acquire(lock_key, timeout=5):
            # Get available burger (atomic)
            burger = self.db.query(
                "SELECT burger_id FROM inventory WHERE location_id = %s AND status = 'available' LIMIT 1 FOR UPDATE",
                (location_id,)
            )
            
            if not burger:
                raise OutOfStockError()
            
            # Update status
            self.db.execute(
                "UPDATE inventory SET status = 'claimed' WHERE burger_id = %s",
                (burger.burger_id,)
            )
            
            # Invalidate cache
            self.cache.delete(f"availability:{location_id}")
            
            return burger.burger_id
```

### Rate Limiter LLD

```python
class RateLimiter:
    def __init__(self, redis: RedisClient):
        self.redis = redis
    
    def check_rate_limit(self, user_id: int, ip_address: str = None) -> bool:
        # Per-user limit: 1 claim
        user_key = f"claim:user:{user_id}"
        if self.redis.exists(user_key):
            return False
        
        # Per-IP limit: 5 claims per hour
        if ip_address:
            ip_key = f"claim:ip:{ip_address}"
            ip_count = self.redis.incr(ip_key)
            if ip_count == 1:
                self.redis.expire(ip_key, 3600)
            if ip_count > 5:
                return False
        
        # Global limit: 5000 claims/second
        global_key = "claim:global"
        global_count = self.redis.incr(global_key)
        if global_count == 1:
            self.redis.expire(global_key, 1)
        if global_count > 5000:
            return False
        
        return True
    
    def record_claim(self, user_id: int, ip_address: str = None):
        # Mark user as claimed
        user_key = f"claim:user:{user_id}"
        self.redis.setex(user_key, 86400, "1")  # 24 hours
```

---

## Fault Tolerance

### Claim Processing Fault Tolerance

**1. Distributed Locking**
- **Redis Locks**: Prevent race conditions
- **Lock Timeout**: 5-second timeout
- **Lock Retry**: Retry with exponential backoff
- **Deadlock Prevention**: Order locks consistently

**2. Idempotency**
- **Idempotent Operations**: Claim operations are idempotent
- **Duplicate Detection**: Check before claiming
- **Idempotency Keys**: Use keys for retries

**3. Database Transaction**
- **ACID Transactions**: Ensure atomicity
- **Rollback on Failure**: Rollback on errors
- **Isolation Levels**: Use appropriate isolation

### Inventory Fault Tolerance

**1. Cache Consistency**
- **Cache Invalidation**: Invalidate on updates
- **Database as Source of Truth**: Always verify with database
- **Cache Refresh**: Refresh cache periodically

**2. Inventory Reconciliation**
- **Periodic Reconciliation**: Reconcile inventory daily
- **Event Replay**: Replay events to rebuild state
- **Manual Fix**: Manual intervention if needed

---

## Failure Safety

### Failure Scenarios & Handling

**1. High Concurrency**

**Scenario**: 5K+ claims per second.

**Impact**: System overload, race conditions.

**Mitigation**:
- **Distributed Locks**: Lock during claim processing
- **Rate Limiting**: Limit claims per second
- **Queue Buffering**: Buffer claims in Kafka
- **Auto-Scaling**: Scale services automatically

**Recovery**:
- **Scale Up**: Add more service instances
- **Load Shedding**: Drop non-critical requests
- **Priority Queue**: Process critical claims first

**2. Inventory Exhaustion**

**Scenario**: All burgers claimed.

**Impact**: Cannot process more claims.

**Mitigation**:
- **Real-time Tracking**: Track availability in real-time
- **Cache Updates**: Update cache on claims
- **Graceful Response**: Return clear error messages

**Recovery**:
- **Inventory Refresh**: Refresh inventory if available
- **Cancellation Processing**: Process cancellations quickly

**3. Database Failure**

**Scenario**: Database becomes unavailable.

**Impact**: Cannot process claims.

**Mitigation**:
- **Database Replication**: Primary-replica setup
- **Automatic Failover**: Promote replica on failure
- **Cache Fallback**: Use cached data when possible

**Recovery**:
- **Failover**: Automatically failover to replica
- **Data Sync**: Sync data when primary recovers
- **State Reconciliation**: Reconcile state after recovery

---

## Scalability Considerations

### 1. Horizontal Scaling

**Claim Services:**
- Stateless services
- Scale horizontally (1000+ req/s per instance)
- Load balancer distributes traffic
- Auto-scaling based on request rate

**Scaling Metrics:**
- **Peak Rate**: 5K claims/second
- **Required Instances**: 5-10 instances (500-1000 req/s each)
- **Database Connections**: Connection pooling (20-50 per instance)

### 2. Database Scaling

**PostgreSQL Scaling:**
- **Read Replicas**: 3-5 read replicas for reads
- **Sharding**: Shard by location_id or user_id
- **Connection Pooling**: PgBouncer for connection pooling
- **Partitioning**: Partition claims table by date

### 3. Caching Strategy

**Multi-Level Caching:**
- **Redis**: Availability counts, rate limits (TTL: 1 second)
- **Application Cache**: User claim status (TTL: 1 hour)
- **CDN**: Static assets

**Cache Invalidation:**
- **Event-Based**: Invalidate on claims
- **TTL-Based**: Short TTL for availability (1 second)
- **Manual**: Manual invalidation if needed

### 4. Message Queue Scaling

**Kafka Scaling:**
- **Partitioning**: Partition by user_id or location_id
- **Replication**: 3 replicas per partition
- **Consumer Groups**: Parallel processing
- **Auto-Scaling**: Scale consumers based on lag

---

## Database Design

### Claims Table

```sql
CREATE TABLE claims (
    claim_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    burger_id BIGINT NOT NULL,
    restaurant_id BIGINT,
    redemption_code VARCHAR(50) UNIQUE NOT NULL,
    status VARCHAR(20) DEFAULT 'claimed', -- claimed, redeemed, expired
    claimed_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,
    redeemed_at TIMESTAMP,
    device_id VARCHAR(255),
    ip_address VARCHAR(45),
    UNIQUE KEY unique_user_claim (user_id),
    INDEX idx_user_id (user_id),
    INDEX idx_redemption_code (redemption_code),
    INDEX idx_status (status)
);
```

### Inventory Table

```sql
CREATE TABLE inventory (
    burger_id BIGSERIAL PRIMARY KEY,
    restaurant_id BIGINT,
    location_id BIGINT,
    status VARCHAR(20) DEFAULT 'available', -- available, claimed, allocated
    allocated_at TIMESTAMP,
    INDEX idx_status (status),
    INDEX idx_restaurant (restaurant_id)
);
```

### Users Table

```sql
CREATE TABLE users (
    user_id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    device_id VARCHAR(255),
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_email (email),
    INDEX idx_device (device_id)
);
```

---

## API Design

### Claim API

```
POST /api/v1/burgers/claim
Headers:
  Authorization: Bearer {token}
  X-Device-ID: {device_id}

{
  "location_id": 123,
  "restaurant_preference": 456
}
```

**Response:**
```json
{
  "claim_id": "claim_123",
  "redemption_code": "BURGER-ABC123-XYZ789",
  "restaurant": {
    "id": 456,
    "name": "Burger Palace",
    "address": "123 Main St"
  },
  "expires_at": "2024-01-15T12:00:00Z",
  "instructions": "Show this code at the restaurant"
}
```

### Availability API

```
GET /api/v1/burgers/availability?location_id=123
```

**Response:**
```json
{
  "available": true,
  "remaining": 50000,
  "total": 6000000,
  "claimed": 5950000
}
```

---

## Claim Flow

### Claim Process

1. **User requests claim**
2. **Rate limiting check** (per user, per IP)
3. **Fraud detection** (duplicate user, device, IP)
4. **Inventory check** (available burgers)
5. **Atomic claim** (database transaction)
6. **Generate redemption code**
7. **Allocate to restaurant**
8. **Send notification**
9. **Update availability cache**

### Atomic Claim Implementation

```python
def claim_burger(user_id: int, location_id: int) -> dict:
    with db.transaction():
        # Check if user already claimed
        existing_claim = db.query(
            "SELECT claim_id FROM claims WHERE user_id = %s",
            (user_id,)
        )
        if existing_claim:
            raise AlreadyClaimedError()
        
        # Get available burger
        burger = db.query(
            "SELECT burger_id FROM inventory WHERE status = 'available' LIMIT 1 FOR UPDATE"
        )
        if not burger:
            raise OutOfStockError()
        
        # Update inventory
        db.execute(
            "UPDATE inventory SET status = 'claimed' WHERE burger_id = %s",
            (burger.burger_id,)
        )
        
        # Create claim
        redemption_code = generate_code()
        claim_id = db.execute(
            "INSERT INTO claims (user_id, burger_id, redemption_code) VALUES (%s, %s, %s)",
            (user_id, burger.burger_id, redemption_code)
        )
        
        return {
            "claim_id": claim_id,
            "redemption_code": redemption_code
        }
```

---

## Rate Limiting & Throttling

### Multi-Level Rate Limiting

```python
class RateLimiter:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def check_rate_limit(self, user_id: int, ip_address: str) -> bool:
        # Per-user limit: 1 claim
        user_key = f"claim:user:{user_id}"
        if self.redis.exists(user_key):
            return False
        
        # Per-IP limit: 5 claims per hour
        ip_key = f"claim:ip:{ip_address}"
        ip_count = self.redis.incr(ip_key)
        if ip_count == 1:
            self.redis.expire(ip_key, 3600)
        if ip_count > 5:
            return False
        
        # Global limit: 5000 claims/second
        global_key = "claim:global"
        global_count = self.redis.incr(global_key)
        if global_count == 1:
            self.redis.expire(global_key, 1)
        if global_count > 5000:
            return False
        
        return True
```

---

## Scalability Considerations

- **Horizontal Scaling**: Multiple claim service instances
- **Database Sharding**: Shard by user_id or location_id
- **Caching**: Cache availability counts (Redis)
- **Queue Processing**: Async processing for non-critical operations
- **Geographic Distribution**: Route by location

---

## Caching Strategy

- **Availability Cache**: Cache remaining count (TTL: 1 second)
- **User Claims Cache**: Cache user claim status (TTL: 1 hour)
- **Rate Limit Cache**: Track rate limits (Redis)

---

## Capacity Planning

- **Total Burgers**: 6M
- **Time Window**: 1 hour = 3,600 seconds
- **Average Rate**: 6M / 3,600 = 1,667 claims/second
- **Peak Rate**: 3x average = 5,000 claims/second
- **Concurrent Users**: 100K+
- **Database**: 10M+ rows (claims + inventory)

---

## Technology Stack

- **Backend**: Go, Java
- **Database**: PostgreSQL (with sharding)
- **Cache**: Redis Cluster
- **Queue**: Kafka
- **Load Balancer**: NGINX, AWS ALB

---

## Interview Discussion Points

1. **High Concurrency**: How do you handle 5K+ claims/second?
2. **Fairness**: How do you ensure fair distribution?
3. **Fraud Prevention**: How do you prevent abuse?
4. **Inventory Management**: How do you track 6M burgers?

---

**Document Version**: 1.0  
**Last Updated**: January 2024

