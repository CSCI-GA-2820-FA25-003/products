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

from flask import request
from flask import current_app as app  # Import Flask application
from flask_restx import Api, Resource, fields, reqparse
from werkzeug.exceptions import MethodNotAllowed
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


@api.errorhandler(MethodNotAllowed)
def handle_method_not_allowed(error):
    """Return JSON for 405 Method Not Allowed"""
    app.logger.error("Method not allowed: %s", error)
    return {
        "status": status.HTTP_405_METHOD_NOT_ALLOWED,
        "error": "Method Not Allowed",
        "message": "The method is not allowed for the requested URL.",
    }, status.HTTP_405_METHOD_NOT_ALLOWED

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
# SWAGGER MODELS
######################################################################


product_model = api.model(
    "Product",
    {
        "id": fields.Integer(readOnly=True),
        "name": fields.String,
        "category": fields.String,
        "availability": fields.Boolean,
        "description": fields.String,
        "price": fields.String,
        "image_url": fields.String,
        "favorited": fields.Boolean,
        "discontinued": fields.Boolean,
    },
)

create_model = api.model(
    "CreateProduct",
    {
        "name": fields.String(required=True),
        "category": fields.String,
        "availability": fields.Boolean,
        "description": fields.String,
        "price": fields.String,
        "image_url": fields.String,
    },
)

product_args = reqparse.RequestParser()
product_args.add_argument("category", type=str)
product_args.add_argument("name", type=str)
product_args.add_argument("availability", type=str)

######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


@api.route("/products", strict_slashes=False)
class ProductCollection(Resource):
    """Handles interactions with collections of Products"""

    @api.doc("list_products")
    @api.expect(product_args)
    @api.marshal_list_with(product_model)
    def get(self):
        """Returns a list of Products"""
        app.logger.info("Request for product list")

        args = product_args.parse_args()
        category = args.get("category")
        name = args.get("name")
        availability = args.get("availability")
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

        results = [p.serialize() for p in products]
        return results, status.HTTP_200_OK

    @api.doc("create_product")
    @api.expect(create_model)
    @api.marshal_with(product_model, code=status.HTTP_201_CREATED)
    def post(self):
        """Create a Product"""
        app.logger.info("Request to Create a product...")
        check_content_type("application/json")

        data = api.payload or {}
        app.logger.info("Processing: %s", data)

        product = Products()
        product.deserialize(data)
        product.create()
        app.logger.info("product with new id [%s] saved!", product.id)

        location_url = api.url_for(
            ProductResource, product_id=product.id, _external=True
        )

        result = product.serialize()
        return result, status.HTTP_201_CREATED, {"Location": location_url}


@api.route("/products/<int:product_id>")
@api.param("product_id", "The Product identifier")
class ProductResource(Resource):
    """Handles interactions with a single Product"""

    @api.doc("get_product")
    @api.response(status.HTTP_404_NOT_FOUND, "Product not found")
    @api.marshal_with(product_model)
    def get(self, product_id):
        """Retrieve a single Product"""
        app.logger.info("Request to Retrieve a product with id [%s]", product_id)

        product = Products.find(product_id)
        if not product or product.discontinued:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"product with id '{product_id}' was not found.",
            )

        app.logger.info("Returning product: %s", product.name)

        result = product.serialize()

        return result, status.HTTP_200_OK

    @api.doc("update_product")
    @api.response(status.HTTP_404_NOT_FOUND, "Product not found")
    @api.expect(create_model)
    @api.marshal_with(product_model)
    def put(self, product_id):
        """Update a Product"""
        app.logger.info("Request to update product with id: %s", product_id)
        check_content_type("application/json")

        product = Products.find(product_id)
        if not product or product.discontinued:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Product with id '{product_id}' was not found.",
            )

        data = api.payload or {}
        app.logger.info("Processing: %s", data)
        product.deserialize(data)
        product.update()

        app.logger.info("Product with ID: %d updated.", product.id)

        result = product.serialize()
        return result, status.HTTP_200_OK

    @api.doc("delete_product")
    @api.response(status.HTTP_204_NO_CONTENT, "Product deleted")
    def delete(self, product_id):
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

        return "", status.HTTP_204_NO_CONTENT


@api.route("/products/<int:product_id>/discontinue")
@api.param("product_id", "The Product identifier")
class ProductDiscontinueResource(Resource):
    """Discontinue a product"""

    @api.doc("discontinue_product")
    @api.response(status.HTTP_200_OK, "Product discontinued")
    @api.response(status.HTTP_400_BAD_REQUEST, "Confirmation missing or invalid")
    @api.response(status.HTTP_404_NOT_FOUND, "Product not found")
    def post(self, product_id):
        """Discontinue a product"""
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


@api.route("/products/<int:product_id>/favorite")
@api.param("product_id", "The Product identifier")
class ProductFavoriteResource(Resource):
    """Favorite a product"""

    @api.doc("favorite_product")
    @api.response(status.HTTP_200_OK, "Product favorited")
    @api.response(status.HTTP_404_NOT_FOUND, "Product not found")
    def put(self, product_id):
        """Favorite a product"""
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

        return {"id": product.id, "favorited": True}, status.HTTP_200_OK


@api.route("/products/<int:product_id>/unfavorite")
@api.param("product_id", "The Product identifier")
class ProductUnfavoriteResource(Resource):
    """Unfavorite a product"""

    @api.doc("unfavorite_product")
    @api.response(status.HTTP_200_OK, "Product unfavorited")
    @api.response(status.HTTP_404_NOT_FOUND, "Product not found")
    def put(self, product_id):
        """Unfavorite a product"""
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

        return {"id": product.id, "favorited": False}, status.HTTP_200_OK

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


def abort(error_code: int, message: str):
    """Logs errors before aborting"""
    app.logger.error(message)
    api.abort(error_code, message)
