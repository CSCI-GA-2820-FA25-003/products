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
Product Steps

Steps file for Products.feature

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import requests
from compare3 import expect
from behave import given  # pylint: disable=no-name-in-module

# HTTP Return Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204

WAIT_TIMEOUT = 60


def _to_bool(value: str) -> bool:
    """Convert common truthy strings to boolean"""
    return str(value).strip() in ["True", "true", "1", "yes", "on"]


@given("the following products")
def step_impl(context):
    """Delete all Products and load new ones"""

    # Get a list of all products
    rest_endpoint = f"{context.base_url}/products"
    context.resp = requests.get(rest_endpoint, timeout=WAIT_TIMEOUT)
    expect(context.resp.status_code).equal_to(HTTP_200_OK)

    # Delete them one by one
    for product in context.resp.json():
        context.resp = requests.delete(
            f"{rest_endpoint}/{product['id']}", timeout=WAIT_TIMEOUT
        )
        expect(context.resp.status_code).equal_to(HTTP_204_NO_CONTENT)

    # Load the database with new products
    for row in context.table:
        availability_str = row.get("availability", row.get("available", "False"))
        discontinued_str = row.get("discontinued", "False")
        favorited_str = row.get("favorited", "False")

        price_value = (
            row["price"].strip()
            if "price" in row and row["price"] is not None
            else "0.0"
        )

        payload = {
            "name": row["name"],
            "category": row.get("category", ""),
            "description": row.get("description", ""),
            "price": price_value,
            "image_url": row.get("image_url", ""),
            "availability": _to_bool(availability_str),
            "discontinued": _to_bool(discontinued_str),
            "favorited": _to_bool(favorited_str),
        }

        context.resp = requests.post(rest_endpoint, json=payload, timeout=WAIT_TIMEOUT)

        if (
            context.resp.status_code != HTTP_201_CREATED
        ):  # This is for debugging purposes only
            print("DEBUG POST payload:", payload)
            print("DEBUG Response:", context.resp.status_code, context.resp.text)

        expect(context.resp.status_code).equal_to(HTTP_201_CREATED)
