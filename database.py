from config import Config
from os import environ
import psycopg2
import logging


class Database:
    @staticmethod
    def connect():
        Config.conn = psycopg2.connect(
            database=environ.get("DB_NAME"),
            host=environ.get("DB_HOST"),
            user=environ.get("DB_USER"),
            password=environ.get("DB_PASSWORD"),
            port=environ.get("DB_PORT"),
        )

    logging.info("Initialized database connection")

    @staticmethod
    def create_tables():
        cursor = Config.conn.cursor()

        logging.info("Creating tables")

        cursor.execute(
            """create table if not exists sellers (
            id serial primary key,
            name text not null unique)"""
        )

        cursor.execute(
            """create table if not exists categories (
            id serial primary key,
            name text not null unique)"""
        )

        cursor.execute(
            """create table if not exists brands (
            id serial primary key,
            name text not null unique)"""
        )

        cursor.execute(
            """create table if not exists products (
            id serial primary key,
            brand_id integer,
            foreign key (brand_id) references brands(id))"""
        )

        cursor.execute(
            """create table if not exists prices (
            datetime timestamptz not null,
            price real not null,
            seller_id integer,
            product_id integer,
            primary key (datetime, seller_id, product_id),
            foreign key (seller_id) references sellers(id),
            foreign key (product_id) references products(id))"""
        )

        cursor.execute(
            """create table if not exists product_sellers (
            product_id integer,
            seller_id integer,
            seller_product_id integer not null,
            seller_name text not null,
            primary key (product_id, seller_id),
            foreign key (product_id) REFERENCES products(id),
            foreign key (seller_id) REFERENCES sellers(id))"""
        )

        cursor.execute(
            """create table if not exists product_categories (
            product_id integer,
            category_id integer,
            primary key (product_id, category_id),
            foreign key (product_id) references products(id),
            foreign key (category_id) references categories(id))"""
        )

        Config.conn.commit()

    @staticmethod
    def drop_tables():
        cursor = Config.conn.cursor()

        logging.info("Dropping tables")

        cursor.execute("DROP TABLE IF EXISTS prices")
        cursor.execute("DROP TABLE IF EXISTS product_sellers")
        cursor.execute("DROP TABLE IF EXISTS product_categories")
        cursor.execute("DROP TABLE IF EXISTS products")
        cursor.execute("DROP TABLE IF EXISTS sellers")
        cursor.execute("DROP TABLE IF EXISTS categories")
        cursor.execute("DROP TABLE IF EXISTS brands")

        Config.conn.commit()
