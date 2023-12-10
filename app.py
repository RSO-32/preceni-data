from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_restful import Api
from dotenv import load_dotenv
from os.path import join, dirname
from models.seller import SellerController
from models.product import ProductController, ProductsController
from database import Database
from health import Health
from metrics import Metrics
from os import environ
import logging, graypy

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
api = Api(app)

# Logging
graylog_handler = graypy.GELFUDPHandler("logs.meteo.pileus.si", 12201)
environment = 'dev' if environ.get("DATA_SERVICE_DEBUG") else 'prod'
graylog_handler.setFormatter(logging.Formatter(f"preceni-data {environment} %(asctime)s %(levelname)s %(name)s %(message)s"))
app.logger.addHandler(graylog_handler)
app.logger.setLevel(logging.INFO)

dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)

Database.connect()
app.logger.info("Connected to database")


api.add_resource(SellerController, "/seller/<id>")
api.add_resource(ProductController, "/product/<id>")
api.add_resource(ProductsController, "/product")


@app.route("/health/live")
def health_live():
    app.logger.info("GET: Health live check")
    status, checks = Health.check_health()
    code = 200 if status == "UP" else 503

    return jsonify({"status": status, "checks": checks}), code


@app.route("/health/test/toggle", methods=["PUT"])
def health_test():
    app.logger.info("PUT: Health test toggle")
    Health.force_fail = not Health.force_fail

    return Health.checkTest()


@app.route("/metrics")
def metrics():
    app.logger.info("GET: Metrics")
    metrics = Metrics.get_metrics()

    response = ""
    for metric in metrics:
        response += f"{metric.name} {metric.value}\n"

    return response


@app.route("/database/create")
def create_tables():
    app.logger.info("GET: Create tables")
    Database.create_tables()
    return "Tables created"


@app.route("/database/drop")
def drop_tables():
    app.logger.info("GET: Drop tables")
    Database.drop_tables()
    return "Tables dropped"


if __name__ == "__main__":
    Metrics.init()
    app.run(
        host="0.0.0.0",
        port=environ.get("DATA_SERVICE_PORT"),
        debug=environ.get("DATA_SERVICE_DEBUG"),
    )
