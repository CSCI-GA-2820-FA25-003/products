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
from flask_restx import Api, Resource, fields, reqparse, inputs
from service.models import Products
from service.common import status  # HTTP Status Codes

######################################################################
# Configure Swagger before initializing it
######################################################################
api = Api(
    app,
    version="1.0.0",
    title="Product Administration RESTful Service",
    description="RESTful API for product management operations.",
    default="products",
    default_label="Products operations",
    doc="/apidocs",  # default also could use doc='/apidocs/'
    prefix="/api",
)

######################################################################
# Swagger Models and Argument Parsers
######################################################################

product_model = api.model(
    "Product",
    {
        "id": fields.Integer(readOnly=True, description="The unique id of a product"),
        "name": fields.String(required=True, description="The name of the product"),
        "category": fields.String(description="The category of the product"),
        "availability": fields.Boolean(description="True if the product is available"),
        "price": fields.Float(description="The price of the product"),
        "description": fields.String(description="The description of the product"),
        "discontinued": fields.Boolean(description="True if the product is discontinued"),
        "favorited": fields.Boolean(description="True if the product is favorited"),
    },
)

create_model = api.model(
    "CreateProduct",
    {
        "name": fields.String(required=True, description="The name of the product"),
        "category": fields.String(description="The category of the product"),
        "availability": fields.Boolean(description="True if the product is available"),
        "price": fields.Float(description="The price of the product"),
        "description": fields.String(description="The description of the product"),
    },
)

product_args = reqparse.RequestParser()
product_args.add_argument(
    "category",
    type=str,
    required=False,
    help="Category filter",
    location="args",
)
product_args.add_argument(
    "name",
    type=str,
    required=False,
    help="Name filter",
    location="args",
)
product_args.add_argument(
    "availability",
    type=inputs.boolean,
    required=False,
    help="Availability filter (true/false)",
    location="args",
)
product_args.add_argument(
    "page",
    type=int,
    required=False,
    help="Page number for pagination",
    location="args",
)
product_args.add_argument(
    "limit",
    type=int,
    required=False,
    help="Page size for pagination",
    location="args",
)

######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Base URL for our service"""
    return app.send_static_file("index.html")


######################################################################
# HEALTH CHECK
######################################################################
@api.route("/health")
class Health(Resource):
    """Health check endpoint for Kubernetes.

    This endpoint is used by Kubernetes liveness and readiness probes
    to verify that the service is running properly.
    """

    def get(self):
        """Health check endpoint for Kubernetes"""
        app.logger.info("Health check requested")
        return {"status": "OK"}, status.HTTP_200_OK


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################

######################################################################
#  PATH: /products/{id}
######################################################################
@api.route("/products/<int:product_id>")
@api.param("product_id", "The Product identifier")
class ProductResource(Resource):
    """
    ProductResource class

    Allows the manipulation of a single Product
    GET /products/{id}    - Returns a Product with the id
    PUT /products/{id}    - Update a Product with the id
    DELETE /products/{id} - Deletes a Product with the id
    """

    # ------------------------------------------------------------------
    # RETRIEVE A PRODUCT
    # ------------------------------------------------------------------
    @api.doc("get_products")
    @api.response(404, "Product not found")
    @api.marshal_with(product_model)
    def get(self, product_id):
        """
        Retrieve a single Product

        This endpoint will return a Product based on its id
        """
        app.logger.info("Request to Retrieve a product with id [%s]", product_id)
        product = Products.find(product_id)
        if not product or getattr(product, "discontinued", False):
            abort(
                status.HTTP_404_NOT_FOUND,
                f"product with id '{product_id}' was not found.",
            )
        return product.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE AN EXISTING PRODUCT
    # ------------------------------------------------------------------
    @api.doc("update_products")
    @api.response(404, "Product not found")
    @api.response(400, "The posted Product data was not valid")
    @api.expect(product_model)
    @api.marshal_with(product_model)
    def put(self, product_id):
        """
        Update a Product

        This endpoint will update a Product based on the body that is posted
        """
        app.logger.info("Request to update product with id: %s", product_id)

        product = Products.find(product_id)
        if not product or getattr(product, "discontinued", False):
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Product with id '{product_id}' was not found.",
            )

        app.logger.debug("Payload = %s", api.payload)
        data = api.payload
        product.deserialize(data)
        product.id = product_id
        product.update()

        app.logger.info("Product with ID: %d updated.", product.id)
        return product.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE A PRODUCT
    # ------------------------------------------------------------------
    @api.doc("delete_products")
    @api.response(204, "Product deleted")
    def delete(self, product_id):
        """
        Delete a Product

        This endpoint will delete a Product based on the id in the path
        """
        app.logger.info("Request to delete product with id: %s", product_id)
        product = Products.find(product_id)
        if product:
            product.delete()
            app.logger.info("Product with id [%s] deleted.", product_id)
        else:
            app.logger.warning(
                "Product with id [%s] not found. Nothing to delete.", product_id
            )

        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /products
