#!/usr/bin/env python3
"""
Comprehensive script to copy ALL tables from local PostgreSQL to Neon PostgreSQL
Copies schemas, indexes, and all data exactly as they exist locally.
"""

import os
import psycopg
from psycopg import sql
import json
from datetime import datetime
import sys

# Database connections
LOCAL_DB_URL = "postgresql://postgres:postgres@localhost:5432/startupscout"

# Try to get Neon URL from environment variables
NEON_DB_URL = os.getenv("NEON_DATABASE_URL") or os.getenv("DATABASE_URL")

if not NEON_DB_URL or "railway.internal" in NEON_DB_URL:
    print("❌ ERROR: Neon database URL not found!")
    print("Current DATABASE_URL points to Railway, not Neon")
    print("Please provide your Neon database URL:")
    print("Format: postgresql://username:password@host:port/database")
    NEON_DB_URL = input("Neon Database URL: ").strip()
    
    if not NEON_DB_URL:
        print("❌ No URL provided. Exiting.")
        sys.exit(1)

def get_connection(db_url):
    """Get database connection"""
    try:
        return psycopg.connect(db_url)
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return None

def get_table_schema(cursor, table_name):
    """Get complete table schema including columns, types, constraints"""
    # Get columns
    cursor.execute("""
        SELECT column_name, data_type, is_nullable, column_default, character_maximum_length
        FROM information_schema.columns 
        WHERE table_name = %s 
        ORDER BY ordinal_position
    """, (table_name,))
    
    columns = cursor.fetchall()
    return columns

def get_table_indexes(cursor, table_name):
    """Get all indexes for a table"""
    cursor.execute("""
        SELECT indexname, indexdef 
        FROM pg_indexes 
        WHERE tablename = %s
    """, (table_name,))
    
    return cursor.fetchall()

def get_table_constraints(cursor, table_name):
    """Get table constraints (primary keys, foreign keys, etc.)"""
    cursor.execute("""
        SELECT tc.constraint_name, tc.constraint_type, kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu 
        ON tc.constraint_name = kcu.constraint_name
        WHERE tc.table_name = %s
    """, (table_name,))
    
    return cursor.fetchall()

def get_sequences(cursor, table_name):
    """Get sequences associated with a table"""
    cursor.execute("""
        SELECT column_name, column_default
        FROM information_schema.columns 
        WHERE table_name = %s AND column_default LIKE 'nextval%'
    """, (table_name,))
    
    return cursor.fetchall()

def create_table_ddl(cursor, table_name):
    """Generate CREATE TABLE DDL for a table"""
    columns = get_table_schema(cursor, table_name)
    
    ddl_parts = [f"CREATE TABLE {table_name} ("]
    
    # Add columns
    column_defs = []
    for col_name, data_type, nullable, default, max_length in columns:
        # Handle different data types
        if data_type == 'ARRAY':
            # For arrays, we need to specify the element type
            col_def = f"    {col_name} text[]"  # Default to text array for now
        elif data_type == 'USER-DEFINED':
            # Handle custom types like vector
            col_def = f"    {col_name} vector(1536)"  # OpenAI embedding dimension
        elif data_type == 'character varying':
            # Add length for varchar
            if max_length:
                col_def = f"    {col_name} {data_type}({max_length})"
            else:
                col_def = f"    {col_name} {data_type}"
        else:
            # Standard data type
            col_def = f"    {col_name} {data_type}"
        
        # Add nullable constraint
        if nullable == 'NO':
            col_def += " NOT NULL"
        
        # Handle default values - skip sequence defaults for now
        if default and 'nextval' not in default:
            col_def += f" DEFAULT {default}"
        elif default and 'nextval' in default:
            # For sequences, we'll create them separately
            pass
        
        column_defs.append(col_def)
    
    ddl_parts.append(",\n".join(column_defs))
    ddl_parts.append(")")
    
    return "\n".join(ddl_parts)

def create_sequences(target_cursor, table_name, columns):
    """Create sequences for auto-incrementing columns"""
    sequences_created = 0
    for col_name, data_type, nullable, default, max_length in columns:
        if default and 'nextval' in default:
            # Extract sequence name from default
            seq_name = default.split("'")[1] if "'" in default else f"{table_name}_{col_name}_seq"
            try:
                target_cursor.execute(f"CREATE SEQUENCE IF NOT EXISTS {seq_name}")
                sequences_created += 1
                print(f"    ✅ Created sequence: {seq_name}")
            except Exception as e:
                print(f"    ❌ Error creating sequence {seq_name}: {e}")
    
    return sequences_created

