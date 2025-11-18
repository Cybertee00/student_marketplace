from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict
from datetime import datetime

# ---------------- USER SCHEMAS ----------------
class UserBase(BaseModel):
    name: str
    surname: str
    email: EmailStr
    phone: str
    username: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    username: Optional[str] = None
    profile_img: Optional[str] = None

class UserUpdateRequest(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    phone: Optional[str] = None
    username: Optional[str] = None
    profile_img: Optional[str] = None

class ProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    phone: Optional[str] = None

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str

class RoleAssignmentRequest(BaseModel):
    role_name: str
    expires_at: Optional[datetime] = None

class UserResponse(UserBase):
    id: int
    profile_img: Optional[str] = None
    created_at: datetime
    is_email_verified: bool = False
    is_phone_verified: bool = False
    email_verification_token: Optional[str] = None
    email_verification_expires_at: Optional[datetime] = None
    phone_verification_code: Optional[str] = None
    phone_verification_expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True
    
    @validator('profile_img', pre=True)
    def transform_profile_img_url(cls, v):
        """Transform profile image URL"""
        if not v:
            return None
        
        # If it's already a Supabase Storage URL, keep it as is
        if v.startswith('https://') and 'supabase.co/storage' in v:
            return v
        # If it's already a full URL, keep it
        elif v.startswith('http://') or v.startswith('https://'):
            return v
        # Legacy local files - convert to relative path
        elif not v.startswith('/'):
            return f"/images/profile/{v}"
        # Already a relative path
        return v

# ---------------- VERIFICATION SCHEMAS ----------------
class EmailVerificationRequest(BaseModel):
    email: EmailStr

class OTPVerificationRequest(BaseModel):
    email: EmailStr
    otp: str

class ResendVerificationRequest(BaseModel):
    email: EmailStr

class VerificationStatusResponse(BaseModel):
    email: str
    is_verified: bool
    verification_status: Dict[str, bool]

# ---------------- PRODUCT SCHEMAS ----------------
class ProductBase(BaseModel):
    title: str
    description: str
    price: float
    category: str
    faculty: Optional[str] = None
    images: Optional[List[str]] = None
    stock_quantity: int = 0
    low_stock_threshold: int = 5
    created_via: str = 'flutter'
    discontinued: bool = False

class ProductCreate(ProductBase):
    approved: Optional[bool] = False  # Allow setting approval status during creation

class ProductUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    faculty: Optional[str] = None
    images: Optional[List[str]] = None
    approved: Optional[bool] = None
    stock_quantity: Optional[int] = None
    low_stock_threshold: Optional[int] = None
    discontinued: Optional[bool] = None

class ProductDiscontinueRequest(BaseModel):
    discontinued: bool = True
    reason: Optional[str] = None

class ProductResponse(ProductBase):
    id: int
    seller_id: int
    approved: bool
    created_at: datetime
    seller: UserResponse
    initial_stock: int
    sold_quantity: int
    is_out_of_stock: bool
    last_stock_update: datetime
    stock_quantity: int  # Add missing stock_quantity field

    class Config:
        from_attributes = True
    
    @validator('images', pre=True)
    def transform_image_urls(cls, v):
        """Transform image URLs (Supabase Storage or legacy local)"""
        if not v:
            return []
        
        if isinstance(v, list):
            transformed_urls = []
            for url in v:
                # If it's already a Supabase Storage URL, keep it as is
                if url.startswith('https://') and 'supabase.co/storage' in url:
                    transformed_urls.append(url)
                # If it's already a full URL, keep it
                elif url.startswith('http://') or url.startswith('https://'):
                    transformed_urls.append(url)
                # Legacy local files - convert to relative path
                elif not url.startswith('/'):
                    transformed_urls.append(f"/images/{url}")
                # Already a relative path
                else:
                    transformed_urls.append(url)
            return transformed_urls
        return v

# ---------------- CART SCHEMAS ----------------
class CartItemBase(BaseModel):
    quantity: int = 1

class CartItemCreate(CartItemBase):
    product_id: int

class CartItemUpdate(BaseModel):
    quantity: int

class CartItemResponse(CartItemBase):
    id: int
    user_id: int
    product_id: int
    product: ProductResponse

    class Config:
        from_attributes = True

# ---------------- ORDER SCHEMAS ----------------
class OrderBase(BaseModel):
    payment_method: str

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    status: Optional[str] = None

class OrderResponse(OrderBase):
    id: int
    user_id: int
    total_amount: float
    status: str
    created_at: datetime
    items: List['OrderItemResponse']

    class Config:
        from_attributes = True

# ---------------- ORDER ITEM SCHEMAS ----------------
class OrderItemBase(BaseModel):
    quantity: int
    price: float

class OrderItemCreate(OrderItemBase):
    product_id: int

class OrderItemResponse(OrderItemBase):
    id: int
    order_id: int
    product_id: int
    product: ProductResponse

    class Config:
        from_attributes = True

# ---------------- FAVORITE SCHEMAS ----------------
class FavoriteBase(BaseModel):
    pass

class FavoriteCreate(FavoriteBase):
    product_id: int

class FavoriteResponse(FavoriteBase):
    id: int
    user_id: int
    product_id: int
    created_at: datetime
    product: ProductResponse

    class Config:
        from_attributes = True

# ---------------- NOTIFICATION SCHEMAS ----------------
class NotificationBase(BaseModel):
    message: str

class NotificationCreate(NotificationBase):
    pass

class NotificationResponse(NotificationBase):
    id: int
    user_id: int
    is_read: bool
    created_at: datetime
    expires_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# ---------------- MESSAGE SCHEMAS ----------------
class MessageBase(BaseModel):
    message: str
    message_type: Optional[str] = "text"
    conversation_id: Optional[str] = None
    parent_message_id: Optional[int] = None

class MessageCreate(MessageBase):
    receiver_id: int

class MessageResponse(MessageBase):
    id: int
    sender_id: int
    receiver_id: int
    is_read: bool
    is_important: bool
    created_at: datetime
    updated_at: datetime
    sender: UserResponse
    receiver: UserResponse
    replies_count: Optional[int] = 0

    class Config:
        from_attributes = True

class MessageUpdate(BaseModel):
    is_read: Optional[bool] = None
    is_important: Optional[bool] = None

class ConversationResponse(BaseModel):
    conversation_id: str
    latest_message: MessageResponse
    participants: List[UserResponse]
    unread_count: int
    total_messages: int

class MessageStats(BaseModel):
    total_messages: int
    unread_messages: int
    important_messages: int
    recent_messages: int
    active_conversations: int
    message_types: Dict[str, int]

# ---------------- AUTH SCHEMAS ----------------
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None

class LoginRequest(BaseModel):
    identifier: str  # username, email, or phone
    password: str

# ---------------- RESPONSE SCHEMAS ----------------
class CartResponse(BaseModel):
    items: List[CartItemResponse]
    total_items: int
    total_amount: float

class ProductListResponse(BaseModel):
    products: List[ProductResponse]
    total: int
    page: int
    size: int

class OrderListResponse(BaseModel):
    orders: List[OrderResponse]
    total: int
    page: int
    size: int

class MessageListResponse(BaseModel):
    messages: List[MessageResponse]
    total: int
    page: int
    size: int

# ---------------- INVENTORY SCHEMAS ----------------
class InventoryLogBase(BaseModel):
    change_type: str
    quantity_changed: int
    previous_stock: int
    new_stock: int
    reason: Optional[str] = None

class InventoryLogCreate(InventoryLogBase):
    product_id: int
    order_id: Optional[int] = None

class InventoryLogResponse(InventoryLogBase):
    id: int
    product_id: int
    user_id: Optional[int] = None
    order_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

class StockUpdateRequest(BaseModel):
    stock_quantity: int
    reason: Optional[str] = None

class InventorySummaryResponse(BaseModel):
    product_id: int
    product_title: str
    current_stock: int
    initial_stock: int
    sold_quantity: int
    is_out_of_stock: bool
    low_stock_alert: bool
    last_stock_update: datetime

    class Config:
        from_attributes = True

# Update forward references
OrderResponse.model_rebuild()
OrderItemResponse.model_rebuild()

# ---------------- REVIEW SCHEMAS ----------------
class ReviewBase(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5 stars")
    comment: Optional[str] = Field(None, max_length=1000, description="Review comment")

class ReviewCreate(ReviewBase):
    product_id: int = Field(..., description="ID of the product being reviewed")

class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5, description="Rating from 1 to 5 stars")
    comment: Optional[str] = Field(None, max_length=1000, description="Review comment")

class ReviewResponse(ReviewBase):
    id: int
    product_id: int
    user_id: int
    user_name: str
    user_surname: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
