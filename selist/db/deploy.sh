#!/bin/bash

source "$(dirname "$0")/../.env"
PGPASSWORD="$DB_ADMIN_PASSWORD" psql -h localhost -U postgres -v db_password="$DB_PASSWORD" -v db_user="$DB_USER" -v db_name="$DB_NAME" -f deploy.sql