#!/usr/bin/env python3
"""
LangFuse Setup Script
Run this to configure LangFuse tracing for your StartupScout app.
"""

import os
import sys

def setup_langfuse():
    print("LangFuse Setup for StartupScout")
    print("=" * 50)
    
    # Check if .env file exists
    env_file = ".env"
    if not os.path.exists(env_file):
        print("No .env file found. Creating one...")
        with open(env_file, "w") as f:
            f.write("# StartupScout Environment Variables\n")
    
    # Read existing .env content
    with open(env_file, "r") as f:
        content = f.read()
    
    # Check if LangFuse is already configured
    if "LANGFUSE_ENABLED=true" in content:
        print("LangFuse appears to be already configured!")
        return
    
    print("\nPlease get your API keys from LangFuse Cloud:")
    print("1. Go to your LangFuse dashboard")
    print("2. Click Settings → API Keys")
    print("3. Copy your Public Key and Secret Key")
    
    print("\nEnter your LangFuse credentials:")
    public_key = input("Public Key (pk_lf_...): ").strip()
    secret_key = input("Secret Key (sk_lf_...): ").strip()
    
    if not public_key or not secret_key:
        print("Keys cannot be empty!")
        return
    
    # Add LangFuse configuration
    langfuse_config = f"""
# LangFuse Tracing Configuration
LANGFUSE_ENABLED=true
LANGFUSE_HOST=https://cloud.langfuse.com
LANGFUSE_PUBLIC_KEY={public_key}
LANGFUSE_SECRET_KEY={secret_key}
LANGFUSE_SAMPLING_RATE=1.0
"""
    
    # Append to .env file
    with open(env_file, "a") as f:
        f.write(langfuse_config)
    
    print("\nLangFuse configuration added to .env file!")
    print("\nNext steps:")
    print("1. Restart your app: uvicorn app.main:app --reload")
    print("2. Make a request to /ask endpoint")
    print("3. Check your LangFuse dashboard for traces!")
    
    print(f"\nYour LangFuse dashboard: https://cloud.langfuse.com/project/cmgwpu3rr000ead070ulzh2ho")

if __name__ == "__main__":
    setup_langfuse()
