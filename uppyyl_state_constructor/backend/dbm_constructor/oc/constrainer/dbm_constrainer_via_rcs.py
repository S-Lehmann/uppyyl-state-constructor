"""This module implements the DBM constraining based on a relative constraint system (RCS)."""

from itertools import permutations

import numpy as np

from uppyyl_simulator.backend.data_structures.dbm.dbm_operations.dbm_operations import (
    DBMOperationGenerator, DBMOperationSequence
)
from uppyyl_state_constructor.backend.dbm_constructor.oc.constrainer.helper import (
    get_cycle, get_zero_equivalence_classes
)

clock_bound_for_all_permutations = 8
node_bound_for_all_permutations = 5


# # https://stackoverflow.com/questions/5602488/random-picks-from-permutation-generator
# def perm_given_index(lst, perm_index):
#     lst = lst[:]
#     for i in range(len(lst) - 1):
#         perm_index, j = divmod(perm_index, len(lst) - i)
#         lst[i], lst[i + j] = lst[i + j], lst[i]
#     return lst

###############
# Constrainer #
###############
class DBMConstrainerViaRCS:
    """A class for DBM constraining based on a relative constraint system (RCS)."""

    def __init__(self):
        """Initializes DBMConstrainerViaRCS."""
        self.seq_constr = None
        self.dbm_source = None
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
        raise Exception(f'No on-the-fly approach for C(RCS) implemented yet.')

    def generate_sequence(self, data):
        """Generates the constraining sequence based on given DBM data.

        Args:
            data: The observed sequence and DBM data.

        Returns:
            The constraining sequence.
        """
        self.seq_constr = generate_constraint_sequence_via_rcs(dbm_source=data["dbm_init"], dbm_target=data["dbm_target"])
        return self.seq_constr

    def get_sequence(self):
        """Gets the constraining sequence.

        Returns:
            The constraining sequence.
        """
        return self.seq_constr


################################################################################

def generate_constraint_sequence_via_rcs(dbm_source, dbm_target):
    """Generates a constraining sequence based on given source and target DBM using the RCS.

    Args:
        dbm_source: The source DBM.
        dbm_target: The target DBM.

    Returns:
        The constraining sequence.
    """
    fixed_edges = []
    for i in range(0, len(dbm_target.matrix)):
        for j in range(0, len(dbm_target.matrix[0])):
            if i == j:
                continue
            if dbm_source.matrix[i][j] == dbm_target.matrix[i][j]:
                fixed_edges.append(((dbm_target.clocks[i], i), (dbm_target.clocks[j], j)))

    eqs = get_zero_equivalence_classes(dbm_target)  # Note: eqs is sorted by index here
    edges = {"fixed": [], "nonfixed": []}

    # Get inter-eq-class edges
    for i, eq_i in enumerate(eqs):
        fixed_edges_with_eq_i_source = list(filter(lambda fixed_edge: fixed_edge[0] in eq_i, fixed_edges))
        for j, eq_j in enumerate(eqs):
            if i == j:
                continue
            fixed_edges_from_eq_i_to_eq_j = list(
                filter(lambda fixed_edge: fixed_edge[1] in eq_j, fixed_edges_with_eq_i_source))
            if fixed_edges_from_eq_i_to_eq_j:
                edges["fixed"].append(fixed_edges_from_eq_i_to_eq_j[0])
            else:
                edges["nonfixed"].append((eq_i[0], eq_j[0]))

    # Get intra-eq-class edges
    for i, eq_i in enumerate(eqs):
        # clock_count = len(dbm_target.clocks)
        # if clock_count <= clock_bound_for_all_permutations:
        node_count = len(eq_i)
        if node_count <= node_bound_for_all_permutations:
            eq_i_permutations = permutations(eq_i)  # Use all permutations
        else:
            eq_i_permutations = [
                np.ndarray.tolist(np.random.permutation(np.array(eq_i, dtype="O")))]  # Use only one single permutation
        max_fixed_count = -1
        max_fixed_cycle_edges = None
        for eq_i_perm in eq_i_permutations:
            cycle_edges = {"fixed": [], "nonfixed": []}
            for edge in get_cycle(eq_i_perm):
                if edge in fixed_edges:
                    cycle_edges["fixed"].append(edge)
                else:
                    cycle_edges["nonfixed"].append(edge)
            fixed_count = len(cycle_edges["fixed"])
            if fixed_count > max_fixed_count:
                max_fixed_count = fixed_count
                max_fixed_cycle_edges = cycle_edges
        edges["fixed"] += max_fixed_cycle_edges["fixed"]
        edges["nonfixed"] += max_fixed_cycle_edges["nonfixed"]

    # print(edges)
    # Generate sequence from edges
    dbm_op_gen = DBMOperationGenerator()
    op_seq = DBMOperationSequence()

    for (source_clock, source_index), (target_clock, target_index) in edges["nonfixed"]:
        row_clock_name = dbm_target.clocks[source_index]
        column_clock_name = dbm_target.clocks[target_index]
        rel = dbm_target.matrix[source_index][target_index].rel
        val = dbm_target.matrix[source_index][target_index].val
        if val != np.inf:
            constr = dbm_op_gen.generate_constraint(clock1=row_clock_name, clock2=column_clock_name, rel=rel, val=val)
            op_seq.append(constr)

    inf_entry_count = 0
    for i in range(0, len(dbm_target.matrix)):
        for j in range(0, len(dbm_target.matrix[0])):
            if dbm_target.matrix[i][j].val == np.inf:
                inf_entry_count += 1

    if len(op_seq) < (len(dbm_target.clocks) * (len(dbm_target.clocks) - 1) - inf_entry_count):
        close = dbm_op_gen.generate_close()
        op_seq.append(close)

    return op_seq
