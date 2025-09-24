
# Student Marketplace Backend API

A comprehensive FastAPI backend for the Student Marketplace application with PostgreSQL database integration.

## Features

- **Authentication**: JWT-based authentication with user registration and login
- **Products**: CRUD operations for products with search and filtering
- **Cart Management**: Add, update, and remove items from shopping cart
- **Orders**: Create orders and manage order history
- **Favorites**: Wishlist functionality for users
- **Database**: PostgreSQL with SQLAlchemy ORM and Alembic migrations

## Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **PostgreSQL**: Relational database
- **SQLAlchemy**: Python SQL toolkit and ORM
- **Alembic**: Database migration tool
- **Pydantic**: Data validation using Python type annotations
- **JWT**: JSON Web Tokens for authentication
- **Passlib**: Password hashing with bcrypt

## Setup Instructions

### 1. Prerequisites

- Python 3.8+
- PostgreSQL database
- pip (Python package manager)

### 2. Database Setup

First, create the PostgreSQL database and user:

```sql
-- Connect to PostgreSQL as superuser
CREATE DATABASE student_marketplace;
CREATE USER marketplace_user WITH PASSWORD '0000';
GRANT ALL PRIVILEGES ON DATABASE student_marketplace TO marketplace_user;
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the backend directory:

```env
DATABASE_URL=postgresql://marketplace_user:0000@localhost:5432/student_marketplace
SECRET_KEY=your-secret-key-here-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 5. Database Migrations

Initialize and run database migrations:

```bash
# Initialize Alembic (if not already done)
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

### 6. Run the Application

```bash
# Development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production server
uvicorn main:app --host 0.0.0.0 --port 8000
```

## API Documentation

Once the server is running, you can access:

- **Interactive API Docs**: http://172.16.8.138:8000/docs
- **ReDoc Documentation**: http://172.16.8.138:8000/redoc
- **OpenAPI Schema**: http://172.16.8.138:8000/openapi.json

## API Endpoints

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login user
- `GET /auth/me` - Get current user info

### Products
- `GET /products/` - Get all products (with pagination and filtering)
- `GET /products/{product_id}` - Get specific product
- `POST /products/` - Create new product
- `PUT /products/{product_id}` - Update product
- `DELETE /products/{product_id}` - Delete product
- `GET /products/categories/list` - Get all categories
- `GET /products/seller/{seller_id}` - Get products by seller

### Cart
- `GET /cart/` - Get user's cart
- `POST /cart/add` - Add item to cart
- `PUT /cart/{item_id}` - Update cart item quantity
- `DELETE /cart/{item_id}` - Remove item from cart
- `DELETE /cart/clear` - Clear entire cart

### Orders
- `POST /orders/checkout` - Create order from cart
- `GET /orders/` - Get user's order history
- `GET /orders/{order_id}` - Get specific order
- `PUT /orders/{order_id}/cancel` - Cancel order

### Favorites
- `GET /favorites/` - Get user's favorites
- `POST /favorites/add` - Add product to favorites
- `DELETE /favorites/{product_id}` - Remove from favorites
- `GET /favorites/check/{product_id}` - Check if product is favorited

## Database Schema

The application includes the following tables:

- **users**: User accounts and profiles
- **products**: Product listings
- **cart_items**: Shopping cart items
- **orders**: Order records
- **order_items**: Individual items in orders
- **favorites**: User wishlist items
- **notifications**: User notifications
- **messages**: Chat messages between users
- **revenue**: Revenue tracking for admin

## Authentication

The API uses JWT tokens for authentication. To access protected endpoints:

1. Register or login to get an access token
2. Include the token in the Authorization header:
   ```
   Authorization: Bearer <your_access_token>
   ```

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

### Code Formatting

```bash
# Install formatting tools
pip install black isort

# Format code
black .
isort .
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Production Deployment

For production deployment:

1. Change the `SECRET_KEY` in the `.env` file
2. Use a proper PostgreSQL server
3. Set up proper CORS origins
4. Use a production ASGI server like Gunicorn with Uvicorn workers
5. Set up proper logging and monitoring

## License

This project is licensed under the MIT License.
