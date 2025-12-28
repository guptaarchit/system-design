# WhatsApp System Design Document

## Table of Contents
1. [Overview](#overview)
2. [Requirements](#requirements)
3. [System Architecture](#system-architecture)
4. [Database Design](#database-design)
5. [API Design](#api-design)
6. [Real-Time Messaging](#real-time-messaging)
7. [Message Delivery & Read Receipts](#message-delivery--read-receipts)
8. [Media Handling](#media-handling)
9. [Group Chat Management](#group-chat-management)
10. [End-to-End Encryption](#end-to-end-encryption)
11. [Scalability Considerations](#scalability-considerations)
12. [Caching Strategy](#caching-strategy)
13. [Load Balancing](#load-balancing)
14. [Security](#security)
15. [Monitoring & Analytics](#monitoring--analytics)
16. [Deployment Strategy](#deployment-strategy)
17. [Capacity Planning](#capacity-planning)
18. [Technology Stack](#technology-stack)
19. [Failure Scenarios & Handling](#failure-scenarios--handling)
20. [Trade-offs & Design Decisions](#trade-offs--design-decisions)
21. [Interview Discussion Points](#interview-discussion-points)

---

## Overview

WhatsApp is a real-time messaging platform that enables users to send text messages, media files, and make voice/video calls. The system must handle billions of messages daily, ensure message delivery, support end-to-end encryption, and provide real-time communication with low latency.

**Key Features:**
- One-on-one messaging
- Group chats (up to 256 members)
- Media sharing (images, videos, documents, audio)
- Voice and video calls
- Status updates (stories)
- Message delivery receipts (single/double tick)
- Read receipts (blue ticks)
- End-to-end encryption
- Offline message delivery
- Last seen status
- Online/offline presence

---

## Requirements

### Functional Requirements

1. **User Management**
   - User registration (phone number based)
   - User authentication (OTP verification)
   - User profile management
   - Contact synchronization
   - Block/unblock users

2. **Messaging**
   - Send/receive text messages
   - Send/receive media messages
   - Message delivery confirmation
   - Read receipts
   - Message status (sent, delivered, read)
   - Message forwarding
   - Message deletion (for everyone)
   - Message search
   - Message archiving

3. **Group Chats**
   - Create groups (up to 256 members)
   - Add/remove members
   - Group admin management
   - Group settings (description, photo)
   - Group message delivery

4. **Media Handling**
   - Image sharing
   - Video sharing
   - Document sharing
   - Audio messages
   - Media compression and optimization
   - Media storage and retrieval

5. **Voice & Video Calls**
   - One-on-one voice calls
   - One-on-one video calls
   - Group voice calls
   - Group video calls
   - Call quality management
   - Call history

6. **Status Updates**
   - Post status (text, image, video)
   - View status of contacts
   - Status expiration (24 hours)
   - Status privacy settings

7. **Presence**
   - Online/offline status
   - Last seen timestamp
   - Typing indicators
   - Privacy controls for presence

### Non-Functional Requirements

1. **Scalability**
   - Support 2B+ active users globally
   - Handle 100B+ messages per day
   - Support 1B+ concurrent connections
   - 99.99% uptime
   - Multi-region deployment

2. **Performance**
   - Message delivery latency: < 100ms (same region)
   - Message delivery latency: < 500ms (cross-region)
   - Media upload/download: Support up to 100MB files
   - Real-time presence updates: < 200ms
   - Typing indicators: < 100ms

3. **Reliability**
   - Message delivery guarantee (at-least-once)
   - Offline message delivery
   - Message persistence
   - No message loss

4. **Security**
   - End-to-end encryption
   - Secure authentication
   - Data privacy
   - Protection against spam/abuse

5. **Availability**
   - 99.99% uptime SLA
   - Graceful degradation
   - Disaster recovery

---

## System Architecture

### High-Level Architecture

```
┌─────────────┐
│   Mobile    │
│   Clients   │
└──────┬──────┘
       │
       │ HTTPS/WSS
       │
┌──────▼─────────────────────────────────────────┐
│           Load Balancer                        │
│         (SSL Termination)                      │
└──────┬─────────────────────────────────────────┘
       │
       ├─────────────────┬─────────────────┐
       │                 │                 │
┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐
│   WebSocket │  │   REST API  │  │   Media     │
│   Servers   │  │   Servers   │  │   Servers   │
│             │  │             │  │             │
│ (Real-time  │  │ (HTTP       │  │ (File       │
│  messaging) │  │  requests)  │  │  upload/    │
│             │  │             │  │  download)  │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                 │                 │
       └─────────────────┼─────────────────┘
                         │
              ┌──────────▼──────────┐
              │   Message Queue     │
              │   (Kafka/RabbitMQ)  │
              └──────────┬──────────┘
                         │
       ┌─────────────────┼─────────────────┐
       │                 │                 │
┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐
│  Message    │  │  Presence   │  │  Media      │
│  Service    │  │  Service    │  │  Service    │
│             │  │             │  │             │
│ - Routing   │  │ - Online    │  │ - Storage   │
│ - Delivery  │  │   status    │  │ - CDN       │
│ - Storage   │  │ - Last seen │  │ - Thumbnail │
└──────┬──────┘  │ - Typing    │  └──────┬──────┘
       │         └──────┬──────┘         │
       │                 │                │
       └─────────────────┼────────────────┘
                         │
              ┌──────────▼──────────┐
              │   Database Layer     │
              │                      │
              │  - User DB (MySQL)   │
              │  - Message DB        │
              │    (Cassandra)       │
              │  - Media DB (S3)     │
              │  - Cache (Redis)     │
              └──────────────────────┘
```

### Component Details

1. **Client Applications**
   - Mobile apps (iOS, Android)
   - Web client
   - Desktop client
   - Uses WebSocket for real-time communication
   - Uses HTTP/REST for non-real-time operations

2. **Load Balancer**
   - Distributes incoming connections
   - SSL/TLS termination
   - Health checks
   - Session affinity for WebSocket connections

3. **WebSocket Servers**
   - Maintain persistent connections
   - Handle real-time message delivery
   - Manage presence updates
   - Handle typing indicators

4. **REST API Servers**
   - User authentication
   - Profile management
   - Contact synchronization
   - Media upload/download endpoints
   - Group management

5. **Message Queue**
   - Decouples message producers and consumers
   - Ensures message delivery
   - Handles message routing
   - Supports message persistence

6. **Message Service**
   - Message routing logic
   - Delivery confirmation
   - Read receipt handling
   - Message storage
   - Offline message queue

7. **Presence Service**
   - Online/offline status tracking
   - Last seen updates
   - Typing indicators
   - Privacy controls

8. **Media Service**
   - Media upload handling
   - Media storage (object storage)
   - Media compression
   - Thumbnail generation
   - CDN integration

---

## Database Design

### User Database (MySQL)

**users**
```sql
CREATE TABLE users (
    user_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(255),
    profile_picture_url VARCHAR(500),
    status_message VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_seen TIMESTAMP,
    is_online BOOLEAN DEFAULT FALSE,
    INDEX idx_phone (phone_number),
    INDEX idx_last_seen (last_seen)
);
```

**contacts**
```sql
CREATE TABLE contacts (
    user_id BIGINT NOT NULL,
    contact_phone_number VARCHAR(20) NOT NULL,
    contact_name VARCHAR(255),
    is_blocked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, contact_phone_number),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    INDEX idx_user (user_id)
);
```

**groups**
```sql
CREATE TABLE groups (
    group_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    group_name VARCHAR(255),
    group_description TEXT,
    group_picture_url VARCHAR(500),
    created_by BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(user_id),
    INDEX idx_created_by (created_by)
);
```

**group_members**
```sql
CREATE TABLE group_members (
    group_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    role ENUM('admin', 'member') DEFAULT 'member',
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (group_id, user_id),
    FOREIGN KEY (group_id) REFERENCES groups(group_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    INDEX idx_group (group_id),
    INDEX idx_user (user_id)
);
```

### Message Database (Cassandra)

**messages**
```sql
CREATE TABLE messages (
    chat_id TEXT,  -- user_id1_user_id2 or group_id
    message_id TIMEUUID,
    sender_id BIGINT,
    message_type TEXT,  -- text, image, video, document, audio
    content TEXT,
    media_url TEXT,
    created_at TIMESTAMP,
    delivered_at TIMESTAMP,
    read_at TIMESTAMP,
    is_deleted BOOLEAN,
    PRIMARY KEY (chat_id, created_at, message_id)
) WITH CLUSTERING ORDER BY (created_at DESC, message_id DESC);
```

**message_status**
```sql
CREATE TABLE message_status (
    message_id TIMEUUID,
    chat_id TEXT,
    user_id BIGINT,
    status TEXT,  -- sent, delivered, read
    updated_at TIMESTAMP,
    PRIMARY KEY (message_id, user_id)
);
```

### Media Storage (S3/Object Storage)

- Store media files in object storage (S3, Azure Blob, GCS)
- Use CDN for media delivery
- Organize by: `media/{user_id}/{message_id}/{filename}`
- Store thumbnails separately: `thumbnails/{user_id}/{message_id}/{filename}`

### Cache (Redis)

**User Presence**
```
Key: presence:{user_id}
Value: {status: "online|offline", last_seen: timestamp}
TTL: 5 minutes
```

**User Sessions**
```
Key: session:{user_id}
Value: {websocket_server_id: "server-123", connected_at: timestamp}
TTL: 1 hour
```

**Recent Messages**
```
Key: chat:{chat_id}:messages
Value: List of recent messages (last 50)
TTL: 1 hour
```

**Typing Indicators**
```
Key: typing:{chat_id}:{user_id}
Value: {is_typing: true, timestamp: ...}
TTL: 10 seconds
```

---

## API Design

### Authentication APIs

**POST /api/v1/auth/register**
```json
Request:
{
  "phone_number": "+1234567890"
}

Response:
{
  "success": true,
  "otp_sent": true
}
```

**POST /api/v1/auth/verify**
```json
Request:
{
  "phone_number": "+1234567890",
  "otp": "123456"
}

Response:
{
  "success": true,
  "token": "jwt_token_here",
  "user": {
    "user_id": 123,
    "phone_number": "+1234567890",
    "name": "John Doe"
  }
}
```

### Messaging APIs

**POST /api/v1/messages/send**
```json
Request:
{
  "chat_id": "123_456",
  "message_type": "text",
  "content": "Hello, how are you?",
  "media_url": null
}

Response:
{
  "success": true,
  "message_id": "uuid-here",
  "created_at": "2024-01-01T12:00:00Z"
}
```

**GET /api/v1/messages/{chat_id}**
```json
Query Parameters:
- limit: 50 (default)
- before: message_id (for pagination)

Response:
{
  "messages": [
    {
      "message_id": "uuid-1",
      "sender_id": 123,
      "message_type": "text",
      "content": "Hello",
      "created_at": "2024-01-01T12:00:00Z",
      "status": "read"
    }
  ],
  "has_more": true
}
```

### Group APIs

**POST /api/v1/groups**
```json
Request:
{
  "group_name": "Family",
  "member_ids": [123, 456, 789]
}

Response:
{
  "success": true,
  "group_id": 1001,
  "group_name": "Family"
}
```

**POST /api/v1/groups/{group_id}/members**
```json
Request:
{
  "user_ids": [999, 888]
}

Response:
{
  "success": true,
  "added_count": 2
}
```

### Media APIs

**POST /api/v1/media/upload**
```json
Request: multipart/form-data
- file: binary
- message_id: uuid

Response:
{
  "success": true,
  "media_url": "https://cdn.whatsapp.com/media/...",
  "thumbnail_url": "https://cdn.whatsapp.com/thumbnails/..."
}
```

**GET /api/v1/media/{media_id}**
```json
Response: Binary file stream
```

### Presence APIs

**PUT /api/v1/presence**
```json
Request:
{
  "status": "online"  // or "offline"
}

Response:
{
  "success": true
}
```

**GET /api/v1/presence/{user_id}**
```json
Response:
{
  "user_id": 123,
  "is_online": true,
  "last_seen": "2024-01-01T12:00:00Z"
}
```

---

## Real-Time Messaging

### WebSocket Protocol

**Connection Establishment**
1. Client connects via WebSocket: `wss://whatsapp.com/ws?token=jwt_token`
2. Server validates token and establishes connection
3. Server stores connection mapping: `user_id -> websocket_connection`
4. Client sends heartbeat every 30 seconds

**Message Flow**
```
Sender Client          WebSocket Server        Message Queue        Receiver WebSocket Server    Receiver Client
     │                        │                        │                        │                        │
     │─── Send Message ──────>│                        │                        │                        │
     │                        │─── Publish ───────────>│                        │                        │
     │                        │                        │─── Route ───────────────>│                        │
     │                        │                        │                        │─── Deliver ────────────>│
     │                        │                        │                        │                        │
     │<─── ACK ───────────────│                        │                        │                        │
     │                        │                        │                        │<─── Delivery Receipt ───│
     │                        │                        │                        │                        │
     │                        │<─── Delivery Status ───│<─── Delivery Receipt ──│                        │
     │<─── Delivery Status ───│                        │                        │                        │
```

### Message Routing

**Routing Logic**
1. Determine if chat is one-on-one or group
2. For one-on-one: Route to recipient's connected server
3. For group: Route to all group members' connected servers
4. If user offline: Store in offline queue

**Server Selection**
- Use consistent hashing to map users to WebSocket servers
- Store mapping in Redis: `user:{user_id} -> server_id`
- When user connects, update mapping
- When routing message, lookup server from Redis

---

## Message Delivery & Read Receipts

### Delivery Status Flow

1. **Sent** (Single Tick)
   - Message successfully sent to server
   - Acknowledged by WebSocket server

2. **Delivered** (Double Tick)
   - Message delivered to recipient's device
   - Recipient's device sends delivery receipt
   - Update message status in database

3. **Read** (Blue Double Tick)
   - Recipient opens chat and views message
   - Client sends read receipt
   - Update message status and notify sender

### Implementation

**Delivery Receipt**
```python
def handle_delivery_receipt(message_id, recipient_id):
    # Update message status
    update_message_status(message_id, recipient_id, "delivered")
    
    # Notify sender
    sender_id = get_message_sender(message_id)
    notify_user(sender_id, {
        "type": "delivery_receipt",
        "message_id": message_id,
        "status": "delivered"
    })
```

**Read Receipt**
```python
def handle_read_receipt(chat_id, recipient_id, last_read_message_id):
    # Update all messages up to last_read_message_id
    mark_messages_as_read(chat_id, recipient_id, last_read_message_id)
    
    # Notify sender
    sender_id = get_chat_other_user(chat_id, recipient_id)
    notify_user(sender_id, {
        "type": "read_receipt",
        "chat_id": chat_id,
        "last_read_message_id": last_read_message_id
    })
```

### Offline Message Delivery

**Offline Queue**
- When user is offline, messages are stored in offline queue
- Queue per user: `offline_queue:{user_id}`
- When user comes online:
  1. Check offline queue
  2. Deliver all pending messages
  3. Clear queue after successful delivery

---

## Media Handling

### Media Upload Flow

1. **Client Upload**
   - Client uploads media to media service
   - Media service generates unique ID
   - Store in object storage (S3)
   - Generate thumbnail (for images/videos)
   - Store thumbnail in object storage

2. **Message Creation**
   - Create message with media_url
   - Send message through normal flow
   - Media is referenced, not embedded

3. **Media Download**
   - Client requests media via CDN
   - CDN serves media with caching
   - For large files, support resumable downloads

### Media Optimization

**Image Processing**
- Compress images (JPEG quality: 85%)
- Generate multiple sizes (thumbnail, medium, full)
- Support WebP format for better compression

**Video Processing**
- Transcode to multiple qualities (240p, 480p, 720p)
- Generate video thumbnails
- Extract metadata (duration, resolution)

**Storage Strategy**
- Hot storage: Recent media (last 30 days) in fast storage
- Cold storage: Older media in cheaper storage
- CDN caching for frequently accessed media

---

## Group Chat Management

### Group Operations

**Create Group**
1. Validate member count (max 256)
2. Create group record in database
3. Add creator as admin
4. Add all members to group_members table
5. Send notification to all members

**Add Members**
1. Validate group exists and user has permission
2. Check member limit
3. Add members to group_members table
4. Send notification to new members
5. Notify existing members about new additions

**Remove Members**
1. Validate permissions
2. Remove from group_members table
3. Send notification to removed member
4. Notify remaining members

**Group Message Routing**
- When message sent to group:
  1. Get all group members from database
  2. Filter out sender
  3. Route message to each member's WebSocket server
  4. Handle offline members via offline queue

### Group Admin Management

- Admins can add/remove members
- Admins can change group settings
- Admins can remove other admins (except creator)
- Store admin list in group_members table with role

---

## End-to-End Encryption

### Encryption Flow

1. **Key Exchange**
   - Each user has a public/private key pair
   - Public keys stored on server
   - Private keys stored only on client

2. **Message Encryption**
   - Sender encrypts message with recipient's public key
   - Encrypted message sent to server
   - Server cannot decrypt message

3. **Message Decryption**
   - Recipient receives encrypted message
   - Decrypts using their private key
   - Displays decrypted message

### Implementation Considerations

- Use Signal Protocol or similar
- Key rotation for security
- Forward secrecy
- Group chat encryption (more complex)

**Note**: Full E2E encryption implementation is complex and requires:
- Key management service
- Key exchange protocol
- Message encryption/decryption on client
- Server acts as message router only

---

## Scalability Considerations

### Horizontal Scaling

1. **WebSocket Servers**
   - Stateless design (connection info in Redis)
   - Add servers as needed
   - Load balancer distributes connections

2. **Message Service**
   - Stateless workers
   - Scale based on message volume
   - Use message queue for load distribution

3. **Database Sharding**
   - Shard by user_id or chat_id
   - Use consistent hashing
   - Cross-shard queries minimized

### Vertical Scaling

- Use high-performance databases
- Optimize database queries
- Use read replicas for read-heavy operations

### Caching Strategy

- Cache user presence (Redis)
- Cache recent messages (Redis)
- Cache user sessions (Redis)
- Cache group member lists (Redis)

---

## Caching Strategy

### Cache Layers

1. **Application Cache (Redis)**
   - User presence: 5 min TTL
   - Recent messages: 1 hour TTL
   - User sessions: 1 hour TTL
   - Typing indicators: 10 sec TTL

2. **CDN Cache**
   - Media files: Long TTL
   - Profile pictures: 1 day TTL
   - Static assets: 1 week TTL

3. **Database Query Cache**
   - Frequently accessed user data
   - Group member lists
   - Contact lists

### Cache Invalidation

- Presence: TTL-based expiration
- Messages: Invalidate on new message
- User data: Invalidate on update
- Group data: Invalidate on member changes

---

## Load Balancing

### Load Balancing Strategy

1. **WebSocket Connections**
   - Use sticky sessions (session affinity)
   - Map user to server consistently
   - Store mapping in Redis

2. **REST API**
   - Round-robin or least connections
   - Health checks
   - Auto-scaling based on load

3. **Message Queue**
   - Partition by chat_id or user_id
   - Distribute load across partitions
   - Consumer groups for parallel processing

---

## Security

### Authentication & Authorization

1. **Phone Number Verification**
   - OTP via SMS
   - Rate limiting on OTP requests
   - OTP expiration (5 minutes)

2. **JWT Tokens**
   - Short-lived access tokens (1 hour)
   - Refresh tokens (30 days)
   - Token rotation

3. **API Security**
   - Rate limiting per user
   - Input validation
   - SQL injection prevention
   - XSS prevention

### Data Security

1. **Encryption at Rest**
   - Encrypt database
   - Encrypt media files
   - Encrypt backups

2. **Encryption in Transit**
   - TLS/SSL for all connections
   - WebSocket over WSS

3. **End-to-End Encryption**
   - Client-side encryption
   - Server cannot read messages
   - Key management

### Abuse Prevention

- Rate limiting on message sending
- Spam detection
- Account blocking
- Report and moderation system

---

## Monitoring & Analytics

### Key Metrics

1. **Performance Metrics**
   - Message delivery latency (p50, p95, p99)
   - API response time
   - WebSocket connection count
   - Active users

2. **System Metrics**
   - CPU, memory, disk usage
   - Database query performance
   - Cache hit rate
   - Queue depth

3. **Business Metrics**
   - Daily active users (DAU)
   - Messages per day
   - Media uploads per day
   - Group chats created

### Monitoring Tools

- Application monitoring: Prometheus, Grafana
- Log aggregation: ELK Stack, Splunk
- Distributed tracing: Jaeger, Zipkin
- Error tracking: Sentry

### Alerts

- High latency alerts
- High error rate alerts
- Database connection pool exhaustion
- Queue backup alerts
- Service downtime alerts

---

## Deployment Strategy

### Deployment Architecture

1. **Multi-Region Deployment**
   - Deploy in multiple regions
   - Route users to nearest region
   - Cross-region message routing

2. **Blue-Green Deployment**
   - Zero-downtime deployments
   - Rollback capability
   - Gradual traffic migration

3. **Containerization**
   - Docker containers
   - Kubernetes orchestration
   - Auto-scaling

### CI/CD Pipeline

1. Code commit triggers build
2. Run tests
3. Build Docker images
4. Deploy to staging
5. Run integration tests
6. Deploy to production (canary → full)

---

## Capacity Planning

### Storage Estimates

**Messages**
- Average message size: 100 bytes (text)
- 100B messages/day = 10GB/day = 3.65TB/year
- With replication (3x): ~11TB/year
- Per user: ~5.5GB/year

**Media**
- Average media size: 2MB
- 10% messages are media = 10B media/day
- 20TB/day = 7.3PB/year
- With compression: ~3.6PB/year

**Database**
- User data: ~1KB/user = 2GB for 2B users
- Messages: 3.65TB/year (growing)
- Need sharding and archiving strategy

### Compute Estimates

**WebSocket Servers**
- Each server handles ~100K connections
- 1B concurrent users = 10K servers
- With redundancy: ~15K servers

**Message Processing**
- Average: 1M messages/second
- Each message: ~1ms processing
- Need ~1000 workers (with overhead)

---

## Technology Stack

### Backend
- **Language**: Go, Java, or Erlang (for concurrency)
- **WebSocket**: Custom or library (gorilla/websocket)
- **Message Queue**: Kafka or RabbitMQ
- **Database**: 
  - MySQL (user data, groups)
  - Cassandra (messages)
  - Redis (cache, presence)
- **Object Storage**: S3, Azure Blob, or GCS
- **CDN**: CloudFront, Cloudflare

### Frontend
- **Mobile**: Native (Swift, Kotlin) or React Native
- **Web**: React or Vue.js
- **WebSocket Client**: Native WebSocket API

### Infrastructure
- **Container Orchestration**: Kubernetes
- **Service Mesh**: Istio (optional)
- **Monitoring**: Prometheus, Grafana
- **Logging**: ELK Stack
- **CI/CD**: Jenkins, GitLab CI, or GitHub Actions

---

## Failure Scenarios & Handling

### Single Server Failure

**WebSocket Server Down**
- Users reconnect to different server
- Connection mapping updated in Redis
- Pending messages delivered from queue

**Database Failure**
- Use database replicas
- Failover to replica
- Read from replica, write to primary

**Message Queue Failure**
- Use queue replication
- Messages persisted to disk
- Replay from disk on recovery

### Region Failure

- Route traffic to other regions
- Cross-region message routing
- Data replication across regions

### Network Partition

- Continue serving local users
- Queue cross-region messages
- Deliver when partition resolves

---

## Trade-offs & Design Decisions

### 1. WebSocket vs HTTP Polling

**Chosen: WebSocket**
- Lower latency for real-time messaging
- More efficient (no polling overhead)
- Better for presence updates

**Trade-off**: More complex connection management

### 2. Database Choice

**Messages: Cassandra**
- High write throughput
- Horizontal scalability
- Time-series data pattern

**User Data: MySQL**
- ACID transactions needed
- Relational data (groups, contacts)
- Better for complex queries

### 3. Message Delivery: At-Least-Once vs Exactly-Once

**Chosen: At-Least-Once**
- Simpler implementation
- Idempotent message handling on client
- Acceptable for messaging (duplicates rare)

**Trade-off**: Need duplicate detection on client

### 4. Media Storage: Database vs Object Storage

**Chosen: Object Storage**
- Cost-effective for large files
- Better scalability
- CDN integration

**Trade-off**: Additional service to manage

### 5. Presence: Push vs Pull

**Chosen: Push (WebSocket)**
- Real-time updates
- Lower server load
- Better user experience

**Trade-off**: More connections to manage

---

## Interview Discussion Points

### Key Topics to Discuss

1. **Message Ordering**
   - How to ensure messages arrive in order?
   - Use sequence numbers or timestamps
   - Handle out-of-order delivery

2. **Group Chat Scalability**
   - How to handle 256-member groups?
   - Message fan-out optimization
   - Read receipt aggregation

3. **Offline Message Delivery**
   - Queue management
   - Delivery guarantees
   - Storage optimization

4. **Media Optimization**
   - Compression strategies
   - Progressive loading
   - Bandwidth optimization

5. **Presence Privacy**
   - Last seen privacy
   - Online status privacy
   - Implementation details

6. **Cross-Platform Sync**
   - Multiple device support
   - Message sync across devices
   - Read receipt consistency

7. **Search Functionality**
   - Full-text search
   - Search indexing
   - Search across media

8. **Backup & Recovery**
   - Message backup
   - Disaster recovery
   - Data retention policies

### Common Follow-up Questions

- How would you handle message deletion for everyone?
- How to prevent spam messages?
- How to implement message reactions?
- How to handle voice/video calls?
- How to implement status updates (stories)?
- How to scale to 5B users?

---

## Additional Considerations

### Voice & Video Calls

- Use WebRTC for peer-to-peer communication
- TURN/STUN servers for NAT traversal
- Signaling via WebSocket
- Fallback to relay servers if needed

### Status Updates (Stories)

- Similar to Instagram stories
- 24-hour expiration
- Media storage and CDN
- View tracking
- Privacy controls

### Message Search

- Index messages in search engine (Elasticsearch)
- Full-text search capability
- Search across media metadata
- Pagination for search results

---

*This document provides a comprehensive system design for WhatsApp. Adjustments may be needed based on specific requirements and constraints.*

