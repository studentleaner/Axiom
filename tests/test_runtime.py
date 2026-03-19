import pytest
from axiom.registry import AxiomRegistry
from axiom.runtime import AxiomRuntime

def get_test_registry():
    r = AxiomRegistry()
    r.register({
        "id": "base.chat",
        "type": "template",
        "inputs": {"context": {"type": "string"}},
        "messages": [{"role": "system", "content": "You are helpful."}]
    })
    
    r.register({
        "id": "prompt.chat",
        "type": "prompt",
        "extends": "base.chat",
        "inputs": {"query": {"type": "string"}},
        "config": {"temperature": 0.5}
    })
    
    r.register({
        "id": "skill.chat",
        "type": "skill",
        "strategy": "pipeline",
        "prompts": ["prompt.chat"]
    })
    
    r.register({
        "id": "usecase.chat",
        "type": "usecase",
        "skills": ["skill.chat"]
    })
    
    return r

def test_runtime_compiles_usecase():
    r = get_test_registry()
    engine = AxiomRuntime(r)
    
    inputs = {"query": "Tell me a joke.", "context": "Be funny."}
    plan = engine.build("usecase.chat", inputs)
    
    assert plan.id == "plan.usecase.chat"
    assert "node_skill_chat" in plan.nodes
    assert len(plan.edges) > 0
    assert plan.nodes["node_skill_chat"].type == "prompt"
    
    node = plan.nodes["node_skill_chat"]
    assert len(node.messages) == 1
    assert node.messages[0]["content"] == "You are helpful."
    assert node.config["temperature"] == 0.5

def test_runtime_fails_missing_inputs():
    r = get_test_registry()
    engine = AxiomRuntime(r)
    
    with pytest.raises(ValueError, match="Missing required input 'context'"):
        engine.build("prompt.chat", {"query": "Hello"})
        
    with pytest.raises(ValueError, match="Missing required input 'query'"):
        engine.build("prompt.chat", {"context": "Hello"})
