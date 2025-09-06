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
        if dashboard_fig and hasattr(dashboard_fig, 'write_html'):\n            dashboard_fig.write_html(\"outputs/enhanced_data_dashboard.html\")\n            visualizations_created.append(\"Enhanced Data Dashboard\")\n            print(\"✓ Enhanced Data Dashboard created\")\n        else:\n            print(\"⚠️  Data Dashboard creation failed\")\n    except Exception as e:\n        print(f\"❌ Data Dashboard error: {e}\")\n        logger.error(f\"Dashboard creation failed: {e}\")\n    \n    # 3.2: Interactive Float Location Map\n    try:\n        logger.info(\"Creating interactive float map...\")\n        float_map = visualizer.create_float_map(floats_df)\n        if float_map and hasattr(float_map, 'save'):\n            float_map.save(\"outputs/enhanced_float_locations.html\")\n            visualizations_created.append(\"Interactive Float Map\")\n            print(\"✓ Interactive Float Map created\")\n        else:\n            print(\"⚠️  Float Map creation failed\")\n    except Exception as e:\n        print(f\"❌ Float Map error: {e}\")\n        logger.error(f\"Float map creation failed: {e}\")\n    \n    # 3.3: Geographic Coverage Analysis\n    try:\n        logger.info(\"Creating geographic coverage plot...\")\n        coverage_fig = visualizer.create_geographic_coverage_plot(floats_df)\n        if coverage_fig and hasattr(coverage_fig, 'write_html'):\n            coverage_fig.write_html(\"outputs/enhanced_geographic_coverage.html\")\n            visualizations_created.append(\"Geographic Coverage Analysis\")\n            print(\"✓ Geographic Coverage Analysis created\")\n        else:\n            print(\"⚠️  Geographic Coverage creation failed\")\n    except Exception as e:\n        print(f\"❌ Geographic Coverage error: {e}\")\n        logger.error(f\"Coverage plot creation failed: {e}\")\n    \n    # 3.4: Profile Visualizations (if measurements available)\n    if summary.get('total_measurements', 0) > 0:\n        try:\n            logger.info(\"Creating profile visualizations...\")\n            first_float = floats_df.iloc[0]['float_id']\n            measurements_df = db.get_measurements_by_profile(first_float, 1)\n            \n            if not measurements_df.empty:\n                # Temperature-Depth Profile\n                temp_profile_fig = visualizer.plot_temperature_depth_profile(measurements_df)\n                if temp_profile_fig and hasattr(temp_profile_fig, 'write_html'):\n                    temp_profile_fig.write_html(f\"outputs/enhanced_temperature_profile_{first_float}.html\")\n                    visualizations_created.append(f\"Temperature Profile (Float {first_float})\")\n                    print(f\"✓ Temperature Profile created for Float {first_float}\")\n                else:\n                    print(\"⚠️  Temperature Profile creation failed\")\n                \n                # Multi-parameter Profile\n                multi_profile_fig = visualizer.create_multi_parameter_profile(measurements_df, first_float)\n                if multi_profile_fig and hasattr(multi_profile_fig, 'write_html'):\n                    multi_profile_fig.write_html(f\"outputs/enhanced_multi_parameter_profile_{first_float}.html\")\n                    visualizations_created.append(f\"Multi-Parameter Profile (Float {first_float})\")\n                    print(f\"✓ Multi-Parameter Profile created for Float {first_float}\")\n                else:\n                    print(\"⚠️  Multi-Parameter Profile creation failed\")\n            else:\n                print(\"⚠️  No measurements available for profile visualization\")\n        except Exception as e:\n            print(f\"❌ Profile visualization error: {e}\")\n            logger.error(f\"Profile visualization failed: {e}\")\n    else:\n        print(\"⚠️  No measurements available for profile visualizations\")\n    \n    # 3.5: Depth Distribution Analysis\n    try:\n        logger.info(\"Creating depth distribution analysis...\")\n        # Combine profile and measurement data for depth analysis\n        combined_data = floats_df.copy()\n        depth_fig = visualizer.create_depth_distribution_plot(combined_data)\n        if depth_fig and hasattr(depth_fig, 'write_html'):\n            depth_fig.write_html(\"outputs/enhanced_depth_distribution.html\")\n            visualizations_created.append(\"Depth Distribution Analysis\")\n            print(\"✓ Depth Distribution Analysis created\")\n        else:\n            print(\"⚠️  Depth Distribution creation failed\")\n    except Exception as e:\n        print(f\"❌ Depth Distribution error: {e}\")\n        logger.error(f\"Depth distribution failed: {e}\")\n    \n    # Step 4: Summary and Results\n    print(f\"\\n🎯 DEMONSTRATION COMPLETE\")\n    print(\"-\" * 40)\n    \n    print(f\"✅ System Status:\")\n    print(f\"   - Database: Populated with {summary.get('total_floats', 0)} floats\")\n    print(f\"   - Profiles: {summary.get('total_profiles', 0)} oceanographic profiles\")\n    print(f\"   - Measurements: {summary.get('total_measurements', 0)} data points\")\n    print(f\"   - Visualizations Created: {len(visualizations_created)}\")\n    \n    if visualizations_created:\n        print(f\"\\n📁 Generated Visualizations:\")\n        for viz in visualizations_created:\n            print(f\"   ✓ {viz}\")\n        \n        print(f\"\\n🌐 Open the following files in your browser to view:\")\n        print(f\"   📊 outputs/enhanced_data_dashboard.html\")\n        print(f\"   🗺️  outputs/enhanced_float_locations.html\")\n        print(f\"   🌍 outputs/enhanced_geographic_coverage.html\")\n        print(f\"   📈 outputs/enhanced_temperature_profile_*.html\")\n        print(f\"   📉 outputs/enhanced_depth_distribution.html\")\n    \n    print(f\"\\n💡 Next Steps:\")\n    print(f\"   - Run populate_enhanced.py to add more realistic measurement data\")\n    print(f\"   - Explore the interactive visualizations in your browser\")\n    print(f\"   - Use the chat interface to query the data\")\n    print(f\"   - Extend the system with additional data sources\")\n    \n    print(f\"\\n🌊 Enhanced ARGO System Ready for Ocean Data Analysis! 🌊\")\n\nif __name__ == \"__main__\":\n    main()
