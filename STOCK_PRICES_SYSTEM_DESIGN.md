# Design a System to View Latest Stock Prices Worldwide

## Table of Contents
1. [Overview](#overview)
2. [Requirements](#requirements)
3. [System Architecture](#system-architecture)
4. [Data Models](#data-models)
5. [API Design](#api-design)
6. [Real-time Data Pipeline](#real-time-data-pipeline)
7. [Price Distribution](#price-distribution)
8. [Scalability Considerations](#scalability-considerations)
9. [Caching Strategy](#caching-strategy)
10. [Load Balancing](#load-balancing)
11. [Security](#security)
12. [Monitoring & Analytics](#monitoring--analytics)
13. [Capacity Planning](#capacity-planning)
14. [Technology Stack](#technology-stack)
15. [Failure Scenarios & Handling](#failure-scenarios--handling)
16. [Trade-offs & Design Decisions](#trade-offs--design-decisions)
17. [Interview Discussion Points](#interview-discussion-points)

---

## Overview

A real-time stock price system that aggregates prices from multiple exchanges worldwide, provides low-latency price updates, supports millions of symbols, and serves price data to millions of users with sub-second latency.

**Key Features:**
- Real-time price updates
- Multi-exchange aggregation
- Historical price data
- Price alerts
- Market data streaming
- Portfolio tracking
- Price charts and analytics

---

## Requirements

### Functional Requirements

1. **Price Data Collection**
   - Collect prices from multiple exchanges
   - Aggregate prices from different sources
   - Handle delayed data (15-minute delay for free tier)

2. **Price Distribution**
   - Real-time price streaming
   - WebSocket connections
   - REST API for price queries

3. **Data Management**
   - Store historical prices
   - Support multiple timeframes (1min, 5min, 1hour, daily)
   - Price normalization across exchanges

### Non-Functional Requirements

1. **Scalability**
   - Support 100K+ stock symbols
   - Handle 1M+ price updates per second
   - Support 10M+ concurrent users
   - Multi-region deployment

2. **Performance**
   - Price update latency: < 100ms
   - Query latency: < 50ms (p95)
   - WebSocket message latency: < 50ms

3. **Reliability**
   - 99.9% uptime
   - No price data loss
   - Handle exchange failures gracefully

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Data Sources (Exchanges)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   NYSE       │  │   NASDAQ     │  │   LSE        │         │
│  │   API        │  │   API        │  │   API        │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────┬───────────────┬───────────────┬───────────────────┘
             │               │               │
             ▼               ▼               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Data Ingestion Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Exchange   │  │   Exchange   │  │   Exchange   │         │
│  │   Adapter 1  │  │   Adapter 2  │  │   Adapter N  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Message Queue                                 │
│              (Kafka)                                            │
│  Topics: price-updates, historical-data                         │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Processing Layer                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Price      │  │   Price      │  │   Aggregator │         │
│  │   Normalizer │  │   Validator  │  │              │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Storage Layer                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Real-time  │  │   Historical │  │   Metadata   │         │
│  │   Prices     │  │   Prices     │  │               │         │
│  │  (Redis)     │  │ (TimescaleDB)│  │ (PostgreSQL)  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Distribution Layer                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   WebSocket  │  │   REST API    │  │   GraphQL     │         │
│  │   Server     │  │   Service    │  │   Service    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                             │
│  (Web Apps, Mobile Apps, Trading Platforms)                     │
└────────────────────────────────────────────────────────────────┘
```

---

## Data Models

### Price Update Structure

```json
{
  "symbol": "AAPL",
  "exchange": "NASDAQ",
  "price": 150.25,
  "change": 2.50,
  "change_percent": 1.69,
  "volume": 50000000,
  "timestamp": 1705312800000,
  "bid": 150.24,
  "ask": 150.26,
  "high": 151.00,
  "low": 149.50,
  "open": 149.75,
  "previous_close": 147.75
}
```

### Database Schema

#### Real-time Prices (Redis)

```
Key: price:{symbol}
Type: Hash
Fields:
  - price: 150.25
  - change: 2.50
  - change_percent: 1.69
  - volume: 50000000
  - timestamp: 1705312800000
  - exchange: NASDAQ
```

#### Historical Prices (TimescaleDB)

```sql
CREATE TABLE stock_prices (
    time TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(10) NOT NULL,
    exchange VARCHAR(20) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    volume BIGINT,
    high DECIMAL(10, 2),
    low DECIMAL(10, 2),
    open DECIMAL(10, 2),
    close DECIMAL(10, 2),
    PRIMARY KEY (time, symbol, exchange)
);

SELECT create_hypertable('stock_prices', 'time');

CREATE INDEX idx_symbol_time ON stock_prices (symbol, time DESC);
```

#### Symbols Metadata (PostgreSQL)

```sql
CREATE TABLE symbols (
    symbol VARCHAR(10) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    exchange VARCHAR(20) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    sector VARCHAR(100),
    industry VARCHAR(100),
    market_cap BIGINT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_exchange (exchange),
    INDEX idx_sector (sector)
);
```

---

## API Design

### REST API

```
GET /api/v1/prices/{symbol}
GET /api/v1/prices?symbols=AAPL,GOOGL,MSFT
GET /api/v1/prices/history/{symbol}?start_time={start}&end_time={end}&interval=1m
GET /api/v1/symbols/search?q={query}
```

**Response:**
```json
{
  "symbol": "AAPL",
  "price": 150.25,
  "change": 2.50,
  "change_percent": 1.69,
  "volume": 50000000,
  "timestamp": 1705312800000,
  "exchange": "NASDAQ"
}
```

### WebSocket API

```javascript
// Connect
ws = new WebSocket("wss://api.example.com/prices/stream");

// Subscribe to symbols
ws.send(JSON.stringify({
  "action": "subscribe",
  "symbols": ["AAPL", "GOOGL", "MSFT"]
}));

// Receive updates
ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  console.log(`${update.symbol}: $${update.price}`);
};
```

---

## Real-time Data Pipeline

### Data Flow

1. **Exchange APIs** send price updates
2. **Adapters** normalize data format
3. **Kafka** buffers updates
4. **Processors** validate and aggregate
5. **Redis** stores latest prices
6. **TimescaleDB** stores historical data
7. **WebSocket** pushes to clients

### Price Aggregation

```python
class PriceAggregator:
    def aggregate_prices(self, symbol: str, prices: list) -> dict:
        # Get prices from multiple exchanges
        valid_prices = [p for p in prices if p['timestamp'] > time.time() - 60]
        
        if not valid_prices:
            return None
        
        # Weighted average by volume
        total_volume = sum(p['volume'] for p in valid_prices)
        weighted_price = sum(
            p['price'] * p['volume'] for p in valid_prices
        ) / total_volume
        
        return {
            'symbol': symbol,
            'price': weighted_price,
            'volume': total_volume,
            'exchanges': len(valid_prices),
            'timestamp': time.time()
        }
```

---

## Price Distribution

### WebSocket Distribution

```python
class PriceStreamManager:
    def __init__(self):
        self.connections = {}  # symbol -> set of connections
        self.redis = Redis()
    
    def subscribe(self, connection, symbols: list):
        for symbol in symbols:
            if symbol not in self.connections:
                self.connections[symbol] = set()
            self.connections[symbol].add(connection)
    
    def publish_price_update(self, symbol: str, price_data: dict):
        # Update Redis
        self.redis.hset(f"price:{symbol}", mapping=price_data)
        
        # Push to subscribed connections
        if symbol in self.connections:
            message = json.dumps({
                'symbol': symbol,
                'price': price_data['price'],
                'timestamp': price_data['timestamp']
            })
            for connection in self.connections[symbol]:
                try:
                    connection.send(message)
                except:
                    # Remove dead connections
                    self.connections[symbol].remove(connection)
```

---

## Scalability Considerations

- **Horizontal Scaling**: Multiple processors and WebSocket servers
- **Kafka Partitioning**: Partition by symbol for ordering
- **Redis Cluster**: Distribute price data across nodes
- **CDN**: Cache static price data
- **Geographic Distribution**: Deploy in multiple regions

---

## Caching Strategy

- **Real-time Prices**: Redis (TTL: 1 minute)
- **Historical Queries**: Cache frequent queries (TTL: 5 minutes)
- **Symbol Metadata**: Cache symbol info (TTL: 1 hour)

---

## Capacity Planning

- **Symbols**: 100K symbols
- **Updates per Second**: 1M updates/second
- **Concurrent Users**: 10M users
- **WebSocket Connections**: 1M connections
- **Storage**: 1KB per price × 1M/sec × 86,400 = 86.4TB/day

---

## Technology Stack

- **Backend**: Go, Java
- **Message Queue**: Kafka
- **Real-time Storage**: Redis Cluster
- **Historical Storage**: TimescaleDB
- **WebSocket**: Socket.io, ws (Node.js)

---

## High-Level Design (HLD)

### System Overview

The stock prices system follows a real-time stream processing architecture:

1. **Data Sources**: Multiple stock exchanges (NYSE, NASDAQ, LSE, etc.)
2. **Ingestion Layer**: Exchange adapters, data normalization
3. **Message Queue**: Buffers price updates (Kafka)
4. **Processing Layer**: Price validation, aggregation, normalization
5. **Storage Layer**: Redis for real-time, TimescaleDB for historical
6. **Distribution Layer**: WebSocket for real-time, REST API for queries

### Component Architecture

**Core Components:**
- **Exchange Adapters**: Normalize data from different exchanges
- **Price Aggregator**: Aggregates prices from multiple exchanges
- **Price Validator**: Validates price data
- **Stream Manager**: Manages WebSocket connections

---

## Low-Level Design (LLD)

### Price Aggregator Implementation

```python
class PriceAggregator:
    def __init__(self, redis_client, timescale_client):
        self.redis = redis_client
        self.timescale = timescale_client
    
    def aggregate_price(self, symbol: str, prices: list) -> dict:
        # Filter valid prices (within last 60 seconds)
        valid_prices = [
            p for p in prices 
            if time.time() - p['timestamp'] < 60
        ]
        
        if not valid_prices:
            return None
        
        # Weighted average by volume
        total_volume = sum(p['volume'] for p in valid_prices)
        weighted_price = sum(
            p['price'] * p['volume'] for p in valid_prices
        ) / total_volume
        
        aggregated = {
            'symbol': symbol,
            'price': weighted_price,
            'volume': total_volume,
            'exchanges': len(valid_prices),
            'timestamp': time.time()
        }
        
        # Update Redis
        self.redis.hset(f"price:{symbol}", mapping=aggregated)
        
        # Store in TimescaleDB (async)
        self.timescale.execute_async(
            """
            INSERT INTO stock_prices (time, symbol, exchange, price, volume)
            VALUES (?, ?, ?, ?, ?)
            """,
            [datetime.utcnow(), symbol, 'aggregated', weighted_price, total_volume]
        )
        
        return aggregated
```

### WebSocket Stream Manager

```python
class PriceStreamManager:
    def __init__(self, redis_client):
        self.connections = {}  # symbol -> set of connections
        self.redis = redis_client
    
    def subscribe(self, connection, symbols: list):
        for symbol in symbols:
            if symbol not in self.connections:
                self.connections[symbol] = set()
            self.connections[symbol].add(connection)
    
    def publish_price_update(self, symbol: str, price_data: dict):
        # Update Redis
        self.redis.hset(f"price:{symbol}", mapping=price_data)
        
        # Push to subscribed connections
        if symbol in self.connections:
            message = json.dumps({
                'symbol': symbol,
                'price': price_data['price'],
                'timestamp': price_data['timestamp']
            })
            
            dead_connections = []
            for connection in self.connections[symbol]:
                try:
                    connection.send(message)
                except Exception:
                    dead_connections.append(connection)
            
            # Remove dead connections
            for conn in dead_connections:
                self.connections[symbol].remove(conn)
```

---

## Fault Tolerance

### Exchange Adapter Resilience

**Multiple Adapters:**
- Separate adapter per exchange
- Independent failure handling
- Retry with exponential backoff

**Data Validation:**
- Validate price data
- Handle missing data
- Fallback to cached prices

### Storage Resilience

**Redis Cluster:**
- Redis Cluster with replication
- Automatic failover
- Data sharded by symbol

**Database Resilience:**
- TimescaleDB replication
- Read from replicas
- Automatic failover

---

## Optimizations

### Processing Optimization

**Batching:**
- Batch price updates
- Reduce Redis operations
- Improve throughput

**Caching:**
- Cache exchange rates
- Cache symbol metadata
- Reduce database queries

### Query Optimization

**Indexing:**
- Index on `symbol, time`
- Optimize time-range queries
- Use materialized views

---

## Failure Safety

### Exchange Failure

**Scenario: Exchange API Down**
- **Impact**: Prices not updated for that exchange
- **Mitigation**:
  - Multiple exchanges per symbol
  - Use other exchanges
  - Serve cached prices
- **Recovery**:
  - Exchange recovers
  - Resume price collection
  - Verify data consistency

### WebSocket Failure

**Scenario: WebSocket Service Down**
- **Impact**: Real-time updates unavailable
- **Mitigation**:
  - Multiple WebSocket servers
  - Fallback to polling
  - Retry connection
- **Recovery**:
  - Service recovers
  - Clients reconnect
  - Resume real-time updates

---

## Scalability

### Horizontal Scaling

**Adapter Scaling:**
- Multiple adapter instances per exchange
- Process in parallel
- Scale independently

**Processing Scaling:**
- Multiple aggregator instances
- Kafka partitions for parallel processing
- Scale based on load

### Performance Scaling

**Throughput Scaling:**
- Increase Kafka partitions
- Add more processing instances
- Optimize batch sizes

**Latency Optimization:**
- Reduce processing time
- Optimize Redis operations
- Use CDN for API responses

---

## Interview Discussion Points

1. **Real-time Updates**: How do you push updates to millions of users?
2. **Data Aggregation**: How do you aggregate prices from multiple exchanges?
3. **Scalability**: How do you handle 1M+ updates per second?
4. **Latency**: How do you minimize latency?

---

**Document Version**: 1.0  
**Last Updated**: January 2024

