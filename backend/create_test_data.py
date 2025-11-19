"""
Script to create test data:
- Admin user
- End user
- Admin role
- 5 sample products

Run this script to populate your Supabase database with test data.

Usage:
    python backend/create_test_data.py
"""

import sys
import os
import time

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from supabase_config import supabase, supabase_admin

# Check if admin client is available
if not supabase_admin:
    print("[ERROR] SUPABASE_SERVICE_KEY is not set in .env file!")
    print("Please add SUPABASE_SERVICE_KEY to backend/.env file")
    print("You can find it in Supabase Dashboard -> Settings -> API -> service_role key")
    sys.exit(1)

# Test User Credentials
ADMIN_EMAIL = "admin@studentmarketplace.com"
ADMIN_PASSWORD = "Admin123!@#"
ADMIN_NAME = "Admin"
ADMIN_SURNAME = "User"
ADMIN_USERNAME = "admin"
ADMIN_PHONE = "+27123456789"

END_USER_EMAIL = "user@studentmarketplace.com"
END_USER_PASSWORD = "User123!@#"
END_USER_NAME = "John"
END_USER_SURNAME = "Doe"
END_USER_USERNAME = "johndoe"
END_USER_PHONE = "+27987654321"

# Sample Products
SAMPLE_PRODUCTS = [
    {
        "title": "MacBook Pro 13-inch",
        "description": "Excellent condition MacBook Pro, 8GB RAM, 256GB SSD. Perfect for students. Comes with charger and original box.",
        "price": 8500.00,
        "category": "Electronics",
        "stock_quantity": 1,
        "images": []
    },
    {
        "title": "Calculus Textbook - 3rd Edition",
        "description": "Calculus: Early Transcendentals 3rd Edition. Used but in great condition. No writing or highlighting.",
        "price": 350.00,
        "category": "Books",
        "stock_quantity": 1,
        "images": []
    },
    {
        "title": "Wireless Mouse - Logitech",
        "description": "Logitech MX Master 3 wireless mouse. Barely used, like new condition. Perfect for laptop users.",
        "price": 450.00,
        "category": "Electronics",
        "stock_quantity": 2,
        "images": []
    },
    {
        "title": "Student Desk Chair",
        "description": "Ergonomic office chair, adjustable height. Great for long study sessions. Some wear but fully functional.",
        "price": 600.00,
        "category": "Furniture",
        "stock_quantity": 1,
        "images": []
    },
    {
        "title": "Scientific Calculator - TI-84",
        "description": "Texas Instruments TI-84 Plus CE graphing calculator. Used for one semester only. Includes case and manual.",
        "price": 800.00,
        "category": "Electronics",
        "stock_quantity": 1,
        "images": []
    }
]

def create_admin_user():
    """Create admin user via Supabase Auth"""
    print("[*] Creating admin user...")
    try:
        # Check if user already exists
        try:
            response = supabase_admin.auth.admin.list_users()
            users = response if isinstance(response, list) else response.users if hasattr(response, 'users') else []
            for user in users:
                user_email = user.email if hasattr(user, 'email') else user.get('email', '')
                user_id = user.id if hasattr(user, 'id') else user.get('id')
                if user_email == ADMIN_EMAIL:
                    print(f"[OK] Admin user already exists: {ADMIN_EMAIL}")
                    # Get profile
                    profile = supabase_admin.table("profiles").select("*").eq("id", user_id).single().execute()
                    if profile.data:
                        return user_id
        except:
            pass
        
        # Try to create user - if it fails, we'll provide manual instructions
        try:
            result = supabase_admin.auth.admin.create_user({
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD,
                "email_confirm": True,  # Auto-confirm email
                "user_metadata": {
                    "name": ADMIN_NAME,
                    "surname": ADMIN_SURNAME,
                    "username": ADMIN_USERNAME,
                    "phone": ADMIN_PHONE
                }
            })
            
            admin_user_id = result.user.id
            print(f"[OK] Admin user created: {ADMIN_EMAIL}")
            print(f"   User ID: {admin_user_id}")
        except Exception as create_error:
            error_msg = str(create_error).lower()
            print(f"[!] Could not create admin user automatically: {create_error}")
            print("[!] This might be due to a database trigger issue.")
            print("[!] Please create the user manually via:")
            print("    1. Supabase Dashboard -> Authentication -> Add User")
            print("    2. Or use the Flutter app registration")
            print(f"[!] Then run this script again - it will detect existing users.")
            raise Exception("User creation failed. Please create users manually first.")
        
        # Wait for profile to be created by trigger
        time.sleep(3)
        
        # Verify profile - try with admin client first
        try:
            profile_response = supabase_admin.table("profiles").select("*").eq("id", admin_user_id).single().execute()
            if profile_response.data:
                print(f"[OK] Admin profile found")
            else:
                raise Exception("Profile not found")
        except:
            print("[!] Profile not found, creating manually...")
            # Create profile manually if trigger didn't work
            try:
                supabase_admin.table("profiles").insert({
                    "id": admin_user_id,
                    "email": ADMIN_EMAIL,
                    "name": ADMIN_NAME,
                    "surname": ADMIN_SURNAME,
                    "username": ADMIN_USERNAME,
                    "phone": ADMIN_PHONE
                }).execute()
                print("[OK] Profile created manually")
            except Exception as e:
                error_msg = str(e).lower()
                if "duplicate" in error_msg or "already exists" in error_msg:
                    print("[OK] Profile already exists")
                else:
                    print(f"[!] Could not create profile: {e}")
        
        return admin_user_id
            
    except Exception as e:
        error_msg = str(e)
        if "already registered" in error_msg.lower() or "user already exists" in error_msg.lower() or "already been registered" in error_msg.lower():
            print(f"[OK] Admin user already exists: {ADMIN_EMAIL}")
            # Try to get existing user
            try:
                response = supabase_admin.auth.admin.list_users()
                users = response if isinstance(response, list) else response.users if hasattr(response, 'users') else []
                for user in users:
                    user_email = user.email if hasattr(user, 'email') else user.get('email', '')
                    if user_email == ADMIN_EMAIL:
                        return user.id if hasattr(user, 'id') else user.get('id')
            except:
                pass
        print(f"[ERROR] Error creating admin user: {e}")
        raise

