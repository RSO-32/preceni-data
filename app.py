from flask import Flask, request
from flask_cors import CORS
from flask_restful import Api
from dotenv import load_dotenv
from os.path import join, dirname
import logging
import sys
from models.seller import SellerController
from models.product import ProductController, ProductsController
from database import Database
from os import environ

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
api = Api(app)

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)

Database.connect()


api.add_resource(SellerController, "/seller/<id>")
api.add_resource(ProductController, "/product/<id>")
api.add_resource(ProductsController, "/product")


@app.route("/database/create")
def create_tables():
    Database.create_tables()
    return "Tables created"


@app.route("/database/drop")
def drop_tables():
    Database.drop_tables()
    return "Tables dropped"

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=environ.get("DATA_SERVICE_PORT"),
        debug=environ.get("DATA_SERVICE_DEBUG"),
    )