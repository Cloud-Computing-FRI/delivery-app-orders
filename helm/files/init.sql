-- Schema for the orders service.
--
-- Each microservice owns its own database. This file runs automatically from
-- /docker-entrypoint-initdb.d on the in-cluster Postgres' first start, against
-- the database named by POSTGRES_DB. For a managed database (prod) run it once
-- against this service's database:
--     psql "<orders connection string>" -f init.sql

CREATE TABLE orders (
    id         SERIAL PRIMARY KEY,
    customer   TEXT NOT NULL,
    restaurant TEXT NOT NULL,
    item       TEXT NOT NULL,
    price      NUMERIC(6, 2) NOT NULL,
    notified   BOOLEAN NOT NULL DEFAULT FALSE
);
