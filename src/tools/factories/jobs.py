from datetime import datetime

import factory
import factory.fuzzy

from storage.sqlalchemy.tables import Job


class JobFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Job

    id = factory.Sequence(lambda n: n + 1)
    title = factory.Faker("pystr", max_chars=50)
    description = factory.Faker("pystr", max_chars=50)
    salary_from = factory.Faker(
        "pydecimal", left_digits=5, right_digits=2, min_value=1, max_value=10000
    )
    salary_to = factory.Faker(
        "pydecimal", left_digits=5, right_digits=2, min_value=10000, max_value=100000
    )
    is_active = factory.Faker("pybool")
    created_at = factory.LazyFunction(datetime.utcnow)