def create_end_user():
    """Create end user via Supabase Auth"""
    print("\n[*] Creating end user...")
    try:
        # Check if user already exists
        try:
            response = supabase_admin.auth.admin.list_users()
            users = response if isinstance(response, list) else response.users if hasattr(response, 'users') else []
            for user in users:
                user_email = user.email if hasattr(user, 'email') else user.get('email', '')
                user_id = user.id if hasattr(user, 'id') else user.get('id')
                if user_email == END_USER_EMAIL:
                    print(f"[OK] End user already exists: {END_USER_EMAIL}")
                    # Get profile
                    profile = supabase_admin.table("profiles").select("*").eq("id", user_id).single().execute()
                    if profile.data:
                        return user_id
        except:
            pass
        
        # Try to create user - if it fails, we'll provide manual instructions
        try:
            result = supabase_admin.auth.admin.create_user({
                "email": END_USER_EMAIL,
                "password": END_USER_PASSWORD,
                "email_confirm": True,  # Auto-confirm email
                "user_metadata": {
                    "name": END_USER_NAME,
                    "surname": END_USER_SURNAME,
                    "username": END_USER_USERNAME,
                    "phone": END_USER_PHONE
                }
            })
            
            end_user_id = result.user.id
            print(f"[OK] End user created: {END_USER_EMAIL}")
            print(f"   User ID: {end_user_id}")
        except Exception as create_error:
            error_msg = str(create_error).lower()
            print(f"[!] Could not create end user automatically: {create_error}")
            print("[!] This might be due to a database trigger issue.")
            print("[!] Please create the user manually via:")
            print("    1. Supabase Dashboard -> Authentication -> Add User")
            print("    2. Or use the Flutter app registration")
            print(f"[!] Then run this script again - it will detect existing users.")
            raise Exception("User creation failed. Please create users manually first.")
        
        # Wait for profile to be created by trigger
        time.sleep(3)
        
        # Verify profile - try with admin client first
        try:
            profile_response = supabase_admin.table("profiles").select("*").eq("id", end_user_id).single().execute()
            if profile_response.data:
                print(f"[OK] End user profile found")
            else:
                raise Exception("Profile not found")
        except:
            print("[!] Profile not found, creating manually...")
            # Create profile manually if trigger didn't work
            try:
                supabase_admin.table("profiles").insert({
                    "id": end_user_id,
                    "email": END_USER_EMAIL,
                    "name": END_USER_NAME,
                    "surname": END_USER_SURNAME,
                    "username": END_USER_USERNAME,
                    "phone": END_USER_PHONE
                }).execute()
                print("[OK] Profile created manually")
            except Exception as e:
                error_msg = str(e).lower()
                if "duplicate" in error_msg or "already exists" in error_msg:
                    print("[OK] Profile already exists")
                else:
                    print(f"[!] Could not create profile: {e}")
        
        return end_user_id
            
    except Exception as e:
        error_msg = str(e)
        if "already registered" in error_msg.lower() or "user already exists" in error_msg.lower() or "already been registered" in error_msg.lower():
            print(f"[OK] End user already exists: {END_USER_EMAIL}")
            # Try to get existing user
            try:
                response = supabase_admin.auth.admin.list_users()
                users = response if isinstance(response, list) else response.users if hasattr(response, 'users') else []
                for user in users:
                    user_email = user.email if hasattr(user, 'email') else user.get('email', '')
                    if user_email == END_USER_EMAIL:
                        return user.id if hasattr(user, 'id') else user.get('id')
            except:
                pass
        print(f"[ERROR] Error creating end user: {e}")
        raise

