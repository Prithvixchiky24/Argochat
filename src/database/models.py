"""
Database models for ARGO data storage.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

Base = declarative_base()

class ARGOFloat(Base):
    """Model for ARGO float metadata."""
    
    __tablename__ = 'argo_floats'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    float_id = Column(String(50), unique=True, nullable=False, index=True)
    wmo_id = Column(String(50), nullable=False)
    institution = Column(String(100), nullable=False)
    data_mode = Column(String(20), nullable=False)
    deployment_date = Column(DateTime)
    last_transmission = Column(DateTime)
    status = Column(String(20), default='active')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ARGOProfile(Base):
    """Model for ARGO profile data matching your NetCDF structure."""
    
    __tablename__ = 'argo_profiles'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    float_id = Column(String(50), nullable=False, index=True)  # From PLATFORM_NUMBER
    cycle_number = Column(Integer, nullable=False)  # From CYCLE_NUMBER
    latitude = Column(Float, nullable=False)  # From LATITUDE
    longitude = Column(Float, nullable=False)  # From LONGITUDE
    profile_time = Column(DateTime, nullable=False)  # From JULD
    platform_number = Column(String(50), index=True)  # PLATFORM_NUMBER from NetCDF
    data_mode = Column(String(20))  # DATA_MODE from NetCDF
    
    # Profile QC flags
    profile_pres_qc = Column(String(1))  # PROFILE_PRES_QC
    profile_temp_qc = Column(String(1))  # PROFILE_TEMP_QC
    profile_psal_qc = Column(String(1))  # PROFILE_PSAL_QC
    position_qc = Column(String(1))  # POSITION_QC
    juld_qc = Column(String(1))  # JULD_QC
    
    # Calculated fields
    max_depth = Column(Float)
    min_depth = Column(Float)
    num_levels = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Index for efficient querying
    __table_args__ = (
        {'extend_existing': True}
    )

class ARGOMeasurement(Base):
    """Model for individual ARGO measurements matching your NetCDF structure."""
    
    __tablename__ = 'argo_measurements'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    float_id = Column(String(50), nullable=False, index=True)
    cycle_number = Column(Integer, nullable=False)
    
    # Raw measurements
    pressure = Column(Float)  # PRES
    temperature = Column(Float)  # TEMP
    salinity = Column(Float)  # PSAL
    
    # Adjusted measurements
    pressure_adjusted = Column(Float)  # PRES_ADJUSTED
    temperature_adjusted = Column(Float)  # TEMP_ADJUSTED
    salinity_adjusted = Column(Float)  # PSAL_ADJUSTED
    
    # Error estimates
    pressure_adjusted_error = Column(Float)  # PRES_ADJUSTED_ERROR
    temperature_adjusted_error = Column(Float)  # TEMP_ADJUSTED_ERROR
    salinity_adjusted_error = Column(Float)  # PSAL_ADJUSTED_ERROR
    
    # Quality control flags
    pressure_qc = Column(String(1))  # PRES_QC
    temperature_qc = Column(String(1))  # TEMP_QC
    salinity_qc = Column(String(1))  # PSAL_QC
    pressure_adjusted_qc = Column(String(1))  # PRES_ADJUSTED_QC
    temperature_adjusted_qc = Column(String(1))  # TEMP_ADJUSTED_QC
    salinity_adjusted_qc = Column(String(1))  # PSAL_ADJUSTED_QC
    
    # Additional BGC parameters (if available)
    oxygen = Column(Float)  # DOXY
    chlorophyll = Column(Float)  # CHLA
    backscatter = Column(Float)  # BBP700
    nitrate = Column(Float)  # NITRATE
    ph = Column(Float)  # PH_IN_SITU_TOTAL
    
    # BGC QC flags
    oxygen_qc = Column(String(1))
    chlorophyll_qc = Column(String(1))
    backscatter_qc = Column(String(1))
    nitrate_qc = Column(String(1))
    ph_qc = Column(String(1))
    
    created_at = Column(DateTime, default=datetime.utcnow)

class ARGOTrajectory(Base):
    """Model for ARGO float trajectory data."""
    
    __tablename__ = 'argo_trajectories'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    float_id = Column(String(50), nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    trajectory_time = Column(DateTime, nullable=False)
    cycle_number = Column(Integer)
    data_mode = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)

class QueryLog(Base):
    """Model for logging user queries."""
    
    __tablename__ = 'query_logs'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_query = Column(Text, nullable=False)
    processed_query = Column(Text)
    sql_query = Column(Text)
    response = Column(Text)
    execution_time = Column(Float)
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class DataSummary(Base):
    """Model for storing data summaries and metadata."""
    
    __tablename__ = 'data_summaries'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    summary_type = Column(String(50), nullable=False)  # 'float', 'region', 'parameter'
    summary_data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
