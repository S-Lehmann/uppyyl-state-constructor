"""This module provides the DBM system."""

__author__ = "Jonas Rinast"

import sys

from .db_value import (
    DBValue
)
from .minimum_addition import (
    MinimumAddition
)
from .minimum_assignment import (
    MinimumAssignment
)
from .static_addition import (
    StaticAddition
)
from .static_assignment import (
    StaticAssignment
)
from ..trans.reduce.graph.graph_reductor import (
    GraphReductor
)
from ..trans.transformation_info import (
    TransformationInfo, Type
)
from ..trans.transformation_system import (
    TransformationSystem
)


class ResetEntry:
    """
    The ResetEntry class is a data class used to encapsulate parameters for
    the instantiation of a Reset Transformation object. It is used as an
    index into a Map for caching purposes.
    """
    def __init__(self, clock, value):
        """Initializes ResetEntry.

        Args:
            clock: The reset clock.
            value: The reset value.
        """
        self.clock = clock
        self.value = value

    def __hash__(self):
        prime = 31
        result = 1
        result = prime * result + self.clock
        result = prime * result + self.value
        return result

    def __eq__(self, other):
        if isinstance(other, ResetEntry):
            if self.clock == other.clock and self.value == other.value:
                return True
        return False


class ConstraintEntry:
    """
    The ConstraintEntry class is a data class used to encapsulate parameters
    for the instantiation of a Constraint Transformation object. It is used
    as an index into a Map for caching purposes.
    """

    def __init__(self, clock1, clock2, constraint):
        """Initializes ConstraintEntry.

        Args:
            clock1: The first constraint clock.
            clock2: The second constraint clock.
            constraint: The constraint value.
        """
        self.clock1 = clock1
        self.clock2 = clock2
        self.constraint = constraint

    def __hash__(self):
        prime = 31
        result = 1
        result = prime * result + self.clock1
        result = prime * result + self.clock2
        result = prime * result + (0 if (self.constraint is None) else hash(self.constraint))
        return result

    def __eq__(self, other):
        if isinstance(other, ConstraintEntry):
            if self.clock1 == other.clock1 and self.clock2 == other.clock2 and self.constraint == other.constraint:
                return True
        return False


