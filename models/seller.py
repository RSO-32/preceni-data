from config import Config
from flask import current_app as app
from flask_restful import Resource
from dataclasses import dataclass


class SellerController(Resource):
    def get(self, id):
        return Seller.get(id).toJSON(), 200


@dataclass
class Seller:
    id: int
    name: str

    @staticmethod
    def get(id: int):
        cursor = Config.conn.cursor()
        query = "SELECT * FROM sellers WHERE id = %s"
        cursor.execute(query, (id,))

        result = cursor.fetchone()
        return Seller(result[0], result[1])

    @staticmethod
    def create(name: str):
        app.logger.info(f"Creating seller {name} if it doesn't exist")

        cursor = Config.conn.cursor()
        query = "INSERT INTO sellers (name) VALUES (%s) ON CONFLICT (name) DO NOTHING RETURNING id"
        cursor.execute(query, (name,))
        Config.conn.commit()

        query = "SELECT id FROM sellers WHERE name = %s"
        cursor.execute(query, (name,))
        id = cursor.fetchone()[0]
        return Seller.get(id)

    def toJSON(self):
        return {"id": self.id, "name": self.name}
