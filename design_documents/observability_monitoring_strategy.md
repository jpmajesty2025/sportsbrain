# Production Observability & Monitoring Strategy for SportsBrain

## Current State Assessment

### What We Have Now
- **Local Logs**: Python logging that prints to console
- **Railway Logs**: Basic stdout/stderr captured by Railway (temporary, not searchable)
- **No Persistent Storage**: Logs disappear after deployment restarts
- **No Alerting**: We don't know when things fail unless users complain
- **No Metrics**: Can't track fallback rates, response times, or success rates

### Critical Gaps
1. **Milvus Fallbacks**: Currently invisible in production
2. **Agent Failures**: No visibility into the 20-30% failure rate
3. **Performance Issues**: No way to identify slow queries
4. **Security Events**: Rate limiting and attacks not tracked
5. **User Behavior**: No analytics on what users actually do

## Proposed Solution Architecture

### Tier 1: Immediate (Free/Low-Cost) - Week 1

#### Option A: Structured Logging to PostgreSQL (Simplest)
```python
# backend/app/monitoring/db_logger.py
from sqlalchemy import create_engine, Column, String, DateTime, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import json

Base = declarative_base()

class SystemLog(Base):
    __tablename__ = 'system_logs'
    
    id = Column(String, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    level = Column(String)  # ERROR, WARNING, INFO
    category = Column(String)  # MILVUS_FALLBACK, AGENT_FAILURE, etc.
    message = Column(String)
    context = Column(JSON)  # Query, user_id, agent_type, etc.
    latency_ms = Column(Float)
    
class ProductionLogger:
    """Log critical events to PostgreSQL for production visibility"""
    
    def __init__(self):
        self.engine = create_engine(os.getenv('DATABASE_URL'))
        Base.metadata.create_all(self.engine)
    
    def log_milvus_fallback(self, query: str, reason: str, user_id: str = None):
        """Log when Milvus fails and we fallback to PostgreSQL"""
        log_entry = SystemLog(
            id=str(uuid.uuid4()),
            level='WARNING',
            category='MILVUS_FALLBACK',
            message=f'Milvus search failed: {reason}',
            context={
                'query': query,
                'user_id': user_id,
                'fallback_method': 'postgresql',
                'timestamp': datetime.utcnow().isoformat()
            }
        )
        session = Session(self.engine)
        session.add(log_entry)
        session.commit()
    
    def log_agent_failure(self, agent_type: str, query: str, error: str):
        """Log agent failures for analysis"""
        # Similar implementation
        pass
```

**Simple Dashboard Endpoint**:
```python
# backend/app/api/monitoring.py
@router.get("/api/monitoring/fallbacks")
async def get_fallback_stats(
    hours: int = 24,
    current_user: User = Depends(get_current_user)
):
    """Get Milvus fallback statistics"""
    if not current_user.is_admin:
        raise HTTPException(403, "Admin only")
    
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    
    stats = db.query(SystemLog).filter(
        SystemLog.category == 'MILVUS_FALLBACK',
        SystemLog.timestamp > cutoff
    ).all()
    
    return {
        'total_fallbacks': len(stats),
        'fallback_rate': len(stats) / total_queries,
        'common_queries': Counter([s.context['query'] for s in stats]).most_common(10),
        'timeline': group_by_hour(stats)
    }
```

#### Option B: Free Tier Cloud Logging (Better for Scale)

**1. Axiom (Free tier: 500MB/month, 30-day retention)**
```python
# backend/app/monitoring/axiom_logger.py
from axiom import Client
import os

class AxiomLogger:
    def __init__(self):
        self.client = Client(os.getenv('AXIOM_TOKEN'))
        self.dataset = 'sportsbrain-prod'
    
    def log_event(self, event_type: str, data: dict):
        """Send structured logs to Axiom"""
        self.client.ingest_events(
            dataset=self.dataset,
            events=[{
                '_time': datetime.utcnow().isoformat(),
                'event_type': event_type,
                **data
            }]
        )
    
    def log_milvus_fallback(self, query: str, reason: str):
        self.log_event('milvus_fallback', {
            'query': query,
            'reason': reason,
            'service': 'sportsbrain-backend'
        })
```

