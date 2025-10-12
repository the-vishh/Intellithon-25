#!/bin/bash
# Quick Start Script for PhishGuard Testing

echo "🚀 PhishGuard - Quick Start Script"
echo "====================================="
echo ""

# Step 1: Check PostgreSQL
echo "📊 Step 1: Checking PostgreSQL..."
if command -v psql &> /dev/null; then
    echo "✅ PostgreSQL is installed"

    # Setup database
    echo "🔧 Setting up database..."
    psql -U postgres -f setup_database.sql

    if [ $? -eq 0 ]; then
        echo "✅ Database created successfully"
    else
        echo "⚠️  Database setup failed. You may need to enter PostgreSQL password."
        echo "   Manual setup: psql -U postgres -f setup_database.sql"
    fi
else
    echo "⚠️  PostgreSQL not found. Install it or skip database features."
fi

echo ""

# Step 2: Configure backend
echo "📝 Step 2: Configuring backend..."
cd backend
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env file"
else
    echo "✅ .env file already exists"
fi

echo ""

# Step 3: Run migrations
echo "📊 Step 3: Running database migrations..."
psql -U phishguard_user -d phishguard -f migrations/2025-10-10-000001_create_user_analytics/up.sql 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Migrations applied successfully"
else
    echo "⚠️  Migrations failed (run manually if needed)"
fi

echo ""

# Step 4: Check Redis
echo "🔄 Step 4: Checking Redis..."
redis-cli ping &> /dev/null
if [ $? -eq 0 ]; then
    echo "✅ Redis is running"
else
    echo "⚠️  Redis not running. Start it with: redis-server"
fi

echo ""

# Step 5: Build backend
echo "🔨 Step 5: Building Rust API..."
echo "   (This may take 2-3 minutes...)"
cargo build --release

if [ $? -eq 0 ]; then
    echo "✅ Backend compiled successfully"
else
    echo "❌ Build failed"
    exit 1
fi

echo ""
echo "========================================="
echo "✅ Setup Complete!"
echo ""
echo "🚀 Next Steps:"
echo "   1. Start API:  cd backend && cargo run --release"
echo "   2. Load extension in Chrome (chrome://extensions/)"
echo "   3. Test by visiting websites"
echo ""
echo "📖 Full guide: See MANUAL_TESTING_GUIDE.md"
echo "========================================="
