# 🗄️ PostgreSQL Database Setup Guide

## Current Status

- ✅ PostgreSQL 17.2 installed at: `C:\Program Files\PostgreSQL\17`
- ✅ PostgreSQL service running
- ✅ Backend .env already configured with correct DATABASE_URL
- ⏳ Database needs to be created

## Quick Setup (Choose One Method)

### Method 1: Using Bash Script (Recommended)

```bash
./setup_db.sh
# Enter your postgres password when prompted
```

### Method 2: Using Windows Batch File

```cmd
setup_db.bat
REM Enter password when prompted
```

### Method 3: Manual Setup

```bash
# Run psql with full path
"/c/Program Files/PostgreSQL/17/bin/psql.exe" -U postgres

# Then run these commands:
CREATE DATABASE phishguard;
CREATE USER phishguard_user WITH PASSWORD 'phishguard123';
GRANT ALL PRIVILEGES ON DATABASE phishguard TO phishguard_user;
\c phishguard
GRANT ALL ON SCHEMA public TO phishguard_user;
\q
```

## After Database Creation

### Step 1: Verify Database Exists

```bash
"/c/Program Files/PostgreSQL/17/bin/psql.exe" -U postgres -l | grep phishguard
```

Should show:

```
phishguard | phishguard_user | UTF8 | ...
```

### Step 2: Run Migrations

```bash
"/c/Program Files/PostgreSQL/17/bin/psql.exe" -U phishguard_user -d phishguard -f backend/migrations/2025-10-10-000001_create_user_analytics/up.sql
```

Enter password when prompted: `phishguard123`

### Step 3: Verify Tables Created

```bash
"/c/Program Files/PostgreSQL/17/bin/psql.exe" -U phishguard_user -d phishguard -c "\dt"
```

Expected tables:

- user_analytics
- user_threat_sources
- malicious_patterns
- detected_threats
- ml_feedback
- ... and more

### Step 4: Restart API

```bash
# Stop current API
taskkill //F //IM phishing-detector-api.exe

# Start with database connection
cd backend
cargo run --release > api_with_db.log 2>&1 &

# Wait for startup
sleep 30

# Test connection
curl http://localhost:8080/health
```

Should show: `"database":"healthy"` (instead of "database":"not_configured")

## Configuration Details

### Database Connection

- **Host**: localhost
- **Port**: 5432
- **Database**: phishguard
- **User**: phishguard_user
- **Password**: phishguard123

### Connection String (Already in backend/.env)

```
DATABASE_URL=postgresql://phishguard_user:phishguard123@localhost:5432/phishguard
```

## Database Schema Overview

### Core Tables

#### `user_analytics`

Stores user activity and threat detection logs

- user_id (UUID)
- url (TEXT)
- is_phishing (BOOLEAN)
- confidence (FLOAT)
- timestamp
- device_fingerprint
- ... and more

#### `user_threat_sources`

Geographic threat intelligence (GeoIP data)

- user_id (UUID)
- country_code (TEXT) - e.g., "US", "CN", "RU"
- country_name (TEXT) - e.g., "United States"
- threat_count (INTEGER)
- phishing_count (INTEGER)
- last_seen (TIMESTAMP)

#### `detected_threats`

Historical threat detections

- threat_id (UUID)
- url (TEXT)
- detection_time (TIMESTAMP)
- threat_level (TEXT)
- confidence (FLOAT)

#### `ml_feedback`

User feedback for model improvement

- feedback_id (UUID)
- url (TEXT)
- actual_label (BOOLEAN)
- predicted_label (BOOLEAN)
- timestamp

## Benefits of PostgreSQL Setup

### Before (Redis Only)

- ❌ Data lost on restart
- ❌ Limited querying
- ❌ No historical analysis
- ❌ No persistent threat intelligence

### After (PostgreSQL)

- ✅ Persistent analytics history
- ✅ Complex SQL queries
- ✅ Long-term trend analysis
- ✅ Geographic threat intelligence over time
- ✅ Model performance tracking
- ✅ User behavior insights
- ✅ Backup and recovery

## Testing Database Connection

### 1. Test Direct Connection

```bash
"/c/Program Files/PostgreSQL/17/bin/psql.exe" -U phishguard_user -d phishguard -c "SELECT version();"
```

### 2. Test API Connection

```bash
# Check health endpoint
curl http://localhost:8080/health

# Should show database status
```

### 3. Test GeoIP Persistence

```bash
# After visiting a phishing site with extension
"/c/Program Files/PostgreSQL/17/bin/psql.exe" -U phishguard_user -d phishguard -c "SELECT * FROM user_threat_sources LIMIT 5;"
```

Should show countries where threats were detected!

## Troubleshooting

### Error: "password authentication failed"

- Check PostgreSQL password for 'postgres' user
- Try resetting: Open pgAdmin → Right-click postgres user → Set password

### Error: "connection refused"

- PostgreSQL service not running
- Run: `sc start postgresql-x64-17`
- Or: Services (services.msc) → postgresql-x64-17 → Start

### Error: "database already exists"

- Database already created (this is fine!)
- Skip to Step 2 (Run Migrations)

### Error: "permission denied for schema public"

- Run grant command:

```sql
"/c/Program Files/PostgreSQL/17/bin/psql.exe" -U postgres -d phishguard -c "GRANT ALL ON SCHEMA public TO phishguard_user;"
```

### Error: "relation does not exist"

- Migrations not run yet
- Run Step 2 (Run Migrations)

## Migration Files Location

Check what migrations are available:

```bash
ls -la backend/migrations/*/up.sql
```

Common migrations:

- `2025-10-10-000001_create_user_analytics/up.sql` - Core analytics tables
- `2025-10-10-000002_create_threat_intel/up.sql` - Threat intelligence
- `2025-10-10-000003_create_ml_feedback/up.sql` - ML feedback loop

## Verifying Everything Works

### 1. Database Created

```bash
"/c/Program Files/PostgreSQL/17/bin/psql.exe" -U postgres -l | grep phishguard
# Should show: phishguard database exists
```

### 2. Tables Created

```bash
"/c/Program Files/PostgreSQL/17/bin/psql.exe" -U phishguard_user -d phishguard -c "\dt"
# Should show: Multiple tables listed
```

### 3. API Connected

```bash
curl http://localhost:8080/health
# Should show: "database":"healthy"
```

### 4. GeoIP Data Persisting

```bash
# Visit a phishing URL with extension loaded
# Then check database:
"/c/Program Files/PostgreSQL/17/bin/psql.exe" -U phishguard_user -d phishguard -c "SELECT country_name, threat_count FROM user_threat_sources ORDER BY threat_count DESC;"
```

## Adding to System PATH (Optional)

To use `psql` without full path:

1. Open Environment Variables:

   - Windows Key → Search "Environment Variables"
   - Click "Edit the system environment variables"
   - Click "Environment Variables" button

2. Edit PATH:

   - Under "System variables" find "Path"
   - Click "Edit"
   - Click "New"
   - Add: `C:\Program Files\PostgreSQL\17\bin`
   - Click OK on all dialogs

3. Restart terminal and test:

```bash
psql --version
# Should work without full path
```

## Next Steps After Setup

1. ✅ Run `./setup_db.sh` or `setup_db.bat`
2. ✅ Run migrations
3. ✅ Restart API
4. ✅ Load Chrome extension
5. ✅ Test complete system
6. ✅ Check database for persisted data

---

**Status**: Ready to set up! PostgreSQL 17 is installed and running.
**Action**: Run `./setup_db.sh` to create the database.
