from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Order, OrderItem, CartItem, User, Notification
from schemas import OrderCreate, OrderResponse, OrderListResponse
from auth import get_current_user
from inventory_service import InventoryService

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/checkout", response_model=OrderResponse)
def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new order from cart items."""
    # Get user's cart items
    cart_items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()
    
    if not cart_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart is empty"
        )
    
    # Check inventory availability for all cart items
    for cart_item in cart_items:
        if not InventoryService.check_stock_availability(db, cart_item.product_id, cart_item.quantity):
            product = cart_item.product
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for '{product.title}'. Available: {product.stock_quantity}, Requested: {cart_item.quantity}"
            )
    
    # Calculate total amount
    total_amount = sum(item.quantity * item.product.price for item in cart_items)
    
    # Create order
    db_order = Order(
        user_id=current_user.id,
        total_amount=total_amount,
        payment_method=order_data.payment_method
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    # Create order items from cart items
    for cart_item in cart_items:
        order_item = OrderItem(
            order_id=db_order.id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity,
            price=cart_item.product.price  # Snapshot of price at purchase time
        )
        db.add(order_item)
    
    # Process inventory reduction
    try:
        InventoryService.process_order_stock_reduction(db, db_order.id, current_user.id)
    except HTTPException as e:
        # Rollback order creation if inventory update fails
        db.rollback()
        raise e
    
    # Clear cart after order creation
    db.query(CartItem).filter(CartItem.user_id == current_user.id).delete()
    
    # Create notification for admin about new order
    # Create notification for admin
    from utils.notification_utils import NotificationUtils
    NotificationUtils.notify_new_order(db, db_order)
    
    db.commit()
    db.refresh(db_order)
    return db_order

@router.post("/create", response_model=OrderResponse)
def create_order_direct(
    order_data: dict,
    db: Session = Depends(get_db)
):
    """Create a new order directly (for payment integration without auth)."""
    try:
        # Extract data from request
        user_id = order_data.get("user_id", 1)  # Default to user 1 for demo
        total_amount = order_data.get("total_amount")
        payment_method = order_data.get("payment_method")
        items = order_data.get("items", [])
        shipping_address = order_data.get("shipping_address")
        notes = order_data.get("notes")
        
        if not all([total_amount, payment_method, items]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing required fields: total_amount, payment_method, items"
            )
        
        # Create order
        db_order = Order(
            user_id=user_id,
            total_amount=total_amount,
            payment_method=payment_method,
            status="pending"
        )
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        
        # Create order items
        for item in items:
            order_item = OrderItem(
                order_id=db_order.id,
                product_id=item["product_id"],
                quantity=item["quantity"],
                price=item["price"]
            )
            db.add(order_item)
        
        # Create notification for admin about new order
        # Create notification for admin
        from utils.notification_utils import NotificationUtils
        NotificationUtils.notify_new_order(db, db_order)
        
        db.commit()
        db.refresh(db_order)
        return db_order
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create order: {str(e)}"
        )

@router.get("/", response_model=OrderListResponse)
def get_user_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's order history."""
    orders = db.query(Order).filter(Order.user_id == current_user.id)
    total = orders.count()
    orders = orders.offset(skip).limit(limit).all()
    
    return OrderListResponse(
        orders=orders,
        total=total,
        page=skip // limit + 1,
        size=limit
    )

@router.get("/user/count")
def get_user_order_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get count of orders made by the current user."""
    count = db.query(Order).filter(Order.user_id == current_user.id).count()
    return {"count": count}

@router.get("/demo/list", response_model=OrderListResponse)
def get_demo_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get demo orders without authentication (for Flutter app testing)."""
    try:
        # Get all orders for demo purposes (user_id = 1)
        orders = db.query(Order).filter(Order.user_id == 1)
        total = orders.count()
        orders = orders.offset(skip).limit(limit).all()
        
        return OrderListResponse(
            orders=orders,
            total=total,
            page=skip // limit + 1,
            size=limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch orders: {str(e)}"
        )

@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific order by ID."""
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return order

@router.get("/demo/{order_id}", response_model=OrderResponse)
def get_demo_order(
    order_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific order by ID without authentication (for Flutter app testing)."""
    try:
        # Get order for demo purposes (user_id = 1)
        order = db.query(Order).filter(
            Order.id == order_id,
            Order.user_id == 1
        ).first()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        return order
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch order: {str(e)}"
        )

@router.put("/{order_id}/cancel")
def cancel_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel an order (only if status is pending)."""
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if order.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order cannot be cancelled"
        )
    
    order.status = "cancelled"
    db.commit()
    return {"message": "Order cancelled successfully"}
