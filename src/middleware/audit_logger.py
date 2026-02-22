"""Audit Logging Middleware"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
import logging
from src.core.database import get_db
from src.services.audit_service import AuditService

logger = logging.getLogger(__name__)


class AuditLoggerMiddleware(BaseHTTPMiddleware):
    """Middleware to automatically log API requests"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        """Process request and log to audit trail"""
        
        # Skip logging for health checks and static files
        if request.url.path in ["/health", "/", "/favicon.ico"] or \
           request.url.path.startswith("/_next") or \
           request.url.path.startswith("/static"):
            return await call_next(request)
        
        # Record start time
        start_time = time.time()
        
        # Get request details
        method = request.method
        path = request.url.path
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Log to audit trail (async to not block response)
        try:
            # Get database session
            db = next(get_db())
            audit_service = AuditService(db)
            
            # Determine event type and action
            event_type = "user_action"
            action = self._get_action_from_method(method)
            resource_type = self._get_resource_type_from_path(path)
            
            # Create audit log
            audit_service.create_log(
                event_type=event_type,
                action=action,
                resource_type=resource_type,
                ip_address=ip_address,
                user_agent=user_agent,
                request_method=method,
                request_path=path,
                response_status=response.status_code,
                duration_ms=duration_ms
            )
            
            db.close()
            
        except Exception as e:
            logger.error(f"Error logging to audit trail: {str(e)}")
        
        return response
    
    def _get_action_from_method(self, method: str) -> str:
        """Map HTTP method to action"""
        mapping = {
            "GET": "read",
            "POST": "create",
            "PUT": "update",
            "PATCH": "update",
            "DELETE": "delete"
        }
        return mapping.get(method, "execute")
    
    def _get_resource_type_from_path(self, path: str) -> str:
        """Extract resource type from path"""
        parts = path.strip("/").split("/")
        
        # API paths typically follow /api/v1/{resource}
        if len(parts) >= 3 and parts[0] == "api":
            resource = parts[2]
            # Singularize common resources
            if resource.endswith("ies"):
                return resource[:-3] + "y"
            elif resource.endswith("s"):
                return resource[:-1]
            return resource
        
        return "unknown"
