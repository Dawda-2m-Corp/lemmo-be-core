from .app_manager import AppManager
import graphene

queries, mutations = AppManager.get_app_schema()


class Query(*queries, graphene.ObjectType):
    hello = graphene.String(default_value="Hi there")


class Mutation(*mutations, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
