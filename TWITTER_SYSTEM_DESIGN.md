# Twitter System Design Document

## Table of Contents
1. [Overview](#overview)
2. [Requirements](#requirements)
3. [High-Level Design (HLD)](#high-level-design-hld)
4. [Low-Level Design (LLD)](#low-level-design-lld)
5. [System Architecture](#system-architecture)
6. [Database Design](#database-design)
7. [API Design](#api-design)
8. [Timeline Generation](#timeline-generation)
9. [Tweet Delivery](#tweet-delivery)
10. [Search Functionality](#search-functionality)
11. [Trending Topics](#trending-topics)
12. [Fault Tolerance](#fault-tolerance)
13. [Failure Safety](#failure-safety)
14. [Scalability Considerations](#scalability-considerations)
15. [Optimizations](#optimizations)
16. [Caching Strategy](#caching-strategy)
17. [Load Balancing](#load-balancing)
18. [Security](#security)
19. [Monitoring & Analytics](#monitoring--analytics)
20. [Deployment Strategy](#deployment-strategy)
21. [Capacity Planning](#capacity-planning)
22. [Technology Stack](#technology-stack)
23. [Failure Scenarios & Handling](#failure-scenarios--handling)
24. [Trade-offs & Design Decisions](#trade-offs--design-decisions)
25. [Interview Discussion Points](#interview-discussion-points)

---

## Overview

Twitter is a social networking platform where users post short messages (tweets), follow other users, and interact through likes, retweets, and replies. The system must handle hundreds of millions of tweets daily, generate personalized timelines in real-time, support real-time search, and manage trending topics.

**Key Features:**
- Tweet creation (280 characters)
- User timeline (home feed)
- User profile timeline
- Follow/unfollow users
- Like, retweet, reply
- Search tweets and users
- Trending topics
- Hashtags and mentions
- Media attachments (images, videos)
- Notifications
- Direct messaging

---

## Requirements

### Functional Requirements

1. **User Management**
   - User registration and authentication
   - User profiles (bio, profile picture, header image)
   - Follow/unfollow users
   - Block/unblock users
   - Privacy settings

2. **Tweet Management**
   - Create tweets (text, up to 280 characters)
   - Delete tweets
   - Edit tweets (limited)
   - Attach media (images, videos, GIFs)
   - Thread tweets (reply chains)

3. **Timeline**
   - Home timeline (tweets from followed users)
   - User timeline (tweets from specific user)
   - Personalized ranking
   - Infinite scroll
   - Real-time updates

4. **Interactions**
   - Like tweets
   - Retweet (share)
   - Quote tweet (retweet with comment)
   - Reply to tweets
   - Bookmark tweets

5. **Search**
   - Search tweets (full-text search)
   - Search users
   - Search by hashtag
   - Advanced search filters
   - Real-time search

6. **Trending Topics**
   - Identify trending topics
   - Show trending hashtags
   - Location-based trending
   - Category-based trending

7. **Notifications**
   - Like notifications
   - Retweet notifications
   - Reply notifications
   - Follow notifications
   - Mention notifications

8. **Direct Messaging**
   - Send direct messages
   - Group messages
   - Media sharing in DMs

### Non-Functional Requirements

1. **Scalability**
   - Support 500M+ active users globally
   - Handle 500M+ tweets per day
   - Handle 200B+ timeline reads per day
   - Support 1M+ tweets per second (peak)
   - 99.99% uptime
   - Multi-region deployment

2. **Performance**
   - Timeline load time: < 2 seconds
   - Tweet creation: < 200ms
   - Search results: < 300ms
   - Like/retweet: < 100ms
   - Real-time updates: < 1 second

3. **Reliability**
   - No tweet loss
   - High availability
   - Graceful degradation
   - Data consistency

4. **Storage**
   - Store billions of tweets
   - Store media files
   - Efficient retrieval
   - Archive old tweets

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
│   API       │  │   Timeline   │  │   Search    │
│   Servers   │  │   Service    │  │   Service   │
│             │  │             │  │             │
│ - Auth     │  │ - Generate  │  │ - Index     │
│ - Tweets   │  │   timeline  │  │   tweets    │
│ - Users    │  │ - Rank      │  │ - Search    │
│ - Media    │  │ - Cache     │  │ - Trends    │
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
│  Tweet      │  │  Timeline   │  │  Notification│
│  Processor  │  │  Generator  │  │  Service    │
│             │  │  Workers    │  │             │
│ - Validate │  │ - Fan-out   │  │ - Generate  │
│ - Store    │  │   tweets    │  │   notifications│
│ - Index    │  │ - Update    │  │ - Send      │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                 │                 │
       └─────────────────┼─────────────────┘
                         │
              ┌──────────▼──────────┐
              │   Database Layer     │
              │                      │
              │  - User DB (MySQL)   │
              │  - Tweet DB          │
              │    (Cassandra)       │
              │  - Timeline Cache   │
              │    (Redis)           │
              │  - Search (ES)       │
              │  - Graph DB          │
              │    (Neo4j)           │
              │  - Media (S3)        │
              └──────────────────────┘
```

### Component Details

1. **API Servers**
   - Handle all HTTP requests
   - Authentication and authorization
   - Request validation
   - Rate limiting

2. **Timeline Service**
   - Generate user timelines
   - Rank tweets
   - Cache timelines
   - Handle timeline updates

3. **Search Service**
   - Index tweets
   - Full-text search
   - User search
   - Hashtag search
   - Trending topics

4. **Tweet Processor**
   - Validate tweets
   - Store tweets
   - Index for search
   - Trigger fan-out

5. **Timeline Generator Workers**
   - Fan-out tweets to followers
   - Update timeline caches
   - Handle high-volume users

6. **Notification Service**
   - Generate notifications
   - Send push notifications
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
    display_name VARCHAR(255),
    bio TEXT,
    profile_image_url VARCHAR(500),
    header_image_url VARCHAR(500),
    location VARCHAR(255),
    website VARCHAR(500),
    birth_date DATE,
    follower_count INT DEFAULT 0,
    following_count INT DEFAULT 0,
    tweet_count INT DEFAULT 0,
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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (follower_id, followee_id),
    FOREIGN KEY (follower_id) REFERENCES users(user_id),
    FOREIGN KEY (followee_id) REFERENCES users(user_id),
    INDEX idx_follower (follower_id),
    INDEX idx_followee (followee_id)
);
```

### Tweet Database (Cassandra)

**tweets**
```sql
CREATE TABLE tweets (
    tweet_id TIMEUUID,
    user_id BIGINT,
    text TEXT,
    media_urls LIST<TEXT>,
    reply_to_tweet_id TIMEUUID,
    retweet_of_tweet_id TIMEUUID,
    quote_tweet_id TIMEUUID,
    like_count COUNTER,
    retweet_count COUNTER,
    reply_count COUNTER,
    quote_count COUNTER,
    created_at TIMESTAMP,
    PRIMARY KEY (user_id, created_at, tweet_id)
) WITH CLUSTERING ORDER BY (created_at DESC, tweet_id DESC);
```

**tweets_by_id**
```sql
CREATE TABLE tweets_by_id (
    tweet_id TIMEUUID PRIMARY KEY,
    user_id BIGINT,
    text TEXT,
    media_urls LIST<TEXT>,
    reply_to_tweet_id TIMEUUID,
    retweet_of_tweet_id TIMEUUID,
    quote_tweet_id TIMEUUID,
    like_count COUNTER,
    retweet_count COUNTER,
    reply_count COUNTER,
    quote_count COUNTER,
    created_at TIMESTAMP,
    INDEX idx_user (user_id)
);
```

**retweets**
```sql
CREATE TABLE retweets (
    tweet_id TIMEUUID,
    user_id BIGINT,
    retweeted_at TIMESTAMP,
    PRIMARY KEY (tweet_id, user_id)
);
```

**user_retweets**
```sql
CREATE TABLE user_retweets (
    user_id BIGINT,
    tweet_id TIMEUUID,
    retweeted_at TIMESTAMP,
    PRIMARY KEY (user_id, retweeted_at, tweet_id)
) WITH CLUSTERING ORDER BY (retweeted_at DESC, tweet_id DESC);
```

**likes**
```sql
CREATE TABLE likes (
    tweet_id TIMEUUID,
    user_id BIGINT,
    liked_at TIMESTAMP,
    PRIMARY KEY (tweet_id, user_id)
);
```

**user_likes**
```sql
CREATE TABLE user_likes (
    user_id BIGINT,
    tweet_id TIMEUUID,
    liked_at TIMESTAMP,
    PRIMARY KEY (user_id, liked_at, tweet_id)
) WITH CLUSTERING ORDER BY (liked_at DESC, tweet_id DESC);
```

**replies**
```sql
CREATE TABLE replies (
    parent_tweet_id TIMEUUID,
    reply_tweet_id TIMEUUID,
    created_at TIMESTAMP,
    PRIMARY KEY (parent_tweet_id, created_at, reply_tweet_id)
) WITH CLUSTERING ORDER BY (created_at ASC, reply_tweet_id ASC);
```

### Timeline Cache (Redis)

**User Timeline**
```
Key: timeline:{user_id}
Value: List of tweet_ids (last 800)
TTL: 1 hour
```

**Tweet Data**
```
Key: tweet:{tweet_id}
Value: JSON tweet data
TTL: 24 hours
```

**User Data**
```
Key: user:{user_id}
Value: JSON user data
TTL: 1 hour
```

**Like Status**
```
Key: like:{tweet_id}:{user_id}
Value: true/false
TTL: 24 hours
```

### Search Database (Elasticsearch)

**tweets_index**
```json
{
  "mappings": {
    "properties": {
      "tweet_id": {"type": "keyword"},
      "user_id": {"type": "long"},
      "text": {"type": "text", "analyzer": "standard"},
      "hashtags": {"type": "keyword"},
      "mentions": {"type": "keyword"},
      "created_at": {"type": "date"},
      "like_count": {"type": "integer"},
      "retweet_count": {"type": "integer"}
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
      "display_name": {"type": "text"},
      "bio": {"type": "text"}
    }
  }
}
```

### Graph Database (Neo4j) - For Social Graph

**Nodes**
- User nodes with properties
- Tweet nodes with properties

**Relationships**
- FOLLOWS: (User)-[:FOLLOWS]->(User)
- LIKED: (User)-[:LIKED]->(Tweet)
- RETWEETED: (User)-[:RETWEETED]->(Tweet)
- REPLIED_TO: (Tweet)-[:REPLIED_TO]->(Tweet)

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
  "display_name": "John Doe"
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

### Tweet APIs

**POST /api/v1/tweets**
```json
Request:
{
  "text": "Hello Twitter! #firsttweet",
  "media_urls": ["https://..."],
  "reply_to_tweet_id": null
}

Response:
{
  "success": true,
  "tweet": {
    "tweet_id": "uuid-here",
    "user_id": 123,
    "text": "Hello Twitter! #firsttweet",
    "created_at": "2024-01-01T12:00:00Z"
  }
}
```

**GET /api/v1/tweets/{tweet_id}**
```json
Response:
{
  "tweet": {
    "tweet_id": "uuid-here",
    "user": {...},
    "text": "...",
    "like_count": 150,
    "retweet_count": 20,
    "reply_count": 10,
    "is_liked": false,
    "is_retweeted": false,
    "created_at": "..."
  }
}
```

**DELETE /api/v1/tweets/{tweet_id}**
```json
Response:
{
  "success": true
}
```

### Timeline APIs

**GET /api/v1/timeline/home**
```json
Query Parameters:
- limit: 20 (default)
- max_id: tweet_id (for pagination)

Response:
{
  "tweets": [
    {
      "tweet_id": "uuid-1",
      "user": {...},
      "text": "...",
      "like_count": 150,
      "retweet_count": 20,
      "is_liked": false,
      "is_retweeted": false,
      "created_at": "..."
    }
  ],
  "next_max_id": "uuid-20"
}
```

**GET /api/v1/timeline/user/{user_id}**
```json
Query Parameters:
- limit: 20
- max_id: tweet_id

Response:
{
  "tweets": [...],
  "next_max_id": "..."
}
```

### Interaction APIs

**POST /api/v1/tweets/{tweet_id}/like**
```json
Response:
{
  "success": true,
  "like_count": 151
}
```

**DELETE /api/v1/tweets/{tweet_id}/like**
```json
Response:
{
  "success": true,
  "like_count": 150
}
```

**POST /api/v1/tweets/{tweet_id}/retweet**
```json
Response:
{
  "success": true,
  "retweet_count": 21
}
```

**POST /api/v1/tweets/{tweet_id}/reply**
```json
Request:
{
  "text": "Great tweet!"
}

Response:
{
  "success": true,
  "reply": {
    "tweet_id": "uuid-here",
    "text": "Great tweet!",
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
    "display_name": "John Doe",
    "bio": "...",
    "follower_count": 1000,
    "following_count": 500,
    "tweet_count": 150,
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

**DELETE /api/v1/users/{user_id}/follow**
```json
Response:
{
  "success": true,
  "is_following": false
}
```

### Search APIs

**GET /api/v1/search/tweets**
```json
Query Parameters:
- q: "search query"
- limit: 20
- max_id: tweet_id

Response:
{
  "tweets": [...],
  "next_max_id": "..."
}
```

**GET /api/v1/search/users**
```json
Query Parameters:
- q: "search query"
- limit: 20

Response:
{
  "users": [...]
}
```

**GET /api/v1/trends**
```json
Query Parameters:
- location: "US" (optional)

Response:
{
  "trends": [
    {
      "name": "#BreakingNews",
      "tweet_count": 50000,
      "url": "..."
    }
  ]
}
```

---

## Timeline Generation

### Timeline Generation Strategies

**Strategy 1: Fan-out on Write (Push Model)**
- When user tweets, push to all followers' timelines
- Fast reads (pre-computed)
- Slow writes (fan-out to millions)
- High storage cost

**Strategy 2: Fan-out on Read (Pull Model)**
- When user reads timeline, fetch from followed users
- Fast writes
- Slow reads (need to merge)
- Lower storage cost

**Strategy 3: Hybrid Approach (Chosen)**
- Fan-out for regular users (push)
- Pull for high-volume users (celebrities)
- Balance between read and write performance

### Fan-out on Write Flow

```
User Creates Tweet
       │
       ▼
Store Tweet in DB
       │
       ▼
Get Followers List
       │
       ├─── Regular Users ───> Push to Timeline Cache
       │
       └─── High-Volume Users ───> Skip (Pull on Read)
```

### Timeline Ranking Algorithm

**Factors:**
1. **Recency** (40%)
   - Newer tweets ranked higher
   - Exponential decay

2. **Engagement** (30%)
   - Likes, retweets, replies
   - Higher engagement = higher rank

3. **Relationship** (20%)
   - Close connections ranked higher
   - Mutual follows
   - Interaction history

4. **Content Quality** (10%)
   - Media content ranked higher
   - Thread tweets
   - Verified accounts

**Formula:**
```
Score = (recency_score * 0.4) + 
        (engagement_score * 0.3) + 
        (relationship_score * 0.2) + 
        (content_quality_score * 0.1)
```

### High-Volume User Handling

**Problem**: Celebrity with 50M followers
- Fan-out to 50M users is expensive
- Storage cost: 50M × tweet_size

**Solution**: Pull Model for High-Volume Users
- Define threshold (e.g., 1M followers)
- Don't fan-out tweets from high-volume users
- Pull their tweets on read
- Merge with pre-computed timeline

**Implementation:**
```python
def get_timeline(user_id):
    # Get pre-computed timeline (regular users)
    timeline = get_cached_timeline(user_id)
    
    # Get tweets from high-volume users
    high_volume_users = get_high_volume_followees(user_id)
    recent_tweets = get_recent_tweets(high_volume_users)
    
    # Merge and rank
    merged_timeline = merge_and_rank(timeline, recent_tweets)
    return merged_timeline
```

---

## Tweet Delivery

### Real-Time Updates

**WebSocket Connection**
- Maintain WebSocket connection
- Push new tweets to followers
- Update timeline in real-time

**Message Queue**
- Publish tweet events to Kafka
- Consumers update timelines
- Push notifications

### Delivery Flow

```
User Creates Tweet
       │
       ▼
Store in Database
       │
       ▼
Publish to Kafka
       │
       ├─── Timeline Service ───> Update Caches
       ├─── Search Service ───> Index Tweet
       ├─── Notification Service ───> Generate Notifications
       └─── WebSocket Service ───> Push to Followers
```

### Timeline Update

**On New Tweet:**
1. Get follower list
2. For each follower:
   - Add tweet_id to timeline cache
   - Push via WebSocket (if connected)
   - Update notification queue

**On Like/Retweet:**
1. Update tweet counters
2. Update timeline ranking
3. Notify tweet author

---

## Search Functionality

### Search Implementation

**Full-Text Search**
- Index tweets in Elasticsearch
- Support hashtag search
- Support mention search
- Support location search

**Search Query**
```json
{
  "query": {
    "multi_match": {
      "query": "search term",
      "fields": ["text", "hashtags", "mentions"],
      "type": "best_fields"
    }
  },
  "sort": [
    {"created_at": "desc"},
    {"_score": "desc"}
  ]
}
```

### Search Ranking

**Factors:**
1. Relevance score (Elasticsearch)
2. Engagement (likes, retweets)
3. Recency
4. Author credibility (verified, followers)

### Real-Time Indexing

- Index tweets immediately after creation
- Update index on edit/delete
- Handle high write volume
- Use bulk indexing

---

## Trending Topics

### Trending Algorithm

**Factors:**
1. **Volume** (40%)
   - Number of tweets with hashtag
   - Growth rate

2. **Velocity** (30%)
   - Rate of increase
   - Spike detection

3. **Recency** (20%)
   - Recent tweets weighted higher
   - Time decay

4. **Diversity** (10%)
   - Unique users
   - Prevent spam

### Implementation

**Track Hashtags**
- Count hashtag mentions per time window
- Calculate growth rate
- Identify spikes
- Rank by score

**Update Frequency**
- Calculate every 15 minutes
- Update trending list
- Cache results

**Database:**
```sql
CREATE TABLE hashtag_trends (
    hashtag TEXT,
    date DATE,
    hour INT,
    count COUNTER,
    unique_users COUNTER,
    PRIMARY KEY (hashtag, date, hour)
);
```

---

## Scalability Considerations

### Horizontal Scaling

1. **API Servers**
   - Stateless design
   - Load balancer distributes requests
   - Auto-scaling

2. **Timeline Service**
   - Shard by user_id
   - Scale workers independently
   - Handle peak loads

3. **Database Sharding**
   - Shard tweets by user_id
   - Shard users by user_id
   - Use consistent hashing

### Vertical Scaling

- Use high-performance databases
- Optimize queries
- Use read replicas
- Partition large tables

### Caching Strategy

- Cache timelines (Redis)
- Cache tweet data (Redis)
- Cache user data (Redis)
- CDN for media files

---

## Caching Strategy

### Cache Layers

1. **Application Cache (Redis)**
   - User timelines: 1 hour TTL
   - Tweet data: 24 hours TTL
   - User data: 1 hour TTL
   - Like/retweet status: 24 hours TTL

2. **CDN Cache**
   - Media files: Long TTL
   - Profile pictures: 1 day TTL
   - Static assets: 1 week TTL

3. **Database Query Cache**
   - Frequently accessed data
   - Expensive queries

### Cache Invalidation

- New tweet: Add to follower timelines
- Like/retweet: Update tweet cache
- User update: Invalidate user cache
- Delete tweet: Remove from timelines

---

## Load Balancing

### Load Balancing Strategy

1. **API Requests**
   - Round-robin or least connections
   - Health checks
   - Session affinity (if needed)

2. **Timeline Requests**
   - Route by user_id
   - Consistent hashing
   - Cache-aware routing

3. **Search Requests**
   - Distribute across search servers
   - Handle peak search times

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
   - Validate tweet length (280 chars)
   - Sanitize content
   - Prevent XSS, SQL injection

### Content Security

1. **Content Moderation**
   - Automated filtering
   - Report system
   - Manual review
   - Block inappropriate content

2. **Spam Prevention**
   - Rate limiting
   - Bot detection
   - Account verification

### Data Security

- Encryption at rest
- Encryption in transit (TLS)
- Secure media storage
- Access controls

---

## Monitoring & Analytics

### Key Metrics

1. **Performance Metrics**
   - Timeline load time (p50, p95, p99)
   - API response time
   - Tweet creation time
   - Search latency

2. **System Metrics**
   - CPU, memory, disk usage
   - Database query performance
   - Cache hit rate
   - Queue depth

3. **Business Metrics**
   - Daily active users (DAU)
   - Tweets per day
   - Likes per day
   - Retweets per day
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

**Tweets**
- Average tweet: 200 bytes (text)
- 500M tweets/day = 100GB/day = 36.5TB/year
- With replication (3x): ~110TB/year
- Per user: ~73KB/year

**Media**
- Average media: 2MB
- 10% tweets have media = 50M media/day
- 100TB/day = 36.5PB/year
- With compression: ~18PB/year

**Timeline Cache**
- 500M users × 800 tweets × 16 bytes = 6.4TB
- With replication: ~20TB

**Database**
- Tweet metadata: ~1KB/tweet = 500GB/day = 182.5TB/year
- User data: ~2KB/user = 1TB for 500M users

### Compute Estimates

**API Servers**
- 200B timeline reads/day = ~2.3M reads/second
- Each server handles 10K requests/second
- Need 230 servers (with redundancy: ~350)

**Timeline Workers**
- 500M tweets/day = ~5,800 tweets/second
- Average 100 followers = 580K fan-outs/second
- Each worker handles 1K fan-outs/second
- Need 580 workers (with overhead: ~900)

---

## Technology Stack

### Backend
- **Language**: Java (Spring Boot) or Scala
- **Message Queue**: Kafka
- **Database**: 
  - MySQL (user data)
  - Cassandra (tweets)
  - Redis (cache)
  - Elasticsearch (search)
  - Neo4j (social graph)
- **Object Storage**: S3, Azure Blob, or GCS
- **CDN**: CloudFront, Cloudflare

### Frontend
- **Mobile**: Native (Swift, Kotlin) or React Native
- **Web**: React or Next.js
- **WebSocket**: For real-time updates

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

### Timeline Cache Failure

- Fallback to database
- Rebuild cache
- Slightly slower but functional

### High Load

- Rate limiting
- Graceful degradation
- Return fewer tweets
- Prioritize popular content

---

## Trade-offs & Design Decisions

### 1. Timeline: Push vs Pull vs Hybrid

**Chosen: Hybrid**
- Push for regular users (fast reads)
- Pull for high-volume users (cost-effective)
- Balance between performance and cost

**Trade-off**: More complex implementation

### 2. Database: SQL vs NoSQL

**Chosen: Hybrid**
- MySQL for user data (ACID, relationships)
- Cassandra for tweets (high write throughput)
- Elasticsearch for search

**Trade-off**: More complex architecture

### 3. Real-Time: WebSocket vs Polling

**Chosen: WebSocket**
- Lower latency
- More efficient
- Better user experience

**Trade-off**: More complex connection management

### 4. Search: Database vs Search Engine

**Chosen: Elasticsearch**
- Better full-text search
- Better ranking
- Scalable

**Trade-off**: Additional infrastructure

### 5. Media Storage: Database vs Object Storage

**Chosen: Object Storage**
- Cost-effective for large files
- Better scalability
- CDN integration

**Trade-off**: Additional service to manage

---

## Interview Discussion Points

### Key Topics to Discuss

1. **Timeline Generation**
   - Push vs Pull model
   - How to handle high-volume users?
   - How to rank tweets?

2. **Fan-out Optimization**
   - How to optimize fan-out?
   - How to handle millions of followers?
   - Batch processing strategies

3. **Search Scalability**
   - How to handle real-time search?
   - How to rank search results?
   - How to handle high search volume?

4. **Trending Topics**
   - How to identify trends?
   - How to prevent spam?
   - How to handle location-based trends?

5. **Media Handling**
   - How to handle video uploads?
   - How to optimize storage?
   - How to handle peak upload times?

6. **Real-Time Updates**
   - How to push updates to users?
   - How to handle connection failures?
   - How to scale WebSocket connections?

7. **Notification System**
   - How to batch notifications?
   - How to prevent notification spam?
   - How to personalize notifications?

8. **Data Consistency**
   - How to ensure consistency?
   - How to handle eventual consistency?
   - How to handle counter updates?

### Common Follow-up Questions

- How would you handle tweet editing?
- How to implement quote tweets?
- How to handle thread tweets?
- How to optimize for low-bandwidth users?
- How to handle spam accounts?
- How to implement verified accounts?
- How to handle tweet deletion?
- How to implement bookmarks?

---

## Additional Considerations

### Tweet Threading

- Link replies to parent tweet
- Display as conversation thread
- Store thread relationships
- Optimize thread loading

### Quote Tweets

- Store reference to original tweet
- Display both tweets
- Track quote count
- Rank by engagement

### Media Attachments

- Support images, videos, GIFs
- Process and optimize media
- Generate thumbnails
- Support multiple media per tweet

### Direct Messaging

- Similar to WhatsApp design
- WebSocket for real-time
- Store messages in database
- Support group messages

---

*This document provides a comprehensive system design for Twitter. Adjustments may be needed based on specific requirements and constraints.*

