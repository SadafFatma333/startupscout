#!/usr/bin/env python3
"""
Simple script to copy data using pg_dump and pg_restore approach
"""

import subprocess
import os
import sys

# Database URLs
LOCAL_DB = "postgresql://postgres:postgres@localhost:5432/startupscout"
NEON_DB = "postgresql://neondb_owner:npg_wpj27akDEOKR@ep-patient-truth-adrb5kdq-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return None

def main():
    print("🚀 Starting simple data copy using pg_dump/pg_restore")
    print("=" * 60)
    
    # Step 1: Dump local database
    dump_cmd = f"docker exec pgvector pg_dump -U postgres -d startupscout --no-owner --no-privileges --clean --if-exists"
    result = run_command(dump_cmd, "Dumping local database")
    
    if not result:
        print("❌ Failed to dump local database")
        return False
    
    # Save dump to file
    with open("local_backup.sql", "w") as f:
        f.write(result.stdout)
    print("✅ Dump saved to local_backup.sql")
    
    # Step 2: Restore to Neon
    restore_cmd = f"psql '{NEON_DB}' -f local_backup.sql"
    result = run_command(restore_cmd, "Restoring to Neon database")
    
    if not result:
        print("❌ Failed to restore to Neon database")
        return False
    
    print("🎉 Data copy completed successfully!")
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
