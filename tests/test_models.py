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

    def test_find_by_name_partial_match(self):
        """It should find products with partial name match"""
        # Create products with specific names
        product1 = Products(name="iPhone 15", category="Electronics", price=999.99, availability=True)
        product1.create()
        product2 = Products(name="iPhone 15 Pro", category="Electronics", price=1199.99, availability=True)
        product2.create()
        product3 = Products(name="Samsung Galaxy", category="Electronics", price=899.99, availability=True)
        product3.create()

        # Test partial match
        found = Products.find_by_name("iPhone").all()
        self.assertEqual(len(found), 2)  # Should find iPhone 15 and iPhone 15 Pro

    def test_find_by_name_case_insensitive(self):
        """It should find products with case-insensitive name search"""
        # Create product with specific name
        product = Products(name="iPhone 15", category="Electronics", price=999.99, availability=True)
        product.create()

        # Test case sensitivity
        found_1 = Products.find_by_name("iphone 15").all()
        found_2 = Products.find_by_name("iphone").all()
        self.assertEqual(len(found_1), 1)  # Should find iPhone 15
        self.assertEqual(len(found_2), 1)  # Should find iPhone 15

    def test_find_by_category_case_insensitive(self):
        """It should find products with case-insensitive category search"""
        # Create product with specific category
        product = Products(name="iPhone 15", category="Electronics", price=999.99, availability=True)
        product.create()

        # Test case sensitivity
        found = Products.find_by_category("electronics").all()
        self.assertEqual(len(found), 1)  # Should find iPhone 15

    def test_find_by_name_partial_and_case_insensitive(self):
        """It should find products with partial name match AND case-insensitive search"""
        # Create products with specific names
        product1 = Products(name="iPhone 15", category="Electronics", price=999.99, availability=True)
        product1.create()
        product2 = Products(name="iPhone 15 Pro", category="Electronics", price=1199.99, availability=True)
        product2.create()
        product3 = Products(name="Samsung Galaxy", category="Electronics", price=899.99, availability=True)
        product3.create()

        # Test partial match with case insensitive
        found = Products.find_by_name("iphone").all()
        self.assertEqual(len(found), 2)  # Should find iPhone 15 and iPhone 15 Pro
        # Verify the results contain the expected products
        found_names = [product.name for product in found]
        self.assertIn("iPhone 15", found_names)
        self.assertIn("iPhone 15 Pro", found_names)

    def test_find_by_category_partial_match(self):
        """It should find products with partial category match"""
        # Create products with specific categories
        product1 = Products(name="MacBook Pro", category="Computers", price=1999.99, availability=True)
        product1.create()
        product2 = Products(name="Dell Laptop", category="Computers", price=1299.99, availability=True)
        product2.create()
        product3 = Products(name="iPhone 15", category="Electronics", price=999.99, availability=True)
        product3.create()

        # Test partial category match
        found = Products.find_by_category("comp").all()
        self.assertEqual(len(found), 2)  # Should find both Computers products

    def test_deserialize_missing_key_raises(self):
        """It should raise DataValidationError when key is missing"""
        p = Products()
        data = {
            # Intendionally leave out the 'name' key
            "description": "Nice widget",
            "price": 9.99,
            "image_url": "http://img",
            "category": "tools",
        }
        with self.assertRaises(DataValidationError) as ctx:
            p.deserialize(data)
        self.assertIn("missing name", str(ctx.exception))

    def test_deserialize_type_error_raises(self):
        """It should raise DataValidationError when data is not a dict"""
        p = Products()
        with self.assertRaises(DataValidationError) as ctx:
            p.deserialize(None)
        self.assertIn("bad or no data", str(ctx.exception))

    def test_deserialize_attribute_error_raises(self):
        """It should raise DataValidationError when object lacks .get()"""

        # pylint: disable=too-few-public-methods
        class IndexOnly:
            """Lightweight helper class that wraps a backing object and provides index access only."""
            def __init__(self, backing):
                self._b = backing

            def __getitem__(self, key):
                return self._b[key]

            # no get

        payload = {
            "name": "Widget",
            "description": "Nice widget",
            "price": 9.99,
            "image_url": "http://img",
            "category": "tools",
        }
        p = Products()
        with self.assertRaises(DataValidationError) as ctx:
            p.deserialize(IndexOnly(payload))
        self.assertIn("Invalid attribute", str(ctx.exception))

    def test_create_exception_rolls_back_and_raises(self):
        """create() should rollback and raise DataValidationError when commit fails"""
        product = ProductsFactory()
        # Mock commit to raise an Exception and ensure rollback is called
        with patch.object(
            db.session, "commit", side_effect=Exception("commit boom")
        ), patch.object(db.session, "rollback") as mock_rollback:
            with self.assertRaises(DataValidationError) as ctx:
                product.create()
            self.assertIn("commit boom", str(ctx.exception))
            mock_rollback.assert_called_once()

    def test_update_exception_rolls_back_and_raises(self):
        """update() should rollback and raise DataValidationError when commit fails"""
        product = ProductsFactory()
        product.create()

        product.description = "will fail to update"
        with patch.object(
            db.session, "commit", side_effect=Exception("update boom")
        ), patch.object(db.session, "rollback") as mock_rollback:
            with self.assertRaises(DataValidationError) as ctx:
                product.update()
            self.assertIn("update boom", str(ctx.exception))
            mock_rollback.assert_called_once()

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
