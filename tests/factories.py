"""
Test Factory to make fake objects for testing
"""

import factory
from service.models import Products


class ProductsFactory(factory.Factory):
    """Creates fake pets that you don't have to feed"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Products

    id = factory.Sequence(lambda n: n)
    name = factory.Faker("name")
    description = factory.Faker("text")
    price = factory.Faker("pydecimal", left_digits=4, right_digits=2, positive=True)
    image_url = factory.Faker("image_url")
    category = factory.Faker("word")
    availability = factory.Faker("boolean")
    discontinued = False

    # NOTE: Add other attributes here if/when needed for tests.
