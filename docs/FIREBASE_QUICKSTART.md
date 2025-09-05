# Firebase Integration Quick Start

**Get Firebase Persistent Memory Working in 5 Minutes**

## 🚀 Quick Setup

### 1. Get Firebase Credentials

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create/select your project
3. Project Settings → Service Accounts → Generate new private key
4. Download the JSON file

### 2. Configure Fresh AI

Copy the template and fill in your values:

```bash
cd /Users/am/Code/Fresh
cp setup_firebase.template.sh setup_firebase.sh
# Edit setup_firebase.sh with your Firebase credentials
```

### 3. Load Environment & Test

```bash
# Load Firebase environment
source ./setup_firebase.sh

# Test Firebase connection
poetry run python -c "
from ai.memory.firestore_store import FirestoreMemoryStore
store = FirestoreMemoryStore()
print('✅ Firebase connected successfully!')
"

# Use persistent memory with Mother Agent
poetry run python -m ai.cli.fresh --use-firestore spawn "Create a hello world function" --output code
```

## ✅ Success Indicators

You should see:
```
🧠 Memory initialized: firestore (firestore_connected=True)
```

## 🔧 Alternative Methods

### Method 1: Environment Variables
```bash
export FIREBASE_PROJECT_ID="your-project-id"
export FIREBASE_CLIENT_EMAIL="your-service-account-email"
export FIREBASE_PRIVATE_KEY="your-private-key"
```

### Method 2: Credentials File
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/firebase-credentials.json"
```

## 🎯 Key Commands

```bash
# Basic agent with persistence
poetry run python -m ai.cli.fresh --use-firestore spawn "your task"

# Enhanced orchestration with persistence
poetry run python -m ai.cli.fresh orchestrate "complex multi-agent research"

# Autonomous development with persistence
poetry run python -m ai.cli.fresh --use-firestore run --once
```

## 📚 Full Documentation

See [Firebase Integration Guide](./FIREBASE_INTEGRATION.md) for complete setup and advanced features.

---

*Last updated: January 2025*
