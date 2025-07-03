# Pense-bête

## Commandes utiles

python manage.py runserver
python manage.py createsuperuser
python manage.py makemigrations
python manage.py migrate

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
uv python manage.py migrate  # Migrate the database
source .env && DJANGO_SUPERUSER_PASSWORD=$ADMIN_PASSWORD DJANGO_SUPERUSER_USERNAME=$ADMIN_USER DJANGO_SUPERUSER_EMAIL=$ADMIN_EMAIL uv run python manage.py createsuperuser --noinput
```
