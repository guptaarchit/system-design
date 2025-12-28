# Develop an Ads Management and Display System for a Social Feed

## Table of Contents
1. [Overview](#overview)
2. [Requirements](#requirements)
3. [High-Level Design (HLD)](#high-level-design-hld)
4. [Low-Level Design (LLD)](#low-level-design-lld)
5. [System Architecture](#system-architecture)
6. [Ad Serving Pipeline](#ad-serving-pipeline)
7. [Database Design](#database-design)
8. [API Design](#api-design)
9. [Ad Targeting](#ad-targeting)
10. [Bidding & Auction](#bidding--auction)
11. [Fault Tolerance](#fault-tolerance)
12. [Failure Safety](#failure-safety)
13. [Scalability Considerations](#scalability-considerations)
14. [Optimizations](#optimizations)
15. [Caching Strategy](#caching-strategy)
16. [Monitoring & Analytics](#monitoring--analytics)
17. [Capacity Planning](#capacity-planning)
18. [Technology Stack](#technology-stack)
19. [Interview Discussion Points](#interview-discussion-points)

---

## Overview

An ads management and display system for a social feed that serves relevant ads to users, manages ad campaigns, handles real-time bidding, tracks ad performance, and optimizes ad delivery. The system must handle millions of ad requests per second, support complex targeting, and provide real-time analytics.

**Key Features:**
- Ad campaign management
- Real-time ad serving
- User targeting and segmentation
- Real-time bidding (RTB)
- Ad performance tracking
- Budget management
- Ad creative management
- A/B testing

---

## Requirements

### Functional Requirements

1. **Ad Campaign Management**
   - Create/edit campaigns
   - Set budgets and bids
   - Define targeting rules
   - Schedule campaigns

2. **Ad Serving**
   - Serve ads in feed
   - Real-time ad selection
   - Ad frequency capping
   - Ad relevance scoring

3. **Targeting**
   - Demographic targeting
   - Interest-based targeting
   - Behavioral targeting
   - Lookalike audiences

4. **Analytics**
   - Impressions tracking
   - Clicks tracking
   - Conversions tracking
   - Performance reporting

### Non-Functional Requirements

1. **Scalability**
   - Handle 10M+ ad requests per second
   - Support 1M+ active campaigns
   - Serve ads with < 100ms latency

2. **Performance**
   - Ad selection: < 50ms
   - Ad serving: < 100ms
   - Real-time bidding: < 200ms

3. **Reliability**
   - 99.9% uptime
   - No ad loss
   - Accurate tracking

---

## High-Level Design (HLD)

### System Overview

The Ads Management System is a distributed, high-throughput system designed to serve personalized ads to users in real-time. The architecture follows a microservices pattern with clear separation of concerns.

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Client Applications                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 │
│  │ Mobile App   │  │  Web App     │  │  API Clients │                 │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                 │
└─────────┼─────────────────┼─────────────────┼──────────────────────────┘
          │                 │                 │
          └─────────────────┴─────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        API Gateway / Load Balancer                      │
│  - Request routing                                                      │
│  - Rate limiting                                                        │
│  - SSL termination                                                      │
│  - Authentication                                                       │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│   Region 1    │    │   Region 2    │    │   Region N    │
│  (US-East)    │    │  (EU-West)    │    │  (AP-South)   │
└───────┬───────┘    └───────┬───────┘    └───────┬───────┘
        │                    │                    │
        ▼                    ▼                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      Ad Serving Service Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 │
│  │ Ad Request   │  │ Ad Selection │  │ Ad Delivery  │                 │
│  │  Handler     │  │   Engine     │  │   Service    │                 │
│  └──────────────┘  └──────────────┘  └──────────────┘                 │
└─────────────────────────────────────────────────────────────────────────┘
        │                    │                    │
        ▼                    ▼                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    Campaign Management Service                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 │
│  │ Campaign     │  │ Budget       │  │ Targeting    │                 │
│  │  Manager     │  │  Manager     │  │  Manager     │                 │
│  └──────────────┘  └──────────────┘  └──────────────┘                 │
└─────────────────────────────────────────────────────────────────────────┘
        │                    │                    │
        ▼                    ▼                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    Bidding & Auction Service                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 │
│  │ RTB          │  │ Auction      │  │ Budget       │                 │
│  │  Engine      │  │  Manager     │  │  Validator   │                 │
│  └──────────────┘  └──────────────┘  └──────────────┘                 │
└─────────────────────────────────────────────────────────────────────────┘
        │                    │                    │
        ▼                    ▼                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    Analytics & Tracking Service                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 │
│  │ Impression   │  │ Click        │  │ Conversion   │                 │
│  │  Tracker     │  │  Tracker     │  │  Tracker     │                 │
│  └──────────────┘  └──────────────┘  └──────────────┘                 │
└─────────────────────────────────────────────────────────────────────────┘
        │                    │                    │
        ▼                    ▼                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         Data Layer                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 │
│  │ PostgreSQL   │  │ Cassandra    │  │ Redis        │                 │
│  │ (Campaigns)  │  │ (Tracking)   │  │ (Cache)      │                 │
│  └──────────────┘  └──────────────┘  └──────────────┘                 │
│                                                                         │
│  ┌──────────────┐  ┌──────────────┐                                  │
│  │Elasticsearch │  │   CDN         │                                  │
│  │ (Ad Index)   │  │ (Creatives)   │                                  │
│  └──────────────┘  └──────────────┘                                  │
└─────────────────────────────────────────────────────────────────────────┘
```

### Key Components

1. **API Gateway**: Entry point for all requests, handles routing, authentication, rate limiting
2. **Ad Serving Service**: Core service for ad selection and delivery
3. **Campaign Management Service**: Manages campaigns, budgets, targeting rules
4. **Bidding & Auction Service**: Handles real-time bidding and auction logic
5. **Analytics Service**: Tracks impressions, clicks, conversions
6. **Data Layer**: Multiple databases optimized for different use cases

### Design Principles

- **Microservices Architecture**: Independent, scalable services
- **Event-Driven**: Asynchronous processing for analytics
- **Caching-First**: Aggressive caching for performance
- **Eventual Consistency**: Acceptable for analytics data
- **Strong Consistency**: Required for budget and campaign data

---

## Low-Level Design (LLD)

### Ad Request Handler

```python
class AdRequestHandler:
    def __init__(self):
        self.ad_selection_engine = AdSelectionEngine()
        self.cache = RedisCache()
        self.metrics = MetricsCollector()
        self.circuit_breaker = CircuitBreaker()
    
    async def handle_request(self, request: AdRequest) -> AdResponse:
        try:
            # Extract context
            user_id = request.user_id
            context = self.extract_context(request)
            
            # Check cache first
            cache_key = f"ad:{user_id}:{hash(context)}"
            cached_ad = await self.cache.get(cache_key)
            if cached_ad:
                return cached_ad
            
            # Get user profile (with fallback)
            user_profile = await self.get_user_profile_with_fallback(user_id)
            
            # Select ad
            selected_ad = await self.ad_selection_engine.select_ad(
                user_id, user_profile, context
            )
            
            # Cache result
            await self.cache.set(cache_key, selected_ad, ttl=60)
            
            # Track asynchronously
            asyncio.create_task(self.track_impression(user_id, selected_ad))
            
            return selected_ad
            
        except Exception as e:
            self.metrics.record_error(e)
            # Fallback to default ad
            return self.get_default_ad()
```

### Ad Selection Engine (Detailed)

```python
class AdSelectionEngine:
    def __init__(self):
        self.targeting_engine = TargetingEngine()
        self.relevance_scorer = RelevanceScorer()
        self.frequency_capper = FrequencyCapper()
        self.budget_validator = BudgetValidator()
        self.cache = RedisCache()
        self.db = DatabasePool()
    
    async def select_ad(self, user_id: int, user_profile: dict, context: dict) -> dict:
        # Step 1: Get eligible campaigns (cached)
        eligible_campaigns = await self.get_eligible_campaigns(user_profile, context)
        
        if not eligible_campaigns:
            return self.get_default_ad()
        
        # Step 2: Get ads for campaigns
        campaign_ads = await self.get_campaign_ads(eligible_campaigns)
        
        # Step 3: Filter by frequency cap
        frequency_filtered = await self.frequency_capper.filter(user_id, campaign_ads)
        
        # Step 4: Validate budgets
        budget_validated = await self.budget_validator.validate(frequency_filtered)
        
        # Step 5: Score by relevance
        scored_ads = await self.relevance_scorer.score(
            user_profile, budget_validated, context
        )
        
        # Step 6: Run auction
        winner = await self.run_auction(scored_ads, user_profile)
        
        return winner
    
    async def get_eligible_campaigns(self, user_profile: dict, context: dict) -> list:
        cache_key = f"eligible_campaigns:{hash(str(user_profile))}:{hash(str(context))}"
        
        # Check cache
        cached = await self.cache.get(cache_key)
        if cached:
            return cached
        
        # Query database
        campaigns = await self.targeting_engine.find_eligible_campaigns(
            user_profile, context
        )
        
        # Cache for 1 minute
        await self.cache.set(cache_key, campaigns, ttl=60)
        
        return campaigns
```

### Targeting Engine (Detailed)

```python
class TargetingEngine:
    def __init__(self):
        self.db = DatabasePool()
        self.elasticsearch = ElasticsearchClient()
        self.cache = RedisCache()
    
    async def find_eligible_campaigns(
        self, user_profile: dict, context: dict
    ) -> list:
        # Build query
        query = self.build_targeting_query(user_profile, context)
        
        # Search Elasticsearch for matching campaigns
        results = await self.elasticsearch.search(
            index="campaigns",
            body=query
        )
        
        campaign_ids = [hit['_id'] for hit in results['hits']['hits']]
        
        # Fetch campaign details from database
        campaigns = await self.db.fetch_campaigns(campaign_ids)
        
        # Filter by active status and dates
        active_campaigns = [
            c for c in campaigns 
            if c['status'] == 'active' and self.is_within_date_range(c)
        ]
        
        return active_campaigns
    
    def build_targeting_query(self, user_profile: dict, context: dict) -> dict:
        must_clauses = []
        
        # Demographic targeting
        if 'age' in user_profile:
            must_clauses.append({
                "range": {
                    "targeting.age_min": {"lte": user_profile['age']},
                    "targeting.age_max": {"gte": user_profile['age']}
                }
            })
        
        if 'gender' in user_profile:
            must_clauses.append({
                "terms": {
                    "targeting.genders": [user_profile['gender']]
                }
            })
        
        # Location targeting
        if 'location' in user_profile:
            must_clauses.append({
                "geo_distance": {
                    "distance": "50km",
                    "targeting.locations": {
                        "lat": user_profile['location']['lat'],
                        "lon": user_profile['location']['lon']
                    }
                }
            })
        
        # Interest targeting
        if 'interests' in user_profile:
            must_clauses.append({
                "terms": {
                    "targeting.interests": user_profile['interests']
                }
            })
        
        # Contextual targeting
        if 'content_category' in context:
            must_clauses.append({
                "terms": {
                    "targeting.content_categories": [context['content_category']]
                }
            })
        
        return {
            "query": {
                "bool": {
                    "must": must_clauses,
                    "filter": [
                        {"term": {"status": "active"}},
                        {"range": {"budget_remaining": {"gt": 0}}}
                    ]
                }
            },
            "size": 100,
            "sort": [{"bid_amount": {"order": "desc"}}]
        }
```

### Budget Validator

```python
class BudgetValidator:
    def __init__(self):
        self.db = DatabasePool()
        self.cache = RedisCache()
        self.lock_manager = DistributedLockManager()
    
    async def validate(self, ads: list) -> list:
        validated_ads = []
        
        for ad in ads:
            campaign_id = ad['campaign_id']
            
            # Check budget with distributed lock
            async with self.lock_manager.acquire(f"budget:{campaign_id}"):
                budget_status = await self.check_budget(campaign_id)
                
                if budget_status['has_budget']:
                    # Reserve budget atomically
                    reserved = await self.reserve_budget(
                        campaign_id, ad['bid_amount']
                    )
                    
                    if reserved:
                        validated_ads.append(ad)
        
        return validated_ads
    
    async def check_budget(self, campaign_id: int) -> dict:
        cache_key = f"budget:{campaign_id}"
        
        # Check cache first
        cached = await self.cache.get(cache_key)
        if cached:
            return cached
        
        # Query database
        campaign = await self.db.fetch_campaign(campaign_id)
        
        budget_info = {
            'has_budget': campaign['budget_spent'] < campaign['budget_total'],
            'daily_budget_ok': campaign['budget_daily_spent'] < campaign['budget_daily'],
            'remaining': campaign['budget_total'] - campaign['budget_spent']
        }
        
        # Cache for 5 seconds
        await self.cache.set(cache_key, budget_info, ttl=5)
        
        return budget_info
    
    async def reserve_budget(self, campaign_id: int, amount: float) -> bool:
        # Atomic budget reservation using database transaction
        async with self.db.transaction():
            campaign = await self.db.fetch_campaign_for_update(campaign_id)
            
            if campaign['budget_spent'] + amount <= campaign['budget_total']:
                await self.db.update_campaign_budget(
                    campaign_id,
                    budget_spent=campaign['budget_spent'] + amount
                )
                return True
            
            return False
```

### Frequency Capper

```python
class FrequencyCapper:
    def __init__(self):
        self.redis = RedisClient()
    
    async def filter(self, user_id: int, ads: list) -> list:
        filtered_ads = []
        
        for ad in ads:
            campaign_id = ad['campaign_id']
            
            # Check frequency cap
            key = f"freq_cap:{user_id}:{campaign_id}"
            
            # Get current count
            count = await self.redis.get(key) or 0
            count = int(count)
            
            # Check against frequency cap
            freq_cap = ad.get('frequency_cap', 3)  # Default 3 per day
            
            if count < freq_cap:
                filtered_ads.append(ad)
                # Increment counter
                await self.redis.incr(key)
                await self.redis.expire(key, 86400)  # 24 hours
        
        return filtered_ads
```

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                             │
│  (Social Feed App, Web App)                                     │
└────────────────┬────────────────────────────────────────────────┘
                 │ HTTPS
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Ad Request Handler                             │
│  - Receive ad requests                                           │
│  - Extract user context                                          │
└────────────┬─────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Ad Selection Engine                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Targeting  │  │   Relevance  │  │   Frequency  │         │
│  │   Engine     │  │   Scorer     │  │   Capper     │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Bidding & Auction                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   RTB        │  │   Budget     │  │   Winner     │         │
│  │   Service    │  │   Manager    │  │   Selector   │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Ad Delivery                                    │
│  - Return ad creative                                            │
│  - Track impression                                              │
└────────────┬─────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Data Layer                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Campaigns  │  │   Ads        │  │   Tracking   │         │
│  │     DB       │  │     DB       │  │     DB       │         │
│  │ (PostgreSQL) │  │ (PostgreSQL) │  │ (Cassandra)  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐                            │
│  │   User       │  │   Ad         │                            │
│  │   Profiles   │  │   Index      │                            │
│  │  (Redis)     │  │(Elasticsearch│                            │
│  └──────────────┘  └──────────────┘                            │
└────────────────────────────────────────────────────────────────┘
```

---

## Ad Serving Pipeline

### Ad Request Flow

```
┌──────────┐         ┌──────────────┐         ┌──────────────┐
│   User   │────────▶│   Ad Request │────────▶│   Targeting │
│   Feed   │         │   Handler    │         │   Engine     │
└──────────┘         └──────────────┘         └──────┬───────┘
                                                     │
                                                     ▼
                                            ┌─────────────────┐
                                            │   Ad Selection  │
                                            │   Engine        │
                                            └──────┬──────────┘
                                                   │
                                                   ▼
                                            ┌─────────────────┐
                                            │   Bidding &     │
                                            │   Auction       │
                                            └──────┬──────────┘
                                                   │
                                                   ▼
                                            ┌─────────────────┐
                                            │   Ad Delivery   │
                                            └─────────────────┘
```

### Ad Selection

```python
class AdSelectionEngine:
    def __init__(self):
        self.targeting_engine = TargetingEngine()
        self.relevance_scorer = RelevanceScorer()
        self.frequency_capper = FrequencyCapper()
    
    def select_ad(self, user_id: int, context: dict) -> dict:
        # Get user profile
        user_profile = self.get_user_profile(user_id)
        
        # Find eligible ads
        eligible_ads = self.targeting_engine.find_eligible_ads(user_profile, context)
        
        # Filter by frequency cap
        frequency_filtered = self.frequency_capper.filter(user_id, eligible_ads)
        
        # Score ads by relevance
        scored_ads = self.relevance_scorer.score(user_profile, frequency_filtered, context)
        
        # Select top ad
        top_ad = self.select_top_ad(scored_ads)
        
        # Track selection
        self.track_ad_selection(user_id, top_ad)
        
        return top_ad
    
    def select_top_ad(self, scored_ads: list) -> dict:
        # Select ad with highest score
        return max(scored_ads, key=lambda x: x['score'])
```

---

## Database Design

### Campaigns Table

```sql
CREATE TABLE campaigns (
    campaign_id BIGSERIAL PRIMARY KEY,
    advertiser_id BIGINT NOT NULL,
    name VARCHAR(255) NOT NULL,
    status VARCHAR(20) DEFAULT 'active', -- active, paused, completed
    budget_total DECIMAL(10, 2),
    budget_daily DECIMAL(10, 2),
    budget_spent DECIMAL(10, 2) DEFAULT 0.00,
    bid_type VARCHAR(20), -- CPC, CPM, CPA
    bid_amount DECIMAL(10, 2),
    start_date DATE,
    end_date DATE,
    targeting_rules JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_status (status),
    INDEX idx_advertiser (advertiser_id)
);
```

### Ads Table

```sql
CREATE TABLE ads (
    ad_id BIGSERIAL PRIMARY KEY,
    campaign_id BIGINT NOT NULL,
    creative_type VARCHAR(20), -- image, video, carousel
    creative_url VARCHAR(500),
    headline VARCHAR(255),
    description TEXT,
    landing_page_url VARCHAR(500),
    status VARCHAR(20) DEFAULT 'active',
    impressions INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id),
    INDEX idx_campaign (campaign_id),
    INDEX idx_status (status)
);
```

### Ad Impressions Table

```sql
CREATE TABLE ad_impressions (
    impression_id BIGSERIAL PRIMARY KEY,
    ad_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    campaign_id BIGINT NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW(),
    user_agent TEXT,
    ip_address VARCHAR(45),
    FOREIGN KEY (ad_id) REFERENCES ads(ad_id),
    INDEX idx_ad_timestamp (ad_id, timestamp),
    INDEX idx_user_timestamp (user_id, timestamp)
) PARTITION BY RANGE (timestamp);
```

---

## API Design

### Ad Serving API

```
GET /api/v1/ads/serve?user_id=123&context={...}
```

**Response:**
```json
{
  "ad_id": 456,
  "creative_url": "https://cdn.example.com/ad.jpg",
  "headline": "Special Offer",
  "description": "Get 20% off",
  "landing_page": "https://example.com/offer",
  "tracking_pixel": "https://track.example.com/impression?id=456"
}
```

### Campaign Management API

```
POST   /api/v1/campaigns
GET    /api/v1/campaigns/{campaign_id}
PUT    /api/v1/campaigns/{campaign_id}
GET    /api/v1/campaigns/{campaign_id}/performance
```

---

## Ad Targeting

### Targeting Engine

```python
class TargetingEngine:
    def find_eligible_ads(self, user_profile: dict, context: dict) -> list:
        eligible_ads = []
        
        # Get active campaigns
        campaigns = self.get_active_campaigns()
        
        for campaign in campaigns:
            if self.matches_targeting(campaign.targeting_rules, user_profile, context):
                ads = self.get_campaign_ads(campaign.campaign_id)
                eligible_ads.extend(ads)
        
        return eligible_ads
    
    def matches_targeting(self, rules: dict, user_profile: dict, context: dict) -> bool:
        # Demographic targeting
        if 'demographics' in rules:
            if not self.match_demographics(rules['demographics'], user_profile):
                return False
        
        # Interest targeting
        if 'interests' in rules:
            if not self.match_interests(rules['interests'], user_profile):
                return False
        
        # Behavioral targeting
        if 'behaviors' in rules:
            if not self.match_behaviors(rules['behaviors'], user_profile):
                return False
        
        # Contextual targeting
        if 'context' in rules:
            if not self.match_context(rules['context'], context):
                return False
        
        return True
```

---

## Bidding & Auction

### Real-time Bidding

```python
class BiddingService:
    def run_auction(self, eligible_ads: list, user_profile: dict) -> dict:
        bids = []
        
        for ad in eligible_ads:
            bid = self.calculate_bid(ad, user_profile)
            bids.append({
                'ad_id': ad['ad_id'],
                'bid': bid,
                'ad': ad
            })
        
        # Select winner (highest bid)
        winner = max(bids, key=lambda x: x['bid'])
        
        # Charge second-price (Vickrey auction)
        second_highest_bid = sorted(bids, key=lambda x: x['bid'], reverse=True)[1]['bid']
        charge_amount = min(winner['bid'], second_highest_bid)
        
        return {
            'winner': winner['ad'],
            'bid': winner['bid'],
            'charge': charge_amount
        }
```

---

## Fault Tolerance

### Fault Tolerance Strategy

The system is designed to handle failures gracefully at multiple levels, ensuring continuous ad serving even when components fail.

### Component-Level Fault Tolerance

#### 1. Ad Serving Service Fault Tolerance

**Failure Scenarios:**
- Service instance crash
- Network partition
- Database connection failure
- Cache unavailability

**Mitigation Strategies:**

```python
class FaultTolerantAdService:
    def __init__(self):
        self.primary_service = AdSelectionEngine()
        self.fallback_service = FallbackAdEngine()
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60
        )
        self.health_checker = HealthChecker()
    
    async def serve_ad(self, request: AdRequest) -> AdResponse:
        try:
            # Check circuit breaker
            if self.circuit_breaker.is_open():
                return await self.fallback_service.serve_ad(request)
            
            # Try primary service
            result = await self.primary_service.select_ad(request)
            
            # Record success
            self.circuit_breaker.record_success()
            
            return result
            
        except Exception as e:
            # Record failure
            self.circuit_breaker.record_failure()
            
            # Fallback to default ad
            return await self.fallback_service.serve_ad(request)
```

**Fallback Mechanisms:**
- **Default Ads**: Pre-configured fallback ads when selection fails
- **Cached Ads**: Serve from cache when real-time selection fails
- **Simplified Selection**: Use cached eligible ads when targeting fails

#### 2. Database Fault Tolerance

**PostgreSQL (Campaigns DB):**
- **Primary-Replica Setup**: Multiple read replicas
- **Connection Pooling**: Handle connection failures gracefully
- **Read Replicas**: Route reads to replicas, writes to primary
- **Failover**: Automatic failover to replica if primary fails

```python
class FaultTolerantDatabase:
    def __init__(self):
        self.primary = DatabaseConnection(primary_config)
        self.replicas = [DatabaseConnection(r) for r in replica_configs]
        self.replica_index = 0
        self.health_checker = HealthChecker()
    
    async def read(self, query: str) -> list:
        # Try replicas first (round-robin)
        for _ in range(len(self.replicas)):
            replica = self.replicas[self.replica_index]
            self.replica_index = (self.replica_index + 1) % len(self.replicas)
            
            if self.health_checker.is_healthy(replica):
                try:
                    return await replica.execute(query)
                except Exception:
                    continue
        
        # Fallback to primary
        return await self.primary.execute(query)
    
    async def write(self, query: str) -> bool:
        try:
            return await self.primary.execute(query)
        except Exception:
            # Retry with exponential backoff
            return await self.retry_with_backoff(query)
```

**Cassandra (Tracking DB):**
- **Multi-Datacenter**: Replication across datacenters
- **Quorum Consistency**: Balance between consistency and availability
- **Hinted Handoff**: Handle temporary node failures
- **Read Repair**: Automatic consistency repair

#### 3. Cache Fault Tolerance

**Redis Cluster:**
- **Cluster Mode**: Automatic sharding and failover
- **Replication**: Each shard has replicas
- **Local Cache Fallback**: In-memory cache when Redis unavailable
- **Circuit Breaker**: Fail fast when Redis is down

```python
class FaultTolerantCache:
    def __init__(self):
        self.redis = RedisCluster()
        self.local_cache = LocalCache(max_size=10000)
        self.circuit_breaker = CircuitBreaker()
    
    async def get(self, key: str) -> Optional[dict]:
        # Try local cache first
        local_value = self.local_cache.get(key)
        if local_value:
            return local_value
        
        # Try Redis if circuit breaker is closed
        if not self.circuit_breaker.is_open():
            try:
                value = await self.redis.get(key)
                if value:
                    # Update local cache
                    self.local_cache.set(key, value, ttl=60)
                    self.circuit_breaker.record_success()
                    return value
            except Exception as e:
                self.circuit_breaker.record_failure()
        
        return None
    
    async def set(self, key: str, value: dict, ttl: int = 3600):
        # Always update local cache
        self.local_cache.set(key, value, ttl=min(ttl, 300))
        
        # Try Redis if circuit breaker is closed
        if not self.circuit_breaker.is_open():
            try:
                await self.redis.set(key, value, ttl=ttl)
                self.circuit_breaker.record_success()
            except Exception as e:
                self.circuit_breaker.record_failure()
```

#### 4. External Service Fault Tolerance

**Elasticsearch:**
- **Cluster Setup**: Multiple nodes with replication
- **Retry Logic**: Exponential backoff on failures
- **Fallback Query**: Use database query when Elasticsearch unavailable

**CDN:**
- **Multiple CDNs**: Fallback to secondary CDN
- **Origin Fallback**: Serve from origin if CDN fails
- **Health Monitoring**: Continuous CDN health checks

### System-Level Fault Tolerance

#### 1. Graceful Degradation

**Degradation Levels:**

1. **Full Functionality**: All services operational
2. **Reduced Targeting**: Use cached targeting data
3. **Simplified Selection**: Skip complex scoring, use basic selection
4. **Default Ads**: Serve pre-configured default ads
5. **No Ads**: Return empty response (last resort)

```python
class GracefulDegradation:
    async def serve_ad(self, request: AdRequest) -> AdResponse:
        try:
            # Level 1: Full functionality
            return await self.full_ad_selection(request)
        except TargetingServiceDown:
            # Level 2: Use cached targeting
            return await self.cached_targeting_selection(request)
        except ScoringServiceDown:
            # Level 3: Simplified selection
            return await self.simplified_selection(request)
        except Exception:
            # Level 4: Default ads
            return await self.default_ad_selection(request)
```

#### 2. Health Checks and Monitoring

**Health Check Endpoints:**
- `/health`: Basic health check
- `/health/ready`: Readiness probe (dependencies available)
- `/health/live`: Liveness probe (service is running)

**Dependency Health:**
- Database connectivity
- Cache connectivity
- External service availability
- Resource utilization (CPU, memory, disk)

#### 3. Retry and Backoff Strategies

**Exponential Backoff:**
```python
class RetryHandler:
    async def execute_with_retry(self, func, max_retries=3):
        for attempt in range(max_retries):
            try:
                return await func()
            except RetryableException as e:
                if attempt == max_retries - 1:
                    raise
                
                wait_time = 2 ** attempt  # Exponential backoff
                await asyncio.sleep(wait_time)
```

**Jitter:**
- Add random jitter to prevent thundering herd
- Spread retry attempts across time

---

## Failure Safety

### Failure Safety Principles

1. **Fail-Safe Defaults**: System defaults to safe state on failure
2. **No Data Loss**: Critical data is never lost
3. **Audit Trail**: All failures are logged and audited
4. **Recovery Mechanisms**: Automatic recovery when possible

### Critical Failure Scenarios

#### 1. Budget Overrun Prevention

**Problem:** Campaign budget exceeded due to concurrent requests.

**Solution:** Distributed locking and atomic operations.

```python
class BudgetSafety:
    async def reserve_budget(self, campaign_id: int, amount: float) -> bool:
        # Use distributed lock
        lock_key = f"budget_lock:{campaign_id}"
        
        async with self.distributed_lock.acquire(lock_key, timeout=5):
            # Check budget
            campaign = await self.db.fetch_campaign_for_update(campaign_id)
            
            if campaign['budget_spent'] + amount > campaign['budget_total']:
                return False
            
            # Atomic update
            await self.db.execute(
                """
                UPDATE campaigns 
                SET budget_spent = budget_spent + %s 
                WHERE campaign_id = %s 
                AND budget_spent + %s <= budget_total
                """,
                (amount, campaign_id, amount)
            )
            
            return True
```

**Safety Mechanisms:**
- Database-level constraints
- Distributed locks
- Atomic transactions
- Budget alerts before exhaustion

#### 2. Ad Impression Tracking Safety

**Problem:** Lost impressions due to tracking service failure.

**Solution:** Multiple tracking mechanisms with guaranteed delivery.

```python
class ImpressionTrackingSafety:
    def __init__(self):
        self.primary_tracker = ImpressionTracker()
        self.queue = MessageQueue()  # Kafka/RabbitMQ
        self.local_buffer = LocalBuffer()
    
    async def track_impression(self, impression: dict):
        # Method 1: Direct tracking (best effort)
        try:
            await self.primary_tracker.track(impression)
        except Exception:
            pass
        
        # Method 2: Queue for async processing (guaranteed)
        await self.queue.publish('impressions', impression)
        
        # Method 3: Local buffer (last resort)
        self.local_buffer.append(impression)
        
        # Background worker processes queue and buffer
```

**Safety Mechanisms:**
- Message queue with persistence
- Local buffer with periodic flush
- Retry mechanisms
- Dead letter queue for failed messages

#### 3. Ad Selection Consistency

**Problem:** Same ad shown multiple times due to race conditions.

**Solution:** Idempotency keys and distributed locks.

```python
class AdSelectionConsistency:
    async def select_ad(self, user_id: int, request_id: str) -> dict:
        # Check if already processed
        cache_key = f"ad_selection:{request_id}"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached
        
        # Use distributed lock per user
        lock_key = f"ad_selection_lock:{user_id}"
        
        async with self.distributed_lock.acquire(lock_key, timeout=1):
            # Double-check cache
            cached = await self.cache.get(cache_key)
            if cached:
                return cached
            
            # Select ad
            ad = await self.select_ad_internal(user_id)
            
            # Cache result
            await self.cache.set(cache_key, ad, ttl=300)
            
            return ad
```

#### 4. Data Corruption Prevention

**Problem:** Corrupted data due to partial updates or failures.

**Solution:** Transactions, validation, and checksums.

```python
class DataIntegrity:
    async def update_campaign(self, campaign_id: int, updates: dict):
        async with self.db.transaction():
            # Validate data
            self.validate_campaign_data(updates)
            
            # Update with checksum
            old_data = await self.db.fetch_campaign(campaign_id)
            old_checksum = self.calculate_checksum(old_data)
            
            # Perform update
            await self.db.update_campaign(campaign_id, updates)
            
            # Verify update
            new_data = await self.db.fetch_campaign(campaign_id)
            new_checksum = self.calculate_checksum(new_data)
            
            if old_checksum == new_checksum and updates:
                raise DataIntegrityError("Update failed")
            
            # Log for audit
            await self.audit_log.log({
                'action': 'update_campaign',
                'campaign_id': campaign_id,
                'old_checksum': old_checksum,
                'new_checksum': new_checksum
            })
```

### Recovery Mechanisms

#### 1. Automatic Recovery

**Service Restart:**
- Kubernetes health checks
- Automatic pod restart
- Gradual traffic increase after recovery

**Database Recovery:**
- Automatic failover to replica
- Connection pool recovery
- Transaction rollback on failure

**Cache Recovery:**
- Automatic reconnection
- Cache warming after recovery
- Gradual cache population

#### 2. Manual Recovery Procedures

**Runbooks:**
- Step-by-step recovery procedures
- Rollback procedures
- Data recovery procedures

**Disaster Recovery:**
- Backup and restore procedures
- Multi-region failover
- Data replication across regions

#### 3. Monitoring and Alerting

**Critical Alerts:**
- Service downtime
- Database failures
- Cache failures
- Budget exhaustion
- High error rates

**Alert Channels:**
- PagerDuty for critical alerts
- Slack for warnings
- Email for informational alerts

---

## Scalability Considerations

### Horizontal Scaling Strategy

#### 1. Stateless Services

All ad serving services are stateless, allowing horizontal scaling:

```python
# Stateless service design
class AdServingService:
    def __init__(self):
        # No local state
        # All state in external stores (DB, Cache)
        self.db = DatabasePool()
        self.cache = RedisClient()
    
    async def serve_ad(self, request: AdRequest) -> AdResponse:
        # No dependency on local state
        # Can run on any instance
        return await self.process_request(request)
```

**Benefits:**
- Easy horizontal scaling
- Load balancer can route to any instance
- No session affinity required
- Easy deployment and rollback

#### 2. Database Scaling

**Read Scaling:**
- Multiple read replicas
- Read queries distributed across replicas
- Connection pooling per replica

**Write Scaling:**
- Database sharding by advertiser_id
- Shard key: `hash(advertiser_id) % num_shards`
- Consistent hashing for shard distribution

```python
class ShardedDatabase:
    def __init__(self):
        self.shards = [
            DatabaseConnection(config) 
            for config in shard_configs
        ]
        self.num_shards = len(self.shards)
    
    def get_shard(self, advertiser_id: int) -> DatabaseConnection:
        shard_index = hash(advertiser_id) % self.num_shards
        return self.shards[shard_index]
    
    async def write_campaign(self, campaign: dict):
        shard = self.get_shard(campaign['advertiser_id'])
        return await shard.insert('campaigns', campaign)
```

**Sharding Strategy:**
- **Shard Key**: advertiser_id (ensures advertiser data on same shard)
- **Shard Count**: Start with 4 shards, scale to 64+ as needed
- **Replication**: Each shard has 2 replicas

#### 3. Cache Scaling

**Redis Cluster:**
- Automatic sharding
- Hash slots distributed across nodes
- Replication for high availability

**Cache Sharding:**
```python
class ShardedCache:
    def __init__(self):
        self.cluster = RedisCluster(
            startup_nodes=[
                {'host': 'redis1', 'port': 6379},
                {'host': 'redis2', 'port': 6379},
                {'host': 'redis3', 'port': 6379},
            ]
        )
    
    async def get(self, key: str) -> Optional[dict]:
        # Redis cluster automatically routes to correct node
        return await self.cluster.get(key)
```

**Cache Capacity Planning:**
- **User Profiles**: 1B users × 1KB = 1TB (with 20% active = 200GB)
- **Eligible Ads Cache**: 1M campaigns × 10KB = 10GB
- **Ad Creatives Metadata**: 10M ads × 500B = 5GB
- **Total**: ~250GB per region (with replication: 750GB)

#### 4. Load Balancing

**Load Balancer Types:**
- **Layer 4 (L4)**: IP and port-based routing
- **Layer 7 (L7)**: HTTP/HTTPS routing with content awareness

**Load Balancing Algorithms:**
- **Round Robin**: Equal distribution
- **Least Connections**: Route to server with fewest connections
- **Consistent Hashing**: Route by user_id for cache affinity
- **Weighted**: Based on server capacity

**Health Checks:**
- Active health checks every 5 seconds
- Mark unhealthy after 3 consecutive failures
- Remove from pool, re-add after recovery

#### 5. Auto-Scaling

**Scaling Policies:**

```yaml
# Kubernetes HPA (Horizontal Pod Autoscaler)
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ad-serving-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ad-serving
  minReplicas: 10
  maxReplicas: 1000
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 30
      - type: Pods
        value: 10
        periodSeconds: 30
```

**Scaling Triggers:**
- CPU utilization > 70%
- Memory utilization > 80%
- Request latency > 100ms (p95)
- Request queue depth > 1000

#### 6. Performance Optimization

**Async Processing:**
- Non-blocking I/O for all operations
- Async/await pattern throughout
- Event loop optimization

**Connection Pooling:**
```python
class OptimizedDatabasePool:
    def __init__(self):
        self.pool = asyncpg.create_pool(
            host='db',
            port=5432,
            database='ads',
            min_size=10,
            max_size=100,
            max_queries=50000,
            max_inactive_connection_lifetime=300
        )
```

**Batch Operations:**
```python
# Batch ad selection for multiple users
async def batch_select_ads(user_ids: list) -> dict:
    # Parallel processing
    tasks = [select_ad(user_id) for user_id in user_ids]
    results = await asyncio.gather(*tasks)
    return dict(zip(user_ids, results))
```

**Query Optimization:**
- Indexed queries
- Query result caching
- Prepared statements
- Connection reuse

### Vertical Scaling Limits

**When to Scale Vertically:**
- Single-threaded bottlenecks
- Large in-memory data structures
- CPU-intensive operations

**Limits:**
- Maximum instance size: 64 vCPU, 512GB RAM
- Beyond this, must scale horizontally

### Capacity Planning

**Request Capacity:**
- Target: 10M requests/second
- Per instance: 10K requests/second (with caching)
- Required instances: 1,000 instances
- With 50% headroom: 1,500 instances

**Storage Capacity:**
- Campaigns DB: 1M campaigns × 10KB = 10GB
- Ads DB: 10M ads × 5KB = 50GB
- Tracking DB: 1B impressions/day × 200B = 200GB/day
- Total: ~260GB (excluding tracking historical data)

**Network Capacity:**
- 10M requests/sec × 2KB response = 20GB/sec = 160Gbps
- Per region: 40Gbps (4 regions)
- CDN handles majority of traffic

---

## Optimizations

### Performance Optimizations

#### 1. Ad Selection Optimization

**Pre-computed Eligible Ads:**

```python
class PrecomputedAdSelector:
    def __init__(self):
        self.eligible_ads_cache = {}  # user_segment -> [ads]
    
    async def precompute_eligible_ads(self, user_segments: list):
        # Pre-compute eligible ads for common user segments
        for segment in user_segments:
            eligible = await self.find_eligible_ads_for_segment(segment)
            self.eligible_ads_cache[segment] = eligible
    
    async def get_eligible_ads_fast(self, user_profile: dict):
        segment = self.get_user_segment(user_profile)
        return self.eligible_ads_cache.get(segment, [])
```

**Parallel Ad Scoring:**

```python
class ParallelAdScorer:
    async def score_ads_parallel(self, ads: list, user_profile: dict):
        # Score multiple ads in parallel
        tasks = [
            self.score_ad(ad, user_profile) for ad in ads
        ]
        
        scores = await asyncio.gather(*tasks)
        return list(zip(ads, scores))
```

#### 2. Targeting Optimization

**Bloom Filter for Campaign Matching:**

```python
class BloomFilterTargeting:
    def __init__(self):
        self.campaign_bloom = BloomFilter(capacity=1000000, error_rate=0.01)
        self.campaign_details = {}
    
    async def match_campaigns_fast(self, user_profile: dict):
        # Quick filter using bloom filter
        candidate_campaigns = []
        for campaign_id in self.campaign_bloom:
            if self.bloom_matches(campaign_id, user_profile):
                candidate_campaigns.append(campaign_id)
        
        # Detailed matching only for candidates
        matched = []
        for campaign_id in candidate_campaigns:
            campaign = self.campaign_details[campaign_id]
            if self.detailed_match(campaign, user_profile):
                matched.append(campaign)
        
        return matched
```

#### 3. Budget Validation Optimization

**Budget Pre-allocation:**

```python
class BudgetPreallocator:
    def __init__(self):
        self.preallocated_budgets = {}  # campaign_id -> allocated_amount
    
    async def preallocate_budget(self, campaign_id: int, amount: float):
        # Pre-allocate budget for faster validation
        async with self.lock_manager.acquire(f"budget:{campaign_id}"):
            campaign = await self.db.get_campaign(campaign_id)
            
            if campaign['budget_spent'] + amount <= campaign['budget_total']:
                self.preallocated_budgets[campaign_id] = \
                    self.preallocated_budgets.get(campaign_id, 0) + amount
                return True
        
        return False
```

#### 4. Query Optimization

**Elasticsearch Query Optimization:**

```python
class OptimizedElasticsearchQuery:
    def build_optimized_query(self, user_profile: dict, context: dict):
        # Use filters instead of queries where possible (faster)
        must_filters = []
        
        # Age filter (exact match - use filter)
        if 'age' in user_profile:
            must_filters.append({
                "range": {
                    "targeting.age_min": {"lte": user_profile['age']},
                    "targeting.age_max": {"gte": user_profile['age']}
                }
            })
        
        # Gender filter (exact match - use filter)
        if 'gender' in user_profile:
            must_filters.append({
                "terms": {
                    "targeting.genders": [user_profile['gender']]
                }
            })
        
        # Use query only for text matching
        must_queries = []
        if 'interests' in user_profile:
            must_queries.append({
                "terms": {
                    "targeting.interests": user_profile['interests']
                }
            })
        
        return {
            "query": {
                "bool": {
                    "filter": must_filters,  # Faster than must
                    "must": must_queries
                }
            },
            "size": 100
        }
```

---

## Caching Strategy

- **User Profiles**: Cache user data (TTL: 5 minutes)
- **Eligible Ads**: Cache eligible ads per user (TTL: 1 minute)
- **Ad Creatives**: Cache ad creatives (TTL: 1 hour)

---

## Monitoring & Analytics

- **Impressions**: Track ad impressions
- **Clicks**: Track ad clicks
- **Conversions**: Track conversions
- **Performance**: CTR, CPC, ROAS

---

## Capacity Planning

- **Ad Requests**: 10M requests/second
- **Active Campaigns**: 1M campaigns
- **Ads**: 10M ads
- **Users**: 1B users

---

## Technology Stack

- **Backend**: Go, Java
- **Database**: PostgreSQL, Cassandra
- **Cache**: Redis
- **Search**: Elasticsearch
- **CDN**: CloudFlare, AWS CloudFront

---

## Interview Discussion Points

1. **Real-time Serving**: How do you serve ads with < 100ms latency?
2. **Targeting**: How do you implement complex targeting?
3. **Bidding**: How do you run real-time auctions?
4. **Scalability**: How do you handle 10M+ requests/second?

---

**Document Version**: 2.0  
**Last Updated**: January 2024

