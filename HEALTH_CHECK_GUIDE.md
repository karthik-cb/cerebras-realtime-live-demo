# 🏥 Health Check Guide for Voice Agent Demo

This guide provides comprehensive health check options for your voice agent demo across different deployment platforms.

## 🎯 **Health Check Endpoints Available**

### **1. Basic Health Check** (`/healthz`)
- **Purpose**: Simple application status
- **Use Case**: Platform health checks (Fly.io, Railway, Render)
- **Response Time**: < 100ms
- **Checks**: Application uptime only

### **2. Standard Health Check** (`/health`)
- **Purpose**: Database connectivity
- **Use Case**: Production monitoring
- **Response Time**: < 500ms
- **Checks**: Application + Database

### **3. Comprehensive Health Check** (`/health/detailed`)
- **Purpose**: All external dependencies
- **Use Case**: Debugging and detailed monitoring
- **Response Time**: < 2s
- **Checks**: Application + Database + APIs + MCP servers

### **4. Kubernetes-Style Checks**
- **Readiness** (`/health/ready`): Can accept traffic?
- **Liveness** (`/health/live`): Is application alive?

## 🔧 **Platform-Specific Configurations**

### **Fly.io Configuration**

**fly.toml**:
```toml
[[http_service.checks]]
  interval = "15s"
  timeout = "2s"
  grace_period = "10s"
  method = "GET"
  path = "/healthz"  # Basic health check

# Optional: Add readiness check
[[http_service.checks]]
  interval = "30s"
  timeout = "5s"
  grace_period = "15s"
  method = "GET"
  path = "/health/ready"
```

**Health Check Strategy**:
- **Startup**: Use `/healthz` for quick checks
- **Monitoring**: Use `/health` for standard monitoring
- **Debugging**: Use `/health/detailed` for troubleshooting

### **Railway Configuration**

**railway.json**:
```json
{
  "deploy": {
    "healthcheckPath": "/healthz",
    "healthcheckTimeout": 100
  }
}
```

**Environment Variables**:
```bash
# Optional: Configure health check behavior
HEALTH_CHECK_TIMEOUT=5
HEALTH_CHECK_INTERVAL=30
```

### **Render Configuration**

**render.yaml**:
```yaml
services:
  - type: web
    name: voice-agent-backend
    healthCheckPath: /healthz
    envVars:
      - key: HEALTH_CHECK_TIMEOUT
        value: "5"
```

### **Google Cloud Run Configuration**

**Dockerfile**:
```dockerfile
# Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7860/healthz || exit 1
```

## 📊 **Health Check Response Examples**

### **Basic Health Check** (`/healthz`)
```json
{
  "status": "healthy",
  "uptime_seconds": 3600,
  "timestamp": "2024-01-15T10:30:00Z",
  "message": "Application is running"
}
```

### **Standard Health Check** (`/health`)
```json
{
  "status": "healthy",
  "uptime_seconds": 3600,
  "timestamp": "2024-01-15T10:30:00Z",
  "checks": {
    "database": {
      "status": "healthy",
      "type": "PostgreSQL",
      "message": "Database connection successful"
    }
  },
  "message": "Standard health check completed"
}
```

### **Comprehensive Health Check** (`/health/detailed`)
```json
{
  "status": "healthy",
  "uptime_seconds": 3600,
  "timestamp": "2024-01-15T10:30:00Z",
  "checks": {
    "database": {
      "status": "healthy",
      "type": "PostgreSQL",
      "message": "Database connection successful"
    },
    "deepgram": {
      "status": "healthy",
      "message": "Deepgram API accessible"
    },
    "cerebras": {
      "status": "healthy",
      "message": "Cerebras API accessible"
    },
    "daily": {
      "status": "disabled",
      "message": "Daily.co API key not configured"
    },
    "mcp_servers": {
      "status": "healthy",
      "servers": {
        "paypal": {
          "status": "configured",
          "message": "PayPal MCP configured"
        },
        "filesystem": {
          "status": "disabled",
          "message": "MCP filesystem disabled"
        }
      },
      "message": "MCP server configuration checked"
    }
  },
  "message": "Comprehensive health check completed"
}
```

