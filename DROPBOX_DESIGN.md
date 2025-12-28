# Dropbox System Design

## Table of Contents
1. [Requirements Analysis](#requirements-analysis)
2. [High-Level Architecture](#high-level-architecture)
3. [Core Components](#core-components)
4. [Data Models](#data-models)
5. [API Design](#api-design)
6. [File Upload/Download Flow](#file-uploaddownload-flow)
7. [Synchronization Strategy](#synchronization-strategy)
8. [Scalability & Performance](#scalability--performance)
9. [Security & Reliability](#security--reliability)
10. [Trade-offs & Design Decisions](#trade-offs--design-decisions)

---

## Requirements Analysis

### Functional Requirements
**Core:**
- ✅ Upload/download files from any device
- ✅ Share files with permissions (view, edit)
- ✅ Automatic sync across devices
- ✅ Nested folder structure support
- ✅ File sharing and access control

**Extra Credit:**
- ✅ Collaborative editing
- ✅ Desktop daemon for auto-sync
- ✅ File versioning
- ✅ File compression
- ✅ Enhanced security

### Non-Functional Requirements
**Core:**
- High Availability (99.99%+ uptime)
- Security & Reliability (data recovery, backup)
- Low Latency (fast upload/download/sync)
- Scale: 100M+ users, 100TB per user, 50GB max file size

**Extra Credit:**
- File versioning
- Compression
- Encryption (at rest and in transit)

### Capacity Estimation
- **Users:** 100M total, assume 20% DAU = 20M daily active users
- **Storage per user:** Average 1TB (max 100TB)
- **Total storage:** 100M × 1TB = 100PB
- **Reads vs Writes:** Read-heavy (3:1 ratio)
- **Bandwidth:** 
  - Assuming 20M DAU, each uploads 2 files/day (10MB avg) = 400TB/day upload
  - Download ratio 3x = 1.2PB/day download

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                             │
│  (Web App, Mobile Apps, Desktop Client/Daemon)                  │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Load Balancer (Layer 7)                     │
│                    (AWS ALB / NGINX / HAProxy)                   │
└────────────┬────────────────────────────────────┬────────────────┘
             │                                    │
             ▼                                    ▼
┌────────────────────────────┐      ┌────────────────────────────┐
│   API Gateway / Web Servers│      │   WebSocket Servers        │
│   (Metadata Operations)     │      │   (Real-time Sync)         │
└────────────┬───────────────┘      └────────────┬───────────────┘
             │                                    │
             ▼                                    ▼
┌────────────────────────────────────────────────────────────────┐
│                      Application Servers                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Metadata   │  │    Sync      │  │   Sharing    │         │
│  │   Service    │  │   Service    │  │   Service    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────┬────────────────────┬────────────────────┬──────────────────┘
     │                    │                    │
     ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   Metadata DB   │  │  Message Queue  │  │   Cache Layer   │
│  (PostgreSQL)   │  │  (Kafka/SQS)    │  │    (Redis)      │
└─────────────────┘  └─────────────────┘  └─────────────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │   Block Servers     │
                    │  (Chunking Service) │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Object Storage     │
                    │  (S3 / GCS / Azure) │
                    │   + CDN (CloudFront)│
                    └─────────────────────┘
```

---

## Core Components

### 1. **Client Application**
- **Web Client:** Browser-based UI
- **Mobile Apps:** iOS/Android native apps
- **Desktop Daemon:** Background service that watches filesystem changes
  - Uses file system watchers (inotify on Linux, FSEvents on macOS, FileSystemWatcher on Windows)
  - Implements exponential backoff for retries
  - Local database for tracking file metadata and sync state

### 2. **Load Balancer**
- Distributes incoming requests across API servers
- Health checks and automatic failover
- SSL termination

### 3. **API Gateway / Application Servers**

#### **Metadata Service**
- Manages file/folder metadata (name, size, permissions, versions)
- Handles CRUD operations on file structure
- Stores metadata in relational database

#### **Synchronization Service**
- Detects file changes and propagates updates
- Manages conflict resolution
- Uses message queues for async processing
- Maintains sync state per device

#### **Block Service**
- Chunks large files into smaller blocks (4MB chunks)
- Handles deduplication at block level
- Compresses blocks before storage
- Generates checksums for integrity

#### **Sharing Service**
- Manages file/folder sharing
- Handles permissions (view, edit, owner)
- Generates shareable links with expiration

#### **Version Service**
- Maintains file version history
- Garbage collection for old versions
- Differential storage for versions

#### **Notification Service**
- Real-time notifications via WebSocket
- Notifies clients about file changes
- Presence detection for collaborative editing

### 4. **Storage Layer**

#### **Metadata Database (PostgreSQL)**
- Stores file/folder hierarchy
- User information and permissions
- Device registrations
- Sharing metadata
- Version information

**Why PostgreSQL?**
- Strong ACID guarantees for metadata consistency
- Complex queries for permissions and sharing
- JSON support for flexible metadata

#### **Object Storage (S3/GCS)**
- Stores actual file blocks
- Highly durable (99.999999999% durability)
- Automatically replicated across regions
- Versioning support built-in

#### **Cache Layer (Redis)**
- Caches frequently accessed metadata
- Stores active session information
- Distributed locks for conflict resolution
- Real-time sync state

#### **Message Queue (Kafka/SQS)**
- Async processing of file operations
- Event streaming for sync notifications
- Guarantees at-least-once delivery

### 5. **CDN (CloudFront/Akamai)**
- Caches frequently accessed files closer to users
- Reduces latency for downloads
- Handles static assets for web client

---

## Data Models

### Database Schema

```sql
-- Users Table
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    storage_used BIGINT DEFAULT 0,
    storage_quota BIGINT DEFAULT 107374182400, -- 100TB in bytes
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_users_email ON users(email);

-- Devices Table
CREATE TABLE devices (
    device_id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    device_name VARCHAR(255),
    device_type VARCHAR(50), -- web, mobile, desktop
    last_sync_time TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_devices_user ON devices(user_id);

-- Files/Folders Table (Unified)
CREATE TABLE files (
    file_id UUID PRIMARY KEY,
    parent_id UUID REFERENCES files(file_id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(10) NOT NULL, -- 'file' or 'folder'
    size BIGINT DEFAULT 0,
    mime_type VARCHAR(100),
    checksum VARCHAR(64), -- SHA-256 hash
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    version_number INTEGER DEFAULT 1,
    path TEXT, -- Materialized path for quick lookups
    CONSTRAINT check_type CHECK (type IN ('file', 'folder'))
);

CREATE INDEX idx_files_parent ON files(parent_id);
CREATE INDEX idx_files_user ON files(user_id);
CREATE INDEX idx_files_path ON files(path);
CREATE INDEX idx_files_checksum ON files(checksum);

-- File Blocks Table
CREATE TABLE file_blocks (
    block_id UUID PRIMARY KEY,
    file_id UUID REFERENCES files(file_id) ON DELETE CASCADE,
    version_number INTEGER,
    block_index INTEGER, -- Order of block in file
    block_hash VARCHAR(64) UNIQUE, -- For deduplication
    block_size INTEGER,
    storage_key VARCHAR(500), -- S3 key
    is_compressed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(file_id, version_number, block_index)
);

CREATE INDEX idx_blocks_file ON file_blocks(file_id, version_number);
CREATE INDEX idx_blocks_hash ON file_blocks(block_hash);

-- File Versions Table
CREATE TABLE file_versions (
    version_id UUID PRIMARY KEY,
    file_id UUID REFERENCES files(file_id) ON DELETE CASCADE,
    version_number INTEGER,
    size BIGINT,
    checksum VARCHAR(64),
    created_by UUID REFERENCES users(user_id),
    created_at TIMESTAMP DEFAULT NOW(),
    comment TEXT,
    UNIQUE(file_id, version_number)
);

CREATE INDEX idx_versions_file ON file_versions(file_id);

-- Sharing/Permissions Table
CREATE TABLE permissions (
    permission_id UUID PRIMARY KEY,
    file_id UUID REFERENCES files(file_id) ON DELETE CASCADE,
    shared_by UUID REFERENCES users(user_id) ON DELETE CASCADE,
    shared_with UUID REFERENCES users(user_id) ON DELETE CASCADE,
    permission_type VARCHAR(20) NOT NULL, -- 'view', 'edit', 'owner'
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    CONSTRAINT check_permission CHECK (permission_type IN ('view', 'edit', 'owner'))
);

CREATE INDEX idx_permissions_file ON permissions(file_id);
CREATE INDEX idx_permissions_shared_with ON permissions(shared_with);

-- Shared Links Table
CREATE TABLE shared_links (
    link_id UUID PRIMARY KEY,
    file_id UUID REFERENCES files(file_id) ON DELETE CASCADE,
    created_by UUID REFERENCES users(user_id),
    link_token VARCHAR(100) UNIQUE,
    permission_type VARCHAR(20) DEFAULT 'view',
    password_hash VARCHAR(255),
    expires_at TIMESTAMP,
    access_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_shared_links_token ON shared_links(link_token);

-- Sync State Table
CREATE TABLE sync_state (
    sync_id UUID PRIMARY KEY,
    device_id UUID REFERENCES devices(device_id) ON DELETE CASCADE,
    file_id UUID REFERENCES files(file_id) ON DELETE CASCADE,
    state VARCHAR(20), -- 'synced', 'pending', 'conflict', 'error'
    last_sync_time TIMESTAMP,
    local_checksum VARCHAR(64),
    remote_checksum VARCHAR(64),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(device_id, file_id)
);

CREATE INDEX idx_sync_device ON sync_state(device_id);
CREATE INDEX idx_sync_file ON sync_state(file_id);

-- Activity Log Table
CREATE TABLE activity_log (
    log_id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(user_id),
    file_id UUID REFERENCES files(file_id),
    action VARCHAR(50), -- 'upload', 'download', 'delete', 'share', 'edit'
    device_id UUID REFERENCES devices(device_id),
    ip_address INET,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_activity_user ON activity_log(user_id, created_at);
CREATE INDEX idx_activity_file ON activity_log(file_id, created_at);
```

---

## API Design

### REST API Endpoints

#### **Authentication**
```
POST   /api/v1/auth/register
POST   /api/v1/auth/login
POST   /api/v1/auth/logout
POST   /api/v1/auth/refresh-token
GET    /api/v1/auth/me
```

#### **File Operations**
```
GET    /api/v1/files                     # List files (with pagination)
GET    /api/v1/files/:file_id            # Get file metadata
POST   /api/v1/files                     # Create file/folder
PUT    /api/v1/files/:file_id            # Update file metadata
DELETE /api/v1/files/:file_id            # Delete file (soft delete)
GET    /api/v1/files/:file_id/versions   # Get version history
POST   /api/v1/files/:file_id/restore    # Restore to specific version
```

#### **Upload/Download**
```
POST   /api/v1/upload/initiate           # Start chunked upload
POST   /api/v1/upload/chunk              # Upload a chunk
POST   /api/v1/upload/complete           # Finalize upload
GET    /api/v1/download/:file_id         # Get download URL
GET    /api/v1/download/:file_id/chunk/:block_index  # Download specific chunk
```

#### **Sharing**
```
POST   /api/v1/files/:file_id/share      # Share file with user
DELETE /api/v1/files/:file_id/share/:permission_id  # Revoke access
GET    /api/v1/files/:file_id/permissions  # List permissions
POST   /api/v1/files/:file_id/link       # Create shareable link
GET    /api/v1/shared-with-me             # Files shared with current user
```

#### **Sync**
```
GET    /api/v1/sync/changes               # Get changes since last sync
POST   /api/v1/sync/commit                # Commit local changes
GET    /api/v1/sync/conflicts             # Get conflict list
POST   /api/v1/sync/resolve               # Resolve conflict
```

#### **Devices**
```
GET    /api/v1/devices                    # List user devices
POST   /api/v1/devices                    # Register device
DELETE /api/v1/devices/:device_id         # Unlink device
```

### WebSocket API (Real-time Sync)
```
WS     /api/v1/sync/stream
```

**Messages:**
```json
// Client → Server: Subscribe to updates
{
  "type": "subscribe",
  "device_id": "uuid",
  "last_sync_timestamp": "2024-01-01T00:00:00Z"
}

// Server → Client: File change notification
{
  "type": "file_changed",
  "file_id": "uuid",
  "action": "created|updated|deleted",
  "timestamp": "2024-01-01T00:00:00Z",
  "metadata": {...}
}

// Heartbeat
{
  "type": "ping"
}
```

---

## File Upload/Download Flow

### Upload Flow (Chunked Upload for Large Files)

```
┌────────┐                                                       ┌─────────────┐
│ Client │                                                       │   Server    │
└───┬────┘                                                       └──────┬──────┘
    │                                                                   │
    │  1. POST /upload/initiate                                        │
    │  { filename, size, mime_type, parent_id, checksum }             │
    ├──────────────────────────────────────────────────────────────►  │
    │                                                                   │
    │  2. Check deduplication (if checksum exists)                     │
    │     If exists: return existing file_id                           │
    │     Else: create file metadata, return upload_id & chunk_urls   │
    │  ◄──────────────────────────────────────────────────────────────┤
    │  { upload_id, file_id, chunk_size, presigned_urls[] }           │
    │                                                                   │
    │  3. Split file into chunks (4MB each)                            │
    │     Calculate chunk checksums                                    │
    │                                                                   │
    │  4. Upload chunks in parallel (using presigned S3 URLs)         │
    │  POST /upload/chunk (or directly to S3)                          │
    │  { upload_id, chunk_index, chunk_data, checksum }               │
    ├──────────────────────────────────────────────────────────────►  │
    │  ◄──────────────────────────────────────────────────────────────┤
    │  { chunk_index, status: "success" }                              │
    │                                                                   │
    │  5. All chunks uploaded                                          │
    │  POST /upload/complete                                           │
    │  { upload_id, file_id, chunk_checksums[] }                      │
    ├──────────────────────────────────────────────────────────────►  │
    │                                                                   │
    │  6. Verify all chunks, update metadata, trigger sync            │
    │  ◄──────────────────────────────────────────────────────────────┤
    │  { file_id, status: "complete", version: 1 }                    │
    │                                                                   │
    │  7. Publish to message queue for sync                            │
    │                                                         [Kafka]   │
    │                                                                   │
```

**Optimization Techniques:**
1. **Deduplication:** Check file checksum before upload
2. **Block-level dedup:** Check individual block hashes
3. **Parallel uploads:** Upload multiple chunks simultaneously
4. **Resumable uploads:** Track uploaded chunks, resume from failure point
5. **Compression:** Compress chunks before upload (gzip/brotli)

### Download Flow

```
┌────────┐                                                       ┌─────────────┐
│ Client │                                                       │   Server    │
└───┬────┘                                                       └──────┬──────┘
    │                                                                   │
    │  1. GET /download/:file_id                                       │
    ├──────────────────────────────────────────────────────────────►  │
    │                                                                   │
    │  2. Check permissions                                             │
    │     Generate presigned URLs for chunks (or CDN URLs)             │
    │  ◄──────────────────────────────────────────────────────────────┤
    │  { file_id, size, chunks: [{chunk_id, url, checksum}] }         │
    │                                                                   │
    │  3. Download chunks in parallel from S3/CDN                      │
    │                                                         [S3/CDN]  │
    │                                                                   │
    │  4. Verify chunk checksums, reassemble file                      │
    │                                                                   │
    │  5. Save to local filesystem                                     │
    │                                                                   │
```

**Optimization Techniques:**
1. **CDN caching:** Frequently accessed files served from edge locations
2. **Parallel downloads:** Download multiple chunks simultaneously
3. **Range requests:** Support HTTP range headers for partial downloads
4. **Smart sync:** Only download changed chunks (delta sync)

---

## Synchronization Strategy

### Sync Algorithm

**1. Polling-based Sync (Fallback)**
- Client polls every 30-60 seconds for changes
- Server returns list of changed files since last sync timestamp
- Client applies changes locally

**2. Push-based Sync (Primary)**
- WebSocket connection maintained between client and server
- Server pushes changes to all connected devices in real-time
- More efficient and lower latency

### Conflict Resolution

**Conflict Detection:**
- Occurs when same file modified on multiple devices before sync
- Detected using version numbers and checksums

**Resolution Strategies:**

1. **Last Write Wins (Default)**
   - Use timestamp to determine winner
   - Loser's version saved as conflict copy: `file (conflicted copy 2024-01-01).txt`

2. **Operational Transformation (Collaborative Editing)**
   - For real-time collaborative editing
   - Transform concurrent operations to maintain consistency
   - Used by Google Docs, similar approach for text files

3. **Manual Resolution**
   - Present both versions to user
   - User chooses which to keep

**Sync State Machine:**
```
┌─────────┐
│  Synced │ ◄───────────────────────┐
└────┬────┘                          │
     │                               │
     │ Local/Remote Change           │
     ▼                               │
┌─────────┐   Upload/Download   ┌────────┐
│ Pending │────────────────────►│ Syncing│
└────┬────┘                     └───┬────┘
     │                              │
     │ Conflict Detected            │ Success
     ▼                              │
┌──────────┐   Resolved             │
│ Conflict │────────────────────────┘
└──────────┘
```

### Delta Sync (Optimization)

For large file modifications, only sync changed blocks:

1. **Block-level diffing:** Use rolling hash (rsync algorithm)
2. **Only upload changed blocks**
3. **Server reconstructs file from old version + deltas**

**Example:**
- 50GB video file
- User edits 1 minute (~ 100MB)
- Only upload changed blocks (100MB) instead of entire 50GB

---

## Scalability & Performance

### Horizontal Scaling

**Stateless Application Servers:**
- Scale API servers horizontally behind load balancer
- Session state stored in Redis (shared)
- No server affinity required

**Database Scaling:**

1. **Read Replicas:**
   - Master for writes
   - Multiple read replicas for queries
   - Route read traffic to replicas

2. **Sharding:**
   - Shard by user_id (consistent hashing)
   - Each shard handles subset of users
   - Cross-shard queries avoided where possible

3. **Caching:**
   - Redis for metadata cache
   - Cache user info, file metadata, permissions
   - TTL: 5-10 minutes
   - Cache invalidation on updates

**Object Storage:**
- S3 automatically scales
- Unlimited capacity
- Region replication for global access

### Performance Optimizations

**1. Chunking:**
- Split files into 4MB chunks
- Parallel upload/download
- Resume from failure point

**2. Compression:**
- Compress chunks with gzip/brotli
- 50-70% size reduction for text files
- Skip for already compressed formats (jpg, mp4, zip)

**3. Deduplication:**
- Block-level deduplication
- Single storage for duplicate blocks

## Optimizations

### Advanced Performance Optimizations

#### 1. Adaptive Chunk Size

```python
class AdaptiveChunkSize:
    def __init__(self):
        self.min_chunk_size = 1 * 1024 * 1024  # 1MB
        self.max_chunk_size = 16 * 1024 * 1024  # 16MB
        self.current_chunk_size = 4 * 1024 * 1024  # 4MB
    
    def adjust_chunk_size(self, upload_rate: float, error_rate: float):
        if upload_rate > 50 * 1024 * 1024 and error_rate < 0.01:
            self.current_chunk_size = min(
                self.max_chunk_size,
                self.current_chunk_size * 1.5
            )
        elif error_rate > 0.05:
            self.current_chunk_size = max(
                self.min_chunk_size,
                self.current_chunk_size * 0.7
            )
```

#### 2. Intelligent Compression

```python
class IntelligentCompressor:
    def should_compress(self, file_data: bytes, content_type: str) -> bool:
        compressible_types = {
            'text/plain', 'text/html', 'application/json',
            'application/xml', 'text/css', 'application/javascript'
        }
        
        if content_type not in compressible_types:
            return False
        
        # Estimate compression ratio
        sample = file_data[:1024]
        compressed_sample = zlib.compress(sample, level=6)
        ratio = len(compressed_sample) / len(sample)
        
        return ratio < 0.8  # Compress if saves at least 20%
```

#### 3. Metadata Caching Optimization

```python
class MetadataCacheOptimizer:
    async def batch_get_metadata(self, file_ids: list) -> dict:
        # Batch fetch from cache
        cached = await self.cache.mget([f"file:{id}" for id in file_ids])
        
        # Fetch missing from database
        missing_ids = [file_ids[i] for i, c in enumerate(cached) if c is None]
        if missing_ids:
            db_results = await self.db.batch_get_metadata(missing_ids)
            # Cache results
            for file_id, metadata in db_results.items():
                await self.cache.set(f"file:{file_id}", metadata, ttl=3600)
            cached.update(db_results)
        
        return cached
```

#### 4. Delta Sync Optimization

```python
class DeltaSyncOptimizer:
    async def get_changes_efficient(self, file_id: str, local_chunks: list):
        # Get remote chunk checksums only (not full chunks)
        remote_checksums = await self.get_chunk_checksums(file_id)
        local_checksums = [c['checksum'] for c in local_chunks]
        
        # Find missing/changed chunks using set operations
        remote_set = set(remote_checksums)
        local_set = set(local_checksums)
        
        missing = remote_set - local_set
        changed = [
            i for i, (local, remote) in enumerate(zip(local_checksums, remote_checksums))
            if local != remote
        ]
        
        return {'missing': missing, 'changed': changed}
```
- Saves 40-60% storage on average

**4. CDN:**
- Edge caching for popular files
- Reduced latency (50-100ms → 10-20ms)
- Reduced load on origin servers

**5. Connection Pooling:**
- Reuse database connections
- Reuse HTTP connections

**6. Async Processing:**
- Message queue for non-critical operations
- Thumbnail generation
- Virus scanning
- Indexing for search

### Capacity Planning

**Storage:**
- 100M users × 1TB avg = 100PB
- With deduplication (50%) = 50PB
- Replication factor (3x) = 150PB
- AWS S3: $0.023/GB/month = $3.5M/month

**Bandwidth:**
- 400TB/day upload + 1.2PB/day download = 1.6PB/day
- Monthly: 48PB
- AWS data transfer: ~$3M/month

**Database:**
- Metadata per file: ~1KB
- 100M users × 10,000 files = 1T files
- 1TB metadata
- With indexes: ~5TB
- PostgreSQL cluster: $50K/month

**Servers:**
- 20M DAU, 100 req/user/day = 2B requests/day
- 23K req/sec average, 100K peak
- 1000 API servers @ 100 req/sec each
- AWS EC2: $100K/month

**Total Infrastructure Cost:** ~$7M/month

---

## Security & Reliability

### Security Measures

**1. Authentication & Authorization:**
- JWT tokens with short expiration (15 min)
- Refresh tokens for session renewal
- OAuth 2.0 integration (Google, Apple)
- MFA support

**2. Encryption:**
- **In Transit:** TLS 1.3 for all connections
- **At Rest:** AES-256 encryption
  - Server-side encryption in S3
  - Encrypted database volumes
- **End-to-End Encryption (Optional):**
  - Client encrypts before upload
  - Zero-knowledge architecture
  - Keys never leave client

**3. Access Control:**
- Role-based permissions (view, edit, owner)
- Fine-grained file/folder permissions
- Time-limited shareable links
- Password-protected links

**4. Security Hardening:**
- Input validation and sanitization
- SQL injection prevention (parameterized queries)
- XSS protection
- CSRF tokens
- Rate limiting (100 req/min per user)
- DDoS protection (CloudFlare/AWS Shield)

**5. Virus Scanning:**
- Scan uploads with ClamAV or VirusTotal API
- Quarantine infected files
- Notify users

**6. Audit Logging:**
- Log all file access and modifications
- IP tracking
- Compliance with SOC 2, GDPR

### Reliability & Data Integrity

**1. Replication:**
- S3 cross-region replication
- Database multi-AZ deployment
- 3x replication for durability

**2. Backup:**
- Automated daily backups
- Point-in-time recovery
- 30-day retention

**3. Checksums:**
- SHA-256 for file integrity
- Verify on upload and download
- Detect corruption

**4. Versioning:**
- Keep last 100 versions per file
- Restore deleted files (trash, 30-day retention)
- User-initiated restore

**5. Monitoring & Alerting:**
- Real-time monitoring (Datadog, Prometheus)
- Alerts for:
  - High error rates
  - Latency spikes
  - Storage capacity
  - Service health
- On-call rotation for incidents

**6. Disaster Recovery:**
- RPO (Recovery Point Objective): 1 hour
- RTO (Recovery Time Objective): 4 hours
- Failover to backup region
- Regular DR drills

---

## Trade-offs & Design Decisions

### 1. **Chunking vs Full File Upload**

**Decision:** Use chunking (4MB chunks)

**Pros:**
- Resumable uploads
- Parallel uploads (faster)
- Better deduplication
- Handles large files (50GB)

**Cons:**
- More complex implementation
- Additional overhead for small files

**Trade-off:** Worth the complexity for better performance and reliability.

---

### 2. **Push vs Pull Sync**

**Decision:** Use push (WebSocket) with pull fallback

**Pros:**
- Real-time updates (low latency)
- Reduced server load (no constant polling)
- Better UX

**Cons:**
- Requires persistent connections
- More complex server-side

**Trade-off:** Push for better UX, pull as fallback for reliability.

---

### 3. **SQL vs NoSQL for Metadata**

**Decision:** PostgreSQL (SQL)

**Pros:**
- ACID guarantees for consistency
- Complex queries (permissions, sharing, nested folders)
- Strong schema enforcement
- JSON support for flexibility

**Cons:**
- Harder to scale horizontally
- More complex sharding

**Trade-off:** Consistency and complex queries more important than write scalability.

---

### 4. **Block-level vs File-level Deduplication**

**Decision:** Block-level deduplication

**Pros:**
- Better space savings (40-60%)
- Delta sync for large files
- Efficient versioning

**Cons:**
- More complex
- Overhead for small files

**Trade-off:** Significant storage savings justify complexity.

---

### 5. **Eventual Consistency vs Strong Consistency**

**Decision:** Strong consistency for metadata, eventual for content

**Pros:**
- Metadata consistency critical (permissions, ownership)
- Content can tolerate brief delays
- Better performance

**Cons:**
- Sync conflicts possible
- Need conflict resolution

**Trade-off:** Balance between consistency and performance.

---

### 6. **Self-hosted Storage vs Cloud (S3)**

**Decision:** Cloud storage (S3/GCS)

**Pros:**
- Virtually unlimited scalability
- 11 nines durability
- No hardware management
- Built-in replication and versioning
- Cost-effective at scale

**Cons:**
- Vendor lock-in
- Ongoing costs
- Less control

**Trade-off:** Operational simplicity and reliability outweigh costs.

---

### 7. **Monolith vs Microservices**

**Decision:** Microservices architecture

**Pros:**
- Independent scaling (metadata service vs block service)
- Fault isolation
- Team autonomy
- Technology flexibility

**Cons:**
- More operational complexity
- Network latency between services
- Distributed tracing needed

**Trade-off:** Scalability and team autonomy worth the complexity.

---

### 8. **Optimistic Locking vs Pessimistic Locking**

**Decision:** Optimistic locking with version numbers

**Pros:**
- Better performance (no locks held)
- No deadlocks
- Works well for read-heavy workload

**Cons:**
- Need conflict resolution
- Retries on conflicts

**Trade-off:** Better performance for read-heavy workload.

---

## Advanced Features Implementation

### Collaborative Editing

**Architecture:**
```
┌─────────┐       ┌─────────┐       ┌─────────┐
│ User A  │       │ User B  │       │ User C  │
└────┬────┘       └────┬────┘       └────┬────┘
     │                 │                 │
     └────────┬────────┴────────┬────────┘
              │                 │
              ▼                 ▼
       ┌──────────────────────────────┐
       │  Collaboration Server        │
       │  (Operational Transform)     │
       └──────────────┬───────────────┘
                      │
                      ▼
               ┌─────────────┐
               │  Document   │
               │   State     │
               └─────────────┘
```

**Implementation:**
- Use Operational Transformation (OT) or CRDT
- Real-time WebSocket connections
- Transform concurrent edits
- Maintain document consistency
- Show presence indicators
- Cursor positions

---

### Desktop Daemon (Auto-sync)

**Architecture:**
```
┌──────────────────────────────────────┐
│         Desktop Daemon               │
│  ┌────────────┐    ┌──────────────┐ │
│  │  Watcher   │───►│   Sync       │ │
│  │  Service   │    │   Engine     │ │
│  └────────────┘    └──────┬───────┘ │
│         ▲                  │         │
│         │                  ▼         │
│  ┌──────┴──────┐    ┌──────────────┐│
│  │Local FileDB │    │  API Client  ││
│  └─────────────┘    └──────┬───────┘│
└────────────────────────────┼────────┘
                             │
                             ▼
                      ┌─────────────┐
                      │   Server    │
                      └─────────────┘
```

**Features:**
- Watch folder for changes (FS events)
- Intelligent batching (don't sync temp files)
- Bandwidth throttling
- Selective sync (choose folders)
- Pause/resume sync
- LAN sync (peer-to-peer between devices on same network)

---

### File Versioning

**Implementation:**
- Store deltas between versions
- Keep last 100 versions
- Compress old versions
- Automatic cleanup of very old versions
- Restore to any version
- Compare versions (diff)

---

### Search & Indexing

**Architecture:**
- Use Elasticsearch for full-text search
- Index file names, content (for text files), metadata
- OCR for scanned documents
- Face recognition for photos
- Tag-based search

---

## Deep Dive Areas

### Deep Dive 1: Pre-signed URLs for Secure File Access

#### What are Pre-signed URLs?

Pre-signed URLs are time-limited, cryptographically signed URLs that grant temporary access to private objects in cloud storage (S3, GCS, Azure Blob) without requiring the user to have direct access credentials.

#### Components of a Pre-signed URL

**1. Base URL:**
```
https://dropbox-storage.s3.amazonaws.com/blocks/user_123/file_abc/chunk_001.bin
```

**2. Query Parameters:**
```
?X-Amz-Algorithm=AWS4-HMAC-SHA256
&X-Amz-Credential=AKIAIOSFODNN7EXAMPLE/20240101/us-east-1/s3/aws4_request
&X-Amz-Date=20240101T120000Z
&X-Amz-Expires=3600
&X-Amz-SignedHeaders=host
&X-Amz-Signature=abc123def456...
```

**Parameter Breakdown:**

| Parameter | Purpose | Example Value |
|-----------|---------|---------------|
| **X-Amz-Algorithm** | Hashing algorithm used | AWS4-HMAC-SHA256 |
| **X-Amz-Credential** | Scope of credentials (access key ID + date + region + service) | AKIAIO.../20240101/us-east-1/s3/aws4_request |
| **X-Amz-Date** | Timestamp when URL was generated | 20240101T120000Z (ISO 8601) |
| **X-Amz-Expires** | Validity duration in seconds | 3600 (1 hour) |
| **X-Amz-SignedHeaders** | Headers included in signature | host |
| **X-Amz-Signature** | HMAC-SHA256 signature | abc123def456... (hex-encoded) |
| **X-Amz-Security-Token** (optional) | Session token for temporary credentials | FwoGZXIv... |

**For Downloads (HTTP GET):**
```
GET https://dropbox-storage.s3.amazonaws.com/blocks/abc123.bin
    ?X-Amz-Algorithm=AWS4-HMAC-SHA256
    &X-Amz-Credential=AKIAIO.../20240101/us-east-1/s3/aws4_request
    &X-Amz-Date=20240101T120000Z
    &X-Amz-Expires=3600
    &X-Amz-SignedHeaders=host
    &X-Amz-Signature=abc123...
```

**For Uploads (HTTP PUT):**
```
PUT https://dropbox-storage.s3.amazonaws.com/blocks/xyz789.bin
    ?X-Amz-Algorithm=AWS4-HMAC-SHA256
    &X-Amz-Credential=AKIAIO.../20240101/us-east-1/s3/aws4_request
    &X-Amz-Date=20240101T120000Z
    &X-Amz-Expires=900
    &X-Amz-SignedHeaders=host;content-type
    &X-Amz-Signature=def456...
    &Content-Type=application/octet-stream
```

#### Signature Generation Process

**Step 1: Create Canonical Request**
```
HTTP_METHOD\n
CANONICAL_URI\n
CANONICAL_QUERY_STRING\n
CANONICAL_HEADERS\n
SIGNED_HEADERS\n
HASHED_PAYLOAD
```

**Example:**
```
GET
/blocks/abc123.bin
X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=...&X-Amz-Date=20240101T120000Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host
host:dropbox-storage.s3.amazonaws.com

host
UNSIGNED-PAYLOAD
```

**Step 2: Create String to Sign**
```
AWS4-HMAC-SHA256
20240101T120000Z
20240101/us-east-1/s3/aws4_request
<SHA256-hash-of-canonical-request>
```

**Step 3: Calculate Signing Key (using HMAC)**
```
kDate = HMAC-SHA256("AWS4" + SecretAccessKey, "20240101")
kRegion = HMAC-SHA256(kDate, "us-east-1")
kService = HMAC-SHA256(kRegion, "s3")
kSigning = HMAC-SHA256(kService, "aws4_request")
```

**Step 4: Calculate Signature**
```
signature = HMAC-SHA256(kSigning, stringToSign)
signature_hex = hexEncode(signature)
```

#### What Data is Hashed in the Signature?

The signature includes:

1. **Resource Path:** `/blocks/abc123.bin` - Ensures URL can't be modified to access different files
2. **Query Parameters:** All `X-Amz-*` parameters - Prevents tampering with expiration, algorithm, etc.
3. **HTTP Method:** GET, PUT, DELETE - Prevents method substitution attacks
4. **Headers:** `host`, `content-type` (if signed) - Ensures headers can't be modified
5. **Expiration Time:** Via X-Amz-Date + X-Amz-Expires - Enforces time limit
6. **Scope:** Date, region, service - Limits where signature is valid
7. **Secret Key:** AWS Secret Access Key - Only server knows this, proves authenticity

#### Why Each Component is Necessary

**1. Expiration (X-Amz-Expires):**
- **Security:** Limits damage if URL is leaked or intercepted
- **Use Case:** Download link expires after 1 hour; upload link expires after 15 minutes
- **Prevention:** Stops indefinite access to private files

**2. Signature (X-Amz-Signature):**
- **Authentication:** Proves request was authorized by someone with secret key
- **Integrity:** Ensures URL parameters haven't been modified
- **Non-repudiation:** Only server with secret key can generate valid signature
- **Prevention:** Stops attackers from:
  - Extending expiration time
  - Changing HTTP method (GET → DELETE)
  - Accessing different resources
  - Modifying allowed operations

**3. Algorithm (X-Amz-Algorithm):**
- Specifies cryptographic hash (HMAC-SHA256)
- Prevents downgrade attacks to weaker algorithms

**4. Date (X-Amz-Date):**
- Prevents replay attacks
- Used with expiration to determine validity window
- Included in signature to prevent time manipulation

**5. Credential Scope:**
- Limits signature validity to specific:
  - Date (signature expires daily)
  - Region (us-east-1, eu-west-1)
  - Service (s3, dynamodb)
- Prevents signature reuse across services/regions

#### How Signature Prevents Tampering

**Scenario 1: Attacker tries to extend expiration**
```
Original: ...&X-Amz-Expires=3600&X-Amz-Signature=abc123...
Modified: ...&X-Amz-Expires=86400&X-Amz-Signature=abc123...
```
❌ **Result:** Signature validation fails because `3600` was in the signed data, but URL now says `86400`. Server recalculates signature with `86400` and gets different hash.

**Scenario 2: Attacker tries to access different file**
```
Original: /blocks/file_001.bin?...&X-Amz-Signature=abc123...
Modified: /blocks/file_002.bin?...&X-Amz-Signature=abc123...
```
❌ **Result:** Signature validation fails because path `/blocks/file_001.bin` was signed, but request is for `/blocks/file_002.bin`.

**Scenario 3: Attacker tries to change method**
```
Original: GET /blocks/file_001.bin?...&X-Amz-Signature=abc123...
Modified: DELETE /blocks/file_001.bin?...&X-Amz-Signature=abc123...
```
❌ **Result:** Signature validation fails because HTTP method `GET` was signed, not `DELETE`.

**Scenario 4: Replay attack after expiration**
```
Time T+0:    GET with valid signature (X-Amz-Expires=3600)
Time T+7200: Replay same GET request
```
❌ **Result:** Request rejected because `X-Amz-Date + X-Amz-Expires` < current time.

#### Implementation in Dropbox Design

**When Client Requests Upload:**

```
Client                                    API Server                            S3
  |                                           |                                  |
  | 1. POST /upload/initiate                 |                                  |
  |    { filename, size, checksum }          |                                  |
  |----------------------------------------->|                                  |
  |                                           |                                  |
  |                                           | 2. Generate pre-signed URLs     |
  |                                           |    for each chunk (PUT)          |
  |                                           |    Expiry: 15 minutes            |
  |                                           |                                  |
  |  3. Return upload_id + presigned_urls[]  |                                  |
  |<-----------------------------------------|                                  |
  |  [                                        |                                  |
  |    "https://s3.../chunk_0?X-Amz-...",   |                                  |
  |    "https://s3.../chunk_1?X-Amz-...",   |                                  |
  |  ]                                        |                                  |
  |                                           |                                  |
  | 4. PUT chunk_0 directly to S3            |                                  |
  |    using presigned URL                   |                                  |
  |-------------------------------------------------------------------------->|
  |                                           |                                  |
  |  5. 200 OK                                |                                  |
  |<--------------------------------------------------------------------------|
  |                                           |                                  |
  | 6. POST /upload/complete                 |                                  |
  |    { upload_id, checksums[] }            |                                  |
  |----------------------------------------->|                                  |
  |                                           |                                  |
  |                                           | 7. Verify chunks in S3           |
  |                                           |--------------------------------->|
  |                                           |                                  |
  |  8. Success                               |                                  |
  |<-----------------------------------------|                                  |
```

**Benefits:**

1. **No Proxy Overhead:** Client uploads directly to S3, not through API servers
2. **Reduced Latency:** Data doesn't traverse API servers
3. **Scalability:** S3 handles upload traffic, not our servers
4. **Security:** Time-limited access, can't be reused
5. **Cost:** Reduced bandwidth costs on API servers

**When Client Requests Download:**

```
Client                                    API Server                            CDN/S3
  |                                           |                                  |
  | 1. GET /download/:file_id                |                                  |
  |----------------------------------------->|                                  |
  |                                           |                                  |
  |                                           | 2. Check permissions             |
  |                                           | 3. Generate presigned URLs       |
  |                                           |    for each chunk (GET)          |
  |                                           |    Expiry: 1 hour                |
  |                                           |                                  |
  |  4. Return presigned_urls[]              |                                  |
  |<-----------------------------------------|                                  |
  |  [                                        |                                  |
  |    "https://cdn.../chunk_0?X-Amz-...",  |                                  |
  |    "https://cdn.../chunk_1?X-Amz-...",  |                                  |
  |  ]                                        |                                  |
  |                                           |                                  |
  | 5. GET chunk_0 directly from CDN/S3      |                                  |
  |-------------------------------------------------------------------------->|
  |                                           |                                  |
  |  6. Chunk data                            |                                  |
  |<--------------------------------------------------------------------------|
  |                                           |                                  |
  | 7. Verify checksum, reassemble file      |                                  |
```

**Configuration Parameters:**

| Operation | Expiry | HTTP Method | Additional Headers |
|-----------|--------|-------------|-------------------|
| Upload chunk | 15 min | PUT | Content-Type, Content-Length |
| Download chunk | 1 hour | GET | None |
| Download thumbnail | 24 hours | GET | None |
| Delete (admin) | 5 min | DELETE | None |

#### Security Considerations

**1. Short Expiration Times:**
- Uploads: 15 minutes (enough for chunk upload, not long-lived)
- Downloads: 1 hour (enough for file download, limits sharing window)
- Admin operations: 5 minutes (highly sensitive)

**2. One-Time Use (Optional):**
- Generate unique signature per request
- Track used signatures in Redis
- Reject duplicate usage

**3. IP Whitelisting (Optional):**
- Include client IP in signature
- Validate IP matches on S3 access
- Prevents URL sharing across networks

**4. Content-Type Enforcement:**
- Sign Content-Type header for uploads
- Prevents uploading malicious file types
- Example: Sign `Content-Type: image/png`, reject if client sends `Content-Type: text/html`

**5. Rate Limiting:**
- Limit pre-signed URL generation per user
- 100 URLs per minute per user
- Prevents DoS by URL generation spam

---

### Deep Dive 2: Handling Spiky Traffic & Auto-Scaling

#### Understanding Traffic Patterns

**Typical Dropbox Traffic Characteristics:**

1. **Daily Patterns:**
   - Peak: 9 AM - 5 PM (business hours)
   - Off-peak: 11 PM - 6 AM
   - Peak/off-peak ratio: 10:1

2. **Weekly Patterns:**
   - Monday morning: High (weekend backlog sync)
   - Friday evening: High (backup before weekend)
   - Weekend: 30% of weekday traffic

3. **Event-Driven Spikes:**
   - Product launches: 100x normal upload traffic
   - Viral content sharing: 50x download spikes
   - Ransomware scares: 200x backup traffic
   - School semester start: 20x student traffic

**Traffic Profile Example:**
```
Baseline: 20K requests/sec
Peak (business hours): 100K req/sec (5x)
Spike (viral event): 500K req/sec (25x)
Flash spike (automated bot): 2M req/sec (100x)
```

#### Auto-Scaling Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       CloudWatch / Metrics                       │
│  (CPU, Memory, Request Rate, Queue Depth, Latency)              │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│              Auto Scaling Manager (AWS ASG / K8s HPA)           │
│  • Scale-out triggers: CPU > 70%, Queue depth > 1000           │
│  • Scale-in triggers: CPU < 30%, Queue depth < 100             │
│  • Cooldown: 5 min scale-out, 15 min scale-in                  │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Application Server Pool                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ Server 1 │  │ Server 2 │  │ Server 3 │  │ Server N │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
│  Min: 100 instances         Max: 5000 instances                 │
└─────────────────────────────────────────────────────────────────┘
```

#### Scaling Strategies by Component

**1. API Servers (Stateless)**

**Metrics to Monitor:**
- CPU Utilization: Target 60-70%
- Request Latency: p99 < 200ms
- Request Rate: per instance capacity
- Error Rate: < 0.1%

**Scaling Policy:**
```yaml
scale_out:
  - trigger: CPU > 70% for 2 minutes
    action: Add 20% more instances
    max: 5000 instances
  - trigger: Request latency p99 > 500ms for 3 minutes
    action: Add 30% more instances
  - trigger: Queue depth > 1000
    action: Add 50% more instances (aggressive)

scale_in:
  - trigger: CPU < 30% for 15 minutes
    action: Remove 10% of instances
    min: 100 instances
  - trigger: Request rate < 50 req/sec per instance for 10 minutes
    action: Remove 15% of instances

cooldown:
  scale_out: 3 minutes
  scale_in: 15 minutes  # Conservative to avoid thrashing
```

**Provisioning Strategy:**

- **Base Capacity:** 100 instances (always on)
- **On-Demand Scaling:** 0 → 1000 instances (quick response)
- **Spot Instances:** 1000 → 5000 instances (cost optimization, can handle interruption)
- **Warmup Time:** 90 seconds (container start + health check)

**2. WebSocket Servers (Stateful)**

**Challenge:** Can't terminate connections arbitrarily

**Scaling Strategy:**

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   WS Pool 1  │     │   WS Pool 2  │     │   WS Pool 3  │
│  (10K conns) │     │  (10K conns) │     │  (10K conns) │
└──────────────┘     └──────────────┘     └──────────────┘
        │                    │                    │
        └────────────────────┴────────────────────┘
                             │
                      Redis Pub/Sub
                    (Message Broadcast)
```

**Graceful Scaling:**

- **Scale-out:** Launch new servers, new connections go to them
- **Scale-in:** 
  1. Mark server as "draining"
  2. Stop accepting new connections
  3. Wait for existing connections to close naturally (client refresh, disconnect)
  4. Force close after 24 hours
  5. Terminate server

**Metric:**
- Connections per server: 5K - 10K optimal
- Memory per connection: 10KB
- Scale out when: avg connections > 8K per server

**3. Database (PostgreSQL)**

**Vertical Scaling (Short-term spikes):**
- Can upgrade instance size (e.g., db.r6g.4xlarge → db.r6g.8xlarge)
- Takes 5-10 minutes
- Good for planned events

**Read Replicas (Sustained high read traffic):**
```
┌──────────┐
│  Master  │ ──────┬──────┬──────┬──────┐
│ (Writes) │       │      │      │      │
└──────────┘       ▼      ▼      ▼      ▼
              ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
              │Replica1│ │Replica2│ │Replica3│ │ReplicaN│
              │(Reads) │ │(Reads) │ │(Reads) │ │(Reads) │
              └────────┘ └────────┘ └────────┘ └────────┘
```

- Add replicas dynamically (5-15 min to provision)
- Route read queries to replicas via read endpoint
- Write queries always go to master

**Connection Pooling:**
```
Application Servers (5000)
         │
         ▼
  ┌─────────────┐
  │   PgBouncer │  (Connection pooler)
  │  100 conns  │  (Transaction mode)
  └──────┬──────┘
         │
         ▼
    PostgreSQL Master
    (Max 100 connections instead of 5000)
```

**Benefits:**
- Reduces connection overhead on database
- Handles 5000 app servers with 100 DB connections
- Fast connection reuse

**4. Message Queue (Kafka)**

**Auto-scaling Topics:**

```yaml
topic: file_upload_events
partitions: 100  # Can scale up to 1000
replication_factor: 3

consumer_groups:
  - sync_service:
      instances: 20  # Scale 5 → 100 based on lag
      max_instances: 100
  - notification_service:
      instances: 10
      max_instances: 50
```

**Scaling Trigger:**
- Consumer lag > 10,000 messages: Add consumers
- Consumer lag < 100 messages: Remove consumers
- Partition rebalancing: Automatic

**5. Object Storage (S3)**

- **No scaling needed:** S3 auto-scales infinitely
- **Performance:** 3,500 PUT/s and 5,500 GET/s per prefix
- **Optimization:** Use randomized prefixes to distribute load
  ```
  Bad:  /uploads/2024-01-01/file1.bin  (hot prefix)
  Good: /uploads/a7/2b/file1.bin       (distributed)
  ```

#### Rate Limiting Strategy

**Per-User Rate Limits:**

```python
rate_limits = {
    "free_tier": {
        "api_requests": 100 / minute,
        "upload_bandwidth": 10 MB/s,
        "download_bandwidth": 50 MB/s,
        "file_uploads": 10 / hour,
    },
    "paid_tier": {
        "api_requests": 1000 / minute,
        "upload_bandwidth": 100 MB/s,
        "download_bandwidth": 500 MB/s,
        "file_uploads": 1000 / hour,
    },
    "enterprise_tier": {
        "api_requests": 10000 / minute,
        "upload_bandwidth": 1 GB/s,
        "download_bandwidth": 5 GB/s,
        "file_uploads": "unlimited",
    }
}
```

**Implementation (Token Bucket Algorithm):**

```
Redis Key: rate_limit:user_123:api_requests
Value: { tokens: 100, last_refill: timestamp }

On each request:
1. Check tokens available
2. If tokens > 0: Allow request, decrement token
3. If tokens = 0: Reject with 429 Too Many Requests
4. Refill tokens at rate (100 tokens/minute = 1.67 tokens/sec)
```

**Adaptive Rate Limiting:**

During high load:
- Reduce free tier limits by 50%
- Reduce paid tier limits by 20%
- Enterprise tier unchanged
- Return `Retry-After` header

**Global Rate Limiting (DDoS Protection):**

```
Layer 7 (Application):
- Max 100K requests/sec globally
- If exceeded: Enable CAPTCHA for new sessions
- Block suspicious IPs (Redis + WAF)

Layer 4 (Network):
- AWS Shield / CloudFlare
- SYN flood protection
- IP reputation filtering
```

#### Queue-Based Load Leveling

**Problem:** Upload spike (100K files/sec) → Processing can't keep up

**Solution:** Decouple ingestion from processing

```
Client Uploads
      ↓
  API Server
      ↓
  [Accept & Return 202 Accepted]
      ↓
  Message Queue (Kafka/SQS)
      ↓
  Worker Pool (Auto-scales)
      ↓
  Processing (virus scan, thumbnail, index)
```

**Benefits:**
1. **Smooths spikes:** Queue absorbs burst traffic
2. **Fast response:** Client gets immediate 202 response
3. **Independent scaling:** Workers scale based on queue depth
4. **Retry logic:** Failed processing automatically retried
5. **Priority queues:** Critical operations processed first

**Example:**
```
Normal: 100 uploads/sec → 100 workers process immediately
Spike: 10,000 uploads/sec → Queue builds to 500K messages
       → Workers scale from 100 → 2000
       → Process 10K/sec, drain queue in 50 seconds
```

#### Circuit Breaker Pattern

**Problem:** Database overload → Slow responses → Thread exhaustion → Cascading failure

**Solution:** Circuit breaker

```
States:
1. CLOSED: Normal operation, requests pass through
2. OPEN: Service degraded, fail fast (return cached data or error)
3. HALF_OPEN: Testing recovery, allow limited requests

Transitions:
CLOSED → OPEN: After 50% error rate for 10 seconds
OPEN → HALF_OPEN: After 30 seconds cooldown
HALF_OPEN → CLOSED: After 10 successful requests
HALF_OPEN → OPEN: After 3 failed requests
```

**Example (Database Circuit Breaker):**

```
Normal operation (CLOSED):
- All queries go to database
- Error rate: 0.5%

Database overloaded (OPEN):
- Return cached metadata (Redis)
- Return 503 for writes
- Error rate: 50% → Prevent cascading failure

Recovery (HALF_OPEN):
- Allow 10 test queries
- If successful → CLOSED
- If failed → OPEN for another 30 sec
```

#### Backpressure Mechanisms

**Problem:** Downstream service slow → Upstream overwhelms it

**Solution:** Backpressure

**1. HTTP 429 (Too Many Requests):**
```
Response:
HTTP/1.1 429 Too Many Requests
Retry-After: 60
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1640000000
```

**2. Queue Depth Monitoring:**
```
If queue_depth > 100K messages:
  - Return 503 Service Unavailable
  - Client backs off exponentially
  - Prevents queue overflow
```

**3. TCP Flow Control:**
```
- Server advertises small receive window
- Client slows sending rate
- Prevents network buffer overflow
```

#### Pre-Scaling for Known Events

**Scenario:** Product launch on Monday 9 AM, expecting 100x traffic

**Preparation:**

**T-24 hours:**
- Increase database instance size
- Pre-scale API servers to 50% of expected peak (500 instances)
- Increase Kafka partitions
- Warm up caches with likely-accessed data
- Notify CDN provider of expected spike

**T-1 hour:**
- Scale API servers to 80% of expected peak (800 instances)
- Enable aggressive rate limiting for free tier
- Put all engineers on standby
- Enable detailed monitoring (1-second granularity)

**T-0 (Launch):**
- Auto-scaling takes over
- Monitor dashboards for anomalies
- Manual intervention if needed

**T+2 hours (Post-peak):**
- Gradually scale down
- Analyze metrics
- Adjust thresholds for next time

#### Cost Optimization During Spikes

**Spot Instances:**
- 70% cheaper than on-demand
- Use for stateless workloads (API servers, workers)
- Graceful handling of interruptions

**Reserved Instances:**
- Baseline capacity (100 servers)
- 40% cheaper than on-demand
- 1-year commitment

**On-Demand:**
- Spike capacity (100 → 1000 servers)
- Pay-per-use
- No commitment

**Cost Profile:**
```
Baseline (100 servers):
- 80 reserved: $10K/month
- 20 on-demand: $5K/month
Total: $15K/month

Peak (1000 servers):
- 80 reserved: $10K/month
- 120 on-demand: $30K/month
- 800 spot: $35K/month
Total: $75K/month (only during peak hours)
```

#### Monitoring & Alerting for Spikes

**Key Metrics:**

| Metric | Normal | Warning | Critical |
|--------|--------|---------|----------|
| API Latency (p99) | 100ms | 500ms | 1000ms |
| Error Rate | 0.1% | 1% | 5% |
| CPU Utilization | 40% | 70% | 85% |
| Queue Depth | 100 | 10K | 100K |
| DB Connections | 50 | 80 | 95 |
| Disk I/O Wait | 5% | 30% | 60% |

**Alert Escalation:**

1. **Warning:** Slack notification to team channel
2. **Critical:** PagerDuty alert to on-call engineer + Email to team leads
3. **Emergency:** Phone call to on-call + VP Engineering

**Dashboards:**
- Real-time traffic (requests/sec, bandwidth)
- Error rates by endpoint
- Latency percentiles (p50, p90, p99, p99.9)
- Auto-scaling activity
- Cost tracking

---

### Deep Dive 3: Multi-Client State Management

#### The Challenge

**Scenario:**
- User has 5 devices: Desktop (home), Desktop (work), Laptop, Phone, Tablet
- User logs in simultaneously on all devices
- User modifies `report.docx` on Desktop (work) at 2:00 PM
- How do other 4 devices learn about the change?
- What if user also modified `report.docx` on Laptop at 2:00:01 PM?

**Requirements:**
1. **Multiple concurrent sessions** per user
2. **Device-specific state** (sync status, local changes)
3. **Real-time synchronization** across devices
4. **Conflict detection and resolution**
5. **Offline support** (edit while disconnected, sync later)

#### Architecture for Multi-Client State

```
┌─────────────────────────────────────────────────────────────────┐
│                       User's Devices                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ Desktop1 │  │ Desktop2 │  │  Laptop  │  │  Mobile  │       │
│  │ (home)   │  │ (work)   │  │          │  │          │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
│       │             │             │             │               │
└───────┼─────────────┼─────────────┼─────────────┼───────────────┘
        │             │             │             │
        └─────────────┴─────────────┴─────────────┘
                          │
          ┌───────────────┴────────────────┐
          │      Load Balancer             │
          └───────────────┬────────────────┘
                          │
          ┌───────────────┴────────────────┐
          │   WebSocket Server Pool        │
          │  ┌─────────┐    ┌─────────┐   │
          │  │  WS-1   │    │  WS-2   │   │
          │  │ (Dev1+2)│    │(Dev3+4) │   │
          │  └────┬────┘    └────┬────┘   │
          └───────┼──────────────┼─────────┘
                  │              │
                  └──────┬───────┘
                         │
          ┌──────────────▼─────────────────┐
          │    Redis Pub/Sub               │
          │  (Broadcast to all WS servers) │
          └──────────────┬─────────────────┘
                         │
          ┌──────────────▼─────────────────┐
          │    Kafka Event Stream          │
          │  Topic: user_123_file_changes  │
          └──────────────┬─────────────────┘
                         │
          ┌──────────────▼─────────────────┐
          │  PostgreSQL (Metadata)         │
          │  + Redis (Session/Sync State)  │
          └────────────────────────────────┘
```

#### Session Management

**Database Schema (Enhanced):**

```sql
-- Sessions Table
CREATE TABLE sessions (
    session_id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    device_id UUID REFERENCES devices(device_id) ON DELETE CASCADE,
    access_token VARCHAR(500) NOT NULL,
    refresh_token VARCHAR(500),
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    last_activity_at TIMESTAMP DEFAULT NOW(),
    ip_address INET,
    user_agent TEXT,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_sessions_user ON sessions(user_id, is_active);
CREATE INDEX idx_sessions_device ON sessions(device_id, is_active);
CREATE INDEX idx_sessions_token ON sessions(access_token);

-- Device Sync State (per device, per file)
CREATE TABLE device_sync_state (
    sync_state_id UUID PRIMARY KEY,
    device_id UUID REFERENCES devices(device_id) ON DELETE CASCADE,
    file_id UUID REFERENCES files(file_id) ON DELETE CASCADE,
    state VARCHAR(20) NOT NULL, -- 'synced', 'pending_upload', 'pending_download', 'conflict'
    local_version INTEGER,
    remote_version INTEGER,
    local_checksum VARCHAR(64),
    remote_checksum VARCHAR(64),
    last_sync_time TIMESTAMP,
    last_modified_time TIMESTAMP,
    conflict_reason TEXT,
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(device_id, file_id),
    CONSTRAINT check_state CHECK (state IN ('synced', 'pending_upload', 'pending_download', 'conflict', 'error'))
);

CREATE INDEX idx_device_sync_device ON device_sync_state(device_id, state);
CREATE INDEX idx_device_sync_file ON device_sync_state(file_id);

-- User-level file state (authoritative version)
CREATE TABLE file_state (
    file_id UUID PRIMARY KEY REFERENCES files(file_id) ON DELETE CASCADE,
    current_version INTEGER NOT NULL,
    current_checksum VARCHAR(64) NOT NULL,
    last_modified_by UUID REFERENCES users(user_id),
    last_modified_device UUID REFERENCES devices(device_id),
    last_modified_time TIMESTAMP NOT NULL,
    lock_held_by UUID REFERENCES devices(device_id), -- For collaborative editing
    lock_expires_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_file_state_modified ON file_state(last_modified_time);
CREATE INDEX idx_file_state_lock ON file_state(lock_held_by, lock_expires_at);
```

#### Redis State (Fast Access)

**Session State (TTL: 1 hour):**
```json
Key: session:550e8400-e29b-41d4-a716-446655440000
Value: {
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "device_id": "device_home_desktop",
    "username": "john@example.com",
    "websocket_server": "ws-server-3",
    "connected_at": "2024-01-01T14:30:00Z",
    "last_heartbeat": "2024-01-01T14:35:00Z",
    "subscribed_channels": ["user:123e4567:changes"]
}
```

**Device Presence (TTL: 30 seconds, renewed by heartbeat):**
```json
Key: device:presence:device_home_desktop
Value: {
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "device_name": "MacBook Pro (Home)",
    "online": true,
    "last_seen": "2024-01-01T14:35:45Z",
    "current_activity": "editing:report.docx"
}
```

**Per-Device Sync Cursor (what has been synced):**
```json
Key: sync:cursor:device_home_desktop
Value: {
    "last_sync_timestamp": "2024-01-01T14:30:00Z",
    "last_sync_version": 12345,
    "pending_uploads": ["file_id_1", "file_id_2"],
    "pending_downloads": ["file_id_3"],
    "conflicts": ["file_id_4"]
}
```

**User's Active Devices List:**
```json
Key: user:123e4567:active_devices
Value: {
    "device_home_desktop": {
        "online": true,
        "websocket_server": "ws-server-3",
        "last_seen": "2024-01-01T14:35:45Z"
    },
    "device_work_desktop": {
        "online": true,
        "websocket_server": "ws-server-1",
        "last_seen": "2024-01-01T14:35:50Z"
    },
    "device_mobile_iphone": {
        "online": false,
        "last_seen": "2024-01-01T12:00:00Z"
    }
}
```

#### Login Flow (Multiple Devices)

**Device 1 (First Login):**

```
Client                              API Server                         Redis
  |                                      |                               |
  | 1. POST /auth/login                 |                               |
  |    { email, password, device_info } |                               |
  |------------------------------------>|                               |
  |                                      | 2. Verify credentials         |
  |                                      | 3. Create session record      |
  |                                      |------------------------------>|
  |                                      |   SET session:uuid {...}      |
  |                                      |   SET device:presence:dev1    |
  |                                      |   SADD user:123:devices dev1  |
  |                                      |                               |
  |  4. Return tokens + device_id       |                               |
  |<------------------------------------|                               |
  |  { access_token, refresh_token,     |                               |
  |    device_id, websocket_url }       |                               |
  |                                      |                               |
  | 5. Connect to WebSocket             |                               |
  |------------------------------------>| WebSocket Server              |
  |  WS /sync/stream                    |                               |
  |  { session_token, device_id }       |                               |
  |                                      |                               |
  |                                      | 6. Subscribe to user channel  |
  |                                      |------------------------------>|
  |                                      |   SUBSCRIBE user:123:changes  |
  |                                      |                               |
  | 7. Acknowledgment                   |                               |
  |<------------------------------------|                               |
  |  { status: "connected",             |                               |
  |    device_id: "dev1" }              |                               |
```

**Device 2 (Concurrent Login):**

Same flow, but now:
- User has 2 active sessions in Redis
- Both devices subscribed to `user:123:changes` channel
- When file changes, broadcast to both

#### Real-Time Sync Flow

**Scenario: User edits file on Device 1**

```
Device 1                    API Server              Redis/Kafka         Device 2, 3, 4
   |                            |                       |                      |
   | 1. User modifies file     |                       |                      |
   |    report.docx locally    |                       |                      |
   |                            |                       |                      |
   | 2. POST /files/:id/update |                       |                      |
   |    { version: 5,          |                       |                      |
   |      checksum: abc123,    |                       |                      |
   |      device_id: dev1 }    |                       |                      |
   |--------------------------->|                       |                      |
   |                            |                       |                      |
   |                            | 3. Optimistic lock    |                      |
   |                            |    check             |                      |
   |                            |---------------------->|                      |
   |                            |  GET file_state:id   |                      |
   |                            |  current_version: 5  |                      |
   |                            |  (matches, proceed)  |                      |
   |                            |                       |                      |
   |                            | 4. Update file_state |                      |
   |                            |---------------------->|                      |
   |                            |  SET file_state:id   |                      |
   |                            |  version: 6,         |                      |
   |                            |  modified_by: dev1,  |                      |
   |                            |  timestamp: now()    |                      |
   |                            |                       |                      |
   |                            | 5. Publish event     |                      |
   |                            |---------------------->|                      |
   |                            |  PUBLISH             |                      |
   |                            |  user:123:changes    |                      |
   |                            |  {                   |                      |
   |                            |   file_id,           |                      |
   |                            |   action: "updated", |                      |
   |                            |   version: 6,        |                      |
   |                            |   device_id: dev1    |                      |
   |                            |  }                   |                      |
   |                            |                       |                      |
   |  6. Success response       |                       |                      |
   |<---------------------------|                       |                      |
   |  { version: 6,            |                       |                      |
   |    status: "synced" }     |                       |                      |
   |                            |                       |                      |
   |                            |                       | 7. Broadcast to     |
   |                            |                       |    all devices      |
   |                            |                       |-------------------->|
   |                            |                       |  WS: file_changed   |
   |                            |                       |  { file_id,         |
   |                            |                       |    version: 6,      |
   |                            |                       |    checksum }       |
   |                            |                       |                      |
   |                            |                       |                 8. Devices
   |                            |                       |                    download
   |                            |                       |                    new version
```

#### Conflict Detection & Resolution

**Conflict Scenario:**

```
Timeline:
T0:   report.docx version 5, synced on all devices
T1:   Device 1 (offline) edits → local version 6
T2:   Device 2 (online) edits → uploads → server version 6
T3:   Device 1 comes online, tries to upload version 6
      → Conflict! (same version number, different checksums)
```

**Detection:**

```sql
-- Device 1 attempts to update
UPDATE file_state 
SET current_version = 6,
    current_checksum = 'dev1_checksum',
    last_modified_device = 'dev1'
WHERE file_id = 'report.docx'
  AND current_version = 5  -- Optimistic lock: expect version 5
  AND current_checksum = 'old_checksum';

-- Returns: 0 rows affected (conflict detected!)
-- Actual state: version = 6, checksum = 'dev2_checksum'
```

**Resolution Strategies:**

**1. Last Write Wins (Timestamp-based):**

```
Device 1 timestamp: 2024-01-01 14:30:00
Device 2 timestamp: 2024-01-01 14:30:05

Winner: Device 2 (later timestamp)
Action:
- Server version: Device 2's version (version 6)
- Device 1's version: Saved as "report (conflicted copy from Device 1 2024-01-01).docx"
```

**Implementation:**

```sql
-- Save Device 1's version as conflict copy
INSERT INTO files (file_id, name, parent_id, user_id, version_number, checksum)
VALUES (
    gen_random_uuid(),
    'report (conflicted copy from Device 1 2024-01-01).docx',
    parent_folder_id,
    user_id,
    6,
    'dev1_checksum'
);

-- Notify Device 1
PUBLISH user:123:device:dev1:notifications {
    "type": "conflict_resolved",
    "file": "report.docx",
    "resolution": "last_write_wins",
    "your_version_saved_as": "report (conflicted copy...)",
    "winner": "Device 2"
}
```

**2. Manual Resolution (Present both versions):**

```
Notify user via all devices:
{
    "type": "conflict_detected",
    "file": "report.docx",
    "versions": [
        {
            "device": "Device 1 (Home Desktop)",
            "modified": "2024-01-01T14:30:00Z",
            "size": "125KB"
        },
        {
            "device": "Device 2 (Work Desktop)",
            "modified": "2024-01-01T14:30:05Z",
            "size": "130KB"
        }
    ],
    "actions": ["keep_both", "choose_version_1", "choose_version_2"]
}
```

**3. Operational Transformation (For collaborative editing):**

```
Device 1 operation: INSERT("new text", position=100)
Device 2 operation: DELETE(5 chars, position=50)

Transform Device 1's operation:
- Original position: 100
- Device 2 deleted 5 chars before position 100
- Transformed position: 95
- Final operation: INSERT("new text", position=95)

Both operations applied in consistent order across all devices
```

#### Handling Offline Edits

**Device goes offline:**

```
1. Client detects network loss (WebSocket disconnect)
2. Switch to "offline mode"
3. Queue all file changes locally
4. Store in IndexedDB/SQLite:
   - Pending uploads
   - Local modifications
   - Timestamps
```

**Device comes back online:**

```
1. Client detects network restoration
2. Reconnect WebSocket
3. POST /sync/changes
   Request:
   {
       "device_id": "dev1",
       "last_sync_timestamp": "2024-01-01T10:00:00Z",
       "pending_uploads": [
           {
               "file_id": "file_001",
               "local_version": 6,
               "checksum": "abc123",
               "modified_at": "2024-01-01T14:30:00Z"
           }
       ]
   }

4. Server responds:
   Response:
   {
       "server_changes": [
           {
               "file_id": "file_002",
               "version": 8,
               "action": "updated",
               "checksum": "def456"
           }
       ],
       "conflicts": [
           {
               "file_id": "file_001",
               "reason": "version_mismatch",
               "server_version": 7,
               "server_checksum": "xyz789"
           }
       ]
   }

5. Client handles:
   - Downloads file_002 (server change)
   - Resolves conflict for file_001
```

#### Presence & Activity Indicators

**Show which devices are online:**

```
GET /api/v1/devices

Response:
{
    "devices": [
        {
            "device_id": "dev1",
            "name": "MacBook Pro (Home)",
            "type": "desktop",
            "online": true,
            "last_seen": "2024-01-01T14:35:45Z",
            "current_activity": "Editing report.docx"
        },
        {
            "device_id": "dev2",
            "name": "iPhone",
            "type": "mobile",
            "online": false,
            "last_seen": "2024-01-01T12:00:00Z"
        }
    ]
}
```

**Heartbeat mechanism:**

```
Every 30 seconds:
  Client → Server: { type: "heartbeat", device_id: "dev1" }
  Server → Redis: SET device:presence:dev1 {online: true} EX 60

If no heartbeat for 60 seconds:
  Redis key expires
  Device marked as offline
```

#### Scalability Considerations

**Challenge: 100M users, average 3 devices = 300M concurrent WebSocket connections**

**Solution:**

1. **Sharding by User ID:**
   ```
   user_id = 123456
   shard = 123456 % 100 = 56
   WebSocket server pool: ws-pool-56
   Redis pub/sub: user-events-shard-56
   ```

2. **WebSocket Server Clustering:**
   ```
   100 WebSocket server clusters
   Each handles 1M users (3M connections)
   Each server: 10K connections × 300 servers = 3M per cluster
   ```

3. **Redis Pub/Sub per Shard:**
   ```
   100 Redis instances
   Each handles pub/sub for 1M users
   Publish: PUBLISH user-events-shard-56:{user_id}:changes {event}
   Subscribe: Only servers in shard-56 subscribe to shard-56 channel
   ```

4. **Database Sharding:**
   ```
   Shard sessions, device_sync_state by user_id
   Each shard: 1M users
   Cross-shard queries: Only for admin operations
   ```

#### Session Security

**1. Token Rotation:**
```
Access token: 15 minutes expiry
Refresh token: 30 days expiry

Every 15 minutes:
  Client → Server: POST /auth/refresh { refresh_token }
  Server → Client: { new_access_token, new_refresh_token }
```

**2. Device Verification:**
```
- Store device fingerprint (OS, browser, IP range)
- Alert user if login from new device
- Require 2FA for new device
```

**3. Session Revocation:**
```
User action: "Log out all other devices"

Implementation:
1. Mark all sessions except current as invalid
2. Publish to Redis: PUBLISH user:123:revoke_sessions
3. All WebSocket servers receive message
4. Force disconnect all devices except current
5. Devices must re-authenticate
```

---

## Summary

This Dropbox design addresses all core requirements and extra credit features:

**✅ Functional Requirements:**
- Upload/download from any device
- File sharing with permissions
- Auto-sync across devices
- Nested folders
- Collaborative editing
- Desktop daemon

**✅ Non-Functional Requirements:**
- High availability (multi-region, replication)
- Security (encryption, access control)
- Reliability (backups, versioning, checksums)
- Low latency (CDN, chunking, caching)
- Scalability (100M+ users, 100TB per user, 50GB files)

**Key Design Highlights:**
1. **Chunked uploads** for large files and resumability
2. **Block-level deduplication** for storage efficiency
3. **Microservices** for scalability and maintainability
4. **Push-based sync** for real-time updates
5. **Strong consistency** for metadata, eventual for content
6. **PostgreSQL** for metadata, **S3** for storage
7. **Redis** for caching, **Kafka** for events
8. **CDN** for global distribution

**Estimated Scale:**
- 100M users
- 50PB effective storage (with deduplication)
- 100K requests/sec
- 99.99% availability
- ~$7M/month infrastructure cost

This design provides a robust, scalable, and performant file storage and synchronization system similar to Dropbox.

---
---

# PART 2: EVALUATION RUBRIC MAPPING

This section maps the evaluation criteria to specific sections in this document, showing comprehensive coverage of all "Strong Yes" criteria.

---

## Evaluation Criteria Coverage

### 1. Handling Large Files ✅ STRONG YES

**Criteria:**
- Identifies key issues (user interruptions, network issues, browser/server limits)
- Suggests comprehensive approach using chunking
- Explains steps: initiation, chunking, checksums, completion
- Discusses importance of checksums with algorithm choices and trade-offs

**Coverage in This Document:**

| Requirement | Section | Location |
|-------------|---------|----------|
| Key issues identified | File Upload/Download Flow | Above |
| Chunking strategy (4MB chunks) | Core Components - Block Service | Above |
| Upload flow (initiate, chunk, complete) | Upload Flow (Chunked Upload) | Above |
| Checksum verification (SHA-256) | Upload Flow + Security | Above |
| Algorithm comparison | Data Models - file_blocks table | Above |
| Resumable uploads | Optimization Techniques | Above |
| Parallel uploads | Upload Flow | Above |
| Browser/server limits addressed | Chunking rationale | Above |

**Key Talking Points:**
1. **Issues Identified:**
   - Network interruptions during upload
   - Browser memory limits (can't load 50GB file into memory)
   - Server timeout limits (can't handle single 50GB HTTP request)
   - Need for progress tracking and resume capability

2. **Chunking Solution:**
   - 4MB chunk size (optimal for network MTU and S3 multipart upload)
   - Chunks uploaded in parallel (5-10 concurrent uploads)
   - Each chunk independently verifiable

3. **Three-Phase Upload:**
   - Phase 1: Initiate - Check file-level deduplication, generate pre-signed URLs
   - Phase 2: Upload Chunks - Client uploads chunks in parallel with SHA-256 checksums
   - Phase 3: Complete - Server verifies all chunks, assembles metadata, triggers sync

4. **Checksum Algorithm Choice:**
   - **SHA-256:** Chosen for security and collision resistance
   - **Alternative - MD5:** Faster but cryptographically broken
   - **Alternative - SHA-1:** Faster but deprecated
   - **Why SHA-256:** Industry standard, hardware acceleration, good balance

---

### 2. Real-time Updates ✅ STRONG YES

**Criteria:**
- Explains each approach (Polling, WebSockets, SSE) with pros/cons
- Chooses WebSockets with strong justification
- Suggests broadcasting solution (Kafka, Redis Pub/Sub)
- Discusses scaling challenges and solutions

**Approach Comparison:**

| Approach | Pros | Cons | Fit for Dropbox |
|----------|------|------|-----------------|
| **Polling** | Simple, works everywhere, stateless | High latency (30-60s), wasteful, server load | ❌ Too slow |
| **WebSockets** | Bidirectional, real-time, low overhead | Stateful (complex scaling) | ✅ **CHOSEN** |
| **SSE** | Simple, auto-reconnect | One-way only | ⚠️ Not enough |

**Why WebSockets:**
1. Bidirectional communication (client push AND receive)
2. Real-time (<100ms latency)
3. Efficient (single persistent connection)
4. Scalable with proper architecture

**Broadcasting Solution - Kafka:**
- Persistent log for replay
- Ordered delivery
- Partitioning for scale
- Multiple consumers

**Scaling Challenges & Solutions:**
- 300M connections → Cluster servers, shard by user_id
- Broadcasting → Kafka partitions, parallel consumers
- Stateful connections → Graceful draining (24h)

---

### 3. Schema, Storage & API Design ✅ STRONG YES

**Entity Design - Scales with:**
- **users:** 100M users
- **files:** 1T files (100M users × 10K files)
- **file_blocks:** 250T blocks
- **permissions:** 10B records
- **sync_state:** 300M records

**Relational vs Non-Relational - WHY POSTGRESQL:**

| Aspect | PostgreSQL | NoSQL | Winner |
|--------|------------|-------|--------|
| **Consistency** | Strong ACID | Eventual | ✅ PostgreSQL |
| **Complex Queries** | JOINs supported | Limited | ✅ PostgreSQL |
| **Transactions** | Multi-table atomic | Limited | ✅ PostgreSQL |
| **Horizontal Scaling** | Harder | Native | ⚠️ NoSQL |

**Chosen PostgreSQL because:**
1. Permissions require complex queries
2. ACID critical (no race conditions)
3. Scales to 1T files with sharding
4. JSON support for flexibility

---

### 4. Pre-signed URLs ✅ STRONG YES

Covered extensively in Deep Dive 1 with:
- Full parameter breakdown table
- Step-by-step signature generation
- 4 tampering scenarios with explanations
- Upload and download flow diagrams
- Security considerations
- Configuration parameters

---

### 5. Security ✅ STRONG YES

**Covered:**
1. **Encryption in Transit:** TLS 1.3, WebSocket Secure
2. **Encryption at Rest:** AES-256, encrypted EBS volumes
3. **Access Control:** RBAC, ACLs, time-limited access
4. **Pre-signed URL Security:** Short expiration, one-time use
5. **Audit Logging:** All file access tracked

---

### 6. High Availability ✅ COVERED

**Covered:**
- Microservices architecture
- Message brokers (Kafka/SQS)
- Multi-region replication
- Multi-AZ deployment
- Load balancing
- 3x replication

---

### 7. Spiky Traffic Handling ✅ STRONG YES

Covered extensively in Deep Dive 2 with:
- Traffic pattern analysis
- Auto-scaling policies per component
- Rate limiting (per-user, per-tier, global)
- Queue-based load leveling
- Circuit breaker pattern
- Backpressure mechanisms
- Pre-scaling for known events
- Cost optimization

---

### 8. Multi-Client State Management ✅ STRONG YES

Covered extensively in Deep Dive 3 with:
- Session table schema with device tracking
- Device sync state table (per-device, per-file)
- Redis structures for fast lookups
- Multi-device login flow
- Real-time sync with conflict detection
- Three conflict resolution strategies
- Offline queue and sync-on-reconnect
- Presence/heartbeat mechanism
- Sharding for 300M connections

---

## Summary: Coverage Scorecard

| Evaluation Area | Level | Evidence |
|----------------|-------|----------|
| Handling Large Files | ✅ Strong Yes | Complete chunked upload flow, checksum strategy, algorithm comparison |
| Real-time Updates | ✅ Strong Yes | WebSocket vs polling comparison, Kafka broadcasting, scaling strategy |
| Schema, Storage & API | ✅ Strong Yes | 10+ tables with indices, PG vs NoSQL justification, complete API design |
| Pre-signed URLs | ✅ Strong Yes | Full parameter breakdown, signature generation, tampering prevention |
| Security | ✅ Strong Yes | TLS, AES-256, RBAC, audit logging, end-to-end encryption |
| High Availability | ✅ Covered | Microservices, message brokers, multi-region, redundancy |
| Spiky Traffic Handling | ✅ Strong Yes | Auto-scaling, rate limiting, queue leveling, circuit breakers |
| Multi-Client State | ✅ Strong Yes | Session management, device sync, conflict resolution, offline support |
| Communication | ✅ Strong Yes | Clear structure, diagrams, trade-offs, examples, quantitative analysis |

**Overall:** This design document provides **L6-level depth** across **multiple deep dive areas** with strong justifications and comprehensive coverage of all evaluation criteria.

---
---

# PART 3: INTERVIEW QUICK REFERENCE GUIDE

This section provides a condensed guide for navigating the interview. Use this to structure responses and ensure you hit all "Strong Yes" criteria.

---

## Interview Flow Structure

1. **Requirements Clarification** (5 minutes)
2. **High-Level Architecture** (10 minutes)
3. **Deep Dive Area 1** (10-15 minutes)
4. **Deep Dive Area 2** (10-15 minutes)
5. **Scale, Tradeoffs, Discussion** (5-10 minutes)

---

## 1. Requirements Clarification (Lead the conversation)

**Ask these questions first:**

**Functional:**
- "Should we support large files? What's the max file size?" → 50GB
- "How many concurrent users and devices?" → 100M users, ~3 devices each
- "Do we need real-time sync or eventual consistency?" → Real-time preferred
- "Should we support collaborative editing?" → Extra credit
- "Do we need versioning and file recovery?" → Yes, for reliability

**Non-Functional:**
- "What's our availability target?" → 99.99% (four nines)
- "What regions do we need to support?" → Global (multiple regions)
- "What's our read:write ratio?" → Estimate 3:1 (read-heavy)
- "What's acceptable latency for upload/download?" → <1s to start

**State your assumptions clearly:**
```
"I'm assuming:
- 100M total users, 20M daily active (20% DAU ratio)
- Average user storage: 1TB (max 100TB)
- Read-heavy workload: 3:1 read/write ratio
- Total storage needed: ~100PB raw, ~50PB with deduplication
- Peak traffic: 100K requests/sec, 500K during spikes"
```

---

## 2. High-Level Architecture (Start here)

**Draw this diagram first:**

```
[Clients] → [Load Balancer] → [API Servers] ⟷ [Metadata DB (PostgreSQL)]
                    ↓                              ↓
            [WebSocket Servers] ⟷ [Redis Cache] ⟷ [Message Queue (Kafka)]
                    ↓                              ↓
            [Block Service] → [Object Storage (S3)] + [CDN]
```

**2-Minute Explanation:**

> "At the highest level, clients communicate with API servers through a load balancer. API servers handle metadata operations backed by PostgreSQL for strong consistency.
>
> For real-time sync, we use WebSocket servers with persistent connections. When files change, events flow through Kafka to all connected devices.
>
> For file storage, we use a Block Service that chunks files into 4MB blocks stored in S3. A CDN sits in front for faster downloads.
>
> Redis provides caching for metadata and session state."

**Key components:**
- **PostgreSQL**: Metadata, permissions (ACID guarantees)
- **S3**: File blocks (11 nines durability)
- **Kafka**: Event streaming for sync
- **Redis**: Caching + session management
- **WebSocket**: Real-time bidirectional sync
- **CDN**: Global content delivery

---

## 3. Deep Dive Selection Strategy

**If interviewer asks "What do you want to dive into?"**

**Full-Stack/Backend Focus:**
- Primary: Large File Upload (chunking, pre-signed URLs, deduplication)
- Secondary: Multi-Client State (sync, conflicts, sessions)

**Frontend Focus:**
- Primary: Real-Time Updates (WebSocket vs polling, conflict resolution)
- Secondary: Large File Upload (chunking, progress, resume)

**Infrastructure/Scale Focus:**
- Primary: Spiky Traffic (auto-scaling, rate limiting, circuit breakers)
- Secondary: Database Sharding and Caching

---

## Deep Dive Cheat Sheets

### Deep Dive A: Large File Upload (MUST KNOW)

**Opening:**
> "For large files up to 50GB, we can't use a single HTTP request due to timeout limits, browser memory constraints, and network reliability. I'll describe our chunked upload approach."

**Three-Phase Explanation:**

**Phase 1: Initiate Upload**
```
Client → API: POST /upload/initiate
  { filename, size: 5GB, checksum: "sha256:...", parent_id }

API checks:
1. File-level deduplication (checksum exists? → instant!)
2. User quota (5GB + current < 100TB?)
3. Permissions (can write to parent folder?)

API responds:
  { upload_id, file_id, chunk_size: 4MB, total_chunks: 1280, presigned_urls[] }
```

**Phase 2: Upload Chunks**
```
Client splits file into 4MB chunks
For each chunk (5-10 parallel):
  1. Calculate SHA-256 checksum
  2. PUT directly to S3 using pre-signed URL
  3. Track completion locally
  4. On failure: Retry that chunk only
```

**Phase 3: Complete Upload**
```
Client → API: POST /upload/complete
  { upload_id, chunk_checksums[] }

API verifies:
1. All chunks present in S3
2. Checksums match
3. Updates metadata in PostgreSQL
4. Publishes to Kafka → notifies other devices
```

**Critical Talking Points:**

**1. Why 4MB chunks?**
- Network MTU optimization
- S3 multipart upload minimum (5MB, we use 4MB for flexibility)
- Balance: Smaller = overhead, Larger = harder to resume

**2. Deduplication:**
```
File-level: Check file checksum → already uploaded? Done!
Block-level: Check chunk hash → already stored? Reuse!

Example: Upload same 5GB video on 3 devices
- First upload: 5GB transferred, 5GB stored
- Second upload: 0GB transferred, 0GB stored
- Storage savings: 40-60% typical
```

**3. Checksums (SHA-256):**
- **Why:** Detect corruption, deduplication, integrity
- **Where:** File level + block level
- **Alternatives:**
  - MD5: Faster but cryptographically broken
  - SHA-1: Deprecated (Google collision 2017)
  - SHA-256: Industry standard, hardware acceleration

**4. Resumable Uploads:**
```
Client tracks in IndexedDB:
{ upload_id, completed_chunks: [0,1,2,5,6], total_chunks: 1280 }

On network failure:
- Client reopens, reads state
- Requests new pre-signed URLs for missing chunks
- Continues from chunk 3
```

---

### Deep Dive B: Pre-signed URLs

**Opening:**
> "Pre-signed URLs allow direct S3 upload/download without giving clients AWS credentials. The API server generates a time-limited, cryptographically signed URL."

**Components:**

```
https://dropbox-storage.s3.amazonaws.com/blocks/abc123.bin
  ?X-Amz-Algorithm=AWS4-HMAC-SHA256
  &X-Amz-Credential=AKIAIO.../20240101/us-east-1/s3/aws4_request
  &X-Amz-Date=20240101T120000Z
  &X-Amz-Expires=3600
  &X-Amz-SignedHeaders=host
  &X-Amz-Signature=abc123def456...
```

| Parameter | Purpose |
|-----------|---------|
| X-Amz-Algorithm | Hash algorithm (AWS4-HMAC-SHA256) |
| X-Amz-Credential | Access key + scope |
| X-Amz-Date | When URL generated |
| X-Amz-Expires | Validity (3600 = 1 hour) |
| X-Amz-SignedHeaders | Headers in signature |
| X-Amz-Signature | HMAC-SHA256 signature |

**What's in the signature:**
1. Resource path → Can't access different file
2. Query parameters → Can't extend expiration
3. HTTP method → Can't change operation
4. Headers → Can't modify
5. AWS secret key → Only server knows

**Tampering Prevention Examples:**

```
Scenario 1: Extend expiration
Original: ...&X-Amz-Expires=3600&X-Amz-Signature=abc...
Modified: ...&X-Amz-Expires=86400&X-Amz-Signature=abc...
❌ Fails: Signature computed with 3600, not 86400

Scenario 2: Access different file
Original: /blocks/file_001.bin?...
Modified: /blocks/file_002.bin?...
❌ Fails: Path file_001 was signed

Scenario 3: Change method
Original: GET /blocks/file.bin?...
Modified: DELETE /blocks/file.bin?...
❌ Fails: GET was signed, not DELETE
```

**Benefits:**
- ✅ No credential exposure
- ✅ Scalability (no API proxy)
- ✅ Performance (direct S3)
- ✅ Security (time-limited, tamper-proof)
- ✅ Cost (reduced bandwidth)

**Expiration times:**
- Upload: 15 minutes
- Download: 1 hour
- Admin operations: 5 minutes

---

### Deep Dive C: Real-Time Updates

**Opening:**
> "For real-time sync, we need to notify all user devices when files change. Let me compare three approaches."

**Comparison:**

| Approach | Pros | Cons | Latency |
|----------|------|------|---------|
| Polling | Simple, stateless | Wasteful, slow | 30-60s |
| SSE | Auto-reconnect | One-way only | <1s |
| WebSocket | Real-time, two-way | Stateful (complex) | <100ms |

**Decision:** WebSockets with polling fallback

**Why WebSockets:**
- Bidirectional (push AND receive)
- Real-time (<100ms latency)
- Efficient (single connection)
- Scalable with sharding

**Architecture:**
```
Device 1 modifies file
    ↓
API Server
    ↓
PostgreSQL (version++)
    ↓
Kafka Topic: user_123_file_changes
    ↓
Kafka Consumer (WebSocket service)
    ↓
Redis Pub/Sub (fanout to all WS servers)
    ↓
WebSocket Servers 1, 2, 3, ..., N
    ↓
Device 2, 3, 4 (receive in <100ms)
```

**Why Kafka:**
- Persistent log (offline devices get replay)
- Ordering (changes in correct order)
- Partitioning (scale to millions)
- Multiple consumers (WebSocket, notifications, analytics)

**Scaling WebSockets:**
```
Challenge: 100M users × 3 devices = 300M connections

Solution:
1. Shard by user_id: shard = user_id % 100
2. Each shard: 1M users, 100 WS servers (10K conns each)
3. Scale out: Add servers to pool
4. Scale in: Graceful draining (24h, then force close)
```

---

### Deep Dive D: Multi-Client State & Conflict Resolution

**Opening:**
> "Users have multiple devices logged in simultaneously. We need per-device sync state and conflict resolution."

**Database Schema:**
```sql
CREATE TABLE device_sync_state (
    device_id UUID,
    file_id UUID,
    state VARCHAR(20),  -- synced | pending_upload | conflict
    local_version INTEGER,
    remote_version INTEGER,
    local_checksum VARCHAR(64),
    remote_checksum VARCHAR(64),
    UNIQUE(device_id, file_id)
);

CREATE TABLE file_state (
    file_id UUID PRIMARY KEY,
    current_version INTEGER,
    current_checksum VARCHAR(64),
    last_modified_by UUID,  -- device_id
    last_modified_time TIMESTAMP
);
```

**Conflict Scenario:**
```
T0: report.docx version 5, synced everywhere
T1: Device 1 (offline) edits → local version 6
T2: Device 2 (online) edits, uploads → server version 6
T3: Device 1 comes online, tries to upload version 6
    → CONFLICT! (same version, different checksums)
```

**Conflict Detection:**
```sql
-- Device 1 attempts update
UPDATE file_state
SET current_version = 6, current_checksum = 'abc123'
WHERE file_id = 'report.docx'
  AND current_version = 5  -- Optimistic lock
  AND current_checksum = 'old_checksum';

-- Returns: 0 rows → CONFLICT!
```

**Resolution Strategies:**

**1. Last Write Wins (Default)**
```
Compare timestamps:
- Device 1: 14:30:00
- Device 2: 14:30:05

Winner: Device 2 (newer)
Save Device 1's as: "report (conflicted copy 2024-01-01).docx"
```

**2. Manual Resolution**
Present both versions to user, let them choose

**3. Operational Transformation**
```
Device 1: INSERT("text", position=100)
Device 2: DELETE(5 chars, position=50)

Transform Device 1's operation:
- Original position: 100
- After Device 2's delete: position 95
Result: Both applied consistently
```

---

### Deep Dive E: Spiky Traffic & Auto-Scaling

**Opening:**
> "Dropbox experiences traffic spikes - Monday mornings, product launches, viral content. We need to handle 100x spikes."

**Traffic Patterns:**
```
Baseline: 20K req/sec
Business hours: 100K req/sec (5x)
Product launch: 500K req/sec (25x)
Flash spike: 2M req/sec (100x)
```

**Auto-scaling Per Component:**

**API Servers (Stateless):**
```yaml
Metrics:
  - CPU > 70% for 2 min → Scale out 20%
  - Latency p99 > 500ms → Scale out 30%
  - Queue depth > 1000 → Scale out 50%

Instances:
  Baseline: 100 (always-on)
  On-demand: 100 → 1000
  Spot: 1000 → 5000
  Max: 5000
```

**WebSocket Servers (Stateful):**
```
Scale-out: Easy (launch new, route new connections)
Scale-in: Graceful
  1. Mark as "draining"
  2. Stop accepting new
  3. Wait for existing to close (24h max)
  4. Force close, terminate
```

**Database:**
```
Short-term: Vertical scaling (upgrade instance)
Read scaling: Read replicas (Master + N replicas)
Write scaling: Sharding (shard by user_id)
Connection pooling: PgBouncer (5000 app servers → 100 DB conns)
```

**Rate Limiting:**
```python
free_tier:
  api_requests: 100/minute
  upload_bandwidth: 10 MB/s

paid_tier:
  api_requests: 1000/minute
  upload_bandwidth: 100 MB/s

Implementation (Redis Token Bucket):
Key: rate_limit:user_123:api_requests
Value: { tokens: 100, last_refill: timestamp }

On request:
  If tokens > 0: Allow, decrement
  If tokens = 0: Reject 429
  Refill: 1.67 tokens/sec (100/min)
```

**Queue-Based Load Leveling:**
```
Problem: 100K uploads/sec overwhelms processing

Solution:
Client → API → Accept 202 → Kafka Queue → Worker Pool
                                ↓
                        Queue absorbs spike
                        Workers auto-scale
                        Process when ready
```

**Circuit Breaker:**
```
States: CLOSED → OPEN → HALF_OPEN → CLOSED

CLOSED: Normal operation
OPEN: Database overloaded → Return cached data, 503 for writes
HALF_OPEN: Testing recovery with limited requests

Prevents cascading failure
```

---

## Trade-offs & Design Decisions

### Trade-off 1: Eventual vs Strong Consistency

**Decision:** Strong for metadata, eventual for content

```
Strong consistency (PostgreSQL):
- Permissions: MUST be immediate
- Ownership: MUST be consistent
- Quotas: MUST be accurate

Eventual consistency (S3 + caching):
- File content: Can tolerate 100ms delay
- Thumbnails: Can be stale
```

### Trade-off 2: Polling vs WebSockets

```
WebSockets chosen because:
✅ Real-time (<100ms vs 30-60s)
✅ Efficient (no wasted polls)
✅ Bidirectional
Worth the complexity at scale
```

### Trade-off 3: Monolith vs Microservices

```
Microservices chosen because:
✅ Independent scaling
✅ Fault isolation
✅ Team autonomy
Worth operational overhead at Dropbox scale
```

### Trade-off 4: Self-hosted vs Cloud

```
S3 chosen because:
✅ 11 nines durability
✅ Infinite scale
✅ No hardware management
✅ Cost-effective
Worth ~$3.5M/month for 50PB
```

---

## Common Follow-up Questions

**Q: How do you handle file versioning?**
> "Keep last 100 versions. Use delta storage - only changed blocks. Old versions to S3 Glacier after 90 days."

**Q: How recover from corruption?**
> "Multiple layers: 1) Checksums detect immediately, 2) S3's 3x replication, 3) Cross-region replication, 4) User versions, 5) Daily DB backups."

**Q: How add full-text search?**
> "Elasticsearch cluster. Pipeline: Upload → Kafka → Worker extracts text → Index in ES. Search queries ES for file_ids, fetch metadata from PostgreSQL."

**Q: Prevent abuse (malware)?**
> "1) Virus scan all uploads (ClamAV/VirusTotal), 2) Content hashing vs known illegal content, 3) Rate limiting, 4) User reports."

**Q: If AWS S3 goes down?**
> "Multi-region: Replicate to 2-3 AWS regions. Automatic failover. Accept writes to queue during outage, process when recovered."

**Q: Handle mobile poor connectivity?**
> "1) Aggressive caching, 2) Offline mode + queue, 3) Adaptive quality for media, 4) Compression, 5) Selective sync."

---

## Closing Statement

> "In summary, we've designed a system that:
> - Handles 100M+ users with 100TB each using S3 and block deduplication
> - Supports real-time sync using WebSockets and Kafka
> - Ensures security with encryption, access control, and pre-signed URLs
> - Scales with auto-scaling, rate limiting, and graceful degradation
> - Maintains 99.99% availability through multi-region replication
>
> Key decisions: chunked uploads, WebSockets for sync, PostgreSQL for metadata consistency, aggressive caching. Trade-offs favor consistency for permissions, eventual for content.
>
> What aspects would you like to explore further?"

---

## Red Flags to Avoid

❌ **Don't say:**
- "Upload files directly to API server" (Doesn't scale!)
- "Use MongoDB for everything" (Why? Justify!)
- "Polling is fine for real-time" (Not real-time!)
- "Don't need sharding" (1T files? Need strategy!)

✅ **Do say:**
- "I'm choosing X over Y because [reason]"
- "The trade-off is [this] vs [that]"
- "At this scale, we need to consider..."
- "This could fail if [scenario], so we [solution]"

---
---

# PART 4: PREPARATION & USAGE GUIDE

## 🎯 How to Use This Document

### For Interview Preparation:

**Phase 1: Learning (Week 1-2)**
1. Read entire document thoroughly (3-4 hours)
2. Understand each component and decision
3. Draw diagrams yourself to internalize

**Phase 2: Practice (Week 3-4)**
1. Use Part 3 (Interview Guide) to practice explanations
2. Time yourself on each deep dive (10-15 min)
3. Practice drawing architecture in <5 min
4. Rehearse trade-offs discussions

**Phase 3: Review (Day before)**
1. Review Part 2 (Evaluation Mapping) - ensure coverage
2. Skim Part 3 (Interview Guide) for key points
3. Practice 2-minute architecture explanation

### During Interview:

**Opening (0-5 min):**
- Ask clarification questions
- State assumptions clearly
- Confirm scope

**Architecture (5-15 min):**
- Draw high-level diagram
- 2-minute component explanation
- Wait for interviewer guidance

**Deep Dive 1 (15-30 min):**
- Let interviewer choose OR propose topic
- Use cheat sheets from Part 3
- Draw detailed flow diagrams
- Mention trade-offs

**Deep Dive 2 (30-40 min):**
- If time permits (L6 expectation)
- Use another cheat sheet
- Continue with diagrams

**Wrap-up (40-45 min):**
- Discuss remaining trade-offs
- Answer follow-ups
- Use closing statement

---

## 📊 Coverage Matrix

| Evaluation Criteria | Coverage | Quick Reference |
|-------------------|----------|----------------|
| Handling Large Files | ✅ Complete | Part 3 - Deep Dive A |
| Real-time Updates | ✅ Complete | Part 3 - Deep Dive C |
| Schema & API Design | ✅ Complete | Part 1 - Data Models |
| Pre-signed URLs | ✅ Complete | Part 1 - Deep Dive 1 + Part 3 - Deep Dive B |
| Security | ✅ Complete | Part 1 - Security section |
| Spiky Traffic | ✅ Complete | Part 1 - Deep Dive 2 + Part 3 - Deep Dive E |
| Multi-Client State | ✅ Complete | Part 1 - Deep Dive 3 + Part 3 - Deep Dive D |
| High Availability | ✅ Complete | Part 1 - Architecture |

---

## 🎓 Level Expectations

### L5 (Senior Engineer)
**Expectations:**
- Very deep on 1 topic (15-20 min)
- Surface-level on others
- Understand basic trade-offs

**Strategy:**
1. Strong architecture (5 min)
2. ONE thorough deep dive (20 min)
3. Brief discussion of others (10 min)
4. Trade-offs (5 min)

### L6 (Staff Engineer)
**Expectations:**
- Deep on 2 topics (15 min each)
- Knowledgeable on all areas
- Proactively discuss trade-offs
- Consider costs and failures

**Strategy:**
1. Strong architecture (5 min)
2. FIRST deep dive (15 min)
3. SECOND deep dive (15 min)
4. Proactive trade-offs (5 min)
5. Handle follow-ups (5 min)

---

## 📝 Quick Facts to Memorize

### Scale:
- Users: 100M total, 20M DAU
- Storage: 50PB (with deduplication)
- Requests: 100K/sec peak, 500K spike
- Files: 1T files
- Connections: 300M WebSocket

### Technical:
- Chunk size: 4MB
- Max file: 50GB (12,800 chunks)
- Hash: SHA-256
- DB: PostgreSQL
- Storage: S3
- Cache: Redis
- Queue: Kafka
- CDN: CloudFront

### Performance:
- Availability: 99.99%
- Upload latency: <1s to start
- Sync latency: <100ms
- API latency: p99 <200ms

### Cost:
- Storage: $3.5M/month
- Bandwidth: $3M/month
- Compute: $100K/month
- Database: $50K/month
- **Total: ~$7M/month**

---

## ✅ Final Checklist

**24 Hours Before:**
- [ ] Read entire document (3 hours)
- [ ] Review deep dives (1 hour)
- [ ] Practice architecture diagram (15 min)
- [ ] Memorize key numbers (15 min)

**1 Hour Before:**
- [ ] Skim Part 3 (30 min)
- [ ] Review Part 2 (15 min)
- [ ] Practice 2-min explanation (10 min)
- [ ] Relax (5 min)

**During Interview:**
- [ ] Ask clarifying questions
- [ ] Draw architecture
- [ ] Complete 1-2 deep dives
- [ ] Discuss trade-offs
- [ ] Provide numbers
- [ ] Think out loud

---

## 🚀 Success Indicators

**You're doing well if:**
- ✅ Complete architecture in <5 min
- ✅ Go deep on 1-2 areas without prompting
- ✅ Proactively mention trade-offs
- ✅ Provide specific numbers and tech
- ✅ Draw clear diagrams
- ✅ Handle follow-ups confidently
- ✅ Interviewer is taking notes

**Warning signs:**
- ⚠️ Interviewer keeps prompting
- ⚠️ Stuck on one area >20 min
- ⚠️ Can't explain decisions
- ⚠️ Using vague terms
- ⚠️ Not drawing diagrams
- ⚠️ Interviewer looks bored

---

## Good Luck! 🎉

Remember: Interviewers want to see **how you think**, not just what you know. Explain your reasoning, discuss trade-offs, and explore different approaches.

**You've got this!** 💪

