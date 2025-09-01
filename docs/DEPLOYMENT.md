# Deployment and Operations Guide

Complete guide for deploying and operating the Fresh AI agent system with persistent memory capabilities. This guide covers environment setup, Firestore configuration, monitoring, and troubleshooting for production deployments.

## Table of Contents
- [Quick Start](#quick-start)
- [Environment Setup](#environment-setup)
- [Memory System Deployment](#memory-system-deployment)
- [Enhanced Agent Deployment](#enhanced-agent-deployment)
- [Production Configuration](#production-configuration)
- [Monitoring and Analytics](#monitoring-and-analytics)
- [Troubleshooting](#troubleshooting)
- [Cross-References](#cross-references)

---

## Quick Start

### Local Development Setup
```bash
# 1. Install dependencies
cd /path/to/Fresh
poetry install --no-root

# 2. Set up basic environment
export PYTHONPATH=/path/to/Fresh

# 3. Test memory system
PYTHONPATH=/path/to/Fresh poetry run python scripts/demo-persistent-memory.py

# 4. Test enhanced agents
PYTHONPATH=/path/to/Fresh poetry run python scripts/demo-agent-activity.py
```

### Production Deployment
```bash
# 1. Set up Firestore credentials
export FIREBASE_PROJECT_ID="your-project-id"
export FIREBASE_PRIVATE_KEY="your-private-key"
export FIREBASE_CLIENT_EMAIL="your-client-email"

# 2. Deploy with persistent memory
PYTHONPATH=/path/to/Fresh poetry run python -c "
from ai.agents.enhanced_agents import create_enhanced_agents
agents = create_enhanced_agents()
print(f'Deployed {len(agents)} enhanced agents with persistent memory')
"
```

---

## Environment Setup

### Development Environment

#### Required Dependencies
```toml
# pyproject.toml - Core dependencies
[tool.poetry.dependencies]
python = "^3.12"
pydantic = "^2.0"
pydantic-settings = "^2.0"

# Optional dependencies (installed as needed)
agency-swarm = {version = "^0.7.0", optional = true}
google-cloud-firestore = {version = "^2.21.0", optional = true}
```

#### Environment Variables
```bash
# Basic configuration
export PYTHONPATH=/path/to/Fresh

# Memory system configuration
export MEMORY_STORE_TYPE=intelligent  # Options: memory, intelligent, firestore

# Optional: Firestore configuration (for persistent memory)
export FIREBASE_PROJECT_ID=your-project-id
export FIREBASE_PRIVATE_KEY=your-private-key
export FIREBASE_CLIENT_EMAIL=your-client-email
export FIREBASE_CREDENTIALS_PATH=/path/to/service-account.json

# Optional: Agent configuration
export AGENT_TEMPERATURE=0.2
export MEMORY_CACHE_SIZE=100
export MEMORY_SYNC_INTERVAL=300
```

### Production Environment

#### Docker Configuration
```dockerfile
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev --no-root

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV MEMORY_STORE_TYPE=firestore

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from ai.memory.store import get_store; store = get_store(); print('Healthy')"

# Run application
CMD ["python", "-m", "ai.agents.enhanced_agents"]
```

#### Docker Compose
```yaml
version: '3.8'
services:
  fresh-agents:
    build: .
    environment:
      - PYTHONPATH=/app
      - MEMORY_STORE_TYPE=firestore
      - FIREBASE_PROJECT_ID=${FIREBASE_PROJECT_ID}
      - FIREBASE_PRIVATE_KEY=${FIREBASE_PRIVATE_KEY}
      - FIREBASE_CLIENT_EMAIL=${FIREBASE_CLIENT_EMAIL}
    volumes:
      - ./data:/app/data
    healthcheck:
      test: ["CMD", "python", "-c", "from ai.memory.store import get_store; get_store()"]
      interval: 30s
      timeout: 10s
      retries: 3
```

---

## Memory System Deployment

### Memory Store Selection

#### Automatic Selection
```python
# Automatic selection based on environment
from ai.memory.store import get_store

store = get_store()  # Selects best available store
print(f"Selected store: {type(store).__name__}")
```

The system automatically selects the best available memory store:
1. **FirestoreMemoryStore** - If Firestore credentials are available
2. **IntelligentMemoryStore** - If Firestore is not available but intelligence is needed
3. **InMemoryMemoryStore** - Basic fallback for development

#### Explicit Selection
```python
# Force specific store type
from ai.memory.store import get_store

# Force Firestore (fails if not available)
firestore_store = get_store("firestore")

# Force intelligent store (no persistence)
intelligent_store = get_store("intelligent")

# Force basic store (minimal features)
basic_store = get_store("memory")
```

### Firestore Configuration

#### Service Account Setup
1. **Create Service Account** in Google Cloud Console
2. **Download JSON key** file
3. **Set environment variables**:

```bash
# Option 1: JSON file path
export FIREBASE_CREDENTIALS_PATH=/path/to/service-account.json

# Option 2: Individual variables
export FIREBASE_PROJECT_ID=your-project-id
export FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n..."
export FIREBASE_CLIENT_EMAIL=service-account@project.iam.gserviceaccount.com
```

#### Firestore Database Setup
```python
# Initialize Firestore with proper configuration
from ai.memory.firestore_store import FirestoreMemoryStore

store = FirestoreMemoryStore(
    max_cache_size=100,        # Local cache limit
    sync_interval=300,         # 5 minutes auto-sync
    collection_name="memories" # Firestore collection name
)

# Test connection
try:
    test_memory = store.write("Test connection", tags=["test"])
    print(f"Firestore connected: {test_memory.id}")
    store.delete(test_memory.id)  # Clean up
except Exception as e:
    print(f"Firestore connection failed: {e}")
```

#### Firestore Security Rules
```javascript
// Firestore security rules for agent memories
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Memories collection - restrict to service account
    match /memories/{memory} {
      allow read, write: if request.auth != null && 
        request.auth.token.email == "your-service-account@project.iam.gserviceaccount.com";
    }
    
    // Memory analytics - allow read for monitoring
    match /analytics/{analytic} {
      allow read: if request.auth != null;
      allow write: if request.auth != null && 
        request.auth.token.email == "your-service-account@project.iam.gserviceaccount.com";
    }
  }
}
```

### Memory Store Configuration

#### Local Cache Management
```python
# Configure intelligent caching
from ai.memory.firestore_store import FirestoreMemoryStore

store = FirestoreMemoryStore(
    max_cache_size=200,      # Increase for high-volume usage
    sync_interval=180,       # More frequent sync for active development
    auto_consolidate=True,   # Enable automatic cleanup
    consolidation_interval=3600  # Consolidate every hour
)
```

#### Memory Consolidation Strategy
```python
# Configure automatic memory cleanup
consolidation_config = {
    "enabled": True,
    "schedule": "0 2 * * *",  # Daily at 2 AM
    "days_back": 14,          # Consider memories older than 14 days
    "min_importance": 0.4,    # Keep memories with importance >= 0.4
    "max_memories": 10000,    # Maximum total memories to keep
}
```

---

## Enhanced Agent Deployment

### Agent Selection and Configuration

#### Production Agent Deployment
```python
# Deploy enhanced agents with full memory capabilities
from ai.agents.enhanced_agents import create_enhanced_agents

# Create all enhanced agents
agents = create_enhanced_agents()

# Verify memory capabilities
for name, agent in agents.items():
    memory_tools = [tool for tool in agent.tools if 'Memory' in tool.__name__]
    print(f"{name}: {len(memory_tools)} memory tools")
```

#### Gradual Migration Strategy
```python
# Gradual migration from standard to enhanced agents
from ai.agents.enhanced_agents import get_agent

deployment_config = {
    'Father': {'enhanced': True, 'ready': True},
    'Architect': {'enhanced': True, 'ready': True}, 
    'Developer': {'enhanced': True, 'ready': True},
    'QA': {'enhanced': False, 'ready': False}  # Migrate later
}

agents = {}
for name, config in deployment_config.items():
    agents[name] = get_agent(name, enhanced=config['enhanced'])
    if config['enhanced']:
        print(f"✅ {name} deployed with enhanced memory")
    else:
        print(f"⏳ {name} using standard configuration")
```

### Agent Configuration Management

#### Environment-Based Configuration
```python
import os
from ai.agents.enhanced_agents import create_enhanced_agents

# Environment-specific agent configuration
env = os.getenv('ENVIRONMENT', 'development')

if env == 'production':
    # Full enhanced agents with Firestore
    agents = create_enhanced_agents()
    memory_config = {
        'store_type': 'firestore',
        'cache_size': 200,
        'sync_interval': 300
    }
elif env == 'staging':
    # Enhanced agents with local intelligent memory
    agents = create_enhanced_agents()
    memory_config = {
        'store_type': 'intelligent',
        'cache_size': 100,
        'sync_interval': None
    }
else:
    # Development with basic memory
    from ai.agents.enhanced_agents import get_agent
    agents = {
        name: get_agent(name, enhanced=False)
        for name in ['Father', 'Architect', 'Developer', 'QA']
    }
    memory_config = {'store_type': 'memory'}
```

#### Agent Monitoring Integration
```python
# Monitor agent memory usage and performance
from ai.monitor.activity import record_memory_operation
from ai.tools.persistent_memory_tools import CrossSessionAnalytics

def monitor_agent_activity():
    # Get memory usage statistics
    analytics = CrossSessionAnalytics(days_back=1)
    stats = analytics.run()
    
    # Record monitoring metrics
    record_memory_operation("analytics")
    
    return {
        'timestamp': datetime.now().isoformat(),
        'memory_stats': stats,
        'agent_status': 'healthy'
    }
```

---

## Production Configuration

### High Availability Setup

#### Load Balancing Configuration
```yaml
# nginx.conf for agent load balancing
upstream fresh_agents {
    server fresh-agent-1:8000;
    server fresh-agent-2:8000;
    server fresh-agent-3:8000;
}

server {
    listen 80;
    server_name agents.example.com;
    
    location / {
        proxy_pass http://fresh_agents;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_timeout 300s;
    }
    
    location /health {
        proxy_pass http://fresh_agents/health;
        access_log off;
    }
}
```

#### Database Connection Pooling
```python
# Firestore connection pooling for high availability
from ai.memory.firestore_store import FirestoreMemoryStore
import threading

class PooledFirestoreStore:
    def __init__(self, pool_size=10):
        self.pool = [
            FirestoreMemoryStore(
                max_cache_size=50,  # Smaller cache per instance
                sync_interval=600   # Less frequent sync
            )
            for _ in range(pool_size)
        ]
        self.current = 0
        self.lock = threading.Lock()
    
    def get_store(self):
        with self.lock:
            store = self.pool[self.current]
            self.current = (self.current + 1) % len(self.pool)
            return store
```

### Security Configuration

#### Environment Variable Security
```bash
# Use secrets management for sensitive variables
export FIREBASE_PRIVATE_KEY=$(vault kv get -field=private_key secret/firebase)
export FIREBASE_CLIENT_EMAIL=$(vault kv get -field=client_email secret/firebase)

# Or use Kubernetes secrets
kubectl create secret generic firebase-credentials \
  --from-literal=project-id=your-project-id \
  --from-literal=private-key=your-private-key \
  --from-literal=client-email=your-client-email
```

#### Network Security
```yaml
# Kubernetes NetworkPolicy for agent security
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: fresh-agents-policy
spec:
  podSelector:
    matchLabels:
      app: fresh-agents
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: fresh-api
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to: []  # Allow all egress for Firestore access
    ports:
    - protocol: TCP
      port: 443
```

### Performance Optimization

#### Memory Store Performance Tuning
```python
# Production-optimized memory store configuration
production_config = {
    "firestore": {
        "max_cache_size": 500,      # Large cache for better performance
        "sync_interval": 900,       # 15-minute sync for stability
        "batch_size": 50,           # Batch operations for efficiency
        "timeout": 30,              # Connection timeout
        "retry_attempts": 3         # Retry failed operations
    },
    "intelligent": {
        "max_keywords": 20,         # Limit keyword extraction
        "importance_threshold": 0.3, # Skip low-importance processing
        "relationship_limit": 10    # Limit relationship computation
    }
}
```

#### Agent Performance Monitoring
```python
# Performance monitoring for production agents
import time
import psutil
from ai.monitor.activity import record_memory_operation

class AgentPerformanceMonitor:
    def __init__(self):
        self.start_time = time.time()
        self.memory_ops = 0
    
    def monitor_operation(self, operation_name):
        start = time.time()
        
        def decorator(func):
            def wrapper(*args, **kwargs):
                result = func(*args, **kwargs)
                duration = time.time() - start
                
                # Record performance metrics
                record_memory_operation(operation_name)
                self.log_performance(operation_name, duration)
                
                return result
            return wrapper
        return decorator
    
    def log_performance(self, operation, duration):
        cpu_percent = psutil.cpu_percent()
        memory_percent = psutil.virtual_memory().percent
        
        metrics = {
            'operation': operation,
            'duration': duration,
            'cpu_usage': cpu_percent,
            'memory_usage': memory_percent,
            'timestamp': time.time()
        }
        
        # Log to monitoring system
        print(f"Performance: {operation} took {duration:.2f}s")
```

---

## Monitoring and Analytics

### Health Checks

#### System Health Monitoring
```python
# Comprehensive health check endpoint
from ai.memory.store import get_store
from ai.agents.enhanced_agents import create_enhanced_agents

def health_check():
    try:
        # Test memory store
        store = get_store()
        test_memory = store.write("Health check", tags=["health"])
        store.delete(test_memory.id)
        
        # Test enhanced agents
        agents = create_enhanced_agents()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "memory_store": type(store).__name__,
            "agents": list(agents.keys()),
            "checks": {
                "memory_write": "ok",
                "agent_creation": "ok"
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "checks": {
                "memory_write": "failed",
                "agent_creation": "failed"
            }
        }
```

#### Memory System Health
```python
# Memory-specific health monitoring
from ai.tools.persistent_memory_tools import CrossSessionAnalytics

def memory_health_check():
    try:
        store = get_store()
        
        # Basic connectivity
        test_memory = store.write("Health test", tags=["health"])
        retrieved = store.read(test_memory.id)
        store.delete(test_memory.id)
        
        # Analytics health (if available)
        health_status = {
            "store_type": type(store).__name__,
            "connectivity": "ok",
            "read_write": "ok"
        }
        
        if hasattr(store, 'get_memory_stats'):
            stats = store.get_memory_stats()
            health_status["cache_size"] = stats.get('local_cache_size', 0)
            health_status["firestore_connected"] = stats.get('firestore_connected', False)
        
        return health_status
        
    except Exception as e:
        return {
            "store_type": "unknown",
            "connectivity": "failed",
            "error": str(e)
        }
```

### Performance Metrics

#### Memory Usage Analytics
```python
# Monitor memory system performance
from ai.tools.persistent_memory_tools import CrossSessionAnalytics

def collect_memory_metrics():
    analytics = CrossSessionAnalytics(days_back=1)
    daily_stats = analytics.run()
    
    # Parse metrics from analytics
    metrics = {
        "total_memories": 0,
        "memory_types": {},
        "average_importance": 0.0,
        "recent_activity": 0,
        "top_keywords": {}
    }
    
    # Extract from analytics string (would be JSON in production)
    if "Total Memories:" in daily_stats:
        # Parse metrics from analytics output
        pass
    
    return metrics
```

#### Agent Performance Tracking
```python
# Track agent performance over time
class AgentMetrics:
    def __init__(self):
        self.operation_counts = {}
        self.operation_durations = {}
        self.error_counts = {}
    
    def record_operation(self, agent_name, operation, duration, success=True):
        key = f"{agent_name}_{operation}"
        
        if key not in self.operation_counts:
            self.operation_counts[key] = 0
            self.operation_durations[key] = []
            self.error_counts[key] = 0
        
        self.operation_counts[key] += 1
        self.operation_durations[key].append(duration)
        
        if not success:
            self.error_counts[key] += 1
    
    def get_metrics(self):
        metrics = {}
        for key in self.operation_counts:
            agent_op = key
            metrics[agent_op] = {
                "count": self.operation_counts[key],
                "avg_duration": sum(self.operation_durations[key]) / len(self.operation_durations[key]),
                "error_rate": self.error_counts[key] / self.operation_counts[key]
            }
        return metrics
```

### Logging and Observability

#### Structured Logging
```python
import logging
import json
from datetime import datetime

# Configure structured logging for production
class StructuredLogger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(handler)
    
    def log_memory_operation(self, operation, agent, duration=None, success=True, **kwargs):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": "INFO" if success else "ERROR",
            "operation": operation,
            "agent": agent,
            "duration": duration,
            "success": success,
            **kwargs
        }
        
        self.logger.info(json.dumps(log_entry))
    
    def log_agent_activity(self, agent_name, action, context=None):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": "INFO",
            "type": "agent_activity",
            "agent": agent_name,
            "action": action,
            "context": context
        }
        
        self.logger.info(json.dumps(log_entry))
```

---

## Troubleshooting

### Common Issues

#### Memory Store Connection Issues

**Problem**: Firestore connection failures
```
FirestoreConnectionError: Could not connect to Firestore
```

**Solutions**:
1. **Check credentials**:
```bash
# Verify environment variables
echo $FIREBASE_PROJECT_ID
echo $FIREBASE_CLIENT_EMAIL
echo ${FIREBASE_PRIVATE_KEY:0:50}...  # First 50 chars only
```

2. **Test connectivity**:
```python
from google.cloud import firestore

try:
    db = firestore.Client()
    collections = list(db.collections())
    print(f"Firestore connected: {len(collections)} collections")
except Exception as e:
    print(f"Firestore error: {e}")
```

3. **Fallback to intelligent store**:
```python
# Graceful degradation
from ai.memory.store import get_store

try:
    store = get_store("firestore")
except:
    print("Firestore unavailable, falling back to intelligent store")
    store = get_store("intelligent")
```

#### Agent Creation Failures

**Problem**: Enhanced agents fail to create
```
ImportError: No module named 'agency_swarm'
```

**Solutions**:
1. **Check optional dependencies**:
```bash
poetry install --extras agency_swarm
# or
pip install agency-swarm
```

2. **Verify fallback behavior**:
```python
from ai.agents.enhanced_agents import create_enhanced_agents, MEMORY_TOOLS_AVAILABLE

print(f"Memory tools available: {MEMORY_TOOLS_AVAILABLE}")
agents = create_enhanced_agents()
print(f"Created {len(agents)} agents")
```

3. **Use graceful degradation**:
```python
try:
    from ai.agents.enhanced_agents import create_enhanced_agents
    agents = create_enhanced_agents()
except ImportError:
    print("Using dummy agents for testing")
    agents = {"Father": None, "Architect": None, "Developer": None, "QA": None}
```

#### Memory Performance Issues

**Problem**: Slow memory operations
```
Memory search taking >5 seconds
```

**Solutions**:
1. **Optimize cache size**:
```python
from ai.memory.firestore_store import FirestoreMemoryStore

# Increase cache for better performance
store = FirestoreMemoryStore(
    max_cache_size=500,  # Increase cache
    sync_interval=900    # Less frequent sync
)
```

2. **Implement connection pooling**:
```python
# Use multiple store instances
stores = [FirestoreMemoryStore() for _ in range(5)]
current_store = 0

def get_pooled_store():
    global current_store
    store = stores[current_store]
    current_store = (current_store + 1) % len(stores)
    return store
```

3. **Monitor and profile**:
```python
import time
from ai.tools.enhanced_memory_tools import SemanticSearchMemory

start = time.time()
search = SemanticSearchMemory(keywords=["test"], limit=10)
result = search.run()
duration = time.time() - start

if duration > 5.0:
    print(f"Slow search detected: {duration:.2f}s")
    # Implement optimizations
```

### Debugging Tools

#### Memory System Diagnostics
```python
# Comprehensive memory system diagnostics
def diagnose_memory_system():
    from ai.memory.store import get_store
    from ai.tools.persistent_memory_tools import CrossSessionAnalytics
    
    print("=== Memory System Diagnostics ===")
    
    # Store information
    store = get_store()
    print(f"Store type: {type(store).__name__}")
    
    # Test basic operations
    try:
        test_memory = store.write("Diagnostic test", tags=["diagnostic"])
        print(f"✅ Write operation: {test_memory.id}")
        
        retrieved = store.read(test_memory.id)
        print(f"✅ Read operation: {retrieved.content}")
        
        store.delete(test_memory.id)
        print("✅ Delete operation successful")
        
    except Exception as e:
        print(f"❌ Basic operations failed: {e}")
    
    # Analytics (if available)
    try:
        analytics = CrossSessionAnalytics(days_back=1)
        stats = analytics.run()
        print("✅ Analytics available")
    except Exception as e:
        print(f"⚠️  Analytics unavailable: {e}")
    
    # Store-specific diagnostics
    if hasattr(store, 'get_memory_stats'):
        try:
            stats = store.get_memory_stats()
            print(f"Cache size: {stats.get('local_cache_size', 'unknown')}")
            print(f"Firestore connected: {stats.get('firestore_connected', 'unknown')}")
        except Exception as e:
            print(f"⚠️  Store stats unavailable: {e}")
```

#### Agent System Diagnostics
```python
# Agent system diagnostics
def diagnose_agent_system():
    from ai.agents.enhanced_agents import create_enhanced_agents, MEMORY_TOOLS_AVAILABLE
    
    print("=== Agent System Diagnostics ===")
    print(f"Memory tools available: {MEMORY_TOOLS_AVAILABLE}")
    
    try:
        agents = create_enhanced_agents()
        print(f"✅ Created {len(agents)} enhanced agents")
        
        for name, agent in agents.items():
            memory_tools = [tool for tool in agent.tools if 'Memory' in tool.__name__]
            print(f"  {name}: {len(memory_tools)} memory tools")
            
    except Exception as e:
        print(f"❌ Agent creation failed: {e}")
        
    # Test tool functionality
    try:
        from ai.tools.enhanced_memory_tools import SmartWriteMemory
        tool = SmartWriteMemory(content="Diagnostic test", tags=["test"])
        result = tool.run()
        print(f"✅ Tool execution: {result}")
    except Exception as e:
        print(f"❌ Tool execution failed: {e}")
```

### Performance Optimization

#### Memory Store Optimization
```python
# Optimize memory store for production workloads
def optimize_memory_store():
    import os
    from ai.memory.firestore_store import FirestoreMemoryStore
    
    # Production configuration
    config = {
        "max_cache_size": int(os.getenv("MEMORY_CACHE_SIZE", "500")),
        "sync_interval": int(os.getenv("MEMORY_SYNC_INTERVAL", "900")),
        "batch_size": int(os.getenv("MEMORY_BATCH_SIZE", "50")),
        "connection_timeout": int(os.getenv("FIRESTORE_TIMEOUT", "30"))
    }
    
    return FirestoreMemoryStore(**config)
```

#### Agent Performance Tuning
```python
# Tune agent performance for production
def tune_agent_performance():
    import os
    
    # Environment-based performance tuning
    environment = os.getenv("ENVIRONMENT", "development")
    
    if environment == "production":
        return {
            "temperature": 0.1,        # More deterministic
            "memory_limit": 1000,      # Higher memory limit
            "cache_ttl": 3600,         # Longer cache TTL
            "batch_operations": True   # Enable batching
        }
    elif environment == "staging":
        return {
            "temperature": 0.2,
            "memory_limit": 500,
            "cache_ttl": 1800,
            "batch_operations": False
        }
    else:
        return {
            "temperature": 0.3,
            "memory_limit": 100,
            "cache_ttl": 300,
            "batch_operations": False
        }
```

---

## Cross-References

### Core Documentation
- [Memory System Architecture](./MEMORY_SYSTEM.md) - Complete memory system overview
- [Enhanced Agent Architecture](./ENHANCED_AGENTS.md) - Enhanced agent capabilities and workflows
- [API Reference](./API_REFERENCE.md) - Comprehensive API documentation
- [Agent Development Guide](./AGENT_DEVELOPMENT.md) - Development best practices

### Implementation Files
- [`ai/memory/store.py`](../ai/memory/store.py) - Memory store factory and interfaces
- [`ai/memory/firestore_store.py`](../ai/memory/firestore_store.py) - Firestore implementation
- [`ai/agents/enhanced_agents.py`](../ai/agents/enhanced_agents.py) - Enhanced agent implementations

### Configuration and Setup
- [ADR-004: Persistent Agent Memory](../.cursor/rules/ADR-004.md) - Architecture decision record
- [`scripts/demo-persistent-memory.py`](../scripts/demo-persistent-memory.py) - Memory system demonstration
- [`scripts/demo-agent-activity.py`](../scripts/demo-agent-activity.py) - Agent activity simulation

### Testing and Validation
- [`tests/test_intelligent_memory.py`](../tests/test_intelligent_memory.py) - Intelligent memory tests
- [`tests/test_firestore_memory.py`](../tests/test_firestore_memory.py) - Firestore memory tests

---

*This deployment guide provides comprehensive coverage for deploying and operating Fresh AI agents with persistent memory in development, staging, and production environments. The system is designed for high availability, security, and performance optimization.*
