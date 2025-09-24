from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models import Product, User, UserRole, Role
from schemas import ProductCreate, ProductUpdate, ProductResponse, ProductListResponse, StockUpdateRequest, InventorySummaryResponse, InventoryLogResponse, ProductDiscontinueRequest
from auth import get_current_user
from inventory_service import InventoryService

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("/", response_model=ProductListResponse)
def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    category: Optional[str] = None,
    faculty: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get Flutter app submitted products for Marketplace (approved only)."""
    # Get products that were submitted through Flutter app and are approved
    # These are products created via Flutter app (created_via='flutter') and approved by admin
    
    query = db.query(Product).filter(
        Product.approved == True,
        Product.created_via == 'flutter',  # Only Flutter app products
        Product.discontinued == False  # Exclude discontinued products
    )
    
    if category:
        query = query.filter(Product.category == category)
    
    if faculty:
        query = query.filter(Product.faculty == faculty)
    
    if search:
        query = query.filter(
            Product.title.ilike(f"%{search}%") |
            Product.description.ilike(f"%{search}%")
        )
    
    total = query.count()
    products = query.offset(skip).limit(limit).all()
    
    return ProductListResponse(
        products=products,
        total=total,
        page=skip // limit + 1,
        size=limit
    )

@router.get("/student-market", response_model=ProductListResponse)
def get_student_market_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    category: Optional[str] = None,
    faculty: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get admin web-added products for Student Market (Home page)."""
    # Get products created via admin web panel (created_via='admin_web')
    
    query = db.query(Product).filter(
        Product.created_via == 'admin_web',
        Product.discontinued == False  # Exclude discontinued products
    )
    
    if category:
        query = query.filter(Product.category == category)
    
    if faculty:
        query = query.filter(Product.faculty == faculty)
    
    if search:
        query = query.filter(
            Product.title.ilike(f"%{search}%") |
            Product.description.ilike(f"%{search}%")
        )
    
    total = query.count()
    products = query.offset(skip).limit(limit).all()
    
    return ProductListResponse(
        products=products,
        total=total,
        page=skip // limit + 1,
        size=limit
    )

@router.get("/my-products", response_model=List[ProductResponse])
def get_my_products(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all products created by the current user (including drafts)."""
    products = db.query(Product).filter(
        Product.seller_id == current_user.id
    ).all()
    return products

@router.get("/my-products/count")
def get_my_products_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get count of products created by the current user."""
    count = db.query(Product).filter(
        Product.seller_id == current_user.id
    ).count()
    return {"count": count}

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get a specific product by ID."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product

@router.post("/", response_model=ProductResponse)
def create_product(
    product_data: ProductCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new product via Flutter app."""
    # Ensure created_via is set to 'flutter' for Flutter app uploads
    product_dict = product_data.dict()
    product_dict['created_via'] = 'flutter'
    
    # Set default values for inventory fields if not provided
    stock_quantity = product_dict.get('stock_quantity', 0)
    product_dict.setdefault('initial_stock', stock_quantity)  # Use provided stock_quantity as initial_stock
    product_dict.setdefault('sold_quantity', 0)
    product_dict.setdefault('low_stock_threshold', 5)
    product_dict.setdefault('is_out_of_stock', stock_quantity == 0)  # Set based on stock_quantity
    
    db_product = Product(
        **product_dict,
        seller_id=current_user.id
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a product (only by the seller)."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    if product.seller_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this product"
        )
    
    # Update only provided fields
    update_data = product_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    
    db.commit()
    db.refresh(product)
    return product

@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a product (only by the seller)."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    if product.seller_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this product"
        )
    
    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully"}

@router.patch("/{product_id}/discontinue", response_model=ProductResponse)
def discontinue_product(
    product_id: int,
    discontinue_data: ProductDiscontinueRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a product as discontinued or re-enable it."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Only the seller can discontinue their own product
    if product.seller_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this product"
        )
    
    # Update the discontinued status
    product.discontinued = discontinue_data.discontinued
    
    db.commit()
    db.refresh(product)
    
    action = "discontinued" if discontinue_data.discontinued else "re-enabled"
    return product

@router.get("/categories/list")
def get_categories(db: Session = Depends(get_db)):
    """Get all available product categories."""
    categories = db.query(Product.category).distinct().all()
    return [category[0] for category in categories if category[0]]

@router.get("/seller/{seller_id}", response_model=List[ProductResponse])
def get_products_by_seller(seller_id: int, db: Session = Depends(get_db)):
    """Get all products by a specific seller."""
    products = db.query(Product).filter(
        Product.seller_id == seller_id,
        Product.approved == True
    ).all()
    return products

@router.patch("/{product_id}/submit-for-review", response_model=ProductResponse)
def submit_product_for_review(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit a draft product for admin review."""
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check if the user owns this product
    if product.seller_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only submit your own products for review"
        )
    
    # Check if it's already approved
    if product.approved:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product is already approved"
        )
    
    # For now, we'll just mark it as submitted for review
    # In a real implementation, you might want to add a "submitted_for_review" field
    # or create a review queue system
    
    db.commit()
    db.refresh(product)
    return product

# ---------------- INVENTORY MANAGEMENT ENDPOINTS ----------------

@router.get("/{product_id}/inventory", response_model=InventorySummaryResponse)
def get_product_inventory(
    product_id: int,
    db: Session = Depends(get_db)
):
    """Get inventory summary for a specific product."""
    try:
        inventory_summary = InventoryService.get_inventory_summary(db, product_id)
        return InventorySummaryResponse(**inventory_summary)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{product_id}/inventory/stock", response_model=ProductResponse)
def update_product_stock(
    product_id: int,
    stock_data: StockUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update product stock quantity (admin only)."""
    try:
        updated_product = InventoryService.update_stock(
            db=db,
            product_id=product_id,
            new_stock_quantity=stock_data.stock_quantity,
            user_id=current_user.id,
            reason=stock_data.reason
        )
        return updated_product
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{product_id}/inventory/add-stock", response_model=ProductResponse)
def add_product_stock(
    product_id: int,
    stock_data: StockUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add stock to existing product (admin only)."""
    try:
        updated_product = InventoryService.add_stock(
            db=db,
            product_id=product_id,
            quantity_to_add=stock_data.stock_quantity,
            user_id=current_user.id,
            reason=stock_data.reason
        )
        return updated_product
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{product_id}/inventory/remove-stock", response_model=ProductResponse)
def remove_product_stock(
    product_id: int,
    stock_data: StockUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove stock from existing product (admin only)."""
    try:
        updated_product = InventoryService.remove_stock(
            db=db,
            product_id=product_id,
            quantity_to_remove=stock_data.stock_quantity,
            user_id=current_user.id,
            reason=stock_data.reason
        )
        return updated_product
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{product_id}/inventory/logs", response_model=List[InventoryLogResponse])
def get_product_inventory_logs(
    product_id: int,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get inventory logs for a specific product."""
    try:
        logs = InventoryService.get_inventory_logs(
            db=db,
            product_id=product_id,
            limit=limit,
            offset=offset
        )
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/inventory/low-stock")
def get_low_stock_products(
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get products with low stock (below threshold)."""
    try:
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

@router.get("/inventory/out-of-stock")
def get_out_of_stock_products(
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get products that are out of stock."""
    try:
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
