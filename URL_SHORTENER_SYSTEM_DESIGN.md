# URL Shortener System Design Document

## Table of Contents
1. [Overview](#overview)
2. [Requirements](#requirements)
3. [System Architecture](#system-architecture)
4. [Database Design](#database-design)
5. [API Design](#api-design)
6. [Scalability Considerations](#scalability-considerations)
7. [Caching Strategy](#caching-strategy)
8. [Load Balancing](#load-balancing)
9. [Security](#security)
10. [Monitoring & Analytics](#monitoring--analytics)
11. [Deployment Strategy](#deployment-strategy)
12. [Capacity Planning](#capacity-planning)
13. [Failure Scenarios & Handling](#failure-scenarios--handling)
14. [Trade-offs & Design Decisions](#trade-offs--design-decisions)
15. [Interview Discussion Points](#interview-discussion-points)

---

## Overview

A URL shortener service that converts long URLs into short, manageable links. The system should handle billions of URLs, support high read/write throughput, and provide analytics on link usage.

**Key Features:**
- Shorten long URLs to compact links
- Redirect short URLs to original URLs
- Track click analytics
- Custom alias support
- Expiration dates for links
- User authentication and link management

---

## Requirements

### Functional Requirements
1. **URL Shortening**
   - Convert long URLs to short codes (e.g., `bit.ly/abc123`)
   - Support custom aliases
   - Validate URL format
   - Handle duplicate URLs (return existing short URL)

2. **URL Redirection**
   - Redirect short URLs to original URLs
   - Handle expired links
   - Track redirect events for analytics

3. **User Management**
   - User registration and authentication
   - Link ownership and management
   - Bulk operations (import/export)

4. **Analytics**
   - Click count per link
   - Geographic distribution
   - Referrer tracking
   - Time-series data

### Non-Functional Requirements
1. **Scalability**
   - Handle 100M+ URLs
   - Support 100K+ writes per second
   - Support 1M+ reads per second
   - 99.9% uptime

2. **Performance**
   - URL shortening: < 100ms latency
   - URL redirection: < 50ms latency
   - 99th percentile latency < 200ms

3. **Availability**
   - Multi-region deployment
   - Automatic failover
   - Data replication

4. **Durability**
   - No data loss
   - Backup and recovery mechanisms

---

## System Architecture

### High-Level Architecture

```
┌─────────────┐
│   Client    │
│  (Browser)  │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────────────┐
│           Load Balancer (CDN)                   │
└──────┬──────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────┐
│         API Gateway / Application Layer         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │   API    │  │   API    │  │   API    │      │
│  │ Server 1 │  │ Server 2 │  │ Server N │      │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘      │
└───────┼─────────────┼─────────────┼────────────┘
        │             │             │
        ▼             ▼             ▼
┌─────────────────────────────────────────────────┐
│              Caching Layer                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │  Redis   │  │  Redis   │  │  Redis   │      │
│  │ Cluster  │  │ Cluster  │  │ Cluster  │      │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘      │
└───────┼─────────────┼─────────────┼────────────┘
        │             │             │
        ▼             ▼             ▼
┌─────────────────────────────────────────────────┐
│            Database Layer                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │   MySQL  │  │   MySQL  │  │   MySQL  │      │
│  │ Primary  │  │ Replica  │  │ Replica  │      │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘      │
└───────┼─────────────┼─────────────┼────────────┘
        │             │             │
        ▼             ▼             ▼
┌─────────────────────────────────────────────────┐
│         Analytics & Storage                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ ClickHouse│  │  S3/GCS │  │  Kafka  │      │
│  │ (Analytics)│ │ (Backup) │ │ (Events)│      │
│  └──────────┘  └──────────┘  └──────────┘      │
└─────────────────────────────────────────────────┘
```

### Component Details

#### 1. Application Layer
- **Technology**: Python (FastAPI/Flask) or Go/Java
- **Responsibilities**:
  - Handle HTTP requests
  - URL validation and sanitization
  - Business logic
  - Authentication/authorization
- **Scaling**: Horizontal scaling with stateless servers

#### 2. Caching Layer
- **Technology**: Redis Cluster
- **Responsibilities**:
  - Cache frequently accessed short URLs
  - Store hot data for fast reads
  - Rate limiting
  - Session management
- **Strategy**: 
  - Cache popular URLs (top 20%)
  - TTL: 24 hours for redirects, 1 hour for metadata

#### 3. Database Layer
- **Technology**: MySQL/PostgreSQL (sharded) or NoSQL (Cassandra/DynamoDB)
- **Responsibilities**:
  - Store URL mappings
  - User data
  - Link metadata
- **Sharding Strategy**: Shard by short code hash or user ID

#### 4. Analytics Layer
- **Technology**: ClickHouse/TimescaleDB or BigQuery
- **Responsibilities**:
  - Store click events
  - Aggregate analytics data
  - Generate reports

---

## Database Design

### Primary Database Schema

#### URLs Table
```sql
CREATE TABLE urls (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    short_code VARCHAR(10) UNIQUE NOT NULL,
    original_url TEXT NOT NULL,
    user_id BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NULL,
    is_active BOOLEAN DEFAULT TRUE,
    click_count BIGINT DEFAULT 0,
    INDEX idx_short_code (short_code),
    INDEX idx_user_id (user_id),
    INDEX idx_expires_at (expires_at)
) ENGINE=InnoDB;
```

#### Users Table
```sql
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_email (email)
) ENGINE=InnoDB;
```

#### Clicks Table (Analytics)
```sql
CREATE TABLE clicks (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    short_code VARCHAR(10) NOT NULL,
    clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent TEXT,
    referrer TEXT,
    country VARCHAR(2),
    city VARCHAR(100),
    INDEX idx_short_code_time (short_code, clicked_at),
    INDEX idx_clicked_at (clicked_at)
) ENGINE=InnoDB;
```

### Database Sharding Strategy

**Shard by Short Code Hash:**
- Hash short code → determine shard
- Example: `hash(short_code) % num_shards`
- Enables distributed storage and parallel queries

**Alternative: Shard by User ID**
- For user-specific queries
- Better for user dashboard queries

---

## API Design

### RESTful API Endpoints

#### 1. Shorten URL
```
POST /api/v1/shorten
Content-Type: application/json

Request:
{
    "url": "https://example.com/very/long/url",
    "custom_alias": "optional-alias",
    "expires_in_days": 30
}

Response:
{
    "short_url": "https://short.ly/abc123",
    "original_url": "https://example.com/very/long/url",
    "expires_at": "2024-02-15T10:30:00Z"
}
```

#### 2. Redirect (GET)
```
GET /{short_code}
Response: 302 Redirect to original URL
```

#### 3. Get URL Details
```
GET /api/v1/urls/{short_code}
Response:
{
    "short_code": "abc123",
    "original_url": "https://example.com/very/long/url",
    "click_count": 1234,
    "created_at": "2024-01-15T10:30:00Z",
    "expires_at": "2024-02-15T10:30:00Z"
}
```

#### 4. Get Analytics
```
GET /api/v1/urls/{short_code}/analytics?start_date=2024-01-01&end_date=2024-01-31
Response:
{
    "total_clicks": 1234,
    "clicks_by_date": [
        {"date": "2024-01-01", "clicks": 100},
        {"date": "2024-01-02", "clicks": 150}
    ],
    "clicks_by_country": [
        {"country": "US", "clicks": 800},
        {"country": "UK", "clicks": 434}
    ],
    "top_referrers": [...]
}
```

#### 5. Delete URL
```
DELETE /api/v1/urls/{short_code}
Response: 204 No Content
```

---

## Data Flow Diagrams

### URL Shortening Flow

```
User Request (POST /api/v1/shorten)
    │
    ▼
API Gateway (Rate Limiting, Auth)
    │
    ▼
Application Server
    │
    ├─ Validate URL
    ├─ Check if URL already shortened (optional)
    │
    ▼
Generate Short Code
    │
    ├─ Hash-based: hash(url + timestamp + salt)
    ├─ Convert to Base62
    └─ Check collision in cache
    │
    ▼
Database Write (Sharded by short_code hash)
    │
    ├─ Write to primary shard
    ├─ Async replication to replicas
    │
    ▼
Cache Write (Redis)
    │
    ├─ Cache short_code → original_url
    └─ TTL: 24 hours
    │
    ▼
Analytics Event (Kafka)
    │
    └─ Async: Log creation event
    │
    ▼
Return Short URL to User
```

### URL Redirection Flow

```
User Request (GET /{short_code})
    │
    ▼
CDN (Check Cache)
    │
    ├─ Cache Hit (80%) → Return Redirect (10-20ms)
    │
    └─ Cache Miss (20%) → Continue
        │
        ▼
    API Gateway
        │
        ▼
    Application Server
        │
        ▼
    Redis Cache (Check)
        │
        ├─ Cache Hit (15%) → Return Redirect (1-2ms)
        │
        └─ Cache Miss (5%) → Continue
            │
            ▼
        Database Query (Sharded)
            │
            ├─ Determine shard (hash(short_code) % num_shards)
            ├─ Query shard (read replica)
            │
            ▼
        Update Cache
            │
            ├─ Write to Redis
            └─ Write to CDN (optional)
            │
            ▼
        Analytics Event (Kafka)
            │
            └─ Async: Log click event
            │
            ▼
        Return Redirect (302) to Original URL
```

### Analytics Processing Flow

```
Click Event
    │
    ▼
Kafka Topic (clicks)
    │
    ├─ Real-time Stream (Flink/Spark Streaming)
    │   └─ Aggregate → ClickHouse (Last 24 hours)
    │
    └─ Batch Processing (Spark)
        └─ Aggregate → ClickHouse (Historical)
            │
            ▼
        Analytics API
            │
            └─ Serve aggregated data
```

---

## Scalability Considerations

### 1. Short Code Generation

**Base62 Encoding:**
- Characters: `[0-9a-zA-Z]` = 62 characters
- 6 characters = 62^6 = 56.8 billion combinations
- 7 characters = 62^7 = 3.5 trillion combinations

**Generation Strategy:**
- **Option A: Counter-based**
  - Use distributed counter (Redis/Zookeeper)
  - Convert counter to base62
  - Pros: Sequential, predictable
  - Cons: Single point of failure, requires coordination

- **Option B: Hash-based**
  - Hash original URL + timestamp
  - Take first 6-7 characters
  - Handle collisions (append random chars)
  - Pros: No coordination needed
  - Cons: Potential collisions

- **Option C: Pre-generated Pools**
  - Pre-generate short codes in batches
  - Store in database/Redis
  - Workers consume from pool
  - Pros: Fast, no collisions
  - Cons: Requires pool management

**Recommended: Hybrid Approach**
- Use hash-based for speed
- Check uniqueness in database
- If collision, append random suffix

### 2. Database Scaling

**Read Scaling:**
- Read replicas for read-heavy operations
- Connection pooling
- Query optimization and indexing

**Write Scaling:**
- Database sharding
- Write-through caching
- Batch writes for analytics

**Sharding Implementation:**
```python
def get_shard(short_code: str, num_shards: int) -> int:
    hash_value = hash(short_code)
    return hash_value % num_shards
```

### 3. Caching Strategy

**Multi-Level Caching:**

1. **L1: Application Cache (In-Memory)**
   - Cache hot URLs in application memory
   - LRU eviction policy
   - TTL: 5 minutes

2. **L2: Redis Cache**
   - Distributed cache
   - Cache popular URLs
   - TTL: 24 hours for redirects
   - Cache-aside pattern

**Cache Keys:**
- `url:{short_code}` → original URL
- `metadata:{short_code}` → URL metadata
- `analytics:{short_code}` → aggregated analytics

### 4. Read/Write Optimization

**Write Path:**
1. Validate URL
2. Generate short code
3. Check cache for existing mapping
4. Write to database (async if possible)
5. Update cache
6. Return short URL

**Read Path (Redirect):**
1. Check L1 cache
2. Check Redis cache
3. Query database (if cache miss)
4. Update cache
5. Redirect to original URL

**Optimization:**
- 80% of traffic is reads (redirects)
- Cache popular URLs aggressively
- Use CDN for static assets
- Database connection pooling

---

## Caching Strategy

### Cache Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  Application    │
│  (L1 Cache)     │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Redis Cluster  │
│  (L2 Cache)     │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│    Database     │
└─────────────────┘
```

### Cache Patterns

1. **Cache-Aside (Lazy Loading)**
   - Application checks cache first
   - On miss, fetch from DB and populate cache
   - Used for: URL redirects, metadata

2. **Write-Through**
   - Write to cache and DB simultaneously
   - Used for: New URL creation

3. **Write-Behind (Write-Back)**
   - Write to cache immediately
   - Async write to DB
   - Used for: Analytics events

### Cache Invalidation

- **TTL-based**: Automatic expiration
- **Event-based**: Invalidate on URL deletion/update
- **LRU eviction**: For memory-constrained scenarios

---

## Load Balancing

### Load Balancer Configuration

**Layer 4 (TCP) Load Balancer:**
- Distribute traffic at transport layer
- Fast, low latency
- Used for: Initial request routing

**Layer 7 (HTTP) Load Balancer:**
- Content-aware routing
- SSL termination
- Used for: API requests

### Load Balancing Algorithms

1. **Round Robin**: Equal distribution
2. **Least Connections**: Route to server with fewest connections
3. **IP Hash**: Consistent routing based on client IP
4. **Weighted Round Robin**: Based on server capacity

### Health Checks

- **Endpoint**: `/health`
- **Interval**: 10 seconds
- **Timeout**: 5 seconds
- **Unhealthy threshold**: 3 consecutive failures

---

## Security

### 1. URL Validation
- Whitelist allowed protocols (http, https)
- Block malicious URLs (phishing, malware)
- Rate limiting per IP/user
- URL length limits

### 2. Authentication & Authorization
- JWT tokens for API authentication
- OAuth 2.0 for third-party integration
- Role-based access control (RBAC)

### 3. Rate Limiting
- **Per IP**: 100 requests/minute
- **Per User**: 1000 requests/minute
- **Per Endpoint**: Different limits for different endpoints
- Implementation: Redis-based sliding window

### 4. DDoS Protection
- CDN with DDoS mitigation (Cloudflare/AWS Shield)
- Rate limiting at edge
- IP blacklisting

### 5. Data Privacy
- Encrypt sensitive data at rest
- HTTPS for all communications
- GDPR compliance (user data deletion)

### 6. Short Code Security
- Prevent enumeration attacks (random, non-sequential)
- Custom alias validation (prevent abuse)
- Expiration for sensitive links

---

## Monitoring & Analytics

### Key Metrics

**System Metrics:**
- Request rate (QPS)
- Latency (p50, p95, p99)
- Error rate
- Cache hit rate
- Database connection pool usage

**Business Metrics:**
- URLs created per day
- Redirects per day
- Active users
- Top URLs by clicks

### Monitoring Tools

- **APM**: New Relic, Datadog, or Prometheus + Grafana
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **Alerting**: PagerDuty, Opsgenie

### Analytics Pipeline

```
Click Event → Kafka → Stream Processor → ClickHouse → Dashboard
```

**Event Schema:**
```json
{
    "short_code": "abc123",
    "timestamp": "2024-01-15T10:30:00Z",
    "ip_address": "192.168.1.1",
    "user_agent": "Mozilla/5.0...",
    "referrer": "https://google.com",
    "country": "US",
    "city": "San Francisco"
}
```

### Error Handling & Retry Logic

**Database Connection Failure:**
```python
@retry(max_attempts=3, backoff=exponential_backoff(base=1, max=10))
def resolve_url(short_code):
    try:
        # Try primary database
        return primary_db.get_url(short_code)
    except DatabaseConnectionError:
        # Failover to replica
        return replica_db.get_url(short_code)
    except Exception as e:
        # Log error and return cached value if available
        logger.error(f"Failed to resolve {short_code}: {e}")
        cached = cache.get(f"url:{short_code}")
        if cached:
            return cached
        raise ServiceUnavailableError("Service temporarily unavailable")
```

**Cache Failure Handling:**
```python
def resolve_url_with_fallback(short_code):
    # Try Redis cache
    try:
        url = redis_cache.get(f"url:{short_code}")
        if url:
            return url
    except RedisError:
        logger.warning("Redis cache unavailable, using fallback")
    
    # Fallback to local cache
    url = local_cache.get(short_code)
    if url:
        return url
    
    # Last resort: database query
    return database.get_url(short_code)
```

**Rate Limiting Response:**
```python
@rate_limit(per_ip=100, per_minute=60)
def shorten_url(original_url):
    if rate_limit_exceeded():
        return {
            "error": "Rate limit exceeded",
            "retry_after": 60,
            "limit": 100,
            "remaining": 0
        }, 429
    # Process request...
```

### Monitoring & Alerting Strategy

**Key Metrics to Monitor:**

1. **System Health:**
   - Request rate (QPS)
   - Error rate (4xx, 5xx)
   - Latency (p50, p95, p99)
   - Database connection pool usage
   - Cache hit rate

2. **Business Metrics:**
   - URLs created per minute
   - Redirects per minute
   - Top URLs by clicks
   - Active users
   - Custom alias usage

3. **Infrastructure:**
   - Database replication lag
   - Cache memory usage
   - Queue depth (Kafka)
   - Disk usage

**Alerting Thresholds:**

| Metric | Warning | Critical | Action |
|--------|---------|---------|--------|
| **Error Rate** | > 1% | > 5% | Scale up, investigate |
| **Latency (p99)** | > 200ms | > 500ms | Check cache, DB |
| **Cache Hit Rate** | < 75% | < 60% | Check cache health |
| **Database CPU** | > 70% | > 90% | Scale read replicas |
| **Queue Depth** | > 10K | > 100K | Scale consumers |

**Example Alert Configuration:**
```yaml
alerts:
  - name: high_error_rate
    condition: error_rate > 0.05
    duration: 5m
    action: page_oncall
    severity: critical
  
  - name: low_cache_hit_rate
    condition: cache_hit_rate < 0.60
    duration: 10m
    action: notify_team
    severity: warning
  
  - name: database_replication_lag
    condition: replication_lag > 10s
    duration: 5m
    action: page_oncall
    severity: critical
```

---

## Deployment Strategy

### Infrastructure

**Cloud Provider**: AWS/GCP/Azure

**Components:**
- **Compute**: Kubernetes (EKS/GKE) or EC2 Auto Scaling Groups
- **Database**: RDS (MySQL) or Cloud SQL with read replicas
- **Cache**: ElastiCache (Redis) or Memorystore
- **CDN**: CloudFront or Cloud CDN
- **Load Balancer**: Application Load Balancer (ALB) or Cloud Load Balancing

### Multi-Region Deployment

```
Region 1 (US-East)          Region 2 (EU-West)
┌─────────────┐            ┌─────────────┐
│   Primary   │◄──────────►│   Replica   │
│   Database  │            │   Database  │
└─────────────┘            └─────────────┘
       ▲                          ▲
       │                          │
┌──────┴──────┐            ┌──────┴──────┐
│  App Servers│            │  App Servers│
└─────────────┘            └─────────────┘
```

**Benefits:**
- Reduced latency (geographic proximity)
- Disaster recovery
- High availability

### CI/CD Pipeline

```
Code Commit → CI (Tests) → Build Docker Image → 
Deploy to Staging → Integration Tests → 
Deploy to Production (Blue-Green Deployment)
```

---

## Capacity Planning

### Storage Estimates

**URLs Table:**
- 100M URLs × 500 bytes = 50 GB
- With indexes: ~150 GB
- Growth: 1M URLs/day = 500 MB/day

**Clicks Table:**
- 1B clicks × 200 bytes = 200 GB/year
- Partition by month for efficient queries

**Total Storage (Year 1):**
- URLs: 150 GB
- Clicks: 200 GB
- Users: 10 GB
- **Total: ~360 GB**

### Compute Requirements

**Write Load:**
- 100K writes/second
- Each write: ~10ms processing
- Required servers: 100K / (1000/10) = 1000 servers
- With 50% utilization: ~500 servers

**Read Load:**
- 1M reads/second
- 80% cache hit rate
- Cache misses: 200K/second
- Each read: ~5ms processing
- Required servers: 200K / (1000/5) = 1000 servers
- With 50% utilization: ~500 servers

**Total: ~1000 servers** (can be optimized with better caching)

**Optimization with Better Caching:**
- 90% cache hit rate (vs 80%): 1M × 10% = 100K DB queries/sec
- Required servers: 100K / (1000/5) = 500 servers
- **Savings**: 50% reduction in servers

### Network Bandwidth

**Outbound (Redirects):**
- 1M redirects/second × 1KB = 1 GB/second = 8 Gbps
- With CDN caching (80% hit rate): 8 Gbps × 20% = 1.6 Gbps from origin

**Inbound (API Requests):**
- 100K requests/second × 2KB = 200 MB/second = 1.6 Gbps

**Total: ~3.2 Gbps** (with CDN optimization)

### Scaling Strategy by URL Count

**Phase 1: 0-1M URLs (MVP)**
- Single MySQL database
- Single Redis instance
- Basic caching
- **Cost**: ~$500/month
- **Servers**: 2-3 servers

**Phase 2: 1M-10M URLs**
- MySQL with 2 read replicas
- Redis cluster (3 nodes)
- CDN for static assets
- **Cost**: ~$2K/month
- **Servers**: 10-20 servers

**Phase 3: 10M-100M URLs**
- MySQL sharding (4 shards)
- Multiple Redis clusters
- CDN with caching
- Analytics pipeline (Kafka + ClickHouse)
- **Cost**: ~$10K/month
- **Servers**: 50-100 servers

**Phase 4: 100M-1B URLs**
- MySQL sharding (16+ shards)
- Multiple Redis clusters per region
- Multi-region deployment
- Advanced analytics
- **Cost**: ~$50K/month
- **Servers**: 200-500 servers

**Scaling Bottlenecks & Solutions:**

| Bottleneck | Solution | Impact |
|------------|----------|--------|
| **Database Writes** | Sharding, async writes | 10x improvement |
| **Database Reads** | Read replicas, caching | 100x improvement |
| **Cache Capacity** | Redis cluster, eviction | 10x improvement |
| **Analytics Load** | Batch processing, sampling | 20x improvement |
| **Short Code Generation** | Hash-based, parallel | 100x improvement |

---

## Technology Stack Recommendations

### Option 1: Cloud-Native (AWS)
- **Compute**: ECS/EKS (Docker containers)
- **Database**: RDS MySQL with read replicas
- **Cache**: ElastiCache Redis
- **CDN**: CloudFront
- **Analytics**: Kinesis + Redshift or Kinesis + S3 + Athena
- **Monitoring**: CloudWatch + X-Ray

### Option 2: Kubernetes (Multi-Cloud)
- **Orchestration**: Kubernetes (EKS/GKE/AKS)
- **Database**: Vitess (MySQL sharding) or CockroachDB
- **Cache**: Redis Cluster
- **CDN**: Cloudflare or Fastly
- **Analytics**: Kafka + ClickHouse
- **Monitoring**: Prometheus + Grafana

### Option 3: Serverless (Cost-Effective)
- **Compute**: AWS Lambda / Google Cloud Functions
- **Database**: DynamoDB or Firestore
- **Cache**: ElastiCache Redis
- **CDN**: CloudFront
- **Analytics**: Kinesis Firehose + S3 + Athena
- **Monitoring**: CloudWatch

---

## Future Enhancements

1. **QR Code Generation**: Generate QR codes for short URLs
2. **Bulk Operations**: Import/export URLs via CSV
3. **Custom Domains**: Allow users to use their own domains
4. **A/B Testing**: Test different destination URLs
5. **Link Expiration**: Automatic expiration with notifications
6. **Password Protection**: Require password for sensitive links
7. **Geographic Targeting**: Redirect based on user location
8. **Mobile App**: Native iOS/Android apps
9. **Browser Extension**: Quick shortening from browser
10. **API Rate Limits**: Tiered plans (free, pro, enterprise)

---

## Conclusion

This system design provides a scalable, high-performance URL shortener capable of handling billions of URLs and millions of requests per second. Key design decisions:

1. **Sharded database** for horizontal scaling
2. **Multi-level caching** for fast reads
3. **Asynchronous analytics** to avoid blocking redirects
4. **Multi-region deployment** for global availability
5. **CDN integration** for reduced latency

The architecture can be incrementally scaled and optimized based on actual usage patterns and requirements.

---

## Failure Scenarios & Handling

### 1. Database Failure

**Scenario:** Primary MySQL database fails or entire database cluster goes down.

**Impact:** 
- **Write Operations**: Cannot create new short URLs
- **Read Operations**: Cannot resolve short URLs to original URLs

**Mitigation:**
- **Read Replicas**: Automatic failover to read replicas for read operations
- **Multi-Region Replication**: Cross-region replication for disaster recovery
- **Circuit Breaker**: Fail gracefully, serve from cache
- **Degraded Mode**: 
  - Writes: Queue requests, process when DB recovers
  - Reads: Serve from cache (80% cache hit rate means most requests succeed)

**Recovery Strategy:**
```python
class DatabaseFailover:
    def shorten_url(self, original_url):
        try:
            return self.primary_db.create_short_url(original_url)
        except DatabaseError:
            # Queue for async processing
            self.queue.put({
                'action': 'shorten',
                'url': original_url,
                'timestamp': time.now()
            })
            # Return temporary response
            return {'status': 'queued', 'message': 'Will be processed shortly'}
    
    def resolve_url(self, short_code):
        # Try cache first (handles 80% of requests)
        cached = self.cache.get(f"url:{short_code}")
        if cached:
            return cached
        
        try:
            url = self.primary_db.get_url(short_code)
            self.cache.set(f"url:{short_code}", url, ttl=86400)
            return url
        except DatabaseError:
            # Try read replica
            try:
                url = self.replica_db.get_url(short_code)
                self.cache.set(f"url:{short_code}", url, ttl=86400)
                return url
            except DatabaseError:
                # Last resort: serve from cache even if expired
                return self.cache.get(f"url:{short_code}") or None
```

**Recovery Time:** < 30 seconds (automatic failover)

### 2. Cache Failure (Redis Down)

**Scenario:** Redis cluster fails or becomes unavailable.

**Impact:** 
- Increased database load (100% cache miss rate)
- Higher latency (database queries slower than cache)
- Potential database overload

**Mitigation:**
- **Redis Cluster**: Multiple nodes, automatic failover
- **Local Cache**: Application-level in-memory cache as backup
- **Database Read Scaling**: Scale read replicas to handle increased load
- **Rate Limiting**: Reduce rate limits temporarily to prevent overload
- **Graceful Degradation**: Accept higher latency (50ms → 200ms)

**Recovery:** Automatic failover within Redis cluster (< 5 seconds)

**Impact Calculation:**
- Normal: 1M reads/sec, 80% cache hit = 200K DB queries/sec
- Cache Down: 1M reads/sec, 0% cache hit = 1M DB queries/sec (5x increase)
- **Solution**: Scale read replicas 5x, or accept higher latency

### 3. Short Code Collision

**Scenario:** Hash-based generation produces duplicate short codes.

**Impact:** 
- URL resolution returns wrong URL
- Data integrity issue

**Mitigation:**
- **Collision Detection**: Check database before returning short code
- **Retry Logic**: If collision detected, append random suffix and retry
- **Base62 Length**: Use 7 characters (3.5 trillion combinations) instead of 6
- **Database Unique Constraint**: Enforce uniqueness at database level

**Implementation:**
```python
def generate_short_code(original_url, max_retries=3):
    for attempt in range(max_retries):
        # Generate base code
        code = hash_to_base62(original_url + str(time.now()) + str(attempt))
        
        # Check for collision
        if not db.exists(code):
            return code
        
        # Collision detected, append random suffix
        code += random_base62(2)  # Add 2 random characters
    
    raise Exception("Failed to generate unique short code")
```

### 4. Analytics Pipeline Failure

**Scenario:** Kafka/ClickHouse fails, analytics events cannot be processed.

**Impact:** 
- Analytics data loss
- No impact on core functionality (URL shortening/redirection)

**Mitigation:**
- **Event Buffering**: Buffer events in application memory if Kafka unavailable
- **Retry Logic**: Retry failed events with exponential backoff
- **Dual Write**: Write to both Kafka and S3 (backup)
- **Graceful Degradation**: Continue core functionality, log events locally

**Recovery:** Replay events from S3 backup when pipeline recovers

### 5. DDoS Attack

**Scenario:** Massive traffic spike from malicious sources.

**Impact:** 
- Service degradation
- Legitimate users cannot access service
- Potential database overload

**Mitigation:**
- **CDN Protection**: Cloudflare/AWS Shield at edge
- **Rate Limiting**: 
  - Per IP: 100 requests/minute
  - Per User: 1000 requests/minute
- **IP Blacklisting**: Block malicious IPs
- **Auto-Scaling**: Scale up to handle legitimate traffic
- **Traffic Analysis**: ML-based anomaly detection

**Example Rate Limiting:**
```python
@rate_limit(per_ip=100, per_minute=60)
def resolve_url(short_code):
    # Rate limiting applied at API gateway level
    return resolve_short_code(short_code)
```

### 6. Region-Wide Outage

**Scenario:** Entire AWS region fails.

**Impact:** All services in that region unavailable.

**Mitigation:**
- **Multi-Region Active-Active**: All regions serve traffic
- **DNS Failover**: Route53 automatic failover to healthy regions
- **Data Replication**: Data replicated across regions
- **Cross-Region Load Balancing**: Distribute traffic across regions

**Recovery Time:** < 1 minute (DNS failover + health checks)

### 7. Short Code Exhaustion

**Scenario:** All possible short codes are used (extremely unlikely with 7 characters).

**Impact:** Cannot generate new short codes.

**Mitigation:**
- **Code Length**: Use 7 characters (3.5 trillion combinations)
- **Code Recycling**: Reuse expired/deleted codes
- **Length Extension**: Increase to 8 characters if needed
- **Monitoring**: Alert when code usage exceeds threshold

**Calculation:**
- 7 characters: 62^7 = 3.5 trillion combinations
- At 100K writes/sec: 3.5 trillion / (100K × 86400) = 405 days to exhaust
- **Solution**: Monitor and extend length before exhaustion

### 8. Hot URL Problem

**Scenario:** Single URL receives massive traffic (viral link).

**Impact:** 
- Cache hotspot
- Database hotspot
- Potential service degradation

**Mitigation:**
- **CDN Caching**: Cache at CDN level (handles most traffic)
- **Cache Replication**: Multiple cache nodes
- **Database Read Replicas**: Distribute reads across replicas
- **Pre-warming**: Pre-cache viral URLs
- **Monitoring**: Alert on traffic spikes

---

## Trade-offs & Design Decisions

### 1. Short Code Generation: Hash vs Counter vs Pre-generated

**Decision:** Hybrid approach (hash-based with collision detection).

**Trade-offs:**

| Approach | Pros | Cons | Use Case |
|----------|------|------|----------|
| **Hash-based** | No coordination, fast | Potential collisions | High throughput |
| **Counter-based** | No collisions, sequential | Single point of failure | Low-medium throughput |
| **Pre-generated** | Fastest, no collisions | Pool management | Very high throughput |

**Why Hash-Based:**
- **Scalability**: No coordination needed, works across multiple servers
- **Speed**: O(1) generation, no database lookup needed
- **Collision Handling**: Rare with 7 characters, easy to detect and retry

**Alternative Considered:** Counter-based with Redis
- **Pros**: No collisions, predictable
- **Cons**: Redis becomes bottleneck, single point of failure
- **Decision**: Hash-based for better scalability

**Collision Probability:**
- 6 characters: 62^6 = 56.8 billion combinations
- At 100K URLs: Collision probability = 0.0001% (very low)
- **Solution**: Use 7 characters for even lower probability

### 2. Database Choice: MySQL vs NoSQL

**Decision:** MySQL (sharded) for URL mappings, NoSQL (Cassandra) for analytics.

**Trade-offs:**

| Aspect | MySQL | Cassandra/DynamoDB |
|--------|-------|-------------------|
| **ACID Compliance** | Yes | No (eventually consistent) |
| **Query Flexibility** | Excellent (SQL) | Limited |
| **Scaling** | Vertical + read replicas | Horizontal |
| **Consistency** | Strong | Eventual |
| **Cost** | Lower | Higher (managed) |

**Why MySQL:**
- **ACID Required**: URL mappings need strong consistency
- **Complex Queries**: User dashboards need SQL flexibility
- **Cost**: Lower cost at scale

**Why Cassandra for Analytics:**
- **High Write Throughput**: 1M+ clicks/day
- **Time-Series Data**: Perfect for analytics
- **Eventual Consistency**: OK for analytics

### 3. Caching Strategy: Cache-Aside vs Write-Through

**Decision:** Cache-Aside (lazy loading) for reads, Write-Through for writes.

**Trade-offs:**

| Pattern | Pros | Cons | Use Case |
|---------|------|------|----------|
| **Cache-Aside** | Simple, cache only what's needed | Cache miss penalty | Reads |
| **Write-Through** | Always consistent | Slower writes | Critical writes |
| **Write-Behind** | Fast writes | Risk of data loss | Non-critical writes |

**Why Cache-Aside for Reads:**
- **Efficiency**: Only cache frequently accessed URLs (80/20 rule)
- **Simplicity**: Easy to implement and debug
- **Flexibility**: Can invalidate cache easily

**Why Write-Through for Writes:**
- **Consistency**: Cache always has latest data
- **Reliability**: No risk of cache inconsistency

**Cache Hit Rate Optimization:**
- Cache top 20% of URLs (Pareto principle)
- **Result**: 80% cache hit rate with 20% of data

### 4. Sharding Strategy: Hash vs Range vs Directory

**Decision:** Hash-based sharding by short_code.

**Trade-offs:**

| Strategy | Pros | Cons | Use Case |
|----------|------|------|----------|
| **Hash-based** | Even distribution | Cross-shard queries | High throughput |
| **Range-based** | Easy queries | Hot spots | Sequential access |
| **Directory-based** | Flexible | Single point of failure | Low-medium scale |

**Why Hash-Based:**
- **Even Distribution**: URLs distributed evenly across shards
- **No Hot Spots**: No single shard gets overloaded
- **Scalability**: Easy to add/remove shards

**Sharding Implementation:**
```python
def get_shard(short_code, num_shards):
    # Consistent hashing for better distribution
    hash_value = hash(short_code)
    return hash_value % num_shards

# Example: 4 shards
# "abc123" → hash = 12345 → shard = 12345 % 4 = 1
# "xyz789" → hash = 67890 → shard = 67890 % 4 = 2
```

**Alternative Considered:** Shard by user_id
- **Pros**: User queries faster (all user URLs in one shard)
- **Cons**: Uneven distribution (some users have many URLs)
- **Decision**: Hash by short_code for even distribution

### 5. Analytics: Real-time vs Batch

**Decision:** Hybrid approach (real-time for recent data, batch for historical).

**Trade-offs:**

| Approach | Latency | Cost | Complexity |
|----------|---------|------|------------|
| **Real-time** | Low (< 1s) | High | High |
| **Batch** | High (hours) | Low | Low |

**Hybrid Strategy:**
- **Real-time**: Last 24 hours (Kafka → ClickHouse)
- **Batch**: Historical data (Kafka → S3 → ClickHouse daily)

**Why Hybrid:**
- **Cost**: Batch processing 10x cheaper than real-time
- **Performance**: Real-time for recent data, batch for historical
- **Result**: 90% cost savings with acceptable latency

### 6. URL Validation: Client vs Server

**Decision:** Both (client for UX, server for security).

**Trade-offs:**

| Location | Pros | Cons |
|----------|------|------|
| **Client** | Fast feedback, better UX | Can be bypassed |
| **Server** | Secure, cannot bypass | Slower feedback |

**Why Both:**
- **Client**: Immediate feedback, better user experience
- **Server**: Security, prevent malicious URLs
- **Validation Rules**:
  - Protocol whitelist (http, https)
  - Domain blacklist (malicious domains)
  - URL length limit (2048 characters)
  - Malware scanning (optional)

### 7. Custom Alias: Allow vs Disallow

**Decision:** Allow custom aliases with validation.

**Trade-offs:**

| Decision | Pros | Cons |
|----------|------|------|
| **Allow** | Better UX, branding | Abuse risk, collision handling |
| **Disallow** | Simpler, no abuse | Less flexible |

**Why Allow:**
- **User Value**: Users can create branded links
- **Mitigation**: 
  - Reserved words blacklist
  - Profanity filter
  - Rate limiting per user
  - Collision detection

**Implementation:**
```python
def create_custom_alias(short_code, user_id):
    # Validate custom alias
    if is_reserved_word(short_code):
        raise ValidationError("Reserved word")
    if contains_profanity(short_code):
        raise ValidationError("Invalid characters")
    
    # Check availability
    if db.exists(short_code):
        raise ConflictError("Alias already taken")
    
    return db.create_url(short_code, original_url, user_id)
```

---

## Interview Discussion Points

### Key Questions to Address

1. **"How would you handle a URL that gets 1M clicks in 1 hour?"**
   - **Answer**: 
     - Pre-warm CDN cache for the URL
     - Scale read replicas to handle database load
     - Cache aggressively (longer TTL)
     - Monitor and alert on traffic spikes
     - Consider rate limiting if malicious

2. **"What if two users shorten the same URL?"**
   - **Answer**:
     - **Option 1**: Return existing short URL (saves storage)
     - **Option 2**: Create new short URL (user-specific)
     - **Decision**: Return existing if no user_id, create new if user_id provided
     - **Rationale**: Balance between storage efficiency and user control

3. **"How do you ensure short codes are not guessable?"**
   - **Answer**:
     - Use hash-based generation (not sequential)
     - Use 7 characters (3.5 trillion combinations)
     - Add random salt to hash input
     - Monitor for enumeration attacks

4. **"What's your strategy for handling expired URLs?"**
   - **Answer**:
     - Soft delete (mark as expired, don't delete immediately)
     - Return 410 Gone status code
     - Option to extend expiration
     - Archive expired URLs for analytics

5. **"How do you handle URL updates (changing destination)?"**
   - **Answer**:
     - Allow updates for URL owner
     - Invalidate cache
     - Log change history
     - Option to create new short URL instead

### Scalability Deep Dive

**Q: "How do you scale from 1M to 1B URLs?"**

**Answer:**

**Phase 1: 1M-10M URLs**
- Single MySQL database
- Single Redis instance
- Basic caching

**Phase 2: 10M-100M URLs**
- MySQL with read replicas
- Redis cluster
- Database sharding (4 shards)

**Phase 3: 100M-1B URLs**
- MySQL sharding (16+ shards)
- Multiple Redis clusters
- CDN for static assets
- Analytics pipeline (Kafka + ClickHouse)

**Key Scaling Principles:**
1. **Horizontal Scaling**: Add shards, not bigger databases
2. **Caching**: Aggressive caching (80%+ hit rate)
3. **Read Replicas**: Scale reads independently
4. **Sharding**: Distribute data evenly
5. **Async Processing**: Decouple analytics from core path

### Performance Optimization

**Q: "How do you optimize redirect latency?"**

**Answer:**

**Current Flow:**
1. Check Redis cache (1-2ms)
2. If miss, query database (10-50ms)
3. Update cache (1-2ms)
4. Redirect (1ms)
**Total: 13-55ms**

**Optimizations:**
1. **CDN Caching**: Cache at CDN level (10-20ms)
2. **Pre-warming**: Pre-cache popular URLs
3. **Connection Pooling**: Reuse database connections
4. **Read Replicas**: Query nearest replica
5. **Local Cache**: In-memory cache in application

**Optimized Flow:**
1. Check CDN cache (10-20ms) - 80% hit rate
2. Check Redis cache (1-2ms) - 15% hit rate
3. Query database (10-50ms) - 5% hit rate
**Average: 15ms** (vs 30ms before)

### Cost Optimization

**Q: "How do you optimize costs at scale?"**

**Answer:**

1. **Database Costs** (40% of total):
   - Sharding reduces per-shard size
   - Archive old URLs to cheaper storage
   - Use read replicas for reads

2. **Cache Costs** (30% of total):
   - Cache only popular URLs (80/20 rule)
   - Use TTL-based expiration
   - Compress cache values

3. **Storage Costs** (20% of total):
   - Archive expired URLs
   - Compress long URLs
   - Delete unused URLs after expiration

4. **Compute Costs** (10% of total):
   - Auto-scaling (scale down during off-peak)
   - Use spot instances for batch jobs
   - Optimize code (reduce CPU usage)

**Total Savings**: 30-40% cost reduction

### Edge Cases

**Q: "How do you handle edge cases?"**

**Answer:**

1. **Very Long URLs (> 2048 chars)**:
   - Reject or truncate
   - Store in separate table if needed

2. **Circular Redirects**:
   - Detect redirect chains
   - Limit redirect depth (max 10)
   - Return error if circular

3. **Malicious URLs**:
   - URL validation
   - Malware scanning
   - Rate limiting
   - Blacklist known malicious domains

4. **Unicode URLs**:
   - Normalize URLs (Punycode)
   - Validate encoding
   - Store normalized version

5. **Expired URLs**:
   - Soft delete (mark expired)
   - Return 410 Gone
   - Option to extend expiration

---

## References

- [TinyURL Architecture](https://www.backblaze.com/blog/how-to-build-a-better-url-shortener/)
- [Bitly Architecture](https://bitly.com/pages/about/technology)
- [System Design Primer](https://github.com/donnemartin/system-design-primer)
- [URL Shortener Design - High Scalability](http://highscalability.com/blog/2012/7/9/the-bitly-architecture-updated-at-4-trillion-clicks-per-mont.html)
- [Consistent Hashing](https://en.wikipedia.org/wiki/Consistent_hashing)
- [Base62 Encoding](https://en.wikipedia.org/wiki/Base62)

