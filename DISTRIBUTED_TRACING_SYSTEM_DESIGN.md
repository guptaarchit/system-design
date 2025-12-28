# Design a Distributed Tracing System

## Table of Contents
1. [Overview](#overview)
2. [Requirements](#requirements)
3. [System Architecture](#system-architecture)
4. [Data Models](#data-models)
5. [API Design](#api-design)
6. [Trace Collection Pipeline](#trace-collection-pipeline)
7. [Trace Storage & Query](#trace-storage--query)
8. [Scalability Considerations](#scalability-considerations)
9. [Caching Strategy](#caching-strategy)
10. [Load Balancing](#load-balancing)
11. [Security](#security)
12. [Monitoring & Analytics](#monitoring--analytics)
13. [Capacity Planning](#capacity-planning)
14. [Technology Stack](#technology-stack)
15. [Failure Scenarios & Handling](#failure-scenarios--handling)
16. [Trade-offs & Design Decisions](#trade-offs--design-decisions)
17. [Interview Discussion Points](#interview-discussion-points)

---

## Overview

A distributed tracing system that tracks requests as they flow through multiple services in a microservices architecture. The system must collect trace data, correlate spans across services, store traces efficiently, and provide fast querying capabilities for debugging and performance analysis.

**Key Features:**
- Distributed trace collection
- Span correlation across services
- Trace sampling and filtering
- Trace storage and retrieval
- Trace visualization and analysis
- Performance metrics extraction
- Error tracking and alerting

---

## Requirements

### Functional Requirements

1. **Trace Collection**
   - Collect spans from multiple services
   - Correlate spans into traces
   - Support OpenTelemetry/W3C Trace Context
   - Handle high-volume trace data

2. **Trace Storage**
   - Store traces with efficient indexing
   - Support time-range queries
   - Support service/trace ID lookups
   - Configurable retention policies

3. **Trace Query**
   - Query by trace ID
   - Query by service name
   - Query by time range
   - Query by tags/metadata

4. **Trace Analysis**
   - Calculate service latency
   - Identify bottlenecks
   - Error rate analysis
   - Dependency graph generation

### Non-Functional Requirements

1. **Scalability**
   - Handle 1M+ spans per second
   - Support 10K+ services
   - Horizontal scaling

2. **Performance**
   - Span ingestion: < 10ms latency
   - Trace query: < 500ms (p95)
   - Real-time trace updates

3. **Reliability**
   - No trace loss (for sampled traces)
   - 99.9% uptime
   - Data durability

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Instrumented Services                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Service 1  │  │   Service 2  │  │   Service N  │         │
│  │  (Agent)     │  │  (Agent)     │  │  (Agent)     │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────┬───────────────┬───────────────┬───────────────────┘
             │               │               │
             ▼               ▼               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Collector Layer                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Collector  │  │   Collector  │  │   Collector  │         │
│  │   Service 1  │  │   Service 2  │  │   Service N │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────┬─────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Message Queue                                 │
│              (Kafka)                                            │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Processing Layer                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Span       │  │   Trace      │  │   Index      │         │
│  │   Processor  │  │   Assembler  │  │   Builder    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────┬─────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Storage Layer                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Trace      │  │   Span       │  │   Index      │         │
│  │   Storage    │  │   Storage    │  │   Storage    │         │
│  │ (Cassandra)  │  │ (Cassandra) │  │ (Elasticsearch│        │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Query Layer                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Query      │  │   Analytics  │  │   UI         │         │
│  │   Service    │  │   Service    │  │   Service    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────────────────────────────────────────────┘
```

---

## Data Models

### Span Structure

```json
{
  "span_id": "span_123",
  "trace_id": "trace_abc",
  "parent_span_id": "span_456",
  "service_name": "user-service",
  "operation_name": "get_user",
  "start_time": 1705312800000,
  "duration": 150,
  "tags": {
    "http.method": "GET",
    "http.status_code": 200,
    "db.query": "SELECT * FROM users"
  },
  "logs": [
    {
      "timestamp": 1705312800100,
      "fields": {
        "event": "query_started",
        "query": "SELECT * FROM users WHERE id = 123"
      }
    }
  ]
}
```

### Trace Structure

```json
{
  "trace_id": "trace_abc",
  "spans": [
    {
      "span_id": "span_1",
      "service": "api-gateway",
      "operation": "handle_request",
      "start_time": 1705312800000,
      "duration": 200,
      "children": ["span_2", "span_3"]
    },
    {
      "span_id": "span_2",
      "service": "user-service",
      "operation": "get_user",
      "start_time": 1705312800050,
      "duration": 150,
      "parent": "span_1"
    }
  ],
  "start_time": 1705312800000,
  "duration": 200,
  "service_count": 3
}
```

### Database Schema

#### Spans Table (Cassandra)

```sql
CREATE TABLE spans (
    trace_id text,
    span_id text,
    service_name text,
    operation_name text,
    start_time timestamp,
    duration bigint,
    tags map<text, text>,
    PRIMARY KEY (trace_id, start_time, span_id)
) WITH CLUSTERING ORDER BY (start_time ASC);
```

#### Trace Index (Elasticsearch)

```json
{
  "trace_id": "trace_abc",
  "service_names": ["api-gateway", "user-service"],
  "start_time": 1705312800000,
  "duration": 200,
  "error": false,
  "tags": {
    "user_id": "123",
    "endpoint": "/api/users/123"
  }
}
```

---

## API Design

### Span Ingestion API

```
POST /api/v1/spans
Content-Type: application/json

[
  {
    "span_id": "span_123",
    "trace_id": "trace_abc",
    "service_name": "user-service",
    "operation_name": "get_user",
    "start_time": 1705312800000,
    "duration": 150,
    "tags": {
      "http.method": "GET"
    }
  }
]
```

### Trace Query API

```
GET /api/v1/traces/{trace_id}
GET /api/v1/traces?service=user-service&start_time=1705312800000&end_time=1705316400000
GET /api/v1/traces?trace_id=trace_abc&span_id=span_123
```

---

## Trace Collection Pipeline

### Collection Flow

1. **Service generates span**
2. **Agent collects span**
3. **Span sent to collector**
4. **Collector validates and enqueues**
5. **Processor correlates spans**
6. **Trace assembler builds complete traces**
7. **Index builder creates search indexes**
8. **Storage writes to database**

### Sampling Strategy

```python
class SamplingStrategy:
    def should_sample(self, trace_id: str, service: str) -> bool:
        # Deterministic sampling based on trace_id hash
        hash_value = hash(trace_id) % 100
        sample_rate = self.get_sample_rate(service)
        return hash_value < sample_rate * 100
```

---

## Trace Storage & Query

### Storage Strategy

- **Hot Storage**: Recent traces (last 24 hours) - Fast access
- **Warm Storage**: Older traces (24 hours - 7 days) - Standard access
- **Cold Storage**: Historical traces (7+ days) - Archive

### Query Optimization

- **Index by trace_id**: Fast trace lookup
- **Index by service**: Service-level queries
- **Index by time**: Time-range queries
- **Index by tags**: Tag-based filtering

---

## Optimizations

### Performance Optimizations

#### 1. Trace Sampling Optimization

**Adaptive Sampling:**

```python
class AdaptiveSampler:
    def __init__(self):
        self.sampling_rates = {}  # service -> rate
        self.error_rates = {}  # service -> error_rate
    
    def should_sample(self, trace: Trace) -> bool:
        service = trace.service_name
        
        # Higher sampling rate for error traces
        if trace.has_error:
            return random.random() < 0.1  # 10% of errors
        
        # Adaptive rate based on service load
        base_rate = self.sampling_rates.get(service, 0.01)  # 1% default
        
        # Increase rate if error rate is high
        error_rate = self.error_rates.get(service, 0)
        if error_rate > 0.05:
            base_rate *= 2
        
        return random.random() < base_rate
```

**Head-Based Sampling:**

```python
class HeadBasedSampler:
    def __init__(self):
        self.sampling_decisions = {}  # trace_id -> decision
    
    def sample_at_head(self, trace_id: str, service: str) -> bool:
        # Make sampling decision at first span
        if trace_id not in self.sampling_decisions:
            decision = self.make_sampling_decision(service)
            self.sampling_decisions[trace_id] = decision
        
        return self.sampling_decisions[trace_id]
```

#### 2. Span Compression

**Span Deduplication:**

```python
class SpanDeduplication:
    def __init__(self):
        self.span_signatures = set()
    
    def get_span_signature(self, span: Span) -> str:
        # Create signature from span attributes
        key_attrs = {
            'operation': span.operation_name,
            'service': span.service_name,
            'tags': sorted(span.tags.items())
        }
        return hashlib.md5(json.dumps(key_attrs).encode()).hexdigest()
    
    def is_duplicate(self, span: Span) -> bool:
        signature = self.get_span_signature(span)
        if signature in self.span_signatures:
            return True
        
        self.span_signatures.add(signature)
        return False
```

**Span Compression:**

```python
class SpanCompressor:
    def compress_span(self, span: Span) -> bytes:
        # Remove redundant data
        compressed_span = {
            'id': span.id,
            'trace_id': span.trace_id,
            'operation': span.operation_name,
            'service': span.service_name,
            'start_time': span.start_time,
            'duration': span.duration,
            'tags': span.tags,  # Keep only non-default tags
            'logs': span.logs if span.logs else None  # Omit if empty
        }
        
        # Compress if large
        json_str = json.dumps(compressed_span)
        if len(json_str) > 1024:
            return zlib.compress(json_str.encode(), level=6)
        
        return json_str.encode()
```

#### 3. Trace Storage Optimization

**Trace Indexing:**

```python
class TraceIndexOptimizer:
    def __init__(self):
        self.index = ElasticsearchIndex()
        self.bloom_filter = BloomFilter(capacity=1000000, error_rate=0.01)
    
    async def index_trace(self, trace: Trace):
        # Use bloom filter for fast existence check
        if self.bloom_filter.contains(trace.trace_id):
            return  # Already indexed
        
        # Index trace metadata (not full trace)
        index_doc = {
            'trace_id': trace.trace_id,
            'service': trace.service_name,
            'operation': trace.operation_name,
            'start_time': trace.start_time,
            'duration': trace.duration,
            'error': trace.has_error,
            'tags': trace.tags
        }
        
        await self.index.index('traces', index_doc)
        self.bloom_filter.add(trace.trace_id)
```

**Time-Based Partitioning:**

```python
class TimePartitionOptimizer:
    def get_partition(self, timestamp: int) -> str:
        # Partition by hour
        dt = datetime.fromtimestamp(timestamp / 1000)
        return f"traces_{dt.strftime('%Y%m%d%H')}"
    
    async def store_trace(self, trace: Trace):
        partition = self.get_partition(trace.start_time)
        await self.storage.store(partition, trace.trace_id, trace)
```

#### 4. Query Optimization

**Trace ID Lookup Caching:**

```python
class TraceQueryCache:
    def __init__(self):
        self.cache = LRUCache(max_size=10000, ttl=300)
    
    async def get_trace(self, trace_id: str) -> Optional[Trace]:
        # Check cache first
        cached = self.cache.get(trace_id)
        if cached:
            return cached
        
        # Query storage
        trace = await self.storage.get_trace(trace_id)
        
        if trace:
            self.cache.set(trace_id, trace)
        
        return trace
```

**Aggregation Optimization:**

```python
class AggregationOptimizer:
    async def aggregate_traces(
        self, 
        service: str, 
        time_range: tuple,
        aggregation: str
    ):
        # Use pre-aggregated data if available
        pre_agg = await self.get_pre_aggregated(service, time_range)
        if pre_agg:
            return pre_agg
        
        # Calculate aggregation
        result = await self.calculate_aggregation(service, time_range, aggregation)
        
        # Cache pre-aggregated result
        await self.cache_pre_aggregated(service, time_range, result)
        
        return result
```

### Network Optimizations

#### 1. Batch Span Collection

**Batch Upload:**

```python
class BatchSpanCollector:
    def __init__(self, batch_size: int = 100, flush_interval: float = 1.0):
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.batch = []
        self.last_flush = time.time()
    
    async def collect_span(self, span: Span):
        self.batch.append(span)
        
        # Flush if batch is full or timeout reached
        if len(self.batch) >= self.batch_size:
            await self.flush()
        elif time.time() - self.last_flush > self.flush_interval:
            await self.flush()
    
    async def flush(self):
        if not self.batch:
            return
        
        # Batch upload spans
        await self.upload_batch(self.batch)
        self.batch.clear()
        self.last_flush = time.time()
```

---

## Scalability Considerations

- **Horizontal Scaling**: Multiple collectors and processors
- **Kafka Partitioning**: Partition by trace_id for ordering
- **Database Sharding**: Shard by trace_id or time
- **Sampling**: Reduce data volume with intelligent sampling

---

## Capacity Planning

- **Spans per Second**: 1M spans/second
- **Traces per Second**: 100K traces/second (assuming 10 spans/trace)
- **Storage**: 1KB per span × 1M spans/sec × 86,400 = 86.4TB/day
- **Retention**: 7 days hot, 30 days warm = ~2.5PB

---

## Technology Stack

- **Collectors**: Go, Java
- **Message Queue**: Kafka
- **Storage**: Cassandra, Elasticsearch
- **Processing**: Apache Flink, Kafka Streams

---

## Interview Discussion Points

1. **Sampling**: How do you handle high-volume traces?
2. **Correlation**: How do you correlate spans across services?
3. **Storage**: How do you store and query traces efficiently?
4. **Performance**: How do you minimize overhead on services?

---

**Document Version**: 1.0  
**Last Updated**: January 2024

