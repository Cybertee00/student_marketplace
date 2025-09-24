from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Text, ARRAY, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

# ---------------- USERS ----------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    surname = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    phone = Column(String(50), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)  # will store hashed password
    profile_img = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Email verification fields
    is_email_verified = Column(Boolean, default=False, nullable=False)
    email_verification_token = Column(String(255), nullable=True)
    email_verification_expires_at = Column(DateTime, nullable=True)
    
    # Phone verification fields
    is_phone_verified = Column(Boolean, default=False, nullable=False)
    phone_verification_code = Column(String(10), nullable=True)
    phone_verification_expires_at = Column(DateTime, nullable=True)

    # relationships
    products = relationship("Product", back_populates="seller")
    orders = relationship("Order", back_populates="buyer")
    cart_items = relationship("CartItem", back_populates="user")
    favorites = relationship("Favorite", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    sent_messages = relationship("Message", foreign_keys="Message.sender_id", back_populates="sender")
    received_messages = relationship("Message", foreign_keys="Message.receiver_id", back_populates="receiver")
    reviews = relationship("Review", back_populates="user")
    
    # role relationships
    user_roles = relationship("UserRole", foreign_keys="UserRole.user_id", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")

# ---------------- PRODUCTS ----------------
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    price = Column(Float, nullable=False)
    category = Column(String(100), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    approved = Column(Boolean, default=False)  # admin approval
    discontinued = Column(Boolean, default=False)  # product discontinued status
    images = Column(ARRAY(String), nullable=True)  # store multiple image URLs as array
    
    # Faculty filtering
    faculty = Column(String(100), index=True, nullable=True)  # humanities, health_environmental, FEBIT, management_science
    
    # Creation method tracking
    created_via = Column(String(20), default='flutter', nullable=False)  # 'flutter' or 'admin_web'
    
    # Inventory management fields
    stock_quantity = Column(Integer, default=0, nullable=False)  # Current stock available
    initial_stock = Column(Integer, default=0, nullable=False)   # Initial stock when product was created
    sold_quantity = Column(Integer, default=0, nullable=False)   # Total quantity sold
    low_stock_threshold = Column(Integer, default=5, nullable=False)  # Alert when stock goes below this
    is_out_of_stock = Column(Boolean, default=True, nullable=False)  # True when stock_quantity = 0
    last_stock_update = Column(DateTime, default=datetime.utcnow)  # When stock was last updated

    # foreign key → seller
    seller_id = Column(Integer, ForeignKey("users.id"))

    # relationships
    seller = relationship("User", back_populates="products")
    cart_items = relationship("CartItem", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")
    favorites = relationship("Favorite", back_populates="product")
    inventory_logs = relationship("InventoryLog", back_populates="product")
    reviews = relationship("Review", back_populates="product")

# ---------------- CART ----------------
class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    quantity = Column(Integer, default=1)

    # foreign keys
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))

    # relationships
    user = relationship("User", back_populates="cart_items")
    product = relationship("Product", back_populates="cart_items")

# ---------------- ORDERS ----------------
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    total_amount = Column(Float, nullable=False)
    payment_method = Column(String(50), nullable=False)  # e.g. "card", "cash_on_delivery"
    status = Column(String(50), default="pending")       # pending, paid, completed, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # foreign key → buyer
    user_id = Column(Integer, ForeignKey("users.id"))

    # relationships
    buyer = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")
    revenue = relationship("Revenue", back_populates="order", uselist=False)

# ---------------- ORDER ITEMS ----------------
class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    quantity = Column(Integer, default=1)
    price = Column(Float, nullable=False)  # snapshot of product price at purchase time

    # foreign keys
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))

    # relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")

# ---------------- FAVORITES / WISHLIST ----------------
class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # foreign keys
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))

    # relationships
    user = relationship("User", back_populates="favorites")
    product = relationship("Product", back_populates="favorites")

# ---------------- NOTIFICATIONS ----------------
class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)  # Auto-deletion date (30 days from creation)
    deleted_at = Column(DateTime, nullable=True)  # Manual deletion timestamp

    # foreign key → user
    user_id = Column(Integer, ForeignKey("users.id"))

    # relationships
    user = relationship("User", back_populates="notifications")

