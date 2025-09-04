#!/usr/bin/env bash
set -euo pipefail

# Setup Firestore emulator for local development
echo "🔥 Setting up Firestore emulator for Fresh development..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is required but not installed."
    echo "Please install Docker Desktop from https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is required but not installed."
    echo "Installing via pip..."
    pip install docker-compose
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi

# Navigate to project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
cd "$PROJECT_ROOT"

# Stop any existing containers
echo "📦 Stopping existing containers..."
docker-compose down 2>/dev/null || true

# Start Firestore emulator
echo "🚀 Starting Firestore emulator..."
docker-compose up -d firestore

# Wait for emulator to be ready
echo "⏳ Waiting for Firestore emulator to be ready..."
MAX_ATTEMPTS=30
ATTEMPT=0
while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    if curl -f http://localhost:8080 &> /dev/null; then
        echo "✅ Firestore emulator is ready!"
        break
    fi
    ATTEMPT=$((ATTEMPT + 1))
    sleep 1
done

if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
    echo "❌ Firestore emulator failed to start. Check docker logs:"
    docker-compose logs firestore
    exit 1
fi

# Create .env.local if it doesn't exist
if [ ! -f .env.local ]; then
    echo "📝 Creating .env.local with Firestore emulator settings..."
    cat > .env.local << EOF
# Firestore Emulator Settings (Local Development)
FIRESTORE_EMULATOR_HOST=localhost:8080
FIREBASE_PROJECT_ID=fresh-local

# Optional: Use IntelligentMemoryStore instead of Firestore for development
# MEMORY_STORE_TYPE=intelligent

# Redis cache (optional, if using)
REDIS_URL=redis://localhost:6379
EOF
fi

# Show status
echo ""
echo "🎉 Firestore emulator setup complete!"
echo ""
echo "📊 Status:"
docker-compose ps

echo ""
echo "🌐 Firestore Emulator UI: http://localhost:4400"
echo ""
echo "📖 Usage:"
echo "  Start emulator:  docker-compose up -d firestore"
echo "  Stop emulator:   docker-compose down"
echo "  View logs:       docker-compose logs -f firestore"
echo ""
echo "🧪 Run tests with Firestore:"
echo "  export FIRESTORE_EMULATOR_HOST=localhost:8080"
echo "  poetry run pytest tests/integration/test_firestore_cross_session.py -v"
echo ""
echo "💡 Tip: Source .env.local in your shell to use emulator:"
echo "  source .env.local"
