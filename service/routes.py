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
Products Service

This service implements a REST API that allows you to Create, Read, Update
and Delete Products
"""

from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
from service.models import Products, DataValidationError
from service.common import status  # HTTP Status Codes


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        "Reminder: return some useful information in json format about the service here",
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################

######################################################################
# UPDATE AN EXISTING PRODUCT
######################################################################
@app.route("/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    """
    Update a Product

    This endpoint will update a Product based on the body that is posted
    """
    app.logger.info("Request to update product with id: %s", product_id)

    check_content_type("application/json")

    product = Products.find(product_id)
    if not product:
        abort(status.HTTP_404_NOT_FOUND, f"Product with id '{product_id}' was not found.")

    # Get the JSON data
    data = request.get_json()
    app.logger.debug("Payload = %s", data)

    # Support partial updates - only update provided fields
    try:
        # Update only the fields that are provided in the request
        if "name" in data:
            product.name = data["name"]
        if "description" in data:
            product.description = data["description"]
        if "price" in data:
            product.price = data["price"]
        if "image_url" in data:
            product.image_url = data["image_url"]
        if "category" in data:
            product.category = data["category"]
        if "availability" in data:
            product.availability = data["availability"]

        # Save the updates
        product.update()

    except (KeyError, TypeError, ValueError) as error:
        abort(status.HTTP_400_BAD_REQUEST, str(error))
    except DataValidationError as error:
        abort(status.HTTP_400_BAD_REQUEST, str(error))

    app.logger.info("Product with ID [%s] updated.", product.id)
    return jsonify(product.serialize()), status.HTTP_200_OK


######################################################################
# DELETE A PRODUCT
######################################################################
@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    """
    Delete a Product

    This endpoint will delete a Product based on the id specified in the path
    """
    app.logger.info("Request to delete product with id: %s", product_id)

    # Find the product
    product = Products.find(product_id)
    if not product:
        abort(status.HTTP_404_NOT_FOUND, f"Product with id '{product_id}' was not found.")

    # Delete the product
    product.delete()

    app.logger.info("Product with ID [%s] deleted.", product.id)
    return "", status.HTTP_204_NO_CONTENT

######################################################################
# READ A product
######################################################################
@app.route("/products/<int:product_id>", methods=["GET"])
def get_products(product_id):
    """
    Retrieve a single product

    This endpoint will return a product based on it's id
    """
    app.logger.info("Request to Retrieve a product with id [%s]", product_id)

    # Attempt to find the product and abort if not found
    product = Products.find(product_id)
    if not product:
        abort(status.HTTP_404_NOT_FOUND, f"product with id '{product_id}' was not found.")

    app.logger.info("Returning product: %s", product.name)
    return jsonify(product.serialize()), status.HTTP_200_OK


######################################################################
# CREATE A NEW PRODUCT
######################################################################
@app.route("/products", methods=["POST"])
def create_products():
    """
    Create a product
    This endpoint will create a product based the data in the body that is posted
    """
    app.logger.info("Request to Create a product...")
    check_content_type("application/json")

    product = Products()
    # Get the data from the request and deserialize it
    data = request.get_json()
    app.logger.info("Processing: %s", data)
    product.deserialize(data)

    # Save the new product to the database
    product.create()
    app.logger.info("product with new id [%s] saved!", product.id)

    # Return the location of the new product

    # Todo: uncomment this code when get_products is implemented 
    location_url = url_for("get_products", product_id=product.id, _external=True)

    # location_url = "unknown"

    return jsonify(product.serialize()), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
# Checks the ContentType of a request
######################################################################
def check_content_type(content_type) -> None:
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )

