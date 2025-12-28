# Design an On-Call Escalation System

## Table of Contents
1. [Overview](#overview)
2. [Requirements](#requirements)
3. [System Architecture](#system-architecture)
4. [Database Design](#database-design)
5. [API Design](#api-design)
6. [Escalation Flow](#escalation-flow)
7. [Notification System](#notification-system)
8. [Scalability Considerations](#scalability-considerations)
9. [Monitoring & Analytics](#monitoring--analytics)
10. [Capacity Planning](#capacity-planning)
11. [Technology Stack](#technology-stack)
12. [Failure Scenarios & Handling](#failure-scenarios--handling)
13. [Interview Discussion Points](#interview-discussion-points)

---

## Overview

An on-call escalation system that manages incident escalations, routes alerts to appropriate on-call engineers, handles escalation policies, and ensures incidents are addressed within SLA timeframes. The system must handle high-volume alerts, support complex escalation rules, and provide reliable notification delivery.

**Key Features:**
- On-call schedule management
- Escalation policy configuration
- Multi-channel notifications
- Incident tracking
- Escalation history
- On-call rotation
- SLA tracking

---

## Requirements

### Functional Requirements

1. **On-Call Management**
   - Create on-call schedules
   - Manage rotations
   - Handle timezone differences
   - Override schedules

2. **Escalation Policies**
   - Define escalation rules
   - Multiple escalation levels
   - Time-based escalations
   - Condition-based escalations

3. **Incident Management**
   - Create incidents from alerts
   - Track incident status
   - Escalate incidents
   - Resolve incidents

4. **Notifications**
   - Send notifications via multiple channels
   - Escalation notifications
   - Acknowledgment tracking

### Non-Functional Requirements

1. **Scalability**
   - Handle 100K+ alerts per day
   - Support 10K+ on-call engineers
   - Process escalations in real-time

2. **Performance**
   - Alert processing: < 100ms
   - Escalation decision: < 500ms
   - Notification delivery: < 5 seconds

3. **Reliability**
   - 99.9% uptime
   - No missed escalations
   - Guaranteed notification delivery

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Alert Sources                                  │
│  (Monitoring Systems, Applications)                              │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Incident Service                               │
│  - Create incidents from alerts                                  │
│  - Validate and enrich                                          │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Escalation Engine                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Policy     │  │   On-Call    │  │   Escalation │         │
│  │   Evaluator  │  │   Resolver   │  │   Executor   │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Notification Service                           │
│  - Multi-channel notifications                                  │
│  - Delivery tracking                                            │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Data Layer                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Incidents  │  │   Schedules  │  │   Policies   │         │
│  │     DB       │  │     DB       │  │     DB       │         │
│  │ (PostgreSQL) │  │ (PostgreSQL) │  │ (PostgreSQL) │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────────────────────────────────────────────┘
```

---

## Database Design

### Incidents Table

```sql
CREATE TABLE incidents (
    incident_id BIGSERIAL PRIMARY KEY,
    alert_id VARCHAR(255) UNIQUE,
    service_name VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL, -- critical, warning, info
    status VARCHAR(20) DEFAULT 'open', -- open, acknowledged, resolved
    title VARCHAR(255) NOT NULL,
    description TEXT,
    current_level INTEGER DEFAULT 1,
    escalated_at TIMESTAMP,
    acknowledged_at TIMESTAMP,
    resolved_at TIMESTAMP,
    sla_deadline TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_status (status),
    INDEX idx_service (service_name),
    INDEX idx_severity (severity)
);
```

### Escalation Policies Table

```sql
CREATE TABLE escalation_policies (
    policy_id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    service_name VARCHAR(100),
    rules JSONB NOT NULL, -- Escalation rules
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### On-Call Schedules Table

```sql
CREATE TABLE on_call_schedules (
    schedule_id BIGSERIAL PRIMARY KEY,
    team_name VARCHAR(100) NOT NULL,
    rotation_type VARCHAR(20), -- daily, weekly, monthly
    timezone VARCHAR(50) DEFAULT 'UTC',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE on_call_assignments (
    assignment_id BIGSERIAL PRIMARY KEY,
    schedule_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    level INTEGER DEFAULT 1, -- Escalation level
    FOREIGN KEY (schedule_id) REFERENCES on_call_schedules(schedule_id),
    INDEX idx_schedule_time (schedule_id, start_time, end_time)
);
```

---

## API Design

### Incident APIs

```
POST   /api/v1/incidents
GET    /api/v1/incidents/{incident_id}
PUT    /api/v1/incidents/{incident_id}/acknowledge
PUT    /api/v1/incidents/{incident_id}/resolve
GET    /api/v1/incidents?status=open&service={service}
```

### Escalation APIs

```
POST   /api/v1/incidents/{incident_id}/escalate
GET    /api/v1/escalations?incident_id={incident_id}
```

---

## Escalation Flow

### Escalation Process

1. **Alert received** → Create incident
2. **Evaluate escalation policy** → Determine escalation rules
3. **Find on-call engineer** → Query schedule for current on-call
4. **Send notification** → Notify on-call engineer
5. **Start timer** → Track acknowledgment deadline
6. **If not acknowledged** → Escalate to next level
7. **Repeat** until acknowledged or max level reached

### Escalation Policy Example

```json
{
  "policy_id": 1,
  "service_name": "payment-service",
  "rules": [
    {
      "level": 1,
      "timeout_minutes": 5,
      "notify_channels": ["pagerduty", "sms"],
      "on_call_schedule": "payment-team-primary"
    },
    {
      "level": 2,
      "timeout_minutes": 10,
      "notify_channels": ["pagerduty", "sms", "phone"],
      "on_call_schedule": "payment-team-secondary"
    },
    {
      "level": 3,
      "timeout_minutes": 15,
      "notify_channels": ["pagerduty", "sms", "phone", "email"],
      "on_call_schedule": "engineering-managers"
    }
  ]
}
```

### Escalation Engine

```python
class EscalationEngine:
    def escalate_incident(self, incident_id: int):
        incident = self.get_incident(incident_id)
        policy = self.get_policy(incident.service_name)
        
        current_level = incident.current_level
        rule = policy.rules[current_level - 1]
        
        # Get on-call engineer
        on_call = self.get_on_call(rule.on_call_schedule, current_level)
        
        # Send notification
        self.send_notification(on_call, incident, rule.notify_channels)
        
        # Schedule escalation check
        self.schedule_escalation_check(
            incident_id,
            current_level + 1,
            rule.timeout_minutes
        )
    
    def check_escalation(self, incident_id: int, next_level: int):
        incident = self.get_incident(incident_id)
        
        # Check if acknowledged
        if incident.status == 'acknowledged':
            return
        
        # Check if max level reached
        policy = self.get_policy(incident.service_name)
        if next_level > len(policy.rules):
            # Max level reached, notify managers
            self.notify_managers(incident)
            return
        
        # Escalate to next level
        incident.current_level = next_level
        self.escalate_incident(incident_id)
```

---

## Notification System

### Multi-Channel Notifications

```python
class NotificationService:
    def send_notification(self, user: dict, incident: dict, channels: list):
        for channel in channels:
            if channel == 'pagerduty':
                self.send_pagerduty(user, incident)
            elif channel == 'sms':
                self.send_sms(user.phone, incident)
            elif channel == 'phone':
                self.call_phone(user.phone, incident)
            elif channel == 'email':
                self.send_email(user.email, incident)
```

---

## Scalability Considerations

- **Horizontal Scaling**: Multiple escalation engines
- **Queue Processing**: Process escalations asynchronously
- **Caching**: Cache on-call schedules and policies
- **Database Optimization**: Index on time-based queries

---

## Capacity Planning

- **Alerts per Day**: 100K alerts/day
- **Incidents per Day**: 10K incidents/day
- **On-Call Engineers**: 10K engineers
- **Escalations per Day**: 1K escalations/day

---

## Technology Stack

- **Backend**: Go, Java
- **Database**: PostgreSQL
- **Queue**: Kafka, RabbitMQ
- **Notifications**: PagerDuty API, Twilio, SendGrid

---

## High-Level Design (HLD)

### System Overview

The on-call escalation system follows an event-driven architecture:

1. **Alert Sources**: Monitoring systems, applications
2. **Incident Service**: Creates incidents from alerts
3. **Escalation Engine**: Evaluates policies, executes escalations
4. **Notification Service**: Sends notifications via multiple channels
5. **Data Layer**: Stores incidents, policies, schedules

### Component Architecture

**Core Components:**
- **Incident Service**: Incident creation, validation, enrichment
- **Escalation Engine**: Policy evaluation, escalation execution
- **On-Call Resolver**: Finds current on-call engineers
- **Notification Service**: Multi-channel notification delivery

---

## Low-Level Design (LLD)

### Escalation Engine Implementation

```python
class EscalationEngine:
    def __init__(self, db_client, on_call_resolver, notification_service):
        self.db = db_client
        self.on_call_resolver = on_call_resolver
        self.notification_service = notification_service
    
    def escalate_incident(self, incident_id: int):
        incident = self.get_incident(incident_id)
        policy = self.get_policy(incident.service_name)
        
        current_level = incident.current_level
        rule = policy.rules[current_level - 1]
        
        # Get on-call engineer
        on_call = self.on_call_resolver.get_on_call(
            rule.on_call_schedule, 
            current_level,
            incident.service_name
        )
        
        if not on_call:
            # No on-call found, escalate to next level
            self.escalate_to_next_level(incident_id)
            return
        
        # Send notification
        self.notification_service.send_notification(
            on_call.user_id,
            incident,
            rule.notify_channels
        )
        
        # Schedule escalation check
        self.schedule_escalation_check(
            incident_id,
            current_level + 1,
            rule.timeout_minutes
        )
    
    def check_escalation(self, incident_id: int, next_level: int):
        incident = self.get_incident(incident_id)
        
        # Check if acknowledged
        if incident.status == 'acknowledged':
            return
        
        # Check if max level reached
        policy = self.get_policy(incident.service_name)
        if next_level > len(policy.rules):
            # Max level reached, notify managers
            self.notify_managers(incident)
            return
        
        # Escalate to next level
        incident.current_level = next_level
        self.escalate_incident(incident_id)
```

### On-Call Resolver Implementation

```python
class OnCallResolver:
    def __init__(self, db_client, timezone_service):
        self.db = db_client
        self.timezone = timezone_service
    
    def get_on_call(self, schedule_name: str, level: int, service_name: str) -> dict:
        # Get current time in schedule timezone
        schedule = self.get_schedule(schedule_name)
        current_time = self.timezone.now(schedule.timezone)
        
        # Find active assignment
        assignment = self.db.execute(
            """
            SELECT user_id, start_time, end_time
            FROM on_call_assignments
            WHERE schedule_id = ? 
            AND level = ?
            AND start_time <= ?
            AND end_time > ?
            ORDER BY start_time DESC
            LIMIT 1
            """,
            [schedule.schedule_id, level, current_time, current_time]
        )
        
        if not assignment:
            return None
        
        # Get user details
        user = self.get_user(assignment[0])
        return {
            'user_id': user.user_id,
            'name': user.name,
            'email': user.email,
            'phone': user.phone
        }
```

---

## Fault Tolerance

### Escalation Engine Resilience

**Multiple Instances:**
- Multiple escalation engine instances
- Process escalations in parallel
- Idempotent escalation operations

**Failure Handling:**
- Retry failed escalations
- Queue for later processing
- Alert on persistent failures

### Notification Resilience

**Multi-Channel Delivery:**
- Send via multiple channels
- Failover if one channel fails
- Retry with exponential backoff

---

## Optimizations

### Caching Strategy

**Policy Cache:**
- Cache escalation policies
- TTL: 1 hour
- Invalidate on policy update

**On-Call Cache:**
- Cache current on-call assignments
- TTL: 5 minutes
- Invalidate on schedule change

### Database Optimization

**Indexing:**
- Index on `schedule_id, start_time, end_time`
- Index on `incident_id, status`
- Optimize on-call queries

---

## Failure Safety

### Escalation Engine Failure

**Scenario: Escalation Engine Down**
- **Impact**: Escalations not processed
- **Mitigation**:
  - Multiple engine instances
  - Queue escalations for processing
  - Health checks
- **Recovery**:
  - Engine recovers
  - Process queued escalations
  - Resume normal operation

### On-Call Resolution Failure

**Scenario: Cannot Find On-Call Engineer**
- **Impact**: Escalation blocked
- **Mitigation**:
  - Escalate to next level
  - Notify managers
  - Fallback to backup schedule
- **Recovery**:
  - Schedule updated
  - Retry escalation
  - Verify on-call assignment

---

## Scalability

### Horizontal Scaling

**Engine Scaling:**
- Multiple escalation engine instances
- Process escalations in parallel
- Scale independently

**Service Scaling:**
- Stateless service instances
- Load balancer distributes requests
- Scale based on load

### Performance Scaling

**Throughput Scaling:**
- Increase processing instances
- Optimize database queries
- Use caching

**Latency Optimization:**
- Reduce database query time
- Cache on-call assignments
- Optimize notification delivery

---

## Interview Discussion Points

1. **Escalation Logic**: How do you implement escalation policies?
2. **On-Call Resolution**: How do you find the right on-call engineer?
3. **Reliability**: How do you ensure no missed escalations?
4. **Timezones**: How do you handle timezone differences?

---

**Document Version**: 1.0  
**Last Updated**: January 2024

