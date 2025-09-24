from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import json

from database import get_db
from models import User, Product, Order, OrderItem, Revenue, Message, Notification
from schemas import UserResponse, ProductResponse, OrderResponse, MessageResponse, NotificationResponse, ProductDiscontinueRequest
from auth import get_current_user
from rbac import RBACService, AuditService, Permissions
from sqlalchemy import func, and_, or_
from sqlalchemy.orm import joinedload
from websocket_manager import manager

router = APIRouter(prefix="/admin", tags=["admin"])

def get_admin_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ensure the current user has admin access"""
    # Check if user has any admin permissions
    user_permissions = RBACService.get_user_permissions(db, current_user.id)
    
    # Check for any admin permission
    admin_permissions = [
        Permissions.DASHBOARD_READ,
        Permissions.PRODUCTS_READ,
        Permissions.ORDERS_READ,
        Permissions.USERS_READ,
        Permissions.REVENUE_READ,
        Permissions.MESSAGES_READ,
        Permissions.NOTIFICATIONS_READ,
        Permissions.AUDIT_READ
    ]
    
    if not any(perm in user_permissions for perm in admin_permissions):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return current_user

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

@router.get("/dashboard")
async def get_dashboard_stats(
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Get dashboard statistics"""
    try:
        # Calculate date ranges
        today = datetime.utcnow().date()
        thirty_days_ago = today - timedelta(days=30)
        
        # Total counts
        total_users = db.query(User).count()
        total_products = db.query(Product).count()
        total_orders = db.query(Order).count()
        pending_approvals = db.query(Order).filter(Order.status == "pending").count()
        
        # Active users (users who have logged in within the last 30 days)
        active_users = db.query(User).filter(
            User.created_at >= thirty_days_ago
        ).count()
        
        # Total revenue
        total_revenue = db.query(func.sum(Revenue.amount)).scalar() or 0
        
        # Revenue trend (last 30 days) - simplified approach
        revenue_trend = []
        for i in range(30):
            date = today - timedelta(days=i)
            start_of_day = datetime.combine(date, datetime.min.time())
            end_of_day = datetime.combine(date, datetime.max.time())
            
            # Get revenue from Revenue table for this date
            daily_revenue = db.query(func.sum(Revenue.amount)).filter(
                Revenue.created_at >= start_of_day,
                Revenue.created_at <= end_of_day
            ).scalar() or 0
            
            # Also include revenue from orders that were delivered on this date
            delivered_orders_revenue = db.query(func.sum(Order.total_amount)).filter(
                Order.updated_at >= start_of_day,
                Order.updated_at <= end_of_day,
                Order.status == 'delivered'
            ).scalar() or 0
            
            total_daily_revenue = float(daily_revenue) + float(delivered_orders_revenue)
            
            revenue_trend.append({
                "date": date.isoformat(),
                "revenue": total_daily_revenue
            })
        revenue_trend.reverse()
        
        # Top products by sales - simplified query
        try:
            top_products = db.query(
                Product.id,
                Product.title,
                func.count(OrderItem.id).label('total_sales'),
                func.sum(OrderItem.price * OrderItem.quantity).label('revenue')
            ).join(OrderItem, Product.id == OrderItem.product_id)\
             .group_by(Product.id, Product.title)\
             .order_by(func.sum(OrderItem.price * OrderItem.quantity).desc())\
             .limit(5).all()
            
            top_products_data = [
                {
                    "id": p.id,
                    "title": p.title,
                    "total_sales": p.total_sales,
                    "revenue": float(p.revenue or 0)
                }
                for p in top_products
            ]
        except Exception as e:
            print(f"Error getting top products: {e}")
            top_products_data = []
        
        # Top categories - simplified query
        try:
            top_categories = db.query(
                Product.category,
                func.count(Product.id).label('total_products'),
                func.sum(OrderItem.price * OrderItem.quantity).label('total_sales')
            ).join(OrderItem, Product.id == OrderItem.product_id)\
             .group_by(Product.category)\
             .order_by(func.sum(OrderItem.price * OrderItem.quantity).desc())\
             .limit(5).all()
            
            top_categories_data = [
                {
                    "category": c.category,
                    "total_products": c.total_products,
                    "total_sales": float(c.total_sales or 0)
                }
                for c in top_categories
            ]
        except Exception as e:
            print(f"Error getting top categories: {e}")
            top_categories_data = []
        
        # Log the dashboard access
        try:
            AuditService.log_action(
                db=db,
                user_id=admin.id,
                action="dashboard.access",
                resource_type="dashboard",
                details={"stats_requested": True},
                request=request
            )
        except Exception as e:
            print(f"Error logging dashboard access: {e}")
        
        return {
            "total_revenue": float(total_revenue),
            "total_users": total_users,
            "total_products": total_products,
            "total_orders": total_orders,
            "pending_approvals": pending_approvals,
            "active_users": active_users,
            "revenue_trend": revenue_trend,
            "top_products": top_products_data,
            "top_categories": top_categories_data
        }
    except Exception as e:
        print(f"Dashboard error: {e}")
        # Return a basic response with error information
        return {
            "total_revenue": 0.0,
            "total_users": 0,
            "total_products": 0,
            "total_orders": 0,
            "pending_approvals": 0,
            "active_users": 0,
            "revenue_trend": [],
            "top_products": [],
            "top_categories": [],
            "error": str(e)
        }

