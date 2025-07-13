import pandas as pd
import json
import numpy as np

class CoreDataEngine:
    """
    Placeholder for your core data processing engine.
    This will be where you implement your relationship detection logic.
    """
    
    def __init__(self):
        self.processed_data = None
    
    def process_data(self, csv_data):
        """
        Process CSV data and return relationships in JSON format.
        This is a placeholder - you'll implement your actual logic here.
        
        Args:
            csv_data (pd.DataFrame): The uploaded CSV data
            
        Returns:
            dict: Relationships in the format expected by the graph visualizer
        """
        # Placeholder implementation - generates sample relationships
        return self._generate_sample_relationships(csv_data)
    
    def _convert_to_serializable(self, obj):
        """Convert numpy/pandas types to JSON serializable types"""
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif pd.isna(obj):
            return None
        else:
            return obj
    
    def _get_column_info(self, df, col):
        """Get column information with proper type conversion"""
        try:
            null_count = int(df[col].isnull().sum())
            unique_count = int(df[col].nunique())
            data_type = str(df[col].dtype)
            
            # Get some sample values
            sample_values = df[col].dropna().head(3).tolist()
            sample_values = [self._convert_to_serializable(val) for val in sample_values]
            
            return {
                "data_type": data_type,
                "null_count": null_count,
                "unique_count": unique_count,
                "sample_values": sample_values,
                "total_rows": len(df)
            }
        except Exception as e:
            return {
                "data_type": "unknown",
                "null_count": 0,
                "unique_count": 0,
                "sample_values": [],
                "total_rows": len(df),
                "error": str(e)
            }
    
    def _generate_sample_relationships(self, df):
        """
        Generate sample relationships for demonstration purposes.
        Replace this with your actual relationship detection logic.
        """
        relationships = {
            "nodes": [],
            "edges": []
        }
        
        # Create nodes from column names
        for i, col in enumerate(df.columns):
            node_data = {
                "id": i,
                "label": str(col),
                "type": "column",
                "properties": self._get_column_info(df, col)
            }
            relationships["nodes"].append(node_data)
        
        # Create sample edges based on column relationships
        # This is a simple example - you'll replace with your logic
        for i in range(len(df.columns)):
            for j in range(i + 1, len(df.columns)):
                # Simple heuristic: if columns have similar names or types, create edge
                col1, col2 = df.columns[i], df.columns[j]
                
                # Calculate a simple similarity score
                similarity = self._calculate_similarity(df, col1, col2)
                
                if similarity > 0.1:  # Threshold for creating edges
                    relationships["edges"].append({
                        "from": i,
                        "to": j,
                        "label": f"similarity_{similarity:.2f}",
                        "weight": float(similarity),
                        "type": "inferred"
                    })
        
        return relationships
    
    def _calculate_similarity(self, df, col1, col2):
        """
        Calculate similarity between two columns.
        This is a placeholder - implement your actual similarity logic.
        """
        try:
            # Simple similarity based on data types
            if df[col1].dtype == df[col2].dtype:
                base_similarity = 0.5
            else:
                base_similarity = 0.1
            
            # Add name similarity
            col1_lower = str(col1).lower()
            col2_lower = str(col2).lower()
            
            if col1_lower in col2_lower or col2_lower in col1_lower:
                base_similarity += 0.3
            
            # Add uniqueness similarity
            unique1 = df[col1].nunique()
            unique2 = df[col2].nunique()
            
            if unique1 == unique2:
                base_similarity += 0.2
            
            return min(base_similarity, 1.0)
            
        except Exception:
            return 0.1
        
    def process_multiple_data(self, csv_data_dict):
        """
        Process multiple CSV files and return relationships in JSON format.
        
        Args:
            csv_data_dict (dict): Dictionary with filename as key and DataFrame as value
            
        Returns:
            dict: Relationships in the format expected by the graph visualizer
        """
        relationships = {
            "nodes": [],
            "edges": []
        }
        
        node_id_counter = 0
        file_node_mapping = {}  # Track which nodes belong to which file
        
        # Create nodes for each file and their columns
        for filename, df in csv_data_dict.items():
            # Create a file node
            file_node = {
                "id": node_id_counter,
                "label": f"File: {filename}",
                "type": "file",
                "properties": {
                    "filename": filename,
                    "rows": len(df),
                    "columns": len(df.columns)
                }
            }
            relationships["nodes"].append(file_node)
            file_node_id = node_id_counter
            node_id_counter += 1
            
            file_node_mapping[filename] = {"file_node": file_node_id, "columns": []}
            
            # Create column nodes for this file
            for col in df.columns:
                column_node = {
                    "id": node_id_counter,
                    "label": f"{filename}: {col}",
                    "type": "column",
                    "properties": self._get_column_info(df, col)
                }
                relationships["nodes"].append(column_node)
                
                # Connect column to file
                relationships["edges"].append({
                    "from": file_node_id,
                    "to": node_id_counter,
                    "label": "contains",
                    "weight": 1.0,
                    "type": "file_structure"
                })
                
                file_node_mapping[filename]["columns"].append(node_id_counter)
                node_id_counter += 1
        
        # Create relationships between columns across files
        self._create_inter_file_relationships(relationships, csv_data_dict, file_node_mapping)
        
        return relationships

    def _create_inter_file_relationships(self, relationships, csv_data_dict, file_node_mapping):
        """Create relationships between columns across different files"""
        files = list(csv_data_dict.keys())
        
        for i, file1 in enumerate(files):
            for j, file2 in enumerate(files):
                if i >= j:  # Avoid duplicate comparisons
                    continue
                    
                df1 = csv_data_dict[file1]
                df2 = csv_data_dict[file2]
                
                # Compare columns between files
                for col1_idx, col1 in enumerate(df1.columns):
                    for col2_idx, col2 in enumerate(df2.columns):
                        similarity = self._calculate_cross_file_similarity(
                            df1, col1, df2, col2, file1, file2
                        )
                        
                        if similarity > 0.3:  # Threshold for cross-file relationships
                            node1_id = file_node_mapping[file1]["columns"][col1_idx]
                            node2_id = file_node_mapping[file2]["columns"][col2_idx]
                            
                            relationships["edges"].append({
                                "from": node1_id,
                                "to": node2_id,
                                "label": f"cross_file_similarity_{similarity:.2f}",
                                "weight": float(similarity),
                                "type": "cross_file_relationship"
                            })

    def _calculate_cross_file_similarity(self, df1, col1, df2, col2, file1, file2):
        """Calculate similarity between columns from different files"""
        try:
            # Basic similarity factors
            similarity = 0.0
            
            # Same column name
            if col1.lower() == col2.lower():
                similarity += 0.5
            
            # Similar data types
            if df1[col1].dtype == df2[col2].dtype:
                similarity += 0.2
            
            # Similar unique value counts (normalized)
            unique1 = df1[col1].nunique()
            unique2 = df2[col2].nunique()
            max_unique = max(unique1, unique2)
            min_unique = min(unique1, unique2)
            
            if max_unique > 0:
                unique_similarity = min_unique / max_unique
                similarity += unique_similarity * 0.3
            
            # Check for common values (sample-based for performance)
            sample1 = set(df1[col1].dropna().astype(str).head(100))
            sample2 = set(df2[col2].dropna().astype(str).head(100))
            
            if sample1 and sample2:
                common_values = len(sample1.intersection(sample2))
                total_values = len(sample1.union(sample2))
                if total_values > 0:
                    similarity += (common_values / total_values) * 0.3
            
            return min(similarity, 1.0)
            
        except Exception:
            return 0.0