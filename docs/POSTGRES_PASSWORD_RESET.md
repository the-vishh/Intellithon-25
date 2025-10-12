# 🔑 PostgreSQL Password Reset Guide

## Method 1: Using pgAdmin (Easiest)

1. **Open pgAdmin 4**

   - Start Menu → Search "pgAdmin"
   - Or: `  `

2. **Connect to Server**

   - If it asks for a password, this is the pgAdmin master password (set during installation)
   - If you don't remember it, skip to Method 2

3. **Reset postgres Password**

   - Expand "Servers" → "PostgreSQL 17"
   - Right-click "Login/Group Roles" → "postgres"
   - Go to "Definition" tab
   - Enter new password (e.g., `postgres123`)
   - Click "Save"

4. **Done!** Now use this password with the setup script

---

## Method 2: Edit pg_hba.conf (Most Reliable)

This temporarily allows connection without password, then you can reset it.

### Step 1: Find pg_hba.conf

```bash
# It's located at:
# C:\Program Files\PostgreSQL\17\data\pg_hba.conf
```

### Step 2: Backup Original

```bash
cp "/c/Program Files/PostgreSQL/17/data/pg_hba.conf" "/c/Program Files/PostgreSQL/17/data/pg_hba.conf.backup"
```

### Step 3: Edit pg_hba.conf

Open the file in a text editor (as Administrator):

```bash
# Right-click Notepad → Run as Administrator
# Then open: C:\Program Files\PostgreSQL\17\data\pg_hba.conf
```

Find this line near the bottom:

```
# IPv4 local connections:
host    all             all             127.0.0.1/32            scram-sha-256
```

Change `scram-sha-256` to `trust`:

```
# IPv4 local connections:
host    all             all             127.0.0.1/32            trust
```

Also change this line:

```
host    all             all             ::1/128                 scram-sha-256
```

To:

```
host    all             all             ::1/128                 trust
```

**Save the file**

### Step 4: Restart PostgreSQL Service

```bash
# Stop service
sc stop postgresql-x64-17

# Wait 5 seconds
sleep 5

# Start service
sc start postgresql-x64-17
```

Or using Services GUI:

- Press `Win + R` → type `services.msc` → Enter
- Find "postgresql-x64-17"
- Right-click → Restart

### Step 5: Connect and Reset Password

Now you can connect without a password:

```bash
"/c/Program Files/PostgreSQL/17/bin/psql.exe" -U postgres
```

Once connected, run:

```sql
ALTER USER postgres WITH PASSWORD 'postgres123';
\q
```

### Step 6: Restore Security

Edit pg_hba.conf again and change `trust` back to `scram-sha-256`:

```
# IPv4 local connections:
host    all             all             127.0.0.1/32            scram-sha-256
host    all             all             ::1/128                 scram-sha-256
```

Save and restart PostgreSQL service again.

### Step 7: Test New Password

```bash
"/c/Program Files/PostgreSQL/17/bin/psql.exe" -U postgres
# Enter: postgres123
```

---

## Method 3: Reinstall PostgreSQL (Last Resort)

If nothing else works:

1. **Uninstall PostgreSQL**

   - Control Panel → Programs → Uninstall PostgreSQL 17
   - Keep your data or remove it

2. **Reinstall**
   - Download from: https://www.postgresql.org/download/windows/
   - During installation, SET A MEMORABLE PASSWORD!
   - Write it down: `postgres123` or similar

---

## Quick Reset Script (Method 2 Automated)

I'll create a script to help with Method 2:

```bash
./reset_postgres_password.sh
```

This will:

1. Backup pg_hba.conf
2. Change authentication to 'trust'
3. Restart PostgreSQL
4. Let you reset password
5. Restore security settings

---

## After Password Reset

Once you have the password, run the database setup:

### Using the new password:

```bash
# Export password (replace with your actual password)
export PGPASSWORD="postgres123"

# Run setup
"/c/Program Files/PostgreSQL/17/bin/psql.exe" -U postgres -f setup_database.sql

# Unset password
unset PGPASSWORD
```

Or edit `setup_db.sh` to include your password.

---

## Common PostgreSQL Passwords

Try these common defaults (if you didn't change it):

- `postgres`
- `admin`
- `root`
- `password`
- `123456`
- (empty - just press Enter)

---

## Still Can't Remember?

Use **Method 2** - it's the most reliable way to reset without knowing the current password.

**Need help?** I can create the automated reset script for you.
