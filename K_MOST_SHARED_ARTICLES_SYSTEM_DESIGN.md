# K Most Shared Articles in Time Windows System Design

## Table of Contents
1. [Overview](#overview)
2. [Requirements](#requirements)
3. [System Architecture](#system-architecture)
4. [Database Design](#database-design)
5. [API Design](#api-design)
6. [Share Event Processing](#share-event-processing)
7. [Real-Time Aggregation](#real-time-aggregation)
8. [Time Window Management](#time-window-management)
9. [Top-K Algorithm](#top-k-algorithm)
10. [Scalability Considerations](#scalability-considerations)
11. [Caching Strategy](#caching-strategy)
12. [Load Balancing](#load-balancing)
13. [Security](#security)
14. [Monitoring & Analytics](#monitoring--analytics)
15. [Deployment Strategy](#deployment-strategy)
16. [Capacity Planning](#capacity-planning)
17. [Technology Stack](#technology-stack)
18. [Failure Scenarios & Handling](#failure-scenarios--handling)
19. [Trade-offs & Design Decisions](#trade-offs--design-decisions)
20. [Interview Discussion Points](#interview-discussion-points)

---

## Overview

A system to identify and rank the K most shared articles across different time windows (24 hours, 1 hour, 5 minutes). The system must handle millions of share events per second, provide real-time rankings, and support multiple time windows simultaneously.

**Key Features:**
- Real-time share event processing
- Multiple time windows (5 minutes, 1 hour, 24 hours)
- Top-K ranking per time window
- Real-time updates
- Historical rankings
- Multi-tenant support

---

## Requirements

### Functional Requirements

1. **Share Event Tracking**
   - Record article share events
   - Track share metadata (user, timestamp, platform)
   - Handle high write throughput

2. **Time Window Aggregation**
   - Aggregate shares by time windows
   - Support multiple windows simultaneously
   - Sliding window support

3. **Top-K Ranking**
   - Calculate top K articles per window
   - Real-time ranking updates
   - Handle ties (same share count)

4. **Query Interface**
   - Get top K articles for a window
   - Get article rank
   - Get share count for article

5. **Historical Data**
   - Store historical rankings
   - Query past rankings
   - Trend analysis

### Non-Functional Requirements

1. **Scalability**
   - Handle 10M+ share events/second
   - Support millions of articles
   - Horizontal scaling

2. **Performance**
   - Share event processing: < 10ms latency
   - Top-K query: < 100ms latency
   - Real-time updates: < 1 second delay

3. **Accuracy**
   - Exact counts (no approximation)
   - Handle concurrent updates
   - No duplicate counting

4. **Availability**
   - 99.9% uptime
   - Automatic failover
   - Zero data loss

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Share Event Sources                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   Web    │  │  Mobile  │  │   API    │  │  Partner │   │
│  │   App    │  │   App    │  │ Clients  │  │   APIs   │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼───────────┘
        │             │             │             │
        └─────────────┴─────────────┴─────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│              Load Balancer / API Gateway                     │
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
│              Share Event Ingestion Service                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │Ingestion │  │Ingestion │  │Ingestion │  │Ingestion │   │
│  │ Service  │  │ Service  │  │ Service  │  │ Service  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼───────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│              Message Queue (Kafka)                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Topic   │  │  Topic   │  │  Topic   │  │  Topic   │   │
│  │(Shares)  │  │(Shares)  │  │(Shares)  │  │(Shares)  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼───────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│              Real-Time Aggregation Service                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │Aggregator│  │Aggregator│  │Aggregator│  │Aggregator│   │
│  │(5min)    │  │(1hour)   │  │(24hour)  │  │(Batch)   │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼───────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│              Storage Layer                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Redis   │  │  Redis   │  │Cassandra │  │PostgreSQL│   │
│  │(Counts)  │  │(Top-K)   │  │(Events)  │  │(Metadata)│   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼───────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│              Query Service                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Query   │  │  Query   │  │  Query   │  │  Query   │   │
│  │ Service  │  │ Service  │  │ Service  │  │ Service  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼───────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│              Caching Layer (Redis)                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Redis   │  │  Redis   │  │  Redis   │  │  Redis   │   │
│  │ Cluster  │  │ Cluster  │  │ Cluster  │  │ Cluster  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Component Details

#### 1. Share Event Ingestion
- **Responsibilities**:
  - Accept share events
  - Validate events
  - Route to Kafka

#### 2. Real-Time Aggregators
- **5-Minute Aggregator**: Sliding 5-minute windows
- **1-Hour Aggregator**: Sliding 1-hour windows
- **24-Hour Aggregator**: Sliding 24-hour windows
- **Batch Aggregator**: Historical aggregation

#### 3. Storage
- **Redis**: Real-time counts and Top-K rankings
- **Cassandra**: Share event history
- **PostgreSQL**: Article metadata

#### 4. Query Service
- **Responsibilities**:
  - Serve Top-K queries
  - Get article ranks
  - Get share counts

---

## Database Design

### Redis Schema

#### Share Counts (Per Window)
```
Key: shares:{window}:{article_id}
Type: String (Integer)
Value: Share count
TTL: Window duration + buffer
```

#### Top-K Rankings (Per Window)
```
Key: topk:{window}:{k}
Type: Sorted Set (ZSET)
Members: article_id
Score: share_count
TTL: Window duration + buffer
```

**Example:**
```redis
ZADD topk:5min:100 article_123 1500
ZADD topk:5min:100 article_456 1200
ZREVRANGE topk:5min:100 0 99 WITHSCORES
```

### Cassandra Schema

#### Share Events Table
```cql
CREATE TABLE share_events (
    article_id TEXT,
    timestamp TIMESTAMP,
    user_id TEXT,
    platform TEXT,
    share_id UUID,
    PRIMARY KEY ((article_id), timestamp, share_id)
) WITH CLUSTERING ORDER BY (timestamp DESC);
```

#### Window Aggregates Table
```cql
CREATE TABLE window_aggregates (
    window_type TEXT,  -- '5min', '1hour', '24hour'
    window_start TIMESTAMP,
    article_id TEXT,
    share_count COUNTER,
    PRIMARY KEY ((window_type, window_start), article_id)
);
```

### PostgreSQL Schema

#### Articles Table
```sql
CREATE TABLE articles (
    article_id VARCHAR(255) PRIMARY KEY,
    title VARCHAR(500),
    author VARCHAR(255),
    published_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_published_at (published_at)
) ENGINE=InnoDB;
```

---

## API Design

### Share Event API

**Record Share**
```
POST /api/v1/shares
Content-Type: application/json

Request:
{
    "article_id": "article_123",
    "user_id": "user_456",
    "platform": "twitter",
    "timestamp": 1609459200
}

Response:
{
    "success": true,
    "share_id": "share_789"
}
```

### Query API

**Get Top K Articles**
```
GET /api/v1/articles/top?window=5min&k=100

Response:
{
    "window": "5min",
    "k": 100,
    "articles": [
        {
            "article_id": "article_123",
            "title": "Example Article",
            "share_count": 1500,
            "rank": 1
        },
        {
            "article_id": "article_456",
            "title": "Another Article",
            "share_count": 1200,
            "rank": 2
        }
    ],
    "updated_at": "2024-01-15T10:30:00Z"
}
```

**Get Article Rank**
```
GET /api/v1/articles/{article_id}/rank?window=1hour

Response:
{
    "article_id": "article_123",
    "window": "1hour",
    "rank": 5,
    "share_count": 5000,
    "updated_at": "2024-01-15T10:30:00Z"
}
```

**Get Share Count**
```
GET /api/v1/articles/{article_id}/shares?window=24hour

Response:
{
    "article_id": "article_123",
    "window": "24hour",
    "share_count": 50000,
    "updated_at": "2024-01-15T10:30:00Z"
}
```

---

## Data Flow Diagrams

### Share Event Processing Flow

```
Share Event Received
    │
    ▼
Ingestion Service
    │
    ├─ Validate Event
    ├─ Deduplicate (Check if already processed)
    │
    ▼
Publish to Kafka
    │
    ├─ Topic: share-events
    ├─ Partition by article_id (for ordering)
    │
    ▼
Real-Time Aggregators (Parallel Processing)
    │
    ├─ 5-Minute Aggregator
    │   ├─ Update Redis Counter: shares:5min:{article_id}
    │   └─ Update Top-K: ZADD topk:5min:100 {article_id} {count}
    │
    ├─ 1-Hour Aggregator
    │   ├─ Update Redis Counter: shares:1hour:{article_id}
    │   └─ Update Top-K: ZADD topk:1hour:100 {article_id} {count}
    │
    └─ 24-Hour Aggregator
        ├─ Update Redis Counter: shares:24hour:{article_id}
        └─ Update Top-K: ZADD topk:24hour:100 {article_id} {count}
    │
    ▼
Store Event in Cassandra (Async)
    │
    └─ For Historical Analysis
```

### Top-K Query Flow

```
Query Request: Get Top 100 (5-minute window)
    │
    ▼
Query Service
    │
    ├─ Check Cache (Redis)
    │   └─ Cache Hit → Return (1-5ms)
    │
    └─ Cache Miss → Continue
        │
        ▼
    Query Redis Sorted Set
        │
        └─ ZREVRANGE topk:5min:100 0 99 WITHSCORES
        │
        ▼
    Enrich with Article Metadata
        │
        ├─ Batch Fetch from PostgreSQL
        └─ Add title, author, etc.
        │
        ▼
    Cache Results (Redis)
        │
        ▼
    Return Results
```

---

## Share Event Processing

### Deduplication

**Challenge:** Prevent duplicate counting of same share.

**Solution:**
- **Idempotency Key**: Use (user_id, article_id, timestamp) as key
- **Redis Set**: Track processed shares
- **TTL**: Expire after window duration

**Implementation:**
```python
class ShareEventProcessor:
    def process_share(self, article_id, user_id, timestamp):
        # Generate idempotency key
        idempotency_key = f"share:{user_id}:{article_id}:{timestamp}"
        
        # Check if already processed
        if redis.exists(idempotency_key):
            return  # Duplicate, skip
        
        # Mark as processed
        redis.setex(idempotency_key, 3600, "1")  # 1 hour TTL
        
        # Process share
        self.increment_counters(article_id)
```

### Counter Updates

**Atomic Operations:**
- Use Redis INCR for counters
- Use Redis ZADD for Top-K updates
- Ensure atomicity

**Implementation:**
```python
def increment_counters(article_id):
    windows = ['5min', '1hour', '24hour']
    
    for window in windows:
        # Increment counter
        count = redis.incr(f"shares:{window}:{article_id}")
        
        # Update Top-K sorted set
        redis.zadd(f"topk:{window}:100", {article_id: count})
        
        # Set TTL
        redis.expire(f"shares:{window}:{article_id}", get_window_ttl(window))
        redis.expire(f"topk:{window}:100", get_window_ttl(window))
```

---

## Real-Time Aggregation

### Sliding Window Aggregation

**5-Minute Window:**
- Track shares in last 5 minutes
- Update every second
- Use Redis with TTL

**1-Hour Window:**
- Track shares in last 1 hour
- Update every minute
- Use Redis with TTL

**24-Hour Window:**
- Track shares in last 24 hours
- Update every 5 minutes
- Use Redis with TTL

**Implementation:**
```python
class WindowAggregator:
    def __init__(self, window_size_seconds):
        self.window_size = window_size_seconds
        self.update_interval = min(window_size_seconds // 10, 60)  # Update 10x per window or every 60s
    
    def aggregate(self, share_events):
        current_time = time.time()
        window_start = current_time - self.window_size
        
        # Process events in window
        for event in share_events:
            if event.timestamp >= window_start:
                self.process_event(event)
        
        # Cleanup old data
        self.cleanup_old_data(window_start)
    
    def process_event(self, event):
        # Increment counter
        redis.incr(f"shares:{self.window_size}:{event.article_id}")
        
        # Update Top-K
        count = redis.get(f"shares:{self.window_size}:{event.article_id}")
        redis.zadd(f"topk:{self.window_size}:100", {event.article_id: count})
```

---

## Time Window Management

### Window Definition

**5-Minute Window:**
- Current window: Last 5 minutes
- Sliding: Updates continuously
- TTL: 10 minutes (buffer)

**1-Hour Window:**
- Current window: Last 1 hour
- Sliding: Updates every minute
- TTL: 2 hours (buffer)

**24-Hour Window:**
- Current window: Last 24 hours
- Sliding: Updates every 5 minutes
- TTL: 48 hours (buffer)

### Window Cleanup

**Cleanup Strategy:**
- Remove expired counters
- Remove expired Top-K entries
- Archive to Cassandra

**Implementation:**
```python
def cleanup_expired_windows():
    windows = ['5min', '1hour', '24hour']
    
    for window in windows:
        # Get all keys for window
        keys = redis.keys(f"shares:{window}:*")
        
        for key in keys:
            ttl = redis.ttl(key)
            if ttl < 0:  # Expired
                article_id = extract_article_id(key)
                
                # Archive to Cassandra
                archive_to_cassandra(window, article_id, redis.get(key))
                
                # Delete from Redis
                redis.delete(key)
```

---

## Top-K Algorithm

### Redis Sorted Set Approach

**Advantages:**
- O(log N) insertion
- O(log N + K) retrieval
- Built-in ranking
- Automatic sorting

**Implementation:**
```python
def update_topk(article_id, count, window, k=100):
    # Add/update article in sorted set
    redis.zadd(f"topk:{window}:{k}", {article_id: count})
    
    # Keep only top K
    redis.zremrangebyrank(f"topk:{window}:{k}", 0, -(k+1))
    
    # Get top K
    topk = redis.zrevrange(f"topk:{window}:{k}", 0, k-1, withscores=True)
    
    return topk
```

### Alternative: Min-Heap Approach

**For Very Large K:**
- Use min-heap of size K
- Track minimum count
- Only update if count > minimum

**Implementation:**
```python
class TopKTracker:
    def __init__(self, k):
        self.k = k
        self.heap = []  # Min-heap
        self.article_counts = {}  # article_id -> count
    
    def update(self, article_id, count):
        if article_id in self.article_counts:
            # Update existing
            self.article_counts[article_id] = count
            self.heapify()
        else:
            # Add new if heap not full or count > min
            if len(self.heap) < self.k:
                heapq.heappush(self.heap, (count, article_id))
                self.article_counts[article_id] = count
            else:
                min_count, min_article = self.heap[0]
                if count > min_count:
                    heapq.heapreplace(self.heap, (count, article_id))
                    del self.article_counts[min_article]
                    self.article_counts[article_id] = count
    
    def get_topk(self):
        return sorted(self.article_counts.items(), key=lambda x: x[1], reverse=True)[:self.k]
```

---

## Scalability Considerations

### 1. Horizontal Scaling

**Partitioning:**
- Partition by article_id
- Distribute load across aggregators
- Use Kafka partitioning

**Sharding:**
- Shard Redis by window type
- Shard Cassandra by article_id
- Distribute queries

### 2. Write Scaling

**Batching:**
- Batch share events
- Reduce Redis operations
- Increase throughput

**Parallel Processing:**
- Process windows in parallel
- Use multiple aggregators
- Scale horizontally

### 3. Read Scaling

**Caching:**
- Cache Top-K results
- Cache article metadata
- Reduce database queries

**Read Replicas:**
- Read from Redis replicas
- Distribute read load

---

## Caching Strategy

### Cache Architecture

```
Query Request
    │
    ▼
Redis Cache (Top-K Results)
    │
    ├─ Cache Hit → Return (1-5ms)
    │
    └─ Cache Miss → Compute Top-K
        │
        ▼
    Cache Results
        │
        ▼
    Return Results
```

### Cache Keys

```
topk:{window}:{k} → Top-K rankings
shares:{window}:{article_id} → Share count
article:{article_id} → Article metadata
```

### Cache Invalidation

**TTL-Based:**
- Top-K results: Window update interval
- Share counts: Window duration + buffer

**Event-Based:**
- Invalidate on significant count changes
- Invalidate on window rollover

---

## Load Balancing

### Load Balancer Architecture

```
Share Events / Queries
    │
    ▼
Load Balancer
    │
    ├─ Ingestion Service 1
    ├─ Ingestion Service 2
    ├─ Query Service 1
    └─ Query Service 2
```

### Load Balancing Strategies

1. **Round-Robin**: Equal distribution
2. **Consistent Hashing**: Route by article_id
3. **Least Connections**: Route to server with fewest connections

---

## Security

### 1. Authentication & Authorization

**Authentication:**
- API keys
- OAuth 2.0

**Authorization:**
- Rate limiting per API key
- Per-tenant quotas

### 2. Rate Limiting

**Rate Limits:**
- Share events: 1000/minute per user
- Queries: 100/minute per API key

---

## Monitoring & Analytics

### Key Metrics

**Performance Metrics:**
- Share event processing latency
- Top-K query latency
- Throughput (events/second)

**Business Metrics:**
- Total shares per window
- Unique articles shared
- Top articles

---

## Deployment Strategy

### Infrastructure

**Cloud Provider**: AWS, GCP, or Azure

**Components:**
- **Compute**: Kubernetes (EKS/GKE)
- **Message Queue**: Kafka (MSK)
- **Cache**: Redis (ElastiCache)
- **Storage**: Cassandra, PostgreSQL

---

## Capacity Planning

### Storage Estimates

**Share Events:**
- 10M events/second
- 10M × 200 bytes = 2 GB/second
- 2 GB/s × 86400 = 172.8 TB/day

**After Aggregation:**
- 1M unique articles
- 1M × 100 bytes = 100 MB per window
- **Total: ~300 MB** (3 windows)

### Compute Requirements

**Aggregation Service:**
- 10M events/second
- Each event: ~1ms processing
- Required servers: 10M / (1000/1) = 10,000 servers
- With batching (100 events/batch): **100 servers**

---

## Technology Stack

### Recommended Stack

**Compute:**
- **Language**: Go or Java
- **Orchestration**: Kubernetes

**Message Queue:**
- **Kafka** (MSK or Confluent Cloud)

**Storage:**
- **Redis** (ElastiCache)
- **Cassandra** (Keyspaces)
- **PostgreSQL** (RDS)

---

## Failure Scenarios & Handling

### 1. Redis Failure

**Scenario:** Redis cluster fails.

**Impact:** Cannot update counters or Top-K.

**Mitigation:**
- **Redis Cluster**: Multiple nodes, replication
- **Fallback**: Write to Kafka, replay later
- **Backup**: Periodic snapshots

### 2. Kafka Failure

**Scenario:** Kafka cluster fails.

**Impact:** Cannot buffer share events.

**Mitigation:**
- **Kafka Cluster**: Multiple brokers, replication
- **Local Buffering**: Buffer in ingestion service
- **Fallback**: Write to S3, process later

### 3. High Cardinality

**Scenario:** Millions of unique articles.

**Impact:** Redis memory exhaustion.

**Mitigation:**
- **Sharding**: Shard Redis by article_id
- **TTL**: Expire old counters
- **Sampling**: Sample for very old articles

---

## Trade-offs & Design Decisions

### 1. Storage: Redis vs Database

**Decision:** Redis for real-time, Database for historical.

**Trade-offs:**

| Aspect | Redis | Database |
|--------|-------|----------|
| **Latency** | Very Low | Low |
| **Throughput** | Very High | High |
| **Durability** | Lower | Higher |
| **Cost** | Higher | Lower |

**Why Redis:**
- **Performance**: Sub-millisecond latency needed
- **Real-time**: Top-K updates in real-time

### 2. Accuracy: Exact vs Approximate

**Decision:** Exact counts (no approximation).

**Trade-offs:**

| Approach | Pros | Cons |
|----------|------|------|
| **Exact** | Accurate | Higher cost |
| **Approximate** | Lower cost | Less accurate |

**Why Exact:**
- **Trust**: Users expect accurate rankings
- **Fairness**: Important for content creators

### 3. Window: Fixed vs Sliding

**Decision:** Sliding windows.

**Trade-offs:**

| Approach | Pros | Cons |
|----------|------|------|
| **Fixed** | Simpler | Less smooth |
| **Sliding** | Smoother | More complex |

**Why Sliding:**
- **User Experience**: Smoother updates
- **Accuracy**: More accurate rankings

---

## Interview Discussion Points

### Key Questions to Address

1. **"How do you handle duplicate shares?"**
   - **Answer**: 
     - Idempotency keys (user_id, article_id, timestamp)
     - Redis Set to track processed shares
     - TTL-based expiration

2. **"How do you ensure accuracy?"**
   - **Answer**:
     - Exact counting (no approximation)
     - Atomic operations (Redis INCR, ZADD)
     - Deduplication

3. **"How do you handle high write throughput?"**
   - **Answer**:
     - Kafka for buffering
     - Batching share events
     - Parallel processing
     - Horizontal scaling

4. **"How do you optimize Top-K queries?"**
   - **Answer**:
     - Redis Sorted Sets (O(log N + K))
     - Caching Top-K results
     - Pre-computation
     - Sharding

5. **"How do you handle window rollover?"**
   - **Answer**:
     - Sliding windows (continuous updates)
     - TTL-based expiration
     - Archive old data to Cassandra
     - Gradual cleanup

---

## High-Level Design (HLD)

### System Overview

The K Most Shared Articles system follows a real-time stream processing architecture:

1. **Ingestion Layer**: Receives share events from multiple sources
2. **Message Queue**: Buffers events for processing (Kafka)
3. **Processing Layer**: Real-time aggregators for each time window
4. **Storage Layer**: Redis for real-time counts, Cassandra for history
5. **Query Layer**: Serves Top-K queries with low latency

### Component Architecture

**Core Components:**
- **Ingestion Service**: Validates and routes share events
- **5-Minute Aggregator**: Processes 5-minute sliding windows
- **1-Hour Aggregator**: Processes 1-hour sliding windows
- **24-Hour Aggregator**: Processes 24-hour sliding windows
- **Query Service**: Serves Top-K queries with enrichment

---

## Low-Level Design (LLD)

### Share Event Processor

```python
class ShareEventProcessor:
    def __init__(self, redis_client, kafka_producer):
        self.redis = redis_client
        self.kafka = kafka_producer
        self.dedup_ttl = 3600  # 1 hour
    
    def process_share(self, article_id: str, user_id: str, timestamp: int):
        # Generate idempotency key
        idempotency_key = f"share:{user_id}:{article_id}:{timestamp}"
        
        # Check if already processed
        if self.redis.exists(idempotency_key):
            return {'success': False, 'reason': 'duplicate'}
        
        # Mark as processed
        self.redis.setex(idempotency_key, self.dedup_ttl, "1")
        
        # Publish to Kafka (partitioned by article_id for ordering)
        self.kafka.send('share-events', {
            'article_id': article_id,
            'user_id': user_id,
            'timestamp': timestamp
        }, key=article_id)
        
        return {'success': True}
```

### Window Aggregator Implementation

```python
class WindowAggregator:
    def __init__(self, window_size_seconds: int, redis_client):
        self.window_size = window_size_seconds
        self.redis = redis_client
        self.k = 100  # Top 100
    
    def process_event(self, event: dict):
        article_id = event['article_id']
        timestamp = event['timestamp']
        
        windows = ['5min', '1hour', '24hour']
        
        for window in windows:
            # Increment counter
            count_key = f"shares:{window}:{article_id}"
            count = self.redis.incr(count_key)
            
            # Update Top-K sorted set
            topk_key = f"topk:{window}:{self.k}"
            self.redis.zadd(topk_key, {article_id: count})
            
            # Set TTL
            ttl = self.get_window_ttl(window)
            self.redis.expire(count_key, ttl)
            self.redis.expire(topk_key, ttl)
            
            # Trim to top K
            self.redis.zremrangebyrank(topk_key, 0, -(self.k + 1))
    
    def get_topk(self, window: str, k: int) -> list:
        topk_key = f"topk:{window}:{k}"
        results = self.redis.zrevrange(topk_key, 0, k - 1, withscores=True)
        
        return [
            {'article_id': article_id, 'share_count': int(count)}
            for article_id, count in results
        ]
```

---

## Fault Tolerance

### Redis Cluster Resilience

**Replication:**
- Redis Cluster with 3 master + 3 replica nodes per shard
- Automatic failover using Redis Sentinel
- Data sharded across multiple nodes

**Failure Handling:**
- Read from replica if master fails
- Write to new master after failover
- Replicate data to new replica

### Kafka Resilience

**Cluster Configuration:**
- Multi-broker Kafka cluster (minimum 3 brokers)
- Topic replication factor: 3
- Producer acknowledgments: `acks=all`

**Failure Handling:**
- Continue with remaining brokers
- Producer retries with exponential backoff
- Consumer group rebalancing on broker failure

### Aggregator Resilience

**Multiple Instances:**
- Multiple aggregator instances per window
- Kafka consumer groups for parallel processing
- Idempotent processing (deduplication)

---

## Optimizations

### Redis Optimization

**Sorted Set Optimization:**
- Only maintain top K in sorted set
- Trim excess entries periodically
- Use ZREMRANGEBYRANK for efficient trimming

**Memory Optimization:**
- Compress article IDs if possible
- Use efficient data structures
- TTL-based expiration

### Processing Optimization

**Batching:**
- Batch multiple events per window update
- Reduce Redis operations
- Improve throughput

**Parallel Processing:**
- Process windows in parallel
- Use multiple aggregator instances
- Partition Kafka topics by article_id

---

## Failure Safety

### Redis Failure

**Scenario: Redis Cluster Failure**
- **Impact**: Cannot update counters or Top-K
- **Mitigation**:
  - Redis Cluster with replication
  - Fallback: Write to Kafka, replay later
  - Periodic snapshots
- **Recovery**:
  - Restore from snapshot
  - Replay events from Kafka
  - Rebuild Top-K from counters

### Kafka Failure

**Scenario: Kafka Unavailable**
- **Impact**: Events not processed
- **Mitigation**:
  - Kafka cluster with multiple brokers
  - Local buffering in ingestion service
  - Fallback to database
- **Recovery**:
  - Kafka recovers, process buffered events
  - Replay from database
  - Verify no data loss

### Count Inconsistency

**Scenario: Counts Don't Match Actual Shares**
- **Impact**: Incorrect Top-K rankings
- **Mitigation**:
  - Periodic reconciliation job
  - Compare Redis counts with Cassandra events
  - Alert on discrepancies
- **Recovery**:
  - Recalculate counts from events
  - Update Redis
  - Rebuild Top-K

---

## Scalability

### Horizontal Scaling

**Aggregator Scaling:**
- Add more aggregator instances
- Kafka partitions for parallel processing
- Scale independently per window

**Redis Scaling:**
- Redis Cluster with sharding
- Add shards as needed
- Distribute load across nodes

### Performance Scaling

**Throughput Scaling:**
- Increase Kafka partitions
- Add more aggregator instances
- Optimize Redis operations

**Query Scaling:**
- Cache Top-K results
- Use read replicas
- Optimize sorted set queries

---

## References

- [Redis Sorted Sets](https://redis.io/commands/zadd/)
- [Kafka Streams](https://kafka.apache.org/documentation/streams/)
- [System Design Primer](https://github.com/donnemartin/system-design-primer)

