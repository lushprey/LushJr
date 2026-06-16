"""
integrations/my_data/directive.py
──────────────────────────────────
Directive that defines tools and system prompt for data operations.

A Directive bundles:
1. A list of Tool objects (what the AI can do)
2. A system prompt (how the AI should behave)

Each tool wraps a method from your DataIntegration backend.

To customize:
- Modify DEFAULT_SYSTEM_PROMPT to change instructions
- Add/remove tools in __init__
- Create custom Tool subclasses for domain-specific logic
"""

import logging
from typing import Any

from integrations.base import BaseDirective, Tool, ToolResult, DataIntegration

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# Custom tools (optional — adapt to your domain)
# ──────────────────────────────────────────────────────────────────────────────

class QueryTool(Tool):
    """
    Query entities with flexible filters.

    This is a generic tool that works with any DataIntegration.
    Filters are backend-specific — the AI will learn from the description.
    """

    def __init__(self, integration: DataIntegration) -> None:
        self._integration = integration

    @property
    def name(self) -> str:
        return "query"

    @property
    def description(self) -> str:
        return "Search for entities matching given criteria (filters are flexible)"

    @property
    def params(self) -> dict:
        return {
            "filters": {
                "type": "object",
                "description": "Filter object (e.g., {'status': 'open', 'date_start': '2025-01-01'})",
                "required": True,
            },
        }

    def execute(self, params: dict[str, Any]) -> ToolResult:
        filters = params.get("filters", {})

        try:
            entities = self._integration.query(filters)

            if not entities:
                return ToolResult(
                    success=True,
                    message="No entities found matching the criteria.",
                    data={"count": 0, "entities": []},
                )

            # Format entities for display
            lines = [f"Found {len(entities)} entity/entities:"]
            for entity in entities:
                lines.append(f"  - {entity.title} (ID: {entity.id})")

            return ToolResult(
                success=True,
                message="\n".join(lines),
                data={
                    "count": len(entities),
                    "entities": [
                        {
                            "id": e.id,
                            "title": e.title,
                            "metadata": e.metadata,
                        }
                        for e in entities
                    ],
                },
            )
        except Exception as e:
            logger.exception("Query failed")
            return ToolResult(success=False, message=f"Query failed: {e}")


class CreateTool(Tool):
    """Create a new entity."""

    def __init__(self, integration: DataIntegration) -> None:
        self._integration = integration

    @property
    def name(self) -> str:
        return "create"

    @property
    def description(self) -> str:
        return "Create a new entity with title and metadata"

    @property
    def params(self) -> dict:
        return {
            "title": {
                "type": "string",
                "description": "Entity title/name",
                "required": True,
            },
            "metadata": {
                "type": "object",
                "description": "Additional data (e.g., {'status': 'new', 'priority': 'high'})",
                "required": False,
            },
        }

    def execute(self, params: dict[str, Any]) -> ToolResult:
        title = params.get("title")
        metadata = params.get("metadata", {})

        if not title:
            return ToolResult(success=False, message="Title is required")

        try:
            from integrations.base import DataEntity

            entity = DataEntity(id="", title=title, metadata=metadata)
            created = self._integration.create(entity)

            return ToolResult(
                success=True,
                message=f"✅ Created: {created.title} (ID: {created.id})",
                data={
                    "id": created.id,
                    "title": created.title,
                    "metadata": created.metadata,
                },
            )
        except Exception as e:
            logger.exception("Create failed")
            return ToolResult(success=False, message=f"Create failed: {e}")


class UpdateTool(Tool):
    """Update an existing entity."""

    def __init__(self, integration: DataIntegration) -> None:
        self._integration = integration

    @property
    def name(self) -> str:
        return "update"

    @property
    def description(self) -> str:
        return "Update an existing entity by ID"

    @property
    def params(self) -> dict:
        return {
            "entity_id": {
                "type": "string",
                "description": "ID of the entity to update",
                "required": True,
            },
            "updates": {
                "type": "object",
                "description": "Fields to update (e.g., {'title': 'new title', 'status': 'done'})",
                "required": True,
            },
        }

    def execute(self, params: dict[str, Any]) -> ToolResult:
        entity_id = params.get("entity_id")
        updates = params.get("updates", {})

        if not entity_id:
            return ToolResult(success=False, message="entity_id is required")
        if not updates:
            return ToolResult(success=False, message="updates object is required")

        try:
            updated = self._integration.update(entity_id, updates)

            return ToolResult(
                success=True,
                message=f"✅ Updated: {updated.title}",
                data={
                    "id": updated.id,
                    "title": updated.title,
                    "metadata": updated.metadata,
                },
            )
        except Exception as e:
            logger.exception("Update failed")
            return ToolResult(success=False, message=f"Update failed: {e}")


class DeleteTool(Tool):
    """Delete an entity."""

    def __init__(self, integration: DataIntegration) -> None:
        self._integration = integration

    @property
    def name(self) -> str:
        return "delete"

    @property
    def description(self) -> str:
        return "Delete an entity by ID"

    @property
    def params(self) -> dict:
        return {
            "entity_id": {
                "type": "string",
                "description": "ID of the entity to delete",
                "required": True,
            },
        }

    def execute(self, params: dict[str, Any]) -> ToolResult:
        entity_id = params.get("entity_id")

        if not entity_id:
            return ToolResult(success=False, message="entity_id is required")

        try:
            self._integration.delete(entity_id)
            return ToolResult(
                success=True,
                message=f"🗑️ Deleted entity {entity_id}",
            )
        except Exception as e:
            logger.exception("Delete failed")
            return ToolResult(success=False, message=f"Delete failed: {e}")


# ──────────────────────────────────────────────────────────────────────────────
# Default system prompt
# ──────────────────────────────────────────────────────────────────────────────

DEFAULT_SYSTEM_PROMPT = """\
Available tools:
- query  : Search for entities
- create : Add a new entity
- update : Modify an existing entity
- delete : Remove an entity
- chat   : Answer general questions

Guidelines:
- Use query first if the user asks about existing entities
- Confirm before deleting (ask user if not explicit)
- Be concise in confirmations
"""


# ──────────────────────────────────────────────────────────────────────────────
# Directive
# ──────────────────────────────────────────────────────────────────────────────

class MyDataDirective(BaseDirective):
    """
    Bundles tools and system prompt for data operations.

    Parameters
    ----------
    integration : DataIntegration
        The backend to use for all operations
    system_prompt : str, optional
        Custom system prompt (overrides default)
    extra_tools : list[Tool], optional
        Additional custom tools to register
    """

    def __init__(
        self,
        integration: DataIntegration,
        system_prompt: str = None,
        extra_tools: list[Tool] = None,
    ) -> None:
        # Build tool list
        tools = [
            QueryTool(integration),
            CreateTool(integration),
            UpdateTool(integration),
            DeleteTool(integration),
        ]

        if extra_tools:
            tools.extend(extra_tools)

        # Use custom prompt or default
        final_prompt = system_prompt or DEFAULT_SYSTEM_PROMPT

        super().__init__(tools=tools, system_prompt=final_prompt)


__all__ = [
    "MyDataDirective",
    "QueryTool",
    "CreateTool",
    "UpdateTool",
    "DeleteTool",
    "DEFAULT_SYSTEM_PROMPT",
]