# Cluster Health Monitoring System Design

## Table of Contents
1. [Overview](#overview)
2. [Requirements](#requirements)
3. [System Architecture](#system-architecture)
4. [Core Components](#core-components)
5. [Database Design](#database-design)
6. [API Design](#api-design)
7. [Metrics Collection](#metrics-collection)
8. [Alerting System](#alerting-system)
9. [Dashboards & Visualization](#dashboards--visualization)
10. [Anomaly Detection](#anomaly-detection)
11. [Scalability Considerations](#scalability-considerations)
12. [Optimizations](#optimizations)
13. [Monitoring & Analytics](#monitoring--analytics)
14. [Deployment Strategy](#deployment-strategy)
15. [Failure Scenarios & Handling](#failure-scenarios--handling)
16. [Trade-offs & Design Decisions](#trade-offs--design-decisions)
17. [Interview Discussion Points](#interview-discussion-points)

---

## Overview

A comprehensive Cluster Health Monitoring System that monitors the health, performance, and availability of distributed systems, clusters, and infrastructure components. The system collects metrics, logs, traces, and events to provide real-time visibility into system health, detect anomalies, and trigger alerts.

**Key Features:**
- Real-time metrics collection
- Health check monitoring
- Performance monitoring
- Resource utilization tracking
- Alerting and notification
- Dashboards and visualization
- Anomaly detection
- Log aggregation
- Distributed tracing
- Capacity planning insights
- Historical data analysis
- Multi-cluster support

---

## Requirements

### Functional Requirements

1. **Metrics Collection**
   - System metrics (CPU, memory, disk, network)
   - Application metrics (request rate, latency, errors)
   - Custom business metrics
   - Infrastructure metrics (Kubernetes, containers)
   - Database metrics
   - Cache metrics

2. **Health Checks**
   - Endpoint health checks (HTTP, TCP, gRPC)
   - Service health checks
   - Dependency health checks
   - Synthetic monitoring
   - Uptime monitoring

3. **Alerting**
   - Threshold-based alerts
   - Anomaly-based alerts
   - Composite alerts
   - Alert routing and escalation
   - Alert suppression
   - Alert acknowledgment

4. **Dashboards**
   - Real-time dashboards
   - Custom dashboards
   - Pre-built templates
   - Interactive visualizations
   - Time-series graphs
   - Heatmaps

5. **Log Aggregation**
   - Centralized log collection
   - Log search and filtering
   - Log correlation
   - Log retention policies

6. **Distributed Tracing**
   - Request tracing across services
   - Trace visualization
   - Performance analysis
   - Dependency mapping

7. **Anomaly Detection**
   - Statistical anomaly detection
   - Machine learning-based detection
   - Pattern recognition
   - Baseline comparison

8. **Reporting**
   - Health reports
   - Performance reports
   - Capacity reports
   - SLA reports
   - Custom reports

### Non-Functional Requirements

1. **Scalability**
   - Support 100K+ metrics per second
   - Monitor 10K+ nodes
   - Handle 1M+ time-series
   - Support 100+ clusters
   - Multi-region deployment
   - 99.9% uptime

2. **Performance**
   - Metric ingestion: < 10ms latency
   - Query response: < 500ms (p95)
   - Alert evaluation: < 1 second
   - Dashboard load: < 2 seconds
   - 99th percentile latency < 1s

3. **Availability**
   - Multi-region active-active
   - Automatic failover
   - Data replication
   - Zero-downtime deployments
   - High availability for critical alerts

4. **Reliability**
   - No metric loss
   - Guaranteed alert delivery
   - Data durability
   - Backup and recovery

5. **Storage**
   - Efficient time-series storage
   - Data compression
   - Retention policies
   - Archive old data

---

## System Architecture

### High-Level Design (HLD)

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Monitored Systems                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │  App 1   │  │  App 2   │  │  App 3   │  │  App N   │     │
│  │(Metrics)│  │(Metrics)│  │(Metrics)│  │(Metrics)│     │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │  Node 1  │  │  Node 2  │  │  Node 3  │  │  Node N  │     │
│  │(Agent)   │  │(Agent)  │  │(Agent)  │  │(Agent)  │     │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘     │
└───────┼─────────────┼──────────────┼──────────────┼────────┘
        │             │               │              │
        └─────────────┴───────────────┴──────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    Collection Layer                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │ Metrics  │  │   Log    │  │  Trace   │  │  Event   │     │
│  │Collector │  │Collector │  │Collector │  │Collector │     │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘     │
└───────┼─────────────┼──────────────┼──────────────┼────────┘
        │             │               │              │
        ▼             ▼               ▼              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Message Queue                              │
│              (Kafka / AWS Kinesis / RabbitMQ)                │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Processing Layer                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │ Metrics  │  │   Log    │  │  Trace   │  │ Anomaly  │     │
│  │Processor │  │Processor │  │Processor │  │ Detector │     │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘     │
└───────┼─────────────┼──────────────┼──────────────┼────────┘
        │             │               │              │
        ▼             ▼               ▼              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Storage Layer                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │TimeSeries│  │Elasticsearch│ │  S3     │  │  Redis   │        │
│  │  DB      │  │  (Logs)  │ │(Archive)│ │(Cache)  │        │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘        │
└───────┼─────────────┼──────────────┼──────────────┼────────┘
        │             │               │              │
        ▼             ▼               ▼              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Service Layer                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │  Query   │  │  Alert   │  │Dashboard│  │  Health  │     │
│  │ Service  │  │ Service  │  │ Service │  │ Service  │     │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘     │
└───────┼─────────────┼──────────────┼──────────────┼────────┘
        │             │               │              │
        ▼             ▼               ▼              ▼
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway                                │
│              (Kong / AWS API Gateway / Envoy)                │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Client Applications                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │Dashboard │  │  Mobile │  │   CLI   │  │   API    │     │
│  │   Web    │  │   App   │  │  Tools  │  │ Clients  │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### HLD Component Breakdown

**1. Collection Layer**
- **Metrics Collector**: Receives metrics from agents, supports multiple protocols
- **Log Collector**: Collects and parses application logs
- **Trace Collector**: Collects distributed traces
- **Event Collector**: Collects system events

**2. Processing Layer**
- **Metrics Processor**: Validates, aggregates, transforms metrics
- **Log Processor**: Parses, enriches, routes logs
- **Trace Processor**: Correlates and processes traces
- **Anomaly Detector**: Detects anomalies using ML/statistical methods

**3. Storage Layer**
- **Time-Series DB**: Stores metrics (InfluxDB, TimescaleDB)
- **Search Engine**: Stores logs (Elasticsearch)
- **Object Storage**: Archives old data (S3)
- **Cache**: Caches queries and metadata (Redis)

**4. Service Layer**
- **Query Service**: Handles time-series queries
- **Alert Service**: Evaluates and routes alerts
- **Dashboard Service**: Renders dashboards
- **Health Service**: Executes health checks

### Component Details

#### 1. Metrics Collector
- Collects metrics from agents
- Supports multiple protocols (Prometheus, StatsD, etc.)
- Buffers and batches metrics
- Handles backpressure

#### 2. Log Collector
- Collects logs from applications
- Supports various log formats
- Parses and enriches logs
- Routes to storage

#### 3. Trace Collector
- Collects distributed traces
- Supports OpenTelemetry, Jaeger
- Correlates traces
- Stores trace data

#### 4. Metrics Processor
- Validates metrics
- Aggregates metrics
- Applies transformations
- Routes to storage

#### 5. Alert Service
- Evaluates alert rules
- Triggers alerts
- Routes alerts
- Manages alert state

#### 6. Query Service
- Time-series queries
- Aggregations
- Downsampling
- Query optimization

#### 7. Dashboard Service
- Dashboard rendering
- Widget management
- Real-time updates
- Export capabilities

#### 8. Health Service
- Health check execution
- Health status aggregation
- Dependency health
- Service health scores

---

## Core Components

### Metrics Collection

**Collection Methods:**
1. **Push Model**: Agents push metrics
2. **Pull Model**: Collector pulls metrics
3. **Hybrid**: Combination of both

**Metrics Types:**
- **Counter**: Incrementing values
- **Gauge**: Current value
- **Histogram**: Distribution of values
- **Summary**: Quantiles and counts

**Collection Agents:**
- Prometheus exporters
- StatsD agents
- Custom agents
- Sidecar containers

### Health Checks

**Check Types:**
- **HTTP**: GET request to endpoint
- **TCP**: Connection test
- **gRPC**: Health check RPC
- **Script**: Custom script execution
- **Synthetic**: End-to-end tests

**Health Check Flow:**
1. Schedule health check
2. Execute check
3. Evaluate result
4. Update health status
5. Trigger alerts if unhealthy

### Alerting System

**Alert Rules:**
```yaml
alert: HighCPUUsage
expr: cpu_usage > 80
for: 5m
labels:
  severity: warning
annotations:
  summary: "High CPU usage detected"
```

**Alert Evaluation:**
1. Query metrics
2. Evaluate expression
3. Check duration
4. Trigger if conditions met
5. Route alert
6. Update alert state

**Alert Routing:**
- Route by severity
- Route by team
- Route by service
- Escalation policies
- On-call rotation

---

## Database Design

### Metrics Table (TimeSeries)

```sql
-- Using PostgreSQL with TimescaleDB
CREATE TABLE metrics (
    time TIMESTAMPTZ NOT NULL,
    metric_name VARCHAR(255) NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    tags JSONB,
    cluster_id VARCHAR(255),
    node_id VARCHAR(255),
    service_id VARCHAR(255),
    PRIMARY KEY (time, metric_name, node_id)
);

-- Create hypertable
SELECT create_hypertable('metrics', 'time');

-- Create indexes
CREATE INDEX idx_metric_name ON metrics(metric_name, time DESC);
CREATE INDEX idx_cluster ON metrics(cluster_id, time DESC);
CREATE INDEX idx_service ON metrics(service_id, time DESC);
CREATE INDEX idx_tags ON metrics USING GIN(tags);
```

### Health Checks Table

```sql
CREATE TABLE health_checks (
    check_id VARCHAR(255) PRIMARY KEY,
    service_id VARCHAR(255) NOT NULL,
    check_type VARCHAR(50) NOT NULL,
    endpoint VARCHAR(500),
    interval_seconds INTEGER DEFAULT 60,
    timeout_seconds INTEGER DEFAULT 5,
    is_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_service (service_id)
);
```

### Health Check Results Table

```sql
CREATE TABLE health_check_results (
    result_id VARCHAR(255) PRIMARY KEY,
    check_id VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL, -- healthy, unhealthy, degraded
    response_time_ms INTEGER,
    error_message TEXT,
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (check_id) REFERENCES health_checks(check_id),
    INDEX idx_check_time (check_id, checked_at DESC),
    INDEX idx_status (status, checked_at)
);
```

### Alerts Table

```sql
CREATE TABLE alerts (
    alert_id VARCHAR(255) PRIMARY KEY,
    alert_rule_id VARCHAR(255) NOT NULL,
    alert_name VARCHAR(255) NOT NULL,
    severity VARCHAR(50) NOT NULL, -- critical, warning, info
    status VARCHAR(50) DEFAULT 'firing', -- firing, resolved, acknowledged
    message TEXT,
    labels JSONB,
    annotations JSONB,
    started_at TIMESTAMP NOT NULL,
    resolved_at TIMESTAMP,
    acknowledged_at TIMESTAMP,
    acknowledged_by VARCHAR(255),
    FOREIGN KEY (alert_rule_id) REFERENCES alert_rules(rule_id),
    INDEX idx_status (status),
    INDEX idx_severity (severity),
    INDEX idx_started (started_at DESC)
);
```

### Alert Rules Table

```sql
CREATE TABLE alert_rules (
    rule_id VARCHAR(255) PRIMARY KEY,
    rule_name VARCHAR(255) NOT NULL,
    expression TEXT NOT NULL,
    duration VARCHAR(50), -- e.g., "5m"
    severity VARCHAR(50) NOT NULL,
    labels JSONB,
    annotations JSONB,
    is_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_enabled (is_enabled)
);
```

### Services Table

```sql
CREATE TABLE services (
    service_id VARCHAR(255) PRIMARY KEY,
    service_name VARCHAR(255) NOT NULL,
    cluster_id VARCHAR(255) NOT NULL,
    namespace VARCHAR(255),
    service_type VARCHAR(50), -- application, database, cache, etc.
    owner_team VARCHAR(255),
    health_status VARCHAR(50) DEFAULT 'unknown', -- healthy, unhealthy, degraded
    last_health_check TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_cluster (cluster_id),
    INDEX idx_health (health_status)
);
```

### Clusters Table

```sql
CREATE TABLE clusters (
    cluster_id VARCHAR(255) PRIMARY KEY,
    cluster_name VARCHAR(255) NOT NULL,
    region VARCHAR(100),
    environment VARCHAR(50), -- production, staging, development
    cluster_type VARCHAR(50), -- kubernetes, ecs, etc.
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_region (region),
    INDEX idx_environment (environment)
);
```

### Nodes Table

```sql
CREATE TABLE nodes (
    node_id VARCHAR(255) PRIMARY KEY,
    cluster_id VARCHAR(255) NOT NULL,
    node_name VARCHAR(255) NOT NULL,
    node_type VARCHAR(50), -- master, worker, etc.
    ip_address VARCHAR(45),
    status VARCHAR(50) DEFAULT 'unknown', -- healthy, unhealthy, down
    last_heartbeat TIMESTAMP,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cluster_id) REFERENCES clusters(cluster_id),
    INDEX idx_cluster (cluster_id),
    INDEX idx_status (status)
);
```

---

## API Design

### Metrics Endpoints

```
POST   /api/v1/metrics
GET    /api/v1/metrics/query?metric={name}&start={start}&end={end}
GET    /api/v1/metrics/query_range?metric={name}&start={start}&end={end}&step={step}
```

### Health Check Endpoints

```
GET    /api/v1/health/checks
POST   /api/v1/health/checks
GET    /api/v1/health/checks/{check_id}
PUT    /api/v1/health/checks/{check_id}
DELETE /api/v1/health/checks/{check_id}
GET    /api/v1/health/services/{service_id}
GET    /api/v1/health/clusters/{cluster_id}
```

### Alert Endpoints

```
GET    /api/v1/alerts
GET    /api/v1/alerts/{alert_id}
POST   /api/v1/alerts/{alert_id}/acknowledge
POST   /api/v1/alerts/{alert_id}/resolve
GET    /api/v1/alert-rules
POST   /api/v1/alert-rules
PUT    /api/v1/alert-rules/{rule_id}
DELETE /api/v1/alert-rules/{rule_id}
```

### Dashboard Endpoints

```
GET    /api/v1/dashboards
POST   /api/v1/dashboards
GET    /api/v1/dashboards/{dashboard_id}
PUT    /api/v1/dashboards/{dashboard_id}
DELETE /api/v1/dashboards/{dashboard_id}
```

### Example API Requests/Responses

**Query Metrics**
```http
GET /api/v1/metrics/query_range?metric=cpu_usage&start=2024-01-15T00:00:00Z&end=2024-01-15T23:59:59Z&step=1m
Authorization: Bearer {token}

Response: 200 OK
{
  "metric": "cpu_usage",
  "values": [
    {"time": "2024-01-15T00:00:00Z", "value": 45.2},
    {"time": "2024-01-15T00:01:00Z", "value": 47.8},
    ...
  ]
}
```

**Get Service Health**
```http
GET /api/v1/health/services/{service_id}
Authorization: Bearer {token}

Response: 200 OK
{
  "service_id": "svc_123",
  "service_name": "user-service",
  "health_status": "healthy",
  "last_health_check": "2024-01-15T10:30:00Z",
  "checks": [
    {
      "check_id": "check_1",
      "check_type": "http",
      "status": "healthy",
      "response_time_ms": 12
    }
  ]
}
```

---

## Metrics Collection

### Collection Architecture

**Agent-Based Collection:**
- Lightweight agents on each node
- Collect system and application metrics
- Push to collectors
- Handle backpressure

**Pull-Based Collection:**
- Prometheus-style scraping
- Service discovery
- Configurable intervals
- Reliable collection

### Metric Processing

**Processing Pipeline:**
1. Receive metric
2. Validate format
3. Apply transformations
4. Aggregate if needed
5. Route to storage
6. Update indexes

**Aggregations:**
- Sum, average, min, max
- Percentiles
- Rate calculations
- Downsampling

---

## Alerting System

### Alert Rule Evaluation

**Evaluation Engine:**
- Time-series query engine
- Expression evaluator
- Duration checker
- State manager

**Alert States:**
- **Inactive**: Condition not met
- **Pending**: Condition met, waiting for duration
- **Firing**: Alert active
- **Resolved**: Condition no longer met
- **Acknowledged**: Manually acknowledged

### Alert Routing

**Routing Rules:**
- Route by severity
- Route by service/team
- Route by cluster/environment
- Escalation policies
- On-call integration

**Notification Channels:**
- Email
- SMS
- PagerDuty
- Slack
- Webhooks

---

## Dashboards & Visualization

### Dashboard Components

**Widget Types:**
- Time-series graphs
- Gauges
- Tables
- Heatmaps
- Pie charts
- Stat cards

**Dashboard Features:**
- Real-time updates
- Time range selection
- Refresh intervals
- Export (PNG, PDF)
- Sharing

---

## Anomaly Detection

### Detection Methods

1. **Statistical Methods**
   - Z-score
   - Moving averages
   - Standard deviation

2. **Machine Learning**
   - Isolation Forest
   - LSTM networks
   - Autoencoders

3. **Rule-Based**
   - Threshold violations
   - Pattern matching
   - Baseline comparison

### Anomaly Detection Pipeline

1. Collect historical data
2. Train model (if ML-based)
3. Monitor metrics
4. Detect anomalies
5. Generate alerts
6. Learn from feedback

---

## Low-Level Design (LLD)

### Metrics Collector LLD

```python
class MetricsCollector:
    def __init__(self, config: dict):
        self.buffer = CircularBuffer(maxsize=10000)
        self.batch_size = config.get('batch_size', 1000)
        self.flush_interval = config.get('flush_interval', 5)  # seconds
        self.kafka_producer = KafkaProducer(bootstrap_servers=config.kafka_servers)
        self.protocols = {
            'prometheus': PrometheusHandler(),
            'statsd': StatsDHandler(),
            'json': JSONHandler()
        }
        self.metrics = {
            'received': Counter('metrics_received'),
            'dropped': Counter('metrics_dropped'),
            'sent': Counter('metrics_sent')
        }
    
    def collect(self, metric: dict, protocol: str = 'json'):
        try:
            # Parse metric based on protocol
            handler = self.protocols.get(protocol)
            parsed_metric = handler.parse(metric)
            
            # Validate metric
            if not self._validate(parsed_metric):
                self.metrics['dropped'].inc()
                return
            
            # Add to buffer
            if not self.buffer.put(parsed_metric):
                # Buffer full, drop metric
                self.metrics['dropped'].inc()
                return
            
            self.metrics['received'].inc()
            
            # Flush if buffer full
            if self.buffer.size() >= self.batch_size:
                self._flush()
        
        except Exception as e:
            logger.error(f"Error collecting metric: {e}")
            self.metrics['dropped'].inc()
    
    def _flush(self):
        metrics = self.buffer.drain()
        if not metrics:
            return
        
        try:
            # Send to Kafka
            for metric in metrics:
                self.kafka_producer.send('metrics', value=metric)
            
            self.metrics['sent'].inc(len(metrics))
        except Exception as e:
            logger.error(f"Error flushing metrics: {e}")
            # Re-add to buffer or dead letter queue
            self.buffer.put_many(metrics)
    
    def _validate(self, metric: dict) -> bool:
        required_fields = ['metric_name', 'value', 'timestamp']
        return all(field in metric for field in required_fields)
```

### Alert Service LLD

```python
class AlertService:
    def __init__(self, config: dict):
        self.rule_engine = RuleEngine()
        self.query_service = QueryService()
        self.notification_service = NotificationService()
        self.alert_store = AlertStore()
        self.evaluation_interval = config.get('evaluation_interval', 15)  # seconds
        self.alert_cache = {}
    
    def evaluate_rules(self):
        # Get all enabled alert rules
        rules = self.rule_engine.get_enabled_rules()
        
        for rule in rules:
            try:
                # Query metrics
                result = self.query_service.query(rule.expression, rule.time_range)
                
                # Evaluate rule
                is_firing = self._evaluate_expression(result, rule.expression)
                
                # Check duration
                if is_firing:
                    if rule.id not in self.alert_cache:
                        self.alert_cache[rule.id] = {
                            'started_at': time.time(),
                            'firing': False
                        }
                    
                    duration = time.time() - self.alert_cache[rule.id]['started_at']
                    
                    if duration >= rule.duration_seconds and not self.alert_cache[rule.id]['firing']:
                        # Trigger alert
                        self._trigger_alert(rule, result)
                        self.alert_cache[rule.id]['firing'] = True
                else:
                    # Clear alert if it was firing
                    if rule.id in self.alert_cache and self.alert_cache[rule.id]['firing']:
                        self._resolve_alert(rule)
                    self.alert_cache.pop(rule.id, None)
            
            except Exception as e:
                logger.error(f"Error evaluating rule {rule.id}: {e}")
    
    def _trigger_alert(self, rule: AlertRule, result: dict):
        alert = Alert(
            alert_id=str(uuid.uuid4()),
            rule_id=rule.id,
            alert_name=rule.name,
            severity=rule.severity,
            status='firing',
            message=rule.annotations.get('summary', ''),
            labels=rule.labels,
            annotations=rule.annotations,
            started_at=datetime.utcnow()
        )
        
        # Store alert
        self.alert_store.save(alert)
        
        # Send notification
        self.notification_service.send(alert)
    
    def _resolve_alert(self, rule: AlertRule):
        # Find firing alert for this rule
        alert = self.alert_store.get_firing_alert(rule.id)
        if alert:
            alert.status = 'resolved'
            alert.resolved_at = datetime.utcnow()
            self.alert_store.update(alert)
            self.notification_service.send_resolution(alert)
```

### Query Service LLD

```python
class QueryService:
    def __init__(self, config: dict):
        self.tsdb_client = TimescaleDBClient(config.tsdb_config)
        self.cache = RedisCache(ttl=60)
        self.query_optimizer = QueryOptimizer()
    
    def query(self, expression: str, time_range: dict) -> dict:
        # Check cache
        cache_key = self._generate_cache_key(expression, time_range)
        cached_result = self.cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Optimize query
        optimized_query = self.query_optimizer.optimize(expression, time_range)
        
        # Execute query
        result = self.tsdb_client.query(optimized_query)
        
        # Cache result
        self.cache.set(cache_key, result)
        
        return result
    
    def query_range(self, metric_name: str, start: datetime, end: datetime, step: str) -> list:
        # Downsample if needed
        if self._should_downsample(start, end, step):
            return self._downsample_query(metric_name, start, end, step)
        
        # Regular query
        query = f"""
            SELECT time, value 
            FROM metrics 
            WHERE metric_name = '{metric_name}' 
            AND time >= '{start}' 
            AND time <= '{end}'
            ORDER BY time
        """
        
        return self.tsdb_client.query(query)
    
    def _should_downsample(self, start: datetime, end: datetime, step: str) -> bool:
        duration = (end - start).total_seconds()
        step_seconds = self._parse_step(step)
        
        # Downsample if more than 1000 data points
        return duration / step_seconds > 1000
    
    def _downsample_query(self, metric_name: str, start: datetime, end: datetime, step: str):
        # Use time_bucket for downsampling
        query = f"""
            SELECT time_bucket('{step}', time) as bucket, 
                   avg(value) as value 
            FROM metrics 
            WHERE metric_name = '{metric_name}' 
            AND time >= '{start}' 
            AND time <= '{end}'
            GROUP BY bucket
            ORDER BY bucket
        """
        
        return self.tsdb_client.query(query)
```

### Health Check Service LLD

```python
class HealthCheckService:
    def __init__(self, config: dict):
        self.check_executor = CheckExecutor()
        self.result_store = HealthCheckResultStore()
        self.scheduler = Scheduler()
        self.aggregator = HealthAggregator()
    
    def register_check(self, check: HealthCheck):
        # Schedule periodic execution
        self.scheduler.schedule(
            check.check_id,
            self._execute_check,
            interval=check.interval_seconds,
            args=(check,)
        )
    
    def _execute_check(self, check: HealthCheck):
        start_time = time.time()
        
        try:
            # Execute check based on type
            if check.check_type == 'http':
                result = self._execute_http_check(check)
            elif check.check_type == 'tcp':
                result = self._execute_tcp_check(check)
            elif check.check_type == 'grpc':
                result = self._execute_grpc_check(check)
            else:
                result = self._execute_script_check(check)
            
            response_time = (time.time() - start_time) * 1000  # ms
            
            # Store result
            check_result = HealthCheckResult(
                check_id=check.check_id,
                status=result['status'],
                response_time_ms=int(response_time),
                checked_at=datetime.utcnow()
            )
            
            self.result_store.save(check_result)
            
            # Update service health
            self._update_service_health(check.service_id)
        
        except Exception as e:
            logger.error(f"Error executing check {check.check_id}: {e}")
            # Store failure result
            check_result = HealthCheckResult(
                check_id=check.check_id,
                status='unhealthy',
                error_message=str(e),
                checked_at=datetime.utcnow()
            )
            self.result_store.save(check_result)
    
    def _execute_http_check(self, check: HealthCheck) -> dict:
        try:
            response = requests.get(
                check.endpoint,
                timeout=check.timeout_seconds
            )
            
            if response.status_code == 200:
                return {'status': 'healthy'}
            else:
                return {'status': 'unhealthy'}
        
        except requests.RequestException:
            return {'status': 'unhealthy'}
    
    def _update_service_health(self, service_id: str):
        # Get recent check results
        results = self.result_store.get_recent_results(service_id, minutes=5)
        
        # Aggregate health
        health_status = self.aggregator.aggregate(results)
        
        # Update service status
        service_store = ServiceStore()
        service_store.update_health_status(service_id, health_status)
```

## Scalability Considerations

### Horizontal Scaling

**1. Stateless Collectors**
- **Strategy**: Deploy multiple collector instances
- **Implementation**: 
  - Load balancer distributes traffic
  - No shared state between instances
  - Kafka for buffering
- **Scaling**: Auto-scale based on metrics ingestion rate

**2. Distributed Processing**
- **Strategy**: Process metrics in parallel
- **Implementation**:
  - Kafka partitions for parallel processing
  - Consumer groups for load distribution
  - Stateless processors
- **Scaling**: Add processors as needed

**3. Sharded Storage**
- **Strategy**: Shard time-series data
- **Implementation**:
  - Shard by metric name or time
  - Distributed time-series database
  - Consistent hashing for shard assignment
- **Scaling**: Add shards as data grows

**4. Load Balancers**
- **Strategy**: Distribute load across services
- **Implementation**:
  - API Gateway for external traffic
  - Internal load balancers for services
  - Health checks for routing
- **Scaling**: Add instances behind load balancers

**5. Auto-Scaling**
- **Strategy**: Scale based on metrics
- **Implementation**:
  - CPU/Memory thresholds
  - Queue depth thresholds
  - Custom metrics
- **Scaling**: Kubernetes HPA or cloud auto-scaling

### Storage Optimization

**1. Data Compression**
- **Strategy**: Compress time-series data
- **Implementation**:
  - Columnar compression (Gorilla, Delta)
  - Snappy compression for logs
  - Compression ratios: 10-100x
- **Impact**: Reduces storage by 90%+

**2. Downsampling**
- **Strategy**: Reduce data granularity over time
- **Implementation**:
  - Keep 1s resolution for 1 hour
  - Keep 1m resolution for 1 day
  - Keep 1h resolution for 1 year
- **Impact**: Reduces storage by 99%+

**3. Retention Policies**
- **Strategy**: Delete old data
- **Implementation**:
  - Hot data: 7 days (fast storage)
  - Warm data: 30 days (standard storage)
  - Cold data: 1 year (cheap storage)
  - Archive: >1 year (object storage)
- **Impact**: Optimizes storage costs

**4. Archival**
- **Strategy**: Move old data to object storage
- **Implementation**:
  - S3 for long-term storage
  - Compressed format
  - Restore on demand
- **Impact**: Reduces active storage costs

**5. Partitioning**
- **Strategy**: Partition data by time
- **Implementation**:
  - Daily or weekly partitions
  - Easy to drop old partitions
  - Faster queries on recent data
- **Impact**: Improves query performance

### Query Optimization

**1. Indexes**
- **Strategy**: Index frequently queried fields
- **Implementation**:
  - B-tree indexes on metric_name, time
  - GIN indexes on tags (JSONB)
  - Composite indexes for common queries
- **Impact**: 10-100x faster queries

**2. Materialized Views**
- **Strategy**: Pre-aggregate common queries
- **Implementation**:
  - Hourly/daily aggregations
  - Refresh periodically
  - Query views instead of raw data
- **Impact**: 100-1000x faster aggregations

**3. Query Caching**
- **Strategy**: Cache query results
- **Implementation**:
  - Redis cache for common queries
  - TTL based on data freshness
  - Invalidate on updates
- **Impact**: Sub-second query responses

**4. Parallel Queries**
- **Strategy**: Execute queries in parallel
- **Implementation**:
  - Split queries by time range
  - Execute on multiple shards
  - Merge results
- **Impact**: Linear speedup with shards

**5. Pre-Aggregation**
- **Strategy**: Pre-compute aggregations
- **Implementation**:
  - Rollup tables for common aggregations
  - Update incrementally
  - Query rollups for historical data
- **Impact**: Fast aggregations on large datasets

---

## Optimizations

### Performance Optimizations

#### 1. Metrics Collection Optimization

**Batch Collection:**

```python
class BatchMetricsCollector:
    def __init__(self, batch_size: int = 1000, flush_interval: float = 5.0):
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.batch = []
        self.last_flush = time.time()
    
    async def collect_metric(self, metric: Metric):
        self.batch.append(metric)
        
        if len(self.batch) >= self.batch_size:
            await self.flush()
        elif time.time() - self.last_flush > self.flush_interval:
            await self.flush()
    
    async def flush(self):
        if not self.batch:
            return
        
        # Batch write to Kafka
        await self.kafka_producer.send_batch(self.batch)
        self.batch.clear()
        self.last_flush = time.time()
```

**Metric Deduplication:**

```python
class MetricDeduplicator:
    def __init__(self):
        self.recent_metrics = set()
        self.ttl = 60  # 1 minute
    
    def deduplicate(self, metric: Metric) -> bool:
        key = (metric.name, metric.labels, metric.timestamp)
        
        if key in self.recent_metrics:
            return False  # Duplicate
        
        self.recent_metrics.add(key)
        return True
```

#### 2. Query Optimization

**Query Result Caching:**

```python
class QueryCacheOptimizer:
    def __init__(self):
        self.cache = LRUCache(max_size=1000, ttl=60)
    
    async def query_with_cache(self, query: str, time_range: tuple) -> list:
        cache_key = f"{query}:{time_range}"
        
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        result = await self.execute_query(query, time_range)
        self.cache.set(cache_key, result)
        
        return result
```

**Pre-aggregation:**

```python
class PreAggregator:
    async def pre_aggregate_metrics(self, metrics: list):
        # Pre-aggregate by time window
        for window in ['1m', '5m', '1h']:
            aggregated = self.aggregate_by_window(metrics, window)
            await self.store_pre_aggregated(window, aggregated)
```

---

## Monitoring & Analytics

### Key Metrics

**System Metrics:**
- Collection rate
- Processing latency
- Storage usage
- Query performance

**Business Metrics:**
- Services monitored
- Alerts fired
- Uptime
- MTTR (Mean Time To Resolve)

---

## Deployment Strategy

### Infrastructure

- **Containerization**: Docker
- **Orchestration**: Kubernetes
- **Time-Series DB**: InfluxDB, TimescaleDB, or Prometheus
- **Search**: Elasticsearch
- **Cache**: Redis

### High Availability

- Multi-region deployment
- Data replication
- Automatic failover
- Backup and recovery

---

## Fault Tolerance

### Collector Fault Tolerance

**1. Collector Redundancy**
```python
class MetricsAgent:
    def __init__(self, collector_urls: list):
        self.collector_urls = collector_urls  # Multiple collectors
        self.current_collector = 0
        self.local_buffer = Queue(maxsize=10000)
        self.retry_queue = Queue()
    
    def send_metric(self, metric: dict):
        # Try to send to current collector
        try:
            response = requests.post(
                self.collector_urls[self.current_collector],
                json=metric,
                timeout=5
            )
            response.raise_for_status()
            return True
        
        except Exception as e:
            # Add to retry queue
            self.retry_queue.put(metric)
            
            # Try next collector
            self.current_collector = (self.current_collector + 1) % len(self.collector_urls)
            
            # Retry with exponential backoff
            self._retry_with_backoff()
            return False
    
    def _retry_with_backoff(self):
        retry_count = 0
        max_retries = 3
        
        while not self.retry_queue.empty() and retry_count < max_retries:
            metric = self.retry_queue.get()
            
            try:
                if self.send_metric(metric):
                    retry_count = 0
                else:
                    retry_count += 1
                    time.sleep(2 ** retry_count)  # Exponential backoff
            
            except Exception:
                # If all collectors fail, buffer locally
                self.local_buffer.put(metric)
```

**2. Agent Buffering**
- **Local Buffer**: Buffer metrics locally when collectors unavailable
- **Persistent Buffer**: Use disk buffer for durability
- **Batch Sending**: Send buffered metrics in batches
- **Backpressure Handling**: Drop metrics if buffer full

**3. Collector Health Checks**
- **Health Endpoints**: Monitor collector health
- **Automatic Failover**: Switch to healthy collectors
- **Circuit Breaker**: Stop sending to failed collectors

### Storage Fault Tolerance

**1. Database Replication**
```python
class TimeSeriesDB:
    def __init__(self, config: dict):
        self.primary = TimescaleDBClient(config.primary)
        self.replicas = [TimescaleDBClient(r) for r in config.replicas]
        self.current_replica = 0
        self.replication_lag_threshold = 60  # seconds
    
    def write(self, metric: dict):
        # Write to primary
        try:
            self.primary.insert(metric)
            
            # Async replication to replicas
            for replica in self.replicas:
                asyncio.create_task(self._replicate_to_replica(replica, metric))
        
        except Exception as e:
            logger.error(f"Error writing to primary: {e}")
            raise
    
    def read(self, query: str):
        # Try primary first
        try:
            return self.primary.query(query)
        except Exception:
            # Fallback to replica
            return self._read_from_replica(query)
    
    def _read_from_replica(self, query: str):
        for replica in self.replicas:
            try:
                # Check replication lag
                lag = replica.get_replication_lag()
                if lag < self.replication_lag_threshold:
                    return replica.query(query)
            except Exception:
                continue
        
        raise DatabaseUnavailableError()
```

**2. Backup and Recovery**
- **Regular Backups**: Daily backups of critical data
- **Point-in-Time Recovery**: Restore to specific timestamp
- **Backup Verification**: Verify backups regularly
- **Recovery Testing**: Test recovery procedures

**3. Read Replicas**
- **Multiple Replicas**: Deploy multiple read replicas
- **Load Distribution**: Distribute reads across replicas
- **Replication Lag Monitoring**: Monitor lag and route accordingly
- **Automatic Failover**: Promote replica on primary failure

### Processing Fault Tolerance

**1. Message Queue Resilience**
```python
class MetricsProcessor:
    def __init__(self, kafka_config: dict):
        self.consumer = KafkaConsumer(
            'metrics',
            bootstrap_servers=kafka_config.servers,
            group_id='metrics-processors',
            enable_auto_commit=False  # Manual commit for reliability
        )
        self.dead_letter_queue = DeadLetterQueue()
        self.max_retries = 3
    
    def process(self):
        for message in self.consumer:
            try:
                # Process metric
                self._process_metric(message.value)
                
                # Commit offset
                self.consumer.commit()
            
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                
                # Retry logic
                if message.retry_count < self.max_retries:
                    message.retry_count += 1
                    # Re-queue message
                    self._requeue_message(message)
                else:
                    # Send to dead letter queue
                    self.dead_letter_queue.put(message)
```

**2. Idempotent Processing**
- **Idempotent Operations**: Make operations idempotent
- **Duplicate Detection**: Detect and skip duplicates
- **Idempotency Keys**: Use keys to identify duplicates

**3. Circuit Breaker**
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

## Failure Safety

### Failure Scenarios & Handling

**1. Collector Failure**

**Scenario**: All metrics collectors fail.

**Impact**: Cannot ingest new metrics.

**Mitigation**:
- **Multiple Collectors**: Deploy multiple collector instances
- **Agent Buffering**: Agents buffer metrics locally
- **Retry Mechanism**: Retry with exponential backoff
- **Dead Letter Queue**: Store failed metrics for later processing
- **Graceful Degradation**: Continue with cached data

**2. Storage Failure**

**Scenario**: Time-series database fails.

**Impact**: Cannot store or query metrics.

**Mitigation**:
- **Replication**: Primary-replica setup with automatic failover
- **Backup Storage**: Regular backups to object storage
- **Read Replicas**: Serve reads from replicas
- **Caching**: Use Redis cache for critical queries
- **Data Recovery**: Restore from backups

**3. Processing Failure**

**Scenario**: Metrics processor fails.

**Impact**: Metrics not processed or aggregated.

**Mitigation**:
- **Multiple Processors**: Deploy multiple processor instances
- **Message Queue**: Kafka buffers messages
- **Retry Logic**: Retry failed processing
- **Dead Letter Queue**: Store failed messages
- **Monitoring**: Alert on processing failures

**4. Query Service Failure**

**Scenario**: Query service becomes unavailable.

**Impact**: Cannot query metrics or dashboards.

**Mitigation**:
- **Multiple Instances**: Deploy multiple query service instances
- **Load Balancer**: Distribute queries across instances
- **Caching**: Cache query results
- **Read Replicas**: Query from read replicas
- **Fallback**: Serve cached data

**5. Alert Service Failure**

**Scenario**: Alert service fails.

**Impact**: Alerts not evaluated or sent.

**Mitigation**:
- **Multiple Instances**: Deploy multiple alert service instances
- **State Persistence**: Persist alert state
- **Retry Logic**: Retry alert evaluation
- **Notification Queue**: Queue notifications
- **Monitoring**: Monitor alert service health

**6. Network Partition**

**Scenario**: Network splits into partitions.

**Impact**: Services in different partitions cannot communicate.

**Mitigation**:
- **Multi-Region**: Deploy in multiple regions
- **Partition Detection**: Detect and handle partitions
- **Graceful Degradation**: Continue operation in partitions
- **Merge Handling**: Merge when partitions reconnect
- **Data Reconciliation**: Reconcile data after merge

### Recovery Mechanisms

**1. Data Recovery**
```python
class DataRecovery:
    def __init__(self, backup_storage: S3Client, tsdb: TimeSeriesDB):
        self.backup_storage = backup_storage
        self.tsdb = tsdb
    
    def restore_from_backup(self, backup_id: str, target_time: datetime):
        # Download backup
        backup_data = self.backup_storage.download(backup_id)
        
        # Restore to target time
        self.tsdb.restore(backup_data, target_time)
        
        # Verify restoration
        self._verify_restoration(target_time)
    
    def point_in_time_recovery(self, target_time: datetime):
        # Find latest backup before target time
        backup = self.backup_storage.find_backup_before(target_time)
        
        # Restore backup
        self.restore_from_backup(backup.id, backup.timestamp)
        
        # Replay transactions after backup
        self._replay_transactions(backup.timestamp, target_time)
```

**2. Service Recovery**
- **Health Checks**: Monitor service health
- **Automatic Restart**: Restart failed services
- **Gradual Recovery**: Gradually increase traffic
- **State Restoration**: Restore service state from storage

**3. Alert Recovery**
- **State Persistence**: Persist alert state
- **Re-evaluation**: Re-evaluate alerts after recovery
- **Notification Retry**: Retry failed notifications
- **Alert Reconciliation**: Reconcile alert state

---

## Trade-offs & Design Decisions

### 1. Push vs Pull

**Decision**: Hybrid approach
**Rationale**: Balance reliability and efficiency

### 2. Storage Technology

**Decision**: Time-series database
**Rationale**: Optimized for time-series data

### 3. Alert Evaluation

**Decision**: Real-time evaluation
**Rationale**: Fast alerting, but higher resource usage

---

## Interview Discussion Points

1. How do you handle high-cardinality metrics?
2. How do you scale metric collection?
3. How do you reduce alert noise?
4. How do you detect anomalies?
5. How do you optimize storage?

---

## Technology Stack

### Backend
- **Language**: Go, Python, or Java
- **Time-Series DB**: InfluxDB, TimescaleDB, Prometheus
- **Search**: Elasticsearch
- **Cache**: Redis
- **Message Queue**: Kafka

### Infrastructure
- **Containerization**: Docker
- **Orchestration**: Kubernetes
- **Monitoring**: Prometheus, Grafana

---

## Conclusion

A Cluster Health Monitoring System is critical for maintaining system reliability and performance. The system must scale to handle millions of metrics while providing real-time visibility and accurate alerting.

Key success factors include:
- Efficient metric collection
- Scalable storage
- Fast queries
- Accurate alerting
- Excellent dashboards
- Anomaly detection

