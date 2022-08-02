"""This module provides a simple transformation."""

__author__ = "Jonas Rinast"

import abc

from .info_transformation import (
    InfoTransformation
)
from .evaluation import (
    Evaluation
)


class SpecificationMapping(abc.ABC):
    """
    The SpecificationMapping interface specifies a single mapping function:
    t_1, t_2, ..., t_N -> t, where t_1, ..., t_n, t of type T
    """

    @abc.abstractmethod
    def map(self, parameters):
        """Maps the function to the parameters.

        Args:
            parameters: The list of parameters.

        Returns:
            None
        """
        pass


class SpecificationEntry:
    """
    The SpecificationEntry class specifies how a SpecificationMapping is
    applied to a variable:
    variable = map(getParameters(parameters))
    where parameters is a list of indices into an Evaluation object.
    """

    def __init__(self, variable, parameters, mapping):
        """initializes SpecificationEntry.

        Args:
            variable: The target variable.
            parameters: The list of indices into an Evaluation object.
            mapping: The specification mapping.
        """
        self.variable = variable
        self.parameters = parameters
        self.mapping = mapping

    def get_parameters(self, evaluation):
        """
        Getter for the parameters for a {@code map()} call depending on the
        provided Evaluation indices and the given Evaluation object.

        Args:
            evaluation: The evaluation to retrieve the parameters from.

        Returns:
            The array with the parameter values.
        """
        ret = [None] * len(self.parameters)
        for i in range(0, len(self.parameters)):
            ret[i] = evaluation.get_evaluation(self.parameters[i])
        return ret


class SimpleTransformation(InfoTransformation):
    """
    The SimpleTransformation class defines a transformation by providing mapping
    functions that are applied to individual variables.

    Note that a SimpleTransformation object can not be instantiated by clients
    directly. To obtain a clean instance, query a TransformationSystem object by
    calling "createSimpleTransformation()".
    """

    def __init__(self, variable_domain):
        """Initializes SimpleTransformation.

        Args:
            variable_domain: The variable domain.
        """
        super().__init__()
        self.variableDomain = variable_domain
        self.specificationSet = []

    def add_specification_entry(self, variable, parameters, mapping):
        """
        Creates and inserts a new SpecificationEntry object for this
        SimpleTransformation object. Call this function (repeatedly) to define
        the desired transformational behavior.

        Args:
            variable: The index of the variable to write.
            parameters: An array of the indices of the variables to map.
            mapping: The mapping to calculate the new value.
        """
        self.specificationSet.append(SpecificationEntry(variable, parameters, mapping))

    def apply(self, evaluation):
        """
        Applies the transformation to the provided Evaluation object. The
        provided Evaluation object may not be modified, a copy should be
        returned.

        Args:
            evaluation: The Evaluation object to transform.

        Returns:
            The transformed Evaluation object.
        """
        result = Evaluation(evaluation=evaluation)

        for e in self.specificationSet:
            result.set_evaluation(e.variable, e.mapping.map(e.get_parameters(evaluation)))
        return result

    def get_read_set(self):
        """
        Getter for a set of variables read by the Transformation object when
        applied. The set contains the indices into the Evaluation object vector.

        Returns:
            The indices set of variables read.
        """
        reads = set()
        for e in self.specificationSet:
            for i in range(0, len(e.parameters)):
                reads.add(e.parameters[i])
        return reads

    def get_write_set(self):
        """
        Getter for a set of variables written by the Transformation object when
        applied. The set contains the indices into the Evaluation object vector.

        Returns:
            The indices set of variables written.
        """
        writes = set()
        for e in self.specificationSet:
            writes.add(e.variable)
        return writes

    def __hash__(self):
        prime = 31
        result = 1
        result = prime * result + (0 if (self.specificationSet is None) else sum(map(hash, self.specificationSet)))
        return result

    def __eq__(self, other):
        if isinstance(other, SimpleTransformation):
            if self.specificationSet == other.specificationSet:
                return True
        return False

    def __str__(self):
        string = ""
        string += "[TRANSFORMATION] { "

        for s in self.specificationSet:
            string += 'x'
            string += str(s.variable)
            string += " = "
            string += str(s.mapping)
            string += '('
            string += str(s.parameters)
            string += ") "
        string += '}'

        return string
