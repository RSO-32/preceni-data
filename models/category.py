from config import Config
from dataclasses import dataclass
from flask import current_app as app


@dataclass
class Category:
    id: int
    name: str

    @staticmethod
    def get(id: int):
        cursor = Config.conn.cursor()
        query = "SELECT * FROM categories WHERE id = %s"
        cursor.execute(query, (id,))

        result = cursor.fetchone()
        return Category(result[0], result[1])

    @staticmethod
    def create(name: str):
        app.logger.info(f"Creating category {name} if it doesn't exist")

        cursor = Config.conn.cursor()
        query = "INSERT INTO categories (name) VALUES (%s) ON CONFLICT (name) DO NOTHING RETURNING *"
        cursor.execute(query, (name,))
        Config.conn.commit()

        query = "SELECT id FROM categories WHERE name = %s"
        cursor.execute(query, (name,))
        id = cursor.fetchone()[0]
        return Category.get(id)

    def toJSON(self):
        return {
            "id": self.id,
            "name": self.name,
        }