## 🚨 **Health Check Status Codes**

### **HTTP Status Codes**
- **200 OK**: All checks passed
- **503 Service Unavailable**: One or more checks failed

### **Component Status Values**
- **healthy**: Component is working correctly
- **unhealthy**: Component has issues
- **disabled**: Component is not configured/enabled
- **error**: Check failed with exception

## 🔍 **Monitoring and Alerting**

### **Recommended Monitoring Setup**

**1. Basic Monitoring** (Every 30 seconds):
```bash
curl -f https://your-app.com/healthz
```

**2. Standard Monitoring** (Every 5 minutes):
```bash
curl -f https://your-app.com/health
```

**3. Detailed Monitoring** (Every 15 minutes):
```bash
curl -f https://your-app.com/health/detailed
```

### **Alerting Rules**

**Critical Alerts**:
- Application down (all endpoints return 503)
- Database connection failed
- Core API services unavailable (Deepgram, Cerebras)

**Warning Alerts**:
- Optional services unavailable (Daily.co, MCP servers)
- High response times (> 2 seconds)

## 🛠️ **Customization Options**

### **Environment Variables**

```bash
# Health check configuration
HEALTH_CHECK_TIMEOUT=5          # Timeout for external API checks
HEALTH_CHECK_INTERVAL=30        # Interval for periodic checks
HEALTH_CHECK_ENABLE_DETAILED=true  # Enable detailed health checks
HEALTH_CHECK_ENABLE_MCP=true    # Enable MCP server checks
```

### **Custom Health Checks**

You can add custom health checks by extending the `HealthChecker` class:

```python
# In webapp/health.py
async def _check_custom_service(self) -> Dict[str, any]:
    """Check custom service"""
    try:
        # Your custom check logic
        return {
            "status": "healthy",
            "message": "Custom service is working"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "message": "Custom service check failed"
        }

# Add to checks dictionary
self.checks["custom_service"] = self._check_custom_service
```

## 🚀 **Deployment Recommendations**

### **For Development**
- Use `/healthz` for basic monitoring
- Check `/health` when debugging database issues

### **For Staging**
- Use `/health` for standard monitoring
- Set up alerts for database connectivity

### **For Production**
- Use `/healthz` for platform health checks
- Use `/health` for application monitoring
- Use `/health/detailed` for debugging
- Set up comprehensive alerting

## 📈 **Performance Considerations**

### **Response Times**
- **Basic**: < 100ms (application only)
- **Standard**: < 500ms (application + database)
- **Comprehensive**: < 2s (all external services)

### **Optimization Tips**
- Use basic health checks for frequent monitoring
- Use comprehensive checks sparingly
- Cache external API responses when possible
- Set appropriate timeouts for external services

## 🔧 **Troubleshooting**

### **Common Issues**

**Health Check Timeout**:
```bash
# Check if application is responding
curl -v https://your-app.com/healthz

# Check application logs
fly logs  # or railway logs, render logs
```

**Database Connection Issues**:
```bash
# Check database connectivity
curl https://your-app.com/health

# Check database URL
echo $DATABASE_URL
```

**External API Issues**:
```bash
# Check detailed health
curl https://your-app.com/health/detailed

# Check specific API keys
echo $DEEPGRAM_API_KEY
echo $CEREBRAS_API_KEY
```

### **Debug Commands**

```bash
# Test health endpoints locally
curl http://localhost:7860/healthz
curl http://localhost:7860/health
curl http://localhost:7860/health/detailed

# Check environment variables
python -c "import os; print('DATABASE_URL:', os.getenv('DATABASE_URL'))"
```

## 🎯 **Best Practices**

1. **Use appropriate health check level** for your monitoring needs
2. **Set reasonable timeouts** to avoid false positives
3. **Monitor response times** to detect performance issues
4. **Set up alerting** for critical health check failures
5. **Test health checks** before deploying to production
6. **Document custom health checks** for team members

---

**Your voice agent demo now has comprehensive health monitoring! 🏥🚀**
