# Design a Job Scheduler

## Table of Contents
1. [Overview](#overview)
2. [Requirements](#requirements)
3. [System Architecture](#system-architecture)
4. [Database Design](#database-design)
5. [API Design](#api-design)
6. [Scheduling Algorithms](#scheduling-algorithms)
7. [Job Execution Flow](#job-execution-flow)
8. [Scalability Considerations](#scalability-considerations)
9. [Load Balancing](#load-balancing)
10. [Security](#security)
11. [Monitoring & Analytics](#monitoring--analytics)
12. [Capacity Planning](#capacity-planning)
13. [Technology Stack](#technology-stack)
14. [Failure Scenarios & Handling](#failure-scenarios--handling)
15. [Trade-offs & Design Decisions](#trade-offs--design-decisions)
16. [Interview Discussion Points](#interview-discussion-points)

---

## Overview

A distributed job scheduler system that can schedule, execute, and monitor millions of jobs. The system must support various job types (one-time, recurring, cron-based), handle job dependencies, provide fault tolerance, and scale horizontally.

**Key Features:**
- Schedule one-time jobs
- Schedule recurring jobs (cron expressions)
- Job dependencies
- Job prioritization
- Job retries and error handling
- Job monitoring and logging
- Resource management
- Multi-tenant support

---

## Requirements

### Functional Requirements

1. **Job Scheduling**
   - Schedule one-time jobs
   - Schedule recurring jobs (cron)
   - Job dependencies
   - Job prioritization

2. **Job Execution**
   - Execute jobs on workers
   - Handle job failures
   - Retry logic
   - Timeout handling

3. **Job Management**
   - Pause/resume jobs
   - Cancel jobs
   - Job history
   - Job status tracking

### Non-Functional Requirements

1. **Scalability**
   - Handle 10M+ jobs
   - Support 100K+ jobs per minute
   - Horizontal scaling

2. **Performance**
   - Schedule job: < 100ms
   - Job execution: As per job requirements
   - 99.9% uptime

3. **Reliability**
   - No job loss
   - At-least-once execution
   - Fault tolerance

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                             │
│  (API Clients, Web UI, CLI Tools)                              │
└────────────────┬────────────────────────────────────────────────┘
                 │ HTTPS
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API Gateway / Load Balancer                    │
└────────────┬────────────────────────────────────┬────────────────┘
             │                                    │
             ▼                                    ▼
┌────────────────────────────┐      ┌────────────────────────────┐
│   Scheduler Service        │      │   Job Manager Service       │
│   - Schedule Jobs          │      │   - Job CRUD               │
│   - Cron Evaluation         │      │   - Job Status             │
└────────────┬──────────────┘      └────────────┬───────────────┘
             │                                    │
             ▼                                    ▼
┌────────────────────────────────────────────────────────────────┐
│                    Job Queue                                     │
│              (Kafka, RabbitMQ, Redis)                          │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Worker Nodes                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Worker 1   │  │   Worker 2   │  │   Worker N   │         │
│  │  - Execute   │  │  - Execute   │  │  - Execute   │         │
│  │  - Monitor   │  │  - Monitor   │  │  - Monitor   │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Data Layer                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Jobs DB    │  │   Execution  │  │   Logs DB    │         │
│  │ (PostgreSQL) │  │     DB       │  │ (Elasticsearch│        │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────────────────────────────────────────────┘
```

---

## Database Design

### Jobs Table

```sql
CREATE TABLE jobs (
    job_id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    job_type VARCHAR(50) NOT NULL, -- one_time, recurring, cron
    schedule VARCHAR(255), -- cron expression or timestamp
    status VARCHAR(20) DEFAULT 'pending', -- pending, scheduled, running, completed, failed
    priority INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    timeout_seconds INTEGER,
    payload JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    next_run_at TIMESTAMP,
    INDEX idx_status (status),
    INDEX idx_next_run (next_run_at),
    INDEX idx_priority (priority DESC)
);
```

### Job Dependencies Table

```sql
CREATE TABLE job_dependencies (
    dependency_id BIGSERIAL PRIMARY KEY,
    job_id BIGINT NOT NULL,
    depends_on_job_id BIGINT NOT NULL,
    FOREIGN KEY (job_id) REFERENCES jobs(job_id),
    FOREIGN KEY (depends_on_job_id) REFERENCES jobs(job_id),
    UNIQUE KEY unique_dependency (job_id, depends_on_job_id)
);
```

### Job Executions Table

```sql
CREATE TABLE job_executions (
    execution_id BIGSERIAL PRIMARY KEY,
    job_id BIGINT NOT NULL,
    worker_id VARCHAR(255),
    status VARCHAR(20) NOT NULL, -- running, completed, failed
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    FOREIGN KEY (job_id) REFERENCES jobs(job_id),
    INDEX idx_job_status (job_id, status),
    INDEX idx_started_at (started_at)
);
```

---

## API Design

### Job APIs

```
POST   /api/v1/jobs
GET    /api/v1/jobs/{job_id}
PUT    /api/v1/jobs/{job_id}
DELETE /api/v1/jobs/{job_id}
POST   /api/v1/jobs/{job_id}/pause
POST   /api/v1/jobs/{job_id}/resume
GET    /api/v1/jobs/{job_id}/executions
```

### Schedule Job Request

```json
POST /api/v1/jobs
{
  "name": "daily-report",
  "job_type": "cron",
  "schedule": "0 0 * * *", // Daily at midnight
  "priority": 5,
  "max_retries": 3,
  "timeout_seconds": 3600,
  "payload": {
    "report_type": "daily",
    "recipients": ["admin@example.com"]
  }
}
```

---

## Scheduling Algorithms

### Cron Evaluation

```python
def evaluate_cron(cron_expr, current_time):
    # Parse cron expression: "minute hour day month weekday"
    parts = cron_expr.split()
    minute, hour, day, month, weekday = parts
    
    # Calculate next run time
    next_run = calculate_next_run(current_time, minute, hour, day, month, weekday)
    return next_run
```

### Priority Scheduling

```python
def schedule_jobs(jobs):
    # Sort by priority (higher first), then by next_run_at
    sorted_jobs = sorted(
        jobs,
        key=lambda j: (j.priority, j.next_run_at),
        reverse=True
    )
    
    # Schedule top priority jobs first
    for job in sorted_jobs:
        if job.next_run_at <= now():
            schedule_job(job)
```

### Dependency Resolution

```python
def resolve_dependencies(job_id):
    # Get all dependencies
    dependencies = get_job_dependencies(job_id)
    
    # Check if all dependencies are completed
    for dep_job_id in dependencies:
        dep_status = get_job_status(dep_job_id)
        if dep_status != 'completed':
            return False
    
    return True
```

---

## Job Execution Flow

### Execution Flow

1. **Scheduler evaluates cron jobs**
2. **Jobs ready to run are enqueued**
3. **Worker picks up job from queue**
4. **Worker executes job**
5. **Worker updates execution status**
6. **On failure, retry or mark as failed**
7. **On success, trigger dependent jobs**

---

## Scalability Considerations

- **Horizontal Scaling**: Multiple scheduler and worker instances
- **Job Queue Partitioning**: Partition by priority or job type
- **Database Sharding**: Shard by job_id or tenant_id

---

## Load Balancing

- **Worker Selection**: Round-robin or least-loaded
- **Priority Queues**: Separate queues by priority
- **Resource-based**: Assign jobs based on worker capacity

---

## Security

- **Authentication**: API keys, OAuth
- **Authorization**: Job-level permissions
- **Isolation**: Multi-tenant isolation

---

## Monitoring & Analytics

- **Job Success Rate**: Percentage of successful jobs
- **Job Latency**: Average execution time
- **Queue Depth**: Jobs waiting in queue
- **Worker Utilization**: CPU/memory usage

---

## Capacity Planning

- **Jobs per Day**: 100M jobs/day
- **Peak Rate**: 100K jobs/minute
- **Workers**: 1000 workers
- **Jobs per Worker**: 100 jobs/minute

---

## Technology Stack

- **Backend**: Go, Java
- **Queue**: Kafka, RabbitMQ, Redis
- **Database**: PostgreSQL
- **Scheduler**: Quartz, Celery

---

## Failure Scenarios & Handling

1. **Worker Failure**: Requeue job, assign to another worker
2. **Scheduler Failure**: Multiple scheduler instances, leader election
3. **Queue Failure**: Queue replication, persistence

---

## High-Level Design (HLD)

### System Overview

The job scheduler follows a distributed architecture with clear separation of concerns:

1. **Client Layer**: API clients, web UI, CLI tools
2. **API Gateway**: Routes requests, handles authentication
3. **Scheduler Service**: Evaluates cron expressions, schedules jobs
4. **Job Manager Service**: Manages job CRUD operations, status tracking
5. **Message Queue**: Buffers jobs for execution (Kafka/RabbitMQ)
6. **Worker Layer**: Executes jobs, reports status
7. **Data Layer**: Stores job definitions, execution history, metadata

### Service Decomposition

**Core Services:**
- **Scheduler Service**: Cron evaluation, job scheduling, dependency resolution
- **Job Manager Service**: Job CRUD, status management, history
- **Worker Service**: Job execution, status reporting, retry logic
- **Dependency Service**: Manages job dependencies, triggers dependent jobs

**Supporting Services:**
- **Notification Service**: Sends job completion/failure notifications
- **Analytics Service**: Tracks job metrics, generates reports
- **Health Service**: Monitors worker health, detects failures

---

## Low-Level Design (LLD)

### Cron Evaluator Implementation

```python
class CronEvaluator:
    def __init__(self):
        self.cron_cache = {}  # Cache parsed cron expressions
    
    def get_next_run_time(self, cron_expr: str, current_time: datetime) -> datetime:
        # Parse cron expression
        if cron_expr not in self.cron_cache:
            self.cron_cache[cron_expr] = self._parse_cron(cron_expr)
        
        parts = self.cron_cache[cron_expr]
        minute, hour, day, month, weekday = parts
        
        # Calculate next run time
        next_time = current_time.replace(second=0, microsecond=0)
        next_time += timedelta(minutes=1)  # Start from next minute
        
        # Find next matching time
        max_iterations = 365 * 24 * 60  # Prevent infinite loops
        iterations = 0
        
        while iterations < max_iterations:
            # Check minute
            if not self._matches(minute, next_time.minute):
                next_time += timedelta(minutes=1)
                iterations += 1
                continue
            
            # Check hour
            if not self._matches(hour, next_time.hour):
                next_time += timedelta(hours=1)
                next_time = next_time.replace(minute=0)
                iterations += 1
                continue
            
            # Check day of month
            if not self._matches(day, next_time.day):
                next_time += timedelta(days=1)
                next_time = next_time.replace(hour=0, minute=0)
                iterations += 1
                continue
            
            # Check month
            if not self._matches(month, next_time.month):
                next_time += timedelta(days=32)
                next_time = next_time.replace(day=1, hour=0, minute=0)
                iterations += 1
                continue
            
            # Check weekday
            if not self._matches(weekday, next_time.weekday()):
                next_time += timedelta(days=1)
                next_time = next_time.replace(hour=0, minute=0)
                iterations += 1
                continue
            
            # All conditions matched
            return next_time
        
        raise ValueError(f"Could not find next run time for cron: {cron_expr}")
    
    def _parse_cron(self, cron_expr: str) -> tuple:
        parts = cron_expr.split()
        if len(parts) != 5:
            raise ValueError("Invalid cron expression")
        
        return tuple(self._parse_field(p) for p in parts)
    
    def _parse_field(self, field: str) -> set:
        # Parse field like "*/5", "1-5", "1,3,5", "*"
        if field == '*':
            return set(range(60))  # For minutes, adjust range as needed
        
        result = set()
        for part in field.split(','):
            if '/' in part:
                # Step value: */5
                base, step = part.split('/')
                if base == '*':
                    base_range = range(60)
                else:
                    base_range = self._parse_range(base)
                result.update(range(min(base_range), max(base_range) + 1, int(step)))
            elif '-' in part:
                # Range: 1-5
                start, end = part.split('-')
                result.update(range(int(start), int(end) + 1))
            else:
                # Single value
                result.add(int(part))
        
        return result
    
    def _matches(self, field_set: set, value: int) -> bool:
        return value in field_set
```

### Job Dependency Resolver

```python
class DependencyResolver:
    def __init__(self, db_client):
        self.db = db_client
        self.dependency_cache = {}  # job_id -> [dependencies]
    
    def resolve_dependencies(self, job_id: int) -> bool:
        """Check if all dependencies are completed"""
        dependencies = self.get_dependencies(job_id)
        
        if not dependencies:
            return True  # No dependencies
        
        for dep_job_id in dependencies:
            status = self.get_job_status(dep_job_id)
            if status != 'completed':
                return False
        
        return True
    
    def get_dependencies(self, job_id: int) -> list:
        if job_id not in self.dependency_cache:
            deps = self.db.execute(
                "SELECT depends_on_job_id FROM job_dependencies WHERE job_id = ?",
                [job_id]
            )
            self.dependency_cache[job_id] = [d[0] for d in deps]
        
        return self.dependency_cache[job_id]
    
    def get_dependents(self, job_id: int) -> list:
        """Get jobs that depend on this job"""
        dependents = self.db.execute(
            "SELECT job_id FROM job_dependencies WHERE depends_on_job_id = ?",
            [job_id]
        )
        return [d[0] for d in dependents]
    
    def trigger_dependents(self, completed_job_id: int):
        """Trigger jobs that depend on completed job"""
        dependents = self.get_dependents(completed_job_id)
        
        for dependent_id in dependents:
            if self.resolve_dependencies(dependent_id):
                # All dependencies satisfied, trigger job
                self.schedule_job(dependent_id)
```

### Job Execution Manager

```python
class JobExecutionManager:
    def __init__(self, queue_client, db_client):
        self.queue = queue_client
        self.db = db_client
        self.workers = {}  # worker_id -> Worker
    
    def execute_job(self, job_id: int, worker_id: str):
        # Get job details
        job = self.get_job(job_id)
        
        # Check if job can run (dependencies, status)
        if not self.can_execute(job):
            return False
        
        # Update job status
        execution_id = self.create_execution(job_id, worker_id)
        
        try:
            # Send to worker
            self.queue.send('job-execution', {
                'execution_id': execution_id,
                'job_id': job_id,
                'payload': job.payload,
                'timeout': job.timeout_seconds
            })
            
            # Update status to running
            self.update_execution_status(execution_id, 'running')
            
            return True
        
        except Exception as e:
            self.update_execution_status(execution_id, 'failed', str(e))
            self.handle_failure(job_id, execution_id, str(e))
            return False
    
    def handle_job_completion(self, execution_id: int, status: str, result: dict):
        execution = self.get_execution(execution_id)
        
        # Update execution
        self.update_execution(execution_id, {
            'status': status,
            'completed_at': datetime.utcnow(),
            'result': result
        })
        
        # Update job status
        if status == 'completed':
            self.update_job_status(execution.job_id, 'completed')
            
            # Trigger dependent jobs
            self.dependency_resolver.trigger_dependents(execution.job_id)
        else:
            # Handle retry
            self.handle_retry(execution.job_id, execution_id)
    
    def handle_retry(self, job_id: int, execution_id: int):
        job = self.get_job(job_id)
        execution = self.get_execution(execution_id)
        
        if execution.retry_count < job.max_retries:
            # Schedule retry with exponential backoff
            delay = 2 ** execution.retry_count  # Exponential backoff
            self.schedule_retry(job_id, delay)
        else:
            # Max retries reached, mark as failed
            self.update_job_status(job_id, 'failed')
            self.send_notification(job_id, 'failed')
```

---

## Fault Tolerance

### Scheduler Redundancy

**Leader Election:**
- Use distributed lock (Redis/ZooKeeper) for leader election
- Only leader evaluates cron and schedules jobs
- Automatic failover on leader failure
- Health checks every 10 seconds

**Implementation:**
```python
class SchedulerLeader:
    def __init__(self, lock_client):
        self.lock = lock_client
        self.leader_lock_key = "scheduler:leader"
        self.is_leader = False
    
    def acquire_leadership(self):
        acquired = self.lock.acquire(
            self.leader_lock_key,
            timeout=60,  # 60 second lease
            renew_interval=30  # Renew every 30 seconds
        )
        
        if acquired:
            self.is_leader = True
            self.start_scheduling()
        else:
            self.is_leader = False
    
    def start_scheduling(self):
        while self.is_leader:
            # Evaluate cron jobs
            self.evaluate_cron_jobs()
            
            # Renew leadership
            if not self.lock.renew(self.leader_lock_key):
                self.is_leader = False
                break
            
            time.sleep(10)  # Check every 10 seconds
```

### Worker Failure Handling

**Heartbeat Mechanism:**
- Workers send heartbeat every 30 seconds
- Mark workers as dead if no heartbeat for 90 seconds
- Reassign jobs from dead workers

**Job Reassignment:**
```python
class WorkerManager:
    def check_worker_health(self):
        current_time = time.time()
        dead_workers = []
        
        for worker_id, last_heartbeat in self.worker_heartbeats.items():
            if current_time - last_heartbeat > 90:  # 90 seconds timeout
                dead_workers.append(worker_id)
        
        # Reassign jobs from dead workers
        for worker_id in dead_workers:
            self.reassign_worker_jobs(worker_id)
            self.remove_worker(worker_id)
    
    def reassign_worker_jobs(self, worker_id: str):
        # Get running jobs for this worker
        running_jobs = self.get_running_jobs(worker_id)
        
        for job_execution in running_jobs:
            # Mark as failed
            self.update_execution_status(
                job_execution.execution_id,
                'failed',
                'worker_failed'
            )
            
            # Requeue job
            self.requeue_job(job_execution.job_id)
```

### Queue Resilience

**Message Durability:**
- Persistent queues (Kafka with replication)
- Acknowledgment required before removing from queue
- Dead letter queue for failed jobs

**Backpressure Handling:**
- Monitor queue depth
- Scale workers based on queue depth
- Throttle job scheduling if queue too deep

---

## Optimizations

### Cron Evaluation Optimization

**Pre-computation:**
- Pre-compute next run times for all cron jobs
- Store in sorted data structure (priority queue)
- Only evaluate jobs whose next_run_at is <= now

**Caching:**
- Cache parsed cron expressions
- Cache next run time calculations
- Invalidate cache on cron expression update

### Job Scheduling Optimization

**Batch Scheduling:**
- Batch multiple jobs into single queue message
- Reduce queue operations
- Improve throughput

**Priority Queues:**
- Separate queues by priority
- Process high-priority jobs first
- Use multiple worker pools per priority

### Database Query Optimization

**Indexing:**
- Index on `next_run_at` for efficient cron evaluation
- Index on `status` for status queries
- Index on `job_id, status` for execution queries

**Query Optimization:**
- Use prepared statements
- Batch queries where possible
- Use read replicas for read-heavy operations

### Worker Pool Optimization

**Connection Pooling:**
- Reuse database connections
- Reuse queue connections
- Reduce connection overhead

**Resource Management:**
- Limit concurrent jobs per worker
- Monitor worker resource usage
- Auto-scale workers based on load

---

## Failure Safety

### Scheduler Failure

**Scenario: Scheduler Service Crashes**
- **Impact**: No new jobs scheduled, existing jobs continue
- **Mitigation**:
  - Multiple scheduler instances with leader election
  - Jobs already queued continue executing
  - New leader takes over scheduling
- **Recovery**:
  - New leader evaluates all cron jobs
  - Catches up on missed schedules
  - Reschedules missed jobs (if configured)

### Worker Failure

**Scenario: Worker Crashes During Job Execution**
- **Impact**: Job execution interrupted, may be incomplete
- **Mitigation**:
  - Heartbeat mechanism detects worker failure
  - Job marked as failed
  - Job requeued for retry
- **Recovery**:
  - Reassign job to another worker
  - Retry with exponential backoff
  - Mark as permanently failed after max retries

### Database Failure

**Scenario: Database Unavailable**
- **Impact**: Cannot read job definitions, update status
- **Mitigation**:
  - Database replication with automatic failover
  - Read from replicas
  - Queue status updates for later processing
- **Recovery**:
  - Failover to replica
  - Replay queued updates
  - Verify data consistency

### Queue Failure

**Scenario: Message Queue Unavailable**
- **Impact**: Cannot queue jobs for execution
- **Mitigation**:
  - Queue replication (Kafka with multiple brokers)
  - Local buffering in scheduler
  - Fallback to database queue
- **Recovery**:
  - Queue recovers, process buffered jobs
  - Replay from database queue
  - Verify no job loss

### Job Execution Failures

**Scenario: Job Throws Exception**
- **Impact**: Job fails, dependent jobs blocked
- **Mitigation**:
  - Catch exceptions in job execution
  - Log error details
  - Retry with exponential backoff
- **Recovery**:
  - Retry job (if retries remaining)
  - Mark as failed after max retries
  - Trigger dependent jobs if configured to continue on failure

---

## Scalability

### Horizontal Scaling

**Scheduler Scaling:**
- Multiple scheduler instances (only leader active)
- Leader election for coordination
- Independent scaling from workers

**Worker Scaling:**
- Add workers dynamically
- Auto-scaling based on queue depth
- Distribute load across workers

**Database Scaling:**
- Read replicas for read-heavy operations
- Sharding by tenant_id or job_id
- Partition job_executions table by time

### Vertical Scaling

**Database Optimization:**
- Increase instance size
- Optimize queries and indexes
- Partition large tables

**Worker Optimization:**
- Increase worker capacity
- Optimize job execution code
- Use faster hardware

### Performance Scaling

**Throughput Scaling:**
- Increase Kafka partitions for parallel processing
- Add more worker instances
- Optimize batch sizes

**Latency Optimization:**
- Reduce database query time
- Reduce queue latency
- Optimize job execution time

### Capacity Planning

**Traffic Growth:**
- Monitor job creation rate
- Plan capacity for 2x current load
- Auto-scaling for predictable growth

**Storage Growth:**
- Monitor database size
- Implement data retention policies
- Archive old execution history

---

## Interview Discussion Points

1. **Cron Evaluation**: How do you efficiently evaluate cron expressions?
2. **Dependencies**: How do you handle job dependencies?
3. **Scalability**: How do you scale to millions of jobs?
4. **Fault Tolerance**: How do you ensure no job loss?

---

**Document Version**: 1.0  
**Last Updated**: January 2024

