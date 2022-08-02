"""This module provides a graph reductor."""

__author__ = "Jonas Rinast"

from .dijkstra_algorithm import (
    DijkstraAlgorithm
)
from .edge import (
    Edge
)
from .node import (
    Node
)
from ..reductor import (
    Reductor
)
from ...evaluation import (
    Evaluation
)


class Projection:
    """
    The Projection class is a data class used to store a projection. A
    Projection object is characterized by the indices of the elements in the
    Evaluation objects that are projected and a resulting projected
    Evaluation object.
    """

    def __init__(self, variables, projection):
        """Initializes Projection.

        Args:
            variables: The variables of the projection.
            projection: The resulting projected evaluation object.
        """
        self.variables = variables
        self.projection = projection

    def __hash__(self):
        prime = 31
        result = 1
        result = prime * result + (0 if (self.projection is None) else hash(self.projection))
        result = prime * result + hash(tuple(self.variables))
        return result

    def __eq__(self, other):
        if isinstance(other, Projection):
            if self.projection == other.projection and self.variables == other.variables:
                return True
        return False


class GraphReductor(Reductor):
    """
    The GraphReductor class implements a reduction algorithm based on an
    reduction graph. The reduction graph captures which Evaluation objects may be
    obtained by the application of a Transformation object to all preceding
    Evaluation objects. Projects are used to calculate the applicability of
    Transformation objects.

    The reduction graph allows a shortest path search to find all Transformation
    objects required to reach the final Evaluation object. All objects not on
    that path may be removed.
    """

    def __init__(self):
        """Initializes GraphReductor."""
        self.evaluations = {}
        self.projections = {}
        self.system = None
        self.dijkstra = None
        self.initialNode = None
        self.currentNode = None

    def initialize(self, system, initial_evaluation):
        """
        Initializes the Reductor object. The Reductor reduces Transformation
        sequences obtained from the given TransformationSystem object. The given
        Evaluation object is the first object of the sequence to reduce.

        Args:
            system: The TransformationSystem object.
            initial_evaluation: The initial Evaluation object.
        """
        self.system = system
        self.currentNode = Node(initial_evaluation)
        self.initialNode = self.currentNode
        self.evaluations[initial_evaluation] = self.currentNode

    def apply(self, evaluation, transformation, transformed_evaluation):
        """
        Instructs the Reductor that a Transformation object has been applied to
        the current Evaluation object. Note that a call to "apply()" may
        invalidate subsequent calls to "getPath()".

        Args:
            evaluation: The Evaluation object the Transformation object was applied to.
            transformation: The Transformation object that was applied.
            transformed_evaluation: the Evaluation object resulting from the Transformation application.
        """
        target = self.evaluations.get(transformed_evaluation)

        if target is None:
            target = Node(transformed_evaluation)
            self.evaluations[transformed_evaluation] = target

        edge = Edge(transformation, target)
        self.currentNode.add_edge(edge)

        projected = Evaluation(evaluation=self.system.get_current_evaluation())
        variable_set = self.system.get_variable_set()
        for w in transformation.get_write_set():
            variable_set.discard(w)
        for r in transformation.get_read_set():
            variable_set.add(r)
        variables = [0] * len(variable_set)

        i = 0
        for val in variable_set:
            variables[i] = val
            i += 1
        projected.project(variables)

        for key, value in self.evaluations.items():
            if key.get_projector(variables).compare(projected):
                value.add_edge(edge)

        for key, value in self.projections.items():
            if transformed_evaluation.get_projector(key.variables).compare(key.projection):
                target.add_edge(value)

        self.projections[Projection(variables, projected)] = edge
        self.currentNode = target

    def eliminate(self):
        """
        Instructs the Reductor to eliminate unnecessary Transformation objects in
        the Transformation sequence established using "apply()". Thereby
        validating subsequent calls to "getPath()".
        """
        self.dijkstra = DijkstraAlgorithm(self.initialNode, self.evaluations.values())
        self.dijkstra.find_shortest_path(self.currentNode)

    def get_path(self):
        """
        Getter for the resulting reduced Transformation object sequence. Always
        returns a fresh List object. Be aware of timing constraints for calling
        "getPath()" as it may not return the most recent result.
        """
        path = []
        self.dijkstra.get_shortest_path(path)
        return path

    def __str__(self):
        string = ""
        string += "[GRAPHREDUCTOR] {\n"

        for n in self.evaluations.values():
            string += '\t'
            if n == self.initialNode:
                string += "[INITIAL] "
            if n == self.currentNode:
                string += "[CURRENT] "
            string += str(n)
            string += '\n'

        string += '}'

        return string
