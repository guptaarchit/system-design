# Surge Pricing System: Uber - Stream Processing

## Table of Contents
1. [Overview](#overview)
2. [Requirements](#requirements)
3. [System Architecture](#system-architecture)
4. [Data Models](#data-models)
5. [API Design](#api-design)
6. [Stream Processing Pipeline](#stream-processing-pipeline)
7. [Surge Calculation Algorithm](#surge-calculation-algorithm)
8. [Real-time Updates](#real-time-updates)
9. [Scalability Considerations](#scalability-considerations)
10. [Caching Strategy](#caching-strategy)
11. [Load Balancing](#load-balancing)
12. [Security](#security)
13. [Monitoring & Analytics](#monitoring--analytics)
14. [Capacity Planning](#capacity-planning)
15. [Technology Stack](#technology-stack)
16. [Failure Scenarios & Handling](#failure-scenarios--handling)
17. [Trade-offs & Design Decisions](#trade-offs--design-decisions)
18. [Interview Discussion Points](#interview-discussion-points)

---

## Overview

A real-time surge pricing system similar to Uber that calculates dynamic pricing based on supply and demand. The system must process location updates from drivers and riders in real-time, calculate surge multipliers for geographic areas, update prices instantly, and handle high-throughput stream processing.

**Key Features:**
- Real-time location tracking
- Supply and demand calculation
- Surge multiplier calculation
- Geographic area (hex/bin) based pricing
- Price updates in real-time
- Historical surge data
- Price prediction

---

## Requirements

### Functional Requirements

1. **Location Tracking**
   - Track driver locations in real-time
   - Track rider requests in real-time
   - Update locations every few seconds

2. **Supply/Demand Calculation**
   - Calculate available drivers per area
   - Calculate active ride requests per area
   - Calculate supply/demand ratio

3. **Surge Calculation**
   - Calculate surge multiplier (1.0x to 5.0x)
   - Apply surge to base price
   - Update prices in real-time

4. **Geographic Areas**
   - Divide map into hexagonal bins
   - Calculate surge per bin
   - Smooth surge across adjacent bins

### Non-Functional Requirements

1. **Scalability**
   - Handle 1M+ location updates per second
   - Support 100K+ concurrent drivers/riders
   - Process updates with < 1 second latency

2. **Performance**
   - Location update: < 100ms
   - Surge calculation: < 500ms
   - Price query: < 50ms

3. **Reliability**
   - 99.9% uptime
   - No data loss
   - Real-time accuracy

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                             │
│  (Driver Apps, Rider Apps)                                     │
└────────────────┬────────────────────────────────────────────────┘
                 │ WebSocket / HTTP
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API Gateway / Load Balancer                   │
└────────────┬────────────────────────────────────┬────────────────┘
             │                                    │
             ▼                                    ▼
┌────────────────────────────┐      ┌────────────────────────────┐
│   Location Service         │      │   Pricing Service         │
│   - Location Updates       │      │   - Price Queries         │
└────────────┬───────────────┘      └────────────┬───────────────┘
             │                                    │
             ▼                                    ▼
┌────────────────────────────────────────────────────────────────┐
│                    Stream Processing Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Location  │  │   Supply/    │  │   Surge      │         │
│  │   Stream    │  │   Demand    │  │   Calculator  │         │
│  │   Processor │  │   Calculator │  │              │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────┬────────────────────┬────────────────────┬──────────────────┘
     │                    │                    │
     ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  Message Queue  │  │   State Store   │  │   Event Bus     │
│  (Kafka)        │  │  (Redis/Redis   │  │   (Kafka)       │
│                 │  │   Streams)      │  │                 │
└─────────────────┘  └─────────────────┘  └─────────────────┘
     │                    │                    │
     ▼                    ▼                    ▼
┌────────────────────────────────────────────────────────────────┐
│                      Data Layer                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Location   │  │   Surge      │  │   Historical │         │
│  │     DB      │  │     DB       │  │     DB       │         │
│  │ (Redis)     │  │  (Redis)     │  │ (Cassandra)  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────────────────────────────────────────────┘
```

---

## Data Models

### Location Update

```json
{
  "user_id": "user_123",
  "user_type": "driver", // driver or rider
  "latitude": 37.7749,
  "longitude": -122.4194,
  "timestamp": 1705312800000,
  "status": "available" // available, on_trip, offline
}
```

### Surge Data Structure (Redis)

```
Key: surge:{hex_bin_id}
Type: Hash
Fields:
  - multiplier: 1.5
  - supply: 10
  - demand: 15
  - updated_at: 1705312800000
```

### Geographic Bin

```python
class HexBin:
    bin_id: str  # Hexagonal bin ID
    center_lat: float
    center_lng: float
    supply: int  # Available drivers
    demand: int  # Active ride requests
    surge_multiplier: float  # 1.0 to 5.0
    last_updated: int
```

---

## API Design

### Location Update API

```
POST /api/v1/location/update
{
  "user_id": "user_123",
  "user_type": "driver",
  "latitude": 37.7749,
  "longitude": -122.4194,
  "status": "available"
}
```

### Price Query API

```
GET /api/v1/pricing/estimate?latitude=37.7749&longitude=-122.4194&ride_type=standard
```

**Response:**
```json
{
  "base_price": 10.00,
  "surge_multiplier": 1.5,
  "final_price": 15.00,
  "hex_bin_id": "hex_abc123",
  "supply": 10,
  "demand": 15
}
```

---

## Stream Processing Pipeline

### Processing Flow

```
┌──────────┐         ┌──────────────┐         ┌──────────────┐
│ Location │────────▶│   Kafka      │────────▶│   Stream     │
│ Updates  │         │   Topic      │         │   Processor  │
└──────────┘         └──────────────┘         └──────┬───────┘
                                                      │
                                                      ▼
                                            ┌─────────────────┐
                                            │   Hex Bin       │
                                            │   Assignment    │
                                            └──────┬──────────┘
                                                   │
                                                   ▼
                                            ┌─────────────────┐
                                            │   Supply/Demand│
                                            │   Aggregation   │
                                            └──────┬──────────┘
                                                   │
                                                   ▼
                                            ┌─────────────────┐
                                            │   Surge         │
                                            │   Calculation   │
                                            └──────┬──────────┘
                                                   │
                                                   ▼
                                            ┌─────────────────┐
                                            │   Redis State   │
                                            │   Store          │
                                            └─────────────────┘
```

### Stream Processing (Apache Flink/Kafka Streams)

```python
class SurgeProcessor:
    def process_location_updates(self, location_stream):
        # Assign to hex bin
        hex_bin = self.get_hex_bin(location.lat, location.lng)
        
        # Update supply/demand
        if location.user_type == 'driver':
            self.update_supply(hex_bin, location.status)
        else:  # rider
            self.update_demand(hex_bin, location.status)
        
        # Calculate surge
        surge = self.calculate_surge(hex_bin)
        
        # Update state store
        self.update_surge_state(hex_bin, surge)
```

---

## Surge Calculation Algorithm

### Surge Formula

```python
def calculate_surge(supply, demand, base_supply_demand_ratio=1.0):
    if supply == 0:
        return 5.0  # Max surge
    
    supply_demand_ratio = supply / max(demand, 1)
    ratio_vs_base = base_supply_demand_ratio / supply_demand_ratio
    
    # Surge multiplier: 1.0x to 5.0x
    surge = min(5.0, max(1.0, ratio_vs_base))
    
    return surge
```

### Smoothing Algorithm

```python
def smooth_surge(hex_bin_id, surge_value):
    # Get adjacent bins
    adjacent_bins = self.get_adjacent_bins(hex_bin_id)
    
    # Calculate weighted average
    total_weight = 1.0
    weighted_sum = surge_value
    
    for adj_bin in adjacent_bins:
        adj_surge = self.get_surge(adj_bin)
        weight = 0.3  # Weight for adjacent bins
        total_weight += weight
        weighted_sum += adj_surge * weight
    
    smoothed_surge = weighted_sum / total_weight
    return smoothed_surge
```

---

## Real-time Updates

### WebSocket Updates

```python
class SurgeUpdateService:
    def notify_surge_change(self, hex_bin_id, new_surge):
        # Get all users in this hex bin
        users = self.get_users_in_bin(hex_bin_id)
        
        # Send WebSocket updates
        for user_id in users:
            self.send_update(user_id, {
                'hex_bin_id': hex_bin_id,
                'surge_multiplier': new_surge
            })
```

---

## Scalability Considerations

- **Horizontal Scaling**: Multiple stream processors
- **Kafka Partitioning**: Partition by hex_bin_id or geographic region
- **State Store Sharding**: Shard Redis by hex_bin_id
- **Geographic Partitioning**: Process regions independently

---

## Caching Strategy

- **Surge Cache**: Cache surge multipliers (Redis)
- **Location Cache**: Cache recent locations
- **Price Cache**: Cache price estimates

---

## Load Balancing

- **Geographic Routing**: Route by geographic region
- **Load-based**: Route to least-loaded processor

---

## Security

- **Authentication**: OAuth for drivers/riders
- **Rate Limiting**: Per user, per endpoint
- **Data Validation**: Validate location data

---

## Monitoring & Analytics

- **Surge Distribution**: Distribution of surge multipliers
- **Supply/Demand Ratio**: Average ratio across areas
- **Update Latency**: Time to calculate and update surge
- **Price Accuracy**: Comparison with actual demand

---

## Capacity Planning

- **Location Updates**: 1M/second
- **Active Drivers**: 100K
- **Active Riders**: 500K
- **Hex Bins**: 10K bins per city
- **Update Frequency**: Every 5 seconds

---

## Technology Stack

- **Stream Processing**: Apache Flink, Kafka Streams
- **Message Queue**: Kafka
- **State Store**: Redis, Redis Streams
- **Database**: Redis, Cassandra
- **Backend**: Go, Java

---

## Failure Scenarios & Handling

1. **Stream Processor Failure**: Auto-restart, state recovery
2. **State Store Failure**: Replication, failover
3. **High Update Rate**: Throttling, batching

---

## High-Level Design (HLD)

### System Overview

The surge pricing system follows a real-time stream processing architecture:

1. **Client Layer**: Driver and rider applications
2. **Location Service**: Receives location updates
3. **Stream Processing**: Processes location updates, calculates supply/demand
4. **Surge Calculator**: Calculates surge multipliers per geographic area
5. **State Store**: Redis for real-time surge data
6. **Distribution Layer**: WebSocket for real-time surge updates

### Component Architecture

**Core Components:**
- **Location Processor**: Processes location updates, assigns to hex bins
- **Supply/Demand Calculator**: Aggregates supply and demand per bin
- **Surge Calculator**: Calculates surge multipliers
- **Stream Manager**: Distributes surge updates via WebSocket

---

## Low-Level Design (LLD)

### Surge Calculator Implementation

```python
class SurgeCalculator:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.base_ratio = 1.0  # Base supply/demand ratio
    
    def calculate_surge(self, hex_bin_id: str) -> float:
        # Get supply and demand
        supply = self.get_supply(hex_bin_id)
        demand = self.get_demand(hex_bin_id)
        
        if supply == 0:
            return 5.0  # Max surge
        
        supply_demand_ratio = supply / max(demand, 1)
        ratio_vs_base = self.base_ratio / supply_demand_ratio
        
        # Surge multiplier: 1.0x to 5.0x
        surge = min(5.0, max(1.0, ratio_vs_base))
        
        # Smooth with adjacent bins
        smoothed_surge = self.smooth_surge(hex_bin_id, surge)
        
        # Update Redis
        self.redis.hset(f"surge:{hex_bin_id}", {
            'multiplier': smoothed_surge,
            'supply': supply,
            'demand': demand,
            'updated_at': time.time()
        })
        
        return smoothed_surge
    
    def smooth_surge(self, hex_bin_id: str, surge: float) -> float:
        # Get adjacent bins
        adjacent_bins = self.get_adjacent_bins(hex_bin_id)
        
        # Calculate weighted average
        total_weight = 1.0
        weighted_sum = surge
        
        for adj_bin in adjacent_bins:
            adj_surge_data = self.redis.hgetall(f"surge:{adj_bin}")
            if adj_surge_data:
                adj_surge = float(adj_surge_data.get('multiplier', 1.0))
                weight = 0.3  # Weight for adjacent bins
                total_weight += weight
                weighted_sum += adj_surge * weight
        
        return weighted_sum / total_weight
```

### Stream Processor Implementation

```python
class SurgeProcessor:
    def __init__(self, redis_client, kafka_consumer):
        self.redis = redis_client
        self.consumer = kafka_consumer
        self.surge_calculator = SurgeCalculator(redis_client)
    
    def process_location_update(self, location: dict):
        # Assign to hex bin
        hex_bin = self.get_hex_bin(location['latitude'], location['longitude'])
        
        # Update supply/demand
        if location['user_type'] == 'driver':
            self.update_supply(hex_bin, location['status'])
        else:  # rider
            self.update_demand(hex_bin, location['status'])
        
        # Calculate surge
        surge = self.surge_calculator.calculate_surge(hex_bin)
        
        # Publish surge update
        self.publish_surge_update(hex_bin, surge)
    
    def update_supply(self, hex_bin: str, status: str):
        supply_key = f"supply:{hex_bin}"
        if status == 'available':
            self.redis.incr(supply_key)
        elif status == 'offline' or status == 'on_trip':
            self.redis.decr(supply_key)
        self.redis.expire(supply_key, 300)  # 5 minutes TTL
```

---

## Fault Tolerance

### Stream Processing Resilience

**State Recovery:**
- Periodic state snapshots
- Recover from checkpoint on failure
- Replay events from Kafka

**Processor Failure:**
- Multiple processor instances
- Kafka consumer groups
- Automatic rebalancing

### State Store Resilience

**Redis Cluster:**
- Redis Cluster with replication
- Automatic failover
- Data sharded by hex_bin_id

---

## Optimizations

### Processing Optimization

**Batching:**
- Batch location updates
- Reduce Redis operations
- Improve throughput

**State Optimization:**
- Efficient state storage
- TTL-based expiration
- Compress state data

### Calculation Optimization

**Caching:**
- Cache surge calculations
- Cache adjacent bin data
- Reduce computation

---

## Failure Safety

### Stream Processor Failure

**Scenario: Processor Crashes**
- **Impact**: Surge not calculated
- **Mitigation**:
  - Multiple processor instances
  - State recovery from checkpoint
  - Replay from Kafka
- **Recovery**:
  - Processor recovers
  - Resume from checkpoint
  - Catch up on missed updates

### State Store Failure

**Scenario: Redis Cluster Down**
- **Impact**: Cannot update surge
- **Mitigation**:
  - Redis Cluster with replication
  - Fallback to database
  - Serve cached surge
- **Recovery**:
  - Redis recovers
  - Rebuild state from events
  - Resume normal operation

---

## Scalability

### Horizontal Scaling

**Processor Scaling:**
- Multiple processor instances
- Kafka partitions for parallel processing
- Scale independently

**State Store Scaling:**
- Redis Cluster with sharding
- Shard by geographic region
- Add shards as needed

### Performance Scaling

**Throughput Scaling:**
- Increase Kafka partitions
- Add more processor instances
- Optimize batch sizes

**Latency Optimization:**
- Reduce processing time
- Optimize Redis operations
- Use efficient algorithms

---

## Interview Discussion Points

1. **Stream Processing**: How do you process 1M+ updates/second?
2. **Surge Calculation**: How do you calculate surge in real-time?
3. **Geographic Partitioning**: How do you handle geographic areas?
4. **Smoothing**: How do you smooth surge across adjacent areas?

---

**Document Version**: 1.0  
**Last Updated**: January 2024

