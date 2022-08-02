"""This module implements the functions to extend timed automata by state construction routines."""
from uppyyl_simulator.backend.ast.parsers.generated.uppaal_c_language_parser import UppaalCLanguageParser

from uppyyl_simulator.backend.ast.parsers.uppaal_c_language_semantics import UppaalCLanguageSemantics
from uppyyl_simulator.backend.data_structures.dbm.dbm_operations.dbm_operations import DelayFuture, Reset, Constraint, \
    Close
from uppyyl_simulator.backend.models.ta.nta import System
from uppyyl_simulator.backend.models.ta.ta import Location, Edge

sync_prefix = "SYNC_"
obs_prefix = "OBS_"
dbm_prefix = "DBM_"

dbm_init_tmpl_name = f'{sync_prefix}DBM_Init'


def get_assignments_for_variable(var_name, val):
    """Gets assignment strings "var_name = var_val" for Uppaal data types.

    Args:
        var_name: The variable name.
        val: The variable value.

    Returns:
        The assignment string.
    """
    assignment_strs = []
    if isinstance(val, bool):
        assignment_str = f'{var_name} = {"true" if val else "false"}'
        assignment_strs.append(assignment_str)
    elif isinstance(val, int):
        assignment_str = f'{var_name} = {val}'
        assignment_strs.append(assignment_str)
    elif isinstance(val, list):
        for i, sub_val in enumerate(val):
            sub_var_name = f'{var_name}[{i}]'
            sub_assignment_strs = get_assignments_for_variable(sub_var_name, sub_val)
            assignment_strs.extend(sub_assignment_strs)
    elif isinstance(val, dict):
        for field_name, field_val in val.items():
            sub_var_name = f'{var_name}.{field_name}'
            sub_assignment_strs = get_assignments_for_variable(sub_var_name, field_val)
            assignment_strs.extend(sub_assignment_strs)
    else:
        raise Exception("Variable has unknown type.")

    return assignment_strs


