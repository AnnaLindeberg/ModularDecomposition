from __future__ import annotations

class ListNode:
    def __init__(self, data : Vertex):
        self.data = data
        self.next : ListNode | None = None
        self.previous : ListNode | None = None
    
    def __str__(self) -> str:
        # VERY verbose version
        # pre = self.previous.data if self.previous is not None else None
        # post = self.next.data if self.next is not None else None
        # return f"Node[{self.data}, pre {pre}, post {post}]"
        return f"[{self.data}]"

class DL_list:
    '''
    Primitive doubly linked list of ListNode elements
    '''
    def __init__(self, nodes: list[ListNode] | None =None) -> None:
        self.head = None
        if nodes is not None:
            node = ListNode(data=nodes.pop(0))
            self.head = node
            for elem in nodes:
                node.next = ListNode(data=elem)
                node.next.previous = node
                node = node.next
    
    def __iter__(self):
        node = self.head
        while node is not None:
            yield node
            node = node.next
    
    def __str__(self) -> str:
        s = ""
        for el in self:
            s += str(el) + ' -- '
        return s[:-4]

    def __repr__(self) -> str:
        return str(self)
    
    def __contains__(self, vertex: Vertex):
        for node in self:
            if node.data == vertex:
                return True
        return False
    
    def prepend(self, node):
        node.next = self.head
        if self.head is not None:
            self.head.previous = node
        self.head = node
    
    def reverse(self):
        current = self.head
        last = current
        while current is not None:
            tmp = current.previous
            current.previous = current.next
            current.next = tmp

            last = current
            current = current.previous

        self.head = last            

# l = DL_list([1,2,3,4,5])
# print(l)
# l.reverse()
# print(l)

class Cell:
    def __init__(self, elements : DL_list, pre : int, post: int) -> None:
        #DL_list of elements
        self.elements = elements
        # integers counting elements before/after this cell, more concretely:
        # pre = (sum of cardinalities of cells before this cell) + 1
        # post = (sum of cardinalities of cells after this cell) - 1
        self.pre = pre
        self.post = post
    
    def __hash__(self):
        return hash((self.pre, self.post))
    
    def __str__(self) -> str:
        return f"Cell {self.elements} with indices {self.pre, self.post}"

    def __repr__(self) -> str:
        return str(self)
    
    def __lt__(self, otherCell) -> bool:
        # assumes cells are part of same partition
        return self.pre < otherCell.pre

    def __contains__(self, vertex : Vertex):
        return vertex in self.elements

    def elementsAsList(self):
        '''
        returns elements as python list instead of DL_list
        '''
        res = []
        for vertex in self.elements:
            res.append(vertex.data)
        
        return res

class Partition:
    '''
    Partition of vertices
    '''
    def __init__(self, cells : list[Cell], size : int) -> None:
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
    
    def restrict(self, cells : list[Cell]) -> Partition:
        '''
        Returns new partition ("deep copied" – all underlying vertices etc are new instances)
        restricted to the given cells. In particular the edges in the adjacency list of the
        given cells' vertices are restricted so that both endpoints lie in one of the given cells.
        '''
        vertices = []
        for cell in cells:
            vertices.extend(cell.elementsAsList())

        # create copies of vertices, initially with no adjacencies
        newVertices = {}
        for vertex in vertices:
            newVertices[vertex.label] = Vertex(label= vertex.label)
        
        # copy arcs
        for vertex in vertices:
            newVertex = newVertices[vertex.label]
            for arc in vertex.adj:
                if arc.y not in vertices:
                    continue
                newEndPoint = newVertices[arc.y.label]
                newArc = Arc(newVertex, newEndPoint)
                newVertex.adj.append(newArc)

                # if the twin arc has been created, we can link them
                possibleTwinArc = newEndPoint.findArc(newVertex)
                if possibleTwinArc is not None:
                    possibleTwinArc.twin = newArc
                    newArc.twin = possibleTwinArc
        
        # copy cells – here I assume the cells are given in the order they should appear
        # since I don't want to think about how complicated it gets otherwise
        newPartitionSize = len(vertices)
        newCells = []
        preCount = 1
        for cell in cells:
            tmp = cell.elementsAsList()
            newCell = Cell(DL_list([newVertices[v.label] for v in tmp]), preCount, newPartitionSize - preCount - len(tmp))
            newCells.append(newCell)
            preCount += len(tmp)

            # lastly add pointers from the new vertices to their cell and cell position
            for node in newCell.elements:
                node.data.cell = newCell
                node.data.cellPos = node

        return Partition(newCells, newPartitionSize)
    
    def union(self, partition):
        '''
        Extends this partition by adding the given cells at 'the end' of this partition
        '''
        for cell in self.cells:
            cell.post += partition.size

        for cell in partition.cells:
            cell.pre += self.size
            self.cells.append(cell)
        
        self.size += partition.size

                

class Vertex:
    '''
    Vertex of LWGraph. Stores (unique, integer) vertex identifier under label,
    an adjacency list of arcs starting at this vertex. 
    and pointers to the current cell (first position of cell, and the vertex's own position).
    '''
    def __init__(self, label: int) -> None:
        self.label = label
        self.cell : Cell = None
        self.cellPos : ListNode = None
        self.adj : list[Vertex] = []
    
    def __repr__(self) -> str:
        return f"vertex {self.label}"
    
    def __hash__(self):
        return hash(self.label)
    
    def __eq__(self, other: Vertex) -> bool:
        # the best I can think of honestly
        return self.label == other.label
    
    def findArc(self, arcTo : Vertex) -> Arc | None:
        for arc in self.adj:
            if arc.y == arcTo:
                return arc
        
        return

class Arc:
    '''
    Arc ie directed edge (x,y) of graph. Stores endpoints x and y, and a pointer to
    its "twin" arc (y,x).
    '''
    def __init__(self, x : Vertex, y  : Vertex) -> None:
        self.x = x
        self.y = y
        self.twin : Arc = None
    
    def __str__(self) -> str:
        return f"({self.x}, {self.y})"
    
    def __repr__(self) -> str:
        return str(self)
    
    def __eq__(self, other: Arc) -> bool:
        return self.x == other.x and self.y == other.y

class LWGraph:
    '''
    Light Weight graph representation as needed for modular decomposition in
    O(n+m*log(n)) time. Stores list of vertices, where each Vertex keeps tracks of
    its own adjacencies. Moreover, the graph stores a partition of its vertices
    '''
    def __init__(self, vertices, partition) -> None:
        self.vertices = vertices
        self.partition = partition
    
    def inducedSubGraph(vertexSet):
        '''Returns induced subgraph on given vertexSet as a new LWGraph instance. The underlying
        partition is kept, containing only the vertices of the subgraph.'''
        pass
