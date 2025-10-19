#!/usr/bin/env python3
"""
Script to upload StartupScout data files to S3.
Run this before deploying to Railway to move large data files out of the Docker image.
"""

import os
import sys
from pathlib import Path
from utils.s3_storage import upload_data_files

def main():
    print("🚀 Uploading StartupScout data files to S3...")
    
    # Check if AWS credentials are set
    if not os.getenv('AWS_ACCESS_KEY_ID'):
        print("❌ AWS_ACCESS_KEY_ID not set. Please set your AWS credentials:")
        print("   export AWS_ACCESS_KEY_ID=your_access_key")
        print("   export AWS_SECRET_ACCESS_KEY=your_secret_key")
        print("   export S3_BUCKET_NAME=your_bucket_name")
        sys.exit(1)
    
    # Upload data files
    try:
        upload_data_files()
        print("✅ Successfully uploaded data files to S3!")
        print("\n📋 Next steps:")
        print("1. Add these environment variables to Railway:")
        print("   - AWS_ACCESS_KEY_ID")
        print("   - AWS_SECRET_ACCESS_KEY") 
        print("   - S3_BUCKET_NAME")
        print("2. Deploy to Railway")
        print("3. The app will download data files from S3 on startup")
    except Exception as e:
        print(f"❌ Error uploading to S3: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
