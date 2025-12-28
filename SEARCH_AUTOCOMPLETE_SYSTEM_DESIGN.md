# Search Autocomplete System Design Document

## Table of Contents
1. [Overview](#overview)
2. [Requirements](#requirements)
3. [System Architecture](#system-architecture)
4. [Database Design](#database-design)
5. [API Design](#api-design)
6. [Trie Data Structure](#trie-data-structure)
7. [Search Ranking Algorithm](#search-ranking-algorithm)
8. [Caching Strategy](#caching-strategy)
9. [Real-Time Updates](#real-time-updates)
10. [Scalability Considerations](#scalability-considerations)
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

A search autocomplete system provides real-time suggestions as users type their search queries. The system must handle millions of queries per second, return results in milliseconds, and support multiple languages and contexts. This design can be applied to search engines, e-commerce sites, social media platforms, and any application requiring fast autocomplete functionality.

**Key Features:**
- Real-time search suggestions (< 100ms latency)
- Prefix matching
- Ranking by popularity/relevance
- Multi-language support
- Context-aware suggestions
- Personalization
- Typo tolerance (fuzzy matching)
- Trending queries
- Recent searches

---

## Requirements

### Functional Requirements

1. **Query Suggestions**
   - Return top N suggestions (typically 5-10)
   - Prefix matching (as user types)
   - Support multiple languages
   - Handle special characters and spaces

2. **Ranking**
   - Rank by popularity (search frequency)
   - Rank by relevance (context, user history)
   - Rank by recency (trending queries)
   - Personalize based on user history

3. **Query Completion**
   - Complete partial queries
   - Suggest related queries
   - Handle typos (fuzzy matching)

4. **Context Awareness**
   - Location-based suggestions
   - Category-specific suggestions
   - Time-based suggestions (trending)

5. **Query Storage**
   - Store search queries
   - Track query frequency
   - Track query trends

### Non-Functional Requirements

1. **Performance**
   - Response time: < 100ms (p99)
   - Response time: < 50ms (p95)
   - Handle 10M+ queries per second
   - Support millions of unique queries

2. **Scalability**
   - Horizontal scaling
   - Handle traffic spikes
   - Multi-region deployment

3. **Availability**
   - 99.99% uptime
   - Graceful degradation
   - No single point of failure

4. **Accuracy**
   - Relevant suggestions
   - High precision (top suggestions are relevant)
   - Low false positives

---

## System Architecture

### High-Level Architecture

```
┌─────────────┐
│   Clients   │
│  (Browser,  │
│   Mobile)   │
└──────┬──────┘
       │
       │ HTTPS
       │
┌──────▼─────────────────────────────────────────┐
│           Load Balancer                        │
└──────┬─────────────────────────────────────────┘
       │
       ├─────────────────┬─────────────────┐
       │                 │                 │
┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐
│  Autocomplete│  │  Query     │  │  Analytics  │
│  API Servers │  │  Collector │  │  Service    │
│              │  │            │  │             │
│ - Handle     │  │ - Collect  │  │ - Analyze   │
│   requests   │  │   queries  │  │   trends    │
│ - Query Trie │  │ - Update   │  │ - Update    │
│ - Rank       │  │   counts   │  │   rankings  │
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
│  Trie       │  │  Cache      │  │  Database   │
│  Service    │  │  (Redis)    │  │             │
│             │  │             │  │ - Query     │
│ - In-memory │  │ - Recent    │  │   metadata │
│   Trie      │  │   queries   │  │ - User     │
│ - Search    │  │ - Popular   │  │   history  │
│   logic     │  │   queries   │  │ - Trends   │
└─────────────┘  └─────────────┘  └─────────────┘
```

### Component Details

1. **Autocomplete API Servers**
   - Handle autocomplete requests
   - Query Trie data structure
   - Rank and filter results
   - Return top N suggestions

2. **Query Collector**
   - Collect search queries from users
   - Track query frequency
   - Update query counts
   - Send to message queue for processing

3. **Analytics Service**
   - Analyze query trends
   - Calculate popularity scores
   - Update rankings
   - Identify trending queries

4. **Trie Service**
   - Maintain in-memory Trie data structure
   - Fast prefix matching
   - Support millions of queries
   - Periodic updates from database

5. **Cache (Redis)**
   - Cache popular queries
   - Cache recent queries per user
   - Cache trending queries
   - Reduce Trie lookups

---

## Database Design

### Query Database (Cassandra or Elasticsearch)

**queries**
```sql
CREATE TABLE queries (
    query_text TEXT PRIMARY KEY,
    frequency COUNTER,
    last_searched TIMESTAMP,
    first_searched TIMESTAMP,
    category TEXT,
    language TEXT,
    INDEX idx_category (category),
    INDEX idx_language (language)
);
```

**query_trends**
```sql
CREATE TABLE query_trends (
    date DATE,
    hour INT,
    query_text TEXT,
    count COUNTER,
    PRIMARY KEY (date, hour, query_text)
) WITH CLUSTERING ORDER BY (hour DESC, count DESC);
```

### User Search History (Cassandra)

**user_searches**
```sql
CREATE TABLE user_searches (
    user_id BIGINT,
    query_text TEXT,
    searched_at TIMESTAMP,
    clicked_result BOOLEAN,
    PRIMARY KEY (user_id, searched_at, query_text)
) WITH CLUSTERING ORDER BY (searched_at DESC);
```

### Query Metadata (MySQL)

**query_metadata**
```sql
CREATE TABLE query_metadata (
    query_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    query_text VARCHAR(500) UNIQUE NOT NULL,
    category VARCHAR(100),
    language VARCHAR(10),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_category (category),
    INDEX idx_language (language)
);
```

### Cache (Redis)

**Popular Queries**
```
Key: popular:{prefix}
Value: List of top queries with prefix
TTL: 1 hour
```

**Recent Queries (Per User)**
```
Key: recent:{user_id}
Value: List of recent queries
TTL: 24 hours
```

**Trending Queries**
```
Key: trending
Value: List of trending queries
TTL: 1 hour
```

---

## API Design

### Autocomplete API

**GET /api/v1/autocomplete**
```json
Query Parameters:
- q: "search query" (required)
- limit: 10 (default, max 20)
- language: "en" (optional)
- category: "products" (optional)
- user_id: 123 (optional, for personalization)

Response:
{
  "suggestions": [
    {
      "query": "iphone 15 pro max",
      "count": 15000,
      "category": "products"
    },
    {
      "query": "iphone 15 pro",
      "count": 12000,
      "category": "products"
    },
    {
      "query": "iphone 15",
      "count": 10000,
      "category": "products"
    }
  ],
  "query_time_ms": 45
}
```

### Query Collection API (Internal)

**POST /api/v1/queries/collect**
```json
Request:
{
  "query": "iphone 15",
  "user_id": 123,
  "timestamp": "2024-01-01T12:00:00Z",
  "clicked": false
}

Response:
{
  "success": true
}
```

### Analytics API (Internal)

**GET /api/v1/analytics/trending**
```json
Query Parameters:
- hours: 24 (default)
- limit: 20

Response:
{
  "trending_queries": [
    {
      "query": "new product launch",
      "count": 50000,
      "growth": 150.5
    }
  ]
}
```

---

## Trie Data Structure

### Trie Overview

A Trie (prefix tree) is ideal for autocomplete because:
- Fast prefix matching (O(m) where m is prefix length)
- Efficient storage of common prefixes
- Easy to traverse and find all words with given prefix

### Trie Node Structure

```python
class TrieNode:
    def __init__(self):
        self.children = {}  # char -> TrieNode
        self.is_end = False
        self.query = None
        self.frequency = 0
        self.metadata = {}  # category, language, etc.
```

### Trie Operations

**Insert Query**
```python
def insert(root, query, frequency, metadata):
    node = root
    for char in query:
        if char not in node.children:
            node.children[char] = TrieNode()
        node = node.children[char]
    node.is_end = True
    node.query = query
    node.frequency = frequency
    node.metadata = metadata
```

**Search Prefix**
```python
def search_prefix(root, prefix):
    node = root
    # Navigate to prefix node
    for char in prefix:
        if char not in node.children:
            return []
        node = node.children[char]
    
    # Collect all queries with this prefix
    results = []
    collect_queries(node, prefix, results)
    return results

def collect_queries(node, prefix, results):
    if node.is_end:
        results.append({
            "query": node.query,
            "frequency": node.frequency,
            "metadata": node.metadata
        })
    
    for char, child in node.children.items():
        collect_queries(child, prefix + char, results)
```

### Optimized Trie with Frequency

**Store Top K at Each Node**
```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.top_queries = []  # Top K queries with this prefix
        # Sorted by frequency
```

**Update Top Queries**
- When inserting, update top queries at each node
- Maintain heap of top K queries
- Efficient for fast retrieval

### Distributed Trie

**Sharding Strategy**
- Shard Trie by first character or hash
- Each server handles subset of queries
- Load balancer routes based on prefix

**Replication**
- Replicate Trie across multiple servers
- Read from any replica
- Update all replicas (eventually consistent)

---

## Search Ranking Algorithm

### Ranking Factors

1. **Frequency (40%)**
   - Higher frequency = higher rank
   - Normalize by total queries

2. **Recency (30%)**
   - Recent queries ranked higher
   - Boost trending queries

3. **Relevance (20%)**
   - Exact prefix match ranked higher
   - Category match (if provided)
   - Language match (if provided)

4. **Personalization (10%)**
   - User's search history
   - User's preferences
   - Location-based suggestions

### Ranking Formula

```
Score = (frequency_score * 0.4) + 
        (recency_score * 0.3) + 
        (relevance_score * 0.2) + 
        (personalization_score * 0.1)
```

### Frequency Score

```python
def frequency_score(frequency, max_frequency):
    # Normalize to 0-1
    return min(frequency / max_frequency, 1.0)
```

### Recency Score

```python
def recency_score(last_searched, now):
    # Exponential decay
    hours_ago = (now - last_searched).total_seconds() / 3600
    return math.exp(-hours_ago / 24)  # Half-life of 24 hours
```

### Relevance Score

```python
def relevance_score(query, prefix, category, language):
    score = 0.0
    
    # Exact prefix match
    if query.startswith(prefix):
        score += 0.5
    
    # Category match
    if category and query_metadata.get('category') == category:
        score += 0.3
    
    # Language match
    if language and query_metadata.get('language') == language:
        score += 0.2
    
    return score
```

### Personalization Score

```python
def personalization_score(query, user_history):
    # Check if user searched this before
    if query in user_history:
        return 0.5
    
    # Check for similar queries
    similarity = max_similarity(query, user_history)
    return similarity * 0.3
```

---

## Caching Strategy

### Multi-Level Caching

1. **Application Cache (In-Memory)**
   - Trie data structure (entire Trie in memory)
   - Fastest access
   - Updated periodically

2. **Redis Cache**
   - Cache popular prefix queries
   - Cache per-user recent queries
   - Cache trending queries
   - TTL: 1 hour

3. **CDN Cache**
   - Cache API responses
   - Edge caching for popular queries
   - TTL: 5 minutes

### Cache Strategy

**Popular Queries**
- Cache top 1000 most popular prefixes
- Update every hour
- Store in Redis with TTL

**User-Specific Cache**
- Cache user's recent searches
- Cache personalized suggestions
- TTL: 24 hours

**Prefix-Based Cache**
```
Key: autocomplete:{prefix}
Value: List of top suggestions
TTL: 1 hour
```

### Cache Invalidation

- Update cache when new queries become popular
- Invalidate on query frequency updates
- Periodic refresh for trending queries

---

## Real-Time Updates

### Query Collection Flow

```
User Types Query
       │
       ▼
Autocomplete API
       │
       ├─── Return Suggestions
       │
       └─── Log Query (async)
              │
              ▼
         Message Queue
              │
              ▼
         Query Collector
              │
              ├─── Update Frequency Count
              ├─── Update Trends
              └─── Update Trie (periodic)
```

### Trie Update Strategy

**Option 1: Periodic Updates**
- Update Trie every 5-10 minutes
- Batch process query frequency updates
- Simple but slightly stale

**Option 2: Real-Time Updates**
- Update Trie on every query (expensive)
- Use write-through cache
- More complex but real-time

**Chosen: Hybrid Approach**
- Update Redis cache immediately
- Update Trie periodically (every 5 minutes)
- Use cache for recent queries
- Use Trie for historical queries

### Trending Queries

**Calculation**
- Track query counts per hour
- Calculate growth rate
- Identify sudden spikes
- Update trending list

**Update Frequency**
- Calculate every 15 minutes
- Update cache
- Update Trie periodically

---

## Scalability Considerations

### Horizontal Scaling

1. **API Servers**
   - Stateless design
   - Load balancer distributes requests
   - Auto-scaling based on load

2. **Trie Servers**
   - Shard Trie by prefix
   - Each server handles subset
   - Consistent hashing for routing

3. **Query Processing**
   - Scale collectors independently
   - Process queries in parallel
   - Batch updates

### Vertical Scaling

- Use high-memory servers for Trie
- Optimize Trie data structure
- Use compression for Trie storage

### Sharding Strategy

**Prefix-Based Sharding**
- Server 1: Queries starting with a-h
- Server 2: Queries starting with i-p
- Server 3: Queries starting with q-z
- Load balancer routes based on first character

**Hash-Based Sharding**
- Hash query prefix
- Route to server based on hash
- More even distribution

---

## Load Balancing

### Load Balancing Strategy

1. **Request Routing**
   - Route based on query prefix
   - Consistent hashing
   - Health checks

2. **Cache-Aware Routing**
   - Route to server with cached data
   - Reduce cache misses
   - Improve performance

3. **Geographic Routing**
   - Route to nearest region
   - Lower latency
   - Better user experience

---

## Security

### Rate Limiting

- Limit requests per user/IP
- Prevent abuse
- Protect against DDoS

### Input Validation

- Sanitize query inputs
- Prevent injection attacks
- Validate query length

### Privacy

- Don't log sensitive queries
- Anonymize user data
- Comply with privacy regulations

---

## Monitoring & Analytics

### Key Metrics

1. **Performance Metrics**
   - Response time (p50, p95, p99)
   - Cache hit rate
   - Trie lookup time
   - Query throughput

2. **Quality Metrics**
   - Click-through rate (CTR)
   - Suggestion relevance
   - User satisfaction

3. **System Metrics**
   - CPU, memory usage
   - Trie size
   - Cache size
   - Queue depth

### Monitoring Tools

- Application monitoring: Prometheus, Grafana
- Log aggregation: ELK Stack
- Distributed tracing: Jaeger

---

## Deployment Strategy

### Multi-Region Deployment

- Deploy in multiple regions
- Route users to nearest region
- Replicate Trie data
- Sync query frequencies

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

**Trie Storage**
- Average query length: 20 characters
- 10M unique queries
- Trie overhead: ~2x
- Total: ~400MB (compressed)

**Query Metadata**
- 10M queries × 1KB = 10GB
- With replication: 30GB

**Cache**
- 1000 popular prefixes × 10KB = 10MB
- Per-user cache: 1KB × 100M users = 100GB

### Compute Estimates

**API Servers**
- 10M queries/second peak
- Each server handles 10K queries/second
- Need 1000 servers (with redundancy: 1500)

**Trie Servers**
- In-memory Trie
- High-memory servers (64GB+)
- 10 servers per region (with sharding)

---

## Technology Stack

### Backend
- **Language**: Java, Go, or C++ (for performance)
- **Trie Implementation**: Custom or library
- **Message Queue**: Kafka
- **Database**: 
  - Cassandra (query frequency)
  - Redis (cache)
  - MySQL (metadata)
- **Search**: Elasticsearch (optional, for advanced features)

### Frontend
- **JavaScript**: Debounce API calls
- **Caching**: Browser cache
- **Optimization**: Request batching

### Infrastructure
- **Container Orchestration**: Kubernetes
- **Monitoring**: Prometheus, Grafana
- **Logging**: ELK Stack

---

## Failure Scenarios & Handling

### Trie Server Failure

- Replicate Trie across servers
- Failover to replica
- Rebuild Trie from database

### Cache Failure

- Fallback to Trie lookup
- Slightly slower but functional
- Rebuild cache on recovery

### Database Failure

- Use database replicas
- Read from replica
- Write to primary

### High Load

- Rate limiting
- Graceful degradation
- Return fewer suggestions
- Prioritize popular queries

---

## Trade-offs & Design Decisions

### 1. Trie vs Elasticsearch

**Chosen: Trie**
- Faster for prefix matching (< 10ms)
- Lower latency
- More memory intensive

**Trade-off**: More complex to maintain

### 2. In-Memory Trie vs Database

**Chosen: In-Memory Trie**
- Fastest access
- Low latency
- Requires high-memory servers

**Trade-off**: Memory cost

### 3. Real-Time vs Periodic Updates

**Chosen: Hybrid (Periodic + Cache)**
- Balance between freshness and performance
- Cache for recent queries
- Trie for historical queries

**Trade-off**: Slightly stale data

### 4. Sharding: Prefix vs Hash

**Chosen: Prefix-Based**
- Easier to implement
- Better cache locality
- Uneven distribution possible

**Trade-off**: May need rebalancing

### 5. Ranking: Simple vs ML

**Chosen: Rule-Based (can evolve to ML)**
- Simpler to implement
- Easier to debug
- Can add ML later

**Trade-off**: Less sophisticated initially

---

## Interview Discussion Points

### Key Topics to Discuss

1. **Trie Optimization**
   - How to reduce memory usage?
   - How to handle millions of queries?
   - Compression techniques?

2. **Fuzzy Matching**
   - How to handle typos?
   - Edit distance algorithms
   - Performance considerations

3. **Multi-Language Support**
   - How to handle different languages?
   - Character encoding
   - Language-specific ranking

4. **Personalization**
   - How to personalize suggestions?
   - Privacy considerations
   - Real-time personalization

5. **Trending Queries**
   - How to identify trends?
   - How to prevent spam?
   - Time-window considerations

6. **Scalability**
   - How to scale to billions of queries?
   - How to handle traffic spikes?
   - Multi-region considerations

7. **Caching Strategy**
   - What to cache?
   - Cache invalidation
   - Cache consistency

8. **Query Completion**
   - How to complete partial queries?
   - Context-aware completion
   - Multi-word queries

### Common Follow-up Questions

- How would you handle fuzzy matching?
- How to support multiple languages?
- How to handle special characters?
- How to prevent query spam?
- How to handle very long queries?
- How to support query suggestions for different categories?
- How to implement "Did you mean?" feature?

---

## Advanced Features

### Fuzzy Matching

**Edit Distance**
- Use Levenshtein distance
- Allow 1-2 character differences
- Rank by edit distance

**Implementation**
- Generate variations of prefix
- Search all variations
- Rank by edit distance

### Multi-Word Queries

- Support queries with spaces
- Match any word in query
- Rank by word position

### Context-Aware Suggestions

- Location-based suggestions
- Category-specific suggestions
- Time-based suggestions
- Device-based suggestions

### Query Completion

- Complete partial words
- Suggest next words
- Use n-gram models

---

## High-Level Design (HLD)

### System Overview

The search autocomplete system follows a real-time query processing architecture:

1. **Client Layer**: Web and mobile applications
2. **API Gateway**: Routes requests, handles rate limiting
3. **Autocomplete Service**: Handles autocomplete requests, queries Trie
4. **Trie Service**: Maintains in-memory Trie data structure
5. **Query Collector**: Collects queries, updates frequencies
6. **Analytics Service**: Analyzes trends, updates rankings

### Component Architecture

**Core Components:**
- **Autocomplete API**: Handles autocomplete requests
- **Trie Service**: In-memory Trie for fast prefix matching
- **Query Collector**: Tracks query frequencies
- **Ranking Service**: Ranks suggestions by relevance

---

## Low-Level Design (LLD)

### Trie Service Implementation

```python
class TrieService:
    def __init__(self):
        self.root = TrieNode()
        self.query_cache = {}  # prefix -> top suggestions
    
    def insert(self, query: str, frequency: int):
        node = self.root
        for char in query:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
            
            # Update top queries at each node
            node.update_top_queries(query, frequency)
        
        node.is_end = True
        node.query = query
        node.frequency = frequency
    
    def search_prefix(self, prefix: str, limit: int = 10) -> list:
        # Check cache first
        cache_key = f"{prefix}:{limit}"
        if cache_key in self.query_cache:
            return self.query_cache[cache_key]
        
        # Navigate to prefix node
        node = self.root
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]
        
        # Get top queries from node
        results = node.get_top_queries(limit)
        
        # Cache results
        self.query_cache[cache_key] = results
        
        return results
```

---

## Fault Tolerance

### Trie Service Resilience

**Replication:**
- Multiple Trie service instances
- Periodic Trie updates from database
- Read from any replica

**Failure Handling:**
- Fallback to database queries
- Serve cached results
- Graceful degradation

---

## Optimizations

### Trie Optimization

**Memory Optimization:**
- Compress Trie structure
- Use efficient data structures
- Garbage collection friendly

**Query Optimization:**
- Cache frequent prefixes
- Pre-compute top queries
- Optimize Trie traversal

### Caching Strategy

**Multi-Level Caching:**
- Application cache (Trie)
- Redis cache (popular queries)
- CDN cache (API responses)

---

## Failure Safety

### Trie Service Failure

**Scenario: Trie Service Down**
- **Impact**: Cannot serve autocomplete
- **Mitigation**:
  - Multiple Trie instances
  - Fallback to database
  - Serve cached results
- **Recovery**:
  - Service recovers
  - Rebuild Trie from database
  - Resume normal operation

---

## Scalability

### Horizontal Scaling

**Service Scaling:**
- Stateless service instances
- Shard Trie by prefix
- Load balancer routes requests

**Trie Scaling:**
- Shard Trie across servers
- Consistent hashing for routing
- Scale horizontally

---

*This document provides a comprehensive system design for a search autocomplete system. Adjustments may be needed based on specific requirements and constraints.*