@router.get("/test-dashboard")
async def test_dashboard(
    db: Session = Depends(get_db)
):
    """Simple test endpoint to check basic database connectivity"""
    try:
        # Test basic queries
        total_users = db.query(User).count()
        total_products = db.query(Product).count()
        total_orders = db.query(Order).count()
        total_revenue = db.query(func.sum(Revenue.amount)).scalar() or 0
        
        return {
            "status": "success",
            "message": "Database connectivity test passed",
            "data": {
                "total_users": total_users,
                "total_products": total_products,
                "total_orders": total_orders,
                "total_revenue": float(total_revenue)
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Database connectivity test failed: {str(e)}",
            "error": str(e)
        }



@router.get("/products")
async def get_products(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=1000),
    category: Optional[str] = None,
    status: Optional[str] = None,
    discontinued: Optional[bool] = None,
    seller_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    search: Optional[str] = None,
    created_via: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Get products with filters and pagination"""
    
    query = db.query(Product).join(User, Product.seller_id == User.id)
    
    # Apply filters
    if category:
        query = query.filter(Product.category == category)
    if status:
        if status == "approved":
            query = query.filter(Product.approved == True)
        elif status == "pending":
            query = query.filter(Product.approved == False)
    if discontinued is not None:
        query = query.filter(Product.discontinued == discontinued)
    if seller_id:
        query = query.filter(Product.seller_id == seller_id)
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Product.title.ilike(search_filter),
                Product.description.ilike(search_filter),
                User.name.ilike(search_filter),
                User.surname.ilike(search_filter)
            )
        )
    if created_via:
        query = query.filter(Product.created_via == created_via)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * limit
    products = query.offset(offset).limit(limit).all()
    
    # Convert to response format
    products_data = []
    for product in products:
        product_dict = {
            "id": product.id,
            "title": product.title,
            "description": product.description,
            "price": float(product.price),
            "category": product.category,
            "images": product.images or [],
            "seller_id": product.seller_id,
            "seller": {
                "id": product.seller.id,
                "name": product.seller.name,
                "surname": product.seller.surname,
                "email": product.seller.email,
                "phone": product.seller.phone,
                "username": product.seller.username,
                "profile_img": product.seller.profile_img,
                "created_at": product.seller.created_at.isoformat()
            },
            "approved": product.approved,
            "discontinued": product.discontinued,
            "status": "approved" if product.approved else "pending",
            "created_at": product.created_at.isoformat(),
            "updated_at": product.created_at.isoformat(),  # Use created_at since updated_at doesn't exist
            # Add inventory data
            "stock_quantity": product.stock_quantity,
            "initial_stock": product.initial_stock,
            "sold_quantity": product.sold_quantity,
            "is_out_of_stock": product.is_out_of_stock,
            "last_stock_update": product.last_stock_update.isoformat() if product.last_stock_update else None,
            "inventory": {
                "stock_quantity": product.stock_quantity,
                "initial_stock": product.initial_stock,
                "sold_quantity": product.sold_quantity,
                "low_stock_threshold": product.low_stock_threshold,
                "is_out_of_stock": product.is_out_of_stock,
                "last_stock_update": product.last_stock_update.isoformat() if product.last_stock_update else None
            }
        }
        products_data.append(product_dict)
    
    return {
        "data": products_data,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit
    }

@router.post("/products")
async def create_product(
    product_data: dict,
    db: Session = Depends(get_db),
    admin: User = Depends(require_permission(Permissions.PRODUCTS_CREATE))
):
    """Create a new product (admin can create products on behalf of any user)"""
    
    # Extract data from request
    title = product_data.get("title")
    description = product_data.get("description")
    price = product_data.get("price")
    category = product_data.get("category")
    images = product_data.get("images", [])
    approved = product_data.get("approved", True)
    seller_id = product_data.get("seller_id", admin.id)  # Default to admin if not specified
    
    # Extract inventory data
    stock_quantity = product_data.get("stock_quantity", 0)
    low_stock_threshold = product_data.get("low_stock_threshold", 5)
    
    # Validate required fields
    if not all([title, description, price, category]):
        raise HTTPException(status_code=400, detail="Missing required fields: title, description, price, category")
    
    # Validate price
    if price <= 0:
        raise HTTPException(status_code=400, detail="Price must be greater than 0")
    
    # Validate inventory fields
    if stock_quantity < 0:
        raise HTTPException(status_code=400, detail="Stock quantity cannot be negative")
    
    if low_stock_threshold < 0:
        raise HTTPException(status_code=400, detail="Low stock threshold cannot be negative")
    
    # Validate images (ensure it's a list)
    if not isinstance(images, list):
        images = []
    
    # Log the product creation attempt
    print(f"Creating product: {title}")
    print(f"Images provided: {images}")
    print(f"Image count: {len(images)}")
    print(f"Stock quantity: {stock_quantity}")
    
    # Check if seller exists
    seller = db.query(User).filter(User.id == seller_id).first()
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    
    # Create new product with inventory fields
    new_product = Product(
        title=title,
        description=description,
        price=price,
        category=category,
        images=images,
        seller_id=seller_id,
        approved=approved,
        created_via='admin_web',  # Mark as created via admin web
        stock_quantity=stock_quantity,
        initial_stock=stock_quantity,
        sold_quantity=0,
        low_stock_threshold=low_stock_threshold,
        is_out_of_stock=stock_quantity == 0,
        last_stock_update=datetime.utcnow(),
        created_at=datetime.utcnow()
    )
    
    try:
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
        
        # Log initial stock if quantity > 0
        if stock_quantity > 0:
            from inventory_service import InventoryService
            InventoryService.log_stock_change(
                db=db,
                product_id=new_product.id,
                change_type="initial_stock",
                quantity_changed=stock_quantity,
                previous_stock=0,
                new_stock=stock_quantity,
                user_id=admin.id,
                reason="Initial stock setup during product creation"
            )
        
        # Log the action
        AuditService.log_action(
            db=db,
            user_id=admin.id,
            action="product_created",
            resource_type="product",
            resource_id=new_product.id,
            details={
                "product_title": title,
                "seller_id": seller_id,
                "approved": approved,
                "stock_quantity": stock_quantity,
                "low_stock_threshold": low_stock_threshold
            }
        )
        
        return {
            "message": "Product created successfully",
            "data": {
                "id": new_product.id,
                "title": new_product.title,
                "description": new_product.description,
                "price": float(new_product.price),
                "category": new_product.category,
                "images": new_product.images or [],
                "seller_id": new_product.seller_id,
                "seller": {
                    "id": seller.id,
                    "name": seller.name,
                    "surname": seller.surname,
                    "email": seller.email,
                    "phone": seller.phone,
                    "username": seller.username,
                    "profile_img": seller.profile_img,
                    "created_at": seller.created_at.isoformat()
                },
                "status": "approved" if new_product.approved else "pending",
                "inventory": {
                    "stock_quantity": new_product.stock_quantity,
                    "initial_stock": new_product.initial_stock,
                    "sold_quantity": new_product.sold_quantity,
                    "low_stock_threshold": new_product.low_stock_threshold,
                    "is_out_of_stock": new_product.is_out_of_stock,
                    "last_stock_update": new_product.last_stock_update.isoformat()
                },
                "created_at": new_product.created_at.isoformat(),
                "updated_at": new_product.created_at.isoformat()
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create product: {str(e)}")

@router.get("/products/{product_id}")
async def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Get a specific product"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {
        "id": product.id,
        "title": product.title,
        "description": product.description,
        "price": float(product.price),
        "category": product.category,

        "images": product.images or [],
        "seller_id": product.seller_id,
        "seller": {
            "id": product.seller.id,
            "name": product.seller.name,
            "surname": product.seller.surname,
            "email": product.seller.email,
            "phone": product.seller.phone,
            "username": product.seller.username,
            "profile_img": product.seller.profile_img,
            "created_at": product.seller.created_at.isoformat()
        },
        "approved": product.approved,
        "discontinued": product.discontinued,
        "status": "approved" if product.approved else "pending",
        "created_at": product.created_at.isoformat(),
        "updated_at": product.created_at.isoformat()  # Use created_at since updated_at doesn't exist
    }

@router.put("/products/{product_id}/approve")
async def approve_product(
    product_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_permission(Permissions.PRODUCTS_APPROVE))
):
    """Approve a product"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product.approved = True
    db.commit()
    
    # Create notification for the seller
    from utils.notification_utils import NotificationUtils
    NotificationUtils.notify_product_approved(db, product)
    
    return {"message": "Product approved successfully", "data": product}

@router.put("/products/{product_id}/reject")
async def reject_product(
    product_id: int,
    reason: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: User = Depends(require_permission(Permissions.PRODUCTS_REJECT))
):
    """Reject a product"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product.approved = False
    db.commit()
    
    # Create notification for the seller
    from utils.notification_utils import NotificationUtils
    NotificationUtils.notify_product_rejected(db, product, reason)
    
    return {"message": "Product rejected", "data": product}

@router.delete("/products/{product_id}")
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_permission(Permissions.PRODUCTS_DELETE))
):
    """Delete a product permanently"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Delete related inventory logs first
    from models import InventoryLog
    db.query(InventoryLog).filter(InventoryLog.product_id == product_id).delete()
    
    # Delete related cart items
    from models import CartItem
    db.query(CartItem).filter(CartItem.product_id == product_id).delete()
    
    # Delete related order items
    from models import OrderItem
    db.query(OrderItem).filter(OrderItem.product_id == product_id).delete()
    
    # Delete related favorites
    from models import Favorite
    db.query(Favorite).filter(Favorite.product_id == product_id).delete()
    
    # Delete related reviews (this should cascade automatically, but let's be explicit)
    from models import Review
    db.query(Review).filter(Review.product_id == product_id).delete()
    
    # Delete the product
    db.delete(product)
    db.commit()
    
    return {"message": "Product deleted successfully"}

@router.put("/products/{product_id}")
async def update_product(
    product_id: int,
    product_data: dict,
    db: Session = Depends(get_db),
    admin: User = Depends(require_permission(Permissions.PRODUCTS_UPDATE))
):
    """Update a product"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Update allowed fields
    allowed_fields = ['title', 'description', 'price', 'category', 'faculty', 'approved']
    inventory_fields = ['stock_quantity', 'low_stock_threshold']
    
    # Track if inventory was updated for logging
    inventory_updated = False
    previous_stock = product.stock_quantity
    
    for field, value in product_data.items():
        if field in allowed_fields:
            setattr(product, field, value)
        elif field in inventory_fields:
            # Validate inventory fields
            if field == 'stock_quantity' and value < 0:
                raise HTTPException(status_code=400, detail="Stock quantity cannot be negative")
            elif field == 'low_stock_threshold' and value < 0:
                raise HTTPException(status_code=400, detail="Low stock threshold cannot be negative")
            
            setattr(product, field, value)
            inventory_updated = True
    
    # Update inventory-related fields
    if 'stock_quantity' in product_data:
        product.is_out_of_stock = product_data['stock_quantity'] == 0
        product.last_stock_update = datetime.utcnow()
    
    db.commit()
    db.refresh(product)
    
    # Log inventory change if stock was updated
    if inventory_updated and 'stock_quantity' in product_data:
        from inventory_service import InventoryService
        InventoryService.log_stock_change(
            db=db,
            product_id=product.id,
            change_type="stock_updated",
            quantity_changed=product_data['stock_quantity'] - previous_stock,
            previous_stock=previous_stock,
            new_stock=product_data['stock_quantity'],
            user_id=admin.id,
            reason="Stock updated via admin panel"
        )
    
    return {"message": "Product updated successfully", "data": product}

@router.patch("/products/{product_id}/discontinue")
async def admin_discontinue_product(
    product_id: int,
    discontinue_data: ProductDiscontinueRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_permission(Permissions.PRODUCTS_UPDATE))
):
    """Admin endpoint to mark a product as discontinued or re-enable it."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Update the discontinued status
    product.discontinued = discontinue_data.discontinued
    
    db.commit()
    db.refresh(product)
    
    # Log the action
    action = "discontinued" if discontinue_data.discontinued else "re-enabled"
    AuditService.log_action(
        db=db,
        user_id=admin.id,
        action=f"product_{action}",
        resource_type="product",
        resource_id=product.id,
        details={
            "product_title": product.title,
            "discontinued": discontinue_data.discontinued,
            "reason": discontinue_data.reason
        }
    )
    
    return {
        "message": f"Product {action} successfully",
        "data": {
            "id": product.id,
            "title": product.title,
            "discontinued": product.discontinued
        }
    }

@router.get("/orders")
async def get_orders(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    buyer_id: Optional[int] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Get orders with filters and pagination"""
    
    # Query orders with buyer and items relationships loaded
    query = db.query(Order).options(
        joinedload(Order.buyer),
        joinedload(Order.items).joinedload(OrderItem.product)
    )
    
    # Apply filters
    if status:
        query = query.filter(Order.status == status)
    if buyer_id:
        query = query.filter(Order.user_id == buyer_id)
    if date_from:
        query = query.filter(Order.created_at >= date_from)
    if date_to:
        query = query.filter(Order.created_at <= date_to)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * limit
    orders = query.offset(offset).limit(limit).all()
    
    # Convert to response format
    orders_data = []
    for order in orders:
        order_dict = {
            "id": order.id,
            "buyer_id": order.user_id,
            "buyer": {
                "id": order.buyer.id,
                "name": order.buyer.name,
                "surname": order.buyer.surname,
                "email": order.buyer.email,
                "phone": order.buyer.phone,
                "username": order.buyer.username,
                "profile_img": order.buyer.profile_img,
                "created_at": order.buyer.created_at.isoformat()
            },
            "items": [
                {
                    "id": item.id,
                    "order_id": item.order_id,
                    "product_id": item.product_id,
                    "product": {
                        "id": item.product.id,
                        "title": item.product.title,
                        "price": float(item.product.price),
                        "images": item.product.images or []
                    },
                    "quantity": item.quantity,
                    "price": float(item.price)
                }
                for item in order.items
            ],
            "total_amount": float(order.total_amount),
            "status": order.status,
            "payment_method": order.payment_method,
            "created_at": order.created_at.isoformat(),
            "updated_at": order.created_at.isoformat()
        }
        orders_data.append(order_dict)
    
    return {
        "data": orders_data,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit
    }


@router.put("/orders/{order_id}/status")
async def update_order_status(
    order_id: int,
    status_data: dict,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Update order status"""
    
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Validate status
    valid_statuses = ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']
    new_status = status_data.get('status')
    
    if new_status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    
    # Store old status for logging
    old_status = order.status
    
    # Update order status
    order.status = new_status
    order.updated_at = datetime.utcnow()
    
    # Check if this order is being delivered and revenue hasn't been tracked yet
    revenue_tracked = False
    if (new_status == 'delivered' and old_status != 'delivered'):
        
        # Check if revenue already exists for this order
        existing_revenue = db.query(Revenue).filter(Revenue.order_id == order_id).first()
        
        if not existing_revenue:
            # Calculate revenue breakdown
            total_amount = order.total_amount
            commission_rate = 0.10  # 10% platform commission
            platform_fee = 5.0  # Fixed R5 platform fee
            commission = total_amount * commission_rate
            seller_revenue = total_amount - commission - platform_fee
            
            # Create revenue record
            revenue = Revenue(
                order_id=order_id,
                amount=total_amount,
                commission=commission,
                platform_fee=platform_fee,
                seller_revenue=seller_revenue,
                payment_method=order.payment_method
            )
            db.add(revenue)
            revenue_tracked = True
    
    try:
        db.commit()
        
        # Log the action
        AuditService.log_action(
            db=db,
            user_id=admin.id,
            action="order.status_update",
            resource_type="order",
            resource_id=order_id,
            details={
                "old_status": old_status, 
                "new_status": new_status,
                "revenue_tracked": revenue_tracked,
                "payment_method": order.payment_method
            },
            request=None
        )
        
        return {
            "success": True,
            "message": f"Order status updated to {new_status}",
            "data": {
                "id": order.id,
                "status": order.status,
                "updated_at": order.updated_at.isoformat(),
                "revenue_tracked": revenue_tracked
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update order status: {str(e)}")



@router.get("/revenue")
async def get_revenue(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    payment_method: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Get revenue data with filters and pagination"""
    
    query = db.query(Revenue)
    
    if date_from:
        query = query.filter(Revenue.created_at >= date_from)
    if date_to:
        query = query.filter(Revenue.created_at <= date_to)
    if payment_method:
        query = query.filter(Revenue.payment_method == payment_method)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * limit
    revenues = query.offset(offset).limit(limit).all()
    
    return {
        "data": [
            {
                "id": revenue.id,
                "order_id": revenue.order_id,
                "amount": float(revenue.amount),
                "commission": float(revenue.commission),
                "platform_fee": float(revenue.platform_fee),
                "seller_revenue": float(revenue.seller_revenue),
                "payment_method": revenue.payment_method,
                "created_at": revenue.created_at.isoformat()
            }
            for revenue in revenues
        ],
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit
    }

@router.get("/revenue/summary")
async def get_revenue_summary(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Get revenue summary statistics"""
    
    query = db.query(Revenue)
    
    if date_from:
        query = query.filter(Revenue.created_at >= date_from)
    if date_to:
        query = query.filter(Revenue.created_at <= date_to)
    
    # Calculate summary statistics
    total_revenue = query.with_entities(func.sum(Revenue.amount)).scalar() or 0
    total_commission = query.with_entities(func.sum(Revenue.commission)).scalar() or 0
    total_platform_fees = query.with_entities(func.sum(Revenue.platform_fee)).scalar() or 0
    total_seller_revenue = query.with_entities(func.sum(Revenue.seller_revenue)).scalar() or 0
    
    # Payment method breakdown
    payment_methods = db.query(
        Revenue.payment_method,
        func.count(Revenue.id).label('count'),
        func.sum(Revenue.amount).label('total_amount')
    ).group_by(Revenue.payment_method).all()
    
    payment_breakdown = [
        {
            "method": pm.payment_method,
            "count": pm.count,
            "total_amount": float(pm.total_amount or 0)
        }
        for pm in payment_methods
    ]
    
    # Daily revenue for the last 7 days
    today = datetime.utcnow().date()
    daily_revenue = []
    for i in range(7):
        date = today - timedelta(days=i)
        daily_total = db.query(func.sum(Revenue.amount)).filter(
            func.date(Revenue.created_at) == date
        ).scalar() or 0
        daily_revenue.append({
            "date": date.isoformat(),
            "revenue": float(daily_total)
        })
    daily_revenue.reverse()
    
    return {
        "summary": {
            "total_revenue": float(total_revenue),
            "total_commission": float(total_commission),
            "total_platform_fees": float(total_platform_fees),
            "total_seller_revenue": float(total_seller_revenue),
            "total_transactions": query.count()
        },
        "payment_breakdown": payment_breakdown,
        "daily_revenue": daily_revenue
    }

@router.get("/revenue/export")
async def export_revenue(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    format: str = Query("csv", regex="^(csv|json)$"),
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Export revenue data"""
    
    query = db.query(Revenue)
    
    if date_from:
        query = query.filter(Revenue.created_at >= date_from)
    if date_to:
        query = query.filter(Revenue.created_at <= date_to)
    
    revenues = query.all()
    
    if format == "csv":
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Order ID', 'Amount', 'Commission', 'Platform Fee', 'Seller Revenue', 'Payment Method', 'Created At'])
        
        for revenue in revenues:
            writer.writerow([
                revenue.id,
                revenue.order_id,
                revenue.amount,
                revenue.commission,
                revenue.platform_fee,
                revenue.seller_revenue,
                revenue.payment_method,
                revenue.created_at.isoformat()
            ])
        
        return {
            "data": output.getvalue(),
            "filename": f"revenue_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv",
            "content_type": "text/csv"
        }
    else:
        return {
            "data": [
                {
                    "id": revenue.id,
                    "order_id": revenue.order_id,
                    "amount": float(revenue.amount),
                    "commission": float(revenue.commission),
                    "platform_fee": float(revenue.platform_fee),
                    "seller_revenue": float(revenue.seller_revenue),
                    "payment_method": revenue.payment_method,
                    "created_at": revenue.created_at.isoformat()
                }
                for revenue in revenues
            ],
            "filename": f"revenue_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json",
            "content_type": "application/json"
        }

@router.get("/messages")
async def get_admin_messages(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    conversation_id: Optional[str] = None,
    user_id: Optional[int] = None,
    message_type: Optional[str] = None,
    is_read: Optional[bool] = None,
    is_important: Optional[bool] = None,
    search: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: User = Depends(require_permission(Permissions.MESSAGES_READ))
):
    """Get all messages for admin management"""
    
    # Base query - get all messages
    query = db.query(Message).options(
        joinedload(Message.sender),
        joinedload(Message.receiver),
        joinedload(Message.parent_message)
    )
    
    # Apply filters
    if conversation_id:
        query = query.filter(Message.conversation_id == conversation_id)
    if user_id:
        query = query.filter(
            or_(Message.sender_id == user_id, Message.receiver_id == user_id)
        )
    if message_type:
        query = query.filter(Message.message_type == message_type)
    if is_read is not None:
        query = query.filter(Message.is_read == is_read)
    if is_important is not None:
        query = query.filter(Message.is_important == is_important)
    if search:
        query = query.filter(Message.message.contains(search))
    if date_from:
        query = query.filter(Message.created_at >= date_from)
    if date_to:
        query = query.filter(Message.created_at <= date_to)
    
    # Get total count
    total = query.count()
    
    # Apply pagination and ordering
    offset = (page - 1) * limit
    messages = query.order_by(Message.created_at.desc()).offset(offset).limit(limit).all()
    
    # Convert to response format
    messages_data = []
    for message in messages:
        message_dict = {
            "id": message.id,
            "sender_id": message.sender_id,
            "receiver_id": message.receiver_id,
            "message": message.message,
            "message_type": message.message_type,
            "conversation_id": message.conversation_id,
            "is_read": message.is_read,
            "is_important": message.is_important,
            "parent_message_id": message.parent_message_id,
            "created_at": message.created_at.isoformat(),
            "updated_at": message.updated_at.isoformat(),
            "sender": {
                "id": message.sender.id,
                "name": message.sender.name,
                "surname": message.sender.surname,
                "email": message.sender.email,
                "username": message.sender.username,
                "profile_img": message.sender.profile_img,
            },
            "receiver": {
                "id": message.receiver.id,
                "name": message.receiver.name,
                "surname": message.receiver.surname,
                "email": message.receiver.email,
                "username": message.receiver.username,
                "profile_img": message.receiver.profile_img,
            },
            "replies_count": len(message.replies) if message.replies else 0
        }
        messages_data.append(message_dict)
    
    return {
        "data": messages_data,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit
    }

@router.get("/messages/conversations")
async def get_admin_conversations(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    user_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: User = Depends(require_permission(Permissions.MESSAGES_READ))
):
    """Get all conversations for admin management"""
    
    # Get unique conversation IDs
    conversation_query = db.query(Message.conversation_id).distinct()
    if user_id:
        conversation_query = conversation_query.filter(
            or_(Message.sender_id == user_id, Message.receiver_id == user_id)
        )
    
    conversation_ids = [row[0] for row in conversation_query.all() if row[0]]
    
    conversations_data = []
    for conv_id in conversation_ids:
        # Get latest message in conversation
        latest_message = db.query(Message).filter(
            Message.conversation_id == conv_id
        ).order_by(Message.created_at.desc()).first()
        
        if latest_message:
            # Get participants in conversation
            participants = db.query(User).join(Message, or_(
                Message.sender_id == User.id,
                Message.receiver_id == User.id
            )).filter(Message.conversation_id == conv_id).distinct().all()
            
            # Get unread count for admin
            unread_count = db.query(Message).filter(
                Message.conversation_id == conv_id,
                Message.receiver_id == admin.id,
                Message.is_read == False
            ).count()
            
            conversation_dict = {
                "conversation_id": conv_id,
                "latest_message": {
                    "id": latest_message.id,
                    "message": latest_message.message,
                    "message_type": latest_message.message_type,
                    "created_at": latest_message.created_at.isoformat(),
                    "sender": {
                        "id": latest_message.sender.id,
                        "name": latest_message.sender.name,
                        "surname": latest_message.sender.surname,
                        "username": latest_message.sender.username,
                    }
                },
                "participants": [
                    {
                        "id": user.id,
                        "name": user.name,
                        "surname": user.surname,
                        "username": user.username,
                        "email": user.email,
                    }
                    for user in participants
                ],
                "unread_count": unread_count,
                "total_messages": db.query(Message).filter(
                    Message.conversation_id == conv_id
                ).count()
            }
            conversations_data.append(conversation_dict)
    
    # Apply pagination
    total = len(conversations_data)
    offset = (page - 1) * limit
    paginated_conversations = conversations_data[offset:offset + limit]
    
    return {
        "data": paginated_conversations,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit
    }

@router.get("/messages/conversations/{conversation_id}")
async def get_admin_conversation_messages(
    conversation_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    admin: User = Depends(require_permission(Permissions.MESSAGES_READ))
):
    """Get all messages in a specific conversation"""
    
    query = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).options(
        joinedload(Message.sender),
        joinedload(Message.receiver),
        joinedload(Message.parent_message)
    )
    
    # Get total count
    total = query.count()
    
    # Apply pagination and ordering
    offset = (page - 1) * limit
    messages = query.order_by(Message.created_at.asc()).offset(offset).limit(limit).all()
    
    # Convert to response format
    messages_data = []
    for message in messages:
        message_dict = {
            "id": message.id,
            "sender_id": message.sender_id,
            "receiver_id": message.receiver_id,
            "message": message.message,
            "message_type": message.message_type,
            "conversation_id": message.conversation_id,
            "is_read": message.is_read,
            "is_important": message.is_important,
            "parent_message_id": message.parent_message_id,
            "created_at": message.created_at.isoformat(),
            "updated_at": message.updated_at.isoformat(),
            "sender": {
                "id": message.sender.id,
                "name": message.sender.name,
                "surname": message.sender.surname,
                "email": message.sender.email,
                "username": message.sender.username,
                "profile_img": message.sender.profile_img,
            },
            "receiver": {
                "id": message.receiver.id,
                "name": message.receiver.name,
                "surname": message.receiver.surname,
                "email": message.receiver.email,
                "username": message.receiver.username,
                "profile_img": message.receiver.profile_img,
            },
            "replies": [
                {
                    "id": reply.id,
                    "message": reply.message,
                    "created_at": reply.created_at.isoformat(),
                    "sender": {
                        "id": reply.sender.id,
                        "name": reply.sender.name,
                        "username": reply.sender.username,
                    }
                }
                for reply in message.replies
            ] if message.replies else []
        }
        messages_data.append(message_dict)
    
    return {
        "data": messages_data,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit,
        "conversation_id": conversation_id
    }

@router.post("/messages/send")
async def admin_send_message(
    message_data: dict,
    db: Session = Depends(get_db),
    admin: User = Depends(require_permission(Permissions.MESSAGES_WRITE))
):
    """Send a message as admin"""
    
    try:
        receiver_id = message_data.get("receiver_id")
        message_content = message_data.get("message")
        conversation_id = message_data.get("conversation_id")
        message_type = message_data.get("message_type", "text")
        parent_message_id = message_data.get("parent_message_id")
        
        if not receiver_id or not message_content:
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        # Check if receiver exists
        receiver = db.query(User).filter(User.id == receiver_id).first()
        if not receiver:
            raise HTTPException(status_code=404, detail="Receiver not found")
        
        # Generate conversation ID if not provided
        if not conversation_id:
            # Check if there's already a conversation between these users
            existing_conversation = db.query(Message.conversation_id).filter(
                Message.conversation_id.isnot(None),
                or_(
                    and_(Message.sender_id == admin.id, Message.receiver_id == receiver_id),
                    and_(Message.sender_id == receiver_id, Message.receiver_id == admin.id)
                )
            ).first()
            
            if existing_conversation:
                conversation_id = existing_conversation.conversation_id
            else:
                # Create new conversation ID
                conversation_id = f"conv_{admin.id}_{receiver_id}_{int(datetime.utcnow().timestamp())}"
        
        # Create new message
        message = Message(
            sender_id=admin.id,
            receiver_id=receiver_id,
            message=message_content,
            message_type=message_type,
            conversation_id=conversation_id,
            parent_message_id=parent_message_id,
            created_at=datetime.utcnow()
        )
        
        db.add(message)
        db.commit()
        db.refresh(message)
        
        # Create notification for the receiver
        from utils.notification_utils import NotificationUtils
        NotificationUtils.notify_new_message(db, message)
        
        # Send real-time notification via WebSocket
        message_data = {
            "id": message.id,
            "sender_id": message.sender_id,
            "receiver_id": message.receiver_id,
            "message": message.message,
            "message_type": message.message_type,
            "conversation_id": message.conversation_id,
            "is_read": message.is_read,
            "is_important": message.is_important,
            "parent_message_id": message.parent_message_id,
            "created_at": message.created_at.isoformat(),
            "updated_at": message.updated_at.isoformat(),
            "sender": {
                "id": admin.id,
                "name": admin.name,
                "surname": admin.surname,
                "username": admin.username,
                "email": admin.email,
                "phone": admin.phone,
                "profile_img": admin.profile_img,
                "created_at": admin.created_at.isoformat()
            },
            "receiver": {
                "id": receiver.id,
                "name": receiver.name,
                "surname": receiver.surname,
                "username": receiver.username,
                "email": receiver.email,
                "phone": receiver.phone,
                "profile_img": receiver.profile_img,
                "created_at": receiver.created_at.isoformat()
            }
        }
        
        # Send real-time notification
        await manager.send_message_notification(
            message_data, 
            message.sender_id, 
            message.receiver_id, 
            message.conversation_id
        )
        
        # Return the created message
        return {
            "id": message.id,
            "message": message.message,
            "message_type": message.message_type,
            "conversation_id": message.conversation_id,
            "created_at": message.created_at.isoformat(),
            "sender": {
                "id": admin.id,
                "name": admin.name,
                "surname": admin.surname,
                "username": admin.username,
            },
            "receiver": {
                "id": receiver.id,
                "name": receiver.name,
                "surname": receiver.surname,
                "username": receiver.username,
            }
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error sending message: {str(e)}")

@router.put("/messages/{message_id}/read")
async def admin_mark_message_read(
    message_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_permission(Permissions.MESSAGES_UPDATE))
):
    """Mark a message as read"""
    
    try:
        message = db.query(Message).filter(Message.id == message_id).first()
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        
        message.is_read = True
        message.updated_at = datetime.utcnow()
        db.commit()
        
        return {"message": "Message marked as read", "message_id": message_id}
        
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error marking message as read: {str(e)}")

@router.put("/messages/{message_id}/important")
async def admin_toggle_message_important(
    message_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_permission(Permissions.MESSAGES_UPDATE))
):
    """Toggle message importance flag"""
    
    try:
        message = db.query(Message).filter(Message.id == message_id).first()
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        
        message.is_important = not message.is_important
        message.updated_at = datetime.utcnow()
        db.commit()
        
        return {
            "message": f"Message {'marked as' if message.is_important else 'unmarked from'} important",
            "message_id": message_id,
            "is_important": message.is_important
        }
        
    except HTTPException as he:
        raise he

@router.post("/messages/send-to-user")
async def admin_send_message_to_user(
    user_id: int,
    message_content: str,
    message_type: str = "admin_response",
    conversation_id: Optional[str] = None,
    parent_message_id: Optional[int] = None,
    db: Session = Depends(get_db),
    admin: User = Depends(require_permission(Permissions.MESSAGES_SEND))
):
    """Send a message from admin to a specific user"""
    
    try:
        # Check if target user exists
        target_user = db.query(User).filter(User.id == user_id).first()
        if not target_user:
            raise HTTPException(status_code=404, detail="Target user not found")
        
        # Create new message
        message = Message(
            sender_id=admin.id,
            receiver_id=user_id,
            message=message_content,
            message_type=message_type,
            conversation_id=conversation_id,
            parent_message_id=parent_message_id,
            is_important=True,  # Admin messages are marked as important by default
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(message)
        db.commit()
        db.refresh(message)
        
        # Create notification for the receiver
        from utils.notification_utils import NotificationUtils
        NotificationUtils.notify_new_message(db, message)
        
        return {
            "id": message.id,
            "message": message.message,
            "message_type": message.message_type,
            "conversation_id": message.conversation_id,
            "is_read": message.is_read,
            "is_important": message.is_important,
            "parent_message_id": message.parent_message_id,
            "created_at": message.created_at.isoformat(),
            "updated_at": message.updated_at.isoformat(),
            "sender": {
                "id": message.sender.id,
                "name": message.sender.name,
                "surname": message.sender.surname,
                "email": message.sender.email,
                "username": message.sender.username,
                "profile_img": message.sender.profile_img,
            },
            "receiver": {
                "id": message.receiver.id,
                "name": message.receiver.name,
                "surname": message.receiver.surname,
                "email": message.receiver.email,
                "username": message.receiver.username,
                "profile_img": message.receiver.profile_img,
            }
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error sending message: {str(e)}")

@router.get("/messages/unread-count")
async def get_admin_unread_messages_count(
    db: Session = Depends(get_db),
    admin: User = Depends(require_permission(Permissions.MESSAGES_READ))
):
    """Get count of unread messages for admin"""
    
    try:
        unread_count = db.query(Message).filter(
            Message.receiver_id == admin.id,
            Message.is_read == False
        ).count()
        
        return {"unread_count": unread_count}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting unread count: {str(e)}")

@router.delete("/messages/{message_id}")
async def admin_delete_message(
    message_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_permission(Permissions.MESSAGES_DELETE))
):
    """Delete a message (admin only)"""
    
    try:
        message = db.query(Message).filter(Message.id == message_id).first()
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        
        # Check if message has replies
        if message.replies:
            raise HTTPException(status_code=400, detail="Cannot delete message with replies")
        
        db.delete(message)
        db.commit()
        
        return {"message": "Message deleted successfully", "message_id": message_id}
        
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting message: {str(e)}")

@router.get("/messages/stats")
async def get_admin_message_stats(
    db: Session = Depends(get_db),
    admin: User = Depends(require_permission(Permissions.MESSAGES_READ))
):
    """Get message statistics for admin dashboard"""
    
    try:
        # Total messages
        total_messages = db.query(Message).count()
        
        # Unread messages
        unread_messages = db.query(Message).filter(Message.is_read == False).count()
        
        # Important messages
        important_messages = db.query(Message).filter(Message.is_important == True).count()
        
        # Messages by type
        message_types = db.query(Message.message_type, func.count(Message.id)).group_by(Message.message_type).all()
        
        # Recent activity (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_messages = db.query(Message).filter(Message.created_at >= week_ago).count()
        
        # Active conversations
        active_conversations = db.query(Message.conversation_id).distinct().count()
        
        return {
            "total_messages": total_messages,
            "unread_messages": unread_messages,
            "important_messages": important_messages,
            "recent_messages": recent_messages,
            "active_conversations": active_conversations,
            "message_types": dict(message_types)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting message stats: {str(e)}")

@router.get("/notifications")
async def get_notifications(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    unread_only: bool = Query(False),
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Get notifications for admin with pagination"""
    
    query = db.query(Notification).filter(
        Notification.user_id == admin.id,
        Notification.deleted_at.is_(None)  # Exclude deleted notifications
    )
    
    if unread_only:
        query = query.filter(Notification.is_read == False)
    
    # Get total count
    total = query.count()
    
    # Apply pagination and ordering (newest first)
    offset = (page - 1) * limit
    notifications = query.order_by(Notification.created_at.desc()).offset(offset).limit(limit).all()
    
    return {
        "data": [
            {
                "id": notification.id,
                "user_id": notification.user_id,
                "title": "Notification",
                "message": notification.message,
                "type": "info",
                "is_read": notification.is_read,
                "created_at": notification.created_at.isoformat()
            }
            for notification in notifications
        ],
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit,
        "unread_count": db.query(Notification).filter(
            Notification.user_id == admin.id,
            Notification.is_read == False,
            Notification.deleted_at.is_(None)  # Exclude deleted notifications
        ).count()
    }

@router.put("/notifications/{notification_id}/read")
async def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Mark a notification as read"""
    
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == admin.id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notification.is_read = True
    db.commit()
    
    return {"message": "Notification marked as read"}

@router.put("/notifications/read-all")
async def mark_all_notifications_as_read(
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Mark all notifications as read"""
    
    db.query(Notification).filter(
        Notification.user_id == admin.id,
        Notification.is_read == False
    ).update({"is_read": True})
    
    db.commit()
    
    return {"message": "All notifications marked as read"}

@router.get("/notifications/unread-count")
async def get_unread_notifications_count(
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Get count of unread notifications"""
    
    unread_count = db.query(Notification).filter(
        Notification.user_id == admin.id,
        Notification.is_read == False,
        Notification.deleted_at.is_(None)  # Exclude deleted notifications
    ).count()
    
    return {"unread_count": unread_count}

@router.delete("/notifications/{notification_id}")
async def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Delete a notification (soft delete)"""
    
    try:
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == admin.id,
            Notification.deleted_at.is_(None)  # Only delete if not already deleted
        ).first()
        
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found or already deleted")
        
        # Soft delete the notification
        notification.deleted_at = datetime.utcnow()
        db.commit()
        
        return {"message": "Notification deleted successfully"}
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting notification: {str(e)}")

@router.delete("/notifications")
async def delete_all_notifications(
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Delete all notifications for admin (soft delete)"""
    
    try:
        notifications = db.query(Notification).filter(
            Notification.user_id == admin.id,
            Notification.deleted_at.is_(None)
        ).all()
        
        deleted_count = 0
        for notification in notifications:
            notification.deleted_at = datetime.utcnow()
            deleted_count += 1
        
        db.commit()
        
        return {"message": f"Deleted {deleted_count} notifications successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting notifications: {str(e)}")



@router.get("/audit-logs")
async def get_audit_logs(
    request: Request,
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    success: Optional[bool] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=1000),
    db: Session = Depends(get_db),
    admin: User = Depends(require_permission(Permissions.AUDIT_READ))
):
    """Get audit logs with optional filters"""
    
    offset = (page - 1) * limit
    
    audit_logs = AuditService.get_audit_logs(
        db=db,
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        success=success,
        limit=limit,
        offset=offset
    )
    
    # Log the audit log access
    AuditService.log_action(
        db=db,
        user_id=admin.id,
        action="audit_logs.access",
        resource_type="audit_logs",
        details={
            "filters": {
                "user_id": user_id,
                "action": action,
                "resource_type": resource_type,
                "success": success
            },
            "page": page,
            "limit": limit
        },
        request=request
    )
    
    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "details": log.details,
            "ip_address": log.ip_address,
            "user_agent": log.user_agent,
            "success": log.success,
            "error_message": log.error_message,
            "created_at": log.created_at.isoformat()
        }
        for log in audit_logs
    ]

# ---------------- INVENTORY MANAGEMENT ENDPOINTS ----------------

@router.get("/products/inventory/low-stock")
async def get_low_stock_products(
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Get products with low stock (below threshold)."""
    try:
        from inventory_service import InventoryService
        products = InventoryService.get_low_stock_products(db, limit)
        return {
            "products": [
                {
                    "id": p.id,
                    "title": p.title,
                    "stock_quantity": p.stock_quantity,
                    "low_stock_threshold": p.low_stock_threshold,
                    "is_out_of_stock": p.is_out_of_stock
                }
                for p in products
            ],
            "total": len(products)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/products/inventory/out-of-stock")
async def get_out_of_stock_products(
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Get products that are out of stock."""
    try:
        from inventory_service import InventoryService
        products = InventoryService.get_out_of_stock_products(db, limit)
        return {
            "products": [
                {
                    "id": p.id,
                    "title": p.title,
                    "stock_quantity": p.stock_quantity,
                    "sold_quantity": p.sold_quantity
                }
                for p in products
            ],
            "total": len(products)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/products/{product_id}/inventory")
async def get_product_inventory(
    product_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Get inventory summary for a specific product."""
    try:
        from inventory_service import InventoryService
        inventory_summary = InventoryService.get_inventory_summary(db, product_id)
        return inventory_summary
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/products/{product_id}/inventory/stock")
async def update_product_stock(
    product_id: int,
    stock_data: dict,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Update product stock quantity (admin only)."""
    try:
        from inventory_service import InventoryService
        updated_product = InventoryService.update_stock(
            db=db,
            product_id=product_id,
            new_stock_quantity=stock_data.get("stock_quantity", 0),
            user_id=admin.id,
            reason=stock_data.get("reason", "Stock updated via admin panel")
        )
        return {"success": True, "data": updated_product}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/products/{product_id}/inventory/add-stock")
async def add_product_stock(
    product_id: int,
    stock_data: dict,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Add stock to existing product (admin only)."""
    try:
        from inventory_service import InventoryService
        updated_product = InventoryService.add_stock(
            db=db,
            product_id=product_id,
            quantity_to_add=stock_data.get("stock_quantity", 0),
            user_id=admin.id,
            reason=stock_data.get("reason", "Stock added via admin panel")
        )
        return {"success": True, "data": updated_product}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/products/{product_id}/inventory/remove-stock")
async def remove_product_stock(
    product_id: int,
    stock_data: dict,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Remove stock from existing product (admin only)."""
    try:
        from inventory_service import InventoryService
        updated_product = InventoryService.remove_stock(
            db=db,
            product_id=product_id,
            quantity_to_remove=stock_data.get("stock_quantity", 0),
            user_id=admin.id,
            reason=stock_data.get("reason", "Stock removed via admin panel")
        )
        return {"success": True, "data": updated_product}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/products/{product_id}/inventory/logs")
async def get_product_inventory_logs(
    product_id: int,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Get inventory logs for a specific product."""
    try:
        from inventory_service import InventoryService
        logs = InventoryService.get_inventory_logs(
            db=db,
            product_id=product_id,
            limit=limit,
            offset=offset
        )
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/debug/orders/{order_id}")
async def debug_order(
    order_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Debug endpoint to check order data"""
    
    # Get order with all relationships
    order = db.query(Order).options(
        joinedload(Order.buyer),
        joinedload(Order.items).joinedload(OrderItem.product)
    ).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Get raw database data
    raw_order = db.execute(
        "SELECT * FROM orders WHERE id = :order_id",
        {"order_id": order_id}
    ).fetchone()
    
    raw_user = db.execute(
        "SELECT * FROM users WHERE id = :user_id",
        {"user_id": order.user_id}
    ).fetchone()
    
    return {
        "order_id": order_id,
        "order_data": {
            "id": order.id,
            "user_id": order.user_id,
            "total_amount": float(order.total_amount),
            "status": order.status,
            "payment_method": order.payment_method,
            "created_at": order.created_at.isoformat()
        },
        "buyer_data": {
            "id": order.buyer.id,
            "name": order.buyer.name,
            "surname": order.buyer.surname,
            "email": order.buyer.email,
            "phone": order.buyer.phone,
            "username": order.buyer.username
        },
        "raw_order_data": dict(raw_order) if raw_order else None,
        "raw_user_data": dict(raw_user) if raw_user else None
    }