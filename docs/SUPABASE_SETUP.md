# 🚀 Supabase Setup Guide for PhishGuard

## Why Supabase?

- ✅ No password reset needed
- ✅ Cloud PostgreSQL database
- ✅ Free tier (500MB database)
- ✅ Automatic backups
- ✅ Web dashboard
- ✅ 100% compatible with your existing code

---

## Step 1: Create Supabase Account

1. Go to: **https://supabase.com**
2. Click **"Start your project"**
3. Sign up with GitHub (recommended) or email
4. Free - no credit card required!

---

## Step 2: Create New Project

1. Click **"New Project"**
2. Fill in:

   - **Name**: `phishguard-db`
   - **Database Password**: Choose a strong password (write it down!)
   - **Region**: Choose closest to you (e.g., US West, EU Central)
   - **Pricing Plan**: Free

3. Click **"Create new project"**
4. Wait ~2 minutes for database to provision

---

## Step 3: Get Connection String

1. In your project dashboard, click **"Settings"** (⚙️ icon)
2. Click **"Database"** in left sidebar
3. Scroll to **"Connection string"**
4. Select **"URI"** tab
5. Copy the connection string - it looks like:

```
postgresql://postgres:[YOUR-PASSWORD]@db.xxxxxxxxxxxxx.supabase.co:5432/postgres
```

6. Replace `[YOUR-PASSWORD]` with the password you set in Step 2

**Example:**

```
postgresql://postgres:MySecurePass123@db.abcdefghijk.supabase.co:5432/postgres
```

---

## Step 4: Update Backend Configuration

Edit `backend/.env`:

```bash
# Replace the DATABASE_URL line with your Supabase connection string
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.xxxxx.supabase.co:5432/postgres
```

**Full example:**

```env
# Rust API Gateway Configuration

# Server
HOST=0.0.0.0
PORT=8080

# Database (Supabase PostgreSQL)
DATABASE_URL=postgresql://postgres:MySecurePass123@db.abcdefghijk.supabase.co:5432/postgres

# Redis
REDIS_URL=redis://127.0.0.1:6379

# ML Service
ML_SERVICE_URL=http://127.0.0.1:8000

# Logging
RUST_LOG=info
```

---

## Step 5: Run Migrations

### Option A: Using Supabase SQL Editor (Easiest)

1. In Supabase dashboard, click **"SQL Editor"** (left sidebar)
2. Click **"New query"**
3. Copy the contents of `backend/migrations/2025-10-10-000001_create_user_analytics/up.sql`
4. Paste into SQL editor
5. Click **"Run"** (or press Ctrl+Enter)
6. Repeat for other migration files

### Option B: Using psql Command

```bash
# Read your migration file
cat backend/migrations/2025-10-10-000001_create_user_analytics/up.sql

# Connect to Supabase and run migration
psql "postgresql://postgres:YOUR_PASSWORD@db.xxxxx.supabase.co:5432/postgres" < backend/migrations/2025-10-10-000001_create_user_analytics/up.sql
```

### Option C: Using Diesel CLI

```bash
cd backend
diesel migration run --database-url="postgresql://postgres:YOUR_PASSWORD@db.xxxxx.supabase.co:5432/postgres"
```

---

## Step 6: Verify Tables Created

**In Supabase Dashboard:**

1. Click **"Table Editor"** (left sidebar)
2. You should see tables:
   - user_analytics
   - user_threat_sources
   - detected_threats
   - ml_feedback
   - malicious_patterns

**Or via psql:**

```bash
psql "postgresql://postgres:YOUR_PASSWORD@db.xxxxx.supabase.co:5432/postgres" -c "\dt"
```

---

## Step 7: Restart API with Supabase

```bash
# Stop current API
taskkill //F //IM phishing-detector-api.exe

# Start with Supabase connection
cd backend
cargo run --release > api_supabase.log 2>&1 &

# Wait for startup
sleep 30

# Test
curl http://localhost:8080/health
```

Should show: `"database":"healthy"`

---

