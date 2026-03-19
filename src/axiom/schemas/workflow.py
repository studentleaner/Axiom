from typing import Dict, List, Optional
from pydantic import Field, BaseModel
from .base import BaseAxiomModel

class WorkflowCondition(BaseModel):
    var: str = Field(..., description="The context variable to evaluate")
    equals: str = Field(..., description="The exact value it must equal")

class WorkflowEdge(BaseModel):
    from_node: str = Field(..., alias="from")
    to_node: str = Field(..., alias="to")
    condition: Optional[WorkflowCondition] = Field(default=None, alias="if")

class WorkflowNode(BaseModel):
    ref: str = Field(..., description="The ID of the Skill or Prompt to uniquely execute")

class Workflow(BaseAxiomModel):
    """Declarative DAG for dynamic conditional execution paths."""
    nodes: Dict[str, WorkflowNode] = Field(default_factory=dict)
    edges: List[WorkflowEdge] = Field(default_factory=list)