class StateConstructionModelAdaptor:
    """A model adaptor for state construction routines."""
    def __init__(self):
        """Initializes StateConstructionModelAdaptor."""
        pass

    @staticmethod
    def add_state_construction_components(system: System, seq, instance_data, loc_state, var_state):
        """Adds all state construction components to a given system.
        These components are:

        1. Synchronized state construction sequences in all original templates, which forces that the original model
           section is only entered when the construction is finished.
        2. The state construction template, which executes the DBM construction and variable assignments.
        3. Additional channel variable declarations and construction template instantiations.

        Args:
            system: The original Uppaal system.
            seq: The DBM operation sequence as base for DBM construction.
            instance_data: Template and argument data for all system instances.
            loc_state: The targeted active location state.
            var_state: The targeted variable state.
        """
        StateConstructionModelAdaptor.add_state_construction_sequences_to_templates(
            system=system, instance_data=instance_data, loc_state=loc_state)
        StateConstructionModelAdaptor.insert_state_construction_template(system=system, seq=seq, var_state=var_state)
        StateConstructionModelAdaptor.add_state_construction_variables(system=system)

    @staticmethod
    def insert_state_construction_template(system: System, seq, var_state):
        """Inserts the state construction template, which executes the DBM construction and variable assignments.

        Args:
            system: The original Uppaal system.
            seq: The DBM operation sequence as base for DBM construction.
            var_state: The targeted variable state.

        Returns:
            The generated state construction template.
        """
        tmpl_init = system.new_template(dbm_init_tmpl_name)

        tmpl_init.set_declaration(decl="")

        # Create new initial location
        loc_init: Location = tmpl_init.new_location(f'Init')
        loc_init.set_whole_position({"x": 0, "y": 0})
        loc_init.set_committed(True)
        tmpl_init.set_init_location(loc_init)

        curr_loc = loc_init

        pos_diff = 100

        seq_len = len(seq)
        seq_index = 0
        loc_count = 0

        while seq_index < seq_len:
            constrs = []
            resets = []
            do_close = False
            do_delay_future = False

            # Gather constraint, reset, close and delay-future operations for next location and edge
            while (seq_index < seq_len) and isinstance(seq[seq_index], Constraint):
                constrs.append(seq[seq_index])
                seq_index += 1

            while (seq_index < seq_len) and isinstance(seq[seq_index], Close):
                do_close = True
                seq_index += 1

            while (seq_index < seq_len) and isinstance(seq[seq_index], Reset):
                resets.append(seq[seq_index])
                seq_index += 1

            while (seq_index < seq_len) and isinstance(seq[seq_index], DelayFuture):
                do_delay_future = True
                seq_index += 1

            # Add next location
            prev_loc = curr_loc
            curr_loc: Location = tmpl_init.new_location(f'Rec{loc_count+1}')
            loc_count += 1
            curr_loc.set_whole_position({"x": 0, "y": loc_count * pos_diff})

            if not do_delay_future:
                curr_loc.set_urgent(True)

            if do_close:
                pass  # Nothing needs to be done here, as "close" is implicitly implied in Uppaal

            # Add new edge
            edge: Edge = tmpl_init.new_edge(source=prev_loc, target=curr_loc)
            for constr in constrs:
                constr_str = constr.uppaal_string()
                edge.new_clock_guard(grd_data=constr_str)

            for reset in resets:
                reset_str = reset.uppaal_string()
                edge.new_reset(rst_data=reset_str)

        # Add final "end" location
        loc_end = tmpl_init.new_location(f'End')
        loc_count += 1
        loc_end.set_whole_position({"x": 0, "y": loc_count * pos_diff})

        edge_init_end = tmpl_init.new_edge(source=curr_loc, target=loc_end)
        edge_init_end.set_sync(f'{dbm_prefix}init_end!')

        # Add assignments for all state variables to final edge
        # (Note: Make sure that all local variables have been transformed into global variables before)
        for var_name, val in var_state["variable"]["system"].items():
            assignment_strs = get_assignments_for_variable(var_name, val)
            for assignment_str in assignment_strs:
                edge_init_end.new_update(updt_data=assignment_str)

        return tmpl_init

    @staticmethod
    def add_state_construction_sequences_to_templates(system: System, instance_data, loc_state):
        """Adds synchronized state construction sequences in all original templates

        Args:
            system: The original Uppaal system.
            instance_data: Template and argument data for all system instances.
            loc_state: The targeted active location state.
        """
        for tmpl_id, tmpl in system.templates.items():

            # Get original init location
            inst_name = next((inst_name for inst_name, inst_data in instance_data.items()
                              if inst_data["template_name"] == tmpl.name), None)
            loc_init_orig_id = loc_state[inst_name]
            loc_init_orig = tmpl.get_location_by_id(id_=loc_init_orig_id)

            # Add artificial synchronization location
            loc_sync_pre_init = tmpl.new_location(f'{sync_prefix}Pre_Init')
            loc_sync_pre_init.set_whole_position({
                "x": loc_init_orig.view["self"]["pos"]["x"] - 50,
                "y": loc_init_orig.view["self"]["pos"]["y"] - 100
            })
            tmpl.set_init_location(loc_sync_pre_init)

            # Add edge between sync location and original init location
            edge_pre_init_to_post_init = tmpl.new_edge(source=loc_sync_pre_init, target=loc_init_orig)
            edge_pre_init_to_post_init.set_sync(f'{dbm_prefix}init_end?')
            edge_pre_init_to_post_init.view["sync_label"]["pos"] = {
                "x": loc_sync_pre_init.view["self"]["pos"]["x"] - 25,
                "y": loc_sync_pre_init.view["self"]["pos"]["y"] + 20
            }
            # Add invariants of original init location as edge guards to ensure a valid transition target
            for inv in loc_init_orig.invariants:
                edge_pre_init_to_post_init.new_clock_guard(grd_data=inv.text)

    @staticmethod
    def add_state_construction_variables(system):
        """Adds channel variable declarations and construction template instantiations.

        Args:
            system: The original Uppaal system.
        """
        uppaal_c_parser = UppaalCLanguageParser(semantics=UppaalCLanguageSemantics())

        # Add init channel to global declaration
        global_decl_ext_str = (
            f'broadcast chan {dbm_prefix}init_end;'
        )
        global_decl_ext_ast = uppaal_c_parser.parse(text=global_decl_ext_str, rule_name="UppaalDeclaration")
        system.declaration.ast["decls"].extend(global_decl_ext_ast["decls"])
        system.declaration.update_text()

        # Add DBM init template instance to system declaration
        dbm_init_inst_name = f'{sync_prefix}Init'
        dbm_init_instance_ast = {
            "astType": 'Instantiation',
            "instanceName": dbm_init_inst_name,
            "params": [],
            "templateName": dbm_init_tmpl_name,
            "args": []
        }
        system.system_declaration.ast["decls"].append(dbm_init_instance_ast)
        system.system_declaration.ast["systemDecl"]["processNames"][0].append(dbm_init_inst_name)
        system.system_declaration.update_text()
