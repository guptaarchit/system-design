# Top K Elements: App Store Rankings, Amazon Bestsellers, etc.

## Table of Contents
1. [Overview](#overview)
2. [Requirements](#requirements)
3. [High-Level Design (HLD)](#high-level-design-hld)
4. [Low-Level Design (LLD)](#low-level-design-lld)
5. [System Architecture](#system-architecture)
6. [Data Models](#data-models)
7. [API Design](#api-design)
8. [Ranking Algorithms](#ranking-algorithms)
9. [Real-time Updates](#real-time-updates)
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

A system to maintain and query top K elements (rankings) for various categories like app store rankings, Amazon bestsellers, trending products, etc. The system must handle high-frequency updates, maintain accurate rankings in real-time, support multiple ranking criteria, and provide fast queries for top K results.

**Key Features:**
- Real-time ranking updates
- Multiple ranking criteria (sales, ratings, downloads, views)
- Top K queries (top 10, top 100, etc.)
- Category-based rankings
- Time-based rankings (daily, weekly, monthly, all-time)
- Trending items detection
- Ranking history and analytics
- Multi-region support

---

## Requirements

### Functional Requirements

1. **Ranking Management**
   - Update item scores/ratings
   - Maintain rankings for multiple categories
   - Support multiple ranking criteria
   - Time-based rankings (daily, weekly, monthly)

2. **Query Operations**
   - Get top K items in a category
   - Get item rank
   - Get items in rank range (e.g., rank 10-20)
   - Filter by criteria

3. **Real-time Updates**
   - Update rankings in real-time
   - Handle high-frequency updates
   - Maintain consistency

4. **Analytics**
   - Ranking history
   - Trend analysis
   - Ranking changes over time

### Non-Functional Requirements

1. **Scalability**
   - Handle 100M+ items
   - Support 1M+ updates per second
   - Support 10K+ queries per second
   - Horizontal scaling

2. **Performance**
   - Top K query: < 10ms latency (p95)
   - Rank update: < 50ms latency (p95)
   - Real-time updates: < 1 second delay

3. **Reliability**
   - 99.9% uptime
   - No ranking data loss
   - Eventual consistency acceptable

---

## High-Level Design (HLD)

### System Overview

The Top K Elements System is a high-performance ranking system that maintains real-time rankings for millions of items across multiple categories. It uses Redis Sorted Sets for efficient ranking operations and supports multiple time windows and ranking criteria.

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Client Applications                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 │
│  │ Web Apps     │  │ Mobile Apps  │  │ API Clients  │                 │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                 │
└─────────┼─────────────────┼─────────────────┼──────────────────────────┘
          │                 │                 │
          └─────────────────┴─────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    API Gateway / Load Balancer                           │
│  - Request routing                                                      │
│  - Rate limiting                                                        │
│  - SSL termination                                                      │
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
│                    Ranking Service Layer                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 │
│  │ Query        │  │ Update       │  │ Batch        │                 │
│  │ Service      │  │ Service      │  │ Processor    │                 │
│  └──────────────┘  └──────────────┘  └──────────────┘                 │
└─────────────────────────────────────────────────────────────────────────┘
        │                    │                    │
        ▼                    ▼                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    Ranking Engine                                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 │
│  │ Redis        │  │ Score        │  │ Ranking      │                 │
│  │ Sorted Sets  │  │ Calculator   │  │ Manager     │                 │
│  └──────────────┘  └──────────────┘  └──────────────┘                 │
└─────────────────────────────────────────────────────────────────────────┘
        │                    │                    │
        ▼                    ▼                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         Data Layer                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │ Redis        │  │ PostgreSQL   │  │ Cassandra    │               │
│  │ Cluster      │  │ (Metadata)   │  │ (History)   │               │
│  └──────────────┘  └──────────────┘  └──────────────┘               │
└─────────────────────────────────────────────────────────────────────────┘
```

### Key Components

1. **Query Service**: Handles top K queries and rank lookups
2. **Update Service**: Processes score updates
3. **Batch Processor**: Batches updates for efficiency
4. **Ranking Engine**: Maintains sorted data structures
5. **Score Calculator**: Computes composite scores

### Design Principles

- **Performance First**: Sub-10ms query latency
- **Real-time Updates**: Near-instant ranking updates
- **Scalability**: Horizontal scaling for millions of items
- **Consistency**: Eventual consistency acceptable for rankings

---

## Low-Level Design (LLD)

### Ranking Service (Detailed)

```python
class RankingService:
    def __init__(self):
        self.redis = RedisCluster()
        self.cache = LRUCache(max_size=10000, ttl=5)
        self.item_db = DatabasePool()
    
    async def get_top_k(
        self, 
        category: str, 
        k: int, 
        time_window: str = 'daily'
    ) -> list:
        # Check cache first
        cache_key = f"top_k:{category}:{k}:{time_window}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        # Query Redis sorted set
        key = f"ranking:{category}:{time_window}"
        items = await self.redis.zrevrange(key, 0, k-1, withscores=True)
        
        # Enrich with item metadata
        item_ids = [item_id for item_id, _ in items]
        metadata = await self.item_db.batch_get_metadata(item_ids)
        
        # Format results
        results = [
            {
                'rank': idx + 1,
                'item_id': item_id,
                'score': score,
                **metadata.get(item_id, {})
            }
            for idx, (item_id, score) in enumerate(items)
        ]
        
        # Cache result
        self.cache.set(cache_key, results)
        
        return results
    
    async def get_rank(
        self, 
        category: str, 
        item_id: str, 
        time_window: str = 'daily'
    ) -> Optional[dict]:
        key = f"ranking:{category}:{time_window}"
        
        # Get rank (0-indexed)
        rank = await self.redis.zrevrank(key, item_id)
        if rank is None:
            return None
        
        # Get score
        score = await self.redis.zscore(key, item_id)
        
        return {
            'rank': rank + 1,
            'score': score,
            'item_id': item_id
        }
```

### Update Service (Detailed)

```python
class UpdateService:
    def __init__(self):
        self.redis = RedisCluster()
        self.batch_processor = BatchProcessor()
        self.score_calculator = ScoreCalculator()
        self.message_queue = MessageQueue()
    
    async def update_score(
        self, 
        item_id: str, 
        category: str, 
        criteria_updates: dict
    ):
        # Calculate new score
        current_score = await self.get_current_score(item_id, category)
        score_delta = self.score_calculator.calculate_delta(
            current_score, criteria_updates
        )
        new_score = current_score + score_delta
        
        # Add to batch processor
        await self.batch_processor.add_update(
            item_id, category, new_score
        )
        
        # Publish update event
        await self.message_queue.publish('score_update', {
            'item_id': item_id,
            'category': category,
            'old_score': current_score,
            'new_score': new_score,
            'score_delta': score_delta
        })
    
    async def get_current_score(self, item_id: str, category: str) -> float:
        # Try Redis first
        key = f"ranking:{category}:daily"
        score = await self.redis.zscore(key, item_id)
        if score is not None:
            return score
        
        # Fallback to database
        item = await self.item_db.get_item(item_id)
        return item.get('current_score', 0.0)
```

### Batch Processor (Detailed)

```python
class BatchProcessor:
    def __init__(self, batch_size: int = 1000, flush_interval: float = 1.0):
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.update_buffer = {}  # (category, time_window) -> [(item_id, score)]
        self.last_flush = time.time()
        self.redis = RedisCluster()
        self.lock_manager = DistributedLockManager()
    
    async def add_update(self, item_id: str, category: str, score: float):
        # Group by category and time window
        for time_window in ['daily', 'weekly', 'monthly', 'all_time']:
            key = (category, time_window)
            if key not in self.update_buffer:
                self.update_buffer[key] = []
            self.update_buffer[key].append((item_id, score))
        
        # Flush if batch is full
        total_updates = sum(len(updates) for updates in self.update_buffer.values())
        if total_updates >= self.batch_size:
            await self.flush()
        elif time.time() - self.last_flush > self.flush_interval:
            await self.flush()
    
    async def flush(self):
        if not self.update_buffer:
            return
        
        # Process each category/window combination
        tasks = [
            self.update_rankings(category, time_window, updates)
            for (category, time_window), updates in self.update_buffer.items()
        ]
        
        await asyncio.gather(*tasks)
        
        self.update_buffer.clear()
        self.last_flush = time.time()
    
    async def update_rankings(
        self, 
        category: str, 
        time_window: str, 
        updates: list
    ):
        key = f"ranking:{category}:{time_window}"
        
        # Use distributed lock to prevent race conditions
        async with self.lock_manager.acquire(f"ranking_lock:{key}"):
            # Batch update Redis sorted set
            score_map = {item_id: score for item_id, score in updates}
            await self.redis.zadd(key, score_map)
```

### Score Calculator (Detailed)

```python
class ScoreCalculator:
    def __init__(self):
        self.weights = {
            'downloads': 0.3,
            'ratings': 0.4,
            'reviews': 0.2,
            'sales': 0.1
        }
    
    def calculate_score(self, criteria: dict) -> float:
        score = (
            criteria.get('downloads', 0) * 0.001 * self.weights['downloads'] +
            criteria.get('average_rating', 0) * 20 * self.weights['ratings'] +
            criteria.get('total_reviews', 0) * 0.1 * self.weights['reviews'] +
            criteria.get('total_sales', 0) * 0.001 * self.weights['sales']
        )
        return score
    
    def calculate_delta(
        self, 
        current_score: float, 
        criteria_updates: dict
    ) -> float:
        # Calculate score for updates only
        update_score = self.calculate_score(criteria_updates)
        
        # Delta is proportional to update score
        return update_score * 0.1  # Scale factor
```

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                             │
│  (Web Apps, Mobile Apps, API Clients)                           │
└────────────────┬────────────────────────────────────────────────┘
                 │ HTTPS
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API Gateway / Load Balancer                   │
│              (NGINX, AWS ALB)                                    │
└────────────┬────────────────────────────────────┬────────────────┘
             │                                    │
             ▼                                    ▼
┌────────────────────────────┐      ┌────────────────────────────┐
│   Ranking Service          │      │   Update Service          │
│   - Top K Queries          │      │   - Score Updates          │
│   - Rank Queries           │      │   - Batch Processing       │
└────────────┬──────────────┘      └────────────┬───────────────┘
             │                                    │
             ▼                                    ▼
┌────────────────────────────────────────────────────────────────┐
│                      Ranking Engine                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Sorted     │  │   Heap        │  │   Skip List   │         │
│  │   Sets       │  │   Manager    │  │   Manager    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────┬────────────────────┬────────────────────┬──────────────────┘
     │                    │                    │
     ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  Message Queue  │  │   Cache Layer   │  │   Event Bus     │
│  (Kafka)        │  │    (Redis)      │  │   (Kafka)       │
└─────────────────┘  └─────────────────┘  └─────────────────┘
     │                    │                    │
     ▼                    ▼                    ▼
┌────────────────────────────────────────────────────────────────┐
│                      Data Layer                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Ranking    │  │   Item       │  │   History    │         │
│  │     DB       │  │     DB       │  │     DB       │         │
│  │  (Redis)     │  │ (PostgreSQL) │  │ (Cassandra)  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────────────────────────────────────────────┘
```

### Component Details

#### 1. Ranking Service
- **Purpose**: Handle ranking queries
- **Responsibilities**:
  - Top K queries
  - Rank lookups
  - Range queries

#### 2. Update Service
- **Purpose**: Handle score updates
- **Responsibilities**:
  - Accept score updates
  - Batch updates
  - Update rankings

#### 3. Ranking Engine
- **Purpose**: Maintain sorted rankings
- **Responsibilities**:
  - Maintain sorted data structures
  - Update rankings on score changes
  - Handle concurrent updates

---

## Data Models

### Item Score Structure

```json
{
  "item_id": "item_123",
  "category": "apps",
  "score": 95.5,
  "criteria": {
    "downloads": 1000000,
    "ratings": 4.5,
    "reviews": 5000,
    "sales": 50000
  },
  "last_updated": 1705312800000
}
```

### Ranking Data Structure (Redis Sorted Set)

```
Key: ranking:{category}:{time_window}
Type: Sorted Set (ZSET)
Score: item_score
Member: item_id

Example:
ranking:apps:daily -> ZSET
  - item_123 -> 95.5
  - item_456 -> 92.3
  - item_789 -> 90.1
```

### Database Schema

#### Items Table (PostgreSQL)

```sql
CREATE TABLE items (
    item_id VARCHAR(255) PRIMARY KEY,
    category VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL,
    current_score DECIMAL(10, 2),
    total_downloads BIGINT DEFAULT 0,
    average_rating DECIMAL(3, 2),
    total_reviews INTEGER DEFAULT 0,
    total_sales BIGINT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_category (category),
    INDEX idx_score (current_score DESC)
);
```

#### Ranking History Table (Cassandra)

```sql
CREATE TABLE ranking_history (
    category VARCHAR,
    time_window VARCHAR, -- daily, weekly, monthly
    timestamp TIMESTAMP,
    item_id VARCHAR,
    rank INT,
    score DECIMAL,
    PRIMARY KEY ((category, time_window, timestamp), rank)
) WITH CLUSTERING ORDER BY (rank ASC);
```

---

## API Design

### Ranking APIs

```
GET /api/v1/rankings/{category}/top?k=10&time_window=daily
GET /api/v1/rankings/{category}/item/{item_id}/rank?time_window=daily
GET /api/v1/rankings/{category}/range?start=10&end=20&time_window=daily
```

**Response:**
```json
{
  "category": "apps",
  "time_window": "daily",
  "rankings": [
    {
      "rank": 1,
      "item_id": "item_123",
      "score": 95.5,
      "name": "App Name"
    },
    {
      "rank": 2,
      "item_id": "item_456",
      "score": 92.3,
      "name": "Another App"
    }
  ],
  "total_items": 1000000
}
```

### Update APIs

```
POST /api/v1/rankings/update
Content-Type: application/json

{
  "item_id": "item_123",
  "category": "apps",
  "score_delta": 5.0,
  "criteria_updates": {
    "downloads": 1000,
    "ratings": 0.1
  }
}
```

---

## Ranking Algorithms

### Score Calculation

```python
def calculate_score(item):
    # Weighted combination of criteria
    score = (
        item.downloads * 0.3 +
        item.average_rating * 20 * 0.4 +
        item.total_reviews * 0.1 * 0.2 +
        item.total_sales * 0.001 * 0.1
    )
    return score
```

### Ranking Maintenance

#### Using Redis Sorted Sets

```python
class RankingManager:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def update_score(self, category, item_id, score, time_window='daily'):
        key = f"ranking:{category}:{time_window}"
        # Update sorted set
        self.redis.zadd(key, {item_id: score})
    
    def get_top_k(self, category, k, time_window='daily'):
        key = f"ranking:{category}:{time_window}"
        # Get top K items (descending order)
        items = self.redis.zrevrange(key, 0, k-1, withscores=True)
        return [
            {'item_id': item_id, 'score': score, 'rank': idx + 1}
            for idx, (item_id, score) in enumerate(items)
        ]
    
    def get_rank(self, category, item_id, time_window='daily'):
        key = f"ranking:{category}:{time_window}"
        # Get rank (0-indexed, so add 1)
        rank = self.redis.zrevrank(key, item_id)
        if rank is not None:
            score = self.redis.zscore(key, item_id)
            return {'rank': rank + 1, 'score': score}
        return None
```

### Time-based Rankings

```python
def update_time_based_rankings(item_id, score):
    # Update daily ranking
    update_score('apps', item_id, score, 'daily')
    
    # Update weekly ranking (last 7 days)
    update_score('apps', item_id, score, 'weekly')
    
    # Update monthly ranking (last 30 days)
    update_score('apps', item_id, score, 'monthly')
    
    # Update all-time ranking
    update_score('apps', item_id, score, 'all_time')
```

---

## Real-time Updates

### Update Flow

```
┌──────────┐         ┌──────────────┐         ┌──────────────┐
│  Client  │────────▶│   Update     │────────▶│   Message   │
│          │         │   Service    │         │    Queue     │
└──────────┘         └──────────────┘         └──────┬───────┘
                                                      │
                                                      ▼
                                            ┌─────────────────┐
                                            │   Batch         │
                                            │   Processor     │
                                            └──────┬──────────┘
                                                   │
                                                   ▼
                                            ┌─────────────────┐
                                            │   Ranking       │
                                            │   Engine        │
                                            └──────┬──────────┘
                                                   │
                                                   ▼
                                            ┌─────────────────┐
                                            │   Redis Sorted  │
                                            │   Sets          │
                                            └─────────────────┘
```

### Batch Processing

```python
class BatchProcessor:
    def __init__(self):
        self.update_buffer = {}
        self.batch_size = 1000
        self.batch_interval = 1  # seconds
    
    def add_update(self, item_id, score_delta):
        if item_id not in self.update_buffer:
            self.update_buffer[item_id] = 0
        self.update_buffer[item_id] += score_delta
    
    def process_batch(self):
        if not self.update_buffer:
            return
        
        # Get current scores
        current_scores = self.get_current_scores(list(self.update_buffer.keys()))
        
        # Update scores
        for item_id, delta in self.update_buffer.items():
            new_score = current_scores.get(item_id, 0) + delta
            self.update_ranking(item_id, new_score)
        
        # Clear buffer
        self.update_buffer = {}
```

---

## Fault Tolerance

### Fault Tolerance Strategy

The ranking system is designed to handle failures gracefully, ensuring ranking queries continue to work even when components fail.

### Component-Level Fault Tolerance

#### 1. Redis Failure Tolerance

**Redis Cluster:**

```python
class FaultTolerantRedis:
    def __init__(self):
        self.redis_cluster = RedisCluster()
        self.local_cache = LocalCache(max_size=10000, ttl=1)
        self.circuit_breaker = CircuitBreaker()
        self.fallback_db = DatabasePool()
    
    async def get_top_k_with_fallback(
        self, 
        category: str, 
        k: int, 
        time_window: str
    ) -> list:
        # Try Redis first
        if not self.circuit_breaker.is_open():
            try:
                return await self.redis_cluster.zrevrange(
                    f"ranking:{category}:{time_window}", 0, k-1
                )
            except Exception as e:
                self.circuit_breaker.record_failure()
        
        # Fallback to database
        return await self.fallback_db.get_top_k(category, k, time_window)
```

#### 2. Update Service Failure

**Message Queue Persistence:**

```python
class FaultTolerantUpdateService:
    async def update_score_with_persistence(
        self, 
        item_id: str, 
        category: str, 
        score: float
    ):
        # Publish to message queue (persistent)
        await self.message_queue.publish('score_update', {
            'item_id': item_id,
            'category': category,
            'score': score,
            'timestamp': time.time()
        })
        
        # Update Redis (best effort)
        try:
            await self.redis.zadd(
                f"ranking:{category}:daily",
                {item_id: score}
            )
        except Exception:
            # Update will be processed from queue
            pass
```

---

## Failure Safety

### Failure Safety Principles

1. **No Ranking Loss**: Rankings persisted in multiple places
2. **Eventual Consistency**: Acceptable for ranking updates
3. **Recovery**: Automatic recovery from failures
4. **Audit Trail**: All updates logged

### Critical Failure Scenarios

#### 1. Ranking Data Loss Prevention

**Problem:** Ranking data lost on Redis failure.

**Solution:** Multi-level persistence.

```python
class RankingPersistence:
    async def update_ranking_safely(
        self, 
        category: str, 
        item_id: str, 
        score: float
    ):
        # Level 1: Update Redis (fast)
        await self.redis.zadd(f"ranking:{category}:daily", {item_id: score})
        
        # Level 2: Persist to database (durable)
        await self.db.update_ranking(category, item_id, score)
        
        # Level 3: Log to message queue (replay capability)
        await self.message_queue.publish('ranking_update', {
            'category': category,
            'item_id': item_id,
            'score': score
        })
```

#### 2. Update Ordering Preservation

**Problem:** Updates processed out of order.

**Solution:** Sequence numbers and idempotency.

```python
class OrderedUpdateProcessor:
    async def process_update(self, update: dict):
        # Check sequence number
        last_sequence = await self.get_last_sequence(update['item_id'])
        if update['sequence'] <= last_sequence:
            return  # Already processed
        
        # Process update
        await self.apply_update(update)
        
        # Update sequence
        await self.set_last_sequence(update['item_id'], update['sequence'])
```

---

## Scalability Considerations

### Horizontal Scaling

1. **Service Scaling**
   - Multiple Ranking Service instances
   - Multiple Update Service instances
   - Load balancer distributes requests

2. **Data Partitioning**
   - Partition by category
   - Each category on separate Redis instance
   - Shard large categories

3. **Redis Cluster**
   - Redis Cluster for distributed sorted sets
   - Hash slots for data distribution
   - Replication for high availability

### Horizontal Scaling Strategy

#### 1. Service Scaling

**Stateless Services:**

```python
class StatelessRankingService:
    def __init__(self):
        # No local state
        self.redis = RedisCluster()
        self.db = DatabasePool()
    
    async def get_top_k(self, category: str, k: int):
        # Can run on any instance
        return await self.query_ranking(category, k)
```

#### 2. Data Partitioning

**Category-Based Sharding:**

```python
class ShardedRankingStore:
    def __init__(self):
        self.shards = {}  # category -> redis_instance
    
    def get_shard(self, category: str) -> Redis:
        # Consistent hashing
        shard_index = hash(category) % len(self.redis_shards)
        return self.redis_shards[shard_index]
    
    async def get_top_k(self, category: str, k: int):
        shard = self.get_shard(category)
        return await shard.zrevrange(f"ranking:{category}:daily", 0, k-1)
```

#### 3. Redis Cluster Scaling

**Automatic Sharding:**

```python
class RedisClusterManager:
    def __init__(self):
        self.cluster = RedisCluster(
            startup_nodes=[
                {'host': 'redis1', 'port': 6379},
                {'host': 'redis2', 'port': 6379},
                {'host': 'redis3', 'port': 6379}
            ]
        )
    
    async def add_node(self, node_config: dict):
        # Add node to cluster
        await self.cluster.add_node(node_config)
        
        # Reshard data
        await self.reshard_cluster()
```

### Vertical Scaling

- **Redis Memory**: Increase memory for larger sorted sets
- **CPU**: More cores for concurrent operations

### Capacity Planning

**Traffic Estimates:**
- Items: 100M items
- Categories: 1000 categories
- Updates per second: 1M updates/second
- Queries per second: 10K queries/second

**Storage Estimates:**
- Redis Memory: 100M items × 100 bytes = 10GB per category
- 1000 categories × 10GB = 10TB (with replication: 30TB)

---

## Optimizations

### Performance Optimizations

#### 1. Query Optimization

**Top K Result Caching:**

```python
class TopKCacheOptimizer:
    def __init__(self):
        self.cache = LRUCache(max_size=10000, ttl=5)
    
    async def get_top_k_cached(
        self, 
        category: str, 
        k: int, 
        time_window: str
    ) -> list:
        cache_key = f"top_k:{category}:{k}:{time_window}"
        
        # Check cache
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        # Query Redis
        results = await self.query_top_k(category, k, time_window)
        
        # Cache result
        self.cache.set(cache_key, results)
        
        return results
```

#### 2. Batch Update Optimization

**Bulk Redis Operations:**

```python
class BulkUpdateOptimizer:
    async def update_scores_bulk(self, updates: list):
        # Group by category and time window
        by_key = {}
        for update in updates:
            key = f"ranking:{update['category']}:{update['time_window']}"
            if key not in by_key:
                by_key[key] = {}
            by_key[key][update['item_id']] = update['score']
        
        # Batch update each key
        tasks = [
            self.redis.zadd(key, score_map)
            for key, score_map in by_key.items()
        ]
        
        await asyncio.gather(*tasks)
```

#### 3. Score Calculation Optimization

**Incremental Score Updates:**

```python
class IncrementalScoreCalculator:
    def calculate_score_delta(
        self, 
        current_score: float, 
        criteria_delta: dict
    ) -> float:
        # Calculate delta instead of full recalculation
        delta = (
            criteria_delta.get('downloads', 0) * 0.001 * 0.3 +
            criteria_delta.get('ratings', 0) * 20 * 0.4 +
            criteria_delta.get('reviews', 0) * 0.1 * 0.2 +
            criteria_delta.get('sales', 0) * 0.001 * 0.1
        )
        return delta
```

#### 4. Memory Optimization

**Sparse Ranking Storage:**

```python
class SparseRankingStorage:
    async def store_ranking_efficiently(
        self, 
        category: str, 
        rankings: list
    ):
        # Only store top N items in Redis
        top_n = 10000  # Top 10K items
        
        if len(rankings) > top_n:
            # Store top N in Redis
            top_rankings = rankings[:top_n]
            await self.redis.zadd(
                f"ranking:{category}:daily",
                {item['item_id']: item['score'] for item in top_rankings}
            )
            
            # Store rest in database
            await self.db.store_rankings(category, rankings[top_n:])
        else:
            # Store all in Redis
            await self.redis.zadd(
                f"ranking:{category}:daily",
                {item['item_id']: item['score'] for item in rankings}
            )
```

---

## Caching Strategy

### Cache Layers

1. **Top K Cache**
   - Cache top 10, top 100 results
   - TTL: 1-5 seconds
   - Invalidate on updates

2. **Rank Cache**
   - Cache item ranks
   - TTL: 5-10 seconds
   - Invalidate on updates

3. **Item Details Cache**
   - Cache item metadata
   - TTL: 1 hour
   - Invalidate on item updates

---

## Load Balancing

- **Round Robin**: For stateless services
- **Consistent Hashing**: For Redis cluster routing
- **Geographic**: Route based on user location

---

## Security

### Authentication & Authorization

- **API Keys**: For programmatic access
- **Rate Limiting**: Per API key
- **Access Control**: Category-level permissions

---

## Monitoring & Analytics

### Key Metrics

- **Query Latency**: Top K query latency
- **Update Latency**: Score update latency
- **Cache Hit Rate**: Cache effectiveness
- **Redis Memory Usage**: Sorted set sizes
- **Update Rate**: Updates per second

---

## Capacity Planning

### Traffic Estimates

- **Items**: 100M items
- **Categories**: 1000 categories
- **Updates per Second**: 1M updates/second
- **Queries per Second**: 10K queries/second

### Storage Estimates

- **Redis Memory**: 
  - 100M items × 100 bytes = 10GB per category
  - 1000 categories × 10GB = 10TB (with replication)

---

## Technology Stack

### Backend

- **Language**: Go, Java, Python
- **Ranking Store**: Redis (Sorted Sets)
- **Database**: PostgreSQL, Cassandra
- **Message Queue**: Kafka

### Infrastructure

- **Cloud**: AWS, GCP
- **Container**: Kubernetes
- **Cache**: Redis Cluster

---

## Failure Scenarios & Handling

1. **Redis Failure**
   - **Mitigation**: Redis Cluster with replication
   - **Recovery**: Failover to replica

2. **High Update Rate**
   - **Mitigation**: Batching, throttling
   - **Recovery**: Queue updates, process asynchronously

---

## Trade-offs & Design Decisions

### 1. Redis Sorted Sets vs Database

**Decision**: Redis Sorted Sets for rankings

**Rationale**: O(log N) updates, O(log N + K) top K queries, much faster than database

### 2. Real-time vs Batch Updates

**Decision**: Hybrid (real-time for critical, batch for others)

**Rationale**: Balance between accuracy and performance

---

## Interview Discussion Points

### Key Topics

1. **Data Structure Choice**
   - Why Redis Sorted Sets?
   - What are alternatives?

2. **Top K Query**
   - How do you efficiently get top K?
   - What's the time complexity?

3. **Real-time Updates**
   - How do you handle high-frequency updates?
   - How do you maintain consistency?

---

**Document Version**: 2.0  
**Last Updated**: January 2024

