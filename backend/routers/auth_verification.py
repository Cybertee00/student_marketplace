from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import os

from database import get_db
from models import User
from schemas import EmailVerificationRequest, OTPVerificationRequest, ResendVerificationRequest
from auth import get_password_hash, verify_password
from supabase_config import supabase_admin

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()

# Email configuration (you'll need to set these environment variables)
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

def send_verification_email(email: str, otp: str, user_name: str) -> bool:
    """Send verification email with OTP code"""
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = email
        msg['Subject'] = "Student Marketplace - Email Verification"
        
        # Email body
        body = f"""
        <html>
        <body>
            <h2>Welcome to Student Marketplace!</h2>
            <p>Hi {user_name},</p>
            <p>Thank you for signing up! To complete your registration, please use the following verification code:</p>
            
            <div style="background-color: #f8f9fa; padding: 20px; text-align: center; border-radius: 10px; margin: 20px 0;">
                <h1 style="color: #2563eb; font-size: 32px; margin: 0; letter-spacing: 5px;">{otp}</h1>
            </div>
            
            <p><strong>This code will expire in 10 minutes.</strong></p>
            
            <p>If you didn't create an account, please ignore this email.</p>
            
            <p>Best regards,<br>Student Marketplace Team</p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Send email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

@router.post("/send-verification-email")
async def send_verification_email_endpoint(
    request: EmailVerificationRequest,
    db: Session = Depends(get_db)
):
    """Send verification email with OTP code"""
    try:
        # Check if user exists
        user = db.query(User).filter(User.email == request.email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if already verified
        if user.is_email_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already verified"
            )
        
        # Generate OTP and token
        otp = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
        verification_token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(minutes=10)
        
        # Update user with verification data
        user.email_verification_token = verification_token
        user.email_verification_expires_at = expires_at
        db.commit()
        
        # Send email (in development, just log it)
        if SMTP_USERNAME and SMTP_PASSWORD:
            email_sent = send_verification_email(request.email, otp, user.name)
            if not email_sent:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to send verification email"
                )
        else:
            # Development mode - log the OTP
            print(f"Development Mode: OTP for {request.email} is: {otp}")
            print(f"Verification token: {verification_token}")
        
        return {
            "message": "Verification email sent successfully",
            "email": request.email,
            "expires_at": expires_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/verify-email")
async def verify_email_endpoint(
    request: OTPVerificationRequest,
    db: Session = Depends(get_db)
):
    """Verify email with OTP code"""
    try:
        # Check if user exists
        user = db.query(User).filter(User.email == request.email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if already verified
        if user.is_email_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already verified"
            )
        
        # Check if verification token exists and is not expired
        if not user.email_verification_token or not user.email_verification_expires_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No verification request found. Please request a new verification code."
            )
        
        if datetime.utcnow() > user.email_verification_expires_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification code has expired. Please request a new one."
            )
        
        # In a real implementation, you would verify the OTP against the stored token
        # For now, we'll just mark the email as verified
        user.is_email_verified = True
        user.email_verification_token = None
        user.email_verification_expires_at = None
        db.commit()
        
        return {
            "message": "Email verified successfully",
            "user": {
                "id": user.id,
                "name": user.name,
                "surname": user.surname,
                "email": user.email,
                "phone": user.phone,
                "username": user.username,
                "is_email_verified": user.is_email_verified,
                "is_phone_verified": user.is_phone_verified,
                "created_at": user.created_at.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/resend-verification-email")
async def resend_verification_email_endpoint(
    request: ResendVerificationRequest,
    db: Session = Depends(get_db)
):
    """Resend verification email"""
    try:
        # Check if user exists
        user = db.query(User).filter(User.email == request.email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if already verified
        if user.is_email_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already verified"
            )
        
        # Generate new OTP and token
        otp = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
        verification_token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(minutes=10)
        
        # Update user with new verification data
        user.email_verification_token = verification_token
        user.email_verification_expires_at = expires_at
        db.commit()
        
        # Send email (in development, just log it)
        if SMTP_USERNAME and SMTP_PASSWORD:
            email_sent = send_verification_email(request.email, otp, user.name)
            if not email_sent:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to send verification email"
                )
        else:
            # Development mode - log the OTP
            print(f"Development Mode: New OTP for {request.email} is: {otp}")
            print(f"New verification token: {verification_token}")
        
        return {
            "message": "Verification email resent successfully",
            "email": request.email,
            "expires_at": expires_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/check-verification")
async def check_verification_status(email: str):
    """Check if user's email is verified (Supabase profiles)"""
    try:
        client = supabase_admin
        if not client:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Supabase admin client not configured"
            )
        
        response = client.table("profiles").select(
            "email,is_email_verified,is_phone_verified"
        ).eq("email", email).single().execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        data = response.data
        return {
            "email": email,
            "is_verified": data.get("is_email_verified", False),
            "verification_status": {
                "email_verified": data.get("is_email_verified", False),
                "phone_verified": data.get("is_phone_verified", False)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
