"""
Supabase Configuration
Initializes Supabase client for the application
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Supabase configuration from environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")  # anon/public key
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")  # service_role key (server-side only)

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        "Missing Supabase configuration. Please set SUPABASE_URL and SUPABASE_KEY in environment variables."
    )

# Create Supabase client (uses anon key - for client-side operations)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Service role client (for admin operations - use carefully!)
# This bypasses Row Level Security
supabase_admin: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY) if SUPABASE_SERVICE_KEY else None