def ensure_admin_role_exists():
    """Ensure admin role exists in database"""
    print("\n[*] Checking admin role...")
    try:
        # Check if admin role exists (use admin client to bypass RLS)
        roles = supabase_admin.table("roles").select("*").eq("name", "admin").execute()
        
        if roles.data and len(roles.data) > 0:
            admin_role_id = roles.data[0]["id"]
            print(f"[OK] Admin role exists (ID: {admin_role_id})")
            return admin_role_id
        else:
            # Create admin role
            print("   Creating admin role...")
            result = supabase_admin.table("roles").insert({
                "name": "admin",
                "description": "Administrator role with full access"
            }).execute()
            
            if result.data:
                admin_role_id = result.data[0]["id"]
                print(f"[OK] Admin role created (ID: {admin_role_id})")
                return admin_role_id
            else:
                raise Exception("Failed to create admin role")
    except Exception as e:
        print(f"[!] Error with admin role: {e}")
        return None

def assign_admin_role(admin_user_id: str, admin_role_id: int):
    """Assign admin role to user"""
    print("\n[*] Assigning admin role to user...")
    try:
        # Check if role already assigned (use admin client to bypass RLS)
        existing = supabase_admin.table("user_roles").select("*").eq("user_id", admin_user_id).eq("role_id", admin_role_id).execute()
        
        if existing.data and len(existing.data) > 0:
            print("[OK] Admin role already assigned")
            return True
        
        # Assign role
        result = supabase_admin.table("user_roles").insert({
            "user_id": admin_user_id,
            "role_id": admin_role_id
        }).execute()
        
        if result.data:
            print("[OK] Admin role assigned successfully")
            return True
        else:
            print("[!] Failed to assign admin role")
            return False
    except Exception as e:
        print(f"[!] Error assigning admin role: {e}")
        return False

def create_products_directly(admin_user_id: str):
    """Create products directly in Supabase database"""
    print("\n[*] Creating products directly in database...")
    
    created_products = []
    
    for i, product_data in enumerate(SAMPLE_PRODUCTS, 1):
        try:
            print(f"\n   Creating product {i}/5: {product_data['title']}")
            
            # Prepare product data for Supabase
            product_payload = {
                "title": product_data["title"],
                "description": product_data["description"],
                "price": product_data["price"],
                "category": product_data["category"],
                "seller_id": admin_user_id,  # UUID from Supabase
                "approved": True,
                "discontinued": False,
                "images": product_data.get("images", []),
                "stock_quantity": product_data.get("stock_quantity", 1),
                "initial_stock": product_data.get("stock_quantity", 1),
                "sold_quantity": 0,
                "low_stock_threshold": 5,
                "is_out_of_stock": product_data.get("stock_quantity", 1) == 0,
                "created_via": "admin_web"
            }
            
            # Insert into database
            result = supabase_admin.table("products").insert(product_payload).execute()
            
            if result.data:
                product = result.data[0]
                print(f"   [OK] Created: {product_data['title']} (ID: {product['id']})")
                created_products.append(product)
            else:
                print(f"   [ERROR] Failed to create product")
                
        except Exception as e:
            print(f"   [ERROR] Error creating product {i}: {e}")
    
    return created_products

def main():
    """Main function to create all test data"""
    print("=" * 60)
    print("Creating Test Data for Student Marketplace")
    print("=" * 60)
    
    try:
        # Step 1: Ensure admin role exists
        admin_role_id = ensure_admin_role_exists()
        
        # Step 2: Create admin user
        admin_user_id = create_admin_user()
        
        # Step 3: Assign admin role
        if admin_role_id and admin_user_id:
            assign_admin_role(admin_user_id, admin_role_id)
        
        # Step 4: Create end user
        end_user_id = create_end_user()
        
        # Step 5: Create products
        if admin_user_id:
            products = create_products_directly(admin_user_id)
            print(f"\n[OK] Created {len(products)} products")
        else:
            print("\n[!] Could not get admin user ID, skipping product creation")
            products = []
        
        # Step 6: Print summary
        print("\n" + "=" * 60)
        print("[OK] Test Data Creation Complete!")
        print("=" * 60)
        print("\nLogin Credentials:")
        print("\nADMIN USER:")
        print(f"   Email: {ADMIN_EMAIL}")
        print(f"   Password: {ADMIN_PASSWORD}")
        print(f"   Username: {ADMIN_USERNAME}")
        print(f"   Phone: {ADMIN_PHONE}")
        
        print("\nEND USER:")
        print(f"   Email: {END_USER_EMAIL}")
        print(f"   Password: {END_USER_PASSWORD}")
        print(f"   Username: {END_USER_USERNAME}")
        print(f"   Phone: {END_USER_PHONE}")
        
        print(f"\n📦 Products Created: {len(products)}")
        for i, product in enumerate(products, 1):
            print(f"   {i}. {product.get('title', 'Unknown')} - R{product.get('price', 0):.2f}")
        
        print("\nIMPORTANT:")
        print("   1. Product images need to be added manually (see HOW_TO_ADD_IMAGES.md)")
        print("   2. You can add images via admin panel or Supabase Storage")
        
        print("\nNext Steps:")
        print("   1. Login to admin panel with admin credentials")
        print("   2. Verify you can see the products")
        print("   3. Add images to products (see HOW_TO_ADD_IMAGES.md)")
        print("   4. Test login with end user credentials in Flutter app")
        
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

