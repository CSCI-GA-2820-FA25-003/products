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
from urllib.parse import quote_plus

from tests.factories import ProductsFactory
from wsgi import app
from service.common import status
from service.models import db, Products

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)

BASE_URL = "/api/products"
BASE_URL_API = "/api/products"


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
        db.drop_all()
        db.create_all()

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

    ######################################################################
    # HEALTH TEST
    ######################################################################
    def test_health(self):
        """It should check the health endpoint"""
        resp = self.client.get("/api/health")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertIn("status", data)
        self.assertEqual(data["status"], "OK")

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

    def test_get_product_list_with_pagination(self):
        """It should Get a paginated list of products and all pages together should include all products"""
        self._create_products(5)
        all_names = set()

        page = 1
        limit = 2
        total_received = 0

        while True:
            response = self.client.get(f"{BASE_URL}?page={page}&limit={limit}")
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            data = response.get_json()
            if not data:
                break

            names = [p["name"] for p in data]
            self.assertEqual(names, sorted(names, key=lambda n: n.lower()))
            overlap = all_names.intersection(names)
            self.assertEqual(len(overlap), 0, f"Pagination overlap detected: {overlap}")

            all_names.update(names)
            total_received += len(data)
            page += 1

        self.assertEqual(
            total_received, 5, f"Expected 5 products total, got {total_received}"
        )
        self.assertEqual(
            len(all_names), 5, "Combined names should be all unique products"
        )

    def test_get_product_list_with_invalid_pagination(self):
        """It should handle invalid pagination parameters gracefully"""
        self._create_products(5)

        response = self.client.get(f"{BASE_URL}?page=abc&limit=0")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.get_json()
        self.assertTrue(len(data) >= 1)
        self.assertIsInstance(data, list)

        names = [p["name"] for p in data]
        self.assertEqual(names, sorted(names, key=lambda n: n.lower()))

    def test_get_product_list_with_zero_pagination(self):
        """It should default to page=1 and limit=20 when page=0 and limit=0"""
        self._create_products(5)

        response = self.client.get(f"{BASE_URL}?page=0&limit=0")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.get_json()
        self.assertEqual(len(data), 5)
        self.assertIsInstance(data, list)

        names = [p["name"] for p in data]
        self.assertEqual(names, sorted(names, key=lambda n: n.lower()))

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
        self.assertFalse(new_product["discontinued"])
        self.assertFalse(new_product["favorited"])

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
        self.assertFalse(new_product["discontinued"])
        self.assertFalse(new_product["favorited"])

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
            "availability": False,
        }

        response = self.client.put(
            f"{BASE_URL}/{test_product.id}",
            json=update_data,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_product = response.get_json()
        self.assertEqual(updated_product["name"], "Updated Product Name")
        self.assertEqual(updated_product["description"], "Updated Description")
        self.assertEqual(updated_product["price"], "199.99")
        self.assertEqual(updated_product["image_url"], "http://updated.com/image.jpg")
        self.assertEqual(updated_product["category"], "Updated Category")
        self.assertEqual(updated_product["availability"], False)
        self.assertFalse(updated_product["discontinued"])

    def test_update_discontinued_product(self):
        """It should return 404 when updating a discontinued product"""
        test_product = self._create_products(1)[0]
        product_id = test_product.id

        # discontinue the product first
        resp = self.client.post(
            f"{BASE_URL}/{product_id}/discontinue", query_string={"confirm": "true"}
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        response = self.client.put(
            f"{BASE_URL}/{product_id}",
            json={"name": "Still Hidden"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        self.assertIn("was not found", data["message"])

    def test_update_product_not_found(self):
        """It should return 404 when updating non-existent product"""
        response = self.client.put(
            f"{BASE_URL}/99999",
            json={"name": "Does Not Matter"},
            content_type="application/json",
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
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_product_bad_request_invalid_type(self):
        """It should return 400 for invalid data types"""
        test_product = self._create_products(1)[0]

        # Send invalid availability type
        response = self.client.put(
            f"{BASE_URL}/{test_product.id}",
            json={"availability": "not_a_boolean"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_product_wrong_content_type(self):
        """It should return 415 for wrong content type"""
        test_product = self._create_products(1)[0]

        response = self.client.put(
            f"{BASE_URL}/{test_product.id}", data="not json", content_type="text/plain"
        )

        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        data = response.get_json()
        self.assertIn("Content-Type must be application/json", data["message"])

    def test_update_product_no_content_type(self):
        """It should return 415 when content type is missing"""
        test_product = self._create_products(1)[0]

        response = self.client.put(
            f"{BASE_URL}/{test_product.id}", data='{"name": "Test"}'
        )

        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    # ----------------------------------------------------------
    # TEST FAVORITE / UNFAVORITE
    # ----------------------------------------------------------
    def test_favorite_product_success(self):
        """It should favorite a product successfully"""
        product = self._create_products(1)[0]

        resp = self.client.put(f"{BASE_URL}/{product.id}/favorite")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertIn("favorited", data)
        self.assertTrue(data["favorited"])

    def test_unfavorite_product_success(self):
        """It should unfavorite a product successfully"""
        product = self._create_products(1)[0]

        # First favorite it
        r1 = self.client.put(f"{BASE_URL}/{product.id}/favorite")
        self.assertEqual(r1.status_code, status.HTTP_200_OK)

        # Then unfavorite it
        r2 = self.client.put(f"{BASE_URL}/{product.id}/unfavorite")
        self.assertEqual(r2.status_code, status.HTTP_200_OK)
        data = r2.get_json()
        self.assertIn("favorited", data)
        self.assertFalse(data["favorited"])

    def test_favorite_product_not_found(self):
        """It should return 404 when trying to favorite a product that does not exist"""
        resp = self.client.put(f"{BASE_URL}/999999/favorite")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_unfavorite_product_not_found(self):
        """It should return 404 when trying to unfavorite a product that does not exist"""
        resp = self.client.put(f"{BASE_URL}/999999/unfavorite")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_idempotent_favorite(self):
        """Favoriting an already favorited product should be idempotent"""
        product = self._create_products(1)[0]

        # First favorite
        r1 = self.client.put(f"{BASE_URL}/{product.id}/favorite")
        self.assertEqual(r1.status_code, status.HTTP_200_OK)
        d1 = r1.get_json()

        # Second favorite (should not double count)
        r2 = self.client.put(f"{BASE_URL}/{product.id}/favorite")
        self.assertEqual(r2.status_code, status.HTTP_200_OK)
        d2 = r2.get_json()

        self.assertTrue(d1.get("favorited", False))
        self.assertTrue(d2.get("favorited", False))

        # If your API returns favorites_count, ensure it didn't increment twice
        if "favorites_count" in d1 or "favorites_count" in d2:
            self.assertEqual(d1.get("favorites_count"), d2.get("favorites_count"))

    def test_favorites_count_optional(self):
        """If implemented, favorites_count should increase with unique users"""
        product = self._create_products(1)[0]

        # Use simple headers if your service supports per-user favorites
        h1 = {"X-User-Id": "user-1"}
        h2 = {"X-User-Id": "user-2"}

        r1 = self.client.put(f"{BASE_URL}/{product.id}/favorite", headers=h1)
        self.assertEqual(r1.status_code, status.HTTP_200_OK)

        r2 = self.client.put(f"{BASE_URL}/{product.id}/favorite", headers=h2)
        self.assertEqual(r2.status_code, status.HTTP_200_OK)

        # Read back the product
        rget = self.client.get(f"{BASE_URL}/{product.id}")
        self.assertEqual(rget.status_code, status.HTTP_200_OK)
        pdata = rget.get_json()

        # Only assert if present (story marks this as optional)
        if "favorites_count" in pdata:
            self.assertGreaterEqual(pdata["favorites_count"], 2)

    # ----------------------------------------------------------
    # TEST METHOD NOT ALLOWED (405) COVERAGE
    # ----------------------------------------------------------
    def test_method_not_allowed_on_collection_put(self):
        """It should return 405 when PUT /products (collection PUT not allowed)"""
        resp = self.client.put(BASE_URL, json={})
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        data = resp.get_json()
        self.assertIsInstance(data, dict)
        self.assertIn("status", data)
        self.assertIn("error", data)

    def test_method_not_allowed_on_item_post(self):
        """It should return 405 when POST /products/<id> (item POST not allowed)"""
        product = self._create_products(1)[0]
        resp = self.client.post(f"{BASE_URL}/{product.id}", json={})
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        data = resp.get_json()
        self.assertIsInstance(data, dict)
        self.assertIn("status", data)
        self.assertIn("error", data)

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

    def test_query_by_category_case_insensitive(self):
        """It should Query products by category with case-insensitive search"""
        # Create specific products with categories for case testing
        test_products = [
            ProductsFactory(
                name="iPhone 15",
                category="Electronics",
                price=999.99,
                availability=True,
            ),
            ProductsFactory(
                name="Samsung Galaxy",
                category="Electronics",
                price=899.99,
                availability=True,
            ),
            ProductsFactory(
                name="MacBook Pro",
                category="Computers",
                price=1999.99,
                availability=True,
            ),
        ]

        created_products = []
        for product in test_products:
            response = self.client.post(BASE_URL, json=product.serialize())
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            created_products.append(response.get_json())

        # Search with different case
        response = self.client.get(BASE_URL, query_string="category=electronics")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 2)  # Should find both Electronics products
        for product in data:
            self.assertEqual(product["category"], "Electronics")

    def test_query_by_name_partial_and_case_insensitive(self):
        """It should Query products by partial name with case-insensitive search"""
        # Create specific products with names for testing
        test_products = [
            ProductsFactory(
                name="iPhone 15",
                category="Electronics",
                price=999.99,
                availability=True,
            ),
            ProductsFactory(
                name="iPhone 15 Pro",
                category="Electronics",
                price=1199.99,
                availability=True,
            ),
            ProductsFactory(
                name="Samsung Galaxy",
                category="Electronics",
                price=899.99,
                availability=True,
            ),
        ]

        created_products = []
        for product in test_products:
            response = self.client.post(BASE_URL, json=product.serialize())
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            created_products.append(response.get_json())

        # Search with partial match and different case
        response = self.client.get(BASE_URL, query_string="name=iphone")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 2)  # Should find iPhone 15 and iPhone 15 Pro
        # Verify all returned products contain "iPhone" in their name
        for product in data:
            self.assertIn("iPhone", product["name"])

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
        """It should delete an existing product and return 204"""
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
        """It should return 204 even if product does not exist"""
        # 99999 is an arbitrary non-existent id
        resp = self.client.delete(f"{BASE_URL}/99999")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_invalid_id_format(self):
        """It should return 404 not found when product ID format is invalid"""
        resp = self.client.delete(f"{BASE_URL}/abc")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_discontinue_requires_confirmation(self):
        """It should reject discontinue without confirmation"""
        test_product = self._create_products(1)[0]
        product_id = test_product.id

        resp = self.client.post(f"{BASE_URL}/{product_id}/discontinue")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        data = resp.get_json()
        self.assertIn("requires confirmation", data["message"])

    def test_discontinue_product(self):
        """It should discontinue a product and hide it from APIs"""
        test_product = self._create_products(1)[0]
        product_id = test_product.id

        resp = self.client.post(
            f"{BASE_URL}/{product_id}/discontinue", query_string={"confirm": "true"}
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertTrue(data["discontinued"])
        self.assertFalse(data["availability"])

        resp = self.client.get(f"{BASE_URL}/{product_id}")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        resp = self.client.get(BASE_URL)
        all_products = resp.get_json()
        self.assertTrue(all(product["id"] != product_id for product in all_products))

        resp = self.client.get(
            BASE_URL, query_string=f"name={quote_plus(test_product.name)}"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.get_json()), 0)

    def test_discontinue_nonexistent_product(self):
        """It should return 404 when discontinuing a missing product"""
        resp = self.client.post(
            f"{BASE_URL}/99999/discontinue", query_string={"confirm": "true"}
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_discontinue_accepts_json_confirmation(self):
        """It should accept multiple confirmation payload formats"""
        products = self._create_products(3)

        payloads = [
            {"confirm": True},
            {"confirm": "YES"},
            {"confirm": 1},
        ]

        for product, payload in zip(products, payloads):
            resp = self.client.post(
                f"{BASE_URL}/{product.id}/discontinue",
                json=payload,
                content_type="application/json",
            )
            self.assertEqual(resp.status_code, status.HTTP_200_OK)
            self.assertTrue(resp.get_json()["discontinued"])

    def test_discontinue_already_discontinued(self):
        """It should return 404 when discontinuing an already discontinued product"""
        test_product = self._create_products(1)[0]
        product_id = test_product.id

        resp = self.client.post(
            f"{BASE_URL}/{product_id}/discontinue", query_string={"confirm": "true"}
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        resp = self.client.post(
            f"{BASE_URL}/{product_id}/discontinue", query_string={"confirm": "true"}
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
