# PgBouncer Configuration for Railway

This directory contains the configuration files needed to deploy PgBouncer as a connection pooler for your PostgreSQL database on Railway.

## 🚀 Quick Setup

### 1. Deploy PgBouncer Service on Railway

1. **Create a new Railway service**:
   - Go to your Railway project
   - Click "New Service" → "GitHub Repo"
   - Select this repository
   - Set **Root Directory** to `/server/pgbouncer`

2. **Configure Environment Variables**:
   - Copy values from `railway.env.example`
   - Set individual PostgreSQL connection variables (PgBouncer expects `DATABASES_` prefix):
     - `DATABASES_HOST` - Your PostgreSQL service hostname
     - `DATABASES_DB` - Your database name
     - `DATABASES_USER` - Your database username
     - `DATABASES_PASSWORD` - Your database password
     - `DATABASES_PORT` - Your database port (usually 5432)
   - Generate MD5 hash: `echo -n "yourpassword" | md5sum`
   - Set `POSTGRES_PASSWORD_HASH` to the generated hash

### 2. Update Your App's Database URL

Change your app's `DATABASE_URL` from:
```
postgresql://user:pass@postgres-host:5432/dbname
```

To:
```
postgresql://user:pass@pgbouncer-service.railway.app:6432/dbname
```

## 🔧 Configuration Details

### `pgbouncer.ini`
- **Pool Mode**: `transaction` (optimized for asyncpg)
- **Max Client Connections**: 100
- **Default Pool Size**: 20
- **Connection Timeouts**: Tuned for Railway's network

### `userlist.txt`
- Contains MD5-hashed passwords for authentication
- Uses environment variables for security

### `Dockerfile`
- Based on official PgBouncer image
- Includes PostgreSQL client for debugging
- Exposes port 6432

## 📊 Connection Flow

```
Your App (asyncpg) → PgBouncer (6432) → PostgreSQL (5432)
    10 connections        20 pool           1 connection
```

## 🔍 Monitoring

### Check PgBouncer Status
```bash
# Connect to PgBouncer admin console
psql -h pgbouncer-service.railway.app -p 6432 -U postgres pgbouncer

# Show pools
SHOW POOLS;

# Show clients
SHOW CLIENTS;

# Show servers
SHOW SERVERS;
```

### Health Check
```bash
# Test connection through PgBouncer
psql -h pgbouncer-service.railway.app -p 6432 -U your_user your_db -c "SELECT 1;"
```

## 🚨 Troubleshooting

### Common Issues

1. **"no such database" error**:
   - Check `POSTGRES_DB` environment variable
   - Verify database name in `pgbouncer.ini`

2. **Authentication failed**:
   - Verify `POSTGRES_PASSWORD_HASH` is correct
   - Check MD5 hash generation

3. **Connection refused**:
   - Verify PgBouncer service is running
   - Check port 6432 is exposed

### Logs
Check Railway logs for PgBouncer service:
```bash
railway logs --service pgbouncer
```

## 🎯 Benefits for asyncpg

- **Connection Multiplexing**: Reduces database connection overhead
- **Better Performance**: Optimized for async operations
- **Cost Savings**: No need for multiple database instances
- **Railway Compatible**: Works with Railway's networking

## 📈 Scaling

As your app grows, you can:
- Increase `max_client_conn` and `default_pool_size`
- Add more PgBouncer instances behind a load balancer
- Monitor connection usage via admin console

