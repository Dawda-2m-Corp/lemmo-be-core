from abc import ABCMeta, abstractmethod
from graphene import Mutation, Boolean, String, JSONString, List
from graphene.types.objecttype import ObjectTypeMeta
from typing import Any, Dict, List, Optional, Union
from core.app_utils import lemmo_message, validate_required_fields, sanitize_data
import graphene
import logging
import traceback

logger = logging.getLogger(__name__)


class GrapheneABCMeta(ABCMeta, ObjectTypeMeta):
    pass


class CoreAuthenticatedMutation(graphene.Mutation, metaclass=GrapheneABCMeta):
    """
    Abstract base class for mutations that require authentication.
    Returns lemmo_message format responses.
    """

    success = graphene.Boolean()
    message = graphene.String()
    error_details = graphene.List(graphene.String)
    data = graphene.JSONString()  # Use JSONString for flexible data structure
    errors = graphene.List(graphene.String)

    @classmethod
    def mutate(cls, root, info, **data):
        """
        Main mutation entry point that handles authentication before
        calling the concrete implementation.
        """
        # Check if user is authenticated
        user = cls.get_authenticated_user(info)
        if not user:
            result = lemmo_message(
                success=False,
                message="Authentication required",
                error_details=["User not authenticated"],
            )
            return cls(**result)

        try:
            # Validate required fields if specified
            if hasattr(cls, "required_fields"):
                missing_fields = validate_required_fields(data, cls.required_fields)
                if missing_fields:
                    result = lemmo_message(
                        success=False,
                        message="Missing required fields",
                        error_details=[f"Missing fields: {', '.join(missing_fields)}"],
                        data=data,
                    )
                    return cls(**result)

            # Sanitize data if allowed fields are specified
            if hasattr(cls, "allowed_fields"):
                data = sanitize_data(data, cls.allowed_fields)

            # Check permissions if needed
            if hasattr(cls, "check_permissions") and not cls.check_permissions(
                user, **data
            ):
                result = lemmo_message(
                    success=False,
                    data=data,
                    message="Insufficient permissions",
                    error_details=["User does not have required permissions"],
                )
                return cls(**result)

            # Call the concrete mutation implementation
            result = cls.perform_mutation(root, info, user, **data)
            return cls(**result)

        except Exception as e:
            logger.error(f"Error during mutation execution: {e}", exc_info=True)
            result = lemmo_message(
                success=False,
                data=data,
                message="An error occurred during mutation execution",
                error_details=[traceback.format_exc()],
            )
            return cls(**result)

    @classmethod
    def get_authenticated_user(cls, info):
        """
        Extract and validate the authenticated user from the request context.
        Override this method to implement your authentication logic.
        """
        # Example implementation - adjust based on your auth system
        context = info.context
        if hasattr(context, "user") and context.user.is_authenticated:
            return context.user

        # Alternative: JWT token validation
        # auth_header = context.META.get('HTTP_AUTHORIZATION')
        # if auth_header and auth_header.startswith('Bearer '):
        #     token = auth_header.split(' ')[1]
        #     return validate_jwt_token(token)

        return None

    @classmethod
    def check_permissions(cls, user, **data) -> bool:
        """
        Check if the user has required permissions for this mutation.
        Override this method to implement permission checking.

        Args:
            user: Authenticated user object
            **data: Mutation arguments

        Returns:
            True if user has permissions, False otherwise
        """
        # Default implementation - always allow
        # Override in subclasses to implement specific permission logic
        return True

    @classmethod
    @abstractmethod
    def perform_mutation(cls, root, info, user, **data) -> Dict[str, Any]:
        """
        Abstract method that concrete mutations must implement.
        This is where the actual mutation logic goes.

        Args:
            root: GraphQL root value
            info: GraphQL resolve info
            user: Authenticated user object
            **data: Mutation arguments

        Returns:
            Dictionary with lemmo_message format
        """
        pass


class CoreUnauthenticatedMutation(graphene.Mutation, metaclass=GrapheneABCMeta):
    """
    Abstract base class for mutations that don't require authentication.
    Returns lemmo_message format responses.
    """

    success = graphene.Boolean()
    message = graphene.String()
    error_details = graphene.List(graphene.String)
    data = graphene.JSONString()
    errors = graphene.List(graphene.String)

    @classmethod
    def mutate(cls, root, info, **data):
        """
        Main mutation entry point that handles validation before
        calling the concrete implementation.
        """
        try:
            # Validate request if validation method exists
            if hasattr(cls, "validate_request") and not cls.validate_request(
                info, **data
            ):
                result = lemmo_message(
                    success=False,
                    message="Invalid request",
                    error_details=["Request validation failed"],
                    data=data,
                )
                return cls(**result)

            # Validate required fields if specified
            if hasattr(cls, "required_fields"):
                missing_fields = validate_required_fields(data, cls.required_fields)
                if missing_fields:
                    result = lemmo_message(
                        success=False,
                        message="Missing required fields",
                        error_details=[f"Missing fields: {', '.join(missing_fields)}"],
                        data=data,
                    )
                    return cls(**result)

            # Sanitize data if allowed fields are specified
            if hasattr(cls, "allowed_fields"):
                data = sanitize_data(data, cls.allowed_fields)

            # Call the concrete mutation implementation
            result = cls.perform_mutation(root, info, **data)
            return cls(**result)

        except Exception as e:
            logger.error(f"Error during mutation execution: {e}", exc_info=True)
            result = lemmo_message(
                success=False,
                data=data,
                message="An error occurred during mutation execution",
                error_details=[traceback.format_exc()],
            )
            return cls(**result)

    @classmethod
    def validate_request(cls, info, **data) -> bool:
        """
        Validate the request before processing.
        Override this method to implement request validation.

        Args:
            info: GraphQL resolve info
            **data: Mutation arguments

        Returns:
            True if request is valid, False otherwise
        """
        # Default implementation - always valid
        # Override in subclasses to implement specific validation logic
        return True

    @classmethod
    @abstractmethod
    def perform_mutation(cls, root, info, **data) -> Dict[str, Any]:
        """
        Abstract method that concrete mutations must implement.
        This is where the actual mutation logic goes.

        Args:
            root: GraphQL root value
            info: GraphQL resolve info
            **data: Mutation arguments

        Returns:
            Dictionary with lemmo_message format
        """
        pass


class CoreQuery(graphene.ObjectType):
    """
    Base class for GraphQL queries with common utilities.
    """

    @classmethod
    def get_user_from_context(cls, info):
        """
        Extract user from GraphQL context.

        Args:
            info: GraphQL resolve info

        Returns:
            User object or None
        """
        context = info.context
        if hasattr(context, "user") and context.user.is_authenticated:
            return context.user
        return None

    @classmethod
    def check_user_permissions(cls, user, required_permissions: List[str]) -> bool:
        """
        Check if user has required permissions.

        Args:
            user: User object
            required_permissions: List of required permissions

        Returns:
            True if user has all required permissions
        """
        if not user:
            return False

        # This is a basic implementation - override based on your permission system
        # Example: check user groups, roles, or specific permissions
        return True


class MutationError(Exception):
    """
    Custom exception for mutation errors.
    """

    def __init__(self, message: str, error_details: Optional[List[str]] = None):
        self.message = message
        self.error_details = error_details or []
        super().__init__(self.message)


class ValidationError(MutationError):
    """
    Exception for validation errors.
    """

    pass


class PermissionError(MutationError):
    """
    Exception for permission errors.
    """

    pass


class BusinessLogicError(MutationError):
    """
    Exception for business logic errors.
    """

    pass
