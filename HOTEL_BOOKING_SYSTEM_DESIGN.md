# Hotel Booking System Design

## Table of Contents
1. [Overview](#overview)
2. [Requirements](#requirements)
3. [System Architecture](#system-architecture)
4. [Database Design](#database-design)
5. [API Design](#api-design)
6. [Room Availability Management](#room-availability-management)
7. [Reservation System](#reservation-system)
8. [Booking Process](#booking-process)
9. [Inventory Management](#inventory-management)
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

A hotel booking system that manages room availability, reservations, and bookings. The system must handle high concurrency, prevent overbooking, support multiple hotels, and provide real-time availability information.

**Key Features:**
- Room availability search
- Real-time inventory management
- Reservation and booking management
- Multi-hotel support
- Price management
- Payment processing
- Cancellation and refunds
- Check-in/check-out management

---

## Requirements

### Functional Requirements

1. **Room Availability**
   - Search rooms by location, dates, guests
   - Real-time availability
   - Filter by amenities, price, rating
   - Show room types and rates

2. **Reservation Management**
   - Create reservations
   - Hold reservations (temporary)
   - Confirm reservations
   - Cancel reservations

3. **Booking Management**
   - Create bookings
   - Process payments
   - Send confirmations
   - Manage check-in/check-out

4. **Inventory Management**
   - Track room availability by date
   - Handle room types and variants
   - Manage room blocks
   - Prevent overbooking

5. **Price Management**
   - Dynamic pricing
   - Seasonal rates
   - Promotional rates
   - Multi-currency support

6. **User Management**
   - User accounts
   - Booking history
   - Preferences
   - Loyalty programs

### Non-Functional Requirements

1. **Scalability**
   - Support 100K+ hotels
   - Handle 1M+ searches per day
   - Support millions of bookings
   - Horizontal scaling

2. **Performance**
   - Search latency: < 200ms
   - Booking creation: < 2 seconds
   - Availability check: < 50ms
   - 99th percentile latency < 500ms

3. **Availability**
   - 99.9% uptime
   - Prevent overbooking
   - Real-time inventory updates
   - Zero data loss

4. **Consistency**
   - Strong consistency for inventory
   - Prevent double booking
   - Accurate availability

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Applications                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │   Web    │  │  Mobile  │  │  Admin   │  │  Partner │     │
│  │   App    │  │   App    │  │  Portal  │  │   API    │     │
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
│              Application Services Layer                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Search  │  │Availability│ │ Booking  │  │ Payment  │   │
│  │ Service  │  │ Service  │  │ Service  │  │ Service  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │Inventory │  │  Price   │  │  User    │  │Notification│ │
│  │ Service  │  │ Service  │  │ Service  │  │ Service  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼───────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│              Caching Layer (Redis)                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Redis   │  │  Redis   │  │  Redis   │  │  Redis   │   │
│  │ Cluster  │  │ Cluster  │  │ Cluster  │  │ Cluster  │   │
│  │(Availability)│ │(Search) │ │(Locks)  │ │(Sessions)│   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼───────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│              Database Layer                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │PostgreSQL│  │PostgreSQL│  │Elasticsearch│ │  Kafka   │   │
│  │(Hotels)  │  │(Bookings)│  │  (Search) │  │(Events)  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼───────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│              External Services                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Payment  │  │  Email    │  │   SMS    │  │  Hotel    │   │
│  │ Gateway  │  │ Service  │  │ Service  │  │  PMS API  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Component Details

#### 1. Search Service
- **Responsibilities**:
  - Search hotels by location, dates
  - Filter and sort results
  - Integrate with Elasticsearch

#### 2. Availability Service
- **Responsibilities**:
  - Check room availability
  - Real-time inventory checks
  - Handle concurrent requests

#### 3. Inventory Service
- **Responsibilities**:
  - Manage room inventory
  - Track availability by date
  - Prevent overbooking

#### 4. Booking Service
- **Responsibilities**:
  - Create bookings
  - Process reservations
  - Manage booking lifecycle

#### 5. Payment Service
- **Responsibilities**:
  - Process payments
  - Handle refunds
  - Payment gateway integration

### HLD Component Breakdown

**1. Client Layer**
- **Web App**: React-based web application
- **Mobile Apps**: iOS/Android native apps
- **Admin Portal**: Hotel management portal
- **Partner API**: API for partners

**2. API Gateway Layer**
- **API Gateway**: Routes requests to services
- **Load Balancer**: Distributes traffic
- **CDN**: Serves static assets

**3. Service Layer**
- **Search Service**: Handles hotel search
- **Availability Service**: Checks room availability
- **Inventory Service**: Manages room inventory
- **Booking Service**: Creates and manages bookings
- **Payment Service**: Processes payments
- **Price Service**: Manages pricing

**4. Processing Layer**
- **Search Indexer**: Indexes hotels for search
- **Price Calculator**: Calculates prices
- **Notification Processor**: Processes notifications

**5. Data Layer**
- **PostgreSQL**: Hotels, bookings, orders
- **Elasticsearch**: Hotel search index
- **Redis**: Availability cache, locks, sessions

---

## Low-Level Design (LLD)

### Booking Service LLD

```python
class BookingService:
    def __init__(self, db: Database, inventory_service: InventoryService,
                 payment_service: PaymentService, lock_manager: LockManager,
                 event_publisher: EventPublisher):
        self.db = db
        self.inventory_service = inventory_service
        self.payment_service = payment_service
        self.lock_manager = lock_manager
        self.event_publisher = event_publisher
    
    def create_booking(self, reservation_id: str, payment_method_id: str,
                      guest_info: dict) -> Booking:
        # Get reservation
        reservation = Reservation.get(reservation_id)
        
        # Validate reservation
        if reservation.status != 'pending':
            raise InvalidReservationError()
        
        if reservation.expires_at < datetime.utcnow():
            raise ReservationExpiredError()
        
        # Acquire distributed lock
        lock_key = f"booking_lock:{reservation.hotel_id}:{reservation.room_type_id}"
        
        with self.lock_manager.acquire(lock_key, timeout=10):
            # Double-check availability
            if not self.inventory_service.check_availability(
                reservation.hotel_id,
                reservation.room_type_id,
                reservation.check_in_date,
                reservation.check_out_date,
                reservation.number_of_rooms
            ):
                raise InsufficientRoomsError()
            
            # Process payment
            payment_result = self.payment_service.process_payment(
                amount=reservation.total_price,
                payment_method_id=payment_method_id
            )
            
            if not payment_result.success:
                raise PaymentFailedError()
            
            # Create booking
            booking = Booking.create(
                reservation_id=reservation_id,
                hotel_id=reservation.hotel_id,
                room_type_id=reservation.room_type_id,
                user_id=reservation.user_id,
                check_in_date=reservation.check_in_date,
                check_out_date=reservation.check_out_date,
                total_price=reservation.total_price,
                payment_status='paid',
                payment_transaction_id=payment_result.transaction_id,
                guest_info=guest_info
            )
            
            # Convert reservation to booking (update inventory)
            self.inventory_service.confirm_reservation(reservation)
            
            # Update reservation status
            reservation.status = 'confirmed'
            reservation.save()
            
            # Publish event
            self.event_publisher.publish('booking.created', {
                'booking_id': booking.id,
                'hotel_id': reservation.hotel_id,
                'total_price': reservation.total_price
            })
            
            return booking
```

### Inventory Service LLD

```python
class InventoryService:
    def __init__(self, db: Database, cache: RedisCache, lock_manager: LockManager):
        self.db = db
        self.cache = cache
        self.lock_manager = lock_manager
    
    def check_availability(self, hotel_id: int, room_type_id: int,
                          check_in: date, check_out: date, num_rooms: int) -> bool:
        # Check cache first
        cache_key = f"availability:{hotel_id}:{room_type_id}:{check_in}"
        cached = self.cache.get(cache_key)
        
        if cached is not None:
            return int(cached) >= num_rooms
        
        # Query database
        dates = self._get_dates_between(check_in, check_out)
        
        for date in dates:
            availability = self.db.query("""
                SELECT available_rooms FROM room_availability
                WHERE hotel_id = %s AND room_type_id = %s AND date = %s
            """, (hotel_id, room_type_id, date))
            
            if not availability or availability.available_rooms < num_rooms:
                return False
        
        return True
    
    def reserve_rooms(self, hotel_id: int, room_type_id: int, check_in: date,
                     check_out: date, num_rooms: int) -> bool:
        lock_key = f"inventory_lock:{hotel_id}:{room_type_id}"
        
        with self.lock_manager.acquire(lock_key, timeout=10):
            dates = self._get_dates_between(check_in, check_out)
            
            # Check availability for all dates
            for date in dates:
                availability = self.db.query("""
                    SELECT available_rooms FROM room_availability
                    WHERE hotel_id = %s AND room_type_id = %s AND date = %s
                    FOR UPDATE
                """, (hotel_id, room_type_id, date))
                
                if not availability or availability.available_rooms < num_rooms:
                    return False
            
            # Reserve rooms (atomic update)
            for date in dates:
                self.db.execute("""
                    UPDATE room_availability
                    SET available_rooms = available_rooms - %s,
                        reserved_rooms = reserved_rooms + %s
                    WHERE hotel_id = %s AND room_type_id = %s AND date = %s
                """, (num_rooms, num_rooms, hotel_id, room_type_id, date))
                
                # Invalidate cache
                self.cache.delete(f"availability:{hotel_id}:{room_type_id}:{date}")
            
            return True
```

### Search Service LLD

```python
class SearchService:
    def __init__(self, elasticsearch: ElasticsearchClient, cache: RedisCache,
                 availability_service: AvailabilityService):
        self.es = elasticsearch
        self.cache = cache
        self.availability_service = availability_service
    
    def search_hotels(self, location: str, check_in: date, check_out: date,
                     guests: int, filters: dict = None) -> SearchResult:
        # Generate cache key
        cache_key = self._generate_cache_key(location, check_in, check_out, guests, filters)
        
        # Check cache
        cached = self.cache.get(cache_key)
        if cached:
            return SearchResult.from_dict(cached)
        
        # Build Elasticsearch query
        es_query = {
            'bool': {
                'must': [
                    {
                        'geo_distance': {
                            'distance': '50km',
                            'location': self._geocode_location(location)
                        }
                    }
                ],
                'filter': self._build_filters(filters)
            }
        }
        
        # Execute search
        response = self.es.search(
            index='hotels',
            body={
                'query': es_query,
                'size': 50
            }
        )
        
        # Process results and check availability
        hotels = []
        for hit in response['hits']['hits']:
            hotel = self._parse_hit(hit)
            
            # Check availability
            available_rooms = self.availability_service.check_availability_for_hotel(
                hotel.id, check_in, check_out, guests
            )
            
            if available_rooms:
                hotel.available_room_types = available_rooms
                hotels.append(hotel)
        
        result = SearchResult(hotels=hotels, total=len(hotels))
        
        # Cache result
        self.cache.set(cache_key, result.to_dict(), ttl=300)  # 5 minutes
        
        return result
```

---

## Fault Tolerance

### Booking Processing Fault Tolerance

**1. Distributed Locking**
- **Redis Locks**: Prevent race conditions
- **Lock Timeout**: 10-second timeout
- **Lock Retry**: Retry with exponential backoff
- **Deadlock Prevention**: Order locks consistently

**2. Payment Processing Resilience**
- **Idempotency**: Make payment operations idempotent
- **Retry Logic**: Retry failed payments
- **Compensation**: Cancel booking if payment fails
- **Multiple Gateways**: Failover to secondary gateway

**3. Inventory Consistency**
- **Atomic Updates**: Use database transactions
- **Optimistic Locking**: Version-based locking
- **Pessimistic Locking**: Row-level locks (FOR UPDATE)
- **Reconciliation**: Periodic reconciliation

---

## Failure Safety

### Failure Scenarios & Handling

**1. Overbooking**

**Scenario**: Multiple users book same room simultaneously.

**Impact**: Overbooking, customer dissatisfaction.

**Mitigation**:
- **Distributed Locks**: Lock during booking
- **Atomic Updates**: Use database transactions
- **Optimistic Locking**: Version-based locking
- **Pessimistic Locking**: Row-level locks

**Recovery**:
- **Compensation**: Offer alternative rooms
- **Refund**: Refund if no alternatives
- **Upgrade**: Upgrade to better room
- **Manual Intervention**: Manual resolution

**2. Payment Failure**

**Scenario**: Payment gateway fails during booking.

**Impact**: Booking created but payment failed.

**Mitigation**:
- **Two-Phase Commit**: Reserve first, charge second
- **Compensation**: Cancel booking if payment fails
- **Retry Logic**: Retry payment with exponential backoff
- **Multiple Gateways**: Failover to secondary gateway

**Recovery**:
- **Payment Retry**: Retry payment automatically
- **Manual Processing**: Manual payment processing
- **Booking Cancellation**: Cancel booking if payment fails

**3. Inventory Inconsistency**

**Scenario**: Cache and database out of sync.

**Impact**: Show incorrect availability.

**Mitigation**:
- **Cache Invalidation**: Invalidate on updates
- **Reconciliation Job**: Periodic reconciliation
- **Database as Source of Truth**: Always verify with database
- **Version Numbers**: Use version numbers for consistency

**Recovery**:
- **Cache Refresh**: Refresh cache from database
- **State Reconciliation**: Reconcile inventory state
- **Manual Fix**: Manual intervention if needed

**4. Search Service Failure**

**Scenario**: Elasticsearch cluster fails.

**Impact**: Cannot search hotels.

**Mitigation**:
- **Elasticsearch Cluster**: Multiple nodes with replication
- **Database Fallback**: Fallback to database search
- **Cached Results**: Serve cached search results
- **Circuit Breaker**: Prevent cascading failures

**Recovery**:
- **Cluster Recovery**: Restart failed nodes
- **Index Recovery**: Rebuild indices from database
- **Cache Warming**: Pre-populate cache

---

## Scalability Considerations

### 1. Horizontal Scaling

**Service Scaling:**
- **Stateless Services**: All services are stateless
- **Scale Horizontally**: Add instances as needed
- **Load Balancer**: Distribute traffic
- **Auto-Scaling**: Scale based on CPU/memory/request rate

**Scaling Metrics:**
- **Search Service**: 500 queries/s per instance
- **Booking Service**: 100 bookings/s per instance
- **Availability Service**: 1000 checks/s per instance

### 2. Database Scaling

**PostgreSQL Scaling:**
- **Read Replicas**: 3-5 read replicas for reads
- **Sharding**: Shard by hotel_id or location
- **Partitioning**: Partition availability table by date
- **Connection Pooling**: PgBouncer for connection pooling

**Elasticsearch Scaling:**
- **Cluster Mode**: Deploy Elasticsearch cluster
- **Sharding**: Shard indices by location
- **Replication**: Replicate indices
- **Index Optimization**: Optimize indices for performance

### 3. Caching Strategy

**Multi-Level Caching:**
- **Redis**: Availability counts (TTL: 1 minute)
- **Redis**: Search results (TTL: 5 minutes)
- **CDN**: Static assets, hotel images

**Cache Invalidation:**
- **Event-Based**: Invalidate on booking/reservation
- **TTL-Based**: Short TTL for availability (1 minute)
- **Manual**: Manual invalidation if needed

### 4. Inventory Management Scaling

**Concurrent Booking Prevention:**
- **Distributed Locks**: Lock per hotel/room_type/date
- **Atomic Operations**: Database-level atomic updates
- **Lock Ordering**: Consistent lock ordering
- **Lock Timeout**: Prevent deadlocks

**Performance Targets:**
- **Availability Check**: < 50ms (p95)
- **Booking Creation**: < 2s (p95)
- **Search Latency**: < 200ms (p95)

---

## Database Design

### PostgreSQL Schema

#### Hotels Table
```sql
CREATE TABLE hotels (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    rating DECIMAL(3, 2),
    amenities JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_city (city),
    INDEX idx_country (country),
    INDEX idx_location (latitude, longitude),
    FULLTEXT idx_search (name, address)
) ENGINE=InnoDB;
```

#### Room Types Table
```sql
CREATE TABLE room_types (
    id BIGSERIAL PRIMARY KEY,
    hotel_id BIGINT NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    max_occupancy INT NOT NULL,
    amenities JSONB,
    base_price DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (hotel_id) REFERENCES hotels(id) ON DELETE CASCADE,
    INDEX idx_hotel_id (hotel_id)
) ENGINE=InnoDB;
```

#### Rooms Table
```sql
CREATE TABLE rooms (
    id BIGSERIAL PRIMARY KEY,
    hotel_id BIGINT NOT NULL,
    room_type_id BIGINT NOT NULL,
    room_number VARCHAR(50),
    floor_number INT,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (hotel_id) REFERENCES hotels(id) ON DELETE CASCADE,
    FOREIGN KEY (room_type_id) REFERENCES room_types(id),
    INDEX idx_hotel_id (hotel_id),
    INDEX idx_room_type_id (room_type_id)
) ENGINE=InnoDB;
```

#### Room Availability Table
```sql
CREATE TABLE room_availability (
    id BIGSERIAL PRIMARY KEY,
    hotel_id BIGINT NOT NULL,
    room_type_id BIGINT NOT NULL,
    date DATE NOT NULL,
    total_rooms INT NOT NULL,
    available_rooms INT NOT NULL,
    reserved_rooms INT NOT NULL DEFAULT 0,
    booked_rooms INT NOT NULL DEFAULT 0,
    blocked_rooms INT NOT NULL DEFAULT 0,  -- Maintenance, etc.
    UNIQUE KEY unique_hotel_room_date (hotel_id, room_type_id, date),
    FOREIGN KEY (hotel_id) REFERENCES hotels(id),
    FOREIGN KEY (room_type_id) REFERENCES room_types(id),
    INDEX idx_date (date),
    INDEX idx_hotel_date (hotel_id, date)
) ENGINE=InnoDB;
```

#### Reservations Table
```sql
CREATE TABLE reservations (
    id BIGSERIAL PRIMARY KEY,
    reservation_number VARCHAR(50) UNIQUE NOT NULL,
    hotel_id BIGINT NOT NULL,
    room_type_id BIGINT NOT NULL,
    user_id BIGINT,
    check_in_date DATE NOT NULL,
    check_out_date DATE NOT NULL,
    number_of_guests INT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',  -- 'pending', 'confirmed', 'cancelled', 'expired'
    total_price DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    expires_at TIMESTAMP,  -- For temporary reservations
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (hotel_id) REFERENCES hotels(id),
    FOREIGN KEY (room_type_id) REFERENCES room_types(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_dates (check_in_date, check_out_date),
    INDEX idx_expires_at (expires_at)
) ENGINE=InnoDB;
```

#### Bookings Table
```sql
CREATE TABLE bookings (
    id BIGSERIAL PRIMARY KEY,
    booking_number VARCHAR(50) UNIQUE NOT NULL,
    reservation_id BIGINT,
    hotel_id BIGINT NOT NULL,
    room_type_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    check_in_date DATE NOT NULL,
    check_out_date DATE NOT NULL,
    number_of_guests INT NOT NULL,
    status VARCHAR(20) DEFAULT 'confirmed',  -- 'confirmed', 'checked_in', 'checked_out', 'cancelled'
    total_price DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    payment_status VARCHAR(20) DEFAULT 'pending',  -- 'pending', 'paid', 'refunded'
    payment_transaction_id VARCHAR(255),
    guest_info JSONB,
    special_requests TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (reservation_id) REFERENCES reservations(id),
    FOREIGN KEY (hotel_id) REFERENCES hotels(id),
    FOREIGN KEY (room_type_id) REFERENCES room_types(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_dates (check_in_date, check_out_date),
    INDEX idx_booking_number (booking_number)
) ENGINE=InnoDB;
```

#### Booking Rooms Table (Many-to-Many)
```sql
CREATE TABLE booking_rooms (
    id BIGSERIAL PRIMARY KEY,
    booking_id BIGINT NOT NULL,
    room_id BIGINT NOT NULL,
    check_in_date DATE NOT NULL,
    check_out_date DATE NOT NULL,
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE,
    FOREIGN KEY (room_id) REFERENCES rooms(id),
    UNIQUE KEY unique_booking_room (booking_id, room_id),
    INDEX idx_room_dates (room_id, check_in_date, check_out_date)
) ENGINE=InnoDB;
```

### Redis Schema

#### Availability Cache
```
Key: availability:{hotel_id}:{room_type_id}:{date}
Type: String (Integer)
Value: Available rooms count
TTL: 5 minutes
```

#### Reservation Lock
```
Key: reservation_lock:{hotel_id}:{room_type_id}:{date}
Type: String
Value: reservation_id
TTL: 15 minutes (reservation hold time)
```

#### Booking Lock
```
Key: booking_lock:{hotel_id}:{room_type_id}:{date}
Type: String
Value: booking_id
TTL: 5 minutes
```

---

## API Design

### Search APIs

**Search Hotels**
```
GET /api/v1/hotels/search?location=San+Francisco&check_in=2024-02-01&check_out=2024-02-03&guests=2

Response:
{
    "hotels": [
        {
            "hotel_id": "hotel_123",
            "name": "Grand Hotel",
            "location": "San Francisco, CA",
            "rating": 4.5,
            "available_room_types": [
                {
                    "room_type_id": "type_1",
                    "name": "Deluxe Room",
                    "price": 150.00,
                    "available_rooms": 5,
                    "max_occupancy": 2
                }
            ],
            "distance_km": 2.5
        }
    ],
    "total_results": 50,
    "pagination": {...}
}
```

### Availability APIs

**Check Availability**
```
POST /api/v1/availability/check
Content-Type: application/json

Request:
{
    "hotel_id": "hotel_123",
    "room_type_id": "type_1",
    "check_in_date": "2024-02-01",
    "check_out_date": "2024-02-03",
    "number_of_rooms": 1
}

Response:
{
    "available": true,
    "available_rooms": 5,
    "price_per_night": 150.00,
    "total_price": 300.00,
    "currency": "USD"
}
```

### Reservation APIs

**Create Reservation**
```
POST /api/v1/reservations
Content-Type: application/json

Request:
{
    "hotel_id": "hotel_123",
    "room_type_id": "type_1",
    "check_in_date": "2024-02-01",
    "check_out_date": "2024-02-03",
    "number_of_guests": 2,
    "number_of_rooms": 1
}

Response:
{
    "success": true,
    "reservation_id": "res_12345",
    "reservation_number": "RES-2024-001234",
    "status": "pending",
    "expires_at": "2024-01-15T10:45:00Z",
    "total_price": 300.00
}
```

### Booking APIs

**Create Booking**
```
POST /api/v1/bookings
Content-Type: application/json

Request:
{
    "reservation_id": "res_12345",
    "payment_method_id": "pm_123",
    "guest_info": {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "phone": "+1234567890"
    }
}

Response:
{
    "success": true,
    "booking_id": "book_12345",
    "booking_number": "BK-2024-001234",
    "status": "confirmed",
    "payment_status": "paid",
    "check_in_date": "2024-02-01",
    "check_out_date": "2024-02-03",
    "total_price": 300.00
}
```

**Get Booking**
```
GET /api/v1/bookings/{booking_id}

Response:
{
    "booking_id": "book_12345",
    "booking_number": "BK-2024-001234",
    "hotel": {
        "name": "Grand Hotel",
        "address": "123 Main St, San Francisco, CA"
    },
    "room_type": {
        "name": "Deluxe Room"
    },
    "check_in_date": "2024-02-01",
    "check_out_date": "2024-02-03",
    "status": "confirmed",
    "total_price": 300.00
}
```

---

## Data Flow Diagrams

### Search Flow

```
User Searches Hotels
    │
    ▼
Search Service
    │
    ├─ Parse Search Parameters
    ├─ Check Cache (Redis)
    │   └─ Cache Hit → Return (10-20ms)
    │
    └─ Cache Miss → Continue
        │
        ▼
    Query Elasticsearch
        │
        ├─ Search by Location
        ├─ Filter by Dates
        └─ Filter by Amenities
        │
        ▼
    For Each Hotel:
        │
        ├─ Check Availability (Redis)
        │   └─ availability:{hotel_id}:{room_type}:{date}
        │
        └─ If Cache Miss → Query Database
            │
            └─ Cache Result
        │
        ▼
    Filter Available Hotels
        │
        ▼
    Cache Search Results
        │
        ▼
    Return Results
```

### Booking Flow

```
User Creates Booking
    │
    ▼
Booking Service
    │
    ├─ Validate Reservation
    ├─ Check Availability (Again)
    │
    ▼
Acquire Distributed Lock
    │
    └─ Lock Key: booking_lock:{hotel_id}:{room_type_id}:{date}
    │
    ▼
Check Availability (Atomic)
    │
    ├─ Query: SELECT available_rooms FROM room_availability
    │   WHERE hotel_id=? AND room_type_id=? AND date BETWEEN ? AND ?
    │
    └─ Verify: available_rooms >= number_of_rooms
    │
    ▼
If Available:
    │
    ├─ Reserve Rooms (Atomic Update)
    │   │
    │   └─ UPDATE room_availability
    │       SET available_rooms = available_rooms - ?,
    │           reserved_rooms = reserved_rooms + ?
    │       WHERE hotel_id=? AND room_type_id=? AND date BETWEEN ? AND ?
    │
    ├─ Create Booking Record
    │   │
    │   └─ INSERT INTO bookings (...)
    │
    ├─ Process Payment
    │   │
    │   ▼
    │   Payment Service
    │   │
    │   ├─ Charge Payment Gateway
    │   └─ Update Payment Status
    │
    ├─ Update Inventory (Release Reservation)
    │   │
    │   └─ UPDATE room_availability
    │       SET reserved_rooms = reserved_rooms - ?,
    │           booked_rooms = booked_rooms + ?
    │
    ├─ Release Lock
    │
    └─ Publish Booking Event (Kafka)
        │
        ├─ Notification Service (Email Confirmation)
        ├─ Inventory Service (Update Cache)
        └─ Analytics Service (Record Metrics)
        │
        ▼
    Return Booking Confirmation
```

---

## Room Availability Management

### Availability Tracking

**Daily Availability:**
- Track availability per room type per date
- Separate counters: total, available, reserved, booked, blocked
- Atomic updates to prevent race conditions

**Implementation:**
```python
class InventoryService:
    @transactional
    def reserve_rooms(self, hotel_id, room_type_id, check_in, check_out, num_rooms):
        # Acquire lock
        lock_key = f"inventory_lock:{hotel_id}:{room_type_id}"
        with redis.lock(lock_key, timeout=10):
            # Check availability for all dates
            dates = self.get_dates_between(check_in, check_out)
            for date in dates:
                availability = self.get_availability(hotel_id, room_type_id, date)
                if availability['available_rooms'] < num_rooms:
                    raise InsufficientRoomsError()
            
            # Reserve rooms (atomic update)
            for date in dates:
                self.update_availability(
                    hotel_id, room_type_id, date,
                    reserved_delta=num_rooms,
                    available_delta=-num_rooms
                )
            
            return True
    
    def update_availability(self, hotel_id, room_type_id, date, 
                           reserved_delta=0, available_delta=0, booked_delta=0):
        # Atomic update using SQL
        sql = """
        UPDATE room_availability
        SET available_rooms = available_rooms + %s,
            reserved_rooms = reserved_rooms + %s,
            booked_rooms = booked_rooms + %s
        WHERE hotel_id = %s AND room_type_id = %s AND date = %s
        """
        db.execute(sql, (available_delta, reserved_delta, booked_delta, 
                        hotel_id, room_type_id, date))
        
        # Update cache
        cache_key = f"availability:{hotel_id}:{room_type_id}:{date}"
        redis.delete(cache_key)  # Invalidate cache
```

### Overbooking Prevention

**Challenge:** Prevent selling more rooms than available.

**Solutions:**
- **Distributed Locks**: Lock during availability check and update
- **Atomic Updates**: Use database transactions
- **Optimistic Locking**: Version-based locking
- **Pessimistic Locking**: Row-level locks

**Implementation:**
```python
def book_rooms_atomic(hotel_id, room_type_id, check_in, check_out, num_rooms):
    # Use database transaction with row locks
    with db.transaction():
        # Lock rows for update
        availability_rows = db.execute("""
            SELECT * FROM room_availability
            WHERE hotel_id = %s AND room_type_id = %s 
            AND date BETWEEN %s AND %s
            FOR UPDATE
        """, (hotel_id, room_type_id, check_in, check_out))
        
        # Check availability
        for row in availability_rows:
            if row['available_rooms'] < num_rooms:
                raise InsufficientRoomsError()
        
        # Update availability
        db.execute("""
            UPDATE room_availability
            SET available_rooms = available_rooms - %s,
                booked_rooms = booked_rooms + %s
            WHERE hotel_id = %s AND room_type_id = %s 
            AND date BETWEEN %s AND %s
        """, (num_rooms, num_rooms, hotel_id, room_type_id, check_in, check_out))
```

---

## Reservation System

### Reservation Types

**1. Temporary Reservation (Hold):**
- Hold rooms for 15 minutes
- User completes booking
- Auto-expires if not confirmed

**2. Confirmed Reservation:**
- Rooms reserved until check-in
- Can be cancelled
- Converted to booking on payment

### Reservation Lifecycle

```
Reservation Created (Pending)
    │
    ├─ Expires (15 min) → Released
    │
    └─ User Confirms → Booking Created
        │
        └─ Reservation Released
```

**Implementation:**
```python
class ReservationService:
    def create_reservation(self, hotel_id, room_type_id, check_in, check_out):
        # Reserve rooms temporarily
        self.inventory_service.reserve_rooms(
            hotel_id, room_type_id, check_in, check_out, 1
        )
        
        # Create reservation record
        reservation = Reservation.create(
            hotel_id=hotel_id,
            room_type_id=room_type_id,
            check_in_date=check_in,
            check_out_date=check_out,
            status='pending',
            expires_at=datetime.now() + timedelta(minutes=15)
        )
        
        # Schedule expiration job
        self.schedule_expiration(reservation.id, minutes=15)
        
        return reservation
    
    def expire_reservation(self, reservation_id):
        reservation = Reservation.get(reservation_id)
        if reservation.status == 'pending':
            # Release rooms
            self.inventory_service.release_reservation(
                reservation.hotel_id,
                reservation.room_type_id,
                reservation.check_in_date,
                reservation.check_out_date
            )
            
            # Update status
            reservation.status = 'expired'
            reservation.save()
```

---

## Booking Process

### Booking Steps

1. **Search**: User searches hotels
2. **Select**: User selects hotel and room
3. **Reserve**: System creates temporary reservation
4. **Payment**: User provides payment details
5. **Confirm**: System processes payment and creates booking
6. **Confirmation**: Send confirmation email

### Payment Processing

**Payment Flow:**
```python
class BookingService:
    def create_booking(self, reservation_id, payment_method_id, guest_info):
        reservation = Reservation.get(reservation_id)
        
        # Validate reservation
        if reservation.status != 'pending':
            raise InvalidReservationError()
        
        if reservation.expires_at < datetime.now():
            raise ReservationExpiredError()
        
        # Process payment
        payment_result = self.payment_service.process_payment(
            amount=reservation.total_price,
            payment_method_id=payment_method_id
        )
        
        if not payment_result.success:
            raise PaymentFailedError()
        
        # Create booking
        booking = Booking.create(
            reservation_id=reservation_id,
            hotel_id=reservation.hotel_id,
            room_type_id=reservation.room_type_id,
            check_in_date=reservation.check_in_date,
            check_out_date=reservation.check_out_date,
            total_price=reservation.total_price,
            payment_status='paid',
            payment_transaction_id=payment_result.transaction_id,
            guest_info=guest_info
        )
        
        # Convert reservation to booking (update inventory)
        self.inventory_service.convert_reservation_to_booking(
            reservation.hotel_id,
            reservation.room_type_id,
            reservation.check_in_date,
            reservation.check_out_date
        )
        
        # Update reservation status
        reservation.status = 'confirmed'
        reservation.save()
        
        # Send confirmation
        self.notification_service.send_booking_confirmation(booking)
        
        return booking
```

---

## Inventory Management

### Inventory Updates

**Update Triggers:**
- New booking created
- Booking cancelled
- Check-in (assign room)
- Check-out (release room)
- Room block (maintenance)

**Implementation:**
```python
class InventoryService:
    def update_inventory_on_booking(self, booking):
        dates = self.get_dates_between(
            booking.check_in_date,
            booking.check_out_date
        )
        
        for date in dates:
            self.update_availability(
                hotel_id=booking.hotel_id,
                room_type_id=booking.room_type_id,
                date=date,
                booked_delta=1,
                reserved_delta=-1  # Release reservation
            )
    
    def update_inventory_on_cancellation(self, booking):
        dates = self.get_dates_between(
            booking.check_in_date,
            booking.check_out_date
        )
        
        for date in dates:
            self.update_availability(
                hotel_id=booking.hotel_id,
                room_type_id=booking.room_type_id,
                date=date,
                booked_delta=-1,
                available_delta=1  # Make available again
            )
```

---

## Scalability Considerations

### 1. Horizontal Scaling

**Services:**
- Stateless services
- Scale horizontally
- Load balancer distributes traffic

**Database:**
- Read replicas for reads
- Sharding by hotel_id for writes

### 2. Availability Search Optimization

**Caching:**
- Cache availability by hotel/room_type/date
- Cache search results
- Invalidate on booking/reservation

**Pre-computation:**
- Pre-compute availability for popular dates
- Batch updates

### 3. Concurrent Booking Prevention

**Distributed Locks:**
- Lock per hotel/room_type/date
- Atomic operations
- Prevent race conditions

---

## Caching Strategy

### Cache Architecture

```
Search Request
    │
    ▼
Redis Cache (Search Results)
    │
    ├─ Cache Hit → Return (10-20ms)
    │
    └─ Cache Miss → Query Database
        │
        └─ Cache Results
```

### Cache Keys

```
search:{location}:{check_in}:{check_out}:{guests} → Search results
availability:{hotel_id}:{room_type_id}:{date} → Availability count
hotel:{hotel_id} → Hotel details
```

### Cache Invalidation

**Event-Based:**
- Invalidate on booking creation
- Invalidate on cancellation
- Invalidate on inventory update

**TTL-Based:**
- Search results: 5 minutes
- Availability: 1 minute
- Hotel details: 1 hour

---

## Load Balancing

### Load Balancer Architecture

```
Booking Requests
    │
    ▼
Load Balancer
    │
    ├─ Booking Service 1
    ├─ Booking Service 2
    ├─ Booking Service 3
    └─ Booking Service N
```

### Load Balancing Strategies

1. **Round-Robin**: Equal distribution
2. **Least Connections**: Route to server with fewest connections
3. **Consistent Hashing**: Route by hotel_id (for local caching)

---

## Security

### 1. Payment Security

**PCI-DSS Compliance:**
- Don't store raw card data
- Use tokenization
- Encrypt payment data

### 2. Booking Security

**Prevent Fraud:**
- Validate user identity
- Rate limiting per user
- Monitor for suspicious patterns

---

## Monitoring & Analytics

### Key Metrics

**Performance Metrics:**
- Search latency
- Booking creation latency
- Availability check latency

**Business Metrics:**
- Bookings per day
- Cancellation rate
- Occupancy rate
- Revenue

---

## Deployment Strategy

### Infrastructure

**Cloud Provider**: AWS, GCP, or Azure

**Components:**
- **Compute**: Kubernetes (EKS/GKE)
- **Database**: PostgreSQL (RDS)
- **Search**: Elasticsearch (OpenSearch)
- **Cache**: Redis (ElastiCache)

---

## Capacity Planning

### Storage Estimates

**Bookings:**
- 1M bookings/day × 365 days = 365M bookings/year
- 365M × 2 KB = 730 GB/year

**Availability:**
- 100K hotels × 10 room types × 365 days = 365M records
- 365M × 200 bytes = 73 GB

**Total Storage: ~800 GB/year**

### Compute Requirements

**Search Service:**
- 1M searches/day = 12 searches/sec average
- Peak: 12 × 10 = 120 searches/sec
- Each search: ~100ms (with caching)
- Required servers: 120 / (1000/100) = 12 servers

**Booking Service:**
- 1M bookings/day = 12 bookings/sec average
- Peak: 12 × 10 = 120 bookings/sec
- Each booking: ~2 seconds (payment processing)
- Required servers: 120 × 2 = 240 servers

---

## Technology Stack

### Recommended Stack

**Compute:**
- **Language**: Java or Go
- **Orchestration**: Kubernetes

**Database:**
- **PostgreSQL** (RDS)

**Search:**
- **Elasticsearch** (OpenSearch)

**Cache:**
- **Redis** (ElastiCache)

**Payment:**
- **Stripe** or **PayPal**

---

## Failure Scenarios & Handling

### 1. Overbooking

**Scenario:** Multiple users book same room simultaneously.

**Impact:** Overbooking, customer dissatisfaction.

**Mitigation:**
- **Distributed Locks**: Lock during booking
- **Atomic Updates**: Use database transactions
- **Optimistic Locking**: Version-based locking

### 2. Payment Failure

**Scenario:** Payment gateway fails during booking.

**Impact:** Booking created but payment failed.

**Mitigation:**
- **Two-Phase Commit**: Reserve first, charge second
- **Compensation**: Cancel booking if payment fails
- **Retry Logic**: Retry payment with exponential backoff

### 3. Inventory Inconsistency

**Scenario:** Cache and database out of sync.

**Impact:** Show incorrect availability.

**Mitigation:**
- **Cache Invalidation**: Invalidate on updates
- **Reconciliation Job**: Periodic reconciliation
- **Database as Source of Truth**: Always verify with database

---

## Trade-offs & Design Decisions

### 1. Availability: Real-time vs Cached

**Decision:** Cached with frequent updates.

**Trade-offs:**

| Approach | Pros | Cons |
|----------|------|------|
| **Real-time** | Always accurate | Higher load |
| **Cached** | Lower load | Slight delay |

**Why Cached:**
- **Performance**: Sub-second response needed
- **Acceptable**: 1-minute cache is acceptable

### 2. Overbooking: Allow vs Prevent

**Decision:** Prevent overbooking (strict enforcement).

**Trade-offs:**

| Approach | Pros | Cons |
|----------|------|------|
| **Prevent** | No customer issues | May reject valid bookings |
| **Allow** | Higher revenue | Customer dissatisfaction |

**Why Prevent:**
- **Customer Trust**: Overbooking damages reputation
- **Legal**: May have legal implications

### 3. Reservation: Hold vs No Hold

**Decision:** Temporary hold (15 minutes).

**Trade-offs:**

| Approach | Pros | Cons |
|----------|------|------|
| **Hold** | Better UX | Inventory locked |
| **No Hold** | No lock | Race conditions |

**Why Hold:**
- **User Experience**: Users need time to complete booking
- **Acceptable**: 15 minutes is reasonable

---

## Interview Discussion Points

### Key Questions to Address

1. **"How do you prevent overbooking?"**
   - **Answer**: 
     - Distributed locks during booking
     - Atomic database updates
     - Row-level locking (FOR UPDATE)
     - Optimistic locking with version numbers

2. **"How do you handle concurrent bookings?"**
   - **Answer**:
     - Distributed locks per hotel/room_type/date
     - Atomic check-and-reserve operations
     - Database transactions
     - Proper ordering

3. **"How do you ensure availability accuracy?"**
   - **Answer**:
     - Cache invalidation on updates
     - Database as source of truth
     - Periodic reconciliation
     - Real-time updates

4. **"How do you handle payment failures?"**
   - **Answer**:
     - Two-phase commit (reserve then charge)
     - Compensation transactions (cancel if payment fails)
     - Retry logic with exponential backoff
     - Manual intervention capability

5. **"How do you scale search?"**
   - **Answer**:
     - Elasticsearch for full-text search
     - Aggressive caching
     - Pre-compute popular searches
     - Shard by location

---

## References

- [E-Commerce System Design](design/ECOMMERCE_SYSTEM_DESIGN.md)
- [System Design Primer](https://github.com/donnemartin/system-design-primer)
- [Booking.com Architecture](http://highscalability.com/blog/2013/10/21/bookingcom-scaling-agile-beyond-a-single-team.html)

