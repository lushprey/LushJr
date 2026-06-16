"""
integrations/my_data/integration.py
────────────────────────────────────
Custom data integration implementation.

This template shows how to create a data backend that works with
the DataIntegration interface. Works with ANY data type:
- Calendar events
- Tasks
- Notes
- CRM contacts
- Database records
- Custom data

Key methods to implement:
- query(): Retrieve entities matching filters
- create(): Add new entity and return with ID
- update(): Modify entity and return updated version
- delete(): Remove/archive entity

To use:
1. Copy to integrations/my_data/
2. Implement the abstract methods
3. Handle your specific backend's API/protocol
"""

import logging
from typing import Any

from integrations.base import BaseIntegration, DataIntegration, DataEntity

logger = logging.getLogger(__name__)


class MyDataIntegration(BaseIntegration, DataIntegration):
    """
    Custom data backend for [YOUR_SERVICE_NAME].

    Implements the generic DataIntegration interface, allowing it to
    work with any data type your service supports.

    Parameters
    ----------
    token : str
        Authentication token for your service
    api_base : str, optional
        Base URL for your API
    database_id : str, optional
        ID of the database/workspace/collection to use
    other_config : str, optional
        Add whatever configuration your backend needs
    """

    def __init__(
        self,
        token: str,
        api_base: str = None,
        database_id: str = None,
        **kwargs,
    ) -> None:
        super().__init__()

        self.token = token
        self.api_base = api_base
        self.database_id = database_id

        # TODO: Initialize your API client here
        # Examples:
        #   self.client = httpx.Client(
        #       base_url=self.api_base,
        #       headers={"Authorization": f"Bearer {self.token}"}
        #   )
        #   self.client = MyServiceClient(token=token, api_base=api_base)

        logger.info(f"Initialized {self.__class__.__name__}")

    # ──────────────────────────────────────────────────────────────────────
    # DataIntegration interface (REQUIRED)
    # ──────────────────────────────────────────────────────────────────────

    def query(self, filters: dict[str, Any]) -> list[DataEntity]:
        """
        Query entities matching the given filters.

        Filters are completely flexible — your implementation decides
        how to interpret them based on your backend's capabilities.

        Examples of filter dicts:
        - Calendar: {"date_start": "2025-01-01", "date_end": "2025-12-31"}
        - Tasks: {"status": "open", "assigned_to": "john"}
        - Notes: {"tag": "work", "created_after": "2025-01-01"}
        - CRM: {"lead_status": "qualified", "industry": "tech"}

        Args:
            filters: Dictionary of filter criteria (backend-specific)

        Returns:
            List of DataEntity objects matching the filters

        Raises:
            Should return empty list if no matches, not raise errors
        """
        logger.debug(f"Querying with filters: {filters}")

        # TODO: Implement your query logic
        # Example pseudo-code:
        # response = self.client.get(
        #     f"/entities",
        #     params=filters,
        # )
        # return [self._parse_entity(e) for e in response.json()["results"]]

        raise NotImplementedError("Implement query() for your backend")

    def create(self, entity: DataEntity) -> DataEntity:
        """
        Create a new entity in your backend.

        The entity's ID may be empty — your backend should assign one
        and return the entity with the populated ID.

        Args:
            entity: DataEntity with title and metadata set
                   (id may be empty)

        Returns:
            The created entity WITH id assigned by backend

        Raises:
            Should raise descriptive errors only on real failures
        """
        logger.debug(f"Creating entity: {entity.title}")

        # TODO: Implement your create logic
        # Example pseudo-code:
        # response = self.client.post(
        #     f"/entities",
        #     json={"title": entity.title, **entity.metadata},
        # )
        # created_id = response.json()["id"]
        # entity.id = created_id
        # return entity

        raise NotImplementedError("Implement create() for your backend")

    def update(self, entity_id: str, updates: dict[str, Any]) -> DataEntity:
        """
        Update an entity and return the updated version.

        Updates dict contains only the fields to change.
        You must fetch the current entity, apply updates, and return it.

        Args:
            entity_id: ID of the entity to update
            updates: Dictionary of fields to update
                    (e.g., {"title": "new title", "status": "done"})

        Returns:
            The updated entity (with all fields)

        Raises:
            May raise if entity not found
        """
        logger.debug(f"Updating entity {entity_id} with: {updates}")

        # TODO: Implement your update logic
        # Example pseudo-code:
        # response = self.client.patch(
        #     f"/entities/{entity_id}",
        #     json=updates,
        # )
        # return self._parse_entity(response.json())

        raise NotImplementedError("Implement update() for your backend")

    def delete(self, entity_id: str) -> None:
        """
        Delete or archive an entity.

        Implementation-dependent: "delete" might mean:
        - Permanently remove (rare, risky)
        - Archive (safer, reversible)
        - Mark as inactive
        - Move to trash

        Choose what makes sense for your backend.

        Args:
            entity_id: ID of the entity to delete

        Raises:
            May raise if entity not found
        """
        logger.debug(f"Deleting entity {entity_id}")

        # TODO: Implement your delete logic
        # Example pseudo-code:
        # self.client.delete(f"/entities/{entity_id}")
        # OR for soft delete:
        # self.client.patch(f"/entities/{entity_id}", json={"archived": True})

        raise NotImplementedError("Implement delete() for your backend")

    # ──────────────────────────────────────────────────────────────────────
    # Private helpers (optional)
    # ──────────────────────────────────────────────────────────────────────

    def _parse_entity(self, raw: dict[str, Any]) -> DataEntity:
        """
        Convert a raw API response to a DataEntity.

        Implement this helper to DRY up the conversion logic.

        Args:
            raw: Raw response from your API

        Returns:
            DataEntity with id, title, and metadata populated
        """
        # TODO: Implement parsing logic for your backend
        # Example:
        # return DataEntity(
        #     id=raw.get("id"),
        #     title=raw.get("title") or raw.get("name"),
        #     metadata={
        #         "created_at": raw.get("created_at"),
        #         "updated_at": raw.get("updated_at"),
        #         "status": raw.get("status"),
        #         # ... other fields
        #     }
        # )

        raise NotImplementedError("Implement _parse_entity() for your backend")


__all__ = ["MyDataIntegration"]