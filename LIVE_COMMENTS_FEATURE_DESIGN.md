# Design a Live Comments Feature for Facebook

## Table of Contents
1. [Overview](#overview)
2. [Requirements](#requirements)
3. [System Architecture](#system-architecture)
4. [Database Design](#database-design)
5. [API Design](#api-design)
6. [Real-time Distribution](#real-time-distribution)
7. [Scalability Considerations](#scalability-considerations)
8. [Caching Strategy](#caching-strategy)
9. [Load Balancing](#load-balancing)
10. [Capacity Planning](#capacity-planning)
11. [Technology Stack](#technology-stack)
12. [Interview Discussion Points](#interview-discussion-points)

---

## Overview

A live comments system that allows users to post comments and see new comments in real-time as they appear. The system must handle millions of concurrent users, deliver comments with low latency, support pagination, and scale horizontally.

**Key Features:**
- Post comments
- Real-time comment updates
- Comment threading/replies
- Comment reactions (likes)
- Comment pagination
- Comment moderation
- Real-time user presence

---

## Requirements

### Functional Requirements

1. **Comment Management**
   - Create comments
   - Edit/delete comments
   - Reply to comments
   - Like comments

2. **Real-time Updates**
   - Push new comments to viewers
   - Show comment count updates
   - Display typing indicators

3. **Pagination**
   - Load comments in pages
   - Infinite scroll support
   - Cursor-based pagination

### Non-Functional Requirements

1. **Scalability**
   - Handle 1M+ concurrent viewers per post
   - Support 100K+ comments per post
   - Process 10K+ comments per second globally

2. **Performance**
   - Comment creation: < 200ms
   - Real-time delivery: < 100ms latency
   - Comment load: < 500ms

3. **Reliability**
   - No comment loss
   - Eventual consistency acceptable
   - 99.9% uptime

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
│                    API Gateway / Load Balancer                   │
└────────────┬────────────────────────────────────┬────────────────┘
             │                                    │
             ▼                                    ▼
┌────────────────────────────┐      ┌────────────────────────────┐
│   Comment Service           │      │   WebSocket Service        │
│   - Create Comments        │      │   - Real-time Updates      │
│   - Manage Comments        │      │   - Connection Management  │
└────────────┬───────────────┘      └────────────┬───────────────┘
             │                                    │
             ▼                                    ▼
┌────────────────────────────────────────────────────────────────┐
│                    Message Queue                                 │
│              (Kafka)                                            │
│  Topics: comments, reactions, typing                           │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Processing Layer                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Comment    │  │   Moderation │  │   Analytics  │         │
│  │   Processor  │  │   Service    │  │   Service    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Data Layer                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Comments   │  │   Reactions   │  │   Presence   │         │
│  │     DB       │  │     DB       │  │     DB       │         │
│  │ (PostgreSQL) │  │ (PostgreSQL) │  │  (Redis)     │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────────────────────────────────────────────┘
```

---

## Database Design

### Comments Table

```sql
CREATE TABLE comments (
    comment_id BIGSERIAL PRIMARY KEY,
    post_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    parent_comment_id BIGINT, -- NULL for top-level comments
    content TEXT NOT NULL,
    like_count INTEGER DEFAULT 0,
    reply_count INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active', -- active, deleted, hidden
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (post_id) REFERENCES posts(post_id),
    FOREIGN KEY (parent_comment_id) REFERENCES comments(comment_id),
    INDEX idx_post_created (post_id, created_at DESC),
    INDEX idx_parent (parent_comment_id),
    INDEX idx_user (user_id)
);
```

### Comment Reactions Table

```sql
CREATE TABLE comment_reactions (
    reaction_id BIGSERIAL PRIMARY KEY,
    comment_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    reaction_type VARCHAR(20) DEFAULT 'like', -- like, love, etc.
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (comment_id) REFERENCES comments(comment_id),
    UNIQUE KEY unique_user_comment (user_id, comment_id),
    INDEX idx_comment (comment_id)
);
```

---

## API Design

### Comment APIs

```
POST   /api/v1/posts/{post_id}/comments
GET    /api/v1/posts/{post_id}/comments?cursor={cursor}&limit=20
PUT    /api/v1/comments/{comment_id}
DELETE /api/v1/comments/{comment_id}
POST   /api/v1/comments/{comment_id}/reactions
```

### WebSocket API

```javascript
// Connect
ws = new WebSocket("wss://api.example.com/comments/stream");

// Subscribe to post
ws.send(JSON.stringify({
  "action": "subscribe",
  "post_id": 123
}));

// Receive new comments
ws.onmessage = (event) => {
  const comment = JSON.parse(event.data);
  displayComment(comment);
};
```

---

## Real-time Distribution

### Comment Distribution

```python
class CommentStreamManager:
    def __init__(self):
        self.connections = {}  # post_id -> set of connections
        self.redis = Redis()
    
    def subscribe(self, connection, post_id: int):
        if post_id not in self.connections:
            self.connections[post_id] = set()
        self.connections[post_id].add(connection)
    
    def publish_comment(self, post_id: int, comment: dict):
        # Store in database
        self.save_comment(comment)
        
        # Publish to Kafka
        self.kafka_producer.send('comments', {
            'post_id': post_id,
            'comment': comment
        })
        
        # Push to WebSocket connections
        if post_id in self.connections:
            message = json.dumps({
                'type': 'new_comment',
                'comment': comment
            })
            for connection in self.connections[post_id]:
                try:
                    connection.send(message)
                except:
                    self.connections[post_id].remove(connection)
```

---

## Scalability Considerations

- **Horizontal Scaling**: Multiple WebSocket servers
- **Kafka Partitioning**: Partition by post_id
- **Database Sharding**: Shard by post_id
- **Caching**: Cache recent comments (Redis)

---

## Caching Strategy

- **Recent Comments**: Cache last 100 comments per post (Redis)
- **Comment Counts**: Cache comment counts (Redis)
- **User Presence**: Track active viewers (Redis)

---

## Capacity Planning

- **Concurrent Viewers**: 1M per popular post
- **Comments per Post**: 100K+ comments
- **Comments per Second**: 10K globally
- **WebSocket Connections**: 10M+ connections

---

## Technology Stack

- **Backend**: Go, Node.js
- **WebSocket**: Socket.io, ws
- **Message Queue**: Kafka
- **Database**: PostgreSQL, Redis
- **Cache**: Redis Cluster

---

## High-Level Design (HLD)

### System Overview

The live comments system follows a real-time event-driven architecture:

1. **Client Layer**: Web and mobile applications
2. **API Gateway**: Routes requests, handles WebSocket connections
3. **Comment Service**: Handles comment CRUD operations
4. **WebSocket Service**: Manages real-time connections, publishes updates
5. **Message Queue**: Buffers comment events (Kafka)
6. **Processing Layer**: Moderation, analytics, notifications
7. **Data Layer**: PostgreSQL for persistence, Redis for caching

### Component Architecture

**Core Services:**
- **Comment Service**: Create, edit, delete comments
- **WebSocket Service**: Real-time comment distribution
- **Moderation Service**: Content moderation, spam detection
- **Notification Service**: Sends notifications for new comments

---

## Low-Level Design (LLD)

### Comment Stream Manager

```python
class CommentStreamManager:
    def __init__(self, redis_client, kafka_producer):
        self.connections = {}  # post_id -> set of WebSocket connections
        self.redis = redis_client
        self.kafka = kafka_producer
    
    def subscribe(self, connection, post_id: int):
        if post_id not in self.connections:
            self.connections[post_id] = set()
        self.connections[post_id].add(connection)
    
    def publish_comment(self, post_id: int, comment: dict):
        # Store in database (async)
        self.save_comment_async(comment)
        
        # Publish to Kafka
        self.kafka.send('comments', {
            'post_id': post_id,
            'comment': comment
        }, key=str(post_id))
        
        # Push to WebSocket connections
        if post_id in self.connections:
            message = json.dumps({
                'type': 'new_comment',
                'comment': comment
            })
            
            dead_connections = []
            for connection in self.connections[post_id]:
                try:
                    connection.send(message)
                except Exception:
                    dead_connections.append(connection)
            
            # Remove dead connections
            for conn in dead_connections:
                self.connections[post_id].remove(conn)
```

### Comment Service Implementation

```python
class CommentService:
    def __init__(self, db_client, redis_client, kafka_producer):
        self.db = db_client
        self.redis = redis_client
        self.kafka = kafka_producer
    
    def create_comment(self, post_id: int, user_id: int, content: str, parent_id: int = None):
        # Validate content
        if not self.validate_content(content):
            raise ValueError("Invalid content")
        
        # Create comment
        comment = {
            'post_id': post_id,
            'user_id': user_id,
            'content': content,
            'parent_comment_id': parent_id,
            'like_count': 0,
            'reply_count': 0,
            'created_at': datetime.utcnow()
        }
        
        # Save to database
        comment_id = self.db.execute(
            """
            INSERT INTO comments (post_id, user_id, content, parent_comment_id, created_at)
            VALUES (?, ?, ?, ?, ?)
            RETURNING comment_id
            """,
            [post_id, user_id, content, parent_id, comment['created_at']]
        )
        comment['comment_id'] = comment_id
        
        # Update reply count if parent exists
        if parent_id:
            self.db.execute(
                "UPDATE comments SET reply_count = reply_count + 1 WHERE comment_id = ?",
                [parent_id]
            )
        
        # Update post comment count
        self.db.execute(
            "UPDATE posts SET comment_count = comment_count + 1 WHERE post_id = ?",
            [post_id]
        )
        
        # Publish to Kafka for real-time distribution
        self.kafka.send('comments', {
            'post_id': post_id,
            'comment': comment
        })
        
        # Cache recent comments
        self.cache_recent_comment(post_id, comment)
        
        return comment
```

---

## Fault Tolerance

### WebSocket Resilience

**Connection Management:**
- Heartbeat mechanism (ping/pong)
- Automatic reconnection on disconnect
- Connection pooling

**Failure Handling:**
- Remove dead connections
- Retry message delivery
- Fallback to polling if WebSocket fails

### Database Resilience

**Replication:**
- PostgreSQL primary-replica setup
- Read from replicas
- Automatic failover

**Transaction Safety:**
- Use transactions for comment creation
- Rollback on failure
- Idempotent operations

---

## Optimizations

### Caching Strategy

**Recent Comments Cache:**
- Cache last 100 comments per post (Redis)
- TTL: 1 hour
- Invalidate on new comment

**Comment Count Cache:**
- Cache comment counts per post
- Update on comment create/delete
- TTL: 30 minutes

### Database Optimization

**Indexing:**
- Index on `post_id, created_at` for efficient queries
- Index on `parent_comment_id` for replies
- Index on `user_id` for user queries

**Pagination:**
- Cursor-based pagination
- Use `created_at` as cursor
- Efficient for large datasets

---

## Failure Safety

### WebSocket Failure

**Scenario: WebSocket Service Down**
- **Impact**: Real-time updates unavailable
- **Mitigation**:
  - Multiple WebSocket servers
  - Load balancer distributes connections
  - Fallback to polling
- **Recovery**:
  - Service recovers
  - Clients reconnect
  - Resume real-time updates

### Database Failure

**Scenario: Database Unavailable**
- **Impact**: Cannot create/read comments
- **Mitigation**:
  - Database replication
  - Read from replicas
  - Queue writes for later
- **Recovery**:
  - Database recovers
  - Process queued writes
  - Verify data consistency

### Message Queue Failure

**Scenario: Kafka Unavailable**
- **Impact**: Comments not distributed in real-time
- **Mitigation**:
  - Kafka cluster with replication
  - Local buffering
  - Fallback to direct WebSocket push
- **Recovery**:
  - Kafka recovers
  - Process buffered messages
  - Resume normal operation

---

## Scalability

### Horizontal Scaling

**WebSocket Scaling:**
- Multiple WebSocket servers
- Load balancer distributes connections
- Sticky sessions for connection affinity

**Comment Service Scaling:**
- Stateless service instances
- Load balancer distributes requests
- Scale independently

### Performance Scaling

**Throughput Scaling:**
- Increase Kafka partitions
- Add more processing instances
- Optimize database queries

**Connection Scaling:**
- Use WebSocket connection pooling
- Optimize connection handling
- Scale WebSocket servers horizontally

---

## Interview Discussion Points

1. **Real-time Updates**: How do you push to millions of viewers?
2. **Scalability**: How do you handle 1M+ concurrent viewers?
3. **Ordering**: How do you maintain comment order?
4. **Pagination**: How do you implement efficient pagination?

---

**Document Version**: 1.0  
**Last Updated**: January 2024

