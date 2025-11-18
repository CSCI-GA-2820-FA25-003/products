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
from service.models import Products, DataValidationError
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
        "available": fields.Boolean(attribute="availability"),
        "description": fields.String,
        "price": fields.Float,
        "favorited": fields.Boolean,
        "discontinued": fields.Boolean,
    },
)

create_model = api.model(
    "CreateProduct",
    {
        "name": fields.String(required=True),
        "category": fields.String,
        "available": fields.Boolean(attribute="availability"),
        "description": fields.String,
        "price": fields.Float,
    },
)

product_args = reqparse.RequestParser()
product_args.add_argument("category", type=str)
product_args.add_argument("name", type=str)
product_args.add_argument("availability", type=str)
product_args.add_argument("page", type=int)
product_args.add_argument("limit", type=int)

######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################

######################################################################
# /products (collection)
######################################################################
@api.route("/products")
class ProductCollection(Resource):
    """Handles list + create"""

    @api.doc("list_products")
    @api.expect(product_args)
    @api.marshal_list_with(product_model)
    def get(self):
        """List products with filtering + pagination"""
        args = product_args.parse_args()

        category = args.get("category")
        name = args.get("name")
        availability = args.get("availability")
        page = args.get("page")
        limit = args.get("limit")

        # Defaulting: tests expect page=1, limit=20 when values = 0 or None
        if not page or page == 0:
            page = 1
        if not limit or limit == 0:
            limit = 20
        if page < 0 or limit < 0:
            abort(status.HTTP_400_BAD_REQUEST, "page and limit must be positive")

        # Base list (model automatically hides discontinued)
        products = Products.all()

        # Filter: category exact match, case-insensitive
        if category:
            cat_lower = category.lower()
            products = [p for p in products if p.category and p.category.lower() == cat_lower]

        # Filter: name partial match, case-insensitive
        if name:
            name_lower = name.lower()
            products = [p for p in products if p.name and name_lower in p.name.lower()]

        # Filter: availability boolean
        if availability is not None:
            is_available = availability.lower() in ["true", "yes", "1"]
            products = [p for p in products if p.availability == is_available]

        # Pagination
        start = (page - 1) * limit
        end = start + limit
        products = products[start:end]

        return [p.serialize() for p in products], status.HTTP_200_OK

    @api.doc("create_products")
    @api.expect(create_model)
    @api.response(201, "Product created")
    @api.marshal_with(product_model, code=201)
    def post(self):
        """Create a new product"""
        if not request.is_json:
            abort(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "Content-Type must be application/json")

        data = request.get_json()
        product = Products()

        try:
            product.deserialize(data)
        except DataValidationError as error:
            abort(status.HTTP_400_BAD_REQUEST, str(error))

        product.create()

        location_url = api.url_for(ProductResource, product_id=product.id)
        return product.serialize(), status.HTTP_201_CREATED, {"Location": location_url}

######################################################################
# /products/<id> (item)
######################################################################
@api.route("/products/<int:product_id>")
@api.param("product_id", "The Product identifier")
class ProductResource(Resource):
    """Retrieve, update, delete"""

    @api.doc("get_product")
    @api.marshal_with(product_model)
    def get(self, product_id):
        product = Products.find(product_id)
        if not product or product.discontinued:
            abort(status.HTTP_404_NOT_FOUND, "Product not found")
        return product.serialize(), status.HTTP_200_OK

    @api.doc("update_product")
    @api.expect(product_model)
    @api.marshal_with(product_model)
    def put(self, product_id):
        if not request.is_json:
            abort(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "Content-Type must be application/json")

        product = Products.find(product_id)
        if not product or product.discontinued:
            abort(status.HTTP_404_NOT_FOUND, "Product not found")

        try:
            product.deserialize(request.get_json())
        except DataValidationError as error:
            abort(status.HTTP_400_BAD_REQUEST, error.args[0])

        product.update()
        return product.serialize(), status.HTTP_200_OK

    @api.doc("delete_product")
    def delete(self, product_id):
        product = Products.find(product_id)
        if product:
            product.delete()
        return "", status.HTTP_204_NO_CONTENT

######################################################################
# /products/<id>/discontinue
######################################################################
@api.route("/products/<int:product_id>/discontinue")
class DiscontinueProduct(Resource):
    @api.doc("discontinue_product")
    def post(self, product_id):
        confirm_arg = request.args.get("confirm")
        confirm_payload = None

        # confirm can be in body OR query string
        if request.is_json:
            payload = request.get_json(silent=True) or {}
            confirm_payload = payload.get("confirm")

        confirmed = False
        if confirm_arg is not None:
            confirmed = confirm_arg.lower() in ["true", "yes", "1"]
        elif confirm_payload is not None:
            if isinstance(confirm_payload, bool):
                confirmed = confirm_payload
            elif isinstance(confirm_payload, str):
                confirmed = confirm_payload.lower() in ["true", "yes", "1"]
            else:
                confirmed = bool(confirm_payload)

        if not confirmed:
            abort(
                status.HTTP_400_BAD_REQUEST,
                "Discontinuing requires confirmation. Add confirm=true to proceed.",
            )

        product = Products.find(product_id)
        if not product or product.discontinued:
            abort(status.HTTP_404_NOT_FOUND, "Product not found")

        product.discontinued = True
        product.availability = False
        product.update()

        return product.serialize(), status.HTTP_200_OK

######################################################################
# /products/<id>/favorite  (PUT + DELETE)
######################################################################
@api.route("/products/<int:product_id>/favorite")
class FavoriteProduct(Resource):
    """Favorite & Unfavorite"""

    def put(self, product_id):
        product = Products.find(product_id)
        if not product or product.discontinued:
            abort(status.HTTP_404_NOT_FOUND, "Product not found")

        # idempotent
        if not getattr(product, "favorited", False):
            product.favorited = True
            product.update()

        return {"id": product.id, "favorited": True}, status.HTTP_200_OK

    def delete(self, product_id):
        product = Products.find(product_id)
        if not product or product.discontinued:
            abort(status.HTTP_404_NOT_FOUND, "Product not found")

        # idempotent
        if getattr(product, "favorited", False):
            product.favorited = False
            product.update()

        return {"id": product.id, "favorited": False}, status.HTTP_200_OK
        
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
