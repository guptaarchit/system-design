# Design Dropbox or Google Drive

## Table of Contents
1. [Overview](#overview)
2. [Requirements](#requirements)
3. [System Architecture](#system-architecture)
4. [Database Design](#database-design)
5. [API Design](#api-design)
6. [File Upload/Download Flow](#file-uploaddownload-flow)
7. [Synchronization Strategy](#synchronization-strategy)
8. [Scalability Considerations](#scalability-considerations)
9. [Optimizations](#optimizations)
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

A cloud storage service similar to Dropbox or Google Drive that allows users to store, sync, and share files across multiple devices. The system must handle file uploads/downloads, maintain file metadata, support real-time synchronization, handle file versioning, and scale to millions of users.

**Key Features:**
- File upload and download
- Multi-device synchronization
- File sharing and permissions
- File versioning
- Real-time updates
- Folder structure
- Search functionality
- Offline access
- Collaboration features

---

## Requirements

### Functional Requirements

1. **File Management**
   - Upload/download files
   - Create/delete folders
   - Move/copy files
   - File versioning
   - File metadata management

2. **Synchronization**
   - Sync across devices
   - Real-time updates
   - Conflict resolution
   - Delta sync (only changed parts)

3. **Sharing**
   - Share files/folders
   - Permission levels (view, edit, manage)
   - Public links
   - Collaboration

4. **Search**
   - Search files by name
   - Full-text search
   - Filter by type, date, size

### Non-Functional Requirements

1. **Scalability**
   - Support 500M+ users
   - Handle 1B+ files
   - Support 100TB+ storage per user
   - Horizontal scaling

2. **Performance**
   - Upload: < 5 seconds for 100MB file
   - Download: < 2 seconds for 100MB file
   - Sync: < 1 second latency
   - Search: < 500ms

3. **Reliability**
   - 99.9% uptime
   - No data loss
   - File durability guarantees

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                             │
│  (Web App, Desktop Client, Mobile Apps)                        │
└────────────────┬────────────────────────────────────────────────┘
                 │ HTTPS
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Load Balancer / API Gateway                   │
└────────────┬────────────────────────────────────┬────────────────┘
             │                                    │
             ▼                                    ▼
┌────────────────────────────┐      ┌────────────────────────────┐
│   Metadata Service         │      │   File Service              │
│   - File Metadata          │      │   - Upload/Download         │
│   - Folder Structure       │      │   - Chunking                │
└────────────┬──────────────┘      └────────────┬───────────────┘
             │                                    │
             ▼                                    ▼
┌────────────────────────────┐      ┌────────────────────────────┐
│   Sync Service             │      │   Storage Service          │
│   - Real-time Updates      │      │   - Object Storage         │
│   - Conflict Resolution    │      │   - Chunk Storage          │
└────────────┬──────────────┘      └────────────┬───────────────┘
             │                                    │
             ▼                                    ▼
┌────────────────────────────────────────────────────────────────┐
│                      Data Layer                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Metadata   │  │   Object    │  │   Chunk     │         │
│  │     DB       │  │   Storage   │  │   Storage    │         │
│  │ (PostgreSQL) │  │  (S3/HDFS)  │  │  (S3/HDFS)  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────────────────────────────────────────────┘
```

---

## Database Design

### Files Table

```sql
CREATE TABLE files (
    file_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    parent_folder_id BIGINT,
    name VARCHAR(255) NOT NULL,
    file_type VARCHAR(50),
    size BIGINT NOT NULL,
    mime_type VARCHAR(100),
    version INTEGER DEFAULT 1,
    checksum VARCHAR(64),
    storage_path VARCHAR(500),
    is_folder BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (parent_folder_id) REFERENCES files(file_id),
    INDEX idx_user_parent (user_id, parent_folder_id),
    INDEX idx_user_name (user_id, name)
);
```

### File Versions Table

```sql
CREATE TABLE file_versions (
    version_id BIGSERIAL PRIMARY KEY,
    file_id BIGINT NOT NULL,
    version_number INTEGER NOT NULL,
    storage_path VARCHAR(500),
    size BIGINT,
    checksum VARCHAR(64),
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (file_id) REFERENCES files(file_id),
    UNIQUE KEY unique_file_version (file_id, version_number)
);
```

### File Shares Table

```sql
CREATE TABLE file_shares (
    share_id BIGSERIAL PRIMARY KEY,
    file_id BIGINT NOT NULL,
    shared_by BIGINT NOT NULL,
    shared_with_user_id BIGINT,
    shared_with_email VARCHAR(255),
    permission VARCHAR(20) NOT NULL, -- view, edit, manage
    share_token VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (file_id) REFERENCES files(file_id)
);
```

---

## API Design

### File APIs

```
POST   /api/v1/files/upload
GET    /api/v1/files/{file_id}/download
PUT    /api/v1/files/{file_id}
DELETE /api/v1/files/{file_id}
GET    /api/v1/files?folder_id={folder_id}
POST   /api/v1/files/{file_id}/share
```

### Sync APIs

```
GET    /api/v1/sync/changes?since={timestamp}
POST   /api/v1/sync/upload-chunk
GET    /api/v1/sync/download-chunk/{chunk_id}
```

---

## File Upload/Download Flow

### Upload Flow

1. **Client initiates upload**
2. **Server creates file metadata**
3. **File chunked into blocks (4MB each)**
4. **Upload chunks in parallel**
5. **Server stores chunks in object storage**
6. **Server creates file record with chunk references**
7. **Server calculates checksum**
8. **Notify other devices via WebSocket**

### Download Flow

1. **Client requests file**
2. **Server retrieves file metadata**
3. **Server retrieves chunk references**
4. **Download chunks in parallel**
5. **Client reassembles file**
6. **Client verifies checksum**

---

## Synchronization Strategy

### Delta Sync

- **Chunk-level sync**: Only sync changed chunks
- **Checksum comparison**: Compare chunk checksums
- **Efficient**: Minimize data transfer

### Conflict Resolution

- **Last Write Wins**: For simple conflicts
- **Merge Strategy**: For text files
- **Conflict Flag**: For complex conflicts

---

## Scalability Considerations

- **Horizontal Scaling**: Multiple service instances
- **Storage Sharding**: Shard by user_id or file_id
- **CDN**: For file downloads
- **Chunking**: Parallel uploads/downloads

---

## Optimizations

### Performance Optimizations

#### 1. Chunked Upload/Download Optimization

**Parallel Chunk Transfer:**

```python
class OptimizedChunkTransfer:
    def __init__(self, max_parallel: int = 10):
        self.max_parallel = max_parallel
        self.semaphore = asyncio.Semaphore(max_parallel)
    
    async def upload_file_parallel(self, file_path: str, file_id: str):
        # Chunk file
        chunks = await self.chunk_file(file_path, chunk_size=4 * 1024 * 1024)  # 4MB
        
        # Upload chunks in parallel
        tasks = [
            self.upload_chunk_with_semaphore(chunk, file_id)
            for chunk in chunks
        ]
        
        results = await asyncio.gather(*tasks)
        return results
    
    async def upload_chunk_with_semaphore(self, chunk: dict, file_id: str):
        async with self.semaphore:
            return await self.upload_chunk(chunk, file_id)
```

**Adaptive Chunk Size:**

```python
class AdaptiveChunkSize:
    def __init__(self):
        self.min_chunk_size = 1 * 1024 * 1024  # 1MB
        self.max_chunk_size = 16 * 1024 * 1024  # 16MB
        self.current_chunk_size = 4 * 1024 * 1024  # 4MB
    
    def adjust_chunk_size(self, upload_rate: float, error_rate: float):
        # Increase chunk size if upload rate is high and error rate is low
        if upload_rate > 50 * 1024 * 1024 and error_rate < 0.01:  # 50MB/s
            self.current_chunk_size = min(
                self.max_chunk_size,
                self.current_chunk_size * 1.5
            )
        # Decrease chunk size if error rate is high
        elif error_rate > 0.05:
            self.current_chunk_size = max(
                self.min_chunk_size,
                self.current_chunk_size * 0.7
            )
```

#### 2. Delta Sync Optimization

**Efficient Change Detection:**

```python
class DeltaSyncOptimizer:
    def __init__(self):
        self.chunk_index = ChunkIndex()  # Maps file_id -> chunk_checksums
    
    async def get_changes(self, file_id: str, local_chunks: list) -> list:
        # Get remote chunk checksums
        remote_chunks = await self.chunk_index.get_chunks(file_id)
        
        # Create checksum map for O(1) lookup
        remote_map = {chunk['checksum']: chunk for chunk in remote_chunks}
        local_map = {chunk['checksum']: chunk for chunk in local_chunks}
        
        # Find missing chunks (chunks in remote but not in local)
        missing_chunks = [
            remote_map[checksum] 
            for checksum in remote_map 
            if checksum not in local_map
        ]
        
        # Find changed chunks (different checksums at same position)
        changed_chunks = []
        for i, local_chunk in enumerate(local_chunks):
            if i < len(remote_chunks):
                remote_chunk = remote_chunks[i]
                if local_chunk['checksum'] != remote_chunk['checksum']:
                    changed_chunks.append(remote_chunk)
        
        return missing_chunks + changed_chunks
```

**Incremental Sync:**

```python
class IncrementalSync:
    async def sync_file(self, file_id: str, last_sync_time: int):
        # Get only changes since last sync
        changes = await self.db.get_file_changes(file_id, since=last_sync_time)
        
        # Group changes by type
        metadata_changes = [c for c in changes if c['type'] == 'metadata']
        content_changes = [c for c in changes if c['type'] == 'content']
        
        # Sync metadata first (lightweight)
        await self.sync_metadata(metadata_changes)
        
        # Sync content changes (only changed chunks)
        await self.sync_content_chunks(content_changes)
```

#### 3. Compression Optimization

**Smart Compression:**

```python
class SmartCompressor:
    def __init__(self):
        self.compressible_types = {
            'text/plain', 'text/html', 'application/json',
            'application/xml', 'text/css', 'application/javascript'
        }
    
    async def compress_if_beneficial(self, file_data: bytes, content_type: str) -> dict:
        # Check if file type is compressible
        if content_type not in self.compressible_types:
            return {'data': file_data, 'compressed': False}
        
        # Try compression
        compressed = zlib.compress(file_data, level=6)
        compression_ratio = len(compressed) / len(file_data)
        
        # Only compress if saves at least 20%
        if compression_ratio < 0.8:
            return {
                'data': compressed,
                'compressed': True,
                'original_size': len(file_data),
                'compressed_size': len(compressed)
            }
        
        return {'data': file_data, 'compressed': False}
```

#### 4. Metadata Caching Optimization

**Aggressive Metadata Caching:**

```python
class MetadataCacheOptimizer:
    def __init__(self):
        self.cache = RedisCache()
        self.local_cache = LocalCache(max_size=10000)
    
    async def get_file_metadata(self, file_id: str) -> dict:
        # Check local cache first (fastest)
        cached = self.local_cache.get(f"file:{file_id}")
        if cached:
            return cached
        
        # Check Redis cache
        cached = await self.cache.get(f"file:{file_id}")
        if cached:
            self.local_cache.set(f"file:{file_id}", cached, ttl=300)
            return cached
        
        # Query database
        metadata = await self.db.get_file_metadata(file_id)
        
        # Cache at multiple levels
        await self.cache.set(f"file:{file_id}", metadata, ttl=3600)
        self.local_cache.set(f"file:{file_id}", metadata, ttl=300)
        
        return metadata
    
    async def batch_get_metadata(self, file_ids: list) -> dict:
        # Batch fetch from cache
        cached_results = await self.cache.mget([f"file:{id}" for id in file_ids])
        
        # Fetch missing from database
        missing_ids = [
            file_ids[i] for i, cached in enumerate(cached_results) if cached is None
        ]
        
        if missing_ids:
            db_results = await self.db.batch_get_metadata(missing_ids)
            # Cache results
            for file_id, metadata in db_results.items():
                await self.cache.set(f"file:{file_id}", metadata, ttl=3600)
            cached_results.update(db_results)
        
        return cached_results
```

#### 5. Storage Optimization

**Deduplication:**

```python
class DeduplicationOptimizer:
    def __init__(self):
        self.chunk_store = ChunkStore()
        self.deduplication_index = {}  # checksum -> chunk_id
    
    async def store_file_with_dedup(self, file_chunks: list) -> list:
        chunk_refs = []
        
        for chunk in file_chunks:
            checksum = chunk['checksum']
            
            # Check if chunk already exists
            if checksum in self.deduplication_index:
                # Reuse existing chunk
                chunk_id = self.deduplication_index[checksum]
            else:
                # Store new chunk
                chunk_id = await self.chunk_store.store(chunk['data'])
                self.deduplication_index[checksum] = chunk_id
            
            chunk_refs.append({
                'chunk_id': chunk_id,
                'offset': chunk['offset'],
                'size': chunk['size']
            })
        
        return chunk_refs
```

**Storage Tiering:**

```python
class StorageTierOptimizer:
    async def optimize_storage_tiers(self, file_id: str, access_pattern: dict):
        # Move files to appropriate storage tier based on access pattern
        last_access = access_pattern.get('last_access', 0)
        access_count = access_pattern.get('access_count', 0)
        age_days = (time.time() - last_access) / 86400
        
        if age_days > 90 and access_count < 10:
            # Move to cold storage
            await self.move_to_cold_storage(file_id)
        elif age_days > 30 and access_count < 50:
            # Move to nearline storage
            await self.move_to_nearline_storage(file_id)
        else:
            # Keep in hot storage
            await self.keep_in_hot_storage(file_id)
```

### Network Optimizations

#### 1. Connection Pooling

**Persistent Connections:**

```python
class ConnectionPoolOptimizer:
    def __init__(self, max_connections: int = 100):
        self.pool = httpx.AsyncClient(
            limits=httpx.Limits(
                max_keepalive_connections=max_connections,
                max_connections=max_connections
            ),
            timeout=httpx.Timeout(30.0)
        )
    
    async def upload_chunk(self, chunk_data: bytes, url: str):
        # Reuse connection from pool
        response = await self.pool.put(url, content=chunk_data)
        return response
```

#### 2. HTTP/2 Multiplexing

**Parallel Requests:**

```python
class HTTP2Optimizer:
    def __init__(self):
        self.client = httpx.AsyncClient(http2=True)
    
    async def download_chunks_parallel(self, chunk_urls: list) -> list:
        # Download multiple chunks in parallel using HTTP/2
        tasks = [
            self.client.get(url) for url in chunk_urls
        ]
        
        responses = await asyncio.gather(*tasks)
        return [r.content for r in responses]
```

### Memory Optimizations

#### 1. Streaming for Large Files

**Stream Processing:**

```python
class StreamingOptimizer:
    async def upload_large_file_streaming(self, file_path: str, file_id: str):
        # Stream file instead of loading into memory
        async with aiofiles.open(file_path, 'rb') as f:
            chunk_id = 0
            while True:
                chunk_data = await f.read(4 * 1024 * 1024)  # 4MB chunks
                if not chunk_data:
                    break
                
                # Upload chunk immediately (don't wait for all chunks)
                await self.upload_chunk({
                    'chunk_id': chunk_id,
                    'data': chunk_data,
                    'file_id': file_id
                })
                
                chunk_id += 1
```

#### 2. Memory-Mapped Files

**Zero-Copy Reads:**

```python
class MemoryMappedOptimizer:
    def read_file_mmap(self, file_path: str, offset: int, size: int) -> bytes:
        # Use memory mapping for large files
        with open(file_path, 'rb') as f:
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                return mm[offset:offset + size]
```

### Cost Optimizations

#### 1. Storage Cost Reduction

**Lifecycle Policies:**

```python
class StorageLifecycleOptimizer:
    async def apply_lifecycle_policy(self, file_id: str):
        file_metadata = await self.get_file_metadata(file_id)
        age_days = (time.time() - file_metadata['created_at']) / 86400
        
        # Move to cheaper storage based on age and access
        if age_days > 365:
            await self.move_to_archive_storage(file_id)
        elif age_days > 90:
            await self.move_to_coldline_storage(file_id)
```

#### 2. Bandwidth Optimization

**CDN Usage:**

```python
class CDNOptimizer:
    async def get_file_via_cdn(self, file_id: str) -> str:
        # Check if file is in CDN cache
        cdn_url = await self.cdn.get_url(file_id)
        if cdn_url:
            return cdn_url
        
        # Upload to CDN for frequently accessed files
        access_count = await self.get_access_count(file_id)
        if access_count > 100:
            await self.cdn.cache_file(file_id)
            return await self.cdn.get_url(file_id)
        
        # Return direct storage URL
        return await self.get_storage_url(file_id)
```

---

## Caching Strategy

- **Metadata Cache**: Cache file metadata (Redis)
- **CDN Cache**: Cache frequently accessed files
- **Chunk Cache**: Cache recently accessed chunks

---

## Security

- **Encryption**: TLS in transit, encryption at rest
- **Access Control**: File-level permissions
- **Authentication**: OAuth 2.0

---

## Capacity Planning

- **Users**: 500M users
- **Files per User**: 10,000 average
- **Total Files**: 5T files
- **Storage**: 100TB per user average = 50EB total

---

## Technology Stack

- **Backend**: Go, Java
- **Storage**: S3, HDFS
- **Database**: PostgreSQL, Cassandra
- **Cache**: Redis
- **CDN**: CloudFlare

---

## Interview Discussion Points

1. **File Chunking**: Why chunk files? How do you handle chunks?
2. **Sync Strategy**: How do you sync across devices?
3. **Conflict Resolution**: How do you handle conflicts?
4. **Scalability**: How do you scale to millions of users?

---

**Document Version**: 1.0  
**Last Updated**: January 2024

