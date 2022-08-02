"""This module implements the DBM approximation based on a given target DBM."""
import random

import numpy as np

from uppyyl_simulator.backend.data_structures.adjacency_matrix.adjacency_matrix import (
    AdjacencyMatrix
)
from uppyyl_simulator.backend.data_structures.dbm.dbm import (
    DBMEntry
)
from uppyyl_simulator.backend.data_structures.dbm.dbm_operations.dbm_operations import (
    DBMOperationGenerator, DBMOperationSequence
)


################
# Approximator #
################
class DBMApproximatorViaDBM:
    """A class for DBM approximation based on a given target DBM."""

    def __init__(self):
        """Initializes DBMApproximatorViaDBM."""
        self.seq_approx = None
        self.approx_func = generate_approximation_sequence_via_dbm_target
        self.clear()

    def clear(self):
        """Clears the currently generated approximation sequence.

        Returns:
            None
        """
        self.seq_approx = DBMOperationSequence()

    def update_sequence(self, data):
        """Updates the approximation sequence based on a given data observation increment.

        Args:
            data: The data of the observation increment.

        Returns:
            The updated approximation sequence.
        """
        raise Exception(f'No on-the-fly approach for O(DBM) implemented yet.')

    def generate_sequence(self, data):
        """Generates the approximation sequence based on given DBM data.

        Args:
            data: The observed sequence and DBM data.

        Returns:
            The approximation sequence.
        """
        self.seq_approx = self.approx_func(data["dbm_target"])
        return self.seq_approx

    def get_sequence(self):
        """Gets the approximation sequence.

        Returns:
            The approximation sequence.
        """
        return self.seq_approx


################################################################################

#####################
# DBM-based version #
#####################
def get_all_pos_prefix_path(graph, curr_node, ord_p, path_sum, visited_nodes):
    """Determines a complete cycle in the graph where all prefixes on that cycle have a positive weight sum.

    Args:
        graph: The weighted graph object.
        curr_node: The currently analysed node.
        ord_p: The already known partial order of nodes.
        path_sum: The current weight sum.
        visited_nodes: A list of already visited nodes.

    Returns:
        The all-positive-prefix cycle.
    """
    visited_nodes = visited_nodes.copy()
    visited_nodes.append(curr_node.name)

    if len(visited_nodes) == len(graph.nodes):
        return visited_nodes
    for edge_id, edge in curr_node.out_edges.items():
        if edge.target.name in visited_nodes:
            continue

        new_path_sum = path_sum + edge.weight
        if new_path_sum >= 0:
            visited_nodes_ret = get_all_pos_prefix_path(graph, edge.target, ord_p, new_path_sum, visited_nodes)
            if visited_nodes_ret is not None:
                return visited_nodes_ret
    return None

def generate_approximation_sequence_via_dbm_target_for_zero_resets(dbm):
    """Generates an approximation sequence based on a given target DBM (based on positive DBM value counts per column).
    This algorithm version ensures that clocks are only reset to 0.

    Args:
        dbm: The target DBM.

    Returns:
        The approximation sequence.
    """

    sign_counts = []
    for clock_index in range(1, len(dbm.clocks)):
        clock = dbm.clocks[clock_index]
        sign_count = 0
        for i in range(0, len(dbm.matrix)):
            if dbm.matrix[i][clock_index].val > 0:
                sign_count += 1
        sign_counts.append((clock, clock_index, sign_count))

    # Sort by occurrences of positive signs in column (clock with the fewest positive column values is reset first)
    # sign_counts.sort(key=lambda x: x[2])
    sign_counts.sort(key=lambda x: (x[2], random.random()))
    clock_order = list(map(lambda x: x[0], sign_counts))

    # Generate the final all-reset-df sequence from reset values and reset order
    dbm_op_gen = DBMOperationGenerator()
    op_seq = DBMOperationSequence()

    for clock_name in clock_order:
        reset = dbm_op_gen.generate_reset(clock=clock_name, val=0)
        op_seq.append(reset)
        delay_future = dbm_op_gen.generate_delay_future()
        op_seq.append(delay_future)

    return op_seq

def generate_approximation_sequence_via_dbm_target(dbm):
    """Generates an approximation sequence based on a given target DBM.

    Args:
        dbm: The target DBM.

    Returns:
        The approximation sequence.
    """
    tdbm = dbm.copy()

    # Create vDBM from tDBM
    clock_reset_val_names = ["V0_REF"] + list(map(lambda c: f'v({c})', dbm.clocks[1:]))
    vdbm = tdbm.copy().negate().transpose()
    vdbm.clocks = clock_reset_val_names

    # Create vGraph from vDBM
    vgraph = vdbm.make_graph()

    # Apply final DF of S_approx to vGraph ...
    v0_ref = vgraph.get_node_by_name("V0_REF")
    for id_, edge in v0_ref.in_edges.items():
        edge.weight = 0

    # ... and to vDBM
    for i in range(0, len(vdbm.matrix[0])):
        vdbm.matrix[0][i] = DBMEntry(0, "<=")

    # Derive partial order from -inf entries
    ord_p = AdjacencyMatrix(headers=tdbm.clocks)
    for i in range(0, len(vdbm.matrix)):
        for j in range(0, len(vdbm.matrix[0])):
            if i == j:
                continue
            if vdbm.matrix[i][j].val == -np.inf:
                ord_p.matrix[i][j] = 1

    # Derive partial order from node-pair cycles
    ord_p = AdjacencyMatrix(headers=tdbm.clocks)
    for i in range(0, len(vdbm.matrix)):
        for j in range(i, len(vdbm.matrix[0])):
            if i == j:
                continue
            if vdbm.matrix[i][j].val <= 0 <= vdbm.matrix[j][i].val:
                ord_p.matrix[i][j] = 1

    # Get the transitive closure of the initial partial order
    ord_p.close()

    # Get the all-positive-prefix path
    all_pos_prefix_path = get_all_pos_prefix_path(vgraph, v0_ref, ord_p, 0, [])
    all_pos_prefix_path_indices = list(map(lambda name: vdbm.clocks.index(name), all_pos_prefix_path))

    # Update vDBM based on the all-positive-prefix path (i.e., set corresponding entries to inf)
    for i, row_index in enumerate(all_pos_prefix_path_indices[1:]):
        for j, column_index in enumerate(all_pos_prefix_path_indices[i + 1:]):
            if row_index != column_index:
                vdbm.matrix[row_index][column_index] = DBMEntry(np.inf, "<=")

    # Close the vDBM to get the final region of valid clock reset values
    vdbm.close()

    # Obtain reset values and reset order from vDBM
    reset_vals = []
    val_indices = all_pos_prefix_path_indices[1:]
    val_indices.reverse()
    for val_index in val_indices:
        val_name = vdbm.clocks[val_index]
        interval = vdbm.get_interval(val_name)
        # val = interval.get_random()
        val = interval.lower_val
        clock_name = tdbm.clocks[val_index]
        reset_vals.append((clock_name, val))

    # Generate the final all-reset-df sequence from reset values and reset order
    dbm_op_gen = DBMOperationGenerator()
    op_seq = DBMOperationSequence()

    for (clock_name, val) in reset_vals:
        reset = dbm_op_gen.generate_reset(clock=clock_name, val=val)
        op_seq.append(reset)
        delay_future = dbm_op_gen.generate_delay_future()
        op_seq.append(delay_future)

    return op_seq
