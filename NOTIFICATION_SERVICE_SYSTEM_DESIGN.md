# Design a Notification Service at Scale

## Table of Contents
1. [Overview](#overview)
2. [Requirements](#requirements)
3. [System Architecture](#system-architecture)
4. [Database Design](#database-design)
5. [API Design](#api-design)
6. [Notification Delivery Flow](#notification-delivery-flow)
7. [Multi-Channel Support](#multi-channel-support)
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

A scalable notification service that can send millions of notifications per day across multiple channels (email, SMS, push, in-app). The system must handle high throughput, support multiple notification types, provide delivery guarantees, and scale horizontally.

**Key Features:**
- Multi-channel notifications (email, SMS, push, in-app)
- Template management
- Notification scheduling
- Delivery tracking
- Retry logic
- Rate limiting
- User preferences
- Notification history

---

## Requirements

### Functional Requirements

1. **Notification Sending**
   - Send email notifications
   - Send SMS notifications
   - Send push notifications
   - Send in-app notifications
   - Batch notifications

2. **Template Management**
   - Create/edit templates
   - Variable substitution
   - Multi-language support

3. **Delivery Management**
   - Delivery tracking
   - Delivery status (sent, delivered, failed)
   - Retry failed notifications
   - Bounce handling

4. **User Preferences**
   - Channel preferences
   - Notification frequency
   - Do-not-disturb settings

### Non-Functional Requirements

1. **Scalability**
   - Handle 100M+ notifications per day
   - Support 1M+ notifications per minute (peak)
   - Horizontal scaling

2. **Performance**
   - Notification queuing: < 50ms
   - Delivery latency: < 5 seconds (p95)
   - 99.9% uptime

3. **Reliability**
   - At-least-once delivery
   - No notification loss
   - Fault tolerance

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                             │
│  (API Clients, Web UI, Internal Services)                      │
└────────────────┬────────────────────────────────────────────────┘
                 │ HTTPS
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API Gateway / Load Balancer                   │
└────────────┬────────────────────────────────────┬────────────────┘
             │                                    │
             ▼                                    ▼
┌────────────────────────────┐      ┌────────────────────────────┐
│   Notification Service     │      │   Template Service        │
│   - Create Notifications   │      │   - Template Management   │
│   - Queue Notifications    │      │   - Variable Substitution │
└────────────┬───────────────┘      └────────────┬───────────────┘
             │                                    │
             ▼                                    ▼
┌────────────────────────────────────────────────────────────────┐
│                    Message Queue                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Email      │  │   SMS        │  │   Push       │         │
│  │   Queue      │  │   Queue      │  │   Queue      │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Delivery Workers                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Email      │  │   SMS        │  │   Push        │         │
│  │   Workers    │  │   Workers    │  │   Workers     │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    External Services                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Email      │  │   SMS        │  │   Push       │         │
│  │   Provider   │  │   Provider   │  │   Provider   │         │
│  │ (SendGrid)   │  │ (Twilio)     │  │ (FCM/APNS)   │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Data Layer                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Notification │  │   Template   │  │   Delivery    │         │
│  │     DB       │  │     DB       │  │     Log       │         │
│  │ (PostgreSQL) │  │ (PostgreSQL) │  │ (Cassandra)  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────────────────────────────────────────────┘
```

---

## Database Design

### Notifications Table

```sql
CREATE TABLE notifications (
    notification_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    channel VARCHAR(20) NOT NULL, -- email, sms, push, in_app
    template_id BIGINT,
    subject VARCHAR(255),
    body TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending', -- pending, queued, sent, delivered, failed
    priority INTEGER DEFAULT 0,
    scheduled_at TIMESTAMP,
    sent_at TIMESTAMP,
    delivered_at TIMESTAMP,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_user_status (user_id, status),
    INDEX idx_scheduled (scheduled_at),
    INDEX idx_status (status)
);
```

### Templates Table

```sql
CREATE TABLE templates (
    template_id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    channel VARCHAR(20) NOT NULL,
    subject_template TEXT,
    body_template TEXT NOT NULL,
    variables JSONB, -- Required variables
    language VARCHAR(10) DEFAULT 'en',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### User Preferences Table

```sql
CREATE TABLE user_preferences (
    preference_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    channel VARCHAR(20) NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    frequency_limit INTEGER, -- Max notifications per hour
    quiet_hours_start TIME,
    quiet_hours_end TIME,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE KEY unique_user_channel (user_id, channel)
);
```

---

## API Design

### Notification APIs

```
POST   /api/v1/notifications
GET    /api/v1/notifications/{notification_id}
GET    /api/v1/notifications?user_id={user_id}&status={status}
POST   /api/v1/notifications/batch
```

### Send Notification Request

```json
POST /api/v1/notifications
{
  "user_id": 123,
  "channel": "email",
  "template_id": 456,
  "variables": {
    "name": "John",
    "amount": "$100"
  },
  "priority": 5,
  "scheduled_at": "2024-01-15T10:00:00Z"
}
```

---

## Notification Delivery Flow

### Delivery Flow

1. **Client sends notification request**
2. **Service validates request**
3. **Service checks user preferences**
4. **Service applies template and variables**
5. **Service queues notification**
6. **Worker picks up notification**
7. **Worker sends via external provider**
8. **Worker updates delivery status**
9. **On failure, retry or move to DLQ**

---

## Multi-Channel Support

### Email Channel

- **Provider**: SendGrid, AWS SES
- **Features**: HTML/Text emails, attachments
- **Rate Limits**: Per provider limits

### SMS Channel

- **Provider**: Twilio, AWS SNS
- **Features**: Text messages, Unicode support
- **Rate Limits**: Per provider limits

### Push Channel

- **Provider**: FCM (Android), APNS (iOS)
- **Features**: Push notifications, badges, sounds
- **Rate Limits**: Per device limits

---

## Scalability Considerations

- **Horizontal Scaling**: Multiple worker instances
- **Queue Partitioning**: Partition by channel or priority
- **Batch Processing**: Batch notifications for efficiency
- **Rate Limiting**: Respect provider and user limits

---

## Caching Strategy

- **Template Cache**: Cache templates (Redis)
- **User Preferences Cache**: Cache user preferences
- **Rate Limit Cache**: Track rate limits per user

---

## Load Balancing

- **Worker Selection**: Round-robin or least-loaded
- **Priority Queues**: Separate queues by priority
- **Channel-specific**: Separate workers per channel

---

## Security

- **Authentication**: API keys, OAuth
- **Rate Limiting**: Per user, per channel
- **Content Validation**: Sanitize notification content

---

## Monitoring & Analytics

- **Delivery Rate**: Percentage of successful deliveries
- **Delivery Latency**: Time to deliver notifications
- **Failure Rate**: Percentage of failed notifications
- **Channel Performance**: Per-channel metrics

---

## Capacity Planning

- **Notifications per Day**: 100M/day
- **Peak Rate**: 1M/minute
- **Workers**: 500 workers (100 per channel)
- **Notifications per Worker**: 2K/minute

---

## Technology Stack

- **Backend**: Go, Java
- **Queue**: Kafka, RabbitMQ
- **Database**: PostgreSQL, Cassandra
- **Providers**: SendGrid, Twilio, FCM, APNS

---

## Failure Scenarios & Handling

1. **Provider Failure**: Retry with exponential backoff, failover to backup provider
2. **Worker Failure**: Requeue notifications, assign to another worker
3. **Queue Failure**: Queue replication, persistence

---

## High-Level Design (HLD)

### System Overview

The notification service follows an event-driven architecture:

1. **Client Layer**: API clients, web UI, internal services
2. **API Gateway**: Routes requests, handles authentication
3. **Notification Service**: Creates notifications, applies templates
4. **Message Queue**: Buffers notifications by channel (Kafka)
5. **Delivery Workers**: Process notifications per channel
6. **External Providers**: Email, SMS, push notification providers

### Component Architecture

**Core Services:**
- **Notification Service**: Notification creation, template application
- **Template Service**: Template management, variable substitution
- **Delivery Service**: Multi-channel delivery coordination
- **Tracking Service**: Delivery status tracking, analytics

---

## Low-Level Design (LLD)

### Notification Service Implementation

```python
class NotificationService:
    def __init__(self, db_client, template_service, queue_client, redis_client):
        self.db = db_client
        self.template_service = template_service
        self.queue = queue_client
        self.redis = redis_client
    
    def send_notification(self, user_id: int, channel: str, template_id: int, 
                         variables: dict, priority: int = 0) -> dict:
        # Check user preferences
        preferences = self.get_user_preferences(user_id, channel)
        if not preferences.get('enabled', True):
            return {'success': False, 'reason': 'channel_disabled'}
        
        # Check rate limits
        if not self.check_rate_limit(user_id, channel):
            return {'success': False, 'reason': 'rate_limit_exceeded'}
        
        # Apply template
        template = self.template_service.get_template(template_id)
        rendered = self.template_service.render(template, variables)
        
        # Create notification record
        notification = {
            'user_id': user_id,
            'channel': channel,
            'template_id': template_id,
            'subject': rendered['subject'],
            'body': rendered['body'],
            'status': 'pending',
            'priority': priority,
            'created_at': datetime.utcnow()
        }
        
        notification_id = self.db.execute(
            """
            INSERT INTO notifications (user_id, channel, template_id, subject, body, status, priority)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            RETURNING notification_id
            """,
            [user_id, channel, template_id, rendered['subject'], rendered['body'], 
             'pending', priority]
        )
        notification['notification_id'] = notification_id
        
        # Queue for delivery
        self.queue.send(f'{channel}-notifications', {
            'notification_id': notification_id,
            'user_id': user_id,
            'channel': channel,
            'subject': rendered['subject'],
            'body': rendered['body']
        }, priority=priority)
        
        return {'success': True, 'notification_id': notification_id}
```

### Delivery Worker Implementation

```python
class DeliveryWorker:
    def __init__(self, channel: str, provider_client, db_client):
        self.channel = channel
        self.provider = provider_client
        self.db = db_client
    
    def process_notification(self, notification: dict):
        try:
            # Send via provider
            result = self.provider.send(
                to=notification['recipient'],
                subject=notification.get('subject'),
                body=notification['body']
            )
            
            # Update status
            self.update_status(notification['notification_id'], 'sent', result)
            
            # Track delivery (async)
            self.track_delivery(notification['notification_id'], result)
            
        except Exception as e:
            # Handle failure
            self.handle_failure(notification, str(e))
    
    def handle_failure(self, notification: dict, error: str):
        retry_count = notification.get('retry_count', 0)
        max_retries = notification.get('max_retries', 3)
        
        if retry_count < max_retries:
            # Retry with exponential backoff
            delay = 2 ** retry_count
            self.schedule_retry(notification, delay)
        else:
            # Max retries reached, move to dead letter queue
            self.move_to_dlq(notification, error)
```

---

## Fault Tolerance

### Provider Resilience

**Multiple Providers:**
- Primary and backup providers per channel
- Automatic failover on provider failure
- Load balancing across providers

**Retry Logic:**
- Exponential backoff for retries
- Max retry attempts: 3
- Dead letter queue for failed notifications

### Queue Resilience

**Message Durability:**
- Persistent queues (Kafka with replication)
- Acknowledgment required
- Dead letter queues

---

## Optimizations

### Batching

**Batch Notifications:**
- Batch multiple notifications
- Reduce provider API calls
- Improve throughput

**Template Caching:**
- Cache rendered templates
- Cache template definitions
- Reduce processing time

### Rate Limiting

**Per-User Rate Limiting:**
- Track notifications per user
- Enforce limits per channel
- Prevent spam

---

## Failure Safety

### Provider Failure

**Scenario: Email Provider Down**
- **Impact**: Email notifications not delivered
- **Mitigation**:
  - Failover to backup provider
  - Queue notifications for later
  - Retry with exponential backoff
- **Recovery**:
  - Provider recovers
  - Process queued notifications
  - Resume normal operation

### Worker Failure

**Scenario: Delivery Worker Crashes**
- **Impact**: Notifications not processed
- **Mitigation**:
  - Multiple worker instances
  - Kafka consumer groups
  - Automatic rebalancing
- **Recovery**:
  - Worker recovers
  - Resume processing from last offset
  - Process queued notifications

---

## Scalability

### Horizontal Scaling

**Worker Scaling:**
- Add more worker instances
- Scale per channel independently
- Auto-scaling based on queue depth

**Service Scaling:**
- Stateless service instances
- Load balancer distributes requests
- Scale independently

### Performance Scaling

**Throughput Scaling:**
- Increase Kafka partitions
- Add more worker instances
- Optimize batch sizes

**Latency Optimization:**
- Reduce queue latency
- Optimize provider API calls
- Use connection pooling

---

## Interview Discussion Points

1. **Multi-Channel**: How do you handle different channels?
2. **Rate Limiting**: How do you implement rate limiting?
3. **Scalability**: How do you scale to millions of notifications?
4. **Delivery Guarantees**: How do you ensure delivery?

---

**Document Version**: 1.0  
**Last Updated**: January 2024

