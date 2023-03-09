from classes import *
from auxiliary import *
from modularDecomp import *
import networkx as nx
import matplotlib.pyplot as plt
import pydot
from networkx.drawing.nx_pydot import graphviz_layout

def drawMD(tree: nx.DiGraph) -> None:
    pos = graphviz_layout(tree, prog="dot")
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

edges = ['ab', 'ad', 'ae', 'bd', 'be', 'cd', 'ce', 'df', 'ef', 'fg', 'fh', 'gh', 'il', 'jl', 'kl']
# charToIntLegend = 'abcdefghijkl'
# edges = [(charToIntLegend.index(s[0]), charToIntLegend.index(s[1])) for s in edges]
edges = [(s[0], s[1]) for s in edges]

G = nx.Graph()
G.add_edges_from(edges)
# print(G)
# nx.draw(G, with_labels=True)
# plt.show()

MD = modularDecomposition(G)
drawMD(MD)

# H = nx.complete_graph(4)
# MD = modularDecomposition(H)
# nx.draw(MD, with_labels=True)
# plt.show()