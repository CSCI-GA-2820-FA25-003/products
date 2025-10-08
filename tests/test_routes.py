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
from tests.factories import ProductsFactory
from wsgi import app
from service.common import status
from service.models import db, Products

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

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    # Todo: Add your test cases here...

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
            
            # Todo: Uncomment code below when get_products is implemented 

            # Check that the location header was correct
            # response = self.client.get(location)
            # self.assertEqual(response.status_code, status.HTTP_200_OK)
            # new_product = response.get_json()
            # self.assertEqual(new_product["name"], test_product.name)
            # self.assertEqual(new_product["description"], test_product.description)
            # self.assertEqual(new_product["price"], test_product.price)
            # self.assertEqual(new_product["image_url"], test_product.image_url)
            # self.assertEqual(new_product["category"], test_product.category)
            # self.assertEqual(new_product["availability"], test_product.availability)