**2. Logtail (Free tier: 1GB/month)**
```python
# backend/app/monitoring/logtail_setup.py
import logging
from logtail import LogtailHandler

# Add to FastAPI startup
handler = LogtailHandler(source_token=os.getenv('LOGTAIL_TOKEN'))
logging.getLogger().addHandler(handler)

# Now all Python logs go to Logtail automatically
logger.warning("MILVUS_FALLBACK", extra={
    "query": query,
    "user_id": user_id,
    "fallback_reason": reason
})
```

### Tier 2: Professional Monitoring (Month 2)

#### Datadog APM (Free tier available)
```python
# backend/app/monitoring/datadog_setup.py
from ddtrace import tracer, patch_all
from datadog import initialize, statsd

# Auto-instrument all libraries
patch_all()

# Initialize
initialize(
    api_key=os.getenv('DD_API_KEY'),
    app_key=os.getenv('DD_APP_KEY')
)

# Custom metrics
class DatadogMetrics:
    @staticmethod
    def track_milvus_fallback():
        statsd.increment('sportsbrain.milvus.fallback')
    
    @staticmethod
    def track_agent_latency(agent_type: str, latency_ms: float):
        statsd.histogram(f'sportsbrain.agent.latency', 
                         latency_ms, 
                         tags=[f'agent:{agent_type}'])
    
    @staticmethod
    def track_rerank_impact(before_score: float, after_score: float):
        improvement = after_score - before_score
        statsd.gauge('sportsbrain.rerank.improvement', improvement)
```

**Benefits**:
- Distributed tracing (see full request flow)
- Real-time alerting
- Custom dashboards
- Anomaly detection
- Log aggregation

### Tier 3: Full Observability Stack (Month 3+)

#### Open Source Stack (Self-Hosted)
```yaml
# docker-compose.observability.yml
version: '3.8'

services:
  # Metrics Collection
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
  
  # Visualization
  grafana:
    image: grafana/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    ports:
      - "3000:3000"
  
  # Log Aggregation
  loki:
    image: grafana/loki
    ports:
      - "3100:3100"
  
  # Distributed Tracing
  jaeger:
    image: jaegertracing/all-in-one
    ports:
      - "16686:16686"
      - "6831:6831/udp"
  
  # Application Metrics
  statsd-exporter:
    image: prom/statsd-exporter
    ports:
      - "9102:9102"
      - "8125:8125/udp"
```

## Implementation Plan

### Phase 1: Database Logging (Day 1)
```python
# backend/app/core/monitoring.py
from enum import Enum
from typing import Optional
import structlog

class EventType(Enum):
    MILVUS_FALLBACK = "milvus_fallback"
    AGENT_FAILURE = "agent_failure"
    AGENT_SUCCESS = "agent_success"
    RERANK_APPLIED = "rerank_applied"
    SECURITY_VIOLATION = "security_violation"
    RATE_LIMIT_HIT = "rate_limit_hit"

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

class MonitoringService:
    """Centralized monitoring for production visibility"""
    
    def __init__(self):
        self.db_logger = ProductionLogger()
        self.metrics = {}
    
    def track_event(
        self,
        event_type: EventType,
        message: str,
        context: dict,
        latency_ms: Optional[float] = None,
        user_id: Optional[str] = None
    ):
        """Track any significant event"""
        
        # Log to structured logger (goes to Railway logs)
        logger.info(
            event_type.value,
            message=message,
            user_id=user_id,
            latency_ms=latency_ms,
            **context
        )
        
        # Log to database for persistence
        self.db_logger.log_event(
            event_type=event_type.value,
            message=message,
            context=context,
            latency_ms=latency_ms,
            user_id=user_id
        )
        
        # Update in-memory metrics (for quick access)
        self._update_metrics(event_type, latency_ms)
    
    def _update_metrics(self, event_type: EventType, latency_ms: Optional[float]):
        """Update in-memory metrics for quick access"""
        key = event_type.value
        if key not in self.metrics:
            self.metrics[key] = {
                'count': 0,
                'total_latency': 0,
                'avg_latency': 0
            }
        
        self.metrics[key]['count'] += 1
        if latency_ms:
            self.metrics[key]['total_latency'] += latency_ms
            self.metrics[key]['avg_latency'] = (
                self.metrics[key]['total_latency'] / 
                self.metrics[key]['count']
            )
    
    def get_metrics_summary(self) -> dict:
        """Get current metrics summary"""
        return {
            'events': self.metrics,
            'milvus_fallback_rate': self._calculate_fallback_rate(),
            'agent_success_rate': self._calculate_success_rate(),
            'avg_response_time': self._calculate_avg_response_time()
        }

# Global instance
monitoring = MonitoringService()
```

