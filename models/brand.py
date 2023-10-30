from config import Config
import logging
import sys
from dataclasses import dataclass

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


@dataclass
class Brand:
    id: int
    name: str

    @staticmethod
    def get(id: int):
        cursor = Config.conn.cursor()
        query = "SELECT * FROM brands WHERE id = %s"
        cursor.execute(query, (id,))

        result = cursor.fetchone()
        return Brand(result[0], result[1])

    @staticmethod
    def create(name: str):
        logging.info(f"Creating brand {name} if it doesn't exist")

        cursor = Config.conn.cursor()
        query = "INSERT INTO brands (name) VALUES (%s) ON CONFLICT (name) DO NOTHING RETURNING *"
        cursor.execute(query, (name,))
        Config.conn.commit()

        query = "SELECT id FROM brands WHERE name = %s"
        cursor.execute(query, (name,))
        id = cursor.fetchone()[0]
        return Brand.get(id)

    def toJSON(self):
        return {
            "id": self.id,
            "name": self.name,
        }
