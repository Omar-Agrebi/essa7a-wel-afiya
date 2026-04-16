"""Business logic service for the Opportunity domain."""
from uuid import UUID

from fastapi import HTTPException, status

from app.models.opportunity import Opportunity
from app.repositories.opportunity_repository import OpportunityRepository
from app.api.schemas.opportunity_schema import (
    OpportunityCreate,
    OpportunityFilter,
    OpportunityUpdate,
)


class OpportunityService:
    """Service layer for all opportunity-related business operations.

    All DB access is delegated exclusively to :class:`OpportunityRepository`.
    No SQLAlchemy imports or raw queries appear here.
    """

    def __init__(self, repo: OpportunityRepository) -> None:
        """Initialise the service with its repository dependency.

        Args:
            repo: An :class:`OpportunityRepository` instance, injected by
                  the FastAPI dependency system or created directly by an agent.
        """
        self.repo = repo

    # ------------------------------------------------------------------
    # Query methods
    # ------------------------------------------------------------------

    async def list_opportunities(
        self,
        filters: OpportunityFilter,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Opportunity]:
        """Return a filtered, paginated list of opportunities.

        Filters are applied sequentially.  When multiple filters are active
        the result set narrows with each applied filter (AND logic).

        Args:
            filters: An :class:`OpportunityFilter` instance whose non-None
                     fields are applied as query constraints.
            skip:    Number of records to skip (pagination offset).
            limit:   Maximum number of records to return.

        Returns:
            A list of :class:`Opportunity` ORM objects matching all filters.
        """
        # Start with the full set, then intersect with each active filter.
        # Because OpportunityRepository has dedicated filter methods that each
        # return a list, we use the most specific single-filter path for the
        # common single-filter case and fall back to a composed query for the
        # multi-filter scenario handled inside the repository's get_all path.
        #
        # Design decision: to keep services free of SQLAlchemy, multi-filter
        # composition is delegated to a dedicated repository method. For v1 we
        # resolve combinations by fetching the narrowest single filter first.

        results: list[Opportunity] | None = None

        if filters.cluster_id is not None:
            results = await self.repo.get_by_cluster(filters.cluster_id)
        if filters.type is not None:
            by_type = await self.repo.get_by_type(filters.type)
            results = by_type if results is None else [o for o in results if o in by_type]
        if filters.category is not None:
            by_cat = await self.repo.get_by_category(filters.category)
            results = by_cat if results is None else [o for o in results if o in by_cat]
        if filters.keyword is not None:
            by_kw = await self.repo.search(filters.keyword)
            results = by_kw if results is None else [o for o in results if o in by_kw]
        if filters.expiring_in_days is not None:
            by_exp = await self.repo.get_expiring_soon(filters.expiring_in_days)
            results = by_exp if results is None else [o for o in results if o in by_exp]

        # No active filter → return paginated full list
        if results is None:
            results = await self.repo.get_all(skip=skip, limit=limit)
        else:
            results = results[skip : skip + limit]

        return results

    async def get_opportunity(self, id: UUID) -> Opportunity:
        """Retrieve a single opportunity by its primary key.

        Args:
            id: The UUID primary key of the opportunity to fetch.

        Returns:
            The matching :class:`Opportunity` ORM object.

        Raises:
            HTTPException 404: When no opportunity with the given ID exists.
        """
        opp = await self.repo.get_by_id(id)
        if opp is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Opportunity with id '{id}' not found.",
            )
        return opp

    async def search_opportunities(self, keyword: str) -> list[Opportunity]:
        """Full-text keyword search across title and description fields.

        Args:
            keyword: The search term to match (case-insensitive).

        Returns:
            A list of matching :class:`Opportunity` records ordered by
            creation date descending.
        """
        return await self.repo.search(keyword)

    async def get_expiring_soon(self, days: int) -> list[Opportunity]:
        """Return opportunities whose deadline falls within the next *days* days.

        Args:
            days: The look-ahead window in days (e.g. 7 for deadlines this week).

        Returns:
            A list of :class:`Opportunity` records ordered by deadline ascending.
        """
        return await self.repo.get_expiring_soon(days)

    # ------------------------------------------------------------------
    # Mutation methods
    # ------------------------------------------------------------------

    async def create_opportunity(self, data: OpportunityCreate) -> Opportunity:
        """Create a new opportunity after checking for URL uniqueness.

        Args:
            data: Validated :class:`OpportunityCreate` payload.

        Returns:
            The newly created :class:`Opportunity` ORM object.

        Raises:
            HTTPException 409: When an opportunity with the same URL already
                               exists in the database.
        """
        existing = await self.repo.get_by_url(data.url)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"An opportunity with url '{data.url}' already exists.",
            )
        return await self.repo.create(data.model_dump())

    async def update_opportunity(self, id: UUID, data: OpportunityUpdate) -> Opportunity:
        """Apply a partial update to an existing opportunity.

        Args:
            id:   The UUID of the opportunity to update.
            data: Validated :class:`OpportunityUpdate` payload containing the
                  fields to change.  ``None`` values are excluded.

        Returns:
            The updated :class:`Opportunity` ORM object.

        Raises:
            HTTPException 404: When no opportunity with the given ID exists.
        """
        # Verify it exists first so we can return a clean 404.
        await self.get_opportunity(id)

        update_data = data.model_dump(exclude_none=True)
        updated = await self.repo.update(id, update_data)
        if updated is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Opportunity with id '{id}' not found.",
            )
        return updated

    async def delete_opportunity(self, id: UUID) -> bool:
        """Delete an opportunity by its primary key.

        Args:
            id: The UUID of the opportunity to delete.

        Returns:
            ``True`` when the record was successfully deleted.

        Raises:
            HTTPException 404: When no opportunity with the given ID exists.
        """
        deleted = await self.repo.delete(id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Opportunity with id '{id}' not found.",
            )
        return True

    async def bulk_upsert_opportunities(self, items: list[dict]) -> dict:
        """Persist a batch of opportunity dicts produced by the MAS pipeline.

        Delegates directly to :meth:`OpportunityRepository.bulk_upsert` which
        will INSERT new records and UPDATE existing ones (keyed by URL).

        Args:
            items: A list of raw dicts conforming to the unified scraper output
                   schema.  Each dict must contain at minimum ``url`` and
                   ``title``.

        Returns:
            A report dict with keys ``inserted``, ``updated``, and ``errors``.
        """
        return await self.repo.bulk_upsert(items)
