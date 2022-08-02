"""This module provides a TA system implementation."""

__author__ = "Jonas Rinast"

import re

from .variable import (
    Variable
)
from ..dbm.dbm_system import (
    DBMSystem
)
from ..trans.transformation_info import (
    TransformationInfo, Type
)

#########
# Regex #
#########
ENDL = re.compile(r"\s*;\s*")
COMMENT = re.compile(r"\s*//[^\n]*\n\s*")
SYNC = re.compile(r"\s*([a-zA-Z_]\w*)(?:\[[^]]+])?\s*([?!])\s*")
UPDATE = re.compile(r"\s*([a-zA-Z_]\w*)\s*:?=\s*(\S+)\s*")
CONSTRAINT = re.compile(
    r"\s*([a-zA-Z_.][\w.]*)(?:\s*-\s*([a-zA-Z_.][\w.]*))?\s*([<>=]=?|\u2264|\u2265|\u2208)\s*(.+)\s*")
INTERVAL = re.compile(r"([\[(])(-?\d+),(-?\d+)([])])")
CONST = re.compile(
    r"\s*const\s+(?:int|bool)\s+([a-zA-Z_]\w*\s+=\s+(?:-?\d+|true|false)"
    r"(?:\s*,\s*[a-zA-Z_]\w*\s+=\s+(?:-?\d+|true|false))*)\s*"
)
URGENTCHAN = re.compile(r"\s*urgent\s+chan\s+([a-zA-Z_]\w*(?:\[[^]]+])?(?:\s*,\s*[a-zA-Z_]\w*(?:\[[^]]+])?)*)\s*")
INSTANCE = re.compile(r"\s*([a-zA-Z_]\w*)\s*=\s*([a-zA-Z_]\w*)\(\s*([^)]*)\)\s*")
ASSIGNMENT = re.compile(r"\s*([a-zA-Z_]\w*)(?:\[[^]]+])?\s*=\s*([^,]*)")
IDENTIFIER = re.compile(r"\s*([a-zA-Z_]\w*)(?:\[[^]]+])?\s*")
PARAMETER = re.compile(r"\s*(const\s+(?:int|bool)|urgent\s+chan)\s+&?\s*([a-zA-Z_]\w*)")

AND = re.compile(r"\s*&&\s*")
COMMA = re.compile(r"\s*,\s*")


class TASystem:
    """
    The TASystem class implements a DBM transformation system based on an UPPAAL
    model. It provides access to the UPPAAL interface and feeds the data to the
    underlying DBMSystem object.
    """

    def __init__(self, clock_names, var_names, system=None):
        """
        Constructs a TASystem object from the provided information on the UPPAAL
        data. The UppaalSystem object is the interface to the UPPAAL engine. The
        Document object is the UPPAAL model, the SystemState object defines the
        initial state of the model and the list of Transition object defines the
        outgoing transitions in the initial state of the UPPAAL model. See the
        UPPAAL Java API for more information.

        Args:
            clock_names: A list of all system clock names.
            var_names:  A list of all system variable names.
            system: The Uppaal system object.
        """
        self.system = system

        self.clockToIndex = {}
        self.indexToClock = {}
        self.clock_count = len(clock_names)  # Includes reference clock t(0), otherwise subtract 1
        self.clocks = []
        self.variableToIndex = {}
        self.variable_count = len(var_names)
        self.variables = []
        self.constantToIndex = {}
        self.constants = []
        self.urgentChannels = set()

        self.transCount = 0

        for i in range(0, self.clock_count):
            clock_name = clock_names[i]  # +1]
            clock = Variable(clock_name)
            clock.set_value(len(self.indexToClock))
            self.clocks.append(clock)
            self.indexToClock[len(self.indexToClock)] = clock
            self.clockToIndex[clock] = len(self.clockToIndex)

        for i in range(0, self.variable_count):
            var_name = var_names[i]
            variable = Variable(var_name)
            self.variables.append(variable)
            self.variableToIndex[variable] = i

        self.dbm_system = DBMSystem(self.clock_count)
        TransformationInfo.register_ta_system(self)

    def get_dbm_system(self):
        """
        Getter for the underlying DBMSystem object.

        Returns:
            The underlying DBMSystem object.
        """
        return self.dbm_system

    def get_clock(self, instance=None, name=None):
        """
        Getter for the Variable object for the clock with the given name in the
        given template instance.

        Args:
            instance: The instance name of an UPPAAL template with the clock.
            name: The name of the clock in the template.

        Returns:
            The Variable object of the clock, or None if not found.
        """
        if name is None:
            return self.clocks[0]

        clock = Variable(name)
        if instance is not None:
            clock.set_instance(instance)

        index = self.clockToIndex.get(clock)

        if index is None:
            clock.set_instance(None)
            index = self.clockToIndex[clock]

            if index is None:
                return None

        return self.clocks[index]

    def get_sequence(self):
        """Gets the current reconstruction sequence.

        Returns:
            The reconstruction sequence.
        """
        path = self.dbm_system.get_transformation_system().get_reduced_path()
        seq_lines = []
        for trans in path:
            info = trans.get_info()
            if info.type == Type.Up:
                seq_lines.append(f'DelayFuture()')
            elif info.type == Type.Urgent:
                pass
            elif info.type == Type.Reset:
                clock1_name = self.clocks[info.clock1].get_full_name()
                seq_lines.append(f'Reset({clock1_name},{info.value.value})')
            elif info.type == Type.Constraint:
                clock1_name = self.clocks[info.clock1].get_full_name()
                clock1_name = "T0_REF" if clock1_name == "t(0)" else clock1_name
                clock2_name = self.clocks[info.clock2].get_full_name()
                clock2_name = "T0_REF" if clock2_name == "t(0)" else clock2_name
                seq_lines.append(
                    f'Constraint({clock1_name},{clock2_name},{"<=" if info.value.bound else "<"},{info.value.value})')

        seq = "\n".join(seq_lines)
        return seq

    # @Override
    def __str__(self):
        string = ""
        string += "[STATISTICS TASystem] Executed Transitions: "

        string += str(self.transCount)
        string += '\n'
        string += str(self.dbm_system)

        return string
