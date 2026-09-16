"""Workflow registration for the example optical orchestrator.

Registers every shipped workflow of the orchestrator-optical module with the
standard orchestrator-core mechanism (one ``LazyWorkflowInstance`` line per
workflow). The workflow names and import paths mirror the shipped workflows of
the module (discoverable via
``python -c "import orchestrator.optical.workflows"`` or the module README);
keep this list in sync when the module ships new workflows.
"""

from orchestrator.core.workflows import LazyWorkflowInstance


LazyWorkflowInstance("orchestrator.optical.workflows.optical_pipe.fiber_patch.create_fiber_patch", "create_fiber_patch"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_pipe.fiber_span.create_fiber_span", "create_fiber_span"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_pipe.leased_spectrum.create_leased_spectrum", "create_leased_spectrum"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_coherent_pluggable.create_optical_coherent_pluggable", "create_optical_coherent_pluggable"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_digital_service.create_optical_digital_service", "create_optical_digital_service"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_location.create_optical_location", "create_optical_module_location"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_node.nokia_flexils.create_nokia_flexils", "create_optical_node_nokia_flexils"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_node.nokia_groove_g30.create_nokia_groove_g30", "create_optical_node_nokia_groove_g30"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_node.nokia_gx_g42.create_nokia_gx_g42", "create_optical_node_nokia_gx_g42"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_spectrum_service.create_optical_spectrum_service", "create_optical_spectrum"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_pipe.fiber_patch.modify_fiber_patch", "modify_fiber_patch"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_pipe.fiber_span.modify_fiber_span", "modify_fiber_span"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_pipe.leased_spectrum.modify_leased_spectrum", "modify_leased_spectrum"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_coherent_pluggable.modify_optical_coherent_pluggable", "modify_optical_coherent_pluggable"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_digital_service.modify_optical_digital_service", "modify_optical_digital_service"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_location.modify_optical_location", "modify_optical_module_location"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_node.nokia_flexils.modify_nokia_flexils", "modify_optical_node_nokia_flexils"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_node.nokia_groove_g30.modify_nokia_groove_g30", "modify_optical_node_nokia_groove_g30"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_node.nokia_gx_g42.modify_nokia_gx_g42", "modify_optical_node_nokia_gx_g42"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_spectrum_service.modify_optical_spectrum_service", "modify_optical_spectrum"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_pipe.fiber_patch.reconcile_fiber_patch", "reconcile_fiber_patch"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_pipe.fiber_span.reconcile_fiber_span", "reconcile_fiber_span"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_pipe.leased_spectrum.reconcile_leased_spectrum", "reconcile_leased_spectrum"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_spectrum_service.reconcile_optical_spectrum_service", "reconcile_optical_spectrum"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_digital_service.reconcile_optical_digital_service", "reconcile_optical_digital_service"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_pipe.fiber_patch.terminate_fiber_patch", "terminate_fiber_patch"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_pipe.fiber_span.terminate_fiber_span", "terminate_fiber_span"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_pipe.leased_spectrum.terminate_leased_spectrum", "terminate_leased_spectrum"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_coherent_pluggable.terminate_optical_coherent_pluggable", "terminate_optical_coherent_pluggable"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_digital_service.terminate_optical_digital_service", "terminate_optical_digital_service"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_location.terminate_optical_location", "terminate_optical_module_location"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_node.nokia_flexils.terminate_nokia_flexils", "terminate_optical_node_nokia_flexils"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_node.nokia_groove_g30.terminate_nokia_groove_g30", "terminate_optical_node_nokia_groove_g30"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_node.nokia_gx_g42.terminate_nokia_gx_g42", "terminate_optical_node_nokia_gx_g42"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_spectrum_service.terminate_optical_spectrum_service", "terminate_optical_spectrum"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_pipe.fiber_patch.validate_fiber_patch", "validate_fiber_patch"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_pipe.fiber_span.validate_fiber_span", "validate_fiber_span"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_pipe.leased_spectrum.validate_leased_spectrum", "validate_leased_spectrum"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_coherent_pluggable.validate_optical_coherent_pluggable", "validate_optical_coherent_pluggable"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_digital_service.validate_optical_digital_service", "validate_optical_digital_service"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_location.validate_optical_location", "validate_optical_module_location"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_node.nokia_flexils.validate_nokia_flexils", "validate_optical_node_nokia_flexils"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_node.nokia_groove_g30.validate_nokia_groove_g30", "validate_optical_node_nokia_groove_g30"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_node.nokia_gx_g42.validate_nokia_gx_g42", "validate_optical_node_nokia_gx_g42"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_spectrum_service.validate_optical_spectrum_service", "validate_optical_spectrum"),
LazyWorkflowInstance("orchestrator.optical.workflows.tasks.bulk_create_optical_nodes", "bulk_create_optical_nodes"),
LazyWorkflowInstance("orchestrator.optical.workflows.tasks.bulk_create_optical_pipes", "bulk_create_optical_pipes"),
