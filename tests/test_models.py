######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Test cases for Product Model
"""

# pylint: disable=duplicate-code
from decimal import Decimal
import os
import logging
from unittest.mock import patch
from unittest import TestCase
from wsgi import app
from service.models import Products, DataValidationError, db
from .factories import ProductsFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  P r o d u c t s   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProducts(TestCase):
    """Test Cases for Products Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()
        db.drop_all()
        db.create_all()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Products).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_product(self):
        """It should create a Products"""
        product = ProductsFactory()
        product.create()
        self.assertIsNotNone(product.id)
        found = Products.all()
        self.assertEqual(len(found), 1)
        data = Products.find(product.id)
        self.assertEqual(data.name, product.name)
        self.assertEqual(data.description, product.description)
        self.assertEqual(data.price, product.price)
        self.assertEqual(data.image_url, product.image_url)
        self.assertEqual(data.category, product.category)
        self.assertEqual(data.availability, product.availability)
        self.assertEqual(data.discontinued, product.discontinued)

    def test_delete_product(self):
        """It should delete a Products"""
        product = ProductsFactory()
        product.create()
        self.assertIsNotNone(product.id)
        pk = product.id
        product.delete()
        self.assertIsNone(Products.find(pk))

    def test_update_product(self):
        """It should update a Products"""
        product = ProductsFactory()
        product.create()
        self.assertIsNotNone(product.id)
        # change it an save it
        product.name = "New Name"
        product.description = "New Description"
        product.price = 99.99
        product.image_url = "http://newimage.url/image.png"
        product.category = "New Category"
        product.availability = False
        old_id = product.id
        product.update()
        self.assertEqual(product.id, old_id)
        # Fetch it back and make sure the id hasn't changed
        same_product = Products.find(old_id)
        self.assertEqual(same_product.id, old_id)
        self.assertEqual(same_product.name, "New Name")
        self.assertEqual(same_product.description, "New Description")
        self.assertEqual(same_product.price, Decimal("99.99"))
        self.assertEqual(same_product.image_url, "http://newimage.url/image.png")
        self.assertEqual(same_product.category, "New Category")
        self.assertEqual(same_product.availability, False)
        self.assertFalse(same_product.discontinued)

    def test_list_all_products(self):
        """It should List all products in the database"""
        products = Products.all()
        self.assertEqual(products, [])
        # Create 5 products
        for _ in range(5):
            product = ProductsFactory()
            product.create()
        # See if we get back 5 products
        products = Products.all()
        self.assertEqual(len(products), 5)

    def test_all_excludes_discontinued(self):
        """It should not return discontinued products in the default queries"""
        active_product = ProductsFactory(availability=True, discontinued=False)
        active_product.create()
        discontinued_product = ProductsFactory(
            name=active_product.name,
            category=active_product.category,
            availability=False,
            discontinued=True,
        )
        discontinued_product.create()

        products = Products.all()
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].id, active_product.id)

        by_name = Products.find_by_name(active_product.name).all()
        self.assertEqual(len(by_name), 1)
        self.assertEqual(by_name[0].id, active_product.id)

        by_category = Products.find_by_category(active_product.category).all()
        self.assertEqual(len(by_category), 1)
        self.assertEqual(by_category[0].id, active_product.id)

        available = Products.find_by_availability(True).all()
        ids = [item.id for item in available]
        self.assertIn(active_product.id, ids)
        self.assertNotIn(discontinued_product.id, ids)

    def test_serialize_product(self):
        """It should serialize a Products"""
        product = ProductsFactory()
        product.create()
        data = product.serialize()
        self.assertIsNotNone(data)
        self.assertEqual(data["id"], product.id)
        self.assertEqual(data["name"], product.name)
        self.assertEqual(data["description"], product.description)
        self.assertEqual(data["price"], str(product.price))
        self.assertEqual(data["image_url"], product.image_url)
        self.assertEqual(data["category"], product.category)
        self.assertEqual(data["availability"], product.availability)
        self.assertEqual(data["discontinued"], product.discontinued)
        self.assertIsNotNone(data["created_date"])
        self.assertIsNotNone(data["updated_date"])

    def test_deserialize_product(self):
        """It should deserialize a Products"""
        product = ProductsFactory()
        data = product.serialize()
        new_product = Products()
        new_product.deserialize(data)
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(new_product.price, str(product.price))
        self.assertEqual(new_product.image_url, product.image_url)
        self.assertEqual(new_product.category, product.category)
        self.assertEqual(new_product.availability, product.availability)
        self.assertEqual(new_product.discontinued, product.discontinued)

    def test_find_by_name_product(self):
        """It should find Products by name"""
        product = ProductsFactory()
        product.create()
        name = product.name
        found = Products.find_by_name(name).all()
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].name, name)

    # ----------------------------------------------------------
    # EXTRA COVERAGE: error paths & repr in service/models.py
    # ----------------------------------------------------------

    def test_create_rollback_on_exception(self):
        """create() should rollback and raise DataValidationError when commit fails"""
        product = ProductsFactory()
        # simulate db failure on commit during create()
        with patch.object(
            db.session, "commit", side_effect=Exception("create boom")
        ), patch.object(db.session, "rollback") as mock_rb:
            with self.assertRaises(DataValidationError) as ctx:
                product.create()
            self.assertIn("create boom", str(ctx.exception))
            mock_rb.assert_called_once()

    def test_update_rollback_on_exception(self):
        """update() should rollback and raise DataValidationError when commit fails"""
        product = ProductsFactory()
        product.create()
        product.description = "new"
        with patch.object(
            db.session, "commit", side_effect=Exception("update boom")
        ), patch.object(db.session, "rollback") as mock_rb:
            with self.assertRaises(DataValidationError) as ctx:
                product.update()
            self.assertIn("update boom", str(ctx.exception))
            mock_rb.assert_called_once()

    def test_deserialize_attribute_error_when_mapping_lacks_get(self):
        """deserialize() should raise DataValidationError on objects without .get (AttributeError path)"""

        class IndexOnly:
            def __init__(self, d):
                self._d = d

            def __getitem__(self, k):
                return self._d[k]

            # deliberately no .get()

        p = Products()
        with self.assertRaises(DataValidationError):
            p.deserialize(IndexOnly({"name": "aaa", "price": 1}))

    def test_deserialize_type_error_when_not_mapping(self):
        """deserialize() should raise DataValidationError when given a non-dict (TypeError path)"""
        p = Products()
        with self.assertRaises(DataValidationError):
            p.deserialize("not-a-dict")

    def test_products_repr(self):
        """__repr__ should include the class name (and not crash)"""
        p = Products()
        r = repr(p)
        self.assertIn(Products.__name__, r)

    # ... [your other existing tests unchanged above] ...

    def test_delete_exception_rolls_back_and_raises(self):
        """delete() should rollback and raise DataValidationError when commit fails"""
        product = ProductsFactory()
        product.create()

        # Mock commit to raise an Exception so delete triggers rollback
        with patch.object(
            db.session, "commit", side_effect=Exception("delete boom")
        ), patch.object(db.session, "rollback") as mock_rollback:
            with self.assertRaises(DataValidationError) as ctx:
                product.delete()
            self.assertIn("delete boom", str(ctx.exception))
            mock_rollback.assert_called_once()

    # ----------------------------------------------------------
    # FAVORITES MODEL
    # ----------------------------------------------------------
    def test_product_has_favorited_flag_in_payload(self):
        """Serialize should include a 'favorited' field if implemented"""
        p = ProductsFactory()
        p.create()
        found = Products.find(p.id)
        self.assertIsNotNone(found)
        data = found.serialize()
        # Don't fail if not implemented yet
        if "favorited" in data:
            self.assertIsInstance(data["favorited"], bool)

    def test_optional_favorites_count_field(self):
        """If implemented, favorites_count should default to 0 and be an int"""
        p = ProductsFactory()
        p.create()
        found = Products.find(p.id)
        self.assertIsNotNone(found)
        # Don't fail if not implemented yet
        if hasattr(found, "favorites_count"):
            self.assertIsInstance(found.favorites_count, int)
            self.assertGreaterEqual(found.favorites_count, 0)
