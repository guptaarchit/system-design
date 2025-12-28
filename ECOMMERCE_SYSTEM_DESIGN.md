# E-Commerce System Design Document

## Table of Contents
1. [Overview](#overview)
2. [Requirements](#requirements)
3. [System Architecture](#system-architecture)
4. [Database Design](#database-design)
5. [API Design](#api-design)
6. [Product Catalog System](#product-catalog-system)
7. [Shopping Cart & Checkout](#shopping-cart--checkout)
8. [Payment Processing](#payment-processing)
9. [Inventory Management](#inventory-management)
10. [Order Fulfillment](#order-fulfillment)
11. [Search & Recommendations](#search--recommendations)
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

An e-commerce platform that enables users to browse products, add items to cart, place orders, and complete purchases. The system must handle high traffic, manage inventory in real-time, process payments securely, and provide personalized shopping experiences.

**Key Features:**
- Product catalog with search and filtering
- Shopping cart management
- Secure payment processing
- Order management and tracking
- Inventory management
- User accounts and authentication
- Product reviews and ratings
- Personalized recommendations
- Multi-vendor/marketplace support
- Shipping and fulfillment tracking

---

## Requirements

### Functional Requirements

1. **Product Catalog**
   - Browse products by category, brand, price range
   - Product search with filters
   - Product details (images, descriptions, specifications)
   - Product variants (size, color, etc.)
   - Stock availability
   - Product reviews and ratings

2. **Shopping Cart**
   - Add/remove items
   - Update quantities
   - Save cart for later
   - Cart persistence across sessions
   - Price calculations (subtotal, tax, shipping)

3. **Checkout & Payment**
   - Multiple payment methods (credit card, PayPal, etc.)
   - Secure payment processing
   - Address management
   - Shipping options and costs
   - Order confirmation
   - Payment gateway integration

4. **Order Management**
   - Order history
   - Order tracking
   - Order status updates
   - Order cancellation and returns
   - Invoice generation

5. **Inventory Management**
   - Real-time stock tracking
   - Low stock alerts
   - Inventory updates
   - Multi-warehouse support
   - Stock reservation during checkout

6. **User Management**
   - User registration and authentication
   - User profiles
   - Order history
   - Wishlist
   - Address book
   - Payment methods storage

7. **Search & Discovery**
   - Full-text product search
   - Faceted search (filters)
   - Product recommendations
   - Trending products
   - Recently viewed items

### Non-Functional Requirements

1. **Scalability**
   - Support 10M+ products
   - Handle 100K+ concurrent users
   - Support 1M+ orders per day
   - 99.9% uptime
   - Multi-region deployment

2. **Performance**
   - Product search: < 200ms latency
   - Page load time: < 2 seconds
   - Checkout completion: < 5 seconds
   - 99th percentile latency < 1s

3. **Availability**
   - Multi-region active-active deployment
   - Automatic failover
   - Data replication across regions
   - Zero-downtime deployments

4. **Security**
   - PCI-DSS compliance for payments
   - Encrypted data transmission (TLS 1.3)
   - Secure authentication (OAuth 2.0, JWT)
   - Fraud detection
   - DDoS protection

5. **Consistency**
   - Strong consistency for inventory
   - Eventual consistency for recommendations
   - ACID transactions for orders
   - Distributed transactions for checkout

---

## System Architecture

### High-Level Design (HLD)

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Layer                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │   Web     │  │  Mobile  │  │   Admin  │  │   API    │  │
│  │  (React)  │  │   (iOS/  │  │  Portal  │  │ Partners │  │
│  │           │  │  Android)│  │          │  │          │  │
│  └────┬──────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
└───────┼───────────────┼─────────────┼─────────────┼────────┘
        │               │               │             │
        └───────────────┴───────────────┴─────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    CDN / Load Balancer                       │
│              (CloudFront / Cloudflare)                      │
└───────────────────────────┬─────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Region 1   │  │   Region 2   │  │   Region N   │
│  (US-East)   │  │  (EU-West)   │  │   (APAC)     │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                  │
       ▼                 ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway / Service Mesh               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   Auth   │  │  Product │  │   Cart   │  │  Order   │   │
│  │ Service  │  │ Service  │  │ Service  │  │ Service  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Payment │  │Inventory │  │  Search  │  │Recommend │   │
│  │ Service │  │ Service  │  │ Service  │  │ Service  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Shipping │  │  Review │  │  User    │  │  Notification│ │
│  │ Service │  │ Service  │  │ Service │  │ Service  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼──────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│                    Caching Layer                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Redis   │  │  Redis   │  │  Redis   │  │  Redis   │   │
│  │ Cluster  │  │ Cluster  │  │ Cluster  │  │ Cluster  │   │
│  │(Sessions)│ │(Products)│ │  (Cart)  │ │(Catalog)│   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼──────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│                    Database Layer                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │PostgreSQL│  │PostgreSQL │  │Cassandra │  │Elasticsearch│ │
│  │(Products)│  │  (Orders) │  │(Events) │  │  (Search) │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │PostgreSQL│  │  MySQL   │  │  Redis   │  │   S3     │   │
│  │(Users)   │  │(Inventory)│ │(Sessions)│ │(Images)  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼──────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│              Message Queue & Storage                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Kafka   │  │   S3     │  │  S3      │  │  S3      │   │
│  │(Events)  │  │(Product  │  │(Orders)  │  │(Logs)    │   │
│  │          │  │ Images)  │  │          │  │          │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Component Details

#### 1. Client Applications
- **Web**: React/Next.js SPA
- **Mobile**: Native iOS (Swift) and Android (Kotlin) apps
- **Admin Portal**: React-based admin dashboard
- **API Partners**: RESTful API for third-party integrations

#### 2. CDN Layer
- **Technology**: CloudFront, Cloudflare, or Fastly
- **Responsibilities**:
  - Cache static assets (images, CSS, JS)
  - Cache product images
  - Reduce latency
  - Handle 80-90% of static content requests

#### 3. API Gateway
- **Technology**: AWS API Gateway, Kong, or Envoy
- **Responsibilities**:
  - Request routing
  - Authentication/authorization
  - Rate limiting
  - Request/response transformation
  - SSL termination

#### 4. Application Services (Microservices)

**Auth Service:**
- User authentication (OAuth 2.0, JWT)
- Session management
- Multi-factor authentication
- Password reset

**Product Service:**
- Product catalog management
- Product CRUD operations
- Product variants management
- Category management

**Cart Service:**
- Shopping cart operations
- Cart persistence
- Price calculations
- Cart expiration

**Order Service:**
- Order creation and management
- Order status tracking
- Order history
- Order cancellation

**Payment Service:**
- Payment processing
- Payment gateway integration (Stripe, PayPal)
- Payment method management
- Refund processing

**Inventory Service:**
- Real-time inventory tracking
- Stock reservation
- Inventory updates
- Low stock alerts

**Search Service:**
- Full-text product search
- Faceted search
- Search ranking
- Search analytics

**Recommendation Service:**
- Personalized product recommendations
- "Customers who bought" suggestions
- Trending products
- Recently viewed items

**Shipping Service:**
- Shipping rate calculation
- Shipping provider integration
- Tracking number management
- Delivery status updates

**Review Service:**
- Product reviews and ratings
- Review moderation
- Aggregated ratings
- Review analytics

**Notification Service:**
- Email notifications
- SMS notifications
- Push notifications
- In-app notifications

#### 5. Caching Layer
- **Technology**: Redis Cluster
- **Responsibilities**:
  - Cache product data
  - Cache search results
  - Session storage
  - Shopping cart storage
  - Rate limiting

#### 6. Database Layer

**PostgreSQL (SQL):**
- Product catalog
- User accounts
- Orders
- Inventory (with strong consistency)
- Relational queries

**Cassandra (NoSQL):**
- User events
- Clickstream data
- Analytics events
- High write throughput

**Elasticsearch:**
- Full-text product search
- Product indexing
- Search analytics

**Redis:**
- Sessions
- Shopping carts
- Rate limiting
- Real-time data

#### 7. Message Queue
- **Kafka**: Event streaming
- **SQS**: Task queues
- **Responsibilities**:
  - Order events
  - Inventory updates
  - Email notifications
  - Analytics events

#### 8. Storage Layer
- **S3**: Product images, order documents, logs
- **CDN**: Cached static assets

### HLD Component Breakdown

**1. Client Layer**
- **Web Application**: React SPA with server-side rendering
- **Mobile Apps**: Native iOS/Android with offline support
- **Admin Portal**: React-based dashboard for merchants
- **API Clients**: RESTful API for partners

**2. Edge Layer**
- **CDN**: CloudFront/Cloudflare for static assets
- **Load Balancer**: ALB/NLB for traffic distribution
- **API Gateway**: Kong/Envoy for request routing

**3. Application Layer**
- **Microservices**: Stateless services for each domain
- **Service Mesh**: Istio/Linkerd for service communication
- **Event Bus**: Kafka for event-driven architecture

**4. Data Layer**
- **SQL Databases**: PostgreSQL for transactional data
- **NoSQL Databases**: Cassandra for event data
- **Search Engine**: Elasticsearch for product search
- **Cache**: Redis for hot data

**5. Infrastructure Layer**
- **Message Queue**: Kafka for event streaming
- **Object Storage**: S3 for media files
- **Monitoring**: Prometheus/Grafana for observability

---

## Low-Level Design (LLD)

### Order Service LLD

```python
class OrderService:
    def __init__(self, db: Database, inventory_service: InventoryService, 
                 payment_service: PaymentService, event_publisher: EventPublisher):
        self.db = db
        self.inventory_service = inventory_service
        self.payment_service = payment_service
        self.event_publisher = event_publisher
        self.cache = RedisCache()
    
    def create_order(self, user_id: int, cart_items: list, shipping_address: dict) -> Order:
        # Start distributed transaction
        with self.db.transaction():
            # Step 1: Reserve inventory
            reservation_result = self.inventory_service.reserve_items(cart_items)
            if not reservation_result.success:
                raise InsufficientInventoryError()
            
            # Step 2: Calculate totals
            order_total = self._calculate_total(cart_items, shipping_address)
            
            # Step 3: Create order record
            order = Order.create(
                user_id=user_id,
                items=cart_items,
                total=order_total,
                status='pending',
                shipping_address=shipping_address
            )
            
            # Step 4: Process payment
            payment_result = self.payment_service.charge(
                amount=order_total,
                payment_method_id=cart_items[0].payment_method_id
            )
            
            if not payment_result.success:
                # Rollback inventory reservation
                self.inventory_service.release_reservation(reservation_result.reservation_id)
                raise PaymentFailedError()
            
            # Step 5: Confirm order
            order.status = 'confirmed'
            order.payment_transaction_id = payment_result.transaction_id
            order.save()
            
            # Step 6: Convert reservation to booking
            self.inventory_service.confirm_reservation(reservation_result.reservation_id)
            
            # Step 7: Publish events
            self.event_publisher.publish('order.created', {
                'order_id': order.id,
                'user_id': user_id,
                'total': order_total
            })
            
            return order
```

### Inventory Service LLD

```python
class InventoryService:
    def __init__(self, db: Database, cache: RedisCache, lock_manager: LockManager):
        self.db = db
        self.cache = cache
        self.lock_manager = lock_manager
    
    def reserve_items(self, items: list) -> ReservationResult:
        reservation_id = str(uuid.uuid4())
        reservations = []
        
        for item in items:
            # Acquire distributed lock
            lock_key = f"inventory_lock:{item.product_id}:{item.variant_id}"
            
            with self.lock_manager.acquire(lock_key, timeout=5):
                # Check availability
                available = self._check_availability(item.product_id, item.variant_id, item.quantity)
                
                if not available:
                    # Release previous reservations
                    for prev_res in reservations:
                        self._release_reservation(prev_res)
                    raise InsufficientInventoryError()
                
                # Reserve inventory
                reservation = self._create_reservation(
                    reservation_id=reservation_id,
                    product_id=item.product_id,
                    variant_id=item.variant_id,
                    quantity=item.quantity,
                    ttl=900  # 15 minutes
                )
                reservations.append(reservation)
                
                # Update cache
                self._update_cache(item.product_id, item.variant_id, -item.quantity)
        
        return ReservationResult(success=True, reservation_id=reservation_id)
    
    def _check_availability(self, product_id: int, variant_id: int, quantity: int) -> bool:
        # Check cache first
        cache_key = f"inventory:{product_id}:{variant_id}"
        cached_qty = self.cache.get(cache_key)
        
        if cached_qty is not None:
            return cached_qty >= quantity
        
        # Query database
        variant = self.db.query(
            "SELECT inventory_quantity FROM product_variants WHERE id = %s FOR UPDATE",
            (variant_id,)
        )
        
        if not variant or variant.inventory_quantity < quantity:
            return False
        
        # Update cache
        self.cache.set(cache_key, variant.inventory_quantity, ttl=60)
        
        return True
```

### Cart Service LLD

```python
class CartService:
    def __init__(self, cache: RedisCache, product_service: ProductService):
        self.cache = cache
        self.product_service = product_service
    
    def add_to_cart(self, user_id: int, product_id: int, variant_id: int, quantity: int) -> Cart:
        cart_key = f"cart:{user_id}"
        
        # Get or create cart
        cart_data = self.cache.get(cart_key)
        if cart_data:
            cart = Cart.from_dict(cart_data)
        else:
            cart = Cart(user_id=user_id, items=[])
        
        # Check if item already in cart
        existing_item = next((item for item in cart.items 
                            if item.product_id == product_id and item.variant_id == variant_id), None)
        
        if existing_item:
            existing_item.quantity += quantity
        else:
            # Get product details
            product = self.product_service.get_product(product_id)
            variant = self.product_service.get_variant(variant_id)
            
            cart_item = CartItem(
                product_id=product_id,
                variant_id=variant_id,
                quantity=quantity,
                price=variant.price,
                product_name=product.name
            )
            cart.items.append(cart_item)
        
        # Recalculate totals
        cart.subtotal = sum(item.price * item.quantity for item in cart.items)
        cart.updated_at = datetime.utcnow()
        
        # Save to cache
        self.cache.set(cart_key, cart.to_dict(), ttl=86400 * 7)  # 7 days
        
        return cart
```

### Search Service LLD

```python
class SearchService:
    def __init__(self, elasticsearch: ElasticsearchClient, cache: RedisCache):
        self.es = elasticsearch
        self.cache = cache
    
    def search_products(self, query: str, filters: dict, page: int = 1, page_size: int = 20) -> SearchResult:
        # Generate cache key
        cache_key = self._generate_cache_key(query, filters, page, page_size)
        
        # Check cache
        cached_result = self.cache.get(cache_key)
        if cached_result:
            return SearchResult.from_dict(cached_result)
        
        # Build Elasticsearch query
        es_query = {
            'bool': {
                'must': [
                    {
                        'multi_match': {
                            'query': query,
                            'fields': ['name^3', 'description', 'tags'],
                            'type': 'best_fields'
                        }
                    }
                ],
                'filter': self._build_filters(filters)
            }
        }
        
        # Execute search
        response = self.es.search(
            index='products',
            body={
                'query': es_query,
                'from': (page - 1) * page_size,
                'size': page_size,
                'sort': self._build_sort(filters.get('sort'))
            }
        )
        
        # Process results
        products = [self._parse_hit(hit) for hit in response['hits']['hits']]
        total = response['hits']['total']['value']
        
        result = SearchResult(
            products=products,
            total=total,
            page=page,
            page_size=page_size
        )
        
        # Cache result
        self.cache.set(cache_key, result.to_dict(), ttl=300)  # 5 minutes
        
        return result
```

---

## Fault Tolerance

### Service-Level Fault Tolerance

**1. Circuit Breaker Pattern**
```python
class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'closed'  # closed, open, half_open
    
    def call(self, func, *args, **kwargs):
        if self.state == 'open':
            if time.time() - self.last_failure_time > self.timeout:
                self.state = 'half_open'
            else:
                raise CircuitBreakerOpenError()
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        self.failure_count = 0
        self.state = 'closed'
    
    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = 'open'
```

**2. Retry Logic with Exponential Backoff**
```python
class RetryHandler:
    def __init__(self, max_retries: int = 3, backoff_factor: float = 2.0):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
    
    def execute(self, func, *args, **kwargs):
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except RetryableError as e:
                if attempt == self.max_retries - 1:
                    raise
                wait_time = self.backoff_factor ** attempt
                time.sleep(wait_time)
            except NonRetryableError:
                raise
```

**3. Bulkhead Pattern**
```python
class BulkheadExecutor:
    def __init__(self, max_workers: int = 10):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.semaphore = Semaphore(max_workers)
    
    def execute(self, func, *args, **kwargs):
        with self.semaphore:
            return self.executor.submit(func, *args, **kwargs).result()
```

### Database Fault Tolerance

**1. Database Replication**
- **Primary-Replica Setup**: PostgreSQL primary with multiple read replicas
- **Automatic Failover**: Promote replica on primary failure
- **Read Distribution**: Route reads to replicas
- **Write Consistency**: Write to primary, replicate asynchronously

**2. Connection Pooling**
```python
class DatabasePool:
    def __init__(self, primary_config: dict, replica_configs: list, pool_size: int = 20):
        self.primary_pool = create_pool(primary_config, pool_size=pool_size)
        self.replica_pools = [create_pool(config, pool_size=pool_size) 
                             for config in replica_configs]
        self.current_replica = 0
    
    def get_read_connection(self):
        # Round-robin replica selection
        pool = self.replica_pools[self.current_replica]
        self.current_replica = (self.current_replica + 1) % len(self.replica_pools)
        return pool.get_connection()
    
    def get_write_connection(self):
        return self.primary_pool.get_connection()
```

**3. Database Health Checks**
- **Periodic Health Checks**: Monitor database health every 30 seconds
- **Automatic Failover**: Switch to replica on primary failure
- **Connection Retry**: Retry failed connections with backoff

### Cache Fault Tolerance

**1. Redis Cluster**
- **Multiple Nodes**: Deploy Redis cluster with 3+ nodes
- **Replication**: Each node has replicas
- **Automatic Failover**: Promote replica on node failure
- **Client-Side Routing**: Route requests to available nodes

**2. Cache Fallback**
```python
class ResilientCache:
    def __init__(self, redis_client: RedisClient, fallback_db: Database):
        self.redis = redis_client
        self.fallback_db = fallback_db
    
    def get(self, key: str):
        try:
            return self.redis.get(key)
        except RedisError:
            # Fallback to database
            return self.fallback_db.get(key)
    
    def set(self, key: str, value: any, ttl: int = None):
        try:
            self.redis.set(key, value, ex=ttl)
        except RedisError:
            # Log error but don't fail
            logger.error(f"Failed to set cache key: {key}")
```

---

## Failure Safety

### Failure Scenarios & Handling

**1. Payment Service Failure**

**Scenario**: Payment gateway is unavailable during checkout.

**Impact**: Cannot process payments, orders stuck in pending state.

**Mitigation**:
- **Queue Payments**: Queue payment requests for retry
- **Graceful Degradation**: Allow order creation, process payment async
- **Multiple Gateways**: Failover to secondary payment gateway
- **Compensation**: Cancel order if payment fails after timeout

**Recovery**:
```python
class PaymentService:
    def process_payment(self, order_id: int, payment_method_id: str):
        try:
            return self.primary_gateway.charge(order_id, payment_method_id)
        except GatewayError:
            # Retry with secondary gateway
            try:
                return self.secondary_gateway.charge(order_id, payment_method_id)
            except GatewayError:
                # Queue for later processing
                self.payment_queue.enqueue(order_id, payment_method_id)
                raise PaymentPendingError()
```

**2. Inventory Service Failure**

**Scenario**: Inventory service becomes unavailable.

**Impact**: Cannot check/reserve inventory, orders may oversell.

**Mitigation**:
- **Cached Inventory**: Use cached inventory data
- **Optimistic Locking**: Allow orders, verify on recovery
- **Manual Review**: Flag orders for manual review
- **Service Redundancy**: Deploy multiple inventory service instances

**Recovery**:
- **Reconciliation Job**: Reconcile inventory after service recovery
- **Order Validation**: Validate orders created during outage
- **Compensation**: Cancel orders if inventory insufficient

**3. Database Failure**

**Scenario**: Primary database fails.

**Impact**: Cannot read/write data, system unavailable.

**Mitigation**:
- **Read Replicas**: Serve reads from replicas
- **Automatic Failover**: Promote replica to primary
- **Connection Pooling**: Retry connections with backoff
- **Graceful Degradation**: Serve cached data when possible

**Recovery**:
- **Failover**: Automatically promote replica
- **Data Sync**: Sync data when primary recovers
- **Backup Restoration**: Restore from backup if needed

**4. Cache Failure**

**Scenario**: Redis cluster fails.

**Impact**: Increased database load, slower responses.

**Mitigation**:
- **Database Fallback**: Query database directly
- **Local Cache**: Use application-level cache
- **Graceful Degradation**: Continue operation with reduced performance
- **Cache Cluster**: Deploy Redis cluster with replication

**Recovery**:
- **Cache Warming**: Pre-populate cache after recovery
- **Gradual Traffic**: Gradually increase traffic to cache
- **Monitoring**: Monitor cache performance

**5. Order Processing Failure**

**Scenario**: Order service fails during order creation.

**Impact**: Orders may be partially created, inconsistent state.

**Mitigation**:
- **Distributed Transactions**: Use saga pattern for distributed transactions
- **Idempotency**: Make operations idempotent
- **Compensation**: Rollback on failure
- **Event Sourcing**: Use events for audit and recovery

**Recovery**:
- **Saga Compensation**: Execute compensation transactions
- **State Reconciliation**: Reconcile order state
- **Manual Intervention**: Flag for manual review

### Recovery Mechanisms

**1. Order State Recovery**
```python
class OrderRecovery:
    def recover_failed_orders(self):
        # Find orders in inconsistent state
        failed_orders = self.db.query(
            "SELECT * FROM orders WHERE status = 'pending' AND created_at < %s",
            (datetime.utcnow() - timedelta(minutes=30),)
        )
        
        for order in failed_orders:
            # Check payment status
            payment_status = self.payment_service.get_status(order.payment_transaction_id)
            
            if payment_status == 'failed':
                # Compensate: Release inventory, cancel order
                self.inventory_service.release_reservation(order.reservation_id)
                order.status = 'cancelled'
                order.save()
            elif payment_status == 'succeeded':
                # Complete order
                order.status = 'confirmed'
                order.save()
```

**2. Inventory Reconciliation**
```python
class InventoryReconciliation:
    def reconcile_inventory(self):
        # Calculate expected inventory from orders
        expected_inventory = {}
        
        orders = self.db.query(
            "SELECT product_id, variant_id, quantity FROM orders WHERE status = 'confirmed'"
        )
        
        for order in orders:
            key = (order.product_id, order.variant_id)
            expected_inventory[key] = expected_inventory.get(key, 0) + order.quantity
        
        # Compare with actual inventory
        for (product_id, variant_id), expected_qty in expected_inventory.items():
            actual_qty = self.db.query(
                "SELECT inventory_quantity FROM product_variants WHERE id = %s",
                (variant_id,)
            )
            
            if actual_qty != expected_qty:
                # Log discrepancy
                logger.warning(f"Inventory mismatch for variant {variant_id}")
                # Update inventory
                self.db.execute(
                    "UPDATE product_variants SET inventory_quantity = %s WHERE id = %s",
                    (expected_qty, variant_id)
                )
```

---

## Database Design

### PostgreSQL Schema

#### Products Table
```sql
CREATE TABLE products (
    id BIGSERIAL PRIMARY KEY,
    sku VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category_id BIGINT NOT NULL,
    brand_id BIGINT,
    price DECIMAL(10, 2) NOT NULL,
    compare_at_price DECIMAL(10, 2),
    cost DECIMAL(10, 2),
    weight DECIMAL(8, 2),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_category (category_id),
    INDEX idx_brand (brand_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    FULLTEXT idx_search (name, description)
) ENGINE=InnoDB;
```

#### Product Variants Table
```sql
CREATE TABLE product_variants (
    id BIGSERIAL PRIMARY KEY,
    product_id BIGINT NOT NULL,
    sku VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255),
    price DECIMAL(10, 2),
    compare_at_price DECIMAL(10, 2),
    inventory_quantity INT DEFAULT 0,
    weight DECIMAL(8, 2),
    option1 VARCHAR(100),  -- e.g., "Size: Large"
    option2 VARCHAR(100),  -- e.g., "Color: Red"
    option3 VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    INDEX idx_product_id (product_id),
    INDEX idx_sku (sku),
    INDEX idx_inventory (inventory_quantity)
) ENGINE=InnoDB;
```

#### Categories Table
```sql
CREATE TABLE categories (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    parent_id BIGINT,
    description TEXT,
    image_url VARCHAR(500),
    sort_order INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES categories(id),
    INDEX idx_parent_id (parent_id),
    INDEX idx_slug (slug)
) ENGINE=InnoDB;
```

#### Users Table
```sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(20),
    date_of_birth DATE,
    email_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB;
```

#### Shopping Carts Table
```sql
CREATE TABLE shopping_carts (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT,
    session_id VARCHAR(255),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_session_id (session_id),
    INDEX idx_expires_at (expires_at)
) ENGINE=InnoDB;
```

#### Cart Items Table
```sql
CREATE TABLE cart_items (
    id BIGSERIAL PRIMARY KEY,
    cart_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    variant_id BIGINT,
    quantity INT NOT NULL DEFAULT 1,
    price DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (cart_id) REFERENCES shopping_carts(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (variant_id) REFERENCES product_variants(id),
    INDEX idx_cart_id (cart_id),
    INDEX idx_product_id (product_id)
) ENGINE=InnoDB;
```

#### Orders Table
```sql
CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    user_id BIGINT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    subtotal DECIMAL(10, 2) NOT NULL,
    tax DECIMAL(10, 2) DEFAULT 0,
    shipping_cost DECIMAL(10, 2) DEFAULT 0,
    discount DECIMAL(10, 2) DEFAULT 0,
    total DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    shipping_address JSONB NOT NULL,
    billing_address JSONB NOT NULL,
    payment_status VARCHAR(20) DEFAULT 'pending',
    payment_method VARCHAR(50),
    payment_transaction_id VARCHAR(255),
    shipping_method VARCHAR(50),
    tracking_number VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_user_id (user_id),
    INDEX idx_order_number (order_number),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB;
```

#### Order Items Table
```sql
CREATE TABLE order_items (
    id BIGSERIAL PRIMARY KEY,
    order_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    variant_id BIGINT,
    sku VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    total DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (variant_id) REFERENCES product_variants(id),
    INDEX idx_order_id (order_id),
    INDEX idx_product_id (product_id)
) ENGINE=InnoDB;
```

#### Inventory Table
```sql
CREATE TABLE inventory (
    id BIGSERIAL PRIMARY KEY,
    variant_id BIGINT NOT NULL,
    warehouse_id BIGINT NOT NULL,
    quantity INT NOT NULL DEFAULT 0,
    reserved_quantity INT DEFAULT 0,
    available_quantity INT GENERATED ALWAYS AS (quantity - reserved_quantity) STORED,
    low_stock_threshold INT DEFAULT 10,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (variant_id) REFERENCES product_variants(id),
    UNIQUE KEY unique_variant_warehouse (variant_id, warehouse_id),
    INDEX idx_variant_id (variant_id),
    INDEX idx_warehouse_id (warehouse_id),
    INDEX idx_available_quantity (available_quantity)
) ENGINE=InnoDB;
```

#### Inventory Transactions Table
```sql
CREATE TABLE inventory_transactions (
    id BIGSERIAL PRIMARY KEY,
    variant_id BIGINT NOT NULL,
    warehouse_id BIGINT NOT NULL,
    transaction_type VARCHAR(20) NOT NULL,  -- 'sale', 'restock', 'adjustment', 'reservation', 'release'
    quantity INT NOT NULL,
    reference_type VARCHAR(50),  -- 'order', 'purchase', 'adjustment'
    reference_id BIGINT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (variant_id) REFERENCES product_variants(id),
    INDEX idx_variant_id (variant_id),
    INDEX idx_created_at (created_at),
    INDEX idx_reference (reference_type, reference_id)
) ENGINE=InnoDB;
```

#### Product Reviews Table
```sql
CREATE TABLE product_reviews (
    id BIGSERIAL PRIMARY KEY,
    product_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    order_id BIGINT,
    rating INT CHECK (rating BETWEEN 1 AND 5),
    title VARCHAR(255),
    review_text TEXT,
    is_verified_purchase BOOLEAN DEFAULT FALSE,
    is_approved BOOLEAN DEFAULT FALSE,
    helpful_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (order_id) REFERENCES orders(id),
    UNIQUE KEY unique_product_user (product_id, user_id),
    INDEX idx_product_id (product_id),
    INDEX idx_user_id (user_id),
    INDEX idx_rating (rating),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB;
```

### Cassandra Schema (Events)

#### User Events Table
```cql
CREATE TABLE user_events (
    user_id UUID,
    event_timestamp TIMESTAMP,
    event_type TEXT,  -- 'view', 'click', 'add_to_cart', 'purchase', 'search'
    product_id TEXT,
    category_id TEXT,
    session_id TEXT,
    device_type TEXT,
    metadata MAP<TEXT, TEXT>,
    PRIMARY KEY ((user_id), event_timestamp, event_type)
) WITH CLUSTERING ORDER BY (event_timestamp DESC);
```

#### Product Views Table
```cql
CREATE TABLE product_views (
    product_id TEXT,
    view_timestamp TIMESTAMP,
    user_id UUID,
    session_id TEXT,
    referrer TEXT,
    device_type TEXT,
    PRIMARY KEY ((product_id), view_timestamp, user_id)
) WITH CLUSTERING ORDER BY (view_timestamp DESC);
```

---

## API Design

### RESTful API Endpoints

#### 1. Product Catalog

**Get Products**
```
GET /api/v1/products?category={category_id}&page=1&limit=20&sort=price_asc

Response:
{
    "products": [
        {
            "id": "123",
            "sku": "PROD-001",
            "name": "Example Product",
            "description": "Product description",
            "price": 29.99,
            "compare_at_price": 39.99,
            "images": ["https://cdn.example.com/image1.jpg"],
            "in_stock": true,
            "rating": 4.5,
            "review_count": 150
        }
    ],
    "pagination": {
        "page": 1,
        "limit": 20,
        "total": 1000,
        "total_pages": 50
    }
}
```

**Get Product Details**
```
GET /api/v1/products/{product_id}

Response:
{
    "id": "123",
    "sku": "PROD-001",
    "name": "Example Product",
    "description": "Detailed description",
    "price": 29.99,
    "variants": [
        {
            "id": "456",
            "sku": "PROD-001-L-RED",
            "name": "Large - Red",
            "price": 29.99,
            "inventory_quantity": 50,
            "options": {
                "size": "Large",
                "color": "Red"
            }
        }
    ],
    "images": [...],
    "reviews": [...],
    "related_products": [...]
}
```

#### 2. Shopping Cart

**Get Cart**
```
GET /api/v1/cart

Response:
{
    "cart_id": "cart_123",
    "items": [
        {
            "id": "item_1",
            "product_id": "123",
            "variant_id": "456",
            "name": "Example Product - Large Red",
            "quantity": 2,
            "price": 29.99,
            "total": 59.98,
            "image_url": "https://..."
        }
    ],
    "subtotal": 59.98,
    "tax": 4.80,
    "shipping": 5.99,
    "total": 70.77
}
```

**Add to Cart**
```
POST /api/v1/cart/items
Content-Type: application/json

Request:
{
    "product_id": "123",
    "variant_id": "456",
    "quantity": 2
}

Response:
{
    "success": true,
    "cart_item": {
        "id": "item_1",
        "product_id": "123",
        "variant_id": "456",
        "quantity": 2,
        "price": 29.99,
        "total": 59.98
    },
    "cart_total": 70.77
}
```

**Update Cart Item**
```
PUT /api/v1/cart/items/{item_id}
Content-Type: application/json

Request:
{
    "quantity": 3
}

Response:
{
    "success": true,
    "cart_item": {...},
    "cart_total": 100.76
}
```

**Remove from Cart**
```
DELETE /api/v1/cart/items/{item_id}

Response:
{
    "success": true,
    "cart_total": 40.78
}
```

#### 3. Checkout & Orders

**Create Order**
```
POST /api/v1/checkout
Content-Type: application/json

Request:
{
    "cart_id": "cart_123",
    "shipping_address": {
        "name": "John Doe",
        "street": "123 Main St",
        "city": "New York",
        "state": "NY",
        "zip": "10001",
        "country": "US"
    },
    "billing_address": {...},
    "shipping_method": "standard",
    "payment_method": "credit_card",
    "payment_token": "tok_visa_1234"
}

Response:
{
    "success": true,
    "order": {
        "order_id": "ORD-12345",
        "order_number": "100001",
        "status": "pending_payment",
        "total": 70.77,
        "items": [...],
        "shipping_address": {...},
        "payment_status": "pending"
    }
}
```

**Get Order**
```
GET /api/v1/orders/{order_id}

Response:
{
    "order_id": "ORD-12345",
    "order_number": "100001",
    "status": "processing",
    "items": [...],
    "shipping_address": {...},
    "tracking_number": "1Z999AA10123456784",
    "estimated_delivery": "2024-01-20",
    "created_at": "2024-01-15T10:30:00Z"
}
```

**Get Order History**
```
GET /api/v1/orders?page=1&limit=20

Response:
{
    "orders": [...],
    "pagination": {...}
}
```

#### 4. Search

**Search Products**
```
GET /api/v1/search?q=laptop&category=electronics&min_price=500&max_price=2000&page=1

Response:
{
    "query": "laptop",
    "total_results": 250,
    "products": [...],
    "facets": {
        "categories": [
            {"name": "Electronics", "count": 150},
            {"name": "Computers", "count": 100}
        ],
        "brands": [
            {"name": "Apple", "count": 50},
            {"name": "Dell", "count": 40}
        ],
        "price_ranges": [
            {"range": "500-1000", "count": 100},
            {"range": "1000-2000", "count": 150}
        ]
    },
    "pagination": {...}
}
```

#### 5. Recommendations

**Get Recommendations**
```
GET /api/v1/recommendations?type=homepage&limit=20

Response:
{
    "sections": [
        {
            "title": "Recommended for You",
            "products": [...]
        },
        {
            "title": "Trending Now",
            "products": [...]
        },
        {
            "title": "Recently Viewed",
            "products": [...]
        }
    ]
}
```

#### 6. Reviews

**Get Product Reviews**
```
GET /api/v1/products/{product_id}/reviews?page=1&limit=10&sort=helpful_desc

Response:
{
    "product_id": "123",
    "average_rating": 4.5,
    "total_reviews": 150,
    "rating_distribution": {
        "5": 75,
        "4": 50,
        "3": 15,
        "2": 5,
        "1": 5
    },
    "reviews": [...]
}
```

**Create Review**
```
POST /api/v1/products/{product_id}/reviews
Content-Type: application/json

Request:
{
    "rating": 5,
    "title": "Great product!",
    "review_text": "Really happy with this purchase.",
    "order_id": "ORD-12345"
}

Response:
{
    "success": true,
    "review": {
        "id": "review_123",
        "rating": 5,
        "title": "Great product!",
        "review_text": "Really happy with this purchase.",
        "is_verified_purchase": true,
        "created_at": "2024-01-15T10:30:00Z"
    }
}
```

---

## Data Flow Diagrams

### Product Browsing Flow

```
User Browses Products
    │
    ▼
Client Application
    │
    ├─ Check Local Cache
    │
    └─ Cache Miss → Request Products
        │
        ▼
    API Gateway (Rate Limit, Auth)
        │
        ▼
    Product Service
        │
        ├─ Check Redis Cache
        │   └─ Cache Hit (80%) → Return (1-2ms)
        │
        └─ Cache Miss (20%) → Continue
            │
            ▼
        Database Query (PostgreSQL)
            │
            ├─ Query Products Table
            ├─ Join with Categories
            └─ Apply Filters/Sorting
            │
            ▼
        Update Cache (Redis)
            │
            └─ Cache Results (TTL: 1 hour)
            │
            ▼
        Return Products to Client
```

### Add to Cart Flow

```
User Adds Item to Cart
    │
    ▼
Cart Service
    │
    ├─ Validate Product/Variant
    ├─ Check Inventory Availability
    │
    ▼
Inventory Service
    │
    ├─ Check Stock (PostgreSQL)
    ├─ Reserve Inventory (if available)
    │   └─ Update reserved_quantity
    │
    └─ Return Availability
    │
    ▼
Cart Service
    │
    ├─ Add Item to Cart
    ├─ Update Redis Cache (Cart)
    ├─ Update Database (PostgreSQL)
    │   └─ Async Write for Persistence
    │
    └─ Calculate Totals
        │
        ▼
    Return Cart Update
```

### Checkout Flow

```
User Initiates Checkout
    │
    ▼
Checkout Service
    │
    ├─ Validate Cart
    ├─ Calculate Totals
    │   ├─ Subtotal
    │   ├─ Tax (based on address)
    │   └─ Shipping Cost
    │
    ▼
User Confirms Order
    │
    ▼
Order Service (Distributed Transaction)
    │
    ├─ Create Order Record
    ├─ Reserve Inventory (Final)
    ├─ Process Payment
    │   │
    │   ▼
    │   Payment Service
    │   │
    │   ├─ Validate Payment Token
    │   ├─ Charge Payment Gateway
    │   └─ Record Transaction
    │
    ├─ Create Order Items
    ├─ Update Inventory (Reduce Stock)
    ├─ Clear Cart
    │
    └─ Publish Order Event (Kafka)
        │
        ├─ Notification Service (Email)
        ├─ Shipping Service (Fulfillment)
        └─ Analytics Service (Events)
        │
        ▼
    Return Order Confirmation
```

### Payment Processing Flow

```
Payment Request
    │
    ▼
Payment Service
    │
    ├─ Validate Payment Method
    ├─ Fraud Detection Check
    │   └─ ML Model Analysis
    │
    ▼
Payment Gateway (Stripe/PayPal)
    │
    ├─ Process Payment
    ├─ Return Transaction ID
    │
    └─ Webhook (Async)
        │
        ▼
    Payment Service
        │
        ├─ Update Order Status
        ├─ Update Payment Status
        └─ Trigger Fulfillment
```

---

## Product Catalog System

### Catalog Architecture

**Product Data Model:**
- **Products**: Base product information
- **Variants**: Product variations (size, color, etc.)
- **Categories**: Hierarchical category structure
- **Attributes**: Product attributes (brand, material, etc.)

**Catalog Features:**
- Multi-level categories
- Product variants and options
- Product images (multiple per product)
- Product specifications
- SEO-friendly URLs

**Catalog Optimization:**
- **Caching**: Cache product data aggressively
- **CDN**: Serve product images from CDN
- **Indexing**: Full-text search index
- **Denormalization**: Pre-compute frequently accessed data

---

## Shopping Cart & Checkout

### Cart Management

**Cart Storage:**
- **Redis**: Active carts (fast access)
- **PostgreSQL**: Persistent storage (backup)
- **Session-based**: For anonymous users
- **User-based**: For logged-in users

**Cart Expiration:**
- Anonymous carts: 7 days
- User carts: 30 days
- Abandoned cart recovery: Email reminders

**Cart Operations:**
- Add item (with inventory check)
- Update quantity
- Remove item
- Apply discount codes
- Calculate totals (subtotal, tax, shipping)

### Checkout Process

**Checkout Steps:**
1. **Cart Review**: Display cart items and totals
2. **Shipping Address**: Collect/select shipping address
3. **Shipping Method**: Select shipping option
4. **Payment**: Enter payment details
5. **Order Confirmation**: Display order summary

**Checkout Optimization:**
- **One-Page Checkout**: Reduce friction
- **Guest Checkout**: Don't require account
- **Saved Addresses**: Quick address selection
- **Payment Methods**: Multiple options
- **Progress Indicator**: Show checkout progress

---

## Payment Processing

### Payment Architecture

**Payment Methods:**
- Credit/Debit Cards (Stripe, Square)
- PayPal
- Apple Pay / Google Pay
- Bank Transfer
- Cryptocurrency (optional)

**Payment Flow:**
1. **Tokenization**: Convert card to token (PCI compliance)
2. **Authorization**: Authorize payment
3. **Capture**: Capture authorized payment
4. **Settlement**: Settle with payment gateway
5. **Refund**: Process refunds if needed

**Security:**
- **PCI-DSS Compliance**: Don't store raw card data
- **Tokenization**: Use payment tokens
- **Encryption**: Encrypt payment data in transit
- **Fraud Detection**: ML-based fraud detection

**Payment Gateway Integration:**
```python
class PaymentService:
    def process_payment(self, order_id, payment_token, amount):
        # Validate payment token
        if not self.validate_token(payment_token):
            raise InvalidPaymentTokenError()
        
        # Fraud detection
        fraud_score = self.fraud_detection.check(order_id, payment_token)
        if fraud_score > 0.8:
            raise FraudDetectedError()
        
        # Process payment via gateway
        result = self.payment_gateway.charge(
            token=payment_token,
            amount=amount,
            currency='USD'
        )
        
        # Record transaction
        self.record_transaction(order_id, result)
        
        # Update order status
        self.order_service.update_payment_status(order_id, result.status)
        
        return result
```

---

## Inventory Management

### Inventory Architecture

**Inventory Tracking:**
- **Real-time Stock**: Track available quantity
- **Reserved Stock**: Reserve during checkout
- **Multi-Warehouse**: Support multiple warehouses
- **Low Stock Alerts**: Alert when stock is low

**Inventory Operations:**
- **Reserve**: Reserve inventory during cart/checkout
- **Release**: Release reserved inventory
- **Deduct**: Deduct inventory on order confirmation
- **Restock**: Add inventory on restock
- **Adjust**: Manual inventory adjustments

**Inventory Consistency:**
- **Strong Consistency**: Use PostgreSQL with transactions
- **Optimistic Locking**: Prevent race conditions
- **Distributed Locks**: For multi-warehouse operations

**Inventory Reservation:**
```python
class InventoryService:
    @transactional
    def reserve_inventory(self, variant_id, quantity, order_id):
        # Check available quantity
        inventory = self.get_inventory(variant_id)
        if inventory.available_quantity < quantity:
            raise InsufficientStockError()
        
        # Reserve inventory
        inventory.reserved_quantity += quantity
        inventory.save()
        
        # Record transaction
        self.create_transaction(
            variant_id=variant_id,
            type='reservation',
            quantity=quantity,
            reference_id=order_id
        )
        
        return inventory
```

---

## Order Fulfillment

### Fulfillment Flow

**Order States:**
1. **Pending**: Order created, payment pending
2. **Payment Processing**: Payment being processed
3. **Paid**: Payment confirmed
4. **Processing**: Order being prepared
5. **Shipped**: Order shipped
6. **Delivered**: Order delivered
7. **Cancelled**: Order cancelled
8. **Refunded**: Order refunded

**Fulfillment Process:**
1. **Order Confirmation**: Confirm payment
2. **Inventory Allocation**: Allocate inventory
3. **Picking**: Pick items from warehouse
4. **Packing**: Pack items
5. **Shipping**: Generate shipping label
6. **Tracking**: Update tracking information
7. **Delivery**: Confirm delivery

**Fulfillment Integration:**
- **Shipping Providers**: FedEx, UPS, DHL APIs
- **Warehouse Management**: WMS integration
- **Tracking**: Real-time tracking updates

---

## Search & Recommendations

### Search Architecture

**Search Features:**
- Full-text search
- Faceted search (filters)
- Autocomplete
- Search suggestions
- Search analytics

**Search Implementation:**
- **Elasticsearch**: Full-text search engine
- **Indexing**: Index products, categories, brands
- **Ranking**: Relevance-based ranking
- **Filters**: Price, category, brand, rating

**Search Optimization:**
- **Autocomplete**: Fast prefix matching
- **Fuzzy Matching**: Handle typos
- **Synonyms**: Handle product synonyms
- **Boosting**: Boost popular products

### Recommendation System

**Recommendation Types:**
- **Collaborative Filtering**: "Customers who bought"
- **Content-Based**: Similar products
- **Popular Products**: Trending items
- **Recently Viewed**: User's browsing history
- **Personalized**: ML-based recommendations

**Recommendation Pipeline:**
```
User Data Collection
    │
    ├─ Purchase History
    ├─ Browsing History
    ├─ Cart Additions
    └─ Search Queries
    │
    ▼
Feature Engineering
    │
    ▼
ML Model Training
    │
    ├─ Collaborative Filtering
    ├─ Content-Based Filtering
    └─ Deep Learning Models
    │
    ▼
Recommendation Generation
    │
    ├─ Real-time (for new users)
    └─ Pre-computed (for existing users)
    │
    ▼
Recommendation API
```

---

## Scalability Considerations

### 1. Horizontal Scaling

**Stateless Services:**
- All microservices are stateless
- Scale horizontally by adding instances
- Load balancer distributes traffic
- Auto-scaling based on CPU/memory/request rate
- Kubernetes HPA for automatic scaling

**Database Scaling:**
- **PostgreSQL**: Read replicas for reads, sharding for writes
- **Cassandra**: Horizontal scaling by adding nodes
- **Elasticsearch**: Cluster scaling with shard rebalancing
- **Redis**: Cluster mode with hash slots

**Scaling Metrics:**
- **Product Service**: Scale based on request rate (target: 1000 req/s per instance)
- **Order Service**: Scale based on order creation rate (target: 100 orders/s per instance)
- **Search Service**: Scale based on search query rate (target: 500 queries/s per instance)

### 2. Database Sharding

**Sharding Strategy:**
- **Products**: Shard by category_id or product_id hash
- **Orders**: Shard by user_id or order_id hash
- **Users**: Shard by user_id hash
- **Inventory**: Shard by product_id hash

**Sharding Implementation:**
```python
class ShardManager:
    def __init__(self, num_shards: int):
        self.num_shards = num_shards
        self.shard_configs = self._load_shard_configs()
    
    def get_shard(self, shard_key: str) -> int:
        hash_value = hash(shard_key)
        return hash_value % self.num_shards
    
    def get_shard_connection(self, shard_key: str):
        shard_id = self.get_shard(shard_key)
        return self.shard_configs[shard_id].get_connection()
    
    def route_query(self, shard_key: str, query: str, params: tuple):
        conn = self.get_shard_connection(shard_key)
        return conn.execute(query, params)
```

**Shard Rebalancing:**
- **Strategy**: Consistent hashing for minimal rebalancing
- **Migration**: Gradual migration with dual writes
- **Monitoring**: Track shard load and rebalance when needed

### 3. Caching Strategy

**Multi-Level Caching:**
1. **CDN**: Static assets, product images (90% hit rate)
2. **Redis**: Product data, search results (80% hit rate)
3. **Application Cache**: Hot data (60% hit rate)
4. **Database Query Cache**: Frequently accessed queries

**Cache Keys:**
```
product:{product_id} → Product data
category:{category_id}:products → Category products
search:{query_hash} → Search results
cart:{user_id} → Shopping cart
user:{user_id} → User data
inventory:{product_id}:{variant_id} → Inventory count
```

**Cache Invalidation:**
- **Event-Based**: Invalidate on product/order updates
- **TTL-Based**: Set expiration for time-sensitive data
- **Version-Based**: Use version numbers for cache validation

**Cache Warming:**
- Pre-populate cache with popular products
- Warm cache on service startup
- Background jobs to refresh cache

### 4. Read/Write Optimization

**Read Optimization:**
- Read replicas for read-heavy queries
- Aggressive caching (multi-level)
- CDN for static content
- Denormalization for common queries
- Materialized views for complex aggregations
- Query result caching

**Write Optimization:**
- Async writes for non-critical data
- Batch writes for analytics
- Write-through cache for critical data
- Database connection pooling
- Write batching for high-throughput scenarios
- Event sourcing for audit trail

**Read/Write Splitting:**
```python
class DatabaseRouter:
    def __init__(self, primary: Database, replicas: list):
        self.primary = primary
        self.replicas = replicas
        self.current_replica = 0
    
    def get_connection(self, read_only: bool = False):
        if read_only:
            # Round-robin replica selection
            conn = self.replicas[self.current_replica]
            self.current_replica = (self.current_replica + 1) % len(self.replicas)
            return conn
        else:
            return self.primary
```

### 5. Inventory Consistency

**Challenge**: Prevent overselling with high concurrency

**Solutions:**
- **Optimistic Locking**: Version-based locking
- **Pessimistic Locking**: Row-level locks (FOR UPDATE)
- **Distributed Locks**: Redis-based locks
- **Reservation System**: Reserve before checkout
- **Atomic Operations**: Database-level atomic updates

**Implementation:**
```python
class InventoryManager:
    def reserve_inventory(self, product_id: int, variant_id: int, quantity: int):
        # Use distributed lock
        lock_key = f"inventory:{product_id}:{variant_id}"
        
        with redis.lock(lock_key, timeout=5):
            # Check and update atomically
            result = self.db.execute("""
                UPDATE product_variants
                SET inventory_quantity = inventory_quantity - %s,
                    reserved_quantity = reserved_quantity + %s,
                    version = version + 1
                WHERE id = %s 
                AND inventory_quantity >= %s
                AND version = %s
                RETURNING version
            """, (quantity, quantity, variant_id, quantity, current_version))
            
            if not result:
                raise InsufficientInventoryError()
```

### 6. Message Queue Scaling

**Kafka Partitioning:**
- Partition by key (user_id, order_id) for ordering
- Multiple partitions for parallel processing
- Consumer groups for load distribution
- Auto-scaling consumers based on lag

**Event Processing:**
- Parallel processing of events
- Batch processing for efficiency
- Dead letter queue for failed events
- Event replay capability

### 7. Search Scaling

**Elasticsearch Optimization:**
- Shard indices by date or category
- Replica shards for read scaling
- Index aliases for zero-downtime updates
- Bulk indexing for efficiency

**Search Caching:**
- Cache popular search queries
- Cache filter combinations
- Pre-compute common aggregations
- CDN caching for search results

### 8. Performance Targets

**Latency Targets:**
- Product page load: < 200ms (p95)
- Search results: < 300ms (p95)
- Add to cart: < 100ms (p95)
- Checkout: < 2s (p95)

**Throughput Targets:**
- Product requests: 10K req/s
- Search queries: 5K queries/s
- Order creation: 1K orders/s
- Payment processing: 500 payments/s

**Scaling Triggers:**
- CPU > 70%: Scale up
- Memory > 80%: Scale up
- Request queue depth > 100: Scale up
- Error rate > 1%: Alert and investigate

---

## Caching Strategy

### Cache Architecture

```
Client Request
    │
    ▼
CDN Cache (Static Assets)
    │
    ├─ Hit → Return (10-20ms)
    │
    └─ Miss → Continue
        │
        ▼
Application Cache (Redis)
    │
    ├─ Hit → Return (1-5ms)
    │
    └─ Miss → Continue
        │
        ▼
Database
    │
    ▼
Return + Populate Caches
```

### Cache Patterns

1. **Cache-Aside**: For product data, search results
2. **Write-Through**: For user sessions, cart data
3. **Write-Behind**: For analytics events
4. **Refresh-Ahead**: For popular products

### Cache Invalidation

**Strategies:**
- **TTL-Based**: Automatic expiration
- **Event-Based**: Invalidate on data updates
- **Versioning**: Versioned cache keys

**Invalidation Events:**
- Product update → Invalidate product cache
- Price change → Invalidate product cache
- Stock update → Invalidate inventory cache
- Order creation → Invalidate cart cache

---

## Load Balancing

### Load Balancer Architecture

```
Internet
    │
    ▼
DNS (Route53/Cloudflare)
    │
    ├─ Region 1 (US-East)
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
API Gateway / Service Mesh
    │
    ├─ Product Service
    ├─ Cart Service
    ├─ Order Service
    └─ Payment Service
```

### Load Balancing Strategies

1. **Geographic**: Route to nearest region
2. **Round-Robin**: Equal distribution
3. **Least Connections**: Route to server with fewest connections
4. **Weighted**: Based on server capacity
5. **Consistent Hashing**: For stateful services

---

## Security

### 1. Authentication & Authorization

**Authentication:**
- OAuth 2.0 / OpenID Connect
- JWT tokens for API authentication
- Multi-factor authentication (MFA)
- Password hashing (bcrypt/argon2)

**Authorization:**
- Role-based access control (RBAC)
- API key management for partners
- Scope-based permissions

### 2. Payment Security

**PCI-DSS Compliance:**
- Don't store raw card data
- Use tokenization
- Encrypt payment data
- Secure payment gateway integration

**Fraud Detection:**
- ML-based fraud detection
- Rate limiting
- IP geolocation checks
- Device fingerprinting

### 3. Data Security

**Encryption:**
- Encrypt data at rest (AES-256)
- Encrypt data in transit (TLS 1.3)
- Encrypt sensitive fields in database

**Data Privacy:**
- GDPR compliance
- User data deletion
- Data export functionality
- Consent management

### 4. API Security

**Rate Limiting:**
- Per user: 1000 requests/minute
- Per IP: 100 requests/minute
- Per endpoint: Different limits

**Input Validation:**
- Sanitize user inputs
- Validate data types
- Prevent injection attacks

### 5. DDoS Protection

**Protection Layers:**
- CDN with DDoS mitigation
- Rate limiting at edge
- IP blacklisting
- Traffic analysis

---

## Monitoring & Analytics

### Key Metrics

**System Metrics:**
- Request rate (QPS)
- Latency (p50, p95, p99)
- Error rate
- Cache hit rate
- Database connection pool usage

**Business Metrics:**
- Daily active users (DAU)
- Orders per day
- Revenue per day
- Average order value (AOV)
- Conversion rate
- Cart abandonment rate

**Product Metrics:**
- Product views
- Add to cart rate
- Purchase rate
- Top products
- Search queries

### Analytics Pipeline

```
User Events
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

### Monitoring Tools

**APM:**
- Datadog, New Relic, or Prometheus + Grafana
- Distributed tracing (Jaeger, Zipkin)

**Logging:**
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Structured logging (JSON)

**Alerting:**
- PagerDuty, Opsgenie
- Custom alert rules

---

## Deployment Strategy

### Infrastructure

**Cloud Provider:** AWS, GCP, or Azure

**Components:**
- **Compute**: Kubernetes (EKS/GKE) or ECS
- **Database**: 
  - PostgreSQL (RDS with read replicas)
  - Cassandra (managed: AWS Keyspaces)
  - Elasticsearch (managed: AWS OpenSearch)
- **Cache**: ElastiCache (Redis)
- **CDN**: CloudFront, Cloudflare
- **Storage**: S3
- **Message Queue**: Kafka (MSK) or Kinesis

### Multi-Region Deployment

```
Region 1 (US-East)          Region 2 (EU-West)          Region 3 (APAC)
┌─────────────┐            ┌─────────────┐            ┌─────────────┐
│   Primary   │◄──────────►│   Replica   │◄──────────►│   Replica   │
│   Database  │            │   Database  │            │   Database  │
└─────────────┘            └─────────────┘            └─────────────┘
       ▲                          ▲                          ▲
       │                          │                          │
┌──────┴──────┐            ┌──────┴──────┐            ┌──────┴──────┐
│  App Servers│            │  App Servers│            │  App Servers│
│  (Active)   │            │  (Active)   │            │  (Active)   │
└─────────────┘            └─────────────┘            └─────────────┘
```

### CI/CD Pipeline

```
Code Commit
    │
    ▼
CI Pipeline
    ├─ Unit Tests
    ├─ Integration Tests
    ├─ Code Quality Checks
    └─ Security Scanning
    │
    ▼
Build Docker Images
    │
    ▼
Deploy to Staging
    │
    ├─ Integration Tests
    ├─ Performance Tests
    └─ User Acceptance Tests
    │
    ▼
Deploy to Production
    ├─ Blue-Green Deployment
    ├─ Canary Deployment
    └─ Rollback on Failure
```

---

## Capacity Planning

### Storage Estimates

**Products:**
- 10M products × 2 KB = 20 GB
- Product images: 10M × 500 KB = 5 TB
- **Total Products: ~5 TB**

**Orders:**
- 1M orders/day × 365 days = 365M orders/year
- 365M orders × 5 KB = 1.8 TB/year
- **Total Orders: ~2 TB/year**

**Users:**
- 50M users × 1 KB = 50 GB
- User data: ~50 GB

**Inventory:**
- 10M variants × 100 bytes = 1 GB
- Inventory transactions: 1B transactions/year × 200 bytes = 200 GB/year

**Total Storage (Year 1): ~8 TB**

### Compute Requirements

**API Servers:**
- 100K concurrent users
- Average 10 requests/user/minute = 1M requests/minute
- Peak load: 10x average = 10M requests/minute = 167K QPS
- Each request: ~50ms processing
- Required servers: 167K / (1000/50) = 8,350 servers
- With 50% utilization: ~4,175 servers

**Search Service:**
- 1M searches/day = 12 searches/second average
- Peak: 12 × 10 = 120 searches/second
- Each search: ~100ms (with caching)
- Required servers: 120 / (1000/100) = 12 servers

**Payment Service:**
- 1M orders/day = 12 orders/second average
- Peak: 12 × 10 = 120 orders/second
- Each payment: ~500ms (gateway call)
- Required servers: 120 / (1000/500) = 60 servers

**Total Compute: ~4,250 servers** (per region)

### Network Bandwidth

**API Traffic:**
- 167K QPS × 5 KB average = 835 MB/s = 6.7 Gbps

**Product Images:**
- 10M image views/day × 500 KB = 5 TB/day = 463 Gbps
- **CDN handles majority of this traffic**

**Total Bandwidth: ~470 Gbps** (mostly CDN)

---

## Technology Stack

### Recommended Stack (AWS)

**Compute:**
- **Container Orchestration**: Kubernetes (EKS) or ECS
- **Serverless**: AWS Lambda for event processing

**Databases:**
- **SQL**: Amazon RDS PostgreSQL with read replicas
- **NoSQL**: Amazon Keyspaces (Cassandra-compatible)
- **Search**: Amazon OpenSearch (Elasticsearch)

**Cache:**
- **Distributed Cache**: Amazon ElastiCache (Redis)

**Storage:**
- **Object Storage**: Amazon S3
- **CDN**: Amazon CloudFront

**Message Queue:**
- **Streaming**: Amazon Kinesis or Apache Kafka (MSK)
- **Queue**: Amazon SQS

**Payment:**
- **Payment Gateway**: Stripe, PayPal, Square

**Monitoring:**
- **APM**: AWS X-Ray, Datadog
- **Logging**: Amazon CloudWatch Logs, ELK Stack
- **Metrics**: Amazon CloudWatch, Prometheus + Grafana

---

## Failure Scenarios & Handling

### 1. Database Failure

**Scenario:** Primary PostgreSQL database fails.

**Impact:** 
- Product catalog unavailable
- Orders cannot be created
- User data unavailable

**Mitigation:**
- **Read Replicas**: Automatic failover to read replicas
- **Multi-Region Replication**: Cross-region replication
- **Circuit Breaker**: Fail gracefully, serve from cache
- **Degraded Mode**: Serve cached products, disable checkout

**Recovery Time:** < 30 seconds

### 2. Inventory Overselling

**Scenario:** Multiple users purchase last item simultaneously.

**Impact:** Overselling, customer dissatisfaction.

**Mitigation:**
- **Optimistic Locking**: Version-based locking
- **Reservation System**: Reserve inventory during checkout
- **Distributed Locks**: Redis-based locks
- **Compensating Transactions**: Cancel orders if oversold

**Implementation:**
```python
@transactional
def purchase_product(variant_id, quantity):
    inventory = Inventory.objects.select_for_update().get(variant_id=variant_id)
    if inventory.available_quantity < quantity:
        raise InsufficientStockError()
    inventory.quantity -= quantity
    inventory.save()
```

### 3. Payment Gateway Failure

**Scenario:** Payment gateway (Stripe) is down.

**Impact:** Cannot process payments, orders stuck.

**Mitigation:**
- **Multiple Payment Gateways**: Support Stripe, PayPal, Square
- **Queue Payments**: Queue payment requests, retry later
- **Graceful Degradation**: Allow order creation, process payment later
- **Manual Processing**: Admin can process payments manually

**Recovery:** Automatic retry with exponential backoff

### 4. Cart Loss

**Scenario:** Redis cache fails, user loses cart.

**Impact:** Poor user experience, lost sales.

**Mitigation:**
- **Database Backup**: Persist carts to PostgreSQL
- **Session Storage**: Store cart in session
- **Recovery**: Recover cart from database on cache miss

### 5. Search Service Failure

**Scenario:** Elasticsearch cluster fails.

**Impact:** Product search unavailable.

**Mitigation:**
- **Database Fallback**: Fallback to database search (slower)
- **Cached Results**: Serve cached search results
- **Degraded Mode**: Disable search, show category browsing

### 6. High Traffic (Black Friday)

**Scenario:** 10x normal traffic during sale.

**Impact:** Service degradation, potential downtime.

**Mitigation:**
- **Auto-Scaling**: Pre-scale before sale
- **CDN**: Cache aggressively
- **Queue System**: Queue requests if overloaded
- **Rate Limiting**: Limit requests per user
- **Degraded Features**: Disable non-critical features

---

## Trade-offs & Design Decisions

### 1. Database Choice: PostgreSQL vs NoSQL

**Decision:** PostgreSQL for transactional data, NoSQL for events.

**Trade-offs:**

| Aspect | PostgreSQL | NoSQL (Cassandra) |
|--------|-----------|-------------------|
| **ACID** | Yes | No |
| **Consistency** | Strong | Eventual |
| **Query Flexibility** | Excellent (SQL) | Limited |
| **Scaling** | Vertical + replicas | Horizontal |
| **Use Case** | Orders, Products | Events, Analytics |

**Why PostgreSQL:**
- **ACID Required**: Orders need strong consistency
- **Complex Queries**: Product catalog needs SQL flexibility
- **Relationships**: Foreign keys, joins needed

### 2. Inventory: Strong vs Eventual Consistency

**Decision:** Strong consistency for inventory.

**Trade-offs:**

| Approach | Pros | Cons |
|----------|------|------|
| **Strong Consistency** | No overselling | Lower throughput |
| **Eventual Consistency** | Higher throughput | Risk of overselling |

**Why Strong Consistency:**
- **Customer Trust**: Overselling damages reputation
- **Legal**: May have legal implications
- **Cost**: Accept lower throughput for accuracy

### 3. Cart Storage: Redis vs Database

**Decision:** Redis for active carts, Database for persistence.

**Trade-offs:**

| Storage | Pros | Cons |
|---------|------|------|
| **Redis** | Fast, scalable | Volatile (can lose data) |
| **Database** | Persistent | Slower, more expensive |

**Hybrid Approach:**
- **Redis**: Active carts (fast access)
- **Database**: Backup (persistence)
- **Result**: Best of both worlds

### 4. Payment: Synchronous vs Asynchronous

**Decision:** Synchronous payment processing.

**Trade-offs:**

| Approach | Pros | Cons |
|----------|------|------|
| **Synchronous** | Immediate feedback | Slower checkout |
| **Asynchronous** | Faster checkout | Complex error handling |

**Why Synchronous:**
- **User Experience**: Immediate confirmation
- **Error Handling**: Easier to handle failures
- **Inventory**: Can reserve inventory immediately

### 5. Search: Database vs Elasticsearch

**Decision:** Elasticsearch for search, Database for storage.

**Trade-offs:**

| Approach | Pros | Cons |
|----------|------|------|
| **Database** | Simple, consistent | Slow for complex queries |
| **Elasticsearch** | Fast, flexible | Additional complexity |

**Why Elasticsearch:**
- **Performance**: 10x faster for search
- **Features**: Faceted search, autocomplete
- **Scalability**: Better for high search volume

---

## Interview Discussion Points

### Key Questions to Address

1. **"How do you prevent inventory overselling?"**
   - **Answer**: 
     - Use optimistic locking (version-based)
     - Reserve inventory during checkout
     - Use distributed locks (Redis)
     - Transactional updates with row-level locks
     - Compensating transactions for failures

2. **"How do you handle a flash sale with 100x traffic?"**
   - **Answer**:
     - Pre-scale infrastructure before sale
     - Cache popular products aggressively
     - Queue system for checkout requests
     - Rate limiting per user
     - Degrade non-critical features

3. **"How do you ensure payment security?"**
   - **Answer**:
     - PCI-DSS compliance
     - Tokenization (don't store raw cards)
     - Encryption (TLS 1.3)
     - Fraud detection (ML-based)
     - Secure payment gateway integration

4. **"How do you handle cart abandonment?"**
   - **Answer**:
     - Save carts for 30 days
     - Email reminders (24h, 48h, 7 days)
     - Offer discounts
     - Retargeting ads
     - Analyze abandonment reasons

5. **"How do you scale product search?"**
   - **Answer**:
     - Use Elasticsearch cluster
     - Cache popular searches
     - Shard index by category
     - Pre-compute facets
     - Use CDN for search results

### Scalability Deep Dive

**Q: "How do you scale from 1K to 10M products?"**

**Answer:**

**Phase 1: 1K-100K Products**
- Single PostgreSQL database
- Basic caching
- Simple search (database queries)

**Phase 2: 100K-1M Products**
- PostgreSQL with read replicas
- Redis caching
- Elasticsearch for search
- CDN for images

**Phase 3: 1M-10M Products**
- Database sharding
- Multiple Elasticsearch nodes
- Aggressive caching
- Image optimization

**Key Scaling Principles:**
1. **Horizontal Scaling**: Add shards, not bigger databases
2. **Caching**: Cache aggressively (80%+ hit rate)
3. **Search**: Use dedicated search engine
4. **CDN**: Offload images to CDN
5. **Denormalization**: Pre-compute frequently accessed data

### Performance Optimization

**Q: "How do you optimize checkout latency?"**

**Answer:**

**Current Flow:**
1. Validate cart (10ms)
2. Calculate totals (20ms)
3. Process payment (500ms) - **Bottleneck**
4. Create order (50ms)
5. Update inventory (30ms)
**Total: 610ms**

**Optimizations:**
1. **Async Payment**: Process payment asynchronously (reduce to 50ms)
2. **Pre-calculate Totals**: Calculate during cart update
3. **Cache Inventory**: Cache inventory checks
4. **Batch Operations**: Batch database writes
5. **Connection Pooling**: Reuse database connections

**Optimized Flow:**
1. Validate cart (10ms)
2. Get pre-calculated totals (5ms)
3. Queue payment (10ms)
4. Create order (50ms)
5. Update inventory (30ms)
**Total: 105ms** (5x improvement)

### Cost Optimization

**Q: "How do you optimize costs at scale?"**

**Answer:**

1. **Database Costs** (40% of total):
   - Use read replicas for reads
   - Archive old orders
   - Compress data

2. **CDN Costs** (30% of total):
   - Optimize images (WebP, compression)
   - Cache aggressively
   - Use regional pricing

3. **Compute Costs** (20% of total):
   - Auto-scaling (scale down during off-peak)
   - Use spot instances for batch jobs
   - Optimize code

4. **Storage Costs** (10% of total):
   - Lifecycle policies (move old data to cheaper storage)
   - Compress images
   - Delete unused data

**Total Savings**: 30-40% cost reduction

---

## References

- [System Design Primer](https://github.com/donnemartin/system-design-primer)
- [E-Commerce Architecture Patterns](https://aws.amazon.com/architecture/ecommerce/)
- [Shopify Architecture](https://engineering.shopify.com/blogs/engineering)
- [Amazon Architecture](http://highscalability.com/amazon-architecture)
- [Stripe Payment Processing](https://stripe.com/docs)
- [Elasticsearch Best Practices](https://www.elastic.co/guide/en/elasticsearch/reference/current/best-practices.html)

