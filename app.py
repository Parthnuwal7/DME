from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
import pandas as pd
from werkzeug.utils import secure_filename
from services.file_handler import FileHandler
from services.graph_updater import GraphUpdater
from core.core_data_engine import CoreDataEngine
from utils.graph_utils import GraphUtils
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload and output directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Initialize services
file_handler = FileHandler(app.config['UPLOAD_FOLDER'])
graph_updater = GraphUpdater(app.config['OUTPUT_FOLDER'])
core_engine = CoreDataEngine()
graph_utils = GraphUtils()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'files' not in request.files:
        flash('No files selected')
        return redirect(request.url)
    
    files = request.files.getlist('files')  # Get list of files
    
    if not files or all(f.filename == '' for f in files):
        flash('No files selected')
        return redirect(request.url)
    
    processed_files = []
    all_csv_data = {}
    
    try:
        # Process each file
        for file in files:
            if file and file.filename.lower().endswith('.csv'):
                # Save file
                filename = file_handler.save_file(file)
                
                # Load CSV data
                csv_data = file_handler.load_csv(filename)
                
                # Check if CSV is empty
                if csv_data.empty:
                    flash(f'The uploaded CSV file {file.filename} is empty')
                    continue
                
                processed_files.append(filename)
                all_csv_data[filename] = csv_data
                flash(f'File {file.filename} uploaded successfully')
        
        if not processed_files:
            flash('No valid CSV files were processed')
            return redirect(url_for('index'))
        
        # Process all data with core engine
        relationships = core_engine.process_multiple_data(all_csv_data)
        
        # Save initial relationships
        graph_updater.save_initial_relationships(relationships)
        
        # Generate visualization
        graph_html = graph_utils.create_interactive_graph(relationships)
        
        # Calculate combined CSV info
        total_rows = sum(len(df) for df in all_csv_data.values())
        total_columns = sum(len(df.columns) for df in all_csv_data.values())
        all_column_names = []
        for df in all_csv_data.values():
            all_column_names.extend(list(df.columns))
        
        return render_template('graph.html', 
                             graph_html=graph_html,
                             filenames=processed_files,  # Changed to plural
                             relationships=json.dumps(relationships, ensure_ascii=False),
                             csv_info={
                                 'files_count': len(processed_files),
                                 'total_rows': total_rows,
                                 'total_columns': total_columns,
                                 'column_names': all_column_names,
                                 'file_details': {fname: {
                                     'rows': len(all_csv_data[fname]),
                                     'columns': len(all_csv_data[fname].columns),
                                     'column_names': list(all_csv_data[fname].columns)
                                 } for fname in processed_files}
                             })
    
    except Exception as e:
        flash(f'Error processing files: {str(e)}')
        return redirect(url_for('index'))

@app.route('/update_graph', methods=['POST'])
def update_graph():
    try:
        data = request.get_json()
        relationships = data.get('relationships', [])
        
        # Update the graph data
        graph_updater.save_edited_relationships(relationships)
        
        # Regenerate visualization
        graph_html = graph_utils.create_interactive_graph(relationships)
        
        return jsonify({
            'success': True,
            'graph_html': graph_html
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/get_relationships')
def get_relationships():
    try:
        relationships = graph_updater.load_edited_relationships()
        return jsonify(relationships)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)