from abc import ABCMeta, abstractmethod
from graphene import ObjectType, String, Boolean, JSONString, List
from graphene.types.objecttype import ObjectTypeMeta
from typing import Any, Dict, List, Optional, Union
from core.app_utils import lemmo_message
import graphene
import logging

logger = logging.getLogger(__name__)


class GrapheneABCMeta(ABCMeta, ObjectTypeMeta):
    pass


class CoreAuthenticatedQuery(ObjectType, metaclass=GrapheneABCMeta):
    """
    Abstract base class for queries that require authentication.
    Provides common utilities for authenticated queries.
    """

    @classmethod
    def get_authenticated_user(cls, info):
        """
        Extract and validate the authenticated user from the request context.
        Override this method to implement your authentication logic.
        """
        context = info.context
        if hasattr(context, "user") and context.user.is_authenticated:
            return context.user
        return None

    @classmethod
    def check_permissions(cls, user, **kwargs) -> bool:
        """
        Check if the user has required permissions for this query.
        Override this method to implement permission checking.

        Args:
            user: Authenticated user object
            **kwargs: Query arguments

        Returns:
            True if user has permissions, False otherwise
        """
        # Default implementation - always allow
        # Override in subclasses to implement specific permission logic
        return True

    @classmethod
    def resolve_with_auth(cls, root, info, **kwargs):
        """
        Resolve method that handles authentication before calling the concrete implementation.
        """
        # Check if user is authenticated
        user = cls.get_authenticated_user(info)
        if not user:
            return None

        # Check permissions if needed
        if hasattr(cls, "check_permissions") and not cls.check_permissions(
            user, **kwargs
        ):
            return None

        # Call the concrete query implementation
        return cls.perform_resolve(root, info, user, **kwargs)

    @classmethod
    @abstractmethod
    def perform_resolve(cls, root, info, user, **kwargs) -> Any:
        """
        Abstract method that concrete queries must implement.
        This is where the actual query logic goes.

        Args:
            root: GraphQL root value
            info: GraphQL resolve info
            user: Authenticated user object
            **kwargs: Query arguments

        Returns:
            Query result
        """
        pass


class CoreUnauthenticatedQuery(ObjectType, metaclass=GrapheneABCMeta):
    """
    Abstract base class for queries that don't require authentication.
    Provides common utilities for unauthenticated queries.
    """

    @classmethod
    def validate_request(cls, info, **kwargs) -> bool:
        """
        Validate the request before processing.
        Override this method to implement request validation.

        Args:
            info: GraphQL resolve info
            **kwargs: Query arguments

        Returns:
            True if request is valid, False otherwise
        """
        # Default implementation - always valid
        # Override in subclasses to implement specific validation logic
        return True

    @classmethod
    def resolve_with_validation(cls, root, info, **kwargs):
        """
        Resolve method that handles validation before calling the concrete implementation.
        """
        # Validate request if validation method exists
        if hasattr(cls, "validate_request") and not cls.validate_request(
            info, **kwargs
        ):
            return None

        # Call the concrete query implementation
        return cls.perform_resolve(root, info, **kwargs)

    @classmethod
    @abstractmethod
    def perform_resolve(cls, root, info, **kwargs) -> Any:
        """
        Abstract method that concrete queries must implement.
        This is where the actual query logic goes.

        Args:
            root: GraphQL root value
            info: GraphQL resolve info
            **kwargs: Query arguments

        Returns:
            Query result
        """
        pass


class PaginatedQuery(ObjectType):
    """
    Base class for paginated queries.
    """

    class Meta:
        abstract = True

    @classmethod
    def get_pagination_params(cls, **kwargs) -> Dict[str, Any]:
        """
        Extract pagination parameters from query arguments.

        Args:
            **kwargs: Query arguments

        Returns:
            Dictionary with pagination parameters
        """
        page = kwargs.get("page", 1)
        page_size = kwargs.get("page_size", 10)

        # Validate pagination parameters
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 10
        if page_size > 100:  # Limit maximum page size
            page_size = 100

        return {"page": page, "page_size": page_size, "offset": (page - 1) * page_size}

    @classmethod
    def create_paginated_response(
        cls, items: List[Any], total_count: int, page: int, page_size: int
    ) -> Dict[str, Any]:
        """
        Create a paginated response.

        Args:
            items: List of items for current page
            total_count: Total number of items
            page: Current page number
            page_size: Number of items per page

        Returns:
            Dictionary with paginated response
        """
        total_pages = (total_count + page_size - 1) // page_size

        return {
            "items": items,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_count": total_count,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_previous": page > 1,
            },
        }


class FilteredQuery(ObjectType):
    """
    Base class for queries with filtering capabilities.
    """

    class Meta:
        abstract = True

    @classmethod
    def apply_filters(cls, queryset, filters: Dict[str, Any]) -> Any:
        """
        Apply filters to a queryset.

        Args:
            queryset: Django queryset or similar
            filters: Dictionary of filters to apply

        Returns:
            Filtered queryset
        """
        # This is a basic implementation - override based on your filtering needs
        for field, value in filters.items():
            if value is not None:
                if hasattr(queryset, "filter"):
                    queryset = queryset.filter(**{field: value})
        return queryset

    @classmethod
    def apply_ordering(cls, queryset, ordering: List[str]) -> Any:
        """
        Apply ordering to a queryset.

        Args:
            queryset: Django queryset or similar
            ordering: List of ordering fields

        Returns:
            Ordered queryset
        """
        if ordering and hasattr(queryset, "order_by"):
            return queryset.order_by(*ordering)
        return queryset


class QueryError(Exception):
    """
    Custom exception for query errors.
    """

    def __init__(self, message: str, error_details: Optional[List[str]] = None):
        self.message = message
        self.error_details = error_details or []
        super().__init__(self.message)


class QueryValidationError(QueryError):
    """
    Exception for query validation errors.
    """

    pass


class QueryPermissionError(QueryError):
    """
    Exception for query permission errors.
    """

    pass
