#!/usr/bin/env python3
"""
Test runner script for StartupScout.
Run different types of tests with appropriate configurations.
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n{description}")
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Success!")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed with exit code {e.returncode}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False


def run_unit_tests():
    """Run unit tests."""
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/test_auth.py",
        "tests/test_rag_pipeline.py",
        "-v", "--tb=short"
    ]
    return run_command(cmd, "Running Unit Tests")


def run_integration_tests():
    """Run integration tests."""
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/test_api_endpoints.py",
        "-v", "--tb=short", "-m", "integration"
    ]
    return run_command(cmd, "Running Integration Tests")


def run_e2e_tests():
    """Run end-to-end tests."""
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/test_e2e.py",
        "-v", "--tb=short", "-m", "e2e"
    ]
    return run_command(cmd, "Running End-to-End Tests")


def run_all_tests():
    """Run all tests."""
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-v", "--tb=short"
    ]
    return run_command(cmd, "Running All Tests")


def run_fast_tests():
    """Run fast tests (excluding slow tests)."""
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-v", "--tb=short", "-m", "not slow"
    ]
    return run_command(cmd, "Running Fast Tests")


def run_with_coverage():
    """Run tests with coverage report."""
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "--cov=app",
        "--cov=utils",
        "--cov-report=html",
        "--cov-report=term-missing",
        "-v"
    ]
    return run_command(cmd, "Running Tests with Coverage")


def lint_code():
    """Run code linting."""
    cmd = [
        sys.executable, "-m", "flake8",
        "app/", "utils/", "tests/",
        "--max-line-length=100",
        "--ignore=E203,W503"
    ]
    return run_command(cmd, "Running Code Linting")


def format_code():
    """Format code."""
    cmd = [
        sys.executable, "-m", "black",
        "app/", "utils/", "tests/",
        "--line-length=100"
    ]
    return run_command(cmd, "Formatting Code")


def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(description="StartupScout Test Runner")
    parser.add_argument(
        "--type",
        choices=["unit", "integration", "e2e", "all", "fast"],
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Run tests with coverage report"
    )
    parser.add_argument(
        "--lint",
        action="store_true",
        help="Run code linting"
    )
    parser.add_argument(
        "--format",
        action="store_true",
        help="Format code"
    )
    parser.add_argument(
        "--install-deps",
        action="store_true",
        help="Install test dependencies"
    )
    
    args = parser.parse_args()
    
    # Install dependencies if requested
    if args.install_deps:
        print("Installing test dependencies...")
        install_cmd = [
            sys.executable, "-m", "pip", "install",
            "pytest", "pytest-cov", "pytest-mock", "httpx",
            "flake8", "black", "mypy"
        ]
        if not run_command(install_cmd, "Installing Dependencies"):
            sys.exit(1)
    
    # Format code if requested
    if args.format:
        if not format_code():
            sys.exit(1)
    
    # Lint code if requested
    if args.lint:
        if not lint_code():
            sys.exit(1)
    
    # Run tests
    success = True
    
    if args.coverage:
        success = run_with_coverage()
    else:
        if args.type == "unit":
            success = run_unit_tests()
        elif args.type == "integration":
            success = run_integration_tests()
        elif args.type == "e2e":
            success = run_e2e_tests()
        elif args.type == "fast":
            success = run_fast_tests()
        elif args.type == "all":
            success = run_all_tests()
    
    if success:
        print("\nAll tests passed!")
        sys.exit(0)
    else:
        print("\nSome tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