class DBMSystem:
    """
    The DBMSystem class builds on the TransformationSystem class to provide a
    transformation system capable of dealing with difference bound matrices. It
    provides access to the DBM modifying transformations, application of those to
    the current DBM system, and pretty printing for a DBM Evaluation object.

    The last DBM in the produced DBM sequence is the current Evaluation object.
    """

    def __init__(self, clock_count):
        """
        Constructor for a DBMSystem object with the given number of clocks.

        Note that the implicit static zero clock is added automatically.

        Args:
            clock_count: The number of clocks in the DBM.
        """
        self.clock_count = clock_count
        self.variable_count = clock_count * clock_count

        self.resets = {}
        self.constraints = {}

        self.reductor = GraphReductor()
        self.transf_system = TransformationSystem(self.variable_count, DBValue, self.reductor)

        self.up = self.create_up_transformation()
        self.urgent = self.create_urgent_transformation()

        self.transCount = 0

        initial = self.create_evaluation()
        self.transf_system.set_initial_evaluation(initial)

    def verify_evaluation(self, evaluation):
        """
        Compares the provided Evaluation object to the current Evaluation object
        of the DBM transformation system. Throws an IllegalStateException if the
        object are not equal. Used to verify that a transformation performed
        correctly.

        Args:
            evaluation: The Evaluation object to compare to the current Evaluation object.
        """
        if evaluation != self.transf_system.get_current_evaluation():
            string = ""
            string += "State verification failed.\n"

            string += str(self.format_evaluation(self.transf_system.get_current_evaluation()))
            string += "\n\nshould be\n"
            string += str(self.format_evaluation(evaluation))
            string += '\n'

            raise Exception(string)

    def verify_reconstruction_path(self, path):
        """
        Compares the current Evaluation object to the result of applying all the
        provided Transformation objects to a fresh DBM transformation system,
        i.e., this function verifies the given sequence produces the same last
        Evaluation object. Throws an IllegalStateException if the Evaluation
        objects do not match.

        Args:
            path: The sequence of Transformation objects to perform and check.
        """
        system = TransformationSystem(self.variable_count, DBValue)
        initial = self.create_evaluation()
        system.set_initial_evaluation(initial)

        for trans in path:
            system.apply_transformation(trans)

        if system.get_current_evaluation() != self.transf_system.get_current_evaluation():
            string = ""
            string += "Path verification failed.\n"

            string += str(self.format_evaluation(system.get_current_evaluation()))
            string += "\n\nshould be\n"
            string += str(self.format_evaluation(self.transf_system.get_current_evaluation()))
            string += '\n'
            string += str(self.reductor)

            raise Exception(string)

    def apply_transformation(self, transformation):
        """
        Applies the given Transformation object to the current Evaluation object.

        Args:
            transformation: The Transformation object to apply.
        """
        self.transCount += 1
        self.transf_system.apply_transformation(transformation)

    def get_clock_count(self):
        """
        Getter for the number of clocks in this DBM system.

        Returns: The number of clocks in this DBM system.

        """
        return self.clock_count

    def get_variable_count(self):
        """
        Getter for the number of variables in this DBM system. This is equal to
        (clocks + 1)^2, every pair of clocks has a variable and an additional
        static zero clock is added in a difference bound matrix.

        Returns:
            The number of variables in this DBM system.
        """
        return self.variable_count

    def get_transformation_system(self):
        """
        Getter for the underlying TransformationSystem object. Using this should
        only be necessary to access reduction functionality.

        Returns: The underlying TransformationSystem object.

        """
        return self.transf_system

    def get_up_transformation(self):
        """
        Getter for the Up Transformation object in this DBM system.

        Returns: The Up Transformation object

        """
        return self.up

    def get_urgent_transformation(self):
        """
        Getter for the Urgent Transformation object in this DBM system.

        Returns:
            The Urgent Transformation object.
        """
        return self.urgent

    def get_reset_transformation(self, clock, value):
        """
        Getter for a Reset Transformation object that sets the given clock to the
        given value. The clock is identified by its index in the Evaluation
        vector.

        Args:
            clock: The index of the clock to reset.
            value: The value to set the clock to.

        Returns:
            The Reset Transformation object.
        """
        entry = ResetEntry(clock, value)
        trans = self.resets.get(entry)

        if trans is None:
            trans = self.create_reset_transformation(clock, value)
            self.resets[entry] = trans

        return trans

    def get_constraint_transformation(self, clock1, clock2, constraint):
        """
        Getter for a Constraint Transformation object that constraints the clock
        difference between the given two clocks by imposing a (strict) upper
        bound according to the given DBValue object.

        Args:
            clock1: The index of the first clock of the clock difference to constrain.
            clock2: The index of the second clock of the clock difference to constrain.
            constraint: The constraint value.

        Returns:
            The Constraint Transformation object.
        """
        entry = ConstraintEntry(clock1, clock2, constraint)
        trans = self.constraints.get(entry)

        if trans is None:
            trans = self.create_constraint_transformation(clock1, clock2, constraint)
            self.constraints[entry] = trans

        return trans

    #
    # Creates and returns a new Evaluation object suitable for use with this
    # DBM system.
    #
    # @return the new Evaluation object
    #
    def create_evaluation(self):
        """
        Creates and returns a new Evaluation object suitable for use with this
        DBM system.

        Returns:
            The new Evaluation object.
        """
        evaluation = self.transf_system.create_evaluation()
        zero = DBValue(value=0, bound=True)

        for i in range(0, self.variable_count):
            evaluation.set_evaluation(i, zero)

        return evaluation

    def get_transformation_count(self):
        """
        Getter for the number of transformation performed with this DBM
        transformation system.

        Returns:
            The number of transformations performed up to now.
        """
        return self.transCount

    def format_evaluation(self, evaluation):
        """
        Formats a DBM Evaluation obtained from this DBMSystem object for pretty
        printing. Returns a multi-line String object in table form containing the
        DBM entries.

        Args:
            evaluation: The Evaluation object to convert to a String object.

        Returns:
            The String representing the Evaluation object.
        """
        string = ""

        maxlen = 0
        for i in range(0, self.variable_count):
            length = len(str(evaluation.get_evaluation(i)))

            if length > maxlen:
                maxlen = length

        maxlen += 1

        for i in range(0, self.variable_count):
            if i % self.clock_count == 0:
                string += '\n'

            val = str(evaluation.get_evaluation(i))
            for j in range(len(val), maxlen):
                string += ' '
            string += str(val)

        return string

    def create_up_transformation(self):
        """Creates an Up transformation.

        Returns:
            The Up transformation.
        """
        infty = StaticAssignment(DBValue(value=sys.maxsize, bound=False))
        trans = self.transf_system.create_simple_transformation()
        parameters = []

        for i in range(self.clock_count, self.variable_count, self.clock_count):
            trans.add_specification_entry(i, parameters, infty)

        trans.set_info(TransformationInfo(type_=Type.Up))

        return trans

    def create_urgent_transformation(self):
        """Creates an Urgent transformation.

        Returns:
            The Urgent transformation.
        """
        minadd = MinimumAddition()
        trans = self.transf_system.create_simple_transformation()
        lft = self.clock_count

        for i in range(1, self.clock_count):
            for top in range(1, self.clock_count):
                if i == top:
                    continue
                index = lft + top
                trans.add_specification_entry(index, [index, lft, top], minadd)

            lft += self.clock_count

        trans.set_info(TransformationInfo(type_=Type.Urgent))

        return trans

    def create_reset_transformation(self, clock, value):
        """Creates a Reset transformation.

        Args:
            clock: The index of the clock to reset.
            value: The value to set the clock to.

        Returns:
            The Reset transformation.
        """
        trans = self.transf_system.create_simple_transformation()
        neg = StaticAddition(DBValue(value=-value, bound=True))
        pos = StaticAddition(DBValue(value=value, bound=True))

        lft = 0
        cln = clock
        row = clock * self.clock_count

        for top in range(0, self.clock_count):
            if top != clock:
                trans.add_specification_entry(cln, [lft], neg)
                trans.add_specification_entry(row, [top], pos)

            lft += self.clock_count
            cln += self.clock_count
            row += 1

        trans.set_info(TransformationInfo(type_=Type.Reset, clock1=clock, value=value))

        return trans

    def create_constraint_transformation(self, clock1, clock2, constraint):
        """Creates a Constraint transformation.

        Args:
            clock1: The index of the first clock of the clock difference to constrain.
            clock2: The index of the second clock of the clock difference to constrain.
            constraint: The constraint value.

        Returns:
            The Constraint transformation.
        """
        compound = self.transf_system.create_compound_transformation()
        trans = self.transf_system.create_simple_transformation()

        index = clock1 * self.clock_count + clock2

        trans.add_specification_entry(index, [index], MinimumAssignment(constraint))
        compound.add_transformation(trans)

        ij = 0
        minadd = MinimumAddition()

        for i in range(0, self.clock_count):
            ix = ij + clock1
            iy = ij + clock2
            xj = clock1 * self.clock_count
            yj = clock2 * self.clock_count

            for j in range(0, self.clock_count):

                if True:
                    trans = self.transf_system.create_simple_transformation()
                    trans.add_specification_entry(ij, [ij, ix, xj], minadd)
                    compound.add_transformation(trans)

                    trans = self.transf_system.create_simple_transformation()
                    trans.add_specification_entry(ij, [ij, iy, yj], minadd)
                    compound.add_transformation(trans)

                xj += 1
                yj += 1
                ij += 1

        compound.set_info(TransformationInfo(type_=Type.Constraint, clock1=clock1, clock2=clock2, value=constraint))

        return compound

    # @Override
    def __str__(self):
        string = ""
        string += "[STATISTICS DBMSystem] Executed Transformations: "

        string += str(self.transCount)
        string += '\n'
        string += str(self.transf_system)

        return string
