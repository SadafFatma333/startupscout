"""
S3 storage utility for StartupScout data files.
This allows us to store large data files in S3 instead of bundling them in the Docker image.
"""

import os
import json
import boto3
from typing import Dict, Any, Optional
from pathlib import Path
import tempfile

class S3Storage:
    def __init__(self):
        self.bucket_name = os.getenv('S3_BUCKET_NAME', 'startupscout-data')
        self.region = os.getenv('AWS_REGION', 'us-west-2')
        
        # Initialize S3 client
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=self.region
        )
    
    def upload_file(self, local_path: str, s3_key: str) -> bool:
        """Upload a file to S3."""
        try:
            self.s3_client.upload_file(local_path, self.bucket_name, s3_key)
            return True
        except Exception as e:
            print(f"Error uploading {local_path} to S3: {e}")
            return False
    
    def download_file(self, s3_key: str, local_path: str) -> bool:
        """Download a file from S3."""
        try:
            self.s3_client.download_file(self.bucket_name, s3_key, local_path)
            return True
        except Exception as e:
            print(f"Error downloading {s3_key} from S3: {e}")
            return False
    
    def file_exists(self, s3_key: str) -> bool:
        """Check if a file exists in S3."""
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except:
            return False
    
    def get_data_file(self, filename: str, local_cache_dir: str = "/tmp/startupscout_data") -> Optional[str]:
        """
        Get a data file from S3, downloading it if not already cached locally.
        Returns the local path to the file.
        """
        # Create cache directory
        os.makedirs(local_cache_dir, exist_ok=True)
        
        local_path = os.path.join(local_cache_dir, filename)
        s3_key = f"data/{filename}"
        
        # If file doesn't exist locally, download from S3
        if not os.path.exists(local_path):
            if self.file_exists(s3_key):
                if self.download_file(s3_key, local_path):
                    print(f"Downloaded {filename} from S3 to {local_path}")
                else:
                    return None
            else:
                print(f"File {filename} not found in S3")
                return None
        
        return local_path
    
    def upload_data_files(self, data_dir: str = "data"):
        """Upload all data files from local data directory to S3."""
        data_path = Path(data_dir)
        
        if not data_path.exists():
            print(f"Data directory {data_dir} does not exist")
            return
        
        uploaded_count = 0
        for file_path in data_path.rglob("*"):
            if file_path.is_file():
                # Create S3 key with relative path
                relative_path = file_path.relative_to(data_path)
                s3_key = f"data/{relative_path}"
                
                if self.upload_file(str(file_path), s3_key):
                    uploaded_count += 1
                    print(f"Uploaded {relative_path} to S3")
        
        print(f"Uploaded {uploaded_count} files to S3")

# Global instance
s3_storage = S3Storage()

def get_data_file(filename: str) -> Optional[str]:
    """Convenience function to get a data file from S3."""
    return s3_storage.get_data_file(filename)

def upload_data_files():
    """Convenience function to upload data files to S3."""
    s3_storage.upload_data_files()
