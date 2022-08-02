"""This module implements the DBM constraining based on a full constraint system (FCS)."""

import numpy as np

from uppyyl_simulator.backend.data_structures.dbm.dbm_operations.dbm_operations import (
    DBMOperationGenerator, DBMOperationSequence
)


###############
# Constrainer #
###############
class DBMConstrainerViaFCS:
    """A class for DBM constraining based on a full constraint system (FCS)."""

    def __init__(self):
        """Initializes DBMConstrainerViaFCS."""
        self.seq_constr = None
        self.clear()

    def clear(self):
        """Clears the currently generated constraining sequence.

        Returns:
            None
        """
        self.seq_constr = DBMOperationSequence()

    def update_sequence(self, data):  # TODO: Optimized on-the-fly implementation
        """Updates the constraining sequence based on a given data observation increment.

        Args:
            data: The data of the observation increment.

        Returns:
            The updated constraining sequence.
        """
        raise Exception(f'No on-the-fly approach for C(FCS) implemented yet.')

    def generate_sequence(self, data):
        """Generates the constraining sequence based on given DBM data.

        Args:
            data: The observed sequence and DBM data.

        Returns:
            The constraining sequence.
        """
        self.seq_constr = generate_constraint_sequence_via_fcs(data["dbm_target"])
        return self.seq_constr

    def get_sequence(self):
        """Gets the constraining sequence.

        Returns:
            The constraining sequence.
        """
        return self.seq_constr


################################################################################

def generate_constraint_sequence_via_fcs(dbm):
    """Generates a constraining sequence based on a given target DBM using the FCS.

    Args:
        dbm: The target DBM.

    Returns:
        The constraining sequence.
    """
    dbm_op_gen = DBMOperationGenerator()
    op_seq = DBMOperationSequence()

    for i in range(len(dbm.matrix)):
        row_clock_name = dbm.clocks[i]
        for j in range(len(dbm.matrix[0])):
            if i != j:
                column_clock_name = dbm.clocks[j]
                rel = dbm.matrix[i][j].rel
                val = dbm.matrix[i][j].val
                if val != np.inf:
                    constr = dbm_op_gen.generate_constraint(clock1=row_clock_name, clock2=column_clock_name, rel=rel,
                                                            val=val)
                    op_seq.append(constr)

    return op_seq
