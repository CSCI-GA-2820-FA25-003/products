"""
Models for Products

All of the models are stored in this module
"""

from datetime import datetime, timezone
import logging

from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DatabaseConnectionError(Exception):
    """Custom Exception when database connection fails"""


class DataValidationError(Exception):
    """Custom Exception with data validation fails"""


# pylint: disable=too-many-instance-attributes
class Products(db.Model):
    """
    Class that represents a Products
    """

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63), nullable=False)
    description = db.Column(db.String(1023), nullable=True)
    price = db.Column(db.Numeric(14, 2), nullable=False)

    image_url = db.Column(db.String(1023), nullable=True)
    category = db.Column(db.String(63), nullable=True)
    availability = db.Column(db.Boolean, default=True, nullable=False)
    favorited = db.Column(db.Boolean, nullable=False, default=False)
    discontinued = db.Column(db.Boolean, default=False, nullable=False)
    created_date = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_date = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self):
        return f"<Products {self.name} id=[{self.id}]>"

    def create(self):
        """
        Creates a Products to the database
        """
        logger.info("Creating %s", self.name)
        self.id = None  # pylint: disable=invalid-name
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating record: %s", self)
            raise DataValidationError(e) from e

    def update(self):
        """
        Updates a Products to the database
        """
        logger.info("Saving %s", self.name)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating record: %s", self)
            raise DataValidationError(e) from e

    def delete(self):
        """Removes a Products from the data store"""
        logger.info("Deleting %s", self.name)
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting record: %s", self)
            raise DataValidationError(e) from e

    def serialize(self):
        """Serializes a Products into a dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "price": str(
                self.price
            ),  # Convert Decimal to string for JSON serialization since Json does not support Decimal
            "description": self.description,
            "image_url": self.image_url,
            "category": self.category,
            "availability": self.availability,
            "favorited": self.favorited,
            "discontinued": self.discontinued,
            "created_date": self.created_date.isoformat() if self.created_date else None,
            "updated_date": self.updated_date.isoformat() if self.updated_date else None,
        }

    def deserialize(self, data):
        """
        Deserializes a Products from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.name = data["name"]
            self.description = data["description"]
            self.price = data["price"]
            self.image_url = data["image_url"]
            self.category = data["category"]
            self.availability = data.get("availability", True)
            self.discontinued = data.get("discontinued", False)
            self.favorited = data.get("favorited", False)
            self.created_date = data.get("created_date", datetime.now(timezone.utc))
            self.updated_date = data.get("updated_date", datetime.now(timezone.utc))
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Products: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Products: body of request contained bad or no data "
                + str(error)
            ) from error
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def all(cls):
        """Returns all of the Productss in the database"""
        logger.info("Processing all Productss")
        return cls.query.filter(cls.discontinued.is_(False)).all()

    @classmethod
    def find(cls, by_id):
        """Finds a Products by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.session.get(cls, by_id)

    @classmethod
    def find_by_name(cls, name):
        """Returns all Productss with the given name

        Args:
            name (string): the name of the Productss you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.discontinued.is_(False)).filter(
            cls.name.ilike(f"%{name}%")
        )

    @classmethod
    def find_by_category(cls, category: str) -> list:
        """Returns all of the products in a category

        :param category: the category of the products you want to match
        :type category: str

        :return: a collection of products in that category
        :rtype: list

        """
        logger.info("Processing category query for %s ...", category)
        return cls.query.filter(cls.discontinued.is_(False)).filter(
            cls.category.ilike(f"%{category}%")
        )

    @classmethod
    def find_by_availability(cls, available: bool = True) -> list:
        """Returns all products by their availability

        :param available: True for products that are available
        :type available: str

        :return: a collection of products that are available
        :rtype: list

        """
        if not isinstance(available, bool):
            raise TypeError("Invalid availability, must be of type boolean")
        logger.info("Processing available query for %s ...", available)
        return cls.query.filter(cls.discontinued.is_(False)).filter(
            cls.availability == available
        )
