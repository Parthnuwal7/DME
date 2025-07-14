from pyvis.network import Network
import json

class GraphUtils:
    def __init__(self):
        self.default_options = {
            "physics": {"enabled": True},
            "interaction": {"hover": True, "selectConnectedEdges": True},
            "manipulation": {"enabled": False}
        }

    def create_interactive_graph(self, relationships):
        net = Network(height="600px", width="100%", bgcolor="#222222", font_color="white")

        seen_nodes = {}

        def add_node(label):
            if label not in seen_nodes:
                node_id = len(seen_nodes)
                net.add_node(node_id, label=label, title=label, color="#97C2FC")
                seen_nodes[label] = node_id
            return seen_nodes[label]

        for rel in relationships:
            from_label = f"{rel['from_table']}:{rel['from_column']}"
            to_label = f"{rel['to_table']}:{rel['to_column']}"
            from_id = add_node(from_label)
            to_id = add_node(to_label)

            net.add_edge(
                from_id,
                to_id,
                label=f"{rel['confidence']:.2f}",
                title=f"FK: {from_label} → {to_label}",
                width=rel['confidence'] * 5
            )

        net.set_options(json.dumps(self.default_options))
        return self._clean_html_for_embedding(net.generate_html())

    def _clean_html_for_embedding(self, html):
        start = html.find('<div id="mynetwork"')
        end = html.rfind('</script>') + 9
        return html[start:end] if start != -1 and end != -1 else html
