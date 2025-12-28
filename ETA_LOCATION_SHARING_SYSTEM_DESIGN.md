# ETA Service and Location Sharing System Design

## Table of Contents
1. [Overview](#overview)
2. [Requirements](#requirements)
3. [System Architecture](#system-architecture)
4. [Database Design](#database-design)
5. [API Design](#api-design)
6. [Real-Time Location Tracking](#real-time-location-tracking)
7. [ETA Calculation](#eta-calculation)
8. [Location Sharing](#location-sharing)
9. [Route Optimization](#route-optimization)
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

A real-time ETA (Estimated Time of Arrival) service and location sharing system for ride-sharing platforms. The system must track driver and rider locations in real-time, calculate accurate ETAs, share locations between parties, and handle millions of concurrent users.

**Key Features:**
- Real-time GPS tracking (driver and rider)
- ETA calculation with traffic data
- Location sharing between driver and rider
- Route optimization
- Real-time updates via WebSocket
- Historical location tracking
- Multi-stop trip support

---

## Requirements

### Functional Requirements

1. **Location Tracking**
   - Track driver location (every 4-5 seconds)
   - Track rider location (every 10-15 seconds)
   - Store location history
   - Handle GPS signal loss

2. **ETA Calculation**
   - Calculate ETA from driver to pickup
   - Calculate ETA from pickup to dropoff
   - Update ETA in real-time
   - Account for traffic conditions
   - Account for route changes

3. **Location Sharing**
   - Share driver location with rider (during active trip)
   - Share rider location with driver (during active trip)
   - Privacy controls (only during trip)
   - Real-time updates

4. **Route Management**
   - Calculate optimal route
   - Handle route changes
   - Multi-stop optimization
   - Traffic-aware routing

5. **Notifications**
   - ETA updates
   - Driver arrival notifications
   - Route change notifications

### Non-Functional Requirements

1. **Scalability**
   - Handle 1M+ concurrent active trips
   - Support millions of users
   - Low latency (< 1 second for updates)

2. **Performance**
   - Location update: < 100ms latency
   - ETA calculation: < 500ms latency
   - Location sharing: < 200ms latency
   - 99th percentile latency < 1s

3. **Accuracy**
   - Accurate ETA predictions
   - Real-time location accuracy
   - Handle GPS inaccuracies

4. **Availability**
   - 99.9% uptime
   - Real-time updates must not fail
   - Graceful degradation

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Applications                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │  Driver  │  │  Rider   │  │  Driver  │  │  Rider   │     │
│  │   App    │  │   App    │  │   App    │  │   App    │     │
│  │ (iOS/    │  │ (iOS/    │  │ (iOS/    │  │ (iOS/    │     │
│  │ Android) │  │ Android) │  │ Android) │  │ Android) │     │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘     │
└───────┼─────────────┼─────────────┼─────────────┼───────────┘
        │             │             │             │
        └─────────────┴─────────────┴─────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│              API Gateway / Load Balancer                     │
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
│              Location Service Layer                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │Location  │  │Location  │  │Location  │  │Location  │   │
│  │Service   │  │Service   │  │Service   │  │Service   │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  ETA     │  │  ETA     │  │  Route   │  │  Route   │   │
│  │ Service  │  │ Service  │  │ Service  │  │ Service  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │Location  │  │Location  │  │Notification│ │Notification│ │
│  │Sharing   │  │Sharing   │  │ Service  │  │ Service  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼───────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│              Real-Time Communication                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │WebSocket │  │WebSocket │  │WebSocket │  │WebSocket │   │
│  │ Server   │  │ Server   │  │ Server   │  │ Server   │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼───────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│              Storage Layer                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Redis   │  │  Redis   │  │Cassandra │  │PostgreSQL│   │
│  │(Current) │  │(GeoSpatial)│ │(History) │  │(Trips)   │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼───────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│              External Services                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Google   │  │  Google   │  │  Google   │  │  Kafka   │   │
│  │ Maps API │  │ Directions│  │  Traffic  │  │(Events)  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Component Details

#### 1. Location Service
- **Responsibilities**:
  - Accept location updates
  - Validate location data
  - Store in Redis (current) and Cassandra (history)
  - Handle GPS signal loss

#### 2. ETA Service
- **Responsibilities**:
  - Calculate ETAs using Google Maps API
  - Cache route data
  - Update ETAs in real-time
  - Handle traffic conditions

#### 3. Route Service
- **Responsibilities**:
  - Calculate optimal routes
  - Handle route changes
  - Multi-stop optimization
  - Traffic-aware routing

#### 4. Location Sharing Service
- **Responsibilities**:
  - Manage location sharing permissions
  - Broadcast locations via WebSocket
  - Privacy controls
  - Real-time updates

#### 5. WebSocket Server
- **Responsibilities**:
  - Maintain WebSocket connections
  - Broadcast location updates
  - Handle connection failures
  - Scale horizontally

### HLD Component Breakdown

**1. Client Layer**
- **Driver App**: iOS/Android app for drivers
- **Rider App**: iOS/Android app for riders
- **Web Dashboard**: Admin dashboard for monitoring

**2. API Gateway Layer**
- **Load Balancer**: Distributes traffic across regions
- **API Gateway**: Routes requests to appropriate services
- **Rate Limiting**: Prevents abuse

**3. Service Layer**
- **Location Service**: Handles location updates
- **ETA Service**: Calculates ETAs
- **Route Service**: Calculates routes
- **Location Sharing Service**: Manages location sharing

**4. Real-Time Layer**
- **WebSocket Servers**: Maintain persistent connections
- **Redis Pub/Sub**: Cross-server communication
- **Message Queue**: Buffers location events

**5. Storage Layer**
- **Redis**: Current locations, geospatial data
- **Cassandra**: Location history
- **PostgreSQL**: Trip metadata

---

## Low-Level Design (LLD)

### Location Service LLD

```python
class LocationService:
    def __init__(self, redis: RedisClient, kafka: KafkaProducer, cassandra: CassandraClient):
        self.redis = redis
        self.kafka = kafka
        self.cassandra = cassandra
    
    def update_location(self, user_id: str, user_type: str, lat: float, lng: float, 
                       trip_id: str = None, metadata: dict = None):
        # Update Redis GeoSpatial
        geo_key = f"location:{user_type}:{user_id}"
        self.redis.geoadd(geo_key, lng, lat, user_id)
        self.redis.expire(geo_key, 7200)  # 2 hours TTL
        
        # Update trip location if in active trip
        if trip_id:
            trip_key = f"trip_location:{trip_id}:{user_type}"
            self.redis.hset(trip_key, mapping={
                'latitude': lat,
                'longitude': lng,
                'timestamp': int(time.time()),
                'accuracy': metadata.get('accuracy', 0),
                'speed': metadata.get('speed', 0),
                'heading': metadata.get('heading', 0)
            })
            self.redis.expire(trip_key, 7200)
        
        # Publish to Kafka for async processing
        self.kafka.publish('location-updates', {
            'user_id': user_id,
            'user_type': user_type,
            'latitude': lat,
            'longitude': lng,
            'trip_id': trip_id,
            'timestamp': time.time(),
            **metadata
        })
        
        # Store in Cassandra (async)
        self._store_history_async(user_id, user_type, lat, lng, trip_id)
```

### ETA Service LLD

```python
class ETAService:
    def __init__(self, google_maps: GoogleMapsClient, cache: RedisCache):
        self.google_maps = google_maps
        self.cache = cache
        self.circuit_breaker = CircuitBreaker(failure_threshold=5, timeout=60)
    
    def calculate_eta(self, origin_lat: float, origin_lng: float, 
                      dest_lat: float, dest_lng: float, trip_id: str = None) -> dict:
        # Generate cache key
        cache_key = self._generate_cache_key(origin_lat, origin_lng, dest_lat, dest_lng)
        
        # Check cache
        cached = self.cache.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # Call Google Maps API with circuit breaker
        try:
            response = self.circuit_breaker.call(
                self.google_maps.directions,
                origin=f"{origin_lat},{origin_lng}",
                destination=f"{dest_lat},{dest_lng}",
                mode='driving',
                traffic_model='best_guess',
                departure_time='now'
            )
            
            route = response['routes'][0]
            leg = route['legs'][0]
            
            result = {
                'eta_seconds': leg['duration']['value'],
                'eta_minutes': leg['duration']['value'] // 60,
                'distance_meters': leg['distance']['value'],
                'distance_miles': leg['distance']['value'] * 0.000621371,
                'polyline': route['overview_polyline']['points'],
                'traffic_condition': self._analyze_traffic(leg)
            }
            
            # Cache result
            ttl = 30 if trip_id else 300  # 30s for active trips, 5min for estimates
            self.cache.set(cache_key, json.dumps(result), ex=ttl)
            
            return result
        
        except CircuitBreakerOpenError:
            # Fallback to cached or historical data
            return self._get_fallback_eta(origin_lat, origin_lng, dest_lat, dest_lng)
```

### Location Sharing Service LLD

```python
class LocationSharingService:
    def __init__(self, websocket_manager: WebSocketManager, trip_store: TripStore):
        self.websocket_manager = websocket_manager
        self.trip_store = trip_store
        self.redis_pubsub = RedisPubSub()
    
    def share_location(self, trip_id: str, user_type: str, location: dict):
        # Verify trip is active
        trip = self.trip_store.get_trip(trip_id)
        if trip.status != 'in_progress':
            return  # Don't share if trip not active
        
        # Get other party's type
        other_party_type = 'rider' if user_type == 'driver' else 'driver'
        
        # Get other party's location
        other_location = self._get_location(trip_id, other_party_type)
        
        # Calculate ETA
        eta = self._calculate_trip_eta(trip_id, location, other_location)
        
        # Prepare message
        message = {
            'type': 'location_update',
            'trip_id': trip_id,
            f'{user_type}_location': location,
            f'{other_party_type}_location': other_location,
            'eta_seconds': eta,
            'timestamp': time.time()
        }
        
        # Broadcast via WebSocket
        self.websocket_manager.broadcast_to_trip(trip_id, message)
        
        # Also publish to Redis Pub/Sub for cross-server communication
        self.redis_pubsub.publish(f"trip:{trip_id}:location", message)
```

### WebSocket Manager LLD

```python
class WebSocketManager:
    def __init__(self, redis: RedisClient):
        self.connections = {}  # trip_id -> set of connections
        self.user_connections = {}  # user_id -> connection
        self.redis = redis
        self.redis_pubsub = redis.pubsub()
        self.redis_pubsub.subscribe('trip:*:location')
    
    def connect(self, user_id: str, trip_id: str, websocket: WebSocket):
        # Store connection
        if trip_id not in self.connections:
            self.connections[trip_id] = set()
        self.connections[trip_id].add(websocket)
        self.user_connections[user_id] = websocket
        
        # Subscribe to Redis Pub/Sub for cross-server updates
        self.redis_pubsub.subscribe(f"trip:{trip_id}:location")
    
    def broadcast_to_trip(self, trip_id: str, message: dict):
        if trip_id not in self.connections:
            return
        
        message_json = json.dumps(message)
        disconnected = []
        
        for connection in self.connections[trip_id]:
            try:
                connection.send(message_json)
            except Exception as e:
                logger.error(f"Error sending message: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for conn in disconnected:
            self.connections[trip_id].discard(conn)
```

---

## Fault Tolerance

### Location Update Fault Tolerance

**1. Retry Logic**
```python
class LocationUpdateHandler:
    def __init__(self, location_service: LocationService, retry_queue: Queue):
        self.location_service = location_service
        self.retry_queue = retry_queue
    
    def handle_update(self, location_data: dict):
        try:
            self.location_service.update_location(**location_data)
        except Exception as e:
            logger.error(f"Failed to update location: {e}")
            # Add to retry queue
            self.retry_queue.put(location_data)
    
    def retry_failed_updates(self):
        while not self.retry_queue.empty():
            location_data = self.retry_queue.get()
            try:
                self.location_service.update_location(**location_data)
            except Exception:
                # Re-queue if still failing
                self.retry_queue.put(location_data)
                time.sleep(1)  # Backoff
```

**2. Circuit Breaker for External APIs**
- **Google Maps API**: Circuit breaker to prevent cascading failures
- **Fallback Strategy**: Use cached ETAs or historical data
- **Health Monitoring**: Monitor API health and switch on degradation

**3. WebSocket Connection Resilience**
- **Automatic Reconnection**: Client reconnects on disconnect
- **Message Queue**: Queue messages during disconnection
- **Heartbeat**: Periodic ping/pong to detect dead connections

### Storage Fault Tolerance

**1. Redis Cluster**
- **Multiple Nodes**: Deploy Redis cluster with 3+ nodes
- **Replication**: Each node has replicas
- **Automatic Failover**: Promote replica on node failure
- **Data Persistence**: AOF and RDB for durability

**2. Cassandra Replication**
- **Replication Factor**: 3 replicas per data center
- **Consistency Levels**: QUORUM for reads/writes
- **Hinted Handoff**: Handle temporary node failures
- **Repair**: Periodic repair for consistency

**3. Database Failover**
- **Read Replicas**: PostgreSQL read replicas
- **Automatic Failover**: Promote replica on primary failure
- **Connection Retry**: Retry connections with exponential backoff

---

## Failure Safety

### Failure Scenarios & Handling

**1. GPS Signal Loss**

**Scenario**: Driver loses GPS signal (tunnel, building).

**Impact**: Cannot track location, ETA becomes inaccurate.

**Mitigation**:
- **Last Known Location**: Use last known location
- **Route Prediction**: Predict location based on route
- **Reconnection**: Resume tracking when signal returns
- **Fallback ETA**: Use route-based ETA without real-time updates

**Recovery**:
```python
class GPSLossHandler:
    def handle_gps_loss(self, user_id: str, trip_id: str):
        # Get last known location
        last_location = self.get_last_location(user_id)
        
        # Get route
        route = self.get_route(trip_id)
        
        # Predict location based on route and speed
        predicted_location = self.predict_location(last_location, route)
        
        # Use predicted location for ETA
        return self.calculate_eta_from_prediction(predicted_location, route)
```

**2. Google Maps API Failure**

**Scenario**: Google Maps API is down or rate limited.

**Impact**: Cannot calculate ETAs.

**Mitigation**:
- **Caching**: Use cached ETAs
- **Historical Data**: Use historical average ETAs
- **Fallback**: Simple distance-based ETA
- **Circuit Breaker**: Prevent cascading failures

**Recovery**:
- **Retry Logic**: Retry with exponential backoff
- **Multiple API Keys**: Rotate API keys
- **Service Degradation**: Continue with reduced functionality

**3. WebSocket Connection Failure**

**Scenario**: WebSocket connection drops.

**Impact**: Location updates not delivered.

**Mitigation**:
- **Reconnection**: Automatic reconnection
- **Polling Fallback**: Fallback to polling API
- **Message Queue**: Queue messages during disconnection
- **Redis Pub/Sub**: Cross-server communication

**Recovery**:
- **Reconnect**: Client automatically reconnects
- **Message Replay**: Replay queued messages on reconnect
- **State Sync**: Sync state on reconnection

**4. Redis Failure**

**Scenario**: Redis cluster fails.

**Impact**: Cannot store/retrieve current locations.

**Mitigation**:
- **Redis Cluster**: Multiple nodes with replication
- **Database Fallback**: Query Cassandra for recent locations
- **Local Cache**: Use application-level cache
- **Graceful Degradation**: Continue with reduced functionality

**Recovery**:
- **Failover**: Automatically failover to healthy nodes
- **Cache Warming**: Pre-populate cache after recovery
- **Data Sync**: Sync data from Cassandra

**5. High Load**

**Scenario**: Sudden spike in location updates.

**Impact**: System overload, increased latency.

**Mitigation**:
- **Rate Limiting**: Limit updates per user
- **Throttling**: Throttle updates during high load
- **Queue Buffering**: Buffer updates in Kafka
- **Auto-Scaling**: Scale services automatically

**Recovery**:
- **Scale Up**: Add more service instances
- **Load Shedding**: Drop non-critical updates
- **Priority Queue**: Process critical updates first

---

## Database Design

### Redis Schema

#### Current Locations (GeoSpatial)
```
Key: location:{user_type}:{user_id}  // user_type: 'driver' or 'rider'
Type: GEO
Members: user_id → (latitude, longitude)
```

**Example:**
```redis
GEOADD location:driver:driver_123 37.7749 -122.4194
GEOPOS location:driver:driver_123 driver_123
```

#### Active Trip Locations
```
Key: trip_location:{trip_id}:{user_type}
Type: Hash
Fields:
  - latitude
  - longitude
  - accuracy
  - speed
  - heading
  - timestamp
TTL: 2 hours
```

### Cassandra Schema

#### Location History Table
```cql
CREATE TABLE location_history (
    user_id UUID,
    user_type TEXT,  -- 'driver' or 'rider'
    timestamp TIMESTAMP,
    latitude DECIMAL,
    longitude DECIMAL,
    accuracy FLOAT,
    speed FLOAT,
    heading FLOAT,
    trip_id UUID,
    PRIMARY KEY ((user_id), timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);
```

#### Trip Locations Table
```cql
CREATE TABLE trip_locations (
    trip_id UUID,
    timestamp TIMESTAMP,
    driver_latitude DECIMAL,
    driver_longitude DECIMAL,
    rider_latitude DECIMAL,
    rider_longitude DECIMAL,
    driver_eta_seconds INT,
    PRIMARY KEY ((trip_id), timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);
```

### PostgreSQL Schema

#### Trips Table
```sql
CREATE TABLE trips (
    id BIGSERIAL PRIMARY KEY,
    trip_id VARCHAR(50) UNIQUE NOT NULL,
    driver_id BIGINT NOT NULL,
    rider_id BIGINT NOT NULL,
    pickup_latitude DECIMAL(10, 8) NOT NULL,
    pickup_longitude DECIMAL(11, 8) NOT NULL,
    dropoff_latitude DECIMAL(10, 8),
    dropoff_longitude DECIMAL(11, 8),
    status VARCHAR(20) DEFAULT 'pending',
    current_eta_seconds INT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_driver_id (driver_id),
    INDEX idx_rider_id (rider_id),
    INDEX idx_status (status)
) ENGINE=InnoDB;
```

---

## API Design

### Location APIs

**Update Location**
```
POST /api/v1/location/update
Content-Type: application/json
Authorization: Bearer {token}

Request:
{
    "user_id": "driver_123",
    "user_type": "driver",  // or "rider"
    "latitude": 37.7749,
    "longitude": -122.4194,
    "accuracy": 10.5,
    "speed": 25.5,
    "heading": 90.0,
    "trip_id": "trip_456"  // Optional, if in active trip
}

Response:
{
    "success": true,
    "timestamp": "2024-01-15T10:30:00Z"
}
```

**Get Current Location**
```
GET /api/v1/location/{user_id}?user_type=driver

Response:
{
    "user_id": "driver_123",
    "user_type": "driver",
    "latitude": 37.7749,
    "longitude": -122.4194,
    "accuracy": 10.5,
    "speed": 25.5,
    "heading": 90.0,
    "timestamp": "2024-01-15T10:30:00Z"
}
```

### ETA APIs

**Calculate ETA**
```
POST /api/v1/eta/calculate
Content-Type: application/json

Request:
{
    "origin_latitude": 37.7749,
    "origin_longitude": -122.4194,
    "destination_latitude": 37.7849,
    "destination_longitude": -122.4094,
    "trip_id": "trip_456"  // Optional, for caching
}

Response:
{
    "eta_seconds": 600,
    "eta_minutes": 10,
    "distance_meters": 5000,
    "distance_miles": 3.1,
    "route": {
        "polyline": "encoded_polyline_string",
        "steps": [...]
    },
    "traffic_condition": "moderate"
}
```

**Get Trip ETA**
```
GET /api/v1/trips/{trip_id}/eta

Response:
{
    "trip_id": "trip_456",
    "driver_to_pickup_eta_seconds": 300,
    "pickup_to_dropoff_eta_seconds": 900,
    "total_eta_seconds": 1200,
    "driver_location": {
        "latitude": 37.7749,
        "longitude": -122.4194
    },
    "pickup_location": {
        "latitude": 37.7800,
        "longitude": -122.4100
    },
    "updated_at": "2024-01-15T10:30:00Z"
}
```

### Location Sharing APIs

**Get Shared Location**
```
GET /api/v1/trips/{trip_id}/location/shared?user_type=rider

Response:
{
    "trip_id": "trip_456",
    "driver_location": {
        "latitude": 37.7749,
        "longitude": -122.4194,
        "accuracy": 10.5,
        "speed": 25.5,
        "heading": 90.0,
        "timestamp": "2024-01-15T10:30:00Z"
    },
    "rider_location": {
        "latitude": 37.7800,
        "longitude": -122.4100,
        "accuracy": 15.0,
        "timestamp": "2024-01-15T10:29:45Z"
    },
    "driver_eta_seconds": 300
}
```

**Subscribe to Location Updates (WebSocket)**
```
WS /api/v1/trips/{trip_id}/location/stream

Message Format:
{
    "type": "location_update",
    "trip_id": "trip_456",
    "driver_location": {...},
    "rider_location": {...},
    "eta_seconds": 300,
    "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## Data Flow Diagrams

### Location Update Flow

```
Driver App Sends Location Update (Every 4-5 seconds)
    │
    ▼
Location Service
    │
    ├─ Validate Location Data
    ├─ Check if in Active Trip
    │
    ▼
Update Redis (Current Location)
    │
    ├─ Update GeoSpatial: GEOADD location:driver:{driver_id} lat lng
    ├─ Update Trip Location: HSET trip_location:{trip_id}:driver {...}
    │
    ▼
Publish to Kafka (Location Event)
    │
    ├─ Topic: location-updates
    │
    ▼
Kafka Consumers (Parallel Processing)
    │
    ├─ ETA Service
    │   ├─ Recalculate ETA
    │   └─ Update ETA Cache
    │
    ├─ Location Sharing Service
    │   └─ Broadcast to Rider via WebSocket
    │
    └─ Storage Service
        └─ Store in Cassandra (History)
```

### ETA Calculation Flow

```
ETA Calculation Request
    │
    ▼
ETA Service
    │
    ├─ Check Cache (Redis)
    │   └─ Cache Key: eta:{origin}:{destination}:{hash}
    │   └─ Cache Hit → Return (1-2ms)
    │
    └─ Cache Miss → Continue
        │
        ▼
    Call Google Maps Directions API
        │
        ├─ Request Route
        ├─ Get Traffic Data
        └─ Get ETA
        │
        ▼
    Cache Result (Redis)
        │
        ├─ TTL: 30 seconds (for active trips)
        └─ TTL: 5 minutes (for estimates)
        │
        ▼
    Return ETA
```

### Location Sharing Flow

```
Location Update Received
    │
    ▼
Location Sharing Service
    │
    ├─ Check Trip Status (Active Trip Only)
    ├─ Get Other Party's Location
    │
    ▼
Broadcast via WebSocket
    │
    ├─ Find WebSocket Connections
    │   ├─ Driver Connection: ws://.../trips/{trip_id}/driver
    │   └─ Rider Connection: ws://.../trips/{trip_id}/rider
    │
    ├─ Send Location Update
    │   └─ JSON Message with locations and ETA
    │
    └─ Handle Connection Failures
        └─ Fallback to Polling API
```

---

## Real-Time Location Tracking

### Location Update Frequency

**Driver:**
- **Active Trip**: Every 4-5 seconds
- **Online (No Trip)**: Every 10-15 seconds

**Rider:**
- **Active Trip**: Every 10-15 seconds
- **Waiting for Driver**: Every 30 seconds

### Location Storage Strategy

**Current Location (Redis):**
- GeoSpatial data structure
- Fast queries
- TTL: 2 hours

**Location History (Cassandra):**
- Time-series data
- Historical analysis
- Long-term storage

**Implementation:**
```python
class LocationService:
    def update_location(self, user_id, user_type, lat, lng, trip_id=None):
        # Update Redis GeoSpatial
        redis.geoadd(f"location:{user_type}:{user_id}", lng, lat, user_id)
        
        # Update trip location if in active trip
        if trip_id:
            redis.hset(
                f"trip_location:{trip_id}:{user_type}",
                mapping={
                    'latitude': lat,
                    'longitude': lng,
                    'timestamp': int(time.time())
                }
            )
            redis.expire(f"trip_location:{trip_id}:{user_type}", 7200)
        
        # Publish to Kafka
        kafka.publish('location-updates', {
            'user_id': user_id,
            'user_type': user_type,
            'latitude': lat,
            'longitude': lng,
            'trip_id': trip_id,
            'timestamp': time.time()
        })
```

---

## ETA Calculation

### ETA Calculation Methods

**1. Google Maps Directions API:**
- Real-time traffic data
- Multiple route options
- Accurate ETAs

**2. Historical Data:**
- Average travel times
- Time-of-day patterns
- Fallback when API unavailable

**3. Machine Learning:**
- Predict ETAs based on patterns
- Account for various factors
- Improve accuracy over time

### ETA Update Strategy

**Update Frequency:**
- **Active Trip**: Every 10-15 seconds
- **Estimated Trip**: Every 30 seconds
- **On Route Change**: Immediately

**Caching Strategy:**
- Cache ETAs for 30 seconds (active trips)
- Cache ETAs for 5 minutes (estimates)
- Invalidate on route change

**Implementation:**
```python
class ETAService:
    def calculate_eta(self, origin_lat, origin_lng, dest_lat, dest_lng, trip_id=None):
        # Check cache
        cache_key = self.get_cache_key(origin_lat, origin_lng, dest_lat, dest_lng)
        cached = redis.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # Call Google Maps API
        response = google_maps.directions(
            origin=f"{origin_lat},{origin_lng}",
            destination=f"{dest_lat},{dest_lng}",
            mode='driving',
            traffic_model='best_guess',
            departure_time='now'
        )
        
        route = response['routes'][0]
        leg = route['legs'][0]
        
        eta_seconds = leg['duration']['value']
        distance_meters = leg['distance']['value']
        
        result = {
            'eta_seconds': eta_seconds,
            'eta_minutes': eta_seconds // 60,
            'distance_meters': distance_meters,
            'distance_miles': distance_meters * 0.000621371,
            'polyline': route['overview_polyline']['points']
        }
        
        # Cache result
        ttl = 30 if trip_id else 300  # 30s for active trips, 5min for estimates
        redis.setex(cache_key, ttl, json.dumps(result))
        
        return result
```

---

## Location Sharing

### Privacy Controls

**Sharing Rules:**
- **During Active Trip Only**: Share locations only when trip is active
- **Trip Participants Only**: Only driver and rider can see each other's locations
- **Automatic Stop**: Stop sharing when trip ends

**Implementation:**
```python
class LocationSharingService:
    def share_location(self, trip_id, user_type, location):
        # Verify trip is active
        trip = self.get_trip(trip_id)
        if trip.status != 'in_progress':
            return  # Don't share if trip not active
        
        # Get other party's connection
        other_party_type = 'rider' if user_type == 'driver' else 'driver'
        connections = self.get_websocket_connections(trip_id, other_party_type)
        
        # Broadcast location update
        message = {
            'type': 'location_update',
            'trip_id': trip_id,
            f'{user_type}_location': location,
            'eta_seconds': self.calculate_trip_eta(trip_id),
            'timestamp': time.time()
        }
        
        for connection in connections:
            connection.send(json.dumps(message))
```

### WebSocket Management

**Connection Management:**
- Maintain WebSocket connections per trip
- Handle reconnections
- Scale horizontally with sticky sessions

**Message Format:**
```json
{
    "type": "location_update",
    "trip_id": "trip_456",
    "driver_location": {
        "latitude": 37.7749,
        "longitude": -122.4194,
        "speed": 25.5,
        "heading": 90.0
    },
    "rider_location": {
        "latitude": 37.7800,
        "longitude": -122.4100
    },
    "eta_seconds": 300,
    "timestamp": 1609459200
}
```

---

## Route Optimization

### Route Calculation

**Google Maps Integration:**
- Directions API for routes
- Traffic-aware routing
- Multiple route options

**Route Caching:**
- Cache routes for 30 seconds
- Invalidate on significant location change
- Pre-compute common routes

**Implementation:**
```python
class RouteService:
    def calculate_route(self, origin_lat, origin_lng, dest_lat, dest_lng):
        # Check cache
        cache_key = f"route:{origin_lat}:{origin_lng}:{dest_lat}:{dest_lng}"
        cached = redis.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # Call Google Maps API
        response = google_maps.directions(
            origin=f"{origin_lat},{origin_lng}",
            destination=f"{dest_lat},{dest_lng}",
            alternatives=True,
            mode='driving'
        )
        
        # Select best route (shortest time)
        best_route = min(
            response['routes'],
            key=lambda r: r['legs'][0]['duration']['value']
        )
        
        route_data = {
            'polyline': best_route['overview_polyline']['points'],
            'distance_meters': best_route['legs'][0]['distance']['value'],
            'duration_seconds': best_route['legs'][0]['duration']['value'],
            'steps': best_route['legs'][0]['steps']
        }
        
        # Cache for 30 seconds
        redis.setex(cache_key, 30, json.dumps(route_data))
        
        return route_data
```

---

## Scalability Considerations

### 1. Location Update Scale

**Challenge:** Millions of location updates per second.

**Solutions:**
- **Batching**: Batch location updates (10-50 updates per batch)
- **Kafka**: Buffer updates asynchronously with partitioning
- **Sharding**: Shard by user_id or trip_id
- **Compression**: Compress location data (reduce by 50-70%)
- **Horizontal Scaling**: Scale location services horizontally

**Implementation:**
```python
class LocationBatcher:
    def __init__(self, batch_size: int = 50, flush_interval: float = 1.0):
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.buffer = []
        self.last_flush = time.time()
    
    def add_update(self, update: dict):
        self.buffer.append(update)
        
        if len(self.buffer) >= self.batch_size:
            self.flush()
        elif time.time() - self.last_flush > self.flush_interval:
            self.flush()
    
    def flush(self):
        if not self.buffer:
            return
        
        # Compress and send batch
        compressed = self.compress_batch(self.buffer)
        self.kafka.publish('location-updates-batch', compressed)
        
        self.buffer = []
        self.last_flush = time.time()
```

### 2. WebSocket Scaling

**Challenge:** Millions of concurrent WebSocket connections.

**Solutions:**
- **Horizontal Scaling**: Multiple WebSocket servers (1000+ connections per server)
- **Sticky Sessions**: Route same client to same server (session affinity)
- **Redis Pub/Sub**: Broadcast across servers
- **Connection Pooling**: Efficient connection management
- **Load Balancing**: Distribute connections across servers

**Scaling Metrics:**
- **Per Server**: 10K-50K concurrent connections
- **Total Capacity**: 1M+ connections with 20-100 servers
- **Message Throughput**: 100K messages/second per server

**Implementation:**
```python
class WebSocketCluster:
    def __init__(self, servers: list, redis: RedisClient):
        self.servers = servers
        self.redis = redis
        self.consistent_hash = ConsistentHash(servers)
    
    def route_connection(self, user_id: str) -> WebSocketServer:
        # Consistent hashing for sticky sessions
        return self.consistent_hash.get_server(user_id)
    
    def broadcast(self, trip_id: str, message: dict):
        # Publish to Redis Pub/Sub for cross-server broadcast
        self.redis.publish(f"trip:{trip_id}", json.dumps(message))
```

### 3. ETA Calculation Scale

**Challenge:** Millions of ETA calculations per second.

**Solutions:**
- **Caching**: Aggressive caching (80%+ hit rate)
- **Batching**: Batch API calls (reduce API calls by 90%)
- **Rate Limiting**: Limit Google Maps API calls per key
- **Fallback**: Use historical data when API rate limited
- **Multiple API Keys**: Rotate API keys for higher limits

**Caching Strategy:**
- **Active Trips**: 30-second cache (frequent updates)
- **Estimates**: 5-minute cache (less frequent)
- **Popular Routes**: Pre-compute and cache
- **Historical Data**: Use for fallback

**Performance Targets:**
- **Cache Hit Rate**: > 80%
- **API Call Reduction**: 90%+ reduction via caching
- **Latency**: < 500ms (p95) with caching

### 4. Database Scaling

**Redis Scaling:**
- **Cluster Mode**: Deploy Redis cluster with hash slots
- **Sharding**: Shard by user_id or trip_id
- **Replication**: 1 replica per master
- **Memory Optimization**: Use efficient data structures

**Cassandra Scaling:**
- **Partitioning**: Partition by user_id
- **Replication**: 3 replicas per data center
- **Compaction**: Regular compaction for performance
- **Read/Write Optimization**: Tune consistency levels

**PostgreSQL Scaling:**
- **Read Replicas**: 3-5 read replicas
- **Sharding**: Shard trips table by trip_id
- **Connection Pooling**: PgBouncer for connection pooling
- **Partitioning**: Partition by date for old data

### 5. Message Queue Scaling

**Kafka Scaling:**
- **Partitioning**: Partition by user_id or trip_id
- **Replication**: 3 replicas per partition
- **Consumer Groups**: Parallel processing
- **Auto-Scaling**: Scale consumers based on lag

**Performance Targets:**
- **Throughput**: 1M+ messages/second
- **Latency**: < 10ms (p95)
- **Durability**: 99.99% message delivery

### 6. Geographic Distribution

**Multi-Region Deployment:**
- **Regional Services**: Deploy services in multiple regions
- **Data Locality**: Store data close to users
- **Cross-Region Replication**: Replicate critical data
- **Route Optimization**: Route requests to nearest region

**Latency Optimization:**
- **Edge Locations**: Deploy at edge locations
- **CDN**: Use CDN for static assets
- **Regional Caching**: Cache data per region
- **Proximity Routing**: Route to nearest data center

---

## Caching Strategy

### Cache Architecture

```
Location Update
    │
    ▼
Redis (Current Location)
    │
    ├─ GeoSpatial: Fast queries
    └─ Trip Location: Per-trip tracking
    │
    ▼
Kafka (Async Processing)
    │
    └─ Store in Cassandra (History)
```

### Cache Keys

```
location:{user_type}:{user_id} → GeoSpatial location
trip_location:{trip_id}:{user_type} → Trip location
eta:{origin}:{destination} → Cached ETA
route:{origin}:{destination} → Cached route
```

### Cache Invalidation

**TTL-Based:**
- Current locations: 2 hours
- ETAs: 30 seconds (active trips), 5 minutes (estimates)
- Routes: 30 seconds

**Event-Based:**
- Invalidate on route change
- Invalidate on trip status change

---

## Load Balancing

### Load Balancer Architecture

```
Location Updates / ETA Requests
    │
    ▼
Load Balancer
    │
    ├─ Location Service 1
    ├─ Location Service 2
    ├─ ETA Service 1
    └─ ETA Service 2
```

### WebSocket Load Balancing

**Sticky Sessions:**
- Route same client to same WebSocket server
- Maintain connection state
- Use session affinity

---

## Security

### 1. Location Privacy

**Privacy Controls:**
- Share locations only during active trips
- Automatic stop on trip end
- User consent required
- Encrypt location data

### 2. Authentication & Authorization

**Authentication:**
- JWT tokens
- Validate trip participation
- Verify user ownership

**Authorization:**
- Only trip participants can see locations
- Validate trip status
- Check permissions

---

## Monitoring & Analytics

### Key Metrics

**Performance Metrics:**
- Location update latency
- ETA calculation latency
- WebSocket message delivery latency
- Google Maps API latency

**Business Metrics:**
- Active trips
- Average ETA accuracy
- Location update frequency
- Route optimization effectiveness

---

## Deployment Strategy

### Infrastructure

**Cloud Provider**: AWS, GCP, or Azure

**Components:**
- **Compute**: Kubernetes (EKS/GKE)
- **Cache**: Redis (ElastiCache)
- **Database**: Cassandra (Keyspaces), PostgreSQL (RDS)
- **WebSocket**: Custom servers or AWS API Gateway WebSocket

---

## Capacity Planning

### Storage Estimates

**Location Data:**
- 1M active trips
- 4 updates/min per user × 2 users = 8 updates/min per trip
- 1M × 8 × 100 bytes = 800 MB/min = 1.15 TB/day

**After Compression:**
- **Total: ~400 GB/day**

### Compute Requirements

**Location Services:**
- 1M trips × 8 updates/min = 8M updates/min = 133K updates/sec
- Each update: ~10ms processing
- Required servers: 133K / (1000/10) = 1,330 servers

**ETA Services:**
- 1M trips × 1 ETA calc/30s = 33K calc/sec
- Each calc: ~200ms (with caching)
- Required servers: 33K × 0.2 = 6,600 servers
- With 80% cache hit rate: **1,320 servers**

---

## Technology Stack

### Recommended Stack

**Compute:**
- **Language**: Go or Java
- **Orchestration**: Kubernetes

**Cache:**
- **Redis** (ElastiCache)

**Database:**
- **Cassandra** (Keyspaces)
- **PostgreSQL** (RDS)

**External Services:**
- **Google Maps API**

**WebSocket:**
- **Custom servers** or **AWS API Gateway WebSocket**

---

## Failure Scenarios & Handling

### 1. GPS Signal Loss

**Scenario:** Driver loses GPS signal (tunnel, building).

**Impact:** Cannot track location.

**Mitigation:**
- **Last Known Location**: Use last known location
- **Prediction**: Predict location based on route
- **Reconnection**: Resume tracking when signal returns

### 2. Google Maps API Failure

**Scenario:** Google Maps API is down or rate limited.

**Impact:** Cannot calculate ETAs.

**Mitigation:**
- **Caching**: Use cached ETAs
- **Historical Data**: Use historical average ETAs
- **Fallback**: Simple distance-based ETA

### 3. WebSocket Connection Failure

**Scenario:** WebSocket connection drops.

**Impact:** Location updates not delivered.

**Mitigation:**
- **Reconnection**: Automatic reconnection
- **Polling Fallback**: Fallback to polling API
- **Message Queue**: Queue messages during disconnection

---

## Trade-offs & Design Decisions

### 1. Update Frequency: High vs Low

**Decision:** High frequency (4-5s for drivers).

**Trade-offs:**

| Frequency | Pros | Cons |
|-----------|------|------|
| **High** | Accurate, smooth | Higher load |
| **Low** | Lower load | Less accurate |

**Why High:**
- **User Experience**: Smooth tracking expected
- **Safety**: Accurate location for safety features

### 2. ETA: Real-time vs Cached

**Decision:** Cached with frequent updates.

**Trade-offs:**

| Approach | Pros | Cons |
|----------|------|------|
| **Real-time** | Always accurate | High API costs |
| **Cached** | Lower costs | Slight delay |

**Why Cached:**
- **Cost**: Google Maps API is expensive
- **Acceptable**: 30-second cache is acceptable

### 3. Location Sharing: Always vs Trip-Only

**Decision:** Trip-only sharing.

**Trade-offs:**

| Approach | Pros | Cons |
|----------|------|------|
| **Trip-Only** | Privacy, secure | Less flexible |
| **Always** | More flexible | Privacy concerns |

**Why Trip-Only:**
- **Privacy**: Users expect privacy
- **Security**: Reduce abuse risk

---

## Interview Discussion Points

### Key Questions to Address

1. **"How do you handle GPS signal loss?"**
   - **Answer**: 
     - Use last known location
     - Predict location based on route
     - Resume tracking when signal returns

2. **"How do you ensure ETA accuracy?"**
   - **Answer**:
     - Real-time traffic data from Google Maps
     - Frequent updates (every 10-15 seconds)
     - Account for route changes
     - Machine learning for improvement

3. **"How do you scale WebSocket connections?"**
   - **Answer**:
     - Horizontal scaling with sticky sessions
     - Redis Pub/Sub for cross-server communication
     - Connection pooling
     - Efficient message broadcasting

4. **"How do you handle Google Maps API rate limits?"**
   - **Answer**:
     - Aggressive caching
     - Batch API calls
     - Fallback to historical data
     - Multiple API keys

5. **"How do you ensure location privacy?"**
   - **Answer**:
     - Share only during active trips
     - Automatic stop on trip end
     - Encrypt location data
     - User consent required

---

## References

- [Uber System Design](design/UBER_SYSTEM_DESIGN.md)
- [Google Maps Directions API](https://developers.google.com/maps/documentation/directions)
- [Redis GeoSpatial](https://redis.io/commands/geoadd/)
- [WebSocket Scaling](https://www.nginx.com/blog/websocket-nginx/)

