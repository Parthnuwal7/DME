// Graph editor functionality

let network;
let nodes, edges;
let originalRelationships;

document.addEventListener('DOMContentLoaded', function() {
    const graphData = buildGraphFromFlatRelationships(currentRelationships);
    currentRelationships = graphData;
    originalRelationships = JSON.parse(JSON.stringify(currentRelationships));
    updateGraphStats();
    setupEventListeners();
    initializeNetwork();
});

function setupEventListeners() {
    // Layout change
    document.getElementById('layout-select').addEventListener('change', function() {
        changeLayout(this.value);
    });
    
    // Node size change
    document.getElementById('node-size').addEventListener('input', function() {
        changeNodeSize(this.value);
    });
    
    // Edge width change
    document.getElementById('edge-width').addEventListener('input', function() {
        changeEdgeWidth(this.value);
    });
}

function initializeNetwork() {
    // This function can be used to initialize vis.js network if needed
    // For now, PyVis handles the network creation
    console.log('Network initialized');
}

function updateGraphStats() {
    const nodeCount = currentRelationships.nodes ? currentRelationships.nodes.length : 0;
    const edgeCount = currentRelationships.edges ? currentRelationships.edges.length : 0;
    
    document.getElementById('node-count').textContent = nodeCount;
    document.getElementById('edge-count').textContent = edgeCount;
}

function changeLayout(layoutType) {
    console.log('Changing layout to:', layoutType);
    // Layout change logic would go here
    // This would interact with the vis.js network
}

function changeNodeSize(size) {
    console.log('Changing node size to:', size);
    // Node size change logic would go here
}

function changeEdgeWidth(width) {
    console.log('Changing edge width to:', width);
    // Edge width change logic would go here
}

function saveGraph() {
    // Get current graph state
    const updatedRelationships = getCurrentGraphState();
    
    fetch('/update_graph', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            relationships: updatedRelationships
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Graph saved successfully!', 'success');
            currentRelationships = updatedRelationships;
        } else {
            showNotification('Error saving graph: ' + data.error, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error saving graph', 'error');
    });
}

function resetGraph() {
    if (confirm('Are you sure you want to reset the graph to its original state?')) {
        currentRelationships = JSON.parse(JSON.stringify(originalRelationships));
        location.reload(); // Simple reload to reset the graph
    }
}

function getCurrentGraphState() {
    // This would extract the current state from the vis.js network
    // For now, return the current relationships
    return currentRelationships;
}

function showNotification(message, type) {
    const alertClass = type === 'success' ? 'alert-success' : 'alert-danger';
    const alertHtml = `
        <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    // Insert at the top of the container
    const container = document.querySelector('.container');
    container.insertAdjacentHTML('afterbegin', alertHtml);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        const alert = container.querySelector('.alert');
        if (alert) {
            alert.remove();
        }
    }, 5000);
}

// Additional utility functions
function addNode(nodeData) {
    currentRelationships.nodes.push(nodeData);
    updateGraphStats();
}

function removeNode(nodeId) {
    currentRelationships.nodes = currentRelationships.nodes.filter(node => node.id !== nodeId);
    currentRelationships.edges = currentRelationships.edges.filter(edge => 
        edge.from !== nodeId && edge.to !== nodeId
    );
    updateGraphStats();
}

function addEdge(edgeData) {
    currentRelationships.edges.push(edgeData);
    updateGraphStats();
}

function removeEdge(edgeId) {
    currentRelationships.edges = currentRelationships.edges.filter(edge => edge.id !== edgeId);
    updateGraphStats();
}

// Update the save function to handle multiple files
function saveGraph() {
    const updatedRelationships = getCurrentGraphState();
    
    fetch('/update_graph', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            relationships: updatedRelationships,
            filenames: currentFilenames // Add this variable to track filenames
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Graph saved successfully!', 'success');
            currentRelationships = updatedRelationships;
        } else {
            showNotification('Error saving graph: ' + data.error, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error saving graph', 'error');
    });
}

function buildGraphFromFlatRelationships(flatRelationships) {
    const nodeMap = {};
    const nodes = [];
    const edges = [];

    flatRelationships.forEach((rel, index) => {
        const fromLabel = `${rel.from_table}:${rel.from_column}`;
        const toLabel = `${rel.to_table}:${rel.to_column}`;

        if (!nodeMap[fromLabel]) {
            nodeMap[fromLabel] = nodes.length;
            nodes.push({ id: nodeMap[fromLabel], label: fromLabel });
        }

        if (!nodeMap[toLabel]) {
            nodeMap[toLabel] = nodes.length;
            nodes.push({ id: nodeMap[toLabel], label: toLabel });
        }

        edges.push({
            from: nodeMap[fromLabel],
            to: nodeMap[toLabel],
            label: `Conf: ${rel.confidence}`,
            title: `FK: ${fromLabel} → ${toLabel}`,
            width: rel.confidence * 5
        });
    });

    return { nodes, edges };
}

