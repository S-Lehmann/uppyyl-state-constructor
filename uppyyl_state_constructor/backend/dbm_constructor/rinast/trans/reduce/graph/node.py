"""This module provides a node."""

__author__ = "Jonas Rinast"


class Node:
    """
    The Node class is a node in the reduction graph of the GraphReductor class.
    It is associated with an Evaluation object, which the Node object represents
    and a set of Edge objects that specify which other Node objects, respectively
    Evaluation objects, may be reached.
    """

    def __init__(self, evaluation):
        """Initializes Node.

        Args:
            evaluation: The evaluation object.
        """
        self.evaluation = evaluation
        self.edges = set()

    def add_edge(self, edge):
        """Adds an edge to the node.

        Args:
            edge: The edge object.
        """
        self.edges.add(edge)

    def get_edges(self):
        """Gets the edges of the node.

        Returns:
            The edges.
        """
        return self.edges

    def get_evaluation(self):
        """Gets the evaluation.

        Returns:
            The evaluation.
        """
        return self.evaluation

    def __hash__(self):
        prime = 31
        result = 1
        result = prime * result + (0 if (self.evaluation is None) else hash(self.evaluation))
        return result

    def __eq__(self, other):
        if isinstance(other, Node):
            if self.evaluation == other.evaluation:
                return True
        return False

    def __str__(self):
        string = ""
        string += "[NODE] {"

        string += str(self.evaluation)
        string += "} {\n"

        for edge in self.edges:
            string += "\t\t"
            string += str(edge)
            string += "\n"
        string += "\t}"

        return string
