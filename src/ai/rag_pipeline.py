"""
Retrieval-Augmented Generation (RAG) pipeline for ARGO data queries.
"""
import logging
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
from datetime import datetime

from .llm_integration import ARGOQueryProcessor
from .vector_store import ARGOVectorStore
from ..database.database_manager import DatabaseManager

logger = logging.getLogger(__name__)

class ARGORAGPipeline:
    """RAG pipeline for processing ARGO data queries."""
    
    def __init__(self, database_manager: DatabaseManager, vector_store: ARGOVectorStore):
        self.query_processor = ARGOQueryProcessor()
        self.database_manager = database_manager
        self.vector_store = vector_store
    
    def process_query(self, user_query: str) -> Dict[str, Any]:
        """
        Process a user query through the RAG pipeline.
        
        Args:
            user_query: Natural language query from user
            
        Returns:
            Dictionary containing query results and response
        """
        try:
            # Step 1: Process natural language query
            processed_query = self.query_processor.process_query(user_query)
            logger.info(f"Processed query: {processed_query}")
            
            # Step 2: Retrieve relevant context from vector store
            context = self._retrieve_context(processed_query)
            
            # Step 3: Generate SQL query
            sql_query = self.query_processor.generate_sql_query(processed_query)
            logger.info(f"Generated SQL: {sql_query}")
            
            # Step 4: Execute database query
            query_result = self._execute_database_query(sql_query, processed_query)
            
            # Step 5: Generate natural language response
            response = self.query_processor.generate_response(
                query_result, user_query, processed_query
            )
            
            # Step 6: Log the query
            self.database_manager.log_query(
                user_query=user_query,
                processed_query=str(processed_query),
                sql_query=sql_query,
                response=response,
                success=True
            )
            
            return {
                'success': True,
                'original_query': user_query,
                'processed_query': processed_query,
                'sql_query': sql_query,
                'context': context,
                'data': query_result.to_dict('records') if not query_result.empty else [],
                'response': response,
                'metadata': {
                    'num_results': len(query_result),
                    'execution_time': None,  # Could be added with timing
                    'timestamp': datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            
            # Log failed query
            self.database_manager.log_query(
                user_query=user_query,
                processed_query=None,
                sql_query=None,
                response=None,
                success=False,
                error_message=str(e)
            )
            
            return {
                'success': False,
                'original_query': user_query,
                'error': str(e),
                'response': f"I encountered an error processing your query: {str(e)}. Please try rephrasing your question.",
                'metadata': {
                    'timestamp': datetime.utcnow().isoformat()
                }
            }
    
    def _retrieve_context(self, processed_query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Retrieve relevant context from vector store."""
        try:
            # Create search query from processed information
            search_terms = []
            
            # Add parameters
            parameters = processed_query.get('parameters', [])
            if parameters:
                search_terms.extend(parameters)
            
            # Add geographic region
            geo_constraints = processed_query.get('geographic_constraints', {})
            if geo_constraints.get('region'):
                search_terms.append(geo_constraints['region'])
            
            # Add intent
            intent = processed_query.get('intent', '')
            if intent:
                search_terms.append(intent)
            
            # Combine search terms
            search_query = " ".join(search_terms) if search_terms else "ARGO ocean data"
            
            # Search vector store
            context = []
            
            # Search profiles
            profile_results = self.vector_store.search_profiles(
                search_query, n_results=5
            )
            context.extend(profile_results)
            
            # Search floats
            float_results = self.vector_store.search_floats(
                search_query, n_results=3
            )
            context.extend(float_results)
            
            return context
            
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return []
    
    def _execute_database_query(self, sql_query: str, processed_query: Dict[str, Any]) -> pd.DataFrame:
        """Execute database query based on processed query information."""
        try:
            intent = processed_query.get('intent', 'profile_analysis')
            parameters = processed_query.get('parameters', [])
            geo_constraints = processed_query.get('geographic_constraints', {})
            temp_constraints = processed_query.get('temporal_constraints', {})
            
            # Handle count queries with raw SQL execution
            if intent in ['measurement_count', 'float_count', 'profile_count']:
                from sqlalchemy import text
                session = self.database_manager.get_session()
                try:
                    result = session.execute(text(sql_query))
                    count_data = result.fetchone()
                    if count_data:
                        # Create a DataFrame with the count result
                        count_value = count_data[0]  # Get the first column value
                        column_name = 'measurement_count' if intent == 'measurement_count' else \
                                     'float_count' if intent == 'float_count' else 'profile_count'
                        return pd.DataFrame([{column_name: count_value}])
                    else:
                        return pd.DataFrame()
                finally:
                    session.close()
            
            # Handle measurement analysis queries
            elif intent == 'measurement_analysis':
                # Use the dedicated method for measurement analysis
                result = self.database_manager.get_measurements_for_analysis(
                    parameter=parameters[0] if parameters else 'temperature',
                    min_lat=geo_constraints.get('min_lat'),
                    max_lat=geo_constraints.get('max_lat'),
                    min_lon=geo_constraints.get('min_lon'),
                    max_lon=geo_constraints.get('max_lon'),
                    start_date=datetime.fromisoformat(temp_constraints['start_date']) if temp_constraints.get('start_date') else None,
                    end_date=datetime.fromisoformat(temp_constraints['end_date']) if temp_constraints.get('end_date') else None,
                    limit=2000
                )
            
            # Handle profile analysis queries
            elif intent == 'profile_analysis':
                # Check if this is actually asking for measurement data
                original_query = processed_query.get('original_query', '').lower()
                if any(word in original_query for word in ['measurement', 'measurements', 'data', 'plot', 'graph', 'chart', 'time series']):
                    # This should be treated as measurement analysis
                    result = self.database_manager.get_measurements_for_analysis(
                        parameter=parameters[0] if parameters else 'temperature',
                        min_lat=geo_constraints.get('min_lat'),
                        max_lat=geo_constraints.get('max_lat'),
                        min_lon=geo_constraints.get('min_lon'),
                        max_lon=geo_constraints.get('max_lon'),
                        start_date=datetime.fromisoformat(temp_constraints['start_date']) if temp_constraints.get('start_date') else None,
                        end_date=datetime.fromisoformat(temp_constraints['end_date']) if temp_constraints.get('end_date') else None,
                        limit=2000
                    )
                else:
                    # Get profiles by parameter
                    result = self.database_manager.get_profiles_by_parameter(
                        parameter=parameters[0] if parameters else 'temperature',
                        min_lat=geo_constraints.get('min_lat'),
                        max_lat=geo_constraints.get('max_lat'),
                        min_lon=geo_constraints.get('min_lon'),
                        max_lon=geo_constraints.get('max_lon'),
                        start_date=datetime.fromisoformat(temp_constraints['start_date']) if temp_constraints.get('start_date') else None,
                        end_date=datetime.fromisoformat(temp_constraints['end_date']) if temp_constraints.get('end_date') else None
                    )
                
            elif intent == 'trajectory_analysis':
                # Get trajectory data
                # This would need to be implemented in database_manager
                result = pd.DataFrame()  # Placeholder
                
            elif intent == 'float_search':
                # Get floats by region
                if geo_constraints.get('min_lat') is not None and geo_constraints.get('max_lat') is not None:
                    result = self.database_manager.get_floats_by_region(
                        min_lat=geo_constraints['min_lat'],
                        max_lat=geo_constraints['max_lat'],
                        min_lon=geo_constraints.get('min_lon', -180),
                        max_lon=geo_constraints.get('max_lon', 180)
                    )
                else:
                    result = pd.DataFrame()
                    
            else:
                # Check if this should be measurement analysis based on original query
                original_query_lower = processed_query.get('original_query', '').lower()
                if any(word in original_query_lower for word in ['measurement', 'measurements', 'data', 'plot', 'graph', 'chart', 'time series', 'show', 'create', 'temperature', 'salinity']):
                    # Force measurement analysis
                    result = self.database_manager.get_measurements_for_analysis(
                        parameter=parameters[0] if parameters else 'temperature',
                        limit=2000
                    )
                else:
                    # Default: get recent profiles
                    result = self.database_manager.get_profiles_by_parameter('temperature')
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing database query: {e}")
            return pd.DataFrame()
    
    def get_similar_queries(self, user_query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get similar queries from query log."""
        try:
            # This would search the query log for similar queries
            # Implementation depends on how you want to store and search query history
            return []
        except Exception as e:
            logger.error(f"Error getting similar queries: {e}")
            return []
    
    def suggest_follow_up_questions(self, query_result: Dict[str, Any]) -> List[str]:
        """Suggest follow-up questions based on query results."""
        try:
            if not query_result.get('success') or not query_result.get('data'):
                return []
            
            data = query_result['data']
            processed_query = query_result.get('processed_query', {})
            
            suggestions = []
            
            # Geographic suggestions
            if len(data) > 0:
                suggestions.append("Show me the trajectory of these floats")
                suggestions.append("Compare these profiles with data from other regions")
            
            # Parameter suggestions
            parameters = processed_query.get('parameters', [])
            if 'temperature' in parameters:
                suggestions.append("Show me salinity profiles for the same region")
            elif 'salinity' in parameters:
                suggestions.append("Show me temperature profiles for the same region")
            
            # Temporal suggestions
            suggestions.append("Show me data from a different time period")
            suggestions.append("Compare with data from the same season last year")
            
            return suggestions[:3]  # Return top 3 suggestions
            
        except Exception as e:
            logger.error(f"Error suggesting follow-up questions: {e}")
            return []
    
    def get_data_summary(self) -> Dict[str, Any]:
        """Get summary of available data."""
        try:
            # Get database summary
            db_summary = self.database_manager.get_data_summary()
            
            # Get vector store stats
            vector_stats = self.vector_store.get_collection_stats()
            
            return {
                'database': db_summary,
                'vector_store': vector_stats,
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting data summary: {e}")
            return {}
