#!/usr/bin/env python3
"""
Startup script for StartupScout.
Downloads necessary data files from S3 before starting the main application.
"""

import os
import sys

def main():
    """Main startup function."""
    print("🚀 Starting StartupScout...")
    
    # Check if we're in production (Railway sets this)
    if os.getenv('RAILWAY_ENVIRONMENT'):
        print("🌐 Running in Railway production environment")
        
        # Try to download data files from S3 if credentials are available
        try:
            from utils.s3_storage import get_data_file
            
            required_files = ["startup_posts_clean.json", "startup_data.json"]
            downloaded_count = 0
            
            for filename in required_files:
                local_path = get_data_file(filename)
                if local_path:
                    downloaded_count += 1
                    print(f"✅ Downloaded {filename}")
                else:
                    print(f"⚠️  Could not download {filename}")
            
            if downloaded_count > 0:
                print(f"✅ Downloaded {downloaded_count} data files from S3")
            else:
                print("⚠️  No data files downloaded - app will run with limited functionality")
                
        except Exception as e:
            print(f"⚠️  S3 download failed: {e}")
            print("   App will start with limited functionality")
    
    else:
        print("🏠 Running in local development environment")
    
    # Start the main application
    print("🎯 Starting FastAPI application...")
    os.execv(sys.executable, [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", os.getenv("PORT", "8000")])

if __name__ == "__main__":
    main()
