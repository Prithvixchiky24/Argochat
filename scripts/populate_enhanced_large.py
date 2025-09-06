"""
Enhanced script to populate the database with large-scale ARGO data.
This version creates 1500 profiles with ~500 measurements per profile.
"""
import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from sqlalchemy.exc import IntegrityError
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import sessionmaker
import uuid

# Add the project root to sys.path so 'src' can be imported
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from src.config import Config
from src.database.database_manager import DatabaseManager
from src.database.models import ARGOFloat
from src.ai.vector_store import ARGOVectorStore
from src.ingestion.argo_ingestion import ARGODataIngestion

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_large_scale_oceanographic_data():
    """Create large-scale oceanographic data: 1500 profiles with comprehensive measurements."""
    
    # Define 10 floats for better distribution
    sample_floats = []
    float_institutions = ['INCOIS', 'CSIR-NIO', 'NIOT', 'IITM', 'SAC']
    
    for i in range(10):
        float_id = f'290{2116 + i}'
        # Stagger deployment dates across different months/years
        deployment_month = ((i * 2) % 12) + 1  # Months 1-12
        deployment_year = 2022 + (i // 6)  # 2022-2023
        sample_floats.append({
            'id': str(uuid.uuid4()),
            'float_id': float_id,
            'wmo_id': float_id,
            'institution': float_institutions[i % len(float_institutions)],
            'data_mode': 'R',
            'deployment_date': datetime(deployment_year, deployment_month, 15),
            'last_transmission': datetime(2025, 9, 1),
            'status': 'active',
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        })

    sample_profiles = []
    sample_measurements = []
    sample_trajectories = []

    # Define expanded deployment regions across Indian Ocean
    regions = [
        {'lat_center': 15.0, 'lon_center': 68.0, 'lat_range': 8.0, 'lon_range': 12.0},  # Arabian Sea
        {'lat_center': 10.0, 'lon_center': 77.0, 'lat_range': 6.0, 'lon_range': 10.0},  # South India
        {'lat_center': 5.0, 'lon_center': 85.0, 'lat_range': 8.0, 'lon_range': 12.0},   # Bay of Bengal
        {'lat_center': -5.0, 'lon_center': 75.0, 'lat_range': 10.0, 'lon_range': 15.0}, # Central Indian Ocean
        {'lat_center': 8.0, 'lon_center': 88.0, 'lat_range': 6.0, 'lon_range': 10.0},   # Eastern Bay of Bengal
        {'lat_center': 12.0, 'lon_center': 80.0, 'lat_range': 5.0, 'lon_range': 8.0},   # Tamil Nadu coast
        {'lat_center': -10.0, 'lon_center': 70.0, 'lat_range': 8.0, 'lon_range': 12.0}, # Southern Indian Ocean
        {'lat_center': 20.0, 'lon_center': 65.0, 'lat_range': 5.0, 'lon_range': 8.0},   # Northern Arabian Sea
        {'lat_center': 0.0, 'lon_center': 80.0, 'lat_range': 6.0, 'lon_range': 10.0},   # Equatorial Indian Ocean
        {'lat_center': 15.0, 'lon_center': 90.0, 'lat_range': 4.0, 'lon_range': 8.0},   # Eastern Bay
    ]

    profile_id = 0
    
    # Create 1500 profiles (150 per float)
    for i, float_data in enumerate(sample_floats):
        float_id = float_data['float_id']
        region = regions[i]
        
        # Create 150 profiles per float (1500 total profiles)
        for cycle in range(1, 151):
            profile_id += 1
            
            # Realistic drift pattern over extended time
            days_since_deployment = cycle * 10  # Cycle every 10 days
            
            # Enhanced random walk with seasonal and geographical constraints
            seasonal_offset = np.sin(2 * np.pi * days_since_deployment / 365.0) * 3.0
            geographical_drift = np.sin(2 * np.pi * days_since_deployment / (365.0 * 2)) * 2.0
            
            lat = region['lat_center'] + np.random.normal(0, region['lat_range']/4) + seasonal_offset
            lon = region['lon_center'] + np.random.normal(0, region['lon_range']/4) + geographical_drift
            
            # Keep within reasonable bounds
            lat = np.clip(lat, -30, 30)
            lon = np.clip(lon, 50, 100)
            
            profile_time = float_data['deployment_date'] + timedelta(days=days_since_deployment)
            
            # Variable depth ranges based on location and season
            if lat > 10:  # Northern regions - variable depth
                max_depth_base = np.random.uniform(1000, 2200)
            elif lat > 0:  # Equatorial - deep
                max_depth_base = np.random.uniform(1500, 2500)  
            else:  # Southern - very deep
                max_depth_base = np.random.uniform(1800, 3000)
                
            max_depth = float(max_depth_base + np.random.normal(0, 300))
            min_depth = float(np.random.uniform(1, 10))
            
            # More measurements per profile (target ~500)
            num_levels = int(np.random.uniform(480, 520))  # 480-520 measurements per profile

            profile = {
                'id': str(uuid.uuid4()),
                'float_id': float_id,
                'cycle_number': cycle,
                'latitude': float(lat),
                'longitude': float(lon),
                'profile_time': profile_time,
                'max_depth': max_depth,
                'min_depth': min_depth,
                'num_levels': num_levels,
                'data_mode': 'R'
            }
            sample_profiles.append(profile)

            # Create trajectory point
            trajectory = {
                'float_id': float_id,
                'latitude': float(lat),
                'longitude': float(lon),
                'trajectory_time': profile_time,
                'cycle_number': cycle,
                'data_mode': 'R'
            }
            sample_trajectories.append(trajectory)

            # Create comprehensive measurements for each profile
            depths = np.logspace(np.log10(min_depth), np.log10(max_depth), num_levels)  # Log spacing for better resolution near surface
            
            for j, depth in enumerate(depths):
                pressure = float(depth * 1.02 + np.random.normal(0, 0.8))
                
                # More sophisticated temperature profile with regional variations
                if region['lat_center'] > 15:  # Arabian Sea - warmer surface
                    surface_temp = 29.0 + np.sin(2 * np.pi * days_since_deployment / 365.0) * 3.0
                elif region['lat_center'] < 0:  # Southern Ocean - cooler
                    surface_temp = 25.0 + np.sin(2 * np.pi * days_since_deployment / 365.0) * 2.0
                else:  # Tropical - warm and stable
                    surface_temp = 28.0 + np.sin(2 * np.pi * days_since_deployment / 365.0) * 2.5
                
                # Complex temperature structure
                if depth < 50:  # Mixed layer
                    temp_base = surface_temp - depth * 0.02
                elif depth < 200:  # Thermocline
                    temp_base = surface_temp - 50 * 0.02 - (depth - 50) * 0.08
                elif depth < 1000:  # Deep thermocline
                    temp_base = surface_temp - 50 * 0.02 - 150 * 0.08 - (depth - 200) * 0.008
                else:  # Abyssal
                    temp_base = 2.5 - (depth - 1000) * 0.0005
                
                temperature = float(temp_base + np.random.normal(0, 0.2))
                
                # Enhanced salinity profile with regional characteristics
                if region['lon_center'] > 85:  # Bay of Bengal - fresher surface due to rivers
                    surface_salinity = 33.8
                elif region['lat_center'] > 15:  # Arabian Sea - saltier due to evaporation
                    surface_salinity = 36.2
                else:  # Open ocean
                    surface_salinity = 35.0
                
                if depth < 100:
                    salinity_base = surface_salinity + np.random.normal(0, 0.3)
                elif depth < 500:
                    salinity_base = 35.0 + depth * 0.0008
                else:
                    salinity_base = 34.7 + np.random.normal(0, 0.1)
                
                salinity = float(salinity_base)
                
                # Sophisticated oxygen profile with oxygen minimum zone
                if depth < 80:
                    oxygen_base = 230.0 - depth * 0.8
                elif depth < 200:  # Near-surface decline
                    oxygen_base = 200.0 - (depth - 80) * 1.2
                elif depth < 800:  # Oxygen minimum zone
                    oxygen_base = 60.0 + np.sin((depth - 200) * 0.01) * 30.0
                elif depth < 1500:  # Deep water recovery
                    oxygen_base = 120.0 + (depth - 800) * 0.03
                else:  # Abyssal
                    oxygen_base = 140.0 + np.random.normal(0, 10)
                
                oxygen = float(max(5, oxygen_base + np.random.normal(0, 12)))
                
                # Realistic biogeochemical parameters with depth and seasonal variations
                seasonal_factor = 1.0 + 0.5 * np.sin(2 * np.pi * days_since_deployment / 365.0)
                
                if depth < 150:  # Euphotic zone
                    chlorophyll = float(max(0, (1.2 - depth * 0.006) * seasonal_factor + np.random.normal(0, 0.15)))
                    nitrate = float(max(0, 1.0 + depth * 0.02 + np.random.normal(0, 0.8)))
                else:  # Below euphotic zone
                    chlorophyll = float(max(0, 0.03 + np.random.normal(0, 0.01)))
                    nitrate = float(18.0 + depth * 0.003 + np.random.normal(0, 3.0))
                
                # pH with carbonate chemistry effects
                ph = float(8.15 - depth * 0.0002 - np.log10(depth/100) * 0.02 + np.random.normal(0, 0.04))
                
                # Backscatter with particle layers
                if depth < 100:
                    backscatter = float(max(0, 0.002 + np.random.exponential(0.001)))
                elif 400 < depth < 600:  # Deep scattering layer
                    backscatter = float(max(0, 0.0015 + np.random.exponential(0.0008)))
                else:
                    backscatter = float(max(0, 0.0005 + np.random.exponential(0.0003)))

                measurement = {
                    'profile_id': profile['id'],
                    'float_id': float_id,
                    'cycle_number': cycle,
                    'pressure': pressure,
                    'depth': float(depth),
                    'temperature': temperature,
                    'salinity': salinity,
                    'oxygen': oxygen,
                    'chlorophyll': chlorophyll,
                    'backscatter': backscatter,
                    'nitrate': nitrate,
                    'ph': ph,
                    'temperature_qc': int(np.random.choice([1, 2], p=[0.96, 0.04])),
                    'salinity_qc': int(np.random.choice([1, 2], p=[0.94, 0.06])),
                    'oxygen_qc': int(np.random.choice([1, 2, 3], p=[0.91, 0.07, 0.02])),
                    'chlorophyll_qc': int(np.random.choice([1, 2, 3], p=[0.86, 0.11, 0.03])),
                    'nitrate_qc': int(np.random.choice([1, 2, 3], p=[0.89, 0.09, 0.02])),
                    'ph_qc': int(np.random.choice([1, 2], p=[0.93, 0.07]))
                }
                sample_measurements.append(measurement)
            
            # Progress reporting
            if profile_id % 100 == 0:
                logger.info(f"Generated {profile_id} profiles with {len(sample_measurements)} measurements so far...")

    logger.info(f"Generated {len(sample_floats)} floats, {len(sample_profiles)} profiles, {len(sample_measurements)} measurements")
    return sample_floats, sample_profiles, sample_measurements, sample_trajectories


def populate_large_scale_database():
    """Populate the database with large-scale realistic data."""
    try:
        db_manager = DatabaseManager()
        vector_store = ARGOVectorStore()

        logger.info("Creating database tables...")
        db_manager.create_tables()

        logger.info("Generating large-scale realistic data (this may take several minutes)...")
        floats, profiles, measurements, trajectories = create_large_scale_oceanographic_data()

        # Store float metadata with conflict resolution
        Session = sessionmaker(bind=db_manager.engine)
        session = Session()

        logger.info("Storing float metadata...")
        try:
            for float_data in floats:
                try:
                    stmt = insert(ARGOFloat).values(float_data).on_conflict_do_update(
                        index_elements=['float_id'],
                        set_={
                            'wmo_id': float_data['wmo_id'],
                            'institution': float_data['institution'],
                            'data_mode': float_data['data_mode'],
                            'deployment_date': float_data['deployment_date'],
                            'last_transmission': float_data['last_transmission'],
                            'status': float_data['status'],
                            'updated_at': float_data['updated_at']
                        }
                    )
                    session.execute(stmt)
                    logger.info(f"Inserted or updated float {float_data['float_id']}")
                except IntegrityError as e:
                    session.rollback()
                    logger.error(f"Error storing float {float_data['float_id']}: {e}")
                    continue
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error during float metadata storage: {e}")
            raise
        finally:
            session.close()

        # Store profiles
        logger.info("Storing profile data...")
        profile_ids = {}
        for i, profile in enumerate(profiles):
            try:
                profile_id = db_manager.store_profile_data(profile)
                profile_ids[f"{profile['float_id']}_{profile['cycle_number']}"] = profile_id
                if (i + 1) % 100 == 0:
                    logger.info(f"Stored {i + 1} profiles...")
            except Exception as e:
                logger.error(f"Error storing profile {profile['float_id']}-{profile['cycle_number']}: {e}")

        # Store measurements in larger batches for efficiency
        logger.info("Storing measurements (this will take a while)...")
        measurement_batch = []
        batch_size = 1000  # Larger batch size for efficiency
        total_stored = 0
        
        for i, measurement in enumerate(measurements):
            # Find the correct profile_id
            key = f"{measurement['float_id']}_{measurement['cycle_number']}"
            if key in profile_ids:
                measurement['profile_id'] = profile_ids[key]
                measurement_batch.append(measurement)
                
                if len(measurement_batch) >= batch_size:
                    try:
                        db_manager.store_measurements(measurement_batch)
                        total_stored += len(measurement_batch)
                        logger.info(f"Stored {total_stored}/{len(measurements)} measurements ({(total_stored/len(measurements)*100):.1f}%)")
                        measurement_batch = []
                    except Exception as e:
                        logger.error(f"Error storing measurement batch: {e}")
                        measurement_batch = []
        
        # Store remaining measurements
        if measurement_batch:
            try:
                db_manager.store_measurements(measurement_batch)
                total_stored += len(measurement_batch)
                logger.info(f"Stored final batch - Total: {total_stored} measurements")
            except Exception as e:
                logger.error(f"Error storing final measurement batch: {e}")

        # Store trajectory data
        logger.info("Storing trajectory data...")
        try:
            db_manager.store_trajectory_data(trajectories)
            logger.info("Trajectory data stored successfully")
        except Exception as e:
            logger.error(f"Error storing trajectory data: {e}")

        # Create vector store documents (sample subset to avoid memory issues)
        logger.info("Creating vector store documents...")
        # Use every 10th profile for vector store to manage memory
        sample_profiles = profiles[::10]  
        profile_docs = []
        
        for profile in sample_profiles:
            float_data = next(f for f in floats if f['float_id'] == profile['float_id'])
            
            profile_doc = {
                'float_id': profile['float_id'],
                'cycle_number': profile['cycle_number'],
                'latitude': float(profile['latitude']),
                'longitude': float(profile['longitude']),
                'profile_time': profile['profile_time'],
                'max_depth': float(profile['max_depth']),
                'num_levels': int(profile['num_levels']),
                'parameters': ['temperature', 'salinity', 'oxygen', 'chlorophyll', 'nitrate', 'ph'],
                'institution': float_data['institution']
            }
            profile_docs.append(profile_doc)

        vector_store.add_profile_documents(profile_docs)

        # Create float documents
        float_docs = []
        for float_data in floats:
            profile_count = len([p for p in profiles if p['float_id'] == float_data['float_id']])
            latest_profile = max([p for p in profiles if p['float_id'] == float_data['float_id']], 
                               key=lambda x: x['profile_time'], default=None)
            
            float_doc = {
                'float_id': float_data['float_id'],
                'wmo_id': float_data['wmo_id'],
                'institution': float_data['institution'],
                'status': float_data['status'],
                'deployment_date': float_data['deployment_date'],
                'last_transmission': float_data['last_transmission'],
                'total_profiles': profile_count,
                'latitude': float(latest_profile['latitude']) if latest_profile else 0,
                'longitude': float(latest_profile['longitude']) if latest_profile else 0
            }
            float_docs.append(float_doc)

        vector_store.add_float_documents(float_docs)

        logger.info("Large-scale database population completed successfully!")

        # Display summary
        summary = db_manager.get_data_summary()
        print(f"\n🌊 LARGE-SCALE DATABASE SUMMARY:")
        print(f"✅ Total Floats: {summary.get('total_floats', 0)}")
        print(f"✅ Total Profiles: {summary.get('total_profiles', 0)}")
        print(f"✅ Total Measurements: {summary.get('total_measurements', 0):,}")
        print(f"✅ Average Measurements per Profile: {summary.get('total_measurements', 0) / max(1, summary.get('total_profiles', 1)):.0f}")

        vector_stats = vector_store.get_collection_stats()
        print(f"\n🔍 VECTOR STORE SUMMARY:")
        print(f"✅ Profile Documents: {vector_stats.get('profiles', {}).get('count', 0)}")
        print(f"✅ Float Documents: {vector_stats.get('floats', {}).get('count', 0)}")

    except Exception as e:
        logger.error(f"Error populating large-scale database: {e}")
        raise

if __name__ == "__main__":
    populate_large_scale_database()
