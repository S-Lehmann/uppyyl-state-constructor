"""This module provides (graph related) helper functions."""


def get_zero_equivalence_classes(dbm):
    """Divides the clocks of a DBM into zero-equivalence classes (i.e., they form a cycle of zero weight sum)

    Args:
        dbm: The source DBM.

    Returns:
        The DBM clocks divided into zero-equivalence classes.
    """
    eqs = []
    remaining_clocks = list(zip(dbm.clocks.copy(), range(0, len(dbm.clocks))))

    while remaining_clocks:
        eq = [remaining_clocks[0]]
        for clock, clock_index in remaining_clocks[1:]:
            first_eq_index = eq[0][1]
            pair_cycle_sum = dbm.matrix[first_eq_index][clock_index] + dbm.matrix[clock_index][first_eq_index]
            if pair_cycle_sum.val == 0:
                eq.append((clock, clock_index))

        eqs.append(eq)
        for clock_data in eq:
            remaining_clocks.remove(clock_data)

    return eqs


def get_cycle(node_list):
    """Generates a cycle of edges from a list of nodes.

    Args:
        node_list: The list of nodes the edge should cycle over in order.

    Returns:

    """
    if len(node_list) <= 1:
        return []
    edges = []
    for i in range(0, len(node_list) - 1):
        edges.append((node_list[i], node_list[i + 1]))
    edges.append((node_list[-1], node_list[0]))
    return edges
