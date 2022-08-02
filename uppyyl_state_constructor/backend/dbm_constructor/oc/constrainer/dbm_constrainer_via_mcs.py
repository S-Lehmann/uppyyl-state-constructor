"""This module implements the DBM constraining based on a minimal constraint system (MCS)."""

import numpy as np

from uppyyl_simulator.backend.data_structures.dbm.dbm_operations.dbm_operations import (
    DBMOperationGenerator, DBMOperationSequence
)
from uppyyl_state_constructor.backend.dbm_constructor.oc.constrainer.helper import (
    get_cycle, get_zero_equivalence_classes
)


###############
# Constrainer #
###############
class DBMConstrainerViaMCS:
    """A class for DBM constraining based on a minimal constraint system (MCS)."""

    def __init__(self):
        """Initializes DBMConstrainerViaMCS."""
        self.seq_constr = None
        self.clear()

    def clear(self):
        """Clears the currently generated constraining sequence.

        Returns:
            None
        """
        self.seq_constr = DBMOperationSequence()

    def update_sequence(self, data):
        """Updates the constraining sequence based on a given data observation increment.

        Args:
            data: The data of the observation increment.

        Returns:
            The updated constraining sequence.
        """
        raise Exception(f'No on-the-fly approach for C(MCS) implemented yet.')

    def generate_sequence(self, data):
        """Generates the constraining sequence based on given DBM data.

        Args:
            data: The observed sequence and DBM data.

        Returns:
            The constraining sequence.
        """
        self.seq_constr = generate_constraint_sequence_via_mcs(data["dbm_target"])
        return self.seq_constr

    def get_sequence(self):
        """Gets the constraining sequence.

        Returns:
            The constraining sequence.
        """
        return self.seq_constr


################################################################################

def generate_constraint_sequence_via_mcs(dbm):
    """Generates a constraining sequence based on a given target DBM using the MCS.

    Args:
        dbm: The target DBM.

    Returns:
        The constraining sequence.
    """
    eqs = get_zero_equivalence_classes(dbm)  # Note: eqs is sorted by index here
    edges = []

    # Get inter-eq-class edges
    for i, eq_i in enumerate(eqs):
        for j, eq_j in enumerate(eqs):
            if i == j:
                continue
            edges.append((eq_i[0], eq_j[0]))

    # Get intra-eq-class edges
    for i, eq_i in enumerate(eqs):
        edges += get_cycle(eq_i)

    # Generate sequence from edges
    dbm_op_gen = DBMOperationGenerator()
    op_seq = DBMOperationSequence()

    for (source_clock, source_index), (target_clock, target_index) in edges:
        row_clock_name = dbm.clocks[source_index]
        column_clock_name = dbm.clocks[target_index]
        rel = dbm.matrix[source_index][target_index].rel
        val = dbm.matrix[source_index][target_index].val
        if val != np.inf:
            constr = dbm_op_gen.generate_constraint(clock1=row_clock_name, clock2=column_clock_name, rel=rel, val=val)
            op_seq.append(constr)

    inf_entry_count = 0
    for i in range(0, len(dbm.matrix)):
        for j in range(0, len(dbm.matrix[0])):
            if dbm.matrix[i][j].val == np.inf:
                inf_entry_count += 1

    if len(op_seq) < (len(dbm.clocks) * (len(dbm.clocks) - 1) - inf_entry_count):
        close = dbm_op_gen.generate_close()
        op_seq.append(close)

    return op_seq
