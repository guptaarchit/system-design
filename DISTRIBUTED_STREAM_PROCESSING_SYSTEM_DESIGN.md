# Distributed Stream Processing System Design (Kafka-like)

## Table of Contents
1. [Overview](#overview)
2. [Requirements](#requirements)
3. [System Architecture](#system-architecture)
4. [Database Design](#database-design)
5. [API Design](#api-design)
6. [Message Storage](#message-storage)
7. [Partitioning & Replication](#partitioning--replication)
8. [Consumer Groups](#consumer-groups)
9. [Scalability Considerations](#scalability-considerations)
10. [Caching Strategy](#caching-strategy)
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

A distributed stream processing system that enables high-throughput, fault-tolerant message streaming. The system must handle millions of messages per second, provide ordering guarantees, support multiple consumers, and ensure durability.

**Key Features:**
- High-throughput message streaming
- Partitioning for parallelism
- Replication for fault tolerance
- Consumer groups for load distribution
- Message ordering within partitions
- At-least-once delivery semantics
- Exactly-once semantics (optional)
- Message retention policies
- Multi-tenant support

---

## Requirements

### Functional Requirements

1. **Message Publishing**
   - Publish messages to topics
   - Support multiple producers per topic
   - Automatic partitioning
   - Batching for efficiency

2. **Message Consumption**
   - Subscribe to topics
   - Consumer groups for load balancing
   - Offset management
   - Multiple consumption patterns (at-least-once, exactly-once)

3. **Topic Management**
   - Create/delete topics
   - Configure partitions
   - Set retention policies
   - Configure replication factor

4. **Partitioning**
   - Automatic partitioning by key
   - Round-robin partitioning
   - Custom partitioning
   - Maintain ordering within partitions

5. **Replication**
   - Replicate partitions across brokers
   - Leader election
   - Automatic failover
   - Consistency guarantees

6. **Consumer Groups**
   - Multiple consumers per group
   - Automatic load balancing
   - Rebalancing on consumer join/leave
   - Offset tracking per group

### Non-Functional Requirements

1. **Scalability**
   - Handle 10M+ messages/second
   - Support 100K+ topics
   - Horizontal scaling
   - Linear performance scaling

2. **Performance**
   - Write latency: < 5ms (p99)
   - Read latency: < 10ms (p99)
   - Throughput: 1M+ messages/second per broker

3. **Durability**
   - No message loss
   - Replication across multiple brokers
   - Persistent storage
   - Configurable retention

4. **Availability**
   - 99.9% uptime
   - Automatic failover
   - Zero-downtime deployments
   - Multi-region support

5. **Consistency**
   - Strong consistency for metadata
   - Eventual consistency for replication
   - Ordering guarantees within partitions

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Producers                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │Producer 1│  │Producer 2│  │Producer 3│  │Producer N│   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼──────────┘
        │             │             │             │
        └─────────────┴─────────────┴─────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│                    Broker Cluster                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Broker 1 │  │ Broker 2 │  │ Broker 3 │  │ Broker N │   │
│  │(Leader)  │  │(Follower)│  │(Follower)│  │(Follower)│   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼──────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│                    Storage Layer                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Local   │  │  Local   │  │  Local   │  │  Local   │   │
│  │  Disk    │  │  Disk    │  │  Disk    │  │  Disk    │   │
│  │(Segments)│  │(Segments)│  │(Segments)│  │(Segments)│   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼──────────┘
        │             │             │             │
        └─────────────┴─────────────┴─────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│                    Consumers                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │Consumer 1│  │Consumer 2│  │Consumer 3│  │Consumer N│   │
│  │(Group A) │  │(Group A) │  │(Group B) │  │(Group B) │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Component Details

#### 1. Broker
- **Responsibilities**:
  - Accept messages from producers
  - Serve messages to consumers
  - Manage partitions
  - Handle replication
  - Store messages on disk

#### 2. Controller
- **Responsibilities**:
  - Manage broker metadata
  - Handle broker failures
  - Leader election
  - Partition assignment
  - Topic creation/deletion

#### 3. Coordinator
- **Responsibilities**:
  - Manage consumer groups
  - Handle consumer join/leave
  - Rebalance partitions
  - Track consumer offsets

#### 4. Storage
- **Segmented Logs**: Append-only log files
- **Index Files**: Offset and timestamp indexes
- **Compaction**: Log compaction for key-value topics

---

## Database Design

### Metadata Storage (ZooKeeper/etcd)

#### Topics Table
```sql
CREATE TABLE topics (
    topic_name VARCHAR(255) PRIMARY KEY,
    num_partitions INT NOT NULL,
    replication_factor INT NOT NULL,
    retention_ms BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Partitions Table
```sql
CREATE TABLE partitions (
    topic_name VARCHAR(255),
    partition_id INT,
    leader_broker_id INT,
    replica_broker_ids JSON,  -- Array of broker IDs
    isr_broker_ids JSON,  -- In-sync replica broker IDs
    PRIMARY KEY (topic_name, partition_id)
);
```

#### Consumer Groups Table
```sql
CREATE TABLE consumer_groups (
    group_id VARCHAR(255) PRIMARY KEY,
    protocol_type VARCHAR(50),
    state VARCHAR(50),  -- 'stable', 'rebalancing'
    coordinator_broker_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Consumer Offsets Table
```sql
CREATE TABLE consumer_offsets (
    group_id VARCHAR(255),
    topic_name VARCHAR(255),
    partition_id INT,
    offset BIGINT,
    metadata TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (group_id, topic_name, partition_id)
);
```

### Message Storage (File System)

#### Segment File Structure
```
topic-partition/
  ├── 00000000000000000000.log  (Segment file)
  ├── 00000000000000000000.index (Offset index)
  ├── 00000000000000000000.timeindex (Timestamp index)
  ├── 00000000000000100000.log
  ├── 00000000000000100000.index
  └── ...
```

**Segment File Format:**
```
Offset | Size | CRC | Magic | Attributes | Key Length | Key | Value Length | Value
```

---

## API Design

### Producer API

**Send Message**
```
POST /api/v1/topics/{topic}/messages
Content-Type: application/json

Request:
{
    "key": "user_123",
    "value": "{\"action\": \"login\", \"timestamp\": 1609459200}",
    "partition": null,  // Auto-partition if null
    "headers": {
        "source": "web-app"
    }
}

Response:
{
    "topic": "user-events",
    "partition": 0,
    "offset": 12345,
    "timestamp": 1609459200000
}
```

**Send Batch**
```
POST /api/v1/topics/{topic}/messages/batch
Content-Type: application/json

Request:
{
    "messages": [
        {"key": "user_123", "value": "..."},
        {"key": "user_456", "value": "..."}
    ]
}

Response:
{
    "results": [
        {"partition": 0, "offset": 12345},
        {"partition": 1, "offset": 67890}
    ]
}
```

### Consumer API

**Subscribe to Topic**
```
POST /api/v1/consumers/{group_id}/subscription
Content-Type: application/json

Request:
{
    "topics": ["user-events", "order-events"],
    "auto_offset_reset": "earliest"  // or "latest"
}

Response:
{
    "success": true,
    "assigned_partitions": [
        {"topic": "user-events", "partition": 0},
        {"topic": "user-events", "partition": 1}
    ]
}
```

**Fetch Messages**
```
GET /api/v1/consumers/{group_id}/messages?max_bytes=1048576&timeout_ms=5000

Response:
{
    "messages": [
        {
            "topic": "user-events",
            "partition": 0,
            "offset": 12345,
            "key": "user_123",
            "value": "...",
            "timestamp": 1609459200000
        }
    ]
}
```

**Commit Offset**
```
POST /api/v1/consumers/{group_id}/offsets
Content-Type: application/json

Request:
{
    "offsets": [
        {
            "topic": "user-events",
            "partition": 0,
            "offset": 12345
        }
    ]
}

Response:
{
    "success": true
}
```

### Admin API

**Create Topic**
```
POST /api/v1/admin/topics
Content-Type: application/json

Request:
{
    "topic": "user-events",
    "num_partitions": 3,
    "replication_factor": 3,
    "config": {
        "retention_ms": 604800000,  // 7 days
        "compression_type": "snappy"
    }
}

Response:
{
    "success": true,
    "topic": "user-events"
}
```

**List Topics**
```
GET /api/v1/admin/topics

Response:
{
    "topics": [
        {
            "name": "user-events",
            "partitions": 3,
            "replication_factor": 3
        }
    ]
}
```

---

## Data Flow Diagrams

### Message Publishing Flow

```
Producer Sends Message
    │
    ▼
Broker (Partition Leader)
    │
    ├─ Validate Topic/Partition
    ├─ Determine Partition (if key provided, hash key; else round-robin)
    │
    ▼
Append to Segment File
    │
    ├─ Write to Log File (.log)
    ├─ Update Index File (.index)
    └─ Update Timestamp Index (.timeindex)
    │
    ▼
Replicate to Followers
    │
    ├─ Send to Follower 1
    ├─ Send to Follower 2
    └─ Wait for ACK (quorum)
    │
    ▼
Return Success to Producer
```

### Message Consumption Flow

```
Consumer Fetches Messages
    │
    ▼
Broker (Partition Leader)
    │
    ├─ Check Consumer Group
    ├─ Get Consumer Offset
    │
    ▼
Read from Segment File
    │
    ├─ Use Index to Find Offset
    ├─ Read Messages from Log
    └─ Return Messages to Consumer
    │
    ▼
Consumer Processes Messages
    │
    ▼
Consumer Commits Offset
    │
    ├─ Update Offset in Coordinator
    └─ Persist Offset
```

### Consumer Rebalancing Flow

```
Consumer Joins Group
    │
    ▼
Coordinator Detects Change
    │
    ▼
Initiate Rebalancing
    │
    ├─ Revoke Current Partitions
    ├─ Calculate New Partition Assignment
    │   └─ Distribute Partitions Among Consumers
    │
    ▼
Assign Partitions to Consumers
    │
    ├─ Consumer 1: Partitions 0, 1
    ├─ Consumer 2: Partitions 2, 3
    └─ Consumer 3: Partitions 4, 5
    │
    ▼
Consumers Resume Consumption
```

---

## Message Storage

### Segmented Log Architecture

**Segment Files:**
- **Log File**: Append-only log of messages
- **Index File**: Maps offset to file position
- **Timestamp Index**: Maps timestamp to offset

**Segment Rotation:**
- Rotate when segment reaches size limit (e.g., 1GB)
- Rotate when time limit reached (e.g., 7 days)
- Old segments deleted based on retention policy

**Log Compaction:**
- For key-value topics
- Keep only latest value per key
- Reduces storage for update-heavy topics

**Implementation:**
```python
class Segment:
    def __init__(self, base_offset, segment_size_limit=1*1024*1024*1024):
        self.base_offset = base_offset
        self.log_file = open(f"{base_offset}.log", "ab")
        self.index_file = open(f"{base_offset}.index", "ab")
        self.size_limit = segment_size_limit
    
    def append(self, offset, message):
        # Write to log file
        position = self.log_file.tell()
        self.log_file.write(self.serialize(message))
        
        # Update index (every N messages or every N bytes)
        if offset % 1000 == 0:  # Index every 1000 messages
            self.index_file.write(struct.pack('>Q', offset, position))
        
        # Check if segment should be rotated
        if self.log_file.tell() >= self.size_limit:
            self.rotate()
    
    def read(self, offset, max_bytes):
        # Find segment containing offset
        if offset < self.base_offset:
            return None
        
        # Use index to find position
        position = self.find_position(offset)
        
        # Read from log file
        self.log_file.seek(position)
        return self.log_file.read(max_bytes)
```

---

## Partitioning & Replication

### Partitioning Strategy

**Partitioning Methods:**
1. **Key-Based**: Hash key to determine partition (maintains ordering per key)
2. **Round-Robin**: Distribute evenly across partitions
3. **Custom**: User-defined partitioner

**Partition Assignment:**
- Producers choose partition based on key
- If no key, round-robin across partitions
- Maintains ordering within partition

### Replication

**Replication Factor:**
- Typically 3 (1 leader + 2 followers)
- Configurable per topic

**Leader Election:**
- Controller elects leader
- Leader handles all reads/writes
- Followers replicate from leader

**In-Sync Replicas (ISR):**
- Replicas that are up-to-date with leader
- Write requires quorum (majority of ISR)
- Ensures durability

**Implementation:**
```python
class Partition:
    def __init__(self, topic, partition_id, replication_factor=3):
        self.topic = topic
        self.partition_id = partition_id
        self.replication_factor = replication_factor
        self.leader_broker_id = None
        self.replica_broker_ids = []
        self.isr_broker_ids = []
    
    def write(self, message):
        # Leader writes to local segment
        if self.is_leader():
            self.local_segment.append(message)
            
            # Replicate to followers
            acks = 0
            for follower_id in self.isr_broker_ids:
                if follower_id != self.leader_broker_id:
                    if self.replicate_to_follower(follower_id, message):
                        acks += 1
            
            # Require quorum (majority)
            if acks >= len(self.isr_broker_ids) // 2:
                return True
        
        return False
```

---

## Consumer Groups

### Consumer Group Architecture

**Consumer Group:**
- Multiple consumers sharing work
- Each partition consumed by one consumer in group
- Automatic load balancing

**Partition Assignment:**
- **Range**: Assign consecutive partitions
- **Round-Robin**: Distribute evenly
- **Sticky**: Minimize reassignment

**Rebalancing:**
- Triggered on consumer join/leave
- Revokes current assignments
- Reassigns partitions
- Consumers resume consumption

**Offset Management:**
- Track offset per partition per group
- Commit offset after processing
- Auto-commit or manual commit

**Implementation:**
```python
class ConsumerGroup:
    def __init__(self, group_id, coordinator):
        self.group_id = group_id
        self.coordinator = coordinator
        self.consumers = []
        self.partition_assignments = {}
    
    def add_consumer(self, consumer_id):
        self.consumers.append(consumer_id)
        self.rebalance()
    
    def remove_consumer(self, consumer_id):
        self.consumers.remove(consumer_id)
        self.rebalance()
    
    def rebalance(self):
        # Calculate new partition assignments
        partitions = self.get_all_partitions()
        assignments = self.assign_partitions(partitions, self.consumers)
        
        # Update assignments
        self.partition_assignments = assignments
        
        # Notify consumers
        for consumer_id, assigned_partitions in assignments.items():
            self.notify_consumer(consumer_id, assigned_partitions)
```

---

## Optimizations

### Performance Optimizations

#### 1. Message Batching

**Producer Batching:**

```python
class BatchProducer:
    def __init__(self, batch_size: int = 100, linger_ms: int = 10):
        self.batch_size = batch_size
        self.linger_ms = linger_ms
        self.batch = []
        self.last_send = time.time()
    
    async def send(self, message: Message):
        self.batch.append(message)
        
        # Send if batch is full or timeout reached
        if len(self.batch) >= self.batch_size:
            await self.flush()
        elif (time.time() - self.last_send) * 1000 > self.linger_ms:
            await self.flush()
    
    async def flush(self):
        if not self.batch:
            return
        
        # Batch send messages
        await self.producer.send_batch(self.batch)
        self.batch.clear()
        self.last_send = time.time()
```

#### 2. Compression Optimization

**Message Compression:**

```python
class CompressionOptimizer:
    def __init__(self):
        self.compression_types = {
            'gzip': gzip.compress,
            'snappy': snappy.compress,
            'lz4': lz4.compress
        }
        self.compression_threshold = 1024  # 1KB
    
    def compress_message(self, message: Message, compression_type: str = 'snappy') -> bytes:
        data = message.serialize()
        
        # Only compress if message is large enough
        if len(data) < self.compression_threshold:
            return data
        
        compressor = self.compression_types.get(compression_type, self.compression_types['snappy'])
        compressed = compressor(data)
        
        # Only use compression if it saves space
        if len(compressed) < len(data) * 0.9:  # At least 10% savings
            message.set_compression(compression_type)
            return compressed
        
        return data
```

#### 3. Zero-Copy Optimization

**Zero-Copy Reads:**

```python
class ZeroCopyReader:
    def read_message_zero_copy(self, segment_file: str, offset: int, size: int) -> bytes:
        # Use memory mapping for zero-copy reads
        with open(segment_file, 'rb') as f:
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                return mm[offset:offset + size]
```

**Sendfile Optimization:**

```python
class SendfileOptimizer:
    async def send_message_sendfile(self, socket, segment_file: str, offset: int, size: int):
        # Use sendfile() system call for zero-copy network transfer
        with open(segment_file, 'rb') as f:
            f.seek(offset)
            await socket.sendfile(f, offset=offset, count=size)
```

#### 4. Consumer Optimization

**Fetch Size Optimization:**

```python
class FetchSizeOptimizer:
    def __init__(self):
        self.fetch_sizes = {}  # consumer_id -> fetch_size
    
    def optimize_fetch_size(self, consumer_id: str, processing_rate: float):
        current_fetch = self.fetch_sizes.get(consumer_id, 1)
        
        # Increase fetch size if processing fast
        if processing_rate > 1000:  # messages/second
            new_fetch = min(current_fetch * 2, 1000)
        # Decrease if processing slow
        elif processing_rate < 100:
            new_fetch = max(current_fetch // 2, 1)
        else:
            new_fetch = current_fetch
        
        self.fetch_sizes[consumer_id] = new_fetch
        return new_fetch
```

**Parallel Processing:**

```python
class ParallelConsumer:
    async def process_messages_parallel(self, messages: list, num_workers: int = 10):
        # Process messages in parallel
        semaphore = asyncio.Semaphore(num_workers)
        
        async def process_with_semaphore(msg):
            async with semaphore:
                return await self.process_message(msg)
        
        tasks = [process_with_semaphore(msg) for msg in messages]
        results = await asyncio.gather(*tasks)
        return results
```

#### 5. Storage Optimization

**Segment Compaction:**

```python
class SegmentCompactor:
    async def compact_segment(self, segment: Segment):
        # Remove deleted/expired messages
        active_messages = [
            msg for msg in segment.messages
            if not msg.deleted and not msg.expired
        ]
        
        # Rewrite segment with only active messages
        new_segment = await self.create_segment(active_messages)
        
        # Replace old segment
        await self.replace_segment(segment.id, new_segment.id)
```

**Index Optimization:**

```python
class IndexOptimizer:
    def create_sparse_index(self, segment: Segment, index_interval: int = 1000):
        # Create sparse index (not every message)
        index = {}
        for i, message in enumerate(segment.messages):
            if i % index_interval == 0:
                index[i] = {
                    'offset': message.offset,
                    'timestamp': message.timestamp
                }
        return index
```

---

## Scalability Considerations

### 1. Horizontal Scaling

**Broker Scaling:**
- Add brokers to cluster
- Redistribute partitions
- No downtime required

**Partition Scaling:**
- Increase partitions per topic
- Enables more parallelism
- Requires consumer rebalancing

### 2. Throughput Optimization

**Batching:**
- Batch multiple messages
- Reduces network overhead
- Increases throughput

**Compression:**
- Compress messages (gzip, snappy, lz4)
- Reduces network bandwidth
- Trade-off: CPU usage

**Zero-Copy:**
- Use sendfile() for reads
- Bypass kernel buffer
- Reduces CPU usage

### 3. Storage Optimization

**Segment Size:**
- Larger segments: Fewer files, better performance
- Smaller segments: Faster recovery, more files

**Retention Policies:**
- Time-based: Delete after N days
- Size-based: Delete when size limit reached
- Compaction: Keep only latest per key

---

## Caching Strategy

### Cache Architecture

**Page Cache:**
- OS page cache for segment files
- Automatic caching by OS
- Fast reads for hot data

**Metadata Cache:**
- Cache topic/partition metadata
- Reduce ZooKeeper/etcd calls
- TTL-based invalidation

### Cache Keys

```
topic:{topic_name} → Topic metadata
partition:{topic}:{partition} → Partition metadata
offset:{group}:{topic}:{partition} → Consumer offset
```

---

## Load Balancing

### Load Balancer Architecture

```
Producers/Consumers
    │
    ▼
Load Balancer
    │
    ├─ Broker 1
    ├─ Broker 2
    ├─ Broker 3
    └─ Broker N
```

### Load Balancing Strategies

1. **Round-Robin**: Equal distribution
2. **Least Connections**: Route to broker with fewest connections
3. **Partition-Aware**: Route to partition leader

---

## Security

### 1. Authentication & Authorization

**Authentication:**
- SASL (Simple Authentication and Security Layer)
- mTLS
- API keys

**Authorization:**
- ACLs (Access Control Lists)
- Topic-level permissions
- Consumer group permissions

### 2. Encryption

**Encryption in Transit:**
- TLS 1.3 for client-broker communication
- TLS for inter-broker communication

**Encryption at Rest:**
- Encrypt segment files
- Key management (AWS KMS, etc.)

---

## Monitoring & Analytics

### Key Metrics

**Broker Metrics:**
- Messages in/out per second
- Bytes in/out per second
- Request latency (p50, p95, p99)
- Disk usage
- Network usage

**Topic Metrics:**
- Messages per second
- Bytes per second
- Partition count
- Replication lag

**Consumer Metrics:**
- Lag (messages behind)
- Consumption rate
- Offset commit rate

---

## Deployment Strategy

### Infrastructure

**Cloud Provider**: AWS, GCP, or Azure

**Components:**
- **Brokers**: EC2 instances (high I/O)
- **Storage**: Local SSDs (NVMe)
- **Coordination**: ZooKeeper or etcd
- **Monitoring**: Prometheus + Grafana

### Multi-Region Deployment

```
Region 1          Region 2          Region 3
┌─────────┐      ┌─────────┐      ┌─────────┐
│ Broker  │      │ Broker  │      │ Broker  │
│ Cluster │      │ Cluster │      │ Cluster │
└─────────┘      └─────────┘      └─────────┘
```

---

## Capacity Planning

### Storage Estimates

**Messages:**
- 10M messages/second
- Average message size: 1 KB
- 10M × 1 KB = 10 GB/second
- 10 GB/s × 86400 = 864 TB/day

**After Compression (3:1):**
- **Total: ~288 TB/day**

**Retention (7 days):**
- **Total Storage: ~2 PB**

### Compute Requirements

**Brokers:**
- 10M messages/second
- Each broker handles: 1M messages/second
- Required brokers: 10M / 1M = 10 brokers
- With replication (3x): **30 brokers**

---

## Technology Stack

### Recommended Stack

**Brokers:**
- **Language**: Java (like Kafka) or Go
- **Storage**: Local SSDs (NVMe)

**Coordination:**
- **ZooKeeper** or **etcd**

**Monitoring:**
- **Prometheus** + **Grafana**

---

## Failure Scenarios & Handling

### 1. Broker Failure

**Scenario:** Broker crashes.

**Impact:** Partitions on that broker unavailable.

**Mitigation:**
- **Replication**: Followers take over
- **Leader Election**: Controller elects new leader
- **Automatic Failover**: Transparent to clients

### 2. Network Partition

**Scenario:** Network split between brokers.

**Impact:** Cannot achieve quorum.

**Mitigation:**
- **Quorum Requirement**: Require majority for writes
- **Read from ISR**: Only read from in-sync replicas
- **Graceful Degradation**: Accept reduced availability

### 3. Consumer Lag

**Scenario:** Consumers fall behind producers.

**Impact:** Increasing lag, potential data loss if retention exceeded.

**Mitigation:**
- **Scale Consumers**: Add more consumers
- **Increase Partitions**: Enable more parallelism
- **Monitor Lag**: Alert on high lag

---

## Trade-offs & Design Decisions

### 1. Durability: Sync vs Async Writes

**Decision:** Configurable (sync for durability, async for performance).

**Trade-offs:**

| Approach | Pros | Cons |
|----------|------|------|
| **Sync** | Guaranteed durability | Slower writes |
| **Async** | Faster writes | Risk of data loss |

**Why Configurable:**
- **Sync**: For critical data
- **Async**: For high-throughput, less critical data

### 2. Ordering: Per-Partition vs Global

**Decision:** Per-partition ordering.

**Trade-offs:**

| Approach | Pros | Cons |
|----------|------|------|
| **Per-Partition** | Scalable, simple | No global ordering |
| **Global** | Strong ordering | Not scalable |

**Why Per-Partition:**
- **Scalability**: Enables parallelism
- **Acceptable**: Most use cases don't need global ordering

### 3. Delivery Semantics: At-Least-Once vs Exactly-Once

**Decision:** Support both (at-least-once default, exactly-once optional).

**Trade-offs:**

| Approach | Pros | Cons |
|----------|------|------|
| **At-Least-Once** | Simple, fast | Duplicates possible |
| **Exactly-Once** | No duplicates | Complex, slower |

**Why Both:**
- **At-Least-Once**: Default for performance
- **Exactly-Once**: For critical use cases

---

## Interview Discussion Points

### Key Questions to Address

1. **"How do you ensure message ordering?"**
   - **Answer**: 
     - Ordering within partitions
     - Key-based partitioning maintains ordering per key
     - Consumers process partitions sequentially

2. **"How do you handle broker failures?"**
   - **Answer**:
     - Replication across brokers
     - Leader election on failure
     - Automatic failover
     - Consumers reconnect to new leader

3. **"How do you prevent message loss?"**
   - **Answer**:
     - Replication (3x typical)
     - Quorum writes (majority of ISR)
     - Persistent storage
     - Consumer offset tracking

4. **"How do you scale consumers?"**
   - **Answer**:
     - Add consumers to group
     - Automatic rebalancing
     - Increase partitions for more parallelism
     - Monitor consumer lag

5. **"How do you handle high throughput?"**
   - **Answer**:
     - Batching messages
     - Compression
     - Zero-copy reads
     - Horizontal scaling (more brokers/partitions)

---

## References

- [Kafka Architecture](https://kafka.apache.org/documentation/)
- [Kafka Design](https://kafka.apache.org/documentation/#design)
- [System Design Primer](https://github.com/donnemartin/system-design-primer)
- [Distributed Systems](https://www.allthingsdistributed.com/)

