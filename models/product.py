import logging
from flask_restful import Resource
from flask import request
import sys
from models.category import Category
from models.seller import Seller
from models.brand import Brand
from dataclasses import dataclass
from datetime import datetime
import requests
from os import environ
from config import Config

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class ProductController(Resource):
    def get(self, id):
        product = Product.get(id)

        if product is None:
            return {"message": "Product not found"}, 404

        return product.toJSON(), 200


class ProductsController(Resource):
    def get(self):
        products = Product.get_all()

        resp = []
        for product in products:
            resp.append(product.toJSON())

        return resp, 200

    def put(self):
        data = request.get_json()

        for product_data in data:
            logging.info(product_data)
            timestamp = datetime.fromisoformat(product_data["timestamp"])
            seller = product_data["seller"]
            seller_product_id = product_data["seller_product_id"]
            seller_product_name = product_data["seller_product_name"]
            price = float(product_data["price"])
            categories = product_data["categories"]
            brand = product_data["brand"]

            seller = Seller.create(seller)
            brand = Brand.create(brand)
            categories = [Category.create(category) for category in categories]

            product = Product.find_by_sellers_id(seller_product_id, seller)
            if product is None:
                product = Product.create(
                    seller,
                    seller_product_id,
                    seller_product_name,
                    brand,
                    categories,
                )

            previous_last_price = product.get_latest_price()
            product.add_price(timestamp, price, seller)

            if previous_last_price is not None and previous_last_price.price > price:
                requests.post(
                    environ.get("NOTIFY_URL"),
                    json={
                        "product_id": product.id,
                        "product_name": product.get_name(),
                        "current_price": price,
                        "previous_price": previous_last_price.price,
                        "seller": seller.name,
                    },
                )

        return 201


@dataclass
class Price:
    datetime: datetime
    price: float
    seller: Seller


@dataclass
class Product:
    id: int
    brand: str
    categories: list[Category]
    prices: list[Price]

    @staticmethod
    def get_all():
        logging.info("GET: All products")

        cursor = Config.conn.cursor()
        query = """
        SELECT products.id, brands.name FROM products 
            JOIN brands ON products.brand_id = brands.id"""
        cursor.execute(query, (id,))
        product_result = cursor.fetchall()

        products = []

        for row in product_result:
            products.append(
                Product(
                    row[0],
                    row[1],
                    Product.get_categories(row[0]),
                    Product.get_prices(row[0]),
                )
            )
        return products

    @staticmethod
    def get(id):
        logging.info(f"GET: Product {id}")

        cursor = Config.conn.cursor()
        query = """
        SELECT products.id, brands.name FROM products 
            JOIN brands ON products.brand_id = brands.id    
        WHERE products.id = %s"""
        cursor.execute(query, (id,))
        product_result = cursor.fetchone()

        if product_result is None:
            return None

        return Product(
            product_result[0],
            product_result[1],
            Product.get_categories(id),
            Product.get_prices(id),
        )

    @staticmethod
    def create(
        seller: Seller,
        seller_product_id: str,
        seller_name: str,
        brand: Brand,
        categories: list[Category],
    ):
        logging.info(
            f"Creating product {seller_name} with brand {brand.id} for seller {seller.id}"
        )

        cursor = Config.conn.cursor()
        query = "INSERT INTO products (brand_id) VALUES (%s) RETURNING id"
        cursor.execute(query, (brand.id,))
        product_id = cursor.fetchone()[0]

        query = "INSERT INTO product_sellers (product_id, seller_id, seller_product_id, seller_name) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING"
        cursor.execute(query, (product_id, seller.id, seller_product_id, seller_name))

        for category in categories:
            query = "INSERT INTO product_categories (product_id, category_id) VALUES (%s, %s) ON CONFLICT DO NOTHING"
            cursor.execute(query, (product_id, category.id))

        Config.conn.commit()

        return Product.get(product_id)

    @staticmethod
    def find_by_sellers_id(product_seller_id, seller: Seller):
        logging.info(
            f"Finding product by seller's id {product_seller_id} for seller {seller.id}"
        )

        cursor = Config.conn.cursor()
        query = "SELECT product_id FROM product_sellers WHERE seller_product_id = %s AND seller_id = %s"
        cursor.execute(query, (product_seller_id, seller.id))

        result = cursor.fetchone()
        if result is None:
            return None
        return Product.get(result[0])

    @staticmethod
    def get_categories(product_id):
        logging.info(f"Getting categories for product {product_id}")

        cursor = Config.conn.cursor()
        query = """
        SELECT categories.id, categories.name FROM categories
            JOIN product_categories ON categories.id = product_categories.category_id
        WHERE product_categories.product_id = %s"""
        cursor.execute(query, (product_id,))
        result = cursor.fetchall()

        return [Category(row[0], row[1]) for row in result]

    @staticmethod
    def get_prices(product_id):
        logging.info(f"Getting prices for product {product_id}")

        cursor = Config.conn.cursor()
        query = """
        SELECT prices.datetime, prices.price, sellers.name FROM prices
            JOIN sellers ON prices.seller_id = sellers.id
        WHERE prices.product_id = %s ORDER BY prices.datetime DESC"""
        cursor.execute(query, (product_id,))
        result = cursor.fetchall()

        return [Price(row[0], row[1], row[2]) for row in result]

    def add_price(self, datetime: datetime, price: float, seller: Seller):
        logging.info(f"Adding price {price} at {datetime} for product {self.id}")

        cursor = Config.conn.cursor()
        query = "INSERT INTO prices (datetime, product_id, seller_id, price) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING"
        cursor.execute(query, (datetime, self.id, seller.id, price))
        Config.conn.commit()

    def get_latest_price(self):
        logging.info(f"Getting latest price for product {self.id}")

        cursor = Config.conn.cursor()
        query = """
        SELECT prices.datetime, prices.price, sellers.name FROM prices
            JOIN sellers ON prices.seller_id = sellers.id
        WHERE prices.product_id = %s ORDER BY prices.datetime DESC LIMIT 1"""
        cursor.execute(query, (self.id,))
        result = cursor.fetchone()

        if result is None:
            return None

        return Price(result[0], result[1], result[2])

    def get_name(self):
        cursor = Config.conn.cursor()
        query = "SELECT seller_name FROM product_sellers WHERE product_id = %s LIMIT 1"
        cursor.execute(query, (self.id,))
        result = cursor.fetchone()

        return result[0]


    def toJSON(self):
        return {
            "id": self.id,
            "name": self.name,
            "brand": self.brand,
            "categories": [category.toJSON() for category in self.categories],
            "prices": [price.toJSON() for price in self.prices],
        }
