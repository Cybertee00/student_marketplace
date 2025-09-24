#!/usr/bin/env python3
"""
Inventory Management Service
Handles product inventory tracking, stock updates, and inventory logs
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime
from fastapi import HTTPException

from models import Product, InventoryLog, Order, OrderItem
from schemas import StockUpdateRequest, InventoryLogCreate


class InventoryService:
    """Service for managing product inventory"""
    
    @staticmethod
    def create_product_with_stock(
        db: Session, 
        product_data: dict, 
        initial_stock: int,
        user_id: int
    ) -> Product:
        """Create a new product with initial stock"""
        # Set inventory fields
        product_data.update({
            "stock_quantity": initial_stock,
            "initial_stock": initial_stock,
            "sold_quantity": 0,
            "is_out_of_stock": initial_stock == 0,
            "last_stock_update": datetime.utcnow()
        })
        
        # Create product
        product = Product(**product_data)
        db.add(product)
        db.commit()
        db.refresh(product)
        
        # Log initial stock
        if initial_stock > 0:
            InventoryService.log_stock_change(
                db=db,
                product_id=product.id,
                change_type="initial_stock",
                quantity_changed=initial_stock,
                previous_stock=0,
                new_stock=initial_stock,
                user_id=user_id,
                reason="Initial stock setup"
            )
        
        return product
    
    @staticmethod
    def update_stock(
        db: Session,
        product_id: int,
        new_stock_quantity: int,
        user_id: int,
        reason: Optional[str] = None
    ) -> Product:
        """Update product stock quantity - Admin products only"""
        product = db.query(Product).filter(
            and_(
                Product.id == product_id,
                Product.created_via == 'admin_web'  # Only admin products
            )
        ).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found or not an admin product")
        
        previous_stock = product.stock_quantity
        quantity_changed = new_stock_quantity - previous_stock
        
        # Update product stock
        product.stock_quantity = new_stock_quantity
        product.is_out_of_stock = new_stock_quantity == 0
        product.last_stock_update = datetime.utcnow()
        
        db.commit()
        db.refresh(product)
        
        # Log the stock change
        InventoryService.log_stock_change(
            db=db,
            product_id=product_id,
            change_type="stock_updated",
            quantity_changed=quantity_changed,
            previous_stock=previous_stock,
            new_stock=new_stock_quantity,
            user_id=user_id,
            reason=reason or "Manual stock update"
        )
        
        return product
    
    @staticmethod
    def add_stock(
        db: Session,
        product_id: int,
        quantity_to_add: int,
        user_id: int,
        reason: Optional[str] = None
    ) -> Product:
        """Add stock to existing product - Admin products only"""
        product = db.query(Product).filter(
            and_(
                Product.id == product_id,
                Product.created_via == 'admin_web'  # Only admin products
            )
        ).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found or not an admin product")
        
        if quantity_to_add <= 0:
            raise HTTPException(status_code=400, detail="Quantity to add must be positive")
        
        previous_stock = product.stock_quantity
        new_stock = previous_stock + quantity_to_add
        
        # Update product stock
        product.stock_quantity = new_stock
        product.is_out_of_stock = False
        product.last_stock_update = datetime.utcnow()
        
        db.commit()
        db.refresh(product)
        
        # Log the stock addition
        InventoryService.log_stock_change(
            db=db,
            product_id=product_id,
            change_type="stock_added",
            quantity_changed=quantity_to_add,
            previous_stock=previous_stock,
            new_stock=new_stock,
            user_id=user_id,
            reason=reason or "Stock addition"
        )
        
        return product
    
    @staticmethod
    def remove_stock(
        db: Session,
        product_id: int,
        quantity_to_remove: int,
        user_id: int,
        reason: Optional[str] = None
    ) -> Product:
        """Remove stock from existing product - Admin products only"""
        product = db.query(Product).filter(
            and_(
                Product.id == product_id,
                Product.created_via == 'admin_web'  # Only admin products
            )
        ).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found or not an admin product")
        
        if quantity_to_remove <= 0:
            raise HTTPException(status_code=400, detail="Quantity to remove must be positive")
        
        if product.stock_quantity < quantity_to_remove:
            raise HTTPException(status_code=400, detail="Insufficient stock")
        
        previous_stock = product.stock_quantity
        new_stock = previous_stock - quantity_to_remove
        
        # Update product stock
        product.stock_quantity = new_stock
        product.is_out_of_stock = new_stock == 0
        product.last_stock_update = datetime.utcnow()
        
        db.commit()
        db.refresh(product)
        
        # Log the stock removal
        InventoryService.log_stock_change(
            db=db,
            product_id=product_id,
            change_type="stock_removed",
            quantity_changed=-quantity_to_remove,
            previous_stock=previous_stock,
            new_stock=new_stock,
            user_id=user_id,
            reason=reason or "Stock removal"
        )
        
        return product
    
    @staticmethod
    def process_order_stock_reduction(
        db: Session,
        order_id: int,
        user_id: int
    ) -> List[Product]:
        """Process stock reduction when order is placed"""
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        updated_products = []
        
        for order_item in order.items:
            product = order_item.product
            
            if product.stock_quantity < order_item.quantity:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Insufficient stock for product '{product.title}'. Available: {product.stock_quantity}, Requested: {order_item.quantity}"
                )
            
            previous_stock = product.stock_quantity
            new_stock = previous_stock - order_item.quantity
            new_sold_quantity = product.sold_quantity + order_item.quantity
            
            # Update product stock
            product.stock_quantity = new_stock
            product.sold_quantity = new_sold_quantity
            product.is_out_of_stock = new_stock == 0
            product.last_stock_update = datetime.utcnow()
            
            updated_products.append(product)
            
            # Log the stock reduction
            InventoryService.log_stock_change(
                db=db,
                product_id=product.id,
                change_type="order_placed",
                quantity_changed=-order_item.quantity,
                previous_stock=previous_stock,
                new_stock=new_stock,
                user_id=user_id,
                order_id=order_id,
                reason=f"Order #{order_id} - {order_item.quantity} units sold"
            )
        
        db.commit()
        return updated_products
    
    @staticmethod
    def process_order_cancellation(
        db: Session,
        order_id: int,
        user_id: int
    ) -> List[Product]:
        """Process stock restoration when order is cancelled"""
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        updated_products = []
        
        for order_item in order.items:
            product = order_item.product
            
            previous_stock = product.stock_quantity
            new_stock = previous_stock + order_item.quantity
            new_sold_quantity = max(0, product.sold_quantity - order_item.quantity)
            
            # Update product stock
            product.stock_quantity = new_stock
            product.sold_quantity = new_sold_quantity
            product.is_out_of_stock = False
            product.last_stock_update = datetime.utcnow()
            
            updated_products.append(product)
            
            # Log the stock restoration
            InventoryService.log_stock_change(
                db=db,
                product_id=product.id,
                change_type="order_cancelled",
                quantity_changed=order_item.quantity,
                previous_stock=previous_stock,
                new_stock=new_stock,
                user_id=user_id,
                order_id=order_id,
                reason=f"Order #{order_id} cancelled - {order_item.quantity} units restored"
            )
        
        db.commit()
        return updated_products
    
    @staticmethod
    def log_stock_change(
        db: Session,
        product_id: int,
        change_type: str,
        quantity_changed: int,
        previous_stock: int,
        new_stock: int,
        user_id: Optional[int] = None,
        order_id: Optional[int] = None,
        reason: Optional[str] = None
    ) -> InventoryLog:
        """Log a stock change in the inventory log"""
        inventory_log = InventoryLog(
            product_id=product_id,
            change_type=change_type,
            quantity_changed=quantity_changed,
            previous_stock=previous_stock,
            new_stock=new_stock,
            user_id=user_id,
            order_id=order_id,
            reason=reason
        )
        
        db.add(inventory_log)
        db.commit()
        db.refresh(inventory_log)
        
        return inventory_log
    
    @staticmethod
    def get_inventory_summary(db: Session, product_id: int) -> Dict[str, Any]:
        """Get comprehensive inventory summary for a product - Admin products only"""
        product = db.query(Product).filter(
            and_(
                Product.id == product_id,
                Product.created_via == 'admin_web'  # Only admin products
            )
        ).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found or not an admin product")
        
        return {
            "product_id": product.id,
            "product_title": product.title,
            "current_stock": product.stock_quantity,
            "initial_stock": product.initial_stock,
            "sold_quantity": product.sold_quantity,
            "is_out_of_stock": product.is_out_of_stock,
            "low_stock_alert": product.stock_quantity <= product.low_stock_threshold,
            "low_stock_threshold": product.low_stock_threshold,
            "last_stock_update": product.last_stock_update,
            "stock_percentage": (product.stock_quantity / product.initial_stock * 100) if product.initial_stock > 0 else 0
        }
    
    @staticmethod
    def get_low_stock_products(db: Session, limit: int = 50) -> List[Product]:
        """Get products with low stock (below threshold) - Admin products only"""
        return db.query(Product).filter(
            and_(
                Product.stock_quantity <= Product.low_stock_threshold,
                Product.stock_quantity > 0,
                Product.created_via == 'admin_web'  # Only admin products
            )
        ).limit(limit).all()
    
    @staticmethod
    def get_out_of_stock_products(db: Session, limit: int = 50) -> List[Product]:
        """Get products that are out of stock - Admin products only"""
        return db.query(Product).filter(
            and_(
                Product.stock_quantity == 0,
                Product.created_via == 'admin_web'  # Only admin products
            )
        ).limit(limit).all()
    
    @staticmethod
    def get_inventory_logs(
        db: Session,
        product_id: Optional[int] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[InventoryLog]:
        """Get inventory logs with optional filtering - Admin products only"""
        query = db.query(InventoryLog).join(Product, InventoryLog.product_id == Product.id).filter(
            Product.created_via == 'admin_web'  # Only admin products
        )
        
        if product_id:
            query = query.filter(InventoryLog.product_id == product_id)
        
        return query.order_by(InventoryLog.created_at.desc()).offset(offset).limit(limit).all()
    
    @staticmethod
    def check_stock_availability(
        db: Session,
        product_id: int,
        requested_quantity: int
    ) -> bool:
        """Check if requested quantity is available in stock"""
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return False
        
        return product.stock_quantity >= requested_quantity and not product.is_out_of_stock
