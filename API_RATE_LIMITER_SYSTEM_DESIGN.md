# API Rate Limiter System Design

## Table of Contents
1. [Overview](#overview)
2. [Requirements](#requirements)
3. [High-Level Design (HLD)](#high-level-design-hld)
4. [Low-Level Design (LLD)](#low-level-design-lld)
5. [System Architecture](#system-architecture)
6. [Database Design](#database-design)
7. [API Design](#api-design)
8. [Rate Limiting Algorithms](#rate-limiting-algorithms)
9. [Distributed Rate Limiting](#distributed-rate-limiting)
10. [Fault Tolerance](#fault-tolerance)
11. [Failure Safety](#failure-safety)
12. [Scalability Considerations](#scalability-considerations)
13. [Optimizations](#optimizations)
14. [Caching Strategy](#caching-strategy)
15. [Load Balancing](#load-balancing)
16. [Security](#security)
17. [Monitoring & Analytics](#monitoring--analytics)
18. [Deployment Strategy](#deployment-strategy)
19. [Capacity Planning](#capacity-planning)
20. [Technology Stack](#technology-stack)
21. [Failure Scenarios & Handling](#failure-scenarios--handling)
22. [Trade-offs & Design Decisions](#trade-offs--design-decisions)
23. [Interview Discussion Points](#interview-discussion-points)

---

## Overview

A distributed API rate limiting system that controls the rate of requests from clients. The system must handle millions of requests per second, support multiple rate limiting algorithms, provide low-latency decisions, and scale horizontally.

**Key Features:**
- Multiple rate limiting algorithms (Token Bucket, Sliding Window, Fixed Window)
- Per-user, per-IP, per-API key rate limiting
- Distributed rate limiting across multiple servers
- Low-latency rate limit checks (< 1ms)
- Configurable rate limits
- Rate limit headers in responses
- Graceful degradation

---

## Requirements

### Functional Requirements

1. **Rate Limit Enforcement**
   - Check rate limit before processing request
   - Support multiple algorithms
   - Return rate limit status

2. **Rate Limit Types**
   - Per-user rate limiting
   - Per-IP rate limiting
   - Per-API key rate limiting
   - Per-endpoint rate limiting
   - Global rate limiting

3. **Rate Limit Algorithms**
   - Token Bucket
   - Sliding Window Log
   - Fixed Window Counter
   - Sliding Window Counter

4. **Rate Limit Headers**
   - X-RateLimit-Limit
   - X-RateLimit-Remaining
   - X-RateLimit-Reset
   - Retry-After (when exceeded)

5. **Configuration**
   - Dynamic rate limit configuration
   - Per-endpoint limits
   - Per-user tier limits
   - Override capabilities

### Non-Functional Requirements

1. **Scalability**
   - Handle 10M+ requests/second
   - Support millions of users
   - Horizontal scaling

2. **Performance**
   - Rate limit check: < 1ms latency (p99)
   - Minimal overhead on request processing
   - High throughput

3. **Accuracy**
   - Accurate rate limit tracking
   - Handle concurrent requests
   - No race conditions

4. **Availability**
   - 99.9% uptime
   - Graceful degradation on failure
   - No single point of failure

5. **Consistency**
   - Consistent rate limiting across servers
   - Handle distributed systems challenges

---

## High-Level Design (HLD)

### System Overview

The API Rate Limiter is a distributed, high-performance system designed to enforce rate limits across multiple servers and regions. The architecture follows a microservices pattern with centralized state management and local caching for optimal performance.

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           API Clients                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 │
│  │ Mobile Apps  │  │  Web Apps    │  │  API Clients │                 │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                 │
└─────────┼─────────────────┼─────────────────┼──────────────────────────┘
          │                 │                 │
          └─────────────────┴─────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    API Gateway / Load Balancer                          │
│  - Request routing                                                      │
│  - SSL termination                                                      │
│  - Initial rate limit check (coarse-grained)                           │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│   Region 1    │    │   Region 2    │    │   Region N    │
│  (US-East)    │    │  (EU-West)    │    │  (AP-South)   │
└───────┬───────┘    └───────┬───────┘    └───────┬───────┘
        │                    │                    │
        ▼                    ▼                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    Rate Limiter Service Layer                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │ Rate Limit   │  │ Rate Limit   │  │ Rate Limit   │               │
│  │  Checker     │  │  Enforcer    │  │  Reporter    │               │
│  └──────────────┘  └──────────────┘  └──────────────┘               │
└─────────────────────────────────────────────────────────────────────────┘
        │                    │                    │
        ▼                    ▼                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    Algorithm Engine Layer                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │ Token Bucket │  │ Sliding      │  │ Fixed Window │               │
│  │  Algorithm   │  │  Window      │  │  Algorithm   │               │
│  └──────────────┘  └──────────────┘  └──────────────┘               │
└─────────────────────────────────────────────────────────────────────────┘
        │                    │                    │
        ▼                    ▼                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    Configuration Service                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │ Rule         │  │ Rule Cache   │  │ Rule         │               │
│  │  Manager     │  │  Manager     │  │  Validator   │               │
│  └──────────────┘  └──────────────┘  └──────────────┘               │
└─────────────────────────────────────────────────────────────────────────┘
        │                    │                    │
        ▼                    ▼                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         Data Layer                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │ Redis        │  │ PostgreSQL   │  │ Local Cache  │               │
│  │ Cluster      │  │ (Config)     │  │ (In-Memory)  │               │
│  └──────────────┘  └──────────────┘  └──────────────┘               │
└─────────────────────────────────────────────────────────────────────────┘
```

### Key Components

1. **API Gateway**: Entry point, performs initial coarse-grained rate limiting
2. **Rate Limiter Service**: Core service for rate limit checks and enforcement
3. **Algorithm Engine**: Implements different rate limiting algorithms
4. **Configuration Service**: Manages rate limit rules and configurations
5. **Data Layer**: Redis for counters, PostgreSQL for config, local cache for performance

### Design Principles

- **Performance First**: Sub-millisecond latency for rate limit checks
- **Distributed Consistency**: Consistent rate limiting across all servers
- **Graceful Degradation**: Fail open when rate limiter is unavailable
- **Scalability**: Horizontal scaling with no single point of failure
- **Flexibility**: Support multiple algorithms and rate limit types

---

## Low-Level Design (LLD)

### Rate Limiter Service (Detailed)

```python
class RateLimiterService:
    def __init__(self):
        self.redis = RedisCluster()
        self.local_cache = LocalCache(max_size=10000, ttl=1)
        self.config_service = ConfigurationService()
        self.algorithm_factory = AlgorithmFactory()
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=10,
            recovery_timeout=30
        )
        self.metrics = MetricsCollector()
    
    async def check_rate_limit(
        self, 
        identifier_type: str,
        identifier_value: str,
        endpoint: str,
        method: str = "GET"
    ) -> RateLimitResult:
        try:
            # Step 1: Get rate limit rule
            rule = await self.get_rate_limit_rule(
                identifier_type, identifier_value, endpoint
            )
            
            if not rule:
                # No rule found, allow request
                return RateLimitResult(allowed=True)
            
            # Step 2: Check local cache first
            cache_key = f"{identifier_type}:{identifier_value}:{endpoint}"
            cached_result = self.local_cache.get(cache_key)
            if cached_result and cached_result['expires_at'] > time.time():
                return cached_result['result']
            
            # Step 3: Get algorithm instance
            algorithm = self.algorithm_factory.create(rule['algorithm'])
            
            # Step 4: Check rate limit
            result = await algorithm.check(
                identifier=identifier_value,
                endpoint=endpoint,
                limit=rule['limit_value'],
                window=rule['window_seconds'],
                burst=rule.get('burst_size')
            )
            
            # Step 5: Cache result locally
            self.local_cache.set(cache_key, {
                'result': result,
                'expires_at': time.time() + 1  # 1 second TTL
            })
            
            # Step 6: Record metrics
            self.metrics.record_rate_limit_check(
                identifier_type, endpoint, result.allowed
            )
            
            return result
            
        except Exception as e:
            self.metrics.record_error(e)
            # Fail open - allow request
            return RateLimitResult(allowed=True, error=str(e))
    
    async def get_rate_limit_rule(
        self, identifier_type: str, identifier_value: str, endpoint: str
    ) -> Optional[dict]:
        # Check cache first
        cache_key = f"rule:{identifier_type}:{identifier_value}:{endpoint}"
        cached_rule = await self.redis.get(cache_key)
        if cached_rule:
            return cached_rule
        
        # Query configuration service
        rule = await self.config_service.get_rule(
            identifier_type, identifier_value, endpoint
        )
        
        if rule:
            # Cache rule for 5 minutes
            await self.redis.set(cache_key, rule, ttl=300)
        
        return rule
```

### Algorithm Factory

```python
class AlgorithmFactory:
    def __init__(self):
        self.redis = RedisCluster()
    
    def create(self, algorithm_type: str) -> RateLimitAlgorithm:
        if algorithm_type == 'token_bucket':
            return TokenBucketAlgorithm(self.redis)
        elif algorithm_type == 'sliding_window':
            return SlidingWindowAlgorithm(self.redis)
        elif algorithm_type == 'fixed_window':
            return FixedWindowAlgorithm(self.redis)
        elif algorithm_type == 'sliding_window_counter':
            return SlidingWindowCounterAlgorithm(self.redis)
        else:
            raise ValueError(f"Unknown algorithm: {algorithm_type}")
```

### Token Bucket Algorithm (Detailed)

```python
class TokenBucketAlgorithm(RateLimitAlgorithm):
    def __init__(self, redis: RedisCluster):
        self.redis = redis
    
    async def check(
        self, identifier: str, endpoint: str, limit: int, 
        window: int, burst: int = None
    ) -> RateLimitResult:
        key = f"tokenbucket:{identifier}:{endpoint}"
        capacity = burst or limit
        refill_rate = limit / window
        
        # Use Lua script for atomicity
        lua_script = """
        local key = KEYS[1]
        local capacity = tonumber(ARGV[1])
        local refill_rate = tonumber(ARGV[2])
        local now = tonumber(ARGV[3])
        local window = tonumber(ARGV[4])
        
        local bucket = redis.call('HMGET', key, 'tokens', 'last_refill')
        local tokens = tonumber(bucket[1])
        local last_refill = tonumber(bucket[2])
        
        -- Initialize if not exists
        if not tokens then
            tokens = capacity
            last_refill = now
        end
        
        -- Refill tokens
        local elapsed = now - last_refill
        local tokens_to_add = elapsed * refill_rate
        tokens = math.min(capacity, tokens + tokens_to_add)
        last_refill = now
        
        -- Consume token
        local allowed = 0
        local remaining = math.floor(tokens)
        
        if tokens >= 1 then
            tokens = tokens - 1
            allowed = 1
            remaining = math.floor(tokens)
        end
        
        -- Update bucket
        redis.call('HMSET', key, 'tokens', tokens, 'last_refill', last_refill)
        redis.call('EXPIRE', key, window)
        
        -- Return result
        return {allowed, remaining, now + window}
        """
        
        result = await self.redis.eval(
            lua_script, 
            keys=[key],
            args=[capacity, refill_rate, int(time.time()), window]
        )
        
        return RateLimitResult(
            allowed=result[0] == 1,
            limit=limit,
            remaining=int(result[1]),
            reset_at=int(result[2])
        )
```

### Configuration Service (Detailed)

```python
class ConfigurationService:
    def __init__(self):
        self.db = DatabasePool()
        self.cache = RedisCache()
        self.rule_cache = LocalCache(max_size=10000, ttl=300)
    
    async def get_rule(
        self, identifier_type: str, identifier_value: str, endpoint: str
    ) -> Optional[dict]:
        # Check local cache
        cache_key = f"{identifier_type}:{identifier_value}:{endpoint}"
        cached = self.rule_cache.get(cache_key)
        if cached:
            return cached
        
        # Check Redis cache
        redis_key = f"rule:{cache_key}"
        redis_cached = await self.cache.get(redis_key)
        if redis_cached:
            self.rule_cache.set(cache_key, redis_cached)
            return redis_cached
        
        # Query database
        rule = await self.db.query(
            """
            SELECT * FROM rate_limit_rules
            WHERE identifier_type = %s
            AND (identifier_value = %s OR identifier_value IS NULL)
            AND (endpoint = %s OR endpoint IS NULL)
            AND is_active = TRUE
            ORDER BY 
                CASE WHEN identifier_value IS NOT NULL THEN 1 ELSE 2 END,
                CASE WHEN endpoint IS NOT NULL THEN 1 ELSE 2 END
            LIMIT 1
            """,
            (identifier_type, identifier_value, endpoint)
        )
        
        if rule:
            # Cache in both Redis and local cache
            await self.cache.set(redis_key, rule, ttl=300)
            self.rule_cache.set(cache_key, rule)
        
        return rule
```

### Circuit Breaker Implementation

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=10, recovery_timeout=30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'closed'  # closed, open, half_open
    
    def is_open(self) -> bool:
        if self.state == 'open':
            # Check if recovery timeout has passed
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = 'half_open'
                self.failure_count = 0
                return False
            return True
        return False
    
    def record_success(self):
        if self.state == 'half_open':
            self.state = 'closed'
        self.failure_count = 0
    
    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'open'
```

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    API Clients                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Client 1 │  │ Client 2 │  │ Client 3 │  │ Client N │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼───────────┘
        │             │             │             │
        └─────────────┴─────────────┴─────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│              API Gateway / Load Balancer                    │
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
│              Rate Limiter Service Layer                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │Rate      │  │Rate      │  │Rate      │  │Rate      │   │
│  │Limiter 1 │  │Limiter 2 │  │Limiter 3 │  │Limiter N │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼───────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│              Distributed Cache (Redis)                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Redis   │  │  Redis   │  │  Redis   │  │  Redis   │   │
│  │ Cluster  │  │ Cluster  │  │ Cluster  │  │ Cluster  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼───────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│              Configuration Service                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │Config    │  │Config    │  │Config    │  │Config    │   │
│  │Service   │  │Service   │  │Service   │  │Service   │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼───────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│              Database (PostgreSQL)                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │PostgreSQL│  │PostgreSQL│  │PostgreSQL│  │PostgreSQL│   │
│  │(Config) │  │(Config)  │  │(Config)  │  │(Config)  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Component Details

#### 1. Rate Limiter Service
- **Responsibilities**:
  - Check rate limits
  - Update rate limit counters
  - Return rate limit status
  - Add rate limit headers

#### 2. Distributed Cache (Redis)
- **Responsibilities**:
  - Store rate limit counters
  - Atomic operations
  - TTL management
  - Shared state across servers

#### 3. Configuration Service
- **Responsibilities**:
  - Manage rate limit rules
  - Per-user, per-endpoint limits
  - Dynamic configuration updates

#### 4. Database (PostgreSQL)
- **Responsibilities**:
  - Store rate limit configurations
  - User tier information
  - Historical rate limit data

---

## Database Design

### PostgreSQL Schema

#### Rate Limit Rules Table
```sql
CREATE TABLE rate_limit_rules (
    id BIGSERIAL PRIMARY KEY,
    identifier_type VARCHAR(50) NOT NULL,  -- 'user_id', 'ip', 'api_key', 'endpoint'
    identifier_value VARCHAR(255),
    endpoint VARCHAR(255),
    algorithm VARCHAR(50) NOT NULL,  -- 'token_bucket', 'sliding_window', 'fixed_window'
    limit_value INT NOT NULL,  -- Requests per window
    window_seconds INT NOT NULL,  -- Window size in seconds
    burst_size INT,  -- For token bucket
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_identifier (identifier_type, identifier_value),
    INDEX idx_endpoint (endpoint),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB;
```

#### User Tiers Table
```sql
CREATE TABLE user_tiers (
    user_id VARCHAR(255) PRIMARY KEY,
    tier_name VARCHAR(50) NOT NULL,  -- 'free', 'pro', 'enterprise'
    rate_limit_rule_id BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (rate_limit_rule_id) REFERENCES rate_limit_rules(id),
    INDEX idx_tier (tier_name)
) ENGINE=InnoDB;
```

#### Rate Limit Overrides Table
```sql
CREATE TABLE rate_limit_overrides (
    id BIGSERIAL PRIMARY KEY,
    identifier_type VARCHAR(50) NOT NULL,
    identifier_value VARCHAR(255) NOT NULL,
    endpoint VARCHAR(255),
    limit_value INT NOT NULL,
    window_seconds INT NOT NULL,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_override (identifier_type, identifier_value, endpoint),
    INDEX idx_expires_at (expires_at)
) ENGINE=InnoDB;
```

### Redis Schema

#### Rate Limit Counters
```
Key: ratelimit:{identifier_type}:{identifier_value}:{endpoint}:{window}
Type: String (Integer) or Hash
Value: Current count or token bucket state
TTL: Window duration + buffer
```

**Example:**
```redis
Key: ratelimit:user_id:user_123:/api/v1/posts:60
Value: 45  # Current count
TTL: 60 seconds
```

#### Token Bucket State
```
Key: tokenbucket:{identifier_type}:{identifier_value}:{endpoint}
Type: Hash
Fields:
  - tokens: Current token count
  - last_refill: Last refill timestamp
TTL: Window duration + buffer
```

---

## API Design

### Rate Limit Check (Internal)

**Check Rate Limit**
```
POST /api/v1/ratelimit/check
Content-Type: application/json

Request:
{
    "identifier_type": "user_id",
    "identifier_value": "user_123",
    "endpoint": "/api/v1/posts",
    "method": "GET"
}

Response:
{
    "allowed": true,
    "limit": 100,
    "remaining": 55,
    "reset_at": 1609459260,
    "retry_after": null
}
```

**Response when Rate Limited:**
```
{
    "allowed": false,
    "limit": 100,
    "remaining": 0,
    "reset_at": 1609459260,
    "retry_after": 60
}
```

### Configuration API

**Create Rate Limit Rule**
```
POST /api/v1/admin/ratelimit/rules
Content-Type: application/json

Request:
{
    "identifier_type": "user_id",
    "identifier_value": "user_123",
    "endpoint": "/api/v1/posts",
    "algorithm": "token_bucket",
    "limit": 100,
    "window_seconds": 60,
    "burst_size": 10
}

Response:
{
    "success": true,
    "rule_id": "rule_123"
}
```

**Get Rate Limit Status**
```
GET /api/v1/ratelimit/status?identifier_type=user_id&identifier_value=user_123&endpoint=/api/v1/posts

Response:
{
    "identifier": "user_123",
    "endpoint": "/api/v1/posts",
    "limit": 100,
    "remaining": 55,
    "reset_at": 1609459260,
    "algorithm": "token_bucket"
}
```

---

## Data Flow Diagrams

### Rate Limit Check Flow

```
API Request Received
    │
    ▼
API Gateway / Middleware
    │
    ├─ Extract Identifier (user_id, IP, API key)
    ├─ Extract Endpoint
    │
    ▼
Rate Limiter Service
    │
    ├─ Get Rate Limit Rule
    │   │
    │   ▼
    │   Configuration Service
    │   │
    │   ├─ Check Cache (Redis)
    │   │   └─ Cache Hit → Return Rule
    │   │
    │   └─ Cache Miss → Query Database
    │       │
    │       └─ Cache Rule
    │
    ▼
Check Rate Limit (Based on Algorithm)
    │
    ├─ Token Bucket Algorithm
    │   ├─ Check Redis: tokenbucket:{identifier}:{endpoint}
    │   ├─ Refill Tokens (if needed)
    │   ├─ Consume Token (if available)
    │   └─ Update Redis
    │
    ├─ Sliding Window Algorithm
    │   ├─ Check Redis: ratelimit:{identifier}:{endpoint}:{window}
    │   ├─ Get Current Count
    │   ├─ Increment Count (if under limit)
    │   └─ Update Redis
    │
    └─ Fixed Window Algorithm
        ├─ Check Redis: ratelimit:{identifier}:{endpoint}:{window_start}
        ├─ Get Current Count
        ├─ Increment Count (if under limit)
        └─ Update Redis
    │
    ▼
Return Rate Limit Decision
    │
    ├─ Allowed → Process Request
    │   └─ Add Rate Limit Headers
    │
    └─ Rate Limited → Return 429 Too Many Requests
        └─ Add Retry-After Header
```

---

## Rate Limiting Algorithms

### 1. Token Bucket Algorithm

**How it Works:**
- Bucket has capacity (burst size)
- Tokens added at fixed rate
- Request consumes one token
- Request allowed if tokens available

**Advantages:**
- Allows bursts
- Smooth rate limiting
- Good for variable traffic

**Implementation:**
```python
class TokenBucket:
    def __init__(self, capacity, refill_rate):
        self.capacity = capacity  # Maximum tokens
        self.refill_rate = refill_rate  # Tokens per second
        self.tokens = capacity
        self.last_refill = time.time()
    
    def consume(self, tokens=1):
        # Refill tokens
        now = time.time()
        elapsed = now - self.last_refill
        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now
        
        # Consume tokens
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False
```

**Redis Implementation:**
```python
def check_token_bucket(identifier, endpoint, limit, window, burst):
    key = f"tokenbucket:{identifier}:{endpoint}"
    
    # Use Lua script for atomicity
    lua_script = """
    local key = KEYS[1]
    local capacity = tonumber(ARGV[1])
    local refill_rate = tonumber(ARGV[2])
    local now = tonumber(ARGV[3])
    
    local bucket = redis.call('HMGET', key, 'tokens', 'last_refill')
    local tokens = tonumber(bucket[1]) or capacity
    local last_refill = tonumber(bucket[2]) or now
    
    -- Refill tokens
    local elapsed = now - last_refill
    local tokens_to_add = elapsed * refill_rate
    tokens = math.min(capacity, tokens + tokens_to_add)
    
    -- Consume token
    if tokens >= 1 then
        tokens = tokens - 1
        redis.call('HMSET', key, 'tokens', tokens, 'last_refill', now)
        redis.call('EXPIRE', key, window)
        return {1, tokens, now + window}  -- allowed, remaining, reset_at
    else
        redis.call('HMSET', key, 'tokens', tokens, 'last_refill', now)
        redis.call('EXPIRE', key, window)
        return {0, 0, now + window}  -- not allowed, remaining, reset_at
    end
    """
    
    result = redis.eval(lua_script, 1, key, burst, limit/window, int(time.time()))
    return {
        'allowed': result[0] == 1,
        'remaining': int(result[1]),
        'reset_at': result[2]
    }
```

### 2. Sliding Window Log Algorithm

**How it Works:**
- Track timestamps of requests
- Count requests in sliding window
- Allow if count < limit

**Advantages:**
- Accurate
- No bursts at window boundaries

**Disadvantages:**
- Memory intensive (stores all timestamps)
- Slower for high cardinality

**Implementation:**
```python
class SlidingWindowLog:
    def __init__(self, limit, window_seconds):
        self.limit = limit
        self.window_seconds = window_seconds
        self.requests = []  # List of timestamps
    
    def is_allowed(self):
        now = time.time()
        window_start = now - self.window_seconds
        
        # Remove old requests
        self.requests = [t for t in self.requests if t > window_start]
        
        # Check limit
        if len(self.requests) < self.limit:
            self.requests.append(now)
            return True
        return False
```

**Redis Implementation:**
```python
def check_sliding_window_log(identifier, endpoint, limit, window):
    key = f"ratelimit:sliding:{identifier}:{endpoint}"
    now = time.time()
    window_start = now - window
    
    # Use sorted set to store timestamps
    # Remove old entries
    redis.zremrangebyscore(key, 0, window_start)
    
    # Count current requests
    count = redis.zcard(key)
    
    if count < limit:
        # Add current request
        redis.zadd(key, {str(now): now})
        redis.expire(key, window)
        return {
            'allowed': True,
            'remaining': limit - count - 1,
            'reset_at': int(now + window)
        }
    else:
        # Get oldest request to calculate reset time
        oldest = redis.zrange(key, 0, 0, withscores=True)
        reset_at = int(oldest[0][1] + window) if oldest else int(now + window)
        return {
            'allowed': False,
            'remaining': 0,
            'reset_at': reset_at
        }
```

### 3. Fixed Window Counter Algorithm

**How it Works:**
- Divide time into fixed windows
- Count requests per window
- Reset counter at window boundary

**Advantages:**
- Simple
- Memory efficient
- Fast

**Disadvantages:**
- Bursts at window boundaries
- Less accurate

**Implementation:**
```python
class FixedWindowCounter:
    def __init__(self, limit, window_seconds):
        self.limit = limit
        self.window_seconds = window_seconds
        self.window_start = int(time.time() // window_seconds) * window_seconds
        self.count = 0
    
    def is_allowed(self):
        now = time.time()
        current_window = int(now // self.window_seconds) * window_seconds
        
        # Reset if new window
        if current_window > self.window_start:
            self.window_start = current_window
            self.count = 0
        
        # Check limit
        if self.count < self.limit:
            self.count += 1
            return True
        return False
```

**Redis Implementation:**
```python
def check_fixed_window(identifier, endpoint, limit, window):
    now = time.time()
    window_start = int(now // window) * window
    key = f"ratelimit:fixed:{identifier}:{endpoint}:{window_start}"
    
    # Increment counter
    count = redis.incr(key)
    redis.expire(key, window)
    
    if count <= limit:
        return {
            'allowed': True,
            'remaining': limit - count,
            'reset_at': window_start + window
        }
    else:
        return {
            'allowed': False,
            'remaining': 0,
            'reset_at': window_start + window
        }
```

### 4. Sliding Window Counter Algorithm

**How it Works:**
- Combine fixed windows
- Weighted average of overlapping windows
- More accurate than fixed window

**Advantages:**
- More accurate than fixed window
- Less memory than sliding window log
- Good balance

**Implementation:**
```python
def check_sliding_window_counter(identifier, endpoint, limit, window):
    now = time.time()
    current_window = int(now // window) * window
    previous_window = current_window - window
    
    current_key = f"ratelimit:sliding_counter:{identifier}:{endpoint}:{current_window}"
    previous_key = f"ratelimit:sliding_counter:{identifier}:{endpoint}:{previous_window}"
    
    # Get counts
    current_count = int(redis.get(current_key) or 0)
    previous_count = int(redis.get(previous_key) or 0)
    
    # Calculate weighted count
    elapsed = now - current_window
    weight = elapsed / window
    estimated_count = current_count + (previous_count * (1 - weight))
    
    if estimated_count < limit:
        redis.incr(current_key)
        redis.expire(current_key, window * 2)
        return {
            'allowed': True,
            'remaining': int(limit - estimated_count - 1),
            'reset_at': current_window + window
        }
    else:
        return {
            'allowed': False,
            'remaining': 0,
            'reset_at': current_window + window
        }
```

---

## Distributed Rate Limiting

### Challenge: Consistency Across Servers

**Problem:** Multiple servers need consistent rate limiting.

**Solutions:**

1. **Centralized Redis:**
   - All servers use same Redis
   - Atomic operations ensure consistency
   - Single point of failure (mitigated by Redis cluster)

2. **Distributed Locks:**
   - Use Redis distributed locks
   - Slower but more consistent
   - Good for critical rate limits

3. **Local + Distributed:**
   - Local cache for fast path
   - Redis for distributed coordination
   - Best of both worlds

### Implementation

```python
class DistributedRateLimiter:
    def __init__(self, redis_client, local_cache):
        self.redis = redis_client
        self.local_cache = local_cache  # Local cache for fast path
        self.local_cache_ttl = 1  # 1 second
    
    def check_rate_limit(self, identifier, endpoint, limit, window):
        cache_key = f"{identifier}:{endpoint}"
        
        # Check local cache first
        cached = self.local_cache.get(cache_key)
        if cached and cached['expires_at'] > time.time():
            return cached['result']
        
        # Check Redis (distributed)
        result = self.check_redis(identifier, endpoint, limit, window)
        
        # Cache locally
        self.local_cache.set(cache_key, {
            'result': result,
            'expires_at': time.time() + self.local_cache_ttl
        })
        
        return result
```

---

## Fault Tolerance

### Fault Tolerance Strategy

The rate limiter is designed to handle failures gracefully, ensuring that rate limiting failures don't break the main application.

### Component-Level Fault Tolerance

#### 1. Redis Failure Tolerance

**Failure Scenarios:**
- Redis cluster node failure
- Network partition
- Redis cluster unavailable
- High latency

**Mitigation Strategies:**

```python
class FaultTolerantRedis:
    def __init__(self):
        self.redis_cluster = RedisCluster()
        self.local_cache = LocalCache(max_size=50000, ttl=1)
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60
        )
        self.fallback_cache = FallbackCache()
    
    async def get(self, key: str) -> Optional[dict]:
        # Try local cache first
        local_value = self.local_cache.get(key)
        if local_value:
            return local_value
        
        # Try Redis if circuit breaker is closed
        if not self.circuit_breaker.is_open():
            try:
                value = await asyncio.wait_for(
                    self.redis_cluster.get(key),
                    timeout=0.01  # 10ms timeout
                )
                if value:
                    self.local_cache.set(key, value, ttl=1)
                    self.circuit_breaker.record_success()
                    return value
            except (asyncio.TimeoutError, ConnectionError, Exception) as e:
                self.circuit_breaker.record_failure()
        
        # Fallback to distributed cache (if available)
        return await self.fallback_cache.get(key)
    
    async def set(self, key: str, value: dict, ttl: int):
        # Always update local cache
        self.local_cache.set(key, value, ttl=min(ttl, 1))
        
        # Try Redis if circuit breaker is closed
        if not self.circuit_breaker.is_open():
            try:
                await asyncio.wait_for(
                    self.redis_cluster.set(key, value, ttl=ttl),
                    timeout=0.01
                )
                self.circuit_breaker.record_success()
            except Exception as e:
                self.circuit_breaker.record_failure()
```

**Fallback Mechanisms:**
- **Local Cache**: In-memory cache for recent decisions
- **Circuit Breaker**: Fail fast when Redis is down
- **Fail Open**: Allow requests when rate limiter unavailable
- **Fallback Cache**: Distributed cache alternative (if available)

#### 2. Database Failure Tolerance

**PostgreSQL (Configuration DB):**
- **Primary-Replica Setup**: Read from replicas, write to primary
- **Connection Pooling**: Handle connection failures
- **Query Timeout**: Fail fast on slow queries
- **Cached Rules**: Cache rules to reduce DB dependency

```python
class FaultTolerantDatabase:
    def __init__(self):
        self.primary = DatabaseConnection(primary_config)
        self.replicas = [DatabaseConnection(r) for r in replica_configs]
        self.replica_index = 0
        self.health_checker = HealthChecker()
        self.rule_cache = LocalCache(max_size=10000, ttl=300)
    
    async def get_rate_limit_rule(self, rule_id: int) -> Optional[dict]:
        # Check cache first
        cached = self.rule_cache.get(f"rule:{rule_id}")
        if cached:
            return cached
        
        # Try replicas
        for _ in range(len(self.replicas)):
            replica = self.replicas[self.replica_index]
            self.replica_index = (self.replica_index + 1) % len(self.replicas)
            
            if self.health_checker.is_healthy(replica):
                try:
                    rule = await asyncio.wait_for(
                        replica.query("SELECT * FROM rate_limit_rules WHERE id = %s", (rule_id,)),
                        timeout=0.1
                    )
                    if rule:
                        self.rule_cache.set(f"rule:{rule_id}", rule)
                        return rule
                except Exception:
                    continue
        
        # Fallback to primary
        try:
            rule = await self.primary.query(
                "SELECT * FROM rate_limit_rules WHERE id = %s", (rule_id,)
            )
            if rule:
                self.rule_cache.set(f"rule:{rule_id}", rule)
            return rule
        except Exception:
            # Return None - will use default behavior
            return None
```

#### 3. Service-Level Fault Tolerance

**Rate Limiter Service:**
- **Health Checks**: Continuous health monitoring
- **Graceful Shutdown**: Finish in-flight requests
- **Circuit Breakers**: Prevent cascading failures
- **Retry Logic**: Exponential backoff for transient failures

```python
class FaultTolerantRateLimiter:
    def __init__(self):
        self.redis = FaultTolerantRedis()
        self.db = FaultTolerantDatabase()
        self.circuit_breaker = CircuitBreaker()
        self.health_status = 'healthy'
    
    async def check_rate_limit(self, request: RateLimitRequest) -> RateLimitResult:
        # Health check
        if not self.is_healthy():
            # Fail open - allow request
            return RateLimitResult(allowed=True, reason='service_unhealthy')
        
        try:
            # Check circuit breaker
            if self.circuit_breaker.is_open():
                return RateLimitResult(allowed=True, reason='circuit_open')
            
            # Perform rate limit check
            result = await self.perform_check(request)
            
            self.circuit_breaker.record_success()
            return result
            
        except Exception as e:
            self.circuit_breaker.record_failure()
            # Fail open
            return RateLimitResult(allowed=True, reason='error', error=str(e))
    
    def is_healthy(self) -> bool:
        # Check dependencies
        redis_healthy = self.redis.is_healthy()
        db_healthy = self.db.is_healthy()
        
        self.health_status = 'healthy' if (redis_healthy and db_healthy) else 'unhealthy'
        return self.health_status == 'healthy'
```

### System-Level Fault Tolerance

#### 1. Fail-Open Strategy

**Decision:** Fail open (allow requests) when rate limiter fails.

**Rationale:**
- Rate limiting is a protective measure, not core functionality
- Better to allow requests than break the application
- Other protections (IP blocking, etc.) still active

**Implementation:**
```python
class FailOpenRateLimiter:
    async def check_rate_limit(self, request: RateLimitRequest) -> RateLimitResult:
        try:
            return await self.check_with_redis(request)
        except RedisUnavailable:
            # Fail open
            return RateLimitResult(allowed=True, reason='redis_unavailable')
        except DatabaseUnavailable:
            # Fail open
            return RateLimitResult(allowed=True, reason='db_unavailable')
        except Exception as e:
            # Log error and fail open
            logger.error(f"Rate limit check failed: {e}")
            return RateLimitResult(allowed=True, reason='unknown_error')
```

#### 2. Graceful Degradation

**Degradation Levels:**

1. **Full Functionality**: Redis and DB available
2. **Cached Rules**: Use cached rules, Redis unavailable
3. **Local Cache Only**: Use local cache, Redis and DB unavailable
4. **Fail Open**: Allow all requests

```python
class GracefulDegradation:
    async def check_rate_limit(self, request: RateLimitRequest) -> RateLimitResult:
        # Level 1: Full functionality
        try:
            return await self.full_check(request)
        except RedisUnavailable:
            # Level 2: Use cached rules
            try:
                return await self.cached_check(request)
            except CacheMiss:
                # Level 3: Local cache only
                try:
                    return await self.local_cache_check(request)
                except:
                    # Level 4: Fail open
                    return RateLimitResult(allowed=True)
```

#### 3. Health Monitoring

**Health Check Endpoints:**
- `/health`: Basic health check
- `/health/ready`: Readiness probe
- `/health/live`: Liveness probe

**Dependency Health:**
- Redis connectivity and latency
- Database connectivity
- Local cache status
- Circuit breaker state

---

## Failure Safety

### Failure Safety Principles

1. **No False Positives**: Don't block legitimate requests
2. **Fail Open**: Allow requests when rate limiter fails
3. **Data Consistency**: Rate limit counters remain consistent
4. **Audit Trail**: All failures logged for analysis

### Critical Failure Scenarios

#### 1. Race Condition Prevention

**Problem:** Concurrent requests may bypass rate limits.

**Solution:** Atomic operations using Redis Lua scripts.

```python
class RaceConditionPrevention:
    async def check_and_increment(self, key: str, limit: int, window: int) -> bool:
        # Atomic check and increment using Lua script
        lua_script = """
        local key = KEYS[1]
        local limit = tonumber(ARGV[1])
        local window = tonumber(ARGV[2])
        local now = tonumber(ARGV[3])
        
        local current = redis.call('GET', key)
        current = tonumber(current) or 0
        
        if current < limit then
            redis.call('INCR', key)
            redis.call('EXPIRE', key, window)
            return {1, current + 1}  -- allowed, new_count
        else
            return {0, current}  -- not allowed, current_count
        end
        """
        
        result = await self.redis.eval(
            lua_script,
            keys=[key],
            args=[limit, window, int(time.time())]
        )
        
        return result[0] == 1
```

#### 2. Counter Overflow Prevention

**Problem:** Counters may overflow or become inconsistent.

**Solution:** Bounded counters and validation.

```python
class CounterSafety:
    async def increment_counter(self, key: str, limit: int) -> int:
        # Use INCR with bounds check
        lua_script = """
        local key = KEYS[1]
        local limit = tonumber(ARGV[1])
        
        local current = redis.call('GET', key)
        current = tonumber(current) or 0
        
        -- Prevent overflow
        if current >= limit then
            return current
        end
        
        -- Increment
        local new_value = redis.call('INCR', key)
        
        -- Validate
        if new_value > limit * 2 then
            -- Reset if somehow exceeded
            redis.call('SET', key, limit)
            return limit
        end
        
        return new_value
        """
        
        result = await self.redis.eval(
            lua_script,
            keys=[key],
            args=[limit]
        )
        
        return int(result)
```

#### 3. Configuration Safety

**Problem:** Invalid or malicious configuration may break rate limiting.

**Solution:** Validation and sanitization.

```python
class ConfigurationSafety:
    def validate_rule(self, rule: dict) -> bool:
        # Validate limit
        if rule['limit_value'] <= 0 or rule['limit_value'] > 1000000:
            raise ValueError("Invalid limit value")
        
        # Validate window
        if rule['window_seconds'] <= 0 or rule['window_seconds'] > 86400:
            raise ValueError("Invalid window size")
        
        # Validate algorithm
        if rule['algorithm'] not in ['token_bucket', 'sliding_window', 'fixed_window']:
            raise ValueError("Invalid algorithm")
        
        # Validate burst size for token bucket
        if rule['algorithm'] == 'token_bucket':
            if 'burst_size' not in rule or rule['burst_size'] <= 0:
                raise ValueError("Burst size required for token bucket")
        
        return True
    
    async def create_rule(self, rule: dict) -> dict:
        # Validate
        self.validate_rule(rule)
        
        # Sanitize
        rule = self.sanitize_rule(rule)
        
        # Create with transaction
        async with self.db.transaction():
            rule_id = await self.db.insert('rate_limit_rules', rule)
            
            # Invalidate cache
            await self.cache.delete_pattern(f"rule:*")
            
            return {'id': rule_id, **rule}
```

#### 4. Data Loss Prevention

**Problem:** Rate limit counters lost on Redis failure.

**Solution:** Persistence and replication.

**Redis Persistence:**
- AOF (Append-Only File) enabled
- RDB snapshots for backup
- Replication to multiple nodes

**Counter Recovery:**
```python
class CounterRecovery:
    async def recover_counters(self):
        # On service restart, recover counters from backup
        # Or start fresh (acceptable for rate limiting)
        pass
    
    async def backup_counters(self):
        # Periodic backup of critical counters
        # Store in database for recovery
        pass
```

### Recovery Mechanisms

#### 1. Automatic Recovery

**Service Recovery:**
- Kubernetes health checks
- Automatic pod restart
- Gradual traffic increase

**Redis Recovery:**
- Automatic failover in cluster
- Reconnection with exponential backoff
- Cache warming after recovery

**Database Recovery:**
- Automatic failover to replica
- Connection pool recovery
- Query retry with backoff

#### 2. Manual Recovery Procedures

**Runbooks:**
- Redis cluster recovery
- Database failover procedures
- Configuration rollback
- Counter reset procedures

#### 3. Monitoring and Alerting

**Critical Alerts:**
- Redis cluster down
- Database unavailable
- High error rate
- Circuit breaker open
- Configuration errors

---

## Scalability Considerations

### Horizontal Scaling Strategy

#### 1. Stateless Services

All rate limiter services are stateless:

```python
class StatelessRateLimiter:
    def __init__(self):
        # No local state
        # All state in Redis
        self.redis = RedisCluster()
        self.local_cache = LocalCache()  # Ephemeral cache only
    
    async def check_rate_limit(self, request: RateLimitRequest) -> RateLimitResult:
        # Can run on any instance
        # No session affinity required
        return await self.process_request(request)
```

**Benefits:**
- Easy horizontal scaling
- Load balancer can route to any instance
- No session affinity required
- Easy deployment and rollback

#### 2. Redis Cluster Scaling

**Sharding Strategy:**
- Automatic sharding by hash slot
- Consistent hashing for key distribution
- Replication for high availability

**Cluster Configuration:**
```python
class RedisClusterConfig:
    def __init__(self):
        self.nodes = [
            {'host': 'redis1', 'port': 6379},
            {'host': 'redis2', 'port': 6379},
            {'host': 'redis3', 'port': 6379},
            # ... more nodes
        ]
        self.replication_factor = 2  # Each shard has 2 replicas
        self.hash_slots = 16384  # Standard Redis cluster hash slots
```

**Scaling Approach:**
- Start with 3 nodes (minimum for cluster)
- Scale to 6, 12, 24+ nodes as needed
- Add nodes without downtime (resharding)

#### 3. Database Scaling

**Read Scaling:**
- Multiple read replicas
- Read queries distributed across replicas
- Connection pooling per replica

**Write Scaling:**
- Single primary (writes are infrequent)
- Connection pooling
- Query optimization

**Partitioning (Future):**
- Partition rules table by identifier_type
- Horizontal partitioning if needed

#### 4. Load Balancing

**Load Balancer Configuration:**
- Layer 7 (HTTP) load balancing
- Health checks every 5 seconds
- Least connections algorithm
- Consistent hashing for cache affinity

**Health Check Configuration:**
```yaml
healthCheck:
  path: /health
  interval: 5s
  timeout: 1s
  healthyThreshold: 2
  unhealthyThreshold: 3
```

#### 5. Auto-Scaling

**Scaling Policies:**

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: rate-limiter-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: rate-limiter
  minReplicas: 5
  maxReplicas: 500
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  - type: Pods
    pods:
      metric:
        name: request_rate
      target:
        type: AverageValue
        averageValue: "1000"  # requests per second per pod
```

**Scaling Triggers:**
- CPU utilization > 70%
- Memory utilization > 80%
- Request rate > 1000 req/s per pod
- Request latency > 1ms (p99)

#### 6. Performance Optimization

**Connection Pooling:**
```python
class OptimizedRedisPool:
    def __init__(self):
        self.pool = redis.ConnectionPool(
            host='redis',
            port=6379,
            max_connections=100,
            retry_on_timeout=True,
            socket_keepalive=True,
            socket_keepalive_options={}
        )
```

**Pipeline Operations:**
```python
async def batch_check_rate_limits(requests: list) -> list:
    # Use Redis pipeline for batch operations
    pipe = redis.pipeline()
    for request in requests:
        key = f"ratelimit:{request.identifier}:{request.endpoint}"
        pipe.get(key)
    
    results = await pipe.execute()
    return results
```

**Local Caching:**
- Cache rate limit rules (5 minute TTL)
- Cache recent decisions (1 second TTL)
- Reduce Redis calls by 90%+

### Vertical Scaling Limits

**When to Scale Vertically:**
- Single-threaded bottlenecks
- Large in-memory data structures
- CPU-intensive operations

**Limits:**
- Maximum instance size: 32 vCPU, 128GB RAM
- Beyond this, must scale horizontally

### Capacity Planning

**Request Capacity:**
- Target: 10M requests/second
- Per instance: 20K requests/second (with caching)
- Required instances: 500 instances
- With 50% headroom: 750 instances

**Redis Capacity:**
- 10M active users
- Average 10 endpoints per user
- 10M × 10 × 200 bytes = 20GB
- With replication (3x): **60GB**

**Storage Capacity:**
- Rate limit rules: 100K rules × 1KB = 100MB
- User tiers: 10M users × 100B = 1GB
- Historical data: 100GB (archived)

**Network Capacity:**
- 10M requests/sec × 500B response = 5GB/sec = 40Gbps
- Per region: 10Gbps (4 regions)

---

## Optimizations

### Performance Optimizations

#### 1. Redis Operation Optimization

**Pipeline Operations:**

```python
class PipelineOptimizer:
    async def check_multiple_rate_limits(self, requests: list):
        # Use Redis pipeline for batch operations
        pipe = self.redis.pipeline()
        
        for req in requests:
            key = f"ratelimit:{req['identifier']}:{req['endpoint']}"
            pipe.get(key)
            pipe.incr(key)
            pipe.expire(key, req['window'])
        
        results = await pipe.execute()
        return results
```

**Lua Script Optimization:**

```python
class OptimizedLuaScript:
    def get_token_bucket_script(self):
        # Optimized Lua script with minimal operations
        return """
        local key = KEYS[1]
        local capacity = tonumber(ARGV[1])
        local refill_rate = tonumber(ARGV[2])
        local now = tonumber(ARGV[3])
        local window = tonumber(ARGV[4])
        
        local bucket = redis.call('HMGET', key, 'tokens', 'last_refill')
        local tokens = tonumber(bucket[1]) or capacity
        local last_refill = tonumber(bucket[2]) or now
        
        local elapsed = now - last_refill
        tokens = math.min(capacity, tokens + elapsed * refill_rate)
        
        if tokens >= 1 then
            tokens = tokens - 1
            redis.call('HMSET', key, 'tokens', tokens, 'last_refill', now)
            redis.call('EXPIRE', key, window)
            return {1, tokens}  -- allowed, remaining
        else
            redis.call('HMSET', key, 'tokens', tokens, 'last_refill', now)
            redis.call('EXPIRE', key, window)
            return {0, 0}  -- not allowed, remaining
        end
        """
```

#### 2. Local Cache Optimization

**Multi-Level Caching:**

```python
class MultiLevelCache:
    def __init__(self):
        self.l1_cache = {}  # In-memory, fastest
        self.l2_cache = LRUCache(max_size=10000, ttl=1)  # Local cache
        self.redis_cache = RedisCache()  # Distributed cache
    
    async def get_rate_limit(self, identifier: str, endpoint: str):
        key = f"{identifier}:{endpoint}"
        
        # L1 cache (in-memory)
        if key in self.l1_cache:
            cached_time, result = self.l1_cache[key]
            if time.time() - cached_time < 0.1:  # 100ms TTL
                return result
        
        # L2 cache (local LRU)
        cached = self.l2_cache.get(key)
        if cached:
            self.l1_cache[key] = (time.time(), cached)
            return cached
        
        # L3 cache (Redis)
        cached = await self.redis_cache.get(key)
        if cached:
            self.l2_cache.set(key, cached)
            self.l1_cache[key] = (time.time(), cached)
            return cached
        
        # Compute
        result = await self.compute_rate_limit(identifier, endpoint)
        
        # Cache at all levels
        self.l1_cache[key] = (time.time(), result)
        self.l2_cache.set(key, result)
        await self.redis_cache.set(key, result, ttl=60)
        
        return result
```

#### 3. Rule Lookup Optimization

**Rule Index:**

```python
class RuleIndexOptimizer:
    def __init__(self):
        self.rule_index = {}  # (identifier_type, endpoint) -> rule_id
        self.rule_cache = {}
    
    async def get_rule_fast(self, identifier_type: str, identifier_value: str, endpoint: str):
        # Check index first
        index_key = (identifier_type, endpoint)
        rule_id = self.rule_index.get(index_key)
        
        if rule_id:
            # Get from cache
            rule = self.rule_cache.get(rule_id)
            if rule:
                return rule
            
            # Fetch from database
            rule = await self.db.get_rule(rule_id)
            self.rule_cache[rule_id] = rule
            return rule
        
        return None
```

---

## Caching Strategy

### Cache Architecture

```
Rate Limit Check
    │
    ▼
Local Cache (In-Memory)
    │
    ├─ Cache Hit → Return (0.1ms)
    │
    └─ Cache Miss → Continue
        │
        ▼
    Redis Cache
        │
        ├─ Cache Hit → Return (1-2ms)
        │
        └─ Cache Miss → Compute
            │
            ▼
        Return + Cache
```

### Cache Keys

```
ratelimit:{identifier}:{endpoint}:{window} → Rate limit counter
rule:{identifier_type}:{identifier_value}:{endpoint} → Rate limit rule
decision:{identifier}:{endpoint} → Cached decision
```

### Cache Invalidation

**TTL-Based:**
- Rate limit counters: Window duration
- Rules: 5 minutes
- Decisions: 1 second

**Event-Based:**
- Invalidate on rule updates
- Invalidate on limit changes

---

## Load Balancing

### Load Balancer Architecture

```
API Requests
    │
    ▼
Load Balancer
    │
    ├─ Rate Limiter Service 1
    ├─ Rate Limiter Service 2
    ├─ Rate Limiter Service 3
    └─ Rate Limiter Service N
```

### Load Balancing Strategies

1. **Round-Robin**: Equal distribution
2. **Least Connections**: Route to server with fewest connections
3. **Consistent Hashing**: Route by identifier (for local caching)

---

## Security

### 1. Rate Limit Bypass Prevention

**Challenges:**
- IP rotation
- Multiple API keys
- Distributed attacks

**Solutions:**
- **IP Reputation**: Track IP reputation
- **Behavioral Analysis**: Detect abnormal patterns
- **Global Limits**: Global rate limits per IP
- **CAPTCHA**: After rate limit exceeded

### 2. Configuration Security

**Access Control:**
- Admin-only configuration API
- Audit logging
- Rate limit on configuration API

---

## Monitoring & Analytics

### Key Metrics

**Performance Metrics:**
- Rate limit check latency
- Redis operation latency
- Cache hit rate
- Throughput

**Business Metrics:**
- Rate limit violations
- Top rate-limited users/IPs
- Rate limit effectiveness
- False positives

### Alerting

**Alerts:**
- High rate limit violation rate
- Redis latency spikes
- Cache hit rate drops
- Configuration errors

---

## Deployment Strategy

### Infrastructure

**Cloud Provider**: AWS, GCP, or Azure

**Components:**
- **Compute**: Kubernetes (EKS/GKE)
- **Cache**: Redis (ElastiCache)
- **Database**: PostgreSQL (RDS)
- **Monitoring**: Prometheus + Grafana

### Multi-Region Deployment

```
Region 1          Region 2          Region 3
┌─────────┐      ┌─────────┐      ┌─────────┐
│Rate     │      │Rate     │      │Rate     │
│Limiter  │      │Limiter  │      │Limiter  │
│         │      │         │      │         │
└────┬────┘      └────┬────┘      └────┬────┘
     │                │                │
     └────────────────┼────────────────┘
                      │
                      ▼
              Redis Cluster
                      │
                      ▼
              PostgreSQL (Replicated)
```

---

## Capacity Planning

### Storage Estimates

**Redis Storage:**
- 10M active users
- Average 10 endpoints per user
- 10M × 10 × 100 bytes = 10 GB
- With replication (3x): **30 GB**

### Compute Requirements

**Rate Limiter Services:**
- 10M requests/second
- Each check: ~1ms (with caching)
- Required servers: 10M / (1000/1) = 10,000 servers
- With caching (90% hit rate): **1,000 servers**

---

## Technology Stack

### Recommended Stack

**Compute:**
- **Language**: Go or Rust (low latency)
- **Orchestration**: Kubernetes

**Cache:**
- **Redis** (ElastiCache)

**Database:**
- **PostgreSQL** (RDS)

**Monitoring:**
- **Prometheus** + **Grafana**

---

## Failure Scenarios & Handling

### 1. Redis Failure

**Scenario:** Redis cluster fails.

**Impact:** Cannot check rate limits.

**Mitigation:**
- **Redis Cluster**: Multiple nodes, replication
- **Graceful Degradation**: Allow all requests if Redis down
- **Local Fallback**: Use local cache
- **Circuit Breaker**: Fail open after threshold

### 2. High Latency

**Scenario:** Redis latency spikes.

**Impact:** Slow rate limit checks.

**Mitigation:**
- **Local Caching**: Cache recent decisions
- **Connection Pooling**: Reuse connections
- **Timeout**: Fail fast on timeout
- **Monitoring**: Alert on latency spikes

### 3. Configuration Errors

**Scenario:** Wrong rate limit configuration.

**Impact:** Incorrect rate limiting.

**Mitigation:**
- **Validation**: Validate configuration
- **Testing**: Test in staging
- **Rollback**: Quick rollback capability
- **Monitoring**: Alert on anomalies

---

## Trade-offs & Design Decisions

### 1. Algorithm: Token Bucket vs Sliding Window

**Decision:** Support multiple algorithms (configurable).

**Trade-offs:**

| Algorithm | Pros | Cons | Use Case |
|-----------|------|------|----------|
| **Token Bucket** | Allows bursts, smooth | More complex | API rate limiting |
| **Sliding Window** | Accurate, no bursts | Memory intensive | Critical rate limits |
| **Fixed Window** | Simple, fast | Bursts at boundaries | Simple use cases |

**Why Multiple:**
- **Token Bucket**: Default for most APIs
- **Sliding Window**: For critical rate limits
- **Fixed Window**: For simple use cases

### 2. Consistency: Strong vs Eventual

**Decision:** Eventual consistency with local cache.

**Trade-offs:**

| Approach | Pros | Cons |
|----------|------|------|
| **Strong** | Accurate | Higher latency |
| **Eventual** | Lower latency | Slight inaccuracy |

**Why Eventual:**
- **Performance**: Sub-millisecond latency needed
- **Acceptable**: Small inaccuracy acceptable for most use cases

### 3. Failure Mode: Fail Open vs Fail Closed

**Decision:** Fail open (allow requests if rate limiter fails).

**Trade-offs:**

| Approach | Pros | Cons |
|----------|------|------|
| **Fail Open** | No service disruption | Risk of abuse |
| **Fail Closed** | Safer | Service disruption |

**Why Fail Open:**
- **Availability**: Rate limiting shouldn't break service
- **Mitigation**: Other protections (IP blocking, etc.)

---

## Interview Discussion Points

### Key Questions to Address

1. **"How do you handle distributed rate limiting?"**
   - **Answer**: 
     - Centralized Redis for shared state
     - Atomic operations (Lua scripts)
     - Local cache for performance
     - Consistent hashing for sharding

2. **"How do you prevent race conditions?"**
   - **Answer**:
     - Atomic Redis operations
     - Lua scripts for complex operations
     - Distributed locks for critical sections

3. **"How do you handle Redis failures?"**
   - **Answer**:
     - Redis cluster with replication
     - Graceful degradation (fail open)
     - Local cache fallback
     - Circuit breaker pattern

4. **"How do you optimize performance?"**
   - **Answer**:
     - Local caching
     - Connection pooling
     - Batching operations
     - Efficient data structures

5. **"How do you handle different rate limit types?"**
   - **Answer**:
     - Hierarchical rate limits (global → user → endpoint)
     - Priority-based evaluation
     - Most restrictive wins

---

## References

- [Token Bucket Algorithm](https://en.wikipedia.org/wiki/Token_bucket)
- [Sliding Window Algorithm](https://en.wikipedia.org/wiki/Sliding_window_protocol)
- [Redis Lua Scripting](https://redis.io/commands/eval/)
- [System Design Primer](https://github.com/donnemartin/system-design-primer)

---

**Document Version**: 2.0  
**Last Updated**: January 2024