######################################################################
@api.route("/products", strict_slashes=False)
class ProductCollection(Resource):
    """Handles all interactions with collections of Products"""

    # ------------------------------------------------------------------
    # LIST ALL PRODUCTS
    # ------------------------------------------------------------------
    @api.doc("list_products")
    @api.expect(product_args, validate=True)
    @api.marshal_list_with(product_model)
    def get(self):
        """Returns all of the Products"""
        app.logger.info("Request for product list")

        products = []

        args = product_args.parse_args()
        category = args.get("category")
        name = args.get("name")
        availability = args.get("availability")
        page = args.get("page")
        limit = args.get("limit")

        if category:
            app.logger.info("Find by category: %s", category)
            products = Products.find_by_category(category)
        elif name:
            app.logger.info("Find by name: %s", name)
            products = Products.find_by_name(name)
        elif availability is not None:
            app.logger.info("Find by available: %s", availability)
            products = Products.find_by_availability(bool(availability))
        else:
            app.logger.info("Find all")
            products = Products.all()

        # Sort by name (case insensitive) like before
        products = sorted(products, key=lambda p: (p.name or "").lower())

        # Pagination
        if page is not None and limit is not None:
            page = max(page or 1, 1)
            if (limit or 0) < 1:
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
        return results, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # ADD A NEW PRODUCT
    # ------------------------------------------------------------------
    @api.doc("create_products")
    @api.response(400, "The posted data was not valid")
    @api.expect(create_model)
    @api.marshal_with(product_model, code=201)
    def post(self):
        """
        Create a Product
        This endpoint will create a Product based on the data in the body that is posted
        """
        app.logger.info("Request to Create a product...")
        check_content_type("application/json")

        product = Products()
        app.logger.debug("Payload = %s", api.payload)
        product.deserialize(api.payload)

        # Save the new product to the database
        product.create()
        app.logger.info("product with new id [%s] saved!", product.id)

        # Return the location of the new product
        location_url = api.url_for(ProductResource, product_id=product.id, _external=True)

        return product.serialize(), status.HTTP_201_CREATED, {"Location": location_url}

    # ------------------------------------------------------------------
    # DELETE ALL PRODUCTS (for testing only)
    # ------------------------------------------------------------------
    @api.doc("delete_all_products")
    @api.response(204, "All Products deleted")
    def delete(self):
        """
        Delete all Products

        This endpoint will delete all Products only if the system is under test
        """
        app.logger.info("Request to Delete all products...")
        if "TESTING" in app.config and app.config["TESTING"]:
            Products.remove_all()
            app.logger.info("Removed all Products from the database")
        else:
            app.logger.warning(
                "Request to clear database while system not under test"
            )

        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /products/{id}/discontinue
######################################################################
@api.route("/products/<int:product_id>/discontinue")
@api.param("product_id", "The Product identifier")
class DiscontinueProductResource(Resource):
    """Discontinue actions on a Product"""

    @api.doc("discontinue_product")
    @api.response(404, "Product not found")
    @api.response(400, "Discontinuing requires confirmation")
    @api.marshal_with(product_model)
    def post(self, product_id):
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

        return product.serialize(), status.HTTP_200_OK


######################################################################
#  PATH: /products/{id}/favorite
######################################################################
@api.route("/products/<int:product_id>/favorite")
@api.param("product_id", "The Product identifier")
class FavoriteProductResource(Resource):
    """Favorite a Product"""

    @api.doc("favorite_product")
    @api.response(404, "Product not found")
    @api.marshal_with(product_model)
    def put(self, product_id):
        """Favorite a product (idempotent)"""
        app.logger.info("Request to favorite product with id: %s", product_id)

        product = Products.find(product_id)
        if not product or product.discontinued:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Product with id '{product_id}' was not found.",
            )

        if not getattr(product, "favorited", False):
            product.favorited = True
            product.update()

        return product.serialize(), status.HTTP_200_OK


######################################################################
#  PATH: /products/{id}/unfavorite
######################################################################
@api.route("/products/<int:product_id>/unfavorite")
@api.param("product_id", "The Product identifier")
class UnfavoriteProductResource(Resource):
    """Unfavorite a Product"""

    @api.doc("unfavorite_product")
    @api.response(404, "Product not found")
    @api.marshal_with(product_model)
    def put(self, product_id):
        """Unfavorite a product (idempotent)"""
        app.logger.info("Request to unfavorite product with id: %s", product_id)

        product = Products.find(product_id)
        if not product or product.discontinued:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Product with id '{product_id}' was not found.",
            )

        if getattr(product, "favorited", False):
            product.favorited = False
            product.update()

        return product.serialize(), status.HTTP_200_OK


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
#  U T I L I T Y   F U N C T I O N S
######################################################################
def abort(error_code: int, message: str):
    """Logs errors before aborting"""
    app.logger.error(message)
    api.abort(error_code, message)


def data_reset():
    """Removes all Products from the database"""
    Products.remove_all()