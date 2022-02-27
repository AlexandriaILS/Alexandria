migrate:
	.venv/bin/python manage.py migrate

dev_data:
	.venv/bin/python manage.py bootstrap_dev_site

run:
	.venv/bin/python manage.py runserver

nuke:
	rm db.sqlite3

shell:
	.venv/bin/python manage.py shell_plus