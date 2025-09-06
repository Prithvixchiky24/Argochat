#!/usr/bin/env python3
"""
Script to recreate the database with updated schema to match your NetCDF variables.
"""

import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

from src.config import Config
from src.database.database_manager import DatabaseManager
from src.database.models import Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def recreate_database():
    """Drop and recreate all tables with new schema."""
    
    print("🔄 Recreating database with updated schema for your NetCDF variables...")
    
    try:
        # Initialize database manager
        db_manager = DatabaseManager()
        
        # Drop all existing tables
        print("Dropping existing tables...")
        Base.metadata.drop_all(bind=db_manager.engine)
        logger.info("Dropped all existing tables")
        
        # Create tables with new schema
        print("Creating tables with new schema...")
        Base.metadata.create_all(bind=db_manager.engine)
        logger.info("Created all tables with new schema")
        
        print("✅ Database successfully recreated!")
        print("\nNew schema includes:")
        print("  ✅ PLATFORM_NUMBER in profiles")
        print("  ✅ All QC flags (PRES_QC, TEMP_QC, PSAL_QC, etc.)")
        print("  ✅ Adjusted variables (PRES_ADJUSTED, TEMP_ADJUSTED, PSAL_ADJUSTED)")
        print("  ✅ Error estimates (PRES_ADJUSTED_ERROR, etc.)")
        print("\nYou can now run: python scripts/populate_from_your_netcdf.py")
        
    except Exception as e:
        print(f"❌ Error recreating database: {e}")
        logger.error(f"Error recreating database: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = recreate_database()
    exit(0 if success else 1)
