#!/usr/bin/env python3
"""
Comprehensive demonstration of the enhanced ARGO oceanographic data system.

This script showcases:
1. Enhanced database population with realistic data
2. Advanced visualization capabilities  
3. Data quality assessment
4. Interactive plotting and mapping
"""

import os
from src.database.database_manager import DatabaseManager
from src.visualization.enhanced_plots import EnhancedARGOVisualizer
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Demonstrate the enhanced ARGO system capabilities."""
    
    print("🌊 Enhanced ARGO Oceanographic Data System Demonstration")
    print("=" * 60)
    
    # Initialize system components
    logger.info("Initializing system components...")
    db = DatabaseManager()
    visualizer = EnhancedARGOVisualizer()
    
    # Create outputs directory if it doesn't exist
    os.makedirs("outputs", exist_ok=True)
    
    # Step 1: Check current data status
    print("\n📊 CHECKING CURRENT DATA STATUS")
    print("-" * 40)
    
    summary = db.get_data_summary()
    print(f"✓ Floats: {summary.get('total_floats', 0)}")
    print(f"✓ Profiles: {summary.get('total_profiles', 0)}")  
    print(f"✓ Measurements: {summary.get('total_measurements', 0)}")
    
    # Geographic coverage
    bounds = summary.get('geographic_bounds', {})
    if bounds:
        print(f"✓ Geographic Coverage:")
        print(f"  - Latitude: {bounds.get('min_lat', 0):.2f}° to {bounds.get('max_lat', 0):.2f}°")
        print(f"  - Longitude: {bounds.get('min_lon', 0):.2f}° to {bounds.get('max_lon', 0):.2f}°")
    
    # Date range
    date_range = summary.get('date_range', {})
    if date_range:
        print(f"✓ Date Range: {date_range.get('start_date', 'N/A')} to {date_range.get('end_date', 'N/A')}")
    
    if summary.get('total_floats', 0) == 0:
        print("\n⚠️  No data available. Please run populate_enhanced.py first.")
        return
    
    # Step 2: Retrieve float data for visualization
    print(f"\n📍 RETRIEVING FLOAT DATA FOR VISUALIZATION")
    print("-" * 40)
    
    floats_df = db.get_floats_by_region(-90, 90, -180, 180)
    print(f"✓ Retrieved {len(floats_df)} float records")
    
    # Display sample float information
    if not floats_df.empty:
        institutions = floats_df['institution'].value_counts()
        print(f"✓ Institutions represented:")
        for inst, count in institutions.items():
            print(f"  - {inst}: {count} floats")
    
    # Step 3: Create comprehensive visualizations
    print(f"\n📈 CREATING ENHANCED VISUALIZATIONS")
    print("-" * 40)
    
    visualizations_created = []
    
    # 3.1: Data Summary Dashboard
    try:
        logger.info("Creating data summary dashboard...")
        dashboard_fig = visualizer.create_data_summary_dashboard(summary, floats_df)
        if dashboard_fig and hasattr(dashboard_fig, 'write_html'):
            dashboard_fig.write_html("outputs/enhanced_data_dashboard.html")
            visualizations_created.append("Enhanced Data Dashboard")
            print("✓ Enhanced Data Dashboard created")
        else:
            print("⚠️  Data Dashboard creation failed")
    except Exception as e:
        print(f"❌ Data Dashboard error: {e}")
        logger.error(f"Dashboard creation failed: {e}")
    
    # 3.2: Interactive Float Location Map
    try:
        logger.info("Creating interactive float map...")
        float_map = visualizer.create_float_map(floats_df)
        if float_map and hasattr(float_map, 'save'):
            float_map.save("outputs/enhanced_float_locations.html")
            visualizations_created.append("Interactive Float Map")
            print("✓ Interactive Float Map created")
        else:
            print("⚠️  Float Map creation failed")
    except Exception as e:
        print(f"❌ Float Map error: {e}")
        logger.error(f"Float map creation failed: {e}")
    
    # 3.3: Geographic Coverage Analysis
    try:
        logger.info("Creating geographic coverage plot...")
        coverage_fig = visualizer.create_geographic_coverage_plot(floats_df)
        if coverage_fig and hasattr(coverage_fig, 'write_html'):
            coverage_fig.write_html("outputs/enhanced_geographic_coverage.html")
            visualizations_created.append("Geographic Coverage Analysis")
            print("✓ Geographic Coverage Analysis created")
        else:
            print("⚠️  Geographic Coverage creation failed")
    except Exception as e:
        print(f"❌ Geographic Coverage error: {e}")
        logger.error(f"Coverage plot creation failed: {e}")
    
    # 3.4: Profile Visualizations (if measurements available)
    if summary.get('total_measurements', 0) > 0:
        try:
            logger.info("Creating profile visualizations...")
            first_float = floats_df.iloc[0]['float_id']
            measurements_df = db.get_measurements_by_profile(first_float, 1)
            
            if not measurements_df.empty:
                # Temperature-Depth Profile
                temp_profile_fig = visualizer.plot_temperature_depth_profile(measurements_df)
                if temp_profile_fig and hasattr(temp_profile_fig, 'write_html'):
                    temp_profile_fig.write_html(f"outputs/enhanced_temperature_profile_{first_float}.html")
                    visualizations_created.append(f"Temperature Profile (Float {first_float})")
                    print(f"✓ Temperature Profile created for Float {first_float}")
                else:
                    print("⚠️  Temperature Profile creation failed")
                
                # Multi-parameter Profile  
                multi_profile_fig = visualizer.create_multi_parameter_profile(measurements_df, first_float)
                if multi_profile_fig and hasattr(multi_profile_fig, 'write_html'):
                    multi_profile_fig.write_html(f"outputs/enhanced_multi_parameter_profile_{first_float}.html")
                    visualizations_created.append(f"Multi-Parameter Profile (Float {first_float})")
                    print(f"✓ Multi-Parameter Profile created for Float {first_float}")
                else:
                    print("⚠️  Multi-Parameter Profile creation failed")
            else:
                print("⚠️  No measurements available for profile visualization")
        except Exception as e:
            print(f"❌ Profile visualization error: {e}")
            logger.error(f"Profile visualization failed: {e}")
    else:
        print("⚠️  No measurements available for profile visualizations")
    
    # Step 4: Summary and Results
    print(f"\n🎯 DEMONSTRATION COMPLETE")
    print("-" * 40)
    
    print(f"✅ System Status:")
    print(f"   - Database: Populated with {summary.get('total_floats', 0)} floats")
    print(f"   - Profiles: {summary.get('total_profiles', 0)} oceanographic profiles")
    print(f"   - Measurements: {summary.get('total_measurements', 0)} data points")
    print(f"   - Visualizations Created: {len(visualizations_created)}")
    
    if visualizations_created:
        print(f"\n📁 Generated Visualizations:")
        for viz in visualizations_created:
            print(f"   ✓ {viz}")
        
        print(f"\n🌐 Open the following files in your browser to view:")
        print(f"   📊 outputs/enhanced_data_dashboard.html")
        print(f"   🗺️  outputs/enhanced_float_locations.html")  
        print(f"   🌍 outputs/enhanced_geographic_coverage.html")
        if summary.get('total_measurements', 0) > 0:
            print(f"   📈 outputs/enhanced_temperature_profile_*.html")
            print(f"   📊 outputs/enhanced_multi_parameter_profile_*.html")
    
    print(f"\n💡 Next Steps:")
    print(f"   - Run populate_enhanced.py to add more realistic measurement data")
    print(f"   - Explore the interactive visualizations in your browser")
    print(f"   - Use the chat interface to query the data")
    print(f"   - Extend the system with additional data sources")
    
    print(f"\n🌊 Enhanced ARGO System Ready for Ocean Data Analysis! 🌊")

if __name__ == "__main__":
    main()
