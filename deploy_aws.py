#!/usr/bin/env python3
"""
AWS deployment script for StartupScout
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

def check_docker():
    """Check if Docker is installed and running."""
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Docker found: {result.stdout.strip()}")
            
            # Check if Docker daemon is running
            result = subprocess.run(['docker', 'info'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Docker daemon is running")
                return True
            else:
                print("❌ Docker daemon is not running")
                return False
    except FileNotFoundError:
        print("❌ Docker not found. Please install it first:")
        print("   https://docs.docker.com/get-docker/")
        return False

def deploy_app_runner():
    """Deploy using AWS App Runner."""
    print("🚀 Deploying to AWS App Runner...")
    
    # Check if apprunner.yaml exists
    if not Path("apprunner.yaml").exists():
        print("❌ apprunner.yaml not found")
        return False
    
    print("📋 App Runner deployment steps:")
    print("1. Go to AWS Console → App Runner")
    print("2. Create service")
    print("3. Source: GitHub")
    print("4. Connect your GitHub repository")
    print("5. Use apprunner.yaml configuration")
    print("6. Set environment variables")
    
    return True

def deploy_ecs():
    """Deploy using AWS ECS with Fargate."""
    print("🚀 Deploying to AWS ECS...")
    
    # Build Docker image
    print("📦 Building Docker image...")
    result = subprocess.run([
        'docker', 'build', 
        '-f', 'Dockerfile.aws',
        '-t', 'startupscout:latest',
        '.'
    ])
    
    if result.returncode != 0:
        print("❌ Docker build failed")
        return False
    
    print("✅ Docker image built successfully")
    
    # Tag for ECR
    print("🏷️  Tagging image for ECR...")
    # You'll need to replace with your actual ECR repository URI
    ecr_uri = "your-account.dkr.ecr.region.amazonaws.com/startupscout"
    
    subprocess.run(['docker', 'tag', 'startupscout:latest', f'{ecr_uri}:latest'])
    
    print("📋 ECS deployment steps:")
    print("1. Create ECR repository")
    print("2. Push image to ECR")
    print("3. Create ECS cluster")
    print("4. Create task definition")
    print("5. Create service")
    
    return True

def main():
    """Main deployment function."""
    print("🚀 StartupScout AWS Deployment")
    print("=" * 40)
    
    # Check prerequisites
    if not check_aws_cli():
        return False
    
    if not check_docker():
        return False
    
    # Choose deployment method
    print("\nChoose deployment method:")
    print("1. AWS App Runner (easiest)")
    print("2. AWS ECS with Fargate")
    print("3. Manual instructions")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        return deploy_app_runner()
    elif choice == "2":
        return deploy_ecs()
    elif choice == "3":
        print_manual_instructions()
        return True
    else:
        print("❌ Invalid choice")
        return False

def print_manual_instructions():
    """Print manual deployment instructions."""
    print("\n📚 Manual AWS Deployment Instructions")
    print("=" * 50)
    
    print("\n🔧 Prerequisites:")
    print("- AWS CLI configured")
    print("- Docker installed")
    print("- Full requirements.txt (✅ Done)")
    
    print("\n🚀 Option 1: AWS App Runner")
    print("1. Go to AWS Console → App Runner")
    print("2. Create service")
    print("3. Source: GitHub")
    print("4. Connect repository: SadafFatma333/startupscout")
    print("5. Use apprunner.yaml")
    print("6. Set environment variables:")
    print("   - OPENAI_API_KEY")
    print("   - DB_HOST, DB_NAME, DB_USER, DB_PASSWORD")
    print("   - REDIS_URL")
    
    print("\n🚀 Option 2: AWS ECS")
    print("1. Create ECR repository")
    print("2. Build and push Docker image")
    print("3. Create ECS cluster")
    print("4. Create task definition")
    print("5. Create service")
    
    print("\n🚀 Option 3: AWS EC2")
    print("1. Launch EC2 instance")
    print("2. Install Docker")
    print("3. Clone repository")
    print("4. Run with docker-compose.aws.yml")

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Deployment setup complete!")
    else:
        print("\n❌ Deployment failed")
        sys.exit(1)
