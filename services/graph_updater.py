import json
import os
from datetime import datetime

class GraphUpdater:
    def __init__(self, output_folder):
        self.output_folder = output_folder
        self.initial_file = os.path.join(output_folder, 'initial_relationships.json')
        self.edited_file = os.path.join(output_folder, 'edited_model.json')
    
    def save_initial_relationships(self, relationships):
        """Save initial auto-generated relationships"""
        data = {
            'relationships': relationships,
            'created_at': datetime.now().isoformat(),
            'version': 'initial'
        }
        
        with open(self.initial_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def save_edited_relationships(self, relationships):
        """Save user-edited relationships"""
        data = {
            'relationships': relationships,
            'updated_at': datetime.now().isoformat(),
            'version': 'edited'
        }
        
        with open(self.edited_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_initial_relationships(self):
        """Load initial relationships"""
        if os.path.exists(self.initial_file):
            with open(self.initial_file, 'r') as f:
                data = json.load(f)
                return data.get('relationships', {})
        return {}
    
    def load_edited_relationships(self):
        """Load edited relationships, fallback to initial if not found"""
        if os.path.exists(self.edited_file):
            with open(self.edited_file, 'r') as f:
                data = json.load(f)
                return data.get('relationships', {})
        
        return self.load_initial_relationships()
    
    def get_version_history(self):
        history = []
        for fpath, label in [(self.initial_file, 'initial'), (self.edited_file, 'edited')]:
            if os.path.exists(fpath):
                with open(fpath, 'r') as f:
                    data = json.load(f)
                    rels = data.get('relationships', [])
                    history.append({
                        'version': label,
                        'created_at' if label == 'initial' else 'updated_at': data.get('created_at' if label == 'initial' else 'updated_at'),
                        'relationship_count': len(rels)
                    })
        return history
