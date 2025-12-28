# Instagram System Design Document

## Table of Contents
1. [Overview](#overview)
2. [Requirements](#requirements)
3. [System Architecture](#system-architecture)
4. [Database Design](#database-design)
5. [API Design](#api-design)
6. [Feed Generation](#feed-generation)
7. [Image/Video Processing](#imagevideo-processing)
8. [Search & Discovery](#search--discovery)
9. [Stories Feature](#stories-feature)
10. [Direct Messaging](#direct-messaging)
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

Instagram is a photo and video sharing social networking platform. Users can upload photos and videos, follow other users, like and comment on posts, share stories, and send direct messages. The system must handle billions of posts, millions of uploads daily, and provide personalized feeds with low latency.

**Key Features:**
- Photo and video uploads
- User feed (timeline)
- Stories (24-hour ephemeral content)
- Direct messaging
- Explore/discovery feed
- Search functionality
- Like and comment system
- Follow/unfollow users
- Hashtags and mentions
- Reels (short-form videos)
- IGTV (long-form videos)
- Live streaming

---

## Requirements

### Functional Requirements

1. **User Management**
   - User registration and authentication
   - User profiles (bio, profile picture, followers/following count)
   - Follow/unfollow users
   - Block/unblock users
   - Privacy settings (public/private accounts)

2. **Content Upload**
   - Upload photos (JPEG, PNG)
   - Upload videos (MP4, MOV)
   - Multiple photos per post (carousel)
   - Apply filters and edits
   - Add captions and hashtags
   - Tag users in posts
   - Location tagging

3. **Feed**
   - Home feed (posts from followed users)
   - Personalized feed ranking
   - Infinite scroll
   - Refresh feed
   - Explore feed (discovery)

4. **Interactions**
   - Like posts
   - Comment on posts
   - Reply to comments
   - Share posts
   - Save posts (collections)
   - Report inappropriate content

5. **Stories**
   - Upload photos/videos as stories
   - Add text, stickers, filters
   - View stories from followed users
   - Story expires after 24 hours
   - Story highlights (saved stories)

6. **Direct Messaging**
   - Send text messages
   - Send photos/videos
   - Group chats
   - Message status (sent, delivered, read)

7. **Search & Discovery**
   - Search users
   - Search hashtags
   - Search locations
   - Explore page (trending content)
   - Suggested users

8. **Notifications**
   - Like notifications
   - Comment notifications
   - Follow notifications
   - Mention notifications
   - Story view notifications

### Non-Functional Requirements

1. **Scalability**
   - Support 1B+ active users globally
   - Handle 100M+ photo uploads per day
   - Handle 500M+ likes per day
   - Support 1B+ feed views per day
   - 99.99% uptime
   - Multi-region deployment

2. **Performance**
   - Feed load time: < 2 seconds
   - Image upload: < 5 seconds
   - Video upload: < 30 seconds (for 1 min video)
   - Search results: < 200ms
   - Like/comment: < 100ms

3. **Storage**
   - Store billions of images and videos
   - Multiple image sizes (thumbnail, medium, full)
   - Video transcoding (multiple qualities)
   - Efficient storage and retrieval

4. **Reliability**
   - No data loss
   - High availability
   - Graceful degradation

5. **Security**
   - Secure authentication
   - Content moderation
   - Privacy controls
   - Protection against abuse

---

## System Architecture

### High-Level Architecture

```
┌─────────────┐
│   Mobile    │
│   Clients   │
│   Web App   │
└──────┬──────┘
       │
       │ HTTPS
       │
┌──────▼─────────────────────────────────────────┐
│           Load Balancer                        │
│         (SSL Termination)                      │
└──────┬─────────────────────────────────────────┘
       │
       ├─────────────────┬─────────────────┐
       │                 │                 │
┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐
│   API       │  │   Media     │  │   Feed      │
│   Servers   │  │   Service   │  │   Service   │
│             │  │             │  │             │
│ - Auth     │  │ - Upload    │  │ - Generate  │
│ - Posts    │  │ - Process   │  │   feed      │
│ - Users    │  │ - Store     │  │ - Rank      │
│ - Search   │  │ - CDN       │  │ - Cache     │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                 │                 │
       └─────────────────┼─────────────────┘
                         │
              ┌──────────▼──────────┐
              │   Message Queue     │
              │   (Kafka)           │
              └──────────┬──────────┘
                         │
       ┌─────────────────┼─────────────────┐
       │                 │                 │
┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐
│  Image      │  │  Video      │  │  Notification│
│  Processing │  │  Processing │  │  Service    │
│  Workers    │  │  Workers    │  │             │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                 │                 │
       └─────────────────┼─────────────────┘
                         │
              ┌──────────▼──────────┐
              │   Database Layer     │
              │                      │
              │  - User DB (MySQL)   │
              │  - Post DB           │
              │    (Cassandra)       │
              │  - Graph DB          │
              │    (Neo4j)           │
              │  - Search (ES)       │
              │  - Cache (Redis)     │
              │  - Media (S3)        │
              └──────────────────────┘
```

### Component Details

1. **API Servers**
   - Handle all HTTP requests
   - Authentication and authorization
   - Request validation
   - Rate limiting

2. **Media Service**
   - Handle media uploads
   - Validate file types and sizes
   - Generate upload URLs
   - Coordinate with processing workers

3. **Feed Service**
   - Generate user feeds
   - Rank posts (relevance, recency)
   - Cache feed data
   - Handle feed refresh

4. **Image Processing Workers**
   - Resize images (multiple sizes)
   - Apply compression
   - Generate thumbnails
   - Store in object storage

5. **Video Processing Workers**
   - Transcode videos (multiple qualities)
   - Generate thumbnails
   - Extract metadata
   - Store in object storage

6. **Notification Service**
   - Generate notifications
   - Send push notifications
   - Send email notifications
   - Batch notifications

---

## Database Design

### User Database (MySQL)

**users**
```sql
CREATE TABLE users (
    user_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    bio TEXT,
    profile_picture_url VARCHAR(500),
    is_private BOOLEAN DEFAULT FALSE,
    follower_count INT DEFAULT 0,
    following_count INT DEFAULT 0,
    post_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email)
);
```

**follows**
```sql
CREATE TABLE follows (
    follower_id BIGINT NOT NULL,
    followee_id BIGINT NOT NULL,
    status ENUM('pending', 'accepted') DEFAULT 'accepted',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (follower_id, followee_id),
    FOREIGN KEY (follower_id) REFERENCES users(user_id),
    FOREIGN KEY (followee_id) REFERENCES users(user_id),
    INDEX idx_follower (follower_id),
    INDEX idx_followee (followee_id)
);
```

### Post Database (Cassandra)

**posts**
```sql
CREATE TABLE posts (
    post_id TIMEUUID,
    user_id BIGINT,
    media_type TEXT,  -- photo, video, carousel
    media_urls LIST<TEXT>,
    caption TEXT,
    location TEXT,
    like_count COUNTER,
    comment_count COUNTER,
    created_at TIMESTAMP,
    PRIMARY KEY (user_id, created_at, post_id)
) WITH CLUSTERING ORDER BY (created_at DESC, post_id DESC);
```

**post_by_id**
```sql
CREATE TABLE post_by_id (
    post_id TIMEUUID PRIMARY KEY,
    user_id BIGINT,
    media_type TEXT,
    media_urls LIST<TEXT>,
    caption TEXT,
    location TEXT,
    like_count COUNTER,
    comment_count COUNTER,
    created_at TIMESTAMP,
    INDEX idx_user (user_id)
);
```

**comments**
```sql
CREATE TABLE comments (
    post_id TIMEUUID,
    comment_id TIMEUUID,
    user_id BIGINT,
    text TEXT,
    parent_comment_id TIMEUUID,  -- for replies
    like_count COUNTER,
    created_at TIMESTAMP,
    PRIMARY KEY (post_id, created_at, comment_id)
) WITH CLUSTERING ORDER BY (created_at ASC, comment_id ASC);
```

**likes**
```sql
CREATE TABLE likes (
    post_id TIMEUUID,
    user_id BIGINT,
    created_at TIMESTAMP,
    PRIMARY KEY (post_id, user_id)
);
```

**user_likes**
```sql
CREATE TABLE user_likes (
    user_id BIGINT,
    post_id TIMEUUID,
    created_at TIMESTAMP,
    PRIMARY KEY (user_id, created_at, post_id)
) WITH CLUSTERING ORDER BY (created_at DESC, post_id DESC);
```

### Graph Database (Neo4j) - For Social Graph

**Nodes**
- User nodes with properties (user_id, username)
- Post nodes with properties (post_id, created_at)

**Relationships**
- FOLLOWS: (User)-[:FOLLOWS]->(User)
- LIKED: (User)-[:LIKED]->(Post)
- COMMENTED: (User)-[:COMMENTED]->(Post)

### Search Database (Elasticsearch)

**posts_index**
```json
{
  "mappings": {
    "properties": {
      "post_id": {"type": "keyword"},
      "user_id": {"type": "long"},
      "caption": {"type": "text", "analyzer": "standard"},
      "hashtags": {"type": "keyword"},
      "location": {"type": "keyword"},
      "created_at": {"type": "date"}
    }
  }
}
```

**users_index**
```json
{
  "mappings": {
    "properties": {
      "user_id": {"type": "long"},
      "username": {"type": "keyword"},
      "full_name": {"type": "text"},
      "bio": {"type": "text"}
    }
  }
}
```

### Cache (Redis)

**User Feed**
```
Key: feed:{user_id}
Value: List of post_ids (last 100)
TTL: 1 hour
```

**Post Data**
```
Key: post:{post_id}
Value: JSON post data
TTL: 24 hours
```

**User Data**
```
Key: user:{user_id}
Value: JSON user data
TTL: 1 hour
```

**Like Count**
```
Key: likes:{post_id}
Value: Count
TTL: 1 hour
```

**Follow Graph**
```
Key: followers:{user_id}
Value: Set of follower_ids
TTL: 30 minutes
```

---

## API Design

### Authentication APIs

**POST /api/v1/auth/register**
```json
Request:
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "secure_password",
  "full_name": "John Doe"
}

Response:
{
  "success": true,
  "user": {
    "user_id": 123,
    "username": "johndoe",
    "token": "jwt_token_here"
  }
}
```

**POST /api/v1/auth/login**
```json
Request:
{
  "username": "johndoe",
  "password": "secure_password"
}

Response:
{
  "success": true,
  "token": "jwt_token_here",
  "user": {...}
}
```

### Post APIs

**POST /api/v1/posts**
```json
Request: multipart/form-data
- media: file(s)
- caption: "Beautiful sunset #sunset"
- location: "San Francisco, CA"

Response:
{
  "success": true,
  "post": {
    "post_id": "uuid-here",
    "user_id": 123,
    "media_urls": ["https://cdn.instagram.com/..."],
    "caption": "Beautiful sunset #sunset",
    "created_at": "2024-01-01T12:00:00Z"
  }
}
```

**GET /api/v1/posts/{post_id}**
```json
Response:
{
  "post": {
    "post_id": "uuid-here",
    "user": {...},
    "media_urls": [...],
    "caption": "...",
    "like_count": 150,
    "comment_count": 20,
    "comments": [...],
    "created_at": "..."
  }
}
```

**DELETE /api/v1/posts/{post_id}**
```json
Response:
{
  "success": true
}
```

### Feed APIs

**GET /api/v1/feed**
```json
Query Parameters:
- limit: 20 (default)
- max_id: post_id (for pagination)

Response:
{
  "posts": [
    {
      "post_id": "uuid-1",
      "user": {...},
      "media_urls": [...],
      "caption": "...",
      "like_count": 150,
      "comment_count": 20,
      "created_at": "..."
    }
  ],
  "next_max_id": "uuid-20"
}
```

**GET /api/v1/feed/explore**
```json
Query Parameters:
- limit: 20
- max_id: post_id

Response:
{
  "posts": [...],
  "next_max_id": "..."
}
```

### Interaction APIs

**POST /api/v1/posts/{post_id}/like**
```json
Response:
{
  "success": true,
  "like_count": 151
}
```

**DELETE /api/v1/posts/{post_id}/like**
```json
Response:
{
  "success": true,
  "like_count": 150
}
```

**POST /api/v1/posts/{post_id}/comments**
```json
Request:
{
  "text": "Great photo!",
  "parent_comment_id": null  // for replies
}

Response:
{
  "success": true,
  "comment": {
    "comment_id": "uuid-here",
    "user": {...},
    "text": "Great photo!",
    "created_at": "..."
  }
}
```

### User APIs

**GET /api/v1/users/{user_id}**
```json
Response:
{
  "user": {
    "user_id": 123,
    "username": "johndoe",
    "full_name": "John Doe",
    "bio": "...",
    "follower_count": 1000,
    "following_count": 500,
    "post_count": 150,
    "is_following": false
  }
}
```

**POST /api/v1/users/{user_id}/follow**
```json
Response:
{
  "success": true,
  "is_following": true
}
```

**GET /api/v1/users/{user_id}/posts**
```json
Query Parameters:
- limit: 20
- max_id: post_id

Response:
{
  "posts": [...],
  "next_max_id": "..."
}
```

### Search APIs

**GET /api/v1/search**
```json
Query Parameters:
- q: "search query"
- type: "users|hashtags|locations|posts"
- limit: 20

Response:
{
  "results": {
    "users": [...],
    "hashtags": [...],
    "locations": [...],
    "posts": [...]
  }
}
```

### Stories APIs

**POST /api/v1/stories**
```json
Request: multipart/form-data
- media: file
- text: "Optional text overlay"

Response:
{
  "success": true,
  "story": {
    "story_id": "uuid-here",
    "media_url": "...",
    "expires_at": "2024-01-02T12:00:00Z"
  }
}
```

**GET /api/v1/stories/feed**
```json
Response:
{
  "stories": [
    {
      "user": {...},
      "stories": [
        {
          "story_id": "uuid-1",
          "media_url": "...",
          "expires_at": "...",
          "viewed": false
        }
      ]
    }
  ]
}
```

---

## Feed Generation

### Feed Generation Strategy

**Approach: Pre-computed Feed**

1. **When User Posts**
   - Get all followers
   - Add post_id to each follower's feed cache
   - Update feed in background

2. **When User Follows**
   - Get recent posts from followee
   - Add to follower's feed cache
   - Merge with existing feed

3. **When User Unfollows**
   - Remove followee's posts from feed cache
   - Update feed

### Feed Ranking Algorithm

**Factors:**
1. **Recency** (40%)
   - Newer posts ranked higher
   - Exponential decay based on time

2. **Engagement** (30%)
   - Likes, comments, shares
   - Higher engagement = higher rank

3. **Relationship** (20%)
   - Close friends ranked higher
   - Mutual connections
   - Interaction history

4. **Content Type** (10%)
   - Videos ranked slightly higher
   - Carousel posts

**Formula:**
```
Score = (recency_score * 0.4) + 
        (engagement_score * 0.3) + 
        (relationship_score * 0.2) + 
        (content_type_score * 0.1)
```

### Feed Generation Flow

```
User Request Feed
       │
       ▼
Check Redis Cache
       │
       ├─── Cache Hit ───> Return cached feed
       │
       └─── Cache Miss ───> Generate Feed
                              │
                              ├──> Get Followed Users
                              ├──> Get Recent Posts
                              ├──> Rank Posts
                              ├──> Store in Cache
                              └──> Return Feed
```

### Feed Refresh

- Background job refreshes feed every hour
- On new post from followed user: Add to feed immediately
- On follow: Merge new user's posts into feed
- On unfollow: Remove user's posts from feed

---

## Image/Video Processing

### Image Processing Pipeline

1. **Upload**
   - Client uploads image to media service
   - Media service validates (size, format)
   - Store original in temporary storage

2. **Processing**
   - Resize to multiple sizes:
     - Thumbnail: 150x150
     - Small: 320x320
     - Medium: 640x640
     - Large: 1080x1080
   - Apply compression (JPEG quality: 85%)
   - Generate WebP version (better compression)
   - Extract metadata (EXIF)

3. **Storage**
   - Upload all sizes to object storage (S3)
   - Store URLs in database
   - Invalidate CDN cache

4. **Delivery**
   - Serve via CDN
   - Client requests appropriate size based on device
   - Progressive loading (thumbnail → full)

### Video Processing Pipeline

1. **Upload**
   - Client uploads video
   - Chunked upload for large files
   - Store in temporary storage

2. **Transcoding**
   - Transcode to multiple qualities:
     - 240p (mobile, low bandwidth)
     - 480p (mobile, medium bandwidth)
     - 720p (tablet, good bandwidth)
     - 1080p (desktop, high bandwidth)
   - Generate HLS segments for adaptive streaming
   - Extract thumbnail frames
   - Extract metadata (duration, resolution, codec)

3. **Storage**
   - Store all qualities in object storage
   - Store thumbnail frames
   - Store manifest files (HLS)

4. **Delivery**
   - Serve via CDN
   - Adaptive bitrate streaming
   - Progressive download option

### Processing Workers

- Use message queue (Kafka) for processing jobs
- Multiple workers process in parallel
- Retry failed processing
- Notify when processing complete

---

## Search & Discovery

### Search Functionality

**Search Types:**
1. **User Search**
   - Search by username
   - Search by full name
   - Rank by relevance and follower count

2. **Hashtag Search**
   - Search hashtags
   - Show post count
   - Show top posts

3. **Location Search**
   - Search locations
   - Show posts from location
   - Rank by recency and engagement

4. **Post Search**
   - Full-text search on captions
   - Search by hashtags
   - Rank by relevance and engagement

### Search Implementation

**Elasticsearch Indexing**
- Index posts on creation/update
- Index users on creation/update
- Update indexes in real-time

**Search Query**
```json
{
  "query": {
    "multi_match": {
      "query": "search term",
      "fields": ["caption", "hashtags", "location"],
      "type": "best_fields"
    }
  },
  "sort": [
    {"created_at": "desc"},
    {"_score": "desc"}
  ]
}
```

### Explore Feed

**Algorithm:**
1. Get trending posts (high engagement, recent)
2. Get posts from users similar to followed users
3. Get posts with similar hashtags to liked posts
4. Rank by:
   - Engagement score
   - Recency
   - User similarity
   - Content diversity

**Implementation:**
- Pre-compute explore feed
- Update every hour
- Cache in Redis
- Personalize per user

---

## Stories Feature

### Stories Architecture

**Storage:**
- Store stories in object storage
- Expire after 24 hours (TTL)
- Store metadata in database

**Database:**
```sql
CREATE TABLE stories (
    story_id TIMEUUID PRIMARY KEY,
    user_id BIGINT NOT NULL,
    media_url TEXT NOT NULL,
    media_type TEXT,  -- photo, video
    created_at TIMESTAMP,
    expires_at TIMESTAMP,
    view_count COUNTER,
    INDEX idx_user_expires (user_id, expires_at)
);
```

**Story Views:**
```sql
CREATE TABLE story_views (
    story_id TIMEUUID,
    viewer_id BIGINT,
    viewed_at TIMESTAMP,
    PRIMARY KEY (story_id, viewer_id)
);
```

### Stories Flow

1. **Upload Story**
   - Upload media
   - Process (resize/transcode)
   - Store in object storage
   - Create story record (expires_at = now + 24h)

2. **View Stories**
   - Get stories from followed users
   - Group by user
   - Order by creation time
   - Mark as viewed

3. **Expiration**
   - Background job deletes expired stories
   - Delete from object storage
   - Delete from database

### Story Highlights

- Users can save stories to highlights
- Highlights don't expire
- Stored separately from regular stories
- Organized by category

---

## Direct Messaging

### Messaging Architecture

Similar to WhatsApp design:
- WebSocket for real-time messaging
- Message queue for delivery
- Store messages in database
- Support text and media messages

**Database:**
```sql
CREATE TABLE messages (
    chat_id TEXT,  -- user_id1_user_id2 or group_id
    message_id TIMEUUID,
    sender_id BIGINT,
    message_type TEXT,  -- text, image, video
    content TEXT,
    media_url TEXT,
    created_at TIMESTAMP,
    delivered_at TIMESTAMP,
    read_at TIMESTAMP,
    PRIMARY KEY (chat_id, created_at, message_id)
) WITH CLUSTERING ORDER BY (created_at DESC, message_id DESC);
```

---

## Scalability Considerations

### Horizontal Scaling

1. **API Servers**
   - Stateless design
   - Load balancer distributes requests
   - Auto-scaling based on load

2. **Processing Workers**
   - Scale workers independently
   - Process jobs from queue
   - Handle peak upload times

3. **Database Sharding**
   - Shard posts by user_id
   - Shard users by user_id
   - Use consistent hashing

### Vertical Scaling

- Use high-performance databases
- Optimize queries
- Use read replicas
- Partition large tables

### Caching Strategy

- Cache user feeds (Redis)
- Cache post data (Redis)
- Cache user data (Redis)
- CDN for media files
- Cache search results

---

## Caching Strategy

### Cache Layers

1. **Application Cache (Redis)**
   - User feeds: 1 hour TTL
   - Post data: 24 hours TTL
   - User data: 1 hour TTL
   - Like counts: 1 hour TTL
   - Follow graph: 30 minutes TTL

2. **CDN Cache**
   - Media files: Long TTL
   - Profile pictures: 1 day TTL
   - Static assets: 1 week TTL

3. **Database Query Cache**
   - Frequently accessed data
   - Expensive queries

### Cache Invalidation

- Post update: Invalidate post cache
- New post: Add to follower feeds
- Like/comment: Update post cache
- User update: Invalidate user cache

---

## Load Balancing

### Load Balancing Strategy

1. **API Requests**
   - Round-robin or least connections
   - Health checks
   - Session affinity (if needed)

2. **Media Uploads**
   - Distribute across media servers
   - Use consistent hashing
   - Handle large file uploads

3. **Feed Requests**
   - Distribute across feed servers
   - Cache-aware routing
   - Handle peak times

---

## Security

### Authentication & Authorization

1. **JWT Tokens**
   - Short-lived access tokens (1 hour)
   - Refresh tokens (30 days)
   - Token rotation

2. **Rate Limiting**
   - Per-user rate limits
   - Per-IP rate limits
   - Prevent abuse

3. **Input Validation**
   - Validate all inputs
   - Sanitize user content
   - Prevent XSS, SQL injection

### Content Security

1. **Content Moderation**
   - Automated content filtering
   - Report system
   - Manual review queue
   - Block inappropriate content

2. **Privacy Controls**
   - Private accounts
   - Block users
   - Restrict story views
   - Control who can comment

### Data Security

- Encryption at rest
- Encryption in transit (TLS)
- Secure media storage
- Access controls

---

## Monitoring & Analytics

### Key Metrics

1. **Performance Metrics**
   - Feed load time (p50, p95, p99)
   - API response time
   - Media upload time
   - Search latency

2. **System Metrics**
   - CPU, memory, disk usage
   - Database query performance
   - Cache hit rate
   - Queue depth

3. **Business Metrics**
   - Daily active users (DAU)
   - Posts per day
   - Likes per day
   - Stories per day
   - Engagement rate

### Monitoring Tools

- Application monitoring: Prometheus, Grafana
- Log aggregation: ELK Stack
- Distributed tracing: Jaeger
- Error tracking: Sentry

---

## Deployment Strategy

### Multi-Region Deployment

- Deploy in multiple regions
- Route users to nearest region
- Replicate data across regions
- Handle cross-region requests

### Blue-Green Deployment

- Zero-downtime deployments
- Rollback capability
- Gradual traffic migration

### Containerization

- Docker containers
- Kubernetes orchestration
- Auto-scaling

---

## Capacity Planning

### Storage Estimates

**Images**
- Average image size: 2MB (original)
- Multiple sizes: ~5MB total per image
- 100M uploads/day = 500TB/day = 182.5PB/year
- With compression: ~90PB/year

**Videos**
- Average video size: 50MB
- Multiple qualities: ~150MB total per video
- 10M uploads/day = 1.5PB/day = 547.5PB/year
- With compression: ~200PB/year

**Database**
- Post metadata: ~1KB/post = 100GB/day = 36.5TB/year
- User data: ~2KB/user = 2GB for 1B users
- Comments: ~500 bytes/comment = 250GB/day = 91TB/year

### Compute Estimates

**API Servers**
- 1B DAU, 100 requests/user/day = 100B requests/day
- ~1.16M requests/second peak
- Each server handles ~10K requests/second
- Need ~120 servers (with redundancy: ~180)

**Processing Workers**
- 100M images/day = ~1,200 images/second
- Each image: ~2 seconds processing
- Need ~2,400 workers (with overhead: ~3,600)

---

## Technology Stack

### Backend
- **Language**: Python (Django/Flask) or Java (Spring Boot)
- **Message Queue**: Kafka
- **Database**: 
  - MySQL (user data)
  - Cassandra (posts, comments)
  - Neo4j (social graph)
  - Elasticsearch (search)
  - Redis (cache)
- **Object Storage**: S3, Azure Blob, or GCS
- **CDN**: CloudFront, Cloudflare
- **Media Processing**: FFmpeg, ImageMagick

### Frontend
- **Mobile**: Native (Swift, Kotlin) or React Native
- **Web**: React or Next.js

### Infrastructure
- **Container Orchestration**: Kubernetes
- **Monitoring**: Prometheus, Grafana
- **Logging**: ELK Stack
- **CI/CD**: Jenkins, GitLab CI

---

## Failure Scenarios & Handling

### Single Server Failure

- Load balancer routes to healthy servers
- No data loss (data in database)
- Graceful degradation

### Database Failure

- Use database replicas
- Failover to replica
- Read from replica, write to primary

### Media Storage Failure

- Replicate media across regions
- Failover to backup storage
- Retry failed uploads

### Processing Failure

- Retry failed processing jobs
- Dead letter queue for failed jobs
- Manual reprocessing option

---

## Trade-offs & Design Decisions

### 1. Feed Generation: Pre-computed vs Real-time

**Chosen: Pre-computed**
- Faster feed load time
- Better user experience
- Higher storage cost
- More complex to maintain

**Trade-off**: Stale feed if not refreshed frequently

### 2. Database: SQL vs NoSQL

**Chosen: Hybrid**
- MySQL for user data (ACID, relationships)
- Cassandra for posts (high write throughput)
- Neo4j for social graph (graph queries)

**Trade-off**: More complex architecture

### 3. Media Storage: Database vs Object Storage

**Chosen: Object Storage**
- Cost-effective for large files
- Better scalability
- CDN integration

**Trade-off**: Additional service to manage

### 4. Search: Database vs Search Engine

**Chosen: Elasticsearch**
- Better full-text search
- Better ranking
- Scalable

**Trade-off**: Additional infrastructure

### 5. Feed Ranking: Simple vs ML-based

**Chosen: Rule-based (can evolve to ML)**
- Simpler to implement
- Easier to debug
- Can add ML later

**Trade-off**: Less personalized initially

---

## High-Level Design (HLD)

### System Overview

Instagram's architecture follows a microservices pattern with clear separation of concerns:

1. **Client Layer**: Mobile apps (iOS/Android), Web application
2. **API Gateway**: Routes requests, handles authentication, rate limiting
3. **Application Services**: Microservices for different functionalities
4. **Data Layer**: Multiple databases optimized for different use cases
5. **Storage Layer**: Object storage for media, CDN for content delivery
6. **Message Queue**: Kafka for asynchronous processing
7. **Processing Layer**: Workers for image/video processing

### Service Decomposition

**Core Services:**
- **Auth Service**: Authentication, authorization, session management
- **User Service**: User profiles, follow/unfollow, user search
- **Post Service**: Post CRUD operations, post metadata
- **Feed Service**: Feed generation, ranking, caching
- **Media Service**: Media upload coordination, processing queue management
- **Interaction Service**: Likes, comments, shares
- **Search Service**: Full-text search, hashtag search, user search
- **Story Service**: Story creation, expiration, highlights
- **Notification Service**: Push notifications, email notifications
- **Direct Messaging Service**: Real-time messaging

**Supporting Services:**
- **Image Processing Workers**: Resize, compress, generate thumbnails
- **Video Processing Workers**: Transcode, generate thumbnails, extract metadata
- **Analytics Service**: Event tracking, metrics collection
- **Moderation Service**: Content moderation, spam detection

### Data Flow Patterns

**Write Path (Post Creation):**
```
Client → API Gateway → Post Service → Kafka → Media Service → 
Processing Workers → Object Storage → CDN
```

**Read Path (Feed Generation):**
```
Client → API Gateway → Feed Service → Cache (Redis) → 
Post Service → Database → Response
```

**Real-time Path (Notifications):**
```
Event → Kafka → Notification Service → Push Service → Client
```

---

## Low-Level Design (LLD)

### Feed Service Implementation

```python
class FeedService:
    def __init__(self, redis_client, post_service, user_service):
        self.redis = redis_client
        self.post_service = post_service
        self.user_service = user_service
        self.feed_cache_ttl = 3600  # 1 hour
    
    def get_feed(self, user_id, limit=20, max_id=None):
        # Check cache first
        cache_key = f"feed:{user_id}"
        cached_feed = self.redis.lrange(cache_key, 0, limit - 1)
        
        if cached_feed and not max_id:
            return self._enrich_posts(cached_feed)
        
        # Get followed users
        followed_users = self.user_service.get_followed_users(user_id)
        
        # Get posts from followed users
        posts = self.post_service.get_posts_by_users(
            followed_users, limit, max_id
        )
        
        # Rank posts (relevance + recency)
        ranked_posts = self._rank_posts(posts, user_id)
        
        # Cache feed
        if not max_id:
            post_ids = [p['post_id'] for p in ranked_posts]
            self.redis.lpush(cache_key, *post_ids)
            self.redis.expire(cache_key, self.feed_cache_ttl)
        
        return ranked_posts
    
    def _rank_posts(self, posts, user_id):
        # Score = engagement_score * 0.7 + recency_score * 0.3
        for post in posts:
            engagement = (post['like_count'] * 0.5 + 
                         post['comment_count'] * 0.3 +
                         post['share_count'] * 0.2)
            recency = self._calculate_recency(post['created_at'])
            post['score'] = engagement * 0.7 + recency * 0.3
        
        return sorted(posts, key=lambda x: x['score'], reverse=True)
    
    def _calculate_recency(self, created_at):
        hours_ago = (time.time() - created_at) / 3600
        return max(0, 1 - hours_ago / 24)  # Decay over 24 hours
```

### Post Service Implementation

```python
class PostService:
    def __init__(self, cassandra_client, redis_client, kafka_producer):
        self.cassandra = cassandra_client
        self.redis = redis_client
        self.kafka = kafka_producer
    
    def create_post(self, user_id, media_urls, caption, location=None):
        post_id = uuid.uuid1()
        created_at = datetime.utcnow()
        
        # Extract hashtags and mentions
        hashtags = self._extract_hashtags(caption)
        mentions = self._extract_mentions(caption)
        
        # Store in Cassandra
        self.cassandra.execute(
            """
            INSERT INTO posts (post_id, user_id, media_urls, caption, 
                             location, like_count, comment_count, created_at)
            VALUES (?, ?, ?, ?, ?, 0, 0, ?)
            """,
            [post_id, user_id, media_urls, caption, location, created_at]
        )
        
        # Index in Elasticsearch (async)
        self.kafka.send('post-indexing', {
            'post_id': str(post_id),
            'user_id': user_id,
            'caption': caption,
            'hashtags': hashtags,
            'location': location,
            'created_at': created_at.isoformat()
        })
        
        # Invalidate feed cache for followers
        self._invalidate_follower_feeds(user_id)
        
        return {'post_id': post_id, 'created_at': created_at}
    
    def _invalidate_follower_feeds(self, user_id):
        # Get followers (cached)
        followers = self.user_service.get_followers(user_id)
        
        # Invalidate feed cache for each follower
        for follower_id in followers:
            self.redis.delete(f"feed:{follower_id}")
```

### Like Service Implementation

```python
class LikeService:
    def __init__(self, cassandra_client, redis_client):
        self.cassandra = cassandra_client
        self.redis = redis_client
    
    def like_post(self, user_id, post_id):
        # Check if already liked
        if self._is_liked(user_id, post_id):
            return {'success': False, 'error': 'already_liked'}
        
        # Use distributed lock to prevent race conditions
        lock_key = f"lock:like:{post_id}"
        with self.redis.lock(lock_key, timeout=5):
            # Double-check
            if self._is_liked(user_id, post_id):
                return {'success': False, 'error': 'already_liked'}
            
            # Add like
            self.cassandra.execute(
                """
                INSERT INTO likes (post_id, user_id, created_at)
                VALUES (?, ?, ?)
                """,
                [post_id, user_id, datetime.utcnow()]
            )
            
            # Update counters (atomic)
            self.cassandra.execute(
                """
                UPDATE posts SET like_count = like_count + 1
                WHERE post_id = ?
                """,
                [post_id]
            )
            
            # Update cache
            self.redis.incr(f"likes:{post_id}")
            self.redis.setex(
                f"user_like:{user_id}:{post_id}", 
                86400,  # 24 hours
                "1"
            )
            
            return {'success': True, 'like_count': self._get_like_count(post_id)}
    
    def _is_liked(self, user_id, post_id):
        # Check cache first
        cached = self.redis.get(f"user_like:{user_id}:{post_id}")
        if cached:
            return True
        
        # Check database
        result = self.cassandra.execute(
            "SELECT * FROM likes WHERE post_id = ? AND user_id = ?",
            [post_id, user_id]
        )
        return len(result) > 0
```

### Image Processing Worker

```python
class ImageProcessingWorker:
    def __init__(self, s3_client, redis_client):
        self.s3 = s3_client
        self.redis = redis_client
    
    def process_image(self, image_data, post_id):
        try:
            # Generate multiple sizes
            sizes = {
                'thumbnail': (150, 150),
                'small': (320, 320),
                'medium': (640, 640),
                'large': (1080, 1080)
            }
            
            processed_urls = {}
            
            for size_name, (width, height) in sizes.items():
                # Resize image
                resized = self._resize_image(image_data, width, height)
                
                # Compress
                compressed = self._compress_image(resized, quality=85)
                
                # Upload to S3
                s3_key = f"posts/{post_id}/{size_name}.jpg"
                url = self.s3.upload(s3_key, compressed)
                processed_urls[size_name] = url
            
            # Update post with processed URLs
            self._update_post_urls(post_id, processed_urls)
            
            return {'success': True, 'urls': processed_urls}
        
        except Exception as e:
            # Log error and send to dead letter queue
            self._handle_error(post_id, str(e))
            raise
    
    def _resize_image(self, image_data, width, height):
        # Use PIL/Pillow for resizing
        from PIL import Image
        import io
        
        img = Image.open(io.BytesIO(image_data))
        img = img.resize((width, height), Image.Resampling.LANCZOS)
        
        output = io.BytesIO()
        img.save(output, format='JPEG')
        return output.getvalue()
```

---

## Fault Tolerance

### Service Redundancy

**Multiple Instances:**
- Each service deployed with multiple instances (minimum 3 per region)
- Load balancer distributes traffic across healthy instances
- Health checks every 10 seconds
- Automatic instance replacement on failure

**Database Replication:**
- **MySQL**: Primary-replica setup with automatic failover
  - 1 primary + 2 replicas per region
  - Read replicas for read-heavy operations
  - Automatic promotion of replica to primary on failure
- **Cassandra**: Multi-datacenter replication
  - Replication factor: 3 per datacenter
  - Cross-datacenter replication for disaster recovery
  - Consistency level: QUORUM for writes, ONE for reads
- **Redis**: Redis Cluster with replication
  - 3 master nodes + 3 replica nodes per shard
  - Automatic failover using Redis Sentinel
  - Data sharded across multiple nodes

### Message Queue Resilience

**Kafka Cluster:**
- Multi-broker Kafka cluster (minimum 3 brokers)
- Topic replication factor: 3
- Producer acknowledgments: `acks=all` for critical topics
- Consumer groups for parallel processing
- Dead letter queues for failed messages
- Message retention: 7 days for critical topics

**Failure Handling:**
```python
class ResilientKafkaProducer:
    def __init__(self, kafka_producer, fallback_storage):
        self.producer = kafka_producer
        self.fallback = fallback_storage
    
    def send(self, topic, message):
        try:
            future = self.producer.send(topic, message)
            future.get(timeout=10)  # Wait for acknowledgment
        except Exception as e:
            # Store in fallback storage (S3) for later processing
            self.fallback.store(topic, message)
            raise
```

### Circuit Breaker Pattern

```python
from circuitbreaker import circuit

class PostServiceClient:
    def __init__(self, post_service_url):
        self.url = post_service_url
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60,
            expected_exception=RequestException
        )
    
    @circuit
    def get_post(self, post_id):
        try:
            response = requests.get(f"{self.url}/posts/{post_id}", timeout=5)
            response.raise_for_status()
            return response.json()
        except RequestException:
            # Fallback to cache or stale data
            return self._get_from_cache(post_id)
```

### Retry Logic with Exponential Backoff

```python
import time
from tenacity import retry, stop_after_attempt, wait_exponential

class DatabaseClient:
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def execute_query(self, query, params):
        try:
            return self.connection.execute(query, params)
        except DatabaseError as e:
            if self._is_retryable_error(e):
                raise  # Retry
            else:
                raise  # Don't retry
```

### Data Consistency Mechanisms

**Distributed Locks:**
- Redis-based distributed locks for critical operations
- Lock timeout to prevent deadlocks
- Lock renewal for long-running operations

**Idempotency:**
- Idempotency keys for all write operations
- Store idempotency keys in Redis with TTL
- Reject duplicate requests based on idempotency key

**Optimistic Locking:**
- Version numbers for posts, comments
- CAS (Compare-And-Swap) operations in Cassandra
- Conflict resolution on version mismatch

---

## Optimizations

### Caching Strategy

**Multi-Level Caching:**
1. **Client Cache**: Cache feed, posts, user data in mobile app
2. **CDN Cache**: Cache media files, static assets
3. **Application Cache**: Redis cache for frequently accessed data
4. **Database Query Cache**: Cache query results

**Cache Keys Design:**
```
feed:{user_id} → List of post IDs
post:{post_id} → Post metadata
user:{user_id} → User profile
likes:{post_id} → Like count
followers:{user_id} → Set of follower IDs
```

**Cache Invalidation:**
- **TTL-based**: Automatic expiration after TTL
- **Event-based**: Invalidate on updates (post creation, like, etc.)
- **Write-through**: Update cache on write operations
- **Cache-aside**: Check cache, fallback to database

### Database Query Optimization

**Indexing Strategy:**
- **MySQL**: Indexes on username, email, user_id
- **Cassandra**: Primary key design for efficient queries
  - Partition key: user_id (for user's posts)
  - Clustering key: created_at DESC (for chronological order)
- **Elasticsearch**: Analyzed fields for full-text search, keyword fields for exact match

**Query Optimization:**
- Batch queries where possible
- Use prepared statements
- Limit result sets with pagination
- Avoid N+1 queries (use JOINs or batch fetching)

**Read Replicas:**
- Route read queries to replicas
- Use primary only for writes
- Monitor replica lag

### Feed Generation Optimization

**Pre-computation:**
- Pre-compute feeds for active users
- Store in Redis with TTL
- Refresh on new posts from followed users

**Incremental Updates:**
- Instead of regenerating entire feed, append new posts
- Use sorted sets in Redis for efficient insertion
- Trim old posts beyond feed size limit

**Ranking Optimization:**
- Pre-calculate engagement scores
- Cache ranking results
- Update scores incrementally on interactions

### Media Processing Optimization

**Parallel Processing:**
- Process multiple sizes in parallel
- Use worker pools for concurrent processing
- Process videos in chunks

**Compression:**
- Use efficient compression algorithms (WebP for images)
- Adaptive quality based on device/network
- Lazy loading of high-resolution images

**CDN Optimization:**
- Cache media files at edge locations
- Use HTTP/2 for multiplexing
- Implement range requests for video streaming

### Network Optimization

**Request Batching:**
- Batch multiple API calls into single request
- Reduce round trips
- Use GraphQL for flexible queries

**Compression:**
- Gzip/Brotli compression for API responses
- Compress images/videos before upload
- Use efficient serialization (Protocol Buffers, MessagePack)

**Connection Pooling:**
- Reuse database connections
- HTTP connection pooling
- WebSocket connections for real-time features

---

## Failure Safety

### Database Failure Handling

**Scenario: MySQL Primary Failure**
- **Detection**: Health check fails, connection errors
- **Mitigation**: 
  - Automatic failover to replica (within 30 seconds)
  - Update DNS/load balancer to point to new primary
  - Promote replica to primary
- **Recovery**: 
  - Sync remaining replicas
  - Restore from backup if data loss detected
  - Replay transaction logs

**Scenario: Cassandra Node Failure**
- **Detection**: Node unresponsive, replication factor not met
- **Mitigation**:
  - Continue serving requests from remaining nodes
  - Use QUORUM consistency (2 out of 3 nodes)
  - Automatic node replacement
- **Recovery**:
  - Repair data on recovered node
  - Stream data from other replicas
  - Verify data consistency

**Scenario: Redis Cluster Failure**
- **Detection**: Cluster nodes down, quorum lost
- **Mitigation**:
  - Fallback to database for reads
  - Use local cache if available
  - Degrade to read-only mode
- **Recovery**:
  - Restore from RDB snapshots
  - Rebuild cache from database
  - Gradually warm up cache

### Service Failure Handling

**Scenario: Feed Service Failure**
- **Impact**: Users cannot load feed
- **Mitigation**:
  - Load balancer routes to healthy instances
  - Serve stale feed from cache if available
  - Return error with retry suggestion
- **Recovery**:
  - Restart failed instances
  - Verify health checks
  - Gradually increase traffic

**Scenario: Media Processing Worker Failure**
- **Impact**: Uploaded media not processed
- **Mitigation**:
  - Store raw media in S3
  - Retry processing from queue
  - Use dead letter queue for failed jobs
- **Recovery**:
  - Reprocess failed jobs
  - Scale up workers if backlog exists
  - Monitor processing queue depth

**Scenario: Kafka Broker Failure**
- **Impact**: Events not processed, processing delays
- **Mitigation**:
  - Kafka cluster continues with remaining brokers
  - Producer retries with exponential backoff
  - Store critical events in fallback storage (S3)
- **Recovery**:
  - Restore failed broker
  - Replay events from fallback storage
  - Verify consumer lag

### Network Partition Handling

**Scenario: Region Isolation**
- **Impact**: Users in isolated region cannot access service
- **Mitigation**:
  - Multi-region deployment with local replicas
  - Serve reads from local region
  - Queue writes for later sync
- **Recovery**:
  - Sync data when partition resolves
  - Resolve conflicts using timestamps
  - Verify data consistency

**Scenario: CDN Failure**
- **Impact**: Slow media loading, increased origin load
- **Mitigation**:
  - Multiple CDN providers (failover)
  - Serve from origin if CDN unavailable
  - Reduce quality/compression to reduce load
- **Recovery**:
  - Switch to backup CDN
  - Scale origin servers
  - Warm up CDN cache

### Data Loss Prevention

**Backup Strategy:**
- **MySQL**: Daily full backups + hourly incremental backups
- **Cassandra**: Snapshot backups every 6 hours
- **S3**: Versioning enabled, cross-region replication
- **Redis**: RDB snapshots every hour + AOF for critical data

**Replication:**
- Multi-region replication for critical data
- Synchronous replication for user data
- Asynchronous replication for posts/comments

**Monitoring:**
- Monitor replication lag
- Alert on backup failures
- Regular backup restoration tests

---

## Scalability

### Horizontal Scaling

**Stateless Services:**
- All application services are stateless
- Scale by adding more instances
- Load balancer distributes traffic
- Auto-scaling based on CPU/memory/request rate

**Database Scaling:**
- **MySQL**: Read replicas for read scaling, sharding for write scaling
- **Cassandra**: Add nodes to cluster, automatic data redistribution
- **Redis**: Redis Cluster with sharding, add shards as needed
- **Elasticsearch**: Add nodes, increase shard count

### Vertical Scaling

**Database Optimization:**
- Increase instance size for databases
- Optimize queries and indexes
- Partition large tables
- Archive old data

**Caching:**
- Increase Redis memory
- Use larger cache TTLs
- Implement cache warming

### Sharding Strategy

**User Sharding:**
- Shard MySQL by user_id (hash-based)
- Each shard handles subset of users
- Shard router determines target shard

**Post Sharding:**
- Cassandra naturally shards by partition key (user_id)
- Each node handles subset of partitions
- Automatic rebalancing on node add/remove

**Feed Sharding:**
- Shard feed cache by user_id
- Each Redis shard handles subset of users
- Consistent hashing for shard assignment

### Load Distribution

**Geographic Distribution:**
- Deploy in multiple regions (US, EU, APAC)
- Route users to nearest region
- Replicate data across regions
- Local read replicas for low latency

**Content Distribution:**
- CDN for media files
- Edge caching for static assets
- Regional data centers for API services

### Performance Scaling

**Throughput Scaling:**
- Increase Kafka partitions for parallel processing
- Add more worker instances
- Optimize batch sizes
- Use connection pooling

**Latency Optimization:**
- Reduce database query time (indexes, query optimization)
- Reduce network latency (CDN, regional deployment)
- Reduce processing time (caching, pre-computation)
- Use async processing where possible

### Capacity Planning

**Traffic Growth:**
- Monitor key metrics (requests/second, active users)
- Plan capacity for 2x current load
- Auto-scaling for predictable growth
- Manual scaling for unexpected spikes

**Storage Growth:**
- Monitor storage usage trends
- Implement data retention policies
- Archive old data to cheaper storage
- Compress data where possible

**Cost Optimization:**
- Use spot instances for non-critical workloads
- Right-size instances based on actual usage
- Use reserved instances for predictable workloads
- Monitor and optimize costs regularly

---

## Interview Discussion Points

### Key Topics to Discuss

1. **Feed Ranking Algorithm**
   - How to rank posts?
   - How to balance recency vs engagement?
   - How to prevent echo chambers?

2. **Stories Expiration**
   - How to efficiently delete expired stories?
   - How to handle story highlights?

3. **Hashtag Trending**
   - How to identify trending hashtags?
   - How to prevent hashtag spam?

4. **Explore Feed**
   - How to personalize explore feed?
   - How to ensure content diversity?

5. **Media Processing**
   - How to handle peak upload times?
   - How to optimize storage costs?

6. **Search Scalability**
   - How to handle search at scale?
   - How to rank search results?

7. **Notification System**
   - How to batch notifications?
   - How to prevent notification spam?

8. **Content Moderation**
   - How to detect inappropriate content?
   - How to handle reports?

### Common Follow-up Questions

- How would you implement Reels?
- How to handle live streaming?
- How to implement IGTV?
- How to optimize for low-bandwidth users?
- How to handle spam accounts?
- How to implement video calls?

---

*This document provides a comprehensive system design for Instagram. Adjustments may be needed based on specific requirements and constraints.*

