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
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Base URL for our service"""
    return app.send_static_file("index.html")

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

# query string arguments
product_args = reqparse.RequestParser()
product_args.add_argument("category", type=str, location="args", required=False, help="Category filter")
product_args.add_argument("name", type=str, location="args", required=False, help="Name filter")
product_args.add_argument(
    "availability",
    type=inputs.boolean,
    location="args",
    required=False,
    help="Availability filter",
)
product_args.add_argument("page", type=int, location="args", required=False, help="Page number for pagination")
product_args.add_argument("limit", type=int, location="args", required=False, help="Page size for pagination")


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
    PUT /products/{id}    - Updates a Product with the id
    DELETE /products/{id} - Deletes a Product with the id
    """

    # ------------------------------------------------------------------
    # RETRIEVE A PRODUCT
    # ------------------------------------------------------------------
    @api.doc("get_products")
    @api.response(404, "Product not found")
    @api.marshal_with(product_model)
    def get(self, product_id):

        app.logger.info("Request to Retrieve a product with id [%s]", product_id)

        product = Products.find(product_id)
        if not product or product.discontinued:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"product with id '{product_id}' was not found.",
            )

        app.logger.info("Returning product: %s", product.name)
        return product.serialize(), status.HTTP_200_OK
    # ------------------------------------------------------------------
    # UPDATE AN EXISTING PRODUCT
    # ------------------------------------------------------------------
    @api.doc("update_products")
    @api.response(404, "Product not found")
    @api.response(400, "The posted Product data was not valid")
    @api.expect(product_model)          # or update_model if you have one
    @api.marshal_with(product_model)
    def put(self, product_id):
        """
        Update a Product

        This endpoint will update a Product based on the body that is posted
        """
        app.logger.info("Request to update product with id: %s", product_id)

        product = Products.find(product_id)
        if not product or product.discontinued:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Product with id '{product_id}' was not found.",
            )

        app.logger.debug("Payload = %s", api.payload)
        data = api.payload
        product.deserialize(data)
        product.update()

        app.logger.info("Product with ID: %d updated.", product.id)
        return product.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE A PRODUCT
    # ------------------------------------------------------------------
    @api.doc("delete_products")
    @api.response(204, "Product deleted")
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

######################################################################
#  PATH: /products/{id}/discontinue
######################################################################
@api.route("/products/<int:product_id>/discontinue")
@api.param("product_id", "The Product identifier")
class DiscontinueProductResource(Resource):
    """Discontinue a product so it is no longer available via the API"""

    @api.doc("discontinue_product")
    @api.response(400, "Discontinuing requires confirmation")
    @api.response(404, "Product not found")
    def post(self, product_id):
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
    """Favorite a product (idempotent)"""

    @api.doc("favorite_product")
    @api.response(404, "Product not found")
    def put(self, product_id):
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
