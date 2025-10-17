#!/usr/bin/env python3
"""
Production deployment script for StartupScout
"""
import os
import sys
import subprocess

def check_production_requirements():
    """Check if all production environment variables are set"""
    required_vars = ["DB_PASSWORD", "DB_HOST"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nSet these variables before running in production:")
        print("export DB_PASSWORD='your_secure_password'")
        print("export DB_HOST='your-production-host.com'")
        return False
    
    return True

def deploy_to_production():
    """Deploy to production"""
    print("🚀 Deploying to production...")
    
    # Set production environment
    os.environ["ENV"] = "prod"
    
    # Check requirements
    if not check_production_requirements():
        sys.exit(1)
    
    print("✅ Environment variables configured")
    
    # Run database migration/seeding
    print("📊 Seeding production database...")
    try:
        result = subprocess.run([sys.executable, "ingestion/seed_db.py"], 
                              capture_output=True, text=True, check=True)
        print("✅ Database seeded successfully")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"❌ Database seeding failed: {e}")
        print(f"Error: {e.stderr}")
        sys.exit(1)
    
    # Start the application
    print("🚀 Starting production server...")
    print("Run: uvicorn app:app --host 0.0.0.0 --port 8000")

if __name__ == "__main__":
    deploy_to_production()

