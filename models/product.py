from flask import current_app as app
from models.category import Category
from models.seller import Seller
from models.brand import Brand
from dataclasses import dataclass
from datetime import datetime
from config import Config


def listProducts_resolver(obj, info):
    try:
        products = [product.toJSON() for product in Product.get_all()]
        payload = {
            "success": True,
            "products": products
        }
    except Exception as error:
        payload = {
            "success": False,
            "errors": [str(error)]
        }
    return payload

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
        app.logger.info("GET: All products")

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
        app.logger.info(f"GET: Product {id}")

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
        app.logger.info(f"Creating product {seller_name} with brand {brand.id} for seller {seller.id}")

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
        app.logger.info(f"Finding product by seller's id {product_seller_id} for seller {seller.id}")

        cursor = Config.conn.cursor()
        query = "SELECT product_id FROM product_sellers WHERE seller_product_id = %s AND seller_id = %s"
        cursor.execute(query, (str(product_seller_id), seller.id))

        result = cursor.fetchone()
        if result is None:
            return None
        return Product.get(result[0])

    @staticmethod
    def get_categories(product_id):
        app.logger.info(f"Getting categories for product {product_id}")

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
        app.logger.info(f"Getting prices for product {product_id}")

        cursor = Config.conn.cursor()
        query = """
        SELECT prices.datetime, prices.price, sellers.name FROM prices
            JOIN sellers ON prices.seller_id = sellers.id
        WHERE prices.product_id = %s ORDER BY prices.datetime DESC"""
        cursor.execute(query, (product_id,))
        result = cursor.fetchall()

        return [Price(row[0], row[1], row[2]) for row in result]

    def add_price(self, datetime: datetime, price: float, seller: Seller):
        app.logger.info(f"Adding price {price} at {datetime} for product {self.id}")

        cursor = Config.conn.cursor()
        query = (
            "INSERT INTO prices (datetime, product_id, seller_id, price) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING"
        )
        cursor.execute(query, (datetime, self.id, seller.id, price))
        Config.conn.commit()

    def get_latest_price(self):
        app.logger.info(f"Getting latest price for product {self.id}")

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

    def priceToJSON(self, price):
        return {
            "datetime": price.datetime.isoformat(),
            "price": price.price,
            "seller": price.seller,
        }

    def toJSON(self):
        return {
            "id": self.id,
            "brand": self.brand,
            "categories": [category.toJSON() for category in self.categories],
            "prices": [self.priceToJSON(price) for price in self.prices],
        }
