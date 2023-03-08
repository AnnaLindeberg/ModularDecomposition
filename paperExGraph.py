from classes import *
from auxiliary import *
from modularDecomp import *
import networkx as nx
import matplotlib.pyplot as plt


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
print(MD)
