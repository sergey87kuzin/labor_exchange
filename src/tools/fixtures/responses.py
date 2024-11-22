import factory

from storage.sqlalchemy.tables import Response


class ResponseFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Response

    id = factory.Sequence(lambda n: n + 1)
    message = factory.Faker("pystr")
