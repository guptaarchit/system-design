# Google Calendar System Design

## Table of Contents
1. [Overview](#overview)
2. [Requirements](#requirements)
3. [System Architecture](#system-architecture)
4. [Database Design](#database-design)
5. [API Design](#api-design)
6. [Event Management Flow](#event-management-flow)
7. [Scheduling & Conflict Detection](#scheduling--conflict-detection)
8. [Notifications & Reminders](#notifications--reminders)
9. [Calendar Sharing & Permissions](#calendar-sharing--permissions)
10. [Real-time Updates](#real-time-updates)
11. [Scalability Considerations](#scalability-considerations)
12. [Caching Strategy](#caching-strategy)
13. [Load Balancing](#load-balancing)
14. [Security](#security)
15. [Monitoring & Analytics](#monitoring--analytics)
16. [Deployment Strategy](#deployment-strategy)
17. [Capacity Planning](#capacity-planning)
18. [Technology Stack](#technology-stack)
19. [Failure Scenarios & Handling](#failure-scenarios--handling)
20. [Trade-offs & Design Decisions](#trade-offs--design-decisions)
21. [Interview Discussion Points](#interview-discussion-points)

---

## Overview

Google Calendar is a time-management and scheduling service that allows users to create, manage, and share events. The system must handle millions of users, support real-time collaboration, detect scheduling conflicts, send notifications, and provide seamless synchronization across devices.

**Key Features:**
- Create, edit, and delete events
- Multiple calendars per user
- Calendar sharing and permissions
- Recurring events
- Event reminders and notifications
- Scheduling conflicts detection
- Time zone support
- Calendar search
- Integration with other services (Gmail, Meet)
- Mobile and web clients
- Real-time updates and synchronization

---

## Requirements

### Functional Requirements

1. **Event Management**
   - Create, read, update, delete events
   - Support for recurring events (daily, weekly, monthly, yearly)
   - Event attendees management
   - Event location and description
   - Event reminders (email, push, SMS)
   - All-day events
   - Time zone support

2. **Calendar Management**
   - Multiple calendars per user
   - Calendar creation and deletion
   - Calendar color coding
   - Calendar visibility settings

3. **Sharing & Permissions**
   - Share calendar with other users
   - Permission levels (view, edit, manage)
   - Public calendar links
   - Group calendars

4. **Scheduling**
   - Detect scheduling conflicts
   - Find available time slots
   - Suggest meeting times
   - Room/resource booking

5. **Notifications**
   - Email notifications
   - Push notifications (mobile)
   - SMS notifications
   - In-app notifications

6. **Search & Discovery**
   - Search events by title, description
   - Filter by date range
   - Filter by calendar
   - Full-text search

### Non-Functional Requirements

1. **Scalability**
   - Support 1B+ users globally
   - Handle 100M+ events per day
   - Support 10M+ concurrent users
   - 99.9% uptime

2. **Performance**
   - Event creation: < 200ms (p95)
   - Calendar view load: < 500ms (p95)
   - Search: < 300ms (p95)
   - Real-time updates: < 100ms latency

3. **Reliability**
   - No data loss
   - Eventual consistency acceptable for non-critical updates
   - Strong consistency for event conflicts

4. **Availability**
   - Multi-region deployment
   - Graceful degradation
   - Offline support (mobile)

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                             │
│  (Web App, Mobile Apps, Desktop Clients)                        │
└────────────────┬────────────────────────────────────────────────┘
                 │ HTTPS/TLS
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CDN & Load Balancer                           │
│              (CloudFlare, AWS ALB)                              │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API Gateway                                   │
│              (Kong, AWS API Gateway)                            │
│              - Authentication                                   │
│              - Rate Limiting                                    │
│              - Request Routing                                  │
└────────────┬────────────────────────────────────┬────────────────┘
             │                                    │
             ▼                                    ▼
┌────────────────────────────┐      ┌────────────────────────────┐
│   Calendar Service        │      │   Event Service            │
│   - Calendar CRUD         │      │   - Event CRUD             │
│   - Sharing Management    │      │   - Conflict Detection     │
└────────────┬──────────────┘      └────────────┬───────────────┘
             │                                    │
             ▼                                    ▼
┌────────────────────────────┐      ┌────────────────────────────┐
│   Scheduling Service       │      │   Notification Service     │
│   - Find Available Time    │      │   - Email Notifications    │
│   - Conflict Detection    │      │   - Push Notifications     │
└────────────┬──────────────┘      └────────────┬───────────────┘
             │                                    │
             ▼                                    ▼
┌────────────────────────────────────────────────────────────────┐
│                      Core Services Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Search     │  │   Recurrence │  │   Sync       │         │
│  │   Service    │  │   Service    │  │   Service    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────┬────────────────────┬────────────────────┬──────────────────┘
     │                    │                    │
     ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  Message Queue  │  │   Cache Layer   │  │   Event Bus     │
│  (Kafka/RabbitMQ│  │    (Redis)      │  │   (Kafka)       │
└─────────────────┘  └─────────────────┘  └─────────────────┘
     │                    │                    │
     ▼                    ▼                    ▼
┌────────────────────────────────────────────────────────────────┐
│                      Data Layer                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Calendar   │  │    Event     │  │   User       │         │
│  │     DB       │  │     DB       │  │     DB       │         │
│  │ (PostgreSQL) │  │ (PostgreSQL) │  │ (PostgreSQL) │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Search     │  │   Time-Series│  │   Analytics  │         │
│  │     DB       │  │     DB       │  │     DB       │         │
│  │(Elasticsearch│  │ (TimescaleDB)│  │ (ClickHouse) │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────────────────────────────────────────────┘
     │                    │                    │
     ▼                    ▼                    ▼
┌────────────────────────────────────────────────────────────────┐
│                    External Services                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Email      │  │   Push       │  │   Gmail      │         │
│  │   Service    │  │   Service    │  │   Integration│         │
│  │  (SendGrid)  │  │  (FCM/APNS)  │  │              │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────────────────────────────────────────────┘
```

### Component Details

#### 1. Calendar Service
- **Purpose**: Manage calendars
- **Responsibilities**:
  - Calendar CRUD operations
  - Calendar sharing and permissions
  - Calendar visibility settings

#### 2. Event Service
- **Purpose**: Manage events
- **Responsibilities**:
  - Event CRUD operations
  - Recurring event expansion
  - Event conflict detection
  - Attendee management

#### 3. Scheduling Service
- **Purpose**: Handle scheduling logic
- **Responsibilities**:
  - Find available time slots
  - Detect conflicts
  - Suggest meeting times
  - Room/resource availability

#### 4. Notification Service
- **Purpose**: Send notifications
- **Responsibilities**:
  - Email notifications
  - Push notifications
  - SMS notifications
  - Reminder scheduling

#### 5. Search Service
- **Purpose**: Event search
- **Responsibilities**:
  - Full-text search
  - Date range filtering
  - Calendar filtering

#### 6. Sync Service
- **Purpose**: Handle synchronization
- **Responsibilities**:
  - Real-time updates
  - Conflict resolution
  - Multi-device sync

### HLD Component Breakdown

**1. Client Layer**
- **Web App**: React-based web application
- **Mobile Apps**: iOS/Android native apps
- **Desktop Clients**: Desktop calendar clients

**2. API Gateway Layer**
- **API Gateway**: Routes requests to services
- **Load Balancer**: Distributes traffic
- **Authentication**: OAuth 2.0 authentication

**3. Service Layer**
- **Calendar Service**: Manages calendars
- **Event Service**: Manages events
- **Scheduling Service**: Handles scheduling logic
- **Notification Service**: Sends notifications
- **Search Service**: Handles event search
- **Sync Service**: Handles synchronization

**4. Processing Layer**
- **Recurrence Service**: Expands recurring events
- **Conflict Detector**: Detects scheduling conflicts
- **Notification Scheduler**: Schedules notifications

**5. Data Layer**
- **PostgreSQL**: Calendars, events, users
- **Elasticsearch**: Event search index
- **Redis**: Cache, sessions, real-time data
- **TimescaleDB**: Time-series data for analytics

---

## Low-Level Design (LLD)

### Event Service LLD

```python
class EventService:
    def __init__(self, db: Database, scheduling_service: SchedulingService,
                 recurrence_service: RecurrenceService, notification_service: NotificationService,
                 websocket_manager: WebSocketManager):
        self.db = db
        self.scheduling_service = scheduling_service
        self.recurrence_service = recurrence_service
        self.notification_service = notification_service
        self.websocket_manager = websocket_manager
    
    def create_event(self, calendar_id: int, event_data: dict) -> Event:
        # Check conflicts
        conflicts = self.scheduling_service.detect_conflicts(
            user_id=event_data['created_by'],
            start_time=event_data['start_time'],
            end_time=event_data['end_time']
        )
        
        if conflicts and event_data.get('prevent_conflicts', True):
            raise ConflictError(conflicts)
        
        # Create event
        event = Event.create(
            calendar_id=calendar_id,
            title=event_data['title'],
            start_time=event_data['start_time'],
            end_time=event_data['end_time'],
            recurrence_rule=event_data.get('recurrence_rule'),
            created_by=event_data['created_by']
        )
        
        # Expand recurring events if needed
        if event.recurrence_rule:
            instances = self.recurrence_service.expand_recurrence(event)
            for instance in instances:
                self._create_event_instance(event, instance)
        
        # Create attendees
        for attendee_data in event_data.get('attendees', []):
            self._create_attendee(event.id, attendee_data)
        
        # Schedule reminders
        for reminder_data in event_data.get('reminders', []):
            self.notification_service.schedule_reminder(event.id, reminder_data)
        
        # Send real-time updates
        self._broadcast_event_update(event, 'created')
        
        return event
    
    def _broadcast_event_update(self, event: Event, action: str):
        # Get all users who should be notified
        attendees = self.get_event_attendees(event.id)
        calendar_owners = self.get_calendar_owners(event.calendar_id)
        
        # Send updates via WebSocket
        for user_id in set(attendees + calendar_owners):
            self.websocket_manager.send_to_user(user_id, {
                'type': 'event_update',
                'action': action,
                'event_id': event.id,
                'event': event.to_dict()
            })
```

### Scheduling Service LLD

```python
class SchedulingService:
    def __init__(self, db: Database, cache: RedisCache):
        self.db = db
        self.cache = cache
    
    def detect_conflicts(self, user_id: int, start_time: datetime, 
                        end_time: datetime, exclude_event_id: int = None) -> list:
        # Get all calendars user has access to
        calendars = self.get_user_calendars(user_id)
        
        # Query overlapping events
        conflicts = []
        for calendar in calendars:
            overlapping_events = self.db.query("""
                SELECT * FROM events
                WHERE calendar_id = %s
                AND start_time < %s
                AND end_time > %s
                AND status != 'cancelled'
                AND id != %s
            """, (calendar.id, end_time, start_time, exclude_event_id or 0))
            
            conflicts.extend(overlapping_events)
        
        return conflicts
    
    def find_available_time(self, attendees: list, duration_minutes: int,
                           start_date: datetime, end_date: datetime) -> list:
        # Get all events for all attendees
        all_events = []
        for attendee in attendees:
            events = self.get_user_events(attendee.user_id, start_date, end_date)
            all_events.extend(events)
        
        # Sort events by start time
        all_events.sort(key=lambda x: x.start_time)
        
        # Find gaps
        available_slots = []
        current_time = start_date
        
        for event in all_events:
            if current_time + timedelta(minutes=duration_minutes) <= event.start_time:
                available_slots.append({
                    'start': current_time,
                    'end': event.start_time
                })
            current_time = max(current_time, event.end_time)
        
        # Check gap after last event
        if current_time + timedelta(minutes=duration_minutes) <= end_date:
            available_slots.append({
                'start': current_time,
                'end': end_date
            })
        
        return available_slots
```

### Notification Service LLD

```python
class NotificationService:
    def __init__(self, email_service: EmailService, push_service: PushService,
                 sms_service: SMSService, scheduler: Scheduler):
        self.email_service = email_service
        self.push_service = push_service
        self.sms_service = sms_service
        self.scheduler = scheduler
    
    def schedule_reminder(self, event_id: int, reminder_data: dict):
        event = Event.get(event_id)
        
        # Calculate reminder time
        reminder_time = event.start_time - timedelta(
            minutes=reminder_data['minutes_before']
        )
        
        # Create reminder record
        reminder = Reminder.create(
            event_id=event_id,
            reminder_type=reminder_data['type'],
            scheduled_time=reminder_time
        )
        
        # Schedule notification job
        self.scheduler.schedule(
            reminder_id=reminder.id,
            execute_at=reminder_time,
            callback=self._send_reminder
        )
    
    def _send_reminder(self, reminder_id: int):
        reminder = Reminder.get(reminder_id)
        event = Event.get(reminder.event_id)
        
        if reminder.reminder_type == 'email':
            self.email_service.send_reminder(event, reminder)
        elif reminder.reminder_type == 'push':
            self.push_service.send_reminder(event, reminder)
        elif reminder.reminder_type == 'sms':
            self.sms_service.send_reminder(event, reminder)
        
        reminder.is_sent = True
        reminder.sent_at = datetime.utcnow()
        reminder.save()
```

---

## Fault Tolerance

### Event Processing Fault Tolerance

**1. Conflict Detection Resilience**
- **Caching**: Cache calendar data for faster conflict detection
- **Optimistic Locking**: Handle concurrent updates
- **Conflict Resolution**: Resolve conflicts automatically or flag for review

**2. Notification Resilience**
- **Retry Logic**: Retry failed notifications
- **Dead Letter Queue**: Store failed notifications
- **Multiple Channels**: Fallback to alternative channels
- **Notification Queue**: Queue notifications for processing

### Database Fault Tolerance

**1. Database Replication**
- **PostgreSQL**: Primary-replica setup
- **Read Replicas**: Scale reads independently
- **Automatic Failover**: Promote replica on primary failure
- **Data Consistency**: Ensure consistency across replicas

**2. Search Index Resilience**
- **Elasticsearch Cluster**: Multiple nodes with replication
- **Index Aliases**: Zero-downtime index updates
- **Index Recovery**: Rebuild indices on failure

---

## Failure Safety

### Failure Scenarios & Handling

**1. Event Service Failure**

**Scenario**: Event service fails during event creation.

**Impact**: Events may be partially created, inconsistent state.

**Mitigation**:
- **Distributed Transactions**: Use saga pattern
- **Idempotency**: Make operations idempotent
- **Compensation**: Rollback on failure
- **Event Sourcing**: Use events for audit and recovery

**Recovery**:
- **Saga Compensation**: Execute compensation transactions
- **State Reconciliation**: Reconcile event state
- **Manual Intervention**: Flag for manual review

**2. Conflict Detection Failure**

**Scenario**: Conflict detection service fails.

**Impact**: Cannot detect conflicts, may create overlapping events.

**Mitigation**:
- **Cached Calendar Data**: Use cached data for conflict detection
- **Optimistic Locking**: Handle concurrent updates
- **Post-Creation Check**: Check conflicts after creation
- **Manual Review**: Flag events for manual review

**Recovery**:
- **Conflict Resolution**: Resolve conflicts automatically
- **User Notification**: Notify users of conflicts
- **Event Adjustment**: Adjust events to resolve conflicts

**3. Notification Failure**

**Scenario**: Notification service fails.

**Impact**: Reminders not sent.

**Mitigation**:
- **Retry Queue**: Queue notifications for retry
- **Dead Letter Queue**: Store failed notifications
- **Multiple Channels**: Fallback to alternative channels
- **Notification Redundancy**: Deploy multiple notification services

**Recovery**:
- **Retry Notifications**: Retry failed notifications
- **Manual Send**: Allow manual sending of notifications
- **Notification Log**: Log all notification attempts

**4. Sync Failure**

**Scenario**: Sync service fails.

**Impact**: Devices out of sync, conflicts.

**Mitigation**:
- **Event Sourcing**: Use events for sync
- **Version Numbers**: Use version numbers for conflict resolution
- **Last Write Wins**: Resolve conflicts with last write wins
- **Manual Sync**: Allow manual sync trigger

**Recovery**:
- **Sync Reconciliation**: Reconcile sync state
- **Conflict Resolution**: Resolve sync conflicts
- **State Sync**: Sync state across devices

---

## Scalability Considerations

### 1. Horizontal Scaling

**Service Scaling:**
- **Stateless Services**: All services are stateless
- **Scale Horizontally**: Add instances as needed
- **Load Balancer**: Distribute traffic
- **Auto-Scaling**: Scale based on CPU/memory/request rate

**Scaling Metrics:**
- **Event Service**: 1000 req/s per instance
- **Search Service**: 500 queries/s per instance
- **Notification Service**: 1000 notifications/s per instance

### 2. Database Scaling

**PostgreSQL Scaling:**
- **Read Replicas**: 3-5 read replicas for reads
- **Sharding**: Shard by user_id
- **Partitioning**: Partition events table by date
- **Connection Pooling**: PgBouncer for connection pooling

**Elasticsearch Scaling:**
- **Cluster Mode**: Deploy Elasticsearch cluster
- **Sharding**: Shard indices by user_id
- **Replication**: Replicate indices
- **Index Optimization**: Optimize indices for performance

### 3. Caching Strategy

**Multi-Level Caching:**
- **Redis**: Calendar views, event data (TTL: 1-5 minutes)
- **Application Cache**: Hot data (TTL: 15 minutes)
- **CDN**: Static assets

**Cache Invalidation:**
- **Event-Based**: Invalidate on event updates
- **TTL-Based**: Set expiration for time-sensitive data
- **Version-Based**: Use version numbers for validation

### 4. Real-time Updates Scaling

**WebSocket Scaling:**
- **Multiple Servers**: Deploy multiple WebSocket servers
- **Sticky Sessions**: Route same client to same server
- **Redis Pub/Sub**: Cross-server communication
- **Connection Pooling**: Efficient connection management

**Performance Targets:**
- **Connections**: 10K-50K per server
- **Message Throughput**: 100K messages/second per server
- **Latency**: < 100ms (p95)

---

## Database Design

### 1. Users Table

```sql
CREATE TABLE users (
    user_id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    timezone VARCHAR(50) DEFAULT 'UTC',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_email (email)
);
```

### 2. Calendars Table

```sql
CREATE TABLE calendars (
    calendar_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    name VARCHAR(255) NOT NULL,
    color VARCHAR(7), -- Hex color code
    description TEXT,
    timezone VARCHAR(50),
    is_primary BOOLEAN DEFAULT FALSE,
    visibility VARCHAR(20) DEFAULT 'private', -- private, public, shared
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    INDEX idx_user_id (user_id),
    INDEX idx_visibility (visibility)
);
```

### 3. Events Table

```sql
CREATE TABLE events (
    event_id BIGSERIAL PRIMARY KEY,
    calendar_id BIGINT NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    location VARCHAR(500),
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ NOT NULL,
    timezone VARCHAR(50),
    is_all_day BOOLEAN DEFAULT FALSE,
    recurrence_rule VARCHAR(500), -- RRULE format
    recurrence_id BIGINT, -- For recurring event instances
    status VARCHAR(20) DEFAULT 'confirmed', -- confirmed, tentative, cancelled
    created_by BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (calendar_id) REFERENCES calendars(calendar_id),
    FOREIGN KEY (created_by) REFERENCES users(user_id),
    INDEX idx_calendar_time (calendar_id, start_time, end_time),
    INDEX idx_start_time (start_time),
    INDEX idx_recurrence_id (recurrence_id),
    INDEX idx_created_by (created_by)
);
```

### 4. Event Attendees Table

```sql
CREATE TABLE event_attendees (
    attendee_id BIGSERIAL PRIMARY KEY,
    event_id BIGINT NOT NULL,
    user_id BIGINT, -- NULL for external attendees
    email VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    response_status VARCHAR(20) DEFAULT 'needsAction', -- needsAction, accepted, declined, tentative
    is_organizer BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (event_id) REFERENCES events(event_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    UNIQUE KEY unique_event_attendee (event_id, email),
    INDEX idx_event_id (event_id),
    INDEX idx_user_id (user_id),
    INDEX idx_email (email)
);
```

### 5. Calendar Shares Table

```sql
CREATE TABLE calendar_shares (
    share_id BIGSERIAL PRIMARY KEY,
    calendar_id BIGINT NOT NULL,
    shared_with_user_id BIGINT, -- NULL for public links
    shared_with_email VARCHAR(255), -- For non-users
    permission VARCHAR(20) NOT NULL, -- view, edit, manage
    share_token VARCHAR(255) UNIQUE, -- For public links
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (calendar_id) REFERENCES calendars(calendar_id),
    FOREIGN KEY (shared_with_user_id) REFERENCES users(user_id),
    INDEX idx_calendar_id (calendar_id),
    INDEX idx_shared_with_user (shared_with_user_id),
    INDEX idx_share_token (share_token)
);
```

### 6. Reminders Table

```sql
CREATE TABLE reminders (
    reminder_id BIGSERIAL PRIMARY KEY,
    event_id BIGINT NOT NULL,
    reminder_type VARCHAR(20) NOT NULL, -- email, push, popup, sms
    minutes_before INTEGER NOT NULL, -- Minutes before event
    is_sent BOOLEAN DEFAULT FALSE,
    sent_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (event_id) REFERENCES events(event_id),
    INDEX idx_event_id (event_id),
    INDEX idx_send_time (minutes_before, is_sent)
);
```

### 7. Event Conflicts Table

```sql
CREATE TABLE event_conflicts (
    conflict_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    event_id_1 BIGINT NOT NULL,
    event_id_2 BIGINT NOT NULL,
    conflict_type VARCHAR(20), -- overlap, double_booking
    detected_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (event_id_1) REFERENCES events(event_id),
    FOREIGN KEY (event_id_2) REFERENCES events(event_id),
    INDEX idx_user_id (user_id),
    INDEX idx_event_1 (event_id_1),
    INDEX idx_event_2 (event_id_2)
);
```

---

## API Design

### Calendar APIs

```
GET    /api/v1/calendars
POST   /api/v1/calendars
GET    /api/v1/calendars/{calendar_id}
PUT    /api/v1/calendars/{calendar_id}
DELETE /api/v1/calendars/{calendar_id}
POST   /api/v1/calendars/{calendar_id}/share
DELETE /api/v1/calendars/{calendar_id}/share/{share_id}
```

### Event APIs

```
GET    /api/v1/calendars/{calendar_id}/events
POST   /api/v1/calendars/{calendar_id}/events
GET    /api/v1/events/{event_id}
PUT    /api/v1/events/{event_id}
DELETE /api/v1/events/{event_id}
POST   /api/v1/events/{event_id}/attendees
GET    /api/v1/events/{event_id}/conflicts
```

### Scheduling APIs

```
GET    /api/v1/scheduling/available?start_time={start}&end_time={end}&attendees={user_ids}
POST   /api/v1/scheduling/suggest
GET    /api/v1/scheduling/conflicts?user_id={user_id}&start_time={start}&end_time={end}
```

### Search APIs

```
GET    /api/v1/search/events?q={query}&start_time={start}&end_time={end}
GET    /api/v1/search/calendars?q={query}
```

### Example: Create Event

**Request:**
```json
POST /api/v1/calendars/{calendar_id}/events
{
  "title": "Team Meeting",
  "description": "Weekly team sync",
  "location": "Conference Room A",
  "start_time": "2024-01-15T10:00:00Z",
  "end_time": "2024-01-15T11:00:00Z",
  "timezone": "America/New_York",
  "attendees": [
    {
      "email": "user1@example.com"
    },
    {
      "email": "user2@example.com"
    }
  ],
  "reminders": [
    {
      "type": "email",
      "minutes_before": 15
    },
    {
      "type": "push",
      "minutes_before": 5
    }
  ],
  "recurrence": {
    "frequency": "weekly",
    "interval": 1,
    "count": 10
  }
}
```

**Response:**
```json
{
  "event_id": "evt_123",
  "title": "Team Meeting",
  "start_time": "2024-01-15T10:00:00Z",
  "end_time": "2024-01-15T11:00:00Z",
  "status": "confirmed",
  "conflicts": [],
  "created_at": "2024-01-10T12:00:00Z"
}
```

---

## Event Management Flow

### Create Event Flow

```
┌──────────┐         ┌──────────────┐         ┌──────────────┐
│  Client  │────────▶│ Event Service│────────▶│  Scheduling  │
│          │         │              │         │   Service    │
└──────────┘         └──────┬───────┘         └──────┬───────┘
                            │                        │
                            ▼                        ▼
                    ┌──────────────┐         ┌──────────────┐
                    │  Conflict    │         │  Available   │
                    │  Detection   │         │  Time Check  │
                    └──────┬───────┘         └──────┬───────┘
                           │                        │
                           ▼                        ▼
                    ┌──────────────┐         ┌──────────────┐
                    │  Event DB    │         │  Notification│
                    │  (Create)    │         │   Service    │
                    └──────┬───────┘         └──────┬───────┘
                           │                        │
                           ▼                        ▼
                    ┌──────────────┐         ┌──────────────┐
                    │  Recurrence  │         │  Send        │
                    │  Expansion   │         │  Invites     │
                    └──────┬───────┘         └──────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  Real-time   │
                    │  Updates     │
                    └──────────────┘
```

### Step-by-Step Process

1. **Event Creation Request**
   - Client sends event creation request
   - Event Service validates input

2. **Conflict Detection**
   - Scheduling Service checks for conflicts
   - Queries events for all attendees in time range
   - Detects overlapping events

3. **Event Creation**
   - Create event record in database
   - Create attendee records
   - Create reminder records

4. **Recurrence Expansion**
   - If recurring event, expand instances
   - Create individual event instances
   - Link via recurrence_id

5. **Notifications**
   - Send invites to attendees
   - Schedule reminders
   - Send real-time updates

---

## Scheduling & Conflict Detection

### Conflict Detection Algorithm

```python
def detect_conflicts(user_id, start_time, end_time, exclude_event_id=None):
    # Get all calendars user has access to
    calendars = get_user_calendars(user_id)
    
    # Query overlapping events
    conflicts = []
    for calendar in calendars:
        overlapping_events = query_events(
            calendar_id=calendar.id,
            start_time__lt=end_time,
            end_time__gt=start_time,
            exclude_event_id=exclude_event_id
        )
        
        for event in overlapping_events:
            if event.status != 'cancelled':
                conflicts.append(event)
    
    return conflicts
```

### Available Time Detection

```python
def find_available_time(attendees, duration_minutes, start_date, end_date):
    # Get all events for all attendees
    all_events = []
    for attendee in attendees:
        events = get_user_events(attendee.user_id, start_date, end_date)
        all_events.extend(events)
    
    # Sort events by start time
    all_events.sort(key=lambda x: x.start_time)
    
    # Find gaps
    available_slots = []
    current_time = start_date
    
    for event in all_events:
        if current_time + duration_minutes <= event.start_time:
            available_slots.append({
                'start': current_time,
                'end': event.start_time
            })
        current_time = max(current_time, event.end_time)
    
    # Check gap after last event
    if current_time + duration_minutes <= end_date:
        available_slots.append({
            'start': current_time,
            'end': end_date
        })
    
    return available_slots
```

---

## Notifications & Reminders

### Reminder Scheduling

```python
def schedule_reminders(event_id, reminders):
    for reminder in reminders:
        reminder_time = event.start_time - timedelta(
            minutes=reminder['minutes_before']
        )
        
        create_reminder(
            event_id=event_id,
            reminder_type=reminder['type'],
            scheduled_time=reminder_time
        )
        
        # Schedule job in job queue
        schedule_notification_job(
            reminder_id=reminder.id,
            execute_at=reminder_time
        )
```

### Notification Types

1. **Email Notifications**
   - Event invites
   - Event updates
   - Reminders
   - Daily agenda

2. **Push Notifications**
   - Real-time event updates
   - Reminders
   - Conflict alerts

3. **SMS Notifications**
   - Critical reminders
   - Event updates (optional)

---

## Calendar Sharing & Permissions

### Permission Levels

1. **View**: Can view events
2. **Edit**: Can create/edit/delete events
3. **Manage**: Can manage calendar settings and sharing

### Sharing Flow

```
┌──────────┐         ┌──────────────┐         ┌──────────────┐
│  Owner   │────────▶│   Calendar   │────────▶│  Permission  │
│          │         │   Service    │         │   Check      │
└──────────┘         └──────┬───────┘         └──────┬───────┘
                            │                        │
                            ▼                        ▼
                    ┌──────────────┐         ┌──────────────┐
                    │  Create Share│         │  Send        │
                    │  Record      │         │  Invitation │
                    └──────┬───────┘         └──────┬───────┘
                           │                        │
                           ▼                        ▼
                    ┌──────────────┐         ┌──────────────┐
                    │  Generate    │         │  Real-time   │
                    │  Share Link  │         │  Update      │
                    └──────────────┘         └──────────────┘
```

---

## Real-time Updates

### WebSocket Connection

```python
# Client connects via WebSocket
ws_connection = WebSocketConnection(user_id)

# On event update
def on_event_update(event_id, changes):
    # Get all users who should be notified
    attendees = get_event_attendees(event_id)
    calendar_owners = get_calendar_owners(event.calendar_id)
    
    # Send updates to connected clients
    for user_id in set(attendees + calendar_owners):
        if user_id in connected_clients:
            send_update(user_id, {
                'type': 'event_update',
                'event_id': event_id,
                'changes': changes
            })
```

### Conflict Resolution

- **Last Write Wins**: For non-critical fields
- **Merge Strategy**: For attendee lists
- **Conflict Flag**: For critical conflicts (time changes)

---

## Scalability Considerations

### Horizontal Scaling

1. **Service Scaling**: Multiple instances of each service
2. **Database Sharding**: Shard by user_id
3. **Read Replicas**: Multiple read replicas for queries
4. **Caching**: Aggressive caching for calendar views

### Partitioning Strategy

- **Events Table**: Partition by calendar_id or time range
- **Users Table**: Shard by user_id
- **Search Index**: Shard by user_id

---

## Caching Strategy

### Cache Layers

1. **Calendar View Cache**
   - Cache calendar views (TTL: 1-5 minutes)
   - Invalidate on event updates

2. **User Calendars Cache**
   - Cache user's calendars (TTL: 15 minutes)
   - Invalidate on calendar changes

3. **Event Details Cache**
   - Cache event details (TTL: 5 minutes)
   - Invalidate on event updates

---

## Load Balancing

- **Round Robin**: For stateless services
- **Sticky Sessions**: For WebSocket connections
- **Geographic**: Route based on user location

---

## Security

### Authentication & Authorization

- **OAuth 2.0**: User authentication
- **JWT Tokens**: API authentication
- **Permission Checks**: Per-calendar permissions

### Data Security

- **Encryption**: TLS for data in transit
- **Access Control**: Row-level security
- **Audit Logging**: All changes logged

---

## Capacity Planning

### Traffic Estimates

- **Users**: 1B users
- **Daily Active Users**: 200M (20%)
- **Events per User**: 10 events/day average
- **Daily Events**: 2B events/day
- **Peak Events**: 3x average = 6B events/day

### Storage Estimates

- **Events per Day**: 2B events
- **Size per Event**: 2KB
- **Daily Storage**: 2B × 2KB = 4TB/day
- **Monthly Storage**: 4TB × 30 = 120TB/month

---

## Technology Stack

### Backend

- **Language**: Java, Go, Python
- **Frameworks**: Spring Boot, Gin
- **Database**: PostgreSQL, Elasticsearch
- **Cache**: Redis
- **Message Queue**: Kafka

### Infrastructure

- **Cloud**: GCP, AWS
- **Container**: Kubernetes
- **CDN**: CloudFlare

---

## Failure Scenarios & Handling

1. **Event Service Failure**
   - **Mitigation**: Multiple instances, load balancer
   - **Recovery**: Auto-restart, failover

2. **Database Failure**
   - **Mitigation**: Replication, backups
   - **Recovery**: Failover to replica

3. **Notification Failure**
   - **Mitigation**: Retry queue, dead letter queue
   - **Recovery**: Retry with exponential backoff

---

## Trade-offs & Design Decisions

### 1. Strong vs Eventual Consistency

**Decision**: Eventual consistency for non-critical updates, strong for conflicts

**Rationale**: Better performance, conflicts handled separately

### 2. Push vs Pull for Updates

**Decision**: Hybrid (push via WebSocket, pull on reconnect)

**Rationale**: Real-time updates with offline support

---

## Interview Discussion Points

### Key Topics

1. **Conflict Detection**
   - How do you detect conflicts efficiently?
   - How do you handle recurring events?

2. **Real-time Updates**
   - How do you sync across devices?
   - How do you handle offline scenarios?

3. **Scalability**
   - How do you scale to 1B users?
   - How do you partition data?

---

**Document Version**: 1.0  
**Last Updated**: January 2024

