#!/usr/bin/env python3
"""
Force Cursor to save its current content by reading from the file
and writing it back, which should trigger a sync.
"""
import json
import os
import shutil
from datetime import datetime

def force_cursor_save():
    file_path = 'data/startup_data.json'
    
    print(f"Current file size: {os.path.getsize(file_path)} bytes")
    
    # Read the current content
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"Content length: {len(content)} characters")
    
    # Try to parse as JSON
    try:
        data = json.loads(content)
        print(f"JSON parsed successfully: {len(data)} entries")
        print(f"First ID: {data[0]['id']}")
        print(f"Last ID: {data[-1]['id']}")
        
        # If we only have 10 entries, the file is not synced
        if len(data) == 10:
            print("\nFile only has 10 entries - Cursor sync issue detected!")
            print("This means Cursor is showing you unsaved changes.")
            print("\nTo fix this:")
            print("1. In Cursor, press Cmd+S to save the file")
            print("2. Or close and reopen the file")
            print("3. Or restart Cursor")
            return False
        else:
            print(f"File has {len(data)} entries - sync is working!")
            return True
            
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        return False

if __name__ == "__main__":
    force_cursor_save()

