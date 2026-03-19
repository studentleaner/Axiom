import pytest
from axiom.adapters.base import BaseAdapter
from axiom.adapters.registry import AdapterRegistry
from axiom.schemas import ExecutionPlan

def test_adapter_registry_lifecycle():
    class CustomEnterpriseAdapter(BaseAdapter):
        def ingest(self, plan: ExecutionPlan):
            pass
        def execute(self):
            return "enterprise_executed"

    AdapterRegistry.register("enterprise", CustomEnterpriseAdapter)
     
    cls = AdapterRegistry.get("enterprise")
    assert cls == CustomEnterpriseAdapter
    
    assert cls().execute() == "enterprise_executed"
    
def test_adapter_registry_throws_on_invalid_inheritance():
    class FakeAdapter:
        pass
        
    with pytest.raises(TypeError, match="must safely explicitly inherit from BaseAdapter"):
        AdapterRegistry.register("fake", FakeAdapter)
        
def test_adapter_registry_dynamic_loading(tmp_path):
    plugin_dir = tmp_path / "mock_axiom_plugin"
    plugin_dir.mkdir()
    (plugin_dir / "__init__.py").write_text(
        "from axiom.adapters.base import BaseAdapter\n"
        "from axiom.adapters.registry import AdapterRegistry\n"
        "class MockPlugin(BaseAdapter):\n"
        "    def ingest(self, plan): pass\n"
        "    def execute(self): return 'mock_loaded_dynamic'\n"
        "AdapterRegistry.register('mock_plugin', MockPlugin)\n"
    )
    
    import sys
    sys.path.insert(0, str(tmp_path))
    
    AdapterRegistry.load_plugin("mock_axiom_plugin")
    
    loaded_cls = AdapterRegistry.get("mock_plugin")
    assert loaded_cls().execute() == "mock_loaded_dynamic"
    
    sys.path.pop(0)
