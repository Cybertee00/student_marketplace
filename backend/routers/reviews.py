from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from sqlalchemy import and_

from database import get_db
from models import User, Product, Review, Order, OrderItem
from schemas import ReviewCreate, ReviewUpdate, ReviewResponse
from auth import get_current_user

router = APIRouter(prefix="/reviews", tags=["reviews"])

def has_user_purchased_product(db: Session, user_id: int, product_id: int) -> bool:
    """Check if a user has purchased a specific product"""
    # Look for order items where the user has ordered this product
    # and the order status is not cancelled
    order_item = db.query(OrderItem).join(Order).filter(
        and_(
            OrderItem.product_id == product_id,
            Order.user_id == user_id,
            Order.status != "cancelled"  # Only count completed orders
        )
    ).first()
    
    return order_item is not None

@router.post("/", response_model=ReviewResponse)
async def create_review(
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new review for a product"""
    
    # Check if product exists
    product = db.query(Product).filter(Product.id == review_data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if user has purchased this product
    if not has_user_purchased_product(db, current_user.id, review_data.product_id):
        raise HTTPException(
            status_code=403, 
            detail="You can only review products you have purchased"
        )
    
    # Check if user has already reviewed this product
    existing_review = db.query(Review).filter(
        Review.product_id == review_data.product_id,
        Review.user_id == current_user.id
    ).first()
    
    if existing_review:
        raise HTTPException(status_code=400, detail="You have already reviewed this product")
    
    # Create new review
    new_review = Review(
        product_id=review_data.product_id,
        user_id=current_user.id,
        rating=review_data.rating,
        comment=review_data.comment,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    
    # Return review with user information
    return ReviewResponse(
        id=new_review.id,
        product_id=new_review.product_id,
        user_id=new_review.user_id,
        user_name=new_review.user.name,
        user_surname=new_review.user.surname,
        rating=new_review.rating,
        comment=new_review.comment,
        created_at=new_review.created_at.isoformat(),
        updated_at=new_review.updated_at.isoformat()
    )

@router.get("/product/{product_id}/can-review")
async def can_user_review_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check if the current user can review a specific product"""
    
    # Check if product exists
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if user has purchased this product
    has_purchased = has_user_purchased_product(db, current_user.id, product_id)
    
    # Check if user has already reviewed this product
    existing_review = db.query(Review).filter(
        Review.product_id == product_id,
        Review.user_id == current_user.id
    ).first()
    
    has_reviewed = existing_review is not None
    
    return {
        "can_review": has_purchased and not has_reviewed,
        "has_purchased": has_purchased,
        "has_reviewed": has_reviewed,
        "message": "You can only review products you have purchased" if not has_purchased else 
                   "You have already reviewed this product" if has_reviewed else 
                   "You can review this product"
    }

@router.get("/product/{product_id}", response_model=List[ReviewResponse])
async def get_product_reviews(
    product_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get all reviews for a specific product"""
    
    # Check if product exists
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get reviews with pagination
    offset = (page - 1) * limit
    reviews = db.query(Review).filter(
        Review.product_id == product_id
    ).order_by(Review.created_at.desc()).offset(offset).limit(limit).all()
    
    # Convert to response format
    reviews_response = []
    for review in reviews:
        reviews_response.append(ReviewResponse(
            id=review.id,
            product_id=review.product_id,
            user_id=review.user_id,
            user_name=review.user.name,
            user_surname=review.user.surname,
            rating=review.rating,
            comment=review.comment,
            created_at=review.created_at.isoformat(),
            updated_at=review.updated_at.isoformat()
        ))
    
    return reviews_response

@router.put("/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: int,
    review_data: ReviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a review (only by the review author)"""
    
    # Get the review
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    # Check if user owns this review
    if review.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only update your own reviews")
    
    # Update review fields
    if review_data.rating is not None:
        review.rating = review_data.rating
    if review_data.comment is not None:
        review.comment = review_data.comment
    
    review.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(review)
    
    # Return updated review
    return ReviewResponse(
        id=review.id,
        product_id=review.product_id,
        user_id=review.user_id,
        user_name=review.user.name,
        user_surname=review.user.surname,
        rating=review.rating,
        comment=review.comment,
        created_at=review.created_at.isoformat(),
        updated_at=review.updated_at.isoformat()
    )

@router.delete("/{review_id}")
async def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a review (only by the review author)"""
    
    # Get the review
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    # Check if user owns this review
    if review.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own reviews")
    
    db.delete(review)
    db.commit()
    
    return {"message": "Review deleted successfully"}

@router.get("/product/{product_id}/stats")
async def get_product_review_stats(
    product_id: int,
    db: Session = Depends(get_db)
):
    """Get review statistics for a product"""
    
    # Check if product exists
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get all reviews for the product
    reviews = db.query(Review).filter(Review.product_id == product_id).all()
    
    if not reviews:
        return {
            "total_reviews": 0,
            "average_rating": 0,
            "rating_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        }
    
    # Calculate statistics
    total_reviews = len(reviews)
    total_rating = sum(review.rating for review in reviews)
    average_rating = round(total_rating / total_reviews, 1)
    
    # Calculate rating distribution
    rating_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for review in reviews:
        rating_distribution[review.rating] += 1
    
    return {
        "total_reviews": total_reviews,
        "average_rating": average_rating,
        "rating_distribution": rating_distribution
    }
