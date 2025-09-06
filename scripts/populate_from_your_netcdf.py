#!/usr/bin/env python3
"""
Enhanced ARGO data ingestion script specifically for your NetCDF files.
Processes all variables: LATITUDE, LONGITUDE, JULD, PRES, TEMP, PSAL,
PRES_ADJUSTED, TEMP_ADJUSTED, PSAL_ADJUSTED, QC flags, PLATFORM_NUMBER, etc.
"""

import sys
import os
# Add the project root and src directories to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, project_root)
sys.path.insert(0, src_path)

import xarray as xr
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import logging
from tqdm import tqdm
import uuid

from src.config import Config
from src.database.database_manager import DatabaseManager
from src.database.models import ARGOFloat, ARGOProfile, ARGOMeasurement, ARGOTrajectory

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedARGOIngestion:
    """Enhanced ARGO data ingestion for your specific NetCDF format."""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.db_manager.create_tables()
        self.data_dir = Path("data/argo_data")
        
    def get_netcdf_files(self):
        """Get all NetCDF files from your data directory."""
        nc_files = list(self.data_dir.glob("*.nc"))
        logger.info(f"Found {len(nc_files)} NetCDF files")
        return nc_files
    
    def process_netcdf_file(self, file_path: Path):
        """Process a single NetCDF file with all your variables."""
        try:
            logger.info(f"Processing: {file_path.name}")
            ds = xr.open_dataset(file_path)
            
            results = {
                'floats_added': 0,
                'profiles_added': 0,
                'measurements_added': 0,
                'errors': []
            }
            
            # Get dimensions
            n_prof = ds.sizes.get('N_PROF', 0)
            n_levels = ds.sizes.get('N_LEVELS', 0)
            
            logger.info(f"File contains {n_prof} profiles with {n_levels} levels each")
            
            # Process each profile
            for prof_idx in range(n_prof):
                try:
                    # Extract profile metadata
                    profile_data = self._extract_profile_data(ds, prof_idx)
                    if not profile_data:
                        continue
                    
                    # Store float metadata (if new)
                    float_id = profile_data['float_id']
                    if not self._float_exists(float_id):
                        self._store_float_metadata(profile_data)
                        results['floats_added'] += 1
                    
                    # Store profile
                    profile_id = self._store_profile(profile_data)
                    if profile_id:
                        results['profiles_added'] += 1
                        
                        # Process measurements for this profile
                        measurements_count = self._process_profile_measurements(ds, prof_idx, profile_id, profile_data)
                        results['measurements_added'] += measurements_count
                
                except Exception as e:
                    error_msg = f"Error processing profile {prof_idx}: {e}"
                    logger.error(error_msg)
                    results['errors'].append(error_msg)
            
            ds.close()
            return results
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            return {'floats_added': 0, 'profiles_added': 0, 'measurements_added': 0, 'errors': [str(e)]}
    
    def _extract_profile_data(self, ds, prof_idx):
        """Extract profile data for a single profile."""
        try:
            # Get basic coordinates and time
            latitude = float(ds.LATITUDE.values[prof_idx])
            longitude = float(ds.LONGITUDE.values[prof_idx])
            
            # Skip invalid coordinates
            if np.isnan(latitude) or np.isnan(longitude) or abs(latitude) > 90 or abs(longitude) > 180:
                return None
            
            # Get time (JULD)
            juld_val = ds.JULD.values[prof_idx]
            if pd.isna(juld_val):
                return None
            
            profile_time = pd.to_datetime(juld_val)
            
            # Extract platform number and cycle
            platform_number = None
            if 'PLATFORM_NUMBER' in ds:
                platform_data = ds.PLATFORM_NUMBER.values[prof_idx]
                if hasattr(platform_data, 'decode'):
                    platform_number = platform_data.decode('utf-8').strip()
                else:
                    platform_number = str(platform_data).strip()
            
            cycle_number = None
            if 'CYCLE_NUMBER' in ds:
                cycle_number = int(ds.CYCLE_NUMBER.values[prof_idx])
            
            # Extract data mode
            data_mode = None
            if 'DATA_MODE' in ds:
                data_mode_val = ds.DATA_MODE.values[prof_idx]
                if hasattr(data_mode_val, 'decode'):
                    data_mode = data_mode_val.decode('utf-8').strip()
                else:
                    data_mode = str(data_mode_val).strip()
            
            # Extract QC flags
            position_qc = self._extract_qc_flag(ds, 'POSITION_QC', prof_idx) if 'POSITION_QC' in ds else None
            juld_qc = self._extract_qc_flag(ds, 'JULD_QC', prof_idx) if 'JULD_QC' in ds else None
            profile_pres_qc = self._extract_qc_flag(ds, 'PROFILE_PRES_QC', prof_idx) if 'PROFILE_PRES_QC' in ds else None
            profile_temp_qc = self._extract_qc_flag(ds, 'PROFILE_TEMP_QC', prof_idx) if 'PROFILE_TEMP_QC' in ds else None
            profile_psal_qc = self._extract_qc_flag(ds, 'PROFILE_PSAL_QC', prof_idx) if 'PROFILE_PSAL_QC' in ds else None
            
            float_id = platform_number or f"unknown_{prof_idx}"
            
            return {
                'float_id': float_id,
                'platform_number': platform_number,
                'cycle_number': cycle_number or prof_idx,
                'latitude': latitude,
                'longitude': longitude,
                'profile_time': profile_time,
                'data_mode': data_mode,
                'position_qc': position_qc,
                'juld_qc': juld_qc,
                'profile_pres_qc': profile_pres_qc,
                'profile_temp_qc': profile_temp_qc,
                'profile_psal_qc': profile_psal_qc
            }
            
        except Exception as e:
            logger.error(f"Error extracting profile data for index {prof_idx}: {e}")
            return None
    
    def _extract_qc_flag(self, ds, var_name, prof_idx):
        """Extract QC flag value."""
        try:
            qc_val = ds[var_name].values[prof_idx]
            if hasattr(qc_val, 'decode'):
                return qc_val.decode('utf-8').strip()
            else:
                return str(qc_val).strip()
        except:
            return None
    
    def _float_exists(self, float_id):
        """Check if float already exists in database."""
        session = self.db_manager.get_session()
        try:
            exists = session.query(ARGOFloat).filter_by(float_id=float_id).first() is not None
            return exists
        finally:
            session.close()
    
    def _store_float_metadata(self, profile_data):
        """Store float metadata."""
        session = self.db_manager.get_session()
        try:
            float_record = ARGOFloat(
                float_id=profile_data['float_id'],
                wmo_id=profile_data['platform_number'] or 'unknown',
                institution='Unknown',
                data_mode=profile_data['data_mode'] or 'R',
                status='active'
            )
            session.add(float_record)
            session.commit()
            logger.debug(f"Added float: {profile_data['float_id']}")
        except Exception as e:
            session.rollback()
            logger.error(f"Error storing float metadata: {e}")
        finally:
            session.close()
    
    def _store_profile(self, profile_data):
        """Store profile data."""
        session = self.db_manager.get_session()
        try:
            profile_record = ARGOProfile(
                float_id=profile_data['float_id'],
                cycle_number=profile_data['cycle_number'],
                latitude=profile_data['latitude'],
                longitude=profile_data['longitude'],
                profile_time=profile_data['profile_time'],
                platform_number=profile_data['platform_number'],
                data_mode=profile_data['data_mode'],
                profile_pres_qc=profile_data['profile_pres_qc'],
                profile_temp_qc=profile_data['profile_temp_qc'],
                profile_psal_qc=profile_data['profile_psal_qc'],
                position_qc=profile_data['position_qc'],
                juld_qc=profile_data['juld_qc']
            )
            session.add(profile_record)
            session.commit()
            return profile_record.id
        except Exception as e:
            session.rollback()
            logger.error(f"Error storing profile: {e}")
            return None
        finally:
            session.close()
    
    def _process_profile_measurements(self, ds, prof_idx, profile_id, profile_data):
        """Process all measurements for a profile."""
        session = self.db_manager.get_session()
        measurements_added = 0
        
        try:
            n_levels = ds.sizes.get('N_LEVELS', 0)
            
            # Get all measurement arrays for this profile
            measurements_data = self._extract_measurements_data(ds, prof_idx, n_levels)
            
            # Process each level
            for level_idx in range(n_levels):
                measurement_data = self._extract_level_measurement(measurements_data, level_idx, profile_id, profile_data)
                
                if measurement_data and self._has_valid_data(measurement_data):
                    measurement_record = ARGOMeasurement(**measurement_data)
                    session.add(measurement_record)
                    measurements_added += 1
            
            # Update profile with calculated fields
            if measurements_added > 0:
                self._update_profile_stats(session, profile_id, measurements_data)
            
            session.commit()
            return measurements_added
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error processing measurements: {e}")
            return 0
        finally:
            session.close()
    
    def _extract_measurements_data(self, ds, prof_idx, n_levels):
        """Extract all measurement arrays for a profile."""
        data = {}
        
        # Core parameters
        variables = {
            'PRES': 'pressure',
            'TEMP': 'temperature', 
            'PSAL': 'salinity',
            'PRES_ADJUSTED': 'pressure_adjusted',
            'TEMP_ADJUSTED': 'temperature_adjusted',
            'PSAL_ADJUSTED': 'salinity_adjusted',
            'PRES_ADJUSTED_ERROR': 'pressure_adjusted_error',
            'TEMP_ADJUSTED_ERROR': 'temperature_adjusted_error',
            'PSAL_ADJUSTED_ERROR': 'salinity_adjusted_error'
        }
        
        # QC flags
        qc_variables = {
            'PRES_QC': 'pressure_qc',
            'TEMP_QC': 'temperature_qc',
            'PSAL_QC': 'salinity_qc',
            'PRES_ADJUSTED_QC': 'pressure_adjusted_qc',
            'TEMP_ADJUSTED_QC': 'temperature_adjusted_qc',
            'PSAL_ADJUSTED_QC': 'salinity_adjusted_qc'
        }
        
        # Extract numerical data
        for nc_var, db_field in variables.items():
            if nc_var in ds:
                data[db_field] = ds[nc_var].values[prof_idx, :]
            else:
                data[db_field] = np.full(n_levels, np.nan)
        
        # Extract QC flags
        for nc_var, db_field in qc_variables.items():
            if nc_var in ds:
                qc_data = ds[nc_var].values[prof_idx, :]
                # Convert QC flags to strings
                if hasattr(qc_data, 'dtype') and qc_data.dtype.kind in ['U', 'S']:
                    data[db_field] = [str(val).strip() if not pd.isna(val) else None for val in qc_data]
                else:
                    data[db_field] = [str(int(val)).strip() if not pd.isna(val) else None for val in qc_data]
            else:
                data[db_field] = [None] * n_levels
        
        return data
    
    def _extract_level_measurement(self, measurements_data, level_idx, profile_id, profile_data):
        """Extract measurement data for a single level."""
        try:
            measurement = {
                'profile_id': profile_id,
                'float_id': profile_data['float_id'],
                'cycle_number': profile_data['cycle_number']
            }
            
            # Add all measurement values
            for field_name, values in measurements_data.items():
                if isinstance(values[level_idx], (str, type(None))):
                    measurement[field_name] = values[level_idx]
                else:
                    val = values[level_idx]
                    # Convert numpy types to Python native types for database compatibility
                    if not pd.isna(val) and val is not None:
                        # Handle numpy scalars by converting to Python float
                        measurement[field_name] = float(val)
                    else:
                        measurement[field_name] = None
            
            return measurement
            
        except Exception as e:
            logger.error(f"Error extracting level measurement: {e}")
            return None
    
    def _has_valid_data(self, measurement_data):
        """Check if measurement has any valid data."""
        key_fields = ['pressure', 'temperature', 'salinity', 'pressure_adjusted', 'temperature_adjusted', 'salinity_adjusted']
        return any(measurement_data.get(field) is not None and not pd.isna(measurement_data.get(field, np.nan)) 
                  for field in key_fields)
    
    def _update_profile_stats(self, session, profile_id, measurements_data):
        """Update profile with calculated statistics."""
        try:
            profile = session.query(ARGOProfile).filter_by(id=profile_id).first()
            if profile:
                # Calculate depth statistics from pressure data
                pressure_data = measurements_data.get('pressure', [])
                valid_pressures = [p for p in pressure_data if not pd.isna(p)]
                
                if valid_pressures:
                    # Convert numpy types to Python native types for database compatibility
                    profile.max_depth = float(max(valid_pressures))
                    profile.min_depth = float(min(valid_pressures))
                    profile.num_levels = int(len(valid_pressures))
        except Exception as e:
            logger.error(f"Error updating profile stats: {e}")
    
    def process_all_files(self, max_files=None):
        """Process all NetCDF files."""
        nc_files = self.get_netcdf_files()
        
        if max_files:
            nc_files = nc_files[:max_files]
            logger.info(f"Processing first {max_files} files only")
        
        total_results = {
            'files_processed': 0,
            'floats_added': 0,
            'profiles_added': 0,
            'measurements_added': 0,
            'errors': []
        }
        
        for file_path in tqdm(nc_files, desc="Processing NetCDF files"):
            try:
                results = self.process_netcdf_file(file_path)
                total_results['files_processed'] += 1
                total_results['floats_added'] += results['floats_added']
                total_results['profiles_added'] += results['profiles_added']
                total_results['measurements_added'] += results['measurements_added']
                total_results['errors'].extend(results['errors'])
                
                if total_results['files_processed'] % 10 == 0:
                    logger.info(f"Processed {total_results['files_processed']} files. "
                              f"Added {total_results['profiles_added']} profiles, "
                              f"{total_results['measurements_added']} measurements")
                
            except Exception as e:
                error_msg = f"Failed to process {file_path}: {e}"
                logger.error(error_msg)
                total_results['errors'].append(error_msg)
        
        return total_results

