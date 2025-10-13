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
TestProducts API Service Test Suite
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from unittest.mock import patch
from tests.factories import ProductsFactory
from wsgi import app
from service.common import status
from service.models import db, Products, DataValidationError
from urllib.parse import quote_plus

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)

BASE_URL = "/products"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestYourResourceService(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Products).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ############################################################
    # Utility function to bulk create products
    ############################################################
    def _create_products(self, count: int = 1) -> list:
        """Factory method to create products in bulk"""
        products = []
        for _ in range(count):
            test_product = ProductsFactory()
            response = self.client.post(BASE_URL, json=test_product.serialize())
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test product",
            )
            new_product = response.get_json()
            test_product.id = new_product["id"]
            products.append(test_product)
        return products

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    # ----------------------------------------------------------
    # TEST LIST
    # ----------------------------------------------------------
    def test_get_product_list(self):
        """It should Get a list of products"""
        self._create_products(5)
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)

    # ----------------------------------------------------------
    # TEST READ
    # ----------------------------------------------------------
    def test_get_product(self):
        """It should Get a single product"""
        # get the id of a product
        test_product = self._create_products(1)[0]
        response = self.client.get(f"{BASE_URL}/{test_product.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["name"], test_product.name)

    def test_get_product_not_found(self):
        """It should not Get a product thats not found"""
        response = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("was not found", data["message"])

    # ----------------------------------------------------------
    # TEST CREATE
    # ----------------------------------------------------------
    def test_create_product(self):
        """It should Create a new Product"""
        test_product = ProductsFactory()
        logging.debug("Test Product: %s", test_product.serialize())
        response = self.client.post(BASE_URL, json=test_product.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_product = response.get_json()
        self.assertEqual(new_product["name"], test_product.name)
        self.assertEqual(new_product["description"], test_product.description)
        self.assertEqual(new_product["price"], str(test_product.price))
        self.assertEqual(new_product["image_url"], test_product.image_url)
        self.assertEqual(new_product["category"], test_product.category)
        self.assertEqual(new_product["availability"], test_product.availability)

        # Check that the location header was correct
        response = self.client.get(location)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_product = response.get_json()
        self.assertEqual(new_product["name"], test_product.name)
        self.assertEqual(new_product["description"], test_product.description)
        self.assertEqual(new_product["price"], str(test_product.price))
        self.assertEqual(new_product["image_url"], test_product.image_url)
        self.assertEqual(new_product["category"], test_product.category)
        self.assertEqual(new_product["availability"], test_product.availability)

    # ----------------------------------------------------------
    # TEST UPDATE
    # ----------------------------------------------------------
    def test_update_product(self):
        """It should Update an existing product"""
        # Create a product using the utility method
        test_product = self._create_products(1)[0]

        # Update the product with all fields
        update_data = {
            "name": "Updated Product Name",
            "description": "Updated Description",
            "price": "199.99",
            "image_url": "http://updated.com/image.jpg",
            "category": "Updated Category",
            "availability": False
        }

        response = self.client.put(
            f"{BASE_URL}/{test_product.id}",
            json=update_data,
            content_type="application/json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_product = response.get_json()
        self.assertEqual(updated_product["name"], "Updated Product Name")
        self.assertEqual(updated_product["description"], "Updated Description")
        self.assertEqual(updated_product["price"], "199.99")
        self.assertEqual(updated_product["image_url"], "http://updated.com/image.jpg")
        self.assertEqual(updated_product["category"], "Updated Category")
        self.assertEqual(updated_product["availability"], False)

    def test_update_product_partial(self):
        """It should partially update a product (only provided fields)"""
        # Create a product
        test_product = self._create_products(1)[0]
        original_name = test_product.name
        original_description = test_product.description

        # Only update price and availability
        response = self.client.put(
            f"{BASE_URL}/{test_product.id}",
            json={"price": "299.99", "availability": False},
            content_type="application/json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_product = response.get_json()
        self.assertEqual(updated_product["price"], "299.99")
        self.assertEqual(updated_product["availability"], False)
        # These should remain unchanged
        self.assertEqual(updated_product["name"], original_name)
        self.assertEqual(updated_product["description"], original_description)

    def test_update_product_not_found(self):
        """It should return 404 when updating non-existent product"""
        response = self.client.put(
            f"{BASE_URL}/99999",
            json={"name": "Does Not Matter"},
            content_type="application/json"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        self.assertIn("was not found", data["message"])

    def test_update_product_bad_request_invalid_price(self):
        """It should return 400 for invalid price data"""
        test_product = self._create_products(1)[0]

        # Send invalid price
        response = self.client.put(
            f"{BASE_URL}/{test_product.id}",
            json={"price": "not_a_number"},
            content_type="application/json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_product_bad_request_invalid_type(self):
        """It should return 400 for invalid data types"""
        test_product = self._create_products(1)[0]

        # Send invalid availability type
        response = self.client.put(
            f"{BASE_URL}/{test_product.id}",
            json={"availability": "not_a_boolean"},
            content_type="application/json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_product_wrong_content_type(self):
        """It should return 415 for wrong content type"""
        test_product = self._create_products(1)[0]

        response = self.client.put(
            f"{BASE_URL}/{test_product.id}",
            data="not json",
            content_type="text/plain"
        )

        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        data = response.get_json()
        self.assertIn("Content-Type must be application/json", data["message"])

    def test_update_product_no_content_type(self):
        """It should return 415 when content type is missing"""
        test_product = self._create_products(1)[0]

        response = self.client.put(
            f"{BASE_URL}/{test_product.id}",
            data='{"name": "Test"}'
        )

        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_update_product_empty_json(self):
        """It should handle empty JSON body (no fields to update)"""
        test_product = self._create_products(1)[0]
        original_name = test_product.name

        # Send empty JSON - should succeed with no changes
        response = self.client.put(
            f"{BASE_URL}/{test_product.id}",
            json={},
            content_type="application/json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_product = response.get_json()
        # Nothing should change
        self.assertEqual(updated_product["name"], original_name)

    def test_update_product_decimal_price_validation(self):
        """It should properly handle decimal price formats"""
        test_product = self._create_products(1)[0]

        # Test various decimal formats
        test_prices = ["0.01", "999.99", "1234.56"]

        for price in test_prices:
            response = self.client.put(
                f"{BASE_URL}/{test_product.id}",
                json={"price": price},
                content_type="application/json"
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            updated_product = response.get_json()
            self.assertEqual(updated_product["price"], price)

    def test_update_product_response_includes_all_fields(self):
        """It should return all product fields in JSON response"""
        test_product = self._create_products(1)[0]

        response = self.client.put(
            f"{BASE_URL}/{test_product.id}",
            json={"name": "Updated"},
            content_type="application/json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_product = response.get_json()

        # Check all fields are present in response
        self.assertIn("id", updated_product)
        self.assertIn("name", updated_product)
        self.assertIn("description", updated_product)
        self.assertIn("price", updated_product)
        self.assertIn("image_url", updated_product)
        self.assertIn("category", updated_product)
        self.assertIn("availability", updated_product)
        self.assertIn("created_date", updated_product)
        self.assertIn("updated_date", updated_product)

    def test_update_product_database_error(self):
        """It should handle database errors during update"""
        test_product = self._create_products(1)[0]

        # Mock the update method to raise a DataValidationError
        with patch.object(Products, 'update') as mock_update:
            mock_update.side_effect = DataValidationError("Database error")

            response = self.client.put(
                f"{BASE_URL}/{test_product.id}",
                json={"name": "This will fail"},
                content_type="application/json"
            )

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            data = response.get_json()
            self.assertIn("Database error", data["message"])

    # ----------------------------------------------------------
    # TEST QUERY
    # ----------------------------------------------------------
    def test_query_by_name(self):
        """It should Query products by name"""
        products = self._create_products(5)
        test_name = products[0].name
        name_count = len([product for product in products if product.name == test_name])
        response = self.client.get(
            BASE_URL, query_string=f"name={quote_plus(test_name)}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), name_count)
        # check the data just to be sure
        for product in data:
            self.assertEqual(product["name"], test_name)

    def test_query_product_list_by_category(self):
        """It should Query products by Category"""
        products = self._create_products(10)
        test_category = products[0].category
        category_products = [
            product for product in products if product.category == test_category
        ]
        response = self.client.get(
            BASE_URL, query_string=f"category={quote_plus(test_category)}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), len(category_products))
        # check the data just to be sure
        for product in data:
            self.assertEqual(product["category"], test_category)

    def test_query_by_availability(self):
        """It should Query products by availability"""
        products = self._create_products(10)
        available_products = [
            product for product in products if product.availability is True
        ]
        unavailable_products = [
            product for product in products if product.availability is False
        ]
        available_count = len(available_products)
        unavailable_count = len(unavailable_products)
        logging.debug("Available products [%d] %s", available_count, available_products)
        logging.debug(
            "Unavailable products [%d] %s", unavailable_count, unavailable_products
        )

        # test for available
        response = self.client.get(BASE_URL, query_string="availability=true")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), available_count)
        # check the data just to be sure
        for product in data:
            self.assertEqual(product["availability"], True)

        # test for unavailable
        response = self.client.get(BASE_URL, query_string="availability=false")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), unavailable_count)
        # check the data just to be sure
        for product in data:
            self.assertEqual(product["availability"], False)

    
    # ----------------------------------------------------------
    # TEST DELETE
    # ----------------------------------------------------------

    def test_delete_existing_product(self):
        """Should delete an existing product and return 204"""
        # Create a product using factory
        test_product = self._create_products(1)[0]
        product_id = test_product.id

        # Verify it exists
        resp = self.client.get(f"{BASE_URL}/{product_id}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # Delete the product
        resp = self.client.delete(f"{BASE_URL}/{product_id}")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        # Confirm it is gone
        resp = self.client.get(f"{BASE_URL}/{product_id}")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


    def test_delete_nonexistent_product(self):
        """Should return 204 even if product does not exist (idempotent behavior)"""
        # 99999 is an arbitrary non-existent id
        resp = self.client.delete(f"{BASE_URL}/99999")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)


    def test_delete_invalid_id_format(self):
        """Should return 404 not found when product ID format is invalid"""
        resp = self.client.delete(f"{BASE_URL}/abc")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
