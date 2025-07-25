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

        # Create a combined query class with all app queries
        query_fields = {}

        # Add a simple hello query for testing
        def resolve_hello(self, info):
            return "Hello from Lemmo Core!"

        query_fields["hello"] = graphene.String(
            default_value="Hi there", resolver=resolve_hello
        )

        # Add all app queries with proper field validation
        for query_class in queries:
            try:
                if hasattr(query_class, "_meta") and hasattr(
                    query_class._meta, "fields"
                ):
                    for field_name, field in query_class._meta.fields.items():
                        # Validate that the field is a proper GraphQL field
                        if hasattr(field, "type") or hasattr(field, "_type"):
                            if field_name not in query_fields:
                                query_fields[field_name] = field
                                logger.debug(f"Added query field: {field_name}")
                        else:
                            logger.warning(
                                f"Skipping invalid field {field_name} from {query_class.__name__}"
                            )
                else:
                    logger.warning(
                        f"Query class {query_class.__name__} has no _meta.fields"
                    )
            except Exception as e:
                logger.error(
                    f"Error processing query class {query_class.__name__}: {e}"
                )
                continue

        # Create the combined Query class
        if query_fields:
            Query = type("Query", (graphene.ObjectType,), query_fields)
        else:
            # Fallback to just the hello query
            class Query(graphene.ObjectType):
                hello = graphene.String(default_value="Hi there")

                def resolve_hello(self, info):
                    return "Hello from Lemmo Core!"

        # Create a combined mutation class with all app mutations
        mutation_fields = {}

        # Add all app mutations with proper field validation
        for mutation_class in mutations:
            try:
                if hasattr(mutation_class, "_meta") and hasattr(
                    mutation_class._meta, "fields"
                ):
                    for field_name, field in mutation_class._meta.fields.items():
                        # Validate that the field is a proper GraphQL field
                        if hasattr(field, "type") or hasattr(field, "_type"):
                            if field_name not in mutation_fields:
                                mutation_fields[field_name] = field
                                logger.debug(f"Added mutation field: {field_name}")
                        else:
                            logger.warning(
                                f"Skipping invalid mutation field {field_name} from {mutation_class.__name__}"
                            )
                else:
                    logger.warning(
                        f"Mutation class {mutation_class.__name__} has no _meta.fields"
                    )
            except Exception as e:
                logger.error(
                    f"Error processing mutation class {mutation_class.__name__}: {e}"
                )
                continue

        # Create the combined Mutation class
        if mutation_fields:
            Mutation = type("Mutation", (graphene.ObjectType,), mutation_fields)
        else:
            # Fallback to empty mutation
            class Mutation(graphene.ObjectType):
                pass

        # Create the schema
        schema = graphene.Schema(query=Query, mutation=Mutation)

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
