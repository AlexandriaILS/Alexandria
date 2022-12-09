FROM postgres:15

RUN apt update && apt install postgresql-contrib -y

RUN echo "CREATE EXTENSION IF NOT EXISTS pg_trgm;\n\\connect template1\nCREATE EXTENSION IF NOT EXISTS pg_trgm;" > /docker-entrypoint-initdb.d/pg_trgm.sql