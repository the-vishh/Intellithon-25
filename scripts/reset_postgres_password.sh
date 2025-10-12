#!/bin/bash
# PostgreSQL Password Reset Script
# This script helps reset the postgres user password

echo "========================================"
echo "PostgreSQL Password Reset Utility"
echo "========================================"
echo ""

PG_DATA="/c/Program Files/PostgreSQL/17/data"
PG_HBA="$PG_DATA/pg_hba.conf"
PG_HBA_BACKUP="$PG_DATA/pg_hba.conf.backup"
PSQL="/c/Program Files/PostgreSQL/17/bin/psql.exe"

# Check if running as admin
echo "Step 1: Checking permissions..."
if [ ! -w "$PG_HBA" ]; then
    echo "❌ ERROR: Need administrator privileges!"
    echo ""
    echo "Please run this script as Administrator:"
    echo "1. Right-click Git Bash"
    echo "2. Select 'Run as Administrator'"
    echo "3. Run: ./reset_postgres_password.sh"
    exit 1
fi

echo "✅ Administrator access confirmed"
echo ""

# Backup pg_hba.conf
echo "Step 2: Backing up pg_hba.conf..."
cp "$PG_HBA" "$PG_HBA_BACKUP"
if [ $? -eq 0 ]; then
    echo "✅ Backup created: pg_hba.conf.backup"
else
    echo "❌ ERROR: Could not create backup"
    exit 1
fi
echo ""

# Modify pg_hba.conf to trust
echo "Step 3: Temporarily disabling password authentication..."
sed -i 's/scram-sha-256/trust/g' "$PG_HBA"
sed -i 's/md5/trust/g' "$PG_HBA"
echo "✅ Authentication set to 'trust' (temporary)"
echo ""

# Restart PostgreSQL
echo "Step 4: Restarting PostgreSQL service..."
sc stop postgresql-x64-17 > /dev/null 2>&1
sleep 3
sc start postgresql-x64-17 > /dev/null 2>&1
sleep 3
echo "✅ PostgreSQL restarted"
echo ""

# Prompt for new password
echo "Step 5: Set new password for 'postgres' user"
echo ""
echo "Enter your new password (or press Enter for 'postgres123'):"
read -s NEW_PASSWORD
if [ -z "$NEW_PASSWORD" ]; then
    NEW_PASSWORD="postgres123"
fi
echo ""

# Reset password
echo "Step 6: Updating password..."
"$PSQL" -U postgres -c "ALTER USER postgres WITH PASSWORD '$NEW_PASSWORD';" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Password updated successfully!"
else
    echo "❌ ERROR: Could not update password"
    echo "Restoring backup..."
    cp "$PG_HBA_BACKUP" "$PG_HBA"
    sc stop postgresql-x64-17 > /dev/null 2>&1
    sleep 2
    sc start postgresql-x64-17 > /dev/null 2>&1
    exit 1
fi
echo ""

# Restore security
echo "Step 7: Restoring password authentication..."
cp "$PG_HBA_BACKUP" "$PG_HBA"
echo "✅ Security settings restored"
echo ""

# Restart PostgreSQL again
echo "Step 8: Final restart..."
sc stop postgresql-x64-17 > /dev/null 2>&1
sleep 3
sc start postgresql-x64-17 > /dev/null 2>&1
sleep 3
echo "✅ PostgreSQL restarted with new settings"
echo ""

# Test connection
echo "Step 9: Testing new password..."
export PGPASSWORD="$NEW_PASSWORD"
"$PSQL" -U postgres -c "SELECT version();" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Connection successful!"
    echo ""
    echo "========================================"
    echo "✅ PASSWORD RESET COMPLETE!"
    echo "========================================"
    echo ""
    echo "Your new postgres password is: $NEW_PASSWORD"
    echo ""
    echo "Next steps:"
    echo "1. Save this password somewhere safe"
    echo "2. Run: ./setup_db.sh"
    echo "3. Use password: $NEW_PASSWORD"
    echo ""
else
    echo "❌ Connection test failed"
    echo "Please try running: ./reset_postgres_password.sh again"
    exit 1
fi

unset PGPASSWORD
