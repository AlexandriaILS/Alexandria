.PHONY: migrate dev_data run nuke shell docs postgres_up postgres_down

migrate:
	.venv/bin/python manage.py migrate

dev_data:
	.venv/bin/python manage.py bootstrap_dev_site

run:
	.venv/bin/python manage.py runserver

clean:
	rm db.sqlite3

shell:
	.venv/bin/python manage.py shell_plus

docs:
	retype watch

# Want to use Postgres to develop locally? Use these commands to spin up a local
# copy of Postgres through docker. Note: this does expect that you've set up the
# `docker` command to not require the use of `sudo`.
psql_up:
	docker run \
		--name dev-postgres \
		-e POSTGRES_PASSWORD=alexandria \
		-v $(PWD)/postgres_data/:/var/lib/postgresql/data -p 5432:5432 postgres

psql_down:
	docker stop dev-postgres
	docker rm dev-postgres

psql_setup:
	docker exec -it dev-postgres bash -c "apt update && apt install postgresql-contrib -y"
	docker exec -it dev-postgres bash -c "printf '\set AUTOCOMMIT on\ncreate database alexandria;create user alexandria with superuser password '\''asdf'\'';grant all on database alexandria to alexandria;' | psql -h localhost -U postgres"

psql_shell:
	docker exec -it dev-postgres bash -c "psql -h localhost -U postgres"

psql_clean:
	sudo rm -rf postgres_data
