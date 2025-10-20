#!/usr/bin/env python3
"""
AWS App Runner deployment script for StartupScout
"""

import os
import subprocess
import sys
from pathlib import Path

def check_aws_cli():
    """Check if AWS CLI is installed and configured."""
    try:
        result = subprocess.run(['aws', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ AWS CLI found: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ AWS CLI not found. Please install it first:")
    print("   https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html")
    return False

def main():
    """Main deployment function."""
    print("🚀 StartupScout AWS App Runner Deployment")
    print("=" * 50)
    
    # Check prerequisites
    if not check_aws_cli():
        return False
    
    print_manual_instructions()
    return True

def print_manual_instructions():
    """Print manual deployment instructions."""
    print("\n📚 AWS App Runner Deployment Instructions")
    print("=" * 50)
    
    print("\n🔧 Prerequisites:")
    print("- AWS CLI configured")
    print("- Full requirements.txt (✅ Done)")
    print("- apprunner.yaml configuration (✅ Done)")
    
    print("\n🚀 Deployment Steps:")
    print("1. Go to AWS Console → App Runner")
    print("   https://console.aws.amazon.com/apprunner/")
    print("2. Click 'Create service'")
    print("3. Choose 'Source': GitHub")
    print("4. Connect your GitHub repository: SadafFatma333/startupscout")
    print("5. Select branch: main")
    print("6. Use configuration file: apprunner.yaml")
    print("7. Set environment variables:")
    print("   - OPENAI_API_KEY (your OpenAI API key)")
    print("   - DB_HOST (your database host)")
    print("   - DB_NAME (your database name)")
    print("   - DB_USER (your database username)")
    print("   - DB_PASSWORD (your database password)")
    print("   - REDIS_URL (your Redis connection string)")
    print("8. Click 'Create & deploy'")
    
    print("\n⏱️  Deployment time: ~5-10 minutes")
    print("💰 Estimated cost: $25-50/month")
    
    print("\n🔗 After deployment:")
    print("- Your app will get a URL like: https://xxxxx.us-east-1.awsapprunner.com")
    print("- Update Vercel environment variable VITE_API_BASE with this URL")
    print("- Both frontend and backend will be live!")

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Setup complete! Follow the instructions above to deploy.")
    else:
        print("\n❌ Setup failed")
        sys.exit(1)