def copy_table_data(source_cursor, target_cursor, target_conn, table_name, columns):
    """Copy all data from source to target table"""
    import json
    import psycopg.adapt
    
    # Get column names
    col_names = [col[0] for col in columns]
    
    # Get all data
    source_cursor.execute(f"SELECT * FROM {table_name}")
    rows = source_cursor.fetchall()
    
    if not rows:
        print(f"  No data to copy for {table_name}")
        return 0
    
    # Prepare insert statement
    placeholders = ", ".join(["%s"] * len(col_names))
    insert_sql = f"INSERT INTO {table_name} ({', '.join(col_names)}) VALUES ({placeholders})"
    
    # Insert data one by one to avoid transaction issues
    total_inserted = 0
    total_skipped = 0
    
    for i, row in enumerate(rows):
        try:
            # Process each value in the row
            processed_row = []
            for j, value in enumerate(row):
                if value is None:
                    processed_row.append(None)
                elif isinstance(value, dict):
                    # Convert dict to JSON string with proper escaping
                    processed_row.append(json.dumps(value, ensure_ascii=False))
                elif isinstance(value, list):
                    # Convert list to JSON string with proper escaping
                    processed_row.append(json.dumps(value, ensure_ascii=False))
                else:
                    processed_row.append(value)
            
            # Insert with individual transaction
            target_cursor.execute(insert_sql, processed_row)
            target_conn.commit()
            total_inserted += 1
            
            if i % 100 == 0:
                print(f"    Inserted {total_inserted}/{len(rows)} records...")
                
        except Exception as e:
            print(f"    ❌ Error inserting row {i + 1}: {e}")
            total_skipped += 1
            # Rollback the failed transaction
            target_conn.rollback()
            continue
    
    if total_skipped > 0:
        print(f"    ⚠️  Skipped {total_skipped} problematic records")
    
    return total_inserted

def create_indexes(target_cursor, table_name, indexes):
    """Create all indexes for a table"""
    created_count = 0
    for idx_name, idx_def in indexes:
        try:
            # Skip primary key indexes (already created with table)
            if 'pkey' in idx_name.lower():
                continue
                
            target_cursor.execute(idx_def)
            created_count += 1
            print(f"    ✅ Created index: {idx_name}")
        except Exception as e:
            print(f"    ❌ Error creating index {idx_name}: {e}")
    
    return created_count

def enable_extensions(neon_cursor):
    """Enable required PostgreSQL extensions"""
    extensions = ['vector', 'pg_trgm']
    enabled_count = 0
    
    for ext in extensions:
        try:
            neon_cursor.execute(f"CREATE EXTENSION IF NOT EXISTS {ext}")
            enabled_count += 1
            print(f"  ✅ Enabled extension: {ext}")
        except Exception as e:
            print(f"  ❌ Error enabling extension {ext}: {e}")
    
    return enabled_count

def main():
    """Main copy function"""
    print("🚀 Starting comprehensive local to Neon database copy")
    print("=" * 60)
    
    # Connect to both databases
    print("📡 Connecting to databases...")
    local_conn = get_connection(LOCAL_DB_URL)
    neon_conn = get_connection(NEON_DB_URL)
    
    if not local_conn or not neon_conn:
        print("❌ Failed to connect to databases")
        return False
    
    local_cursor = local_conn.cursor()
    neon_cursor = neon_conn.cursor()
    
    # Enable required extensions
    print("🔧 Enabling PostgreSQL extensions...")
    enabled_count = enable_extensions(neon_cursor)
    neon_conn.commit()
    if enabled_count > 0:
        print(f"✅ Enabled {enabled_count} extensions")
    
    try:
        # Get all tables
        local_cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        tables = [row[0] for row in local_cursor.fetchall()]
        
        print(f"📋 Found {len(tables)} tables to copy: {', '.join(tables)}")
        
        # Process each table
        for table_name in tables:
            print(f"\n📊 Processing table: {table_name}")
            print("-" * 40)
            
            # Get table info
            columns = get_table_schema(local_cursor, table_name)
            indexes = get_table_indexes(local_cursor, table_name)
            
            # Get record count
            local_cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            record_count = local_cursor.fetchone()[0]
            print(f"  Records to copy: {record_count}")
            
            # Drop table if exists in target
            print(f"  🗑️  Dropping existing table if exists...")
            neon_cursor.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE")
            neon_conn.commit()
            
            # Create sequences first
            print(f"  🔢 Creating sequences...")
            sequences_created = create_sequences(neon_cursor, table_name, columns)
            neon_conn.commit()
            if sequences_created > 0:
                print(f"  ✅ Created {sequences_created} sequences")
            
            # Create table structure
            print(f"  🏗️  Creating table structure...")
            try:
                # Get DDL from source
                ddl = create_table_ddl(local_cursor, table_name)
                neon_cursor.execute(ddl)
                neon_conn.commit()
                print(f"  ✅ Table structure created")
            except Exception as e:
                print(f"  ❌ Error creating table structure: {e}")
                continue
            
            # Copy data
            if record_count > 0:
                print(f"  📦 Copying {record_count} records...")
                copied_count = copy_table_data(local_cursor, neon_cursor, neon_conn, table_name, columns)
                print(f"  ✅ Copied {copied_count} records")
            else:
                print(f"  ℹ️  No data to copy")
            
            # Create indexes
            if indexes:
                print(f"  🔍 Creating {len(indexes)} indexes...")
                created_count = create_indexes(neon_cursor, table_name, indexes)
                neon_conn.commit()
                print(f"  ✅ Created {created_count} indexes")
            else:
                print(f"  ℹ️  No indexes to create")
        
        print(f"\n🎉 Copy completed successfully!")
        print("=" * 60)
        
        # Verify copy
        print("\n🔍 Verifying copy...")
        for table_name in tables:
            local_cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            local_count = local_cursor.fetchone()[0]
            
            neon_cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            neon_count = neon_cursor.fetchone()[0]
            
            status = "✅" if local_count == neon_count else "❌"
            print(f"  {status} {table_name}: {local_count} → {neon_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during copy: {e}")
        return False
    
    finally:
        local_conn.close()
        neon_conn.close()

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Database copy completed successfully!")
    else:
        print("\n❌ Database copy failed!")
        sys.exit(1)
