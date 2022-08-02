"""This module provides an edge."""

__author__ = "Jonas Rinast"


class Edge:
    """
    The Edge class is an edge in the reduction graph of the GraphReductor class.
    It is associated with a Transformation object, which the Edge object represents
    and a Node object, which is the target of the edge.
    """

    def __init__(self, transformation, target):
        self.transformation = transformation
        self.target = target

    def get_target(self):
        """Gets the edge target.

        Returns:
            The edge target.
        """
        return self.target

    def get_transformation(self):
        """Gets the evaluation.

        Returns:
            The evaluation.
        """
        return self.transformation

    def __hash__(self):
        prime = 31
        result = 1
        result = prime * result + (0 if (self.target is None) else hash(self.target))
        result = prime * result + (0 if (self.transformation is None) else hash(self.transformation))
        return result

    def __eq__(self, other):
        if isinstance(other, Edge):
            if self.target == other.target and self.transformation == other.transformation:
                return True
        return False

    def __str__(self):
        string = ""
        string += "[EDGE] {"

        string += str(self.target.get_evaluation())
        string += ' '
        string += str(self.transformation)
        string += '}'

        return string
