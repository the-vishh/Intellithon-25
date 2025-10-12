#!/bin/bash
# Simple PostgreSQL Database Setup - With Password Prompt
# This version asks for your postgres password

PSQL="/c/Program Files/PostgreSQL/17/bin/psql.exe"

echo "========================================"
echo "PhishGuard Database Setup"
echo "========================================"
echo ""
echo "This will create the PhishGuard database."
echo ""
echo "If you don't remember your PostgreSQL password,"
echo "run: ./reset_postgres_password.sh (as Administrator)"
echo ""
echo "========================================"
echo ""

# Try common passwords first
echo "Trying common default passwords..."
for PASS in "postgres" "" "admin" "root" "postgres123" "password"; do
    export PGPASSWORD="$PASS"
    "$PSQL" -U postgres -c "SELECT 1;" > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "✅ Connected with password: '$PASS'"
        echo ""
        echo "Creating database..."
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
            echo "Your postgres password is: $PASS"
            echo ""
        fi
        unset PGPASSWORD
        exit 0
    fi
done

unset PGPASSWORD

echo "❌ Could not connect with common passwords"
echo ""
echo "Please enter your PostgreSQL 'postgres' password:"
echo "(or press Ctrl+C to cancel and run ./reset_postgres_password.sh)"
echo ""
read -s PGPASSWORD
export PGPASSWORD

echo ""
echo "Connecting to PostgreSQL..."
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
else
    echo ""
    echo "========================================"
    echo "❌ ERROR: Could not create database"
    echo "========================================"
    echo ""
    echo "Wrong password? Try:"
    echo "1. Run as Administrator: ./reset_postgres_password.sh"
    echo "2. Or manually reset in pgAdmin"
    echo ""
fi

unset PGPASSWORD
