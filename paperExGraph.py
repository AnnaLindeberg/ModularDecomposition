from modularDecomp import modularDecomposition
import networkx as nx
import matplotlib.pyplot as plt

def drawMD(tree):
    pos = nx.nx_agraph.graphviz_layout(tree, prog="dot")
    labels = {}
    for vertex in tree:
        if 'MDlabel' in tree.nodes[vertex]:
            labels[vertex] = tree.nodes[vertex]['MDlabel']
        elif tree.out_degree(vertex) == 0:
            label, = vertex 
            labels[vertex] = str(label)
        else:
            labels[vertex] = str(tuple(vertex))
    nx.draw(tree, pos = pos, ax = None, labels = labels)
    plt.show()

# Want to decompose the graph given in the paper?
# G = nx.Graph()
# edges = ['ab', 'ad', 'ae', 'bd', 'be', 'cd', 'ce', 'df', 'ef', 'fg', 'fh', 'gh', 'il', 'jl', 'kl']
# charToIntLegend = 'abcdefghijkl'
# edges = [(charToIntLegend.index(s[0]), charToIntLegend.index(s[1])) for s in edges]
# edges = [(s[0], s[1]) for s in edges]
# G.add_edges_from(edges)

# You can, ofcourse, also use some nx-built-in graph such as
# G = nx.complete_graph(100)
# G = nx.path_graph(4)
# G = nx.star_graph(4)
# ... etc

# Here's for a larger random graph
# with higher probability you'll likely get a primitive graph
edge_prob = 0.01
G = nx.fast_gnp_random_graph(100, edge_prob)
MD = modularDecomposition(G)

# Here we print the strong, non-trivial modules of G
print("The strong, non-trivial modules are:")
for module in MD:
    if len(module) == nx.number_of_nodes(G):
        print(f"root is labeled {MD.nodes[module]['MDlabel']}")
    elif len(module) == 1:
        continue
    print(f"{set(module)} with label {MD.nodes[module]['MDlabel']}")


# Want to draw the graph+MD as well?
# Note that the MD-tree is drawn when you close the given graph.
nx.draw(G, with_labels=True)
plt.show()
drawMD(MD)