def main():
    """Main function."""
    print("🌊 Enhanced ARGO NetCDF Ingestion")
    print("=" * 50)
    
    try:
        # Validate configuration
        Config.validate()
        
        # Initialize ingestion system
        ingestion = EnhancedARGOIngestion()
        
        # Process files (start with first 5 for testing)
        print("Processing your NetCDF files...")
        results = ingestion.process_all_files(max_files=5)
        
        # Print results
        print("\n" + "=" * 50)
        print("INGESTION RESULTS")
        print("=" * 50)
        print(f"Files processed: {results['files_processed']}")
        print(f"Floats added: {results['floats_added']}")
        print(f"Profiles added: {results['profiles_added']}")
        print(f"Measurements added: {results['measurements_added']}")
        
        if results['errors']:
            print(f"\nErrors encountered: {len(results['errors'])}")
            for error in results['errors'][:5]:  # Show first 5 errors
                print(f"  - {error}")
        
        print("\n✅ Database now contains all your NetCDF variables!")
        print("✅ You can now run accurate queries with:")
        print("   - LATITUDE, LONGITUDE, JULD")
        print("   - PRES, TEMP, PSAL")
        print("   - PRES_ADJUSTED, TEMP_ADJUSTED, PSAL_ADJUSTED")
        print("   - All QC flags")
        print("   - PLATFORM_NUMBER, CYCLE_NUMBER, DATA_MODE")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