### Phase 2: Integration Points (Day 2)

**Updated TradeImpact Agent**:
```python
from app.core.monitoring import monitoring, EventType

def analyze_trade_impact(self, input_str: str) -> str:
    start_time = time.time()
    user_id = self.context.get('user_id')  # If available
    
    try:
        # Try Milvus first
        milvus_results = self._search_trade_documents(input_str)
        
        if "Milvus connection not configured" in milvus_results:
            # CRITICAL: Log the fallback!
            monitoring.track_event(
                event_type=EventType.MILVUS_FALLBACK,
                message="Milvus search failed, using PostgreSQL",
                context={
                    'query': input_str,
                    'agent': 'TradeImpact',
                    'reason': 'connection_failed'
                },
                user_id=user_id
            )
            
            # Use PostgreSQL fallback
            result = self._fallback_trade_analysis(input_str)
        else:
            result = milvus_results
        
        # Track success
        latency = (time.time() - start_time) * 1000
        monitoring.track_event(
            event_type=EventType.AGENT_SUCCESS,
            message="Trade impact analysis completed",
            context={'query': input_str, 'agent': 'TradeImpact'},
            latency_ms=latency,
            user_id=user_id
        )
        
        return result
        
    except Exception as e:
        # Track failure
        monitoring.track_event(
            event_type=EventType.AGENT_FAILURE,
            message=f"Trade impact analysis failed: {str(e)}",
            context={
                'query': input_str,
                'agent': 'TradeImpact',
                'error': str(e),
                'traceback': traceback.format_exc()
            },
            user_id=user_id
        )
        raise
```

### Phase 3: Monitoring Dashboard (Day 3)

**Simple Admin Dashboard**:
```python
# backend/app/api/admin.py
from fastapi import APIRouter, Depends, HTTPException
from app.core.monitoring import monitoring

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.get("/monitoring/dashboard")
async def monitoring_dashboard(
    current_user: User = Depends(get_current_admin_user)
):
    """Get monitoring dashboard data"""
    
    # Get last 24 hours of data
    recent_logs = monitoring.get_recent_logs(hours=24)
    
    # Calculate key metrics
    total_requests = len(recent_logs)
    milvus_fallbacks = len([l for l in recent_logs 
                           if l.event_type == 'milvus_fallback'])
    agent_failures = len([l for l in recent_logs 
                         if l.event_type == 'agent_failure'])
    
    # Get patterns
    fallback_queries = Counter([
        l.context.get('query', 'unknown') 
        for l in recent_logs 
        if l.event_type == 'milvus_fallback'
    ])
    
    return {
        'summary': {
            'total_requests': total_requests,
            'milvus_fallback_rate': (milvus_fallbacks / total_requests * 100) 
                                   if total_requests > 0 else 0,
            'agent_failure_rate': (agent_failures / total_requests * 100) 
                                if total_requests > 0 else 0,
            'avg_latency_ms': monitoring.get_avg_latency(),
        },
        'milvus_fallbacks': {
            'count': milvus_fallbacks,
            'top_queries': fallback_queries.most_common(10),
            'timeline': group_by_hour(milvus_fallbacks)
        },
        'agent_performance': monitoring.get_agent_metrics(),
        'recent_errors': monitoring.get_recent_errors(limit=20),
        'alerts': monitoring.get_active_alerts()
    }

@router.get("/monitoring/export")
async def export_logs(
    start_date: datetime,
    end_date: datetime,
    event_type: Optional[str] = None,
    current_user: User = Depends(get_current_admin_user)
):
    """Export logs for analysis"""
    logs = monitoring.export_logs(
        start_date=start_date,
        end_date=end_date,
        event_type=event_type
    )
    
    # Convert to CSV or JSON
    return {
        'logs': logs,
        'count': len(logs),
        'export_time': datetime.utcnow()
    }
```

