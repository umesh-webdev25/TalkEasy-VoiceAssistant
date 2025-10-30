#!/usr/bin/env python3
"""
JWT Secret Key Generator for Vercel Deployment
Run this script to generate a secure JWT secret key for your Vercel environment variables.
"""

import secrets
import os

def generate_jwt_secret():
    """Generate a secure JWT secret key"""
    # Generate a 32-byte (256-bit) random secret and convert to hex
    secret = secrets.token_hex(32)
    return secret

def main():
    print("🔐 JWT Secret Key Generator for Vercel")
    print("=" * 50)

    secret = generate_jwt_secret()

    print(f"\n✅ Generated JWT Secret Key: {secret}")
    print(f"   Length: {len(secret)} characters")
    print(f"   Security: {len(secret) * 4} bits")

    print("\n📋 Copy this value to your Vercel Environment Variables:")
    print(f"   JWT_SECRET_KEY={secret}")

    print("\n⚠️  IMPORTANT:")
    print("   - Keep this secret secure and never commit it to version control")
    print("   - Use the same secret for both local development and production")
    print("   - If you change this secret, all existing JWT tokens will become invalid")

    # Also show how to set it in .env for local development
    env_file = ".env"
    if os.path.exists(env_file):
        print(f"\n💡 For local development, add to your {env_file} file:")
        print(f"   JWT_SECRET_KEY={secret}")
    else:
        print(f"\n💡 Create a {env_file} file for local development with:")
        print(f"   JWT_SECRET_KEY={secret}")

if __name__ == "__main__":
    main()