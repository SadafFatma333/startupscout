#!/usr/bin/env python3
"""
Deployment script for StartupScout.
Supports multiple deployment platforms.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description, check=True):
    """Run a command and handle errors."""
    print(f"\n{description}")
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=check, capture_output=True, text=True)
        print("Success!")
        if result.stdout:
            print(result.stdout)
        return True, result
    except subprocess.CalledProcessError as e:
        print(f"Failed with exit code {e.returncode}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False, e


def check_prerequisites():
    """Check if required tools are installed."""
    print("Checking prerequisites...")
    
    required_tools = {
        "git": "Git version control",
        "python3": "Python interpreter",
        "pip3": "Python package manager"
    }
    
    missing_tools = []
    
    for tool, description in required_tools.items():
        success, _ = run_command([tool, "--version"], f"Checking {description}", check=False)
        if not success:
            missing_tools.append(tool)
    
    if missing_tools:
        print(f"Missing required tools: {', '.join(missing_tools)}")
        print("Please install the missing tools and try again.")
        return False
    
    print("All prerequisites satisfied!")
    return True


def deploy_railway():
    """Deploy to Railway."""
    print("Deploying to Railway...")
    
    # Check if Railway CLI is installed
    success, _ = run_command(["railway", "--version"], "Checking Railway CLI", check=False)
    if not success:
        print("Installing Railway CLI...")
        success, _ = run_command(["npm", "install", "-g", "@railway/cli"], "Installing Railway CLI")
        if not success:
            return False
    
    # Login to Railway
    print("Logging into Railway...")
    success, _ = run_command(["railway", "login"], "Railway Login")
    if not success:
        print("Failed to login to Railway. Please try again.")
        return False
    
    # Create new project
    print("Creating Railway project...")
    success, _ = run_command(["railway", "new"], "Creating Railway Project")
    if not success:
        return False
    
    # Deploy
    print("Deploying application...")
    success, _ = run_command(["railway", "up"], "Deploying to Railway")
    if not success:
        return False
    
    # Get deployment URL
    print("Getting deployment URL...")
    success, result = run_command(["railway", "domain"], "Getting Railway URL")
    if success and result.stdout:
        url = result.stdout.strip()
        print(f"Deployment successful!")
        print(f"Your app is live at: https://{url}")
        print(f"API docs: https://{url}/docs")
        print(f"Health check: https://{url}/health")
        print(f"Metrics: https://{url}/metrics")
        print("")
        print("REQUIRED: Set up environment variables in Railway:")
        print("1. Go to your Railway project dashboard")
        print("2. Click on your service → Variables tab")
        print("3. Add these REQUIRED variables:")
        print("")
        print("   OPENAI_API_KEY=sk-your-openai-key-here")
        print("   JWT_SECRET=your-super-secret-jwt-key-change-this")
        print("   ADMIN_API_KEY=your-admin-api-key-change-this")
        print("")
        print("4. Railway automatically provides DATABASE_URL")
        print("5. Restart your service after adding variables")
        print("")
        print("Get your OpenAI API key from: https://platform.openai.com/api-keys")
    
    return True




def setup_environment():
    """Set up environment variables."""
    print("Setting up environment...")
    
    env_file = Path(".env.dev")
    if not env_file.exists():
        print("Creating environment file...")
        
        env_content = """# StartupScout Environment Configuration

# Database
DB_HOST=localhost
DB_NAME=startupscout
DB_USER=your_db_user
DB_PASSWORD=your_db_password

# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
JWT_SECRET=your_jwt_secret_change_me
ADMIN_API_KEY=your_admin_api_key

# Optional: LangFuse Tracing
LANGFUSE_ENABLED=false
LANGFUSE_HOST=https://cloud.langfuse.com
LANGFUSE_PUBLIC_KEY=your_public_key
LANGFUSE_SECRET_KEY=your_secret_key
LANGFUSE_SAMPLING_RATE=0.25

# Optional: LangGraph
USE_LANGGRAPH=false
"""
        
        with open(env_file, "w") as f:
            f.write(env_content)
        
        print(f"Created {env_file}")
        print("Please edit the environment file with your actual values.")
    
    return True


def install_dependencies():
    """Install Python dependencies."""
    print("Installing dependencies...")
    
    success, _ = run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], "Install Dependencies")
    if not success:
        return False
    
    print("Dependencies installed!")
    return True


def run_tests():
    """Run tests before deployment."""
    print("Running tests...")
    
    success, _ = run_command([sys.executable, "run_tests.py", "--type", "fast"], "Run Fast Tests")
    if not success:
        print("Some tests failed. Continue deployment? (y/n)")
        response = input().lower()
        if response != 'y':
            return False
    
    return True


def main():
    """Main deployment function."""
    parser = argparse.ArgumentParser(description="StartupScout Deployment Script")
    parser.add_argument(
        "platform",
        choices=["railway", "local"],
        help="Deployment platform"
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip running tests before deployment"
    )
    parser.add_argument(
        "--skip-deps",
        action="store_true",
        help="Skip installing dependencies"
    )
    
    args = parser.parse_args()
    
    print("StartupScout Deployment Script")
    print("=" * 50)
    
    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)
    
    # Set up environment
    if not setup_environment():
        sys.exit(1)
    
    # Install dependencies
    if not args.skip_deps:
        if not install_dependencies():
            sys.exit(1)
    
    # Run tests
    if not args.skip_tests:
        if not run_tests():
            sys.exit(1)
    
    # Deploy based on platform
    success = False
    
    if args.platform == "railway":
        success = deploy_railway()
    elif args.platform == "local":
        print("Starting local development server...")
        success, _ = run_command([
            sys.executable, "-m", "uvicorn",
            "app.main:app",
            "--reload",
            "--host", "0.0.0.0",
            "--port", "8000"
        ], "Start Local Server")
        
        if success:
            print("Local server started!")
            print("Your app is running at: http://localhost:8000")
            print("API docs: http://localhost:8000/docs")
            print("Health check: http://localhost:8000/health")
    
    if success:
        print("\nDeployment successful!")
        print("Your StartupScout application is now live!")
    else:
        print("\nDeployment failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
