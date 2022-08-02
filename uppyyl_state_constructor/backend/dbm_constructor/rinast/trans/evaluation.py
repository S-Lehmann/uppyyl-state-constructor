"""This module provides an evaluation."""

__author__ = "Jonas Rinast"

from ..dbm.db_value import (
    DBValue
)


class Projector:
    """
    The Projector class is a helper class to project an Evaluation object to
    fewer elements. It provides an Enumeration to cycle through the projected
    values and it allows to compare the projected Evaluation object to
    another Evaluation object.
    """

    def __init__(self, variables, values):
        """Initializes Projector.

        Args:
            variables: The input variables.
            values: The projected values.
        """
        self.variables = variables
        self.current = 0
        self.values = values

        variables.sort()

    def has_more_elements(self):
        """Checks if the iterator has more elements.

        Returns:
            The checking result.
        """
        return self.current < len(self.variables)

    def next_element(self):
        """Gets the next iterator element.

        Returns:
            The next iterator element.
        """
        ret = self.values[self.variables[self.current]]
        self.current += 1
        return ret

    def compare(self, evaluation):
        """
        Compares the project Evaluation object to the given Evaluation
        object.

        Args:
            evaluation: The Evaluation object to compare to.

        Returns:
            Indication of whether the projected Evaluation is equal.
        """
        if evaluation.get_size() != len(self.variables):
            return False
        for i in range(0, len(self.variables)):
            if evaluation.get_evaluation(i) != self.values[self.variables[i]]:
                return False
        return True


class Evaluation:
    """
    The Evaluation class is a data class representing a vector of elements of the
    given type parameter. It is meant to identify states in a transformation
    system defined by a TransformationSystem object.

    The Evaluation class requires the underlying type to have a copy constructor
    and an equality relation equals(Object obj).

    Fresh instances of the Evaluation class should generally only be obtained
    using the createEvaluation() method of the associated
    TransformationSystem object to prevent conflicts of vector lengths.
    """

    def __init__(self, evaluation=None, variable_count=None):
        """Initializes Evaluation.

        Args:
            evaluation: The input evaluation.
            variable_count: The number of variables.
        """
        if evaluation is not None:
            self.values = []
            for i in range(0, len(evaluation.values)):
                self.values.append(DBValue(other=evaluation.values[i]))
        elif variable_count is not None:
            self.values = [None] * variable_count

    def get_evaluation(self, i):
        """Gets the evaluation of a value at index i.

        Args:
            i: The value index.

        Returns:
            The evaluation of a value at index i.
        """
        return self.values[i]

    def get_size(self):
        """Gets the number of values.

        Returns:
            the number of values.
        """
        return len(self.values)

    def get_projector(self, indices):
        """
        Getter for a Projector object that projects the Evaluation object onto
        the vector elements identified by the indices in the given array.

        Note that the order of the indices in the array does not matter for the
        projection. The following two arrays produce the same Projector object:
        "int[] indices1 = new int[] 1, 2"
        "int[] indices1 = new int[] 2, 1"

        Args:
            indices: The array containing the indices of the elements to project on.

        Returns:
            The Projector object projecting the Evaluation.
        """
        return Projector(indices, self.values)

    def set_evaluation(self, i, value):
        """Sets the evaluation of the value at index i.

        Args:
            i: The value index.
            value: The new value.
        """
        self.values[i] = value

    def project(self, indices):
        """
        Projects the current Evaluation onto the elements identified by the
        indices in the given array.

        Note that calling "project()" modifies the original Evaluation
        object and loses information. If you require the values projected away
        later on use a Projector object "getProjector()".

        Args:
            indices: The array containing the indices of the elements to project on.
        """
        new_values = []
        projector = self.get_projector(indices)
        i = 0

        while projector.has_more_elements():
            new_values.append(DBValue(other=projector.next_element()))
            i += 1

        self.values = new_values

    def __hash__(self):
        prime = 31
        result = 1
        result = prime * result + hash(tuple(self.values))
        return result

    def __eq__(self, other):
        if isinstance(other, Evaluation):
            if self.values == other.values:
                return True
        return False

    def __str__(self):
        string = ""
        string += "[EVALUATION] { "

        for i in range(0, len(self.values)):
            string += str(self.values[i])
            string += " "
        string += "}"

        return string
