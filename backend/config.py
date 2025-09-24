"""
Configuration file for the Student Marketplace application
"""

import os
from typing import Optional

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:0000@localhost:5432/student_marketplace")

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

# Email Configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
SMTP_USE_SSL = os.getenv("SMTP_USE_SSL", "false").lower() == "true"

# Email Templates
EMAIL_FROM_NAME = os.getenv("EMAIL_FROM_NAME", "Student Marketplace")
EMAIL_FROM_ADDRESS = os.getenv("EMAIL_FROM_ADDRESS", "noreply@studentmarketplace.com")

# Verification Configuration
VERIFICATION_TOKEN_EXPIRE_MINUTES = int(os.getenv("VERIFICATION_TOKEN_EXPIRE_MINUTES", "10"))
VERIFICATION_OTP_LENGTH = int(os.getenv("VERIFICATION_OTP_LENGTH", "6"))
VERIFICATION_RESEND_COOLDOWN_SECONDS = int(os.getenv("VERIFICATION_RESEND_COOLDOWN_SECONDS", "60"))

# Security Configuration
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))  # 1 hour

# Development Configuration
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

def get_smtp_config() -> dict:
    """Get SMTP configuration for email sending"""
    return {
        "server": SMTP_SERVER,
        "port": SMTP_PORT,
        "username": SMTP_USERNAME,
        "password": SMTP_PASSWORD,
        "use_tls": SMTP_USE_TLS,
        "use_ssl": SMTP_USE_SSL,
        "from_name": EMAIL_FROM_NAME,
        "from_address": EMAIL_FROM_ADDRESS,
    }

def is_production() -> bool:
    """Check if running in production environment"""
    return ENVIRONMENT.lower() == "production"

def is_development() -> bool:
    """Check if running in development environment"""
    return ENVIRONMENT.lower() == "development"

def get_verification_config() -> dict:
    """Get verification configuration"""
    return {
        "token_expire_minutes": VERIFICATION_TOKEN_EXPIRE_MINUTES,
        "otp_length": VERIFICATION_OTP_LENGTH,
        "resend_cooldown_seconds": VERIFICATION_RESEND_COOLDOWN_SECONDS,
    }

def get_database_url() -> str:
    """Get database URL"""
    return DATABASE_URL

def get_jwt_secret_key() -> str:
    """Get JWT secret key"""
    return SECRET_KEY

def get_jwt_algorithm() -> str:
    """Get JWT algorithm"""
    return ALGORITHM

def get_jwt_expire_minutes() -> int:
    """Get JWT token expiration time in minutes"""
    return ACCESS_TOKEN_EXPIRE_MINUTES
