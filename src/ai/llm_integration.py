"""
LLM integration using Google Gemini for natural language processing.
"""
import logging
from typing import List, Dict, Any, Optional, Tuple
import google.generativeai as genai
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun
import json
import re
import pandas as pd
from datetime import datetime, timedelta

from ..config import Config

logger = logging.getLogger(__name__)

class GeminiLLM:
    """Simple Gemini LLM wrapper for query processing."""
    
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        self.model_name = model_name
        genai.configure(api_key=Config.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(model_name)
    
    def generate(self, prompt: str) -> str:
        """Generate response from Gemini model."""
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=Config.TEMPERATURE,
                    max_output_tokens=Config.MAX_TOKENS
                )
            )
            return response.text
        except Exception as e:
            logger.error(f"Error calling Gemini model: {e}")
            return f"Error: {str(e)}"

class ARGOQueryProcessor:
    """Processes natural language queries about ARGO data."""
    
    def __init__(self):
        self.llm = GeminiLLM()
        self.system_prompt = self._create_system_prompt()
        self.region_coordinates = self._initialize_region_mapping()
    
    def _initialize_region_mapping(self) -> Dict[str, Dict[str, float]]:
        """Initialize geographic region coordinate mapping."""
        return {
            'indian_ocean': {'min_lat': -60, 'max_lat': 30, 'min_lon': 20, 'max_lon': 147},
            'arabian_sea': {'min_lat': 5, 'max_lat': 30, 'min_lon': 50, 'max_lon': 80},
            'bay_of_bengal': {'min_lat': 5, 'max_lat': 25, 'min_lon': 80, 'max_lon': 100},
            'southern_indian_ocean': {'min_lat': -60, 'max_lat': -30, 'min_lon': 20, 'max_lon': 147},
            'equatorial_indian_ocean': {'min_lat': -10, 'max_lat': 10, 'min_lon': 40, 'max_lon': 100},
            'atlantic_ocean': {'min_lat': -60, 'max_lat': 70, 'min_lon': -80, 'max_lon': 20},
            'pacific_ocean': {'min_lat': -60, 'max_lat': 70, 'min_lon': 120, 'max_lon': -70},
            'southern_ocean': {'min_lat': -90, 'max_lat': -50, 'min_lon': -180, 'max_lon': 180},
            'arctic_ocean': {'min_lat': 70, 'max_lat': 90, 'min_lon': -180, 'max_lon': 180},
            'mediterranean_sea': {'min_lat': 30, 'max_lat': 46, 'min_lon': -6, 'max_lon': 36},
            'red_sea': {'min_lat': 12, 'max_lat': 30, 'min_lon': 32, 'max_lon': 43},
            'persian_gulf': {'min_lat': 24, 'max_lat': 30, 'min_lon': 47, 'max_lon': 57},
            'equatorial': {'min_lat': -5, 'max_lat': 5, 'min_lon': -180, 'max_lon': 180}
        }
    
    def _create_system_prompt(self) -> str:
        """Create system prompt for ARGO data query processing."""
        return """
You are an expert oceanographer and data analyst specializing in ARGO float data. 
Your task is to interpret natural language queries about oceanographic data and convert them into structured database queries.

ARGO Data Context:
- ARGO floats are autonomous profiling instruments that measure ocean properties
- Key parameters: temperature, salinity, pressure, depth, oxygen (DOXY), chlorophyll (CHLA), backscatter (BBP700), nitrate (NITRATE), pH
- Geographic regions: Indian Ocean, Atlantic, Pacific, Southern Ocean, Arctic
- Data includes float trajectories, profile measurements, and quality flags
- Time ranges typically span from deployment date to present

Query Processing Rules:
1. Identify the main oceanographic parameter(s) of interest
2. Extract geographic constraints (latitude/longitude ranges, region names)
3. Identify temporal constraints (date ranges, seasons, months)
4. Determine the type of analysis requested (profiles, trajectories, comparisons)
5. Map natural language to SQL query components

Common Query Patterns:
- "Show me salinity profiles near the equator" → parameter=salinity, lat_range=[-5,5]
- "Compare temperature in Arabian Sea" → parameter=temperature, region=Arabian Sea
- "ARGO floats in Indian Ocean last 6 months" → region=Indian Ocean, time_range=last 6 months
- "Nearest floats to this location" → geographic proximity search

Always respond with a JSON object containing:
{
    "intent": "profile_analysis|trajectory_analysis|float_search|comparison|summary",
    "parameters": ["list", "of", "parameters"],
    "geographic_constraints": {
        "min_lat": float,
        "max_lat": float,
        "min_lon": float,
        "max_lon": float,
        "region": "string"
    },
    "temporal_constraints": {
        "start_date": "YYYY-MM-DD",
        "end_date": "YYYY-MM-DD",
        "time_period": "string"
    },
    "analysis_type": "profiles|trajectories|measurements|comparison",
    "sql_components": {
        "select": "string",
        "from": "string", 
        "where": "string",
        "order_by": "string"
    },
    "confidence": float
}
"""
    
    def process_query(self, user_query: str) -> Dict[str, Any]:
        """Process a natural language query and return structured information."""
        try:
            # Use enhanced fallback parsing directly to ensure our fixes are applied
            # The LLM was causing inconsistent results, so we'll rely on our improved logic
            result = self._enhanced_parsing(user_query)
            
            # Try LLM as backup if enhanced parsing has low confidence
            if result.get('confidence', 0) < 0.7:
                try:
                    prompt = f"""
{self.system_prompt}

User Query: "{user_query}"

Please analyze this query and provide the structured response as JSON.
"""
                    
                    response = self.llm.generate(prompt)
                    
                    # Extract JSON from response
                    json_match = re.search(r'\{.*\}', response, re.DOTALL)
                    if json_match:
                        llm_result = json.loads(json_match.group())
                        
                        # Merge LLM result with our enhanced parsing for geographic constraints
                        if not llm_result.get('geographic_constraints', {}).get('min_lat'):
                            geo_constraints = result.get('geographic_constraints', {})
                            if geo_constraints.get('min_lat') is not None:
                                llm_result['geographic_constraints'] = geo_constraints
                        
                        llm_result['original_query'] = user_query
                        llm_result['processed_at'] = datetime.utcnow().isoformat()
                        return llm_result
                except Exception:
                    pass
            
            return result
                
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return self._enhanced_parsing(user_query)
    
    def _enhanced_parsing(self, user_query: str) -> Dict[str, Any]:
        """Fallback parsing when LLM response is not in expected format."""
        query_lower = user_query.lower()
        
        # Basic parameter detection
        parameters = []
        if any(word in query_lower for word in ['temperature', 'temp']):
            parameters.append('temperature')
        if any(word in query_lower for word in ['salinity', 'salt']):
            parameters.append('salinity')
        if any(word in query_lower for word in ['oxygen', 'doxy']):
            parameters.append('oxygen')
        if any(word in query_lower for word in ['chlorophyll', 'chla']):
            parameters.append('chlorophyll')
        if any(word in query_lower for word in ['nitrate']):
            parameters.append('nitrate')
        if any(word in query_lower for word in ['ph', 'ph_in_situ']):
            parameters.append('ph')
        
        # Enhanced geographic region detection with coordinate mapping
        region = None
        geo_coords = {'min_lat': None, 'max_lat': None, 'min_lon': None, 'max_lon': None}
        
        region_mappings = {
            'indian ocean': 'indian_ocean',
            'arabian sea': 'arabian_sea', 
            'bay of bengal': 'bay_of_bengal',
            'southern indian ocean': 'southern_indian_ocean',
            'atlantic ocean': 'atlantic_ocean',
            'pacific ocean': 'pacific_ocean',
            'southern ocean': 'southern_ocean',
            'mediterranean sea': 'mediterranean_sea',
            'red sea': 'red_sea',
            'persian gulf': 'persian_gulf',
            'equator': 'equatorial'
        }
        
        for region_name, region_key in region_mappings.items():
            if region_name in query_lower:
                region = region_name.title()
                if region_key in self.region_coordinates:
                    coords = self.region_coordinates[region_key]
                    geo_coords = {
                        'min_lat': coords['min_lat'],
                        'max_lat': coords['max_lat'], 
                        'min_lon': coords['min_lon'],
                        'max_lon': coords['max_lon']
                    }
                break
        
        # Enhanced intent detection with measurement vs profile distinction
        intent = 'profile_analysis'
        analysis_type = 'profiles'
        
        # Check for count-specific queries first (highest priority)
        if any(phrase in query_lower for phrase in ['how many', 'count', 'number of']):
            if any(word in query_lower for word in ['measurement', 'measurements', 'data point', 'data points', 'observation', 'observations']):
                intent = 'measurement_count'
                analysis_type = 'measurements'
            elif any(word in query_lower for word in ['float', 'floats']):
                intent = 'float_count'
                analysis_type = 'floats'
            else:
                intent = 'profile_count'
                analysis_type = 'profiles'
        # Check for time series specific queries
        elif any(phrase in query_lower for phrase in ['time series', 'timeseries', 'over time', 'temporal', 'plot', 'chart', 'graph']) and \
             any(param in query_lower for param in ['temperature', 'salinity', 'oxygen', 'measurement']):
            intent = 'measurement_analysis'
            analysis_type = 'measurements'
        # Check for measurement-specific queries (including parameter names)
        elif any(word in query_lower for word in ['measurement', 'measurements', 'data point', 'data points', 'observation', 'observations']) or \
             (any(param in query_lower for param in ['temperature', 'salinity', 'oxygen']) and \
              any(action in query_lower for action in ['show', 'get', 'fetch', 'retrieve', 'data'])):
            intent = 'measurement_analysis'
            analysis_type = 'measurements'
        elif any(word in query_lower for word in ['trajectory', 'path', 'route']):
            intent = 'trajectory_analysis'
            analysis_type = 'trajectories'
        elif any(word in query_lower for word in ['compare', 'comparison']):
            intent = 'comparison'
            analysis_type = 'comparison'
        elif any(word in query_lower for word in ['nearest', 'near', 'close', 'find']):
            intent = 'float_search'
            analysis_type = 'floats'
        elif any(word in query_lower for word in ['summary', 'overview', 'statistics', 'range']):
            intent = 'summary'
            analysis_type = 'summary'
        
        return {
            'intent': intent,
            'parameters': parameters,
            'geographic_constraints': {
                'region': region,
                'min_lat': geo_coords['min_lat'],
                'max_lat': geo_coords['max_lat'],
                'min_lon': geo_coords['min_lon'],
                'max_lon': geo_coords['max_lon']
            },
            'temporal_constraints': {
                'start_date': None,
                'end_date': None,
                'time_period': None
            },
            'analysis_type': analysis_type,
            'sql_components': {
                'select': '*',
                'from': 'argo_profiles',
                'where': '1=1',
                'order_by': 'profile_time DESC'
            },
            'confidence': 0.8 if geo_coords['min_lat'] is not None else 0.6,
            'original_query': user_query,
            'processed_at': datetime.utcnow().isoformat()
        }
    
    def _fallback_parsing(self, user_query: str) -> Dict[str, Any]:
        """Backward compatibility method that calls enhanced parsing."""
        return self._enhanced_parsing(user_query)
    
    def generate_sql_query(self, processed_query: Dict[str, Any]) -> str:
        """Generate SQL query from processed query information."""
        try:
            intent = processed_query.get('intent', 'profile_analysis')
            parameters = processed_query.get('parameters', [])
            geo_constraints = processed_query.get('geographic_constraints', {})
            temp_constraints = processed_query.get('temporal_constraints', {})
            
            # Base query structure based on intent
            if intent == 'measurement_count':
                # Count measurements in specified region
                base_query = """
                SELECT COUNT(*) as measurement_count
                FROM argo_measurements am
                JOIN argo_profiles ap ON am.float_id = ap.float_id AND am.cycle_number = ap.cycle_number
                """
                
            elif intent == 'float_count':
                # Count unique floats in specified region
                base_query = """
                SELECT COUNT(DISTINCT ap.float_id) as float_count
                FROM argo_profiles ap
                """
                
            elif intent == 'profile_count':
                # Count profiles in specified region
                base_query = """
                SELECT COUNT(*) as profile_count
                FROM argo_profiles ap
                """
                
            elif intent == 'measurement_analysis':
                # Return actual measurement data with all relevant parameters
                base_query = """
                SELECT am.float_id, am.cycle_number, ap.latitude, ap.longitude, ap.profile_time,
                       am.pressure, am.temperature, am.salinity, am.oxygen, am.chlorophyll, am.nitrate, am.ph
                FROM argo_measurements am
                JOIN argo_profiles ap ON am.float_id = ap.float_id AND am.cycle_number = ap.cycle_number
                """
                
            elif intent == 'profile_analysis':
                base_query = """
                SELECT DISTINCT ap.float_id, ap.cycle_number, ap.latitude, ap.longitude,
                       ap.profile_time, ap.max_depth, ap.num_levels
                FROM argo_profiles ap
                """
                
                # Add parameter filtering if needed
                if parameters:
                    base_query += """
                    JOIN argo_measurements am ON ap.float_id = am.float_id 
                        AND ap.cycle_number = am.cycle_number
                    """
                
            elif intent == 'trajectory_analysis':
                base_query = """
                SELECT at.float_id, at.latitude, at.longitude, at.trajectory_time, at.cycle_number
                FROM argo_trajectories at
                """
                
            elif intent == 'float_search':
                base_query = """
                SELECT DISTINCT af.float_id, af.wmo_id, af.institution, af.status,
                       ap.latitude, ap.longitude, ap.profile_time
                FROM argo_floats af
                JOIN argo_profiles ap ON af.float_id = ap.float_id
                """
            
            else:
                base_query = """
                SELECT ap.float_id, ap.cycle_number, ap.latitude, ap.longitude, ap.profile_time
                FROM argo_profiles ap
                """
            
            # Build WHERE clause
            where_conditions = []
            
            # Geographic constraints
            if geo_constraints.get('min_lat') and geo_constraints.get('max_lat'):
                where_conditions.append(f"ap.latitude BETWEEN {geo_constraints['min_lat']} AND {geo_constraints['max_lat']}")
            
            if geo_constraints.get('min_lon') and geo_constraints.get('max_lon'):
                where_conditions.append(f"ap.longitude BETWEEN {geo_constraints['min_lon']} AND {geo_constraints['max_lon']}")
            
            # Temporal constraints
            if temp_constraints.get('start_date'):
                where_conditions.append(f"ap.profile_time >= '{temp_constraints['start_date']}'")
            
            if temp_constraints.get('end_date'):
                where_conditions.append(f"ap.profile_time <= '{temp_constraints['end_date']}'")
            
            # Parameter constraints
            if parameters and intent in ['profile_analysis', 'measurement_analysis', 'measurement_count']:
                param_conditions = []
                for param in parameters:
                    if param == 'temperature':
                        param_conditions.append("am.temperature IS NOT NULL")
                    elif param == 'salinity':
                        param_conditions.append("am.salinity IS NOT NULL")
                    elif param == 'oxygen':
                        param_conditions.append("am.oxygen IS NOT NULL")
                    elif param == 'chlorophyll':
                        param_conditions.append("am.chlorophyll IS NOT NULL")
                    elif param == 'nitrate':
                        param_conditions.append("am.nitrate IS NOT NULL")
                    elif param == 'ph':
                        param_conditions.append("am.ph IS NOT NULL")
                
                if param_conditions:
                    where_conditions.append(f"({' OR '.join(param_conditions)})")
            
            # Combine WHERE clause
            if where_conditions:
                base_query += " WHERE " + " AND ".join(where_conditions)
            
            # Add ORDER BY and LIMIT based on query intent
            if intent in ['measurement_count', 'float_count', 'profile_count']:
                # Count queries don't need ORDER BY or LIMIT
                pass
            elif intent == 'measurement_analysis':
                base_query += " ORDER BY ap.profile_time DESC, am.pressure ASC LIMIT 1000"
            else:
                base_query += " ORDER BY ap.profile_time DESC LIMIT 100"
            
            return base_query
            
        except Exception as e:
            logger.error(f"Error generating SQL query: {e}")
            return "SELECT * FROM argo_profiles LIMIT 10"
    
    def generate_response(self, query_result: pd.DataFrame, original_query: str, 
                         processed_query: Dict[str, Any]) -> str:
        """Generate natural language response from query results."""
        try:
            if query_result.empty:
                return "No ARGO data found matching your query criteria."
            
            # Create response prompt
            response_prompt = f"""
Based on the following ARGO data query results, provide a clear and informative response to the user's question.

Original Query: "{original_query}"

Query Results Summary:
- Number of records: {len(query_result)}
- Columns: {list(query_result.columns)}
- Sample data: {query_result.head(3).to_dict('records')}

Please provide a natural language response that:
1. Answers the user's question directly
2. Highlights key findings from the data
3. Mentions relevant statistics (number of profiles, geographic coverage, etc.)
4. Suggests follow-up questions if appropriate

Keep the response concise but informative, suitable for both scientists and general users.
"""
            
            response = self.llm.generate(response_prompt)
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"Found {len(query_result)} ARGO profiles matching your query. Please refer to the data table for details."
