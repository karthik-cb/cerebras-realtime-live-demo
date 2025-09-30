"""
Comprehensive health check system for the voice agent demo.
Provides different levels of health checks for various deployment scenarios.
"""

import asyncio
import os
import time
from datetime import datetime
from typing import Dict, List, Optional

import httpx
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from loguru import logger
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from common.config import SERVICE_API_KEYS
from common.database import default_session_factory


class HealthChecker:
    """Comprehensive health check system"""
    
    def __init__(self):
        self.start_time = time.time()
        self.checks = {
            "database": self._check_database,
            "deepgram": self._check_deepgram,
            "cerebras": self._check_cerebras,
            "daily": self._check_daily,
            "mcp_servers": self._check_mcp_servers,
        }
    
    async def _check_database(self) -> Dict[str, any]:
        """Check database connectivity and basic operations"""
        try:
            async with default_session_factory() as session:
                # Test basic query
                result = await session.execute(text("SELECT 1"))
                result.scalar()
                
                # Test database type
                db_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./sesame.db")
                if "postgresql" in db_url:
                    db_type = "PostgreSQL"
                elif "mysql" in db_url:
                    db_type = "MySQL"
                else:
                    db_type = "SQLite"
                
                return {
                    "status": "healthy",
                    "type": db_type,
                    "message": "Database connection successful"
                }
        except SQLAlchemyError as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "message": "Database connection failed"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "message": "Database check failed"
            }
    
    async def _check_deepgram(self) -> Dict[str, any]:
        """Check Deepgram API connectivity"""
        api_key = SERVICE_API_KEYS.get("deepgram")
        if not api_key:
            return {
                "status": "disabled",
                "message": "Deepgram API key not configured"
            }
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    "https://api.deepgram.com/v1/projects",
                    headers={"Authorization": f"Token {api_key}"}
                )
                
                if response.status_code == 200:
                    return {
                        "status": "healthy",
                        "message": "Deepgram API accessible"
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "error": f"HTTP {response.status_code}",
                        "message": "Deepgram API returned error"
                    }
        except httpx.TimeoutException:
            return {
                "status": "unhealthy",
                "error": "Timeout",
                "message": "Deepgram API timeout"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "message": "Deepgram API check failed"
            }
    
    async def _check_cerebras(self) -> Dict[str, any]:
        """Check Cerebras API connectivity"""
        api_key = SERVICE_API_KEYS.get("cerebras")
        if not api_key:
            return {
                "status": "disabled",
                "message": "Cerebras API key not configured"
            }
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    "https://api.cerebras.ai/v1/models",
                    headers={"Authorization": f"Bearer {api_key}"}
                )
                
                if response.status_code == 200:
                    return {
                        "status": "healthy",
                        "message": "Cerebras API accessible"
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "error": f"HTTP {response.status_code}",
                        "message": "Cerebras API returned error"
                    }
        except httpx.TimeoutException:
            return {
                "status": "unhealthy",
                "error": "Timeout",
                "message": "Cerebras API timeout"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "message": "Cerebras API check failed"
            }
    
    async def _check_daily(self) -> Dict[str, any]:
        """Check Daily.co API connectivity"""
        api_key = SERVICE_API_KEYS.get("daily")
        if not api_key:
            return {
                "status": "disabled",
                "message": "Daily.co API key not configured"
            }
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    "https://api.daily.co/v1/rooms",
                    headers={"Authorization": f"Bearer {api_key}"}
                )
                
                if response.status_code == 200:
                    return {
                        "status": "healthy",
                        "message": "Daily.co API accessible"
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "error": f"HTTP {response.status_code}",
                        "message": "Daily.co API returned error"
                    }
        except httpx.TimeoutException:
            return {
                "status": "unhealthy",
                "error": "Timeout",
                "message": "Daily.co API timeout"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "message": "Daily.co API check failed"
            }
    
    async def _check_mcp_servers(self) -> Dict[str, any]:
        """Check MCP server availability"""
        mcp_status = {}
        
        # Check PayPal MCP if enabled
        if os.getenv("MCP_PAYPAL_SANDBOX_ENABLED", "false").lower() == "true":
            paypal_client_id = os.getenv("PAYPAL_CLIENT_ID")
            if paypal_client_id:
                mcp_status["paypal"] = {
                    "status": "configured",
                    "message": "PayPal MCP configured"
                }
            else:
                mcp_status["paypal"] = {
                    "status": "misconfigured",
                    "message": "PayPal MCP enabled but client ID missing"
                }
        else:
            mcp_status["paypal"] = {
                "status": "disabled",
                "message": "PayPal MCP disabled"
            }
        
        # Check other MCP servers
        mcp_servers = [
            "MCP_FILESYSTEM_ENABLED",
            # "MCP_DATABASE_ENABLED", 
            "MCP_WEATHER_ENABLED",
            # "MCP_CALENDAR_ENABLED"
        ]
        
        for server in mcp_servers:
            enabled = os.getenv(server, "false").lower() == "true"
            mcp_status[server.lower().replace("mcp_", "").replace("_enabled", "")] = {
                "status": "enabled" if enabled else "disabled",
                "message": f"MCP {server} {'enabled' if enabled else 'disabled'}"
            }
        
        return {
            "status": "healthy",
            "servers": mcp_status,
            "message": "MCP server configuration checked"
        }
    
    async def basic_health(self) -> Dict[str, any]:
        """Basic health check - just application status"""
        uptime = time.time() - self.start_time
        return {
            "status": "healthy",
            "uptime_seconds": uptime,
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Application is running"
        }
    
    async def standard_health(self) -> Dict[str, any]:
        """Standard health check - includes database"""
        uptime = time.time() - self.start_time
        db_check = await self._check_database()
        
        overall_status = "healthy" if db_check["status"] == "healthy" else "unhealthy"
        
        return {
            "status": overall_status,
            "uptime_seconds": uptime,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {
                "database": db_check
            },
            "message": "Standard health check completed"
        }
    
    async def comprehensive_health(self) -> Dict[str, any]:
        """Comprehensive health check - all components"""
        uptime = time.time() - self.start_time
        
        # Run all checks concurrently
        check_tasks = [check_func() for check_func in self.checks.values()]
        check_results = await asyncio.gather(*check_tasks, return_exceptions=True)
        
        # Process results
        checks = {}
        overall_status = "healthy"
        
        for check_name, result in zip(self.checks.keys(), check_results):
            if isinstance(result, Exception):
                checks[check_name] = {
                    "status": "error",
                    "error": str(result),
                    "message": f"{check_name} check failed with exception"
                }
                overall_status = "unhealthy"
            else:
                checks[check_name] = result
                if result["status"] == "unhealthy":
                    overall_status = "unhealthy"
        
        return {
            "status": overall_status,
            "uptime_seconds": uptime,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": checks,
            "message": "Comprehensive health check completed"
        }


# Global health checker instance
health_checker = HealthChecker()
