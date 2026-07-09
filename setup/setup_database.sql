-- Exegol Vault: one-time database bootstrap.
-- Run as the postgres superuser (pgAdmin Query Tool on the 'postgres'
-- database, or: psql -U postgres -f setup_database.sql).
--
-- CHANGE THE PASSWORD below, then put the same value in .env
-- as DB_APP_PASSWORD.

CREATE ROLE "Exegol-Vault" LOGIN PASSWORD 'CHANGE_ME_app_role_password';
CREATE DATABASE "Exegol-Vault" OWNER "Exegol-Vault";

-- Optional: a separate demo database for trying the app with sample data
-- (seed it afterwards with: python setup/seed_demo.py)
-- CREATE DATABASE "Exegol-Vault-Demo" OWNER "Exegol-Vault";
