from classes import *
from auxiliary import *

vertices = {}
for v in "abcdefghijkl":
    vertices[v] = Vertex(v)
    vertices[v].adj = []

edges = ['ab', 'ad', 'ae', 'bd', 'be', 'cd', 'ce', 'df', 'ef', 'fg', 'fh', 'gh', 'il', 'jl', 'kl']
arcs = []

for x, y in edges:
    edge = Arc(vertices[x], vertices[y])
    twinEdge = Arc(vertices[y], vertices[x])
    edge.twin = twinEdge
    twinEdge.twin = edge
    vertices[x].adj.append(edge)
    vertices[y].adj.append(twinEdge)
    arcs.append(edge)

# for vertex in vertices.values():
#     print(vertex.adj)

a = vertices.pop('a')
b_h = [vertex for vertex in vertices.values()]
smallCell = Cell(DL_list([a]), 1, 6)
a.cell = smallCell
a.cellPos = smallCell.elements.head

largeCell = Cell(DL_list(b_h), 2, -1)
for node in largeCell.elements:
    node.data.cell = largeCell
    node.data.cellPos = node

partition = Partition([smallCell, largeCell], 8)
print(partition)
# pivot(partition, a, a.adj)

# orderedVertexPartition(partition)
# print(partition)
# Pprime = partition.restrict(partition.cells[:2])
# print(Pprime)
# for cell in Pprime.cells:
#     for vertex in cell.elements:
#         print(vertex)
#         for arc in vertex.data.adj:
#             print(arc, arc.twin)
#         print('')

# print(arcsFromCell(partition.cells[1]))

# split test on cell {b,c,d}
# splitArcs = []
# splitArcs.append(partition.cells[1].elements.head.data.adj[0])
# dadj = partition.cells[1].elements.head.next.data.adj
# splitArcs.append(dadj[0])
# splitArcs += dadj[-2:]
# eadj = partition.cells[1].elements.head.next.next.data.adj
# splitArcs += [eadj[0]] + eadj[-2:]

print(orderedVertexPartition(partition))