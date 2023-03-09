import networkx as nx
from collections import deque
from typing import Union
# TODO: bad imports
from classes import *
import auxiliary as aux


def recOVP(graph: nx.Graph, vertexPrio: list[Union[int, Cell]]) -> nx.DiGraph:
    if nx.number_of_nodes(graph) == 1:
        T = nx.DiGraph()
        # there's some "scrap" data still in graph so we clean up by adding node manually
        for vertex in graph:
            if isinstance(vertex, Cell):
                # I think this is always true here
                vertex = frozenset(vertex.elements)
                T.add_node(vertex)
                T.graph['root'] = vertex
            else:
                raise NotImplementedError("Should this really happen")
        return T
    
    # pick isolate or highest no. vertex
    possibleIsolated = list(nx.isolates(graph))

    if possibleIsolated:
        pivotVertex = possibleIsolated[0]
    else:
        for vertex in vertexPrio:
            if vertex in graph:
                pivotVertex = vertex
                break

    # prepare graph and partition
    partition = prepareGraph(graph)
    partition.createCell(graph, pivotVertex)
    modules = aux.orderedVertexPartition(graph, partition, set())[0].cells
    # modules = partition.cells

    # initialize root node
    rootVertex = aux.flattenToFrozen(modules)
    MDtree = nx.DiGraph()
    MDtree.add_node(rootVertex)
    MDtree.graph['root'] = rootVertex

    # MD label this node (?) TODO
    # if not nx.is_connected(graph):
    #     MDtree.nodes[rootVertex]['MDlabel'] = 'parallel'
    # elif not nx.is_connected(nx.complement(graph)):
    #     MDtree.nodes[rootVertex]['MDlabel'] = 'series'
    # else:
    #     MDtree.nodes[rootVertex]['MDlabel'] = 'prime'
    
    for module in modules:
        subgraph = aux.subgraph(graph, module.elements)
        subtree = recOVP(subgraph, vertexPrio)
        MDtree = nx.compose(subtree, MDtree)
        root = MDtree.graph['root']
        child = subtree.graph['root']
        MDtree.add_edge(root, child)
    
    return MDtree

def unreducedMD(graph: nx.Graph, partition: Partition) -> nx.DiGraph:
    '''
    Meant to implement the full algorithm of paper.
    '''
    if nx.number_of_nodes(graph) == 1:
        T = nx.DiGraph()
        # there's some "scrap" data still in graph so we clean up by adding node manually
        for vertex in graph:
            if isinstance(vertex, int):
                vertex = frozenset([vertex])
                T.add_node(vertex)
                T.graph['root'] = vertex
        return T
    
    # pick "smallest" vertex
    # TODO: what, exactly, do they mean with smallest here? see alg 1 of paper
    # here we pick smallest as appearing first in the nx-graph: is that a bad idea?
    pivotVertex = list(graph)[0]

    # find the partition G(P,v) of maximal v-avoiding modules with ordered vertex partition
    partition.createCell(graph, pivotVertex)
    maxModules, quotientEdges = aux.orderedVertexPartition(graph, partition, set())

    print("G/P(G,v) is ", maxModules)
    # find the quotient graph G/G(P,v) and MD of it
    quotient = nx.Graph()
    quotientEdges = aux.streamlineEdges(graph, quotientEdges, maxModules)
    quotient.add_nodes_from(maxModules.cells)
    quotient.add_edges_from(quotientEdges)
    priority = maxModules.cells.copy()
    priority.reverse()
    quotientMD = recOVP(quotient, priority)

    # find MD of each module in maxModules and attach to MD of quotient
    for module in maxModules.cells:
        subgraph = aux.subgraph(graph, module.elements)
        subPartition = maxModules.restrict(subgraph, [module])
        subtree = unreducedMD(subgraph, subPartition)

        # now attach this subtree to the partial MD we have established
        if 'root' in subtree.graph:
            quotientMD = nx.compose(subtree, quotientMD)
        else:
            pass

    return quotientMD

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
