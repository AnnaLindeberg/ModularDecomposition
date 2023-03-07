import networkx as nx
import matplotlib.pyplot as plt
K_5 = nx.complete_graph(5)
fig = plt.figure
nx.draw(K_5, with_labels=True, font_weight='bold')
plt.show()