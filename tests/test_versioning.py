import pytest
from axiom.registry import AxiomRegistry
from axiom.runtime import AxiomRuntime

def test_registry_version_resolution():
    r = AxiomRegistry()
    r.register({
        "id": "prompt.hello", "type": "prompt", "version": "1.0.0",
        "inputs": {}, "config": {"temperature": 0.5}
    })
    r.register({
        "id": "prompt.hello", "type": "prompt", "version": "1.1.0",
        "inputs": {}, "config": {"temperature": 1.0}
    })
    
    # Implicit latest fetch
    latest = r.get("prompt.hello")
    assert latest.version == "1.1.0"
    
    # Explicit version fetch
    v1 = r.get("prompt.hello@1.0.0")
    assert v1.version == "1.0.0"

def test_conflict_throws_error():
    r = AxiomRegistry()
    r.register({"id": "prompt.hello", "type": "prompt", "version": "1.0.0"})
    with pytest.raises(ValueError, match="Version collision"):
        r.register({"id": "prompt.hello", "type": "prompt", "version": "1.0.0"})

def test_ast_pins_versions():
    r = AxiomRegistry()
    r.register({"id": "prompt.hello", "type": "prompt", "version": "1.2.5"})
    
    engine = AxiomRuntime(r)
    plan = engine.build("prompt.hello")
    
    node = list(plan.nodes.values())[0]
    
    # The output plan must explicitly freeze the semantic version natively
    assert node.ref == "prompt.hello@1.2.5"
    assert node.resolved_prompts[0] == "prompt.hello@1.2.5"
