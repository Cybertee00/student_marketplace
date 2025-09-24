# STUDENT_MARKERTAPP

A fully functional Flutter application for a student marketplace where students can buy and sell products. This app provides a modern, user-friendly interface with all the essential features for a marketplace application.

## Features

### 🔐 Authentication & User Management
- **User Registration**: Complete registration with name, surname, email, phone, username, and password
- **Flexible Login**: Login using username, email, or phone number
- **Secure Authentication**: JWT-based token system with password hashing
- **User Profiles**: Manage user information and preferences

### 🏠 Home & Marketplace
- **Product Feed**: Grid view of all available products
- **Search Functionality**: Search products by title, description, or category
- **Category Filtering**: Filter products by categories (Books, Electronics, Clothing, etc.)
- **Product Cards**: Attractive product cards with images, prices, and seller info

### 🛒 Shopping Cart
- **Add to Cart**: Add products to shopping cart
- **Quantity Management**: Adjust quantities in cart
- **Cart Summary**: View total items and price
- **Remove Items**: Remove products from cart
- **Persistent Storage**: Cart data persists between app sessions

### 📱 Product Details
- **Image Carousel**: Multiple product images with carousel slider
- **Detailed Information**: Complete product details including description, condition, tags
- **Seller Information**: Display seller name and contact details
- **Add to Cart**: Direct add to cart functionality

### 🎨 Modern UI/UX
- **Material Design 3**: Modern Material Design implementation
- **Dark/Light Theme**: Support for both light and dark themes
- **Responsive Design**: Works on various screen sizes
- **Smooth Animations**: Engaging animations and transitions
- **Student-Friendly Colors**: Deep blue and lime green color scheme

### 📱 Navigation
- **Drawer Menu**: Hamburger menu with all app sections
- **Bottom Navigation**: Quick access to main features
- **Route Management**: Clean navigation using GoRouter

## Technical Stack

### Core Technologies
- **Flutter**: Cross-platform mobile development framework
- **Dart**: Programming language
- **Provider**: State management solution

### Key Dependencies
- **go_router**: Navigation and routing
- **shared_preferences**: Local data storage
- **cached_network_image**: Image caching and loading
- **carousel_slider**: Image carousel functionality
- **google_fonts**: Custom typography
- **crypto**: Password hashing and security
- **uuid**: Unique identifier generation

### Architecture
- **MVVM Pattern**: Model-View-ViewModel architecture
- **Provider Pattern**: State management
- **Service Layer**: Business logic separation
- **Repository Pattern**: Data access abstraction

## Project Structure

```
lib/
├── constants/
│   └── app_constants.dart          # App constants, colors, themes
├── models/
│   ├── user_model.dart             # User data model
│   ├── product_model.dart          # Product data model
│   ├── cart_item_model.dart        # Cart item model
│   └── order_model.dart            # Order data model
├── providers/
│   ├── auth_provider.dart          # Authentication state management
│   └── cart_provider.dart          # Cart state management
├── services/
│   ├── auth_service.dart           # Authentication logic
│   ├── product_service.dart        # Product management
│   └── cart_service.dart           # Cart operations
├── screens/
│   ├── splash_screen.dart          # App splash screen
│   ├── auth/
│   │   ├── login_screen.dart       # Login screen
│   │   └── register_screen.dart    # Registration screen
│   ├── home_screen.dart            # Main marketplace
│   ├── cart_screen.dart            # Shopping cart
│   ├── favorites_screen.dart       # Favorites (placeholder)
│   ├── profile_screen.dart         # User profile (placeholder)
│   └── product/
│       ├── product_detail_screen.dart  # Product details
│       └── sell_product_screen.dart    # Sell product (placeholder)
├── widgets/
│   ├── product_card.dart           # Product card widget
│   ├── cart_item_widget.dart       # Cart item widget
│   ├── category_filter.dart        # Category filter widget
│   └── search_bar.dart             # Search bar widget
└── main.dart                       # App entry point
```

## Getting Started

### Prerequisites
- Flutter SDK (3.8.1 or higher)
- Dart SDK
- Android Studio / VS Code
- Android Emulator or Physical Device

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd student_marketplace
   ```

2. **Install dependencies**
   ```bash
   flutter pub get
   ```

3. **Run the application**
   ```bash
   flutter run
   ```

### Demo Credentials
For testing purposes, you can use these demo credentials:
- **Username**: demo_user
- **Password**: password123

Or register a new account with your own details.

## Features Implementation Status

### ✅ Completed Features
- [x] User Authentication (Login/Register)
- [x] Product Listing and Browsing
- [x] Product Search and Filtering
- [x] Shopping Cart Management
- [x] Product Details View
- [x] Modern UI/UX Design
- [x] Navigation and Routing
- [x] Local Data Persistence

### 🚧 In Progress / Planned Features
- [ ] Product Selling Interface
- [ ] User Profile Management
- [ ] Favorites/Wishlist
- [ ] Order Management
- [ ] Payment Integration
- [ ] Push Notifications
- [ ] In-app Messaging
- [ ] Admin Panel
- [ ] Image Upload
- [ ] Real-time Updates

## Design Guidelines

### Color Scheme
- **Primary**: Deep Blue (#2C3E50) - Trusted & modern
- **Accent**: Vibrant Lime Green (#27AE60) - Energetic & student-friendly
- **Background**: Light Gray (#ECF0F1) - Clean & readable
- **Surface**: White - Clean interface
- **Text**: Dark Gray (#2C3E50) - Good readability

### Typography
- **Font Family**: Inter (Google Fonts)
- **Headings**: Bold, 24px
- **Subheadings**: Semi-bold, 18px
- **Body**: Regular, 16px
- **Captions**: Regular, 14px

### UI Components
- **Cards**: Rounded corners, subtle shadows
- **Buttons**: Rounded, with hover effects
- **Input Fields**: Outlined style with focus states
- **Navigation**: Clean, minimal design

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please open an issue in the repository or contact the development team.

---

**Built with ❤️ for students by students**
