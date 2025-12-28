# Distributed Metrics Logging and Aggregation System Design

## Table of Contents
1. [Overview](#overview)
2. [Requirements](#requirements)
3. [System Architecture](#system-architecture)
4. [Database Design](#database-design)
5. [API Design](#api-design)
6. [Metrics Collection](#metrics-collection)
7. [Metrics Aggregation](#metrics-aggregation)
8. [Time-Series Storage](#time-series-storage)
9. [Query Engine](#query-engine)
10. [Scalability Considerations](#scalability-considerations)
11. [Caching Strategy](#caching-strategy)
12. [Load Balancing](#load-balancing)
13. [Security](#security)
14. [Monitoring & Analytics](#monitoring--analytics)
15. [Deployment Strategy](#deployment-strategy)
16. [Capacity Planning](#capacity-planning)
17. [Technology Stack](#technology-stack)
18. [Failure Scenarios & Handling](#failure-scenarios--handling)
19. [Trade-offs & Design Decisions](#trade-offs--design-decisions)
20. [Interview Discussion Points](#interview-discussion-points)

---

## Overview

A distributed metrics logging and aggregation system that collects, stores, and queries time-series metrics from millions of services. The system must handle high write throughput, provide low-latency queries, and support real-time alerting.

**Key Features:**
- High-throughput metrics ingestion
- Real-time and batch aggregation
- Time-series storage and querying
- Multi-dimensional metrics (tags/labels)
- Downsampling and retention policies
- Alerting and anomaly detection
- Dashboard visualization
- Multi-tenant support

---

## Requirements

### Functional Requirements

1. **Metrics Ingestion**
   - Accept metrics from millions of services
   - Support multiple metric types (counter, gauge, histogram, summary)
   - Handle high write throughput (millions of metrics/second)
   - Support multiple protocols (HTTP, gRPC, StatsD, Prometheus)

2. **Metrics Storage**
   - Store time-series data efficiently
   - Support high cardinality (millions of unique time series)
   - Compression and downsampling
   - Configurable retention policies

3. **Metrics Aggregation**
   - Real-time aggregation (1s, 5s, 1min intervals)
   - Batch aggregation (hourly, daily)
   - Multiple aggregation functions (sum, avg, min, max, count)
   - Group by dimensions (tags/labels)

4. **Querying**
   - Time-range queries
   - Multi-dimensional filtering
   - Aggregation queries
   - Downsampling queries
   - Sub-second query latency

5. **Alerting**
   - Real-time alert evaluation
   - Multiple alert conditions (threshold, rate, anomaly)
   - Alert routing and notification
   - Alert deduplication

6. **Visualization**
   - Dashboard creation
   - Graph rendering
   - Real-time updates

### Non-Functional Requirements

1. **Scalability**
   - Handle 10M+ metrics/second ingestion
   - Support 100M+ unique time series
   - 99.9% uptime
   - Horizontal scaling

2. **Performance**
   - Write latency: < 10ms (p99)
   - Query latency: < 100ms (p95), < 500ms (p99)
   - Real-time aggregation: < 1 second delay

3. **Availability**
   - Multi-region deployment
   - Automatic failover
   - Data replication
   - Zero data loss

4. **Durability**
   - No data loss
   - Backup and recovery
   - Point-in-time recovery

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Metrics Producers                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │ Service  │  │ Service  │  │ Service  │  │ Service  │     │
│  │    1     │  │    2     │  │    3     │  │    N     │     │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘     │
└───────┼─────────────┼─────────────┼─────────────┼───────────┘
        │             │             │             │
        └─────────────┴─────────────┴─────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│              Metrics Collection Layer                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │Collector │  │Collector │  │Collector │  │Collector │   │
│  │  Agent   │  │  Agent   │  │  Agent   │  │  Agent   │   │
│  │  (SDK)   │  │  (SDK)   │  │  (SDK)   │  │  (SDK)   │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼──────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│              Load Balancer / API Gateway                   │
└───────────────────────────┬───────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Region 1   │  │   Region 2   │  │   Region N   │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                  │
       ▼                 ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│              Ingestion Service Layer                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │Ingestion │  │Ingestion │  │Ingestion │  │Ingestion │  │
│  │ Service  │  │ Service  │  │ Service  │  │ Service  │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
└───────┼─────────────┼─────────────┼─────────────┼──────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│              Message Queue (Kafka)                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  Topic   │  │  Topic   │  │  Topic   │  │  Topic   │  │
│  │(Metrics) │  │(Metrics) │  │(Metrics) │  │(Metrics) │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
└───────┼─────────────┼─────────────┼─────────────┼──────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│              Aggregation Service Layer                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │Real-time │  │Real-time │  │  Batch   │  │  Batch   │  │
│  │Aggregator│  │Aggregator│  │Aggregator│  │Aggregator│  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
└───────┼─────────────┼─────────────┼─────────────┼──────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│              Time-Series Storage                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │InfluxDB  │  │TimescaleDB│ │  ClickHouse│ │  Cassandra│ │
│  │          │  │          │  │          │  │          │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼──────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│              Query Service Layer                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Query   │  │  Query   │  │  Query   │  │  Query   │   │
│  │ Service  │  │ Service  │  │ Service  │  │ Service  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼──────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│              Caching Layer (Redis)                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Redis   │  │  Redis   │  │  Redis   │  │  Redis   │   │
│  │ Cluster  │  │ Cluster  │  │ Cluster  │  │ Cluster  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼──────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│              Alerting Service                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Alert   │  │  Alert   │  │Notification│ │Notification│ │
│  │ Evaluator│  │ Evaluator│  │ Service  │  │ Service  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Component Details

#### 1. Metrics Collection Layer
- **Collector Agents**: Lightweight SDKs deployed with services
- **Protocols**: HTTP, gRPC, StatsD, Prometheus
- **Responsibilities**:
  - Collect metrics from services
  - Batch and buffer metrics
  - Send to ingestion service

#### 2. Ingestion Service
- **Technology**: Go, Java, or Rust (high performance)
- **Responsibilities**:
  - Accept metrics from collectors
  - Validate metrics
  - Route to Kafka topics
  - Rate limiting per tenant

#### 3. Message Queue (Kafka)
- **Topics**: Partitioned by metric name or tenant
- **Responsibilities**:
  - Buffer metrics
  - Enable parallel processing
  - Provide replay capability

#### 4. Aggregation Service
- **Real-time Aggregators**: Stream processing (Flink, Kafka Streams)
- **Batch Aggregators**: Spark, Flink batch jobs
- **Responsibilities**:
  - Aggregate metrics by time windows
  - Group by dimensions
  - Calculate aggregations (sum, avg, min, max)

#### 5. Time-Series Storage
- **InfluxDB**: High write throughput
- **TimescaleDB**: PostgreSQL extension, SQL queries
- **ClickHouse**: Columnar storage, fast aggregations
- **Cassandra**: High cardinality support

#### 6. Query Service
- **Technology**: Go or Java
- **Responsibilities**:
  - Execute queries
  - Cache results
  - Downsample queries
  - Multi-storage query federation

#### 7. Alerting Service
- **Alert Evaluator**: Evaluate alert rules
- **Notification Service**: Send alerts (email, Slack, PagerDuty)

---

## Database Design

### Time-Series Schema (InfluxDB)

#### Metrics Table Structure
```
Measurement: metrics
Tags:
  - metric_name (e.g., "cpu_usage")
  - host (e.g., "server-01")
  - service (e.g., "api-service")
  - environment (e.g., "production")
  - region (e.g., "us-east-1")
Fields:
  - value (float64)
  - count (int64)  // for histograms
Timestamp: Unix timestamp (nanoseconds)
```

#### Example Data Point
```
cpu_usage,host=server-01,service=api-service,environment=production value=75.5 1609459200000000000
```

### Relational Schema (TimescaleDB)

#### Metrics Table
```sql
CREATE TABLE metrics (
    time TIMESTAMPTZ NOT NULL,
    metric_name VARCHAR(255) NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    tags JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (time, metric_name, tags)
);

-- Convert to hypertable for time-series optimization
SELECT create_hypertable('metrics', 'time');

-- Indexes
CREATE INDEX idx_metric_name ON metrics(metric_name);
CREATE INDEX idx_tags ON metrics USING GIN(tags);
CREATE INDEX idx_time_metric ON metrics(time DESC, metric_name);
```

#### Aggregated Metrics Table
```sql
CREATE TABLE aggregated_metrics (
    time TIMESTAMPTZ NOT NULL,
    metric_name VARCHAR(255) NOT NULL,
    aggregation_type VARCHAR(50) NOT NULL,  -- 'sum', 'avg', 'min', 'max', 'count'
    window_size INTERVAL NOT NULL,  -- '1s', '5s', '1m', '1h', '1d'
    value DOUBLE PRECISION NOT NULL,
    tags JSONB,
    PRIMARY KEY (time, metric_name, aggregation_type, window_size, tags)
);

SELECT create_hypertable('aggregated_metrics', 'time');
```

#### Alert Rules Table
```sql
CREATE TABLE alert_rules (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    metric_name VARCHAR(255) NOT NULL,
    condition_type VARCHAR(50) NOT NULL,  -- 'threshold', 'rate', 'anomaly'
    condition_config JSONB NOT NULL,
    evaluation_window INTERVAL NOT NULL,
    severity VARCHAR(20) NOT NULL,  -- 'critical', 'warning', 'info'
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## API Design

### RESTful API Endpoints

#### 1. Metrics Ingestion

**Write Metrics**
```
POST /api/v1/metrics/write
Content-Type: application/json

Request:
{
    "metrics": [
        {
            "metric": "cpu_usage",
            "value": 75.5,
            "timestamp": 1609459200,
            "tags": {
                "host": "server-01",
                "service": "api-service",
                "environment": "production"
            }
        },
        {
            "metric": "memory_usage",
            "value": 60.2,
            "timestamp": 1609459200,
            "tags": {
                "host": "server-01",
                "service": "api-service"
            }
        }
    ]
}

Response:
{
    "success": true,
    "metrics_written": 2
}
```

**Write Metrics (Prometheus Format)**
```
POST /api/v1/metrics/write/prometheus
Content-Type: text/plain

cpu_usage{host="server-01",service="api-service"} 75.5 1609459200
memory_usage{host="server-01",service="api-service"} 60.2 1609459200
```

#### 2. Query Metrics

**Query Metrics**
```
GET /api/v1/metrics/query?metric=cpu_usage&start=1609459200&end=1609462800&aggregation=avg&window=1m

Response:
{
    "metric": "cpu_usage",
    "data_points": [
        {
            "time": "2024-01-15T10:00:00Z",
            "value": 75.5
        },
        {
            "time": "2024-01-15T10:01:00Z",
            "value": 76.2
        }
    ],
    "aggregation": "avg",
    "window": "1m"
}
```

**Query with Filters**
```
POST /api/v1/metrics/query
Content-Type: application/json

Request:
{
    "metric": "cpu_usage",
    "start": "2024-01-15T10:00:00Z",
    "end": "2024-01-15T11:00:00Z",
    "filters": {
        "host": "server-01",
        "environment": "production"
    },
    "aggregation": "avg",
    "window": "5m"
}

Response:
{
    "metric": "cpu_usage",
    "data_points": [...],
    "aggregation": "avg",
    "window": "5m"
}
```

#### 3. Alert Management

**Create Alert Rule**
```
POST /api/v1/alerts/rules
Content-Type: application/json

Request:
{
    "name": "High CPU Usage",
    "metric": "cpu_usage",
    "condition": {
        "type": "threshold",
        "operator": ">",
        "value": 80.0
    },
    "evaluation_window": "5m",
    "severity": "critical",
    "notifications": ["email", "slack"]
}

Response:
{
    "success": true,
    "alert_rule_id": "alert_123"
}
```

**List Alerts**
```
GET /api/v1/alerts?status=active

Response:
{
    "alerts": [
        {
            "id": "alert_123",
            "name": "High CPU Usage",
            "status": "firing",
            "severity": "critical",
            "fired_at": "2024-01-15T10:30:00Z"
        }
    ]
}
```

---

## Data Flow Diagrams

### Metrics Ingestion Flow

```
Service Emits Metric
    │
    ▼
Collector Agent (SDK)
    │
    ├─ Batch Metrics (Every 10s or 100 metrics)
    ├─ Compress Metrics
    │
    ▼
Ingestion Service
    │
    ├─ Validate Metrics
    ├─ Rate Limit (Per Tenant)
    ├─ Enrich with Metadata
    │
    ▼
Kafka Topic (Partitioned by Metric Name)
    │
    ├─ Partition 0: cpu_usage
    ├─ Partition 1: memory_usage
    └─ Partition N: other_metrics
    │
    ▼
Real-time Aggregator (Kafka Streams/Flink)
    │
    ├─ Aggregate by 1s, 5s, 1m windows
    ├─ Group by Tags
    └─ Calculate Aggregations
    │
    ▼
Time-Series Storage (InfluxDB/TimescaleDB)
    │
    └─ Write Aggregated Metrics
```

### Query Flow

```
User Query Request
    │
    ▼
Query Service
    │
    ├─ Parse Query
    ├─ Check Cache (Redis)
    │   └─ Cache Hit → Return (1-5ms)
    │
    └─ Cache Miss → Continue
        │
        ▼
    Determine Query Strategy
        │
        ├─ Recent Data (< 1 hour) → Real-time Storage
        ├─ Historical Data (> 1 hour) → Aggregated Storage
        └─ Very Old Data (> 30 days) → Downsampled Storage
        │
        ▼
    Execute Query (Parallel)
        │
        ├─ Query Real-time Storage
        ├─ Query Aggregated Storage
        └─ Merge Results
        │
        ▼
    Cache Results (Redis)
        │
        ▼
    Return Results to User
```

---

## Metrics Collection

### Collector Agent (SDK)

**Features:**
- Lightweight (minimal overhead)
- Batching and buffering
- Automatic retry
- Compression
- Multiple protocol support

**Implementation:**
```python
class MetricsCollector:
    def __init__(self, endpoint, batch_size=100, flush_interval=10):
        self.endpoint = endpoint
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.buffer = []
        self.last_flush = time.time()
    
    def record(self, metric_name, value, tags=None, timestamp=None):
        metric = {
            'metric': metric_name,
            'value': value,
            'tags': tags or {},
            'timestamp': timestamp or int(time.time())
        }
        self.buffer.append(metric)
        
        # Flush if buffer is full or time elapsed
        if len(self.buffer) >= self.batch_size:
            self.flush()
        elif time.time() - self.last_flush >= self.flush_interval:
            self.flush()
    
    def flush(self):
        if not self.buffer:
            return
        
        # Send batch to ingestion service
        self.send_metrics(self.buffer)
        self.buffer = []
        self.last_flush = time.time()
```

### Ingestion Service

**Features:**
- High throughput (millions of metrics/sec)
- Validation
- Rate limiting
- Routing to Kafka

**Implementation:**
```python
class IngestionService:
    def ingest_metrics(self, metrics, tenant_id):
        # Rate limiting
        if not self.rate_limiter.allow(tenant_id, len(metrics)):
            raise RateLimitExceededError()
        
        # Validate metrics
        validated_metrics = []
        for metric in metrics:
            if self.validate_metric(metric):
                validated_metrics.append(metric)
        
        # Route to Kafka (partition by metric name)
        for metric in validated_metrics:
            partition = self.get_partition(metric['metric'])
            self.kafka_producer.send(
                topic='metrics',
                partition=partition,
                value=metric
            )
```

---

## Metrics Aggregation

### Real-Time Aggregation

**Technology**: Kafka Streams or Flink

**Aggregation Windows:**
- 1 second
- 5 seconds
- 1 minute

**Aggregation Functions:**
- Sum
- Average
- Min
- Max
- Count
- Percentiles (p50, p95, p99)

**Implementation:**
```python
class RealTimeAggregator:
    def aggregate(self, metrics_stream):
        # Group by metric name and tags
        grouped = metrics_stream.group_by(
            key=lambda m: (m['metric'], tuple(sorted(m['tags'].items())))
        )
        
        # Aggregate by time windows
        aggregated = grouped.window(
            window_size=timedelta(seconds=60)
        ).aggregate(
            sum=lambda acc, m: acc + m['value'],
            count=lambda acc, m: acc + 1,
            min=lambda acc, m: min(acc, m['value']),
            max=lambda acc, m: max(acc, m['value'])
        )
        
        # Write to storage
        aggregated.foreach(self.write_to_storage)
```

### Batch Aggregation

**Technology**: Spark or Flink Batch

**Aggregation Windows:**
- 1 hour
- 1 day
- 1 week

**Use Cases:**
- Historical analysis
- Long-term trends
- Cost optimization (downsampling)

---

## Time-Series Storage

### Storage Options

**InfluxDB:**
- **Pros**: High write throughput, efficient compression
- **Cons**: Limited query flexibility
- **Use Case**: High-frequency metrics

**TimescaleDB:**
- **Pros**: SQL queries, PostgreSQL compatibility
- **Cons**: Lower write throughput than InfluxDB
- **Use Case**: Complex queries, relational data

**ClickHouse:**
- **Pros**: Fast aggregations, columnar storage
- **Cons**: Complex setup, limited real-time updates
- **Use Case**: Analytics, reporting

**Cassandra:**
- **Pros**: High cardinality, horizontal scaling
- **Cons**: No native time-series optimization
- **Use Case**: Very high cardinality metrics

### Storage Strategy

**Multi-Tier Storage:**
1. **Hot Storage** (Last 24 hours): InfluxDB
2. **Warm Storage** (24 hours - 30 days): TimescaleDB
3. **Cold Storage** (30+ days): ClickHouse (downsampled)

---

## Query Engine

### Query Processing

**Query Types:**
1. **Raw Queries**: Return raw data points
2. **Aggregation Queries**: Return aggregated data
3. **Downsampling Queries**: Return downsampled data
4. **Multi-Metric Queries**: Query multiple metrics

**Query Optimization:**
- **Caching**: Cache frequent queries
- **Downsampling**: Automatically downsample long-range queries
- **Parallel Execution**: Query multiple partitions in parallel
- **Index Usage**: Use indexes for fast filtering

**Implementation:**
```python
class QueryService:
    def query(self, query_request):
        # Check cache
        cache_key = self.get_cache_key(query_request)
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        # Determine storage tier
        storage = self.select_storage(query_request.start, query_request.end)
        
        # Execute query
        results = storage.query(query_request)
        
        # Cache results
        self.cache.set(cache_key, results, ttl=60)
        
        return results
    
    def select_storage(self, start, end):
        duration = end - start
        if duration < timedelta(hours=24):
            return self.hot_storage  # InfluxDB
        elif duration < timedelta(days=30):
            return self.warm_storage  # TimescaleDB
        else:
            return self.cold_storage  # ClickHouse
```

---

## Optimizations

### Performance Optimizations

#### 1. Metrics Ingestion Optimization

**Batch Ingestion:**

```python
class BatchIngester:
    def __init__(self, batch_size: int = 1000, flush_interval: float = 1.0):
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.batch = []
        self.last_flush = time.time()
    
    async def ingest_metric(self, metric: Metric):
        self.batch.append(metric)
        
        # Flush if batch is full or timeout reached
        if len(self.batch) >= self.batch_size:
            await self.flush()
        elif time.time() - self.last_flush > self.flush_interval:
            await self.flush()
    
    async def flush(self):
        if not self.batch:
            return
        
        # Batch write to Kafka
        await self.kafka_producer.send_batch(self.batch)
        self.batch.clear()
        self.last_flush = time.time()
```

**Metric Deduplication:**

```python
class MetricDeduplicator:
    def __init__(self):
        self.recent_metrics = {}  # (name, labels, timestamp) -> metric
        self.ttl = 60  # 1 minute
    
    def deduplicate(self, metric: Metric) -> Optional[Metric]:
        key = (metric.name, tuple(sorted(metric.labels.items())), metric.timestamp)
        
        # Check if duplicate
        if key in self.recent_metrics:
            return None  # Duplicate
        
        # Store metric
        self.recent_metrics[key] = metric
        
        # Cleanup old metrics
        self.cleanup_old_metrics()
        
        return metric
```

#### 2. Aggregation Optimization

**Pre-Aggregation:**

```python
class PreAggregator:
    def __init__(self):
        self.aggregation_windows = {
            '1m': 60,
            '5m': 300,
            '1h': 3600
        }
    
    async def pre_aggregate(self, metrics: list):
        # Aggregate metrics by time window
        for window_name, window_seconds in self.aggregation_windows.items():
            aggregated = self.aggregate_by_window(metrics, window_seconds)
            await self.store_pre_aggregated(window_name, aggregated)
```

**Incremental Aggregation:**

```python
class IncrementalAggregator:
    def __init__(self):
        self.aggregation_state = {}  # (metric_name, labels, window) -> state
    
    async def aggregate_incremental(self, metric: Metric):
        key = (metric.name, tuple(sorted(metric.labels.items())), '1m')
        
        if key not in self.aggregation_state:
            self.aggregation_state[key] = {
                'sum': 0,
                'count': 0,
                'min': float('inf'),
                'max': float('-inf')
            }
        
        state = self.aggregation_state[key]
        state['sum'] += metric.value
        state['count'] += 1
        state['min'] = min(state['min'], metric.value)
        state['max'] = max(state['max'], metric.value)
```

#### 3. Storage Optimization

**Downsampling:**

```python
class Downsampler:
    async def downsample_metrics(self, time_series: list, target_resolution: int):
        # Downsample old data to reduce storage
        if len(time_series) > 10000:  # Threshold
            # Keep every Nth point
            step = len(time_series) // target_resolution
            downsampled = time_series[::step]
            return downsampled
        
        return time_series
```

**Compression:**

```python
class TimeSeriesCompressor:
    def compress_time_series(self, time_series: list) -> bytes:
        # Use delta encoding for timestamps
        timestamps = [p['timestamp'] for p in time_series]
        values = [p['value'] for p in time_series]
        
        # Delta encode timestamps
        timestamp_deltas = [timestamps[0]] + [
            timestamps[i] - timestamps[i-1] 
            for i in range(1, len(timestamps))
        ]
        
        # Compress
        data = {
            'timestamps': timestamp_deltas,
            'values': values
        }
        
        return zlib.compress(json.dumps(data).encode(), level=6)
```

#### 4. Query Optimization

**Query Result Caching:**

```python
class QueryCache:
    def __init__(self):
        self.cache = LRUCache(max_size=1000, ttl=60)
    
    async def query_with_cache(
        self, 
        query: str, 
        time_range: tuple,
        step: int
    ):
        cache_key = f"{query}:{time_range}:{step}"
        
        # Check cache
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        # Execute query
        result = await self.execute_query(query, time_range, step)
        
        # Cache result
        self.cache.set(cache_key, result)
        
        return result
```

**Parallel Query Execution:**

```python
class ParallelQueryExecutor:
    async def execute_parallel_queries(self, queries: list) -> list:
        # Execute multiple queries in parallel
        tasks = [self.execute_query(q) for q in queries]
        results = await asyncio.gather(*tasks)
        return results
```

---

## Scalability Considerations

### 1. Horizontal Scaling

**Ingestion Service:**
- Stateless, scale horizontally
- Load balancer distributes traffic
- Kafka partitions enable parallel processing

**Aggregation Service:**
- Kafka Streams/Flink auto-scales
- Partition-based parallelism

**Query Service:**
- Stateless, scale horizontally
- Cache reduces database load

### 2. Partitioning Strategy

**Kafka Partitioning:**
- Partition by metric name (hash)
- Enables parallel processing
- Maintains ordering per metric

**Storage Partitioning:**
- Partition by time (time-based)
- Partition by metric name (metric-based)
- Partition by tenant (multi-tenant)

### 3. Cardinality Management

**Challenge**: High cardinality (millions of unique time series)

**Solutions:**
- **Tag Cardinality Limits**: Limit number of unique tag values
- **Cardinality Estimation**: Monitor and alert on high cardinality
- **Cardinality Reduction**: Aggregate high-cardinality metrics

---

## Caching Strategy

### Cache Architecture

```
Query Request
    │
    ▼
Redis Cache
    │
    ├─ Cache Hit → Return (1-5ms)
    │
    └─ Cache Miss → Query Storage
        │
        ▼
    Return + Cache Results
```

### Cache Keys

```
query:{metric}:{start}:{end}:{aggregation}:{window} → Query results
alert:{alert_id}:{time} → Alert evaluation results
```

### Cache Invalidation

**TTL-Based:**
- Query results: 60 seconds
- Alert results: 30 seconds

**Event-Based:**
- Invalidate on metric updates
- Invalidate on alert rule changes

---

## Load Balancing

### Load Balancer Architecture

```
Metrics Producers
    │
    ▼
Load Balancer (Round-Robin)
    │
    ├─ Ingestion Service 1
    ├─ Ingestion Service 2
    ├─ Ingestion Service 3
    └─ Ingestion Service N
```

### Load Balancing Strategies

1. **Round-Robin**: Equal distribution
2. **Least Connections**: Route to server with fewest connections
3. **Consistent Hashing**: Route by metric name (maintains ordering)

---

## Security

### 1. Authentication & Authorization

**Authentication:**
- API keys
- OAuth 2.0
- mTLS

**Authorization:**
- Role-based access control (RBAC)
- Tenant isolation
- Metric-level permissions

### 2. Data Privacy

**Encryption:**
- Encrypt data at rest
- Encrypt data in transit (TLS 1.3)

**Data Isolation:**
- Multi-tenant isolation
- Tenant-specific storage

### 3. Rate Limiting

**Rate Limits:**
- Per tenant: 1M metrics/minute
- Per API key: 100K metrics/minute
- Per IP: 10K metrics/minute

---

## Monitoring & Analytics

### Key Metrics

**System Metrics:**
- Ingestion rate (metrics/second)
- Query latency (p50, p95, p99)
- Storage write latency
- Cache hit rate
- Error rate

**Business Metrics:**
- Total metrics ingested
- Unique time series
- Query volume
- Alert firing rate

### Monitoring Pipeline

```
System Metrics → Metrics System → Dashboards → Alerts
```

---

## Deployment Strategy

### Infrastructure

**Cloud Provider**: AWS, GCP, or Azure

**Components:**
- **Compute**: Kubernetes (EKS/GKE)
- **Message Queue**: Kafka (MSK) or Confluent Cloud
- **Storage**: InfluxDB, TimescaleDB, ClickHouse
- **Cache**: Redis (ElastiCache)
- **Monitoring**: Prometheus, Grafana

### Multi-Region Deployment

```
Region 1          Region 2          Region 3
┌─────────┐      ┌─────────┐      ┌─────────┐
│Ingestion│      │Ingestion│      │Ingestion│
│ Service │      │ Service │      │ Service │
└────┬────┘      └────┬────┘      └────┬────┘
     │                │                │
     └────────────────┼────────────────┘
                      │
                      ▼
              Kafka Cluster
                      │
                      ▼
              Storage (Replicated)
```

---

## Capacity Planning

### Storage Estimates

**Raw Metrics:**
- 10M metrics/second
- 10M × 100 bytes = 1 GB/second
- 1 GB/s × 86400 = 86.4 TB/day
- **Total Raw: ~86 TB/day**

**After Aggregation (1 minute):**
- 10M metrics/sec → 600K metrics/min
- 600K × 100 bytes = 60 MB/min
- 60 MB/min × 1440 = 86.4 GB/day
- **Total Aggregated: ~86 GB/day**

**After Compression:**
- Compression ratio: 10:1
- **Total Compressed: ~8.6 GB/day**

### Compute Requirements

**Ingestion Service:**
- 10M metrics/second
- Each metric: ~1ms processing
- Required servers: 10M / (1000/1) = 10,000 servers
- With 50% utilization: ~5,000 servers

**Aggregation Service:**
- 10M metrics/second input
- After aggregation: 600K metrics/min = 10K metrics/sec
- Each aggregation: ~10ms
- Required servers: 10K / (1000/10) = 100 servers

**Query Service:**
- 1K queries/second
- Each query: ~50ms (with caching)
- Required servers: 1K / (1000/50) = 50 servers

**Total Compute: ~5,150 servers**

---

## Technology Stack

### Recommended Stack (AWS)

**Compute:**
- **Container Orchestration**: Kubernetes (EKS)
- **Serverless**: AWS Lambda for batch aggregation

**Message Queue:**
- **Streaming**: Amazon MSK (Kafka) or Confluent Cloud

**Storage:**
- **Time-Series**: InfluxDB Cloud or TimescaleDB Cloud
- **Analytics**: Amazon Timestream or ClickHouse

**Cache:**
- **Distributed Cache**: Amazon ElastiCache (Redis)

**Monitoring:**
- **APM**: AWS X-Ray, Datadog
- **Metrics**: Prometheus + Grafana

---

## Failure Scenarios & Handling

### 1. Ingestion Service Failure

**Scenario:** Ingestion service crashes.

**Impact:** Metrics cannot be ingested.

**Mitigation:**
- **Multiple Instances**: Run multiple ingestion instances
- **Automatic Failover**: Load balancer routes to healthy instances
- **Retry Logic**: Collector agents retry with exponential backoff

### 2. Kafka Failure

**Scenario:** Kafka cluster fails.

**Impact:** Metrics cannot be buffered.

**Mitigation:**
- **Kafka Cluster**: Multiple brokers, replication
- **Local Buffering**: Collector agents buffer locally
- **Fallback Storage**: Write to S3 if Kafka unavailable

### 3. Storage Failure

**Scenario:** Time-series database fails.

**Impact:** Cannot query metrics.

**Mitigation:**
- **Replication**: Replicate data across regions
- **Backup**: Daily backups
- **Multi-Storage**: Use multiple storage systems

### 4. High Cardinality

**Scenario:** Metric with millions of unique tag combinations.

**Impact:** Storage explosion, query performance degradation.

**Mitigation:**
- **Cardinality Limits**: Limit tag cardinality
- **Cardinality Monitoring**: Alert on high cardinality
- **Aggregation**: Pre-aggregate high-cardinality metrics

---

## Trade-offs & Design Decisions

### 1. Storage: InfluxDB vs TimescaleDB

**Decision:** Multi-tier storage (InfluxDB for hot, TimescaleDB for warm).

**Trade-offs:**

| Aspect | InfluxDB | TimescaleDB |
|--------|----------|-------------|
| **Write Throughput** | Very High | High |
| **Query Flexibility** | Limited | Excellent (SQL) |
| **Compression** | Excellent | Good |
| **SQL Support** | Limited | Full |

**Why Multi-Tier:**
- **InfluxDB**: High write throughput for real-time data
- **TimescaleDB**: SQL queries for complex analytics
- **Result**: Best of both worlds

### 2. Aggregation: Real-time vs Batch

**Decision:** Both (real-time for recent data, batch for historical).

**Trade-offs:**

| Approach | Pros | Cons |
|----------|------|------|
| **Real-time** | Low latency | Higher cost |
| **Batch** | Lower cost | Higher latency |

**Why Both:**
- **Real-time**: For dashboards and alerts
- **Batch**: For historical analysis and cost optimization

### 3. Compression: Lossless vs Lossy

**Decision:** Lossy compression for old data, lossless for recent data.

**Trade-offs:**

| Approach | Pros | Cons |
|----------|------|------|
| **Lossless** | No data loss | Lower compression |
| **Lossy** | Higher compression | Data loss |

**Why Lossy for Old Data:**
- **Cost**: Significant storage savings
- **Acceptable**: Old data doesn't need full precision

---

## Interview Discussion Points

### Key Questions to Address

1. **"How do you handle high cardinality metrics?"**
   - **Answer**: 
     - Limit tag cardinality
     - Monitor and alert on high cardinality
     - Pre-aggregate high-cardinality metrics
     - Use sampling for very high cardinality

2. **"How do you ensure no data loss?"**
   - **Answer**:
     - Kafka replication (3x)
     - Storage replication
     - Collector agent local buffering
     - Daily backups

3. **"How do you optimize query performance?"**
   - **Answer**:
     - Aggressive caching
     - Downsampling for long-range queries
     - Indexes on time and tags
     - Parallel query execution

4. **"How do you handle burst traffic?"**
   - **Answer**:
     - Kafka buffers traffic
     - Auto-scaling ingestion services
     - Rate limiting per tenant
     - Graceful degradation

5. **"How do you support multi-tenancy?"**
   - **Answer**:
     - Tenant isolation at storage level
     - Per-tenant rate limiting
     - Tenant-specific retention policies
     - RBAC for access control

---

## References

- [Prometheus Architecture](https://prometheus.io/docs/introduction/overview/)
- [InfluxDB Documentation](https://docs.influxdata.com/)
- [TimescaleDB Documentation](https://docs.timescale.com/)
- [Kafka Streams](https://kafka.apache.org/documentation/streams/)
- [System Design Primer](https://github.com/donnemartin/system-design-primer)