## Step 8: Test Database Connection

### Test Write

```bash
# Visit a phishing site with extension loaded
# Data should be saved to Supabase
```

### View in Dashboard

1. Go to Supabase dashboard
2. Click **"Table Editor"**
3. Click **"user_analytics"** table
4. You should see your activity logs!

### Query Data

In SQL Editor, run:

```sql
-- View recent activities
SELECT * FROM user_analytics ORDER BY created_at DESC LIMIT 10;

-- View threat sources by country
SELECT country_name, threat_count
FROM user_threat_sources
ORDER BY threat_count DESC;
```

---

## Supabase Benefits for PhishGuard

### 1. **Web Dashboard**

- View all data in real-time
- Run SQL queries
- Monitor database size
- See API usage

### 2. **Automatic Backups**

- Daily backups on free tier
- Point-in-time recovery on paid tier
- Data never lost

### 3. **Built-in Features**

- Row Level Security (RLS)
- Real-time subscriptions
- Auto-generated REST API
- Authentication (if needed later)

### 4. **Scalability**

- Start free (500MB)
- Upgrade as needed
- No server management

### 5. **Security**

- SSL/TLS encryption
- Connection pooling
- Database firewall

---

## Connection String Formats

### For Diesel (Rust)

```
postgresql://postgres:password@db.xxxxx.supabase.co:5432/postgres
```

### For psql CLI

```
postgresql://postgres:password@db.xxxxx.supabase.co:5432/postgres
```

### With Connection Pooling (Recommended for Production)

```
postgresql://postgres:password@db.xxxxx.supabase.co:6543/postgres?pgbouncer=true
```

---

## Troubleshooting

### Error: "connection refused"

- Check internet connection
- Verify connection string is correct
- Ensure Supabase project is active

### Error: "password authentication failed"

- Double-check password in connection string
- Password should be URL-encoded (e.g., `@` becomes `%40`)

### Error: "SSL required"

- Add `?sslmode=require` to connection string:

```
postgresql://postgres:password@db.xxxxx.supabase.co:5432/postgres?sslmode=require
```

### Error: "too many connections"

- Free tier has 60 connection limit
- Use connection pooling port 6543
- Or close unused connections

---

## Migration Script

I'll create a script to help migrate from local to Supabase:

```bash
./migrate_to_supabase.sh
```

This will:

1. Export data from Redis (if any)
2. Update .env with Supabase URL
3. Run migrations
4. Test connection

---

## Comparing Costs

### Supabase Free Tier

- 500 MB database
- 2 GB bandwidth/month
- 50,000 monthly active users
- **Perfect for PhishGuard!**

### Supabase Pro ($25/month)

- 8 GB database
- 250 GB bandwidth
- Daily backups
- Point-in-time recovery

**For your use case:** Free tier is more than enough!

---

## Security Best Practices

1. **Never commit .env to Git**

```bash
# Already in .gitignore, but verify:
cat .gitignore | grep .env
```

2. **Use Environment Variables**

```bash
# In production, set DATABASE_URL as env var
export DATABASE_URL="postgresql://..."
```

3. **Enable Row Level Security (RLS)**

```sql
-- In Supabase SQL Editor
ALTER TABLE user_analytics ENABLE ROW LEVEL SECURITY;
```

4. **Rotate Passwords Regularly**

- In Supabase: Settings → Database → Reset database password

---

## Quick Setup Checklist

- [ ] Create Supabase account
- [ ] Create new project
- [ ] Copy connection string
- [ ] Update backend/.env
- [ ] Run migrations in SQL Editor
- [ ] Restart API
- [ ] Test health endpoint
- [ ] Load extension and test

---

## Next Steps After Supabase Setup

1. ✅ Database configured and working
2. Run migrations
3. Restart API
4. Load Chrome extension
5. Test complete system
6. View data in Supabase dashboard!

---

**Time to setup:** ~10 minutes
**Cost:** FREE
**Benefit:** No more local database issues!

Ready to switch to Supabase? It's the easiest solution for your password problem!
