#!/usr/bin/env python3
"""
Startup script for StartupScout.
Downloads necessary data files from S3 before starting the main application.
"""

import os
import sys
import time
from pathlib import Path
from utils.s3_storage import get_data_file

def download_required_files():
    """Download required data files from S3."""
    print("🔄 Downloading data files from S3...")
    
    required_files = [
        "startup_posts_clean.json",
        "startup_data.json"
    ]
    
    downloaded_files = []
    failed_files = []
    
    for filename in required_files:
        print(f"📥 Downloading {filename}...")
        local_path = get_data_file(filename)
        
        if local_path:
            downloaded_files.append(filename)
            print(f"✅ Downloaded {filename}")
        else:
            failed_files.append(filename)
            print(f"❌ Failed to download {filename}")
    
    if failed_files:
        print(f"⚠️  Warning: {len(failed_files)} files failed to download: {failed_files}")
        print("   The app will start but some features may not work.")
    
    print(f"✅ Startup complete: {len(downloaded_files)} files ready")
    return len(downloaded_files) > 0

def main():
    """Main startup function."""
    print("🚀 Starting StartupScout...")
    
    # Check if we're in production (Railway sets this)
    if os.getenv('RAILWAY_ENVIRONMENT'):
        print("🌐 Running in Railway production environment")
        
        # Download data files from S3
        if not download_required_files():
            print("⚠️  Warning: Some data files could not be downloaded")
            print("   Continuing startup anyway...")
    
    else:
        print("🏠 Running in local development environment")
    
    # Start the main application
    print("🎯 Starting FastAPI application...")
    os.execv(sys.executable, [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", os.getenv("PORT", "8000")])

if __name__ == "__main__":
    main()
