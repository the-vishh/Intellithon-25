#!/bin/bash
# PhishGuard Database Setup (Bash version)
# Run with: ./setup_db.sh

PSQL="/c/Program Files/PostgreSQL/17/bin/psql.exe"

echo "========================================"
echo "PhishGuard Database Setup"
echo "========================================"
echo ""
echo "Enter PostgreSQL 'postgres' user password:"
read -s PGPASSWORD
export PGPASSWORD

echo ""
echo "Creating database and user..."
"$PSQL" -U postgres -f setup_database.sql

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "✅ SUCCESS! Database created."
    echo "========================================"
    echo ""
    echo "Database: phishguard"
    echo "User: phishguard_user"
    echo "Password: phishguard123"
    echo ""
    echo "Next steps:"
    echo "1. Update backend/.env with DATABASE_URL"
    echo "2. Run migrations"
    echo "3. Restart API"
    echo ""
else
    echo ""
    echo "========================================"
    echo "❌ ERROR: Database setup failed"
    echo "========================================"
    echo ""
    echo "Check:"
    echo "- PostgreSQL password is correct"
    echo "- PostgreSQL service is running"
    echo "- Port 5432 is available"
    echo ""
fi

unset PGPASSWORD
