"""This module provides the transformation system."""

__author__ = "Jonas Rinast"

from .compound_transformation import (
    CompoundTransformation
)
from .evaluation import (
    Evaluation
)
from .reduce.identity_reductor import (
    IdentityReductor
)
from .simple_transformation import (
    SimpleTransformation
)


class TransformationSystem:
    """
    The TransformationSystem class allows specification of a general
    transformation system and maintains a transformation sequence of that system.
    A state of the transformation system is a vector of elements of the type
    provided in the type argument.

    The TransformationSystem class feeds the transformation sequence to a given
    Reductor object while constructing the sequence and thus allows to retrieve
    the reduced sequence of Transformation objects if desired.
    """

    def __init__(self, variable_count, variable_domain, reductor=None):
        """Initializes TransformationSystem.

        Creates a new TransformationSystem where a state is a vector of size
        variable_count where each element is of type
        variable_domain. The supplied Reductor object is used to reduce
        transformation sequences created with this TransformationSystem object.

        Args:
            variable_count: The number of variables in a state.
            variable_domain: The type of the state variables.
            reductor: The Reductor object to reduce the transformation sequence.
        """
        self.variableCount = variable_count
        self.variableDomain = variable_domain
        self.variableSet = set()

        for i in range(0, variable_count):
            self.variableSet.add(i)

        self.invalidated = True
        self.reductor = reductor if reductor else IdentityReductor()
        self.currentEvaluation = None
        self.transCount = 0

    def create_evaluation(self):
        """
        Creates a new Evaluation object with the correct size and type for usage
        with the TransformationSystem object.

        Returns:
            A new Evaluation object.
        """
        return Evaluation(variable_count=self.variableCount)

    def create_simple_transformation(self):
        """
        Creates a new SimpleTransformation object for use with the
        TransformationSystem object.

        Returns:
            A new SimpleTransformation object.
        """
        return SimpleTransformation(self.variableDomain)

    @staticmethod
    def create_compound_transformation():
        """
        Creates a new CompoundTransformation object for use with the
        TransformationSystem object.

        Returns:
            A new CompoundTransformation object.
        """
        return CompoundTransformation()

    def set_initial_evaluation(self, initial_evaluation):
        """
        Sets the initial Evaluation when constructing a sequence of Evaluation
        objects by applying Transformation objects.

        Args:
            initial_evaluation: the initial Evaluation object.

        Returns:
            None
        """
        self.currentEvaluation = initial_evaluation
        self.reductor.initialize(self, initial_evaluation)

    def apply_transformation(self, transformation):
        """
        Extends the current transformation sequence by applying the given
        Transformation object to the current Evaluation object. Feeds the results
        to the Reduction object if applicable.

        Args:
            transformation: the Transformation object to apply to the current Evaluation object.

        Returns:
            None
        """
        result = transformation.apply(self.currentEvaluation)
        self.reductor.apply(self.currentEvaluation, transformation, result)
        self.currentEvaluation = result
        self.transCount += 1
        self.invalidated = True

    def set_reductor(self, reductor):
        """
        Sets the Reductor object used to reduce a transformation sequence
        generated with this TransformationSystem object.<br>

        Note that a call to "setReductor()" while generating a sequence
        will probably break the reduction procedure. Thus, after setting the
        Reductor object call "setInitialEvaluation()" to reset the sequence
        and initialize the Reductor object. You probably will want to construct
        the correct TransformationSystem object directly.

        Args:
            reductor: The Reductor object to use from now on.
        """
        self.reductor = reductor

    def get_reductor(self):
        """
        Getter for the underlying Reductor object. All handling of the reduction
        is done by the TransformationSystem object, thus take care when accessing
        the Reductor object. You will probably want to use this to output
        Reductor information using the "toString()" method of the Reductor
        object.

        Returns:
            The Reductor used by the TransformationSystem object.
        """
        return self.reductor

    def get_current_evaluation(self):
        """
        Getter for the current Evaluation object, i.e., the Evaluation object at
        the end of the produced sequence.

        Returns:
            The current Evaluation object.
        """
        return self.currentEvaluation

    def get_variable_count(self):
        """
        Getter for the number of variables a state in this transformation system
        has.

        Returns:
            The number of variables of a state.
        """
        return self.variableCount

    def get_variable_domain(self):
        """
        Getter for the class, i.e., domain, of the state variable in this
        transformation system.

        Returns:
            The class of the state variables.
        """
        return self.variableDomain

    def get_variable_set(self):
        """
        A utility function returning a Set containing the natural numbers from 0
        to "getVariableCount()". Useful when eliminating individual
        variables for projecting states.

        Returns:
            A set of all indices of state variables.
        """
        return set(self.variableSet)

    def get_reduced_path(self):
        """
        Getter for the reduced transformation sequence produced by the Reductor
        object.

        Returns:
            The reduced Transformation object sequence.
        """
        if self.invalidated:
            self.reductor.eliminate()
            self.invalidated = False

        return self.reductor.get_path()

    def __str__(self):
        string = ""
        string += "[STATISTICS TransformationSystem<"

        string += str(self.variableDomain.getSimpleName())
        string += ">] Executed Transformations: "
        string += str(self.transCount)

        return string
