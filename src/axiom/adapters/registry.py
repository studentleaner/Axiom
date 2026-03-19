import importlib
from typing import Dict, Type
from .base import BaseAdapter

class AdapterRegistry:
    """Manages discovery and instantiation of Axiom Execution Translators offline seamlessly."""
    
    _adapters: Dict[str, Type[BaseAdapter]] = {}

    @classmethod
    def register(cls, name: str, adapter_cls: Type[BaseAdapter]):
        """Registers an adapter class securely isolated against a canonical string identifier."""
        if not issubclass(adapter_cls, BaseAdapter):
            raise TypeError(f"Adapter '{name}' must safely explicitly inherit from BaseAdapter.")
        cls._adapters[name] = adapter_cls

    @classmethod
    def get(cls, name: str) -> Type[BaseAdapter]:
        """Resolves the framework adapter class constructor completely uninstantiated."""
        if name not in cls._adapters:
            raise ValueError(f"Adapter '{name}' securely not found. Please dynamically load_plugin() the appropriate module.")
        return cls._adapters[name]

    @classmethod
    def load_plugin(cls, module_path: str):
        """Dynamically safely evaluates an external Python package bridging native offline registration definitions."""
        try:
            importlib.import_module(module_path)
        except ImportError as e:
            raise ImportError(f"Failed to securely load generic Axiom plugin module '{module_path}': {str(e)}")
