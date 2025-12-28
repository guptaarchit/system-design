# Weather Application System Design

## Table of Contents
1. [Overview](#overview)
2. [Requirements](#requirements)
3. [System Architecture](#system-architecture)
4. [Data Sources & Integration](#data-sources--integration)
5. [Database Design](#database-design)
6. [API Design](#api-design)
7. [Caching Strategy](#caching-strategy)
8. [Real-Time Updates](#real-time-updates)
9. [Location Services](#location-services)
10. [Notification System](#notification-system)
11. [Scalability Considerations](#scalability-considerations)
12. [Monitoring & Analytics](#monitoring--analytics)
13. [Deployment Strategy](#deployment-strategy)
14. [Failure Scenarios & Handling](#failure-scenarios--handling)
15. [Trade-offs & Design Decisions](#trade-offs--design-decisions)
16. [Interview Discussion Points](#interview-discussion-points)

---

## Overview

A comprehensive Weather Application that provides accurate, real-time weather information, forecasts, alerts, and personalized weather experiences for users worldwide. The system aggregates data from multiple weather providers, processes it efficiently, and delivers it to millions of users through web and mobile applications.

**Key Features:**
- Current weather conditions
- Hourly and daily forecasts (up to 10 days)
- Weather alerts and notifications
- Location-based weather
- Historical weather data
- Weather maps and radar
- Personalized weather insights
- Multi-location support
- Weather widgets
- Social sharing

---

## Requirements

### Functional Requirements

1. **Weather Data Display**
   - Current conditions (temperature, humidity, wind, etc.)
   - Hourly forecast (next 24-48 hours)
   - Daily forecast (next 7-10 days)
   - Weather alerts (severe weather warnings)
   - Weather maps (radar, satellite, precipitation)
   - Air quality index
   - UV index
   - Sunrise/sunset times

2. **Location Services**
   - GPS-based location detection
   - Search by city name
   - Search by ZIP code
   - Search by coordinates
   - Save favorite locations
   - Recent locations history

3. **User Features**
   - User accounts and profiles
   - Customizable units (Celsius/Fahrenheit)
   - Notification preferences
   - Favorite locations
   - Weather widgets
   - Historical data access

4. **Notifications**
   - Severe weather alerts
   - Daily weather summaries
   - Rain/snow alerts
   - Temperature alerts
   - Custom alert rules

5. **Weather Maps**
   - Interactive weather maps
   - Radar imagery
   - Satellite imagery
   - Precipitation maps
   - Temperature maps
   - Wind maps

6. **Historical Data**
   - Past weather conditions
   - Historical trends
   - Climate data
   - Weather statistics

### Non-Functional Requirements

1. **Scalability**
   - Support 50M+ users
   - Handle 100K+ requests per second
   - Support 10M+ concurrent users
   - Multi-region deployment
   - 99.9% uptime

2. **Performance**
   - Weather data fetch: < 200ms (p95)
   - Map loading: < 1 second
   - Search results: < 100ms
   - Real-time updates: < 5 seconds latency
   - 99th percentile latency < 500ms

3. **Availability**
   - Multi-region active-active
   - Automatic failover
   - Data redundancy
   - Zero-downtime deployments

4. **Data Accuracy**
   - Aggregate from multiple sources
   - Data validation and quality checks
   - Regular updates (every 15 minutes)
   - Historical data accuracy

5. **Cost Efficiency**
   - Efficient caching
   - Data source cost optimization
   - CDN usage
   - Rate limiting

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Applications                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │   Web    │  │   iOS    │  │ Android  │  │  Widget  │  │
│  │  Client  │  │   App    │  │   App    │  │  Client  │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
└───────┼─────────────┼───────────────┼──────────────┼────────┘
        │             │               │              │
        └─────────────┴───────────────┴──────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    CDN / Edge Network                        │
│              (CloudFlare / AWS CloudFront)                   │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway / Load Balancer              │
│              (Kong / AWS API Gateway / Envoy)               │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Application Services                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Weather  │  │ Location │  │   Alert  │  │   Map    │  │
│  │ Service  │  │ Service  │  │ Service  │  │ Service  │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │   User   │  │Historical│ │Notification│ │ Analytics│  │
│  │ Service  │  │ Service  │  │ Service  │  │ Service  │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
└───────┼─────────────┼──────────────┼──────────────┼────────┘
        │             │               │              │
        ▼             ▼               ▼              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Caching Layer                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Redis   │  │  Redis   │  │  Redis   │  │  Redis   │   │
│  │(Weather) │ │(Location)│ │(Forecast) │ │(Maps)    │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼──────────────┼──────────────┼────────┘
        │             │               │              │
        ▼             ▼               ▼              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Database Layer                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │PostgreSQL│  │PostgreSQL│  │ TimeSeries│ │PostgreSQL│   │
│  │ (Users)  │  │(Locations)│ │  (Weather)│ │ (Alerts) │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼──────────────┼──────────────┼────────┘
        │             │               │              │
        ▼             ▼               ▼              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Data Ingestion Layer                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Weather  │  │ Weather  │  │ Weather  │  │   Map    │   │
│  │Provider 1│  │Provider 2│  │Provider 3│  │ Provider │   │
│  │  (API)   │  │  (API)   │  │  (API)   │  │  (API)   │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼──────────────┼──────────────┼────────┘
        │             │               │              │
        ▼             ▼               ▼              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Message Queue                             │
│              (Kafka / AWS SQS / RabbitMQ)                   │
└─────────────────────────────────────────────────────────────┘
```

### Component Details

#### 1. Weather Service
- Fetches current weather
- Provides forecasts
- Aggregates multiple data sources
- Data normalization

#### 2. Location Service
- Geocoding (address to coordinates)
- Reverse geocoding (coordinates to address)
- Location search
- Location validation

#### 3. Alert Service
- Weather alert generation
- Alert distribution
- Alert preferences management
- Alert history

#### 4. Map Service
- Weather map generation
- Radar/satellite imagery
- Map tile serving
- Interactive map features

#### 5. User Service
- User management
- Preferences storage
- Favorite locations
- Usage analytics

#### 6. Historical Service
- Historical data storage
- Historical data queries
- Trend analysis
- Climate data

#### 7. Notification Service
- Push notifications
- Email notifications
- SMS notifications
- In-app notifications

---

## Data Sources & Integration

### Weather Data Providers

1. **OpenWeatherMap**
   - Current weather, forecasts
   - Historical data
   - Weather maps
   - Air quality

2. **WeatherAPI**
   - Comprehensive forecasts
   - Historical data
   - Astronomy data

3. **AccuWeather**
   - Detailed forecasts
   - Severe weather alerts
   - Minute-by-minute forecasts

4. **NOAA (National Weather Service)**
   - Free US weather data
   - Official alerts
   - Radar data

5. **Weather.gov**
   - Free US weather data
   - Official forecasts
   - Alerts

### Data Aggregation Strategy

**Multi-Source Aggregation:**
- Fetch from multiple providers
- Compare and validate data
- Use weighted average for forecasts
- Prefer authoritative sources for alerts

**Data Normalization:**
- Standardize units
- Normalize data formats
- Handle missing data
- Data quality scoring

**Update Frequency:**
- Current weather: Every 15 minutes
- Forecasts: Every hour
- Alerts: Real-time
- Maps: Every 5-10 minutes

---

## Database Design

### Users Table

```sql
CREATE TABLE users (
    user_id VARCHAR(255) PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    username VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_email (email)
);
```

### User Preferences Table

```sql
CREATE TABLE user_preferences (
    preference_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    temperature_unit VARCHAR(10) DEFAULT 'celsius', -- celsius, fahrenheit
    wind_speed_unit VARCHAR(10) DEFAULT 'kmh', -- kmh, mph, ms
    pressure_unit VARCHAR(10) DEFAULT 'hpa', -- hpa, inHg, mmHg
    language VARCHAR(10) DEFAULT 'en',
    timezone VARCHAR(50),
    notification_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    UNIQUE KEY uk_user_id (user_id)
);
```

### Locations Table

```sql
CREATE TABLE locations (
    location_id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    country_code VARCHAR(2),
    timezone VARCHAR(50),
    elevation INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_coordinates (latitude, longitude),
    INDEX idx_name (name)
);
```

### User Favorite Locations Table

```sql
CREATE TABLE user_favorite_locations (
    favorite_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    location_id VARCHAR(255) NOT NULL,
    display_name VARCHAR(255),
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (location_id) REFERENCES locations(location_id) ON DELETE CASCADE,
    UNIQUE KEY uk_user_location (user_id, location_id),
    INDEX idx_user_id (user_id)
);
```

### Weather Data Table (TimeSeries)

```sql
-- Using PostgreSQL with TimescaleDB extension
CREATE TABLE weather_data (
    time TIMESTAMPTZ NOT NULL,
    location_id VARCHAR(255) NOT NULL,
    temperature DECIMAL(5, 2),
    feels_like DECIMAL(5, 2),
    humidity INTEGER,
    pressure INTEGER,
    wind_speed DECIMAL(5, 2),
    wind_direction INTEGER,
    visibility INTEGER,
    uv_index DECIMAL(3, 1),
    cloud_cover INTEGER,
    weather_code VARCHAR(50),
    weather_description TEXT,
    precipitation DECIMAL(5, 2),
    data_source VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (time, location_id),
    FOREIGN KEY (location_id) REFERENCES locations(location_id)
);

-- Create hypertable for time-series optimization
SELECT create_hypertable('weather_data', 'time');

-- Create indexes
CREATE INDEX idx_location_time ON weather_data(location_id, time DESC);
CREATE INDEX idx_weather_code ON weather_data(weather_code);
```

### Forecasts Table

```sql
CREATE TABLE forecasts (
    forecast_id VARCHAR(255) PRIMARY KEY,
    location_id VARCHAR(255) NOT NULL,
    forecast_type VARCHAR(50) NOT NULL, -- hourly, daily
    forecast_time TIMESTAMPTZ NOT NULL,
    temperature DECIMAL(5, 2),
    feels_like DECIMAL(5, 2),
    humidity INTEGER,
    pressure INTEGER,
    wind_speed DECIMAL(5, 2),
    wind_direction INTEGER,
    precipitation_probability INTEGER,
    precipitation_amount DECIMAL(5, 2),
    weather_code VARCHAR(50),
    weather_description TEXT,
    data_source VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (location_id) REFERENCES locations(location_id),
    INDEX idx_location_forecast (location_id, forecast_time),
    INDEX idx_forecast_time (forecast_time)
);
```

### Weather Alerts Table

```sql
CREATE TABLE weather_alerts (
    alert_id VARCHAR(255) PRIMARY KEY,
    location_id VARCHAR(255) NOT NULL,
    alert_type VARCHAR(50) NOT NULL, -- severe, tornado, flood, etc.
    severity VARCHAR(50) NOT NULL, -- minor, moderate, severe, extreme
    title VARCHAR(255) NOT NULL,
    description TEXT,
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ NOT NULL,
    source VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (location_id) REFERENCES locations(location_id),
    INDEX idx_location_active (location_id, is_active),
    INDEX idx_time_range (start_time, end_time)
);
```

### User Alerts Table

```sql
CREATE TABLE user_alerts (
    user_alert_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    location_id VARCHAR(255) NOT NULL,
    alert_type VARCHAR(50) NOT NULL, -- temperature, precipitation, severe
    condition VARCHAR(255) NOT NULL, -- JSON condition
    is_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (location_id) REFERENCES locations(location_id),
    INDEX idx_user_enabled (user_id, is_enabled)
);
```

---

## API Design

### Weather Endpoints

```
GET    /api/v1/weather/current?lat={lat}&lon={lon}
GET    /api/v1/weather/current?location_id={location_id}
GET    /api/v1/weather/hourly?lat={lat}&lon={lon}&hours={hours}
GET    /api/v1/weather/daily?lat={lat}&lon={lon}&days={days}
GET    /api/v1/weather/alerts?lat={lat}&lon={lon}
GET    /api/v1/weather/historical?lat={lat}&lon={lon}&date={date}
```

### Location Endpoints

```
GET    /api/v1/locations/search?q={query}
GET    /api/v1/locations/geocode?lat={lat}&lon={lon}
POST   /api/v1/locations
GET    /api/v1/locations/{location_id}
```

### User Endpoints

```
GET    /api/v1/users/{user_id}/favorites
POST   /api/v1/users/{user_id}/favorites
DELETE /api/v1/users/{user_id}/favorites/{location_id}
GET    /api/v1/users/{user_id}/preferences
PUT    /api/v1/users/{user_id}/preferences
GET    /api/v1/users/{user_id}/alerts
POST   /api/v1/users/{user_id}/alerts
```

### Map Endpoints

```
GET    /api/v1/maps/radar?lat={lat}&lon={lon}&zoom={zoom}
GET    /api/v1/maps/satellite?lat={lat}&lon={lon}&zoom={zoom}
GET    /api/v1/maps/precipitation?lat={lat}&lon={lon}&zoom={zoom}
```

### Example API Requests/Responses

**Get Current Weather**
```http
GET /api/v1/weather/current?lat=37.7749&lon=-122.4194
Authorization: Bearer {token}

Response: 200 OK
{
  "location": {
    "location_id": "loc_123",
    "name": "San Francisco, CA, US",
    "latitude": 37.7749,
    "longitude": -122.4194
  },
  "current": {
    "temperature": 18.5,
    "feels_like": 17.2,
    "humidity": 65,
    "pressure": 1013,
    "wind_speed": 12.5,
    "wind_direction": 270,
    "visibility": 10000,
    "uv_index": 5.2,
    "cloud_cover": 30,
    "weather": {
      "code": "partly_cloudy",
      "description": "Partly cloudy"
    },
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

**Get Hourly Forecast**
```http
GET /api/v1/weather/hourly?lat=37.7749&lon=-122.4194&hours=24

Response: 200 OK
{
  "location": {...},
  "forecast": [
    {
      "time": "2024-01-15T11:00:00Z",
      "temperature": 19.0,
      "precipitation_probability": 10,
      "weather": {
        "code": "clear",
        "description": "Clear sky"
      }
    },
    ...
  ]
}
```

---

## Caching Strategy

### Cache Layers

1. **CDN Cache** (Edge)
   - Static assets
   - Weather maps
   - TTL: 5-10 minutes

2. **Application Cache** (Redis)
   - Current weather: 15 minutes
   - Hourly forecast: 30 minutes
   - Daily forecast: 1 hour
   - Location data: 24 hours
   - Search results: 1 hour

3. **Database Cache**
   - Query result caching
   - Materialized views

### Cache Keys

```
weather:current:{location_id}
weather:hourly:{location_id}:{hours}
weather:daily:{location_id}:{days}
location:{location_id}
location:search:{query_hash}
map:radar:{lat}:{lon}:{zoom}
```

### Cache Invalidation

- Time-based expiration
- Event-based invalidation (new data available)
- Manual invalidation (admin actions)

---

## Real-Time Updates

### WebSocket Connection

- Real-time weather updates
- Alert notifications
- Map updates

### Server-Sent Events (SSE)

- Simpler than WebSocket
- One-way communication
- Automatic reconnection

### Polling Fallback

- Long polling for updates
- Exponential backoff
- Efficient polling intervals

---

## Location Services

### Geocoding

- Address → Coordinates
- City name → Coordinates
- ZIP code → Coordinates

### Reverse Geocoding

- Coordinates → Address
- Coordinates → City/State/Country

### Location Search

- Fuzzy search
- Autocomplete
- Recent locations
- Popular locations

---

## Notification System

### Notification Types

1. **Severe Weather Alerts**
   - Tornado warnings
   - Flood warnings
   - Severe thunderstorm warnings

2. **Daily Summaries**
   - Morning weather summary
   - Evening forecast

3. **Custom Alerts**
   - Temperature thresholds
   - Precipitation alerts
   - Wind speed alerts

### Notification Channels

- Push notifications
- Email
- SMS (for critical alerts)
- In-app notifications

---

## Scalability Considerations

### Horizontal Scaling

- Stateless services
- Load balancer
- Database read replicas
- Redis cluster
- CDN for static content

### Data Partitioning

- Partition weather data by location
- Partition forecasts by date
- Shard user data by user_id

### Rate Limiting

- Per-user rate limits
- Per-IP rate limits
- Tiered API limits (free, premium)

---

## Monitoring & Analytics

### Key Metrics

**Performance Metrics:**
- API response time
- Cache hit rate
- Data source latency
- Error rate

**Business Metrics:**
- Daily active users
- API requests per user
- Popular locations
- Alert delivery rate

**Data Quality Metrics:**
- Data source availability
- Data freshness
- Data accuracy scores

### Alerting

- High error rate
- Slow response times
- Data source failures
- Cache miss rate spikes

---

## Deployment Strategy

### Infrastructure

- **Containerization**: Docker
- **Orchestration**: Kubernetes
- **CDN**: CloudFlare or AWS CloudFront
- **Database**: PostgreSQL with TimescaleDB

### Multi-Region Deployment

- Regional data centers
- Regional caching
- Data replication
- Route users to nearest region

---

## High-Level Design (HLD)

### System Overview

The Weather Application is a distributed system that aggregates weather data from multiple providers, processes it efficiently, and delivers accurate forecasts to millions of users worldwide. It uses multi-source data aggregation, intelligent caching, and real-time updates.

### HLD Architecture Components

```
┌─────────────────────────────────────────────────────────────────┐
│                    Client Layer                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │   Web    │  │   iOS    │  │ Android  │  │  Widget  │       │
│  │  Client  │  │   App    │  │   App    │  │  Client  │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
└───────┼─────────────┼───────────────┼──────────────┼──────────┘
        │             │               │              │
        └─────────────┴───────────────┴──────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CDN / Edge Network                           │
│  - Static assets caching                                        │
│  - Geographic distribution                                      │
│  - DDoS protection                                              │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              API Gateway / Load Balancer                        │
│  - Request routing                                             │
│  - Rate limiting                                               │
│  - SSL termination                                             │
└───────────────────────────┬─────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│   Region 1    │  │   Region 2    │  │   Region N    │
│  (US-East)    │  │  (EU-West)    │  │  (AP-South)  │
└───────┬───────┘  └───────┬───────┘  └───────┬───────┘
        │                   │                   │
        ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────────────────┐
│              Application Services Layer                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ Weather  │  │ Location │  │   Alert  │  │   Map    │       │
│  │ Service  │  │ Service  │  │ Service  │  │ Service  │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │   User   │  │Historical│ │Notification│ │ Analytics│       │
│  │ Service  │  │ Service  │  │ Service  │  │ Service  │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
└───────┼─────────────┼───────────────┼──────────────┼────────┘
        │             │               │              │
        ▼             ▼               ▼              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Caching Layer                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │  Redis   │  │  Redis   │  │  Redis   │  │  Redis   │       │
│  │(Weather) │ │(Location)│ │(Forecast) │ │(Maps)    │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
└───────┼─────────────┼──────────────┼──────────────┼────────┘
        │             │               │              │
        ▼             ▼               ▼              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Database Layer                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │PostgreSQL│  │PostgreSQL│  │ TimeSeries│ │PostgreSQL│      │
│  │ (Users)  │  │(Locations)│ │  (Weather)│ │ (Alerts) │      │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘      │
└───────┼─────────────┼──────────────┼──────────────┼────────┘
        │             │               │              │
        ▼             ▼               ▼              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Data Ingestion Layer                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ Weather  │  │ Weather  │  │ Weather  │  │   Map    │      │
│  │Provider 1│  │Provider 2│  │Provider 3│  │ Provider │      │
│  │  (API)   │  │  (API)   │  │  (API)   │  │  (API)   │      │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘      │
└───────┼─────────────┼──────────────┼──────────────┼────────┘
        │             │               │              │
        ▼             ▼               ▼              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Message Queue                                 │
│              (Kafka / AWS SQS / RabbitMQ)                       │
└─────────────────────────────────────────────────────────────────┘
```

### Design Principles

- **Data Accuracy**: Multi-source aggregation for reliability
- **Performance**: Sub-200ms response times
- **Scalability**: Handle 100K+ requests per second
- **Cost Efficiency**: Intelligent caching and rate limiting
- **High Availability**: Multi-region active-active deployment

---

## Low-Level Design (LLD)

### Weather Service (Detailed Implementation)

```python
class WeatherService:
    def __init__(self):
        self.providers = [
            OpenWeatherMapProvider(),
            WeatherAPIProvider(),
            AccuWeatherProvider()
        ]
        self.redis = RedisCluster()
        self.db = DatabasePool()
        self.aggregator = WeatherDataAggregator()
    
    async def get_current_weather(
        self, 
        latitude: float, 
        longitude: float
    ) -> WeatherData:
        """Get current weather with multi-source aggregation"""
        location_id = await self.get_location_id(latitude, longitude)
        
        # Check cache first
        cache_key = f"weather:current:{location_id}"
        cached = await self.redis.get(cache_key)
        if cached:
            return WeatherData.from_json(cached)
        
        # Fetch from multiple providers in parallel
        provider_results = await asyncio.gather(
            *[p.get_current_weather(latitude, longitude) 
              for p in self.providers],
            return_exceptions=True
        )
        
        # Filter successful results
        valid_results = [
            r for r in provider_results 
            if not isinstance(r, Exception)
        ]
        
        if not valid_results:
            # All providers failed, use cached data
            return await self.get_cached_weather(location_id)
        
        # Aggregate data from multiple sources
        aggregated = self.aggregator.aggregate(valid_results)
        
        # Cache result
        await self.redis.setex(
            cache_key, 
            900,  # 15 minutes
            aggregated.to_json()
        )
        
        # Store in database for historical analysis
        await self.store_weather_data(location_id, aggregated)
        
        return aggregated
    
    async def get_forecast(
        self,
        latitude: float,
        longitude: float,
        days: int = 7
    ) -> List[ForecastData]:
        """Get weather forecast"""
        location_id = await self.get_location_id(latitude, longitude)
        cache_key = f"weather:forecast:{location_id}:{days}"
        
        # Check cache
        cached = await self.redis.get(cache_key)
        if cached:
            return [ForecastData.from_json(f) for f in json.loads(cached)]
        
        # Fetch from providers
        provider_results = await asyncio.gather(
            *[p.get_forecast(latitude, longitude, days) 
              for p in self.providers],
            return_exceptions=True
        )
        
        valid_results = [
            r for r in provider_results 
            if not isinstance(r, Exception)
        ]
        
        if not valid_results:
            return await self.get_cached_forecast(location_id, days)
        
        # Aggregate forecasts
        aggregated = self.aggregate_forecasts(valid_results)
        
        # Cache
        await self.redis.setex(
            cache_key,
            3600,  # 1 hour
            json.dumps([f.to_json() for f in aggregated])
        )
        
        return aggregated
```

### Weather Data Aggregator (Detailed)

```python
class WeatherDataAggregator:
    def __init__(self):
        self.provider_weights = {
            'openweathermap': 0.4,
            'weatherapi': 0.35,
            'accuweather': 0.25
        }
    
    def aggregate(self, results: List[WeatherData]) -> WeatherData:
        """Aggregate weather data from multiple sources"""
        if len(results) == 1:
            return results[0]
        
        # Weighted average for numerical values
        temperature = self.weighted_average(
            [r.temperature for r in results],
            [self.provider_weights.get(r.source, 0.33) 
             for r in results]
        )
        
        humidity = self.weighted_average(
            [r.humidity for r in results],
            [self.provider_weights.get(r.source, 0.33) 
             for r in results]
        )
        
        # Most common for categorical values
        weather_code = self.most_common(
            [r.weather_code for r in results]
        )
        
        # Average for other metrics
        pressure = sum(r.pressure for r in results) / len(results)
        wind_speed = sum(r.wind_speed for r in results) / len(results)
        
        return WeatherData(
            temperature=temperature,
            humidity=humidity,
            pressure=pressure,
            wind_speed=wind_speed,
            weather_code=weather_code,
            source='aggregated',
            confidence=self.calculate_confidence(results)
        )
    
    def calculate_confidence(self, results: List[WeatherData]) -> float:
        """Calculate confidence score based on agreement"""
        if len(results) < 2:
            return 0.5
        
        # Check temperature agreement
        temps = [r.temperature for r in results]
        temp_variance = np.var(temps)
        temp_agreement = 1.0 / (1.0 + temp_variance / 10.0)
        
        # Check weather code agreement
        codes = [r.weather_code for r in results]
        code_agreement = len(set(codes)) / len(codes)
        
        # Combined confidence
        confidence = (temp_agreement + code_agreement) / 2.0
        return min(1.0, max(0.0, confidence))
```

### Location Service (Detailed)

```python
class LocationService:
    def __init__(self):
        self.redis = RedisCluster()
        self.db = DatabasePool()
        self.geocoding_cache = LRUCache(max_size=10000, ttl=86400)
    
    async def search_locations(self, query: str) -> List[Location]:
        """Search locations by name"""
        # Check cache
        cache_key = f"location:search:{hash(query)}"
        cached = await self.redis.get(cache_key)
        if cached:
            return [Location.from_json(l) for l in json.loads(cached)]
        
        # Search database
        locations = await self.db.search_locations(query)
        
        # If not found, use geocoding API
        if not locations:
            locations = await self.geocode_location(query)
            # Store in database
            for loc in locations:
                await self.db.store_location(loc)
        
        # Cache results
        await self.redis.setex(
            cache_key,
            3600,  # 1 hour
            json.dumps([l.to_json() for l in locations])
        )
        
        return locations
    
    async def geocode_location(self, query: str) -> List[Location]:
        """Geocode location using external API"""
        # Try primary geocoding service
        try:
            return await self.primary_geocoder.geocode(query)
        except APIError:
            # Fallback to secondary
            return await self.fallback_geocoder.geocode(query)
```

---

## Fault Tolerance

### Fault Tolerance Strategy

The system handles failures at multiple levels, ensuring continuous service even when components fail.

### Component-Level Fault Tolerance

#### 1. Weather Provider Failure Tolerance

**Multi-Provider Fallback:**
```python
class FaultTolerantWeatherService:
    def __init__(self):
        self.primary_provider = OpenWeatherMapProvider()
        self.fallback_providers = [
            WeatherAPIProvider(),
            AccuWeatherProvider()
        ]
        self.circuit_breakers = {
            provider.name: CircuitBreaker()
            for provider in [self.primary_provider] + self.fallback_providers
        }
    
    async def get_weather(self, lat, lng):
        # Try primary provider
        if not self.circuit_breakers['openweathermap'].is_open():
            try:
                return await self.primary_provider.get_weather(lat, lng)
            except APIError:
                self.circuit_breakers['openweathermap'].record_failure()
        
        # Try fallback providers
        for provider in self.fallback_providers:
            if not self.circuit_breakers[provider.name].is_open():
                try:
                    return await provider.get_weather(lat, lng)
                except APIError:
                    self.circuit_breakers[provider.name].record_failure()
        
        # All providers failed, use cached data
        return await self.get_cached_weather(lat, lng)
```

#### 2. Database Failure Tolerance

**Read Replicas and Caching:**
```python
class FaultTolerantDatabase:
    def __init__(self):
        self.primary = DatabaseConnection(primary_config)
        self.replicas = [DatabaseConnection(r) for r in replica_configs]
        self.redis = RedisCluster()
    
    async def get_weather_data(self, location_id):
        # Try cache first
        cached = await self.redis.get(f"weather:{location_id}")
        if cached:
            return json.loads(cached)
        
        # Try primary database
        try:
            data = await self.primary.query(
                "SELECT * FROM weather_data WHERE location_id = $1",
                location_id
            )
            # Cache result
            await self.redis.setex(
                f"weather:{location_id}",
                900,
                json.dumps(data)
            )
            return data
        except DatabaseError:
            # Try read replica
            for replica in self.replicas:
                try:
                    return await replica.query(
                        "SELECT * FROM weather_data WHERE location_id = $1",
                        location_id
                    )
                except DatabaseError:
                    continue
            
            # All databases failed, return cached if available
            return await self.redis.get(f"weather:{location_id}") or None
```

#### 3. Cache Failure Tolerance

**Multi-Level Caching:**
```python
class FaultTolerantCache:
    def __init__(self):
        self.redis_primary = RedisCluster(primary_config)
        self.redis_fallback = RedisCluster(fallback_config)
        self.local_cache = LRUCache(max_size=1000, ttl=60)
    
    async def get(self, key):
        # Try local cache
        value = self.local_cache.get(key)
        if value:
            return value
        
        # Try primary Redis
        try:
            value = await self.redis_primary.get(key)
            if value:
                self.local_cache.set(key, value)
                return value
        except RedisError:
            pass
        
        # Try fallback Redis
        try:
            value = await self.redis_fallback.get(key)
            if value:
                self.local_cache.set(key, value)
                return value
        except RedisError:
            pass
        
        return None
```

---

## Failure Safety

### Failure Safety Principles

1. **No Data Loss**: All weather data persisted in multiple places
2. **Graceful Degradation**: System continues with cached data
3. **Automatic Recovery**: System recovers when failures resolve
4. **Data Consistency**: Eventual consistency acceptable for weather data

### Critical Failure Scenarios

#### 1. All Weather Providers Fail

**Problem:** All external weather APIs unavailable.

**Solution:** Multi-layer fallback strategy.

```python
class FailureSafeWeatherService:
    async def get_weather(self, lat, lng):
        # Level 1: Try providers
        try:
            return await self.fetch_from_providers(lat, lng)
        except AllProvidersFailedError:
            pass
        
        # Level 2: Use recent cached data
        cached = await self.get_recent_cache(lat, lng, max_age_hours=6)
        if cached:
            cached['source'] = 'cached'
            cached['age_hours'] = self.calculate_age(cached)
            return cached
        
        # Level 3: Use historical average
        historical = await self.get_historical_average(lat, lng)
        if historical:
            return {
                **historical,
                'source': 'historical',
                'note': 'Using historical average'
            }
        
        # Level 4: Return error with helpful message
        raise WeatherUnavailableError(
            "Weather data temporarily unavailable. Please try again later."
        )
```

#### 2. Database Complete Failure

**Problem:** Database completely unavailable.

**Solution:** Cache-only mode with eventual consistency.

```python
class FailureSafeDatabase:
    async def store_weather_data(self, location_id, data):
        # Always write to cache first (fast)
        await self.redis.setex(
            f"weather:{location_id}",
            900,
            json.dumps(data)
        )
        
        # Try database (may fail)
        try:
            await self.db.insert_weather_data(location_id, data)
        except DatabaseError:
            # Queue for retry
            await self.retry_queue.enqueue(
                'store_weather',
                location_id,
                data
            )
```

#### 3. High Traffic Spikes

**Problem:** Sudden traffic spike overwhelms system.

**Solution:** Rate limiting and queueing.

```python
class TrafficSpikeHandler:
    def __init__(self):
        self.rate_limiter = RateLimiter(
            requests_per_minute=100,
            burst_size=20
        )
        self.request_queue = asyncio.Queue(maxsize=10000)
    
    async def handle_request(self, request):
        # Check rate limit
        if not await self.rate_limiter.allow(request.user_id):
            # Queue request
            await self.request_queue.put(request)
            return {
                'status': 'queued',
                'estimated_wait_seconds': self.estimate_wait_time()
            }
        
        # Process request
        return await self.process_request(request)
```

---

## Optimizations

### Performance Optimizations

#### 1. Aggressive Caching

**Multi-Level Caching:**
```python
class OptimizedWeatherService:
    def __init__(self):
        self.l1_cache = LRUCache(max_size=1000, ttl=60)  # Local
        self.l2_cache = RedisCluster()  # Distributed
        self.l3_cache = CDNCache()  # Edge
    
    async def get_weather(self, lat, lng):
        location_id = await self.get_location_id(lat, lng)
        
        # L1: Local cache
        cached = self.l1_cache.get(location_id)
        if cached:
            return cached
        
        # L2: Redis cache
        cached = await self.l2_cache.get(f"weather:{location_id}")
        if cached:
            self.l1_cache.set(location_id, cached)
            return cached
        
        # L3: CDN cache (for popular locations)
        cached = await self.l3_cache.get(location_id)
        if cached:
            await self.l2_cache.set(f"weather:{location_id}", cached)
            self.l1_cache.set(location_id, cached)
            return cached
        
        # Fetch from providers
        data = await self.fetch_from_providers(lat, lng)
        
        # Update all caches
        self.l1_cache.set(location_id, data)
        await self.l2_cache.setex(
            f"weather:{location_id}",
            900,
            json.dumps(data)
        )
        await self.l3_cache.set(location_id, data, ttl=600)
        
        return data
```

#### 2. Batch Processing

**Batch Location Processing:**
```python
class BatchedLocationProcessor:
    def __init__(self, batch_size=100, flush_interval=5.0):
        self.batch = []
        self.batch_size = batch_size
        self.flush_interval = flush_interval
    
    async def process_location(self, location):
        self.batch.append(location)
        
        if len(self.batch) >= self.batch_size:
            await self.flush()
    
    async def flush(self):
        if not self.batch:
            return
        
        # Batch geocode
        results = await self.geocoder.batch_geocode(self.batch)
        
        # Batch store in database
        await self.db.batch_insert_locations(results)
        
        self.batch.clear()
```

#### 3. Database Query Optimization

**Read Replicas:**
```python
class OptimizedDatabase:
    async def get_weather_data(self, location_id):
        # Use read replica for reads
        async with self.read_replica_pool.acquire() as conn:
            return await conn.fetchrow(
                "SELECT * FROM weather_data WHERE location_id = $1",
                location_id
            )
```

**Connection Pooling:**
```python
class DatabasePool:
    def __init__(self):
        self.pool = asyncpg.create_pool(
            database_url,
            min_size=10,
            max_size=50,
            max_queries=50000
        )
```

#### 4. API Cost Optimization

**Intelligent Rate Limiting:**
```python
class CostOptimizedProvider:
    def __init__(self):
        self.api_calls_today = 0
        self.daily_limit = 100000
        self.cache_hit_rate_target = 0.8
    
    async def get_weather(self, lat, lng):
        # Check if we should use cache instead
        if self.should_use_cache():
            return await self.get_cached_weather(lat, lng)
        
        # Make API call
        if self.api_calls_today < self.daily_limit:
            self.api_calls_today += 1
            return await self.provider.get_weather(lat, lng)
        else:
            # Limit reached, use cache
            return await self.get_cached_weather(lat, lng)
```

---

## Scalability Considerations

### Horizontal Scaling Strategy

#### 1. Service Scaling

**Stateless Services:**
- All state in Redis/Database
- Multiple instances behind load balancer
- Auto-scaling based on load

#### 2. Database Scaling

**Sharding:**
- Shard by location_id
- Read replicas for reads
- Partition by date for historical data

#### 3. Cache Scaling

**Redis Cluster:**
- Shard by location_id
- Consistent hashing
- Replication for high availability

#### 4. CDN Scaling

**Geographic Distribution:**
- Edge locations worldwide
- Cache popular locations
- Reduce origin load

### Capacity Planning

**Traffic Estimates:**
- 50M users
- 100K requests/second
- 10M concurrent users
- 1M unique locations

**Storage Estimates:**
- Weather data: 1M locations × 1KB = 1GB
- Historical data: 1M locations × 24 updates/day × 1KB = 24GB/day
- User data: 50M users × 2KB = 100GB

**Compute Estimates:**
- API servers: 100K req/sec × 200ms = 20K concurrent requests
- Processing: 100K req/sec × 10ms = 1K concurrent operations

---

## Failure Scenarios & Handling

### Weather Provider Failure

**Scenario**: Primary weather provider API fails
**Mitigation**: 
- Fallback to secondary providers
- Use cached data
- Graceful degradation
- Circuit breaker pattern

### Database Failure

**Scenario**: Database becomes unavailable
**Mitigation**:
- Read replicas
- Cache fallback
- Circuit breaker
- Queue operations for retry

### High Traffic

**Scenario**: Sudden traffic spike
**Mitigation**:
- Auto-scaling
- Rate limiting
- CDN caching
- Queue requests
- Graceful degradation

### Cache Failure

**Scenario**: Redis cluster fails
**Mitigation**:
- Fallback to database
- Local caching
- Reduced cache TTL
- Graceful degradation

---

## Trade-offs & Design Decisions

### 1. Data Source Strategy

**Decision**: Multi-source aggregation
**Rationale**: Better accuracy, redundancy

### 2. Cache Strategy

**Decision**: Multi-layer caching
**Rationale**: Balance freshness and performance

### 3. Update Frequency

**Decision**: 15 minutes for current weather
**Rationale**: Balance accuracy and API costs

### 4. Real-Time Updates

**Decision**: WebSocket with polling fallback
**Rationale**: Best user experience with reliability

---

## Interview Discussion Points

1. How do you ensure data accuracy?
2. How do you handle multiple data sources?
3. How do you scale to millions of users?
4. How do you optimize API costs?
5. How do you handle location search at scale?
6. How do you ensure real-time updates?

---

## Technology Stack

### Backend
- **Language**: Go, Python, or Node.js
- **Framework**: Gin (Go), FastAPI (Python), Express (Node.js)
- **Database**: PostgreSQL with TimescaleDB
- **Cache**: Redis
- **Message Queue**: Kafka or RabbitMQ

### Frontend
- **Web**: React, Vue.js
- **Mobile**: React Native, Flutter
- **Maps**: Mapbox, Google Maps

### Infrastructure
- **CDN**: CloudFlare, AWS CloudFront
- **Containerization**: Docker
- **Orchestration**: Kubernetes
- **Monitoring**: Prometheus, Grafana

---

## Conclusion

A well-designed Weather Application requires careful consideration of data sources, caching strategies, real-time updates, and scalability. The system must balance accuracy, performance, and cost while providing an excellent user experience.

Key success factors include:
- Reliable data sources
- Efficient caching
- Scalable architecture
- Real-time capabilities
- Cost optimization
- Excellent user experience

