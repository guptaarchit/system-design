# Create a Distributed File Transfer System like BitTorrent

## Table of Contents
1. [Overview](#overview)
2. [Requirements](#requirements)
3. [System Architecture](#system-architecture)
4. [Peer Discovery](#peer-discovery)
5. [Piece Management](#piece-management)
6. [Database Design](#database-design)
7. [API Design](#api-design)
8. [Download Strategy](#download-strategy)
9. [Upload Strategy](#upload-strategy)
10. [Scalability Considerations](#scalability-considerations)
11. [Optimizations](#optimizations)
12. [Security](#security)
13. [Capacity Planning](#capacity-planning)
14. [Technology Stack](#technology-stack)
15. [Interview Discussion Points](#interview-discussion-points)

---

## Overview

A distributed file transfer system similar to BitTorrent that enables efficient file sharing by breaking files into pieces and allowing peers to download from multiple sources simultaneously. The system must handle peer discovery, piece distribution, download coordination, and incentivize sharing.

**Key Features:**
- File chunking into pieces
- Peer discovery and connection
- Piece-based download from multiple peers
- Piece verification (checksums)
- Download prioritization (rarest first)
- Upload management (tit-for-tat)
- Tracker coordination
- DHT (Distributed Hash Table) support

---

## Requirements

### Functional Requirements

1. **File Management**
   - Create torrents from files
   - Break files into pieces
   - Generate piece hashes
   - Create torrent metadata

2. **Peer Discovery**
   - Register with tracker
   - Discover peers
   - Connect to peers
   - Maintain peer list

3. **Piece Transfer**
   - Request pieces from peers
   - Upload pieces to peers
   - Verify piece integrity
   - Manage piece availability

4. **Download Management**
   - Coordinate piece downloads
   - Prioritize rare pieces
   - Handle peer failures
   - Resume downloads

### Non-Functional Requirements

1. **Scalability**
   - Support millions of peers
   - Handle thousands of files
   - Efficient bandwidth utilization

2. **Performance**
   - Fast download speeds
   - Low overhead
   - Efficient piece distribution

3. **Reliability**
   - Handle peer failures
   - Resume interrupted downloads
   - Data integrity guarantees

---

## System Architecture

### High-Level Design (HLD)

```
┌─────────────────────────────────────────────────────────────────┐
│                    Peers (Clients)                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Peer 1     │  │   Peer 2     │  │   Peer N    │         │
│  │  - Download  │  │  - Download  │  │  - Download │         │
│  │  - Upload    │  │  - Upload    │  │  - Upload   │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────┬───────────────┬───────────────┬───────────────────┘
             │               │               │
             ▼               ▼               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Tracker Service                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Peer       │  │   Torrent    │  │   Statistics │         │
│  │   Registry   │  │   Manager    │  │   Service    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DHT (Distributed Hash Table)                   │
│  - Peer discovery without tracker                                │
│  - Distributed peer information                                  │
└────────────────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Data Layer                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Torrents   │  │   Peers      │  │   Pieces     │         │
│  │     DB       │  │     DB       │  │   Metadata   │         │
│  │ (PostgreSQL) │  │ (PostgreSQL) │  │ (Redis)      │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────────────────────────────────────────────┘
```

### HLD Component Breakdown

**1. Peer Layer**
- **Peer Client**: Handles file downloads/uploads, piece management, peer connections
- **Piece Manager**: Manages piece availability, download priority, verification
- **Connection Manager**: Manages peer connections, handshakes, message routing

**2. Tracker Layer**
- **Peer Registry**: Maintains active peer list per torrent
- **Torrent Manager**: Manages torrent metadata, statistics
- **Statistics Service**: Tracks download/upload statistics, peer counts

**3. DHT Layer**
- **DHT Node**: Participates in distributed hash table for peer discovery
- **Routing Table**: Maintains Kademlia routing table
- **Peer Store**: Stores peer information in DHT

**4. Data Layer**
- **Torrents DB**: Stores torrent metadata, piece hashes
- **Peers DB**: Stores peer information, connection history
- **Pieces Metadata**: Caches piece availability, download state

---

## Peer Discovery

### Tracker Protocol

```python
class TrackerClient:
    def __init__(self, tracker_url: str):
        self.tracker_url = tracker_url
        self.peer_id = self.generate_peer_id()
    
    def announce(self, info_hash: str, port: int, uploaded: int, downloaded: int, left: int):
        params = {
            'info_hash': info_hash,
            'peer_id': self.peer_id,
            'port': port,
            'uploaded': uploaded,
            'downloaded': downloaded,
            'left': left,
            'event': 'started'
        }
        
        response = requests.get(self.tracker_url, params=params)
        peers = self.parse_peers(response.content)
        return peers
    
    def parse_peers(self, data: bytes) -> list:
        # Parse peer list from tracker response
        peers = []
        # Implementation depends on format (binary or bencoded)
        return peers
```

### DHT (Distributed Hash Table)

```python
class DHTNode:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.routing_table = {}
        self.data_store = {}
    
    def find_peers(self, info_hash: str) -> list:
        # Find nodes closest to info_hash
        closest_nodes = self.find_closest_nodes(info_hash, k=8)
        
        # Query nodes for peers
        peers = []
        for node in closest_nodes:
            node_peers = self.query_node(node, 'get_peers', info_hash)
            peers.extend(node_peers)
        
        return peers
    
    def store_peer(self, info_hash: str, peer_info: dict):
        # Store peer information in DHT
        key = self.hash(info_hash)
        self.data_store[key] = peer_info
```

---

## Piece Management

### Torrent Metadata

```python
class TorrentMetadata:
    def __init__(self, file_path: str, piece_size: int = 256 * 1024):  # 256KB
        self.file_path = file_path
        self.piece_size = piece_size
        self.file_size = os.path.getsize(file_path)
        self.piece_count = (self.file_size + piece_size - 1) // piece_size
        self.pieces = []
        self.generate_pieces()
    
    def generate_pieces(self):
        with open(self.file_path, 'rb') as f:
            for i in range(self.piece_count):
                piece_data = f.read(self.piece_size)
                piece_hash = hashlib.sha1(piece_data).digest()
                self.pieces.append({
                    'index': i,
                    'hash': piece_hash,
                    'size': len(piece_data)
                })
    
    def create_torrent_file(self) -> dict:
        return {
            'info': {
                'name': os.path.basename(self.file_path),
                'length': self.file_size,
                'piece length': self.piece_size,
                'pieces': b''.join(p['hash'] for p in self.pieces)
            },
            'announce': 'http://tracker.example.com/announce'
        }
```

### Piece Download Manager

```python
class PieceManager:
    def __init__(self, torrent_metadata: dict):
        self.metadata = torrent_metadata
        self.pieces = {}  # piece_index -> Piece
        self.downloaded_pieces = set()
        self.available_pieces = {}  # piece_index -> set of peer_ids
    
    def request_piece(self, peer_id: str) -> int:
        # Rarest first strategy
        rarest_piece = self.get_rarest_piece()
        if rarest_piece is not None:
            return rarest_piece
        return None
    
    def get_rarest_piece(self) -> int:
        # Find piece with fewest available peers
        if not self.available_pieces:
            return None
        
        rarest_piece = min(
            self.available_pieces.items(),
            key=lambda x: len(x[1])
        )[0]
        
        return rarest_piece
    
    def verify_piece(self, piece_index: int, piece_data: bytes) -> bool:
        expected_hash = self.metadata['pieces'][piece_index]
        actual_hash = hashlib.sha1(piece_data).digest()
        return expected_hash == actual_hash
    
    def save_piece(self, piece_index: int, piece_data: bytes):
        if self.verify_piece(piece_index, piece_data):
            self.pieces[piece_index] = piece_data
            self.downloaded_pieces.add(piece_index)
            return True
        return False
```

---

## Database Design

### Torrents Table

```sql
CREATE TABLE torrents (
    info_hash VARCHAR(40) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    total_size BIGINT NOT NULL,
    piece_size INTEGER NOT NULL,
    piece_count INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_name (name)
);
```

### Peers Table

```sql
CREATE TABLE peers (
    peer_id VARCHAR(255) PRIMARY KEY,
    info_hash VARCHAR(40) NOT NULL,
    ip_address VARCHAR(45) NOT NULL,
    port INTEGER NOT NULL,
    uploaded BIGINT DEFAULT 0,
    downloaded BIGINT DEFAULT 0,
    left BIGINT NOT NULL,
    last_seen TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (info_hash) REFERENCES torrents(info_hash),
    INDEX idx_info_hash (info_hash),
    INDEX idx_last_seen (last_seen)
);
```

---

## API Design

### Tracker APIs

```
GET /announce?info_hash={hash}&peer_id={id}&port={port}&uploaded={up}&downloaded={down}&left={left}
Response: List of peers

GET /scrape?info_hash={hash}
Response: Torrent statistics
```

### Peer APIs

```
POST /peer/handshake
{
  "info_hash": "...",
  "peer_id": "..."
}

POST /peer/message
{
  "type": "request", // request, piece, have, bitfield
  "piece_index": 0,
  "block_offset": 0,
  "block_length": 16384
}
```

---

## Download Strategy

### Rarest First

```python
def rarest_first_strategy(piece_manager):
    # Download pieces that are rarest first
    # This ensures pieces don't become unavailable
    rarest = piece_manager.get_rarest_piece()
    return rarest
```

### Endgame Mode

```python
def endgame_mode(piece_manager):
    # When most pieces downloaded, request from all peers
    # to finish quickly
    if piece_manager.completion_percentage() > 0.9:
        return piece_manager.get_missing_pieces()
    return None
```

---

## Upload Strategy

### Tit-for-Tat

```python
class UploadManager:
    def __init__(self):
        self.peer_upload_rates = {}  # peer_id -> upload_rate
    
    def should_upload_to(self, peer_id: str) -> bool:
        # Upload to peers that upload to us
        if peer_id in self.peer_upload_rates:
            return self.peer_upload_rates[peer_id] > 0
        return False
    
    def update_upload_rate(self, peer_id: str, rate: float):
        self.peer_upload_rates[peer_id] = rate
```

---

## Low-Level Design (LLD)

### Peer Client Architecture

```python
class PeerClient:
    def __init__(self, peer_id: str, config: dict):
        self.peer_id = peer_id
        self.tracker_client = TrackerClient(config.tracker_url)
        self.dht_node = DHTNode(peer_id)
        self.piece_manager = PieceManager()
        self.connection_manager = ConnectionManager(max_connections=50)
        self.download_manager = DownloadManager()
        self.upload_manager = UploadManager()
        self.metadata_store = MetadataStore()
    
    def start_download(self, torrent_file: dict):
        # 1. Parse torrent metadata
        metadata = self.parse_torrent(torrent_file)
        self.metadata_store.save(metadata)
        
        # 2. Initialize piece manager
        self.piece_manager.initialize(metadata)
        
        # 3. Discover peers
        peers = self.discover_peers(metadata.info_hash)
        
        # 4. Connect to peers
        for peer in peers:
            self.connection_manager.connect(peer)
        
        # 5. Start download
        self.download_manager.start()
    
    def discover_peers(self, info_hash: str) -> list:
        peers = []
        
        # Try tracker first
        try:
            tracker_peers = self.tracker_client.announce(info_hash)
            peers.extend(tracker_peers)
        except TrackerError:
            pass
        
        # Fallback to DHT
        dht_peers = self.dht_node.find_peers(info_hash)
        peers.extend(dht_peers)
        
        return peers
```

### Connection Manager LLD

```python
class ConnectionManager:
    def __init__(self, max_connections: int = 50):
        self.max_connections = max_connections
        self.active_connections = {}  # peer_id -> Connection
        self.connection_pool = Queue(maxsize=max_connections)
        self.message_handler = MessageHandler()
    
    def connect(self, peer_info: dict):
        if len(self.active_connections) >= self.max_connections:
            # Use tit-for-tat to decide which connection to drop
            self._drop_worst_peer()
        
        connection = PeerConnection(peer_info)
        connection.handshake()
        
        if connection.is_connected():
            self.active_connections[peer_info['peer_id']] = connection
            self._start_message_loop(connection)
    
    def _start_message_loop(self, connection: PeerConnection):
        while connection.is_connected():
            message = connection.receive()
            self.message_handler.handle(message, connection)
    
    def _drop_worst_peer(self):
        # Drop peer with lowest upload rate
        worst_peer = min(
            self.active_connections.items(),
            key=lambda x: x[1].upload_rate
        )
        worst_peer[1].close()
        del self.active_connections[worst_peer[0]]
```

### Piece Manager LLD

```python
class PieceManager:
    def __init__(self, torrent_metadata: dict):
        self.metadata = torrent_metadata
        self.pieces = {}  # piece_index -> Piece
        self.downloaded_pieces = set()
        self.available_pieces = {}  # piece_index -> set(peer_ids)
        self.piece_priority = {}  # piece_index -> priority
        self.piece_requests = {}  # piece_index -> set(peer_ids requesting)
    
    def update_piece_availability(self, peer_id: str, bitfield: bytes):
        # Update which pieces peer has
        for i, bit in enumerate(bitfield):
            if bit:
                piece_index = i
                if piece_index not in self.available_pieces:
                    self.available_pieces[piece_index] = set()
                self.available_pieces[piece_index].add(peer_id)
    
    def request_piece(self, peer_id: str) -> Optional[int]:
        # Rarest first strategy
        rarest_piece = self._get_rarest_piece()
        
        if rarest_piece is None:
            return None
        
        # Check if peer has this piece
        if peer_id not in self.available_pieces.get(rarest_piece, set()):
            return None
        
        # Mark as requested
        if rarest_piece not in self.piece_requests:
            self.piece_requests[rarest_piece] = set()
        self.piece_requests[rarest_piece].add(peer_id)
        
        return rarest_piece
    
    def _get_rarest_piece(self) -> Optional[int]:
        if not self.available_pieces:
            return None
        
        # Filter out already downloaded pieces
        available = {
            idx: peers 
            for idx, peers in self.available_pieces.items()
            if idx not in self.downloaded_pieces
        }
        
        if not available:
            return None
        
        # Find rarest piece
        rarest_piece = min(
            available.items(),
            key=lambda x: len(x[1])
        )[0]
        
        return rarest_piece
    
    def save_piece(self, piece_index: int, piece_data: bytes) -> bool:
        # Verify piece hash
        if not self._verify_piece(piece_index, piece_data):
            return False
        
        # Save piece
        self.pieces[piece_index] = piece_data
        self.downloaded_pieces.add(piece_index)
        
        # Remove from requests
        if piece_index in self.piece_requests:
            del self.piece_requests[piece_index]
        
        return True
    
    def _verify_piece(self, piece_index: int, piece_data: bytes) -> bool:
        expected_hash = self.metadata['pieces'][piece_index]
        actual_hash = hashlib.sha1(piece_data).digest()
        return expected_hash == actual_hash
```

### Tracker Service LLD

```python
class TrackerService:
    def __init__(self):
        self.peer_registry = PeerRegistry()
        self.torrent_manager = TorrentManager()
        self.statistics_service = StatisticsService()
        self.cache = RedisCache()
    
    def announce(self, info_hash: str, peer_info: dict):
        # Validate request
        if not self._validate_announce(peer_info):
            raise InvalidAnnounceError()
        
        # Update peer registry
        self.peer_registry.register(info_hash, peer_info)
        
        # Update statistics
        self.statistics_service.update(info_hash, peer_info)
        
        # Get peer list (cached)
        peers = self._get_peer_list(info_hash, peer_info['peer_id'])
        
        return peers
    
    def _get_peer_list(self, info_hash: str, requesting_peer_id: str, limit: int = 50):
        # Try cache first
        cache_key = f"peers:{info_hash}"
        cached_peers = self.cache.get(cache_key)
        if cached_peers:
            return cached_peers
        
        # Get from database
        all_peers = self.peer_registry.get_peers(info_hash)
        
        # Exclude requesting peer
        peers = [p for p in all_peers if p['peer_id'] != requesting_peer_id]
        
        # Randomize and limit
        random.shuffle(peers)
        peers = peers[:limit]
        
        # Cache for 30 seconds
        self.cache.set(cache_key, peers, ttl=30)
        
        return peers
```

## Scalability Considerations

### Horizontal Scaling

**1. Distributed Trackers**
- **Strategy**: Multiple tracker instances behind load balancer
- **Implementation**: 
  - Shared database (PostgreSQL cluster)
  - Redis for peer list caching
  - Consistent hashing for peer distribution
- **Scaling**: Add tracker instances as needed

**2. DHT Scaling**
- **Strategy**: Decentralized peer discovery
- **Implementation**:
  - Kademlia DHT protocol
  - Each peer participates in DHT
  - No central bottleneck
- **Scaling**: Naturally scales with peer count

**3. Peer Connection Management**
- **Strategy**: Limit concurrent connections per peer
- **Implementation**:
  - Max 50-100 connections per peer
  - Connection prioritization (tit-for-tat)
  - Connection pooling
- **Scaling**: Each peer manages own connections

**4. Bandwidth Management**
- **Strategy**: Throttle upload/download per peer
- **Implementation**:
  - Token bucket algorithm
  - Configurable rate limits
  - Priority-based bandwidth allocation
- **Scaling**: Distributed across peers

### Database Scaling

**1. Torrents Database**
- **Sharding**: Shard by info_hash
- **Replication**: Read replicas for queries
- **Caching**: Redis cache for hot torrents

**2. Peers Database**
- **Partitioning**: Partition by info_hash
- **TTL**: Auto-delete stale peer records
- **Caching**: Redis for active peer lists

### Performance Optimization

**1. Piece Distribution**
- **Rarest First**: Ensures piece availability
- **Endgame Mode**: Request from all peers when near completion
- **Choking Algorithm**: Prioritize good uploaders

**2. Network Optimization**
- **Connection Reuse**: Reuse TCP connections
- **Message Batching**: Batch multiple piece requests
- **Compression**: Compress metadata messages

---

## Fault Tolerance

### Tracker Fault Tolerance

**1. Tracker Failover**
```python
class TrackerClient:
    def __init__(self, tracker_urls: list):
        self.tracker_urls = tracker_urls  # Multiple tracker URLs
        self.current_tracker = 0
        self.failed_trackers = set()
    
    def announce(self, info_hash: str, peer_info: dict):
        max_retries = len(self.tracker_urls)
        
        for attempt in range(max_retries):
            try:
                tracker_url = self.tracker_urls[self.current_tracker]
                return self._announce_to_tracker(tracker_url, info_hash, peer_info)
            except TrackerError as e:
                self.failed_trackers.add(self.current_tracker)
                self.current_tracker = (self.current_tracker + 1) % len(self.tracker_urls)
                if attempt == max_retries - 1:
                    raise AllTrackersFailedError()
        
        # Fallback to DHT
        return self.dht_node.find_peers(info_hash)
```

**2. Tracker Redundancy**
- **Multiple Trackers**: Each torrent can have multiple tracker URLs
- **Failover**: Automatically switch to next tracker
- **DHT Fallback**: Use DHT when all trackers fail
- **Health Checks**: Monitor tracker health

**3. Database Redundancy**
- **Primary-Replica**: PostgreSQL primary with read replicas
- **Automatic Failover**: Promote replica on primary failure
- **Data Replication**: Synchronous replication for consistency

### Peer Fault Tolerance

**1. Peer Connection Resilience**
```python
class PeerConnection:
    def __init__(self, peer_info: dict):
        self.peer_info = peer_info
        self.socket = None
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 3
        self.last_heartbeat = time.time()
    
    def connect(self):
        try:
            self.socket = socket.create_connection(
                (self.peer_info['ip'], self.peer_info['port']),
                timeout=10
            )
            self.reconnect_attempts = 0
            return True
        except (socket.error, socket.timeout) as e:
            self.reconnect_attempts += 1
            if self.reconnect_attempts < self.max_reconnect_attempts:
                time.sleep(2 ** self.reconnect_attempts)  # Exponential backoff
                return self.connect()
            return False
    
    def send_keepalive(self):
        if time.time() - self.last_heartbeat > 120:  # 2 minutes
            try:
                self.socket.send(b'\x00\x00\x00\x00')  # Keepalive message
                self.last_heartbeat = time.time()
            except socket.error:
                self.handle_disconnection()
```

**2. Piece Download Resilience**
- **Multiple Sources**: Download same piece from multiple peers
- **Retry Logic**: Retry failed piece downloads
- **Timeout Handling**: Timeout slow peer connections
- **Piece Verification**: Verify every downloaded piece

**3. Download State Persistence**
```python
class DownloadState:
    def __init__(self, torrent_file: str):
        self.torrent_file = torrent_file
        self.state_file = f"{torrent_file}.state"
    
    def save_state(self, piece_manager: PieceManager):
        state = {
            'downloaded_pieces': list(piece_manager.downloaded_pieces),
            'piece_data': {idx: piece.hex() for idx, piece in piece_manager.pieces.items()},
            'timestamp': time.time()
        }
        with open(self.state_file, 'wb') as f:
            pickle.dump(state, f)
    
    def load_state(self) -> dict:
        if os.path.exists(self.state_file):
            with open(self.state_file, 'rb') as f:
                return pickle.load(f)
        return None
```

### DHT Fault Tolerance

**1. Node Failure Handling**
- **Routing Table Maintenance**: Remove failed nodes
- **Node Replacement**: Find replacement nodes
- **Data Replication**: Store data on multiple nodes

**2. Network Partition Handling**
- **Multiple DHT Networks**: Connect to multiple DHT networks
- **Bootstrap Nodes**: Maintain list of bootstrap nodes
- **Network Discovery**: Discover new nodes when network partitions

## Failure Safety

### Failure Scenarios & Handling

**1. Tracker Failure**

**Scenario**: All tracker servers are down.

**Impact**: Cannot discover new peers.

**Mitigation**:
- **DHT Fallback**: Use DHT for peer discovery
- **Cached Peers**: Use previously discovered peers
- **Peer Exchange**: Exchange peer lists with connected peers
- **Retry Logic**: Periodically retry tracker connections

**2. Peer Disconnection**

**Scenario**: Peer disconnects during download.

**Impact**: Lost piece download progress.

**Mitigation**:
- **Multiple Sources**: Request same piece from multiple peers
- **State Persistence**: Save download state periodically
- **Resume Capability**: Resume downloads from saved state
- **Connection Pool**: Maintain pool of connected peers

**3. Piece Corruption**

**Scenario**: Downloaded piece fails hash verification.

**Impact**: Invalid piece data.

**Mitigation**:
- **Hash Verification**: Verify every piece before saving
- **Re-download**: Automatically re-download corrupted pieces
- **Multiple Verification**: Verify from multiple sources
- **Error Logging**: Log corruption events for analysis

**4. Database Failure**

**Scenario**: Database becomes unavailable.

**Impact**: Cannot store/retrieve peer and torrent data.

**Mitigation**:
- **Read Replicas**: Failover to read replicas
- **Caching**: Use Redis cache for critical data
- **Graceful Degradation**: Continue operation with cached data
- **Data Recovery**: Recover from backups

**5. Network Partition**

**Scenario**: Network splits into multiple partitions.

**Impact**: Peers in different partitions cannot communicate.

**Mitigation**:
- **Multiple Networks**: Connect to multiple DHT networks
- **Bootstrap Nodes**: Maintain diverse bootstrap nodes
- **Partition Detection**: Detect and handle partitions
- **Merge Handling**: Merge when partitions reconnect

### Recovery Mechanisms

**1. Download Recovery**
```python
class DownloadRecovery:
    def __init__(self, torrent_file: str):
        self.torrent_file = torrent_file
        self.state_manager = DownloadState(torrent_file)
    
    def recover_download(self, piece_manager: PieceManager):
        # Load saved state
        state = self.state_manager.load_state()
        if not state:
            return False
        
        # Restore downloaded pieces
        for piece_index in state['downloaded_pieces']:
            piece_data = bytes.fromhex(state['piece_data'][piece_index])
            if piece_manager.verify_piece(piece_index, piece_data):
                piece_manager.save_piece(piece_index, piece_data)
        
        return True
```

**2. Peer List Recovery**
- **Tracker Re-announce**: Re-announce to tracker periodically
- **DHT Refresh**: Refresh peer list from DHT
- **Peer Exchange**: Exchange peer lists with connected peers

**3. State Synchronization**
- **Periodic Saves**: Save state every N pieces
- **Checkpointing**: Create checkpoints at milestones
- **Incremental Updates**: Update state incrementally

---

## Optimizations

### Performance Optimizations

#### 1. Piece Download Optimization

**Rarest-First Strategy:**

```python
class RarestFirstOptimizer:
    def select_next_piece(self, available_pieces: list, piece_availability: dict) -> int:
        # Select rarest piece first (better for swarm health)
        rarest_pieces = sorted(
            available_pieces,
            key=lambda p: piece_availability.get(p, 0)
        )
        return rarest_pieces[0] if rarest_pieces else None
```

**Parallel Piece Downloads:**

```python
class ParallelDownloadOptimizer:
    def __init__(self, max_parallel: int = 5):
        self.max_parallel = max_parallel
        self.semaphore = asyncio.Semaphore(max_parallel)
    
    async def download_pieces_parallel(self, pieces: list, peers: list):
        tasks = [
            self.download_piece_with_semaphore(piece, peers)
            for piece in pieces
        ]
        
        results = await asyncio.gather(*tasks)
        return results
    
    async def download_piece_with_semaphore(self, piece_id: int, peers: list):
        async with self.semaphore:
            # Select best peer for this piece
            peer = self.select_best_peer(piece_id, peers)
            return await self.download_from_peer(piece_id, peer)
```

#### 2. Peer Selection Optimization

**Tit-for-Tat Algorithm:**

```python
class TitForTatOptimizer:
    def select_peers(self, available_peers: list, max_peers: int = 50):
        # Rank peers by upload rate to us
        ranked_peers = sorted(
            available_peers,
            key=lambda p: p.get_upload_rate_to_us(),
            reverse=True
        )
        
        # Select top N peers
        return ranked_peers[:max_peers]
```

**Choking Algorithm:**

```python
class ChokingOptimizer:
    def update_choked_peers(self, peers: list):
        # Unchoke top 4 uploaders
        top_uploaders = sorted(
            peers,
            key=lambda p: p.get_upload_rate_to_us(),
            reverse=True
        )[:4]
        
        # Choke others
        for peer in peers:
            if peer in top_uploaders:
                peer.unchoke()
            else:
                peer.choke()
```

#### 3. Piece Verification Optimization

**Parallel Verification:**

```python
class ParallelVerifier:
    async def verify_pieces_parallel(self, pieces: list):
        # Verify multiple pieces in parallel
        tasks = [
            self.verify_piece(piece) for piece in pieces
        ]
        
        results = await asyncio.gather(*tasks)
        return results
```

---

## Security

- **Piece Verification**: SHA-1 checksums
- **Peer Authentication**: Optional peer authentication
- **Rate Limiting**: Prevent abuse
- **Encryption**: Optional piece encryption

### Security Enhancements

**1. Piece Verification**
- **SHA-1 Checksums**: Verify every piece before saving
- **Multiple Verification**: Verify from multiple sources
- **Corruption Detection**: Detect and handle corrupted pieces

**2. Peer Authentication**
- **Optional Authentication**: Support authenticated peers
- **Certificate Validation**: Validate peer certificates
- **Encryption**: Encrypt peer-to-peer communication

**3. Rate Limiting**
- **Connection Limits**: Limit connections per IP
- **Request Throttling**: Throttle piece requests
- **Bandwidth Limits**: Limit bandwidth per peer

**4. DDoS Protection**
- **Rate Limiting**: Limit requests per IP
- **Connection Limits**: Limit concurrent connections
- **IP Blacklisting**: Blacklist malicious IPs

---

## Capacity Planning

- **Peers**: 1M+ peers
- **Torrents**: 100K+ torrents
- **Pieces**: 1B+ pieces
- **Bandwidth**: 10Gbps per tracker

---

## Technology Stack

- **Backend**: Go, Python
- **Protocol**: BitTorrent protocol
- **Database**: PostgreSQL, Redis
- **DHT**: Kademlia DHT

---

## Interview Discussion Points

1. **Piece Distribution**: How do you efficiently distribute pieces?
2. **Peer Discovery**: How do you discover peers?
3. **Incentivization**: How do you incentivize uploading?
4. **Scalability**: How do you scale to millions of peers?

---

**Document Version**: 1.0  
**Last Updated**: January 2024

