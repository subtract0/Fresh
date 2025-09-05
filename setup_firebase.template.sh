#!/bin/bash
# Firebase Environment Setup Template for Fresh AI
# Copy this file to setup_firebase.sh and fill in your actual credentials

echo "Setting up Firebase environment for Fresh AI..."

# ==========================================
# REPLACE THESE WITH YOUR ACTUAL VALUES
# ==========================================

export FIREBASE_PROJECT_ID="your-firebase-project-id"
export FIREBASE_CLIENT_EMAIL="your-service-account@your-project.iam.gserviceaccount.com"
export FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----
YOUR_ACTUAL_PRIVATE_KEY_CONTENT_HERE
-----END PRIVATE KEY-----"

# Alternative: Set path to your credentials JSON file
# export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/firebase-service-account.json"

# ==========================================
# VALIDATION AND STATUS
# ==========================================

if [ "$FIREBASE_PROJECT_ID" = "your-firebase-project-id" ]; then
    echo "⚠️  WARNING: You need to replace template values with your actual Firebase credentials!"
    echo ""
    echo "📋 Setup Steps:"
    echo "1. Copy this file: cp setup_firebase.template.sh setup_firebase.sh"
    echo "2. Edit setup_firebase.sh with your Firebase project credentials"
    echo "3. Run: source ./setup_firebase.sh"
    echo ""
    echo "📚 See docs/FIREBASE_INTEGRATION.md for detailed setup instructions"
    exit 1
fi

echo "✅ Firebase environment variables set!"
echo "🔑 Project ID: $FIREBASE_PROJECT_ID"
echo "📧 Client Email: $FIREBASE_CLIENT_EMAIL"
echo "🔐 Private Key: $(if [ -n "$FIREBASE_PRIVATE_KEY" ]; then echo 'Set'; else echo 'Not set'; fi)"
echo ""
echo "🚀 You can now run Fresh CLI with persistent memory:"
echo "  poetry run python -m ai.cli.fresh --use-firestore spawn 'your task'"
echo "  poetry run python -m ai.cli.fresh orchestrate 'complex multi-agent task'"
echo ""
echo "🔍 To verify Firebase connection:"
echo "  poetry run python -c \"from ai.memory.firestore_store import FirestoreMemoryStore; store = FirestoreMemoryStore(); print('✅ Firebase connected successfully!')\""
