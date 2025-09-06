#!/usr/bin/env python3
"""
Simple script to check the populated database contents
"""

from src.database.database_manager import DatabaseManager

def main():
    db = DatabaseManager()
    
    # Check data summary
    summary = db.get_data_summary()

    print('Database contents:')
    print(f'- Floats: {summary.get("total_floats", 0)}')
    print(f'- Profiles: {summary.get("total_profiles", 0)}')
    print(f'- Measurements: {summary.get("total_measurements", 0)}')

    # Get geographic bounds
    bounds = summary.get('geographic_bounds', {})
    if bounds:
        print(f'\nGeographic coverage:')
        print(f'- Latitude: {bounds.get("min_lat", 0):.2f} to {bounds.get("max_lat", 0):.2f}')
        print(f'- Longitude: {bounds.get("min_lon", 0):.2f} to {bounds.get("max_lon", 0):.2f}')
            
    # Get date range
    date_range = summary.get('date_range', {})
    if date_range:
        print(f'\nDate range:')
        print(f'- Start: {date_range.get("start_date", "N/A")}')
        print(f'- End: {date_range.get("end_date", "N/A")}')

    # Get sample measurements for one profile
    floats_df = db.get_floats_by_region(-90, 90, -180, 180)  # Get all floats
    if not floats_df.empty:
        print(f'\nSample float data:')
        for i, row in floats_df.head(3).iterrows():
            print(f'  - {row["float_id"]} ({row["institution"]}): {row["status"]}')
        
        # Get sample measurements from first float
        first_float = floats_df.iloc[0]
        measurements_df = db.get_measurements_by_profile(first_float['float_id'], 1)
        if not measurements_df.empty:
            print(f'\nMeasurement parameters available (from profile {first_float["float_id"]}-1):')
            for col in measurements_df.columns:
                if col not in ['pressure', 'depth'] and not col.endswith('_qc'):
                    values = measurements_df[col].dropna()
                    if len(values) > 0:
                        print(f'  - {col}: {values.min():.2f} to {values.max():.2f} (avg: {values.mean():.2f})')

if __name__ == "__main__":
    main()
