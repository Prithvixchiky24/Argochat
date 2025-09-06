"""
Enhanced plotting capabilities for ARGO oceanographic data visualization.
Provides comprehensive plotting functions for profiles, time series, and maps.
"""
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import folium
from folium import plugins
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Tuple, Any
import streamlit as st

logger = logging.getLogger(__name__)

class EnhancedARGOVisualizer:
    """Enhanced visualization class for ARGO data with comprehensive plotting capabilities."""
    
    def __init__(self):
        self.colors = {
            'temperature': '#FF6B6B',
            'salinity': '#4ECDC4', 
            'oxygen': '#45B7D1',
            'chlorophyll': '#96CEB4',
            'nitrate': '#FFEAA7',
            'ph': '#DDA0DD',
            'pressure': '#95A5A6',
            'depth': '#34495E'
        }
        
        self.institutions = {
            'INCOIS': '#E74C3C',
            'CSIR-NIO': '#3498DB', 
            'NIOT': '#2ECC71',
            'default': '#95A5A6'
        }
    
    def create_temperature_depth_profile(self, data: pd.DataFrame, 
                                       float_ids: List[str] = None) -> go.Figure:
        """Create temperature-depth profile plots."""
        try:
            fig = go.Figure()
            
            if float_ids is None:
                float_ids = data['float_id'].unique()
            
            for float_id in float_ids[:6]:  # Limit to 6 floats for readability
                float_data = data[data['float_id'] == float_id]
                if not float_data.empty and 'temperature' in float_data.columns:
                    fig.add_trace(go.Scatter(
                        x=float_data['temperature'],
                        y=-float_data['depth'],  # Negative for depth
                        mode='lines+markers',
                        name=f'Float {float_id}',
                        line=dict(width=2),
                        marker=dict(size=4),
                        hovertemplate=(
                            f'<b>Float {float_id}</b><br>' +
                            'Temperature: %{x:.2f}°C<br>' +
                            'Depth: %{y:.0f}m<extra></extra>'
                        )
                    ))
            
            fig.update_layout(
                title='Temperature-Depth Profiles',
                xaxis_title='Temperature (°C)',
                yaxis_title='Depth (m)',
                height=600,
                hovermode='closest',
                template='plotly_white'
            )
            
            return fig
        except Exception as e:
            logger.error(f"Error creating temperature-depth profile: {e}")
            return go.Figure()
    
    def create_multi_parameter_profile(self, data: pd.DataFrame, 
                                     float_id: str) -> go.Figure:
        """Create multi-parameter profile plot for a single float."""
        try:
            float_data = data[data['float_id'] == float_id].sort_values('depth')
            
            if float_data.empty:
                return go.Figure().add_annotation(
                    text=f"No data available for float {float_id}",
                    xref="paper", yref="paper", x=0.5, y=0.5,
                    showarrow=False, font_size=16
                )
            
            # Create subplots
            fig = make_subplots(
                rows=2, cols=3,
                subplot_titles=['Temperature', 'Salinity', 'Oxygen', 
                              'Chlorophyll', 'Nitrate', 'pH'],
                vertical_spacing=0.08,
                horizontal_spacing=0.05
            )
            
            parameters = ['temperature', 'salinity', 'oxygen', 
                         'chlorophyll', 'nitrate', 'ph']
            units = ['°C', 'PSU', 'μmol/kg', 'mg/m³', 'μmol/kg', '']
            positions = [(1,1), (1,2), (1,3), (2,1), (2,2), (2,3)]
            
            for param, unit, (row, col) in zip(parameters, units, positions):
                if param in float_data.columns and not float_data[param].isna().all():
                    fig.add_trace(
                        go.Scatter(
                            x=float_data[param],
                            y=-float_data['depth'],
                            mode='lines+markers',
                            name=param.title(),
                            line=dict(color=self.colors.get(param, '#333333'), width=2),
                            marker=dict(size=3),
                            showlegend=False,
                            hovertemplate=(
                                f'<b>{param.title()}</b><br>' +
                                f'{param.title()}: %{{x:.2f}} {unit}<br>' +
                                'Depth: %{y:.0f}m<extra></extra>'
                            )
                        ),
                        row=row, col=col
                    )
                    
                    fig.update_xaxes(title_text=f'{param.title()} ({unit})', 
                                   row=row, col=col)
                    fig.update_yaxes(title_text='Depth (m)', row=row, col=col)
            
            fig.update_layout(
                title=f'Multi-Parameter Profile - Float {float_id}',
                height=800,
                template='plotly_white'
            )
            
            return fig
        except Exception as e:
            logger.error(f"Error creating multi-parameter profile: {e}")
            return go.Figure()
    
    def create_time_series_plot(self, data: pd.DataFrame, 
                               parameter: str = 'temperature',
                               depth_range: Tuple[float, float] = (0, 100)) -> go.Figure:
        """Create time series plot for a parameter at specific depth range."""
        try:
            # Filter by depth range
            depth_data = data[
                (data['depth'] >= depth_range[0]) & 
                (data['depth'] <= depth_range[1])
            ]
            
            if depth_data.empty or parameter not in depth_data.columns:
                return go.Figure().add_annotation(
                    text=f"No {parameter} data available for depth range {depth_range[0]}-{depth_range[1]}m",
                    xref="paper", yref="paper", x=0.5, y=0.5,
                    showarrow=False, font_size=16
                )
            
            # Group by float and calculate mean values over time
            time_series = depth_data.groupby(['float_id', 'profile_time'])[parameter].mean().reset_index()
            
            fig = go.Figure()
            
            for float_id in time_series['float_id'].unique():
                float_ts = time_series[time_series['float_id'] == float_id]
                fig.add_trace(go.Scatter(
                    x=float_ts['profile_time'],
                    y=float_ts[parameter],
                    mode='lines+markers',
                    name=f'Float {float_id}',
                    line=dict(width=2),
                    marker=dict(size=6),
                    hovertemplate=(
                        f'<b>Float {float_id}</b><br>' +
                        f'{parameter.title()}: %{{y:.2f}}<br>' +
                        'Date: %{x}<br>' +
                        f'Depth: {depth_range[0]}-{depth_range[1]}m<extra></extra>'
                    )
                ))
            
            unit = {'temperature': '°C', 'salinity': 'PSU', 'oxygen': 'μmol/kg',
                   'chlorophyll': 'mg/m³', 'nitrate': 'μmol/kg', 'ph': ''}.get(parameter, '')
            
            fig.update_layout(
                title=f'{parameter.title()} Time Series ({depth_range[0]}-{depth_range[1]}m depth)',
                xaxis_title='Date',
                yaxis_title=f'{parameter.title()} ({unit})',
                height=500,
                template='plotly_white',
                hovermode='x unified'
            )
            
            return fig
        except Exception as e:
            logger.error(f"Error creating time series plot: {e}")
            return go.Figure()
    
    def create_geographic_map(self, data: pd.DataFrame, 
                            parameter: str = None,
                            map_center: Tuple[float, float] = (10.0, 75.0)) -> folium.Map:
        """Create interactive geographic map of float locations."""
        try:
            # Create base map
            m = folium.Map(
                location=map_center,
                zoom_start=6,
                tiles='OpenStreetMap'
            )
            
            # Add different tile layers
            folium.TileLayer('Stamen Terrain').add_to(m)
            folium.TileLayer('CartoDB positron').add_to(m)
            
            # Get latest position for each float
            latest_positions = data.groupby('float_id').agg({
                'latitude': 'last',
                'longitude': 'last',
                'profile_time': 'last',
                'float_id': 'first',
                **({'institution': 'first'} if 'institution' in data.columns else {})
            }).reset_index(drop=True)
            
            # Add markers for each float
            for _, row in latest_positions.iterrows():
                institution = row.get('institution', 'Unknown')
                color = self.institutions.get(institution, self.institutions['default'])
                
                popup_text = f"""
                <b>Float {row['float_id']}</b><br>
                Institution: {institution}<br>
                Latest Position: {row['latitude']:.3f}°N, {row['longitude']:.3f}°E<br>
                Last Update: {row['profile_time'].strftime('%Y-%m-%d') if pd.notna(row['profile_time']) else 'N/A'}
                """
                
                folium.CircleMarker(
                    location=[row['latitude'], row['longitude']],
                    radius=8,
                    popup=folium.Popup(popup_text, max_width=200),
                    color='white',
                    weight=2,
                    fillColor=color,
                    fillOpacity=0.7
                ).add_to(m)
            
            # Add trajectories if enough data
            if len(data) > len(latest_positions):
                for float_id in data['float_id'].unique():
                    float_data = data[data['float_id'] == float_id].sort_values('profile_time')
                    if len(float_data) > 1:
                        trajectory_coords = [
                            [row['latitude'], row['longitude']] 
                            for _, row in float_data.iterrows()
                        ]
                        
                        folium.PolyLine(
                            trajectory_coords,
                            weight=2,
                            color=self.institutions.get(
                                float_data['institution'].iloc[0] if 'institution' in float_data else 'Unknown',
                                self.institutions['default']
                            ),
                            opacity=0.6,
                            popup=f'Float {float_id} trajectory'
                        ).add_to(m)
            
            # Add layer control
            folium.LayerControl().add_to(m)
            
            return m
            
        except Exception as e:
            logger.error(f"Error creating geographic map: {e}")
            # Return basic map on error
            return folium.Map(location=map_center, zoom_start=6)
    
    def create_parameter_comparison(self, data: pd.DataFrame, 
                                  parameters: List[str],
                                  depth_level: float = 100) -> go.Figure:
        """Create comparison plot of multiple parameters at a specific depth."""
        try:
            # Filter data near the specified depth (±25m tolerance)
            depth_data = data[
                (data['depth'] >= depth_level - 25) & 
                (data['depth'] <= depth_level + 25)
            ]
            
            if depth_data.empty:
                return go.Figure().add_annotation(
                    text=f"No data available near {depth_level}m depth",
                    xref="paper", yref="paper", x=0.5, y=0.5,
                    showarrow=False, font_size=16
                )
            
            # Create subplots for parameters
            n_params = len(parameters)
            cols = min(3, n_params)
            rows = (n_params - 1) // cols + 1
            
            fig = make_subplots(
                rows=rows, cols=cols,
                subplot_titles=[param.title() for param in parameters],
                vertical_spacing=0.12
            )
            
            for i, param in enumerate(parameters):
                if param in depth_data.columns and not depth_data[param].isna().all():
                    row = (i // cols) + 1
                    col = (i % cols) + 1
                    
                    # Box plot by institution if available
                    if 'institution' in depth_data.columns:
                        for institution in depth_data['institution'].unique():
                            inst_data = depth_data[depth_data['institution'] == institution]
                            fig.add_trace(
                                go.Box(
                                    y=inst_data[param],
                                    name=institution,
                                    boxpoints='outliers',
                                    marker_color=self.institutions.get(institution, self.institutions['default']),
                                    showlegend=(i == 0)  # Only show legend for first subplot
                                ),
                                row=row, col=col
                            )
                    else:
                        # Simple histogram if no institution data
                        fig.add_trace(
                            go.Histogram(
                                x=depth_data[param],
                                name=param.title(),
                                marker_color=self.colors.get(param, '#333333'),
                                showlegend=False
                            ),
                            row=row, col=col
                        )
                    
                    unit = {'temperature': '°C', 'salinity': 'PSU', 'oxygen': 'μmol/kg',
                           'chlorophyll': 'mg/m³', 'nitrate': 'μmol/kg', 'ph': ''}.get(param, '')
                    fig.update_yaxes(title_text=f'{param.title()} ({unit})', row=row, col=col)
            
            fig.update_layout(
                title=f'Parameter Comparison at {depth_level}m Depth',
                height=400 * rows,
                template='plotly_white'
            )
            
            return fig
        except Exception as e:
            logger.error(f"Error creating parameter comparison: {e}")
            return go.Figure()
    
    def create_correlation_heatmap(self, data: pd.DataFrame, 
                                 parameters: List[str] = None) -> go.Figure:
        """Create correlation heatmap between oceanographic parameters."""
        try:
            if parameters is None:
                parameters = ['temperature', 'salinity', 'oxygen', 'chlorophyll', 'nitrate', 'ph']
            
            # Filter data to include only specified parameters
            available_params = [p for p in parameters if p in data.columns]
            
            if len(available_params) < 2:
                return go.Figure().add_annotation(
                    text="Not enough parameters for correlation analysis",
                    xref="paper", yref="paper", x=0.5, y=0.5,
                    showarrow=False, font_size=16
                )
            
            # Calculate correlation matrix
            correlation_data = data[available_params].corr()
            
            # Create heatmap
            fig = go.Figure(data=go.Heatmap(
                z=correlation_data.values,
                x=[param.title() for param in correlation_data.columns],
                y=[param.title() for param in correlation_data.index],
                colorscale='RdBu',
                zmid=0,
                text=np.round(correlation_data.values, 2),
                texttemplate='%{text}',
                textfont={"size": 12},
                hovertemplate='<b>%{x} vs %{y}</b><br>Correlation: %{z:.3f}<extra></extra>'
            ))
            
            fig.update_layout(
                title='Parameter Correlation Matrix',
                height=600,
                template='plotly_white'
            )
            
            return fig
        except Exception as e:
            logger.error(f"Error creating correlation heatmap: {e}")
            return go.Figure()
    
    def create_depth_distribution_plot(self, data: pd.DataFrame) -> go.Figure:
        """Create depth distribution analysis plot."""
        try:
            fig = make_subplots(
                rows=1, cols=2,
                subplot_titles=['Profile Depth Distribution', 'Measurement Depth Coverage'],
                column_widths=[0.5, 0.5]
            )
            
            # Profile depth distribution
            if 'max_depth' in data.columns:
                fig.add_trace(
                    go.Histogram(
                        x=data['max_depth'],
                        name='Max Depth',
                        marker_color='#3498DB',
                        opacity=0.7,
                        nbinsx=20
                    ),
                    row=1, col=1
                )
            
            # Measurement depth coverage
            if 'depth' in data.columns:
                fig.add_trace(
                    go.Histogram(
                        x=data['depth'],
                        name='All Measurements',
                        marker_color='#E74C3C',
                        opacity=0.7,
                        nbinsx=30
                    ),
                    row=1, col=2
                )
            
            fig.update_layout(
                title='Depth Analysis',
                height=400,
                template='plotly_white',
                showlegend=False
            )
            
            fig.update_xaxes(title_text='Depth (m)', row=1, col=1)
            fig.update_xaxes(title_text='Depth (m)', row=1, col=2)
            fig.update_yaxes(title_text='Count', row=1, col=1)
            fig.update_yaxes(title_text='Count', row=1, col=2)
            
            return fig
        except Exception as e:
            logger.error(f"Error creating depth distribution plot: {e}")
            return go.Figure()
    
    def create_data_quality_dashboard(self, data: pd.DataFrame) -> go.Figure:
        """Create data quality assessment dashboard."""
        try:
            qc_columns = [col for col in data.columns if col.endswith('_qc')]
            
            if not qc_columns:
                return go.Figure().add_annotation(
                    text="No quality control data available",
                    xref="paper", yref="paper", x=0.5, y=0.5,
                    showarrow=False, font_size=16
                )
            
            n_qc = len(qc_columns)
            cols = min(3, n_qc)
            rows = (n_qc - 1) // cols + 1
            
            fig = make_subplots(
                rows=rows, cols=cols,
                subplot_titles=[col.replace('_qc', '').title() + ' QC' for col in qc_columns],
                vertical_spacing=0.15
            )
            
            qc_labels = {1: 'Good', 2: 'Probably Good', 3: 'Probably Bad', 4: 'Bad', 9: 'Missing'}
            colors = ['#2ECC71', '#F39C12', '#E74C3C', '#8B0000', '#95A5A6']
            
            for i, qc_col in enumerate(qc_columns):
                row = (i // cols) + 1
                col = (i % cols) + 1
                
                qc_counts = data[qc_col].value_counts().sort_index()
                labels = [qc_labels.get(qc, f'QC {qc}') for qc in qc_counts.index]
                values = qc_counts.values
                
                fig.add_trace(
                    go.Pie(
                        labels=labels,
                        values=values,
                        name=qc_col,
                        marker_colors=colors[:len(labels)],
                        showlegend=(i == 0)  # Only show legend for first pie
                    ),
                    row=row, col=col
                )
            
            fig.update_layout(
                title='Data Quality Assessment',
                height=300 * rows,
                template='plotly_white'
            )
            
            return fig
        except Exception as e:
            logger.error(f"Error creating data quality dashboard: {e}")
            return go.Figure()
    
    def create_float_map(self, data: pd.DataFrame) -> folium.Map:
        """Create a map showing float locations."""
        return self.create_geographic_map(data)
    
    def create_data_summary_dashboard(self, summary: dict, floats_df: pd.DataFrame = None) -> go.Figure:
        """Create a comprehensive data summary dashboard."""
        try:
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=[
                    'Data Counts', 'Geographic Coverage', 
                    'Institution Distribution', 'Date Range Coverage'
                ],
                specs=[[{'type': 'bar'}, {'type': 'scattergeo'}],
                       [{'type': 'pie'}, {'type': 'bar'}]],
                vertical_spacing=0.15
            )
            
            # Data counts
            counts = ['Floats', 'Profiles', 'Measurements']
            values = [
                summary.get('total_floats', 0),
                summary.get('total_profiles', 0), 
                summary.get('total_measurements', 0)
            ]
            
            fig.add_trace(
                go.Bar(x=counts, y=values, name='Data Counts',
                      marker_color=['#E74C3C', '#3498DB', '#2ECC71']),
                row=1, col=1
            )
            
            # Geographic coverage
            bounds = summary.get('geographic_bounds', {})
            if bounds and all(v is not None for v in bounds.values()):
                fig.add_trace(
                    go.Scattergeo(
                        lon=[bounds['min_lon'], bounds['max_lon'], bounds['min_lon'], bounds['max_lon']],
                        lat=[bounds['min_lat'], bounds['min_lat'], bounds['max_lat'], bounds['max_lat']],
                        mode='markers',
                        name='Coverage Bounds',
                        marker=dict(size=8, color='red')
                    ),
                    row=1, col=2
                )
            
            # Institution distribution (if float data provided)
            if floats_df is not None and 'institution' in floats_df.columns:
                inst_counts = floats_df['institution'].value_counts()
                colors = [self.institutions.get(inst, self.institutions['default']) 
                         for inst in inst_counts.index]
                
                fig.add_trace(
                    go.Pie(
                        labels=inst_counts.index,
                        values=inst_counts.values,
                        name='Institutions',
                        marker_colors=colors
                    ),
                    row=2, col=1
                )
            
            # Date range (simplified representation)
            date_range = summary.get('date_range', {})
            if date_range:
                start_date = date_range.get('start_date')
                end_date = date_range.get('end_date')
                
                if start_date and end_date:
                    # Show years active
                    if hasattr(start_date, 'year') and hasattr(end_date, 'year'):
                        years = list(range(start_date.year, end_date.year + 1))
                        year_counts = [1] * len(years)  # Simplified - just show active years
                        
                        fig.add_trace(
                            go.Bar(x=years, y=year_counts, name='Years Active',
                                  marker_color='#9B59B6'),
                            row=2, col=2
                        )
            
            fig.update_layout(
                title='ARGO Data Summary Dashboard',
                height=800,
                showlegend=False,
                template='plotly_white'
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating summary dashboard: {e}")
            return go.Figure()
    
    def create_geographic_coverage_plot(self, data: pd.DataFrame) -> go.Figure:
        """Create geographic coverage plot."""
        try:
            fig = go.Figure()
            
            # Add scatter plot of float locations
            if 'institution' in data.columns:
                for institution in data['institution'].unique():
                    inst_data = data[data['institution'] == institution]
                    fig.add_trace(go.Scattergeo(
                        lon=inst_data['longitude'],
                        lat=inst_data['latitude'],
                        text=inst_data['float_id'],
                        mode='markers',
                        name=institution,
                        marker=dict(
                            size=8,
                            color=self.institutions.get(institution, self.institutions['default'])
                        )
                    ))
            else:
                fig.add_trace(go.Scattergeo(
                    lon=data['longitude'],
                    lat=data['latitude'],
                    text=data['float_id'],
                    mode='markers',
                    name='ARGO Floats',
                    marker=dict(size=8, color='#3498DB')
                ))
            
            fig.update_layout(
                title='Geographic Coverage of ARGO Floats',
                geo=dict(
                    projection_type='mercator',
                    showland=True,
                    landcolor='rgb(243, 243, 243)',
                    coastlinecolor='rgb(204, 204, 204)',
                ),
                height=600
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating geographic coverage plot: {e}")
            return go.Figure()
    
    def plot_temperature_depth_profile(self, data: pd.DataFrame) -> go.Figure:
        """Create temperature-depth profile plot - alias for existing method."""
        return self.create_temperature_depth_profile(data)
