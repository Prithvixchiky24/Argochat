"""
Enhanced script to populate the database with comprehensive ARGO data.
This version creates more realistic oceanographic data with proper measurements.
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

def create_realistic_oceanographic_data():
    """Create realistic oceanographic data for demonstration."""
    
    # Define 6 floats with more realistic deployment patterns
    sample_floats = [
        {
            'id': str(uuid.uuid4()),
            'float_id': '2902116',
            'wmo_id': '2902116',
            'institution': 'INCOIS',
            'data_mode': 'R',
            'deployment_date': datetime(2023, 1, 15),
            'last_transmission': datetime(2025, 9, 1),
            'status': 'active',
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        },
        {
            'id': str(uuid.uuid4()),
            'float_id': '2902117',
            'wmo_id': '2902117',
            'institution': 'INCOIS',
            'data_mode': 'R',
            'deployment_date': datetime(2023, 2, 20),
            'last_transmission': datetime(2025, 8, 28),
            'status': 'active',
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        },
        {
            'id': str(uuid.uuid4()),
            'float_id': '2902118',
            'wmo_id': '2902118',
            'institution': 'CSIR-NIO',
            'data_mode': 'R',
            'deployment_date': datetime(2023, 3, 10),
            'last_transmission': datetime(2025, 8, 25),
            'status': 'active',
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        },
        {
            'id': str(uuid.uuid4()),
            'float_id': '2902119',
            'wmo_id': '2902119',
            'institution': 'CSIR-NIO',
            'data_mode': 'R',
            'deployment_date': datetime(2023, 4, 5),
            'last_transmission': datetime(2025, 8, 30),
            'status': 'active',
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        },
        {
            'id': str(uuid.uuid4()),
            'float_id': '2902120',
            'wmo_id': '2902120',
            'institution': 'INCOIS',
            'data_mode': 'R',
            'deployment_date': datetime(2023, 5, 12),
            'last_transmission': datetime(2025, 9, 2),
            'status': 'active',
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        },
        {
            'id': str(uuid.uuid4()),
            'float_id': '2902121',
            'wmo_id': '2902121',
            'institution': 'NIOT',
            'data_mode': 'R',
            'deployment_date': datetime(2023, 6, 1),
            'last_transmission': datetime(2025, 8, 29),
            'status': 'active',
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
    ]

    sample_profiles = []
    sample_measurements = []
    sample_trajectories = []

    # Define realistic deployment regions in Indian Ocean
    regions = {
        '2902116': {'lat_center': 15.0, 'lon_center': 68.0, 'lat_range': 5.0, 'lon_range': 8.0},  # Arabian Sea
        '2902117': {'lat_center': 10.0, 'lon_center': 77.0, 'lat_range': 4.0, 'lon_range': 6.0},  # South India
        '2902118': {'lat_center': 5.0, 'lon_center': 85.0, 'lat_range': 6.0, 'lon_range': 8.0},   # Bay of Bengal
        '2902119': {'lat_center': -5.0, 'lon_center': 75.0, 'lat_range': 8.0, 'lon_range': 10.0}, # Central Indian Ocean
        '2902120': {'lat_center': 8.0, 'lon_center': 88.0, 'lat_range': 5.0, 'lon_range': 7.0},   # Eastern Bay of Bengal
        '2902121': {'lat_center': 12.0, 'lon_center': 80.0, 'lat_range': 4.0, 'lon_range': 6.0},  # Tamil Nadu coast
    }

    profile_id = 0
    
    for float_data in sample_floats:
        float_id = float_data['float_id']
        region = regions[float_id]
        
        # Create 20 profiles per float (120 total profiles)
        for cycle in range(1, 21):
            profile_id += 1
            
            # Realistic drift pattern
            days_since_deployment = (datetime.now() - float_data['deployment_date']).days
            cycle_days = cycle * 10  # Cycle every 10 days
            
            # Random walk from center with seasonal drift
            seasonal_offset = np.sin(2 * np.pi * cycle_days / 365.0) * 2.0  # Seasonal movement
            
            lat = region['lat_center'] + np.random.normal(0, region['lat_range']/3) + seasonal_offset
            lon = region['lon_center'] + np.random.normal(0, region['lon_range']/3) + seasonal_offset * 0.5
            
            profile_time = float_data['deployment_date'] + timedelta(days=cycle_days)
            
            # Realistic depth ranges based on region
            if region['lat_center'] > 0:  # Northern Indian Ocean - shallower
                max_depth_base = np.random.uniform(800, 1800)
            else:  # Southern Indian Ocean - deeper
                max_depth_base = np.random.uniform(1200, 2000)
                
            max_depth = float(max_depth_base + np.random.normal(0, 200))
            min_depth = float(np.random.uniform(2, 15))
            num_levels = int(max_depth / 10) + np.random.randint(10, 30)  # More realistic level count

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

            # Create realistic measurements for each profile
            depths = np.linspace(min_depth, max_depth, num_levels)
            
            for i, depth in enumerate(depths):
                pressure = float(depth * 1.02 + np.random.normal(0, 0.5))  # Pressure slightly > depth
                
                # Realistic temperature profile with thermocline
                if depth < 100:  # Mixed layer
                    temp_base = 28.0 - depth * 0.05  # Surface layer cooling
                elif depth < 500:  # Thermocline
                    temp_base = 24.0 - (depth - 100) * 0.02  # Rapid cooling
                else:  # Deep water
                    temp_base = 4.0 - (depth - 500) * 0.001  # Slow cooling
                
                temperature = float(temp_base + np.random.normal(0, 0.3))
                
                # Realistic salinity profile
                if depth < 50:
                    salinity_base = 35.0 + np.random.normal(0, 0.2)  # Variable surface
                elif depth < 200:
                    salinity_base = 35.2 + depth * 0.001  # Increasing with depth
                else:
                    salinity_base = 34.8 + np.random.normal(0, 0.1)  # Stable deep water
                
                salinity = float(salinity_base)
                
                # Realistic oxygen profile
                if depth < 100:
                    oxygen_base = 220.0 - depth * 0.5  # High surface, declining
                elif depth < 800:
                    oxygen_base = 180.0 - (depth - 100) * 0.1  # Oxygen minimum zone
                else:
                    oxygen_base = 150.0 + (depth - 800) * 0.02  # Slight increase
                
                oxygen = float(max(10, oxygen_base + np.random.normal(0, 15)))
                
                # Realistic biogeochemical parameters
                if depth < 200:  # Euphotic zone
                    chlorophyll = float(max(0, 0.8 - depth * 0.004 + np.random.normal(0, 0.1)))
                    nitrate = float(max(0, 2.0 + depth * 0.01 + np.random.normal(0, 0.5)))
                else:  # Below euphotic zone
                    chlorophyll = float(max(0, 0.05 + np.random.normal(0, 0.02)))
                    nitrate = float(15.0 + depth * 0.005 + np.random.normal(0, 2.0))
                
                # pH decreases with depth due to CO2
                ph = float(8.1 - depth * 0.0003 + np.random.normal(0, 0.05))
                
                # Backscatter (particle content)
                backscatter = float(max(0, 0.001 + np.random.exponential(0.0005)))

                measurement = {
                    'profile_id': profile['id'],  # Link to profile
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
                    'temperature_qc': np.random.choice([1, 2], p=[0.95, 0.05]),  # Mostly good quality
                    'salinity_qc': np.random.choice([1, 2], p=[0.93, 0.07]),
                    'oxygen_qc': np.random.choice([1, 2, 3], p=[0.90, 0.08, 0.02]),
                    'chlorophyll_qc': np.random.choice([1, 2, 3], p=[0.85, 0.12, 0.03]),
                    'nitrate_qc': np.random.choice([1, 2, 3], p=[0.88, 0.10, 0.02]),
                    'ph_qc': np.random.choice([1, 2], p=[0.92, 0.08])
                }
                sample_measurements.append(measurement)

    logger.info(f"Generated {len(sample_floats)} floats, {len(sample_profiles)} profiles, {len(sample_measurements)} measurements")
    return sample_floats, sample_profiles, sample_measurements, sample_trajectories


def populate_enhanced_database():
    """Populate the database with enhanced realistic data."""
    try:
        db_manager = DatabaseManager()
        vector_store = ARGOVectorStore()

        logger.info("Creating database tables...")
        db_manager.create_tables()

        logger.info("Generating enhanced realistic data...")
        floats, profiles, measurements, trajectories = create_realistic_oceanographic_data()

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
        for profile in profiles:
            try:
                profile_id = db_manager.store_profile_data(profile)
                profile_ids[f"{profile['float_id']}_{profile['cycle_number']}"] = profile_id
                logger.info(f"Stored profile {profile['float_id']}-{profile['cycle_number']}")
            except Exception as e:
                logger.error(f"Error storing profile {profile['float_id']}-{profile['cycle_number']}: {e}")

        # Store measurements with proper profile_id linking
        logger.info("Storing measurements...")
        measurement_batch = []
        batch_size = 500
        
        for measurement in measurements:
            # Find the correct profile_id
            key = f"{measurement['float_id']}_{measurement['cycle_number']}"
            if key in profile_ids:
                measurement['profile_id'] = profile_ids[key]
                measurement_batch.append(measurement)
                
                if len(measurement_batch) >= batch_size:
                    try:
                        db_manager.store_measurements(measurement_batch)
                        logger.info(f"Stored batch of {len(measurement_batch)} measurements")
                        measurement_batch = []
                    except Exception as e:
                        logger.error(f"Error storing measurement batch: {e}")
                        measurement_batch = []
        
        # Store remaining measurements
        if measurement_batch:
            try:
                db_manager.store_measurements(measurement_batch)
                logger.info(f"Stored final batch of {len(measurement_batch)} measurements")
            except Exception as e:
                logger.error(f"Error storing final measurement batch: {e}")

        # Store trajectory data
        logger.info("Storing trajectory data...")
        try:
            db_manager.store_trajectory_data(trajectories)
            logger.info("Trajectory data stored successfully")
        except Exception as e:
            logger.error(f"Error storing trajectory data: {e}")

        # Create vector store documents
        logger.info("Creating vector store documents...")
        profile_docs = []
        for profile in profiles:
            float_data = next(f for f in floats if f['float_id'] == profile['float_id'])
            
            # Find measurements for this profile
            profile_measurements = [m for m in measurements 
                                 if m['float_id'] == profile['float_id'] 
                                 and m['cycle_number'] == profile['cycle_number']]

            available_params = []
            if any(m.get('temperature') is not None for m in profile_measurements): 
                available_params.append('temperature')
            if any(m.get('salinity') is not None for m in profile_measurements): 
                available_params.append('salinity')
            if any(m.get('oxygen') is not None for m in profile_measurements): 
                available_params.append('oxygen')
            if any(m.get('chlorophyll') is not None for m in profile_measurements): 
                available_params.append('chlorophyll')
            if any(m.get('nitrate') is not None for m in profile_measurements): 
                available_params.append('nitrate')
            if any(m.get('ph') is not None for m in profile_measurements): 
                available_params.append('ph')

            profile_doc = {
                'float_id': profile['float_id'],
                'cycle_number': profile['cycle_number'],
                'latitude': float(profile['latitude']),
                'longitude': float(profile['longitude']),
                'profile_time': profile['profile_time'],
                'max_depth': float(profile['max_depth']),
                'num_levels': int(profile['num_levels']),
                'parameters': available_params,
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

        logger.info("Enhanced database population completed successfully!")

        # Display summary
        summary = db_manager.get_data_summary()
        print(f"\nEnhanced Database Summary:")
        print(f"Total Floats: {summary.get('total_floats', 0)}")
        print(f"Total Profiles: {summary.get('total_profiles', 0)}")
        print(f"Total Measurements: {summary.get('total_measurements', 0)}")

        vector_stats = vector_store.get_collection_stats()
        print(f"\nVector Store Summary:")
        print(f"Profile Documents: {vector_stats.get('profiles', {}).get('count', 0)}")
        print(f"Float Documents: {vector_stats.get('floats', {}).get('count', 0)}")

    except Exception as e:
        logger.error(f"Error populating enhanced database: {e}")
        raise

if __name__ == "__main__":
    populate_enhanced_database()
