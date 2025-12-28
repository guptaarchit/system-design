# Netflix: Limit Number of Screens System Design

## Table of Contents
1. [Overview](#overview)
2. [Requirements](#requirements)
3. [System Architecture](#system-architecture)
4. [Database Design](#database-design)
5. [API Design](#api-design)
6. [Screen Tracking System](#screen-tracking-system)
7. [Concurrent Stream Management](#concurrent-stream-management)
8. [Screen Limit Enforcement](#screen-limit-enforcement)
9. [Scalability Considerations](#scalability-considerations)
10. [Caching Strategy](#caching-strategy)
11. [Load Balancing](#load-balancing)
12. [Security](#security)
13. [Monitoring & Analytics](#monitoring--analytics)
14. [Deployment Strategy](#deployment-strategy)
15. [Capacity Planning](#capacity-planning)
16. [Technology Stack](#technology-stack)
17. [Failure Scenarios & Handling](#failure-scenarios--handling)
18. [Trade-offs & Design Decisions](#trade-offs--design-decisions)
19. [Interview Discussion Points](#interview-discussion-points)

---

## Overview

A system to limit the number of concurrent screens a Netflix user can watch simultaneously. The system must track active streams, enforce screen limits based on subscription tiers, handle edge cases, and provide real-time enforcement.

**Key Features:**
- Track active streams per user/profile
- Enforce screen limits (1, 2, 4 screens based on plan)
- Real-time stream tracking
- Handle stream start/stop events
- Graceful handling of network issues
- Support for different device types
- Profile-level screen limits

---

## Requirements

### Functional Requirements

1. **Screen Limit Configuration**
   - Different limits per subscription tier
   - Basic: 1 screen
   - Standard: 2 screens
   - Premium: 4 screens
   - Configurable per account

2. **Stream Tracking**
   - Track active streams per user/profile
   - Track device information
   - Track content being watched
   - Track stream start/stop times

3. **Screen Limit Enforcement**
   - Check screen limit before allowing new stream
   - Reject new stream if limit exceeded
   - Handle edge cases (network disconnects, app crashes)

4. **Stream Management**
   - Start stream (check limit)
   - Stop stream (release screen)
   - Update stream status (heartbeat)
   - Handle stream timeouts

5. **User Experience**
   - Clear error messages when limit exceeded
   - Option to stop other streams
   - Show active streams to user

### Non-Functional Requirements

1. **Scalability**
   - Handle 100M+ concurrent streams
   - Support millions of users
   - Low latency enforcement (< 50ms)

2. **Performance**
   - Stream start check: < 50ms latency
   - Heartbeat update: < 10ms latency
   - 99th percentile latency < 100ms

3. **Availability**
   - 99.9% uptime
   - Graceful degradation
   - No false rejections

4. **Accuracy**
   - Accurate stream counting
   - Handle concurrent requests
   - No race conditions

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Applications                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │   Web    │  │  Mobile  │  │    TV    │  │  Tablet  │     │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘     │
└───────┼─────────────┼─────────────┼─────────────┼───────────┘
        │             │             │             │
        └─────────────┴─────────────┴─────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│              API Gateway / Load Balancer                     │
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
│              Stream Management Service                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Stream  │  │  Stream  │  │  Stream  │  │  Stream  │   │
│  │ Service  │  │ Service  │  │ Service  │  │ Service  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼───────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│              Screen Limit Service                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Limit   │  │  Limit   │  │  Limit   │  │  Limit   │   │
│  │ Service  │  │ Service  │  │ Service  │  │ Service  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼───────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│              Distributed Cache (Redis)                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Redis   │  │  Redis   │  │  Redis   │  │  Redis   │   │
│  │ Cluster  │  │ Cluster  │  │ Cluster  │  │ Cluster  │   │
│  │(Streams) │  │(Limits)  │  │(Heartbeat)│ │(Locks)   │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼───────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│              Database Layer                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │Cassandra │  │PostgreSQL│  │PostgreSQL│  │  Kafka   │   │
│  │(Streams) │  │(Users)   │  │(Limits)  │  │(Events)  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Component Details

#### 1. Stream Management Service
- **Responsibilities**:
  - Handle stream start requests
  - Track active streams
  - Handle stream stop events
  - Process heartbeats

#### 2. Screen Limit Service
- **Responsibilities**:
  - Check screen limits
  - Enforce limits
  - Get active stream count
  - Handle limit violations

#### 3. Distributed Cache (Redis)
- **Responsibilities**:
  - Store active streams
  - Track stream counts per user/profile
  - Distributed locks
  - Heartbeat tracking

#### 4. Database Layer
- **Cassandra**: Stream history
- **PostgreSQL**: User accounts, subscription tiers
- **Kafka**: Stream events

---

## Database Design

### PostgreSQL Schema

#### Users Table
```sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    subscription_tier VARCHAR(50) NOT NULL,  -- 'basic', 'standard', 'premium'
    screen_limit INT NOT NULL,  -- 1, 2, or 4
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_subscription_tier (subscription_tier)
) ENGINE=InnoDB;
```

#### User Profiles Table
```sql
CREATE TABLE user_profiles (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    profile_name VARCHAR(255) NOT NULL,
    screen_limit INT,  -- NULL means use user's limit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB;
```

### Redis Schema

#### Active Streams
```
Key: active_streams:{user_id}:{profile_id}
Type: Set
Members: stream_id
TTL: 2 hours (stream timeout)
```

#### Stream Metadata
```
Key: stream:{stream_id}
Type: Hash
Fields:
  - user_id
  - profile_id
  - device_id
  - content_id
  - started_at
  - last_heartbeat
TTL: 2 hours
```

#### Stream Count
```
Key: stream_count:{user_id}:{profile_id}
Type: String (Integer)
Value: Current active stream count
TTL: 2 hours
```

### Cassandra Schema

#### Stream History Table
```cql
CREATE TABLE stream_history (
    user_id UUID,
    profile_id UUID,
    stream_id UUID,
    started_at TIMESTAMP,
    stopped_at TIMESTAMP,
    device_id TEXT,
    content_id TEXT,
    duration_seconds INT,
    PRIMARY KEY ((user_id, profile_id), started_at, stream_id)
) WITH CLUSTERING ORDER BY (started_at DESC);
```

---

## API Design

### Stream Management APIs

**Start Stream**
```
POST /api/v1/streams/start
Content-Type: application/json
Authorization: Bearer {token}

Request:
{
    "user_id": "user_123",
    "profile_id": "profile_1",
    "device_id": "device_456",
    "content_id": "movie_789",
    "device_type": "mobile"
}

Response (Success):
{
    "success": true,
    "stream_id": "stream_abc123",
    "active_streams": 2,
    "screen_limit": 4,
    "remaining_screens": 2
}

Response (Limit Exceeded):
{
    "success": false,
    "error": "screen_limit_exceeded",
    "active_streams": 4,
    "screen_limit": 4,
    "active_streams_list": [
        {
            "stream_id": "stream_1",
            "device_id": "device_1",
            "content_id": "movie_1",
            "started_at": "2024-01-15T10:00:00Z"
        }
    ],
    "message": "You have reached your screen limit. Please stop another stream to continue."
}
```

**Stop Stream**
```
POST /api/v1/streams/{stream_id}/stop
Content-Type: application/json

Request:
{
    "user_id": "user_123",
    "profile_id": "profile_1"
}

Response:
{
    "success": true,
    "stream_id": "stream_abc123",
    "active_streams": 1
}
```

**Update Heartbeat**
```
PUT /api/v1/streams/{stream_id}/heartbeat
Content-Type: application/json

Request:
{
    "user_id": "user_123",
    "profile_id": "profile_1"
}

Response:
{
    "success": true,
    "stream_id": "stream_abc123",
    "last_heartbeat": "2024-01-15T10:30:00Z"
}
```

**Get Active Streams**
```
GET /api/v1/streams/active?user_id={user_id}&profile_id={profile_id}

Response:
{
    "user_id": "user_123",
    "profile_id": "profile_1",
    "active_streams": 2,
    "screen_limit": 4,
    "streams": [
        {
            "stream_id": "stream_1",
            "device_id": "device_1",
            "device_type": "mobile",
            "content_id": "movie_1",
            "content_title": "Example Movie",
            "started_at": "2024-01-15T10:00:00Z",
            "last_heartbeat": "2024-01-15T10:30:00Z"
        }
    ]
}
```

**Stop Other Stream**
```
POST /api/v1/streams/{stream_id}/stop-other
Content-Type: application/json

Request:
{
    "user_id": "user_123",
    "profile_id": "profile_1",
    "stream_to_stop": "stream_xyz"
}

Response:
{
    "success": true,
    "stopped_stream": "stream_xyz",
    "active_streams": 3
}
```

---

## Data Flow Diagrams

### Stream Start Flow

```
User Starts Stream
    │
    ▼
Stream Management Service
    │
    ├─ Validate Request
    ├─ Get User Subscription Tier
    │   │
    │   ▼
    │   User Service (PostgreSQL)
    │   │
    │   └─ Get screen_limit
    │
    ▼
Screen Limit Service
    │
    ├─ Acquire Distributed Lock
    │   │
    │   └─ Lock Key: lock:{user_id}:{profile_id}
    │
    ├─ Get Active Stream Count
    │   │
    │   ▼
    │   Redis: GET stream_count:{user_id}:{profile_id}
    │   │
    │   └─ If not exists, count from active_streams set
    │
    ├─ Check Limit
    │   │
    │   ├─ If count < limit → Allow
    │   │
    │   └─ If count >= limit → Reject
    │       │
    │       └─ Return error with active streams list
    │
    ▼
If Allowed:
    │
    ├─ Generate Stream ID
    ├─ Add to Active Streams Set
    │   │
    │   └─ Redis: SADD active_streams:{user_id}:{profile_id} {stream_id}
    │
    ├─ Store Stream Metadata
    │   │
    │   └─ Redis: HSET stream:{stream_id} {...}
    │
    ├─ Increment Stream Count
    │   │
    │   └─ Redis: INCR stream_count:{user_id}:{profile_id}
    │
    ├─ Set TTL (2 hours)
    │
    ├─ Release Lock
    │
    └─ Publish Stream Start Event (Kafka)
        │
        ▼
    Return Success to Client
```

### Stream Stop Flow

```
User Stops Stream
    │
    ▼
Stream Management Service
    │
    ├─ Validate Stream Ownership
    │
    ▼
Screen Limit Service
    │
    ├─ Acquire Distributed Lock
    │
    ├─ Remove from Active Streams Set
    │   │
    │   └─ Redis: SREM active_streams:{user_id}:{profile_id} {stream_id}
    │
    ├─ Decrement Stream Count
    │   │
    │   └─ Redis: DECR stream_count:{user_id}:{profile_id}
    │
    ├─ Delete Stream Metadata
    │   │
    │   └─ Redis: DEL stream:{stream_id}
    │
    ├─ Release Lock
    │
    └─ Publish Stream Stop Event (Kafka)
        │
        ▼
    Store in Stream History (Cassandra)
        │
        ▼
    Return Success to Client
```

### Heartbeat Flow

```
Client Sends Heartbeat (Every 30 seconds)
    │
    ▼
Stream Management Service
    │
    ├─ Validate Stream Exists
    │
    ├─ Update Last Heartbeat
    │   │
    │   └─ Redis: HSET stream:{stream_id} last_heartbeat {timestamp}
    │
    ├─ Refresh TTL
    │   │
    │   └─ Redis: EXPIRE stream:{stream_id} 7200
    │
    └─ Return Success
```

---

## Screen Tracking System

### Active Stream Tracking

**Redis Data Structures:**
1. **Set**: `active_streams:{user_id}:{profile_id}` - List of active stream IDs
2. **Hash**: `stream:{stream_id}` - Stream metadata
3. **String**: `stream_count:{user_id}:{profile_id}` - Current count (for fast lookup)

**Implementation:**
```python
class ScreenLimitService:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def check_and_reserve_screen(self, user_id, profile_id, stream_id, screen_limit):
        lock_key = f"lock:{user_id}:{profile_id}"
        
        # Acquire distributed lock
        with self.redis.lock(lock_key, timeout=5):
            # Get current count
            count_key = f"stream_count:{user_id}:{profile_id}"
            current_count = int(self.redis.get(count_key) or 0)
            
            # Verify by counting set (for accuracy)
            streams_key = f"active_streams:{user_id}:{profile_id}"
            actual_count = self.redis.scard(streams_key)
            
            # Use maximum (handle race conditions)
            current_count = max(current_count, actual_count)
            
            # Check limit
            if current_count >= screen_limit:
                # Get active streams for error message
                active_stream_ids = self.redis.smembers(streams_key)
                active_streams = self.get_stream_details(active_stream_ids)
                
                return {
                    'allowed': False,
                    'current_count': current_count,
                    'limit': screen_limit,
                    'active_streams': active_streams
                }
            
            # Reserve screen
            self.redis.sadd(streams_key, stream_id)
            self.redis.incr(count_key)
            self.redis.expire(streams_key, 7200)  # 2 hours
            self.redis.expire(count_key, 7200)
            
            return {
                'allowed': True,
                'current_count': current_count + 1,
                'limit': screen_limit
            }
    
    def release_screen(self, user_id, profile_id, stream_id):
        lock_key = f"lock:{user_id}:{profile_id}"
        
        with self.redis.lock(lock_key, timeout=5):
            streams_key = f"active_streams:{user_id}:{profile_id}"
            count_key = f"stream_count:{user_id}:{profile_id}"
            
            # Remove from set
            removed = self.redis.srem(streams_key, stream_id)
            
            if removed:
                # Decrement count
                self.redis.decr(count_key)
            
            # Clean up stream metadata
            self.redis.delete(f"stream:{stream_id}")
```

---

## Concurrent Stream Management

### Handling Concurrent Requests

**Challenge:** Multiple devices trying to start streams simultaneously.

**Solution:**
- **Distributed Locks**: Use Redis locks
- **Atomic Operations**: Use Redis atomic operations
- **Idempotency**: Handle duplicate requests

**Implementation:**
```python
def start_stream_atomic(user_id, profile_id, stream_id, screen_limit):
    lock_key = f"lock:{user_id}:{profile_id}"
    
    # Lua script for atomic operation
    lua_script = """
    local streams_key = KEYS[1]
    local count_key = KEYS[2]
    local stream_id = ARGV[1]
    local limit = tonumber(ARGV[2])
    
    -- Get current count
    local count = tonumber(redis.call('GET', count_key) or 0)
    local actual_count = redis.call('SCARD', streams_key)
    count = math.max(count, actual_count)
    
    -- Check limit
    if count >= limit then
        return {0, count}  -- Not allowed, current count
    end
    
    -- Add stream
    redis.call('SADD', streams_key, stream_id)
    redis.call('INCR', count_key)
    redis.call('EXPIRE', streams_key, 7200)
    redis.call('EXPIRE', count_key, 7200)
    
    return {1, count + 1}  -- Allowed, new count
    """
    
    streams_key = f"active_streams:{user_id}:{profile_id}"
    count_key = f"stream_count:{user_id}:{profile_id}"
    
    result = self.redis.eval(lua_script, 2, streams_key, count_key, stream_id, screen_limit)
    
    return {
        'allowed': result[0] == 1,
        'current_count': result[1]
    }
```

---

## Screen Limit Enforcement

### Limit Configuration

**Subscription Tiers:**
- **Basic**: 1 screen
- **Standard**: 2 screens
- **Premium**: 4 screens

**Profile-Level Limits:**
- Can override user limit per profile
- Useful for parental controls

**Implementation:**
```python
def get_screen_limit(user_id, profile_id):
    # Check profile-level limit first
    profile_limit = get_profile_limit(profile_id)
    if profile_limit:
        return profile_limit
    
    # Get user subscription tier
    user = get_user(user_id)
    tier_limits = {
        'basic': 1,
        'standard': 2,
        'premium': 4
    }
    
    return tier_limits.get(user.subscription_tier, 1)
```

### Enforcement Points

1. **Stream Start**: Check limit before allowing
2. **Stream Resume**: Check limit on resume
3. **Device Switch**: Check limit when switching devices

---

## Scalability Considerations

### 1. Horizontal Scaling

**Stream Services:**
- Stateless services
- Scale horizontally
- Load balancer distributes traffic

**Redis Cluster:**
- Shard by user_id
- Distribute load
- High availability

### 2. Performance Optimization

**Local Caching:**
- Cache user limits
- Cache active stream counts (short TTL)
- Reduce Redis calls

**Batching:**
- Batch heartbeat updates
- Reduce network calls

### 3. Memory Optimization

**Key Design:**
- Short Redis keys
- Efficient data structures
- TTL-based expiration

---

## Caching Strategy

### Cache Architecture

```
Stream Start Request
    │
    ▼
Local Cache (User Limits)
    │
    ├─ Cache Hit → Use Limit
    │
    └─ Cache Miss → Query Database
        │
        └─ Cache Result
        │
        ▼
    Redis (Active Streams)
        │
        └─ Check/Update Count
```

### Cache Keys

```
user_limit:{user_id}:{profile_id} → Screen limit
stream_count:{user_id}:{profile_id} → Active stream count
active_streams:{user_id}:{profile_id} → Set of active stream IDs
```

### Cache Invalidation

**TTL-Based:**
- User limits: 1 hour
- Stream counts: 2 hours (stream TTL)

**Event-Based:**
- Invalidate on subscription change
- Invalidate on profile limit change

---

## Load Balancing

### Load Balancer Architecture

```
Stream Requests
    │
    ▼
Load Balancer
    │
    ├─ Stream Service 1
    ├─ Stream Service 2
    ├─ Stream Service 3
    └─ Stream Service N
```

### Load Balancing Strategies

1. **Round-Robin**: Equal distribution
2. **Consistent Hashing**: Route by user_id (for local caching)
3. **Least Connections**: Route to server with fewest connections

---

## Security

### 1. Authentication & Authorization

**Authentication:**
- JWT tokens
- Validate user ownership of stream

**Authorization:**
- Users can only manage their own streams
- Validate stream ownership before operations

### 2. Abuse Prevention

**Challenges:**
- Users trying to bypass limits
- Multiple accounts
- Automated scripts

**Solutions:**
- **Device Fingerprinting**: Track unique devices
- **Rate Limiting**: Limit stream start attempts
- **Monitoring**: Detect abnormal patterns

---

## Monitoring & Analytics

### Key Metrics

**Performance Metrics:**
- Stream start latency
- Screen limit check latency
- Heartbeat processing latency

**Business Metrics:**
- Active streams per user
- Screen limit violations
- Average streams per user
- Device distribution

### Alerting

**Alerts:**
- High screen limit violation rate
- Redis latency spikes
- Stream timeout issues

---

## Deployment Strategy

### Infrastructure

**Cloud Provider**: AWS, GCP, or Azure

**Components:**
- **Compute**: Kubernetes (EKS/GKE)
- **Cache**: Redis (ElastiCache)
- **Database**: PostgreSQL (RDS), Cassandra (Keyspaces)
- **Message Queue**: Kafka (MSK)

---

## Capacity Planning

### Storage Estimates

**Redis Storage:**
- 100M active users
- Average 2 active streams per user
- 100M × 2 × 200 bytes = 40 GB
- With replication (3x): **120 GB**

### Compute Requirements

**Stream Services:**
- 1M stream starts/second
- Each check: ~10ms (with caching)
- Required servers: 1M / (1000/10) = 10,000 servers
- With caching (80% hit rate): **2,000 servers**

---

## Technology Stack

### Recommended Stack

**Compute:**
- **Language**: Go or Java
- **Orchestration**: Kubernetes

**Cache:**
- **Redis** (ElastiCache)

**Database:**
- **PostgreSQL** (RDS)
- **Cassandra** (Keyspaces)

**Message Queue:**
- **Kafka** (MSK)

---

## Failure Scenarios & Handling

### 1. Redis Failure

**Scenario:** Redis cluster fails.

**Impact:** Cannot check screen limits.

**Mitigation:**
- **Redis Cluster**: Multiple nodes, replication
- **Graceful Degradation**: Allow streams if Redis down (temporary)
- **Fallback**: Query database (slower)
- **Circuit Breaker**: Fail open after threshold

### 2. Network Partition

**Scenario:** Network split between services.

**Impact:** Inconsistent stream counts.

**Mitigation:**
- **Quorum Requirement**: Require majority for updates
- **Reconciliation**: Periodic reconciliation job
- **Monitoring**: Alert on inconsistencies

### 3. Stream Timeout

**Scenario:** Client crashes, doesn't send stop event.

**Impact:** Stream counts remain high, blocking new streams.

**Mitigation:**
- **Heartbeat Timeout**: Expire streams without heartbeat
- **TTL**: Automatic expiration (2 hours)
- **Cleanup Job**: Periodic cleanup of stale streams

---

## Trade-offs & Design Decisions

### 1. Accuracy: Exact vs Approximate

**Decision:** Exact counting (no approximation).

**Trade-offs:**

| Approach | Pros | Cons |
|----------|------|------|
| **Exact** | Accurate, fair | Higher cost |
| **Approximate** | Lower cost | Less accurate |

**Why Exact:**
- **Fairness**: Users pay for specific limits
- **Trust**: Users expect accurate enforcement

### 2. Storage: Redis vs Database

**Decision:** Redis for real-time, Database for history.

**Trade-offs:**

| Storage | Pros | Cons |
|---------|------|------|
| **Redis** | Fast, real-time | Volatile |
| **Database** | Persistent | Slower |

**Why Both:**
- **Redis**: Real-time enforcement
- **Database**: Historical data, audit trail

### 3. Heartbeat: Frequent vs Infrequent

**Decision:** Every 30 seconds.

**Trade-offs:**

| Frequency | Pros | Cons |
|-----------|------|------|
| **Frequent** | Fast detection | Higher load |
| **Infrequent** | Lower load | Slower detection |

**Why 30 seconds:**
- **Balance**: Good detection time vs load
- **User Experience**: Quick recovery from crashes

---

## Interview Discussion Points

### Key Questions to Address

1. **"How do you prevent race conditions?"**
   - **Answer**: 
     - Distributed locks (Redis)
     - Atomic operations (Lua scripts)
     - Idempotent operations

2. **"How do you handle network disconnects?"**
   - **Answer**:
     - Heartbeat mechanism
     - TTL-based expiration
     - Cleanup job for stale streams

3. **"How do you ensure accuracy?"**
   - **Answer**:
     - Exact counting (no approximation)
     - Atomic operations
     - Periodic reconciliation

4. **"How do you handle concurrent stream starts?"**
   - **Answer**:
     - Distributed locks
     - Atomic check-and-reserve operations
     - Proper ordering

5. **"What if Redis fails?"**
   - **Answer**:
     - Redis cluster with replication
     - Graceful degradation (allow temporarily)
     - Fallback to database (slower)

---

## High-Level Design (HLD)

### System Overview

The screen limit system follows a real-time distributed architecture:

1. **Client Layer**: Web, mobile, TV, tablet applications
2. **API Gateway**: Routes requests, handles authentication
3. **Stream Management Service**: Handles stream start/stop, heartbeats
4. **Screen Limit Service**: Enforces screen limits, tracks active streams
5. **Distributed Cache**: Redis for real-time stream tracking
6. **Database Layer**: PostgreSQL for user data, Cassandra for stream history

### Component Architecture

**Core Services:**
- **Stream Management Service**: Stream lifecycle management
- **Screen Limit Service**: Limit enforcement, stream counting
- **User Service**: User subscription tier, limit configuration
- **Notification Service**: Notifies users of limit violations

---

## Low-Level Design (LLD)

### Screen Limit Service Implementation

```python
class ScreenLimitService:
    def __init__(self, redis_client, db_client):
        self.redis = redis_client
        self.db = db_client
    
    def check_and_reserve_screen(self, user_id: str, profile_id: str, 
                                 stream_id: str, screen_limit: int) -> dict:
        lock_key = f"lock:{user_id}:{profile_id}"
        
        # Acquire distributed lock
        with self.redis.lock(lock_key, timeout=5):
            # Get current count
            count_key = f"stream_count:{user_id}:{profile_id}"
            current_count = int(self.redis.get(count_key) or 0)
            
            # Verify by counting set (for accuracy)
            streams_key = f"active_streams:{user_id}:{profile_id}"
            actual_count = self.redis.scard(streams_key)
            
            # Use maximum (handle race conditions)
            current_count = max(current_count, actual_count)
            
            # Check limit
            if current_count >= screen_limit:
                # Get active streams for error message
                active_stream_ids = self.redis.smembers(streams_key)
                active_streams = self.get_stream_details(active_stream_ids)
                
                return {
                    'allowed': False,
                    'current_count': current_count,
                    'limit': screen_limit,
                    'active_streams': active_streams
                }
            
            # Reserve screen (atomic operation)
            self.redis.sadd(streams_key, stream_id)
            self.redis.incr(count_key)
            self.redis.expire(streams_key, 7200)  # 2 hours
            self.redis.expire(count_key, 7200)
            
            return {
                'allowed': True,
                'current_count': current_count + 1,
                'limit': screen_limit
            }
```

---

## Fault Tolerance

### Redis Cluster Resilience

**Replication:**
- Redis Cluster with replication
- Automatic failover
- Data sharded across nodes

**Failure Handling:**
- Read from replica if master fails
- Write to new master after failover
- Graceful degradation to database

### Service Resilience

**Multiple Instances:**
- Multiple service instances
- Load balancer distributes requests
- Health checks

**Circuit Breaker:**
- Circuit breaker for Redis calls
- Fallback to database
- Prevent cascade failures

---

## Optimizations

### Caching Strategy

**User Limits Cache:**
- Cache user subscription tiers
- Cache screen limits per user/profile
- TTL: 1 hour

**Stream Count Cache:**
- Cache active stream counts
- Update on stream start/stop
- TTL: 2 hours (stream TTL)

### Database Optimization

**Indexing:**
- Index on `user_id, subscription_tier`
- Index on `user_id, profile_id`
- Optimize limit queries

**Query Optimization:**
- Use prepared statements
- Batch queries where possible
- Read from replicas

---

## Failure Safety

### Redis Failure

**Scenario: Redis Cluster Down**
- **Impact**: Cannot check screen limits
- **Mitigation**:
  - Redis Cluster with replication
  - Graceful degradation to database
  - Circuit breaker pattern
- **Recovery**:
  - Redis recovers
  - Rebuild cache from database
  - Resume normal operation

### Service Failure

**Scenario: Stream Service Down**
- **Impact**: Cannot start/stop streams
- **Mitigation**:
  - Multiple service instances
  - Load balancer routes to healthy instances
  - Retry logic
- **Recovery**:
  - Service recovers
  - Process queued requests
  - Resume normal operation

---

## Scalability

### Horizontal Scaling

**Service Scaling:**
- Stateless service instances
- Load balancer distributes requests
- Scale independently

**Redis Scaling:**
- Redis Cluster with sharding
- Shard by user_id
- Add shards as needed

### Performance Scaling

**Throughput Scaling:**
- Increase service instances
- Optimize Redis operations
- Reduce database queries

**Latency Optimization:**
- Cache user limits
- Optimize Redis queries
- Use local cache

---

## References

- [Netflix System Design](design/NETFLIX_SYSTEM_DESIGN.md)
- [Redis Distributed Locks](https://redis.io/topics/distlock)
- [System Design Primer](https://github.com/donnemartin/system-design-primer)

