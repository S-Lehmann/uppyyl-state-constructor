"""This module provides a transformation info."""

__author__ = "Jonas Rinast"

from enum import Enum

from ..dbm.db_value import (
    DBValue
)


class Type(Enum):
    """
    The Type enumeration defines different transformation types UPPAAL
    provides:

    1. Up Transformation: Removes the upper bounds on clocks.
    2. Reset Transformation: Resets a clock to a provided value.
    3. Constraint Transformation: Introduces a new clock constraint.
    """
    Up = 1
    Urgent = 2
    Reset = 3
    Constraint = 4


class TransformationInfo:
    """
    The TransformationInfo class provides additional information for a
    Transformation object that is not necessary to perform the transformation of
    the Evaluation objects itself. The provided data is meta data linked to the
    UPPAAL verification tool. The object modifies no data an is a pure data
    object only providing information.

    Note that the TransformationInfo class makes no effort to ensure encapsulated
    data is valid.
    """
    ta_system = None

    @staticmethod
    def register_ta_system(ta_system):
        """
        Establishes a link to a TASystem object for all TransformationInfo
        objects. The TASystem object is used for resolving clock variable
        requests.

        Args:
            ta_system: The TASystem to use to obtain clock variables.
        """
        TransformationInfo.ta_system = ta_system

    def __init__(self, type_, clock1=None, clock2=None, value=None):
        """
        Constructor for a TransformationInfo object.

        Uppaal Reset Annotation: clock = value
        Uppaal Guard or Invariant: clock1 - clock2 (<|<=) value
        Args:
            type_: The desired type.
            clock1: The index into Evaluation objects for the first clock.
            clock2: The index into Evaluation objects for the second clock.
            value: The constraining int / DBValue object.
        """
        self.type = type_
        if type_ == Type.Up or type_ == Type.Urgent:
            self.clock1 = 0
            self.clock2 = 0
            self.value = None
        elif type_ == Type.Reset:
            assert isinstance(value, int)
            self.clock1 = clock1
            self.clock2 = 0
            self.value = DBValue(value=value, bound=True)
        elif type_ == Type.Constraint:
            assert isinstance(value, DBValue)
            self.clock1 = clock1
            self.clock2 = clock2
            self.value = value

    def get_type(self):
        """
        Getter for the Type of the TransformationInfo object.

        Returns:
            The type.
        """
        return self.type

    def get_first_clock(self):
        """
        Getter for the clock of a Reset TransformationInfo object or the first
        clock in a Constraint TransformationInfo object.

        Returns:
            The Variable object representing the clock.
        """
        return self.ta_system.clocks[self.clock1]

    def get_second_clock(self):
        """
        Getter for the second clock in a Constraint TransformationInfo object.

        Returns:
            The Variable object representing the clock.
        """
        return self.ta_system.clocks[self.clock2]

    def get_value(self):
        """
        Getter for the constraining DBValue in a Constraint TransformationInfo
        object.

        Returns:
            The value.
        """
        return self.value

    def __str__(self):
        string = ""
        # print(self.type, self.clock1, self.clock2, self.value)
        if self.type == Type.Reset:
            string += str(self.get_first_clock().get_name())
            string += " = "
            string += str(self.value.get_value())

        elif self.type == Type.Constraint:
            if self.clock1 == 0:
                string += str(self.get_second_clock().get_name())
                string += " >"
                if self.value.get_bound():
                    string += '='
                string += ' '
                string += str(-self.value.get_value())
            else:
                string += str(self.get_first_clock().get_name())
                if self.clock2 != 0:
                    string += " - "
                    string += str(self.get_second_clock().get_name())

                string += " <"
                if self.value.get_bound():
                    string += '='
                string += ' '
                string += str(self.value.get_value())

        elif self.type == Type.Up:
            string += "Up"

        elif self.type == Type.Urgent:
            string += "Urgent"

        return string
