"""unidep - Unified Conda and Pip requirements management.

This module contains the Hatchling integration.
"""
from __future__ import annotations

from pathlib import Path

from hatchling.metadata.plugin.interface import MetadataHookInterface
from hatchling.plugin import hookimpl

from unidep._setuptools_integration import get_python_dependencies
from unidep.utils import dependencies_filename, identify_current_platform

__all__ = ["UnidepRequirementsMetadataHook"]


class UnidepRequirementsMetadataHook(MetadataHookInterface):
    """Hatch hook to populate ``'project.depencencies'`` from ``requirements.yaml``."""

    PLUGIN_NAME = "unidep"

    def update(self, metadata: dict) -> None:
        """Update the project table's metadata."""
        if "dependencies" not in metadata.get("dynamic", []):
            return
        project_root = Path().resolve()
        try:
            requirements_file = dependencies_filename(project_root)
        except FileNotFoundError:
            return
        if "dependencies" in metadata:
            error_msg = (
                "You have a requirements.yaml file in your project root or"
                " configured unidep in `pyproject.toml` with [tool.unidep],"
                " but you are also using [project.dependencies]."
                " Please choose either requirements.yaml or"
                " [project.dependencies], but not both."
            )
            raise RuntimeError(error_msg)
        metadata["dependencies"] = get_python_dependencies(
            requirements_file,
            platforms=[identify_current_platform()],
            raises_if_missing=False,
        )


@hookimpl
def hatch_register_metadata_hook() -> type[UnidepRequirementsMetadataHook]:
    return UnidepRequirementsMetadataHook
