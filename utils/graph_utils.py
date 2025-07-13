from pyvis.network import Network
import json
import tempfile
import os

class GraphUtils:
    def __init__(self):
        self.default_options = {
            "physics": {
                "enabled": True,
                "stabilization": {"iterations": 100}
            },
            "interaction": {
                "hover": True,
                "selectConnectedEdges": True
            },
            "manipulation": {
                "enabled": True,
                "addNode": True,
                "addEdge": True,
                "deleteNode": True,
                "deleteEdge": True
            }
        }
    
    def create_interactive_graph(self, relationships):
        """Create an interactive graph using PyVis"""
        net = Network(height="600px", width="100%", bgcolor="#222222", font_color="white")
        
        # Add nodes
        for node in relationships.get('nodes', []):
            net.add_node(
                node['id'],
                label=node['label'],
                title=self._create_node_tooltip(node),
                color=self._get_node_color(node.get('type', 'default'))
            )
        
        # Add edges
        for edge in relationships.get('edges', []):
            net.add_edge(
                edge['from'],
                edge['to'],
                label=edge.get('label', ''),
                title=self._create_edge_tooltip(edge),
                width=edge.get('weight', 1) * 5
            )
        
        # Set options
        net.set_options(json.dumps(self.default_options))
        
        # Generate HTML
        html = net.generate_html()
        
        # Clean up the HTML to make it embeddable
        return self._clean_html_for_embedding(html)
    
    def _create_node_tooltip(self, node):
        """Create tooltip text for nodes"""
        tooltip = f"<b>{node['label']}</b><br>"
        if 'properties' in node:
            for key, value in node['properties'].items():
                tooltip += f"{key}: {value}<br>"
        return tooltip
    
    def _create_edge_tooltip(self, edge):
        """Create tooltip text for edges"""
        tooltip = f"<b>{edge.get('label', 'Connection')}</b><br>"
        tooltip += f"Weight: {edge.get('weight', 1)}<br>"
        tooltip += f"Type: {edge.get('type', 'unknown')}"
        return tooltip
    
    def _get_node_color(self, node_type):
        """Get color based on node type"""
        colors = {
            'column': '#97C2FC',
            'table': '#FB7E81',
            'entity': '#7BE141',
            'default': '#DDDDDD'
        }
        return colors.get(node_type, colors['default'])
    
    def _clean_html_for_embedding(self, html):
        """Clean PyVis HTML for embedding in Flask template"""
        # Remove html, head, body tags and keep only the div content
        start = html.find('<div id="')
        end = html.rfind('</div>') + 6
        
        if start != -1 and end != -1:
            return html[start:end]
        
        return html