#!/usr/bin/env python3
"""
User Management Router
Handles user CRUD operations and role management for admin panel
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import get_db
from models import User, Role, UserRole, Permission, RolePermission, AuditLog
from auth import get_current_user
from rbac import RBACService, AuditService, Permissions
from schemas import UserResponse, UserUpdateRequest, RoleAssignmentRequest

router = APIRouter(prefix="/admin/users", tags=["admin-users"])

def require_permission(permission_name: str):
    """Dependency to require a specific permission"""
    def dependency(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        if not RBACService.has_permission(db, current_user.id, permission_name):
            raise HTTPException(status_code=403, detail=f"Permission '{permission_name}' required")
        return current_user
    return dependency

@router.get("")
async def get_users(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    role_filter: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: User = Depends(require_permission(Permissions.USERS_READ))
):
    """Get all users with pagination and filtering"""
    
    offset = (page - 1) * limit
    
    # Build query
    query = db.query(User)
    
    # Apply filters
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (User.name.ilike(search_term)) |
            (User.surname.ilike(search_term)) |
            (User.email.ilike(search_term)) |
            (User.username.ilike(search_term))
        )
    
    if status == "active":
        query = query.filter(User.id.in_(
            db.query(UserRole.user_id).filter(UserRole.is_active == True)
        ))
    elif status == "inactive":
        query = query.filter(~User.id.in_(
            db.query(UserRole.user_id).filter(UserRole.is_active == True)
        ))
    
    # Get total count
    total = query.count()
    
    # Get paginated results
    users = query.offset(offset).limit(limit).all()
    
    # Get roles for each user
    user_data = []
    for user in users:
        user_roles = db.query(UserRole).filter(
            UserRole.user_id == user.id,
            UserRole.is_active == True
        ).all()
        
        roles = []
        for user_role in user_roles:
            role = db.query(Role).filter(Role.id == user_role.role_id).first()
            if role:
                roles.append({
                    "id": role.id,
                    "name": role.name,
                    "description": role.description,
                    "assigned_at": user_role.assigned_at.isoformat() if user_role.assigned_at else None,
                    "assigned_by": user_role.assigned_by
                })
        
        # Get all permissions for this user
        permissions = RBACService.get_user_permissions(db, user.id)
        
        user_data.append({
            "id": user.id,
            "name": user.name,
            "surname": user.surname,
            "email": user.email,
            "phone": user.phone,
            "username": user.username,
            "profile_img": user.profile_img,
            "created_at": user.created_at.isoformat(),
            "roles": roles,
            "permissions": permissions,
            "total_permissions": len(permissions),
            "is_active": len(user_roles) > 0
        })
    
    # Filter by role if specified
    if role_filter:
        user_data = [user for user in user_data if any(role["name"] == role_filter for role in user["roles"])]
    
    AuditService.log_action(
        db=db,
        user_id=admin.id,
        action="users.list",
        resource_type="users",
        details={
            "filters": {
                "search": search,
                "role_filter": role_filter,
                "status": status
            },
            "page": page,
            "limit": limit,
            "total": total
        },
        request=request
    )
    
    return {
        "users": user_data,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit
    }

@router.get("/roles/available")
async def get_available_roles(
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(require_permission(Permissions.USERS_READ))
):
    """Get all available roles for assignment"""
    
    roles = db.query(Role).all()
    
    role_data = []
    for role in roles:
        # Get permissions for this role
        role_permissions = db.query(RolePermission).filter(
            RolePermission.role_id == role.id
        ).all()
        
        permissions = []
        for role_perm in role_permissions:
            permission = db.query(Permission).filter(
                Permission.id == role_perm.permission_id
            ).first()
            if permission:
                permissions.append({
                    "id": permission.id,
                    "name": permission.name,
                    "description": permission.description
                })
        
        role_data.append({
            "id": role.id,
            "name": role.name,
            "description": role.description,
            "permissions": permissions,
            "permission_count": len(permissions)
        })
    
    return {"roles": role_data}

@router.get("/stats")
async def get_user_stats(
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(require_permission(Permissions.USERS_READ))
):
    """Get user statistics"""
    
    total_users = db.query(User).count()
    
    # Users with roles
    users_with_roles = db.query(UserRole.user_id).distinct().count()
    
    # Users by role
    role_stats = []
    roles = db.query(Role).all()
    for role in roles:
        count = db.query(UserRole).filter(
            UserRole.role_id == role.id,
            UserRole.is_active == True
        ).count()
        role_stats.append({
            "role_name": role.name,
            "user_count": count
        })
    
    # Recent registrations (last 30 days)
    from datetime import timedelta
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_registrations = db.query(User).filter(
        User.created_at >= thirty_days_ago
    ).count()
    
    AuditService.log_action(
        db=db,
        user_id=admin.id,
        action="user.stats.view",
        resource_type="users",
        request=request
    )
    
    return {
        "total_users": total_users,
        "users_with_roles": users_with_roles,
        "users_without_roles": total_users - users_with_roles,
        "role_distribution": role_stats,
        "recent_registrations": recent_registrations
    }

@router.get("/{user_id}")
async def get_user(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_permission(Permissions.USERS_READ))
):
    """Get detailed user information"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user roles
    user_roles = db.query(UserRole).filter(
        UserRole.user_id == user.id,
        UserRole.is_active == True
    ).all()
    
    roles = []
    for user_role in user_roles:
        role = db.query(Role).filter(Role.id == user_role.role_id).first()
        if role:
            # Get permissions for this role
            role_permissions = db.query(RolePermission).filter(
                RolePermission.role_id == role.id
            ).all()
            
            permissions = []
            for role_perm in role_permissions:
                permission = db.query(Permission).filter(
                    Permission.id == role_perm.permission_id
                ).first()
                if permission:
                    permissions.append({
                        "id": permission.id,
                        "name": permission.name,
                        "description": permission.description,
                        "resource": permission.resource,
                        "action": permission.action
                    })
            
            roles.append({
                "id": role.id,
                "name": role.name,
                "description": role.description,
                "assigned_at": user_role.assigned_at.isoformat(),
                "assigned_by": user_role.assigned_by,
                "permissions": permissions
            })
    
    # Get all permissions for this user
    all_permissions = RBACService.get_user_permissions(db, user.id)
    
    # Get user activity (recent audit logs)
    recent_activity = db.query(AuditLog).filter(
        AuditLog.user_id == user.id
    ).order_by(AuditLog.created_at.desc()).limit(10).all()
    
    activity = []
    for log in recent_activity:
        activity.append({
            "id": log.id,
            "action": log.action,
            "resource_type": log.resource_type,
            "success": log.success,
            "created_at": log.created_at.isoformat(),
            "ip_address": log.ip_address
        })
    
    AuditService.log_action(
        db=db,
        user_id=admin.id,
        action="user.view",
        resource_type="user",
        resource_id=user_id,
        request=request
    )
    
    return {
        "id": user.id,
        "name": user.name,
        "surname": user.surname,
        "email": user.email,
        "phone": user.phone,
        "username": user.username,
        "profile_img": user.profile_img,
        "created_at": user.created_at.isoformat(),
        "roles": roles,
        "permissions": all_permissions,
        "total_permissions": len(all_permissions),
        "is_active": len(user_roles) > 0,
        "recent_activity": activity
    }

