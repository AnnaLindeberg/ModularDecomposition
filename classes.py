from __future__ import annotations
from collections import deque
import networkx as nx

class Cell:
    def __init__(self, elements: deque[int], pre: int, post: int) -> None:
        # deque of elements – doubly linked list
        self.elements = elements
        # integers counting elements before/after this cell, more concretely:
        # pre = (sum of cardinalities of cells before this cell) + 1
        # post = (sum of cardinalities of cells after this cell) - 1
        # hence we have (for each cell) that  pre + post + cardinality(cell) = no. of nodes in underlying graph
        self.pre = pre
        self.post = post
    
    def __hash__(self):
        return hash((self.pre, self.post))
    
    def __str__(self) -> str:
        # return f"Cell {self.elements} with indices {self.pre, self.post}"
        return f"Cell{str(self.elements)[6:-1]}"

    def __repr__(self) -> str:
        return str(self)
    
    def __lt__(self, otherCell: Cell) -> bool:
        # assumes cells are part of same partition
        return self.pre < otherCell.pre

    def __contains__(self, vertex: int):
        return vertex in self.elements
    
    def __eq__(self, other: Cell) -> bool:
        return self.elements == other.elements and self.pre == other.pre and self.post == other.post
    
    def copy(self) -> Cell:
        '''
        Returns a copy of this cell, including a (shallow) copy of its list of elements. 
        '''
        elemCopy = self.elements.copy()
        return Cell(elemCopy, self.pre, self.post)

class Partition:

    def __init__(self, cells: list[Cell], size: int) -> None:
        '''
        
        '''
        self.cells = cells
        #no of nodes in partition ie in G
        self.size = size
    
    def __str__(self) -> str:
        s = f"Partition of size {self.size} with cells:\n"
        for cell in self.cells:
            s += str(cell) + '\n'
        return s
    
    def __repr__(self) -> str:
        return str(self)
    
    def __contains__(self, cell: Cell) -> bool:
        return cell in self.cells
    
    def restrict(self, graph: nx.Graph, cells: list[Cell]) -> Partition:
        '''
        Returns new partition restricted to copies of the given cells. 
        In particular, if all cells of the partition is given as input, a copy of the partition is given.
        '''
        # find size of new partition
        newPartitionSize = 0
        for cell in cells:
            newPartitionSize += len(cell.elements)
        
        # copy cells – here I assume the cells are given in the order they should appear
        # since I don't want to think about how complicated it gets otherwise
        newCells = []
        preCount = 1
        for cell in cells:
            newCell = cell.copy()

            newCell.pre = preCount
            newCell.post = newPartitionSize - preCount - len(newCell.elements)

            newCells.append(newCell)
            preCount += len(newCell.elements)

            # lastly add pointers from the new vertices to their cell and cell position
            for cellIdx, vertex in enumerate(cell.elements):
                graph.nodes[vertex]['cell'] = newCell
                graph.nodes[vertex]['cellIdx'] = cellIdx

        return Partition(newCells, newPartitionSize)
    
    def union(self, partition):
        '''
        Extends this partition by adding the given cells at 'the end' of this partition
        '''
        # update indices of existing cells
        for cell in self.cells:
            cell.post += partition.size

        # add the given cells with updated indices
        for cell in partition.cells:
            cell.pre += self.size
            self.cells.append(cell)
        
        self.size += partition.size

    def createCell(self, graph: nx.Graph, vertex: int) -> None:
        '''
        Takes a vertex in the partition and puts it in its own cell.
        Usually called when the partition has a single cell, singling out
        a single-vertex cell. 
        '''
        currentCell = graph.nodes[vertex]['cell']

        # vertex already in its own cell
        if len(currentCell.elements) == 1:
            return
        
        # remove vertex from current cell
        currentCell.elements.remove(vertex)

        # update indices of cells
        for cell in self.cells:
            if cell.pre < currentCell.pre:
                cell.pre += 1
                cell.post -= 1
        
        currentCell.pre += 1

        # then, at last, create the new cell.
        newCell = Cell(deque([vertex]), 1, self.size - 2)
        graph.nodes[vertex]['cell'] = newCell
        self.cells = [newCell] + self.cells
    
    def flatList(self, reversed=False) -> list(int):
        '''
        Returns list of vertices in partition, ordered as they appear in the partition.
        '''
        res = []
        for cell in self.cells:
            for v in cell.elements:
                res.append(v)
        
        if reversed:
            res.reverse()

        return res
