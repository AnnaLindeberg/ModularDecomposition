import networkx as nx
# TODO: bad import
from classes import *

def unreducedMD(partition: Partition) -> nx.DiGraph:
    '''
    Meant to implement the full algorithm of paper.
    '''
    pass

def reduceMD(modDecomp: nx.DiGraph) -> nx.DiGraph:
    '''
    Meant to calculate reduced modular decomposition from (possibly) unreduced modular decomposition.
    '''
    pass

def graphToPartition(graph: nx.Graph) -> Partition:
    '''
    Takes nx-graph (directed) G and outputs a partition with a single cell containing
    all vertices of G. Adjacencies of G are encoded. '''
    # TODO: now assumes G's vertices are integers only. Is this really necessary in algorithm
    # or just an assumption for assumptions sake? If G has other vertices, do we need integer aliases?
    
    # create custom vertices 
    vertices: dict(int, Vertex) = {}
    for vertex in graph:
        vertices[vertex] = Vertex(label = vertex)
    
    # then create arcs
    for vertex, neighbors in graph.adj.items():
        newVertex = vertices[vertex]
        for neighbor in neighbors.keys():
            newEndPoint = vertices[neighbor]
            arc = Arc(newVertex, newEndPoint)
            newVertex.adj.append(arc)
            
            possibleTwinArc = newEndPoint.findArc(newVertex)
            if possibleTwinArc is not None:
                possibleTwinArc.twin = arc
                arc.twin = possibleTwinArc
    
    # then create single cell and link vertices to appropriate place in it
    cell = Cell(DL_list(), 1, -1)
    for vertex in vertices.values():
        newListNode = ListNode(vertex)
        cell.elements.prepend(newListNode)
        vertex.cell = cell
        vertex.cellPos = newListNode
    
    # just to keep sane
    cell.elements.reverse()

    return Partition([cell], nx.number_of_nodes(graph))




def modularDecomposition(graph: nx.Graph) -> nx.DiGraph:
    '''
    Meant to be the only call user of nx actually makes.
    '''
    return reduceMD(unreducedMD(graphToPartition(graph)))

G = nx.complete_graph(4)
p = graphToPartition(G)

print(p)