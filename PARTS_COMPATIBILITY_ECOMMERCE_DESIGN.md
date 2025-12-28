# Design a Parts Compatibility Feature for an eCommerce Site

## Table of Contents
1. [Overview](#overview)
2. [Requirements](#requirements)
3. [System Architecture](#system-architecture)
4. [Compatibility Engine](#compatibility-engine)
5. [Database Design](#database-design)
6. [API Design](#api-design)
7. [Search & Filtering](#search--filtering)
8. [Scalability Considerations](#scalability-considerations)
9. [Caching Strategy](#caching-strategy)
10. [Capacity Planning](#capacity-planning)
11. [Technology Stack](#technology-stack)
12. [Interview Discussion Points](#interview-discussion-points)

---

## Overview

A parts compatibility system for an eCommerce site that helps customers find compatible parts for their products. The system must handle complex compatibility rules, support multiple product categories, provide fast search, and scale to millions of products and compatibility relationships.

**Key Features:**
- Product compatibility checking
- Compatible parts search
- Compatibility rules engine
- Product attribute matching
- Compatibility recommendations
- Filter by compatibility
- Compatibility history

---

## Requirements

### Functional Requirements

1. **Compatibility Management**
   - Define compatibility rules
   - Check part compatibility
   - Find compatible parts
   - Handle multiple compatibility types

2. **Search & Discovery**
   - Search compatible parts
   - Filter by compatibility
   - Show compatibility details
   - Recommend compatible parts

3. **Product Attributes**
   - Manage product attributes
   - Attribute-based matching
   - Specification comparison

### Non-Functional Requirements

1. **Scalability**
   - Support 10M+ products
   - Handle 100M+ compatibility relationships
   - Fast compatibility checks (< 100ms)

2. **Performance**
   - Compatibility check: < 50ms
   - Search: < 200ms
   - Filter: < 100ms

3. **Accuracy**
   - Accurate compatibility matching
   - Handle edge cases
   - Support complex rules

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                             │
│  (Web App, Mobile App)                                          │
└────────────────┬────────────────────────────────────────────────┘
                 │ HTTPS
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API Gateway                                   │
└────────────┬────────────────────────────────────┬────────────────┘
             │                                    │
             ▼                                    ▼
┌────────────────────────────┐      ┌────────────────────────────┐
│   Compatibility Service    │      │   Search Service           │
│   - Check Compatibility    │      │   - Search Compatible     │
│   - Find Compatible        │      │   - Filter Results         │
└────────────┬───────────────┘      └────────────┬───────────────┘
             │                                    │
             ▼                                    ▼
┌────────────────────────────────────────────────────────────────┐
│                    Compatibility Engine                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Rule      │  │   Attribute  │  │   Matching   │         │
│  │   Evaluator │  │   Matcher    │  │   Engine     │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Data Layer                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Products  │  │ Compatibility│  │   Attributes │         │
│  │     DB      │  │     Rules    │  │     DB       │         │
│  │ (PostgreSQL)│  │  (PostgreSQL)│  │ (PostgreSQL) │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐                            │
│  │ Compatibility│  │   Search     │                            │
│  │   Index      │  │   Index      │                            │
│  │(Elasticsearch│  │(Elasticsearch│                            │
│  └──────────────┘  └──────────────┘                            │
└────────────────────────────────────────────────────────────────┘
```

---

## Compatibility Engine

### Compatibility Types

1. **Direct Compatibility**: Explicit compatibility relationships
2. **Attribute-based**: Match by product attributes
3. **Rule-based**: Complex compatibility rules
4. **Category-based**: Compatibility by product category

### Compatibility Check

```python
class CompatibilityEngine:
    def __init__(self):
        self.rule_evaluator = RuleEvaluator()
        self.attribute_matcher = AttributeMatcher()
    
    def check_compatibility(self, part_id: int, product_id: int) -> dict:
        # Check direct compatibility
        if self.is_directly_compatible(part_id, product_id):
            return {
                'compatible': True,
                'confidence': 1.0,
                'reason': 'direct_match'
            }
        
        # Check attribute-based compatibility
        attribute_match = self.check_attribute_compatibility(part_id, product_id)
        if attribute_match['compatible']:
            return attribute_match
        
        # Check rule-based compatibility
        rule_match = self.check_rule_compatibility(part_id, product_id)
        if rule_match['compatible']:
            return rule_match
        
        return {
            'compatible': False,
            'confidence': 0.0,
            'reason': 'no_match'
        }
    
    def find_compatible_parts(self, product_id: int, filters: dict = None) -> list:
        # Get product attributes
        product = self.get_product(product_id)
        
        # Find compatible parts
        compatible_parts = []
        
        # Direct compatibility
        direct_parts = self.get_directly_compatible_parts(product_id)
        compatible_parts.extend(direct_parts)
        
        # Attribute-based compatibility
        attribute_parts = self.find_by_attributes(product.attributes)
        compatible_parts.extend(attribute_parts)
        
        # Rule-based compatibility
        rule_parts = self.find_by_rules(product_id)
        compatible_parts.extend(rule_parts)
        
        # Deduplicate and rank
        unique_parts = self.deduplicate(compatible_parts)
        ranked_parts = self.rank_by_confidence(unique_parts)
        
        # Apply filters
        if filters:
            ranked_parts = self.apply_filters(ranked_parts, filters)
        
        return ranked_parts
```

### Attribute Matching

```python
class AttributeMatcher:
    def match_attributes(self, part_attrs: dict, product_attrs: dict) -> dict:
        matches = 0
        total = len(product_attrs)
        
        for key, value in product_attrs.items():
            if key in part_attrs:
                if self.compare_values(part_attrs[key], value):
                    matches += 1
        
        confidence = matches / total if total > 0 else 0.0
        
        return {
            'compatible': confidence >= 0.8,  # 80% match threshold
            'confidence': confidence,
            'matched_attributes': matches,
            'total_attributes': total
        }
    
    def compare_values(self, part_value: any, product_value: any) -> bool:
        # Handle different value types
        if isinstance(part_value, (int, float)) and isinstance(product_value, (int, float)):
            # Range matching for numeric values
            return abs(part_value - product_value) <= self.get_tolerance(part_value)
        elif isinstance(part_value, str) and isinstance(product_value, str):
            # String matching
            return part_value.lower() == product_value.lower()
        else:
            return part_value == product_value
```

---

## Database Design

### Products Table

```sql
CREATE TABLE products (
    product_id BIGSERIAL PRIMARY KEY,
    sku VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    category_id BIGINT,
    brand VARCHAR(100),
    attributes JSONB, -- {year: 2020, model: "XYZ", size: "Large"}
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_category (category_id),
    INDEX idx_brand (brand)
);
```

### Compatibility Rules Table

```sql
CREATE TABLE compatibility_rules (
    rule_id BIGSERIAL PRIMARY KEY,
    part_id BIGINT NOT NULL,
    compatible_with_product_id BIGINT, -- NULL for rule-based
    rule_type VARCHAR(50) NOT NULL, -- direct, attribute, rule
    rule_definition JSONB, -- Rule logic
    confidence DECIMAL(3, 2) DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (part_id) REFERENCES products(product_id),
    INDEX idx_part (part_id),
    INDEX idx_compatible_with (compatible_with_product_id)
);
```

### Compatibility Cache Table

```sql
CREATE TABLE compatibility_cache (
    cache_key VARCHAR(255) PRIMARY KEY,
    part_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    compatible BOOLEAN NOT NULL,
    confidence DECIMAL(3, 2),
    cached_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,
    INDEX idx_part_product (part_id, product_id)
);
```

---

## API Design

### Compatibility APIs

```
GET /api/v1/compatibility/check?part_id=123&product_id=456
GET /api/v1/compatibility/parts?product_id=456&category=brakes&limit=20
GET /api/v1/compatibility/details?part_id=123&product_id=456
```

### Search API

```
GET /api/v1/search/compatible?product_id=456&q=brake+pad&filters={...}
```

**Response:**
```json
{
  "product_id": 456,
  "compatible_parts": [
    {
      "part_id": 123,
      "name": "Brake Pad Set",
      "compatible": true,
      "confidence": 0.95,
      "matched_attributes": ["year", "model", "size"],
      "price": 49.99
    }
  ],
  "total": 25
}
```

---

## Search & Filtering

### Elasticsearch Index

```json
{
  "mappings": {
    "properties": {
      "product_id": {"type": "keyword"},
      "name": {"type": "text"},
      "category": {"type": "keyword"},
      "attributes": {
        "type": "nested",
        "properties": {
          "key": {"type": "keyword"},
          "value": {"type": "text"}
        }
      },
      "compatible_with": {"type": "keyword"}
    }
  }
}
```

### Search Implementation

```python
class CompatibilitySearch:
    def search_compatible(self, product_id: int, query: str, filters: dict):
        # Get product
        product = self.get_product(product_id)
        
        # Build search query
        search_query = {
            "bool": {
                "must": [
                    {"match": {"name": query}},
                    {"term": {"compatible_with": product_id}}
                ],
                "filter": self.build_filters(filters)
            }
        }
        
        # Execute search
        results = self.elasticsearch.search(
            index="products",
            body={"query": search_query}
        )
        
        return results
```

---

## Scalability Considerations

- **Horizontal Scaling**: Multiple compatibility service instances
- **Caching**: Cache compatibility results (Redis)
- **Indexing**: Elasticsearch for fast search
- **Database Optimization**: Indexes on compatibility relationships

---

## Caching Strategy

- **Compatibility Results**: Cache check results (TTL: 1 hour)
- **Compatible Parts Lists**: Cache part lists (TTL: 30 minutes)
- **Product Attributes**: Cache product data (TTL: 1 hour)

---

## Capacity Planning

- **Products**: 10M products
- **Compatibility Relationships**: 100M relationships
- **Compatibility Checks**: 1M checks/day
- **Search Queries**: 100K queries/day

---

## Technology Stack

- **Backend**: Java, Python
- **Database**: PostgreSQL
- **Search**: Elasticsearch
- **Cache**: Redis
- **API**: REST, GraphQL

---

## High-Level Design (HLD)

### System Overview

The parts compatibility system follows a service-oriented architecture:

1. **Client Layer**: Web and mobile applications
2. **API Gateway**: Routes requests, handles authentication
3. **Compatibility Service**: Checks compatibility, finds compatible parts
4. **Search Service**: Full-text search with compatibility filtering
5. **Compatibility Engine**: Rule evaluation, attribute matching
6. **Data Layer**: PostgreSQL for products/rules, Elasticsearch for search

### Component Architecture

**Core Services:**
- **Compatibility Service**: Compatibility checking, part discovery
- **Search Service**: Search with compatibility filters
- **Rule Engine**: Evaluates compatibility rules
- **Attribute Matcher**: Matches product attributes

---

## Low-Level Design (LLD)

### Compatibility Engine Implementation

```python
class CompatibilityEngine:
    def __init__(self, db_client, cache_client):
        self.db = db_client
        self.cache = cache_client
    
    def check_compatibility(self, part_id: int, product_id: int) -> dict:
        # Check cache first
        cache_key = f"compat:{part_id}:{product_id}"
        cached = self.cache.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # Check direct compatibility
        if self.is_directly_compatible(part_id, product_id):
            result = {'compatible': True, 'confidence': 1.0, 'reason': 'direct_match'}
            self.cache.setex(cache_key, 3600, json.dumps(result))  # 1 hour TTL
            return result
        
        # Check attribute-based compatibility
        attribute_match = self.check_attribute_compatibility(part_id, product_id)
        if attribute_match['compatible']:
            self.cache.setex(cache_key, 3600, json.dumps(attribute_match))
            return attribute_match
        
        # Check rule-based compatibility
        rule_match = self.check_rule_compatibility(part_id, product_id)
        if rule_match['compatible']:
            self.cache.setex(cache_key, 3600, json.dumps(rule_match))
            return rule_match
        
        result = {'compatible': False, 'confidence': 0.0, 'reason': 'no_match'}
        self.cache.setex(cache_key, 3600, json.dumps(result))
        return result
```

---

## Fault Tolerance

### Service Resilience

**Multiple Instances:**
- Multiple compatibility service instances
- Load balancer distributes requests
- Health checks

**Database Resilience:**
- Database replication
- Read from replicas
- Automatic failover

---

## Optimizations

### Caching Strategy

**Compatibility Cache:**
- Cache compatibility results
- TTL: 1 hour
- Invalidate on product update

**Product Cache:**
- Cache product attributes
- TTL: 1 hour
- Reduce database queries

### Database Optimization

**Indexing:**
- Index on compatibility relationships
- Index on product attributes
- Optimize compatibility queries

---

## Failure Safety

### Service Failure

**Scenario: Compatibility Service Down**
- **Impact**: Cannot check compatibility
- **Mitigation**:
  - Multiple service instances
  - Serve cached results
  - Graceful degradation
- **Recovery**:
  - Service recovers
  - Resume normal operation
  - Verify cache consistency

---

## Scalability

### Horizontal Scaling

**Service Scaling:**
- Stateless service instances
- Load balancer distributes requests
- Scale independently

**Database Scaling:**
- Read replicas for queries
- Sharding by product category
- Optimize queries

---

## Interview Discussion Points

1. **Compatibility Rules**: How do you handle complex compatibility rules?
2. **Performance**: How do you make compatibility checks fast?
3. **Accuracy**: How do you ensure accurate compatibility matching?
4. **Scalability**: How do you scale to millions of products?

---

**Document Version**: 1.0  
**Last Updated**: January 2024

