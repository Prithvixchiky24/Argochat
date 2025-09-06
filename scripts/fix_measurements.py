#!/usr/bin/env python3
"""
Quick script to check and fix the measurements storage issue
"""

from src.database.database_manager import DatabaseManager
from sqlalchemy import text
import logging
import pandas as pd

logging.basicConfig(level=logging.INFO)

def main():
    """Check measurements and fix if needed."""
    
    db = DatabaseManager()
    
    # First check what's in the database
    print("Checking database contents...")
    
    # Try to run a raw SQL query to check measurements
    session = db.get_session()
    try:
        # Check if measurements table has data
        result = session.execute(text("SELECT COUNT(*) FROM argo_measurements"))
        measurement_count = result.scalar()
        print(f"Measurements in database: {measurement_count}")
        
        # Check profiles
        result = session.execute(text("SELECT COUNT(*) FROM argo_profiles"))
        profile_count = result.scalar()
        print(f"Profiles in database: {profile_count}")
        
        if measurement_count == 0 and profile_count > 0:
            print("❌ Issue confirmed: Profiles exist but no measurements!")
            print("This suggests the measurements weren't properly committed.")
            
            # Get a sample profile to test measurement storage
            result = session.execute(text("SELECT * FROM argo_profiles LIMIT 1"))
            profile = result.fetchone()
            
            if profile:
                print(f"Sample profile: {profile.float_id}-{profile.cycle_number}")
                print(f"Profile ID: {profile.id}")
                
                # Let's create some test measurements for this profile
                test_measurements = []
                for i in range(5):  # Just 5 test measurements
                    test_measurements.append({
                        'profile_id': str(profile.id),
                        'float_id': profile.float_id,
                        'cycle_number': profile.cycle_number,
                        'pressure': float(i * 10),
                        'depth': float(i * 10 + 5),
                        'temperature': 25.0 + i * 0.5,
                        'salinity': 35.0 + i * 0.1,
                        'oxygen': 200.0 - i * 5
                    })
                
                print(f"Attempting to store {len(test_measurements)} test measurements...")
                measurement_ids = db.store_measurements(test_measurements)
                print(f"✅ Successfully stored {len(measurement_ids)} test measurements")
                
                # Verify they were stored
                result = session.execute(text("SELECT COUNT(*) FROM argo_measurements"))
                new_count = result.scalar()
                print(f"New measurement count: {new_count}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    main()
