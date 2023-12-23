from config import Config
from os import environ
import psycopg2
from flask import current_app as app

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

    @staticmethod
    def create_tables():
        cursor = Config.conn.cursor()

        app.logger.info("Creating tables")

        cursor.execute(
            """create table if not exists users (
            id serial primary key,
            first_name text,
            last_name text,
            email text unique,
            password_hash text)"""
        )

        cursor.execute(
            """create table if not exists user_tokens (
            id serial primary key,
            user_id integer,
            token text,
            expires_at timestamptz,
            created_at timestamptz default now(),
            foreign key (user_id) references users (id))"""
        )

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
            """create table if not exists notifications (
                      id serial primary key,
                      user_id integer,
                      product_id integer,
                      price real not null,
                      constraint unique_user_id_product_id unique (user_id, product_id),
                      foreign key (user_id) references users(id),
                      foreign key (product_id) references products(id))"""
        )

        cursor.execute(
            """create table if not exists user_notifications (
                id serial primary key,
                user_id integer,
                discord_webhook text,
                foreign key (user_id) references users(id))"""
        )

        cursor.execute(
            """create table if not exists product_sellers (
            product_id integer,
            seller_id integer,
            seller_product_id text not null,
            seller_name text not null,
            image_url text,
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

        app.logger.info("Dropping tables")

        cursor.execute("DROP TABLE IF EXISTS prices CASCADE")
        cursor.execute("DROP TABLE IF EXISTS product_sellers CASCADE")
        cursor.execute("DROP TABLE IF EXISTS product_categories CASCADE")
        cursor.execute("DROP TABLE IF EXISTS products CASCADE")
        cursor.execute("DROP TABLE IF EXISTS sellers CASCADE")
        cursor.execute("DROP TABLE IF EXISTS categories CASCADE")
        cursor.execute("DROP TABLE IF EXISTS brands CASCADE")
        cursor.execute("DROP TABLE IF EXISTS notifications CASCADE")
        cursor.execute("DROP TABLE IF EXISTS user_notifications CASCADE")
        cursor.execute("DROP TABLE IF EXISTS user_tokens CASCADE")
        cursor.execute("DROP TABLE IF EXISTS users CASCADE")

        Config.conn.commit()
