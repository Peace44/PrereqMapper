import networkx as nx
import matplotlib.pyplot as plt



# Define the Subject class
class Subject:
    def __init__(self, subject_id, title, prerequisites=None, content=""):
        self.subject_id = subject_id
        self.title = title
        self.prerequisites = prerequisites if prerequisites is not None else []
        self.content = content

    def __repr__(self):
        prereq_str = ', '.join(self.prerequisites) if self.prerequisites else ''
        return f"\n{self.subject_id} ==> {self.title}\nPrereq: {prereq_str}\n{self.content}\n"



# Step 1: Parse the input file and create Subject objects
def parse_input_file(filename):
    subjects = {}
    with open(filename, 'r') as file:
        content_lines = file.read().split('\n\n')  # Split by double newlines
        for block in content_lines:
            lines = block.strip().split('\n')
            header = lines[0]
            content = '\n'.join(lines[2:]) if len(lines) > 2 else ""
            
            # Extract subject ID and title
            subject_id, title = header.split(' ', 1)
            
            # Extract prerequisites
            prereq_line = lines[1].strip()
            prerequisites = prereq_line.replace('Prereq: ', '').split(', ') if prereq_line != 'Prereq:' else []

            subjects[subject_id] = Subject(subject_id, title, prerequisites, content)
    return subjects



# Step 2: Create the graph using Subject objects
def create_graph(subjects):
    G = nx.DiGraph()
    # First, add all subjects and their prerequisites as nodes to the graph
    for subject_id, subject in subjects.items():
        G.add_node(subject_id, title=subject.title)
        for prereq in subject.prerequisites:
            if prereq not in G:
                G.add_node(prereq, title=subjects.get(prereq, Subject(prereq, "")).title)

    # Now, add edges for immediate prerequisites only
    for subject_id, subject in subjects.items():
        immediate_prereqs = set(subject.prerequisites)
        # Remove transitive prerequisites
        for prereq in list(immediate_prereqs):
            # Check if the prerequisite is in the graph to avoid the error
            if prereq in G:
                transitive_prereqs = nx.ancestors(G, prereq)
                immediate_prereqs -= transitive_prereqs
        # Add edges for immediate prerequisites
        for prereq in immediate_prereqs:
            G.add_edge(prereq, subject_id)

    return G



# Step 3: Assign layers and add layer info to each node
def assign_layers(G):
    layers = {}
    for node in nx.topological_sort(G):
        preds = list(G.predecessors(node))
        node_layer = 0 if not preds else max(layers[pred] for pred in preds) + 1
        layers[node] = node_layer
        G.nodes[node]['subset'] = node_layer  # Add layer info to the node
    return layers


# Step 4: Visualization
def visualize_graph(G):
    # Make sure the 'subset' attribute is used for the multipartite layout
    layout = nx.multipartite_layout(G, subset_key='subset')
    
    # Draw the parts we want
    nx.draw_networkx_nodes(G, layout, node_size=50, node_color='blue')
    nx.draw_networkx_edges(G, layout, arrowstyle='->', arrowsize=10)
    nx.draw_networkx_labels(G, layout, font_size=8)
    
    # Plot the graph
    plt.title("Graph Visualization")
    plt.savefig('graph-visualization.png')



def minimize_prerequisite_chains(all_paths):
    # Sort paths by length (longest first)
    all_paths.sort(key=len, reverse=True)
    unique_paths = all_paths.copy()

    # Remove paths that are subsumed by longer paths
    for path in all_paths:
        for longer_path in unique_paths:
            if path != longer_path and set(path).issubset(set(longer_path)):
                unique_paths.remove(path)
                break
    return unique_paths

def write_layers_to_file(G, layers, filename):
    # Group subjects by layers
    layers_to_subjects = {}
    for subject, layer in layers.items():
        layers_to_subjects.setdefault(layer, []).append(subject)
    
    # Sort layers
    sorted_layers = sorted(layers_to_subjects.keys())
    
    with open(filename, 'w') as file:
        for layer in sorted_layers:
            # Write the layer heading
            file.write(f"Layer {layer}:\n")
            for subject in sorted(layers_to_subjects[layer]):
                # Find all paths from root nodes to the subject
                root_nodes = [n for n, d in G.in_degree() if d == 0]
                all_paths = []
                for root in root_nodes:
                    for path in nx.all_simple_paths(G, source=root, target=subject):
                        all_paths.append(path)
                
                # Minimize the prerequisite chains
                minimized_paths = minimize_prerequisite_chains(all_paths)
                
                # Format the paths
                if minimized_paths:
                    formatted_paths = [' ==> '.join(path) for path in minimized_paths]
                    file.write(f"{'; '.join(formatted_paths)}\n")
                else:
                    # Subject has no prerequisites
                    file.write(f"{subject}\n")
            file.write("\n")  # Separate layers with a newline


# Main function to run the app
def main(input_file):
    subjects = parse_input_file(input_file)
    G = create_graph(subjects)
    layers = assign_layers(G)
    visualize_graph(G)
    write_layers_to_file(G, layers, output_file)



# Run the app
if __name__ == "__main__":
    input_file = 'Course6TheoreticalCS.txt'
    output_file = 'Output' + input_file
    main(input_file)