**Frontend Monitoring Component**:
```tsx
// frontend/src/components/Admin/MonitoringDashboard.tsx
import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip } from 'recharts';

const MonitoringDashboard: React.FC = () => {
    const [metrics, setMetrics] = useState(null);
    
    useEffect(() => {
        fetchMetrics();
        const interval = setInterval(fetchMetrics, 30000); // Refresh every 30s
        return () => clearInterval(interval);
    }, []);
    
    const fetchMetrics = async () => {
        const response = await fetch('/api/admin/monitoring/dashboard');
        const data = await response.json();
        setMetrics(data);
    };
    
    if (!metrics) return <div>Loading...</div>;
    
    return (
        <div className="monitoring-dashboard">
            <h2>System Monitoring</h2>
            
            {/* Alert Banner */}
            {metrics.summary.milvus_fallback_rate > 50 && (
                <Alert severity="error">
                    Critical: Milvus fallback rate is {metrics.summary.milvus_fallback_rate.toFixed(1)}%
                </Alert>
            )}
            
            {/* Key Metrics */}
            <Grid container spacing={3}>
                <Grid item xs={3}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6">Total Requests</Typography>
                            <Typography variant="h3">{metrics.summary.total_requests}</Typography>
                        </CardContent>
                    </Card>
                </Grid>
                
                <Grid item xs={3}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6">Milvus Fallback Rate</Typography>
                            <Typography variant="h3" color={metrics.summary.milvus_fallback_rate > 10 ? 'error' : 'inherit'}>
                                {metrics.summary.milvus_fallback_rate.toFixed(1)}%
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>
                
                <Grid item xs={3}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6">Agent Success Rate</Typography>
                            <Typography variant="h3">
                                {(100 - metrics.summary.agent_failure_rate).toFixed(1)}%
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>
                
                <Grid item xs={3}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6">Avg Response Time</Typography>
                            <Typography variant="h3">{metrics.summary.avg_latency_ms.toFixed(0)}ms</Typography>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>
            
            {/* Fallback Timeline */}
            <Card style={{ marginTop: 20 }}>
                <CardContent>
                    <Typography variant="h6">Milvus Fallbacks Over Time</Typography>
                    <LineChart width={800} height={300} data={metrics.milvus_fallbacks.timeline}>
                        <XAxis dataKey="hour" />
                        <YAxis />
                        <Tooltip />
                        <Line type="monotone" dataKey="count" stroke="#8884d8" />
                    </LineChart>
                </CardContent>
            </Card>
            
            {/* Top Failing Queries */}
            <Card style={{ marginTop: 20 }}>
                <CardContent>
                    <Typography variant="h6">Top Queries Triggering Fallback</Typography>
                    <List>
                        {metrics.milvus_fallbacks.top_queries.map(([query, count]) => (
                            <ListItem key={query}>
                                <ListItemText 
                                    primary={query} 
                                    secondary={`${count} failures`} 
                                />
                            </ListItem>
                        ))}
                    </List>
                </CardContent>
            </Card>
        </div>
    );
};
```

## Cost Analysis

### Free Tier Options
1. **PostgreSQL Logging**: $0 (uses existing database)
2. **Axiom**: $0 (500MB/month free)
3. **Logtail**: $0 (1GB/month free)
4. **Datadog**: $0 (5 hosts free for students)

### Paid Options (When Scaling)
1. **Datadog Full**: ~$15/host/month
2. **New Relic**: ~$25/user/month
3. **Splunk**: ~$150/GB/month
4. **Custom ELK Stack**: ~$50/month (small instance)

## Implementation Priority

### Week 1: Foundation
1. Database logging table
2. MonitoringService class
3. Milvus fallback tracking
4. Basic admin API endpoint

### Week 2: Integration
1. Update all agents with monitoring
2. Add reranking metrics
3. Security event tracking
4. Performance metrics

### Week 3: Visualization
1. Admin dashboard UI
2. Alert system
3. Export functionality
4. Documentation

## Success Criteria

1. **100% Visibility**: Every Milvus fallback is logged
2. **<5min Detection**: Problems identified within 5 minutes
3. **Root Cause Analysis**: Can identify why agents fail
4. **Performance Tracking**: Know exactly how fast/slow we are
5. **Proactive Alerts**: Get notified before users complain

## Conclusion

Start with PostgreSQL logging (immediate, free, uses existing infrastructure), then gradually add specialized tools as the system grows. The key is to have SOMETHING in place now rather than flying blind in production.