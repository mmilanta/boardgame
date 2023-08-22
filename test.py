class Node:
    def __init__(self, row: int, col: int, edges, connecting_border):
        self.row = row
        self.col = col
        self.connecting_border = connecting_border
        # 1 if its connected to left border
        # -1 if its connected to right border 0 otherwise
        self.edges = edges


class Graph:
    def __init__(self) -> None:
        self.nodes = []

    def append_node(self, node: Node) -> None:
        for n in self.nodes:
            if connect(n, node):
                if link(n, node):
                    return True
        return False


def link(node1: Node, node2: Node):
    if node1.connecting_border * node2.connecting_border == -1:
        return True
    if node1.connecting_border == node2.connecting_border:
        return False
    if node1.connecting_border == 0 and node2.connecting_border != 0:
        node1.connecting_border = 1
        for node_it in node1.edges:
            link(node1, node_it)


def connect(node1: Node, node2: Node):
    return abs(node1.row - node2.row) <= 1 and abs(node1.col - node2.col) <= 1


class Solution(object):
    def latestDayToCross(self, row, col, cells):
        """
        :type row: int
        :type col: int
        :type cells: List[List[int]]
        :rtype: int
        """
        graph = Graph()
        count = 0
        for cell in cells:
            if cell[1] == 0:
                connecting_border = 1
            if cell[1] == col - 1:
                connecting_border = -1
            if graph.append_node(Node(cell[0],
                                      cell[1],
                                      [],
                                      connecting_border)):
                return count
            count += 1