@router.put("/{user_id}")
async def update_user(
    request: Request,
    user_id: int,
    user_data: UserUpdateRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_permission(Permissions.USERS_UPDATE))
):
    """Update user information"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update user fields
    if user_data.name is not None:
        user.name = user_data.name
    if user_data.surname is not None:
        user.surname = user_data.surname
    if user_data.phone is not None:
        user.phone = user_data.phone
    if user_data.username is not None:
        user.username = user_data.username
    if user_data.profile_img is not None:
        user.profile_img = user_data.profile_img
    
    db.commit()
    db.refresh(user)
    
    AuditService.log_action(
        db=db,
        user_id=admin.id,
        action="user.update",
        resource_type="user",
        resource_id=user_id,
        details={"updated_fields": user_data.dict(exclude_unset=True)},
        request=request
    )
    
    return {"message": "User updated successfully", "user_id": user_id}

@router.post("/{user_id}/roles")
async def assign_role(
    request: Request,
    user_id: int,
    role_data: RoleAssignmentRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_permission(Permissions.USERS_ROLE_ASSIGN))
):
    """Assign a role to a user"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        user_role = RBACService.assign_role_to_user(
            db=db,
            user_id=user_id,
            role_name=role_data.role_name,
            assigned_by=admin.id,
            expires_at=role_data.expires_at
        )
        
        AuditService.log_action(
            db=db,
            user_id=admin.id,
            action="user.role.assign",
            resource_type="user_role",
            resource_id=user_role.id,
            details={
                "target_user_id": user_id,
                "role_name": role_data.role_name,
                "expires_at": role_data.expires_at.isoformat() if role_data.expires_at else None
            },
            request=request
        )
        
        return {"message": f"Role '{role_data.role_name}' assigned successfully", "user_role_id": user_role.id}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{user_id}/roles/{role_name}")
async def remove_role(
    request: Request,
    user_id: int,
    role_name: str,
    db: Session = Depends(get_db),
    admin: User = Depends(require_permission(Permissions.USERS_ROLE_REMOVE))
):
    """Remove a role from a user"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        RBACService.remove_role_from_user(db, user_id, role_name, admin.id)
        
        AuditService.log_action(
            db=db,
            user_id=admin.id,
            action="user.role.remove",
            resource_type="user_role",
            details={
                "target_user_id": user_id,
                "role_name": role_name
            },
            request=request
        )
        
        return {"message": f"Role '{role_name}' removed successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
