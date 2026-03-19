from typing import Dict, Any, List, Optional
from ..registry import AxiomRegistry
from ..schemas import Template, Prompt, Skill, UseCase, Workflow
from ..schemas.execution_plan import ExecutionPlan, ExecutionNode, ExecutionEdge

class AxiomRuntime:
    """Deterministic graph compiler for Axiom execution plans."""
    
    def __init__(self, registry: AxiomRegistry):
        self.registry = registry

    def _render_content(self, content: str, variables: Dict[str, Any]) -> str:
        """Simple template rendering replacing {{var}} with values."""
        result = content
        for k, v in variables.items():
            result = result.replace(f"{{{{{k}}}}}", str(v))
        return result

    def build(self, entrypoint_id: str, runtime_inputs: Dict[str, Any] = None) -> ExecutionPlan:
        runtime_inputs = runtime_inputs or {}
        
        entry = self.registry.get(entrypoint_id)
        if not entry:
            raise ValueError(f"Entrypoint '{entrypoint_id}' not found in registry.")
            
        nodes: Dict[str, ExecutionNode] = {}
        edges: List[ExecutionEdge] = []

        def _add_prompt_node(prompt_id: str, custom_node_id: Optional[str] = None) -> str:
            prompt = self.registry.get(prompt_id)
            if not prompt or not isinstance(prompt, Prompt):
                raise ValueError(f"Prompt '{prompt_id}' not found or invalid.")
                
            template = None
            if prompt.extends:
                template = self.registry.get(prompt.extends)
                if not template or not isinstance(template, Template):
                    raise ValueError(f"Base template '{prompt.extends}' for prompt '{prompt_id}' not found.")
                    
                for req_input in template.inputs.keys():
                    if req_input not in runtime_inputs:
                        raise ValueError(f"Missing required input '{req_input}' for inherited template '{template.id}'")
            
            for req_input in prompt.inputs.keys():
                if req_input not in runtime_inputs:
                    raise ValueError(f"Missing required input '{req_input}' for prompt '{prompt.id}'")

            resolved_messages = []
            if template and template.messages:
                for msg in template.messages:
                    rendered = self._render_content(msg.content, runtime_inputs)
                    resolved_messages.append({"role": msg.role.value, "content": rendered})
            
            merged_config = prompt.config.model_dump(exclude_unset=True) if prompt.config else {}
            
            version = getattr(prompt, "version", "1.0.0")
            frozen_ref = f"{prompt.id}@{version}"
            
            node_id = custom_node_id or f"node_{prompt.id.replace('.', '_')}"
            while node_id in nodes and not custom_node_id:
                 node_id += "_next"
                 
            nodes[node_id] = ExecutionNode(
                type="prompt",
                ref=frozen_ref,       
                messages=resolved_messages,
                config=merged_config,
                resolved_prompts=[frozen_ref] 
            )
            return node_id

        def _compile_target(ref_id: str, base_node_id: str) -> tuple[str, str]:
            """Compiles a single ref (Prompt or Skill) subgraph. 
               Returns (first_node_id, last_node_id).
            """
            target = self.registry.get(ref_id)
            if not target:
                raise ValueError(f"Target '{ref_id}' not found.")
                
            first_id = None
            prev_id = None
            
            if isinstance(target, Prompt):
                n = _add_prompt_node(target.id, base_node_id)
                return (n, n)
            elif isinstance(target, Skill):
                for i, prompt_id in enumerate(target.prompts or []):
                    n_id = f"{base_node_id}_{i}" if i > 0 else base_node_id
                    n = _add_prompt_node(prompt_id, n_id)
                    if not first_id:
                        first_id = n
                    if prev_id:
                        edges.append(ExecutionEdge(**{"from": prev_id, "to": n}))
                    prev_id = n
                return (first_id or base_node_id, prev_id or base_node_id)
            else:
                raise ValueError(f"Workflow nodes must reference Skills or Prompts. Found: {type(target).__name__}")

        if isinstance(entry, Workflow):
            wf_topology = {}
            for wf_node_id, wf_node in entry.nodes.items():
                first_node, last_node = _compile_target(wf_node.ref, wf_node_id)
                wf_topology[wf_node_id] = (first_node, last_node)
                
            for edge in entry.edges:
                from_id = edge.from_node
                to_id = edge.to_node
                
                if from_id not in wf_topology and from_id != "start":
                    raise ValueError(f"Workflow edge from unknown node: {from_id}")
                if to_id not in wf_topology:
                    raise ValueError(f"Workflow edge to unknown node: {to_id}")
                    
                actual_from = wf_topology[from_id][1] if from_id in wf_topology else "start"
                actual_to = wf_topology[to_id][0]
                
                condition_dump = edge.condition.model_dump() if edge.condition else None
                edges.append(ExecutionEdge(**{"from": actual_from, "to": actual_to, "condition": condition_dump}))

        elif isinstance(entry, UseCase):
            last_node_id = "start"
            for skill_id in entry.skills:
                first, last = _compile_target(skill_id, f"node_{skill_id.replace('.', '_')}")
                edges.append(ExecutionEdge(**{"from": last_node_id, "to": first}))
                last_node_id = last
                
        elif isinstance(entry, Skill):
            last_node_id = "start"
            first, last = _compile_target(entry.id, f"node_{entry.id.replace('.', '_')}")
            edges.append(ExecutionEdge(**{"from": last_node_id, "to": first}))
            
        elif isinstance(entry, Prompt):
            last_node_id = "start"
            first, last = _compile_target(entry.id, f"node_{entry.id.replace('.', '_')}")
            edges.append(ExecutionEdge(**{"from": last_node_id, "to": first}))

        else:
            raise ValueError(f"Unsupported entrypoint type: {type(entry).__name__}")
            
        return ExecutionPlan(
            id=f"plan.{entrypoint_id}",
            entrypoint=entrypoint_id,
            nodes=nodes,
            edges=edges,
            resolved_inputs=runtime_inputs
        )
