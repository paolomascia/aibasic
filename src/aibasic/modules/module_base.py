"""
Base Module Interface for AIbasic Modules

This module defines the standard interface that all AIbasic modules should implement
to provide rich metadata for the compiler and documentation generation.
"""

import sys
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod


class ModuleMetadata:
    """Standard metadata structure for AIbasic modules."""

    def __init__(
        self,
        name: str,
        task_type: str,
        description: str,
        version: str = "1.0.0",
        keywords: Optional[List[str]] = None,
        dependencies: Optional[List[str]] = None
    ):
        self.name = name
        self.task_type = task_type
        self.description = description
        self.version = version
        self.keywords = keywords or []
        self.dependencies = dependencies or []

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary format."""
        return {
            "name": self.name,
            "task_type": self.task_type,
            "description": self.description,
            "version": self.version,
            "keywords": self.keywords,
            "dependencies": self.dependencies
        }


class MethodInfo:
    """Information about a module method."""

    def __init__(
        self,
        name: str,
        description: str,
        parameters: Dict[str, str],
        returns: str,
        examples: Optional[List[str]] = None
    ):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.returns = returns
        self.examples = examples or []

    def to_dict(self) -> Dict[str, Any]:
        """Convert method info to dictionary format."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "returns": self.returns,
            "examples": self.examples
        }


class AIbasicModuleBase(ABC):
    """
    Base class for AIbasic modules.

    All modules should inherit from this class or implement these methods
    to provide rich metadata for the compiler.
    """

    @classmethod
    @abstractmethod
    def get_metadata(cls) -> ModuleMetadata:
        """
        Get module metadata.

        Returns:
            ModuleMetadata: Module information including name, description, keywords
        """
        pass

    @classmethod
    @abstractmethod
    def get_usage_notes(cls) -> List[str]:
        """
        Get detailed usage notes for the module.

        Returns:
            List[str]: Usage notes, best practices, and important information
        """
        pass

    @classmethod
    @abstractmethod
    def get_methods_info(cls) -> List[MethodInfo]:
        """
        Get information about all public methods in the module.

        Returns:
            List[MethodInfo]: Detailed information about each method
        """
        pass

    @classmethod
    @abstractmethod
    def get_examples(cls) -> List[str]:
        """
        Get usage examples in AIbasic natural language format.

        Returns:
            List[str]: Example AIbasic instructions
        """
        pass

    @classmethod
    def get_full_documentation(cls) -> Dict[str, Any]:
        """
        Get complete documentation for the module.

        Returns:
            Dict[str, Any]: Complete documentation including metadata, usage notes, methods, examples
        """
        metadata = cls.get_metadata()

        return {
            "metadata": metadata.to_dict(),
            "usage_notes": cls.get_usage_notes(),
            "methods": [method.to_dict() for method in cls.get_methods_info()],
            "examples": cls.get_examples()
        }


def collect_all_modules_metadata() -> Dict[str, Dict[str, Any]]:
    """
    Collect metadata from all available modules.

    Returns:
        Dict[str, Dict[str, Any]]: Dictionary mapping task types to module documentation
    """
    from aibasic import modules

    all_metadata = {}

    # Get all module classes - some may not be importable if dependencies are missing
    module_classes = []
    for name in dir(modules):
        if name.endswith('Module') and not name.startswith('_'):
            try:
                module_class = getattr(modules, name)
                module_classes.append(module_class)
            except Exception as e:
                # Module couldn't be imported (likely missing dependencies)
                print(f"Warning: {name} could not be imported: {e}", file=sys.stderr)
                continue

    for module_class in module_classes:
        # Check if module implements the interface
        if hasattr(module_class, 'get_metadata'):
            try:
                metadata = module_class.get_metadata()
                task_type = metadata.task_type
                all_metadata[task_type] = module_class.get_full_documentation()
            except Exception as e:
                # Module doesn't fully implement interface yet, skip
                print(f"Warning: {module_class.__name__} metadata error: {e}", file=sys.stderr)
                continue

    return all_metadata


def generate_prompt_context(task_type: str) -> str:
    """
    Generate rich context for LLM prompt based on module metadata.

    Args:
        task_type: The task type identifier

    Returns:
        str: Formatted context for LLM prompt
    """
    all_metadata = collect_all_modules_metadata()

    if task_type not in all_metadata:
        return ""

    doc = all_metadata[task_type]
    metadata = doc["metadata"]

    context = f"""
## {metadata['name']} Module

**Description:** {metadata['description']}
**Task Type:** ({task_type})
**Version:** {metadata['version']}

### Usage Notes:
"""

    for note in doc["usage_notes"]:
        context += f"- {note}\n"

    context += "\n### Available Methods:\n"
    for method in doc["methods"]:
        context += f"\n**{method['name']}**\n"
        context += f"  Description: {method['description']}\n"
        context += f"  Parameters:\n"
        for param, desc in method['parameters'].items():
            context += f"    - {param}: {desc}\n"
        context += f"  Returns: {method['returns']}\n"
        if method['examples']:
            context += f"  Examples:\n"
            for example in method['examples']:
                context += f"    - {example}\n"

    context += "\n### AIbasic Examples:\n"
    for example in doc["examples"]:
        context += f"  {example}\n"

    return context
