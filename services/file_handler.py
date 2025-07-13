import os
import pandas as pd
from werkzeug.utils import secure_filename
import uuid

class FileHandler:
    def __init__(self, upload_folder):
        self.upload_folder = upload_folder
        self.allowed_extensions = {'csv'}
    
    def allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def save_file(self, file):
        """Save uploaded file and return unique filename"""
        if file and self.allowed_file(file.filename):
            # Generate unique filename
            original_filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{original_filename}"
            filepath = os.path.join(self.upload_folder, unique_filename)
            
            file.save(filepath)
            return unique_filename
        
        raise ValueError("Invalid file type")
    
    def load_csv(self, filename):
        """Load CSV file and return pandas DataFrame with better error handling"""
        filepath = os.path.join(self.upload_folder, filename)
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File {filename} not found")
        
        try:
            # Try different encodings and separators
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            separators = [',', ';', '\t', '|']
            
            df = None
            for encoding in encodings:
                for sep in separators:
                    try:
                        df = pd.read_csv(filepath, encoding=encoding, sep=sep, 
                                       on_bad_lines='skip', low_memory=False)
                        if not df.empty and len(df.columns) > 1:
                            break
                    except (UnicodeDecodeError, pd.errors.ParserError):
                        continue
                if df is not None and not df.empty and len(df.columns) > 1:
                    break
            
            if df is None or df.empty:
                raise ValueError("Could not parse CSV file or file is empty")
            
            # Clean column names
            df.columns = df.columns.astype(str).str.strip()
            
            # Remove completely empty rows
            df = df.dropna(how='all')
            
            if df.empty:
                raise ValueError("CSV file contains no data after cleaning")
            
            return df
            
        except Exception as e:
            raise ValueError(f"Error reading CSV file: {str(e)}")
    
    def delete_file(self, filename):
        """Delete uploaded file"""
        filepath = os.path.join(self.upload_folder, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False
    
    def get_file_info(self, filename):
        """Get information about the uploaded file"""
        filepath = os.path.join(self.upload_folder, filename)
        if os.path.exists(filepath):
            stat = os.stat(filepath)
            return {
                'size': stat.st_size,
                'created': stat.st_ctime,
                'modified': stat.st_mtime
            }
        return None
    def save_multiple_files(self, files):
        """Save multiple uploaded files and return list of unique filenames"""
        saved_files = []
        
        for file in files:
            if file and self.allowed_file(file.filename):
                try:
                    filename = self.save_file(file)
                    saved_files.append(filename)
                except ValueError as e:
                    # Log error but continue with other files
                    print(f"Error saving file {file.filename}: {e}")
                    continue
        
        return saved_files

    def load_multiple_csvs(self, filenames):
        """Load multiple CSV files and return dictionary of DataFrames"""
        csv_data = {}
        
        for filename in filenames:
            try:
                df = self.load_csv(filename)
                csv_data[filename] = df
            except Exception as e:
                print(f"Error loading file {filename}: {e}")
                continue
        
        return csv_data