# Uber System Design Document

## Table of Contents
1. [Overview](#overview)
2. [Requirements](#requirements)
3. [System Architecture](#system-architecture)
4. [Database Design](#database-design)
5. [API Design](#api-design)
6. [Real-Time Location Tracking](#real-time-location-tracking)
7. [Ride Matching System](#ride-matching-system)
8. [Dynamic Pricing (Surge Pricing)](#dynamic-pricing-surge-pricing)
9. [Route Optimization](#route-optimization)
10. [Payment Processing](#payment-processing)
11. [Notification System](#notification-system)
12. [Scalability Considerations](#scalability-considerations)
13. [Caching Strategy](#caching-strategy)
14. [Load Balancing](#load-balancing)
15. [Security](#security)
16. [Monitoring & Analytics](#monitoring--analytics)
17. [Deployment Strategy](#deployment-strategy)
18. [Capacity Planning](#capacity-planning)
19. [Technology Stack](#technology-stack)
20. [Failure Scenarios & Handling](#failure-scenarios--handling)
21. [Trade-offs & Design Decisions](#trade-offs--design-decisions)
22. [Interview Discussion Points](#interview-discussion-points)

---

## Overview

Uber is a ride-sharing platform that connects riders with drivers in real-time. The system must handle millions of concurrent users, match riders with nearby drivers, calculate optimal routes, implement dynamic pricing, and process payments securely.

**Key Features:**
- Real-time location tracking (GPS)
- Driver-rider matching
- Dynamic pricing (surge pricing)
- Route optimization and navigation
- Payment processing
- Real-time notifications
- Trip history and ratings
- Multi-city support
- Driver earnings management
- Safety features

---

## Requirements

### Functional Requirements

1. **User Management**
   - Rider registration and authentication
   - Driver registration and verification
   - User profiles
   - Payment methods management
   - Trip history

2. **Location Services**
   - Real-time GPS tracking
   - Location updates (every 4-5 seconds)
   - Geocoding (address to coordinates)
   - Reverse geocoding (coordinates to address)
   - Location history

3. **Ride Matching**
   - Find nearby available drivers
   - Match rider with best driver
   - Driver acceptance/rejection
   - Multiple ride types (UberX, UberXL, Uber Black)
   - Ride sharing (UberPool)

4. **Ride Management**
   - Request ride
   - Driver assignment
   - Trip tracking (real-time)
   - Trip completion
   - Cancellation handling

5. **Pricing**
   - Base fare calculation
   - Distance-based pricing
   - Time-based pricing
   - Surge pricing (dynamic pricing)
   - Promo codes and discounts

6. **Route Optimization**
   - Calculate optimal route
   - ETA estimation
   - Traffic-aware routing
   - Multi-stop trips

7. **Payment Processing**
   - Automatic payment on trip completion
   - Multiple payment methods
   - Split payment
   - Refund processing

8. **Notifications**
   - Push notifications
   - SMS notifications
   - In-app notifications
   - Real-time trip updates

### Non-Functional Requirements

1. **Scalability**
   - Support 100M+ users globally
   - Handle 1M+ concurrent active users
   - Support 15M+ trips per day
   - 99.9% uptime
   - Multi-region deployment

2. **Performance**
   - Location update latency: < 1 second
   - Driver matching: < 5 seconds
   - ETA calculation: < 500ms
   - Payment processing: < 2 seconds
   - 99th percentile latency < 2s

3. **Availability**
   - Multi-region active-active deployment
   - Automatic failover
   - Data replication across regions
   - Zero-downtime deployments

4. **Real-Time Requirements**
   - Real-time location updates
   - Real-time driver matching
   - Real-time trip tracking
   - Real-time notifications

5. **Security**
   - Encrypted location data
   - Secure payment processing
   - Driver/rider verification
   - Fraud detection
   - Data privacy (GDPR compliance)

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Applications                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Rider   │  │  Driver  │  │  Admin   │  │  Partner │   │
│  │   App    │  │   App    │  │  Portal  │  │   API    │   │
│  │ (iOS/    │  │ (iOS/    │  │  (Web)   │  │          │   │
│  │ Android) │  │ Android) │  │          │  │          │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼───────────────┼──────────────┼────────┘
        │             │               │              │
        └─────────────┴───────────────┴──────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway / Load Balancer              │
│              (Kong / AWS API Gateway / Envoy)               │
└───────────────────────────┬─────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Region 1   │  │   Region 2   │  │   Region N   │
│  (US-West)   │  │  (EU-West)   │  │   (APAC)     │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                  │
       ▼                 ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                    Application Services Layer               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │   Auth   │  │ Location │  │ Matching │  │  Trip    │  │
│  │ Service  │  │ Service  │  │ Service  │  │ Service  │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Pricing  │  │  Route   │  │ Payment  │  │Notification│ │
│  │ Service  │  │ Service  │  │ Service  │  │ Service  │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  User    │  │  Driver  │  │  Rating  │  │  Analytics│ │
│  │ Service  │  │ Service  │  │ Service  │  │ Service  │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
└───────┼─────────────┼───────────────┼──────────────┼────────┘
        │             │               │              │
        ▼             ▼               ▼              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Caching Layer                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Redis   │  │  Redis   │  │  Redis   │  │  Redis   │   │
│  │ Cluster  │  │ Cluster  │  │ Cluster  │  │ Cluster  │   │
│  │(Location)│ │(Matching)│ │(Pricing) │ │(Sessions)│   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼──────────────┼──────────────┼────────┘
        │             │               │              │
        ▼             ▼               ▼              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Database Layer                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │PostgreSQL│  │PostgreSQL│  │Cassandra │  │TimescaleDB│   │
│  │(Users)   │  │ (Trips)  │  │(Location)│  │(Analytics)│   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │PostgreSQL│  │  Redis   │  │  Redis   │  │   S3     │   │
│  │(Drivers) │  │(Geospatial)│ │(Sessions)│ │(Logs)    │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼──────────────┼──────────────┼────────┘
        │             │               │              │
        ▼             ▼               ▼              ▼
┌─────────────────────────────────────────────────────────────┐
│              Message Queue & External Services             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Kafka   │  │  Kafka   │  │  SQS      │  │  S3      │   │
│  │(Events)  │  │(Location)│  │(Tasks)   │  │(Logs)    │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Google   │  │  Stripe  │  │  Twilio  │  │  FCM/APNS│   │
│  │ Maps API │  │(Payment) │  │   (SMS)  │  │(Push)    │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Component Details

#### 1. Client Applications
- **Rider App**: iOS and Android native apps
- **Driver App**: iOS and Android native apps
- **Admin Portal**: Web-based admin dashboard
- **Partner API**: RESTful API for third-party integrations

#### 2. API Gateway
- **Technology**: Kong, AWS API Gateway, or Envoy
- **Responsibilities**:
  - Request routing
  - Authentication/authorization
  - Rate limiting
  - Request/response transformation
  - WebSocket support for real-time updates

#### 3. Application Services (Microservices)

**Auth Service:**
- User authentication (OAuth 2.0, JWT)
- Driver verification
- Session management
- Multi-factor authentication

**Location Service:**
- Real-time GPS tracking
- Location updates processing
- Geocoding/reverse geocoding
- Location history

**Matching Service:**
- Find nearby drivers
- Match rider with driver
- Driver acceptance/rejection
- Ride type matching

**Trip Service:**
- Trip creation and management
- Trip status tracking
- Trip completion
- Cancellation handling

**Pricing Service:**
- Base fare calculation
- Surge pricing calculation
- Promo code application
- Price estimation

**Route Service:**
- Route calculation
- ETA estimation
- Traffic-aware routing
- Multi-stop optimization

**Payment Service:**
- Payment processing
- Payment gateway integration
- Split payment
- Refund processing

**Notification Service:**
- Push notifications
- SMS notifications
- In-app notifications
- Real-time trip updates

**User Service:**
- User profile management
- Trip history
- Payment methods
- Preferences

**Driver Service:**
- Driver profile management
- Earnings tracking
- Availability management
- Driver ratings

**Rating Service:**
- Trip ratings
- Driver/rider ratings
- Rating aggregation
- Review moderation

#### 4. Caching Layer
- **Technology**: Redis Cluster
- **Responsibilities**:
  - Cache driver locations (geospatial)
  - Cache pricing data
  - Session storage
  - Rate limiting
  - Real-time matching data

#### 5. Database Layer

**PostgreSQL (SQL):**
- User accounts
- Driver accounts
- Trip records
- Payment transactions
- Relational queries

**Cassandra (NoSQL):**
- Location history
- Real-time location data
- High write throughput
- Time-series data

**TimescaleDB:**
- Time-series analytics
- Trip metrics
- Performance metrics

**Redis:**
- Geospatial data (driver locations)
- Sessions
- Real-time matching
- Rate limiting

#### 6. Message Queue
- **Kafka**: Event streaming (location updates, trip events)
- **SQS**: Task queues (notifications, analytics)

#### 7. External Services
- **Google Maps API**: Geocoding, routing, traffic data
- **Stripe**: Payment processing
- **Twilio**: SMS notifications
- **FCM/APNS**: Push notifications

---

## Database Design

### PostgreSQL Schema

#### Users Table
```sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    profile_image_url VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    phone_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_phone (phone),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB;
```

#### Drivers Table
```sql
CREATE TABLE drivers (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    license_number VARCHAR(100) UNIQUE NOT NULL,
    vehicle_make VARCHAR(100),
    vehicle_model VARCHAR(100),
    vehicle_year INT,
    vehicle_color VARCHAR(50),
    license_plate VARCHAR(50),
    vehicle_type VARCHAR(50),  -- 'uberx', 'uberxl', 'uber_black'
    is_online BOOLEAN DEFAULT FALSE,
    is_available BOOLEAN DEFAULT FALSE,
    current_latitude DECIMAL(10, 8),
    current_longitude DECIMAL(11, 8),
    current_location_updated_at TIMESTAMP,
    rating DECIMAL(3, 2),
    total_trips INT DEFAULT 0,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_user_id (user_id),
    INDEX idx_is_online (is_online),
    INDEX idx_is_available (is_available),
    INDEX idx_vehicle_type (vehicle_type),
    INDEX idx_location (current_latitude, current_longitude)
) ENGINE=InnoDB;
```

#### Trips Table
```sql
CREATE TABLE trips (
    id BIGSERIAL PRIMARY KEY,
    trip_number VARCHAR(50) UNIQUE NOT NULL,
    rider_id BIGINT NOT NULL,
    driver_id BIGINT,
    status VARCHAR(20) DEFAULT 'pending',  -- 'pending', 'accepted', 'arriving', 'in_progress', 'completed', 'cancelled'
    ride_type VARCHAR(50) NOT NULL,  -- 'uberx', 'uberxl', 'uber_black', 'uber_pool'
    
    -- Pickup location
    pickup_latitude DECIMAL(10, 8) NOT NULL,
    pickup_longitude DECIMAL(11, 8) NOT NULL,
    pickup_address TEXT,
    
    -- Dropoff location
    dropoff_latitude DECIMAL(10, 8),
    dropoff_longitude DECIMAL(11, 8),
    dropoff_address TEXT,
    
    -- Pricing
    base_fare DECIMAL(10, 2),
    distance_fare DECIMAL(10, 2),
    time_fare DECIMAL(10, 2),
    surge_multiplier DECIMAL(3, 2) DEFAULT 1.0,
    promo_discount DECIMAL(10, 2) DEFAULT 0,
    total_fare DECIMAL(10, 2),
    currency VARCHAR(3) DEFAULT 'USD',
    
    -- Trip details
    distance_miles DECIMAL(8, 2),
    duration_minutes INT,
    estimated_duration_minutes INT,
    estimated_distance_miles DECIMAL(8, 2),
    
    -- Timestamps
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    accepted_at TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    cancelled_at TIMESTAMP,
    
    -- Payment
    payment_status VARCHAR(20) DEFAULT 'pending',
    payment_method_id BIGINT,
    payment_transaction_id VARCHAR(255),
    
    -- Ratings
    rider_rating INT CHECK (rider_rating BETWEEN 1 AND 5),
    driver_rating INT CHECK (driver_rating BETWEEN 1 AND 5),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (rider_id) REFERENCES users(id),
    FOREIGN KEY (driver_id) REFERENCES drivers(id),
    INDEX idx_rider_id (rider_id),
    INDEX idx_driver_id (driver_id),
    INDEX idx_status (status),
    INDEX idx_requested_at (requested_at),
    INDEX idx_trip_number (trip_number)
) ENGINE=InnoDB;
```

#### Trip Locations Table (Real-time tracking)
```sql
CREATE TABLE trip_locations (
    id BIGSERIAL PRIMARY KEY,
    trip_id BIGINT NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    accuracy FLOAT,
    speed FLOAT,
    heading FLOAT,
    is_rider_location BOOLEAN DEFAULT FALSE,
    is_driver_location BOOLEAN DEFAULT FALSE,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trip_id) REFERENCES trips(id) ON DELETE CASCADE,
    INDEX idx_trip_id (trip_id),
    INDEX idx_recorded_at (recorded_at)
) ENGINE=InnoDB;
```

#### Payment Methods Table
```sql
CREATE TABLE payment_methods (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    type VARCHAR(50) NOT NULL,  -- 'credit_card', 'debit_card', 'paypal', 'apple_pay'
    provider VARCHAR(50),  -- 'stripe', 'paypal'
    token VARCHAR(255) NOT NULL,  -- Payment token (PCI compliance)
    last_four_digits VARCHAR(4),
    expiry_month INT,
    expiry_year INT,
    is_default BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_is_default (is_default)
) ENGINE=InnoDB;
```

#### Surge Pricing Zones Table
```sql
CREATE TABLE surge_zones (
    id BIGSERIAL PRIMARY KEY,
    city_id BIGINT NOT NULL,
    zone_name VARCHAR(255),
    boundary POLYGON NOT NULL,  -- Geospatial polygon
    surge_multiplier DECIMAL(3, 2) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    effective_from TIMESTAMP,
    effective_until TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_city_id (city_id),
    INDEX idx_is_active (is_active),
    SPATIAL INDEX idx_boundary (boundary)
) ENGINE=InnoDB;
```

### Cassandra Schema (Location Data)

#### Driver Locations Table
```cql
CREATE TABLE driver_locations (
    driver_id UUID,
    timestamp TIMESTAMP,
    latitude DECIMAL,
    longitude DECIMAL,
    accuracy FLOAT,
    speed FLOAT,
    heading FLOAT,
    is_available BOOLEAN,
    vehicle_type TEXT,
    PRIMARY KEY ((driver_id), timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);
```

#### Location History Table
```cql
CREATE TABLE location_history (
    user_id UUID,
    timestamp TIMESTAMP,
    latitude DECIMAL,
    longitude DECIMAL,
    user_type TEXT,  -- 'rider' or 'driver'
    trip_id UUID,
    PRIMARY KEY ((user_id), timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);
```

### Redis Geospatial Data

**Driver Locations (Redis GeoSpatial):**
```
Key: drivers:available:{city_id}
Type: GEO
Members: driver_id -> (latitude, longitude)
```

**Example:**
```redis
GEOADD drivers:available:sf 37.7749 -122.4194 driver_123
GEORADIUS drivers:available:sf 37.7749 -122.4194 5 km WITHDIST
```

---

## API Design

### RESTful API Endpoints

#### 1. Location Services

**Update Location**
```
POST /api/v1/location/update
Content-Type: application/json
Authorization: Bearer {token}

Request:
{
    "latitude": 37.7749,
    "longitude": -122.4194,
    "accuracy": 10.5,
    "speed": 25.5,
    "heading": 90.0
}

Response:
{
    "success": true,
    "timestamp": "2024-01-15T10:30:00Z"
}
```

**Get Nearby Drivers**
```
GET /api/v1/drivers/nearby?latitude=37.7749&longitude=-122.4194&radius=5&vehicle_type=uberx

Response:
{
    "drivers": [
        {
            "driver_id": "driver_123",
            "latitude": 37.7750,
            "longitude": -122.4195,
            "distance_km": 0.5,
            "eta_minutes": 3,
            "vehicle_type": "uberx",
            "rating": 4.8
        }
    ],
    "total": 15
}
```

#### 2. Ride Management

**Request Ride**
```
POST /api/v1/rides/request
Content-Type: application/json

Request:
{
    "pickup_latitude": 37.7749,
    "pickup_longitude": -122.4194,
    "pickup_address": "123 Main St, San Francisco, CA",
    "dropoff_latitude": 37.7849,
    "dropoff_longitude": -122.4094,
    "dropoff_address": "456 Market St, San Francisco, CA",
    "ride_type": "uberx",
    "payment_method_id": "pm_123"
}

Response:
{
    "success": true,
    "trip": {
        "trip_id": "trip_12345",
        "trip_number": "UB-2024-001234",
        "status": "pending",
        "estimated_fare": 15.50,
        "estimated_eta_minutes": 5,
        "surge_multiplier": 1.2,
        "driver": null
    }
}
```

**Get Trip Status**
```
GET /api/v1/trips/{trip_id}

Response:
{
    "trip_id": "trip_12345",
    "trip_number": "UB-2024-001234",
    "status": "in_progress",
    "driver": {
        "driver_id": "driver_123",
        "name": "John Doe",
        "rating": 4.8,
        "vehicle": "Toyota Camry 2020",
        "license_plate": "ABC123"
    },
    "pickup_location": {
        "latitude": 37.7749,
        "longitude": -122.4194,
        "address": "123 Main St"
    },
    "dropoff_location": {
        "latitude": 37.7849,
        "longitude": -122.4094,
        "address": "456 Market St"
    },
    "current_location": {
        "latitude": 37.7799,
        "longitude": -122.4144
    },
    "estimated_arrival": "2024-01-15T10:35:00Z",
    "fare": {
        "base_fare": 2.55,
        "distance_fare": 8.50,
        "time_fare": 4.45,
        "surge_multiplier": 1.2,
        "total": 18.40
    }
}
```

**Cancel Trip**
```
POST /api/v1/trips/{trip_id}/cancel
Content-Type: application/json

Request:
{
    "reason": "changed_mind"
}

Response:
{
    "success": true,
    "cancellation_fee": 5.00,
    "refund_amount": 13.40
}
```

#### 3. Driver APIs

**Go Online**
```
POST /api/v1/drivers/online
Content-Type: application/json

Request:
{
    "latitude": 37.7749,
    "longitude": -122.4194
}

Response:
{
    "success": true,
    "status": "online",
    "available_rides": 5
}
```

**Accept Ride**
```
POST /api/v1/drivers/rides/{trip_id}/accept

Response:
{
    "success": true,
    "trip": {
        "trip_id": "trip_12345",
        "rider": {
            "name": "Jane Smith",
            "rating": 4.9,
            "pickup_address": "123 Main St"
        },
        "estimated_fare": 15.50
    }
}
```

**Update Trip Status**
```
PUT /api/v1/drivers/trips/{trip_id}/status
Content-Type: application/json

Request:
{
    "status": "arriving"  // 'arriving', 'in_progress', 'completed'
}

Response:
{
    "success": true,
    "status": "arriving"
}
```

#### 4. Pricing

**Get Price Estimate**
```
GET /api/v1/pricing/estimate?pickup_lat=37.7749&pickup_lng=-122.4194&dropoff_lat=37.7849&dropoff_lng=-122.4094&ride_type=uberx

Response:
{
    "estimates": [
        {
            "ride_type": "uberx",
            "estimated_fare": {
                "low": 12.50,
                "high": 18.50,
                "currency": "USD"
            },
            "estimated_duration_minutes": 15,
            "estimated_distance_miles": 3.5,
            "surge_multiplier": 1.2
        },
        {
            "ride_type": "uberxl",
            "estimated_fare": {
                "low": 18.00,
                "high": 25.00,
                "currency": "USD"
            }
        }
    ]
}
```

#### 5. Trip History

**Get Trip History**
```
GET /api/v1/trips?page=1&limit=20

Response:
{
    "trips": [
        {
            "trip_id": "trip_12345",
            "trip_number": "UB-2024-001234",
            "status": "completed",
            "pickup_address": "123 Main St",
            "dropoff_address": "456 Market St",
            "fare": 18.40,
            "completed_at": "2024-01-15T10:45:00Z",
            "driver": {
                "name": "John Doe",
                "rating": 4.8
            }
        }
    ],
    "pagination": {
        "page": 1,
        "limit": 20,
        "total": 150,
        "total_pages": 8
    }
}
```

---

## Data Flow Diagrams

### Request Ride Flow

```
Rider Requests Ride
    │
    ▼
Ride Service
    │
    ├─ Validate Request
    ├─ Calculate Price Estimate
    │   │
    │   ▼
    │   Pricing Service
    │   │
    │   ├─ Get Base Fare
    │   ├─ Calculate Distance/Time
    │   ├─ Check Surge Pricing
    │   └─ Apply Promo Codes
    │
    ▼
Create Trip Record (PostgreSQL)
    │
    ▼
Matching Service
    │
    ├─ Find Nearby Drivers
    │   │
    │   ▼
    │   Location Service
    │   │
    │   ├─ Query Redis GeoSpatial
    │   │   └─ GEORADIUS drivers:available:sf lat lng 5 km
    │   │
    │   └─ Filter by Vehicle Type
    │   │
    │   ▼
    │   Calculate ETA for Each Driver
    │   │
    │   ▼
    │   Route Service
    │   │
    │   └─ Get ETA from Google Maps API
    │
    ├─ Rank Drivers (by ETA, Rating)
    │
    └─ Send Ride Request to Top Drivers
        │
        ▼
    Notification Service
        │
        ├─ Push Notification to Drivers
        └─ SMS Notification (optional)
        │
        ▼
    Wait for Driver Acceptance (30 seconds timeout)
        │
        ├─ Driver Accepts → Assign Driver
        │
        └─ No Acceptance → Retry with Next Drivers
            │
            └─ After 3 attempts → Notify Rider (No drivers available)
```

### Real-Time Location Update Flow

```
Driver App Sends Location Update (Every 4-5 seconds)
    │
    ▼
Location Service
    │
    ├─ Validate Location Data
    ├─ Update Redis GeoSpatial
    │   └─ GEOADD drivers:available:sf lat lng driver_id
    │
    ├─ Update PostgreSQL (Current Location)
    │   └─ UPDATE drivers SET current_latitude=..., current_longitude=...
    │
    └─ Publish to Kafka (Location Event)
        │
        ▼
    Kafka Consumer (Location Processor)
        │
        ├─ Update Cassandra (Location History)
        ├─ Update Matching Service Cache
        └─ Trigger Notifications (if needed)
            │
            └─ If Active Trip → Update Rider App
```

### Trip Completion Flow

```
Driver Marks Trip Complete
    │
    ▼
Trip Service
    │
    ├─ Validate Trip Status
    ├─ Calculate Final Fare
    │   │
    │   ▼
    │   Pricing Service
    │   │
    │   ├─ Calculate Distance (from trip_locations)
    │   ├─ Calculate Duration
    │   ├─ Apply Base Fare
    │   ├─ Apply Distance/Time Fares
    │   └─ Apply Surge Multiplier
    │
    ├─ Update Trip Status to 'completed'
    │
    ├─ Process Payment
    │   │
    │   ▼
    │   Payment Service
    │   │
    │   ├─ Charge Payment Method
    │   ├─ Record Transaction
    │   └─ Update Payment Status
    │
    ├─ Release Driver (Make Available)
    │
    ├─ Update Inventory (if applicable)
    │
    └─ Publish Trip Completion Event (Kafka)
        │
        ├─ Notification Service (Send Receipt)
        ├─ Rating Service (Request Ratings)
        ├─ Analytics Service (Record Metrics)
        └─ Driver Service (Update Earnings)
```

---

## Real-Time Location Tracking

### Location Update Architecture

**Update Frequency:**
- **Active Trip**: Every 4-5 seconds
- **Driver Online**: Every 10-15 seconds
- **Rider Browsing**: Every 30 seconds

**Location Storage:**
- **Redis GeoSpatial**: Real-time driver locations (for matching)
- **PostgreSQL**: Current location (for queries)
- **Cassandra**: Location history (for analytics)

**GeoSpatial Queries:**
```python
class LocationService:
    def update_driver_location(self, driver_id, lat, lng):
        # Update Redis GeoSpatial
        redis.geoadd(
            f"drivers:available:{city_id}",
            lng, lat, driver_id
        )
        
        # Update PostgreSQL
        Driver.objects.filter(id=driver_id).update(
            current_latitude=lat,
            current_longitude=lng,
            current_location_updated_at=now()
        )
        
        # Publish to Kafka
        kafka.publish('location_updates', {
            'driver_id': driver_id,
            'latitude': lat,
            'longitude': lng,
            'timestamp': now()
        })
    
    def find_nearby_drivers(self, lat, lng, radius_km=5, vehicle_type=None):
        # Query Redis GeoSpatial
        drivers = redis.georadius(
            f"drivers:available:{city_id}",
            lng, lat, radius_km, 'km',
            withdist=True,
            withcoord=True
        )
        
        # Filter by vehicle type if specified
        if vehicle_type:
            drivers = [d for d in drivers if d['vehicle_type'] == vehicle_type]
        
        return drivers
```

---

## Ride Matching System

### Matching Algorithm

**Matching Criteria:**
1. **Distance**: Closest drivers first
2. **ETA**: Shortest estimated arrival time
3. **Rating**: Higher-rated drivers preferred
4. **Vehicle Type**: Match ride type
5. **Availability**: Only available drivers

**Matching Process:**
```python
class MatchingService:
    def match_rider_to_driver(self, trip_request):
        # Get nearby drivers
        nearby_drivers = self.location_service.find_nearby_drivers(
            lat=trip_request.pickup_latitude,
            lng=trip_request.pickup_longitude,
            radius_km=5,
            vehicle_type=trip_request.ride_type
        )
        
        if not nearby_drivers:
            return None
        
        # Calculate ETA for each driver
        drivers_with_eta = []
        for driver in nearby_drivers:
            eta = self.route_service.calculate_eta(
                driver_lat=driver['latitude'],
                driver_lng=driver['longitude'],
                pickup_lat=trip_request.pickup_latitude,
                pickup_lng=trip_request.pickup_longitude
            )
            drivers_with_eta.append({
                **driver,
                'eta_minutes': eta
            })
        
        # Rank drivers (ETA + Rating)
        ranked_drivers = sorted(
            drivers_with_eta,
            key=lambda d: (d['eta_minutes'], -d['rating'])
        )
        
        # Send request to top 3 drivers
        for driver in ranked_drivers[:3]:
            if self.send_ride_request(driver['driver_id'], trip_request):
                return driver
        
        return None
    
    def send_ride_request(self, driver_id, trip_request):
        # Send push notification
        self.notification_service.send_push(
            driver_id=driver_id,
            title="New Ride Request",
            body=f"Pickup: {trip_request.pickup_address}",
            data={'trip_id': trip_request.trip_id}
        )
        
        # Wait for acceptance (30 seconds)
        return self.wait_for_acceptance(driver_id, trip_request.trip_id, timeout=30)
```

### Matching Optimization

**Challenges:**
- **Scale**: Millions of location updates per second
- **Latency**: Match must happen in < 5 seconds
- **Accuracy**: Find best driver, not just closest

**Solutions:**
- **GeoSpatial Indexing**: Redis GeoSpatial for fast queries
- **Caching**: Cache driver locations
- **Pre-computation**: Pre-calculate ETAs
- **Batch Processing**: Batch location updates

---

## Dynamic Pricing (Surge Pricing)

### Surge Pricing Algorithm

**Surge Factors:**
1. **Supply/Demand Ratio**: Available drivers vs ride requests
2. **Time of Day**: Peak hours (rush hour, nightlife)
3. **Events**: Concerts, sports games
4. **Weather**: Bad weather increases demand
5. **Historical Data**: Patterns from past data

**Surge Calculation:**
```python
class PricingService:
    def calculate_surge_multiplier(self, city_id, zone_id, ride_type):
        # Get current demand
        active_requests = self.get_active_requests(city_id, zone_id, ride_type)
        
        # Get current supply
        available_drivers = self.get_available_drivers(city_id, zone_id, ride_type)
        
        # Calculate supply/demand ratio
        if available_drivers == 0:
            return 3.0  # Maximum surge
        
        ratio = active_requests / available_drivers
        
        # Base surge calculation
        if ratio < 0.5:
            surge = 1.0  # No surge
        elif ratio < 1.0:
            surge = 1.0 + (ratio - 0.5) * 0.5  # 1.0 - 1.25
        elif ratio < 2.0:
            surge = 1.25 + (ratio - 1.0) * 0.75  # 1.25 - 2.0
        else:
            surge = min(2.0 + (ratio - 2.0) * 0.5, 3.0)  # 2.0 - 3.0
        
        # Apply time-based adjustments
        hour = datetime.now().hour
        if hour in [7, 8, 17, 18]:  # Rush hours
            surge *= 1.2
        
        # Apply event-based adjustments
        events = self.get_active_events(city_id, zone_id)
        if events:
            surge *= 1.3
        
        return min(surge, 3.0)  # Cap at 3x
```

### Surge Zone Management

**Zone Definition:**
- Divide city into zones (geospatial polygons)
- Calculate surge per zone
- Update surge every 1-2 minutes

**Surge Display:**
- Show surge multiplier on map
- Color-code zones (green = no surge, red = high surge)
- Update in real-time

---

## Route Optimization

### Route Calculation

**Route Service:**
- **Google Maps API**: Primary routing engine
- **Traffic Data**: Real-time traffic information
- **ETA Calculation**: Estimated time of arrival
- **Multi-stop Optimization**: For UberPool

**Route Optimization:**
```python
class RouteService:
    def calculate_route(self, origin_lat, origin_lng, dest_lat, dest_lng):
        # Call Google Maps API
        response = google_maps.directions(
            origin=f"{origin_lat},{origin_lng}",
            destination=f"{dest_lat},{dest_lng}",
            mode='driving',
            alternatives=True
        )
        
        # Select best route (shortest time)
        best_route = min(
            response['routes'],
            key=lambda r: r['legs'][0]['duration']['value']
        )
        
        return {
            'distance_meters': best_route['legs'][0]['distance']['value'],
            'duration_seconds': best_route['legs'][0]['duration']['value'],
            'polyline': best_route['overview_polyline']['points']
        }
    
    def calculate_eta(self, driver_lat, driver_lng, pickup_lat, pickup_lng):
        # Calculate ETA from driver to pickup
        route = self.calculate_route(driver_lat, driver_lng, pickup_lat, pickup_lng)
        return route['duration_seconds'] / 60  # Convert to minutes
```

### Traffic-Aware Routing

**Traffic Considerations:**
- Real-time traffic data from Google Maps
- Historical traffic patterns
- Time-of-day adjustments
- Weather impact on traffic

---

## Payment Processing

### Payment Flow

**Payment Methods:**
- Credit/Debit Cards (Stripe)
- PayPal
- Apple Pay / Google Pay
- Uber Credits

**Payment Processing:**
```python
class PaymentService:
    def process_trip_payment(self, trip_id):
        trip = Trip.objects.get(id=trip_id)
        
        # Get payment method
        payment_method = PaymentMethod.objects.get(
            id=trip.payment_method_id
        )
        
        # Charge payment
        charge = stripe.Charge.create(
            amount=int(trip.total_fare * 100),  # Convert to cents
            currency=trip.currency.lower(),
            customer=payment_method.token,
            description=f"Trip {trip.trip_number}"
        )
        
        # Update trip
        trip.payment_status = 'paid'
        trip.payment_transaction_id = charge.id
        trip.save()
        
        return charge
```

### Split Payment

**Split Payment Feature:**
- Multiple riders can split fare
- Each rider pays their portion
- Automatic calculation

---

## Notification System

### Notification Types

1. **Push Notifications**: Real-time trip updates
2. **SMS Notifications**: Important updates
3. **In-App Notifications**: App notifications
4. **Email Notifications**: Receipts, summaries

### Notification Flow

```
Event Occurs (Trip Status Change)
    │
    ▼
Notification Service
    │
    ├─ Determine Recipients
    │   ├─ Rider (for trip updates)
    │   └─ Driver (for ride requests)
    │
    ├─ Get User Preferences
    │
    ├─ Send Push Notification
    │   │
    │   ▼
    │   FCM/APNS
    │
    ├─ Send SMS (if critical)
    │   │
    │   ▼
    │   Twilio
    │
    └─ Send Email (if needed)
        │
        ▼
    Email Service
```

---

## Scalability Considerations

### 1. Location Updates Scale

**Challenge:** Millions of location updates per second

**Solutions:**
- **Batching**: Batch location updates (every 5 seconds)
- **Kafka**: Stream location updates asynchronously
- **Redis GeoSpatial**: Fast geospatial queries
- **Sharding**: Shard by city/region

### 2. Matching Scale

**Challenge:** Match millions of riders with drivers in real-time

**Solutions:**
- **GeoSpatial Indexing**: Redis GeoSpatial for O(log N) queries
- **Caching**: Cache driver locations
- **Pre-filtering**: Filter by city before matching
- **Parallel Processing**: Match multiple riders simultaneously

### 3. Database Scaling

**PostgreSQL Scaling:**
- Read replicas for read-heavy queries
- Sharding by city_id or user_id
- Partitioning trip table by date

**Cassandra Scaling:**
- Horizontal scaling by adding nodes
- Partition by user_id or driver_id
- Time-based partitioning

### 4. Real-Time Updates

**WebSocket Connections:**
- **Challenge**: Millions of concurrent WebSocket connections
- **Solution**: 
  - WebSocket servers (separate from API servers)
  - Load balancing WebSocket connections
  - Connection pooling

---

## Caching Strategy

### Cache Architecture

```
Location Update
    │
    ▼
Redis GeoSpatial (Driver Locations)
    │
    ├─ Real-time Matching Queries
    └─ Fast GeoSpatial Searches
    │
    ▼
PostgreSQL (Current Location)
    │
    └─ Persistent Storage
    │
    ▼
Cassandra (Location History)
    │
    └─ Historical Data
```

### Cache Patterns

1. **Write-Through**: Driver locations (Redis + PostgreSQL)
2. **Cache-Aside**: Trip data, user data
3. **Write-Behind**: Location history (Cassandra)

### Cache Keys

```
drivers:available:{city_id} → GeoSpatial driver locations
trip:{trip_id} → Trip data
user:{user_id} → User data
driver:{driver_id} → Driver data
surge:{city_id}:{zone_id} → Surge pricing data
```

---

## Load Balancing

### Load Balancer Architecture

```
Internet
    │
    ▼
DNS (Route53/Cloudflare)
    │
    ├─ Region 1 (US-West)
    ├─ Region 2 (EU-West)
    └─ Region 3 (APAC)
    │
    ▼
Global Load Balancer
    │
    ├─ Application Load Balancer (ALB)
    └─ Network Load Balancer (NLB)
    │
    ▼
API Gateway
    │
    ├─ Location Service
    ├─ Matching Service
    ├─ Trip Service
    └─ Payment Service
```

### WebSocket Load Balancing

**Challenge:** WebSocket connections are stateful

**Solutions:**
- **Sticky Sessions**: Route same client to same server
- **Redis Pub/Sub**: Broadcast messages across servers
- **Message Queue**: Use Kafka for cross-server communication

---

## Security

### 1. Location Privacy

**Encryption:**
- Encrypt location data in transit (TLS 1.3)
- Encrypt location data at rest
- Anonymize location data for analytics

**Access Control:**
- Only authorized users can see locations
- Drivers see rider location only during active trip
- Riders see driver location only during active trip

### 2. Payment Security

**PCI-DSS Compliance:**
- Don't store raw card data
- Use tokenization (Stripe tokens)
- Encrypt payment data

### 3. Driver/Rider Verification

**Verification:**
- Driver license verification
- Background checks
- Phone verification
- Email verification

### 4. Fraud Detection

**Fraud Prevention:**
- ML-based fraud detection
- Unusual trip patterns
- Payment fraud detection
- Account takeover detection

---

## Monitoring & Analytics

### Key Metrics

**System Metrics:**
- Location update rate
- Matching latency
- Trip completion rate
- Payment success rate
- API latency (p50, p95, p99)

**Business Metrics:**
- Daily active riders
- Daily active drivers
- Trips per day
- Revenue per day
- Average trip fare
- Surge pricing utilization

**Operational Metrics:**
- Driver acceptance rate
- Trip cancellation rate
- Average ETA accuracy
- Customer satisfaction (ratings)

### Analytics Pipeline

```
Events (Location, Trip, Payment)
    │
    ▼
Kafka (Event Stream)
    │
    ├─ Real-time Processing (Flink)
    │   └─ Real-time Dashboards
    │
    └─ Batch Processing (Spark)
        └─ Data Warehouse (Redshift)
            └─ Analytics & Reporting
```

---

## Deployment Strategy

### Infrastructure

**Cloud Provider:** AWS, GCP, or Azure

**Components:**
- **Compute**: Kubernetes (EKS/GKE) or ECS
- **Database**: 
  - PostgreSQL (RDS with read replicas)
  - Cassandra (managed: AWS Keyspaces)
  - Redis (ElastiCache)
- **Message Queue**: Kafka (MSK) or Kinesis
- **CDN**: CloudFront
- **Monitoring**: CloudWatch, Datadog

### Multi-Region Deployment

```
Region 1 (US-West)      Region 2 (EU-West)      Region 3 (APAC)
┌─────────────┐        ┌─────────────┐        ┌─────────────┐
│   Primary   │◄──────►│   Replica   │◄──────►│   Replica   │
│   Database  │        │   Database  │        │   Database  │
└─────────────┘        └─────────────┘        └─────────────┘
       ▲                      ▲                      ▲
       │                      │                      │
┌──────┴──────┐        ┌──────┴──────┐        ┌──────┴──────┐
│  App Servers│        │  App Servers│        │  App Servers│
│  (Active)   │        │  (Active)   │        │  (Active)   │
└─────────────┘        └─────────────┘        └─────────────┘
```

---

## Capacity Planning

### Storage Estimates

**Trips:**
- 15M trips/day × 365 days = 5.5B trips/year
- 5.5B trips × 2 KB = 11 TB/year
- **Total Trips: ~11 TB/year**

**Location Data:**
- 1M active users × 4 updates/min × 60 min × 24 hours = 5.76B updates/day
- 5.76B updates/day × 100 bytes = 576 GB/day = 210 TB/year
- **Total Location Data: ~210 TB/year**

**Users:**
- 100M users × 1 KB = 100 GB

**Total Storage (Year 1): ~221 TB**

### Compute Requirements

**Location Service:**
- 1M active users × 4 updates/min = 4M updates/min = 67K updates/sec
- Each update: ~10ms processing
- Required servers: 67K / (1000/10) = 670 servers

**Matching Service:**
- 1M ride requests/day = 12 requests/sec average
- Peak: 12 × 10 = 120 requests/sec
- Each match: ~2 seconds (including ETA calculation)
- Required servers: 120 × 2 = 240 servers

**Trip Service:**
- 15M trips/day = 174 trips/sec average
- Peak: 174 × 10 = 1,740 trips/sec
- Each trip: ~50ms processing
- Required servers: 1,740 / (1000/50) = 87 servers

**Total Compute: ~1,000 servers** (per region)

### Network Bandwidth

**Location Updates:**
- 67K updates/sec × 500 bytes = 33.5 MB/s = 268 Mbps

**API Traffic:**
- 10K QPS × 5 KB average = 50 MB/s = 400 Mbps

**Total Bandwidth: ~670 Mbps**

---

## Technology Stack

### Recommended Stack (AWS)

**Compute:**
- **Container Orchestration**: Kubernetes (EKS) or ECS
- **Serverless**: AWS Lambda for event processing

**Databases:**
- **SQL**: Amazon RDS PostgreSQL with read replicas
- **NoSQL**: Amazon Keyspaces (Cassandra-compatible)
- **Cache**: Amazon ElastiCache (Redis)
- **Time-Series**: TimescaleDB

**Message Queue:**
- **Streaming**: Amazon Kinesis or Apache Kafka (MSK)
- **Queue**: Amazon SQS

**External Services:**
- **Maps**: Google Maps API
- **Payment**: Stripe
- **SMS**: Twilio
- **Push**: FCM (Android), APNS (iOS)

**Monitoring:**
- **APM**: AWS X-Ray, Datadog
- **Logging**: Amazon CloudWatch Logs, ELK Stack
- **Metrics**: Amazon CloudWatch, Prometheus + Grafana

---

## Failure Scenarios & Handling

### 1. Location Service Failure

**Scenario:** Location service crashes or becomes unavailable.

**Impact:** Cannot track drivers, matching fails.

**Mitigation:**
- **Multiple Instances**: Run multiple location service instances
- **Graceful Degradation**: Use last known location
- **Fallback**: Query database for last known location
- **Circuit Breaker**: Fail gracefully, retry later

**Recovery:** Automatic restart, restore from database

### 2. Matching Service Failure

**Scenario:** Matching service fails, cannot match riders with drivers.

**Impact:** Riders cannot get rides.

**Mitigation:**
- **Multiple Instances**: Run multiple matching service instances
- **Fallback Algorithm**: Simple distance-based matching
- **Queue Requests**: Queue ride requests, process when service recovers
- **Manual Assignment**: Admin can manually assign drivers

### 3. Payment Gateway Failure

**Scenario:** Stripe payment gateway is down.

**Impact:** Cannot process payments, trips stuck.

**Mitigation:**
- **Multiple Gateways**: Support Stripe, PayPal
- **Queue Payments**: Queue payment requests, retry later
- **Manual Processing**: Admin can process payments manually
- **Graceful Degradation**: Allow trip completion, process payment later

### 4. High Surge Demand

**Scenario:** Sudden spike in demand (concert, sports game).

**Impact:** Not enough drivers, long wait times.

**Mitigation:**
- **Surge Pricing**: Increase prices to attract more drivers
- **Driver Incentives**: Bonus for drivers in surge zones
- **Pre-positioning**: Pre-position drivers near events
- **Notification**: Notify riders of high demand

### 5. Driver App Crash

**Scenario:** Driver app crashes, cannot receive ride requests.

**Impact:** Driver unavailable, lost revenue.

**Mitigation:**
- **App Monitoring**: Monitor app crashes
- **Automatic Recovery**: Auto-restart app
- **Fallback**: SMS notifications if app unavailable
- **Support**: Quick support for drivers

### 6. GPS Signal Loss

**Scenario:** Driver loses GPS signal (tunnel, building).

**Impact:** Cannot track driver location.

**Mitigation:**
- **Last Known Location**: Use last known location
- **Prediction**: Predict location based on route
- **Reconnection**: Resume tracking when signal returns
- **Manual Update**: Allow driver to manually update location

---

## Trade-offs & Design Decisions

### 1. Location Storage: Redis vs Database

**Decision:** Redis GeoSpatial for real-time, PostgreSQL for persistence.

**Trade-offs:**

| Storage | Pros | Cons |
|---------|------|------|
| **Redis GeoSpatial** | Fast queries, real-time | Volatile, memory-limited |
| **PostgreSQL** | Persistent, reliable | Slower geospatial queries |

**Why Both:**
- **Redis**: Fast matching queries (O(log N))
- **PostgreSQL**: Persistent storage, complex queries
- **Result**: Best of both worlds

### 2. Matching: Real-time vs Batch

**Decision:** Real-time matching with timeout.

**Trade-offs:**

| Approach | Pros | Cons |
|----------|------|------|
| **Real-time** | Fast, accurate | High load, complex |
| **Batch** | Lower load, simpler | Slower, less accurate |

**Why Real-time:**
- **User Experience**: Riders expect quick matches
- **Accuracy**: Real-time location data is more accurate
- **Competitive**: Industry standard

### 3. Surge Pricing: Manual vs Automatic

**Decision:** Automatic surge pricing with manual overrides.

**Trade-offs:**

| Approach | Pros | Cons |
|----------|------|------|
| **Automatic** | Fast, scalable | May not account for edge cases |
| **Manual** | Precise control | Slow, doesn't scale |

**Hybrid Approach:**
- **Automatic**: Algorithm calculates surge
- **Manual Override**: Admins can adjust for events
- **Result**: Best of both worlds

### 4. Payment: Pre-authorization vs Post-payment

**Decision:** Post-payment (charge after trip completion).

**Trade-offs:**

| Approach | Pros | Cons |
|----------|------|------|
| **Pre-authorization** | Guaranteed payment | Complex refunds |
| **Post-payment** | Simple, accurate fare | Risk of failed payment |

**Why Post-payment:**
- **Accuracy**: Final fare may differ from estimate
- **Simplicity**: No refunds needed
- **User Experience**: Pay for actual service

### 5. Location Updates: High Frequency vs Low Frequency

**Decision:** High frequency (every 4-5 seconds) for active trips.

**Trade-offs:**

| Frequency | Pros | Cons |
|-----------|------|------|
| **High (4-5s)** | Accurate tracking | High load, battery drain |
| **Low (30s)** | Lower load | Less accurate |

**Why High Frequency:**
- **User Experience**: Real-time tracking expected
- **Safety**: Accurate location for safety features
- **Optimization**: Can optimize with batching

---

## Interview Discussion Points

### Key Questions to Address

1. **"How do you match a rider with the best driver?"**
   - **Answer**: 
     - Find nearby drivers using GeoSpatial query
     - Calculate ETA for each driver
     - Rank by ETA and rating
     - Send request to top drivers
     - Wait for acceptance (30 seconds)

2. **"How do you prevent overselling (matching same driver to multiple riders)?"**
   - **Answer**:
     - Use distributed locks (Redis)
     - Reserve driver when request sent
     - Release if not accepted
     - Atomic operations for driver assignment

3. **"How do you calculate surge pricing?"**
   - **Answer**:
     - Monitor supply/demand ratio
     - Calculate surge multiplier (1.0x - 3.0x)
     - Apply time-based and event-based adjustments
     - Update every 1-2 minutes

4. **"How do you handle GPS signal loss?"**
   - **Answer**:
     - Use last known location
     - Predict location based on route
     - Resume tracking when signal returns
     - Allow manual location update

5. **"How do you scale location updates?"**
   - **Answer**:
     - Batch updates (every 5 seconds)
     - Use Kafka for async processing
     - Redis GeoSpatial for fast queries
     - Shard by city/region

### Scalability Deep Dive

**Q: "How do you scale from 1K to 100M users?"**

**Answer:**

**Phase 1: 1K-100K Users**
- Single region
- Single PostgreSQL database
- Basic Redis caching
- Simple matching algorithm

**Phase 2: 100K-10M Users**
- Multiple regions
- PostgreSQL with read replicas
- Redis cluster
- GeoSpatial indexing
- Kafka for events

**Phase 3: 10M-100M Users**
- Multi-region active-active
- Database sharding
- Multiple Redis clusters
- Advanced matching algorithm
- ML-based surge pricing

**Key Scaling Principles:**
1. **GeoSpatial Indexing**: Use Redis GeoSpatial for fast queries
2. **Async Processing**: Use Kafka for location updates
3. **Caching**: Cache driver locations aggressively
4. **Sharding**: Shard by city/region
5. **Load Balancing**: Distribute load across regions

### Performance Optimization

**Q: "How do you optimize matching latency?"**

**Answer:**

**Current Flow:**
1. Find nearby drivers (50ms)
2. Calculate ETA for each (200ms × N drivers)
3. Rank drivers (10ms)
4. Send requests (100ms)
**Total: 360ms+ (depends on N)**

**Optimizations:**
1. **Pre-filter**: Filter by city before geospatial query
2. **Cache ETAs**: Cache ETA calculations
3. **Parallel ETA**: Calculate ETAs in parallel
4. **Limit Drivers**: Only consider top 10 closest drivers
5. **Pre-compute**: Pre-compute common routes

**Optimized Flow:**
1. Pre-filter by city (5ms)
2. Find nearby drivers (50ms)
3. Parallel ETA calculation (200ms for top 10)
4. Rank and send (50ms)
**Total: 305ms** (vs 360ms+)

### Cost Optimization

**Q: "How do you optimize costs at scale?"**

**Answer:**

1. **Database Costs** (40% of total):
   - Use read replicas for reads
   - Archive old trips
   - Compress location data

2. **External API Costs** (30% of total):
   - Cache Google Maps API responses
   - Batch geocoding requests
   - Use cheaper alternatives when possible

3. **Compute Costs** (20% of total):
   - Auto-scaling (scale down during off-peak)
   - Use spot instances for batch jobs
   - Optimize matching algorithm

4. **Storage Costs** (10% of total):
   - Archive old location data
   - Compress trip data
   - Use cheaper storage for analytics

**Total Savings**: 30-40% cost reduction

---

## References

- [System Design Primer](https://github.com/donnemartin/system-design-primer)
- [Uber Engineering Blog](https://eng.uber.com/)
- [Real-Time Location Tracking](https://www.uber.com/en-US/blog/real-time-location-tracking/)
- [Redis GeoSpatial](https://redis.io/commands/geoadd/)
- [Google Maps API](https://developers.google.com/maps/documentation)
- [Stripe Payment Processing](https://stripe.com/docs)
- [Kafka Event Streaming](https://kafka.apache.org/)

