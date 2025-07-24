from abc import ABCMeta, abstractmethod
from graphene import Mutation, Boolean, String, JSONString, List
from graphene.types.objecttype import ObjectTypeMeta
from typing import Any, Dict, List, Optional
from core.app_utils import lemmo_message
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
                error_details=["User not authenticated"]
            )
            return cls(**result)

        try:
            # Check permissions if needed
            if hasattr(cls, 'check_permissions') and not cls.check_permissions(user, **data):
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
                error_details=[traceback.format_exc()]
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
        if hasattr(context, 'user') and context.user.is_authenticated:
            return context.user

        # Alternative: JWT token validation
        # auth_header = context.META.get('HTTP_AUTHORIZATION')
        # if auth_header and auth_header.startswith('Bearer '):
        #     token = auth_header.split(' ')[1]
        #     return validate_jwt_token(token)

        return None

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
            Dict: lemmo_message format dictionary
        """
        pass

    @classmethod
    def check_permissions(cls, user, **data) -> bool:
        """
        Optional permission checking method.
        Override in concrete mutations for specific permission logic.

        Args:
            user: Authenticated user object
            **data: Mutation arguments

        Returns:
            bool: True if user has permission, False otherwise
        """
        return True


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
        Main mutation entry point for unauthenticated mutations.
        """
        try:
            # Optional rate limiting or other checks
            if not cls.validate_request(info, **data):
                result = lemmo_message(
                    success=False,
                    data=data,
                    message="Request validation failed",
                    error_details=["Request did not pass validation checks"]
                )
                return cls(**result)

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
                errors=[str(e)]
            )
            return cls(**result)

    @classmethod
    def validate_request(cls, info, **data) -> bool:
        """
        Optional request validation for unauthenticated mutations.
        Override for rate limiting, CAPTCHA validation, etc.

        Args:
            info: GraphQL resolve info
            **data: Mutation arguments

        Returns:
            bool: True if request is valid, False otherwise
        """
        # Example: Basic rate limiting by IP
        # ip_address = get_client_ip(info.context)
        # return check_rate_limit(ip_address)
        return True

    @classmethod
    @abstractmethod
    def perform_mutation(cls, root, info, **data) -> Dict[str, Any]:
        """
        Abstract method that concrete mutations must implement.
        This is where the actual mutation logic goes.

        Args:
            root: GraphQL resolve info
            info: GraphQL resolve info
            **kwargs: Mutation arguments

        Returns:
            Dict: lemmo_message format dictionary
        """
        pass


# Example concrete implementations

# class CreatePostMutation(CoreAuthenticatedMutation):
#     """Example authenticated mutation for creating a post"""

#     class Arguments:
#         title = graphene.String(required=True)
#         content = graphene.String(required=True)

#     @classmethod
#     def perform_mutation(cls, root, info, user, title, content):
#         # Check specific permissions
#         if not cls.check_permissions(user, action='create_post'):
#             return lemmo_message(
#                 success=False,
#                 message="Insufficient permissions to create post",
#                 error_details=["User does not have create_post permission"]
#             )

#         # Validate input
#         error_details = []
#         if len(title.strip()) < 3:
#             error_details.append("Title must be at least 3 characters long")
#         if len(content.strip()) < 10:
#             error_details.append("Content must be at least 10 characters long")

#         if error_details:
#             return lemmo_message(
#                 success=False,
#                 message="Validation failed",
#                 error_details=error_details
#             )

#         # Create the post (pseudo-code)
#         try:
#             # post = Post.objects.create(
#             #     title=title,
#             #     content=content,
#             #     author=user
#             # )

#             # Mock post data
#             post_data = {
#                 "id": 123,
#                 "title": title,
#                 "content": content,
#                 "author": user.username,
#                 "created_at": "2025-07-24T10:00:00Z"
#             }

#             return lemmo_message(
#                 success=True,
#                 message="Post created successfully",
#                 data={"post": post_data}
#             )

#         except Exception as e:
#             return lemmo_message(
#                 success=False,
#                 message="Failed to create post",
#                 error_details=[f"Database error: {str(e)}"]
#             )

#     @classmethod
#     def check_permissions(cls, user, **kwargs):
#         # Example permission check
#         return hasattr(user, 'has_perm') and user.has_perm('blog.add_post')


# class RegisterUserMutation(CoreUnauthenticatedMutation):
#     """Example unauthenticated mutation for user registration"""

#     class Arguments:
#         email = graphene.String(required=True)
#         password = graphene.String(required=True)
#         username = graphene.String(required=True)

#     @classmethod
#     def perform_mutation(cls, root, info, email, password, username):
#         # Validate input
#         error_details = []
#         if len(password) < 8:
#             error_details.append("Password must be at least 8 characters long")
#         if len(username.strip()) < 3:
#             error_details.append("Username must be at least 3 characters long")
#         if '@' not in email:
#             error_details.append("Invalid email format")

#         if error_details:
#             return lemmo_message(
#                 success=False,
#                 message="Validation failed",
#                 error_details=error_details
#             )

#         # Create user (pseudo-code)
#         try:
#             # Check if user already exists
#             # if User.objects.filter(username=username).exists():
#             #     return lemmo_message(
#             #         success=False,
#             #         message="User already exists",
#             #         error_details=["Username is already taken"]
#             #     )

#             # user = User.objects.create_user(
#             #     username=username,
#             #     email=email,
#             #     password=password
#             # )

#             # Mock user data
#             user_data = {
#                 "id": 456,
#                 "username": username,
#                 "email": email,
#                 "created_at": "2025-07-24T10:00:00Z"
#             }

#             return lemmo_message(
#                 success=True,
#                 message="User registered successfully",
#                 data={"user": user_data}
#             )

#         except Exception as e:
#             return lemmo_message(
#                 success=False,
#                 message="Registration failed",
#                 error_details=[f"Database error: {str(e)}"]
#             )


# # Schema registration example
# class Mutation(graphene.ObjectType):
#     create_post = CreatePostMutation.Field()
#     register_user = RegisterUserMutation.Field()
