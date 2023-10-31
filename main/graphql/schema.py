import strawberry
from asgiref.sync import sync_to_async
from dataclasses import dataclass
from strawberry.django.views import AsyncGraphQLView

from main.enums import AppEnumCollection, AppEnumCollectionData
from apps.common.enums import GlobalPermissionTypeEnum
from apps.user.models import User

from apps.user import queries as user_queries, mutations as user_mutations

from .permissions import IsAuthenticated


@dataclass
class UserContext:
    user: User
    permissions: set[User.Permission]


class CustomAsyncGraphQLView(AsyncGraphQLView):
    @staticmethod
    @sync_to_async
    def get_global_permissions(user: User) -> set[GlobalPermissionTypeEnum]:
        if not user.is_anonymous:
            return user.get_global_permissions()
        return set()


@strawberry.type
class PublicQuery(
    user_queries.PublicQuery,
):
    id: strawberry.ID = strawberry.ID('public')


@strawberry.type
class PrivateQuery(
    user_queries.PrivateQuery,
):
    id: strawberry.ID = strawberry.ID('private')


@strawberry.type
class PublicMutation(
    user_mutations.PublicMutation,
):
    id: strawberry.ID = strawberry.ID('public')


@strawberry.type
class PrivateMutation(
    user_mutations.PrivateMutation,
):
    id: strawberry.ID = strawberry.ID('private')


@strawberry.type
class Query:
    public: PublicQuery = strawberry.field(
        resolver=lambda: PublicQuery()
    )
    private: PrivateQuery = strawberry.field(
        permission_classes=[IsAuthenticated],
        resolver=lambda: PrivateQuery()
    )
    enums: AppEnumCollection = strawberry.field(
        resolver=lambda: AppEnumCollectionData()
    )


@strawberry.type
class Mutation:
    public: PublicMutation = strawberry.field(resolver=lambda: PublicMutation())
    private: PrivateMutation = strawberry.field(
        resolver=lambda: PrivateMutation(),
        permission_classes=[IsAuthenticated],
    )


schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
)
