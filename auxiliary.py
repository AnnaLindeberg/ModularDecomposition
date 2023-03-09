import networkx as nx
from typing import Union
# TODO: bad import
from classes import *

def subgraph(graph: nx.Graph, vertices: list[Union[int, Cell]]) -> nx.Graph:
    ''' Return actual copied subgraph instance, rather than subgraph view.'''
    subgraph = nx.Graph()
    subgraph.add_nodes_from((n, graph.nodes[n]) for n in vertices)
    subgraph.add_edges_from((n, nbr, d)
        for n, nbrs in graph.adj.items() if n in vertices
        for nbr, d in nbrs.items() if nbr in vertices)

    return subgraph

def bucket_group(arcs: list[tuple[int, int]], buckets: list[int]) -> list[list[tuple[int, int]]]:
    '''
    Bucket group the given arcs into the given buckets: i.e. return a semi-sorted 
    version of arcs where arcs with the same first coordinate appear consecutive.
    These groups are not necessarily sorted.

    arcs: list of arcs with integer coordinates
    buckets: list of all integers that will appear as a first coordinate of an arc in arcs
    '''
    buckets = {bucket:[] for bucket in buckets}
    for arc in arcs:
        buckets[arc[0]].append(arc)
    
    # now all arcs are properly grouped, bring together in list of lists
    res = []
    for group in buckets.values():
        res.append(group)
    
    return res

def edgesFromCell(graph: nx.Graph, cell : Cell) -> list[tuple[int, int]]:
    '''
    Takes cell C and returns arcs (x,y) where x lies in C, y does not.
    '''
    # use more convenient data structure
    edges = []
    for vertex in cell.elements:
        for neighbor in graph[vertex]:
            if neighbor not in cell:
                edges.append((vertex, neighbor))
    
    return edges

def mergeCells(cells: list[Cell]) -> Cell:
    '''
    Takes (consecutive for reasonable output) cells of partition and merge into new cell.
    '''
    resCell = cells[0].copy()
    for cell in cells[1:]:
        resCell.elements.extend(cell.elements)
        resCell.post -= len(cell.elements)

    return resCell

def flattenToFrozen(cells: list[Cell]) -> frozenset:
    res = []
    for cell in cells:
        for el in cell.elements:
            if isinstance(el, Cell):
                recCall = flattenToFrozen([el])
                for rel in recCall:
                    res.append(rel)
            elif isinstance(el, int) or isinstance(el, str):
                res.append(el)
    return frozenset(res)

# def edgeRepresentatives(graph: nx.Graph, edges: list[tuple[int, int]], fromCells: list[Cell]) -> list[tuple[Cell, Cell]]:
#     # this should use radix grouping but TODO
#     # here naive approach
#     cellEdges = set()

#     for x,y in edges:
#         xCell = graph.nodes[x]['cell']
#         yCell = graph.nodes[y]['cell']
#         cellEdges.add((xCell, yCell))
    
#     return list(cellEdges)

def streamlineEdges(graph: nx.Graph, edges: set[tuple[int, int]], partition: Partition) -> list[tuple[Cell, Cell]]:
    cellEdges = set()
    for x, y in edges:
        xCell = graph.nodes[x]['cell']
        yCell = graph.nodes[y]['cell']
        if xCell not in partition or yCell not in partition:
            raise Exception('something is off')
        
        cellEdges.add((xCell, yCell))
    return list(cellEdges)

