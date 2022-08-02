"""This module provides the dijkstra algorithm."""

__author__ = "Jonas Rinast"

import sys
from queue import PriorityQueue


class DistPrioritizedNode:
    """
    The DijkstraAlgorithm class implements the classic shortest path search in a
    directed graph by Dijkstra on the reduction graph constructed by the
    GraphReductor class.
    """
    def __init__(self, dist, node):
        """Initializes DistPrioritizedNode.

        Args:
            dist: The distance value.
            node: The node.
        """
        self.dist = dist
        self.node = node

    def __lt__(self, other):
        return self.dist < other.dist


class DijkstraAlgorithm:
    """An implementation of the Dijkstra shortest path algorithm."""

    def __init__(self, initial, nodes):
        """
        Initializes the shortest path algorithm. The search looks for paths from
        the given initial location using the graph with the given node set, which
        must be the complete graph node set.

        Args:
            initial: The starting node of the search.
            nodes: The graph nodes to search.
        """
        self.distances = {}
        self.predecessors = {}
        self.transformations = {}
        self.queue_size = len(nodes)
        self.queue = PriorityQueue(maxsize=self.queue_size)
        self.target = None

        for node in nodes:
            distance = 0 if (node == initial) else sys.maxsize
            self.distances[node] = distance
            self.predecessors[node] = None
            self.queue.put(DistPrioritizedNode(distance, node))

    def find_shortest_path(self, target):
        """
        Calculates the shortest path to the given target Node object.

        Args:
            target: The target Node.

        Returns:
            None
        """
        self.target = target

        while not self.queue.empty():
            # print(len(self.queue.queue))
            queue_elem = self.queue.get()
            node = queue_elem.node
            dist = queue_elem.dist
            # dist = self.distances[node]

            # finished or no path available
            if (node == target) or (dist == sys.maxsize):
                return

            for edge in node.get_edges():
                neighbor = edge.get_target()

                if dist + 1 < self.distances[neighbor]:
                    self.distances[neighbor] = dist + 1
                    self.transformations[neighbor] = edge.get_transformation()
                    self.predecessors[neighbor] = node
                    old_queue = self.queue
                    self.queue = PriorityQueue(maxsize=self.queue_size)
                    while not old_queue.empty():
                        old_queue_elem = old_queue.get()
                        if old_queue_elem.node != neighbor:
                            self.queue.put(old_queue_elem)
                    self.queue.put(DistPrioritizedNode(dist + 1, neighbor))
                    # self.queue.remove(neighbor)
                    # self.queue.add(neighbor)

    def get_shortest_path(self, path):
        """
        Getter for the shortest path through the graph from the initial to the
        target Node object. Note that this method clears the given List container
        and then adds the Transformation objects.

        Args:
            path: the Transformation object sequence from the initial to the target Evaluation object.
        """
        current = self.target

        path.clear()
        while self.predecessors.get(current) is not None:
            path.insert(0, self.transformations[current])
            current = self.predecessors[current]

    # def compare(self, node1, node2):
    #     return self.distances[node1] - self.distances[node2]
