from typing import Dict, List, Any, Optional
from pydantic import BaseModel, ConfigDict, Field

class ExecutionNode(BaseModel):
    type: str
    ref: str
    messages: Optional[List[Dict[str, str]]] = None
    config: Optional[Dict[str, Any]] = None
    resolved_prompts: Optional[List[str]] = None

class ExecutionEdge(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    from_node: str = Field(alias="from")
    to_node: str = Field(alias="to")
    condition: Optional[Dict[str, Any]] = None

class ExecutionPlan(BaseModel):
    id: str
    entrypoint: str
    nodes: Dict[str, ExecutionNode]
    edges: List[ExecutionEdge]
    resolved_inputs: Dict[str, Any]
