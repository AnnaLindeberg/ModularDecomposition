from classes import *

def bucket_group(arcs : list[Arc], buckets : list[Vertex]) -> list[list[Arc]]:
    '''
    Bucket group the given arcs into the given buckets: i.e. return a semi-sorted 
    version of arcs where arcs with the same first coordinate appear consecutive.
    These groups are not necessarily sorted.

    arcs: list of arcs with integer coordinates
    buckets: list of all integers that will appear as a first coordinate of an arc in arcs
    '''
    buckets = {bucket:[] for bucket in buckets}
    for arc in arcs:
        buckets[arc.x].append(arc)
    
    # now all arcs are properly grouped, bring together in list of lists
    res = []
    for group in buckets.values():
        res.append(group)
    
    return res

def arcsFromCell(cell : Cell) -> list[Arc]:
    '''
    Takes cell C and returns arcs (x,y) where x lies in C, y does not.
    '''
    # use more convenient data structure
    vertices = cell.elementsAsList()
    arcs = []
    for vertex in vertices:
        for neighbor in vertex.adj:
            if neighbor.y not in vertices:
                arcs.append(neighbor)
    
    return arcs


def pivot(partition, x, arcs):
        ''' 
        Pivot at given vertex x. Variable arcs should contain list of all arcs (x,y) where y
        lies in some cell of a pre-decided subset Q of the underlying partition. 
        After pivoting, the partition will be refined so that every module contained in a cell of 
        the partition is still contained in a single cell of the refined partition. Additionally,
        any cell of the refined partition contained in a member of Q will consist of only neighbors
        or only non-neighbors of x. 
        '''
        # TODO: break into smaller pieces of code
        affectedCells = {}
        affectedVertices = set()
        for arc in arcs:
            affectedVertices.add(arc.y)
            yCell = arc.y.cell
            if yCell in affectedCells:
                affectedCells[yCell].append(arc.y)
            else:
                affectedCells[yCell] = [arc.y]
        

        xCell = x.cell
        for cell, vertices in affectedCells.items():
            # if all of the vertices in the cell should be moved to new cell 
            # we might as well not move them at all
            if all([vertex.data in affectedVertices for vertex in cell.elements]):
                continue

            newCellElements = DL_list()
            for vertex in cell.elements:
                if vertex.data not in vertices:
                    continue
                # add vertex to new cell
                newNode = ListNode(data = vertex.data)
                vertex.cellPos = newNode
                newCellElements.prepend(newNode)
                # change pointers from cell vertex was previously in i.e. remove vertex
                if vertex.previous is not None:
                    vertex.previous.next = vertex.next
                if vertex.next is not None:
                    vertex.next.previous = vertex.previous
                if cell.elements.head == vertex:
                    cell.elements.head = vertex.next
            
            # to keep vertices in the same order as before, reverse
            newCellElements.reverse() 
            
            # calculate new indices for the old cell and the new cell
            # and add the new cell to the partition
            # TODO: explain the maths here
            if cell.pre < xCell.pre:
                # the cell we split comes before the cell of x, hence the newCell after cell
                newCell = Cell(newCellElements, partition.size - cell.post - len(vertices), cell.post)
                cell.post = cell.post + len(vertices)
                partition.cells.insert(partition.cells.index(cell) + 1, newCell)
            elif cell.pre > xCell.pre:
                # the cell we split comes after the cell of x, hence the newCell before cell
                newCell = Cell(newCellElements, cell.pre, partition.size - cell.pre - len(vertices))
                cell.pre =  cell.pre + len(vertices)
                partition.cells.insert(partition.cells.index(cell), newCell)
            else:
                print("WARNING, your assumption of C_OLD ≠ X was invalid")
            
            # did you move all vertices ie cell is now empty? then remove it
            if cell.pre + cell.post == partition.size:
                partition.cells.remove(cell)

            # lastly: add pointers from vertex to (beginning of) new cell
            for vertex in vertices:
                vertex.cell = newCell

def split(partition : Partition, xCell : Cell, arcs : list[Arc]) -> tuple[Partition, Partition]:
    # TODO: is it really necessary to give the buckets here, seems dumb
    # anyway a lot of extra iteration here –– remove
    groupedArcs = bucket_group(arcs, [arc.x for arc in arcs])
    groupedTwins = bucket_group([arc.twin for arc in arcs], [arc.twin.x for arc in arcs])
    for arcs in groupedArcs:
        pivot(partition, arcs[0].x, arcs)
    
    cellIdx = partition.cells.index(xCell)
    rightPartition = partition.restrict(partition.cells[:cellIdx] + partition.cells[cellIdx + 1:])
    
    xCellLabels = [node.data.label for node in xCell.elements]

    for arcs in groupedTwins:
        pivot(partition, arcs[0].x, arcs)
    
    cellsToKeep = []
    for cell in partition.cells:
        if cell.elements.head.data.label in xCellLabels:
            cellsToKeep.append(cell)
    leftPartition = partition.restrict(cellsToKeep)

    return leftPartition, rightPartition

    
def orderedVertexPartition(partition : Partition) -> Partition:
    if len(partition.cells) == 1:
        return partition
    
    # pick non-maximal element of partition
    # TODO: why? is it only for run-time analysis?
    cell = min(partition.cells)
    arcs = arcsFromCell(cell)
    left, right = split(partition, cell, arcs)
    
    combined = orderedVertexPartition(left)
    combined.union(orderedVertexPartition(right))
    return combined
