# Pense-bête

## Commandes utiles

uv run manage.py runserver
uv run manage.py createsuperuser
uv run manage.py makemigrations
uv run manage.py migrate

## Setup

### Prerequisites

- PostgreSQL database installed and running
- Python 3.9 (maybe higher)
- UV installed
- .env configured from .env.sample

### Commands

```shell
cd db && ./deploy.sh  # setup the database
uv sync  # Install python and dependencies
uv run python manage.py migrate  # Migrate the database
source .env && DJANGO_SUPERUSER_PASSWORD=$ADMIN_PASSWORD DJANGO_SUPERUSER_USERNAME=$ADMIN_USER DJANGO_SUPERUSER_EMAIL=$ADMIN_EMAIL uv run python manage.py createsuperuser --noinput
```

### Deployment

Upload code to server, then run:

```shell
uv run  python manage.py collectstatic --noinput
sudo supervisorctl restart selist
```