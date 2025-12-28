# Design a Feature to Show the Number of Users Viewing a Page

## Table of Contents
1. [Overview](#overview)
2. [Requirements](#requirements)
3. [System Architecture](#system-architecture)
4. [Data Models](#data-models)
5. [API Design](#api-design)
6. [Viewer Tracking](#viewer-tracking)
7. [Real-time Updates](#real-time-updates)
8. [Scalability Considerations](#scalability-considerations)
9. [Caching Strategy](#caching-strategy)
10. [Capacity Planning](#capacity-planning)
11. [Technology Stack](#technology-stack)
12. [Interview Discussion Points](#interview-discussion-points)

---

## Overview

A system to track and display the number of users currently viewing a page in real-time. The system must handle millions of concurrent page views, provide accurate counts, update counts in real-time, and scale horizontally.

**Key Features:**
- Track active viewers per page
- Real-time viewer count updates
- Distinguish unique viewers
- Handle page navigation
- Show "X people viewing" indicator
- Privacy considerations

---

## Requirements

### Functional Requirements

1. **Viewer Tracking**
   - Track when user views a page
   - Track when user leaves a page
   - Distinguish unique viewers
   - Handle page refreshes

2. **Count Display**
   - Show current viewer count
   - Update count in real-time
   - Format count (e.g., "1,234 people viewing")

3. **Privacy**
   - Anonymous tracking
   - No personal information stored
   - Respect user privacy settings

### Non-Functional Requirements

1. **Scalability**
   - Handle 10M+ concurrent page views
   - Support 1M+ unique pages
   - Process 100K+ viewer events per second

2. **Performance**
   - Track viewer: < 50ms
   - Get count: < 100ms
   - Real-time update: < 1 second delay

3. **Accuracy**
   - Accurate counts (within 1-2% tolerance)
   - Handle disconnections gracefully
   - Clean up stale viewers

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                             │
│  (Web Browsers, Mobile Apps)                                    │
└────────────────┬────────────────────────────────────────────────┘
                 │ HTTPS / WebSocket
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API Gateway                                   │
└────────────┬────────────────────────────────────┬────────────────┘
             │                                    │
             ▼                                    ▼
┌────────────────────────────┐      ┌────────────────────────────┐
│   Viewer Tracking Service  │      │   Count Service            │
│   - Track Viewers          │      │   - Get Counts              │
│   - Heartbeat Management   │      │   - Real-time Updates      │
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
│  │   Viewer     │  │   Count      │  │   Cleanup   │         │
│  │   Aggregator │  │   Calculator │  │   Service    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Storage Layer                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Active     │  │   Historical │  │   Metadata   │         │
│  │   Viewers    │  │   Counts     │  │              │         │
│  │  (Redis)     │  │ (Cassandra)  │  │ (PostgreSQL) │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────────────────────────────────────────────┘
```

---

## Data Models

### Viewer Tracking Structure (Redis)

```
Key: viewers:{page_id}
Type: Set
Members: {session_id_1, session_id_2, ...}
TTL: 5 minutes (refreshed on heartbeat)

Key: viewer:{session_id}
Type: Hash
Fields:
  - page_id: 123
  - last_seen: 1705312800000
TTL: 5 minutes
```

### Count Cache (Redis)

```
Key: count:{page_id}
Type: String
Value: 1234
TTL: 10 seconds
```

---

## API Design

### Tracking APIs

```
POST /api/v1/viewers/track
{
  "page_id": "page_123",
  "session_id": "session_abc"
}

POST /api/v1/viewers/heartbeat
{
  "page_id": "page_123",
  "session_id": "session_abc"
}

DELETE /api/v1/viewers/untrack
{
  "page_id": "page_123",
  "session_id": "session_abc"
}
```

### Count APIs

```
GET /api/v1/viewers/count?page_id=page_123
```

**Response:**
```json
{
  "page_id": "page_123",
  "count": 1234,
  "formatted": "1,234 people viewing",
  "timestamp": 1705312800000
}
```

### WebSocket API

```javascript
// Connect
ws = new WebSocket("wss://api.example.com/viewers/stream");

// Subscribe to page
ws.send(JSON.stringify({
  "action": "subscribe",
  "page_id": "page_123"
}));

// Receive count updates
ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  updateViewerCount(update.count);
};
```

---

## Viewer Tracking

### Tracking Implementation

```python
class ViewerTracker:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.viewer_ttl = 300  # 5 minutes
    
    def track_viewer(self, page_id: str, session_id: str):
        # Add to page viewers set
        viewer_key = f"viewers:{page_id}"
        self.redis.sadd(viewer_key, session_id)
        self.redis.expire(viewer_key, self.viewer_ttl)
        
        # Store session metadata
        session_key = f"viewer:{session_id}"
        self.redis.hset(session_key, mapping={
            'page_id': page_id,
            'last_seen': int(time.time() * 1000)
        })
        self.redis.expire(session_key, self.viewer_ttl)
        
        # Publish update
        self.publish_count_update(page_id)
    
    def heartbeat(self, page_id: str, session_id: str):
        # Refresh TTL
        viewer_key = f"viewers:{page_id}"
        if self.redis.sismember(viewer_key, session_id):
            self.redis.expire(viewer_key, self.viewer_ttl)
            
            session_key = f"viewer:{session_id}"
            self.redis.hset(session_key, 'last_seen', int(time.time() * 1000))
            self.redis.expire(session_key, self.viewer_ttl)
    
    def untrack_viewer(self, page_id: str, session_id: str):
        # Remove from page viewers
        viewer_key = f"viewers:{page_id}"
        self.redis.srem(viewer_key, session_id)
        
        # Delete session metadata
        session_key = f"viewer:{session_id}"
        self.redis.delete(session_key)
        
        # Publish update
        self.publish_count_update(page_id)
    
    def get_count(self, page_id: str) -> int:
        viewer_key = f"viewers:{page_id}"
        return self.redis.scard(viewer_key)
```

---

## Real-time Updates

### Count Update Distribution

```python
class CountUpdateService:
    def __init__(self):
        self.redis = Redis()
        self.websocket_connections = {}  # page_id -> set of connections
    
    def subscribe(self, connection, page_id: str):
        if page_id not in self.websocket_connections:
            self.websocket_connections[page_id] = set()
        self.websocket_connections[page_id].add(connection)
    
    def publish_count_update(self, page_id: str):
        # Get current count
        count = self.get_count(page_id)
        
        # Update cache
        count_key = f"count:{page_id}"
        self.redis.setex(count_key, 10, count)
        
        # Push to WebSocket connections
        if page_id in self.websocket_connections:
            message = json.dumps({
                'type': 'count_update',
                'page_id': page_id,
                'count': count,
                'formatted': self.format_count(count)
            })
            
            for connection in list(self.websocket_connections[page_id]):
                try:
                    connection.send(message)
                except:
                    self.websocket_connections[page_id].remove(connection)
    
    def format_count(self, count: int) -> str:
        if count == 0:
            return "No one viewing"
        elif count == 1:
            return "1 person viewing"
        else:
            return f"{count:,} people viewing"
```

---

## High-Level Design (HLD)

### System Overview

The Users Viewing Page Feature is a real-time system that tracks and displays the number of users currently viewing a page. It uses WebSocket connections for real-time updates, Redis for fast counting, and message queues for event processing.

### HLD Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Client Applications                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                     │
│  │   Web    │  │   iOS    │  │ Android  │                     │
│  │ Browser  │  │   App    │  │   App    │                     │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘                     │
└───────┼─────────────┼───────────────┼──────────────────────────┘
        │             │               │
        └─────────────┴───────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│              API Gateway / Load Balancer                        │
│  - Request routing                                             │
│  - Rate limiting                                               │
│  - WebSocket support                                           │
└───────────────────────────┬─────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│   Region 1    │  │   Region 2    │  │   Region N    │
└───────┬───────┘  └───────┬───────┘  └───────┬───────┘
        │                   │                   │
        ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────────────────┐
│              Application Services Layer                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ Viewer   │  │  Count   │  │ Cleanup  │  │  WebSocket│      │
│  │ Tracking │  │ Service  │  │ Service  │  │  Service │       │
│  │ Service  │  │          │  │          │  │          │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
└───────┼─────────────┼──────────────┼──────────────┼────────┘
        │             │               │              │
        ▼             ▼               ▼              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Real-Time Layer                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │WebSocket │  │WebSocket │  │  Redis   │  │  Redis   │       │
│  │  Server  │  │  Server  │  │ Pub/Sub  │  │  Streams │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
└───────┼─────────────┼──────────────┼──────────────┼────────┘
        │             │               │              │
        ▼             ▼               ▼              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Caching Layer                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │  Redis   │  │  Redis   │  │  Redis   │  │  Redis   │       │
│  │ Cluster  │  │ Cluster  │  │ Cluster  │  │ Cluster  │       │
│  │(Viewers) │ │(Counts)  │ │(Sessions)│ │(Metadata)│       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
└───────┼─────────────┼──────────────┼──────────────┼────────┘
        │             │               │              │
        ▼             ▼               ▼              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Database Layer                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │PostgreSQL│  │PostgreSQL│  │Cassandra │  │PostgreSQL│      │
│  │(Metadata)│ │(Sessions)│ │(History) │ │(Analytics)│      │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘      │
└───────┼─────────────┼──────────────┼──────────────┼────────┘
        │             │               │              │
        ▼             ▼               ▼              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Message Queue                                 │
│              (Kafka / RabbitMQ)                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Design Principles

- **Real-Time Updates**: Sub-second count updates
- **High Accuracy**: Within 1-2% tolerance
- **Scalability**: Handle 10M+ concurrent viewers
- **Fault Tolerance**: Graceful degradation on failures
- **Privacy**: Anonymous tracking, no PII stored

---

## Low-Level Design (LLD)

### Viewer Tracking Service (Detailed)

```python
class ViewerTrackingService:
    def __init__(self):
        self.redis = RedisCluster()
        self.kafka = KafkaProducer()
        self.heartbeat_interval = 30  # seconds
        self.viewer_ttl = 300  # 5 minutes
    
    async def track_viewer(self, page_id: str, session_id: str):
        """Track a new viewer on a page"""
        # Add to page viewers set
        viewer_key = f"viewers:{page_id}"
        await self.redis.sadd(viewer_key, session_id)
        await self.redis.expire(viewer_key, self.viewer_ttl)
        
        # Store session metadata
        session_key = f"viewer:{session_id}"
        await self.redis.hset(session_key, mapping={
            'page_id': page_id,
            'last_seen': int(time.time() * 1000),
            'tracked_at': int(time.time() * 1000)
        })
        await self.redis.expire(session_key, self.viewer_ttl)
        
        # Publish count update event
        await self.publish_count_update(page_id)
        
        # Schedule heartbeat
        asyncio.create_task(
            self.start_heartbeat(page_id, session_id)
        )
    
    async def heartbeat(self, page_id: str, session_id: str):
        """Refresh viewer presence"""
        viewer_key = f"viewers:{page_id}"
        
        # Check if still in set
        if await self.redis.sismember(viewer_key, session_id):
            # Refresh TTL
            await self.redis.expire(viewer_key, self.viewer_ttl)
            
            # Update last seen
            session_key = f"viewer:{session_id}"
            await self.redis.hset(
                session_key, 
                'last_seen', 
                int(time.time() * 1000)
            )
            await self.redis.expire(session_key, self.viewer_ttl)
            
            return True
        return False
    
    async def untrack_viewer(self, page_id: str, session_id: str):
        """Remove viewer from page"""
        viewer_key = f"viewers:{page_id}"
        removed = await self.redis.srem(viewer_key, session_id)
        
        if removed:
            # Delete session metadata
            session_key = f"viewer:{session_id}"
            await self.redis.delete(session_key)
            
            # Publish count update
            await self.publish_count_update(page_id)
    
    async def start_heartbeat(self, page_id: str, session_id: str):
        """Periodic heartbeat to keep viewer active"""
        while True:
            await asyncio.sleep(self.heartbeat_interval)
            
            if not await self.heartbeat(page_id, session_id):
                # Viewer removed, stop heartbeat
                break
    
    async def publish_count_update(self, page_id: str):
        """Publish count update to message queue"""
        count = await self.get_count(page_id)
        
        await self.kafka.publish('viewer_count_updates', {
            'page_id': page_id,
            'count': count,
            'timestamp': int(time.time() * 1000)
        })
```

### Count Service (Detailed)

```python
class CountService:
    def __init__(self):
        self.redis = RedisCluster()
        self.cache_ttl = 10  # seconds
    
    async def get_count(self, page_id: str) -> int:
        """Get current viewer count for a page"""
        # Check cache first
        cache_key = f"count:{page_id}"
        cached_count = await self.redis.get(cache_key)
        
        if cached_count:
            return int(cached_count)
        
        # Calculate count from viewer set
        viewer_key = f"viewers:{page_id}"
        count = await self.redis.scard(viewer_key)
        
        # Cache count
        await self.redis.setex(cache_key, self.cache_ttl, count)
        
        return count
    
    async def update_count(self, page_id: str, count: int):
        """Update cached count"""
        cache_key = f"count:{page_id}"
        await self.redis.setex(cache_key, self.cache_ttl, count)
```

### Cleanup Service (Detailed)

```python
class CleanupService:
    def __init__(self):
        self.redis = RedisCluster()
        self.cleanup_interval = 60  # seconds
    
    async def cleanup_stale_viewers(self):
        """Remove stale viewers that haven't sent heartbeat"""
        while True:
            await asyncio.sleep(self.cleanup_interval)
            
            # Scan all viewer sets
            cursor = 0
            while True:
                cursor, keys = await self.redis.scan(
                    cursor, 
                    match="viewers:*",
                    count=100
                )
                
                for viewer_key in keys:
                    await self.cleanup_page_viewers(viewer_key)
                
                if cursor == 0:
                    break
    
    async def cleanup_page_viewers(self, viewer_key: str):
        """Clean up stale viewers for a specific page"""
        page_id = viewer_key.split(':')[1]
        
        # Get all viewers
        session_ids = await self.redis.smembers(viewer_key)
        
        current_time = int(time.time() * 1000)
        stale_threshold = 300000  # 5 minutes in milliseconds
        
        for session_id in session_ids:
            session_key = f"viewer:{session_id}"
            session_data = await self.redis.hgetall(session_key)
            
            if session_data:
                last_seen = int(session_data.get('last_seen', 0))
                
                # Remove if stale
                if current_time - last_seen > stale_threshold:
                    await self.redis.srem(viewer_key, session_id)
                    await self.redis.delete(session_key)
        
        # Update count if viewers were removed
        if session_ids:
            await self.publish_count_update(page_id)
```

---

## Fault Tolerance

### Fault Tolerance Strategy

The system is designed to handle failures gracefully, ensuring viewer counts remain accurate even when components fail.

### Component-Level Fault Tolerance

#### 1. Redis Failure Tolerance

**Redis Cluster with Replication:**
```python
class FaultTolerantRedis:
    def __init__(self):
        self.primary_cluster = RedisCluster()
        self.fallback_cluster = RedisCluster(fallback_config)
        self.local_cache = LRUCache(max_size=1000, ttl=5)
        self.circuit_breaker = CircuitBreaker()
    
    async def get_count(self, page_id: str) -> int:
        # Try primary cluster
        if not self.circuit_breaker.is_open():
            try:
                count = await self.primary_cluster.scard(
                    f"viewers:{page_id}"
                )
                return count
            except RedisError:
                self.circuit_breaker.record_failure()
        
        # Try fallback cluster
        try:
            return await self.fallback_cluster.scard(
                f"viewers:{page_id}"
            )
        except RedisError:
            # Last resort: local cache
            cached = self.local_cache.get(f"count:{page_id}")
            if cached:
                return cached
            
            # Return 0 if all fail
            return 0
```

#### 2. WebSocket Connection Failure

**Automatic Reconnection:**
```python
class ResilientWebSocketClient:
    def __init__(self, url):
        self.url = url
        self.ws = None
        self.reconnect_delay = 1
        self.max_reconnect_delay = 60
    
    async def connect(self):
        while True:
            try:
                self.ws = await websockets.connect(self.url)
                self.reconnect_delay = 1  # Reset delay
                await self.on_connect()
                break
            except Exception as e:
                logger.error(f"Connection failed: {e}")
                await asyncio.sleep(self.reconnect_delay)
                self.reconnect_delay = min(
                    self.reconnect_delay * 2,
                    self.max_reconnect_delay
                )
    
    async def on_connect(self):
        # Resubscribe to pages
        for page_id in self.subscribed_pages:
            await self.subscribe(page_id)
```

#### 3. Message Queue Failure

**Local Buffering:**
```python
class FailureSafeEventPublisher:
    def __init__(self):
        self.kafka = KafkaProducer()
        self.local_buffer = LocalBuffer(max_size=10000)
    
    async def publish(self, topic, message):
        try:
            await self.kafka.publish(topic, message)
        except KafkaError:
            # Buffer locally
            await self.local_buffer.append(topic, message)
            
            # Retry worker will process when Kafka recovers
            asyncio.create_task(self.retry_worker())
```

---

## Failure Safety

### Failure Safety Principles

1. **No Count Loss**: Counts persisted in multiple places
2. **Graceful Degradation**: System continues with reduced accuracy
3. **Automatic Recovery**: System recovers when failures resolve
4. **Idempotency**: Operations can be safely retried

### Critical Failure Scenarios

#### 1. Redis Complete Failure

**Problem:** Redis cluster completely unavailable.

**Solution:** Multi-layer fallback.

```python
class FailureSafeCountService:
    async def get_count(self, page_id: str) -> int:
        # Level 1: Try Redis
        try:
            return await self.redis.scard(f"viewers:{page_id}")
        except RedisError:
            pass
        
        # Level 2: Try database
        try:
            return await self.db.get_viewer_count(page_id)
        except DatabaseError:
            pass
        
        # Level 3: Return cached value
        cached = self.local_cache.get(f"count:{page_id}")
        if cached:
            return cached
        
        # Level 4: Return 0 (graceful degradation)
        return 0
```

#### 2. WebSocket Server Failure

**Problem:** WebSocket server crashes, connections lost.

**Solution:** Automatic reconnection with state recovery.

```python
class FailureSafeWebSocketManager:
    async def handle_reconnection(self, session_id: str):
        # Recover session state
        session_data = await self.redis.hgetall(
            f"session:{session_id}"
        )
        
        if session_data:
            page_id = session_data['page_id']
            
            # Re-track viewer
            await self.tracking_service.track_viewer(
                page_id, 
                session_id
            )
            
            # Resubscribe to updates
            await self.subscribe_to_updates(page_id)
```

#### 3. Count Inconsistency

**Problem:** Counts become inconsistent across regions.

**Solution:** Periodic reconciliation.

```python
class CountReconciliationService:
    async def reconcile_counts(self):
        """Periodically reconcile counts across regions"""
        while True:
            await asyncio.sleep(300)  # Every 5 minutes
            
            # Get all pages
            pages = await self.get_all_pages()
            
            for page_id in pages:
                # Calculate actual count from all regions
                actual_count = await self.calculate_actual_count(
                    page_id
                )
                
                # Update cached count
                await self.count_service.update_count(
                    page_id, 
                    actual_count
                )
```

---

## Optimizations

### Performance Optimizations

#### 1. Count Caching Optimization

**Aggressive Caching:**
```python
class OptimizedCountService:
    def __init__(self):
        self.redis = RedisCluster()
        self.local_cache = LRUCache(max_size=10000, ttl=5)
        self.cache_ttl = 10
    
    async def get_count(self, page_id: str) -> int:
        # L1: Local cache
        cached = self.local_cache.get(page_id)
        if cached:
            return cached
        
        # L2: Redis cache
        cache_key = f"count:{page_id}"
        cached = await self.redis.get(cache_key)
        if cached:
            self.local_cache.set(page_id, int(cached))
            return int(cached)
        
        # L3: Calculate from set
        count = await self.redis.scard(f"viewers:{page_id}")
        
        # Update caches
        await self.redis.setex(cache_key, self.cache_ttl, count)
        self.local_cache.set(page_id, count)
        
        return count
```

#### 2. Batch Operations

**Batch Heartbeat Processing:**
```python
class BatchedHeartbeatProcessor:
    def __init__(self, batch_size=100, flush_interval=5.0):
        self.batch = []
        self.batch_size = batch_size
        self.flush_interval = flush_interval
    
    async def add_heartbeat(self, page_id: str, session_id: str):
        self.batch.append((page_id, session_id))
        
        if len(self.batch) >= self.batch_size:
            await self.flush()
    
    async def flush(self):
        if not self.batch:
            return
        
        # Batch update Redis
        pipe = self.redis.pipeline()
        for page_id, session_id in self.batch:
            pipe.expire(f"viewers:{page_id}", 300)
            pipe.hset(
                f"viewer:{session_id}",
                'last_seen',
                int(time.time() * 1000)
            )
        await pipe.execute()
        
        self.batch.clear()
```

#### 3. WebSocket Optimization

**Connection Pooling:**
```python
class OptimizedWebSocketManager:
    def __init__(self, max_connections_per_server=10000):
        self.connection_pool = {}
        self.max_connections = max_connections_per_server
    
    async def get_or_create_connection(self, user_id: str):
        if user_id in self.connection_pool:
            return self.connection_pool[user_id]
        
        # Create new connection
        ws = await self.create_websocket_connection(user_id)
        self.connection_pool[user_id] = ws
        
        return ws
```

#### 4. Database Query Optimization

**Read Replicas:**
```python
class OptimizedDatabase:
    async def get_viewer_count(self, page_id: str):
        # Use read replica for read operations
        async with self.read_replica_pool.acquire() as conn:
            return await conn.fetchval(
                "SELECT COUNT(*) FROM active_viewers WHERE page_id = $1",
                page_id
            )
```

---

## Scalability Considerations

### Horizontal Scaling Strategy

#### 1. Service Scaling

**Stateless Services:**
- All state in Redis/Database
- Multiple instances behind load balancer
- Auto-scaling based on load

#### 2. Redis Scaling

**Redis Cluster:**
- Shard by page_id
- Consistent hashing
- Replication for high availability

#### 3. WebSocket Scaling

**Connection Distribution:**
- Multiple WebSocket servers
- Sticky sessions
- Redis Pub/Sub for cross-server communication

#### 4. Database Scaling

**Sharding:**
- Shard by page_id
- Read replicas for reads
- Partition by date for historical data

### Capacity Planning

**Traffic Estimates:**
- 10M concurrent viewers
- 1M unique pages
- 100K events/second
- 1M WebSocket connections

**Storage Estimates:**
- Viewer sets: 1M pages × 100 viewers × 50 bytes = 5GB
- Session metadata: 10M sessions × 200 bytes = 2GB
- Historical data: 100K events/sec × 500 bytes = 50MB/sec

**Compute Estimates:**
- WebSocket servers: 1M connections / 10K per server = 100 servers
- Processing: 100K events/sec × 1ms = 100 concurrent operations

---

## Caching Strategy

### Cache Layers

1. **L1: Local Cache (In-Memory)**
   - TTL: 5 seconds
   - Size: 10K entries
   - Fastest access

2. **L2: Redis Cache**
   - TTL: 10 seconds
   - Distributed cache
   - Fast access

3. **L3: Database**
   - Persistent storage
   - Slower but reliable

### Cache Invalidation

- Time-based expiration (TTL)
- Event-based invalidation (viewer join/leave)
- Manual invalidation (admin actions)

---

## Capacity Planning

- **Concurrent Viewers**: 10M viewers
- **Unique Pages**: 1M pages
- **Events per Second**: 100K events/second
- **Redis Memory**: 10M viewers × 100 bytes = 1GB
- **WebSocket Connections**: 1M connections
- **Database Storage**: 50GB/day for historical data

---

## Technology Stack

- **Backend**: Go, Node.js
- **WebSocket**: Socket.io, ws
- **Storage**: Redis Cluster
- **Message Queue**: Kafka
- **Database**: PostgreSQL, Cassandra

---

## Interview Discussion Points

1. **Accuracy**: How do you ensure accurate counts?
   - Heartbeat mechanism
   - Stale viewer cleanup
   - Count reconciliation

2. **Scalability**: How do you handle 10M+ concurrent viewers?
   - Horizontal scaling
   - Redis clustering
   - WebSocket distribution

3. **Real-time**: How do you push updates in real-time?
   - WebSocket connections
   - Redis Pub/Sub
   - Event-driven architecture

4. **Cleanup**: How do you handle stale viewers?
   - TTL-based expiration
   - Periodic cleanup jobs
   - Heartbeat timeout

---

**Document Version**: 2.0  
**Last Updated**: January 2024

