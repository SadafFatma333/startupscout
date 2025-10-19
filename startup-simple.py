#!/usr/bin/env python3
"""
Simple startup script for StartupScout without S3 dependencies.
"""

import os
import sys

def main():
    """Main startup function."""
    print("🚀 Starting StartupScout...")
    
    # Start the main application directly
    print("🎯 Starting FastAPI application...")
    os.execv(sys.executable, [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", os.getenv("PORT", "8000")])

if __name__ == "__main__":
    main()
