# System to Collect Performance Metrics from Thousands of Servers

## Table of Contents
1. [Overview](#overview)
2. [Requirements](#requirements)
3. [System Architecture](#system-architecture)
4. [Data Models](#data-models)
5. [API Design](#api-design)
6. [Metrics Collection Flow](#metrics-collection-flow)
7. [Data Storage & Aggregation](#data-storage--aggregation)
8. [Query & Retrieval System](#query--retrieval-system)
9. [Scalability Considerations](#scalability-considerations)
10. [Caching Strategy](#caching-strategy)
11. [Load Balancing](#load-balancing)
12. [Security](#security)
13. [Monitoring & Alerting](#monitoring--alerting)
14. [Deployment Strategy](#deployment-strategy)
15. [Capacity Planning](#capacity-planning)
16. [Technology Stack](#technology-stack)
17. [Failure Scenarios & Handling](#failure-scenarios--handling)
18. [Trade-offs & Design Decisions](#trade-offs--design-decisions)
19. [Interview Discussion Points](#interview-discussion-points)

---

## Overview

A distributed system to collect, store, and query performance metrics from thousands of servers in real-time. The system must handle high-volume metric ingestion, provide low-latency queries, support time-series data, and scale horizontally to accommodate growing infrastructure.

**Key Features:**
- Real-time metrics collection from thousands of servers
- Support for multiple metric types (CPU, memory, disk, network, custom)
- High-throughput data ingestion
- Low-latency querying and aggregation
- Time-series data storage and retention
- Real-time alerting based on metrics
- Dashboard visualization
- Metric downsampling and compression
- Multi-tenant support

---

## Requirements

### Functional Requirements

1. **Metrics Collection**
   - Collect metrics from thousands of servers
   - Support multiple metric types (CPU, memory, disk I/O, network, custom)
   - Configurable collection intervals (1s, 5s, 10s, 1min, etc.)
   - Support for tags/labels (server_id, region, environment, etc.)
   - Batch and streaming ingestion

2. **Data Storage**
   - Store time-series metrics efficiently
   - Support high write throughput
   - Fast time-range queries
   - Data retention policies (hot/warm/cold storage)
   - Data compression and downsampling

3. **Query & Retrieval**
   - Query metrics by time range
   - Aggregate functions (sum, avg, min, max, percentile)
   - Group by tags/labels
   - Support for complex queries
   - Low-latency queries (< 100ms for recent data)

4. **Alerting**
   - Real-time alerting based on metric thresholds
   - Support for complex alert rules
   - Alert notification channels (email, Slack, PagerDuty)
   - Alert deduplication

5. **Visualization**
   - Dashboard creation
   - Real-time metric visualization
   - Historical trend analysis
   - Export capabilities

### Non-Functional Requirements

1. **Scalability**
   - Support 10,000+ servers
   - Handle 1M+ metrics per second ingestion
   - Support 10,000+ concurrent queries
   - Horizontal scaling

2. **Performance**
   - Ingestion latency: < 100ms (p95)
   - Query latency: < 100ms for recent data (p95)
   - Query latency: < 1s for historical data (p95)
   - 99.9% uptime

3. **Reliability**
   - No data loss during ingestion
   - Data durability guarantees
   - Fault tolerance
   - Graceful degradation

4. **Storage**
   - Efficient storage (compression, downsampling)
   - Configurable retention (hot: 7 days, warm: 30 days, cold: 1 year)
   - Cost-effective storage tiers

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Agent Layer (Servers)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Server 1   │  │   Server 2   │  │   Server N   │         │
│  │   (Agent)    │  │   (Agent)    │  │   (Agent)    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────┬───────────────┬───────────────┬───────────────────┘
             │               │               │
             ▼               ▼               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Load Balancer / API Gateway                   │
│              (NGINX, HAProxy, AWS ALB)                          │
└────────────┬─────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Ingestion Layer                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Collector  │  │   Collector  │  │   Collector  │         │
│  │   Service 1  │  │   Service 2  │  │   Service N │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│  - Validate metrics                                              │
│  - Transform & normalize                                          │
│  - Rate limiting                                                 │
└────────────┬─────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Message Queue                                 │
│              (Kafka, Apache Pulsar)                             │
│  - Buffering                                                     │
│  - Load distribution                                             │
│  - Backpressure handling                                         │
└────────────┬─────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Processing Layer                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Aggregator │  │   Aggregator │  │   Aggregator │         │
│  │   Service 1  │  │   Service 2  │  │   Service N │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│  - Pre-aggregation                                               │
│  - Downsampling                                                  │
│  - Compression                                                   │
└────────────┬─────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Storage Layer                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Time-Series │  │  Time-Series │  │  Time-Series │         │
│  │     DB 1     │  │     DB 2     │  │     DB N     │         │
│  │ (InfluxDB/   │  │ (InfluxDB/   │  │ (InfluxDB/   │         │
│  │  TimescaleDB)│  │  TimescaleDB)│  │  TimescaleDB)│         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Hot Store  │  │   Warm Store  │  │   Cold Store │         │
│  │  (In-Memory) │  │  (SSD/HDD)    │  │  (S3/Glacier)│         │
│  │  (7 days)    │  │  (30 days)    │  │  (1 year+)   │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Query Layer                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Query      │  │   Query      │  │   Query      │         │
│  │   Service 1  │  │   Service 2  │  │   Service N │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│  - Query routing                                                  │
│  - Aggregation                                                    │
│  - Result caching                                                 │
└────────────┬─────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Application Layer                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Dashboard   │  │   Alerting   │  │    API        │         │
│  │   Service    │  │   Service    │  │   Gateway     │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

### Component Details

#### 1. Agent (Server-side)
- **Purpose**: Collect metrics from servers
- **Responsibilities**:
  - Collect system metrics (CPU, memory, disk, network)
  - Collect application metrics (custom metrics)
  - Batch metrics for efficient transmission
  - Compress and send to ingestion layer
  - Handle retries and backoff

#### 2. Collector Service
- **Purpose**: Receive and validate metrics
- **Responsibilities**:
  - Accept metrics from agents
  - Validate metric format
  - Rate limiting per server
  - Transform and normalize metrics
  - Route to appropriate queue

#### 3. Message Queue
- **Purpose**: Buffer and distribute metrics
- **Responsibilities**:
  - Handle backpressure
  - Distribute load to processors
  - Provide durability
  - Support multiple consumers

#### 4. Aggregator Service
- **Purpose**: Process and aggregate metrics
- **Responsibilities**:
  - Pre-aggregate metrics (reduce data volume)
  - Downsample older data
  - Compress metrics
  - Route to appropriate storage tier

#### 5. Time-Series Database
- **Purpose**: Store time-series metrics
- **Responsibilities**:
  - Efficient time-series storage
  - Fast time-range queries
  - Compression
  - Retention management

#### 6. Query Service
- **Purpose**: Handle metric queries
- **Responsibilities**:
  - Parse query requests
  - Route to appropriate storage
  - Aggregate results
  - Cache frequent queries

---

## Data Models

### Metric Data Structure

```json
{
  "metric_name": "cpu.usage",
  "timestamp": 1705312800000,
  "value": 75.5,
  "tags": {
    "server_id": "server-001",
    "region": "us-east-1",
    "environment": "production",
    "datacenter": "dc1"
  },
  "metric_type": "gauge" // gauge, counter, histogram, summary
}
```

### Database Schema (TimescaleDB/PostgreSQL)

```sql
-- Metrics table (hypertable for time-series)
CREATE TABLE metrics (
    time TIMESTAMPTZ NOT NULL,
    metric_name VARCHAR(255) NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    server_id VARCHAR(100),
    region VARCHAR(50),
    environment VARCHAR(50),
    tags JSONB,
    PRIMARY KEY (time, metric_name, server_id)
);

-- Convert to hypertable
SELECT create_hypertable('metrics', 'time');

-- Indexes
CREATE INDEX idx_metrics_name_time ON metrics (metric_name, time DESC);
CREATE INDEX idx_metrics_server_time ON metrics (server_id, time DESC);
CREATE INDEX idx_metrics_tags ON metrics USING GIN (tags);

-- Retention policy (automated)
SELECT add_retention_policy('metrics', INTERVAL '7 days');
```

### Metadata Schema

```sql
-- Servers metadata
CREATE TABLE servers (
    server_id VARCHAR(100) PRIMARY KEY,
    hostname VARCHAR(255),
    ip_address INET,
    region VARCHAR(50),
    environment VARCHAR(50),
    datacenter VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'active'
);

-- Metric definitions
CREATE TABLE metric_definitions (
    metric_name VARCHAR(255) PRIMARY KEY,
    metric_type VARCHAR(20), -- gauge, counter, histogram
    unit VARCHAR(50),
    description TEXT,
    collection_interval INTEGER, -- seconds
    retention_days INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## API Design

### Metrics Ingestion API

```
POST /api/v1/metrics
Content-Type: application/json

[
  {
    "metric_name": "cpu.usage",
    "timestamp": 1705312800000,
    "value": 75.5,
    "tags": {
      "server_id": "server-001",
      "region": "us-east-1"
    }
  },
  {
    "metric_name": "memory.usage",
    "timestamp": 1705312800000,
    "value": 60.2,
    "tags": {
      "server_id": "server-001",
      "region": "us-east-1"
    }
  }
]
```

**Response:**
```json
{
  "status": "success",
  "ingested": 2,
  "failed": 0
}
```

### Query API

```
GET /api/v1/query?metric=cpu.usage&server_id=server-001&start_time=1705312800000&end_time=1705316400000&aggregation=avg&interval=1m
```

**Response:**
```json
{
  "metric": "cpu.usage",
  "server_id": "server-001",
  "data": [
    {
      "time": "2024-01-15T10:00:00Z",
      "value": 75.5
    },
    {
      "time": "2024-01-15T10:01:00Z",
      "value": 76.2
    }
  ]
}
```

### Batch Query API

```
POST /api/v1/query/batch
Content-Type: application/json

{
  "queries": [
    {
      "metric": "cpu.usage",
      "server_id": "server-001",
      "start_time": 1705312800000,
      "end_time": 1705316400000,
      "aggregation": "avg",
      "interval": "1m"
    },
    {
      "metric": "memory.usage",
      "server_id": "server-001",
      "start_time": 1705312800000,
      "end_time": 1705316400000,
      "aggregation": "avg",
      "interval": "1m"
    }
  ]
}
```

---

## Metrics Collection Flow

### Collection Flow

```
┌──────────┐         ┌──────────────┐         ┌──────────────┐
│  Server  │────────▶│   Collector  │────────▶│   Message   │
│  Agent   │         │   Service    │         │    Queue     │
└──────────┘         └──────────────┘         └──────┬───────┘
                                                     │
                                                     ▼
                                            ┌─────────────────┐
                                            │   Aggregator    │
                                            │   Service       │
                                            └──────┬──────────┘
                                                   │
                                                   ▼
                                            ┌─────────────────┐
                                            │  Time-Series DB │
                                            └─────────────────┘
```

### Step-by-Step Process

1. **Agent Collection**
   - Agent collects metrics from server (every 10s)
   - Batches metrics (10-100 metrics per batch)
   - Compresses batch
   - Sends to Collector Service

2. **Ingestion**
   - Collector Service receives batch
   - Validates metrics format
   - Checks rate limits per server
   - Transforms and normalizes
   - Publishes to Kafka topic

3. **Processing**
   - Aggregator Service consumes from Kafka
   - Pre-aggregates metrics (1min, 5min, 1hour windows)
   - Downsamples older data
   - Compresses data
   - Writes to Time-Series DB

4. **Storage**
   - Hot storage: Recent data (last 7 days) - In-memory/SSD
   - Warm storage: Older data (7-30 days) - SSD/HDD
   - Cold storage: Historical data (30+ days) - Object storage

---

## Data Storage & Aggregation

### Storage Tiers

1. **Hot Storage (0-7 days)**
   - **Storage**: In-memory cache + SSD
   - **Retention**: 7 days
   - **Granularity**: 10 seconds
   - **Purpose**: Real-time queries and dashboards

2. **Warm Storage (7-30 days)**
   - **Storage**: SSD/HDD
   - **Retention**: 30 days
   - **Granularity**: 1 minute (downsampled)
   - **Purpose**: Historical analysis

3. **Cold Storage (30+ days)**
   - **Storage**: Object storage (S3, Glacier)
   - **Retention**: 1+ years
   - **Granularity**: 1 hour (downsampled)
   - **Purpose**: Long-term retention, compliance

### Aggregation Strategy

- **Raw Data**: Store for 1 hour (hot storage)
- **1-minute Aggregates**: Store for 7 days (hot storage)
- **5-minute Aggregates**: Store for 30 days (warm storage)
- **1-hour Aggregates**: Store for 1 year (cold storage)

### Compression

- **Algorithm**: Gorilla compression (for time-series)
- **Compression Ratio**: ~10:1 for time-series data
- **Lossless**: For recent data
- **Lossy**: For downsampled data (acceptable)

---

## Query & Retrieval System

### Query Types

1. **Time-Range Queries**
   - Query metrics for a specific time range
   - Support for relative time (last 1 hour, last 7 days)

2. **Aggregation Queries**
   - Sum, Average, Min, Max
   - Percentiles (p50, p95, p99)
   - Rate of change
   - Group by tags

3. **Multi-Metric Queries**
   - Query multiple metrics in single request
   - Join metrics by time

### Query Optimization

1. **Query Routing**
   - Route to appropriate storage tier based on time range
   - Recent queries → Hot storage
   - Historical queries → Warm/Cold storage

2. **Caching**
   - Cache frequent queries (TTL: 1-5 minutes)
   - Cache aggregation results
   - Invalidate on new data

3. **Parallel Queries**
   - Split queries across time ranges
   - Parallel execution
   - Merge results

4. **Query Limits**
   - Max time range: 30 days for detailed queries
   - Max data points: 10,000 per query
   - Rate limiting per user

---

## Scalability Considerations

### Horizontal Scaling

1. **Ingestion Scaling**
   - Multiple Collector Service instances
   - Load balancer distributes requests
   - Kafka partitions for parallel processing

2. **Processing Scaling**
   - Multiple Aggregator Service instances
   - Kafka consumer groups for parallel consumption
   - Auto-scaling based on queue depth

3. **Storage Scaling**
   - Database sharding by time or metric name
   - Read replicas for queries
   - Partitioning by time (monthly partitions)

4. **Query Scaling**
   - Multiple Query Service instances
   - Query result caching
   - Read replicas for read-heavy workloads

### Vertical Scaling

- **Database Optimization**: Indexing, query optimization
- **Connection Pooling**: Efficient connection management
- **Memory Optimization**: Efficient data structures

---

## Caching Strategy

### Cache Layers

1. **Agent Cache**
   - Cache metrics locally before sending
   - Batch multiple metrics
   - Reduce network calls

2. **Query Cache**
   - Cache frequent queries (Redis)
   - TTL: 1-5 minutes
   - Invalidate on new data

3. **Aggregation Cache**
   - Cache pre-aggregated results
   - TTL: 5-15 minutes
   - Reduces computation

### Cache Invalidation

- **Time-based**: TTL expiration
- **Event-based**: Invalidate on new data for affected metrics
- **LRU**: Evict least recently used entries

---

## Load Balancing

### Load Balancing Strategy

- **Ingestion**: Round-robin or least connections
- **Queries**: Round-robin with health checks
- **Geographic**: Route based on server region

### Health Checks

- **Endpoint**: `/health`
- **Interval**: 10 seconds
- **Timeout**: 5 seconds
- **Failure Threshold**: 3 consecutive failures

---

## Security

### Authentication & Authorization

1. **API Keys**
   - Per-server API keys for agents
   - Scoped permissions
   - Rate limiting per key

2. **User Authentication**
   - OAuth 2.0 / JWT for users
   - Role-based access control (RBAC)
   - Multi-tenant isolation

### Data Security

1. **Encryption**
   - TLS for data in transit
   - Encryption at rest for sensitive data

2. **Network Security**
   - VPC isolation
   - Firewall rules
   - DDoS protection

---

## Monitoring & Alerting

### System Metrics

- Ingestion rate (metrics/second)
- Query latency (p50, p95, p99)
- Storage usage
- Error rates
- Queue depth

### Alerting Rules

- High ingestion latency
- High query latency
- Storage capacity warnings
- Service failures
- Data loss detection

---

## Deployment Strategy

### Deployment Architecture

- **Multi-Region**: Deploy in multiple regions
- **Blue-Green**: Zero-downtime deployments
- **Canary**: Gradual rollout

### CI/CD Pipeline

```
Code → Build → Test → Build Image → Deploy Staging → 
E2E Tests → Deploy Production (Canary) → Monitor → Full Rollout
```

---

## Capacity Planning

### Traffic Estimates

- **Servers**: 10,000 servers
- **Metrics per Server**: 50 metrics
- **Collection Interval**: 10 seconds
- **Metrics per Second**: 10,000 × 50 / 10 = 50,000 metrics/second
- **Peak Load**: 3x average = 150,000 metrics/second

### Storage Estimates

- **Metrics per Day**: 50,000 × 86,400 = 4.32B metrics/day
- **Size per Metric**: 100 bytes (compressed)
- **Daily Storage**: 4.32B × 100 bytes = 432GB/day
- **Monthly Storage**: 432GB × 30 = 12.96TB/month
- **Annual Storage**: ~156TB/year (with compression)

### Compute Estimates

- **Collector Services**: 50 instances
- **Aggregator Services**: 100 instances
- **Query Services**: 50 instances
- **Database Servers**: 20 primary + 40 replicas

---

## Technology Stack

### Backend Services

- **Language**: Go, Java, Python
- **Frameworks**: Spring Boot, Gin, FastAPI

### Data Storage

- **Time-Series DB**: InfluxDB, TimescaleDB, ClickHouse
- **Message Queue**: Apache Kafka, Apache Pulsar
- **Cache**: Redis
- **Cold Storage**: AWS S3, Google Cloud Storage

### Infrastructure

- **Cloud**: AWS, GCP, Azure
- **Container Orchestration**: Kubernetes
- **Service Mesh**: Istio (optional)

### Monitoring

- **Metrics**: Prometheus
- **Logging**: ELK Stack
- **Tracing**: Jaeger

---

## Failure Scenarios & Handling

### Failure Scenarios

1. **Agent Failure**
   - **Impact**: Metrics not collected from server
   - **Mitigation**: Retry logic, buffering
   - **Recovery**: Automatic reconnection

2. **Collector Service Failure**
   - **Impact**: Metrics not ingested
   - **Mitigation**: Multiple instances, load balancer
   - **Recovery**: Auto-restart, failover

3. **Message Queue Failure**
   - **Impact**: Metrics buffered, not processed
   - **Mitigation**: Queue replication, persistence
   - **Recovery**: Queue recovery, replay

4. **Database Failure**
   - **Impact**: Cannot store/query metrics
   - **Mitigation**: Replication, backups
   - **Recovery**: Failover to replica

5. **Network Partition**
   - **Impact**: Agents cannot send metrics
   - **Mitigation**: Local buffering, retry
   - **Recovery**: Automatic reconnection

---

## Trade-offs & Design Decisions

### 1. Push vs Pull Model

**Decision**: Push model (agents push metrics)

**Trade-off**:
- **Pros**: Lower latency, real-time, scalable
- **Cons**: More complex agent management

**Rationale**: Push model provides better real-time capabilities and scales better.

### 2. Time-Series DB vs Relational DB

**Decision**: Time-Series DB (InfluxDB/TimescaleDB)

**Trade-off**:
- **Pros**: Optimized for time-series, better compression, faster queries
- **Cons**: Less flexible than relational DB

**Rationale**: Time-series DBs are optimized for this use case.

### 3. Real-time vs Batch Processing

**Decision**: Hybrid (real-time for recent, batch for historical)

**Trade-off**:
- **Pros**: Balance between latency and cost
- **Cons**: More complex architecture

**Rationale**: Real-time for recent data, batch for cost-effective historical processing.

### 4. Data Retention

**Decision**: Tiered retention (hot/warm/cold)

**Trade-off**:
- **Pros**: Cost-effective, balances performance and cost
- **Cons**: More complex query routing

**Rationale**: Most queries are for recent data, older data accessed less frequently.

---

## Interview Discussion Points

### Key Topics

1. **High-Volume Ingestion**
   - How do you handle 1M+ metrics/second?
   - How do you prevent data loss?
   - How do you handle backpressure?

2. **Storage Efficiency**
   - How do you compress time-series data?
   - How do you downsample data?
   - How do you manage retention?

3. **Query Performance**
   - How do you optimize queries?
   - How do you handle complex aggregations?
   - How do you cache query results?

4. **Scalability**
   - How do you scale horizontally?
   - How do you partition data?
   - How do you handle hotspots?

5. **Reliability**
   - How do you ensure no data loss?
   - How do you handle failures?
   - How do you recover from failures?

### Common Questions

**Q: How do you handle 1 million metrics per second?**

**A:**
- Multiple Collector Service instances behind load balancer
- Kafka for buffering and load distribution
- Multiple Aggregator Service instances consuming in parallel
- Database sharding and partitioning
- Efficient compression and batching

**Q: How do you ensure no data loss?**

**A:**
- Kafka provides durability (replication)
- Agent retries with exponential backoff
- Local buffering on agents
- Database replication
- Regular backups

**Q: How do you optimize storage costs?**

**A:**
- Compression (Gorilla algorithm)
- Downsampling older data
- Tiered storage (hot/warm/cold)
- Retention policies
- Efficient data structures

---

## High-Level Design (HLD)

### System Overview

The metrics collection system follows a distributed stream processing architecture:

1. **Agent Layer**: Collects metrics from servers
2. **Ingestion Layer**: Receives and validates metrics
3. **Message Queue**: Buffers metrics for processing (Kafka)
4. **Processing Layer**: Aggregates, downsamples, compresses metrics
5. **Storage Layer**: Time-series database (hot/warm/cold tiers)
6. **Query Layer**: Serves metric queries with low latency

### Component Architecture

**Core Components:**
- **Collector Service**: Validates and routes metrics
- **Aggregator Service**: Pre-aggregates metrics, downsamples
- **Storage Service**: Writes to time-series database
- **Query Service**: Handles metric queries, aggregations

---

## Low-Level Design (LLD)

### Metrics Collector Implementation

```python
class MetricsCollector:
    def __init__(self, kafka_producer, rate_limiter):
        self.kafka = kafka_producer
        self.rate_limiter = rate_limiter
    
    def collect_metrics(self, metrics: list, server_id: str):
        # Rate limiting per server
        if not self.rate_limiter.check(server_id):
            raise RateLimitExceededError()
        
        # Validate metrics
        validated_metrics = []
        for metric in metrics:
            if self.validate_metric(metric):
                validated_metrics.append(metric)
        
        # Publish to Kafka (partitioned by server_id)
        for metric in validated_metrics:
            self.kafka.send('metrics', {
                'server_id': server_id,
                'metric': metric
            }, key=server_id)
        
        return {'ingested': len(validated_metrics), 'failed': len(metrics) - len(validated_metrics)}
```

### Aggregator Service Implementation

```python
class MetricsAggregator:
    def __init__(self, timescale_client, redis_client):
        self.timescale = timescale_client
        self.redis = redis_client
    
    def aggregate_metrics(self, metrics: list):
        # Group by metric name and time window
        grouped = {}
        for metric in metrics:
            key = (metric['metric_name'], self.get_time_window(metric['timestamp']))
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(metric)
        
        # Aggregate each group
        for (metric_name, time_window), metric_list in grouped.items():
            aggregated = self.aggregate_group(metric_name, metric_list)
            
            # Write to database
            self.timescale.execute(
                """
                INSERT INTO metrics (time, metric_name, value, server_id, tags)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT (time, metric_name, server_id) 
                DO UPDATE SET value = ?
                """,
                [time_window, metric_name, aggregated['value'], aggregated['server_id'], 
                 json.dumps(aggregated['tags']), aggregated['value']]
            )
    
    def aggregate_group(self, metric_name: str, metrics: list) -> dict:
        # Aggregate based on metric type
        if metrics[0]['metric_type'] == 'gauge':
            # Average for gauge
            value = sum(m['value'] for m in metrics) / len(metrics)
        elif metrics[0]['metric_type'] == 'counter':
            # Sum for counter
            value = sum(m['value'] for m in metrics)
        else:
            value = metrics[-1]['value']  # Last value
        
        return {
            'metric_name': metric_name,
            'value': value,
            'server_id': metrics[0]['tags']['server_id'],
            'tags': metrics[0]['tags']
        }
```

---

## Fault Tolerance

### Collector Resilience

**Multiple Instances:**
- Multiple collector instances
- Load balancer distributes requests
- Health checks every 10 seconds

**Rate Limiting:**
- Per-server rate limiting
- Prevent overload
- Graceful degradation

### Storage Resilience

**Database Replication:**
- TimescaleDB replication
- Read from replicas
- Automatic failover

**Backup Strategy:**
- Periodic backups
- Cross-region replication
- Point-in-time recovery

---

## Optimizations

### Processing Optimization

**Batching:**
- Batch multiple metrics
- Reduce database writes
- Improve throughput

**Compression:**
- Gorilla compression for time-series
- Reduce storage space
- Trade CPU for storage

### Query Optimization

**Indexing:**
- Index on `metric_name, time`
- Index on `server_id, time`
- GIN index on tags

**Caching:**
- Cache frequent queries
- Cache aggregation results
- TTL-based expiration

---

## Failure Safety

### Collector Failure

**Scenario: Collector Service Down**
- **Impact**: Metrics not ingested
- **Mitigation**:
  - Multiple collector instances
  - Agents retry with exponential backoff
  - Local buffering on agents
- **Recovery**:
  - Service recovers
  - Process buffered metrics
  - Resume normal operation

### Storage Failure

**Scenario: Database Unavailable**
- **Impact**: Cannot store metrics
- **Mitigation**:
  - Database replication
  - Queue metrics for later processing
  - Fallback to temporary storage
- **Recovery**:
  - Database recovers
  - Process queued metrics
  - Verify data integrity

---

## Scalability

### Horizontal Scaling

**Collector Scaling:**
- Add more collector instances
- Load balancer distributes load
- Scale independently

**Aggregator Scaling:**
- Multiple aggregator instances
- Kafka consumer groups
- Parallel processing

### Performance Scaling

**Throughput Scaling:**
- Increase Kafka partitions
- Add more processing instances
- Optimize batch sizes

**Query Scaling:**
- Read replicas for queries
- Cache query results
- Optimize database queries

---

**Document Version**: 1.0  
**Last Updated**: January 2024

