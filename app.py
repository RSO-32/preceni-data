from flask import request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from os.path import join, dirname
from database import Database
from health import Health
from metrics import Metrics
from os import environ
import logging, graypy
from flask_openapi3 import OpenAPI, Info, Tag
from uuid import uuid4
from models.product import Product
from models.seller import Seller
from models.brand import Brand
from models.category import Category
import requests
from datetime import datetime
from pydantic import BaseModel, Field
from ariadne import (
    load_schema_from_path,
    make_executable_schema,
    graphql_sync,
    snake_case_fallback_resolvers,
    ObjectType,
)
from ariadne.constants import PLAYGROUND_HTML
from models.product import listProducts_resolver

info = Info(title="Preceni data", version="1.0.0", description="Preceni data API")
app = OpenAPI(__name__, info=info, doc_prefix="/data/openapi")
CORS(app)  # Enable CORS for all routes

# Logging
graylog_handler = graypy.GELFUDPHandler("logs.meteo.pileus.si", 12201)
environment = "dev" if environ.get("DATA_SERVICE_DEBUG") else "prod"
graylog_handler.setFormatter(
    logging.Formatter(f"preceni-data {environment} %(asctime)s %(levelname)s %(name)s %(message)s")
)
app.logger.addHandler(graylog_handler)
app.logger.setLevel(logging.INFO)

dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)

Database.connect()
app.logger.info("Connected to database")


#
# OpenAPI anotacije:
# - summary
# - description
# - responses
# - tags
# - parameters
#

products_tag = Tag(name="product", description="Product")
database_tag = Tag(name="database", description="Database")
health_tag = Tag(name="health", description="Health and metrics")


class ProductPath(BaseModel):
    id: int = Field(..., description="product id")


class CategoryResponse(BaseModel):
    id: int
    name: str


class ProductResponse(BaseModel):
    id: int
    brand: str
    categories: list[CategoryResponse]
    prices: list[dict]


class ProductsResponse(BaseModel):
    products: list[ProductResponse]


@app.get("/data/health/live", tags=[health_tag], summary="Health live check")
def health_live():
    app.logger.info("GET: Health live check")
    status, checks = Health.check_health()
    code = 200 if status == "UP" else 503

    return jsonify({"status": status, "checks": checks}), code


@app.put("/data/health/test/toggle", tags=[health_tag], summary="Health test toggle")
def health_test():
    app.logger.info("PUT: Health test toggle")
    Health.force_fail = not Health.force_fail

    return Health.checkTest()


@app.get("/data/metrics", tags=[health_tag], summary="Metrics")
def metrics():
    app.logger.info("GET: Metrics")
    metrics = Metrics.get_metrics()

    response = ""
    for metric in metrics:
        response += f"{metric.name} {metric.value}\n"

    return response


@app.get("/data/database/create", tags=[database_tag], summary="Create tables")
def create_tables():
    app.logger.info("GET: Create tables")
    Database.create_tables()
    return "Tables created"


@app.get("/data/database/drop", tags=[database_tag], summary="Drop tables")
def drop_tables():
    app.logger.info("GET: Drop tables")
    Database.drop_tables()
    return "Tables dropped"


@app.get("/data/products/<int:id>", tags=[products_tag], summary="Get product by id", responses={200: ProductResponse})
def get_product(path: ProductPath):
    id = path.id
    uuid = uuid4()
    app.logger.info(f"START: GET /product/<id> [{uuid}]")
    product = Product.get(id)

    if product is None:
        return {"message": "Product not found"}, 404

    app.logger.info(f"END: GET /product/<id> [{uuid}]")
    return product.toJSON(), 200


@app.get("/data/products", tags=[products_tag], summary="Get all products", responses={200: ProductsResponse})
def get_products():
    uuid = uuid4()
    app.logger.info(f"START: GET /products [{uuid}]")
    products = Product.get_all()

    resp = []
    for product in products:
        resp.append(product.toJSON())

    app.logger.info(f"END: GET /products [{uuid}]")
    return resp, 200


@app.post("/data/products", tags=[products_tag], summary="Create product from barcode")
def post_products():
    uuid = uuid4()
    app.logger.info(f"START: POST /products [{uuid}]")
    data = request.get_json()
    barcode = data["barcode"]

    headers = {
        "X-RapidAPI-Key": environ.get("RAPIDAPI_KEY"),
        "X-RapidAPI-Host": "barcodes1.p.rapidapi.com",
    }
    response = requests.get("https://barcodes1.p.rapidapi.com", headers=headers, params={"query": barcode}).json()

    brand = Brand.create(response["product"]["manufacturer"])
    categories = [Category.create(category) for category in response["product"]["category"]]

    seller_info = response["product"]["online_stores"][0]
    seller = Seller.create(seller_info["name"])
    product = Product.create(
        seller,
        seller_info["name"] + response["product"]["title"],
        response["product"]["title"],
        brand,
        categories,
    )
    price = float(seller_info["price"].replace("€", ""))
    product.add_price(datetime.now(), price, seller)

    app.logger.info(f"END: POST /products [{uuid}]")

    return product.toJSON(), 201


@app.put("/data/products", tags=[products_tag], summary="Create or update products")
def put_products():
    uuid = uuid4()
    app.logger.info(f"START: PUT /products [{uuid}]")
    data = request.get_json()

    for product_data in data:
        app.logger.info(product_data)
        timestamp = datetime.fromisoformat(product_data["timestamp"])
        seller = product_data["seller"]
        seller_product_id = product_data["seller_product_id"]
        seller_product_name = product_data["seller_product_name"]
        image_url = product_data["image_url"]
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
                image_url,
                brand,
                categories,
            )

        previous_last_price = product.get_latest_price()
        product.add_price(timestamp, price, seller)

        if previous_last_price is not None and previous_last_price.price > price:
            try:
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
            except Exception as e:
                app.logger.error("Failed to notify, is notify service up?")

    app.logger.info(f"END: PUT /products [{uuid}]")
    return "Products updated", 200


query = ObjectType("Query")
query.set_field("listProducts", listProducts_resolver)

type_defs = load_schema_from_path("schema.graphql")
schema = make_executable_schema(type_defs, query, snake_case_fallback_resolvers)


@app.route("/data/graphql", methods=["GET"])
def graphql_playground():
    return PLAYGROUND_HTML, 200


@app.route("/data/graphql", methods=["POST"])
def graphql_server():
    data = request.get_json()
    success, result = graphql_sync(schema, data, context_value=request, debug=app.debug)
    status_code = 200 if success else 400
    return jsonify(result), status_code


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=environ.get("DATA_SERVICE_PORT"),
        debug=environ.get("DATA_SERVICE_DEBUG"),
    )
