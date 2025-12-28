# Key-Value Store System Design

## Table of Contents
1. [Overview](#overview)
2. [Requirements](#requirements)
3. [System Architecture](#system-architecture)
4. [Database Design](#database-design)
5. [API Design](#api-design)
6. [Storage Engine](#storage-engine)
7. [Consistency Model](#consistency-model)
8. [Replication & Sharding](#replication--sharding)
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

A distributed key-value store that provides high-performance, scalable storage for key-value pairs. The system must handle millions of operations per second, support high availability, and provide consistency guarantees.

**Key Features:**
- High-throughput read/write operations
- Low-latency access
- Horizontal scaling
- Replication for availability
- Sharding for distribution
- Configurable consistency levels
- TTL (Time-To-Live) support
- Multi-tenant support

---

## Requirements

### Functional Requirements

1. **Basic Operations**
   - PUT(key, value): Store key-value pair
   - GET(key): Retrieve value by key
   - DELETE(key): Delete key-value pair
   - EXISTS(key): Check if key exists

2. **Advanced Operations**
   - Batch operations (multi-get, multi-put)
   - Conditional updates (compare-and-swap)
   - Atomic increments/decrements
   - Range queries (scan)

3. **Data Management**
   - TTL (Time-To-Live) support
   - Versioning
   - Compression
   - Expiration policies

4. **Consistency**
   - Strong consistency (linearizability)
   - Eventual consistency
   - Configurable consistency levels

5. **Replication**
   - Automatic replication
   - Configurable replication factor
   - Cross-region replication

6. **Sharding**
   - Automatic sharding
   - Consistent hashing
   - Rebalancing

### Non-Functional Requirements

1. **Scalability**
   - Handle 10M+ operations/second
   - Support billions of keys
   - Horizontal scaling
   - Linear performance scaling

2. **Performance**
   - Read latency: < 1ms (p99)
   - Write latency: < 5ms (p99)
   - Throughput: 1M+ ops/second per node

3. **Availability**
   - 99.9% uptime
   - Automatic failover
   - Zero-downtime scaling
   - Multi-region support

4. **Durability**
   - No data loss
   - Write-ahead logging (WAL)
   - Periodic snapshots
   - Replication

5. **Consistency**
   - Configurable consistency levels
   - Strong consistency option
   - Eventual consistency option

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Clients                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Client 1 │  │ Client 2 │  │ Client 3 │  │ Client N │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼──────────┘
        │             │             │             │
        └─────────────┴─────────────┴─────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│              Load Balancer / Proxy Layer                     │
└───────────────────────────┬─────────────────────────────────┘
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
│              Storage Node Cluster                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Node 1  │  │  Node 2  │  │  Node 3  │  │  Node N │   │
│  │(Shard 1) │  │(Shard 2) │  │(Shard 3) │  │(Shard N)│   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼──────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│              Storage Layer                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   Memtable│ │   Memtable│ │   Memtable│ │   Memtable│ │
│  │  (RAM)   │  │  (RAM)   │  │  (RAM)   │  │  (RAM)   │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   SSTable│ │   SSTable│ │   SSTable│ │   SSTable│ │
│  │  (Disk)  │  │  (Disk)  │  │  (Disk)  │  │  (Disk)  │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼──────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│              Replication Layer                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Replica  │  │ Replica  │  │ Replica  │  │ Replica  │   │
│  │   Set 1  │  │   Set 2  │  │   Set 3  │  │   Set N  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Component Details

#### 1. Proxy/Load Balancer
- **Responsibilities**:
  - Route requests to appropriate nodes
  - Consistent hashing for sharding
  - Load balancing
  - Caching (optional)

#### 2. Storage Node
- **Responsibilities**:
  - Handle read/write operations
  - Manage memtable and SSTables
  - Handle replication
  - Compaction

#### 3. Coordination Service
- **Technology**: ZooKeeper, etcd, or Consul
- **Responsibilities**:
  - Cluster membership
  - Shard assignment
  - Leader election
  - Configuration management

#### 4. Storage Engine
- **Memtable**: In-memory sorted structure (B-tree or LSM-tree)
- **SSTable**: Immutable sorted files on disk
- **WAL**: Write-ahead log for durability

---

## Database Design

### Key-Value Schema

#### Key-Value Entry
```
Key: String (up to 64KB)
Value: Binary (up to 1MB, configurable)
Metadata:
  - Version (for optimistic concurrency)
  - TTL (Time-To-Live)
  - Timestamp
  - Checksum
```

#### Memtable Structure (LSM-Tree)
```
Memtable (In-Memory):
  - Sorted key-value pairs
  - Size limit: 64MB (configurable)
  - When full: Flush to SSTable
```

#### SSTable Structure
```
SSTable File:
  - Data Block: Sorted key-value pairs
  - Index Block: Key → Data Block offset
  - Bloom Filter: Fast key existence check
  - Footer: Metadata
```

### Metadata Storage (Coordination Service)

#### Shard Metadata
```sql
CREATE TABLE shards (
    shard_id INT PRIMARY KEY,
    start_key VARCHAR(255),
    end_key VARCHAR(255),
    primary_node_id INT,
    replica_node_ids JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Node Metadata
```sql
CREATE TABLE nodes (
    node_id INT PRIMARY KEY,
    host VARCHAR(255),
    port INT,
    status VARCHAR(50),  -- 'active', 'down', 'recovering'
    shard_ids JSON,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## API Design

### Basic Operations

**PUT**
```
PUT /api/v1/keys/{key}
Content-Type: application/json

Request:
{
    "value": "base64_encoded_value",
    "ttl": 3600,  // Optional, seconds
    "version": 123  // Optional, for conditional update
}

Response:
{
    "success": true,
    "version": 124,
    "timestamp": 1609459200
}
```

**GET**
```
GET /api/v1/keys/{key}?consistency=strong

Response:
{
    "key": "user_123",
    "value": "base64_encoded_value",
    "version": 124,
    "timestamp": 1609459200,
    "ttl": 3600
}
```

**DELETE**
```
DELETE /api/v1/keys/{key}

Response:
{
    "success": true
}
```

**EXISTS**
```
HEAD /api/v1/keys/{key}

Response:
200 OK (exists) or 404 Not Found
```

### Batch Operations

**Multi-GET**
```
POST /api/v1/keys/batch/get
Content-Type: application/json

Request:
{
    "keys": ["key1", "key2", "key3"]
}

Response:
{
    "results": [
        {"key": "key1", "value": "...", "found": true},
        {"key": "key2", "value": "...", "found": true},
        {"key": "key3", "found": false}
    ]
}
```

**Multi-PUT**
```
POST /api/v1/keys/batch/put
Content-Type: application/json

Request:
{
    "items": [
        {"key": "key1", "value": "..."},
        {"key": "key2", "value": "..."}
    ]
}

Response:
{
    "success": true,
    "items_written": 2
}
```

### Advanced Operations

**Compare-and-Swap**
```
PUT /api/v1/keys/{key}?compare_version=123

Request:
{
    "value": "new_value"
}

Response:
{
    "success": true,
    "version": 124
}
// Or if version mismatch:
{
    "success": false,
    "error": "version_mismatch",
    "current_version": 125
}
```

**Increment/Decrement**
```
POST /api/v1/keys/{key}/increment?delta=1

Response:
{
    "success": true,
    "value": 101,
    "version": 126
}
```

**Scan (Range Query)**
```
GET /api/v1/keys?prefix=user_&limit=100&cursor=abc123

Response:
{
    "keys": [
        {"key": "user_001", "value": "..."},
        {"key": "user_002", "value": "..."}
    ],
    "cursor": "def456",
    "has_more": true
}
```

---

## Data Flow Diagrams

### Write Flow

```
Client PUT Request
    │
    ▼
Proxy/Load Balancer
    │
    ├─ Hash Key → Determine Shard
    ├─ Route to Primary Node
    │
    ▼
Storage Node (Primary)
    │
    ├─ Write to WAL (Write-Ahead Log)
    ├─ Write to Memtable
    │
    ├─ If Memtable Full → Flush to SSTable
    │
    ▼
Replicate to Replicas
    │
    ├─ Send to Replica 1
    ├─ Send to Replica 2
    └─ Wait for ACK (quorum)
    │
    ▼
Return Success to Client
```

### Read Flow

```
Client GET Request
    │
    ▼
Proxy/Load Balancer
    │
    ├─ Hash Key → Determine Shard
    ├─ Route to Node (Primary or Replica based on consistency)
    │
    ▼
Storage Node
    │
    ├─ Check Memtable (Fast Path)
    │   └─ Found → Return
    │
    └─ Not Found → Check SSTables
        │
        ├─ Use Bloom Filter (Fast Check)
        ├─ Use Index to Find SSTable
        ├─ Read from SSTable
        │
        └─ Return Value
```

### Compaction Flow

```
Background Compaction Process
    │
    ├─ Monitor SSTable Count
    ├─ When Threshold Reached → Trigger Compaction
    │
    ▼
Merge Multiple SSTables
    │
    ├─ Read from Multiple SSTables (Sorted)
    ├─ Merge and Deduplicate
    ├─ Write New SSTable
    │
    ▼
Delete Old SSTables
    │
    └─ Update Metadata
```

---

## Storage Engine

### LSM-Tree (Log-Structured Merge Tree)

**Components:**
1. **Memtable**: In-memory sorted structure
2. **SSTables**: Immutable sorted files on disk
3. **WAL**: Write-ahead log for durability

**Write Path:**
1. Write to WAL (for durability)
2. Write to Memtable
3. When Memtable full, flush to SSTable

**Read Path:**
1. Check Memtable
2. Check SSTables (newest first)
3. Use Bloom Filter to skip SSTables
4. Use Index to find key in SSTable

**Compaction:**
- Merge multiple SSTables into one
- Remove duplicates (keep latest)
- Reduce read amplification

**Implementation:**
```python
class LSMStorageEngine:
    def __init__(self):
        self.memtable = SortedDict()  # In-memory sorted structure
        self.sstables = []  # List of SSTable files
        self.wal = WriteAheadLog()
        self.memtable_size_limit = 64 * 1024 * 1024  # 64MB
    
    def put(self, key, value):
        # Write to WAL first (for durability)
        self.wal.append(key, value)
        
        # Write to memtable
        self.memtable[key] = value
        
        # Check if memtable is full
        if self.memtable_size() >= self.memtable_size_limit:
            self.flush_memtable()
    
    def get(self, key):
        # Check memtable first
        if key in self.memtable:
            return self.memtable[key]
        
        # Check SSTables (newest first)
        for sstable in reversed(self.sstables):
            # Use Bloom filter to skip if key not present
            if not sstable.bloom_filter.might_contain(key):
                continue
            
            # Read from SSTable
            value = sstable.get(key)
            if value is not None:
                return value
        
        return None
    
    def flush_memtable(self):
        # Create new SSTable from memtable
        sstable = SSTable.create_from_memtable(self.memtable)
        self.sstables.append(sstable)
        
        # Clear memtable
        self.memtable.clear()
        
        # Trigger compaction if needed
        if len(self.sstables) > self.compaction_threshold:
            self.compact()
```

---

## Consistency Model

### Consistency Levels

**Strong Consistency (Linearizability):**
- All reads see latest write
- Requires quorum reads/writes
- Higher latency

**Eventual Consistency:**
- Reads may see stale data
- Lower latency
- Acceptable for many use cases

**Read Consistency:**
- **Strong**: Read from primary or quorum
- **Eventual**: Read from any replica

**Write Consistency:**
- **Strong**: Write to quorum
- **Eventual**: Write to primary, async replication

### Implementation

```python
class ConsistencyManager:
    def read(self, key, consistency_level):
        shard = self.get_shard(key)
        
        if consistency_level == 'strong':
            # Read from primary or quorum
            return self.read_from_quorum(shard, key)
        else:
            # Read from any replica
            return self.read_from_any(shard, key)
    
    def write(self, key, value, consistency_level):
        shard = self.get_shard(key)
        
        if consistency_level == 'strong':
            # Write to quorum
            return self.write_to_quorum(shard, key, value)
        else:
            # Write to primary, async replication
            return self.write_to_primary(shard, key, value)
```

---

## Replication & Sharding

### Sharding Strategy

**Consistent Hashing:**
- Hash key to determine shard
- Virtual nodes for better distribution
- Minimal rebalancing on node add/remove

**Implementation:**
```python
class ConsistentHasher:
    def __init__(self, nodes, virtual_nodes_per_node=150):
        self.ring = {}
        self.nodes = []
        
        for node in nodes:
            for i in range(virtual_nodes_per_node):
                virtual_node_id = f"{node}:{i}"
                hash_value = hash(virtual_node_id)
                self.ring[hash_value] = node
            self.nodes.append(node)
        
        self.sorted_hashes = sorted(self.ring.keys())
    
    def get_shard(self, key):
        key_hash = hash(key)
        
        # Find first node with hash >= key_hash
        for hash_value in self.sorted_hashes:
            if hash_value >= key_hash:
                return self.ring[hash_value]
        
        # Wrap around to first node
        return self.ring[self.sorted_hashes[0]]
```

### Replication

**Replication Factor:**
- Typically 3 (1 primary + 2 replicas)
- Configurable per key or namespace

**Replication Strategy:**
- **Synchronous**: Wait for quorum
- **Asynchronous**: Write to primary, replicate async

**Leader Election:**
- Use coordination service (ZooKeeper/etcd)
- Automatic failover on leader failure

---

## Scalability Considerations

### 1. Horizontal Scaling

**Add Nodes:**
- Add node to cluster
- Rebalance shards
- Minimal data movement (consistent hashing)

**Partition Scaling:**
- Increase number of shards
- Redistribute keys
- Requires rebalancing

### 2. Read Scaling

**Read Replicas:**
- Multiple replicas per shard
- Distribute read load
- Eventual consistency reads

### 3. Write Scaling

**Partitioning:**
- More shards = more parallelism
- Distribute write load
- Linear scaling

---

## Caching Strategy

### Cache Architecture

**Multi-Level Caching:**
1. **Client Cache**: Cache frequently accessed keys
2. **Proxy Cache**: Cache at proxy layer
3. **Node Cache**: Cache hot keys in memory

**Cache Invalidation:**
- TTL-based expiration
- Event-based invalidation
- Version-based invalidation

---

## Load Balancing

### Load Balancer Architecture

```
Clients
    │
    ▼
Load Balancer (Consistent Hashing)
    │
    ├─ Node 1 (Shard 1)
    ├─ Node 2 (Shard 2)
    ├─ Node 3 (Shard 3)
    └─ Node N (Shard N)
```

### Load Balancing Strategies

1. **Consistent Hashing**: Route by key hash
2. **Round-Robin**: For non-key operations
3. **Least Connections**: For load balancing

---

## Security

### 1. Authentication & Authorization

**Authentication:**
- API keys
- mTLS
- OAuth 2.0

**Authorization:**
- Namespace-level permissions
- Key-prefix permissions
- Read/write permissions

### 2. Encryption

**Encryption in Transit:**
- TLS 1.3

**Encryption at Rest:**
- Encrypt SSTables
- Key management (AWS KMS)

---

## Monitoring & Analytics

### Key Metrics

**Performance Metrics:**
- Read latency (p50, p95, p99)
- Write latency (p50, p95, p99)
- Throughput (ops/second)
- Error rate

**Storage Metrics:**
- Disk usage
- Memtable size
- SSTable count
- Compaction rate

**Cluster Metrics:**
- Node health
- Replication lag
- Shard distribution

---

## Deployment Strategy

### Infrastructure

**Cloud Provider**: AWS, GCP, or Azure

**Components:**
- **Nodes**: EC2 instances (high I/O)
- **Storage**: Local SSDs (NVMe)
- **Coordination**: ZooKeeper or etcd
- **Monitoring**: Prometheus + Grafana

### Multi-Region Deployment

```
Region 1          Region 2          Region 3
┌─────────┐      ┌─────────┐      ┌─────────┐
│ Cluster │      │ Cluster │      │ Cluster │
│         │◄────►│         │◄────►│         │
└─────────┘      └─────────┘      └─────────┘
```

---

## Capacity Planning

### Storage Estimates

**Keys:**
- 1B keys × 1 KB average = 1 TB
- With replication (3x): **3 TB**
- With overhead (20%): **3.6 TB**

### Compute Requirements

**Nodes:**
- 10M operations/second
- Each node handles: 1M ops/second
- Required nodes: 10M / 1M = **10 nodes**
- With replication (3x): **30 nodes**

---

## Technology Stack

### Recommended Stack

**Storage Engine:**
- **Language**: C++ or Rust (performance)
- **LSM-Tree**: Custom implementation or RocksDB

**Coordination:**
- **ZooKeeper** or **etcd**

**Monitoring:**
- **Prometheus** + **Grafana**

---

## Failure Scenarios & Handling

### 1. Node Failure

**Scenario:** Storage node crashes.

**Impact:** Shard unavailable.

**Mitigation:**
- **Replication**: Replicas take over
- **Automatic Failover**: Elect new primary
- **Rebalancing**: Redistribute shards

### 2. Network Partition

**Scenario:** Network split between nodes.

**Impact:** Cannot achieve quorum.

**Mitigation:**
- **Quorum Requirement**: Require majority
- **Read from ISR**: Only read from in-sync replicas
- **Graceful Degradation**: Accept reduced availability

### 3. Disk Failure

**Scenario:** Disk fails on node.

**Impact:** Data loss on that disk.

**Mitigation:**
- **Replication**: Data replicated on other nodes
- **WAL**: Replay WAL from replicas
- **Backup**: Periodic backups

---

## Trade-offs & Design Decisions

### 1. Storage: LSM-Tree vs B-Tree

**Decision:** LSM-Tree for write-heavy workloads.

**Trade-offs:**

| Aspect | LSM-Tree | B-Tree |
|--------|----------|--------|
| **Write Performance** | Excellent | Good |
| **Read Performance** | Good | Excellent |
| **Space Amplification** | Higher | Lower |
| **Write Amplification** | Higher | Lower |

**Why LSM-Tree:**
- **Write Performance**: Better for write-heavy workloads
- **Sequential Writes**: Better disk utilization

### 2. Consistency: Strong vs Eventual

**Decision:** Support both (configurable).

**Trade-offs:**

| Approach | Pros | Cons |
|----------|------|------|
| **Strong** | No stale reads | Higher latency |
| **Eventual** | Lower latency | Stale reads possible |

**Why Both:**
- **Strong**: For critical data
- **Eventual**: For high-performance use cases

### 3. Compaction: Leveled vs Size-Tiered

**Decision:** Leveled compaction.

**Trade-offs:**

| Approach | Pros | Cons |
|----------|------|------|
| **Leveled** | Lower read amplification | Higher write amplification |
| **Size-Tiered** | Lower write amplification | Higher read amplification |

**Why Leveled:**
- **Read Performance**: Better for read-heavy workloads
- **Space Efficiency**: Better space utilization

---

## Interview Discussion Points

### Key Questions to Address

1. **"How do you ensure consistency?"**
   - **Answer**: 
     - Configurable consistency levels
     - Quorum reads/writes for strong consistency
     - Version vectors for conflict resolution

2. **"How do you handle node failures?"**
   - **Answer**:
     - Replication across nodes
     - Automatic failover
     - Rebalancing on node add/remove

3. **"How do you scale horizontally?"**
   - **Answer**:
     - Consistent hashing for sharding
     - Add nodes, rebalance shards
     - Linear scaling

4. **"How do you optimize read performance?"**
   - **Answer**:
     - Memtable for hot data
     - Bloom filters for SSTables
     - Caching at multiple levels
     - Read replicas

5. **"How do you handle high write throughput?"**
   - **Answer**:
     - LSM-Tree for sequential writes
     - Batching writes
     - Asynchronous replication
     - Horizontal scaling (more shards)

---

## High-Level Design (HLD)

### System Overview

The key-value store follows a distributed architecture:

1. **Client Layer**: Applications using the key-value store
2. **Proxy Layer**: Routes requests, handles consistent hashing
3. **Storage Node Layer**: Handles read/write operations, manages data
4. **Coordination Layer**: Manages cluster membership, shard assignment
5. **Storage Engine**: LSM-Tree for efficient writes
6. **Replication Layer**: Ensures data durability and availability

### Service Decomposition

**Core Components:**
- **Proxy Service**: Request routing, load balancing, caching
- **Storage Node**: Handles operations, manages memtable/SSTables
- **Coordination Service**: Cluster management, leader election
- **Replication Manager**: Handles data replication

---

## Low-Level Design (LLD)

### LSM Storage Engine Implementation

```python
class LSMStorageEngine:
    def __init__(self, wal_path: str, sstable_dir: str):
        self.memtable = SortedDict()  # In-memory sorted structure
        self.sstables = []  # List of SSTable files
        self.wal = WriteAheadLog(wal_path)
        self.memtable_size_limit = 64 * 1024 * 1024  # 64MB
        self.compaction_threshold = 10
    
    def put(self, key: str, value: bytes):
        # Write to WAL first (for durability)
        self.wal.append(key, value)
        
        # Write to memtable
        self.memtable[key] = value
        
        # Check if memtable is full
        if self.memtable_size() >= self.memtable_size_limit:
            self.flush_memtable()
    
    def get(self, key: str) -> bytes:
        # Check memtable first
        if key in self.memtable:
            return self.memtable[key]
        
        # Check SSTables (newest first)
        for sstable in reversed(self.sstables):
            # Use Bloom filter to skip if key not present
            if not sstable.bloom_filter.might_contain(key):
                continue
            
            # Read from SSTable
            value = sstable.get(key)
            if value is not None:
                return value
        
        return None
    
    def flush_memtable(self):
        # Create new SSTable from memtable
        sstable = SSTable.create_from_memtable(self.memtable, self.sstable_dir)
        self.sstables.append(sstable)
        
        # Clear memtable
        self.memtable.clear()
        
        # Clear WAL (data now in SSTable)
        self.wal.clear()
        
        # Trigger compaction if needed
        if len(self.sstables) > self.compaction_threshold:
            self.compact()
```

### Consistent Hashing Implementation

```python
class ConsistentHasher:
    def __init__(self, nodes: list, virtual_nodes_per_node: int = 150):
        self.ring = {}
        self.nodes = []
        
        for node in nodes:
            for i in range(virtual_nodes_per_node):
                virtual_node_id = f"{node}:{i}"
                hash_value = self.hash(virtual_node_id)
                self.ring[hash_value] = node
            self.nodes.append(node)
        
        self.sorted_hashes = sorted(self.ring.keys())
    
    def get_node(self, key: str) -> str:
        key_hash = self.hash(key)
        
        # Find first node with hash >= key_hash
        for hash_value in self.sorted_hashes:
            if hash_value >= key_hash:
                return self.ring[hash_value]
        
        # Wrap around to first node
        return self.ring[self.sorted_hashes[0]]
    
    def hash(self, value: str) -> int:
        # Use consistent hash function (e.g., MD5, SHA-1)
        import hashlib
        return int(hashlib.md5(value.encode()).hexdigest(), 16)
```

---

## Fault Tolerance

### Node Failure Handling

**Replication:**
- Each key replicated to N nodes (typically 3)
- Automatic failover to replica
- Rebalance on node add/remove

**Failure Detection:**
- Health checks every 10 seconds
- Mark node as dead after 3 consecutive failures
- Trigger replica promotion

### Data Consistency

**Quorum Reads/Writes:**
- Write to quorum (N/2 + 1 nodes)
- Read from quorum for strong consistency
- Read from any node for eventual consistency

**Conflict Resolution:**
- Use vector clocks or timestamps
- Last-write-wins for simple cases
- Application-level conflict resolution

---

## Optimizations

### Write Optimization

**Batching:**
- Batch multiple writes
- Reduce network calls
- Improve throughput

**Compression:**
- Compress SSTables
- Reduce storage space
- Trade CPU for I/O

### Read Optimization

**Bloom Filters:**
- Fast existence check
- Skip SSTables that don't contain key
- Reduce I/O operations

**Caching:**
- Cache frequently accessed keys
- Multi-level caching
- Reduce database queries

---

## Failure Safety

### Node Failure

**Scenario: Storage Node Crashes**
- **Impact**: Shard unavailable, data loss risk
- **Mitigation**:
  - Replication across nodes
  - Automatic failover
  - Rebalance shards
- **Recovery**:
  - Promote replica to primary
  - Replicate to new node
  - Verify data consistency

### Network Partition

**Scenario: Network Split**
- **Impact**: Cannot achieve quorum
- **Mitigation**:
  - Quorum requirement (majority)
  - Read from in-sync replicas only
  - Graceful degradation
- **Recovery**:
  - Merge partitions when resolved
  - Resolve conflicts
  - Sync data

### Data Loss

**Scenario: Disk Failure**
- **Impact**: Data loss on that disk
- **Mitigation**:
  - Replication on other nodes
  - WAL for durability
  - Periodic backups
- **Recovery**:
  - Restore from replica
  - Replay WAL
  - Verify data integrity

---

## Scalability

### Horizontal Scaling

**Add Nodes:**
- Add node to cluster
- Rebalance shards using consistent hashing
- Minimal data movement

**Shard Scaling:**
- Increase number of shards
- Redistribute keys
- Linear scaling

### Performance Scaling

**Throughput Scaling:**
- More shards = more parallelism
- Distribute write load
- Scale linearly

**Latency Optimization:**
- Reduce network hops
- Optimize queries
- Use caching

---

## References

- [DynamoDB Architecture](https://aws.amazon.com/dynamodb/)
- [Cassandra Architecture](https://cassandra.apache.org/)
- [RocksDB](https://rocksdb.org/)
- [System Design Primer](https://github.com/donnemartin/system-design-primer)

