# Design Facebook Likes Feature with Live Updates

## Table of Contents
1. [Overview](#overview)
2. [Requirements](#requirements)
3. [System Architecture](#system-architecture)
4. [Database Design](#database-design)
5. [API Design](#api-design)
6. [Like Flow](#like-flow)
7. [Real-time Updates](#real-time-updates)
8. [Scalability Considerations](#scalability-considerations)
9. [Caching Strategy](#caching-strategy)
10. [Capacity Planning](#capacity-planning)
11. [Technology Stack](#technology-stack)
12. [Interview Discussion Points](#interview-discussion-points)

---

## Overview

A likes system with real-time updates that allows users to like posts/comments and see like counts update instantly. The system must handle millions of likes per second, provide real-time updates to all viewers, prevent duplicate likes, and scale horizontally.

**Key Features:**
- Like/unlike posts and comments
- Real-time like count updates
- Show who liked (for friends)
- Like notifications
- Aggregate like counts
- Handle high concurrency

---

## Requirements

### Functional Requirements

1. **Like Management**
   - Like/unlike posts
   - Like/unlike comments
   - Prevent duplicate likes
   - Toggle like (like if not liked, unlike if liked)

2. **Real-time Updates**
   - Update like count instantly
   - Push updates to all viewers
   - Show like animations

3. **Social Features**
   - Show friends who liked
   - Like notifications
   - Like history

### Non-Functional Requirements

1. **Scalability**
   - Handle 1M+ likes per second
   - Support 10M+ concurrent users
   - Process likes for billions of posts

2. **Performance**
   - Like action: < 100ms
   - Count query: < 50ms
   - Real-time update: < 200ms latency

3. **Reliability**
   - No duplicate likes
   - Accurate counts
   - Eventual consistency acceptable

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                             │
│  (Web Apps, Mobile Apps)                                        │
└────────────────┬────────────────────────────────────────────────┘
                 │ HTTPS / WebSocket
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API Gateway                                   │
└────────────┬────────────────────────────────────┬────────────────┘
             │                                    │
             ▼                                    ▼
┌────────────────────────────┐      ┌────────────────────────────┐
│   Like Service             │      │   WebSocket Service        │
│   - Process Likes          │      │   - Real-time Updates      │
│   - Validate Likes         │      │   - Connection Management  │
└────────────┬───────────────┘      └────────────┬───────────────┘
             │                                    │
             ▼                                    ▼
┌────────────────────────────────────────────────────────────────┐
│                    Message Queue                                 │
│              (Kafka)                                            │
│  Topics: likes, unlike, notifications                          │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Processing Layer                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Like       │  │   Count      │  │   Notification│        │
│  │   Processor  │  │   Aggregator │  │   Service    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Data Layer                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Likes      │  │   Counts      │  │   Users      │         │
│  │     DB       │  │   Cache       │  │     DB       │         │
│  │ (PostgreSQL) │  │  (Redis)      │  │ (PostgreSQL) │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────────────────────────────────────────────┘
```

### HLD Component Breakdown

**1. Client Layer**
- **Web Apps**: React-based web applications
- **Mobile Apps**: iOS/Android native apps

**2. API Gateway Layer**
- **API Gateway**: Routes requests to services
- **WebSocket Gateway**: Manages WebSocket connections

**3. Service Layer**
- **Like Service**: Processes like/unlike operations
- **WebSocket Service**: Manages real-time connections
- **Update Service**: Broadcasts updates to clients

**4. Processing Layer**
- **Like Processor**: Processes like events
- **Count Aggregator**: Aggregates counts
- **Notification Service**: Sends notifications

**5. Data Layer**
- **PostgreSQL**: Likes, users
- **Redis**: Counts, user-like mappings, WebSocket state

---

## Low-Level Design (LLD)

### Like Service LLD

```python
class LikeService:
    def __init__(self, redis: RedisClient, db: Database, kafka: KafkaProducer):
        self.redis = redis
        self.db = db
        self.kafka = kafka
    
    def toggle_like(self, user_id: int, target_type: str, target_id: int) -> dict:
        like_key = f"liked_by:{target_type}:{target_id}"
        count_key = f"like_count:{target_type}:{target_id}"
        
        # Check if already liked (atomic operation)
        is_liked = self.redis.sismember(like_key, user_id)
        
        if is_liked:
            # Unlike
            self.redis.srem(like_key, user_id)
            count = self.redis.decr(count_key)
            
            # Delete from database
            self.db.execute(
                "DELETE FROM likes WHERE user_id = %s AND target_type = %s AND target_id = %s",
                (user_id, target_type, target_id)
            )
            
            action = 'unlike'
        else:
            # Like
            self.redis.sadd(like_key, user_id)
            count = self.redis.incr(count_key)
            
            # Insert into database
            self.db.execute(
                "INSERT INTO likes (user_id, target_type, target_id) VALUES (%s, %s, %s)",
                (user_id, target_type, target_id)
            )
            
            action = 'like'
        
        # Publish update
        self.publish_update(target_type, target_id, action, user_id, count)
        
        return {
            'action': action,
            'count': count,
            'is_liked': not is_liked
        }
    
    def publish_update(self, target_type: str, target_id: int, action: str, 
                      user_id: int, count: int):
        # Publish to Kafka
        self.kafka.publish('like-updates', {
            'target_type': target_type,
            'target_id': target_id,
            'action': action,
            'user_id': user_id,
            'count': count,
            'timestamp': time.time()
        })
```

### WebSocket Update Service LLD

```python
class LikeUpdateService:
    def __init__(self, websocket_manager: WebSocketManager, redis_pubsub: RedisPubSub):
        self.websocket_manager = websocket_manager
        self.redis_pubsub = redis_pubsub
        self.subscriptions = {}  # target_key -> set of connections
    
    def subscribe(self, connection: WebSocket, target_type: str, target_id: int):
        target_key = f"{target_type}:{target_id}"
        if target_key not in self.subscriptions:
            self.subscriptions[target_key] = set()
        self.subscriptions[target_key].add(connection)
    
    def publish_update(self, target_type: str, target_id: int, action: str, 
                      user_id: int, count: int):
        target_key = f"{target_type}:{target_id}"
        
        if target_key in self.subscriptions:
            message = json.dumps({
                'type': action,
                'target_type': target_type,
                'target_id': target_id,
                'user_id': user_id,
                'count': count
            })
            
            disconnected = []
            for connection in list(self.subscriptions[target_key]):
                try:
                    connection.send(message)
                except Exception:
                    disconnected.append(connection)
            
            # Remove disconnected connections
            for conn in disconnected:
                self.subscriptions[target_key].discard(conn)
```

---

## Fault Tolerance

### Like Operation Fault Tolerance

**1. Idempotency**
- **Idempotent Operations**: Like/unlike operations are idempotent
- **Redis Set Operations**: Atomic operations prevent duplicates
- **Idempotency Keys**: Use keys for retry operations

**2. Distributed Locking**
- **Redis Locks**: Prevent race conditions
- **Lock Timeout**: Prevent deadlocks
- **Lock Retry**: Retry with exponential backoff

**3. Event Processing Resilience**
- **Kafka Replication**: 3 replicas per partition
- **Consumer Groups**: Parallel processing with fault tolerance
- **Dead Letter Queue**: Store failed events
- **Event Replay**: Replay events on recovery

### WebSocket Fault Tolerance

**1. Connection Resilience**
- **Automatic Reconnection**: Client reconnects on disconnect
- **Message Queue**: Queue messages during disconnection
- **Heartbeat**: Detect dead connections
- **Connection Pooling**: Efficient connection management

**2. Cross-Server Communication**
- **Redis Pub/Sub**: Broadcast across WebSocket servers
- **Sticky Sessions**: Route same client to same server
- **Message Replay**: Replay messages on reconnect

---

## Failure Safety

### Failure Scenarios & Handling

**1. Redis Failure**

**Scenario**: Redis cluster fails.

**Impact**: Cannot track likes or serve counts.

**Mitigation**:
- **Redis Cluster**: Multiple nodes with replication
- **Database Fallback**: Query database (slower)
- **Graceful Degradation**: Accept likes, sync later
- **Local Cache**: Use application-level cache

**Recovery**:
- **Failover**: Automatically failover to healthy nodes
- **Cache Warming**: Pre-populate cache from database
- **Count Rebuild**: Rebuild counts from database

**2. WebSocket Connection Failure**

**Scenario**: WebSocket connection drops.

**Impact**: Real-time updates not delivered.

**Mitigation**:
- **Reconnection**: Automatic reconnection
- **Polling Fallback**: Fallback to polling API
- **Message Queue**: Queue messages during disconnection
- **Redis Pub/Sub**: Cross-server communication

**Recovery**:
- **Reconnect**: Client automatically reconnects
- **Message Replay**: Replay queued messages
- **State Sync**: Sync state on reconnection

**3. Kafka Failure**

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

---

## Database Design

### Likes Table

```sql
CREATE TABLE likes (
    like_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    target_type VARCHAR(20) NOT NULL, -- post, comment
    target_id BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE KEY unique_user_target (user_id, target_type, target_id),
    INDEX idx_target (target_type, target_id),
    INDEX idx_user (user_id)
);
```

### Like Counts Cache (Redis)

```
Key: like_count:{target_type}:{target_id}
Type: String
Value: 1234
TTL: None (updated on like/unlike)

Key: liked_by:{target_type}:{target_id}
Type: Set
Members: {user_id_1, user_id_2, ...}
TTL: None
```

---

## API Design

### Like APIs

```
POST   /api/v1/likes
{
  "target_type": "post",
  "target_id": 123
}

DELETE /api/v1/likes
{
  "target_type": "post",
  "target_id": 123
}

GET    /api/v1/likes/count?target_type=post&target_id=123
GET    /api/v1/likes/users?target_type=post&target_id=123&limit=10
```

### WebSocket API

```javascript
// Connect
ws = new WebSocket("wss://api.example.com/likes/stream");

// Subscribe to post
ws.send(JSON.stringify({
  "action": "subscribe",
  "target_type": "post",
  "target_id": 123
}));

// Receive like updates
ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  if (update.type === 'like') {
    incrementLikeCount(update.target_id);
  } else if (update.type === 'unlike') {
    decrementLikeCount(update.target_id);
  }
};
```

---

## Like Flow

### Like Process

1. **User clicks like**
2. **Validate request** → Check authentication, target exists
3. **Check if already liked** → Query cache/database
4. **Toggle like** → Insert if not liked, delete if liked
5. **Update count** → Increment/decrement count cache
6. **Publish event** → Send to Kafka
7. **Push update** → Broadcast to WebSocket connections
8. **Send notification** → Notify post owner (if not self-like)

### Like Implementation

```python
class LikeService:
    def __init__(self):
        self.redis = Redis()
        self.db = Database()
    
    def toggle_like(self, user_id: int, target_type: str, target_id: int) -> dict:
        like_key = f"liked_by:{target_type}:{target_id}"
        count_key = f"like_count:{target_type}:{target_id}"
        
        # Check if already liked
        is_liked = self.redis.sismember(like_key, user_id)
        
        if is_liked:
            # Unlike
            self.redis.srem(like_key, user_id)
            self.redis.decr(count_key)
            
            # Delete from database
            self.db.execute(
                "DELETE FROM likes WHERE user_id = %s AND target_type = %s AND target_id = %s",
                (user_id, target_type, target_id)
            )
            
            action = 'unlike'
        else:
            # Like
            self.redis.sadd(like_key, user_id)
            self.redis.incr(count_key)
            
            # Insert into database
            self.db.execute(
                "INSERT INTO likes (user_id, target_type, target_id) VALUES (%s, %s, %s)",
                (user_id, target_type, target_id)
            )
            
            action = 'like'
        
        # Get updated count
        count = int(self.redis.get(count_key) or 0)
        
        # Publish update
        self.publish_update(target_type, target_id, action, user_id, count)
        
        return {
            'action': action,
            'count': count,
            'is_liked': not is_liked
        }
```

---

## Real-time Updates

### Update Distribution

```python
class LikeUpdateService:
    def __init__(self):
        self.websocket_connections = {}  # target_key -> set of connections
    
    def subscribe(self, connection, target_type: str, target_id: int):
        target_key = f"{target_type}:{target_id}"
        if target_key not in self.websocket_connections:
            self.websocket_connections[target_key] = set()
        self.websocket_connections[target_key].add(connection)
    
    def publish_update(self, target_type: str, target_id: int, action: str, user_id: int, count: int):
        target_key = f"{target_type}:{target_id}"
        
        if target_key in self.websocket_connections:
            message = json.dumps({
                'type': action,
                'target_type': target_type,
                'target_id': target_id,
                'user_id': user_id,
                'count': count
            })
            
            for connection in list(self.websocket_connections[target_key]):
                try:
                    connection.send(message)
                except:
                    self.websocket_connections[target_key].remove(connection)
```

---

## Scalability Considerations

### 1. Horizontal Scaling

**Like Services:**
- Multiple like service instances (stateless)
- Scale horizontally (1000+ req/s per instance)
- Load balancer distributes traffic
- Auto-scaling based on request rate

**WebSocket Services:**
- Multiple WebSocket server instances
- 10K-50K connections per server
- Sticky sessions for connection affinity
- Redis Pub/Sub for cross-server communication

**Scaling Metrics:**
- **Like Operations**: 1M likes/second = 1000 instances
- **WebSocket Connections**: 10M connections = 200-1000 servers
- **Message Throughput**: 100K messages/second per server

### 2. Redis Cluster Scaling

**Cluster Configuration:**
- **Hash Slots**: Distribute data across nodes
- **Replication**: 1 replica per master
- **Sharding**: Shard by target_id hash
- **Memory**: 100GB+ per cluster node

**Performance Targets:**
- **Operations**: 100K+ ops/second per node
- **Latency**: < 1ms (p95)
- **Availability**: 99.9% uptime

### 3. Kafka Partitioning

**Partition Strategy:**
- **Partition by target_id**: Ensures ordering per target
- **Multiple Partitions**: Parallel processing
- **Consumer Groups**: Load distribution
- **Auto-Scaling**: Scale consumers based on lag

**Performance Targets:**
- **Throughput**: 1M+ messages/second
- **Latency**: < 10ms (p95)
- **Durability**: 99.99% message delivery

### 4. Database Sharding

**Sharding Strategy:**
- **Shard by target_id**: Distribute load
- **Consistent Hashing**: Minimal rebalancing
- **Read Replicas**: Scale reads independently
- **Connection Pooling**: Efficient connection management

**Sharding Implementation:**
```python
class ShardManager:
    def __init__(self, num_shards: int):
        self.num_shards = num_shards
    
    def get_shard(self, target_id: int) -> int:
        return hash(target_id) % self.num_shards
    
    def route_query(self, target_id: int, query: str, params: tuple):
        shard_id = self.get_shard(target_id)
        conn = self.shard_connections[shard_id]
        return conn.execute(query, params)
```

### 5. WebSocket Scaling

**Connection Management:**
- **Sticky Sessions**: Route same client to same server
- **Connection Pooling**: Efficient connection management
- **Redis Pub/Sub**: Cross-server broadcast
- **Load Balancing**: Distribute connections

**Scaling Strategy:**
- **Per Server**: 10K-50K concurrent connections
- **Total Capacity**: 10M+ connections with 200-1000 servers
- **Message Throughput**: 100K messages/second per server

### 6. Caching Strategy

**Multi-Level Caching:**
- **L1 Cache**: Application-level cache (hot data)
- **L2 Cache**: Redis cache (counts, mappings)
- **L3 Cache**: Database query cache

**Cache Invalidation:**
- **Event-Based**: Invalidate on like/unlike
- **TTL-Based**: Set expiration for time-sensitive data
- **Version-Based**: Use version numbers for validation

---

## Caching Strategy

- **Like Counts**: Cache in Redis (updated on like/unlike)
- **Liked By Sets**: Store in Redis Sets
- **User Likes**: Cache user's likes (TTL: 5 minutes)

---

## Capacity Planning

- **Likes per Second**: 1M likes/second
- **Concurrent Users**: 10M users
- **Posts**: 1B+ posts
- **Redis Memory**: 1B posts × 100 bytes = 100GB (with compression)

---

## Technology Stack

- **Backend**: Go, Java
- **WebSocket**: Socket.io, ws
- **Message Queue**: Kafka
- **Database**: PostgreSQL, Redis Cluster

---

## Interview Discussion Points

1. **Concurrency**: How do you handle 1M+ likes per second?
2. **Real-time**: How do you push updates to all viewers?
3. **Consistency**: How do you ensure accurate counts?
4. **Idempotency**: How do you prevent duplicate likes?

---

**Document Version**: 1.0  
**Last Updated**: January 2024

