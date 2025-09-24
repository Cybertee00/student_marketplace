#!/usr/bin/env python3
"""
Role-Based Access Control (RBAC) Service
Handles user roles, permissions, and access control for the Student Marketplace
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime
from fastapi import HTTPException, Request
from models import User, Role, Permission, UserRole, RolePermission, AuditLog


class RBACService:
    """Role-Based Access Control service for managing user permissions"""
    
    @staticmethod
    def get_user_roles(db: Session, user_id: int) -> List[Role]:
        """Get all active roles for a user"""
        user_roles = db.query(UserRole).filter(
            and_(
                UserRole.user_id == user_id,
                UserRole.is_active == True,
                or_(
                    UserRole.expires_at == None,
                    UserRole.expires_at > datetime.utcnow()
                )
            )
        ).all()
        
        return [user_role.role for user_role in user_roles]
    
    @staticmethod
    def get_user_permissions(db: Session, user_id: int) -> List[str]:
        """Get all permissions for a user based on their roles"""
        user_roles = db.query(UserRole).filter(
            and_(
                UserRole.user_id == user_id,
                UserRole.is_active == True,
                or_(
                    UserRole.expires_at == None,
                    UserRole.expires_at > datetime.utcnow()
                )
            )
        ).all()
        
        role_ids = [user_role.role_id for user_role in user_roles]
        
        if not role_ids:
            return []
        
        permissions = db.query(Permission).join(RolePermission).filter(
            RolePermission.role_id.in_(role_ids)
        ).all()
        
        return [permission.name for permission in permissions]
    
    @staticmethod
    def has_permission(db: Session, user_id: int, permission_name: str) -> bool:
        """Check if a user has a specific permission"""
        permissions = RBACService.get_user_permissions(db, user_id)
        return permission_name in permissions
    
    @staticmethod
    def has_any_permission(db: Session, user_id: int, permission_names: List[str]) -> bool:
        """Check if a user has any of the specified permissions"""
        permissions = RBACService.get_user_permissions(db, user_id)
        return any(perm in permissions for perm in permission_names)
    
    @staticmethod
    def has_all_permissions(db: Session, user_id: int, permission_names: List[str]) -> bool:
        """Check if a user has all of the specified permissions"""
        permissions = RBACService.get_user_permissions(db, user_id)
        return all(perm in permissions for perm in permission_names)
    
    @staticmethod
    def assign_role_to_user(
        db: Session, 
        user_id: int, 
        role_name: str, 
        assigned_by: int,
        expires_at: Optional[datetime] = None
    ) -> UserRole:
        """Assign a role to a user"""
        # Check if role exists
        role = db.query(Role).filter(Role.name == role_name).first()
        if not role:
            raise HTTPException(status_code=404, detail=f"Role '{role_name}' not found")
        
        # Check if user already has this role
        existing_role = db.query(UserRole).filter(
            and_(
                UserRole.user_id == user_id,
                UserRole.role_id == role.id,
                UserRole.is_active == True
            )
        ).first()
        
        if existing_role:
            raise HTTPException(status_code=400, detail=f"User already has role '{role_name}'")
        
        # Create new user role
        user_role = UserRole(
            user_id=user_id,
            role_id=role.id,
            assigned_by=assigned_by,
            expires_at=expires_at,
            is_active=True
        )
        
        db.add(user_role)
        db.commit()
        db.refresh(user_role)
        
        return user_role
    
    @staticmethod
    def remove_role_from_user(db: Session, user_id: int, role_name: str, removed_by: int) -> bool:
        """Remove a role from a user"""
        role = db.query(Role).filter(Role.name == role_name).first()
        if not role:
            raise HTTPException(status_code=404, detail=f"Role '{role_name}' not found")
        
        user_role = db.query(UserRole).filter(
            and_(
                UserRole.user_id == user_id,
                UserRole.role_id == role.id,
                UserRole.is_active == True
            )
        ).first()
        
        if not user_role:
            raise HTTPException(status_code=404, detail=f"User does not have role '{role_name}'")
        
        user_role.is_active = False
        db.commit()
        
        return True
    
    @staticmethod
    def create_role(db: Session, name: str, description: str = None) -> Role:
        """Create a new role"""
        existing_role = db.query(Role).filter(Role.name == name).first()
        if existing_role:
            raise HTTPException(status_code=400, detail=f"Role '{name}' already exists")
        
        role = Role(name=name, description=description)
        db.add(role)
        db.commit()
        db.refresh(role)
        
        return role
    
    @staticmethod
    def create_permission(
        db: Session, 
        name: str, 
        resource: str, 
        action: str, 
        description: str = None
    ) -> Permission:
        """Create a new permission"""
        existing_permission = db.query(Permission).filter(Permission.name == name).first()
        if existing_permission:
            raise HTTPException(status_code=400, detail=f"Permission '{name}' already exists")
        
        permission = Permission(
            name=name,
            resource=resource,
            action=action,
            description=description
        )
        db.add(permission)
        db.commit()
        db.refresh(permission)
        
        return permission
    
    @staticmethod
    def assign_permission_to_role(
        db: Session, 
        role_name: str, 
        permission_name: str, 
        granted_by: int
    ) -> RolePermission:
        """Assign a permission to a role"""
        role = db.query(Role).filter(Role.name == role_name).first()
        if not role:
            raise HTTPException(status_code=404, detail=f"Role '{role_name}' not found")
        
        permission = db.query(Permission).filter(Permission.name == permission_name).first()
        if not permission:
            raise HTTPException(status_code=404, detail=f"Permission '{permission_name}' not found")
        
        # Check if permission is already assigned
        existing = db.query(RolePermission).filter(
            and_(
                RolePermission.role_id == role.id,
                RolePermission.permission_id == permission.id
            )
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail=f"Permission '{permission_name}' already assigned to role '{role_name}'")
        
        role_permission = RolePermission(
            role_id=role.id,
            permission_id=permission.id,
            granted_by=granted_by
        )
        
        db.add(role_permission)
        db.commit()
        db.refresh(role_permission)
        
        return role_permission


class AuditService:
    """Service for logging audit events"""
    
    @staticmethod
    def log_action(
        db: Session,
        user_id: Optional[int],
        action: str,
        resource_type: str,
        resource_id: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> AuditLog:
        """Log an audit event"""
        
        # Extract client information from request
        ip_address = None
        user_agent = None
        
        if request:
            # Get IP address
            if "x-forwarded-for" in request.headers:
                ip_address = request.headers["x-forwarded-for"].split(",")[0].strip()
            elif "x-real-ip" in request.headers:
                ip_address = request.headers["x-real-ip"]
            else:
                ip_address = request.client.host if request.client else None
            
            # Get user agent
            user_agent = request.headers.get("user-agent")
        
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            error_message=error_message
        )
        
        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)
        
        return audit_log
    
    @staticmethod
    def get_user_audit_logs(
        db: Session, 
        user_id: int, 
        limit: int = 100, 
        offset: int = 0
    ) -> List[AuditLog]:
        """Get audit logs for a specific user"""
        return db.query(AuditLog).filter(
            AuditLog.user_id == user_id
        ).order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()
    
    @staticmethod
    def get_audit_logs(
        db: Session,
        user_id: Optional[int] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        success: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditLog]:
        """Get audit logs with optional filters"""
        query = db.query(AuditLog)
        
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        if action:
            query = query.filter(AuditLog.action == action)
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)
        if success is not None:
            query = query.filter(AuditLog.success == success)
        
        return query.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()


# Permission constants for easy reference
class Permissions:
    # Dashboard permissions
    DASHBOARD_READ = "admin.dashboard.read"
    
    # Product permissions
    PRODUCTS_READ = "admin.products.read"
    PRODUCTS_CREATE = "admin.products.create"
    PRODUCTS_APPROVE = "admin.products.approve"
    PRODUCTS_REJECT = "admin.products.reject"
    PRODUCTS_DELETE = "admin.products.delete"
    PRODUCTS_UPDATE = "admin.products.update"
    
    # Order permissions
    ORDERS_READ = "admin.orders.read"
    ORDERS_UPDATE = "admin.orders.update"
    ORDERS_DELETE = "admin.orders.delete"
    
    # User permissions
    USERS_READ = "admin.users.read"
    USERS_UPDATE = "admin.users.update"
    USERS_DELETE = "admin.users.delete"
    USERS_ROLE_ASSIGN = "admin.users.role.assign"
    USERS_ROLE_REMOVE = "admin.users.role.remove"
    
    # Revenue permissions
    REVENUE_READ = "admin.revenue.read"
    REVENUE_EXPORT = "admin.revenue.export"
    
    # Message permissions
    MESSAGES_READ = "admin.messages.read"
    MESSAGES_WRITE = "admin.messages.write"
    MESSAGES_UPDATE = "admin.messages.update"
    MESSAGES_DELETE = "admin.messages.delete"
    MESSAGES_MANAGE = "admin.messages.manage"
    MESSAGES_SEND = "admin.messages.send"
    
    # Notification permissions
    NOTIFICATIONS_READ = "admin.notifications.read"
    NOTIFICATIONS_SEND = "admin.notifications.send"
    
    # Audit permissions
    AUDIT_READ = "admin.audit.read"
    
    # Role and permission management
    ROLES_READ = "admin.roles.read"
    ROLES_CREATE = "admin.roles.create"
    ROLES_UPDATE = "admin.roles.update"
    ROLES_DELETE = "admin.roles.delete"
    
    PERMISSIONS_READ = "admin.permissions.read"
    PERMISSIONS_CREATE = "admin.permissions.create"
    PERMISSIONS_ASSIGN = "admin.permissions.assign"


# Role constants
class Roles:
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MODERATOR = "moderator"
    SUPPORT = "support"
    USER = "user"


def require_permission(permission_name: str):
    """Decorator to require a specific permission for an endpoint"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # This will be implemented in the dependency injection
            pass
        return wrapper
    return decorator


def require_any_permission(permission_names: List[str]):
    """Decorator to require any of the specified permissions"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # This will be implemented in the dependency injection
            pass
        return wrapper
    return decorator
