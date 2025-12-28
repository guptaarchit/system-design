# Facebook Marketplace System Design

## Table of Contents
1. [Overview](#overview)
2. [Requirements](#requirements)
3. [System Architecture](#system-architecture)
4. [Core Components](#core-components)
5. [Database Design](#database-design)
6. [API Design](#api-design)
7. [Search & Discovery](#search--discovery)
8. [Recommendation System](#recommendation-system)
9. [Messaging System](#messaging-system)
10. [Payment Processing](#payment-processing)
11. [Image Storage & Processing](#image-storage--processing)
12. [Scalability Considerations](#scalability-considerations)
13. [Monitoring & Analytics](#monitoring--analytics)
14. [Deployment Strategy](#deployment-strategy)
15. [Failure Scenarios & Handling](#failure-scenarios--handling)
16. [Trade-offs & Design Decisions](#trade-offs--design-decisions)
17. [Interview Discussion Points](#interview-discussion-points)

---

## Overview

A comprehensive Marketplace System for Facebook that enables users to buy and sell items locally and globally. The system supports product listings, search, recommendations, messaging, payments, and various marketplace features similar to Facebook Marketplace, eBay, or Craigslist.

**Key Features:**
- Product listing creation and management
- Advanced search and filtering
- Location-based discovery
- Product recommendations
- Buyer-seller messaging
- Payment processing
- Order management
- Reviews and ratings
- Saved searches and favorites
- Category browsing
- Image upload and management
- Shipping and delivery options

---

## Requirements

### Functional Requirements

1. **Product Listings**
   - Create, edit, delete listings
   - Multiple images per listing
   - Product categories
   - Price and currency
   - Location (city, state, country)
   - Product description
   - Condition (new, used, etc.)
   - Availability status
   - Listing expiration

2. **Search & Discovery**
   - Full-text search
   - Category filtering
   - Price range filtering
   - Location-based search
   - Distance-based sorting
   - Date-based sorting
   - Price sorting
   - Relevance sorting

3. **User Features**
   - User profiles
   - Seller profiles
   - Saved listings (favorites)
   - Saved searches
   - Purchase history
   - Selling history
   - Watchlist

4. **Messaging**
   - Buyer-seller communication
   - In-app messaging
   - Message notifications
   - File/image sharing in messages

5. **Transactions**
   - Order creation
   - Payment processing
   - Order tracking
   - Order cancellation
   - Refund processing
   - Shipping integration

6. **Reviews & Ratings**
   - Product reviews
   - Seller ratings
   - Buyer ratings
   - Review moderation

7. **Notifications**
   - New message notifications
   - Price drop alerts
   - Listing expiration reminders
   - Order updates
   - Saved search matches

8. **Moderation**
   - Content moderation
   - Spam detection
   - Fraud detection
   - Report and flag system

### Non-Functional Requirements

1. **Scalability**
   - Support 100M+ listings
   - Handle 10M+ daily active users
   - Support 1M+ concurrent users
   - Handle 100K+ searches per second
   - Multi-region deployment
   - 99.9% uptime

2. **Performance**
   - Search results: < 200ms (p95)
   - Listing load: < 300ms
   - Image load: < 500ms
   - Message delivery: < 100ms
   - 99th percentile latency < 1s

3. **Availability**
   - Multi-region active-active
   - Automatic failover
   - Data replication
   - Zero-downtime deployments

4. **Reliability**
   - No data loss
   - Transaction consistency
   - Message delivery guarantee
   - Image availability

5. **Security**
   - Secure payment processing
   - Fraud detection
   - Content moderation
   - User verification
   - Data privacy (GDPR)

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Applications                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │   Web    │  │   iOS    │  │ Android  │  │   API    │  │
│  │  Client  │  │   App    │  │   App    │  │  Client  │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
└───────┼─────────────┼──────────────┼──────────────┼────────┘
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
│  │ Listing  │  │  Search  │  │Recommendation│ │ Messaging│ │
│  │ Service  │  │ Service  │  │  Service  │  │ Service  │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  Order   │  │ Payment  │  │   User   │  │  Image   │  │
│  │ Service  │  │ Service  │  │ Service  │  │ Service  │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Review   │  │Notification│ │ Moderation│ │ Analytics│  │
│  │ Service  │  │ Service  │  │ Service  │  │ Service  │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
└───────┼─────────────┼──────────────┼──────────────┼────────┘
        │             │               │              │
        ▼             ▼               ▼              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Caching Layer                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Redis   │  │  Redis   │  │  Redis   │  │  Redis   │   │
│  │(Listings)│ │(Search)  │ │(User Data)│ │(Sessions)│   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼──────────────┼──────────────┼────────┘
        │             │               │              │
        ▼             ▼               ▼              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Database Layer                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │PostgreSQL│  │PostgreSQL│  │Elasticsearch│ │PostgreSQL│   │
│  │(Listings)│ │(Orders)  │ │  (Search)  │ │(Messages)│   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼──────────────┼──────────────┼────────┘
        │             │               │              │
        ▼             ▼               ▼              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Storage Layer                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   S3     │  │   S3     │  │   S3     │  │   CDN    │   │
│  │(Images)  │ │(Thumbnails)│ │(Documents)│ │(Delivery)│   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Component Details

#### 1. Listing Service
- Create, update, delete listings
- Listing metadata management
- Category management
- Availability management

#### 2. Search Service
- Full-text search
- Filtering and sorting
- Faceted search
- Search result ranking

#### 3. Recommendation Service
- Personalized recommendations
- Similar items
- Trending items
- Category recommendations

#### 4. Messaging Service
- Real-time messaging
- Message history
- File sharing
- Read receipts

#### 5. Order Service
- Order creation and management
- Order tracking
- Order cancellation
- Order history

#### 6. Payment Service
- Payment processing
- Refund processing
- Payment method management
- Transaction history

#### 7. Image Service
- Image upload
- Image processing (resize, optimize)
- Thumbnail generation
- CDN delivery

#### 8. Review Service
- Review creation
- Rating calculation
- Review moderation
- Review display

### HLD Component Breakdown

**1. Client Layer**
- **Web App**: React-based web application
- **Mobile Apps**: iOS/Android native apps
- **Admin Portal**: React-based admin dashboard

**2. API Gateway Layer**
- **API Gateway**: Routes requests to services
- **Load Balancer**: Distributes traffic
- **CDN**: Serves static assets and images

**3. Service Layer**
- **Listing Service**: Manages product listings
- **Search Service**: Handles search queries
- **Recommendation Service**: Generates recommendations
- **Messaging Service**: Manages buyer-seller communication
- **Order Service**: Handles orders
- **Payment Service**: Processes payments

**4. Processing Layer**
- **Image Processor**: Processes uploaded images
- **Search Indexer**: Indexes listings for search
- **Recommendation Engine**: Generates recommendations

**5. Data Layer**
- **PostgreSQL**: Listings, orders, users
- **Elasticsearch**: Search index
- **Redis**: Cache, sessions
- **S3**: Image storage

---

## Low-Level Design (LLD)

### Listing Service LLD

```python
class ListingService:
    def __init__(self, db: Database, cache: RedisCache, s3: S3Client, 
                 search_indexer: SearchIndexer):
        self.db = db
        self.cache = cache
        self.s3 = s3
        self.search_indexer = search_indexer
    
    def create_listing(self, seller_id: int, listing_data: dict) -> Listing:
        # Create listing record
        listing = Listing.create(
            seller_id=seller_id,
            title=listing_data['title'],
            description=listing_data['description'],
            category_id=listing_data['category_id'],
            price=listing_data['price'],
            status='active'
        )
        
        # Upload images
        image_urls = []
        for image in listing_data.get('images', []):
            url = self.s3.upload_image(image, listing.id)
            image_urls.append(url)
        
        # Update listing with image URLs
        listing.images = image_urls
        listing.save()
        
        # Index in Elasticsearch
        self.search_indexer.index_listing(listing)
        
        # Cache listing
        self.cache.set(f"listing:{listing.id}", listing.to_dict(), ttl=3600)
        
        return listing
```

### Search Service LLD

```python
class SearchService:
    def __init__(self, elasticsearch: ElasticsearchClient, cache: RedisCache):
        self.es = elasticsearch
        self.cache = cache
    
    def search_listings(self, query: str, filters: dict, page: int = 1, 
                      page_size: int = 20) -> SearchResult:
        # Generate cache key
        cache_key = self._generate_cache_key(query, filters, page, page_size)
        
        # Check cache
        cached = self.cache.get(cache_key)
        if cached:
            return SearchResult.from_dict(cached)
        
        # Build Elasticsearch query
        es_query = {
            'bool': {
                'must': [
                    {
                        'multi_match': {
                            'query': query,
                            'fields': ['title^3', 'description'],
                            'type': 'best_fields'
                        }
                    }
                ],
                'filter': self._build_filters(filters)
            }
        }
        
        # Execute search
        response = self.es.search(
            index='listings',
            body={
                'query': es_query,
                'from': (page - 1) * page_size,
                'size': page_size,
                'sort': self._build_sort(filters.get('sort'))
            }
        )
        
        # Process results
        listings = [self._parse_hit(hit) for hit in response['hits']['hits']]
        total = response['hits']['total']['value']
        
        result = SearchResult(listings=listings, total=total, page=page, page_size=page_size)
        
        # Cache result
        self.cache.set(cache_key, result.to_dict(), ttl=300)
        
        return result
```

### Messaging Service LLD

```python
class MessagingService:
    def __init__(self, db: Database, websocket_manager: WebSocketManager, 
                 redis_pubsub: RedisPubSub):
        self.db = db
        self.websocket_manager = websocket_manager
        self.redis_pubsub = redis_pubsub
    
    def send_message(self, conversation_id: str, sender_id: int, content: str) -> Message:
        # Create message record
        message = Message.create(
            conversation_id=conversation_id,
            sender_id=sender_id,
            content=content
        )
        
        # Get conversation
        conversation = Conversation.get(conversation_id)
        
        # Update conversation metadata
        conversation.last_message_at = datetime.utcnow()
        conversation.last_message_preview = content[:100]
        
        # Update unread count
        recipient_id = conversation.buyer_id if sender_id == conversation.seller_id else conversation.seller_id
        if recipient_id == conversation.buyer_id:
            conversation.buyer_unread_count += 1
        else:
            conversation.seller_unread_count += 1
        
        conversation.save()
        
        # Send via WebSocket
        self.websocket_manager.send_to_user(recipient_id, {
            'type': 'new_message',
            'conversation_id': conversation_id,
            'message': message.to_dict()
        })
        
        # Publish to Redis Pub/Sub for cross-server communication
        self.redis_pubsub.publish(f"conversation:{conversation_id}", message.to_dict())
        
        return message
```

---

## Fault Tolerance

### Service-Level Fault Tolerance

**1. Circuit Breaker Pattern**
- **Search Service**: Circuit breaker for Elasticsearch
- **Payment Service**: Circuit breaker for payment gateways
- **Image Service**: Circuit breaker for S3

**2. Retry Logic**
- **Database Operations**: Retry with exponential backoff
- **External APIs**: Retry failed API calls
- **Message Queue**: Retry failed message processing

**3. Bulkhead Pattern**
- **Isolate Services**: Separate thread pools per service
- **Resource Limits**: Limit resources per service
- **Failure Isolation**: Prevent cascading failures

### Database Fault Tolerance

**1. Database Replication**
- **PostgreSQL**: Primary-replica setup
- **Read Replicas**: Scale reads independently
- **Automatic Failover**: Promote replica on primary failure

**2. Elasticsearch Cluster**
- **Multiple Nodes**: Deploy cluster with 3+ nodes
- **Replication**: Replicate indices
- **Sharding**: Shard indices for performance

---

## Failure Safety

### Failure Scenarios & Handling

**1. Search Service Failure**

**Scenario**: Elasticsearch cluster fails.

**Impact**: Cannot search listings.

**Mitigation**:
- **Elasticsearch Cluster**: Multiple nodes with replication
- **Database Fallback**: Fallback to database search (slower)
- **Cached Results**: Serve cached search results
- **Circuit Breaker**: Prevent cascading failures

**Recovery**:
- **Cluster Recovery**: Restart failed nodes
- **Index Recovery**: Rebuild indices from database
- **Cache Warming**: Pre-populate cache

**2. Payment Service Failure**

**Scenario**: Payment processor down.

**Impact**: Cannot process payments.

**Mitigation**:
- **Queue Payments**: Queue payment requests
- **Retry Mechanism**: Retry with exponential backoff
- **Multiple Providers**: Failover to secondary provider
- **Graceful Degradation**: Allow order creation, process payment async

**Recovery**:
- **Service Recovery**: Restart payment service
- **Payment Retry**: Retry queued payments
- **Manual Processing**: Manual intervention if needed

**3. Image Service Failure**

**Scenario**: S3 or image processing fails.

**Impact**: Cannot upload/process images.

**Mitigation**:
- **S3 Replication**: Replicate across regions
- **Local Buffering**: Buffer uploads locally
- **Retry Logic**: Retry failed uploads
- **Fallback**: Use alternative storage

**Recovery**:
- **Service Recovery**: Restart image service
- **Upload Retry**: Retry failed uploads
- **Data Sync**: Sync data from backup

---

## Core Components

### Search Architecture

**Search Flow:**
1. User enters search query
2. Parse and normalize query
3. Check cache
4. Query Elasticsearch
5. Apply filters
6. Rank results
7. Return paginated results
8. Cache results

**Search Features:**
- Full-text search on title, description
- Category filtering
- Price range filtering
- Location filtering
- Distance-based sorting
- Relevance ranking
- Faceted search

### Recommendation System

**Recommendation Types:**
1. **Collaborative Filtering**: Based on similar users
2. **Content-Based**: Based on item similarity
3. **Hybrid**: Combine both approaches
4. **Location-Based**: Nearby items
5. **Trending**: Popular items

**Recommendation Pipeline:**
1. Collect user behavior data
2. Generate candidate items
3. Score and rank candidates
4. Apply business rules
5. Return top N recommendations

---

## Database Design

### Listings Table

```sql
CREATE TABLE listings (
    listing_id VARCHAR(255) PRIMARY KEY,
    seller_id VARCHAR(255) NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    category_id VARCHAR(255) NOT NULL,
    subcategory_id VARCHAR(255),
    price DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    condition VARCHAR(50) NOT NULL, -- new, used, refurbished
    status VARCHAR(50) DEFAULT 'active', -- active, sold, expired, deleted
    location_latitude DECIMAL(10, 8),
    location_longitude DECIMAL(11, 8),
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(2),
    zip_code VARCHAR(20),
    shipping_available BOOLEAN DEFAULT FALSE,
    local_pickup_only BOOLEAN DEFAULT FALSE,
    view_count INTEGER DEFAULT 0,
    favorite_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    sold_at TIMESTAMP,
    FOREIGN KEY (seller_id) REFERENCES users(user_id),
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    INDEX idx_seller (seller_id),
    INDEX idx_category (category_id),
    INDEX idx_status (status),
    INDEX idx_location (location_latitude, location_longitude),
    INDEX idx_created_at (created_at DESC),
    INDEX idx_price (price),
    FULLTEXT INDEX ft_title_description (title, description)
);
```

### Listing Images Table

```sql
CREATE TABLE listing_images (
    image_id VARCHAR(255) PRIMARY KEY,
    listing_id VARCHAR(255) NOT NULL,
    image_url VARCHAR(500) NOT NULL,
    thumbnail_url VARCHAR(500),
    image_order INTEGER DEFAULT 0,
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (listing_id) REFERENCES listings(listing_id) ON DELETE CASCADE,
    INDEX idx_listing (listing_id),
    INDEX idx_order (listing_id, image_order)
);
```

### Categories Table

```sql
CREATE TABLE categories (
    category_id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    parent_id VARCHAR(255),
    level INTEGER DEFAULT 1,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES categories(category_id),
    INDEX idx_parent (parent_id)
);
```

### Orders Table

```sql
CREATE TABLE orders (
    order_id VARCHAR(255) PRIMARY KEY,
    listing_id VARCHAR(255) NOT NULL,
    buyer_id VARCHAR(255) NOT NULL,
    seller_id VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(50) DEFAULT 'pending', -- pending, paid, shipped, delivered, cancelled, refunded
    payment_method VARCHAR(50),
    payment_id VARCHAR(255),
    shipping_address TEXT,
    tracking_number VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (listing_id) REFERENCES listings(listing_id),
    FOREIGN KEY (buyer_id) REFERENCES users(user_id),
    FOREIGN KEY (seller_id) REFERENCES users(user_id),
    INDEX idx_buyer (buyer_id),
    INDEX idx_seller (seller_id),
    INDEX idx_status (status)
);
```

### Messages Table

```sql
CREATE TABLE messages (
    message_id VARCHAR(255) PRIMARY KEY,
    conversation_id VARCHAR(255) NOT NULL,
    sender_id VARCHAR(255) NOT NULL,
    recipient_id VARCHAR(255) NOT NULL,
    listing_id VARCHAR(255),
    content TEXT NOT NULL,
    message_type VARCHAR(50) DEFAULT 'text', -- text, image, file
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id) REFERENCES users(user_id),
    FOREIGN KEY (recipient_id) REFERENCES users(user_id),
    FOREIGN KEY (listing_id) REFERENCES listings(listing_id),
    INDEX idx_conversation (conversation_id, created_at),
    INDEX idx_recipient_unread (recipient_id, is_read)
);
```

### Conversations Table

```sql
CREATE TABLE conversations (
    conversation_id VARCHAR(255) PRIMARY KEY,
    listing_id VARCHAR(255),
    buyer_id VARCHAR(255) NOT NULL,
    seller_id VARCHAR(255) NOT NULL,
    last_message_at TIMESTAMP,
    last_message_preview TEXT,
    buyer_unread_count INTEGER DEFAULT 0,
    seller_unread_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (listing_id) REFERENCES listings(listing_id),
    FOREIGN KEY (buyer_id) REFERENCES users(user_id),
    FOREIGN KEY (seller_id) REFERENCES users(user_id),
    UNIQUE KEY uk_listing_buyer_seller (listing_id, buyer_id, seller_id),
    INDEX idx_buyer (buyer_id),
    INDEX idx_seller (seller_id)
);
```

### Reviews Table

```sql
CREATE TABLE reviews (
    review_id VARCHAR(255) PRIMARY KEY,
    order_id VARCHAR(255) NOT NULL,
    reviewer_id VARCHAR(255) NOT NULL,
    reviewee_id VARCHAR(255) NOT NULL,
    listing_id VARCHAR(255) NOT NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    is_verified_purchase BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (reviewer_id) REFERENCES users(user_id),
    FOREIGN KEY (reviewee_id) REFERENCES users(user_id),
    FOREIGN KEY (listing_id) REFERENCES listings(listing_id),
    UNIQUE KEY uk_order_reviewer (order_id, reviewer_id),
    INDEX idx_reviewee (reviewee_id),
    INDEX idx_listing (listing_id)
);
```

### User Favorites Table

```sql
CREATE TABLE user_favorites (
    favorite_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    listing_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (listing_id) REFERENCES listings(listing_id) ON DELETE CASCADE,
    UNIQUE KEY uk_user_listing (user_id, listing_id),
    INDEX idx_user (user_id)
);
```

### Saved Searches Table

```sql
CREATE TABLE saved_searches (
    search_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    query TEXT,
    filters JSONB,
    location_latitude DECIMAL(10, 8),
    location_longitude DECIMAL(11, 8),
    radius INTEGER, -- in kilometers
    notification_enabled BOOLEAN DEFAULT TRUE,
    last_notified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user (user_id)
);
```

---

## API Design

### Listing Endpoints

```
GET    /api/v1/listings
POST   /api/v1/listings
GET    /api/v1/listings/{listing_id}
PUT    /api/v1/listings/{listing_id}
DELETE /api/v1/listings/{listing_id}
POST   /api/v1/listings/{listing_id}/images
DELETE /api/v1/listings/{listing_id}/images/{image_id}
GET    /api/v1/listings/{listing_id}/similar
```

### Search Endpoints

```
GET    /api/v1/search?q={query}
GET    /api/v1/search/listings?q={query}&category={cat}&price_min={min}&price_max={max}
GET    /api/v1/search/nearby?lat={lat}&lon={lon}&radius={radius}
```

### Recommendation Endpoints

```
GET    /api/v1/recommendations
GET    /api/v1/recommendations/for-listing/{listing_id}
GET    /api/v1/recommendations/trending
```

### Order Endpoints

```
POST   /api/v1/orders
GET    /api/v1/orders
GET    /api/v1/orders/{order_id}
PUT    /api/v1/orders/{order_id}/status
POST   /api/v1/orders/{order_id}/cancel
```

### Messaging Endpoints

```
GET    /api/v1/conversations
GET    /api/v1/conversations/{conversation_id}/messages
POST   /api/v1/conversations/{conversation_id}/messages
PUT    /api/v1/messages/{message_id}/read
```

### Example API Requests/Responses

**Create Listing**
```http
POST /api/v1/listings
Content-Type: application/json
Authorization: Bearer {token}

{
  "title": "iPhone 13 Pro Max",
  "description": "Like new condition, 256GB",
  "category_id": "electronics",
  "subcategory_id": "phones",
  "price": 800.00,
  "currency": "USD",
  "condition": "used",
  "location": {
    "latitude": 37.7749,
    "longitude": -122.4194,
    "city": "San Francisco",
    "state": "CA",
    "country": "US"
  },
  "shipping_available": true
}

Response: 201 Created
{
  "listing_id": "lst_123",
  "title": "iPhone 13 Pro Max",
  "status": "active",
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Search Listings**
```http
GET /api/v1/search/listings?q=iphone&category=electronics&price_min=500&price_max=1000&lat=37.7749&lon=-122.4194&radius=50

Response: 200 OK
{
  "results": [
    {
      "listing_id": "lst_123",
      "title": "iPhone 13 Pro Max",
      "price": 800.00,
      "distance": 5.2,
      "images": ["https://..."],
      "seller": {
        "user_id": "usr_456",
        "name": "John Doe",
        "rating": 4.8
      }
    }
  ],
  "total": 150,
  "page": 1,
  "page_size": 20
}
```

---

## Search & Discovery

### Elasticsearch Index Structure

```json
{
  "mappings": {
    "properties": {
      "listing_id": {"type": "keyword"},
      "title": {"type": "text", "analyzer": "standard"},
      "description": {"type": "text", "analyzer": "standard"},
      "category_id": {"type": "keyword"},
      "price": {"type": "float"},
      "location": {"type": "geo_point"},
      "status": {"type": "keyword"},
      "created_at": {"type": "date"}
    }
  }
}
```

### Search Ranking

**Factors:**
- Relevance score (text match)
- Distance (for location-based)
- Recency
- Seller rating
- Price competitiveness
- View count

---

## Recommendation System

### Collaborative Filtering

- Find similar users
- Recommend items liked by similar users
- Matrix factorization
- Real-time recommendations

### Content-Based Filtering

- Analyze item features
- Find similar items
- Category-based recommendations
- Price-based recommendations

---

## Messaging System

### Real-Time Messaging

- WebSocket for real-time delivery
- Message queue for reliability
- Read receipts
- Typing indicators
- Message history

### Message Flow

1. User sends message
2. Store in database
3. Push to recipient via WebSocket
4. If offline, queue for delivery
5. Send push notification
6. Update conversation metadata

---

## Payment Processing

### Payment Flow

1. Buyer initiates purchase
2. Create order
3. Process payment (Stripe/PayPal)
4. Update order status
5. Notify seller
6. Handle shipping
7. Mark as delivered
8. Release payment to seller

### Payment Methods

- Credit/debit cards
- PayPal
- Apple Pay
- Google Pay
- Bank transfer

---

## Image Storage & Processing

### Image Processing Pipeline

1. Upload image
2. Validate (size, format)
3. Store in S3
4. Generate thumbnails (multiple sizes)
5. Optimize for web
6. Store metadata in database
7. CDN delivery

### Image Sizes

- Original
- Large (1200px)
- Medium (600px)
- Thumbnail (300px)
- Small (150px)

---

## Scalability Considerations

### 1. Horizontal Scaling

**Stateless Services:**
- All microservices are stateless
- Scale horizontally by adding instances
- Load balancer distributes traffic
- Auto-scaling based on CPU/memory/request rate

**Scaling Metrics:**
- **Listing Service**: 1000 req/s per instance
- **Search Service**: 500 queries/s per instance
- **Messaging Service**: 1000 messages/s per instance
- **Order Service**: 100 orders/s per instance

**Database Scaling:**
- **PostgreSQL**: Read replicas for reads, sharding for writes
- **Elasticsearch**: Cluster scaling with shard rebalancing
- **Redis**: Cluster mode with hash slots
- **S3**: Unlimited storage, CDN for delivery

### 2. Caching Strategy

**Multi-Level Caching:**
1. **CDN**: Static assets, product images (90% hit rate)
2. **Redis**: Listing data, search results (80% hit rate)
3. **Application Cache**: Hot data (60% hit rate)

**Cache Keys:**
```
listing:{listing_id} → Listing data
search:{query_hash} → Search results
user:{user_id} → User data
conversation:{conversation_id} → Conversation data
recommendations:{user_id} → Recommendations
```

**Cache Invalidation:**
- **Event-Based**: Invalidate on listing/order updates
- **TTL-Based**: Set expiration for time-sensitive data
- **Version-Based**: Use version numbers for validation

### 3. Database Sharding

**Sharding Strategy:**
- **Listings**: Shard by location (city/state)
- **Messages**: Shard by conversation_id hash
- **Orders**: Shard by user_id hash
- **Users**: Shard by user_id hash

**Sharding Implementation:**
```python
class ShardManager:
    def __init__(self, num_shards: int):
        self.num_shards = num_shards
    
    def get_shard(self, shard_key: str) -> int:
        return hash(shard_key) % self.num_shards
    
    def route_query(self, shard_key: str, query: str, params: tuple):
        shard_id = self.get_shard(shard_key)
        conn = self.shard_connections[shard_id]
        return conn.execute(query, params)
```

### 4. Search Scaling

**Elasticsearch Optimization:**
- **Sharding**: Shard indices by location or category
- **Replication**: Replica shards for read scaling
- **Index Aliases**: Zero-downtime index updates
- **Bulk Indexing**: Batch indexing for efficiency

**Search Caching:**
- **Query Cache**: Cache popular search queries
- **Filter Cache**: Cache filter combinations
- **Result Cache**: Cache search results
- **CDN**: Cache search results at edge

### 5. Message Queue Scaling

**Kafka Partitioning:**
- **Partition by conversation_id**: Ensures ordering per conversation
- **Multiple Partitions**: Parallel processing
- **Consumer Groups**: Load distribution
- **Auto-Scaling**: Scale consumers based on lag

**Performance Targets:**
- **Throughput**: 1M+ messages/second
- **Latency**: < 10ms (p95)
- **Durability**: 99.99% message delivery

### 6. Image Storage Scaling

**S3 Optimization:**
- **CDN Integration**: CloudFront for fast delivery
- **Image Optimization**: Multiple sizes (thumbnail, medium, large)
- **Compression**: Compress images for faster loading
- **Lazy Loading**: Load images on demand

**Storage Strategy:**
- **Original Images**: S3 standard storage
- **Thumbnails**: S3 standard-IA (infrequent access)
- **CDN**: CloudFront for delivery
- **Backup**: Cross-region replication

---

## Monitoring & Analytics

### Key Metrics

**Performance:**
- Search latency
- Listing load time
- Image load time
- Message delivery time

**Business:**
- Daily active users
- Listings created
- Orders completed
- Revenue
- Conversion rate

**Quality:**
- Search relevance
- Recommendation accuracy
- User satisfaction
- Fraud rate

---

## Deployment Strategy

### Infrastructure

- **Containerization**: Docker
- **Orchestration**: Kubernetes
- **Database**: PostgreSQL
- **Search**: Elasticsearch
- **Cache**: Redis
- **Storage**: S3
- **CDN**: CloudFront

### Multi-Region

- Regional deployments
- Data replication
- Route to nearest region
- Cross-region messaging

---

## Failure Scenarios & Handling

### Search Service Failure

**Scenario**: Elasticsearch cluster fails
**Mitigation**: 
- Fallback to database search
- Read replicas
- Cache recent searches

### Payment Service Failure

**Scenario**: Payment processor down
**Mitigation**:
- Queue payment requests
- Retry mechanism
- Multiple payment providers

---

## Trade-offs & Design Decisions

### 1. Search Technology

**Decision**: Elasticsearch
**Rationale**: Powerful search, good performance, scalable

### 2. Image Storage

**Decision**: S3 with CDN
**Rationale**: Scalable, cost-effective, fast delivery

### 3. Messaging

**Decision**: WebSocket + Message Queue
**Rationale**: Real-time with reliability

---

## Interview Discussion Points

1. How do you handle search at scale?
2. How do you generate recommendations?
3. How do you handle real-time messaging?
4. How do you prevent fraud?
5. How do you optimize image delivery?

---

## Technology Stack

### Backend
- **Language**: Go, Python, or Java
- **Framework**: Gin (Go), FastAPI (Python), Spring Boot (Java)
- **Database**: PostgreSQL
- **Search**: Elasticsearch
- **Cache**: Redis
- **Storage**: S3
- **Message Queue**: Kafka or RabbitMQ

### Frontend
- **Web**: React, Vue.js
- **Mobile**: React Native, Flutter

### Infrastructure
- **Containerization**: Docker
- **Orchestration**: Kubernetes
- **CDN**: CloudFront
- **Monitoring**: Prometheus, Grafana

---

## Conclusion

A Marketplace System requires careful design of search, recommendations, messaging, payments, and image handling. The system must scale to millions of listings and users while providing excellent search and discovery experiences.

Key success factors include:
- Fast and relevant search
- Accurate recommendations
- Reliable messaging
- Secure payments
- Excellent user experience

