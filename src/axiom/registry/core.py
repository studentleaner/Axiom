from typing import Dict, List, Optional, Any
from ..schemas import BaseAxiomModel, Template, Prompt, Skill, UseCase
from .loader import SchemaLoader

class AxiomRegistry:
    """In-memory registry for indexing and resolving Axiom schemas deterministically by version."""
    
    def __init__(self):
        self._items: Dict[str, List[BaseAxiomModel]] = {}
        self._by_id_version: Dict[str, BaseAxiomModel] = {}
        
        self._by_type: Dict[str, List[str]] = {}
        self._by_capability: Dict[str, List[str]] = {}

    def load_directory(self, path: str):
        raw_schemas = SchemaLoader.scan_directory(path)
        for raw in raw_schemas:
            self.register(raw)
            
    def _parse_version(self, version_str: str) -> tuple:
        try:
            return tuple(map(int, version_str.split(".")))
        except Exception:
            return (0, 0, 0)

    def register(self, raw_data: Dict[str, Any]) -> BaseAxiomModel:
        if "type" not in raw_data:
            raise ValueError("Schema missing required 'type' field.")
            
        t = raw_data["type"]
        if t == "template": model = Template(**raw_data)
        elif t == "prompt": model = Prompt(**raw_data)
        elif t == "skill": model = Skill(**raw_data)
        elif t == "usecase": model = UseCase(**raw_data)
        else: raise ValueError(f"Unknown schema type: {t}")

        version = getattr(model, "version", "1.0.0")
        model_id_version = f"{model.id}@{version}"
        
        if model_id_version in self._by_id_version:
            raise ValueError(f"Version collision: {model_id_version} is already registered.")

        self._by_id_version[model_id_version] = model
        self._items.setdefault(model.id, []).append(model)
        
        self._by_type.setdefault(model.type, []).append(model.id)
        if model.capability:
            for cap in model.capability:
                self._by_capability.setdefault(cap, []).append(model.id)
                
        return model

    def get(self, ref: str) -> Optional[BaseAxiomModel]:
        """Gets exact id@version, or highest semantic version if just id is passed."""
        if "@" in ref:
            return self._by_id_version.get(ref)
            
        candidates = self._items.get(ref)
        if not candidates:
            return None
            
        best = sorted(candidates, key=lambda m: self._parse_version(getattr(m, "version", "1.0.0")))
        return best[-1]

    def find_by_type(self, entity_type: str) -> List[BaseAxiomModel]:
        ids = self._by_type.get(entity_type, [])
        return [self.get(i) for i in ids if self.get(i)]

    def find_by_capability(self, capability: str) -> List[BaseAxiomModel]:
        ids = self._by_capability.get(capability, [])
        return [self.get(i) for i in ids if self.get(i)]
