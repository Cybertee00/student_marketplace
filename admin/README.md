# Student Marketplace Admin Panel

A modern, responsive web application for managing the Student Marketplace platform. Built with React, TypeScript, and Tailwind CSS.

## Features

### 🎯 Dashboard
- **Revenue Analytics**: Total revenue, daily/weekly/monthly trends
- **User Statistics**: Active users, total registrations
- **Product Metrics**: Total products, pending approvals
- **Order Tracking**: Total orders and status overview
- **Interactive Charts**: Revenue trends, category distribution, top products

### 📦 Product Management
- **Product Moderation**: Approve/reject pending products
- **Catalog Management**: Add, edit, delete products
- **Advanced Filtering**: Search by category, status, price range
- **Bulk Operations**: Mass approve/reject products
- **Product Details**: View images, descriptions, seller info

### 🛒 Order Management
- **Order Tracking**: View all orders with status updates
- **Order Details**: Products, quantities, buyer info, payment method
- **Status Management**: Update order status (pending, paid, completed, cancelled)
- **Revenue Linking**: Connect orders to revenue reports

### 👥 User Management
- **User Directory**: List all registered users
- **Activity History**: View user orders and product listings
- **Account Management**: Deactivate/remove users
- **User Profiles**: Detailed user information and activity

### 📊 Reports & Analytics
- **Revenue Reports**: Generate reports by day/week/month
- **Export Functionality**: CSV and PDF export
- **Performance Analytics**: Product performance, category analysis
- **Top Sellers**: Identify and track top-performing sellers

### 💬 Communication
- **Messaging System**: Chat interface with sellers
- **Notifications**: Real-time notifications for admin
- **Message History**: Stored conversations in database
- **Seller Support**: Direct communication for verification

## Tech Stack

- **Frontend**: React 18, TypeScript, Vite
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **Icons**: Lucide React
- **Forms**: React Hook Form + Zod validation
- **State Management**: React Query
- **HTTP Client**: Axios
- **Notifications**: React Hot Toast
- **Routing**: React Router DOM

## Getting Started

### Prerequisites
- Node.js 18+ 
- npm or yarn
- Backend API running on `http://localhost:8000`

### Installation

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Start development server**:
   ```bash
   npm run dev
   ```

3. **Open in browser**:
   Navigate to `http://localhost:3001`

### Build for Production

```bash
npm run build
```

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── Layout.tsx      # Main layout with sidebar
│   └── LoadingSpinner.tsx
├── contexts/           # React contexts
│   └── AuthContext.tsx # Authentication state
├── pages/              # Page components
│   ├── DashboardPage.tsx
│   ├── ProductsPage.tsx
│   ├── OrdersPage.tsx
│   ├── UsersPage.tsx
│   ├── ReportsPage.tsx
│   ├── MessagesPage.tsx
│   └── LoginPage.tsx
├── services/           # API services
│   └── api.ts         # HTTP client and endpoints
├── types/              # TypeScript type definitions
│   └── index.ts
├── App.tsx            # Main app component
└── main.tsx           # Entry point
```

## API Integration

The admin panel integrates with the FastAPI backend through the following endpoints:

### Authentication
- `POST /api/auth/login` - Admin login
- `GET /api/auth/me` - Get current user

### Dashboard
- `GET /api/admin/dashboard` - Dashboard statistics

### Products
- `GET /api/admin/products` - List products with filters
- `GET /api/admin/products/{id}` - Get product details
- `POST /api/admin/products` - Create product
- `PUT /api/admin/products/{id}` - Update product
- `DELETE /api/admin/products/{id}` - Delete product
- `PUT /api/admin/products/{id}/approve` - Approve product
- `PUT /api/admin/products/{id}/reject` - Reject product

### Orders
- `GET /api/admin/orders` - List orders
- `GET /api/admin/orders/{id}` - Get order details
- `PUT /api/admin/orders/{id}/status` - Update order status

### Users
- `GET /api/admin/users` - List users
- `GET /api/admin/users/{id}` - Get user details
- `PUT /api/admin/users/{id}` - Update user
- `PUT /api/admin/users/{id}/deactivate` - Deactivate user

### Revenue
- `GET /api/admin/revenue` - Get revenue data
- `GET /api/admin/revenue/export` - Export revenue report

### Messages
- `GET /api/admin/messages` - Get messages
- `POST /api/admin/messages` - Send message
- `PUT /api/admin/messages/{id}/read` - Mark as read

## Authentication

The admin panel uses JWT-based authentication:

1. **Login**: Admin credentials are validated against the backend
2. **Token Storage**: JWT tokens are stored in localStorage
3. **Auto-logout**: Expired tokens automatically redirect to login
4. **Protected Routes**: All admin pages require authentication

### Demo Credentials
- **Email**: `admin@university.edu`
- **Password**: `admin123`

## Styling

The application uses Tailwind CSS with a custom color scheme:

- **Primary**: Blue (#3b82f6) - Main brand color
- **Secondary**: Gray (#64748b) - Text and borders
- **Success**: Green (#22c55e) - Success states
- **Warning**: Orange (#f59e0b) - Warning states
- **Danger**: Red (#ef4444) - Error states

## Responsive Design

The admin panel is fully responsive:

- **Desktop**: Full sidebar navigation
- **Tablet**: Collapsible sidebar
- **Mobile**: Hamburger menu with overlay

## Development

### Code Style
- TypeScript for type safety
- ESLint for code linting
- Prettier for code formatting
- React Query for server state management

### State Management
- **Local State**: React useState for component state
- **Server State**: React Query for API data
- **Global State**: React Context for authentication

### Error Handling
- Global error boundaries
- API error interceptors
- User-friendly error messages
- Toast notifications for feedback

## Deployment

### Environment Variables
Create a `.env` file:
```env
VITE_API_URL=http://localhost:8000
```

### Build Process
1. Run `npm run build`
2. Deploy the `dist` folder to your web server
3. Configure reverse proxy to handle API requests

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is part of the Student Marketplace platform.

## Support

For support and questions, please contact the development team.
