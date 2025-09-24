# 🔔 Student Marketplace - Notification System Guide

## 📋 Overview

The notification system automatically sends notifications to users for important events in the marketplace. This guide explains how it works and what notifications are available.

## 🎯 Notification Types

### 1. **Message Notifications**
- **Trigger**: When a user receives a new message
- **Recipients**: Message receiver
- **Example**: "New message from Admin User: Hello! Thank you for your inquiry..."

### 2. **Product Approval Notifications**
- **Trigger**: When admin approves a user's product
- **Recipients**: Product seller
- **Example**: "Great news! Your product 'iPhone 12' has been approved and is now live in the marketplace."

### 3. **Product Rejection Notifications**
- **Trigger**: When admin rejects a user's product
- **Recipients**: Product seller
- **Example**: "Your product 'iPhone 12' was not approved. Reason: Image quality too low. Please review and resubmit."

### 4. **Order Notifications**
- **New Order**: Admin gets notified when a new order is placed
- **Order Updates**: User gets notified when order status changes
- **Examples**:
  - Admin: "New order #123 from John Doe for R250.00"
  - User: "Order #123: Your order has been shipped! You'll receive tracking details soon."

### 5. **Stock Notifications**
- **Low Stock**: Seller gets notified when product stock is low
- **Out of Stock**: Seller gets notified when product is out of stock
- **Examples**:
  - "Low stock alert: 'iPhone 12' has only 3 items left. Consider restocking soon."
  - "Out of stock: 'iPhone 12' is now out of stock. Please restock to continue selling."

### 6. **Sales Notifications**
- **Product Sold**: Seller gets notified when their product is sold
- **Example**: "Sale! 2 unit(s) of 'iPhone 12' sold in order #123"

### 7. **User Management Notifications**
- **New User**: Admin gets notified when a new user registers
- **Welcome**: New user gets a welcome notification
- **Examples**:
  - Admin: "New user registered: John Doe (john@university.edu)"
  - User: "Welcome to Student Marketplace, John! Start by exploring products or listing your own items for sale."

## 🔧 How It Works

### Backend Implementation

1. **NotificationUtils Class** (`backend/utils/notification_utils.py`)
   - Centralized utility for creating notifications
   - Handles all notification types
   - Automatically creates notifications when events occur

2. **Automatic Triggers**
   - Messages: When `send_message()` or `admin_send_message_to_user()` is called
   - Products: When `approve_product()` or `reject_product()` is called
   - Orders: When `create_order()` is called
   - Stock: When product stock changes (can be added to product update endpoints)

### API Endpoints

#### Get Notifications
```http
GET /notifications
GET /notifications?unread_only=true
```

#### Get Unread Count
```http
GET /notifications/unread-count
```

#### Mark as Read
```http
PUT /notifications/{notification_id}/read
PUT /notifications/read-all
```

#### Create Notification (Admin Only)
```http
POST /notifications
{
  "user_id": 2,
  "message": "Custom notification message"
}
```

## 📱 Flutter App Integration

### Notification Service
The Flutter app uses `NotificationService` to:
- Fetch notifications from the backend
- Get unread notification count
- Mark notifications as read
- Display notifications in the UI

### Notification Display
- **Home Screen**: Shows unread notification count in the app bar
- **Notifications Screen**: Lists all notifications with read/unread status
- **Real-time Updates**: Notifications are fetched when the app loads

## 🚀 Adding New Notification Types

To add a new notification type:

1. **Add method to NotificationUtils**:
```python
@staticmethod
def notify_custom_event(db: Session, user_id: int, details: str) -> None:
    notification_message = f"Custom event: {details}"
    NotificationUtils.create_notification(
        db=db,
        user_id=user_id,
        message=notification_message,
        notification_type="custom_event"
    )
```

2. **Call the method in the relevant endpoint**:
```python
# In your endpoint
NotificationUtils.notify_custom_event(db, user_id, "Event details")
```

## 🔄 Real-time Notifications (Future Enhancement)

For real-time notifications, you can integrate:
- **WebSockets**: For instant notifications
- **Push Notifications**: For mobile app notifications
- **Email Notifications**: For important events

## 📊 Notification Analytics

The system tracks:
- Total notifications sent
- Read/unread status
- Notification types
- User engagement

## 🛠️ Configuration

### Admin Settings
- Configure which events trigger notifications
- Set notification message templates
- Manage notification preferences

### User Settings
- Allow users to opt-out of certain notification types
- Set notification frequency preferences

## 🧪 Testing Notifications

### Test Scenarios
1. **Send a message** → Check if receiver gets notification
2. **Approve a product** → Check if seller gets notification
3. **Place an order** → Check if admin gets notification
4. **Update order status** → Check if customer gets notification

### Test Commands
```bash
# Test notification creation
curl -X POST "http://localhost:8000/notifications" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 2, "message": "Test notification"}'

# Test getting notifications
curl -X GET "http://localhost:8000/notifications" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 📈 Benefits

1. **User Engagement**: Users stay informed about important events
2. **Admin Efficiency**: Admins get notified of new orders and user activities
3. **Better UX**: Users don't miss important updates
4. **Automated Communication**: Reduces manual communication needs
5. **Real-time Updates**: Users get instant feedback on their actions

## 🔮 Future Enhancements

1. **Push Notifications**: Mobile app notifications
2. **Email Notifications**: Important events via email
3. **Notification Preferences**: User-customizable notification settings
4. **Notification Templates**: Customizable message templates
5. **Notification Scheduling**: Delayed or scheduled notifications
6. **Notification Analytics**: Detailed notification performance metrics

---

The notification system is now fully integrated and will automatically notify users about important events in the marketplace! 🎉
