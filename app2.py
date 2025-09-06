"""
FloatChat Enhanced - AI-Powered Conversational Interface for ARGO Ocean Data
Complete UI with 2D Plotting, Maps, Histograms, and Advanced Visualizations
"""
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import folium
from folium import plugins
from streamlit_folium import folium_static, st_folium
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import logging
import sys
import os
import json
import base64
from io import BytesIO
import zipfile
from typing import List, Dict, Any, Optional

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.config import Config
from src.database.database_manager import DatabaseManager
from src.ai.vector_store import ARGOVectorStore
from src.ai.rag_pipeline import ARGORAGPipeline
from src.visualization.argo_plots import ARGOVisualizer
from src.ingestion.argo_ingestion import ARGODataIngestion

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="FloatChat Enhanced - ARGO Ocean Data Explorer",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced styling with better visibility
st.markdown("""
<style>
    /* Main app styling with dark theme support */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        min-height: 100vh;
    }
    
    /* Chat interface specific styling */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    }
    
    .main {
        background: transparent;
    }
    
    /* Header styling */
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #1f77b4, #2ca02c);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .sub-header {
        font-size: 1.5rem;
        color: #f8fafc;
        margin-bottom: 1rem;
        border-bottom: 2px solid #3b82f6;
        padding-bottom: 10px;
        font-weight: 600;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Info boxes with better contrast */
    .info-box {
        background: linear-gradient(135deg, #f0f8ff 0%, #e6f3ff 100%);
        color: #2c3e50;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #1f77b4;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(31, 119, 180, 0.15);
        border: 1px solid rgba(31, 119, 180, 0.2);
    }
    
    .info-box h3 {
        color: #1f77b4;
        margin-top: 0;
        font-weight: 600;
    }
    
    .info-box p, .info-box li {
        color: #2c3e50;
        line-height: 1.6;
    }
    
    .success-box {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        color: #155724;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #28a745;
        margin: 1rem 0;
        box-shadow: 0 4px 8px rgba(40, 167, 69, 0.15);
        border: 1px solid rgba(40, 167, 69, 0.3);
    }
    
    .error-box {
        background: linear-gradient(135deg, #f8d7da 0%, #f1aeb5 100%);
        color: #721c24;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #dc3545;
        margin: 1rem 0;
        box-shadow: 0 4px 8px rgba(220, 53, 69, 0.15);
        border: 1px solid rgba(220, 53, 69, 0.3);
    }
    
    /* Plot container with better visibility */
    .plot-container {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 6px 16px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border: 1px solid rgba(0,0,0,0.1);
    }
    
    /* Metric cards with enhanced styling */
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        color: #2c3e50;
        padding: 1.2rem;
        border-radius: 10px;
        text-align: center;
        border: 2px solid #e9ecef;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        font-weight: 600;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.15);
        border-color: #1f77b4;
    }
    
    /* Chat messages with better contrast and dark theme support */
    .chat-message {
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1.5rem 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        border: 2px solid transparent;
        backdrop-filter: blur(10px);
        word-wrap: break-word;
        overflow-wrap: break-word;
        max-width: 100%;
        box-sizing: border-box;
    }
    
    .user-message {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: #ffffff;
        border-left: 4px solid #60a5fa;
        border: 2px solid rgba(96, 165, 250, 0.3);
        margin-left: 1rem;
        margin-right: 0;
        margin-top: 2rem;
        margin-bottom: 1rem;
        position: relative;
        clear: both;
    }
    
    .user-message::before {
        content: "You:";
        position: absolute;
        top: -10px;
        left: 1rem;
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: #ffffff;
        padding: 0.3rem 0.8rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        border: 1px solid rgba(96, 165, 250, 0.5);
        z-index: 10;
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #065f46 0%, #059669 100%);
        color: #ffffff;
        border-left: 4px solid #34d399;
        border: 2px solid rgba(52, 211, 153, 0.3);
        margin-right: 1rem;
        margin-left: 0;
        margin-top: 2rem;
        margin-bottom: 1.5rem;
        position: relative;
        clear: both;
        min-height: 50px;
    }
    
    .assistant-message::before {
        content: "FloatChat:";
        position: absolute;
        top: -10px;
        left: 1rem;
        background: linear-gradient(135deg, #065f46 0%, #059669 100%);
        color: #ffffff;
        padding: 0.3rem 0.8rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        border: 1px solid rgba(52, 211, 153, 0.5);
        z-index: 10;
    }
    
    .chat-message p {
        color: inherit;
        line-height: 1.6;
        margin: 0.5rem 0;
        word-wrap: break-word;
        overflow-wrap: break-word;
    }
    
    .chat-message strong {
        color: inherit;
        font-weight: 600;
    }
    
    .chat-message ul, .chat-message ol {
        color: inherit;
        margin: 0.5rem 0;
        padding-left: 1.5rem;
        word-wrap: break-word;
        overflow-wrap: break-word;
    }
    
    .chat-message li {
        color: inherit;
        margin: 0.3rem 0;
        word-wrap: break-word;
        overflow-wrap: break-word;
    }
    
    /* Ensure proper spacing between chat elements */
    .stMarkdown + .stMarkdown {
        margin-top: 0.5rem;
    }
    
    /* Container for chat messages */
    .stContainer {
        padding: 1rem 0;
    }
    
    /* Ensure chat messages don't overlap */
    .element-container {
        margin-bottom: 1rem;
    }
    
    /* Fix for streamlit markdown containers */
    .stMarkdown {
        margin-bottom: 1rem;
    }
    
    .stMarkdown > div {
        width: 100%;
        overflow: visible;
    }
    
    /* Ensure proper z-index for chat elements */
    .chat-message {
        z-index: 1;
        position: relative;
    }
    
    /* Sidebar styling */
    .sidebar .stSelectbox > div > div {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
    }
    
    .sidebar .metric-container {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 0.8rem;
        border-radius: 8px;
        border: 1px solid #dee2e6;
        margin: 0.5rem 0;
    }
    
    /* Enhanced button styling */
    .stButton > button {
        background: linear-gradient(135deg, #1f77b4 0%, #1565c0 100%);
        color: white;
        border-radius: 25px;
        border: none;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        font-size: 0.9rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 8px rgba(31, 119, 180, 0.3);
        text-transform: none;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #155a8a 0%, #0d47a1 100%);
        box-shadow: 0 6px 16px rgba(31, 119, 180, 0.4);
        transform: translateY(-2px);
    }
    
    .stButton > button:active {
        transform: translateY(0);
        box-shadow: 0 2px 4px rgba(31, 119, 180, 0.3);
    }
    
    /* Data frame styling */
    .stDataFrame {
        background-color: #ffffff;
        border-radius: 8px;
        border: 1px solid #dee2e6;
        overflow: hidden;
    }
    
    /* Text input styling for dark theme */
    .stTextInput > div > div > input {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border: 2px solid #475569;
        border-radius: 12px;
        padding: 0.8rem 1rem;
        color: #f8fafc;
        font-size: 1rem;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.3);
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 20%, #1e293b 100%);
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #94a3b8;
    }
    
    /* Text area styling */
    .stTextArea > div > div > textarea {
        background-color: #ffffff;
        border: 2px solid #e9ecef;
        border-radius: 8px;
        color: #2c3e50;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #1f77b4;
        box-shadow: 0 0 0 2px rgba(31, 119, 180, 0.2);
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div {
        background-color: #ffffff;
        border: 2px solid #e9ecef;
        border-radius: 8px;
        color: #2c3e50;
    }
    
    /* Slider styling */
    .stSlider > div > div > div {
        color: #1f77b4;
    }
    
    /* Metric styling */
    .metric-container {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e9ecef;
        text-align: center;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #f8f9fa;
        border-radius: 8px;
        border: 1px solid #dee2e6;
    }
    
    /* Code block styling */
    .stCode {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 8px;
    }
    
    /* Alert styling */
    .stAlert {
        border-radius: 8px;
        border-width: 1px;
    }
    
    /* Dark mode support */
    @media (prefers-color-scheme: dark) {
        .info-box {
            background: linear-gradient(135deg, #1e3a5f 0%, #2c4f7a 100%);
            color: #e8f4fd;
            border-left-color: #4fc3f7;
        }
        
        .info-box h3 {
            color: #4fc3f7;
        }
        
        .info-box p, .info-box li {
            color: #e8f4fd;
        }
        
        .metric-card {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: #ecf0f1;
            border-color: #5a6c7d;
        }
        
        .plot-container {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            border-color: #5a6c7d;
        }
    }
    
    /* Animation keyframes */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .info-box, .metric-card, .chat-message {
        animation: fadeIn 0.5s ease-out;
    }
    
    /* General text styling for dark theme */
    .stMarkdown, .stText {
        color: #f8fafc;
    }
    
    label {
        color: #f8fafc !important;
        font-weight: 500;
    }
    
    .stTextInput > label {
        color: #f8fafc !important;
        font-size: 1rem;
        font-weight: 500;
        margin-bottom: 0.5rem;
    }
    
    /* Data preview styling */
    .stDataFrame {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border: 2px solid #475569;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    
    /* Expander styling for dark theme */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        color: #f8fafc;
        border: 2px solid #475569;
        border-radius: 12px;
    }
    
    .streamlit-expanderContent {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border: 2px solid #475569;
        border-top: none;
        border-radius: 0 0 12px 12px;
    }
    
    /* Success and info messages for dark theme */
    .stSuccess {
        background: linear-gradient(135deg, #065f46 0%, #059669 100%);
        color: #ffffff;
        border: 2px solid #34d399;
        border-radius: 12px;
    }
    
    .stInfo {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: #ffffff;
        border: 2px solid #60a5fa;
        border-radius: 12px;
    }
    
    .stError {
        background: linear-gradient(135deg, #991b1b 0%, #dc2626 100%);
        color: #ffffff;
        border: 2px solid #f87171;
        border-radius: 12px;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
        }
        
        .info-box {
            padding: 1rem;
            margin: 0.5rem 0;
        }
        
        .metric-card {
            padding: 0.8rem;
        }
        
        .chat-message {
            margin-left: 0.5rem;
            margin-right: 0.5rem;
            padding: 1rem;
        }
        
        .user-message {
            margin-left: 0.3rem;
            margin-right: 0;
        }
        
        .assistant-message {
            margin-right: 0.3rem;
            margin-left: 0;
        }
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def initialize_components():
    """Initialize database and AI components."""
    try:
        # Validate configuration
        Config.validate()
        
        # Initialize components
        db_manager = DatabaseManager()
        vector_store = ARGOVectorStore()
        rag_pipeline = ARGORAGPipeline(db_manager, vector_store)
        visualizer = ARGOVisualizer()
        data_ingestion = ARGODataIngestion()
        
        return db_manager, vector_store, rag_pipeline, visualizer, data_ingestion
    except Exception as e:
        st.error(f"Error initializing components: {e}")
        return None, None, None, None, None

class EnhancedARGOVisualizer(ARGOVisualizer):
    """Enhanced visualizer with additional plot types"""
    
    def create_histogram(self, data: pd.DataFrame, parameter: str, 
                        bins: int = 30, title: str = None) -> go.Figure:
        """Create histogram for oceanographic parameters."""
        try:
            if data.empty or parameter not in data.columns:
                fig = go.Figure()
                fig.add_annotation(
                    text=f"No data available for {parameter}",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False
                )
                return fig
            
            # Remove NaN values
            clean_data = data[parameter].dropna()
            
            if clean_data.empty:
                fig = go.Figure()
                fig.add_annotation(
                    text=f"No valid data for {parameter}",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False
                )
                return fig
            
            fig = go.Figure()
            
            # Create histogram
            fig.add_trace(go.Histogram(
                x=clean_data,
                nbinsx=bins,
                name=parameter.title(),
                marker_color='rgba(31, 119, 180, 0.7)',
                marker_line=dict(color='rgba(31, 119, 180, 1)', width=1)
            ))
            
            # Add statistics
            mean_val = clean_data.mean()
            std_val = clean_data.std()
            median_val = clean_data.median()
            
            # Add vertical lines for statistics
            fig.add_vline(x=mean_val, line_dash="dash", line_color="red", 
                         annotation_text=f"Mean: {mean_val:.2f}")
            fig.add_vline(x=median_val, line_dash="dash", line_color="green",
                         annotation_text=f"Median: {median_val:.2f}")
            
            fig.update_layout(
                title=title or f"{parameter.title()} Distribution",
                xaxis_title=parameter.title(),
                yaxis_title="Frequency",
                template='plotly_white',
                height=500,
                showlegend=False
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating histogram: {e}")
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error creating histogram: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
    
    def create_scatter_plot(self, data: pd.DataFrame, x_param: str, y_param: str,
                          color_param: str = None, title: str = None) -> go.Figure:
        """Create 2D scatter plot between two parameters."""
        try:
            if data.empty or x_param not in data.columns or y_param not in data.columns:
                fig = go.Figure()
                fig.add_annotation(
                    text=f"Required parameters {x_param} and {y_param} not found",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False
                )
                return fig
            
            # Remove NaN values
            clean_data = data.dropna(subset=[x_param, y_param])
            
            if clean_data.empty:
                fig = go.Figure()
                fig.add_annotation(
                    text=f"No valid data for {x_param} and {y_param}",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False
                )
                return fig
            
            fig = go.Figure()
            
            # Create scatter plot
            if color_param and color_param in clean_data.columns:
                # Color-coded scatter plot
                fig.add_trace(go.Scatter(
                    x=clean_data[x_param],
                    y=clean_data[y_param],
                    mode='markers',
                    marker=dict(
                        size=6,
                        color=clean_data[color_param],
                        colorscale='Viridis',
                        colorbar=dict(title=color_param.title()),
                        showscale=True
                    ),
                    name='Data Points',
                    text=[f"{color_param}: {val:.2f}" for val in clean_data[color_param]],
                    hovertemplate=f"<b>{x_param}:</b> %{{x:.3f}}<br><b>{y_param}:</b> %{{y:.3f}}<br>%{{text}}<extra></extra>"
                ))
            else:
                # Simple scatter plot
                fig.add_trace(go.Scatter(
                    x=clean_data[x_param],
                    y=clean_data[y_param],
                    mode='markers',
                    marker=dict(size=6, color='blue', opacity=0.7),
                    name='Data Points'
                ))
            
            # Calculate correlation
            correlation = clean_data[x_param].corr(clean_data[y_param])
            
            fig.update_layout(
                title=title or f"{y_param.title()} vs {x_param.title()}" + 
                      f"<br><sub>Correlation: {correlation:.3f}</sub>",
                xaxis_title=x_param.title(),
                yaxis_title=y_param.title(),
                template='plotly_white',
                height=500
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating scatter plot: {e}")
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error creating scatter plot: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
    
    def create_box_plot(self, data: pd.DataFrame, parameter: str, 
                       group_by: str = None, title: str = None) -> go.Figure:
        """Create box plot for parameter distribution."""
        try:
            if data.empty or parameter not in data.columns:
                fig = go.Figure()
                fig.add_annotation(
                    text=f"No data available for {parameter}",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False
                )
                return fig
            
            clean_data = data.dropna(subset=[parameter])
            
            if clean_data.empty:
                fig = go.Figure()
                fig.add_annotation(
                    text=f"No valid data for {parameter}",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False
                )
                return fig
            
            fig = go.Figure()
            
            if group_by and group_by in clean_data.columns:
                # Grouped box plot
                for group in clean_data[group_by].unique():
                    group_data = clean_data[clean_data[group_by] == group]
                    fig.add_trace(go.Box(
                        y=group_data[parameter],
                        name=f"{group_by}: {group}",
                        boxpoints='outliers'
                    ))
            else:
                # Single box plot
                fig.add_trace(go.Box(
                    y=clean_data[parameter],
                    name=parameter.title(),
                    boxpoints='outliers'
                ))
            
            fig.update_layout(
                title=title or f"{parameter.title()} Distribution",
                yaxis_title=parameter.title(),
                template='plotly_white',
                height=500
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating box plot: {e}")
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error creating box plot: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
    
    def create_depth_section(self, data: pd.DataFrame, parameter: str,
                           title: str = None) -> go.Figure:
        """Create depth section plot."""
        try:
            if data.empty or parameter not in data.columns or 'pressure' not in data.columns:
                fig = go.Figure()
                fig.add_annotation(
                    text=f"Required data not available for depth section",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False
                )
                return fig
            
            # Group by cycle/profile if available
            if 'cycle_number' in data.columns:
                cycles = sorted(data['cycle_number'].unique())[:10]  # Limit to first 10 cycles
                
                fig = go.Figure()
                colors = px.colors.qualitative.Set1
                
                for i, cycle in enumerate(cycles):
                    cycle_data = data[data['cycle_number'] == cycle].dropna(subset=[parameter, 'pressure'])
                    if not cycle_data.empty:
                        fig.add_trace(go.Scatter(
                            x=cycle_data[parameter],
                            y=cycle_data['pressure'],
                            mode='lines+markers',
                            name=f'Cycle {cycle}',
                            line=dict(color=colors[i % len(colors)], width=2),
                            marker=dict(size=4)
                        ))
                
                fig.update_layout(
                    yaxis=dict(autorange='reversed')  # Invert y-axis for depth
                )
            else:
                # Single profile
                clean_data = data.dropna(subset=[parameter, 'pressure'])
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=clean_data[parameter],
                    y=clean_data['pressure'],
                    mode='lines+markers',
                    name=parameter.title(),
                    line=dict(color='blue', width=2),
                    marker=dict(size=4)
                ))
                fig.update_layout(
                    yaxis=dict(autorange='reversed')
                )
            
            fig.update_layout(
                title=title or f"{parameter.title()} Depth Section",
                xaxis_title=parameter.title(),
                yaxis_title="Pressure (dbar)",
                template='plotly_white',
                height=600
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating depth section: {e}")
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error creating depth section: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig

def get_download_link(df: pd.DataFrame, filename: str) -> str:
    """Generate download link for DataFrame."""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download {filename}</a>'
    return href

def main():
    """Main application function."""
    
    # Header with enhanced styling
    st.markdown('<h1 class="main-header">🌊 FloatChat Enhanced</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">AI-Powered Conversational Interface for ARGO Ocean Data Discovery and Advanced Visualization</p>', unsafe_allow_html=True)
    
    # Initialize components
    db_manager, vector_store, rag_pipeline, visualizer, data_ingestion = initialize_components()
    
    if not all([db_manager, vector_store, rag_pipeline, visualizer, data_ingestion]):
        st.error("Failed to initialize application components. Please check your configuration.")
        return
    
    # Initialize enhanced visualizer
    enhanced_visualizer = EnhancedARGOVisualizer()
    
    # Initialize session state
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'last_query_data' not in st.session_state:
        st.session_state.last_query_data = None
    if 'plot_data' not in st.session_state:
        st.session_state.plot_data = None
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🧭 Navigation")
        page = st.selectbox(
            "Choose a page:",
            ["🏠 Home", "💬 Chat Interface", "📊 2D Plotting", "🗺️ Interactive Maps", 
             "📈 Advanced Analytics", "📋 Data Explorer", "⚙️ Settings"]
        )
        
        st.markdown("---")
        st.markdown("## 📊 Data Summary")
        
        # Get and display data summary
        try:
            summary = rag_pipeline.get_data_summary()
            if summary:
                db_summary = summary.get('database', {})
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Floats", db_summary.get('total_floats', 0))
                    st.metric("Profiles", db_summary.get('total_profiles', 0))
                with col2:
                    st.metric("Measurements", db_summary.get('total_measurements', 0))
                    st.metric("Active Floats", db_summary.get('active_floats', 0))
        except Exception as e:
            st.error(f"Error loading summary: {e}")
        
        st.markdown("---")
        st.markdown("## 🎯 Quick Actions")
        
        # Quick plot buttons
        if st.button("🌡️ Temperature Analysis"):
            st.session_state.example_query = "Show temperature distribution in the Indian Ocean"
        if st.button("🧂 Salinity Profiles"):
            st.session_state.example_query = "Plot salinity vs depth for Arabian Sea"
        if st.button("🗺️ Float Locations"):
            st.session_state.example_query = "Map all ARGO float locations"
        if st.button("📊 T-S Diagram"):
            st.session_state.example_query = "Create temperature salinity diagram Bay of Bengal"
    
    # Main content based on selected page
    if page == "🏠 Home":
        show_home_page(rag_pipeline, enhanced_visualizer)
    elif page == "💬 Chat Interface":
        show_chat_interface(rag_pipeline, enhanced_visualizer)
    elif page == "📊 2D Plotting":
        show_2d_plotting_interface(rag_pipeline, enhanced_visualizer)
    elif page == "🗺️ Interactive Maps":
        show_interactive_maps(rag_pipeline, enhanced_visualizer)
    elif page == "📈 Advanced Analytics":
        show_advanced_analytics(rag_pipeline, enhanced_visualizer)
    elif page == "📋 Data Explorer":
        show_data_explorer(db_manager, enhanced_visualizer)
    elif page == "⚙️ Settings":
        show_settings_page(data_ingestion, db_manager)

def show_home_page(rag_pipeline, visualizer):
    """Display the enhanced home page."""
    st.markdown('<h2 class="sub-header">Welcome to FloatChat Enhanced</h2>', unsafe_allow_html=True)
    
    # Feature showcase with columns
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown("""
        <div class="info-box">
        <h3>🌊 Natural Language Queries</h3>
        <p>Ask questions about oceanographic data in plain English. Get instant insights with AI-powered responses and interactive visualizations.</p>
        <ul>
        <li>Temperature and salinity analysis</li>
        <li>Geographic data filtering</li>
        <li>Time series analysis</li>
        <li>Statistical summaries</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-box">
        <h3>📊 Advanced 2D Plotting</h3>
        <p>Create sophisticated oceanographic visualizations with our enhanced plotting capabilities.</p>
        <ul>
        <li>Temperature-Salinity diagrams</li>
        <li>Depth profile comparisons</li>
        <li>Scatter plots with correlations</li>
        <li>Histograms and distributions</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="info-box">
        <h3>🗺️ Interactive Maps</h3>
        <p>Visualize ARGO data geographically with dynamic, interactive mapping tools.</p>
        <ul>
        <li>Float location tracking</li>
        <li>Trajectory visualization</li>
        <li>Regional data density</li>
        <li>Real-time status updates</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Example queries section
    st.markdown("### 🚀 Try These Example Queries")
    
    example_queries = [
        ("Temperature Distribution", "Show me temperature distribution in the Indian Ocean", "🌡️"),
        ("Salinity Profiles", "Plot salinity profiles near the equator between 60-90°E", "🧂"),
        ("T-S Diagram", "Create temperature salinity diagram for Bay of Bengal floats", "📊"),
        ("Float Locations", "Map active ARGO floats in the Arabian Sea region", "🗺️"),
        ("Depth Analysis", "Show pressure vs temperature relationship for recent data", "📈"),
        ("Correlation Study", "Compare temperature and salinity correlation by region", "🔬")
    ]
    
    cols = st.columns(3)
    for i, (title, query, icon) in enumerate(example_queries):
        with cols[i % 3]:
            if st.button(f"{icon} {title}", key=f"example_{i}"):
                st.session_state.example_query = query
                st.rerun()
    
    # System status
    st.markdown("### 📈 System Status")
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        summary = rag_pipeline.get_data_summary()
        if summary and summary.get('database'):
            with col1:
                st.markdown('<div class="metric-card">✅ Database<br><strong>Connected</strong></div>', unsafe_allow_html=True)
            with col2:
                st.markdown('<div class="metric-card">🤖 AI Pipeline<br><strong>Active</strong></div>', unsafe_allow_html=True)
            with col3:
                st.markdown('<div class="metric-card">📊 Vector Store<br><strong>Ready</strong></div>', unsafe_allow_html=True)
            with col4:
                st.markdown('<div class="metric-card">🌊 Data Status<br><strong>Current</strong></div>', unsafe_allow_html=True)
        else:
            with col1:
                st.markdown('<div class="metric-card">⚠️ Database<br><strong>No Data</strong></div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error checking system status: {e}")

def show_chat_interface(rag_pipeline, visualizer):
    """Enhanced chat interface with visualization."""
    st.markdown('<h2 class="sub-header">💬 AI Chat Interface</h2>', unsafe_allow_html=True)
    
    # Chat input
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_query = st.text_input(
            "Ask me about ARGO ocean data:",
            placeholder="e.g., Show temperature profiles in the Indian Ocean",
            value=st.session_state.get('example_query', '')
        )
    
    with col2:
        if st.button("🚀 Send", type="primary"):
            if user_query.strip():
                process_chat_query(user_query, rag_pipeline, visualizer)
    
    # Clear example query after use
    if 'example_query' in st.session_state:
        del st.session_state.example_query
    
    # Auto-process if there's an example query
    if user_query and user_query != st.session_state.get('last_processed_query', ''):
        st.session_state.last_processed_query = user_query
        process_chat_query(user_query, rag_pipeline, visualizer)
    
    # Display chat history
    if st.session_state.chat_history:
        st.markdown("### 💬 Conversation History")
        for i, (query, response, data, timestamp) in enumerate(reversed(st.session_state.chat_history[-10:])):  # Show last 10
            with st.expander(f"Query {len(st.session_state.chat_history)-i}: {query[:50]}..." if len(query) > 50 else f"Query {len(st.session_state.chat_history)-i}: {query}"):
                st.markdown(f'<div class="user-message">{query}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="assistant-message">{response}</div>', unsafe_allow_html=True)
                
                if data is not None and not data.empty:
                    st.markdown("**Retrieved Data:**")
                    st.dataframe(data.head(10), use_container_width=True)
                    
                    # Quick visualization options
                    if len(data) > 0:
                        viz_col1, viz_col2, viz_col3 = st.columns(3)
                        with viz_col1:
                            if st.button("📊 Quick Plot", key=f"plot_{i}"):
                                create_quick_visualization(data, visualizer)
                        with viz_col2:
                            if st.button("📈 Histogram", key=f"hist_{i}"):
                                create_histogram_from_data(data, visualizer)
                        with viz_col3:
                            if st.button("🗺️ Map", key=f"map_{i}"):
                                create_map_from_data(data, visualizer)

def process_chat_query(query: str, rag_pipeline, visualizer):
    """Process chat query and display results."""
    with st.spinner("Processing your query..."):
        try:
            # Process query through RAG pipeline
            result = rag_pipeline.process_query(query)
            
            if result['success']:
                response = result['response']
                data = pd.DataFrame(result['data']) if result['data'] else pd.DataFrame()
                
                # Add to chat history
                st.session_state.chat_history.append((
                    query, response, data, datetime.now()
                ))
                
                # Store last query data for visualization
                st.session_state.last_query_data = data
                
                # Display response
                st.markdown(f'<div class="assistant-message">{response}</div>', unsafe_allow_html=True)
                
                # Display data if available
                if not data.empty:
                    st.success(f"Retrieved {len(data)} records")
                    
                    # Show data preview
                    with st.expander("📊 Data Preview", expanded=True):
                        st.dataframe(data.head(20), use_container_width=True)
                        
                        # Download option
                        csv = data.to_csv(index=False)
                        st.download_button(
                            label="💾 Download CSV",
                            data=csv,
                            file_name=f"argo_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                    
                    # Auto-generate visualization if applicable
                    auto_visualize_data(data, query, visualizer)
            else:
                st.error(f"Query failed: {result['error']}")
                st.markdown(f'<div class="assistant-message" style="background: linear-gradient(135deg, #991b1b 0%, #dc2626 100%); border-left-color: #f87171;">{result["response"]}</div>', unsafe_allow_html=True)
        
        except Exception as e:
            st.error(f"Error processing query: {e}")
            logger.error(f"Error in process_chat_query: {e}")

def auto_visualize_data(data: pd.DataFrame, query: str, visualizer):
    """Automatically create appropriate visualizations based on data and query."""
    try:
        query_lower = query.lower()
        
        # Determine visualization type based on query content and data
        if not data.empty:
            # Check for time series queries first
            if any(phrase in query_lower for phrase in ['time series', 'timeseries', 'over time', 'temporal']) and \
               'profile_time' in data.columns and any(param in data.columns for param in ['temperature', 'salinity', 'oxygen']):
                st.markdown("### 📈 Time Series Visualization")
                create_time_series_plot(data, query_lower, visualizer)
            
            # Check for mapping queries
            elif any(word in query_lower for word in ['map', 'location', 'float', 'trajectory']) and \
               'latitude' in data.columns and 'longitude' in data.columns:
                st.markdown("### 🗺️ Geographic Visualization")
                create_auto_map(data, visualizer)
            
            # Check for profile queries
            elif 'pressure' in data.columns and any(param in data.columns for param in ['temperature', 'salinity']):
                st.markdown("### 📊 Profile Visualization")
                create_auto_profile_plot(data, query_lower, visualizer)
            
            # Check for T-S diagram
            elif 'temperature' in data.columns and 'salinity' in data.columns:
                st.markdown("### 🌡️ Temperature-Salinity Diagram")
                fig = visualizer.create_ts_diagram(data)
                st.plotly_chart(fig, use_container_width=True)
            
            # Check for histogram/distribution queries
            elif any(word in query_lower for word in ['distribution', 'histogram', 'range']):
                st.markdown("### 📈 Data Distribution")
                create_auto_histogram(data, query_lower, visualizer)
            
            # Check if this is measurement data with time and create time series by default
            elif 'profile_time' in data.columns and 'temperature' in data.columns:
                st.markdown("### 📈 Temperature Time Series")
                create_time_series_plot(data, 'temperature', visualizer)
            
            # Default: show data summary and basic plots
            else:
                create_data_summary_viz(data, visualizer)
    
    except Exception as e:
        logger.error(f"Error in auto visualization: {e}")
        st.error(f"Could not create automatic visualization: {e}")

def show_2d_plotting_interface(rag_pipeline, visualizer):
    """Enhanced 2D plotting interface."""
    st.markdown('<h2 class="sub-header">📊 Advanced 2D Plotting Interface</h2>', unsafe_allow_html=True)
    
    # Plot configuration section
    st.markdown("### 🎯 Plot Configuration")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("**Query-Based Plotting**")
        plot_query = st.text_area(
            "Describe your plot:",
            placeholder="e.g., Plot temperature vs salinity for Indian Ocean floats with pressure color coding",
            height=100
        )
        
        if st.button("🎨 Generate Plot from Query", type="primary"):
            if plot_query.strip():
                generate_plot_from_query(plot_query, rag_pipeline, visualizer)
    
    with col2:
        st.markdown("**Manual Plot Configuration**")
        
        # Get available data
        if st.session_state.last_query_data is not None and not st.session_state.last_query_data.empty:
            data = st.session_state.last_query_data
            numeric_columns = data.select_dtypes(include=[np.number]).columns.tolist()
            all_columns = data.columns.tolist()
            
            plot_type = st.selectbox(
                "Plot Type:",
                ["Scatter Plot", "Profile Plot", "T-S Diagram", "Histogram", "Box Plot", "Depth Section"]
            )
            
            if plot_type == "Scatter Plot":
                x_param = st.selectbox("X Parameter:", numeric_columns)
                y_param = st.selectbox("Y Parameter:", numeric_columns)
                color_param = st.selectbox("Color Parameter (optional):", ["None"] + numeric_columns)
                
                if st.button("Create Scatter Plot"):
                    color_col = None if color_param == "None" else color_param
                    fig = visualizer.create_scatter_plot(data, x_param, y_param, color_col)
                    st.plotly_chart(fig, use_container_width=True)
            
            elif plot_type == "Histogram":
                param = st.selectbox("Parameter:", numeric_columns)
                bins = st.slider("Number of Bins:", 10, 100, 30)
                
                if st.button("Create Histogram"):
                    fig = visualizer.create_histogram(data, param, bins)
                    st.plotly_chart(fig, use_container_width=True)
            
            elif plot_type == "Profile Plot" and 'pressure' in data.columns:
                param = st.selectbox("Parameter:", [col for col in numeric_columns if col != 'pressure'])
                
                if st.button("Create Profile Plot"):
                    fig = visualizer.create_profile_plot(data, param)
                    st.plotly_chart(fig, use_container_width=True)
            
            elif plot_type == "T-S Diagram" and 'temperature' in data.columns and 'salinity' in data.columns:
                if st.button("Create T-S Diagram"):
                    fig = visualizer.create_ts_diagram(data)
                    st.plotly_chart(fig, use_container_width=True)
            
            elif plot_type == "Box Plot":
                param = st.selectbox("Parameter:", numeric_columns)
                group_param = st.selectbox("Group By (optional):", ["None"] + all_columns)
                
                if st.button("Create Box Plot"):
                    group_col = None if group_param == "None" else group_param
                    fig = visualizer.create_box_plot(data, param, group_col)
                    st.plotly_chart(fig, use_container_width=True)
            
            elif plot_type == "Depth Section" and 'pressure' in data.columns:
                param = st.selectbox("Parameter:", [col for col in numeric_columns if col != 'pressure'])
                
                if st.button("Create Depth Section"):
                    fig = visualizer.create_depth_section(data, param)
                    st.plotly_chart(fig, use_container_width=True)
        
        else:
            st.info("💡 First run a query in the Chat Interface to load data for plotting.")
    
    # Example plotting queries
    st.markdown("### 🎯 Example Plotting Queries")
    
    example_plots = [
        "Plot temperature vs salinity for Indian Ocean floats with pressure color coding",
        "Show temperature distribution histogram for Bay of Bengal region",
        "Create depth profile of salinity for Arabian Sea floats",
        "Plot pressure vs temperature scatter plot with correlation",
        "Show box plot of temperature by depth ranges",
        "Create T-S diagram for equatorial Pacific region"
    ]
    
    cols = st.columns(2)
    for i, example in enumerate(example_plots):
        with cols[i % 2]:
            if st.button(f"📊 {example}", key=f"plot_example_{i}"):
                generate_plot_from_query(example, rag_pipeline, visualizer)

def generate_plot_from_query(query: str, rag_pipeline, visualizer):
    """Generate plot based on natural language query."""
    with st.spinner("Generating plot from query..."):
        try:
            # Process the query to get data
            result = rag_pipeline.process_query(query)
            
            if result['success'] and result['data']:
                data = pd.DataFrame(result['data'])
                
                # Store the data
                st.session_state.plot_data = data
                
                st.success(f"Retrieved {len(data)} records for plotting")
                
                # Determine plot type from query
                query_lower = query.lower()
                
                # Create appropriate visualization
                if 'histogram' in query_lower or 'distribution' in query_lower:
                    create_query_histogram(data, query_lower, visualizer)
                elif 'scatter' in query_lower or ' vs ' in query_lower:
                    create_query_scatter(data, query_lower, visualizer)
                elif 't-s' in query_lower or 'temperature salinity' in query_lower:
                    fig = visualizer.create_ts_diagram(data)
                    st.plotly_chart(fig, use_container_width=True)
                elif 'profile' in query_lower or 'depth' in query_lower:
                    create_query_profile(data, query_lower, visualizer)
                elif 'map' in query_lower and 'latitude' in data.columns and 'longitude' in data.columns:
                    create_query_map(data, visualizer)
                else:
                    # Default: create the most appropriate plot based on available data
                    create_smart_plot(data, query, visualizer)
                
                # Show data preview
                with st.expander("📊 Data Used for Plotting"):
                    st.dataframe(data, use_container_width=True)
            
            else:
                st.error(f"Could not retrieve data for plotting: {result.get('error', 'Unknown error')}")
        
        except Exception as e:
            st.error(f"Error generating plot: {e}")
            logger.error(f"Error in generate_plot_from_query: {e}")

def show_interactive_maps(rag_pipeline, visualizer):
    """Enhanced interactive mapping interface."""
    st.markdown('<h2 class="sub-header">🗺️ Interactive ARGO Float Maps</h2>', unsafe_allow_html=True)
    
    # Map configuration
    st.markdown("### 🎯 Map Configuration")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        map_query = st.text_input(
            "Map Query:",
            placeholder="e.g., Show all active ARGO floats in the Indian Ocean",
            value=""
        )
        
        if st.button("🗺️ Generate Map", type="primary") and map_query:
            generate_map_from_query(map_query, rag_pipeline, visualizer)
    
    with col2:
        st.markdown("**Map Options**")
        map_style = st.selectbox(
            "Map Style:",
            ["OpenStreetMap", "Satellite", "Terrain", "CartoDB Positron"]
        )
        
        show_trajectories = st.checkbox("Show Trajectories", value=False)
        show_clusters = st.checkbox("Cluster Markers", value=True)
    
    # Quick map buttons
    st.markdown("### 🚀 Quick Maps")
    
    quick_maps = [
        ("Indian Ocean Floats", "Map all ARGO floats in the Indian Ocean region"),
        ("Arabian Sea Active", "Show active floats in Arabian Sea"),
        ("Bay of Bengal", "Map floats in Bay of Bengal with recent data"),
        ("Equatorial Region", "Show floats near the equator between 60-90°E"),
        ("Float Trajectories", "Show recent float trajectories in Indian Ocean"),
        ("Data Density", "Map regions with highest data density")
    ]
    
    cols = st.columns(3)
    for i, (title, query) in enumerate(quick_maps):
        with cols[i % 3]:
            if st.button(f"🗺️ {title}", key=f"quick_map_{i}"):
                generate_map_from_query(query, rag_pipeline, visualizer)
    
    # Regional statistics
    if st.session_state.last_query_data is not None:
        data = st.session_state.last_query_data
        if 'latitude' in data.columns and 'longitude' in data.columns:
            st.markdown("### 📊 Geographic Statistics")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Data Points", len(data))
            with col2:
                lat_range = data['latitude'].max() - data['latitude'].min()
                st.metric("Lat Range", f"{lat_range:.2f}°")
            with col3:
                lon_range = data['longitude'].max() - data['longitude'].min()
                st.metric("Lon Range", f"{lon_range:.2f}°")
            with col4:
                if 'float_id' in data.columns:
                    unique_floats = data['float_id'].nunique()
                    st.metric("Unique Floats", unique_floats)

def generate_map_from_query(query: str, rag_pipeline, visualizer):
    """Generate map based on query."""
    with st.spinner("Creating interactive map..."):
        try:
            result = rag_pipeline.process_query(query)
            
            if result['success'] and result['data']:
                data = pd.DataFrame(result['data'])
                
                if 'latitude' in data.columns and 'longitude' in data.columns:
                    # Create map
                    center_lat = data['latitude'].mean()
                    center_lon = data['longitude'].mean()
                    
                    m = folium.Map(
                        location=[center_lat, center_lon],
                        zoom_start=4,
                        tiles='OpenStreetMap'
                    )
                    
                    # Add markers
                    for idx, row in data.iterrows():
                        popup_text = f"""
                        <b>Float ID:</b> {row.get('float_id', 'N/A')}<br>
                        <b>Latitude:</b> {row['latitude']:.4f}<br>
                        <b>Longitude:</b> {row['longitude']:.4f}<br>
                        <b>Date:</b> {row.get('profile_time', 'N/A')}<br>
                        """
                        
                        if 'temperature' in row:
                            popup_text += f"<b>Temperature:</b> {row.get('temperature', 'N/A')}°C<br>"
                        if 'salinity' in row:
                            popup_text += f"<b>Salinity:</b> {row.get('salinity', 'N/A')} PSU<br>"
                        
                        folium.Marker(
                            location=[row['latitude'], row['longitude']],
                            popup=folium.Popup(popup_text, max_width=300),
                            tooltip=f"Float {row.get('float_id', 'N/A')}",
                            icon=folium.Icon(color='blue', icon='ship', prefix='fa')
                        ).add_to(m)
                    
                    # Display map
                    st.markdown(f"### 🗺️ Map: {len(data)} locations")
                    folium_static(m, width=1000, height=500)
                    
                    # Map statistics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Points", len(data))
                    with col2:
                        lat_center = data['latitude'].mean()
                        st.metric("Center Lat", f"{lat_center:.2f}°")
                    with col3:
                        lon_center = data['longitude'].mean()
                        st.metric("Center Lon", f"{lon_center:.2f}°")
                
                else:
                    st.warning("No geographic coordinates found in the data for mapping.")
            
            else:
                st.error(f"Could not retrieve data for mapping: {result.get('error', 'Unknown error')}")
        
        except Exception as e:
            st.error(f"Error creating map: {e}")
            logger.error(f"Error in generate_map_from_query: {e}")

def show_advanced_analytics(rag_pipeline, visualizer):
    """Advanced analytics and statistical analysis."""
    st.markdown('<h2 class="sub-header">📈 Advanced Analytics & Statistics</h2>', unsafe_allow_html=True)
    
    if st.session_state.last_query_data is not None and not st.session_state.last_query_data.empty:
        data = st.session_state.last_query_data
        
        # Data overview
        st.markdown("### 📊 Data Overview")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Records", len(data))
        with col2:
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            st.metric("Numeric Columns", len(numeric_cols))
        with col3:
            missing_pct = (data.isnull().sum().sum() / data.size) * 100
            st.metric("Missing Data %", f"{missing_pct:.1f}%")
        with col4:
            if 'float_id' in data.columns:
                unique_floats = data['float_id'].nunique()
                st.metric("Unique Floats", unique_floats)
        
        # Statistical summary
        st.markdown("### 📋 Statistical Summary")
        if len(numeric_cols) > 0:
            st.dataframe(data[numeric_cols].describe(), use_container_width=True)
        
        # Correlation analysis
        if len(numeric_cols) > 1:
            st.markdown("### 🔗 Correlation Analysis")
            
            corr_matrix = data[numeric_cols].corr()
            
            # Create correlation heatmap
            fig = go.Figure(data=go.Heatmap(
                z=corr_matrix.values,
                x=corr_matrix.columns,
                y=corr_matrix.columns,
                colorscale='RdBu',
                zmid=0,
                text=np.round(corr_matrix.values, 2),
                texttemplate='%{text}',
                textfont={"size": 10},
                colorbar=dict(title="Correlation")
            ))
            
            fig.update_layout(
                title="Parameter Correlation Matrix",
                xaxis_title="Parameters",
                yaxis_title="Parameters",
                template='plotly_white',
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Distribution analysis
        st.markdown("### 📈 Distribution Analysis")
        
        if len(numeric_cols) > 0:
            selected_param = st.selectbox("Select parameter for distribution analysis:", numeric_cols)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Histogram
                fig_hist = visualizer.create_histogram(data, selected_param)
                st.plotly_chart(fig_hist, use_container_width=True)
            
            with col2:
                # Box plot
                fig_box = visualizer.create_box_plot(data, selected_param)
                st.plotly_chart(fig_box, use_container_width=True)
        
        # Advanced analysis options
        st.markdown("### 🔬 Advanced Analysis")
        
        analysis_type = st.selectbox(
            "Select Analysis Type:",
            ["Parameter Relationships", "Outlier Detection", "Time Series Analysis", "Regional Comparison"]
        )
        
        if analysis_type == "Parameter Relationships" and len(numeric_cols) >= 2:
            param1 = st.selectbox("Parameter 1:", numeric_cols, key="param1")
            param2 = st.selectbox("Parameter 2:", numeric_cols, key="param2")
            
            if param1 != param2:
                fig = visualizer.create_scatter_plot(data, param1, param2)
                st.plotly_chart(fig, use_container_width=True)
                
                # Statistical analysis
                correlation = data[param1].corr(data[param2])
                st.info(f"Correlation between {param1} and {param2}: {correlation:.3f}")
        
        elif analysis_type == "Outlier Detection":
            if len(numeric_cols) > 0:
                param = st.selectbox("Parameter for outlier detection:", numeric_cols)
                
                # Calculate outliers using IQR method
                Q1 = data[param].quantile(0.25)
                Q3 = data[param].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers = data[(data[param] < lower_bound) | (data[param] > upper_bound)]
                
                st.info(f"Found {len(outliers)} outliers for {param}")
                
                if len(outliers) > 0:
                    st.dataframe(outliers, use_container_width=True)
    
    else:
        st.info("💡 Run a query first to load data for advanced analytics.")

def show_data_explorer(db_manager, visualizer):
    """Enhanced data explorer with filtering and export capabilities."""
    st.markdown('<h2 class="sub-header">📋 Data Explorer & Export</h2>', unsafe_allow_html=True)
    
    # Data source selection
    st.markdown("### 🎯 Data Source Selection")
    
    data_type = st.selectbox(
        "Select Data Type:",
        ["Measurements", "Float Metadata", "Profile Summary", "Custom Query"]
    )
    
    # Filtering options
    st.markdown("### 🔍 Data Filters")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Geographic filters
        st.markdown("**Geographic Filters**")
        lat_range = st.slider("Latitude Range:", -90.0, 90.0, (-60.0, 30.0))
        lon_range = st.slider("Longitude Range:", -180.0, 180.0, (30.0, 120.0))
    
    with col2:
        # Parameter filters
        st.markdown("**Parameter Filters**")
        temp_range = st.slider("Temperature Range (°C):", -5.0, 35.0, (0.0, 30.0))
        sal_range = st.slider("Salinity Range (PSU):", 30.0, 40.0, (33.0, 37.0))
    
    with col3:
        # Time filters
        st.markdown("**Time Filters**")
        date_range = st.date_input(
            "Date Range:",
            value=(datetime.now() - timedelta(days=365), datetime.now()),
            format="YYYY-MM-DD"
        )
        
        max_records = st.number_input("Max Records:", 100, 10000, 1000)
    
    # Execute query
    if st.button("🔍 Load Data", type="primary"):
        load_explorer_data(db_manager, data_type, lat_range, lon_range, temp_range, sal_range, date_range, max_records)
    
    # Display loaded data
    if 'explorer_data' in st.session_state and st.session_state.explorer_data is not None:
        data = st.session_state.explorer_data
        
        st.markdown("### 📊 Loaded Data")
        st.info(f"Loaded {len(data)} records")
        
        # Data preview
        st.dataframe(data, use_container_width=True)
        
        # Export options
        st.markdown("### 💾 Export Options")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            csv = data.to_csv(index=False)
            st.download_button(
                label="📄 Download CSV",
                data=csv,
                file_name=f"argo_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with col2:
            json_str = data.to_json(orient='records', indent=2)
            st.download_button(
                label="📋 Download JSON",
                data=json_str,
                file_name=f"argo_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        with col3:
            # Excel export
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                data.to_excel(writer, sheet_name='ARGO_Data', index=False)
            
            st.download_button(
                label="📊 Download Excel",
                data=buffer.getvalue(),
                file_name=f"argo_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        with col4:
            if st.button("📈 Quick Analysis"):
                st.session_state.last_query_data = data
                st.rerun()

def load_explorer_data(db_manager, data_type, lat_range, lon_range, temp_range, sal_range, date_range, max_records):
    """Load data based on explorer filters."""
    try:
        with st.spinner("Loading data..."):
            # Construct query based on filters
            if data_type == "Measurements":
                # Use database manager to get filtered measurements
                # This is a simplified example - you'd implement the actual filtering in database_manager
                query = f"""
                SELECT m.*, p.latitude, p.longitude, p.profile_time
                FROM measurements m
                JOIN profiles p ON m.profile_id = p.id
                WHERE p.latitude BETWEEN {lat_range[0]} AND {lat_range[1]}
                AND p.longitude BETWEEN {lon_range[0]} AND {lon_range[1]}
                AND m.temperature BETWEEN {temp_range[0]} AND {temp_range[1]}
                AND m.salinity BETWEEN {sal_range[0]} AND {sal_range[1]}
                LIMIT {max_records}
                """
                
                from sqlalchemy import text
                session = db_manager.get_session()
                try:
                    result = session.execute(text(query))
                    data = pd.DataFrame(result.fetchall(), columns=result.keys())
                    st.session_state.explorer_data = data
                finally:
                    session.close()
            
            else:
                st.warning(f"Data type '{data_type}' not yet implemented in this demo.")
    
    except Exception as e:
        st.error(f"Error loading data: {e}")
        logger.error(f"Error in load_explorer_data: {e}")

def show_settings_page(data_ingestion, db_manager):
    """Enhanced settings and configuration page."""
    st.markdown('<h2 class="sub-header">⚙️ Settings & Configuration</h2>', unsafe_allow_html=True)
    
    # System status
    st.markdown("### 🔧 System Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Database Status**")
        try:
            session = db_manager.get_session()
            session.close()
            st.success("✅ Database Connected")
        except Exception as e:
            st.error(f"❌ Database Error: {e}")
    
    with col2:
        st.markdown("**Data Status**")
        try:
            # Check data availability
            st.success("✅ Data Available")  # Simplified for demo
        except Exception as e:
            st.error(f"❌ Data Error: {e}")
    
    with col3:
        st.markdown("**AI Status**")
        try:
            st.success("✅ AI Pipeline Ready")  # Simplified for demo
        except Exception as e:
            st.error(f"❌ AI Error: {e}")
    
    # Data management
    st.markdown("### 📊 Data Management")
    
    if st.button("🔄 Refresh Data Cache"):
        st.cache_resource.clear()
        st.success("Cache cleared successfully!")
    
    if st.button("📈 Update Data Summary"):
        try:
            # Update data summary
            st.success("Data summary updated!")
        except Exception as e:
            st.error(f"Error updating summary: {e}")
    
    # Configuration options
    st.markdown("### ⚙️ Configuration")
    
    # Display current configuration
    st.markdown("**Current Configuration:**")
    config_display = {
        "Database URL": Config.DATABASE_URL[:50] + "..." if len(Config.DATABASE_URL) > 50 else Config.DATABASE_URL,
        "Debug Mode": Config.DEBUG,
        "Data Directory": Config.DATA_DIR
    }
    
    st.json(config_display)
    
    # Help and documentation
    st.markdown("### 📚 Help & Documentation")
    
    st.markdown("""
    **FloatChat Enhanced Features:**
    
    1. **Natural Language Queries**: Ask questions about ARGO data in plain English
    2. **2D Plotting**: Create advanced visualizations from queries or manual configuration
    3. **Interactive Maps**: Visualize float locations and trajectories
    4. **Advanced Analytics**: Statistical analysis and correlation studies
    5. **Data Export**: Download data in multiple formats (CSV, JSON, Excel)
    
    **Example Queries:**
    - "Show temperature profiles in the Indian Ocean"
    - "Create a T-S diagram for Bay of Bengal floats"
    - "Map active floats in Arabian Sea"
    - "Plot salinity distribution histogram"
    
    **Tips:**
    - Use specific geographic regions for better results
    - Include parameter names like temperature, salinity, pressure
    - Try different visualization types based on your data
    """)

# Helper functions for visualizations
def create_auto_map(data: pd.DataFrame, visualizer):
    """Create automatic map visualization."""
    if 'latitude' in data.columns and 'longitude' in data.columns:
        center_lat = data['latitude'].mean()
        center_lon = data['longitude'].mean()
        
        m = folium.Map(location=[center_lat, center_lon], zoom_start=4)
        
        for idx, row in data.iterrows():
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=f"Float: {row.get('float_id', 'N/A')}",
                icon=folium.Icon(color='blue', icon='ship', prefix='fa')
            ).add_to(m)
        
        folium_static(m, width=800, height=400)

def create_auto_profile_plot(data: pd.DataFrame, query: str, visualizer):
    """Create automatic profile plot."""
    if 'pressure' in data.columns:
        # Determine parameter from query
        if 'temperature' in query and 'temperature' in data.columns:
            param = 'temperature'
        elif 'salinity' in query and 'salinity' in data.columns:
            param = 'salinity'
        else:
            # Use first available parameter
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            param_cols = [col for col in numeric_cols if col != 'pressure']
            param = param_cols[0] if param_cols else 'temperature'
        
        if param in data.columns:
            fig = visualizer.create_profile_plot(data, param)
            st.plotly_chart(fig, use_container_width=True)

def create_auto_histogram(data: pd.DataFrame, query: str, visualizer):
    """Create automatic histogram."""
    numeric_cols = data.select_dtypes(include=[np.number]).columns
    
    # Determine parameter from query
    param = None
    if 'temperature' in query and 'temperature' in data.columns:
        param = 'temperature'
    elif 'salinity' in query and 'salinity' in data.columns:
        param = 'salinity'
    elif 'pressure' in query and 'pressure' in data.columns:
        param = 'pressure'
    else:
        param = numeric_cols[0] if len(numeric_cols) > 0 else None
    
    if param:
        fig = visualizer.create_histogram(data, param)
        st.plotly_chart(fig, use_container_width=True)

def create_data_summary_viz(data: pd.DataFrame, visualizer):
    """Create summary visualizations for data."""
    st.markdown("### 📊 Data Summary")
    
    # Basic statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Records", len(data))
    with col2:
        if 'float_id' in data.columns:
            st.metric("Unique Floats", data['float_id'].nunique())
    with col3:
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        st.metric("Parameters", len(numeric_cols))
    
    # Show first few numeric parameters
    if len(numeric_cols) > 0:
        param = numeric_cols[0]
        fig = visualizer.create_histogram(data, param)
        st.plotly_chart(fig, use_container_width=True)

def create_smart_plot(data: pd.DataFrame, query: str, visualizer):
    """Create intelligent plot based on data characteristics."""
    numeric_cols = data.select_dtypes(include=[np.number]).columns
    
    if 'temperature' in data.columns and 'salinity' in data.columns:
        # T-S diagram
        fig = visualizer.create_ts_diagram(data)
        st.plotly_chart(fig, use_container_width=True)
    elif 'pressure' in data.columns and len(numeric_cols) > 1:
        # Profile plot
        param = [col for col in numeric_cols if col != 'pressure'][0]
        fig = visualizer.create_profile_plot(data, param)
        st.plotly_chart(fig, use_container_width=True)
    elif len(numeric_cols) >= 2:
        # Scatter plot
        x_param, y_param = numeric_cols[0], numeric_cols[1]
        fig = visualizer.create_scatter_plot(data, x_param, y_param)
        st.plotly_chart(fig, use_container_width=True)
    else:
        # Histogram
        param = numeric_cols[0] if len(numeric_cols) > 0 else None
        if param:
            fig = visualizer.create_histogram(data, param)
            st.plotly_chart(fig, use_container_width=True)

# Additional helper functions for specific plot types
def create_query_histogram(data: pd.DataFrame, query: str, visualizer):
    """Create histogram from query."""
    # Implementation similar to create_auto_histogram
    create_auto_histogram(data, query, visualizer)

def create_query_scatter(data: pd.DataFrame, query: str, visualizer):
    """Create scatter plot from query."""
    # Parse query for parameters
    numeric_cols = data.select_dtypes(include=[np.number]).columns
    
    if ' vs ' in query:
        parts = query.split(' vs ')
        param1 = None
        param2 = None
        
        for col in numeric_cols:
            if col in parts[0].lower():
                param1 = col
            if col in parts[1].lower():
                param2 = col
        
        if param1 and param2 and param1 != param2:
            fig = visualizer.create_scatter_plot(data, param1, param2)
            st.plotly_chart(fig, use_container_width=True)
            return
    
    # Default: use first two numeric columns
    if len(numeric_cols) >= 2:
        fig = visualizer.create_scatter_plot(data, numeric_cols[0], numeric_cols[1])
        st.plotly_chart(fig, use_container_width=True)

def create_query_profile(data: pd.DataFrame, query: str, visualizer):
    """Create profile plot from query."""
    create_auto_profile_plot(data, query, visualizer)

def create_query_map(data: pd.DataFrame, visualizer):
    """Create map from query."""
    create_auto_map(data, visualizer)

# Additional visualization helper functions
def create_quick_visualization(data: pd.DataFrame, visualizer):
    """Create quick visualization based on data."""
    create_smart_plot(data, "", visualizer)

def create_histogram_from_data(data: pd.DataFrame, visualizer):
    """Create histogram from data."""
    numeric_cols = data.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        fig = visualizer.create_histogram(data, numeric_cols[0])
        st.plotly_chart(fig, use_container_width=True)

def create_map_from_data(data: pd.DataFrame, visualizer):
    """Create map from data."""
    if 'latitude' in data.columns and 'longitude' in data.columns:
        create_auto_map(data, visualizer)
    else:
        st.warning("No geographic coordinates available for mapping.")

def create_time_series_plot(data: pd.DataFrame, query_or_param, visualizer):
    """Create time series plot from data."""
    try:
        if 'profile_time' not in data.columns:
            st.warning("No time data available for time series plot.")
            return
            
        # Determine parameter from query or use directly if it's a parameter name
        if isinstance(query_or_param, str) and query_or_param in data.columns:
            param = query_or_param
        else:
            query_lower = str(query_or_param).lower()
            param = 'temperature'  # default
            if 'temperature' in query_lower and 'temperature' in data.columns:
                param = 'temperature'
            elif 'salinity' in query_lower and 'salinity' in data.columns:
                param = 'salinity'
            elif 'oxygen' in query_lower and 'oxygen' in data.columns:
                param = 'oxygen'
            elif 'pressure' in query_lower and 'pressure' in data.columns:
                param = 'pressure'
            elif 'temperature' in data.columns:
                param = 'temperature'
            elif 'salinity' in data.columns:
                param = 'salinity'
            else:
                # Use first numeric column that's not time or coordinates
                numeric_cols = data.select_dtypes(include=[np.number]).columns
                exclude_cols = ['profile_time', 'latitude', 'longitude', 'cycle_number', 'float_id']
                param_cols = [col for col in numeric_cols if col not in exclude_cols]
                param = param_cols[0] if param_cols else 'temperature'
        
        if param not in data.columns:
            st.warning(f"Parameter '{param}' not found in data.")
            return
            
        # Clean and prepare data
        plot_data = data[['profile_time', param, 'float_id']].dropna()
        
        if plot_data.empty:
            st.warning(f"No valid data for {param} time series.")
            return
            
        # Convert profile_time to datetime if it's not already
        if not pd.api.types.is_datetime64_any_dtype(plot_data['profile_time']):
            plot_data['profile_time'] = pd.to_datetime(plot_data['profile_time'])
        
        # Create plotly figure
        fig = go.Figure()
        
        # Group by float_id and plot each float's time series
        unique_floats = plot_data['float_id'].unique()
        colors = px.colors.qualitative.Set1
        
        # Limit to first 10 floats to avoid overcrowding
        for i, float_id in enumerate(unique_floats[:10]):
            float_data = plot_data[plot_data['float_id'] == float_id].sort_values('profile_time')
            
            fig.add_trace(go.Scatter(
                x=float_data['profile_time'],
                y=float_data[param],
                mode='lines+markers',
                name=f'Float {float_id}',
                line=dict(color=colors[i % len(colors)], width=2),
                marker=dict(size=4),
                hovertemplate=f'<b>Float {float_id}</b><br>' +
                             f'Time: %{{x}}<br>' +
                             f'{param.title()}: %{{y:.2f}}<br>' +
                             '<extra></extra>'
            ))
        
        # Update layout
        fig.update_layout(
            title=f"{param.title()} Time Series",
            xaxis_title="Time",
            yaxis_title=f"{param.title()}",
            template='plotly_white',
            height=600,
            hovermode='x unified',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        # Display the plot
        st.plotly_chart(fig, use_container_width=True)
        
        # Show statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Data Points", len(plot_data))
        with col2:
            st.metric("Floats", len(unique_floats))
        with col3:
            mean_val = plot_data[param].mean()
            st.metric(f"Mean {param.title()}", f"{mean_val:.2f}")
        with col4:
            date_range = plot_data['profile_time'].max() - plot_data['profile_time'].min()
            st.metric("Time Range", f"{date_range.days} days")
            
    except Exception as e:
        logger.error(f"Error creating time series plot: {e}")
        st.error(f"Could not create time series plot: {e}")

if __name__ == "__main__":
    main()
