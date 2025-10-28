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
from service.models import Products
from service.common import status  # HTTP Status Codes


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        jsonify(
            {
                "name": "Products REST API Service",
                "version": "1.0.0",
                "description": "Provides RESTful API for managing product inventory",
                "endpoints": {
                    "list_products": "/products",
                    "create_product": "/products (POST)",
                    "get_product": "/products/<product_id>",
                    "update_product": "/products/<product_id> (PUT)",
                    "delete_product": "/products/<product_id> (DELETE)",
                    "discontinue_product": "/products/<product_id>/discontinue (POST)",
                },
                "status": "healthy",
            }
        ),
        status.HTTP_200_OK,
    )

######################################################################
# HEALTH CHECK
######################################################################


@app.route("/health")
def health():
    """Health check endpoint for Kubernetes"""
    app.logger.info("Health check requested")
    return jsonify({"status": "OK"}), status.HTTP_200_OK

######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


######################################################################
# LIST ALL products
######################################################################
@app.route("/products", methods=["GET"])
def list_products():
    """Returns all of the products"""
    app.logger.info("Request for product list")

    products = []

    # Parse any arguments from the query string
    category = request.args.get("category")
    name = request.args.get("name")
    availability = request.args.get("availability")
    page_param = request.args.get("page")
    limit_param = request.args.get("limit")

    if category:
        app.logger.info("Find by category: %s", category)
        products = Products.find_by_category(category)
    elif name:
        app.logger.info("Find by name: %s", name)
        products = Products.find_by_name(name)
    elif availability:
        app.logger.info("Find by available: %s", availability)
        # create bool from string
        available_value = availability.lower() in ["true", "yes", "1"]
        products = Products.find_by_availability(available_value)
    else:
        app.logger.info("Find all")
        products = Products.all()

    products = sorted(products, key=lambda p: (p.name or "").lower())
    if page_param is not None and limit_param is not None:
        try:
            page = int(page_param)
            limit = int(limit_param)
        except (TypeError, ValueError):
            page = 1
            limit = 100

        page = max(page, 1)
        if limit < 1:
            limit = 100

        start = (page - 1) * limit
        end = start + limit
        products = products[start:end]
        app.logger.info(
            "Paginated results: page=%d, limit=%d, returning %d products",
            page,
            limit,
            len(products),
        )
    else:
        app.logger.info("No pagination parameters provided, returning all products")

    results = [product.serialize() for product in products]
    return jsonify(results), status.HTTP_200_OK


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
    if not product or product.discontinued:
        abort(
            status.HTTP_404_NOT_FOUND, f"product with id '{product_id}' was not found."
        )

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
    location_url = url_for("get_products", product_id=product.id, _external=True)

    return (
        jsonify(product.serialize()),
        status.HTTP_201_CREATED,
        {"Location": location_url},
    )


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
    if not product or product.discontinued:
        abort(
            status.HTTP_404_NOT_FOUND, f"Product with id '{product_id}' was not found."
        )

    data = request.get_json()
    app.logger.info("Processing: %s", data)
    product.deserialize(data)
    product.update()

    app.logger.info("Product with ID: %d updated.", product.id)
    return jsonify(product.serialize()), status.HTTP_200_OK


######################################################################
# DELETE A PRODUCT
######################################################################
@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    """Delete a Product"""
    app.logger.info("Request to delete product with id: %s", product_id)

    product = Products.find(product_id)
    if product:
        product.delete()
        app.logger.info("Product with id [%s] deleted.", product_id)
    else:
        app.logger.warning(
            "Product with id [%s] not found. Nothing to delete.", product_id
        )

    return jsonify(message=f"Product {product_id} deleted."), status.HTTP_204_NO_CONTENT


######################################################################
# DISCONTINUE A PRODUCT
######################################################################
@app.route("/products/<int:product_id>/discontinue", methods=["POST"])
def discontinue_product(product_id):
    """Discontinue a product so it is no longer available via the API"""
    app.logger.info("Request to discontinue product with id: %s", product_id)

    confirm_arg = request.args.get("confirm")
    confirm_payload = None
    if request.is_json:
        payload = request.get_json(silent=True) or {}
        if isinstance(payload, dict):
            confirm_payload = payload.get("confirm")

    confirmed = False
    if confirm_arg is not None:
        confirmed = str(confirm_arg).lower() in ["true", "yes", "1", "y"]
    elif confirm_payload is not None:
        if isinstance(confirm_payload, bool):
            confirmed = confirm_payload
        elif isinstance(confirm_payload, str):
            confirmed = confirm_payload.lower() in ["true", "yes", "1", "y"]
        elif isinstance(confirm_payload, (int, float)):
            confirmed = bool(confirm_payload)

    if not confirmed:
        abort(
            status.HTTP_400_BAD_REQUEST,
            "Discontinuing requires confirmation. Add confirm=true to proceed.",
        )

    product = Products.find(product_id)
    if not product or product.discontinued:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"product with id '{product_id}' was not found.",
        )

    product.discontinued = True
    product.availability = False
    product.update()
    app.logger.info("Product with id [%s] discontinued.", product_id)

    return jsonify(product.serialize()), status.HTTP_200_OK


######################################################################
# FAVORITE / UNFAVORITE A PRODUCT
######################################################################


@app.route("/products/<int:product_id>/favorite", methods=["PUT"])
def favorite_product(product_id):
    """Favorite a product (idempotent)"""
    app.logger.info("Request to favorite product with id: %s", product_id)

    product = Products.find(product_id)
    if not product or product.discontinued:
        abort(
            status.HTTP_404_NOT_FOUND, f"Product with id '{product_id}' was not found."
        )

    if not getattr(product, "favorited", False):
        product.favorited = True
        product.update()

    return jsonify({"id": product.id, "favorited": True}), status.HTTP_200_OK


@app.route("/products/<int:product_id>/unfavorite", methods=["PUT"])
def unfavorite_product(product_id):
    """Unfavorite a product (idempotent)"""
    app.logger.info("Request to unfavorite product with id: %s", product_id)

    product = Products.find(product_id)
    if not product or product.discontinued:
        abort(
            status.HTTP_404_NOT_FOUND, f"Product with id '{product_id}' was not found."
        )

    if getattr(product, "favorited", False):
        product.favorited = False
        product.update()

    return jsonify({"id": product.id, "favorited": False}), status.HTTP_200_OK