def pivot(graph: nx.Graph, partition: Partition, pivotVertex: int, arcs: list[tuple[int, int]]) -> None:
        ''' 
        Pivot at given vertex x. Variable arcs should contain list of all arcs (x,y) where y
        lies in some cell of a pre-decided subset Q of the underlying partition. 
        After pivoting, the partition will be refined so that every module contained in a cell of 
        the partition is still contained in a single cell of the refined partition. Additionally,
        any cell of the refined partition contained in a member of Q will consist of only neighbors
        or only non-neighbors of x. 
        '''
        # TODO: break into smaller pieces of code?

        # Identify which cells will be affected first
        # At the same time we identify which cells will form a new cell
        # and, for convenience later on, store a set of all cells that will be moved
        affectedCells = {}
        affectedVertices = set()
        for _ , y in arcs:
            affectedVertices.add(y)
            yCell = graph.nodes[y]['cell']
            if yCell in affectedCells:
                affectedCells[yCell].append(y)
            else:
                affectedCells[yCell] = [y]
        
        # we now iterate over each cell that will be split 
        xCell = graph.nodes[pivotVertex]['cell']
        for cell, vertices in affectedCells.items():
            # if all of the vertices in the cell should be moved to new cell 
            # we might as well not move them at all
            if all([vertex in affectedVertices for vertex in cell.elements]):
                continue

            # calculate new indices for the old cell and the new cell
            # and add the new cell to the partition
            # TODO: explain the maths here
            if cell.pre < xCell.pre:
                # the cell we split comes after the cell of x, hence the newCell before cell
                newCell = Cell(deque(vertices), cell.pre, partition.size - cell.pre - len(vertices))
                cell.pre =  cell.pre + len(vertices)
                partition.cells.insert(partition.cells.index(cell), newCell)
            elif cell.pre > xCell.pre:
                # the cell we split comes before the cell of x, hence the newCell after cell
                newCell = Cell(deque(vertices), partition.size - cell.post - len(vertices), cell.post)
                cell.post = cell.post + len(vertices)
                partition.cells.insert(partition.cells.index(cell) + 1, newCell)
            else:
                print("WARNING, your assumption of C_OLD ≠ X was invalid")
                
            
            # lastly: add pointers from vertex to (beginning of) new cell
            # and remove them from their old cell
            for vertex in vertices:
                graph.nodes[vertex]['cell'].elements.remove(vertex)
                graph.nodes[vertex]['cell'] = newCell
                # TODO: I still believe this is redundant but what goes
                graph.nodes[vertex]['cellIdx'] = newCell.elements.index(vertex)


def split(graph: nx.Graph, partition : Partition, xCell : Cell, arcs : list[tuple[int, int]]) -> tuple[list[Cell], list[Cell]]:

    # TODO: is it really necessary to give the buckets here, seems dumb
    # anyway a lot of extra iteration here –– remove
    groupedArcs = bucket_group(arcs, [arc[0] for arc in arcs])
    groupedTwins = bucket_group([(arc[1], arc[0]) for arc in arcs], [arc[1] for arc in arcs])
    
    
    # first pivot so that (potentially) cells not contained in xCell are split
    for arcs in groupedArcs:
        pivot(graph, partition, arcs[0][0], arcs)
    

    # single out cells not contained in xCell
    xCellIdx = partition.cells.index(xCell)
    non_xCells = partition.cells[:xCellIdx] + partition.cells[xCellIdx + 1:]
    

    # then pivot so that (potentially) xCell is split into multiple cells
    # but first we save the vertices that lie in xCell, so that we can
    # find cells contained in xCell after it has been changed
    verticesInxCell = xCell.elements.copy()

    for arcs in groupedTwins:
        pivot(graph, partition, arcs[0][0], arcs)
    
    # single out cells contained in xCell
    cellsInxCell = []
    for cell in partition.cells:
        # suffices to check that one element was in xCell before
        if cell.elements[0] in verticesInxCell:
            cellsInxCell.append(cell)

    return cellsInxCell, non_xCells


def orderedVertexPartition(graph: nx.Graph, partition: Partition, 
                           collectedEdges: set[tuple[int, int]]) -> tuple[Partition, set[tuple[int, int]]]:
    if len(partition.cells) == 1:
        return partition, collectedEdges
    
    # pick non-maximal element of partition
    # TODO: why? is it only for run-time analysis?
    cell = min(partition.cells).copy()

    # Only way I got this to work here is to create subgraphs
    # otherwise the pointers get messed up during the recursive calls
    # TODO: think of other, more efficient, solution?
    edges = edgesFromCell(graph, cell)
    inCell, notInCell = split(graph, partition, cell, edges)
    
    # collect edges, needed to compute quotient G/P(G,v)
    # collectedEdges.extend(edgeRepresentatives(graph, edges, inCell))
    collectedEdges.update(edges)

    # calls to G|cell
    gRestrictToCell = nx.subgraph(graph, cell.elements)
    leftPartition = partition.restrict(gRestrictToCell, inCell)
    leftCall, moreEdges = orderedVertexPartition(gRestrictToCell, leftPartition, collectedEdges)

    collectedEdges.update(moreEdges)

    # calls to G - cell
    gWithoutCell = nx.subgraph(graph, [vertex for vertex in graph if vertex not in cell.elements])
    rightPartition = partition.restrict(gWithoutCell, notInCell)
    rightCall, moreEdges = orderedVertexPartition(gWithoutCell, rightPartition, collectedEdges)
    
    collectedEdges.update(moreEdges)

    leftCall.union(rightCall)

    return leftCall, collectedEdges
