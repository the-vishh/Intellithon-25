# 🚀 REDIS DEPLOYMENT GUIDE

# ==========================

## Quick Start with Docker

### Option 1: Docker Run (Fastest)

```bash
docker run -d \
  --name phishing-redis \
  -p 6379:6379 \
  -v redis-data:/data \
  redis:alpine \
  redis-server \
  --maxmemory 2gb \
  --maxmemory-policy allkeys-lru \
  --save ""
```

### Option 2: Docker Compose (Recommended)

```bash
cd backend
docker-compose up -d redis
```

### Option 3: Local Installation

#### Windows (Chocolatey)

```bash
choco install redis-64
redis-server --maxmemory 2gb --maxmemory-policy allkeys-lru
```

#### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis
```

#### macOS (Homebrew)

```bash
brew install redis
brew services start redis
```

## Configuration

### Optimal Settings for Phishing Detection

```redis
# Memory Management
maxmemory 2gb
maxmemory-policy allkeys-lru

# Performance
save ""  # Disable persistence for speed
appendonly no

# Network
bind 0.0.0.0
port 6379
timeout 0
tcp-keepalive 300

# Limits
maxclients 10000
```

### Connection Test

```bash
# Test Redis connection
redis-cli ping
# Expected: PONG

# Set test value
redis-cli set test "hello"

# Get test value
redis-cli get test
# Expected: "hello"

# Monitor commands in real-time
redis-cli monitor
```

## Monitoring

### Check Memory Usage

```bash
redis-cli info memory
```

### Check Statistics

```bash
redis-cli info stats
```

### View Cache Keys

```bash
# Count keys
redis-cli dbsize

# List phishing detection keys
redis-cli keys "phishing:v1:*"

# Get key TTL
redis-cli ttl "phishing:v1:abc123..."
```

## Performance Tuning

### Expected Performance

- **Latency**: <1ms for GET/SET operations
- **Throughput**: 100,000+ ops/second
- **Memory**: 2GB max (stores ~500K cached URLs)
- **Hit Rate**: 80-90% (repeat URL queries)

### Cache Strategy

- **Key Format**: `phishing:v1:{sha256(url)}`
- **Safe URLs**: 24 hour TTL
- **Phishing URLs**: 7 day TTL
- **Eviction**: LRU when memory full

## Troubleshooting

### Can't Connect

```bash
# Check if Redis is running
redis-cli ping

# Check port
netstat -an | grep 6379

# Check Docker container
docker ps | grep redis
docker logs phishing-redis
```

### High Memory Usage

```bash
# Check memory
redis-cli info memory | grep used_memory_human

# Clear all keys (USE WITH CAUTION)
redis-cli flushall

# Clear only phishing keys
redis-cli --scan --pattern "phishing:v1:*" | xargs redis-cli del
```

### Slow Performance

```bash
# Check slow queries
redis-cli slowlog get 10

# Check latency
redis-cli --latency

# Check connected clients
redis-cli client list
```

## Docker Compose (Full Stack)

Create `docker-compose.yml`:

```yaml
version: "3.8"

services:
  redis:
    image: redis:alpine
    container_name: phishing-redis
    ports:
      - "6379:6379"
    command: >
      redis-server
      --maxmemory 2gb
      --maxmemory-policy allkeys-lru
      --save ""
    volumes:
      - redis-data:/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3

volumes:
  redis-data:
```

Start: `docker-compose up -d`
Stop: `docker-compose down`
Logs: `docker-compose logs -f redis`

## Production Deployment

### Security Best Practices

```redis
# Set password (in redis.conf)
requirepass your_strong_password_here

# Bind to specific IP
bind 127.0.0.1

# Rename dangerous commands
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command CONFIG ""
```

### High Availability

- Use Redis Sentinel for automatic failover
- Set up master-replica replication
- Consider Redis Cluster for horizontal scaling

### Monitoring Tools

- RedisInsight (GUI)
- Prometheus + Grafana
- DataDog / New Relic integrations

## Success Criteria

✅ Redis responds to PING
✅ Can SET and GET values
✅ Rust API can connect (test with `cargo run`)
✅ Python ML service can connect (optional)
✅ Latency <10ms for cache hits
✅ Hit rate >80% after warmup

## Next Steps

1. Start Redis: `docker run -d --name phishing-redis -p 6379:6379 redis:alpine`
2. Test connection: `redis-cli ping`
3. Start Rust API: `cd backend && cargo run`
4. Start Python ML: `cd ml-service && python3 app.py`
5. Test full stack: `curl -X POST http://localhost:8080/api/check-url -H "Content-Type: application/json" -d '{"url":"https://google.com"}'`
