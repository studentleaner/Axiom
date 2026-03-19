from typing import Dict, Any, List
from ..registry import AxiomRegistry
from ..schemas import Template, Prompt, Skill, UseCase
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
        
        last_node_id = "start"

        def _add_prompt_node(prompt_id: str, last_edge_from: str) -> str:
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
            
            # Freeze the Exact Deterministic Execution Variables
            version = getattr(prompt, "version", "1.0.0")
            frozen_ref = f"{prompt.id}@{version}"
            
            node_id = f"node_{prompt.id.replace('.', '_')}"
            while node_id in nodes:
                 node_id += "_next"
                 
            nodes[node_id] = ExecutionNode(
                type="prompt",
                ref=frozen_ref,       
                messages=resolved_messages,
                config=merged_config,
                resolved_prompts=[frozen_ref] 
            )
            edges.append(ExecutionEdge(**{"from": last_edge_from, "to": node_id}))
            return node_id

        if isinstance(entry, UseCase):
            for skill_id in entry.skills:
                skill = self.registry.get(skill_id)
                if not skill or not isinstance(skill, Skill):
                    raise ValueError(f"Skill '{skill_id}' not found.")
                for prompt_id in (skill.prompts or []):
                    last_node_id = _add_prompt_node(prompt_id, last_node_id)
                    
        elif isinstance(entry, Skill):
            for prompt_id in (entry.prompts or []):
                last_node_id = _add_prompt_node(prompt_id, last_node_id)
                
        elif isinstance(entry, Prompt):
            _add_prompt_node(entry.id, last_node_id)

        else:
            raise ValueError(f"Unsupported entrypoint type: {type(entry).__name__}")
            
        return ExecutionPlan(
            id=f"plan.{entrypoint_id}",
            entrypoint=entrypoint_id,
            nodes=nodes,
            edges=edges,
            resolved_inputs=runtime_inputs
        )
