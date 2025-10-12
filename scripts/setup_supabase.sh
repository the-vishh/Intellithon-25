#!/bin/bash
# Supabase Configuration Helper for PhishGuard

echo "========================================"
echo "PhishGuard - Supabase Setup Helper"
echo "========================================"
echo ""
echo "This script will help you configure Supabase"
echo ""

# Check if .env exists
if [ ! -f "backend/.env" ]; then
    echo "❌ ERROR: backend/.env not found"
    exit 1
fi

echo "Step 1: Get your Supabase connection string"
echo ""
echo "1. Go to: https://supabase.com"
echo "2. Sign up / Sign in"
echo "3. Create new project (name: phishguard-db)"
echo "4. Go to: Settings → Database → Connection string → URI"
echo "5. Copy the connection string"
echo ""
echo "It should look like:"
echo "postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres"
echo ""
echo "========================================"
echo ""
echo "Paste your Supabase connection string here:"
read -r SUPABASE_URL

if [ -z "$SUPABASE_URL" ]; then
    echo "❌ No connection string provided"
    exit 1
fi

# Validate URL format
if [[ ! "$SUPABASE_URL" =~ ^postgresql:// ]]; then
    echo "❌ Invalid connection string format"
    echo "Should start with: postgresql://"
    exit 1
fi

if [[ ! "$SUPABASE_URL" =~ supabase\.co ]]; then
    echo "⚠️  Warning: This doesn't look like a Supabase URL"
    echo "Are you sure this is correct? (y/n)"
    read -r CONFIRM
    if [ "$CONFIRM" != "y" ]; then
        exit 1
    fi
fi

# Backup .env
echo ""
echo "Step 2: Backing up current .env..."
cp backend/.env backend/.env.backup
echo "✅ Backup created: backend/.env.backup"

# Update DATABASE_URL in .env
echo ""
echo "Step 3: Updating DATABASE_URL..."
sed -i "s|^DATABASE_URL=.*|DATABASE_URL=$SUPABASE_URL|" backend/.env
echo "✅ DATABASE_URL updated in backend/.env"

# Show updated config
echo ""
echo "========================================"
echo "Configuration Updated!"
echo "========================================"
echo ""
cat backend/.env
echo ""

# Test connection
echo "========================================"
echo "Step 4: Testing connection..."
echo ""

# Check if psql is available
if command -v psql &> /dev/null; then
    psql "$SUPABASE_URL" -c "SELECT version();" > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "✅ Connection successful!"
        echo ""
        echo "Next steps:"
        echo "1. Run migrations: ./run_supabase_migrations.sh"
        echo "2. Restart API"
        echo "3. Test complete system"
    else
        echo "❌ Connection failed"
        echo "Check your connection string and try again"
    fi
else
    echo "⚠️  psql not found - skipping connection test"
    echo "Assuming connection is OK"
    echo ""
    echo "Next steps:"
    echo "1. Run migrations via Supabase dashboard"
    echo "2. Restart API"
    echo "3. Test with: curl http://localhost:8080/health"
fi

echo ""
echo "========================================"
echo "Setup complete!"
echo "========================================"
