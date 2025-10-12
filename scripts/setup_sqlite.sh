#!/bin/bash
# SQLite Database Setup for PhishGuard

echo "========================================"
echo "PhishGuard SQLite Database Setup"
echo "========================================"
echo ""

DB_FILE="backend/phishguard.db"
MIGRATION_FILE="backend/migrations/2025-10-10-000001_create_user_analytics/up_sqlite.sql"

# Check if migration file exists
if [ ! -f "$MIGRATION_FILE" ]; then
    echo "❌ ERROR: Migration file not found: $MIGRATION_FILE"
    exit 1
fi

# Check if sqlite3 is available
if ! command -v sqlite3 &> /dev/null; then
    echo "❌ ERROR: sqlite3 command not found"
    echo ""
    echo "Install SQLite3:"
    echo "  Windows: Download from https://www.sqlite.org/download.html"
    echo "  Or use: choco install sqlite"
    echo "  Or use: scoop install sqlite"
    echo ""
    echo "Alternatively, the Rust app will create the database automatically"
    echo "when it starts (using bundled SQLite)."
    echo ""
    read -p "Continue anyway? (y/n): " CONTINUE
    if [ "$CONTINUE" != "y" ]; then
        exit 1
    fi
fi

echo "Step 1: Creating SQLite database..."
echo ""

# Create backend directory if it doesn't exist
mkdir -p backend

# Check if database already exists
if [ -f "$DB_FILE" ]; then
    echo "⚠️  Database file already exists: $DB_FILE"
    echo ""
    read -p "Delete and recreate? (y/n): " RECREATE
    if [ "$RECREATE" = "y" ]; then
        rm "$DB_FILE"
        echo "✅ Old database deleted"
    else
        echo "Keeping existing database"
    fi
fi

echo ""
echo "Step 2: Running migrations..."
echo ""

# Run migrations
if command -v sqlite3 &> /dev/null; then
    sqlite3 "$DB_FILE" < "$MIGRATION_FILE"

    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Migrations completed successfully!"
    else
        echo ""
        echo "❌ ERROR: Migration failed"
        exit 1
    fi
else
    echo "⚠️  sqlite3 not available, skipping manual migration"
    echo "Database will be created when API starts"
fi

echo ""
echo "Step 3: Verifying database..."
echo ""

if [ -f "$DB_FILE" ]; then
    DB_SIZE=$(du -h "$DB_FILE" | cut -f1)
    echo "✅ Database file created: $DB_FILE ($DB_SIZE)"

    if command -v sqlite3 &> /dev/null; then
        echo ""
        echo "Tables created:"
        sqlite3 "$DB_FILE" ".tables"

        echo ""
        echo "Database info:"
        sqlite3 "$DB_FILE" "PRAGMA database_list;"
    fi
else
    echo "⚠️  Database file not created yet"
    echo "It will be created when the API starts"
fi

echo ""
echo "========================================"
echo "✅ SQLite Setup Complete!"
echo "========================================"
echo ""
echo "Database: $DB_FILE"
echo "Type: SQLite 3"
echo "Location: Local file (no server needed)"
echo ""
echo "Benefits:"
echo "  ✅ No password required"
echo "  ✅ No server setup"
echo "  ✅ Fast local access"
echo "  ✅ Single file backup"
echo "  ✅ Perfect for Chrome extension"
echo ""
echo "Next steps:"
echo "  1. Restart API: taskkill //F //IM phishing-detector-api.exe"
echo "  2. Start API: cd backend && cargo run --release &"
echo "  3. Test: curl http://localhost:8080/health"
echo ""
echo "To view data:"
echo "  sqlite3 $DB_FILE"
echo "  sqlite> SELECT * FROM user_threat_sources;"
echo "  sqlite> .quit"
echo ""
