import pytest
from axiom.registry import AxiomRegistry
from axiom.runtime import AxiomRuntime

def test_workflow_conditional_branching():
    r = AxiomRegistry()
    
    r.register({
        "id": "base.agent", "type": "template", "inputs": {"intent": {"type": "string"}},
        "messages": [{"role": "system", "content": "You are processing intent: {{intent}}"}]
    })
    
    r.register({
        "id": "prompt.detect_intent", "type": "prompt", "extends": "base.agent", "inputs": {"intent": {"type": "string"}}
    })
    r.register({
        "id": "prompt.refund", "type": "prompt", "extends": "base.agent", "inputs": {"intent": {"type": "string"}}
    })
    r.register({
        "id": "prompt.shipping", "type": "prompt", "extends": "base.agent", "inputs": {"intent": {"type": "string"}}
    })
    
    r.register({
        "id": "workflow.router",
        "type": "workflow",
        "nodes": {
            "start": {"ref": "prompt.detect_intent"},
            "refund": {"ref": "prompt.refund"},
            "shipping": {"ref": "prompt.shipping"}
        },
        "edges": [
            {"from": "start", "to": "refund", "if": {"var": "intent", "equals": "refund"}},
            {"from": "start", "to": "shipping", "if": {"var": "intent", "equals": "shipping"}}
        ]
    })
    
    engine = AxiomRuntime(r)
    plan = engine.build("workflow.router", {"intent": "refund"})
    
    assert "start" in plan.nodes
    assert "refund" in plan.nodes
    assert "shipping" in plan.nodes
    
    assert plan.nodes["start"].messages[0]["content"] == "You are processing intent: refund"
    
    refund_edge = [e for e in plan.edges if e.to_node == "refund"][0]
    shipping_edge = [e for e in plan.edges if e.to_node == "shipping"][0]
    
    assert refund_edge.condition == {"var": "intent", "equals": "refund"}
    assert shipping_edge.condition == {"var": "intent", "equals": "shipping"}
