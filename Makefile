.PHONY: migrate dev_data run nuke shell docs db_up db_down db_setup test wipe_db wipe_redis pretty

migrate:
	uv run python manage.py migrate

dev_data:
	uv run python manage.py bootstrap_dev_site

run:
	uv run python manage.py runserver

wipe_db:
	docker exec -it dev-postgres bash -c "psql -h localhost -U postgres -c 'drop database if exists alexandria;'"

wipe_redis:
	docker exec -it dev-redis bash -c "redis-cli FLUSHALL"

clean: | wipe_db wipe_redis db_setup migrate

shell:
	uv run python manage.py shell_plus

docs:
	retype watch

# Want to use Postgres to develop locally? Use these commands to spin up a local
# copy of Postgres through docker. Note: this does expect that you've set up the
# `docker` command to not require the use of `sudo`.
db_up:
	docker volume create pgdata
	docker run -d \
		--name dev-postgres \
		-e POSTGRES_PASSWORD=alexandria \
		-v pgdata:/var/lib/postgresql \
		-p 5432:5432 postgres
	docker run -d \
		--name dev-redis \
		-p 6379:6379 redis

db_down:
	docker stop dev-postgres
	docker stop dev-redis
	docker rm dev-postgres
	docker rm dev-redis

# Install dependency for trigram similarities, force it to be available for every
# test database, and then create the database and user information we'll use to
# connect with.
db_setup:
	docker exec -it dev-postgres bash -c "apt update && apt install postgresql-contrib -y"
	docker exec -it dev-postgres bash -c "echo \"SELECT 'CREATE DATABASE alexandria' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'alexandria')\gexec\" | psql -h localhost -U postgres"
	docker exec -it dev-postgres bash -c "psql -h localhost -U postgres -d template1 -c 'CREATE EXTENSION IF NOT EXISTS pg_trgm;'"
	docker exec -it dev-postgres bash -c "printf '\set AUTOCOMMIT on\nDROP ROLE IF EXISTS alexandria; CREATE USER alexandria WITH SUPERUSER PASSWORD '\''asdf'\''; GRANT ALL ON DATABASE alexandria TO alexandria;' | psql -h localhost -U postgres"

psql_shell:
	docker exec -it dev-postgres bash -c "psql -h localhost -U postgres"

test:
	uv run pytest -n auto

# launch the django_lightweight_queue worker
worker:
	uv run python manage.py queue_runner --config=alexandria/settings/routing.py

pretty:
	@uv run black . \
	&& uv run isort . \
	&& git ls-files -z -- '*.html' | xargs -0r .venv/bin/djade || true \
	&& git ls-files -z -- '*.partial' | xargs -0r .venv/bin/djade || true
