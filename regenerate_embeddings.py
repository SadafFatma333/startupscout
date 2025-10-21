#!/usr/bin/env python3
"""
Script to regenerate embeddings in production database using OpenAI
This fixes the dimension mismatch between local (minilm) and production (openai) embeddings
"""

import os
import sys
from dotenv import load_dotenv
from config.settings import DB_CONFIG, EMBEDDING_BACKEND, OPENAI_API_KEY
from utils.embeddings import get_embedding
from utils.logger import setup_logger
from psycopg import connect

logger = setup_logger("regenerate_embeddings")

def regenerate_embeddings():
    """Regenerate all embeddings in the database using the current embedding backend"""
    
    # Ensure we're using OpenAI for production
    if EMBEDDING_BACKEND != "openai":
        logger.error(f"Expected EMBEDDING_BACKEND=openai, got {EMBEDDING_BACKEND}")
        return False
    
    if not OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY not set")
        return False
    
    logger.info(f"Regenerating embeddings using {EMBEDDING_BACKEND} backend")
    
    # Connect to database
    conn = connect(**DB_CONFIG)
    cur = conn.cursor()
    
    try:
        # Get all records that need embedding regeneration
        cur.execute("""
            SELECT id, title, decision, summary, content, comments, tags, stage, source, url
            FROM decisions
            WHERE embedding IS NOT NULL OR embedding IS NULL
            ORDER BY id
        """)
        
        records = cur.fetchall()
        total = len(records)
        logger.info(f"Found {total} records to process")
        
        if total == 0:
            logger.info("No records found to process")
            return True
        
        # Process each record
        success_count = 0
        error_count = 0
        
        for i, (id_val, title, decision, summary, content, comments, tags, stage, source, url) in enumerate(records):
            try:
                # Create text for embedding
                text_parts = []
                if title:
                    text_parts.append(title)
                if decision:
                    text_parts.append(decision)
                if summary:
                    text_parts.append(summary)
                if content:
                    text_parts.append(content)
                
                text = " ".join(text_parts)
                
                if not text.strip():
                    logger.warning(f"Record {id_val} has no text content, skipping")
                    continue
                
                # Generate embedding
                logger.info(f"Processing record {id_val} ({i+1}/{total}): {title[:50]}...")
                embedding, model = get_embedding(text)
                
                if not embedding:
                    logger.warning(f"Failed to generate embedding for record {id_val}")
                    error_count += 1
                    continue
                
                # Update the database
                cur.execute("""
                    UPDATE decisions 
                    SET embedding = %s, embedding_model = %s, embedding_updated_at = NOW()
                    WHERE id = %s
                """, (embedding, model, id_val))
                
                success_count += 1
                
                # Commit every 10 records to avoid long transactions
                if (i + 1) % 10 == 0:
                    conn.commit()
                    logger.info(f"Committed {i+1}/{total} records")
                
            except Exception as e:
                logger.error(f"Error processing record {id_val}: {e}")
                error_count += 1
                continue
        
        # Final commit
        conn.commit()
        
        logger.info(f"Embedding regeneration complete!")
        logger.info(f"Successfully processed: {success_count}")
        logger.info(f"Errors: {error_count}")
        logger.info(f"Total records: {total}")
        
        return error_count == 0
        
    except Exception as e:
        logger.error(f"Database error: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    # Load environment
    load_dotenv()
    
    logger.info("Starting embedding regeneration...")
    logger.info(f"Environment: {os.getenv('ENV', 'dev')}")
    logger.info(f"Embedding backend: {EMBEDDING_BACKEND}")
    logger.info(f"Database: {DB_CONFIG.get('host', 'unknown')}")
    
    success = regenerate_embeddings()
    
    if success:
        logger.info("✅ Embedding regeneration completed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Embedding regeneration failed!")
        sys.exit(1)
