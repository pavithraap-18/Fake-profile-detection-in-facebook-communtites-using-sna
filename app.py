from flask import Flask, request, render_template
import os
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
STATIC_FOLDER = 'static'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    suspicious_nodes = []
    total_nodes = 0
    graph_image = None

    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.csv'):
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)

            # Load CSV and create graph
            df = pd.read_csv(filepath)
            G = nx.Graph()
            G.add_edges_from(df.values)

            # Compute clustering coefficients
            clustering = nx.clustering(G)
            threshold = 0.1
            suspicious_nodes = [node for node, cc in clustering.items() if cc < threshold]
            total_nodes = G.number_of_nodes()

            # Create graph visualization
            plt.figure(figsize=(8, 6))
            pos = nx.spring_layout(G)
            color_map = ['red' if node in suspicious_nodes else 'green' for node in G.nodes()]
            nx.draw(G, pos, with_labels=True, node_color=color_map, node_size=600, font_size=10)
            plt.title("Community Graph")
            image_path = os.path.join(STATIC_FOLDER, 'graph.png')
            plt.savefig(image_path)
            plt.close()
            graph_image = 'graph.png'

            return render_template('index.html', suspicious=suspicious_nodes, total=total_nodes, graph=graph_image)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)