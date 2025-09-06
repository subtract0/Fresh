# Firebase Integration Guide

**Firebase Persistent Memory for Fresh AI Agent System**

This guide covers the complete setup and usage of Firebase Firestore for persistent agent memory in the Fresh AI system.

## 🎯 Overview

Firebase integration provides:
- **Persistent Memory**: Agent memories survive restarts and deployments
- **Cross-Session Learning**: Agents remember context between sessions
- **Scalable Storage**: Google Cloud Firestore backend
- **Automatic Synchronization**: Local cache with cloud persistence
- **Memory Analytics**: Advanced memory querying and analysis

## 🔧 Prerequisites

- Google Cloud Project with Firestore enabled
- Firebase Admin SDK service account credentials
- Fresh AI system installed with Poetry

## 📋 Setup Process

### 1. Firebase Project Setup

1. **Create/Access Firebase Project**:
   - Go to [Firebase Console](https://console.firebase.google.com/)
   - Create a new project or use existing one
   - Enable Firestore Database

2. **Generate Service Account Credentials**:
   - Project Settings → Service Accounts
   - Generate new private key
   - Download the JSON credentials file

### 2. Credential Configuration

#### Option A: Environment Variables (Recommended)

Create a setup script or add to your `.env` file:

```bash
# Firebase Configuration
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@your-project.iam.gserviceaccount.com
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----
[Your Private Key Content]
-----END PRIVATE KEY-----"
```

#### Option B: Credentials File

```bash
# Set path to credentials JSON file
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/firebase-credentials.json
```

### 3. Fresh AI Configuration

The system automatically detects Firebase credentials and enables persistent memory when available.

## 🚀 Usage

### Basic Usage with CLI

```bash
# Enable Firebase persistent memory
poetry run python -m ai.cli.fresh --use-firestore spawn "your task" --output code

# Enhanced orchestration with persistence
poetry run python -m ai.cli.fresh orchestrate "complex research task"

# Run autonomous loop with persistent memory
poetry run python -m ai.cli.fresh --use-firestore run --once
```

### Programmatic Usage

```python
from ai.memory.store import get_store, set_memory_store
from ai.memory.firestore_store import FirestoreMemoryStore
from ai.agents.mother import MotherAgent

# Initialize Firestore memory
firestore_store = FirestoreMemoryStore()
set_memory_store(firestore_store)

# Create mother agent with persistent memory
mother = MotherAgent()

# Agent operations now use persistent memory
result = mother.run(
    name="test_agent",
    instructions="Create a hello world function",
    model="gpt-4o-mini",
    output_type="code"
)
```

## 🔍 Verification

Check that Firebase is working:

```python
from ai.memory.store import get_store

store = get_store()
print("Memory store type:", type(store).__name__)

# Should show: FirestoreMemoryStore
```

Successful connection shows:
```
🧠 Memory initialized: firestore (firestore_connected=True)
```

## 🎛️ Configuration Options

### FirestoreMemoryStore Parameters

```python
FirestoreMemoryStore(
    project_id=None,           # Auto-detected from environment
    collection_name="agent_memories",  # Firestore collection
    max_local_cache=100,       # Local cache size
    sync_on_write=True         # Immediate sync to cloud
)
```

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `FIREBASE_PROJECT_ID` | Google Cloud Project ID | Yes |
| `FIREBASE_CLIENT_EMAIL` | Service account email | Yes |
| `FIREBASE_PRIVATE_KEY` | Private key (with newlines) | Yes |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to JSON credentials | Alternative |
| `FIRESTORE_EMULATOR_HOST` | Emulator host for testing | No |

## 📊 Memory Management

### Memory Operations

```python
# Write memory with tags and classification
memory = store.write(
    content="Learned how to implement authentication",
    tags=["learning", "auth", "security"]
)

# Query memories by tags
auth_memories = store.query(
    tags=["auth"],
    limit=10
)

# Search by keywords (intelligent store)
search_results = store.search_by_keywords(
    ["authentication", "login"],
    limit=5
)
```

### Memory Types

The system supports various memory types:
- `CONTEXT`: General context information
- `GOAL`: Objectives and targets
- `TASK`: Specific tasks and outcomes
- `ERROR`: Error patterns and solutions
- `KNOWLEDGE`: Learned facts and procedures
- `PROGRESS`: Progress tracking

## 🔧 Advanced Features

### Memory Consolidation

```python
# Automatic cleanup of old, low-importance memories
from ai.tools.persistent_memory_tools import MemoryConsolidation

consolidator = MemoryConsolidation(
    days_back=30,
    min_importance=0.6,
    dry_run=False  # Set to True for testing
)
result = consolidator.run()
```

### Cross-Session Analytics

```python
from ai.tools.persistent_memory_tools import CrossSessionAnalytics

analytics = CrossSessionAnalytics(days_back=30)
report = analytics.run()
print(report)  # Detailed analytics report
```

## 🐛 Troubleshooting

### Common Issues

1. **"Firestore not available" Error**:
   ```
   pip install google-cloud-firestore
   ```

2. **Authentication Errors**:
   - Verify credentials are correctly set
   - Check project ID matches Firebase project
   - Ensure service account has Firestore permissions

3. **Connection Timeouts**:
   - Check network connectivity
   - Verify Firestore is enabled in project
   - Try using emulator for local development

### Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Fallback Behavior

If Firebase is unavailable, the system automatically falls back to:
1. IntelligentMemoryStore (local with semantic search)
2. InMemoryMemoryStore (basic local storage)

## 🔒 Security Best Practices

1. **Never commit credentials** to version control
2. **Use environment variables** or secure credential stores
3. **Restrict service account permissions** to Firestore only
4. **Use Firebase Security Rules** for additional protection
5. **Rotate credentials regularly**

### Example Security Rules

```javascript
// Firestore Security Rules
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Allow service account full access
    match /agent_memories/{document} {
      allow read, write: if request.auth != null;
    }
  }
}
```

## 📈 Performance Optimization

### Local Caching

- Local cache reduces Firestore read operations
- Configurable cache size (default: 100 items)
- LRU eviction policy for optimal memory usage

### Batch Operations

- Automatic batching for bulk memory operations
- Reduced API calls and improved performance
- Configurable batch sizes

### Index Optimization

The system creates indexes for:
- Memory tags (for filtering)
- Creation timestamps (for chronological queries)
- Memory types (for categorical searches)
- Keywords (for semantic search)

## 🔄 Migration and Backup

### Exporting Memories

```python
from ai.memory.firestore_store import FirestoreMemoryStore

store = FirestoreMemoryStore()
memories = store.query(limit=1000)  # Export all memories

import json
with open('memory_backup.json', 'w') as f:
    json.dump([asdict(mem) for mem in memories], f, default=str)
```

### Importing Memories

```python
with open('memory_backup.json', 'r') as f:
    memory_data = json.load(f)

for mem_dict in memory_data:
    store.write(
        content=mem_dict['content'],
        tags=mem_dict['tags']
    )
```

## 📚 Additional Resources

- [Firebase Documentation](https://firebase.google.com/docs)
- [Firestore Python SDK](https://firebase.google.com/docs/firestore/quickstart#python)
- [Google Cloud Authentication](https://cloud.google.com/docs/authentication)
- [Fresh AI Memory System](./MEMORY_SYSTEM.md)

## 🆘 Support

If you encounter issues:
1. Check the [troubleshooting section](#troubleshooting)
2. Review Firebase console for errors
3. Enable debug logging for detailed information
4. Verify credentials and permissions

---

*Last updated: January 2025*  
*Firebase Integration Status: ✅ Fully Implemented and Tested*
