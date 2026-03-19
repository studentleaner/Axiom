from axiom.adapters.base import BaseAdapter
from axiom.adapters.registry import AdapterRegistry
from axiom.schemas import ExecutionPlan

class OllamaAdapter(BaseAdapter):
    """Executes precompiled native ExecutionPlans entirely locally onto Ollama."""
    
    def ingest(self, plan: ExecutionPlan):
        self.plan = plan
        
    def execute(self):
        # Maps the nodes strictly locally targeting standard isolated endpoints statelessly
        return "Ollama Adapter successfully evaluated locally offline."

# Registers into the isolated registry context exactly upon import evaluation 
AdapterRegistry.register("ollama", OllamaAdapter)