# ---------------- MESSAGES (BUYER ↔ SELLER CHAT) ----------------
class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(Text, nullable=False)
    message_type = Column(String(50), default="text")  # text, image, file, order_inquiry, support
    conversation_id = Column(String(100), nullable=True)  # Group messages by conversation
    is_read = Column(Boolean, default=False)
    is_important = Column(Boolean, default=False)  # Mark important messages
    parent_message_id = Column(Integer, ForeignKey("messages.id"), nullable=True)  # For replies
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # foreign keys
    sender_id = Column(Integer, ForeignKey("users.id"))
    receiver_id = Column(Integer, ForeignKey("users.id"))

    # relationships
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_messages")
    parent_message = relationship("Message", remote_side=[id], backref="replies")

# ---------------- REVENUE TRACKING (for admin dashboard) ----------------
class Revenue(Base):
    __tablename__ = "revenue"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)  # Total order amount
    commission = Column(Float, default=0.0)  # Platform commission (e.g., 10%)
    platform_fee = Column(Float, default=0.0)  # Fixed platform fee
    seller_revenue = Column(Float, default=0.0)  # Amount that goes to seller
    payment_method = Column(String(50), nullable=False)  # Payment method used
    created_at = Column(DateTime, default=datetime.utcnow)

    # foreign key → order
    order_id = Column(Integer, ForeignKey("orders.id"))
    
    # relationship
    order = relationship("Order", back_populates="revenue")

# ---------------- ROLES AND PERMISSIONS ----------------
class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)  # e.g., "admin", "moderator", "user"
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # relationships
    user_roles = relationship("UserRole", back_populates="role")
    role_permissions = relationship("RolePermission", back_populates="role")

class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)  # e.g., "admin.dashboard", "admin.products.approve"
    description = Column(Text, nullable=True)
    resource = Column(String(50), nullable=False)  # e.g., "dashboard", "products", "users"
    action = Column(String(50), nullable=False)    # e.g., "read", "write", "delete", "approve"
    created_at = Column(DateTime, default=datetime.utcnow)

    # relationships
    role_permissions = relationship("RolePermission", back_populates="permission")

class UserRole(Base):
    __tablename__ = "user_roles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    assigned_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # who assigned this role
    assigned_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)  # optional role expiration
    is_active = Column(Boolean, default=True)

    # relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="user_roles")
    role = relationship("Role", back_populates="user_roles")
    assigned_by_user = relationship("User", foreign_keys=[assigned_by])

class RolePermission(Base):
    __tablename__ = "role_permissions"

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    permission_id = Column(Integer, ForeignKey("permissions.id"), nullable=False)
    granted_at = Column(DateTime, default=datetime.utcnow)
    granted_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # relationships
    role = relationship("Role", back_populates="role_permissions")
    permission = relationship("Permission", back_populates="role_permissions")
    granted_by_user = relationship("User", foreign_keys=[granted_by])

# ---------------- AUDIT LOGS ----------------
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # nullable for anonymous actions
    action = Column(String(100), nullable=False)  # e.g., "login", "product.approve", "user.role.assign"
    resource_type = Column(String(50), nullable=False)  # e.g., "user", "product", "order"
    resource_id = Column(Integer, nullable=True)  # ID of the affected resource
    details = Column(JSON, nullable=True)  # additional details about the action
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(Text, nullable=True)  # browser/client info
    success = Column(Boolean, default=True)  # whether the action was successful
    error_message = Column(Text, nullable=True)  # error details if action failed
    created_at = Column(DateTime, default=datetime.utcnow)

    # relationships
    user = relationship("User")

# ---------------- INVENTORY LOGS ----------------
class InventoryLog(Base):
    __tablename__ = "inventory_logs"

    id = Column(Integer, primary_key=True, index=True)
    change_type = Column(String(50), nullable=False)  # "stock_added", "stock_removed", "order_placed", "order_cancelled", "initial_stock"
    quantity_changed = Column(Integer, nullable=False)  # Positive for additions, negative for removals
    previous_stock = Column(Integer, nullable=False)    # Stock before change
    new_stock = Column(Integer, nullable=False)         # Stock after change
    reason = Column(Text, nullable=True)                # Reason for change (e.g., "Order #123", "Manual stock update")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # foreign keys
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Who made the change (admin/seller)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)  # Related order if applicable
    
    # relationships
    product = relationship("Product", back_populates="inventory_logs")
    user = relationship("User")
    order = relationship("Order")

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5 stars
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    product = relationship("Product", back_populates="reviews")
    user = relationship("User", back_populates="reviews")
