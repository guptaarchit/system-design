# Facebook Likes Count System Design

## Table of Contents
1. [Overview](#overview)
2. [Requirements](#requirements)
3. [System Architecture](#system-architecture)
4. [Database Design](#database-design)
5. [API Design](#api-design)
6. [Like Event Processing](#like-event-processing)
7. [Count Aggregation](#count-aggregation)
8. [High-Profile User Optimization](#high-profile-user-optimization)
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

A system to count Facebook likes, especially optimized for high-profile users who receive millions of likes. The system must handle billions of like events, provide real-time counts, and scale efficiently for viral content.

**Key Features:**
- Real-time like counting
- Optimized for high-profile users
- Handle millions of likes per post
- Like/unlike support
- Per-user like tracking (prevent duplicate likes)
- Aggregated counts
- Historical like data

---

## Requirements

### Functional Requirements

1. **Like Operations**
   - Like a post
   - Unlike a post
   - Check if user liked a post
   - Get like count for a post

2. **Count Display**
   - Real-time like counts
   - Cached counts for performance
   - Accurate counts (no approximation)

3. **High-Profile Optimization**
   - Optimized storage for viral posts
   - Efficient counting for millions of likes
   - Fast queries for popular content

4. **User Features**
   - See who liked a post
   - Like history per user
   - Mutual likes

### Non-Functional Requirements

1. **Scalability**
   - Handle 1B+ like events/day
   - Support posts with 100M+ likes
   - Horizontal scaling

2. **Performance**
   - Like operation: < 50ms latency
   - Count query: < 10ms latency
   - 99th percentile latency < 100ms

3. **Accuracy**
   - Exact counts (no approximation)
   - Handle concurrent likes
   - No duplicate counting

4. **Availability**
   - 99.9% uptime
   - No data loss
   - Graceful degradation

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Applications                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │   Web    │  │  Mobile  │  │   API    │  │  Partner │     │
│  │   App    │  │   App    │  │ Clients  │  │   APIs   │     │
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
│              Like Service Layer                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Like    │  │  Like    │  │  Count   │  │  Count   │   │
│  │ Service  │  │ Service  │  │ Service  │  │ Service  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼───────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│              Message Queue (Kafka)                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Topic   │  │  Topic   │  │  Topic   │  │  Topic   │   │
│  │(Like     │  │(Like     │  │(Like     │  │(Like     │   │
│  │ Events)  │  │ Events)  │  │ Events)  │  │ Events)  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼───────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│              Aggregation Service                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │Real-time │  │Real-time │  │  Batch   │  │  Batch   │   │
│  │Aggregator│  │Aggregator│  │Aggregator│  │Aggregator│   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼───────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│              Storage Layer                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Redis   │  │  Redis   │  │Cassandra │  │PostgreSQL│   │
│  │(Counts)  │  │(User-Like)│ │(Events)  │  │(Metadata)│   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼───────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│              Query Service                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Query   │  │  Query   │  │  Query   │  │  Query   │   │
│  │ Service  │  │ Service  │  │ Service  │  │ Service  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Component Details

#### 1. Like Service
- **Responsibilities**:
  - Handle like/unlike operations
  - Check duplicate likes
  - Validate requests

#### 2. Count Service
- **Responsibilities**:
  - Serve like counts
  - Cache counts
  - Handle high-profile posts

#### 3. Aggregation Service
- **Responsibilities**:
  - Aggregate like events
  - Update counts
  - Handle batch processing

### HLD Component Breakdown

**1. Client Layer**
- **Web App**: React-based web application
- **Mobile Apps**: iOS/Android native apps
- **API Clients**: RESTful API for partners

**2. Service Layer**
- **Like Service**: Handles like/unlike operations
- **Count Service**: Serves like counts
- **Aggregation Service**: Processes like events

**3. Processing Layer**
- **Kafka**: Event streaming for like events
- **Real-time Aggregator**: Processes events in real-time
- **Batch Aggregator**: Processes events in batches

**4. Storage Layer**
- **Redis**: Like counts, user-like mappings
- **Cassandra**: Like events, historical data
- **PostgreSQL**: Post metadata

---

## Low-Level Design (LLD)

### Like Service LLD

```python
class LikeService:
    def __init__(self, redis: RedisClient, kafka: KafkaProducer, lock_manager: LockManager):
        self.redis = redis
        self.kafka = kafka
        self.lock_manager = lock_manager
    
    def toggle_like(self, post_id: str, user_id: str) -> dict:
        lock_key = f"lock:{post_id}:{user_id}"
        
        with self.lock_manager.acquire(lock_key, timeout=5):
            # Check if already liked
            liked_key = f"user_liked:{post_id}"
            is_liked = self.redis.sismember(liked_key, user_id)
            
            if is_liked:
                # Unlike
                self.redis.srem(liked_key, user_id)
                count = self.redis.decr(f"like_count:{post_id}")
                action = 'unlike'
            else:
                # Like
                self.redis.sadd(liked_key, user_id)
                count = self.redis.incr(f"like_count:{post_id}")
                action = 'like'
            
            # Publish event
            self.kafka.publish('like-events', {
                'post_id': post_id,
                'user_id': user_id,
                'event_type': action,
                'count': count,
                'timestamp': time.time()
            })
            
            return {
                'action': action,
                'count': count,
                'is_liked': not is_liked
            }
```

### Count Aggregator LLD

```python
class CountAggregator:
    def __init__(self, redis: RedisClient, cassandra: CassandraClient):
        self.redis = redis
        self.cassandra = cassandra
    
    def process_events(self, events: list):
        # Group by post_id
        post_events = {}
        for event in events:
            post_id = event['post_id']
            if post_id not in post_events:
                post_events[post_id] = []
            post_events[post_id].append(event)
        
        # Aggregate per post
        for post_id, events in post_events.items():
            like_count = sum(1 for e in events if e['event_type'] == 'like')
            unlike_count = sum(1 for e in events if e['event_type'] == 'unlike')
            
            delta = like_count - unlike_count
            
            # Update Redis count
            if delta != 0:
                self.redis.incrby(f"like_count:{post_id}", delta)
            
            # Update Cassandra (batch)
            self._update_cassandra_summary(post_id, delta)
    
    def _update_cassandra_summary(self, post_id: str, delta: int):
        # Update counter in Cassandra
        self.cassandra.execute(
            "UPDATE post_likes_summary SET like_count = like_count + %s WHERE post_id = %s",
            (delta, post_id)
        )
```

---

## Fault Tolerance

### Like Operation Fault Tolerance

**1. Idempotency**
- **Idempotent Operations**: Like/unlike operations are idempotent
- **Duplicate Detection**: Redis Set prevents duplicate likes
- **Idempotency Keys**: Use idempotency keys for retries

**2. Distributed Locking**
- **Redis Locks**: Prevent race conditions
- **Lock Timeout**: 5-second timeout to prevent deadlocks
- **Lock Retry**: Retry with exponential backoff

**3. Event Processing Resilience**
- **Kafka Replication**: 3 replicas per partition
- **Consumer Groups**: Parallel processing with fault tolerance
- **Dead Letter Queue**: Store failed events for retry
- **Event Replay**: Replay events on recovery

### Count Service Fault Tolerance

**1. Cache Fallback**
- **Redis Primary**: Primary cache for counts
- **Database Fallback**: Query Cassandra on cache miss
- **Graceful Degradation**: Continue with reduced performance

**2. Count Reconciliation**
- **Periodic Reconciliation**: Reconcile counts daily
- **Event Replay**: Replay events to rebuild counts
- **Database as Source of Truth**: Cassandra is source of truth

---

## Failure Safety

### Failure Scenarios & Handling

**1. Redis Failure**

**Scenario**: Redis cluster fails.

**Impact**: Cannot track likes or serve counts.

**Mitigation**:
- **Redis Cluster**: Multiple nodes with replication
- **Database Fallback**: Query Cassandra (slower)
- **Graceful Degradation**: Accept likes, sync later
- **Local Cache**: Use application-level cache

**Recovery**:
- **Failover**: Automatically failover to healthy nodes
- **Cache Warming**: Pre-populate cache from Cassandra
- **Count Rebuild**: Rebuild counts from events

**2. Kafka Failure**

**Scenario**: Kafka cluster fails.

**Impact**: Cannot buffer like events.

**Mitigation**:
- **Kafka Cluster**: Multiple brokers with replication
- **Local Buffering**: Buffer in service
- **Fallback**: Write directly to database
- **Retry Queue**: Queue events for later processing

**Recovery**:
- **Broker Recovery**: Restart failed brokers
- **Event Replay**: Replay events from last offset
- **State Sync**: Sync state from database

**3. Count Inconsistency**

**Scenario**: Count and actual likes mismatch.

**Impact**: Incorrect counts displayed.

**Mitigation**:
- **Reconciliation Job**: Periodic reconciliation
- **Database as Source of Truth**: Rebuild from events
- **Monitoring**: Alert on inconsistencies
- **Version Numbers**: Use version numbers for consistency

**Recovery**:
- **Count Rebuild**: Rebuild counts from Cassandra events
- **Event Replay**: Replay events to fix counts
- **Manual Fix**: Manual intervention if needed

---

## Database Design

### Redis Schema

#### Like Counts
```
Key: like_count:{post_id}
Type: String (Integer)
Value: Current like count
TTL: None (persistent)
```

#### User-Like Mapping
```
Key: user_liked:{post_id}
Type: Set
Members: user_id
TTL: None (persistent)
```

**Example:**
```redis
SADD user_liked:post_123 user_456
SISMEMBER user_liked:post_123 user_456  # Check if liked
SCARD user_liked:post_123  # Get count
```

### Cassandra Schema

#### Like Events Table
```cql
CREATE TABLE like_events (
    post_id UUID,
    user_id UUID,
    event_timestamp TIMESTAMP,
    event_type TEXT,  -- 'like' or 'unlike'
    PRIMARY KEY ((post_id), event_timestamp, user_id)
) WITH CLUSTERING ORDER BY (event_timestamp DESC);
```

#### Post Likes Summary Table
```cql
CREATE TABLE post_likes_summary (
    post_id UUID PRIMARY KEY,
    like_count COUNTER,
    updated_at TIMESTAMP
);
```

### PostgreSQL Schema

#### Posts Table
```sql
CREATE TABLE posts (
    id BIGSERIAL PRIMARY KEY,
    post_id VARCHAR(255) UNIQUE NOT NULL,
    author_id BIGINT NOT NULL,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_high_profile BOOLEAN DEFAULT FALSE,
    INDEX idx_author_id (author_id),
    INDEX idx_is_high_profile (is_high_profile)
) ENGINE=InnoDB;
```

---

## API Design

### Like APIs

**Like a Post**
```
POST /api/v1/posts/{post_id}/like
Content-Type: application/json
Authorization: Bearer {token}

Request:
{
    "user_id": "user_123"
}

Response:
{
    "success": true,
    "post_id": "post_456",
    "liked": true,
    "like_count": 1000001
}
```

**Unlike a Post**
```
DELETE /api/v1/posts/{post_id}/like
Content-Type: application/json

Request:
{
    "user_id": "user_123"
}

Response:
{
    "success": true,
    "post_id": "post_456",
    "liked": false,
    "like_count": 1000000
}
```

**Get Like Count**
```
GET /api/v1/posts/{post_id}/likes/count

Response:
{
    "post_id": "post_456",
    "like_count": 1000000,
    "updated_at": "2024-01-15T10:30:00Z"
}
```

**Check if User Liked**
```
GET /api/v1/posts/{post_id}/likes/check?user_id={user_id}

Response:
{
    "post_id": "post_456",
    "user_id": "user_123",
    "liked": true
}
```

**Get Users Who Liked**
```
GET /api/v1/posts/{post_id}/likes/users?limit=100&cursor=abc123

Response:
{
    "post_id": "post_456",
    "users": [
        {
            "user_id": "user_123",
            "name": "John Doe",
            "liked_at": "2024-01-15T10:00:00Z"
        }
    ],
    "cursor": "def456",
    "has_more": true
}
```

---

## Data Flow Diagrams

### Like Event Flow

```
User Likes Post
    │
    ▼
Like Service
    │
    ├─ Check if Already Liked (Redis)
    │   └─ SISMEMBER user_liked:{post_id} {user_id}
    │
    ├─ If Already Liked → Return Error
    │
    └─ If Not Liked → Continue
        │
        ▼
    Acquire Distributed Lock
        │
        └─ Lock Key: lock:{post_id}:{user_id}
        │
        ▼
    Double-Check (Prevent Race Condition)
        │
        └─ Check Again if Liked
        │
        ▼
    If Not Liked:
        │
        ├─ Add to User-Like Set
        │   └─ Redis: SADD user_liked:{post_id} {user_id}
        │
        ├─ Increment Count
        │   └─ Redis: INCR like_count:{post_id}
        │
        ├─ Publish Like Event (Kafka)
        │   │
        │   └─ Topic: like-events
        │   │
        │   └─ Partition by post_id
        │
        └─ Release Lock
        │
        ▼
    Return Success
```

### Count Query Flow

```
User Requests Like Count
    │
    ▼
Count Service
    │
    ├─ Check Cache (Redis)
    │   └─ GET like_count:{post_id}
    │   └─ Cache Hit → Return (1-2ms)
    │
    └─ Cache Miss → Continue
        │
        ▼
    Check if High-Profile Post
        │
        ├─ If High-Profile → Use Optimized Path
        │   │
        │   └─ Query Aggregated Count (Cassandra)
        │
        └─ If Regular Post → Use Standard Path
            │
            └─ Count from Redis Set
                │
                └─ SCARD user_liked:{post_id}
            │
        ▼
    Cache Result (Redis)
        │
        ▼
    Return Count
```

---

## Like Event Processing

### Event Processing Pipeline

```
Like Event Published to Kafka
    │
    ▼
Kafka Consumer (Like Aggregator)
    │
    ├─ Group Events by Post ID
    ├─ Aggregate Like/Unlike Events
    │
    ▼
Update Counts
    │
    ├─ Real-time Update (Redis)
    │   └─ INCR/DECR like_count:{post_id}
    │
    └─ Batch Update (Cassandra)
        │
        └─ Update post_likes_summary table
        │
        ▼
    Store Event (Cassandra)
        │
        └─ For Historical Analysis
```

### Deduplication

**Challenge:** Prevent duplicate likes from same user.

**Solution:**
- **Redis Set**: Track user-post pairs
- **Atomic Operations**: Use Redis atomic operations
- **Distributed Locks**: Prevent race conditions

**Implementation:**
```python
class LikeService:
    def like_post(self, post_id, user_id):
        lock_key = f"lock:{post_id}:{user_id}"
        
        with redis.lock(lock_key, timeout=5):
            # Check if already liked
            liked_key = f"user_liked:{post_id}"
            if redis.sismember(liked_key, user_id):
                raise AlreadyLikedError()
            
            # Add like
            redis.sadd(liked_key, user_id)
            count = redis.incr(f"like_count:{post_id}")
            
            # Publish event
            kafka.publish('like-events', {
                'post_id': post_id,
                'user_id': user_id,
                'event_type': 'like',
                'timestamp': time.time()
            })
            
            return count
```

---

## Count Aggregation

### Aggregation Strategy

**Real-Time Aggregation:**
- Update Redis count immediately
- Low latency
- For display

**Batch Aggregation:**
- Aggregate events in batches
- Update Cassandra
- For historical data

**Implementation:**
```python
class CountAggregator:
    def aggregate_likes(self, events):
        # Group by post_id
        post_events = {}
        for event in events:
            post_id = event['post_id']
            if post_id not in post_events:
                post_events[post_id] = []
            post_events[post_id].append(event)
        
        # Aggregate per post
        for post_id, events in post_events.items():
            like_count = sum(1 for e in events if e['event_type'] == 'like')
            unlike_count = sum(1 for e in events if e['event_type'] == 'unlike')
            
            # Update Redis
            redis.incrby(f"like_count:{post_id}", like_count - unlike_count)
            
            # Update Cassandra (batch)
            self.update_cassandra_summary(post_id, like_count - unlike_count)
```

---

## High-Profile User Optimization

### Optimization Strategies

**1. Separate Storage:**
- Store high-profile posts separately
- Optimized data structures
- Pre-aggregated counts

**2. Caching:**
- Aggressive caching for popular posts
- Longer TTL
- Pre-warming

**3. Batch Processing:**
- Batch like events for high-profile posts
- Reduce write load
- Periodic aggregation

**Implementation:**
```python
class HighProfileOptimizer:
    def is_high_profile(self, post_id):
        # Check if post has > 1M likes
        count = redis.get(f"like_count:{post_id}")
        return int(count or 0) > 1000000
    
    def optimize_storage(self, post_id):
        if self.is_high_profile(post_id):
            # Use optimized storage
            # - Pre-aggregated counts
            # - Batch updates
            # - Separate Redis instance
            return self.get_optimized_count(post_id)
        else:
            # Use standard storage
            return self.get_standard_count(post_id)
```

---

## Scalability Considerations

### 1. Horizontal Scaling

**Like Services:**
- Stateless services
- Scale horizontally (1000+ req/s per instance)
- Partition by post_id for local caching
- Load balancer distributes traffic

**Kafka:**
- Partition by post_id (ensures ordering per post)
- Parallel processing with consumer groups
- High throughput (1M+ events/second)
- Auto-scaling consumers based on lag

**Scaling Metrics:**
- **Like Operations**: 1M likes/second = 1000 instances (1000 req/s each)
- **Count Queries**: 100M queries/day = 100 instances (1000 req/s each)
- **Event Processing**: 1M events/second = 200 aggregator instances

### 2. Storage Optimization

**High-Profile Posts:**
- Separate storage tier (dedicated Redis instance)
- Pre-aggregation (pre-compute counts)
- Batch updates (reduce write load)
- Optimized data structures

**Regular Posts:**
- Standard Redis storage
- Real-time updates
- Efficient Set operations

**Storage Strategy:**
```python
class StorageOptimizer:
    def get_storage_tier(self, post_id: str) -> str:
        count = self.get_count(post_id)
        if count > 1000000:  # High-profile threshold
            return 'high_profile'
        return 'standard'
    
    def optimize_storage(self, post_id: str):
        tier = self.get_storage_tier(post_id)
        if tier == 'high_profile':
            # Use optimized storage
            return self.get_optimized_count(post_id)
        else:
            # Use standard storage
            return self.get_standard_count(post_id)
```

### 3. Count Optimization

**Caching:**
- Cache counts aggressively (Redis)
- Pre-compute for popular posts
- Invalidate on updates
- Multi-level caching (L1: Redis, L2: Application cache)

**Cache Strategy:**
- **Counts**: Persistent cache (updated on like/unlike)
- **User-Like Sets**: Redis Sets (O(1) operations)
- **Metadata**: Cache post metadata (TTL: 1 hour)

**Performance Targets:**
- **Cache Hit Rate**: > 95%
- **Count Query Latency**: < 10ms (p95)
- **Like Operation Latency**: < 50ms (p95)

### 4. Database Scaling

**Redis Scaling:**
- **Cluster Mode**: Deploy Redis cluster with hash slots
- **Sharding**: Shard by post_id hash
- **Replication**: 1 replica per master
- **Memory**: 100GB+ per cluster node

**Cassandra Scaling:**
- **Partitioning**: Partition by post_id
- **Replication**: 3 replicas per data center
- **Compaction**: Regular compaction for performance
- **Tuning**: Optimize read/write consistency levels

**PostgreSQL Scaling:**
- **Read Replicas**: 3-5 read replicas
- **Sharding**: Shard posts table by post_id
- **Connection Pooling**: PgBouncer for connection pooling

### 5. Event Processing Scaling

**Kafka Consumer Scaling:**
- **Consumer Groups**: Multiple consumer groups for parallel processing
- **Partition Assignment**: Assign partitions to consumers
- **Auto-Scaling**: Scale consumers based on lag
- **Batch Processing**: Process events in batches (100-1000 events)

**Aggregation Scaling:**
- **Real-time Aggregators**: Process events in real-time (low latency)
- **Batch Aggregators**: Process events in batches (high throughput)
- **Parallel Processing**: Process multiple posts in parallel

### 6. High-Profile Post Optimization

**Challenges:**
- Posts with 100M+ likes
- High read/write load
- Count accuracy critical

**Solutions:**
- **Separate Tier**: Dedicated Redis instance for high-profile posts
- **Pre-aggregation**: Pre-compute counts
- **Batch Updates**: Batch like events (reduce write load)
- **Read Optimization**: Optimize count queries
- **Sharding**: Shard user-like sets across multiple Redis instances

---

## Caching Strategy

### Cache Architecture

```
Like Count Request
    │
    ▼
Redis Cache
    │
    ├─ Cache Hit → Return (1-2ms)
    │
    └─ Cache Miss → Compute
        │
        └─ Count from Set or Database
        │
        └─ Cache Result
```

### Cache Keys

```
like_count:{post_id} → Like count
user_liked:{post_id} → Set of user IDs who liked
post:{post_id}:metadata → Post metadata
```

### Cache Invalidation

**Event-Based:**
- Invalidate on like/unlike
- Update count atomically

**TTL-Based:**
- Counts: No TTL (persistent)
- Metadata: 1 hour

---

## Load Balancing

### Load Balancer Architecture

```
Like Requests
    │
    ▼
Load Balancer
    │
    ├─ Like Service 1
    ├─ Like Service 2
    ├─ Count Service 1
    └─ Count Service 2
```

### Load Balancing Strategies

1. **Consistent Hashing**: Route by post_id (for local caching)
2. **Round-Robin**: Equal distribution
3. **Least Connections**: Route to server with fewest connections

---

## Security

### 1. Authentication & Authorization

**Authentication:**
- JWT tokens
- Validate user identity

**Authorization:**
- Users can only like/unlike their own actions
- Validate post access

### 2. Rate Limiting

**Rate Limits:**
- Per user: 1000 likes/minute
- Per IP: 100 likes/minute
- Prevent abuse

---

## Monitoring & Analytics

### Key Metrics

**Performance Metrics:**
- Like operation latency
- Count query latency
- Kafka processing latency

**Business Metrics:**
- Total likes per day
- Likes per post distribution
- High-profile post counts
- User engagement

---

## Deployment Strategy

### Infrastructure

**Cloud Provider**: AWS, GCP, or Azure

**Components:**
- **Compute**: Kubernetes (EKS/GKE)
- **Cache**: Redis (ElastiCache)
- **Database**: Cassandra (Keyspaces), PostgreSQL (RDS)
- **Message Queue**: Kafka (MSK)

---

## Capacity Planning

### Storage Estimates

**Like Events:**
- 1B likes/day × 365 days = 365B events/year
- 365B × 100 bytes = 36.5 TB/year

**User-Like Sets:**
- 1B posts × average 1000 likes = 1T user-post pairs
- 1T × 16 bytes = 16 TB

**After Compression:**
- **Total: ~20 TB/year**

### Compute Requirements

**Like Services:**
- 1B likes/day = 11.6K likes/sec average
- Peak: 11.6K × 10 = 116K likes/sec
- Each like: ~10ms processing
- Required servers: 116K / (1000/10) = 1,160 servers

**Count Services:**
- 100M count queries/day = 1.16K queries/sec average
- Peak: 1.16K × 10 = 11.6K queries/sec
- Each query: ~5ms (with caching)
- Required servers: 11.6K / (1000/5) = 58 servers

**Total Compute: ~1,220 servers**

---

## Technology Stack

### Recommended Stack

**Compute:**
- **Language**: Go or Java
- **Orchestration**: Kubernetes

**Cache:**
- **Redis** (ElastiCache)

**Database:**
- **Cassandra** (Keyspaces)
- **PostgreSQL** (RDS)

**Message Queue:**
- **Kafka** (MSK)

---

## Failure Scenarios & Handling

### 1. Redis Failure

**Scenario:** Redis cluster fails.

**Impact:** Cannot track likes or serve counts.

**Mitigation:**
- **Redis Cluster**: Multiple nodes, replication
- **Fallback**: Query Cassandra (slower)
- **Graceful Degradation**: Accept likes, sync later

### 2. Kafka Failure

**Scenario:** Kafka cluster fails.

**Impact:** Cannot buffer like events.

**Mitigation:**
- **Kafka Cluster**: Multiple brokers, replication
- **Local Buffering**: Buffer in service
- **Fallback**: Write directly to database

### 3. Count Inconsistency

**Scenario:** Count and actual likes mismatch.

**Impact:** Incorrect counts displayed.

**Mitigation:**
- **Reconciliation Job**: Periodic reconciliation
- **Database as Source of Truth**: Rebuild from events
- **Monitoring**: Alert on inconsistencies

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
- **User Trust**: Users expect accurate counts
- **Fairness**: Important for content creators

### 2. Storage: Redis Set vs Database

**Decision:** Redis Set for user-liked tracking.

**Trade-offs:**

| Storage | Pros | Cons |
|---------|------|------|
| **Redis Set** | Fast, efficient | Memory intensive |
| **Database** | Persistent | Slower |

**Why Redis Set:**
- **Performance**: O(1) operations
- **Efficiency**: Efficient for membership checks

### 3. Aggregation: Real-time vs Batch

**Decision:** Both (real-time for display, batch for history).

**Trade-offs:**

| Approach | Pros | Cons |
|----------|------|------|
| **Real-time** | Immediate updates | Higher load |
| **Batch** | Lower load | Delayed updates |

**Why Both:**
- **Real-time**: For user display
- **Batch**: For cost optimization and history

---

## Interview Discussion Points

### Key Questions to Address

1. **"How do you prevent duplicate likes?"**
   - **Answer**: 
     - Redis Set to track user-post pairs
     - Atomic operations (SADD returns 1 if new, 0 if exists)
     - Distributed locks for race conditions

2. **"How do you handle high-profile posts with millions of likes?"**
   - **Answer**:
     - Separate storage tier
     - Pre-aggregated counts
     - Batch processing
     - Optimized data structures

3. **"How do you ensure count accuracy?"**
   - **Answer**:
     - Exact counting (no approximation)
     - Atomic operations
     - Periodic reconciliation
     - Database as source of truth

4. **"How do you scale for billions of likes?"**
   - **Answer**:
     - Partition by post_id
     - Kafka for event streaming
     - Batch aggregation
     - Horizontal scaling

5. **"How do you handle unlike operations?"**
   - **Answer**:
     - Remove from Redis Set
     - Decrement count
     - Publish unlike event
     - Update aggregated counts

---

## References

- [Facebook Engineering Blog](https://engineering.fb.com/)
- [System Design Primer](https://github.com/donnemartin/system-design-primer)
- [Redis Sets](https://redis.io/commands/sadd/)

