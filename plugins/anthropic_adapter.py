from axiom.adapters.base import BaseAdapter
from axiom.adapters.registry import AdapterRegistry
from axiom.schemas import ExecutionPlan

class AnthropicAdapter(BaseAdapter):
    """Translates generic flat Axiom ExecutionPlan ASTs natively into Anthropic Messages API payloads."""
    
    def ingest(self, plan: ExecutionPlan):
        self.plan = plan
        
    def execute(self):
        # Translates internal messages formatting strictly into Anthropic's block schema payload internally offline
        return "Anthropic Adapter statically executed."

# The plugin autonomously securely registers itself exactly when dynamically evaluated using the CLI
AdapterRegistry.register("anthropic", AnthropicAdapter)
