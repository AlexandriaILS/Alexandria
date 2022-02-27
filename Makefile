migrate:
	.venv/bin/python manage.py migrate

dev_data:
	.venv/bin/python manage.py bootstrap_dev_site

run:
	.venv/bin/python manage.py runserver