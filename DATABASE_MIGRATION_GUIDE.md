# 🗄️ Database Migration Guide: SQLite to Cloud Databases

This guide explains how to migrate your voice agent demo from local SQLite to cloud databases while maintaining async SQLAlchemy compatibility.

## 🎯 **Async SQLAlchemy Compatibility**

**✅ Good News**: Your existing code is **already compatible** with cloud databases!

**Current Setup**:
- ✅ Uses `AsyncSession` and `async_sessionmaker`
- ✅ Uses `create_async_engine` with async drivers
- ✅ All database operations are async-compatible

**What Changes**: Only the database URL and driver, not your application code!

## 🔧 **Required Changes**

### **1. Update Requirements**

**Before** (SQLite only):
```txt
sqlalchemy[aiosqlite]
```

**After** (Multi-database support):
```txt
sqlalchemy[postgresql,aiosqlite]
```

### **2. Database URL Formats**

**SQLite** (Local development):
```bash
DATABASE_URL="sqlite+aiosqlite:///./sesame.db"
```

**PostgreSQL** (Railway, Render, Supabase):
```bash
DATABASE_URL="postgresql+asyncpg://user:password@host:port/database"
```

**MySQL** (PlanetScale):
```bash
DATABASE_URL="mysql+aiomysql://user:password@host:port/database"
```

## 🚀 **Platform-Specific Setup**

### **Railway (PostgreSQL)**

**Setup**:
1. Add PostgreSQL service in Railway dashboard
2. Railway automatically provides `DATABASE_URL`
3. No code changes needed!

**Environment Variables**:
```bash
# Railway automatically sets this
DATABASE_URL="postgresql+asyncpg://postgres:password@host:port/railway"
```

### **Render (PostgreSQL)**

**Setup**:
1. Add PostgreSQL service in Render dashboard
2. Get connection string from database settings
3. Set as environment variable

**Environment Variables**:
```bash
DATABASE_URL="postgresql+asyncpg://user:password@host:port/database"
```

### **Fly.io (External Database)**

**Option A: Supabase (Recommended)**
```bash
# 1. Create Supabase project
# 2. Get connection string from Settings → Database
# 3. Set as Fly.io secret
fly secrets set DATABASE_URL="postgresql+asyncpg://postgres:password@host:port/postgres"
```

**Option B: PlanetScale (MySQL)**
```bash
# 1. Create PlanetScale database
# 2. Get connection string
# 3. Set as Fly.io secret
fly secrets set DATABASE_URL="mysql+aiomysql://user:password@host:port/database"
```

## 🔄 **Migration Process**

### **Step 1: Update Requirements**

```bash
# Update requirements.txt
sqlalchemy[postgresql,aiosqlite]
```

### **Step 2: Set Database URL**

**For Railway**:
```bash
# Railway automatically provides DATABASE_URL
# No action needed!
```

**For Render**:
```bash
# Set in Render dashboard → Environment Variables
DATABASE_URL=postgresql+asyncpg://user:password@host:port/database
```

**For Fly.io**:
```bash
# Set as secret
fly secrets set DATABASE_URL="postgresql+asyncpg://user:password@host:port/database"
```

### **Step 3: Deploy and Test**

```bash
# Deploy your application
# The database schema will be automatically created on first run
```

## 🧪 **Testing Database Connection**

### **Local Testing with PostgreSQL**

```bash
# Install PostgreSQL locally
# Set DATABASE_URL to local PostgreSQL
export DATABASE_URL="postgresql+asyncpg://postgres:password@localhost:5432/voice_agent"

# Run your application
python sesame.py run
```

### **Test Database Operations**

```python
# Test script to verify database connection
import asyncio
from common.database import default_session_factory
from common.models import Conversation

async def test_database():
    async with default_session_factory() as session:
        # Test creating a conversation
        conversation = Conversation(title="Test Conversation")
        session.add(conversation)
        await session.commit()
        
        # Test querying
        result = await session.execute(select(Conversation))
        conversations = result.scalars().all()
        print(f"Found {len(conversations)} conversations")

# Run the test
asyncio.run(test_database())
```

## 🔍 **Database-Specific Considerations**

### **PostgreSQL**

**Advantages**:
- ✅ Full async support
- ✅ Excellent performance
- ✅ Rich feature set
- ✅ Widely supported by cloud platforms

**Connection String Format**:
```bash
postgresql+asyncpg://user:password@host:port/database
```

### **MySQL**

**Advantages**:
- ✅ Full async support
- ✅ Good performance
- ✅ PlanetScale compatibility

**Connection String Format**:
```bash
mysql+aiomysql://user:password@host:port/database
```

**Note**: Some MySQL features may differ from SQLite/PostgreSQL.

### **SQLite**

**Advantages**:
- ✅ Perfect for local development
- ✅ No external dependencies
- ✅ Fast for small datasets

**Limitations**:
- ❌ Not suitable for production
- ❌ No concurrent writes
- ❌ Limited scalability

## 🚨 **Common Issues and Solutions**

### **Issue 1: Connection Pool Exhaustion**

**Problem**: Too many concurrent connections

**Solution**:
```python
# In database.py
self._engine = create_async_engine(
    db_url,
    pool_size=10,          # Maximum connections
    max_overflow=20,       # Additional connections
    pool_recycle=3600,     # Recycle connections every hour
    pool_pre_ping=True,    # Test connections before use
)
```

### **Issue 2: Database Schema Differences**

**Problem**: SQLite vs PostgreSQL/MySQL syntax differences

**Solution**: Your models are already compatible! SQLAlchemy handles the differences.

### **Issue 3: Connection Timeouts**

**Problem**: Long-running connections timeout

**Solution**:
```python
# In database.py
self._engine = create_async_engine(
    db_url,
    pool_recycle=3600,     # Recycle connections every hour
    pool_pre_ping=True,    # Test connections before use
)
```

## 📊 **Performance Comparison**

| Database | Local Dev | Production | Async Support | Cloud Support |
|----------|-----------|------------|---------------|---------------|
| **SQLite** | ✅ Excellent | ❌ Not suitable | ✅ Full | ❌ Limited |
| **PostgreSQL** | ✅ Good | ✅ Excellent | ✅ Full | ✅ Excellent |
| **MySQL** | ✅ Good | ✅ Good | ✅ Full | ✅ Good |

## 🎯 **Recommended Setup**

### **Development**
```bash
# Use SQLite for local development
DATABASE_URL="sqlite+aiosqlite:///./sesame.db"
```

### **Production**
```bash
# Use PostgreSQL for production
DATABASE_URL="postgresql+asyncpg://user:password@host:port/database"
```

### **Platform-Specific Recommendations**

- **Railway**: Use built-in PostgreSQL
- **Render**: Use built-in PostgreSQL  
- **Fly.io**: Use Supabase PostgreSQL
- **Vercel**: Use external PostgreSQL (Supabase, PlanetScale)

## 🚀 **Next Steps**

1. **Update requirements.txt** with PostgreSQL support
2. **Choose your cloud database** (PostgreSQL recommended)
3. **Set DATABASE_URL** in your deployment platform
4. **Deploy and test** - schema will be created automatically
5. **Monitor performance** and adjust connection pool settings

## 📞 **Support**

- **SQLAlchemy Async**: [docs.sqlalchemy.org](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- **PostgreSQL**: [postgresql.org](https://www.postgresql.org/)
- **PlanetScale**: [planetscale.com](https://planetscale.com/)
- **Supabase**: [supabase.com](https://supabase.com/)

---

**Your async SQLAlchemy setup is ready for cloud databases! 🚀🗄️**
