import networkx as nx
from collections import deque
# TODO: bad imports
from classes import *
import auxiliary as aux


def recOVP(partition: Partition) -> nx.DiGraph:
    if partition.size  == 1:
        T = nx.DiGraph()
        T.add_node(partition.cells[0].elements.head.data.label)
        return T
    
    # TODO: unfinished

def unreducedMD(graph: nx.Graph, partition: Partition) -> nx.DiGraph:
    '''
    Meant to implement the full algorithm of paper.
    '''
    if nx.number_of_nodes(graph) == 1:
        return nx.DiGraph(graph)
    
    # pick "smallest" vertex
    # TODO: what, exactly, do they mean with smallest here? see alg 1 of paper
    # here we pick smallest as appearing first in the nx-graph: is that a bad idea?
    pivotVertex = list(graph)[0]

    # find the partition G(P,v) with ordered vertex partition
    partition.createCell(graph, pivotVertex)
    maxModules = aux.orderedVertexPartition(graph, partition)
    return maxModules

def reduceMD(modDecomp: nx.DiGraph) -> nx.DiGraph:
    '''
    Meant to calculate reduced modular decomposition from (possibly) unreduced modular decomposition.
    '''
    # TODO: actually reduce
    return modDecomp

def prepareGraph(graph: nx.Graph) -> Partition:
    '''
    Takes nx-graph (undirected) G and outputs a partition with a single cell containing
    all vertices of G. Moreover, G is equipped with proper vertex- and edge-attributes as needed, namely:
    *   each vertex in G has an attribute 'cell' pointing to the cell its contained in
    *   each vertex in G has an attribute 'cellIdx' giving the index of the vertex in the elements of its cell

    possibly also (TODO)
    (*   each edge in G has an attribute 'twin' pointing to its twin edge i.e. (x,y) points to (y,x) and vice versa)

    '''
    # TODO: now assumes G's vertices are integers only. Is this really necessary in algorithm
    # or just an assumption for assumptions sake? If G has other vertices, do we need integer aliases?
    vertices: deque[int] = deque(list(graph))
    cell = Cell(vertices, 1, -1)

    # add the vertex attributes
    for vertex in graph:
        graph.nodes[vertex]['cell'] = cell
        graph.nodes[vertex]['cellIdx'] = list(graph).index(vertex)

    # TODO: do we ever really need the twin edge pointers? if so, add them.

    return Partition([cell], nx.number_of_nodes(graph))



def modularDecomposition(graph: nx.Graph) -> nx.DiGraph:
    '''
    Meant to be the only call user of nx actually makes.
    '''
    partition = prepareGraph(graph)
    return reduceMD(unreducedMD(graph, partition))
