from .app_manager import AppManager
from .gql.queries.core import CoreAuthenticatedQuery
import graphene
import logging

logger = logging.getLogger(__name__)


class BaseQuery(CoreAuthenticatedQuery):
    """
    Base query class that combines all app queries.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add any base query fields here


class BaseMutation(graphene.ObjectType):
    """
    Base mutation class that combines all app mutations.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add any base mutation fields here


def create_schema() -> graphene.Schema:
    """
    Create and return the GraphQL schema with all app queries and mutations.

    Returns:
        GraphQL schema object
    """
    try:
        # Get queries and mutations from all apps
        queries, mutations = AppManager.get_app_schema()

        # Create base query class with all app queries
        if queries:
            query_classes = [BaseQuery] + queries
            Query = type("Query", tuple(query_classes), {})
        else:
            Query = BaseQuery

        # Add a simple hello query for testing
        class HelloQuery(BaseQuery):
            hello = graphene.String(default_value="Hi there")

            def resolve_hello(self, info):
                return "Hello from Lemmo Core!"

        # Create base mutation class with all app mutations
        if mutations:
            mutation_classes = [BaseMutation] + mutations
            Mutation = type("Mutation", tuple(mutation_classes), {})
        else:
            Mutation = BaseMutation

        # Create the schema
        schema = graphene.Schema(query=HelloQuery, mutation=Mutation)

        logger.info(
            f"Created GraphQL schema with {len(queries)} queries and {len(mutations)} mutations"
        )
        return schema

    except Exception as e:
        logger.error(f"Error creating GraphQL schema: {e}")

        # Return a minimal schema in case of error
        class ErrorQuery(graphene.ObjectType):
            hello = graphene.String(default_value="Schema Error")

            def resolve_hello(self, info):
                return "Schema creation failed"

        class ErrorMutation(graphene.ObjectType):
            pass

        return graphene.Schema(query=ErrorQuery, mutation=ErrorMutation)


# Create the default schema
schema = create_schema()


def get_schema_info() -> dict:
    """
    Get information about the current GraphQL schema.

    Returns:
        Dictionary with schema information
    """
    try:
        queries, mutations = AppManager.get_app_schema()
        return {
            "query_count": len(queries),
            "mutation_count": len(mutations),
            "apps_loaded": len(AppManager.get_apps()),
            "schema_valid": True,
        }
    except Exception as e:
        logger.error(f"Error getting schema info: {e}")
        return {
            "query_count": 0,
            "mutation_count": 0,
            "apps_loaded": 0,
            "schema_valid": False,
            "error": str(e),
        }


def reload_schema() -> graphene.Schema:
    """
    Reload the GraphQL schema by re-importing all app modules.

    Returns:
        Updated GraphQL schema object
    """
    global schema
    try:
        schema = create_schema()
        logger.info("GraphQL schema reloaded successfully")
        return schema
    except Exception as e:
        logger.error(f"Error reloading GraphQL schema: {e}")
        return schema
